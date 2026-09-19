"""Review guidance exposes existing gates without changing money or approvals."""
from datetime import date

import pytest

from clausegraph.demo import load_demo
from clausegraph.engine import optimize
from clausegraph.extraction import rule_blocker, rule_blockers
from clausegraph.review import review_queue
from clausegraph.schemas import PlanRequest, Workspace


def workspace():
    scenario, documents, rules = load_demo()
    from clausegraph.graph import build_graph
    return Workspace(session_id="review-unit", mode="synthetic", revision=7, scenario=scenario,
                     documents=documents, rules=rules, graph=build_graph(scenario, rules, documents))


def rule(data, identifier):
    return next(item for item in data.rules if item.id == identifier)


def item(data, identifier):
    return next(entry for entry in review_queue(data).items if entry.subject_id == identifier)


def codes(entry):
    return {blocker.code for blocker in entry.blockers}


def test_synthetic_assistance_lists_separate_reasons_without_estimated_benefit():
    data = workspace()
    before = data.model_dump(mode="json")
    result = review_queue(data)
    assert result.revision == 7
    assert [entry.subject_id for entry in result.items] == ["rule-assistance"]
    assistance = result.items[0]
    assert {"human_review", "condition_unresolved", "approval_pending", "missing_date"} <= codes(assistance)
    assert assistance.action_ids == ["claim-assistance"]
    assert assistance.priority == 1 and assistance.disposition == "needs_review"
    assert assistance.evidence and not assistance.missing_source
    assert data.model_dump(mode="json") == before
    plan = optimize(data.scenario, data.rules, PlanRequest())
    assert plan.proposed.minimum_balance_cents == 5000
    assert plan.proposed.ending_balance_cents == 50000


def test_essential_obligations_first_then_actions_with_stable_ties():
    data = workspace()
    for identifier in ["rule-rent", "rule-phone", "rule-groceries"]:
        rule(data, identifier).review_status = "pending"
    result = review_queue(data)
    assert [entry.subject_id for entry in result.items[:2]] == ["rule-groceries", "rule-rent"]
    assert all(entry.priority == 0 for entry in result.items[:2])
    reversed_data = data.model_copy(deep=True)
    reversed_data.rules.reverse()
    reversed_data.scenario.actions.reverse()
    reversed_data.scenario.events.reverse()
    assert review_queue(reversed_data) == result


def test_missing_obligation_amount_and_date_are_critical_without_inventing_values():
    data = workspace()
    source = rule(data, "rule-loan")
    source.amount_cents = None
    source.due_date = None
    entry = item(data, source.id)
    assert entry.priority == 0
    assert {"missing_amount", "missing_date"} <= codes(entry)
    assert source.amount_cents is None and source.due_date is None
    assert data.scenario.events[2].amount_cents == 45000


@pytest.mark.parametrize("approval,disposition,code", [
    ("pending", "waiting", "approval_pending"), ("denied", "blocked", "approval_denied"),
])
def test_recorded_approval_is_not_changed_by_guidance_or_nominal_assumptions(approval, disposition, code):
    data = workspace()
    source = rule(data, "rule-shift")
    source.approval_status = approval
    data.scenario.actions[0].approval_status = approval
    data.plan = optimize(data.scenario, data.rules,
                         PlanRequest(approval_overrides={"rule-shift": "approved", "shift-payment": "approved"},
                                     include_conditional=True))
    entry = item(data, "rule-shift")
    assert entry.disposition == disposition and code in codes(entry)
    assert source.approval_status == approval
    assert data.scenario.actions[0].approval_status == approval


def test_all_rule_blockers_keep_legacy_first_message_and_approval_option():
    data = workspace()
    source = rule(data, "rule-assistance")
    source.evidence_status = "disputed"
    source.entity_ambiguous = True
    source.conditions[0].resolved = True
    source.conditions[0].satisfied = False
    source.approval_status = "denied"
    blockers = rule_blockers(source)
    assert {entry.category for entry in blockers} == {"review", "evidence", "condition", "approval"}
    assert rule_blocker(source) == "Assistance eligibility unconfirmed requires human review."
    assert "approval_denied" not in {entry.code for entry in rule_blockers(source, check_approval=False)}
    assert item(data, source.id).disposition == "blocked"


