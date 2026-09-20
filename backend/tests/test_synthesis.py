"""Bounded synthesis checked against a separate small integer-cash oracle."""
from datetime import date
from itertools import product

import pytest

from clausegraph import synthesis
from clausegraph.demo import load_demo
from clausegraph.engine import optimize
from clausegraph.resilient_demo import load_resilient_demo
from clausegraph.schemas import (
    ApprovalUncertainty, Condition, Effect, IncomeAmountUncertainty, IncomeDateUncertainty,
    PlanRequest, PlanResult, ScheduledAction, SynthesisAdoptRequest, SynthesisRequest,
)
from clausegraph.synthesis import CandidateUnavailable, revalidate_candidate, synthesize_plan


def setup(**assumptions):
    scenario, documents, rules = load_resilient_demo()
    source = optimize(scenario, rules, PlanRequest(**assumptions))
    bounds = [IncomeDateUncertainty(id="payday", event_id="resilient-paycheck", earliest="2026-09-03",
        latest="2026-09-05", rationale="Synthetic user assumption.")]
    return scenario, documents, rules, source, SynthesisRequest(plan_id=source.id, revision=source.revision, uncertainties=bounds)


def adoption(result):
    return SynthesisAdoptRequest(synthesis_request=result.assumptions,
        selected_actions=[ScheduledAction(action_id=a.action_id, execution_date=a.execution_date) for a in result.candidate.actions],
        candidate_fingerprint=result.candidate_fingerprint)


def test_separate_fixture_exact_sources_debt_fee_and_immutable_search(monkeypatch):
    s, docs, rules, plan, req = setup()
    before = s.model_dump_json(), [r.model_dump_json() for r in rules], plan.model_dump_json()
    import clausegraph.engine as engine
    monkeypatch.setattr(engine, "optimize", lambda *a, **k: pytest.fail("Search must never optimize per outcome"))
    for rule in rules:
        for evidence in rule.evidence:
            text = next(d for d in docs if d.id == evidence.document_id).pages[evidence.page - 1].text
            assert text[evidence.char_start:evidence.char_end] == evidence.quote
    result = synthesize_plan(s, rules, plan, req)
    assert result.status == "FOUND" and result.termination == "VERIFIED_CANDIDATE"
    assert [a.action_id for a in plan.actions] == ["early-shift"]
    assert [a.action_id for a in result.candidate.actions] == ["late-shift"]
    assert result.nominal_costs.total_action_fees_cents == 0
    assert result.candidate_costs.total_action_fees_cents == 100
    assert result.verification.status == "SAFE" and result.verification.coverage_complete
    assert result.verification.worst_case.minimum_balance_cents == result.candidate.proposed.minimum_balance_cents == 4900
    assert result.candidate.proposed.ending_balance_cents == 4900
    assert result.candidate.generation_mode == "resilient" and result.candidate.solver_status == "FIXED_VERIFIED"
    assert not result.candidate.objective_proven and result.candidate.solver_wall_time_seconds == 0
    assert (result.total_candidate_tuples, result.visited_candidate_tuples, result.refuted_candidate_tuples) == ("4", 2, 1)
    assert result.nominal_checks == 2 and result.uncertainty_checks == 3
    assert before == (s.model_dump_json(), [r.model_dump_json() for r in rules], plan.model_dump_json())
    saved = revalidate_candidate(s, rules, plan, adoption(result))
    assert saved.plan.id != result.candidate.id and saved.verification.plan_id == saved.plan.id
    assert saved.plan.actions == result.candidate.actions and saved.plan.proposed == result.candidate.proposed
    assert saved.plan.synthesis_provenance.fingerprint == result.candidate_fingerprint
    legacy = plan.model_dump(exclude={"generation_mode", "synthesis_provenance"})
    assert PlanResult.model_validate(legacy).generation_mode == "nominal"


@pytest.mark.parametrize("opening,minimum_income", list(product([0, 99, 100, 4999, 5000, 9999, 10000], [5000, 10000])))
def test_integer_oracle_matches_first_safe_tuple_or_exhaustive_refutation(opening, minimum_income):
    s, _, rules, plan, req = setup(opening_balance_cents=opening)
    req.uncertainties.append(IncomeAmountUncertainty(id="amount", event_id="resilient-paycheck",
        minimum_cents=minimum_income, maximum_cents=minimum_income + 2, rationale="Three exact cent values."))
    # Independent arithmetic, not engine/verifier helpers: enumerate the documented
    # tuple order, reject mutual exclusion, then apply one debt and its actual fee.
    expected = None
    for early, late in product([False, True], repeat=2):
        if early and late:
            continue
        due, fee = (5, 100) if late else (3, 0) if early else (2, 0)
        cases = [(3, 10000), *product(range(3, 6), range(minimum_income, minimum_income + 3))]
        safe = True
        for payday, income in cases:
            cash = opening
            for day in range(1, 8):
                cash += income if day == payday else 0
                cash -= 10000 if day == due else 0
                cash -= fee if day == 1 else 0
                safe &= cash >= 0
        if safe:
            expected = ["early-shift"] if early else ["late-shift"] if late else []
            break
    result = synthesize_plan(s, rules, plan, req)
    if expected is None:
        assert result.status == "NO_SOLUTION" and result.search_exhausted
        assert result.refuted_candidate_tuples == int(result.total_candidate_tuples)
    else:
        assert result.status == "FOUND"
        assert [a.action_id for a in result.candidate.actions] == expected


