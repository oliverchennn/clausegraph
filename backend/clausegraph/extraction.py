"""Native extraction and a closed, evidence-gated compilation boundary."""
from __future__ import annotations

import csv
import io
import multiprocessing
import re
from datetime import date, datetime
from decimal import Decimal
from pathlib import PurePath

from pypdf import PdfReader

from .schemas import (
    Action, ApprovalStatus, Document, DocumentPage, ExtractionResult, FinancialEvent,
    ReviewBlocker, ReviewStatus, Rule, Scenario,
)


MAX_NATIVE_PAGES = 200
MAX_NATIVE_CHARACTERS = 2_000_000
MAX_NATIVE_BYTES = 20 * 1024 * 1024
PDF_PARSE_TIMEOUT_SECONDS = 20.0
_NUMBER = r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?"
_MONEY = re.compile(rf"(?:\$\s*({_NUMBER})(?!\d|[.,]\d)|USD\s*({_NUMBER})(?!\d|[.,]\d)|(?<![\d.,])({_NUMBER})\s*(?:USD|dollars?)\b|(?<![\d.,])(\d+)\s*cents?\b)", re.IGNORECASE)


def _pdf_worker(content: bytes, connection):
    """A killable process contains expensive parsing of untrusted PDF streams."""
    try:
        reader = PdfReader(io.BytesIO(content), strict=True)
        if reader.is_encrypted:
            raise ValueError("Encrypted PDFs must be decrypted before upload.")
        if len(reader.pages) > MAX_NATIVE_PAGES:
            raise ValueError(f"Documents are limited to {MAX_NATIVE_PAGES} pages.")
        pages = []
        characters = 0
        for index, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            characters += len(text)
            if characters > MAX_NATIVE_CHARACTERS:
                raise ValueError("Extracted text exceeds the document limit.")
            pages.append({"page": index + 1, "text": text})
        connection.send((True, pages))
    except Exception:
        connection.send((False, "PDF could not be parsed within document limits; check that it is valid and unencrypted."))
    finally:
        connection.close()


def _extract_pdf(content: bytes) -> list[DocumentPage]:
    context = multiprocessing.get_context("spawn")
    parent, child = context.Pipe(duplex=False)
    process = context.Process(target=_pdf_worker, args=(content, child), daemon=True)
    try:
        process.start()
        child.close()
        if not parent.poll(PDF_PARSE_TIMEOUT_SECONDS):
            raise ValueError("Native PDF extraction timed out. Split or simplify this document and retry.")
        try:
            succeeded, payload = parent.recv()
        except EOFError as exc:
            raise ValueError("Native PDF extraction stopped unexpectedly.") from exc
        if not succeeded:
            raise ValueError(payload)
        return [DocumentPage.model_validate(page) for page in payload]
    finally:
        parent.close()
        child.close()
        if process.pid is not None:
            if process.is_alive():
                process.terminate()
            process.join(timeout=1)
            if process.is_alive():
                process.kill()
                process.join(timeout=1)
            process.close()


def extract_native(content: bytes, filename: str, media_type: str) -> list[DocumentPage]:
    """Preserve page-local text exactly; no model, OCR, or outbound call here."""
    if len(content) > MAX_NATIVE_BYTES:
        raise ValueError("The document exceeds the native extraction byte limit.")
    suffix = PurePath(filename).suffix.casefold()
    if suffix == ".pdf" and media_type == "application/pdf":
        if not content.startswith(b"%PDF-"):
            raise ValueError("The uploaded file does not have a PDF signature.")
        pages = _extract_pdf(content)
    elif (suffix == ".txt" and media_type in ("text/plain", "application/octet-stream")) or (suffix == ".csv" and media_type in ("text/csv", "application/csv", "application/vnd.ms-excel", "text/plain")):
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError("Text and CSV documents must use UTF-8 encoding.") from exc
        if "\x00" in text:
            raise ValueError("Binary content is not accepted as text.")
        if suffix == ".csv":
            try:
                list(csv.reader(io.StringIO(text), strict=True))
            except csv.Error as exc:
                raise ValueError("The CSV is malformed.") from exc
        pages = [DocumentPage(page=1, text=text)]
    else:
        raise ValueError("Supported document types are PDF, UTF-8 text, and CSV with matching filename and media type.")
    if sum(len(page.text) for page in pages) > MAX_NATIVE_CHARACTERS:
        raise ValueError("Extracted text exceeds the document limit.")
    return pages


