from datetime import date, timedelta
from itertools import product
from random import Random

import pytest

from clausegraph import engine
from clausegraph.demo import START, load_demo
from clausegraph.engine import optimize, simulate
from clausegraph.schemas import Action, Condition, Effect, Evidence, FinancialEvent, PlanRequest, Rule, Scenario


def supported_rule(identifier="rule", **kwargs):
    quote = "Synthetic: payment may be cancelled and removed, or moved to 2026-09-05 or 2026-09-06. "
    quote += "Possible fixture amounts: " + ", ".join(f"{amount} cents" for amount in range(200))
    quote += ". Fixture fees: " + "; ".join(f"{amount} cents fee" for amount in range(61))
    return Rule(id=identifier, title=identifier, kind="option", evidence=[Evidence(document_id="doc", page=1, char_start=0, char_end=len(quote), quote=quote)], evidence_status="supported", review_status="reviewed", **kwargs)


def action(identifier, effects, **kwargs):
    if any(effect.operation == "shift" for effect in effects):
        kwargs.setdefault("approval_status", "approved")
    return Action(id=identifier, title=identifier, description="Synthetic reviewed action", kind="cancel", source_rule_ids=["rule"], effects=effects, earliest_date=START, latest_date=START + timedelta(days=1), recommended_date=START, review_status="reviewed", **kwargs)


def event(identifier, day, amount, direction="expense", **kwargs):
    return FinancialEvent(id=identifier, title=identifier, date=START + timedelta(days=day), amount_cents=amount, direction=direction, **kwargs)


def scenario(events, actions=(), opening=100, horizon=5):
    return Scenario(id="small", title="Small exact case", start_date=START, horizon_days=horizon, opening_balance_cents=opening, events=events, actions=list(actions))


def test_denied_approval_overrides_approved_fixture():
    data, _, rules = load_demo()
    plan = optimize(data, rules, PlanRequest(approval_overrides={"shift-payment": "denied"}))
    assert plan.proposed.minimum_balance_cents == -40000
    assert plan.proposed.additional_cash_required_cents == 40000
    assert plan.state == "infeasible"
    assert plan.solver_status == "OPTIMAL"  # Cash infeasibility is not model infeasibility.


def test_pending_approval_only_enters_labeled_conditional_result():
    data, _, rules = load_demo()
    data.actions[0].approval_status = "pending"
    rules[5].approval_status = "pending"
    normal = optimize(data, rules)
    assert normal.proposed.minimum_balance_cents == -40000
    conditional = optimize(data, rules, PlanRequest(include_conditional=True))
    assert conditional.state == "conditional"
    assert conditional.proposed.minimum_balance_cents == 5000
    assert conditional.actions[0].conditional
    assert data.actions[0].approval_status == "pending"
    assert rules[5].approval_status == "pending"


def test_approval_override_cannot_forge_confirmed_approval():
    data, _, rules = load_demo()
    data.actions[0].approval_status = "pending"
    request = PlanRequest(approval_overrides={"shift-payment": "approved"})
    assert optimize(data, rules, request).proposed.minimum_balance_cents == -40000
    request.include_conditional = True
    assert optimize(data, rules, request).state == "conditional"


@pytest.mark.parametrize("change", ["review", "evidence", "conditions", "entity"])
def test_review_and_evidence_gates_cannot_be_overridden_by_assumptions(change):
    data, _, rules = load_demo()
    if change == "review":
        rules[5].review_status = "pending"
    elif change == "evidence":
        rules[5].evidence_status = "disputed"
    elif change == "entity":
        rules[5].entity_ambiguous = True
    else:
        rules[5].conditions = [Condition(fact="eligible", value=True)]
    plan = optimize(data, rules, PlanRequest(include_conditional=True))
    assert plan.proposed.minimum_balance_cents == -40000
    assert not plan.actions


def test_unsupported_benefit_cannot_hide_in_baseline():
    data, _, rules = load_demo()
    data.events.append(event("invented-grant", 0, 500000, "income", source_rule_ids=["rule-assistance"]))
    plan = optimize(data, rules, PlanRequest(include_conditional=True))
    assert plan.baseline.minimum_balance_cents == -40000
    assert all("invented-grant" not in row.event_ids for row in plan.proposed.daily)
    assert any("excluded from the ledger" in warning for warning in plan.warnings)