@pytest.mark.parametrize("missing", ["document", "version", "evidence"])
def test_unavailable_source_never_looks_verified(missing):
    data = workspace()
    source = rule(data, "rule-rent")
    if missing == "document":
        data.documents = [document for document in data.documents if document.id != "doc-1"]
    elif missing == "version":
        source.evidence[0].version = 99
    else:
        source.evidence = []
    entry = item(data, "rule-rent")
    assert entry.missing_source and not entry.evidence
    assert "missing_source" in codes(entry)


def test_source_deleted_from_retained_expense_is_an_event_task():
    data = workspace()
    data.rules = [source for source in data.rules if source.id != "rule-rent"]
    data.documents = [document for document in data.documents if document.id != "doc-1"]
    entry = item(data, "rent")
    assert entry.subject_kind == "event" and entry.priority == 0
    assert entry.rule_ids == [] and entry.evidence == [] and entry.missing_source
    assert entry.event_ids == ["rent"]
    assert data.scenario.events[0].amount_cents == 160000


def test_dependencies_point_to_the_actual_prerequisite_rule():
    data = workspace()
    rule(data, "rule-loan").review_status = "pending"
    entry = item(data, "rule-loan")
    assert "shift-payment" in entry.action_ids
    assert entry.rule_ids == ["rule-loan"]


def test_cycles_remain_reviewable_without_traversal_loop():
    data = workspace()
    rule(data, "rule-loan").dependencies = ["rule-shift"]
    assert "rule_cycle" in codes(item(data, "rule-loan"))
    assert "rule_cycle" in codes(item(data, "rule-shift"))


def test_action_with_missing_rule_is_not_hidden():
    data = workspace()
    data.scenario.actions[0].source_rule_ids = ["absent"]
    entry = item(data, "shift-payment")
    assert entry.subject_kind == "action" and entry.missing_source
    assert "missing_source" in codes(entry)


def test_unrepresented_obligation_is_not_silently_zero():
    data = workspace()
    data.scenario.events = [event for event in data.scenario.events if event.id != "rent"]
    assert "unrepresented_obligation" in codes(item(data, "rule-rent"))


def test_direct_action_approval_gate_is_visible_when_sources_are_reviewed():
    data = workspace()
    data.scenario.actions[0].approval_status = "denied"
    entry = item(data, "shift-payment")
    assert "approval_denied" in codes(entry)
    assert entry.disposition == "blocked"


def test_action_denial_is_not_hidden_by_a_source_pending_decision():
    data = workspace()
    rule(data, "rule-shift").approval_status = "pending"
    data.scenario.actions[0].approval_status = "denied"
    assert item(data, "rule-shift").disposition == "waiting"
    action = item(data, "shift-payment")
    assert action.disposition == "blocked" and "approval_denied" in codes(action)


@pytest.mark.parametrize("field,value,code", [
    ("evidence_status", "unsupported", "unsupported_evidence"),
    ("entity_ambiguous", True, "ambiguous_entity"),
])
def test_evidence_issues_are_not_duplicated_as_dependency_failures(field, value, code):
    data = workspace()
    setattr(rule(data, "rule-rent"), field, value)
    blockers = [blocker for blocker in item(data, "rule-rent").blockers if blocker.code == code]
    assert len(blockers) == 1 and blockers[0].category == "evidence"


def test_valid_unsourced_intake_and_actual_transactions_are_not_fabricated_blockers():
    data = workspace()
    data.rules = []
    data.documents = []
    data.scenario.actions = []
    for event in data.scenario.events:
        event.source_rule_ids = []
    data.scenario.events[0].kind = "actual"
    data.scenario.events[0].date = date(2026, 8, 31)
    assert review_queue(data).items == []
