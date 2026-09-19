from datetime import timedelta
from hashlib import sha256
from pathlib import Path

import pytest
from pydantic import ValidationError

from clausegraph.demo import START, load_demo
from clausegraph.schemas import FinancialEvent, PlanRequest


def test_six_synthetic_documents_have_exact_evidence():
    scenario, documents, rules = load_demo()
    assert len(documents) == 6
    by_id = {doc.id: doc for doc in documents}
    for doc in documents:
        assert doc.synthetic and len(doc.sha256) == 64
        path = Path(__file__).resolve().parents[2] / "fixtures" / doc.name
        assert doc.sha256 == sha256(path.read_bytes()).hexdigest()
    for rule in rules:
        for source in rule.evidence:
            page = by_id[source.document_id].pages[source.page - 1]
            assert page.text[source.char_start:source.char_end] == source.quote
    assert scenario.opening_balance_cents == 200000
    assert sum(e.amount_cents for e in scenario.events if e.direction == "expense" and e.date < START + timedelta(days=20)) == 240000


@pytest.mark.parametrize("amount", [1.5, True, "2000", -1])
def test_money_contract_rejects_non_integer_cents(amount):
    with pytest.raises(ValidationError):
        FinancialEvent(id="x", title="x", date=START, amount_cents=amount, direction="expense")


def test_horizon_bounds_are_explicit():
    with pytest.raises(ValidationError):
        PlanRequest(horizon_days=0)
    with pytest.raises(ValidationError):
        PlanRequest(horizon_days=367)


def test_complete_demo_acceptance():
    from clausegraph.engine import optimize, simulate
    scenario, _, rules = load_demo()
    baseline = simulate(scenario)
    assert baseline.minimum_balance_cents == -40000
    assert baseline.ending_balance_cents == 50000
    assert baseline.first_shortfall_date == START + timedelta(days=12)
    assert baseline.additional_cash_required_cents == 40000
    assert [event.id for event in baseline.beyond_horizon] == ["device"]
    plan = optimize(scenario, rules)
    assert plan.proposed.minimum_balance_cents == 5000
    assert plan.proposed.ending_balance_cents == 50000
    assert [action.action_id for action in plan.actions] == ["shift-payment"]
    assert plan.state == "confirmed"
    assert plan.objective_proven
    assert len(plan.decision_traces) == 1
    trace = plan.decision_traces[0]
    assert trace.action_id == "shift-payment"
    assert trace.source_rule_ids == ["rule-shift", "rule-loan"]
    assert trace.source_document_ids == ["doc-3"]
    assert len(trace.changes) == 1
    assert trace.changes[0].operation == "shift"
    assert trace.changes[0].before.date == START + timedelta(days=12)
    assert trace.changes[0].after.date == START + timedelta(days=25)
    assert trace.changes[0].before.amount_cents == trace.changes[0].after.amount_cents == 45000
    scenario.actions[0].approval_status = "denied"
    rules[5].approval_status = "denied"
    denied = optimize(scenario, rules)
    assert denied.proposed.minimum_balance_cents == -40000
    assert denied.state == "infeasible"
    assert "claim-assistance" in denied.excluded_actions


def test_cancelling_phone_relocates_device_debt_once():
    from clausegraph.engine import simulate
    scenario, _, _ = load_demo()
    result = simulate(scenario, {"cancel-phone": START + timedelta(days=3)})
    assert result.minimum_balance_cents == -82000
    assert result.ending_balance_cents == 8000
    assert not result.beyond_horizon
    assert sum(day.expense_cents for day in result.daily) == 282000


def test_forced_cancellation_trace_exposes_removed_service_and_accelerated_debt():
    from clausegraph.engine import optimize
    scenario, _, rules = load_demo()
    request = PlanRequest(force_action_ids=["cancel-phone"],
        exclude_action_ids=["shift-payment", "claim-assistance"])
    plan = optimize(scenario, rules, request)
    assert plan.proposed.minimum_balance_cents == -82000
    assert plan.proposed.ending_balance_cents == 8000
    assert [trace.action_id for trace in plan.decision_traces] == ["cancel-phone"]
    remove, accelerate = plan.decision_traces[0].changes
    assert remove.operation == "remove" and remove.before.id == "phone" and remove.after is None
    assert accelerate.operation == "accelerate" and accelerate.before.id == "device"
    assert accelerate.after.date == plan.actions[0].execution_date