def monetary_values(text: str) -> set[int]:
    """Parse literal money without binary floating point or model arithmetic."""
    values: set[int] = set()
    for match in _MONEY.finditer(text):
        groups = match.groups()
        if groups[3] is not None:
            values.add(int(groups[3]))
        else:
            token = next(value for value in groups[:3] if value is not None)
            values.add(int(Decimal(token.replace(",", "")) * 100))
    if re.search(r"\b(?:no fee|without (?:a )?fee|fee[- ]free)\b", text, re.IGNORECASE):
        values.add(0)
    return values


def _date_supported(value, text: str) -> bool:
    if re.search(rf"(?<!\d){value.isoformat()}(?!\d)", text):
        return True
    for token in re.findall(r"\b[A-Za-z]+\s+\d{1,2},?\s+\d{4}\b", text):
        for fmt in ("%B %d, %Y", "%B %d %Y", "%b %d, %Y", "%b %d %Y"):
            try:
                if datetime.strptime(token, fmt).date() == value:
                    return True
            except ValueError:
                continue
    return False


def _csv_money(document: Document, quotes: str) -> set[int]:
    """Only an explicitly USD/cents-labeled CSV column can support bare numbers."""
    if document.media_type not in ("text/csv", "application/csv", "application/vnd.ms-excel"):
        return set()
    values = set()
    for page in document.pages:
        rows = list(csv.reader(io.StringIO(page.text)))
        if not rows:
            continue
        for index, column in enumerate(rows[0]):
            name = column.strip().casefold()
            if name not in ("amount_usd", "amount_cents", "usd", "cents"):
                continue
            for quote_row in csv.reader(io.StringIO(quotes)):
                if len(quote_row) <= index:
                    continue
                token = quote_row[index]
                if re.fullmatch(_NUMBER, token):
                    value = Decimal(token.replace(",", "")) * (1 if "cents" in name else 100)
                    if value == value.to_integral_value():
                        values.add(int(value))
    return values


def validate_extraction(result: ExtractionResult, document: Document) -> ExtractionResult:
    """Check exact provenance/numbers; a model can never attest human approval."""
    validated = result.model_copy(deep=True)
    pages = {page.page: page.text for page in document.pages}
    seen: set[str] = set()
    for rule in validated.rules:
        reasons: list[str] = []
        if len(pages) != len(document.pages):
            reasons.append("document contains duplicate page identifiers")
        if rule.id in seen:
            reasons.append("duplicate rule identifier")
        seen.add(rule.id)
        if not rule.evidence:
            reasons.append("no evidence quote")
        for evidence in rule.evidence:
            text = pages.get(evidence.page)
            if evidence.document_id != document.id or evidence.version != document.version:
                reasons.append("document identity or version mismatch")
            if text is None or not evidence.quote.strip() or evidence.char_start >= evidence.char_end or evidence.char_end > len(text) or text[evidence.char_start:evidence.char_end] != evidence.quote:
                reasons.append("quote or page-local character offsets do not match")
        quotes = "\n".join(evidence.quote for evidence in rule.evidence)
        if rule.amount_cents is not None and rule.amount_cents not in monetary_values(quotes) | _csv_money(document, quotes):
            reasons.append("amount is not present as literal money in the evidence")
        if rule.due_date is not None and not _date_supported(rule.due_date, quotes):
            reasons.append("date is not present as an explicit date in the evidence")
        if rule.entity_ambiguous:
            reasons.append("entity match requires review")
        # Resolution of user facts and third-party authorization is a separate human workflow.
        for condition in rule.conditions:
            condition.resolved = False
            condition.satisfied = None
        rule.review_status = ReviewStatus.unresolved if reasons else ReviewStatus.pending
        if rule.approval_status == ApprovalStatus.approved or (rule.kind == "benefit" and rule.approval_status == ApprovalStatus.not_required):
            rule.approval_status = ApprovalStatus.pending
        if reasons:
            rule.evidence_status = "unsupported"
            rule.verifier_notes = "; ".join(reasons)
            validated.warnings.append(f"{rule.title}: {rule.verifier_notes}.")
        elif rule.evidence_status not in ("disputed", "unsupported"):
            rule.evidence_status = "supported"
    for action in validated.actions:
        action.review_status = ReviewStatus.pending
        if action.approval_status == ApprovalStatus.approved or (action.kind in ("claim", "request", "shift") and action.approval_status == ApprovalStatus.not_required):
            action.approval_status = ApprovalStatus.pending
    return validated


