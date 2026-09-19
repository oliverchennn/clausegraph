"""Deterministic cash accounting and bounded, lexicographic CP-SAT planning."""
from __future__ import annotations

import time
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

from ortools.sat.python import cp_model

from .extraction import rule_blocker
from .graph import dependency_issues
from .schemas import (
    Action, ApprovalStatus, DailyBalance, FinancialEvent, PlanRequest, PlanResult,
    PlannedAction, ReviewStatus, Rule, Scenario, Simulation,
)


SOLVER_TIME_LIMIT_SECONDS = 5.0
MAX_ACTIONS = 100
MAX_OPTIONS = 10_000


def _end(scenario: Scenario) -> date:
    return scenario.start_date + timedelta(days=scenario.horizon_days)


def _effect_date(effect, execution: date, fallback: date | None = None) -> date:
    if effect.date is not None and effect.offset_days is not None:
        raise ValueError("A date effect cannot specify both a date and an offset.")
    if effect.date is not None:
        return effect.date
    if effect.offset_days is not None:
        if not -3660 <= effect.offset_days <= 3660:
            raise ValueError("Date offsets are limited to ten years.")
        try:
            return execution + timedelta(days=effect.offset_days)
        except OverflowError as exc:
            raise ValueError("Date effect is outside the supported calendar.") from exc
    if fallback is not None:
        return fallback
    raise ValueError("Date effect has no date.")


def _action_changes(scenario: Scenario, action: Action, execution: date) -> tuple[set[str], list[FinancialEvent]]:
    """Materialize one action using only the original ledger, never other effects."""
    if not (action.earliest_date <= execution <= action.latest_date):
        raise ValueError("Execution date is outside the action window.")
    if not (scenario.start_date <= execution < _end(scenario)):
        raise ValueError("Execution date is outside the planning horizon.")
    if action.service_id in scenario.essential_service_ids and not action.preserves_essential_services:
        raise ValueError("Action would remove a protected essential service.")
    original = {event.id: event for event in scenario.events}
    removed: set[str] = set()
    replacements: list[FinancialEvent] = []
    added_ids: set[str] = set()
    for effect in action.effects:
        if effect.operation == "add":
            event = effect.event.model_copy(deep=True)
            if event.id in original or event.id in added_ids:
                raise ValueError("Added event duplicates an existing financial event.")
            if event.obligation_id and any(item.obligation_id == event.obligation_id for item in scenario.events):
                raise ValueError("An existing obligation must be moved, not added a second time.")
            if event.kind != "projected":
                raise ValueError("A proposed action cannot create an actual event.")
            event.date = _effect_date(effect, execution, event.date)
            if event.date < execution:
                raise ValueError("An action cannot create cash before its execution date.")
            replacements.append(event)
            added_ids.add(event.id)
            continue
        target = original.get(effect.target_event_id)
        if target is None:
            raise ValueError(f"Target event {effect.target_event_id} does not exist.")
        if target.id in removed:
            raise ValueError("Multiple effects mutate the same event within one action.")
        if target.kind == "actual" or target.date < scenario.start_date:
            raise ValueError("Actual or historical financial events cannot be changed.")
        if execution > target.date:
            raise ValueError("The action occurs after the original obligation date.")
        if target.essential or target.service_id in scenario.essential_service_ids:
            if effect.operation == "remove" or not action.preserves_essential_services:
                raise ValueError("Essential expenses cannot be silently removed.")
        removed.add(target.id)
        if effect.operation in ("shift", "accelerate"):
            updated = target.model_copy(deep=True)
            updated.date = _effect_date(effect, execution)
            if updated.date < execution:
                raise ValueError("A moved obligation cannot precede action execution.")
            if effect.operation == "accelerate" and (target.direction != "expense" or updated.date > target.date):
                raise ValueError("Acceleration must move an existing debt earlier.")
            replacements.append(updated)
    if action.fee_cents:
        fee_id = f"action-fee:{action.id}"
        if fee_id in original or fee_id in added_ids:
            raise ValueError("Action fee identifier collides with an existing event.")
        replacements.append(FinancialEvent(id=fee_id, title=f"{action.title} fee", date=execution, amount_cents=action.fee_cents, direction="expense", source_rule_ids=action.source_rule_ids))
    return removed, replacements