def test_intake_income_without_source_and_actual_history_are_retained():
    data = scenario([event("user-income", 0, 100, "income"), event("booked", 1, 50, "income", kind="actual", source_rule_ids=["missing"])])
    assert optimize(data, []).proposed.ending_balance_cents == 250


def test_horizon_is_start_inclusive_end_exclusive_and_preserves_future_debt():
    data = scenario([event("past", -1, 1000), event("start", 0, 10), event("last", 4, 20), event("future", 5, 30)])
    result = simulate(data)
    assert result.minimum_balance_cents == 70
    assert result.daily[0].expense_cents == 10
    assert result.daily[-1].expense_cents == 20
    assert [(item.id, item.amount_cents) for item in result.beyond_horizon] == [("future", 30)]


def test_deferral_past_horizon_remains_an_obligation():
    moved = action("move", [Effect(operation="shift", target_event_id="bill", date=START + timedelta(days=5))], approval_status="approved")
    data = scenario([event("bill", 1, 150)], [moved])
    plan = optimize(data, [supported_rule()])
    assert plan.proposed.ending_balance_cents == 100
    assert plan.proposed.beyond_horizon[0].amount_cents == 150
    assert "deferrals are not savings" in " ".join(plan.warnings)


def test_essentials_cannot_be_removed_even_with_misleading_preservation_flag():
    remove = action("remove", [Effect(operation="remove", target_event_id="rent")], preserves_essential_services=True)
    data = scenario([event("rent", 1, 150, essential=True)], [remove])
    plan = optimize(data, [supported_rule()])
    assert plan.proposed.minimum_balance_cents == -50
    assert "Essential" in plan.excluded_actions["remove"]
    forced = optimize(data, [supported_rule()], PlanRequest(force_action_ids=["remove"]))
    assert forced.state == "unresolved" and forced.solver_status == "INFEASIBLE"


@pytest.mark.parametrize("actual, day", [(True, 1), (False, -1)])
def test_actual_and_past_obligations_are_immutable(actual, day):
    remove = action("remove", [Effect(operation="remove", target_event_id="bill")])
    data = scenario([event("bill", day, 100, kind="actual" if actual else "projected")], [remove])
    plan = optimize(data, [supported_rule()])
    assert "remove" in plan.excluded_actions


def test_conflicting_effects_cannot_double_count_same_event():
    actions = [action("remove", [Effect(operation="remove", target_event_id="bill")]), action("shift", [Effect(operation="shift", target_event_id="bill", date=START + timedelta(days=4))])]
    data = scenario([event("bill", 1, 100)], actions)
    plan = optimize(data, [supported_rule()])
    assert plan.proposed.ending_balance_cents <= 100
    with pytest.raises(ValueError, match="collide"):
        simulate(data, {"remove": START, "shift": START})
    forced = optimize(data, [supported_rule()], PlanRequest(force_action_ids=["remove", "shift"]))
    assert forced.solver_status == "INFEASIBLE"


def test_duplicate_debt_addition_and_backwards_acceleration_fail_closed():
    debt = event("device", 10, 48000, obligation_id="principal")
    duplicate = action("duplicate", [Effect(operation="add", event=event("new", 2, 48000, obligation_id="principal"))])
    wrong_date = action("late-acceleration", [Effect(operation="accelerate", target_event_id="device", date=START + timedelta(days=11))])
    data = scenario([debt], [duplicate, wrong_date])
    plan = optimize(data, [supported_rule()])
    assert set(plan.excluded_actions) == {"duplicate", "late-acceleration"}


def test_dependencies_are_ordered_and_mutual_exclusions_enforced():
    prerequisite = action("first", [], burden=0)
    remove = action("second", [Effect(operation="remove", target_event_id="bill")], requires=["first"])
    data = scenario([event("bill", 1, 150)], [remove, prerequisite])
    plan = optimize(data, [supported_rule()])
    assert [item.action_id for item in plan.actions] == ["first", "second"]
    assert plan.actions[0].execution_date <= plan.actions[1].execution_date
    remove.excludes = ["first"]
    data.actions = [remove, prerequisite]
    assert optimize(data, [supported_rule()]).proposed.minimum_balance_cents == -50