def rule_blockers(rule: Rule, *, check_approval: bool = True) -> list[ReviewBlocker]:
    """Describe every existing gate, in the legacy first-blocker order."""
    blockers = []
    if rule.review_status != ReviewStatus.reviewed:
        blockers.append(ReviewBlocker(code="review_rejected" if rule.review_status == ReviewStatus.rejected else "human_review",
            category="review", message=f"{rule.title} requires human review.",
            next_step="This rule was rejected. Keep it excluded unless corrected source evidence justifies a new review."
            if rule.review_status == ReviewStatus.rejected else "Read the original source, check the extracted facts and save your review."))
    if not rule.evidence or rule.evidence_status != "supported":
        blockers.append(ReviewBlocker(code="unsupported_evidence", category="evidence",
            message=f"{rule.title} lacks supported evidence.",
            next_step="Check the original quote, page and version. A confirmation note cannot override failed source checks."))
    if rule.entity_ambiguous:
        blockers.append(ReviewBlocker(code="ambiguous_entity", category="evidence",
            message=f"{rule.title} has an ambiguous entity match.",
            next_step="Obtain an unambiguous source identifying the correct party or account; do not infer an entity match."))
    if any(not condition.resolved or condition.satisfied is not True for condition in rule.conditions):
        unsatisfied = any(condition.resolved and condition.satisfied is False for condition in rule.conditions)
        blockers.append(ReviewBlocker(code="condition_unsatisfied" if unsatisfied else "condition_unresolved",
            category="condition", message=f"{rule.title} has unresolved or unsatisfied conditions.",
            next_step="A recorded condition is not satisfied. Keep the option excluded unless new evidence changes that fact."
            if unsatisfied else "Check each stated condition against evidence; leave unknown conditions unresolved."))
    if check_approval and (rule.approval_status not in (ApprovalStatus.approved, ApprovalStatus.not_required) or (rule.kind == "benefit" and rule.approval_status != ApprovalStatus.approved)):
        denied = rule.approval_status == ApprovalStatus.denied
        blockers.append(ReviewBlocker(code="approval_denied" if denied else "approval_pending",
            category="approval", message=f"{rule.title} lacks required third-party approval.",
            next_step="The recorded decision is denied. Only update it after a new decision from the relevant party."
            if denied else "Wait for an actual third-party decision; human source review does not grant approval."))
    return blockers


def rule_blocker(rule: Rule, *, check_approval: bool = True) -> str | None:
    """Preserve the planner/compiler's original first-blocker messages and order."""
    blockers = rule_blockers(rule, check_approval=check_approval)
    return blockers[0].message if blockers else None


def _incoming_money_supported(rule: Rule) -> bool:
    quotes = "\n".join(evidence.quote for evidence in rule.evidence)
    incoming = re.search(r"\b(?:paycheck|payroll|income|refund\w*|reimburs\w*|grant|benefit|deposited|disburs\w*|receiv\w*)\b", quotes, re.IGNORECASE)
    expense = re.search(r"\b(?:rent|fees?|charges?|charged|repay\w*|deduct\w*|debit\w*|purchase|cost)\b|\byou\s+owe\b", quotes, re.IGNORECASE)
    return bool(incoming and not expense)