def _materialize(scenario: Scenario, selected: dict[str, date]) -> list[FinancialEvent]:
    actions = {action.id: action for action in scenario.actions}
    if len(actions) != len(scenario.actions) or len({event.id for event in scenario.events}) != len(scenario.events):
        raise ValueError("Financial event and action identifiers must be unique.")
    if any(aid not in actions for aid in selected):
        raise ValueError("Selected action does not exist.")
    removed: set[str] = set()
    appended: dict[str, FinancialEvent] = {}
    for aid, execution in selected.items():
        action = actions[aid]
        if any(dep not in selected or selected[dep] > execution for dep in action.requires):
            raise ValueError("Action prerequisites must be selected and executed first.")
        if any(other in selected for other in action.excludes):
            raise ValueError("Mutually exclusive actions cannot both be selected.")
        targets, additions = _action_changes(scenario, action, execution)
        if targets & removed or any(event.id in appended for event in additions):
            raise ValueError("Selected actions collide on the same financial event.")
        removed.update(targets)
        appended.update({event.id: event for event in additions})
    return [event.model_copy(deep=True) for event in scenario.events if event.id not in removed] + list(appended.values())


def simulate(scenario: Scenario, selected: dict[str, date] | None = None) -> Simulation:
    """Account for selected effects; optimize() applies evidence/approval gates."""
    events = _materialize(scenario, selected or {})
    by_day: dict[date, list[FinancialEvent]] = defaultdict(list)
    for event in events:
        by_day[event.date].append(event)
    balance = scenario.opening_balance_cents
    daily: list[DailyBalance] = []
    for offset in range(scenario.horizon_days):
        day = scenario.start_date + timedelta(days=offset)
        items = by_day[day]
        income = sum(event.amount_cents for event in items if event.direction == "income")
        expense = sum(event.amount_cents for event in items if event.direction == "expense")
        balance += income - expense
        daily.append(DailyBalance(date=day, balance_cents=balance, income_cents=income, expense_cents=expense, event_ids=sorted(event.id for event in items)))
    minimum = min(row.balance_cents for row in daily)
    return Simulation(daily=daily, minimum_balance_cents=minimum, ending_balance_cents=balance, first_shortfall_date=next((row.date for row in daily if row.balance_cents < 0), None), additional_cash_required_cents=max(0, -minimum), beyond_horizon=sorted((event for event in events if event.date >= _end(scenario)), key=lambda event: (event.date, event.id)))


def _effective_scenario(scenario: Scenario, request: PlanRequest) -> Scenario:
    effective = scenario.model_copy(deep=True)
    if request.opening_balance_cents is not None:
        effective.opening_balance_cents = request.opening_balance_cents
    if request.horizon_days is not None:
        effective.horizon_days = request.horizon_days
    if request.income_date is not None or request.income_cents is not None:
        incomes = [event for event in effective.events if event.direction == "income" and event.kind == "projected"]
        if len(incomes) != 1:
            raise ValueError("Income controls require exactly one projected income event; edit intake for multiple incomes.")
        if request.income_date is not None:
            incomes[0].date = request.income_date
        if request.income_cents is not None:
            incomes[0].amount_cents = request.income_cents
    return effective


def _approval_gate(identifier: str, stored: ApprovalStatus, request: PlanRequest, *, required: bool = False) -> tuple[str | None, bool]:
    override = request.approval_overrides.get(identifier)
    effective = override if override is not None else stored
    if effective == ApprovalStatus.denied:
        return "Required third-party approval was denied.", False
    if override == ApprovalStatus.approved and stored != ApprovalStatus.approved:
        if request.include_conditional:
            return None, True
        return "An approval assumption requires a labeled conditional scenario.", False
    if override == ApprovalStatus.not_required and stored != ApprovalStatus.not_required:
        return "An assumption cannot remove a required approval.", False
    if effective == ApprovalStatus.pending or (required and effective != ApprovalStatus.approved):
        if request.include_conditional:
            return None, True
        return "Required third-party approval is pending.", False
    return None, False


