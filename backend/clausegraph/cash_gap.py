"""Bounded hypothetical-cash diagnostic for one saved fixed schedule.

Generalizes the `scripts/verify_demo.py` diagnostic. It answers a single
question: holding the saved actions and execution dates fixed, how much
explicitly hypothetical additional opening cash would the declared bounded
model need? It never searches for new permissions, edits clauses, or combines
repairs, and an amount it reports is a diagnostic, never funding.
"""
from __future__ import annotations

from datetime import date as Date, datetime, timezone
from uuid import uuid4

from clausegraph.schemas import (
    CashGapDiagnostic, CashGapRequest, MinimalityWitness, PlanResult, Rule, Scenario,
    VerificationRequest, VerificationResult,
)
from clausegraph.verification import verify_plan

# Only a shortfall in daily closing cash can be repaired by opening cash.
# Authorization, evidence, accounting, essential services and dependencies cannot.
CASH_REPAIRABLE = "nonnegative_balance"


def _verification_request(request: CashGapRequest) -> VerificationRequest:
    return VerificationRequest(
        plan_id=request.plan_id, revision=request.revision,
        uncertainties=[item.model_copy(deep=True) for item in request.uncertainties],
        max_cases=request.max_cases, time_limit_seconds=request.time_limit_seconds,
    )


def _base_opening_cents(scenario: Scenario, plan: PlanResult) -> int:
    saved = plan.assumptions.opening_balance_cents
    return scenario.opening_balance_cents if saved is None else saved


def _with_extra_cash(plan: PlanResult, base_opening_cents: int, extra_cents: int) -> PlanResult:
    """Same plan, same actions, same dates; only the declared opening cash moves."""
    funded = plan.model_copy(deep=True)
    funded.assumptions.opening_balance_cents = base_opening_cents + extra_cents
    return funded


def _blocking_properties(baseline: VerificationResult) -> list[str]:
    counterexample = baseline.counterexample
    if counterexample is None:
        return []
    return sorted({failure.property for failure in counterexample.failures})


def _limiting_links(baseline: VerificationResult) -> tuple[Date | None, list[str], list[str]]:
    """Point at the date, events and rules that drive the required buffer."""
    worst = baseline.worst_case
    limiting_date = worst.first_shortfall_date if worst else None
    if limiting_date is None and baseline.counterexample:
        limiting_date = baseline.counterexample.earliest_failing_date
    event_ids: list[str] = []
    if worst and limiting_date is not None:
        for day in worst.daily:
            if day.date == limiting_date:
                event_ids = list(day.event_ids)
                break
    rule_ids: list[str] = []
    counterexample = baseline.counterexample
    if counterexample:
        for failure in counterexample.failures:
            rule_ids.extend(failure.source_rule_ids)
        if not event_ids:
            event_ids = [item.event.id for item in counterexample.events
                         if limiting_date is None or item.event.date == limiting_date]
        for item in counterexample.events:
            if item.event.id in event_ids:
                rule_ids.extend(item.event.source_rule_ids or [])
    return limiting_date, sorted(set(event_ids)), sorted(set(rule_ids))


def _witness(tested_cents: int, result: VerificationResult) -> MinimalityWitness:
    return MinimalityWitness(
        tested_additional_cents=tested_cents, status=result.status,
        coverage_complete=result.coverage_complete,
        earliest_failing_date=result.counterexample.earliest_failing_date if result.counterexample else None,
    )