def test_action_dates_cannot_escape_deadlines_or_apply_retroactively():
    data, _, rules = load_demo()
    late = PlanRequest(force_action_ids=["shift-payment"], action_dates={"shift-payment": START + timedelta(days=12)})
    assert optimize(data, rules, late).state == "unresolved"
    assert optimize(data, rules, PlanRequest(action_dates={"shift-payment": START + timedelta(days=11)})).state == "confirmed"


def test_timeout_is_not_reported_as_optimal(monkeypatch):
    data, _, rules = load_demo()
    monkeypatch.setattr(engine, "SOLVER_TIME_LIMIT_SECONDS", 0)
    plan = optimize(data, rules)
    assert plan.solver_status == "UNKNOWN"
    assert not plan.objective_proven
    assert plan.state == "unresolved"


def test_feasible_candidate_does_not_claim_objective_proof(monkeypatch):
    data, _, rules = load_demo()
    original = engine.cp_model.CpSolver.solve

    def feasible(self, model):
        status = original(self, model)
        return engine.cp_model.FEASIBLE if status == engine.cp_model.OPTIMAL else status

    monkeypatch.setattr(engine.cp_model.CpSolver, "solve", feasible)
    plan = optimize(data, rules)
    assert plan.solver_status == "FEASIBLE"
    assert not plan.objective_proven
    assert plan.proposed.minimum_balance_cents == 5000


@pytest.mark.parametrize("seed", range(12))
def test_solver_matches_exhaustive_small_cases(seed):
    random = Random(seed)
    rules = [supported_rule()]
    actions = [
        action("a-remove", [Effect(operation="remove", target_event_id="a")], fee_cents=random.randrange(0, 35), burden=random.randrange(1, 4)),
        action("a-move", [Effect(operation="shift", target_event_id="a", date=START + timedelta(days=4))], fee_cents=random.randrange(0, 20), burden=random.randrange(1, 4)),
        action("b-remove", [Effect(operation="remove", target_event_id="b")], fee_cents=random.randrange(0, 60), burden=random.randrange(1, 4)),
    ]
    data = scenario([event("a", 1, random.randrange(40, 120)), event("b", 2, random.randrange(20, 80)), event("pay", 3, random.randrange(40, 120), "income")], actions, opening=random.randrange(40, 100))
    candidates = []
    for dates in product((None, START, START + timedelta(days=1)), repeat=len(actions)):
        selected = {item.id: day for item, day in zip(actions, dates) if day is not None}
        try:
            ledger = simulate(data, selected)
        except ValueError:
            continue
        fees = sum(item.fee_cents for item in actions if item.id in selected)
        burden = sum(item.burden for item in actions if item.id in selected)
        candidates.append((ledger.minimum_balance_cents, -fees, -burden))
    plan = optimize(data, rules)
    picked = {item.action_id for item in plan.actions}
    actual = (plan.proposed.minimum_balance_cents, -sum(item.fee_cents for item in actions if item.id in picked), -sum(item.burden for item in actions if item.id in picked))
    assert actual == max(candidates)
    assert plan.objective_proven


def test_unknown_approvals_and_income_ambiguity_are_explicit():
    data = scenario([event("income1", 1, 10, "income"), event("income2", 2, 20, "income")])
    with pytest.raises(ValueError, match="exactly one"):
        optimize(data, [], PlanRequest(income_date=date(2026, 9, 4)))
    assert optimize(data, [], PlanRequest(approval_overrides={"missing": "approved"})).state == "unresolved"


def test_unreviewed_or_deleted_expense_sources_retain_money_and_prevent_confirmation():
    data, _, rules = load_demo()
    rules[0].review_status = "pending"
    plan = optimize(data, rules)
    assert plan.proposed.minimum_balance_cents == 5000
    assert plan.state == "unresolved"
    assert any("Rent remains" in warning for warning in plan.warnings)
    deleted = optimize(data, [rule for rule in rules if rule.id != "rule-rent"])
    assert deleted.proposed.ending_balance_cents == 50000
    assert deleted.state == "unresolved"