def _gates(scenario: Scenario, rules: list[Rule], request: PlanRequest) -> tuple[dict[str, str], set[str]]:
    rule_map = {rule.id: rule for rule in rules}
    issues = dependency_issues(scenario, rules)
    rule_reasons: dict[str, str] = {}
    conditional_rules: set[str] = set()
    for issue in issues:
        if issue.blocking:
            for rid in issue.rule_ids:
                rule_reasons[rid] = issue.message
    for rule in rules:
        reason = rule_blocker(rule, check_approval=False)
        if reason:
            rule_reasons[rule.id] = reason
        reason, conditional = _approval_gate(rule.id, rule.approval_status, request, required=rule.kind == "benefit")
        if reason:
            rule_reasons[rule.id] = reason
        if conditional:
            conditional_rules.add(rule.id)
    # Only a reviewed, supported and approved replacement supersedes an old rule.
    for rule in rules:
        if rule.id not in rule_reasons and rule.id not in conditional_rules:
            for old in rule.supersedes:
                rule_reasons[old] = f"Superseded by {rule.title}."
    while True:
        before = (len(rule_reasons), len(conditional_rules))
        for rule in rules:
            if any(dep not in rule_map or dep in rule_reasons for dep in rule.dependencies):
                rule_reasons[rule.id] = "A required rule is missing or not eligible."
            if any(dep in conditional_rules for dep in rule.dependencies):
                conditional_rules.add(rule.id)
        if (len(rule_reasons), len(conditional_rules)) == before:
            break
    excluded: dict[str, str] = {}
    conditional_actions: set[str] = set()
    for action in scenario.actions:
        if action.id in request.exclude_action_ids:
            excluded[action.id] = "Excluded in scenario controls."
        elif action.review_status != ReviewStatus.reviewed:
            excluded[action.id] = "Action requires human review."
        elif not action.source_rule_ids or any(rid not in rule_map for rid in action.source_rule_ids):
            excluded[action.id] = "Action lacks a known source rule."
        elif any(rid in rule_reasons for rid in action.source_rule_ids):
            excluded[action.id] = next(rule_reasons[rid] for rid in action.source_rule_ids if rid in rule_reasons)
        reason, conditional = _approval_gate(action.id, action.approval_status, request, required=action.kind in ("shift", "claim", "request") and not any(rule_map[rid].approval_status == ApprovalStatus.approved for rid in action.source_rule_ids if rid in rule_map))
        if reason:
            excluded[action.id] = reason
        if conditional or any(rid in conditional_rules for rid in action.source_rule_ids):
            conditional_actions.add(action.id)
    action_ids = {action.id for action in scenario.actions}
    while True:
        before = (len(excluded), len(conditional_actions))
        for action in scenario.actions:
            if any(dep not in action_ids or dep in excluded for dep in action.requires):
                excluded[action.id] = "A prerequisite action is unavailable."
            if any(dep in conditional_actions for dep in action.requires):
                conditional_actions.add(action.id)
        if before == (len(excluded), len(conditional_actions)):
            break
    return excluded, conditional_actions