def event_evidence_blocker(event: FinancialEvent, rules: list[Rule], *, check_values: bool = True) -> str | None:
    """An amount/date quote cannot turn a payable bill into incoming cash."""
    if event.kind != "projected":
        return "Extracted candidates cannot attest an actual transaction."
    indexed = {rule.id: rule for rule in rules}
    if not event.source_rule_ids or any(rid not in indexed for rid in event.source_rule_ids):
        return "Event lacks a known source rule."
    sources = [indexed[rid] for rid in event.source_rule_ids]
    matching = [rule for rule in sources if not check_values or (rule.amount_cents == event.amount_cents and rule.due_date == event.date)]
    if not matching:
        return "No single source obligation supports both the event amount and date."
    if event.direction == "income" and not any(_incoming_money_supported(rule) for rule in matching):
        return "The event source does not unambiguously describe incoming money."
    if event.direction == "expense" and all(_incoming_money_supported(rule) for rule in matching):
        return "The event source describes incoming money, not an expense."
    return None


def action_evidence_blocker(action: Action, rules: list[Rule], events: list[FinancialEvent] | None = None) -> str | None:
    """Check each transformation's literals and target linkage independently of approvals.

    These narrow checks do not establish semantic truth; reviewed source rules
    and evidence verification remain separate prerequisites in both callers.
    """
    indexed = {rule.id: rule for rule in rules}
    if not action.source_rule_ids or any(rid not in indexed for rid in action.source_rule_ids):
        return "Action lacks a known source rule."
    source_ids = set(action.source_rule_ids)
    pending = list(source_ids)
    while pending:
        rule = indexed[pending.pop()]
        for rid in rule.dependencies:
            if rid in indexed and rid not in source_ids:
                source_ids.add(rid)
                pending.append(rid)
    sources = [indexed[rid] for rid in source_ids]
    quotes = "\n".join(evidence.quote for rule in sources for evidence in rule.evidence)
    amounts = monetary_values(quotes) | {rule.amount_cents for rule in sources if rule.amount_cents is not None}
    fees = set()
    for match in _MONEY.finditer(quotes):
        before = quotes[max(0, match.start() - 40):match.start()]
        after = quotes[match.end():match.end() + 40]
        if re.search(r"\bfees?\s*(?:(?:of|is|:)\s*)?$", before, re.IGNORECASE) or re.match(r"\s*(?:(?:processing|cancellation|late|service)\s+)?fees?\b", after, re.IGNORECASE):
            fees.update(monetary_values(match.group(0)))
    if (action.fee_cents or fees) and action.fee_cents not in fees:
        return "The action fee is missing or not supported by a source fee clause."
    targets = {event.id: event for event in events or []}
    operation_cues = {
        "remove": r"\b(?:cancel\w*|terminat\w*|remov\w*|waiv\w*)\b",
        "shift": r"\b(?:mov\w*|shift\w*|reschedul\w*|defer\w*|extend\w*|extension)\b",
        "accelerate": r"\b(?:accelerat\w*|becomes? due|due immediately|due on (?:the )?cancellation)\b",
    }
    if any(effect.operation == "remove" for effect in action.effects) and re.search(operation_cues["accelerate"], quotes, re.IGNORECASE) and not any(effect.operation == "accelerate" for effect in action.effects):
        return "The cancellation omits the debt acceleration described by its source."
    for effect in action.effects:
        if effect.operation in operation_cues and not re.search(operation_cues[effect.operation], quotes, re.IGNORECASE):
            return f"Source evidence does not describe the {effect.operation} transformation."
        if effect.date is not None and not _date_supported(effect.date, quotes):
            return "The effect date is not supported by an explicit source date."
        if effect.offset_days is not None:
            explicit_days = effect.offset_days >= 0 and re.search(rf"\b{effect.offset_days}\s+days?\b", quotes, re.IGNORECASE)
            same_day = effect.offset_days == 0 and re.search(r"\b(?:immediately|same day|on the (?:cancellation|execution|action) date)\b", quotes, re.IGNORECASE)
            if not explicit_days and not same_day:
                return "The effect's relative date is not supported by the source."
        if effect.operation == "add" and effect.event:
            if effect.event.amount_cents not in amounts:
                return "The added event amount is not supported by the source."
            if effect.event.source_rule_ids and not set(effect.event.source_rule_ids).issubset(source_ids):
                return "The added event references unrelated source rules."
            if effect.date is None and effect.offset_days is None and not _date_supported(effect.event.date, quotes):
                return "The added event date is not supported by an explicit source date."
            if effect.event.kind != "projected":
                return "An action cannot invent an actual transaction."
            if effect.event.direction == "income" and not any(_incoming_money_supported(rule) and effect.event.amount_cents in monetary_values("\n".join(e.quote for e in rule.evidence)) for rule in sources):
                return "The source does not identify the added amount as incoming money."
        elif events is not None:
            target = targets.get(effect.target_event_id)
            if target is None:
                return "The target financial event is missing."
            if target.source_rule_ids:
                if not set(target.source_rule_ids).intersection(source_ids):
                    return "The action source does not identify the target obligation."
            elif target.amount_cents not in amounts:
                return "The target obligation amount is not linked to the action evidence."
    return None


