"""Oracles and label discipline for the bounded hypothetical-cash diagnostic.

A reported amount must be a verified diagnostic for one fixed schedule, never
funding, and never a repair for authorization or evidence failures.
"""
from datetime import timedelta

import pytest

from clausegraph.cash_gap import diagnose_cash_gap
from clausegraph.demo import START, load_demo
from clausegraph.engine import optimize
from clausegraph.schemas import (
    ApprovalUncertainty, CashGapRequest, FinancialEvent, IncomeDateUncertainty, Scenario,
)


def diagnose(data, rules, plan, dimensions=(), **kwargs):
    return diagnose_cash_gap(data, rules, plan, CashGapRequest(
        plan_id=plan.id, revision=plan.revision, uncertainties=list(dimensions), **kwargs,
    ))


def paydays(first=20, last=27, identifier="paycheck"):
    return IncomeDateUncertainty(id="payday", event_id=identifier, earliest=START + timedelta(days=first),
                                 latest=START + timedelta(days=last), rationale="User-declared delay window.")


def small_ledger(opening, bills, pay_cents=1000, horizon=5):
    """A tiny hand-checkable ledger with no rules, actions or approvals."""
    return Scenario(id="cash-gap-oracle", title="Synthetic cash-gap oracle", start_date=START,
                    horizon_days=horizon, opening_balance_cents=opening, actions=[], events=[
                        FinancialEvent(id=f"bill-{day}", title="Essential bill", date=START + timedelta(days=day),
                                       direction="expense", amount_cents=amount, essential=True)
                        for day, amount in bills
                    ] + [FinancialEvent(id="pay", title="User-entered pay", date=START + timedelta(days=2),
                                        direction="income", amount_cents=pay_cents)])


def oracle_buffer(opening, bills, pay_cents, horizon, first, last):
    """Brute-force the true minimum buffer over the declared payday product."""
    worst = None
    for payday in range(first, last + 1):
        balance = opening
        lowest = balance
        for day in range(horizon):
            balance += (pay_cents if day == payday else 0)
            balance -= sum(value for due, value in bills if due == day)
            lowest = min(lowest, balance)
        worst = lowest if worst is None else min(worst, lowest)
    return max(0, -worst)


def test_eight_date_synthetic_proves_the_forty_thousand_cent_buffer():
    scenario, _, rules = load_demo()
    plan = optimize(scenario, rules)
    result = diagnose(scenario, rules, plan, [paydays()])
    assert result.status == "PROVEN_MINIMUM"
    assert result.additional_opening_cash_cents == 40000
    assert result.minimality_proven is True
    assert result.baseline.status == "UNSAFE"
    # The same fixed schedule, not a re-optimized one.
    assert result.funded is not None and result.funded.status == "SAFE"
    assert [item.action_id for item in result.funded.fixed_actions] == [item.action_id for item in plan.actions]
    assert [item.execution_date for item in result.funded.fixed_actions] == [item.execution_date for item in plan.actions]
    # One cent less must actually fail before minimality is claimed.
    assert result.minimality_witness is not None
    assert result.minimality_witness.tested_additional_cents == 39999
    assert result.minimality_witness.status == "UNSAFE"
    # The limiting date, events and rules are linked for review.
    assert result.limiting_date == START + timedelta(days=25)
    assert "loan" in result.limiting_event_ids
    assert "rule-loan" in result.limiting_rule_ids


def test_amount_is_labeled_a_diagnostic_and_never_funding():
    scenario, _, rules = load_demo()
    plan = optimize(scenario, rules)
    result = diagnose(scenario, rules, plan, [paydays()])
    assert result.is_funding is False
    assert any("not funding" in warning for warning in result.warnings)
    # Nothing in the saved plan or scenario moved.
    assert scenario.opening_balance_cents == 200000
    assert plan.assumptions.opening_balance_cents is None


def test_future_obligations_stay_visible_in_the_funded_check():
    scenario, _, rules = load_demo()
    plan = optimize(scenario, rules)
    result = diagnose(scenario, rules, plan, [paydays()])
    assert result.funded is not None and result.funded.worst_case is not None
    # The device principal is beyond the horizon and must not be dropped.
    assert any(event.id == "device" for event in result.funded.worst_case.beyond_horizon)
    assert any("timing changes, not savings" in warning for warning in result.warnings)