def diagnose_cash_gap(scenario: Scenario, rules: list[Rule], plan: PlanResult,
                      request: CashGapRequest) -> CashGapDiagnostic:
    """Report a verified-sufficient buffer, a proven lower bound, or why cash cannot help."""
    started = datetime.now(timezone.utc)
    verification_request = _verification_request(request)
    baseline = verify_plan(scenario, rules, plan, verification_request)
    base_opening = _base_opening_cents(scenario, plan)
    limiting_date, limiting_event_ids, limiting_rule_ids = _limiting_links(baseline)
    blocking = _blocking_properties(baseline)
    warnings = ["An additional-cash amount is a bounded diagnostic. It is not funding, income, "
                "an approval, or a change to any obligation."]
    warnings.extend(baseline.warnings)

    def build(status: str, statement: str, *, additional: int | None = None, lower_bound: int | None = None,
              minimal: bool = False, funded: VerificationResult | None = None,
              witness: MinimalityWitness | None = None, extra: list[str] | None = None) -> CashGapDiagnostic:
        return CashGapDiagnostic(
            id=str(uuid4()), plan_id=plan.id, revision=plan.revision, status=status,
            additional_opening_cash_cents=additional, lower_bound_cents=lower_bound,
            minimality_proven=minimal, baseline=baseline, funded=funded, minimality_witness=witness,
            limiting_date=limiting_date, limiting_event_ids=limiting_event_ids,
            limiting_rule_ids=limiting_rule_ids, blocking_properties=blocking, statement=statement,
            warnings=sorted(set(warnings + (extra or []))), generated_at=started,
        )

    if baseline.status == "SAFE":
        return build("NOT_REQUIRED", "The saved fixed schedule is already safe for every case in the "
                                     "declared bounded model; no additional cash is required.",
                     additional=0, lower_bound=0, minimal=True)

    non_cash = [item for item in blocking if item != CASH_REPAIRABLE]
    if non_cash:
        return build("NOT_REPAIRABLE_WITH_CASH",
                     "The declared model fails for reasons money cannot repair: "
                     f"{', '.join(non_cash)}. Resolve those before asking about a cash buffer.",
                     extra=["Missing evidence and unauthorized schedules are never repaired by adding cash."])

    worst = baseline.worst_case
    if worst is None:
        return build("INCONCLUSIVE", "No case produced a permitted cash simulation, so no cash "
                                     "requirement can be established for this schedule.")

    observed_minimum = worst.minimum_balance_cents
    if observed_minimum >= 0:
        # Without proven coverage, "no shortfall seen yet" is not "no shortfall exists".
        if not baseline.worst_case_proven:
            return build("INCONCLUSIVE",
                         "Coverage stopped before every declared case was evaluated and no shortfall "
                         "appeared in the cases checked, so no cash requirement is established.")
        return build("NOT_REPAIRABLE_WITH_CASH",
                     "Daily cash never goes negative in any case of the declared model, so the failure is "
                     "not a cash shortfall and additional opening cash would not address it.")

    candidate = -observed_minimum
    funded = verify_plan(scenario, rules, _with_extra_cash(plan, base_opening, candidate), verification_request)

    if funded.status != "SAFE":
        incomplete = not (baseline.coverage_complete and funded.coverage_complete)
        unresolved = "required ledger or evidence facts remain unresolved, which cash cannot settle" \
            if funded.status == "UNKNOWN" and not incomplete else "no sufficient amount is established here"
        return build("INCONCLUSIVE" if incomplete else "NOT_REPAIRABLE_WITH_CASH",
                     f"Adding {candidate} cents did not make the same fixed schedule safe in the declared "
                     f"model: {unresolved}.",
                     lower_bound=candidate, funded=funded)

    if not baseline.worst_case_proven:
        return build("SUFFICIENT_NOT_PROVEN_MINIMAL",
                     f"{candidate} cents of hypothetical opening cash verified the same fixed schedule, but "
                     "the baseline worst case was not proven, so this is not established as the minimum.",
                     additional=candidate, lower_bound=candidate, funded=funded)

    witness_result = verify_plan(scenario, rules, _with_extra_cash(plan, base_opening, candidate - 1),
                                 verification_request)
    witness = _witness(candidate - 1, witness_result)
    if witness_result.status == "SAFE" or not witness_result.coverage_complete:
        return build("SUFFICIENT_NOT_PROVEN_MINIMAL",
                     f"{candidate} cents verified the same fixed schedule, but one cent less was not shown "
                     "to fail, so minimality is not proven.",
                     additional=candidate, lower_bound=candidate, funded=funded, witness=witness)

    return build("PROVEN_MINIMUM",
                 f"{candidate} cents of explicitly hypothetical additional opening cash is the proven minimum "
                 "for this fixed schedule across every case in the declared bounded model: that amount "
                 "verifies safe and one cent less fails.",
                 additional=candidate, lower_bound=candidate, minimal=True, funded=funded, witness=witness)