def compile_rules(result: ExtractionResult) -> ExtractionResult:
    """Return only supported executable DSL artifacts; retain rules for review."""
    compiled = result.model_copy(deep=True)
    rules = {rule.id: rule for rule in compiled.rules}
    blocked = {rule.id for rule in compiled.rules if rule_blocker(rule)}
    from .graph import dependency_issues
    graph_scenario = Scenario(id="compilation", title="Compilation validation", start_date=date(2000, 1, 1), opening_balance_cents=0, events=compiled.events, actions=compiled.actions)
    blocked.update(rid for issue in dependency_issues(graph_scenario, compiled.rules) if issue.blocking for rid in issue.rule_ids)
    while True:
        expanded = blocked | {rule.id for rule in compiled.rules if any(dep not in rules or dep in blocked for dep in rule.dependencies)}
        if expanded == blocked:
            break
        blocked = expanded
    # Dependency cycles cannot establish one another's evidence.
    import networkx as nx
    graph = nx.DiGraph()
    graph.add_nodes_from(rules)
    graph.add_edges_from((rule.id, dep) for rule in compiled.rules for dep in rule.dependencies if dep in rules)
    for component in nx.strongly_connected_components(graph):
        if len(component) > 1 or any(graph.has_edge(node, node) for node in component):
            blocked.update(component)
    for node in tuple(blocked):
        if node in graph:
            blocked.update(nx.ancestors(graph, node))
    for rule in compiled.rules:
        if rule.id not in blocked:
            blocked.update(rule.supersedes)
    for node in tuple(blocked):
        if node in graph:
            blocked.update(nx.ancestors(graph, node))

    def sources_valid(ids: list[str]) -> bool:
        return bool(ids) and all(rid in rules and rid not in blocked for rid in ids)

    actions = []
    for action in compiled.actions:
        valid = sources_valid(action.source_rule_ids) and action.review_status == ReviewStatus.reviewed and action.approval_status in (ApprovalStatus.approved, ApprovalStatus.not_required)
        valid = valid and action_evidence_blocker(action, compiled.rules) is None
        if valid:
            actions.append(action)
        else:
            compiled.warnings.append(f"{action.title}: executable action withheld until evidence, amounts, dates, review and approval are supported.")
    # Cascading missing action dependencies also fail closed.
    while True:
        ids = {action.id for action in actions}
        filtered = [action for action in actions if all(dep in ids for dep in action.requires)]
        if len(filtered) == len(actions):
            break
        actions = filtered
    compiled.actions = actions
    compiled.events = [event for event in compiled.events if sources_valid(event.source_rule_ids) and event_evidence_blocker(event, compiled.rules) is None]
    return compiled
