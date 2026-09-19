"""Native extraction and a closed, evidence-gated compilation boundary."""
from __future__ import annotations

import csv
import io
import re
from datetime import datetime
from decimal import Decimal
from pathlib import PurePath

from pypdf import PdfReader

from .schemas import ApprovalStatus, Document, DocumentPage, ExtractionResult, ReviewStatus, Rule


MAX_NATIVE_PAGES = 200
MAX_NATIVE_CHARACTERS = 2_000_000
_NUMBER = r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?"
_MONEY = re.compile(rf"(?:\$\s*({_NUMBER})|USD\s*({_NUMBER})|({_NUMBER})\s*(?:USD|dollars?)\b|(\d+)\s*cents?\b)", re.IGNORECASE)


def extract_native(content: bytes, filename: str, media_type: str) -> list[DocumentPage]:
    """Preserve page-local text exactly; no model, OCR, or outbound call here."""
    suffix = PurePath(filename).suffix.casefold()
    if suffix == ".pdf" and media_type == "application/pdf":
        if not content.startswith(b"%PDF-"):
            raise ValueError("The uploaded file does not have a PDF signature.")
        reader = PdfReader(io.BytesIO(content), strict=True)
        if reader.is_encrypted:
            raise ValueError("Encrypted PDFs must be decrypted before upload.")
        if len(reader.pages) > MAX_NATIVE_PAGES:
            raise ValueError(f"Documents are limited to {MAX_NATIVE_PAGES} pages.")
        pages = [DocumentPage(page=index + 1, text=page.extract_text() or "") for index, page in enumerate(reader.pages)]
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
    if value.isoformat() in text:
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


def rule_blocker(rule: Rule, *, check_approval: bool = True) -> str | None:
    if rule.review_status != ReviewStatus.reviewed:
        return f"{rule.title} requires human review."
    if not rule.evidence or rule.evidence_status != "supported":
        return f"{rule.title} lacks supported evidence."
    if rule.entity_ambiguous:
        return f"{rule.title} has an ambiguous entity match."
    if any(not condition.resolved or condition.satisfied is not True for condition in rule.conditions):
        return f"{rule.title} has unresolved or unsatisfied conditions."
    if check_approval and (rule.approval_status not in (ApprovalStatus.approved, ApprovalStatus.not_required) or (rule.kind == "benefit" and rule.approval_status != ApprovalStatus.approved)):
        return f"{rule.title} lacks required third-party approval."
    return None


def compile_rules(result: ExtractionResult) -> ExtractionResult:
    """Return only supported executable DSL artifacts; retain rules for review."""
    compiled = result.model_copy(deep=True)
    rules = {rule.id: rule for rule in compiled.rules}
    blocked = {rule.id for rule in compiled.rules if rule_blocker(rule)}
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

    def sources_valid(ids: list[str]) -> bool:
        return bool(ids) and all(rid in rules and rid not in blocked for rid in ids)

    actions = []
    for action in compiled.actions:
        valid = sources_valid(action.source_rule_ids) and action.review_status == ReviewStatus.reviewed and action.approval_status in (ApprovalStatus.approved, ApprovalStatus.not_required)
        amounts = {rules[rid].amount_cents for rid in action.source_rule_ids if rid in rules}
        quotes = "\n".join(e.quote for rid in action.source_rule_ids if rid in rules for e in rules[rid].evidence)
        if action.fee_cents and action.fee_cents not in monetary_values(quotes):
            valid = False
        for effect in action.effects:
            if effect.operation == "add" and effect.event:
                if effect.event.amount_cents not in amounts or not _date_supported(effect.date or effect.event.date, quotes):
                    valid = False
            if effect.date is not None and not _date_supported(effect.date, quotes):
                valid = False
            if effect.offset_days is not None:
                explicit_days = re.search(rf"\b{abs(effect.offset_days)}\s+days?\b", quotes, re.IGNORECASE)
                same_day = effect.offset_days == 0 and re.search(r"\b(?:immediately|same day|on the (?:cancellation|execution|action) date)\b", quotes, re.IGNORECASE)
                if not explicit_days and not same_day:
                    valid = False
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
    compiled.events = [event for event in compiled.events if sources_valid(event.source_rule_ids) and event.amount_cents in {rules[rid].amount_cents for rid in event.source_rule_ids} and any(rules[rid].due_date == event.date for rid in event.source_rule_ids)]
    return compiled
