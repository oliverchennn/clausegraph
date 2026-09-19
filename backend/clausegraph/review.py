"""Read-only review guidance from canonical gates; no optimization or cash ranking."""
from __future__ import annotations

from .engine import _approval_gate, _gates
from .extraction import action_evidence_blocker, event_evidence_blocker, rule_blockers
from .graph import dependency_issues
from .schemas import (
    ApprovalStatus, PlanRequest, ReviewBlocker, ReviewQueue, ReviewQueueItem, ReviewStatus, Workspace,
)


def review_queue(workspace: Workspace) -> ReviewQueue:
    scenario, rules = workspace.scenario, workspace.rules
    indexed = {rule.id: rule for rule in rules}
    actions = {action.id: action for action in scenario.actions}
    documents = {document.id: document for document in workspace.documents}
    issues = dependency_issues(scenario, rules)
    # Recorded state only: preview/nominal approval assumptions do not resolve review tasks.
    excluded, _ = _gates(scenario, rules, PlanRequest())
    items: list[ReviewQueueItem] = []

    def rule_closure(ids):
        found = set()
        pending = list(ids)
        while pending:
            identifier = pending.pop()
            if identifier in found:
                continue
            found.add(identifier)
            if identifier in indexed:
                pending.extend(indexed[identifier].dependencies)
        return found

    def action_sources(action):
        found, pending, sources = set(), [action.id], set()
        while pending:
            identifier = pending.pop()
            if identifier in found or identifier not in actions:
                continue
            found.add(identifier)
            sources.update(rule_closure(actions[identifier].source_rule_ids))
            pending.extend(actions[identifier].requires)
        return sources

    affected = {action.id: action_sources(action) for action in scenario.actions}
    essential = rule_closure(rid for event in scenario.events
        if event.essential or event.service_id in scenario.essential_service_ids for rid in event.source_rule_ids)
    represented = {rid for event in scenario.events for rid in event.source_rule_ids}
    recorded_blockers = {rule.id: rule_blockers(rule) for rule in rules}
    superseded = {old for rule in rules if not recorded_blockers[rule.id] for old in rule.supersedes}

    def add(kind, identifier, title, priority, blockers, rule_ids, action_ids, event_ids, *, missing=False):
        if not blockers:
            return
        unique = list({(blocker.code, blocker.message): blocker for blocker in blockers}.values())
        codes = {blocker.code for blocker in unique}
        terminal = {"approval_denied", "condition_unsatisfied", "review_rejected"}
        disposition = "blocked" if codes & terminal else "waiting" if codes == {"approval_pending"} else "needs_review"
        evidence = {}
        for rid in rule_ids:
            for source in indexed[rid].evidence if rid in indexed else []:
                document = documents.get(source.document_id)
                if document is not None and document.version == source.version:
                    key = (source.document_id, source.version, source.page, source.char_start, source.char_end)
                    evidence[key] = source
                else:
                    missing = True
        items.append(ReviewQueueItem(id=f"{kind}:{identifier}", subject_kind=kind, subject_id=identifier,
            title=title, priority=priority, disposition=disposition, blockers=unique,
            rule_ids=sorted(rid for rid in set(rule_ids) if rid in indexed), action_ids=sorted(set(action_ids)),
            event_ids=sorted(set(event_ids)), evidence=[evidence[key] for key in sorted(evidence)],
            missing_source=missing))

    for rule in sorted(rules, key=lambda item: item.id):
        blockers = list(recorded_blockers[rule.id])
        missing = not rule.evidence or any(source.document_id not in documents or
            documents[source.document_id].version != source.version for source in rule.evidence)
        if missing:
            blockers.append(ReviewBlocker(code="missing_source", category="evidence",
                message="The cited source or version is unavailable in this workspace.",
                next_step="Provide the missing original source before treating this rule as verified."))
        for issue in issues:
            if issue.blocking and rule.id in issue.rule_ids:
                if issue.code in {"unsupported_evidence", "ambiguous_entity"} and any(
                        blocker.code == issue.code for blocker in blockers):
                    continue
                blockers.append(ReviewBlocker(code=issue.code, category="dependency", message=issue.message,
                    next_step="Inspect the linked clauses and resolve the documented conflict or missing dependency."))
        missing_facts = rule.kind in ("obligation", "benefit") and (rule.amount_cents is None or rule.due_date is None)
        if rule.kind in ("obligation", "benefit"):
            for field, value in [("amount", rule.amount_cents), ("date", rule.due_date)]:
                if value is None:
                    blockers.append(ReviewBlocker(code=f"missing_{field}", category="fact",
                        message=f"The source-backed {field} is unresolved.",
                        next_step=f"Check the original source for an explicit {field}; leave it unknown if the source does not provide one."))
        if (rule.kind == "obligation" and rule.review_status != ReviewStatus.rejected and
                rule.id not in represented and rule.id not in superseded and
                (rule.due_date is None or rule.due_date >= scenario.start_date)):
            blockers.append(ReviewBlocker(code="unrepresented_obligation", category="fact",
                message="This obligation is not represented by a recorded ledger event.",
                next_step="Review its source and recorded intake; do not treat missing obligations as zero cost."))
        action_ids = [aid for aid, sources in affected.items() if rule.id in sources]
        priority = 0 if rule.id in essential or (rule.kind == "obligation" and missing_facts) else 1 if action_ids else 2
        add("rule", rule.id, rule.title, priority, blockers, [rule.id], action_ids,
            [event.id for event in scenario.events if rule.id in event.source_rule_ids], missing=missing)

    queued_rules = {item.subject_id for item in items if item.subject_kind == "rule"}
    for action in sorted(scenario.actions, key=lambda item: item.id):
        blockers = []
        missing = not action.source_rule_ids or any(rid not in indexed for rid in action.source_rule_ids)
        covered = bool(affected[action.id] & queued_rules)
        if missing:
            blockers.append(ReviewBlocker(code="missing_source", category="evidence",
                message="Action lacks a known source rule.", next_step="Provide the missing source and review its rule before using this action."))
        if action.review_status != ReviewStatus.reviewed and not covered:
            blockers.append(ReviewBlocker(code="review_rejected" if action.review_status == ReviewStatus.rejected else "human_review",
                category="review", message="Action requires human review.",
                next_step="Review the action's source rules; do not approve an action without supported sources."))
        requires_approval = action.kind in ("shift", "claim", "request") or any(effect.operation == "shift" for effect in action.effects)
        reason, _ = _approval_gate(action.id, action.approval_status, PlanRequest(), required=requires_approval and not any(
            indexed[rid].approval_status == ApprovalStatus.approved for rid in action.source_rule_ids if rid in indexed))
        approval_code = "approval_denied" if action.approval_status == ApprovalStatus.denied else "approval_pending"
        source_approval = any(blocker.code == approval_code for rid in action.source_rule_ids
            for blocker in recorded_blockers.get(rid, []))
        if reason and not source_approval:
            denied = action.approval_status == ApprovalStatus.denied
            blockers.append(ReviewBlocker(code="approval_denied" if denied else "approval_pending", category="approval",
                message=reason, next_step="Keep the recorded denial unless the relevant party issues a new decision."
                if denied else "Wait for the required third-party decision and record its source; review alone does not grant approval."))
        evidence_reason = action_evidence_blocker(action, rules, scenario.events) if not missing else None
        if evidence_reason and not covered:
            blockers.append(ReviewBlocker(code="action_evidence", category="evidence", message=evidence_reason,
                next_step="Check the action's exact amounts, dates and event links against its original source."))
        if action.id in excluded and not blockers and not covered:
            blockers.append(ReviewBlocker(code="action_gate", category="authorization", message=excluded[action.id],
                next_step="Inspect the action's sources and prerequisites before using it."))
        add("action", action.id, action.title, 1, blockers, action.source_rule_ids, [action.id],
            [effect.target_event_id for effect in action.effects if effect.target_event_id], missing=missing)

    for event in sorted(scenario.events, key=lambda item: item.id):
        # Unsourced user intake and actual transactions are permitted by the engine.
        if event.kind != "projected" or not event.source_rule_ids:
            continue
        missing = any(rid not in indexed for rid in event.source_rule_ids)
        reason = event_evidence_blocker(event, rules)
        if reason:
            add("event", event.id, event.title, 0 if event.essential or event.service_id in scenario.essential_service_ids else 2,
                [ReviewBlocker(code="missing_source" if missing else "event_evidence", category="evidence", message=reason,
                    next_step="Provide the missing original source and review the recorded obligation." if missing else
                    "Check the recorded event's direction, amount and date against its source; do not silently remove expenses.")],
                event.source_rule_ids, [action.id for action in scenario.actions if any(
                    effect.target_event_id == event.id for effect in action.effects)], [event.id], missing=missing)
    return ReviewQueue(revision=workspace.revision, items=sorted(items, key=lambda item: (item.priority, item.id)))
