"""Finite oracles and safety regressions for the fixed-plan verifier."""
from datetime import timedelta
from itertools import product
from random import Random

import pytest

from clausegraph import verification
from clausegraph.demo import START, load_demo
from clausegraph.engine import optimize, simulate
from clausegraph.schemas import (
    Action, ApprovalUncertainty, Effect, Evidence, FinancialEvent,
    IncomeAmountUncertainty, IncomeDateUncertainty, PlanRequest, PlannedAction,
    Rule, Scenario, VerificationRequest, VerificationResult,
)
from clausegraph.verification import verify_plan


def verify(data, rules, plan, dimensions=(), **kwargs):
    return verify_plan(data, rules, plan, VerificationRequest(
        plan_id=plan.id, revision=plan.revision, uncertainties=list(dimensions), **kwargs,
    ))


def dates(first=20, last=27, identifier="paycheck"):
    return IncomeDateUncertainty(id="payday", event_id=identifier, earliest=START + timedelta(days=first),
                                 latest=START + timedelta(days=last), rationale="User-declared delay window.")


def amounts(low=90000, high=90002, identifier="paycheck"):
    return IncomeAmountUncertainty(id="amount", event_id=identifier, minimum_cents=low,
                                   maximum_cents=high, rationale="User-declared pay amount range.")


def approval(target="shift-payment", outcomes=("approved", "denied", "pending")):
    return ApprovalUncertainty(id="decision", target_id=target, outcomes=list(outcomes),
                               rationale="Hypothetical third-party decision outcomes.")


def test_safe_full_date_amount_range_and_input_immutability():
    data, _, rules = load_demo()
    plan = optimize(data, rules)
    before = data.model_dump_json(), [r.model_dump_json() for r in rules], plan.model_dump_json()
    result = verify(data, rules, plan, [dates(last=25), amounts()])
    assert result.status == "SAFE" and result.solver_status == "EXHAUSTED"
    assert result.checked_cases == result.total_cases == 18
    assert result.coverage_complete and result.worst_case_proven
    assert result.worst_case.minimum_balance_cents == 5000
    assert result.horizon_start == START and result.horizon_end_exclusive == START + timedelta(days=60)
    assert "only" in result.statement
    assert before == (data.model_dump_json(), [r.model_dump_json() for r in rules], plan.model_dump_json())
    assert VerificationResult.model_validate_json(result.model_dump_json()) == result


def test_unsafe_delay_exact_earliest_counterexample_and_source_trace():
    data, _, rules = load_demo()
    plan = optimize(data, rules)
    result = verify(data, rules, plan, [dates()])
    assert plan.proposed.minimum_balance_cents == 5000
    assert result.status == "UNSAFE" and result.checked_cases == 8
    assert result.counterexample.assignment[0].value == "2026-09-27"
    assert result.counterexample.earliest_failing_date == START + timedelta(days=25)
    assert result.counterexample.balance_cents == -40000
    assert result.worst_case.minimum_balance_cents == -40000 and result.worst_case_proven
    changed = next(item for item in result.counterexample.events if item.event.id == "loan")
    assert changed.action_ids == ["shift-payment"]
    assert changed.event.source_rule_ids == ["rule-loan"]
    assert result.fixed_actions == plan.actions
    assert result.counterexample.simulation.beyond_horizon[0].id == "device"


@pytest.mark.parametrize("outcome", ["denied", "pending"])
@pytest.mark.parametrize("target", ["shift-payment", "rule-shift"])
def test_nonapproved_outcome_is_unauthorized_not_a_cash_simulation(target, outcome):
    data, _, rules = load_demo()
    plan = optimize(data, rules)
    result = verify(data, rules, plan, [approval(target, [outcome])])
    assert result.status == "UNSAFE"
    assert result.counterexample.simulation is None and result.counterexample.balance_cents is None
    assert result.counterexample.earliest_failing_date == plan.actions[0].execution_date
    assert result.counterexample.failures[0].property == "authorization"
    assert result.worst_case is None and not result.worst_case_proven
    assert data.actions[0].approval_status == rules[5].approval_status == "approved"


def test_conditional_nominal_approval_is_not_automatically_verified():
    data, _, rules = load_demo()
    data.actions[0].approval_status = "pending"
    rules[5].approval_status = "pending"
    plan = optimize(data, rules, PlanRequest(include_conditional=True))
    assert plan.state == "conditional"
    assert verify(data, rules, plan).status == "UNSAFE"
    first = approval("shift-payment", ["approved"])
    second = approval("rule-shift", ["approved"])
    second.id = "rule-decision"
    assert verify(data, rules, plan, [first, second]).status == "SAFE"
    assert data.actions[0].approval_status == rules[5].approval_status == "pending"