def test_obligation_not_yet_materialized_cannot_produce_false_confirmation():
    data, _, rules = load_demo()
    rules[0].review_status = "pending"
    data.events = [event for event in data.events if event.id != "rent"]
    plan = optimize(data, rules)
    assert plan.state == "unresolved"
    assert any("may not be fully represented" in warning for warning in plan.warnings)


def test_cancellation_cannot_omit_source_acceleration_or_mutate_unrelated_loan():
    data, _, rules = load_demo()
    data.actions[1].effects = data.actions[1].effects[:1]
    plan = optimize(data, rules)
    assert "omits the debt acceleration" in plan.excluded_actions["cancel-phone"]
    data, _, rules = load_demo()
    data.actions[1].effects[0].target_event_id = "loan"
    plan = optimize(data, rules)
    assert "does not identify the target" in plan.excluded_actions["cancel-phone"]


def test_optimization_rechecks_forged_effect_dates_and_money():
    data, _, rules = load_demo()
    data.actions[0].effects[0].date = START + timedelta(days=60)
    plan = optimize(data, rules)
    assert plan.proposed.minimum_balance_cents == -40000
    assert "not supported" in plan.excluded_actions["shift-payment"]
    data, _, rules = load_demo()
    data.actions[0].effects.append(Effect(operation="add", event=event("free-money", 25, 999999, "income")))
    assert "not supported" in optimize(data, rules).excluded_actions["shift-payment"]


def test_conditional_rule_dependency_approval_propagates_through_reverse_order():
    data, _, rules = load_demo()
    prerequisite = supported_rule("authorization", approval_status="pending")
    middle = supported_rule("middle", dependencies=["authorization"])
    rules[5].dependencies.append("middle")
    rules.extend([middle, prerequisite])
    assert optimize(data, rules).proposed.minimum_balance_cents == -40000
    conditional = optimize(data, rules, PlanRequest(include_conditional=True))
    assert conditional.state == "conditional"
    assert conditional.actions[0].conditional


def test_extreme_magnitudes_return_model_invalid_instead_of_overflow():
    data = scenario([event("bill", 1, 10**100)])
    result = optimize(data, [])
    assert result.solver_status == "MODEL_INVALID"
    assert result.state == "unresolved"
    data = scenario([], [action("large", [], burden=10**100)])
    assert optimize(data, [supported_rule()]).solver_status == "MODEL_INVALID"


def test_plan_assumptions_survive_json_roundtrip_and_do_not_alias_request():
    from clausegraph.schemas import PlanResult
    data, _, rules = load_demo()
    request = PlanRequest(opening_balance_cents=210000, approval_overrides={"shift-payment": "denied"})
    plan = optimize(data, rules, request)
    request.approval_overrides.clear()
    restored = PlanResult.model_validate_json(plan.model_dump_json())
    assert restored.assumptions.approval_overrides == {"shift-payment": "denied"}
    assert restored.assumptions.opening_balance_cents == 210000


def test_duplicate_obligation_entries_are_visible_and_never_confirmed():
    data = scenario([event("a", 1, 10, obligation_id="same"), event("b", 1, 10, obligation_id="same")])
    plan = optimize(data, [])
    assert plan.proposed.ending_balance_cents == 80
    assert plan.state == "unresolved"
    assert any("same obligation" in warning for warning in plan.warnings)


def test_calendar_overflow_is_an_explicit_validation_error():
    data = scenario([])
    data.start_date = date.max
    with pytest.raises(ValueError, match="calendar"):
        optimize(data, [])


def test_source_backed_expense_cannot_be_inverted_into_income():
    data, _, rules = load_demo()
    data.events[0].direction = "income"
    plan = optimize(data, rules)
    assert all("rent" not in row.event_ids for row in plan.baseline.daily)
    assert any("Rent is excluded" in warning for warning in plan.warnings)
    assert plan.state == "unresolved"


def test_explicit_income_scenario_assumptions_remain_available():
    data, _, rules = load_demo()
    plan = optimize(data, rules, PlanRequest(income_cents=100000))
    assert plan.proposed.ending_balance_cents == 60000
