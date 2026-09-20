"""Bounded first-feasible search for one recorded-permission fixed schedule.

Search never optimizes per outcome or saves a plan. Adoption reconstructs and
independently verifies an untrusted tuple before the API can persist it.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from math import prod
from time import monotonic
from uuid import uuid4

from .engine import MAX_ACTIONS, MAX_OPTIONS, _action_changes, _decision_trace, _effective_scenario, _end, _gates, _prepare_ledger
from .extraction import action_evidence_blocker
from .schemas import (
    Action, PlanResult, PlannedAction, Rule, Scenario, ScheduledAction, SynthesisAdoptionResult,
    SynthesisAdoptRequest, SynthesisCosts, SynthesisProvenance, SynthesisRefutation, SynthesisRequest,
    SynthesisResult, VerificationRequest,
)
from .verification import FixedPlanCheck, _dimension_size, _validate_targets, check_fixed_plan, verify_plan


class CandidateUnavailable(ValueError):
    """A revalidation could not establish the displayed candidate; save nothing."""


class _Cutoff(Exception):
    def __init__(self, reason: str, detail: str):
        self.reason, self.detail = reason, detail


@dataclass
class _Budget:
    request: SynthesisRequest
    started: float
    nominal: int = 0
    uncertainty: int = 0

    @property
    def remaining_cases(self) -> int:
        return self.request.max_case_checks - self.nominal - self.uncertainty

    def remaining_time(self) -> float:
        remaining = self.request.time_limit_seconds - (monotonic() - self.started)
        if remaining <= 0:
            raise _Cutoff("TIME_LIMIT", "The shared synthesis time limit was reached.")
        return remaining

    def nominal_check(self, scenario, rules, selected, assumptions) -> FixedPlanCheck:
        self.remaining_time()
        if self.remaining_cases <= 0:
            raise _Cutoff("CASE_LIMIT", "The shared nominal/uncertainty case budget was reached.")
        result = check_fixed_plan(scenario, rules, selected, assumptions)
        self.nominal += 1
        return result


@dataclass
class _Domain:
    base: Scenario
    prepared: Scenario
    rules: list[Rule]
    source: PlanResult
    actions: dict[str, Action]
    options: list[tuple[str, list[date | None]]]
    excluded: dict[str, str]
    empty_check: FixedPlanCheck
    total: int


def _costs(actions: dict[str, Action], selected) -> SynthesisCosts:
    return SynthesisCosts(total_action_fees_cents=sum(actions[aid].fee_cents for aid in selected),
        total_action_burden=sum(actions[aid].burden for aid in selected))


def _validate_inputs(scenario, rules, source, request):
    if source.id != request.plan_id or source.revision != request.revision:
        raise ValueError("Synthesis requires the matching current saved plan and revision.")
    if source.assumptions.include_conditional or source.assumptions.approval_overrides:
        raise ValueError("Synthesis v1 requires recorded approvals. Save a plan without conditional approval assumptions or overrides.")
    for label, items in (("action", scenario.actions), ("event", scenario.events), ("rule", rules)):
        if len({item.id for item in items}) != len(items):
            raise ValueError(f"Duplicate {label} identifiers are ambiguous.")
    actions = {action.id: action for action in scenario.actions}
    saved = [item.action_id for item in source.actions]
    if len(set(saved)) != len(saved) or set(saved) - actions.keys():
        raise ValueError("The saved plan has duplicate or unknown selected action identifiers.")
    controls = source.assumptions
    forced, excluded = set(controls.force_action_ids), set(controls.exclude_action_ids)
    if len(forced) != len(controls.force_action_ids) or len(excluded) != len(controls.exclude_action_ids):
        raise ValueError("Forced and excluded action lists must not contain duplicates.")
    if forced & excluded:
        raise ValueError("An action cannot be both forced and excluded.")
    if (forced | excluded | set(controls.action_dates)) - actions.keys():
        raise ValueError("Saved scenario controls contain unknown action identifiers.")
    end = _end(scenario)
    for aid, day in controls.action_dates.items():
        action = actions[aid]
        if not (scenario.start_date <= day < end and action.earliest_date <= day <= action.latest_date):
            raise ValueError("An explicit action date is outside its window or the displayed horizon.")
    _validate_targets(scenario, rules, request)


def _prepare(scenario, rules, source, budget: _Budget) -> _Domain:
    base = _effective_scenario(scenario, source.assumptions)
    _validate_inputs(base, rules, source, budget.request)
    budget.remaining_time()
    magnitude = base.opening_balance_cents + sum(event.amount_cents for event in base.events)
    magnitude += sum(action.fee_cents + sum(effect.event.amount_cents for effect in action.effects if effect.event)
                     for action in base.actions)
    if len(base.actions) > MAX_ACTIONS or magnitude > 10**12 or sum(action.burden for action in base.actions) > 10**12:
        raise _Cutoff("MODEL_LIMIT", "The action count or numeric magnitude exceeds the bounded synthesis model limits.")
    empty = budget.nominal_check(base, rules, {}, source.assumptions)
    if empty.unresolved:
        raise _Cutoff("UNRESOLVED", "Required nominal ledger/evidence facts remain unresolved. " + " ".join(empty.warnings))
    if empty.simulation is None:
        raise _Cutoff("UNRESOLVED", "The nominal ledger cannot be fully simulated. " + " ".join(f.message for f in empty.failures))
    prepared, _, _ = _prepare_ledger(base, rules, source.assumptions)
    excluded, _ = _gates(prepared, rules, source.assumptions)
    actions = {action.id: action for action in prepared.actions}
    options = []
    count = 0
    for aid, action in sorted(actions.items()):
        budget.remaining_time()
        available: list[date | None] = [] if aid in source.assumptions.force_action_ids else [None]
        reason = excluded.get(aid) or action_evidence_blocker(action, rules, prepared.events)
        if not reason:
            first = max(base.start_date, action.earliest_date)
            last = min(_end(base) - timedelta(days=1), action.latest_date)
            dates = [source.assumptions.action_dates[aid]] if aid in source.assumptions.action_dates else (
                first + timedelta(days=offset) for offset in range(max(0, (last - first).days + 1)))
            reason = "No permitted execution date lies inside the action window and horizon."
            for day in dates:
                budget.remaining_time()
                try:
                    _action_changes(prepared, action, day)
                except ValueError as exc:
                    reason = str(exc)
                    continue
                available.append(day)
                count += 1
                if count > MAX_OPTIONS:
                    raise _Cutoff("MODEL_LIMIT", "The action/date option limit was reached during domain construction.")
        if not any(day is not None for day in available):
            excluded[aid] = reason or "Action is unavailable."
        options.append((aid, available))
    return _Domain(base, prepared, rules, source, actions, options, excluded, empty,
                   prod(len(values) for _, values in options))


def _selected(options, index: int) -> dict[str, date]:
    selected = {}
    for aid, values in reversed(options):
        index, offset = divmod(index, len(values))
        if values[offset] is not None:
            selected[aid] = values[offset]
    return dict(sorted(selected.items()))


def _schedule(selected) -> list[ScheduledAction]:
    return [ScheduledAction(action_id=aid, execution_date=day) for aid, day in sorted(selected.items())]


def _render(domain: _Domain, selected: dict[str, date], checked: FixedPlanCheck) -> PlanResult:
    remaining, ordered = set(selected), []
    while remaining:
        ready = [aid for aid in remaining if all(dep in ordered for dep in domain.actions[aid].requires)]
        if not ready:
            raise ValueError("Selected actions contain an unsupported dependency cycle.")
        aid = min(ready, key=lambda item: (selected[item], item))
        ordered.append(aid)
        remaining.remove(aid)
    planned = [PlannedAction(action_id=aid, execution_date=selected[aid], order=index + 1,
        explanation=domain.actions[aid].description, source_rule_ids=domain.actions[aid].source_rule_ids)
        for index, aid in enumerate(ordered)]
    warnings = [*checked.warnings, "This is a verified feasible fixed schedule; no synthesis optimum is claimed."]
    if checked.simulation.beyond_horizon:
        warnings.append("Future obligations remain beyond the horizon; deferrals are timing changes, not savings.")
    return PlanResult(id=str(uuid4()), revision=domain.source.revision, state="confirmed",
        solver_status="FIXED_VERIFIED", solver_wall_time_seconds=0, generation_mode="resilient",
        baseline=domain.empty_check.simulation, proposed=checked.simulation, actions=planned,
        decision_traces=[_decision_trace(domain.prepared, domain.actions[aid], selected[aid], domain.rules) for aid in ordered],
        excluded_actions=domain.excluded, warnings=warnings, objective_proven=False,
        generated_at=datetime.now(timezone.utc), assumptions=domain.source.assumptions.model_copy(deep=True))


def _evaluate(domain: _Domain, selected, budget: _Budget):
    checked = domain.empty_check if not selected else budget.nominal_check(
        domain.base, domain.rules, selected, domain.source.assumptions)
    if checked.failures or checked.unresolved or checked.simulation is None:
        return checked, None, None
    candidate = _render(domain, selected, checked)
    remaining = budget.remaining_time()
    if budget.remaining_cases <= 0:
        raise _Cutoff("CASE_LIMIT", "No shared case budget remains for independent candidate verification.")
    verification = verify_plan(domain.base, domain.rules, candidate, VerificationRequest(
        plan_id=candidate.id, revision=candidate.revision, uncertainties=budget.request.uncertainties,
        max_cases=budget.remaining_cases, time_limit_seconds=remaining))
    budget.uncertainty += verification.checked_cases
    return checked, candidate, verification


def _fingerprint(domain, candidate, verification, request) -> str:
    # A content comparison, not a credential. Every adoption rechecks gates and cases.
    payload = {"source_plan_id": domain.source.id, "revision": domain.source.revision,
        "request": request.model_dump(mode="json"),
        "candidate": candidate.model_dump(mode="json", exclude={"id", "generated_at", "synthesis_provenance", "solver_wall_time_seconds"}),
        "proof": verification.model_dump(mode="json", include={"status", "fixed_actions", "horizon_start", "horizon_end_exclusive",
            "total_cases", "checked_cases", "coverage_complete", "worst_case", "worst_case_assignment", "worst_case_proven", "counterexample"})}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _provenance(domain, candidate, verification, request) -> str:
    fingerprint = _fingerprint(domain, candidate, verification, request)
    candidate.synthesis_provenance = SynthesisProvenance(source_plan_id=domain.source.id,
        fingerprint=fingerprint, request=request.model_copy(deep=True))
    return fingerprint


def synthesize_plan(scenario: Scenario, rules: list[Rule], source: PlanResult, request: SynthesisRequest) -> SynthesisResult:
    budget = _Budget(request, monotonic())
    domain = None
    visited = refuted = unresolved = 0
    example = None
    warnings: set[str] = set()

    def result(status, termination, *, candidate=None, verification=None):
        fingerprint = _provenance(domain, candidate, verification, request) if candidate else None
        statement = {
            "FOUND": "One permitted fixed schedule passed the saved nominal case and every declared uncertainty case. No optimality is claimed.",
            "NO_SOLUTION": "No schedule in the recorded-permission domain survives the saved nominal case plus every declared uncertainty case within this horizon.",
            "INCONCLUSIVE": "No verified candidate is available; the bounded search did not establish that a resilient schedule is impossible.",
        }[status]
        return SynthesisResult(id=str(uuid4()), plan_id=source.id, revision=source.revision, status=status,
            termination=termination, assumptions=request.model_copy(deep=True), nominal_assumptions=source.assumptions.model_copy(deep=True),
            total_candidate_tuples=str(domain.total) if domain else None,
            uncertainty_cases_per_candidate=str(prod(_dimension_size(item) for item in request.uncertainties)),
            visited_candidate_tuples=visited, refuted_candidate_tuples=refuted, unresolved_candidate_tuples=unresolved,
            nominal_checks=budget.nominal, uncertainty_checks=budget.uncertainty,
            search_exhausted=domain is not None and visited == domain.total,
            candidate=candidate, verification=verification, candidate_fingerprint=fingerprint,
            nominal_costs=_costs(domain.actions, [action.action_id for action in source.actions]) if domain else None,
            candidate_costs=_costs(domain.actions, [action.action_id for action in candidate.actions]) if candidate else None,
            example_refutation=example, excluded_actions=domain.excluded if domain else {}, statement=statement,
            warnings=sorted(warnings), runtime_seconds=round(monotonic() - budget.started, 6), generated_at=datetime.now(timezone.utc))

    try:
        domain = _prepare(scenario, rules, source, budget)
        for index in range(min(domain.total, request.max_candidates)):
            budget.remaining_time()
            selected = _selected(domain.options, index)
            visited += 1
            checked, candidate, verification = _evaluate(domain, selected, budget)
            warnings.update(checked.warnings)
            if checked.failures:
                refuted += 1
                if example is None:
                    example = SynthesisRefutation(stage="nominal", selected_actions=_schedule(selected), failures=checked.failures)
            elif verification is None:
                unresolved += 1
            elif verification.status == "SAFE" and verification.coverage_complete:
                return result("FOUND", "VERIFIED_CANDIDATE", candidate=candidate, verification=verification)
            elif verification.status == "UNSAFE":
                refuted += 1
                if example is None:
                    example = SynthesisRefutation(stage="uncertainty", selected_actions=_schedule(selected),
                        failures=verification.counterexample.failures, counterexample=verification.counterexample)
            else:
                unresolved += 1
                warnings.update(verification.warnings)
                if verification.solver_status in ("TIME_LIMIT", "CASE_LIMIT"):
                    return result("INCONCLUSIVE", verification.solver_status)
        if visited == domain.total and refuted == domain.total:
            return result("NO_SOLUTION", "EXHAUSTED")
        return result("INCONCLUSIVE", "UNRESOLVED" if visited == domain.total else "CANDIDATE_LIMIT")
    except _Cutoff as exc:
        warnings.add(exc.detail)
        if visited > refuted + unresolved:
            unresolved += 1
        return result("INCONCLUSIVE", exc.reason)


def revalidate_candidate(scenario: Scenario, rules: list[Rule], source: PlanResult,
                         body: SynthesisAdoptRequest) -> SynthesisAdoptionResult:
    """Reconstruct an untrusted tuple; never trust a hash or previous SAFE badge."""
    request = body.synthesis_request
    budget = _Budget(request, monotonic())
    try:
        domain = _prepare(scenario, rules, source, budget)
        selected = {item.action_id: item.execution_date for item in body.selected_actions}
        if set(selected) - domain.actions.keys():
            raise ValueError("Candidate contains an unknown action.")
        for aid, values in domain.options:
            if selected.get(aid) not in values:
                raise ValueError("Candidate is outside the recorded-permission/action-constraint domain.")
        checked, candidate, verification = _evaluate(domain, selected, budget)
        if checked.failures or candidate is None or verification is None or verification.status != "SAFE" or not verification.coverage_complete:
            raise CandidateUnavailable("The exact candidate could not be independently verified. Refresh the preview; no plan was saved.")
        fingerprint = _provenance(domain, candidate, verification, request)
        if fingerprint != body.candidate_fingerprint:
            raise CandidateUnavailable("Candidate contents differ from the displayed preview. Refresh and review before adoption.")
        return SynthesisAdoptionResult(plan=candidate, verification=verification)
    except _Cutoff as exc:
        raise CandidateUnavailable(f"Candidate revalidation is inconclusive ({exc.reason}). No plan was saved.") from exc