def test_explicit_nominal_approval_assumptions_are_retained_and_labeled():
    data, _, rules = load_demo()
    data.actions[0].approval_status = "pending"
    plan = optimize(data, rules, PlanRequest(include_conditional=True, approval_overrides={"shift-payment": "approved"}))
    result = verify(data, rules, plan)
    assert result.status == "SAFE"
    assert result.nominal_assumptions.approval_overrides == {"shift-payment": "approved"}
    assert any("hypothetical" in warning for warning in result.warnings)
    assert verify(data, rules, plan, [approval(outcomes=["pending"])]).status == "UNSAFE"


def test_timeout_without_proof_is_unknown(monkeypatch):
    data, _, rules = load_demo()
    plan = optimize(data, rules)
    ticks = iter([0.0, 6.0, 6.1])
    monkeypatch.setattr(verification.time, "monotonic", lambda: next(ticks))
    result = verify(data, rules, plan, [dates(last=25)])
    assert result.status == "UNKNOWN" and result.solver_status == "TIME_LIMIT"
    assert result.checked_cases == 0 and not result.coverage_complete and not result.worst_case_proven


def test_timeout_after_concrete_failure_retains_the_unsafe_witness(monkeypatch):
    data, _, rules = load_demo()
    plan = optimize(data, rules)
    ticks = iter([0.0, 0.0, 6.0, 6.1])
    monkeypatch.setattr(verification.time, "monotonic", lambda: next(ticks))
    result = verify(data, rules, plan, [dates(first=26, last=27)])
    assert result.status == "UNSAFE" and result.solver_status == "TIME_LIMIT"
    assert result.checked_cases == 1 and result.counterexample.balance_cents == -40000
    assert not result.coverage_complete and not result.worst_case_proven


def test_case_limit_never_turns_a_safe_sample_into_a_proof():
    data, _, rules = load_demo()
    plan = optimize(data, rules)
    result = verify(data, rules, plan, [dates()], max_cases=1)
    assert result.status == "UNKNOWN" and result.solver_status == "CASE_LIMIT"
    assert result.worst_case.minimum_balance_cents == 5000
    assert not result.worst_case_proven and not result.coverage_complete


def test_concrete_failure_remains_unsafe_when_case_limit_interrupts_search():
    data, _, rules = load_demo()
    plan = optimize(data, rules)
    result = verify(data, rules, plan, [dates(first=26, last=29)], max_cases=1)
    assert result.status == "UNSAFE" and result.solver_status == "CASE_LIMIT"
    assert result.counterexample.balance_cents == -40000
    assert not result.worst_case_proven


def test_huge_integer_domain_is_counted_without_eager_allocation():
    data, _, rules = load_demo()
    plan = optimize(data, rules)
    result = verify(data, rules, plan, [amounts(low=0, high=10_000_000_000)], max_cases=1)
    assert result.total_cases == 10_000_000_001 and result.checked_cases == 1
    assert result.status == "UNSAFE" and result.solver_status == "CASE_LIMIT"


@pytest.mark.parametrize("seed", range(10))
def test_all_integer_amounts_and_dates_match_independent_small_ledger_oracle(seed):
    random = Random(seed)
    opening = random.randrange(1, 10)
    bills = [(1, random.randrange(1, 10)), (3, random.randrange(1, 10))]
    data = Scenario(id="finite", title="Synthetic exact oracle", start_date=START, horizon_days=5,
                    opening_balance_cents=opening, actions=[], events=[
                        FinancialEvent(id=f"bill-{day}", title="Essential bill", date=START + timedelta(days=day),
                                       direction="expense", amount_cents=amount, essential=True)
                        for day, amount in bills
                    ] + [FinancialEvent(id="pay", title="User-entered pay", date=START + timedelta(days=2),
                                        direction="income", amount_cents=10)])
    plan = optimize(data, [])
    result = verify(data, [], plan, [dates(first=0, last=5, identifier="pay"), amounts(8, 11, "pay")])
    candidates = []
    for amount, payday in product(range(8, 12), range(6)):
        balance, rows, first = opening, [], None
        for day in range(5):
            balance += (amount if day == payday else 0) - sum(value for due, value in bills if due == day)
            rows.append(balance)
            if balance < 0 and first is None:
                first = START + timedelta(days=day)
        candidates.append((min(rows), first, amount, payday))
    assert result.checked_cases == result.total_cases == len(candidates) == 24
    assert result.worst_case.minimum_balance_cents == min(item[0] for item in candidates)
    assert result.worst_case_proven
    assert result.status == ("SAFE" if all(item[0] >= 0 for item in candidates) else "UNSAFE")
    if result.counterexample:
        assert result.counterexample.earliest_failing_date == min(item[1] for item in candidates if item[1])
        # Amount is the first dimension in deterministic enumeration. Ties retain
        # the smallest amount/date assignment that reaches the earliest failure.
        first = next(item for item in candidates if item[1] == result.counterexample.earliest_failing_date)
        assert [item.value for item in result.counterexample.assignment] == [first[2], (START + timedelta(days=first[3])).isoformat()]


