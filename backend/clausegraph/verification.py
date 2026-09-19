"""Bounded finite model checking of a saved, fixed action schedule.

Every date, integer cent and declared approval outcome is a discrete state.
There is no sampling, optimization, probability estimate or alternate money
model here: concrete states use the planner's gates and ledger transitions.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from math import prod
from uuid import uuid4

from .engine import (
    _action_changes, _effective_scenario, _end, _gates, _materialize,
    _prepare_ledger, simulate,
)
from .extraction import action_evidence_blocker, event_evidence_blocker, rule_blocker
from .graph import dependency_issues
from .schemas import (
    ApprovalStatus, Counterexample, FinancialEvent, PlanRequest, PlanResult,
    Rule, Scenario, Simulation, UncertaintyAssignment, VerificationFailure,
    VerificationRequest, VerificationResult, VerificationTraceEvent,
)


@dataclass
class FixedPlanCheck:
    """One concrete state; absent simulation means no authorized cash trace."""

    simulation: Simulation | None = None
    failures: list[VerificationFailure] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    unresolved: bool = False
    events: list[FinancialEvent] = field(default_factory=list)


def _failure_property(message: str) -> str:
    message = message.lower()
    if "essential" in message:
        return "essential_services"
    if any(word in message for word in ("prerequisite", "dependency", "exclusive", "cycle")):
        return "dependencies"
    if any(word in message for word in ("evidence", "source", "review", "supported", "condition", "entity")):
        return "evidence"
    if any(word in message for word in ("approval", "execution", "window", "horizon", "excluded")):
        return "authorization"
    return "accounting"


def check_fixed_plan(
    scenario: Scenario, rules: list[Rule], selected: dict[str, date],
    assumptions: PlanRequest | None = None, *, assumed_income_fields: dict[str, set[str]] | None = None,
) -> FixedPlanCheck:
    """Check one concretized assignment, without selecting/replacing actions.

    Approvals must already be concrete on isolated copies. Conditional approval
    is deliberately disabled; callers must never pass hypothetical status as a
    recorded decision. This helper does not mutate its arguments.
    """
    strict = (assumptions or PlanRequest()).model_copy(deep=True)
    strict.include_conditional = False
    strict.approval_overrides = {}
    assumed_income_fields = {key: set(value) for key, value in (assumed_income_fields or {}).items()}
    nominal_fields = ({"date"} if strict.income_date is not None else set()) | ({"amount_cents"} if strict.income_cents is not None else set())
    if nominal_fields:
        incomes = [event for event in scenario.events if event.direction == "income" and event.kind == "projected"]
        if len(incomes) != 1:
            raise ValueError("Nominal income assumptions require exactly one projected income event.")
        assumed_income_fields.setdefault(incomes[0].id, set()).update(nominal_fields)
    prepared, warnings, unresolved = _prepare_ledger(
        scenario, rules, strict, assumed_income_ids=set(assumed_income_fields),
    )
    result = FixedPlanCheck(warnings=warnings, unresolved=unresolved)
    rule_map = {rule.id: rule for rule in rules}
    # Missing/unchecked ledger evidence must not disappear into a SAFE badge,
    # even if the conservative optimizer would withhold that projected income.
    for event in scenario.events:
        if event.kind != "projected" or not event.source_rule_ids:
            continue
        reason = next((
            "A source rule is missing." if rid not in rule_map else rule_blocker(rule_map[rid], check_approval=False)
            for rid in event.source_rule_ids
            if rid not in rule_map or rule_blocker(rule_map[rid], check_approval=False)
        ), None)
        overrides = assumed_income_fields.get(event.id, set()) if event.direction == "income" else set()
        check_values = not overrides
        reason = reason or event_evidence_blocker(event, rules, check_values=check_values)
        if not reason and overrides:
            # A date assumption cannot excuse an unsupported amount, and an
            # amount assumption cannot excuse an unsupported date. Both values
            # must still match one source except the explicitly changed fields.
            sources = [rule_map[rid] for rid in event.source_rule_ids if rid in rule_map]
            matching = [source for source in sources if
                        ("date" in overrides or source.due_date == event.date) and
                        ("amount_cents" in overrides or source.amount_cents == event.amount_cents)]
            if not matching:
                reason = "An income value outside the declared assumptions lacks a matching source."
            else:
                restricted = event.model_copy(deep=True)
                restricted.source_rule_ids = [source.id for source in matching]
                reason = event_evidence_blocker(restricted, rules, check_values=False)
        if reason:
            result.unresolved = True
            result.warnings.append(f"{event.title}: {reason}")
    for issue in dependency_issues(scenario, rules):
        if issue.code in ("duplicate_id", "duplicate_obligation"):
            result.unresolved = True
            result.warnings.append(issue.message)

    actions = {action.id: action for action in prepared.actions}
    excluded, conditional = _gates(prepared, rules, strict)
    for aid, execution in sorted(selected.items(), key=lambda item: (item[1], item[0])):
        action = actions.get(aid)
        reason = excluded.get(aid)
        if action is None:
            reason = "Selected action does not exist."
        elif not reason:
            reason = action_evidence_blocker(action, rules, prepared.events)
        if not reason and aid in conditional:
            reason = "Required third-party approval is unresolved."
        if not reason and action:
            if any(dep not in selected or selected[dep] > execution for dep in action.requires):
                reason = "Action prerequisites must be selected and executed first."
            elif any(other in selected for other in action.excludes):
                reason = "Mutually exclusive actions cannot both be selected."
            else:
                try:
                    _action_changes(prepared, action, execution)
                except ValueError as exc:
                    reason = str(exc)
        if reason:
            result.failures.append(VerificationFailure(
                property=_failure_property(reason), message=reason, date=execution,
                action_id=aid, source_rule_ids=action.source_rule_ids if action else [],
            ))
    if result.failures:
        return result
    try:
        result.events = _materialize(prepared, selected)
        simulation = simulate(prepared, selected)
    except ValueError as exc:
        result.failures.append(VerificationFailure(
            property=_failure_property(str(exc)), message=str(exc), date=scenario.start_date,
            source_rule_ids=sorted({rid for aid in selected if aid in actions for rid in actions[aid].source_rule_ids}),
        ))
        return result
    if result.unresolved:
        # A partial ledger is insufficient to prove either liquidity safety or
        # a cash counterexample; structural/authorization failures above remain
        # conclusive independently of the unresolved cash facts.
        return result
    result.simulation = simulation
    if simulation.first_shortfall_date is not None:
        first = next(row for row in simulation.daily if row.date == simulation.first_shortfall_date)
        result.failures.append(VerificationFailure(
            property="nonnegative_balance", message="Daily balance falls below zero.", date=first.date,
            source_rule_ids=sorted({rid for event in result.events if event.id in first.event_ids for rid in event.source_rule_ids}),
        ))
    return result


def _dimension_size(dimension) -> int:
    if dimension.kind == "income_date":
        return (dimension.latest - dimension.earliest).days + 1
    if dimension.kind == "income_amount":
        return dimension.maximum_cents - dimension.minimum_cents + 1
    return len(dimension.outcomes)


def _assignment(dimensions, sizes: list[int], index: int) -> list[UncertaintyAssignment]:
    # Mixed-radix indexing avoids itertools.product eagerly allocating huge
    # integer ranges before the work/time limit can stop the checker.
    indices = [0] * len(dimensions)
    for position in range(len(dimensions) - 1, -1, -1):
        index, indices[position] = divmod(index, sizes[position])
    assignment = []
    for dimension, offset in zip(dimensions, indices):
        if dimension.kind == "income_date":
            value = (dimension.earliest + timedelta(days=offset)).isoformat()
        elif dimension.kind == "income_amount":
            value = dimension.minimum_cents + offset
        else:
            value = sorted(dimension.outcomes)[offset]
        assignment.append(UncertaintyAssignment(dimension_id=dimension.id, value=value))
    return assignment


def _validate_targets(scenario: Scenario, rules: list[Rule], request: VerificationRequest) -> None:
    events = {event.id: event for event in scenario.events}
    actions = {action.id: action for action in scenario.actions}
    rule_map = {rule.id: rule for rule in rules}
    for dimension in request.uncertainties:
        if dimension.kind == "approval":
            if dimension.target_id in actions and dimension.target_id in rule_map:
                raise ValueError("Approval target is ambiguous between an action and a rule.")
            if dimension.target_id not in actions and dimension.target_id not in rule_map:
                raise ValueError(f"Unknown approval target: {dimension.target_id}.")
        else:
            event = events.get(dimension.event_id)
            if event is None or event.direction != "income" or event.kind != "projected":
                raise ValueError("Income uncertainty requires a known projected income event.")
            if event.date < scenario.start_date:
                raise ValueError("Uncertainty cannot change historical income.")
            if dimension.kind == "income_date" and dimension.earliest < scenario.start_date:
                raise ValueError("Income date uncertainty cannot precede the verification horizon.")


def _counterexample(assignment, check: FixedPlanCheck, selected: dict[str, date], scenario: Scenario) -> Counterexample:
    first = min((failure.date for failure in check.failures if failure.date), default=None)
    row = next((row for row in check.simulation.daily if row.date == first), None) if check.simulation else None
    event_actions: dict[str, list[str]] = {}
    for action in scenario.actions:
        if action.id not in selected:
            continue
        for effect in action.effects:
            identifier = effect.event.id if effect.operation == "add" and effect.event else effect.target_event_id
            if identifier:
                event_actions.setdefault(identifier, []).append(action.id)
        if action.fee_cents:
            event_actions[f"action-fee:{action.id}"] = [action.id]
    return Counterexample(
        assignment=assignment, earliest_failing_date=first, balance_cents=row.balance_cents if row else None,
        failures=check.failures, simulation=check.simulation,
        events=[VerificationTraceEvent(event=event, action_ids=sorted(event_actions.get(event.id, [])))
                for event in sorted(check.events, key=lambda item: (item.date, item.id))],
    )


def verify_plan(scenario: Scenario, rules: list[Rule], plan: PlanResult, request: VerificationRequest) -> VerificationResult:
    """Check all declared finite states or report exactly why coverage stopped."""
    started = time.monotonic()
    if request.plan_id != plan.id or request.revision != plan.revision:
        raise ValueError("Verification requires the matching saved plan and workspace revision.")
    base = _effective_scenario(scenario, plan.assumptions)
    end = _end(base)
    _validate_targets(base, rules, request)
    dimensions = sorted(request.uncertainties, key=lambda item: (item.kind, item.id))
    sizes = [_dimension_size(item) for item in dimensions]
    total = prod(sizes)
    selected = {action.action_id: action.execution_date for action in plan.actions}
    checked = 0
    solver_status = "EXHAUSTED"
    warnings: set[str] = set()
    counterexample = None
    worst = None
    worst_assignment = []
    unresolved = False
    all_simulated = True
    invalid = len(selected) != len(plan.actions)
    if invalid:
        warnings.add("The saved plan contains duplicate selected action identifiers.")
    known_approvals = {action.id for action in base.actions} | {rule.id for rule in rules}
    if set(plan.assumptions.approval_overrides) - known_approvals:
        invalid = True
        warnings.add("The saved plan contains unknown approval identifiers.")
    if any(value == ApprovalStatus.not_required for value in plan.assumptions.approval_overrides.values()):
        # Preserve the nominal gate: an assumption may not remove a required
        # approval, even when the resulting plan happened to select nothing.
        statuses = {item.id: item.approval_status for item in [*base.actions, *rules]}
        if any(value == ApprovalStatus.not_required and statuses.get(key) != value
               for key, value in plan.assumptions.approval_overrides.items()):
            invalid = True
            warnings.add("A nominal assumption cannot remove a required approval.")
    assumed_income_fields: dict[str, set[str]] = {}
    for item in dimensions:
        if item.kind != "approval":
            assumed_income_fields.setdefault(item.event_id, set()).add("date" if item.kind == "income_date" else "amount_cents")
    if plan.assumptions.approval_overrides:
        warnings.add("Nominal approval overrides are hypothetical model assumptions, not recorded third-party decisions.")
    if not plan.assumptions.include_conditional:
        statuses = {item.id: item.approval_status for item in [*base.actions, *rules]}
        if any(value == ApprovalStatus.approved and statuses.get(key) != ApprovalStatus.approved
               for key, value in plan.assumptions.approval_overrides.items()):
            invalid = True
            warnings.add("An unrecorded approval assumption requires a labeled conditional nominal scenario.")
    for index in range(min(total, request.max_cases)):
        if invalid:
            solver_status = "INVALID_MODEL"
            break
        if time.monotonic() - started >= request.time_limit_seconds:
            solver_status = "TIME_LIMIT"
            break
        assignment = _assignment(dimensions, sizes, index)
        concrete = base.model_copy(deep=True)
        concrete_rules = [rule.model_copy(deep=True) for rule in rules]
        approvals = dict(plan.assumptions.approval_overrides)
        events = {event.id: event for event in concrete.events}
        for dimension, value in zip(dimensions, assignment):
            if dimension.kind == "income_date":
                events[dimension.event_id].date = date.fromisoformat(str(value.value))
            elif dimension.kind == "income_amount":
                events[dimension.event_id].amount_cents = value.value
            else:
                approvals[dimension.target_id] = ApprovalStatus(value.value)
        for item in [*concrete.actions, *concrete_rules]:
            if item.id in approvals:
                item.approval_status = approvals[item.id]
        check = check_fixed_plan(concrete, concrete_rules, selected, plan.assumptions, assumed_income_fields=assumed_income_fields)
        checked += 1
        unresolved = unresolved or check.unresolved
        warnings.update(check.warnings)
        all_simulated = all_simulated and check.simulation is not None
        if check.simulation and (worst is None or check.simulation.minimum_balance_cents < worst.minimum_balance_cents):
            worst, worst_assignment = check.simulation, assignment
        if check.failures:
            candidate = _counterexample(assignment, check, selected, concrete)
            # Enumeration is lexicographic; strict comparison retains the first
            # (simplest) assignment when its earliest failure date ties.
            if counterexample is None or (candidate.earliest_failing_date or date.max) < (counterexample.earliest_failing_date or date.max):
                counterexample = candidate
    if checked < total and solver_status == "EXHAUSTED":
        solver_status = "CASE_LIMIT"
    complete = checked == total and solver_status == "EXHAUSTED"
    status = "UNSAFE" if counterexample else "SAFE" if complete and not unresolved else "UNKNOWN"
    if status == "SAFE":
        statement = "Verified safe for every case in the declared bounded model and displayed horizon only."
    elif status == "UNSAFE":
        statement = "A concrete assignment in the declared bounded model violates the fixed plan's safety properties."
    else:
        statement = "Safety is unknown: the bounded check is incomplete or required ledger/evidence facts remain unresolved."
    if not complete:
        warnings.add("Coverage is incomplete; observed balances are not a proven worst case and the counterexample may not be the earliest possible failure.")
    if not all_simulated:
        warnings.add("Unauthorized or unresolved schedules have no permitted cash simulation; any reported balance covers only fully evaluated authorized cases.")
    if worst and worst.beyond_horizon:
        warnings.add("Future obligations are retained beyond the horizon; deferrals are timing changes, not savings.")
    return VerificationResult(
        id=str(uuid4()), plan_id=plan.id, revision=plan.revision, status=status, solver_status=solver_status,
        runtime_seconds=round(time.monotonic() - started, 6), horizon_start=base.start_date,
        horizon_end_exclusive=end, assumptions=request.model_copy(deep=True), nominal_assumptions=plan.assumptions.model_copy(deep=True),
        fixed_actions=[action.model_copy(deep=True) for action in plan.actions], dimension_count=len(dimensions),
        total_cases=total, checked_cases=checked, coverage_complete=complete, worst_case=worst,
        worst_case_assignment=worst_assignment, worst_case_proven=complete and all_simulated and not unresolved,
        counterexample=counterexample, statement=statement, warnings=sorted(warnings), generated_at=datetime.now(timezone.utc),
    )