@pytest.mark.parametrize("kwargs,termination", [({"max_candidates": 1}, "CANDIDATE_LIMIT"),
    ({"max_case_checks": 1}, "CASE_LIMIT"), ({"max_case_checks": 4}, "CASE_LIMIT")])
def test_limits_never_imply_no_solution(kwargs, termination):
    s, _, rules, plan, req = setup()
    req = req.model_copy(update=kwargs)
    result = synthesize_plan(s, rules, plan, req)
    assert result.status == "INCONCLUSIVE" and result.termination == termination
    assert result.candidate is result.verification is None
    assert result.nominal_checks + result.uncertainty_checks <= req.max_case_checks


def test_last_budget_unit_success_and_empty_uncertainty():
    s, _, rules, plan, req = setup()
    req.max_case_checks = 5
    assert synthesize_plan(s, rules, plan, req).status == "FOUND"
    req.uncertainties = []
    req.max_case_checks = 3
    result = synthesize_plan(s, rules, plan, req)
    assert result.status == "FOUND" and result.uncertainty_checks == 1


def test_no_actions_zero_domain_and_forced_date_constraints():
    s, _, rules, plan, req = setup(force_action_ids=["early-shift"])
    assert synthesize_plan(s, rules, plan, req).status == "NO_SOLUTION"
    plan.assumptions.force_action_ids = ["late-shift"]
    result = synthesize_plan(s, rules, plan, req)
    assert result.status == "FOUND" and result.total_candidate_tuples == "2"
    s.actions[1].approval_status = "denied"
    result = synthesize_plan(s, rules, plan, req)
    assert result.status == "NO_SOLUTION" and result.total_candidate_tuples == "0"
    s.actions = []
    plan.actions = []
    plan.assumptions = PlanRequest(opening_balance_cents=10000)
    result = synthesize_plan(s, rules, plan, req)
    assert result.status == "FOUND" and result.total_candidate_tuples == "1" and result.candidate.actions == []


@pytest.mark.parametrize("target", ["action", "rule"])
@pytest.mark.parametrize("status", ["pending", "denied"])
def test_hypothetical_approval_does_not_expand_recorded_permission_domain(target, status):
    s, _, rules, plan, req = setup()
    item = s.actions[1] if target == "action" else rules[3]
    item.approval_status = status
    req.uncertainties.append(ApprovalUncertainty(id="approval", target_id=item.id,
        outcomes=["approved"], rationale="Hypothetical only, not recorded consent."))
    result = synthesize_plan(s, rules, plan, req)
    assert result.status == "NO_SOLUTION" and "late-shift" in result.excluded_actions
    assert item.approval_status == status


@pytest.mark.parametrize("reason", ["missing", "unreviewed", "condition", "duplicate_debt"])
def test_unresolved_ledger_never_proves_impossibility(reason):
    s, _, rules, plan, req = setup()
    if reason == "missing":
        rules.pop(0)
    elif reason == "unreviewed":
        rules[0].review_status = "pending"
    elif reason == "condition":
        rules[0].conditions = [Condition(fact="Unknown prerequisite", resolved=False)]
    else:
        duplicate = s.events[0].model_copy(deep=True)
        duplicate.id = "duplicate-debt"
        s.events.append(duplicate)
    result = synthesize_plan(s, rules, plan, req)
    assert result.status == "INCONCLUSIVE" and result.termination == "UNRESOLVED"
    assert result.candidate is None and result.total_candidate_tuples is None


def test_model_and_time_limits_do_not_publish_partial_domains(monkeypatch):
    s, _, rules, plan, req = setup()
    monkeypatch.setattr(synthesis, "MAX_OPTIONS", 1)
    result = synthesize_plan(s, rules, plan, req)
    assert result.termination == "MODEL_LIMIT" and result.total_candidate_tuples is None
    ticks = iter([0, 6, 6.1])
    monkeypatch.setattr(synthesis, "monotonic", lambda: next(ticks))
    result = synthesize_plan(s, rules, plan, req)
    assert result.status == "INCONCLUSIVE" and result.termination == "TIME_LIMIT"