def test_horizon_end_income_is_retained_but_not_counted_early():
    data, _, rules = load_demo()
    plan = optimize(data, rules, PlanRequest(horizon_days=26))
    result = verify(data, rules, plan, [dates(first=25, last=26)])
    assert result.status == "UNSAFE"
    assert result.worst_case.beyond_horizon[0].id == "paycheck"
    assert result.worst_case.ending_balance_cents == -40000
    assert verify(data, rules, plan, [dates(first=25, last=25)]).status == "SAFE"


@pytest.mark.parametrize("mutation", ["missing", "review", "amount", "unrepresented"])
def test_unresolved_ledger_cannot_be_safe(mutation):
    data, _, rules = load_demo()
    plan = optimize(data, rules)
    if mutation == "missing":
        rules = [rule for rule in rules if rule.id != "rule-rent"]
    elif mutation == "review":
        rules[0].review_status = "pending"
    elif mutation == "amount":
        data.events[0].amount_cents = 0
    else:
        data.events = [event for event in data.events if event.id != "rent"]
    result = verify(data, rules, plan)
    assert result.status == "UNKNOWN"
    assert not result.worst_case_proven and result.worst_case is None


def test_acceleration_moves_principal_once_and_preserves_future_debt():
    data, _, rules = load_demo()
    plan = optimize(data, rules, PlanRequest(force_action_ids=["cancel-phone"], exclude_action_ids=["shift-payment"]))
    result = verify(data, rules, plan, [dates(first=20, last=21)])
    assert result.status == "UNSAFE"
    assert result.worst_case.minimum_balance_cents == -82000 and result.worst_case.ending_balance_cents == 8000
    device = [item.event for item in result.counterexample.events if item.event.id == "device"]
    assert len(device) == 1 and device[0].amount_cents == 48000
    assert not any(item.id == "device" for item in result.counterexample.simulation.beyond_horizon)
    assert not any(item.event.id == "phone" for item in result.counterexample.events)


def test_fixed_schedule_does_not_reoptimize_even_when_alternative_is_safe():
    data, _, rules = load_demo()
    plan = optimize(data, rules, PlanRequest(exclude_action_ids=["shift-payment"]))
    assert not plan.actions and plan.proposed.minimum_balance_cents == -40000
    result = verify(data, rules, plan, [dates(first=20, last=20)])
    assert result.status == "UNSAFE" and result.fixed_actions == []
    assert optimize(data, rules).proposed.minimum_balance_cents == 5000


def test_essential_removal_is_invalid_even_when_cash_would_improve():
    quote = "Synthetic: you may cancel the 150 cents payment on 2026-09-02."
    rule = Rule(id="r", title="Cancellation", kind="option", review_status="reviewed", evidence_status="supported",
                evidence=[Evidence(document_id="doc", page=1, char_start=0, char_end=len(quote), quote=quote)])
    action = Action(id="cancel", title="Cancel bill", description="Synthetic action", kind="cancel", source_rule_ids=["r"],
                    earliest_date=START, latest_date=START, recommended_date=START, review_status="reviewed",
                    effects=[Effect(operation="remove", target_event_id="bill")])
    data = Scenario(id="essential", title="Synthetic essential", start_date=START, horizon_days=3, opening_balance_cents=100,
                    events=[FinancialEvent(id="bill", title="Essential", date=START + timedelta(days=1),
                                           direction="expense", amount_cents=150, essential=True)], actions=[action])
    plan = optimize(data, [rule])
    plan.actions = [PlannedAction(action_id="cancel", execution_date=START, order=1, explanation="Injected invalid plan", source_rule_ids=["r"])]
    result = verify(data, [rule], plan)
    assert result.status == "UNSAFE"
    assert result.counterexample.failures[0].property == "essential_services"
    assert result.counterexample.simulation is None
    assert simulate(data).minimum_balance_cents == -50