@pytest.mark.parametrize("opening, bills, pay_cents", [
    (100, [(1, 400), (3, 200)], 1000),
    (0, [(0, 50), (2, 50), (4, 50)], 10),
    (500, [(4, 900)], 100),
    (250, [(1, 100), (2, 100), (3, 100)], 250),
])
def test_independent_small_ledger_oracle(opening, bills, pay_cents):
    data = small_ledger(opening, bills, pay_cents)
    plan = optimize(data, [])
    result = diagnose(data, [], plan, [paydays(first=0, last=4, identifier="pay")])
    expected = oracle_buffer(opening, bills, pay_cents, 5, 0, 4)
    if expected == 0:
        assert result.status == "NOT_REQUIRED"
        assert result.additional_opening_cash_cents == 0
    else:
        assert result.status == "PROVEN_MINIMUM"
        assert result.additional_opening_cash_cents == expected
        assert result.minimality_proven is True
        assert result.funded is not None and result.funded.status == "SAFE"


def test_zero_gap_case_requires_nothing():
    data = small_ledger(100000, [(1, 100)], pay_cents=1000)
    plan = optimize(data, [])
    result = diagnose(data, [], plan, [paydays(first=0, last=4, identifier="pay")])
    assert result.status == "NOT_REQUIRED"
    assert result.additional_opening_cash_cents == 0
    assert result.lower_bound_cents == 0
    assert result.baseline.status == "SAFE"
    assert result.funded is None


def test_case_cutoff_never_becomes_an_exact_minimum():
    scenario, _, rules = load_demo()
    plan = optimize(scenario, rules)
    result = diagnose(scenario, rules, plan, [paydays()], max_cases=2)
    assert result.baseline.coverage_complete is False
    assert result.status == "INCONCLUSIVE"
    assert result.additional_opening_cash_cents is None
    assert result.minimality_proven is False
    # A checked case still establishes a floor, which is not a minimum.
    assert result.lower_bound_cents is None or result.lower_bound_cents > 0


def test_time_cutoff_never_becomes_an_exact_minimum():
    scenario, _, rules = load_demo()
    plan = optimize(scenario, rules)
    result = diagnose(scenario, rules, plan, [paydays()], time_limit_seconds=0.001)
    assert result.status in ("INCONCLUSIVE", "NOT_REPAIRABLE_WITH_CASH")
    assert result.additional_opening_cash_cents is None
    assert result.minimality_proven is False


def test_denied_approval_is_never_repaired_by_cash():
    scenario, _, rules = load_demo()
    plan = optimize(scenario, rules)
    decision = ApprovalUncertainty(id="decision", target_id="shift-payment",
                                   outcomes=["approved", "denied", "pending"],
                                   rationale="Hypothetical third-party decision outcomes.")
    result = diagnose(scenario, rules, plan, [decision])
    assert result.status == "NOT_REPAIRABLE_WITH_CASH"
    assert result.additional_opening_cash_cents is None
    assert result.minimality_proven is False
    assert "authorization" in result.blocking_properties


def test_unresolved_evidence_is_never_repaired_by_cash():
    scenario, _, rules = load_demo()
    plan = optimize(scenario, rules)
    pending = [rule.model_copy(deep=True) for rule in rules]
    for rule in pending:
        if rule.id == "rule-loan":
            rule.evidence_status = "unsupported"
    result = diagnose(scenario, pending, plan, [paydays()])
    assert result.status != "PROVEN_MINIMUM"
    assert result.additional_opening_cash_cents is None
    assert result.minimality_proven is False
    assert result.baseline.status != "SAFE"


def test_inputs_are_never_mutated():
    scenario, _, rules = load_demo()
    plan = optimize(scenario, rules)
    before = (scenario.model_dump(mode="json"), [rule.model_dump(mode="json") for rule in rules],
              plan.model_dump(mode="json"))
    diagnose(scenario, rules, plan, [paydays()])
    assert scenario.model_dump(mode="json") == before[0]
    assert [rule.model_dump(mode="json") for rule in rules] == before[1]
    assert plan.model_dump(mode="json") == before[2]