def test_huge_products_stay_exact_and_bounded():
    s, _, rules, plan, req = setup(opening_balance_cents=20000)
    extra = s.events[1].model_copy(deep=True)
    extra.id = "second-income"
    extra.source_rule_ids = []
    s.events.append(extra)
    req.uncertainties = [IncomeAmountUncertainty(id=identifier, event_id=event_id,
        minimum_cents=0, maximum_cents=10**10, rationale="Representation stress test, not a probability.")
        for identifier, event_id in [("amount", "resilient-paycheck"), ("second", "second-income")]]
    req.max_case_checks = 2
    result = synthesize_plan(s, rules, plan, req)
    assert result.uncertainty_cases_per_candidate == "100000000020000000001"
    assert result.status == "INCONCLUSIVE" and result.uncertainty_checks == 1


@pytest.mark.parametrize("assumptions", [{"include_conditional": True}, {"approval_overrides": {"late-shift": "approved"}},
    {"force_action_ids": ["bad"]}, {"force_action_ids": ["late-shift", "late-shift"]},
    {"force_action_ids": ["late-shift"], "exclude_action_ids": ["late-shift"]},
    {"action_dates": {"late-shift": date(2026, 9, 2)}}])
def test_invalid_or_unsupported_controls_rejected(assumptions):
    s, _, rules, plan, req = setup()
    plan.assumptions = PlanRequest(**assumptions)
    with pytest.raises(ValueError):
        synthesize_plan(s, rules, plan, req)


def test_forged_fingerprint_tuple_and_changed_budget_fail_closed():
    s, _, rules, plan, req = setup()
    result = synthesize_plan(s, rules, plan, req)
    body = adoption(result)
    body.candidate_fingerprint = "0" * 64
    with pytest.raises(CandidateUnavailable):
        revalidate_candidate(s, rules, plan, body)
    body = adoption(result)
    body.selected_actions[0].action_id = "early-shift"
    with pytest.raises(CandidateUnavailable):
        revalidate_candidate(s, rules, plan, body)
    body = adoption(result)
    body.synthesis_request.max_case_checks = 1
    with pytest.raises(CandidateUnavailable):
        revalidate_candidate(s, rules, plan, body)


def test_original_demo_still_has_no_safe_schedule_and_retained_future_debt():
    s, _, rules = load_demo()
    plan = optimize(s, rules)
    assert plan.baseline.minimum_balance_cents == -40000 and plan.proposed.minimum_balance_cents == 5000
    req = SynthesisRequest(plan_id=plan.id, revision=plan.revision, uncertainties=[IncomeDateUncertainty(
        id="payday", event_id="paycheck", earliest="2026-09-21", latest="2026-09-28", rationale="Original demo range.")])
    result = synthesize_plan(s, rules, plan, req)
    assert result.status == "NO_SOLUTION" and result.search_exhausted
    req.uncertainties = []
    result = synthesize_plan(s, rules, plan, req)
    assert result.status == "FOUND" and any(e.id == "device" for e in result.candidate.proposed.beyond_horizon)


def test_same_day_dependency_order_and_write_collision():
    s, _, rules, plan, req = setup(force_action_ids=["late-shift"])
    prerequisite = s.actions[0].model_copy(deep=True)
    prerequisite.id = "z-prerequisite"
    prerequisite.kind = "keep"
    prerequisite.effects, prerequisite.excludes = [], []
    s.actions[0] = prerequisite
    s.actions[1].requires = [prerequisite.id]
    s.actions[1].excludes = []
    plan.actions = []
    result = synthesize_plan(s, rules, plan, req)
    assert result.status == "FOUND"
    assert [a.action_id for a in result.candidate.actions] == ["z-prerequisite", "late-shift"]
    prerequisite.effects = [Effect(operation="shift", target_event_id="resilient-bill", date="2026-09-03")]
    result = synthesize_plan(s, rules, plan, req)
    assert result.status == "NO_SOLUTION" and result.candidate is None


@pytest.mark.parametrize("blocker", ["essential", "superseded", "effect_timing"])
def test_unavailable_actions_do_not_supply_fabricated_cash(blocker):
    s, _, rules, plan, req = setup()
    if blocker == "essential":
        s.events[0].essential = True
        s.actions[1].kind = "cancel"
        s.actions[1].effects = [Effect(operation="remove", target_event_id="resilient-bill")]
    elif blocker == "superseded":
        replacement = rules[3].model_copy(deep=True)
        replacement.id = "replacement-option"
        replacement.supersedes = [rules[3].id]
        rules.append(replacement)
    else:
        s.actions[1].earliest_date = s.actions[1].latest_date = date(2026, 9, 3)
    result = synthesize_plan(s, rules, plan, req)
    assert result.status == "NO_SOLUTION" and "late-shift" in result.excluded_actions


def test_unknown_target_and_duplicate_input_ids_rejected():
    s, _, rules, plan, req = setup()
    req.uncertainties[0].event_id = "unknown"
    with pytest.raises(ValueError, match="known projected income"):
        synthesize_plan(s, rules, plan, req)
    req.uncertainties = []
    s.actions.append(s.actions[0].model_copy(deep=True))
    with pytest.raises(ValueError, match="Duplicate action"):
        synthesize_plan(s, rules, plan, req)