def optimize(scenario: Scenario, rules: list[Rule], request: PlanRequest | None = None, revision: int = 1) -> PlanResult:
    """Maximize minimum cash, then minimize fees, burden and execution dates.

    Maximizing the minimum first strictly prefers every nonnegative plan over
    every shortfall plan. A negative proven maximum is a cash diagnostic, not
    an infeasible CP-SAT model or fictitious funding.
    """
    started = time.monotonic()
    request = request or PlanRequest()
    scenario = _effective_scenario(scenario, request)
    warnings: list[str] = []
    rule_map = {rule.id: rule for rule in rules}
    blocked_rules = {rule.id for rule in rules if rule_blocker(rule)}
    blocked_rules.update(rid for issue in dependency_issues(scenario, rules) if issue.blocking for rid in issue.rule_ids)
    for rule in rules:
        reason, conditional = _approval_gate(rule.id, rule.approval_status, request, required=rule.kind == "benefit")
        if reason or conditional:
            blocked_rules.add(rule.id)
    while True:
        expanded = blocked_rules | {rule.id for rule in rules if any(dep not in rule_map or dep in blocked_rules for dep in rule.dependencies)}
        if expanded == blocked_rules:
            break
        blocked_rules = expanded
    retained = []
    for event in scenario.events:
        if event.direction == "income" and event.kind == "projected" and event.source_rule_ids and any(rid not in rule_map or rid in blocked_rules for rid in event.source_rule_ids):
            warnings.append(f"{event.title} is excluded from the ledger because its evidence, conditions, review or approval are unresolved. Conditional income requires an explicit eligible claim action.")
        else:
            retained.append(event)
    scenario.events = retained
    baseline = simulate(scenario)
    excluded, conditional_actions = _gates(scenario, rules, request)

    def result(state, status, proposed=baseline, planned=None, proven=False):
        return PlanResult(id=str(uuid4()), revision=revision, state=state, solver_status=status, solver_wall_time_seconds=round(time.monotonic() - started, 6), baseline=baseline, proposed=proposed, actions=planned or [], excluded_actions=excluded, warnings=warnings, objective_proven=proven, generated_at=datetime.now(timezone.utc))

    if len(scenario.actions) > MAX_ACTIONS:
        warnings.append(f"Planner limit is {MAX_ACTIONS} actions. Narrow the scenario before solving.")
        return result("unresolved", "UNKNOWN")
    model = cp_model.CpModel()
    options: dict[str, list[tuple[date, cp_model.IntVar, set[str], list[FinancialEvent]]]] = {}
    chosen: dict[str, cp_model.IntVar] = {}
    execution_days: dict[str, cp_model.IntVar] = {}
    actions = {action.id: action for action in scenario.actions}
    unknown = (set(request.force_action_ids) | set(request.action_dates) | set(request.exclude_action_ids)) - set(actions)
    if unknown:
        warnings.append(f"Unknown action identifiers: {', '.join(sorted(unknown))}.")
        return result("unresolved", "INFEASIBLE")
    unknown_approvals = set(request.approval_overrides) - (set(actions) | {rule.id for rule in rules})
    if unknown_approvals:
        warnings.append(f"Unknown approval identifiers: {', '.join(sorted(unknown_approvals))}.")
        return result("unresolved", "INFEASIBLE")
    for aid, action in sorted(actions.items()):
        if aid in excluded:
            continue
        first = max(scenario.start_date, action.earliest_date)
        last = min(_end(scenario) - timedelta(days=1), action.latest_date)
        dates = [request.action_dates[aid]] if aid in request.action_dates else [first + timedelta(days=offset) for offset in range(max(0, (last - first).days + 1))]
        available = []
        failure = "No execution date lies inside the action window and horizon."
        for day in dates:
            try:
                removed, additions = _action_changes(scenario, action, day)
            except ValueError as exc:
                failure = str(exc)
                continue
            variable = model.new_bool_var(f"{aid}@{day.isoformat()}")
            available.append((day, variable, removed, additions))
        if not available:
            excluded[aid] = failure
            continue
        options[aid] = available
        chosen[aid] = model.new_bool_var(f"select:{aid}")
        model.add(sum(item[1] for item in available) == chosen[aid])
        execution_days[aid] = model.new_int_var(0, scenario.horizon_days, f"execution:{aid}")
        model.add(execution_days[aid] == sum(((day - scenario.start_date).days + 1) * variable for day, variable, _, _ in available))
    if sum(len(items) for items in options.values()) > MAX_OPTIONS:
        warnings.append(f"Planner limit is {MAX_OPTIONS} action/date combinations. Narrow action windows.")
        return result("unresolved", "UNKNOWN")
    for aid, variable in chosen.items():
        for dep in actions[aid].requires:
            if dep not in chosen:
                model.add(variable == 0)
                excluded[aid] = "A prerequisite action has no valid execution date."
            else:
                model.add(variable <= chosen[dep])
                model.add(execution_days[dep] <= execution_days[aid]).only_enforce_if(variable)
        for other in actions[aid].excludes:
            if other in chosen:
                model.add(variable + chosen[other] <= 1)
    for aid in request.force_action_ids:
        if aid not in chosen or aid in excluded:
            warnings.append(f"Forced action {aid} is unavailable: {excluded.get(aid, 'unknown action')}.")
            return result("unresolved", "INFEASIBLE")
        model.add(chosen[aid] == 1)
    # Every event (and every added identifier) has at most one selected writer.
    writers: dict[str, dict[str, cp_model.IntVar]] = defaultdict(dict)
    for aid, items in options.items():
        for _, _, removed, additions in items:
            for identifier in removed | {event.id for event in additions}:
                writers[identifier][aid] = chosen[aid]
            for event in additions:
                if event.obligation_id:
                    writers[f"obligation:{event.obligation_id}"][aid] = chosen[aid]
    for by_action in writers.values():
        if len(by_action) > 1:
            model.add(sum(by_action.values()) <= 1)

    original = {event.id: event for event in scenario.events}
    deltas: list[list] = [[] for _ in range(scenario.horizon_days)]
    absolute_bound = scenario.opening_balance_cents + sum(event.amount_cents for event in scenario.events) + 1
    for items in options.values():
        for _, variable, removed, additions in items:
            changes: dict[date, int] = defaultdict(int)
            for identifier in removed:
                event = original[identifier]
                changes[event.date] -= event.amount_cents if event.direction == "income" else -event.amount_cents
            for event in additions:
                changes[event.date] += event.amount_cents if event.direction == "income" else -event.amount_cents
            running = 0
            for offset in range(scenario.horizon_days):
                running += changes.get(scenario.start_date + timedelta(days=offset), 0)
                if running:
                    deltas[offset].append(running * variable)
            absolute_bound += sum(abs(amount) for amount in changes.values())
    if absolute_bound > 10**15:
        warnings.append("Scenario magnitudes exceed the solver's safe integer bound.")
        return result("unresolved", "MODEL_INVALID")
    minimum = model.new_int_var(-absolute_bound, absolute_bound, "minimum_daily_balance")
    for offset, day in enumerate(baseline.daily):
        model.add(minimum <= day.balance_cents + sum(deltas[offset]))
    fees = sum(actions[aid].fee_cents * variable for aid, variable in chosen.items())
    burden = sum(actions[aid].burden * variable for aid, variable in chosen.items())
    # Stable tie breaking is bounded and intentionally subordinate to fee/burden.
    execution = sum((index + 1) * execution_days[aid] for index, aid in enumerate(sorted(chosen)))
    phases = [(minimum, True), (fees, False), (burden, False), (execution, False)]
    best: dict[str, date] | None = None
    last_status = "UNKNOWN"
    proven = True
    for expression, maximize in phases:
        remaining = SOLVER_TIME_LIMIT_SECONDS - (time.monotonic() - started)
        if remaining <= 0:
            proven = False
            break
        if maximize:
            model.maximize(expression)
        else:
            model.minimize(expression)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = remaining
        solver.parameters.num_search_workers = 1
        solver.parameters.random_seed = 0
        status = solver.solve(model)
        name = solver.status_name(status)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            proven = False
            if best is None:
                last_status = name
            break
        best = {aid: day for aid, items in options.items() for day, variable, _, _ in items if solver.value(variable)}
        last_status = name
        if status != cp_model.OPTIMAL:
            proven = False
            break
        model.add(expression == int(solver.value(expression)))
    if best is None:
        warnings.append("No solver solution was found within the constraints and time limit; the displayed ledger is the baseline.")
        return result("infeasible" if last_status == "INFEASIBLE" else "unresolved", last_status)
    if not proven:
        last_status = "FEASIBLE"
        warnings.append("A feasible candidate was found, but all lexicographic objectives were not proven optimal within the time limit.")
    proposed = simulate(scenario, best)
    # Topological order resolves same-day prerequisites in the human checklist.
    ordered: list[str] = []
    remaining_ids = set(best)
    while remaining_ids:
        ready = [aid for aid in remaining_ids if all(dep in ordered for dep in actions[aid].requires)]
        if not ready:
            warnings.append("Selected actions have an unsupported dependency cycle.")
            return result("unresolved", "MODEL_INVALID")
        selected_id = min(ready, key=lambda aid: (best[aid], aid))
        ordered.append(selected_id)
        remaining_ids.remove(selected_id)
    planned = [PlannedAction(action_id=aid, execution_date=best[aid], order=index + 1, explanation=("Conditional on third-party approval. " if aid in conditional_actions else "") + actions[aid].description, source_rule_ids=actions[aid].source_rule_ids, conditional=aid in conditional_actions) for index, aid in enumerate(ordered)]
    if any(action.conditional for action in planned):
        state = "conditional"
        warnings.append("Conditional approval assumptions do not change persisted approvals.")
    elif proposed.minimum_balance_cents < 0:
        state = "infeasible" if proven else "unresolved"
    else:
        state = "confirmed"
    if proposed.additional_cash_required_cents:
        warnings.append("Additional cash required is a shortfall diagnostic, not an assumed income event." if proven else "The displayed cash gap belongs to this candidate; a global minimum cash requirement has not been proven.")
    if proposed.beyond_horizon:
        warnings.append("Future obligations remain on the ledger beyond the displayed horizon; deferrals are not savings.")
    return result(state, last_status, proposed, planned, proven)