@pytest.mark.parametrize("mutation", ["missing_dependency", "late_date", "duplicate_action", "duplicate_debt"])
def test_fixed_schedule_validity_and_accounting_fail_closed(mutation):
    data, _, rules = load_demo()
    plan = optimize(data, rules)
    if mutation == "missing_dependency":
        data.actions[0].requires = ["cancel-phone"]
    elif mutation == "late_date":
        plan.actions[0].execution_date = START + timedelta(days=12)
    elif mutation == "duplicate_action":
        plan.actions.append(plan.actions[0].model_copy(deep=True))
    else:
        clone = data.events[0].model_copy(deep=True)
        clone.id = "duplicated-rent"
        data.events.append(clone)
    result = verify(data, rules, plan)
    assert result.status != "SAFE" and not result.worst_case_proven
    if mutation == "duplicate_action":
        assert result.solver_status == "INVALID_MODEL"


@pytest.mark.parametrize("kind", ["actual", "expense", "unknown", "before_start", "approval_unknown", "revision"])
def test_invalid_uncertainty_targets_are_explicit(kind):
    data, _, rules = load_demo()
    plan = optimize(data, rules)
    dimension = dates()
    if kind == "actual":
        next(event for event in data.events if event.id == "paycheck").kind = "actual"
    elif kind == "expense":
        dimension.event_id = "rent"
    elif kind == "unknown":
        dimension.event_id = "missing"
    elif kind == "before_start":
        dimension.earliest = START - timedelta(days=1)
    elif kind == "approval_unknown":
        dimension = approval("missing")
    else:
        request = VerificationRequest(plan_id=plan.id, revision=plan.revision + 1)
        with pytest.raises(ValueError, match="revision"):
            verify_plan(data, rules, plan, request)
        return
    with pytest.raises(ValueError):
        verify(data, rules, plan, [dimension])


def test_multiple_income_dimensions_only_override_their_declared_events():
    data, _, rules = load_demo()
    data.events.append(FinancialEvent(id="second-pay", title="Explicit intake", date=START + timedelta(days=2),
                                      direction="income", amount_cents=1))
    plan = optimize(data, rules)
    second = amounts(1, 3, "second-pay")
    result = verify(data, rules, plan, [dates(last=25), second])
    assert result.status == "SAFE" and result.total_cases == 18
    assert result.worst_case.minimum_balance_cents == 5001


@pytest.mark.parametrize("dimension_kind", ["amount", "date"])
@pytest.mark.parametrize("nominal", [False, True])
def test_income_assumption_does_not_excuse_an_unsupported_unchanged_field(dimension_kind, nominal):
    data, _, rules = load_demo()
    plan = optimize(data, rules)
    income = next(event for event in data.events if event.id == "paycheck")
    if dimension_kind == "amount":
        income.date += timedelta(days=1)
        dimension = amounts()
        if nominal:
            plan.assumptions.income_cents = 90001
    else:
        income.amount_cents += 1
        dimension = dates(last=25)
        if nominal:
            plan.assumptions.income_date = START + timedelta(days=21)
    result = verify(data, rules, plan, [] if nominal else [dimension])
    assert result.status == "UNKNOWN" and result.worst_case is None
    assert any("outside the declared assumptions" in warning for warning in result.warnings)


def test_source_income_direction_is_not_overridden_by_date_and_amount_assumptions():
    data, _, rules = load_demo()
    plan = optimize(data, rules)
    income = next(event for event in data.events if event.id == "paycheck")
    income.source_rule_ids = ["rule-rent"]
    result = verify(data, rules, plan, [dates(last=25), amounts()])
    assert result.status == "UNKNOWN" and result.worst_case is None


def test_unresolved_income_evidence_never_becomes_safe_by_withholding_it():
    data, _, rules = load_demo()
    plan = optimize(data, rules, PlanRequest(opening_balance_cents=400000))
    next(rule for rule in rules if rule.id == "rule-income").evidence_status = "unsupported"
    result = verify(data, rules, plan)
    assert result.status == "UNKNOWN" and not result.worst_case_proven
