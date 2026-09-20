"""Bounded verification limits and interactions with saved nominal assumptions."""
from datetime import timedelta
from itertools import product

import pytest
from fastapi.testclient import TestClient

from clausegraph.api import create_app
from clausegraph.config import Settings
from clausegraph.demo import START
from clausegraph.engine import optimize
from clausegraph.schemas import FinancialEvent, PlanRequest, Scenario, VerificationRequest, VerificationResult
from clausegraph.storage import Store
from clausegraph.verification import verify_plan


def amount(identifier="pay", low=3, high=5):
    return dict(kind="income_amount", id=f"amount-{identifier}", event_id=identifier,
                minimum_cents=low, maximum_cents=high, rationale="Synthetic assumed amount.")


def dates(identifier="pay", first=0, last=2):
    return dict(kind="income_date", id=f"date-{identifier}", event_id=identifier,
                earliest=(START + timedelta(days=first)).isoformat(),
                latest=(START + timedelta(days=last)).isoformat(), rationale="Synthetic assumed date.")


def small_ledger():
    return Scenario(id="limits", title="Synthetic bounded ledger", start_date=START,
        horizon_days=3, opening_balance_cents=0, actions=[], events=[
            FinancialEvent(id="pay", title="Explicit intake income", date=START,
                amount_cents=10, direction="income"),
            FinancialEvent(id="bill", title="Essential expense", date=START + timedelta(days=1),
                amount_cents=5, direction="expense", essential=True)])


@pytest.mark.parametrize("varied", ["amount", "date", "both"])
def test_uncertainties_override_nominal_income_values_and_match_independent_oracle(varied):
    scenario = small_ledger()
    plan = optimize(scenario, [], PlanRequest(income_cents=25, income_date=START))
    dimensions = ([amount()] if varied != "date" else []) + ([dates()] if varied != "amount" else [])
    request = VerificationRequest(plan_id=plan.id, revision=plan.revision, uncertainties=dimensions)
    before = scenario.model_dump_json(), plan.model_dump_json(), request.model_dump_json()
    result = verify_plan(scenario, [], plan, request)
    candidates = []
    for cents, payday in product(range(3, 6) if varied != "date" else [25],
                                range(3) if varied != "amount" else [0]):
        balance, rows = 0, []
        for day in range(3):
            balance += (cents if day == payday else 0) - (5 if day == 1 else 0)
            rows.append(balance)
        candidates.append(rows)
    assert result.status == "UNSAFE"
    assert result.total_cases == result.checked_cases == len(candidates)
    assert result.coverage_complete and result.worst_case_proven
    assert [row.balance_cents for row in result.worst_case.daily] == min(candidates, key=min)
    assert result.counterexample.earliest_failing_date == START + timedelta(days=1)
    assert result.nominal_assumptions == plan.assumptions
    assert result.assumptions == request and result.fixed_actions == plan.actions
    assert before == (scenario.model_dump_json(), plan.model_dump_json(), request.model_dump_json())


@pytest.fixture
def api(tmp_path):
    settings = Settings(_env_file=None, database_url=f"sqlite:///{tmp_path / 'limits.db'}",
        local_storage_path=tmp_path / "originals", nvidia_api_key="", gemini_api_key="",
        elevenlabs_api_key="", spaces_endpoint="", spaces_bucket="", spaces_access_key_id="",
        spaces_secret_access_key="")
    store = Store(settings)
    try:
        with TestClient(create_app(settings=settings, store=store)) as client:
            workspace = client.post("/api/sessions", json={"demo": True}).json()
            headers = {"Authorization": f"Bearer {workspace['session_id']}"}
            plan = client.post("/api/plan", headers=headers,
                json={"income_cents": 90000, "income_date": "2026-09-21"}).json()
            yield client, headers, plan
    finally:
        store.engine.dispose()


def test_api_persists_the_actual_uncertain_income_witness_without_changing_nominal_plan(api):
    client, headers, plan = api
    before = client.get("/api/workspace", headers=headers).json()
    request = dict(plan_id=plan["id"], revision=plan["revision"],
        uncertainties=[dates("paycheck", 20, 27)])
    response = client.post("/api/verify", headers=headers, json=request)
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["status"] == "UNSAFE"
    assert result["checked_cases"] == result["total_cases"] == 8
    assert result["worst_case_proven"] and result["coverage_complete"]
    witness = result["counterexample"]
    assert witness["assignment"][0]["value"] == "2026-09-27"
    assert witness["earliest_failing_date"] == "2026-09-26" and witness["balance_cents"] == -40000
    income = next(item["event"] for item in witness["events"] if item["event"]["id"] == "paycheck")
    assert income["date"] == "2026-09-27" and income["amount_cents"] == 90000
    assert client.get("/api/verifications", headers=headers).json() == [result]
    assert client.get("/api/workspace", headers=headers).json() == before


def test_combined_date_amount_and_approval_coverage_does_not_prove_cash_for_unauthorized_cases(api):
    client, headers, plan = api
    response = client.post("/api/verify", headers=headers, json=dict(plan_id=plan["id"],
        revision=plan["revision"], uncertainties=[dates("paycheck", 20, 21),
            amount("paycheck", 90000, 90001), dict(kind="approval", id="decision",
                target_id="shift-payment", outcomes=["pending", "approved", "denied"],
                rationale="Hypothetical decisions; no recorded approval changes.")]))
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["checked_cases"] == result["total_cases"] == 12
    assert result["coverage_complete"] and result["status"] == "UNSAFE"
    assert not result["worst_case_proven"] and result["worst_case"]["minimum_balance_cents"] == 5000
    assert result["counterexample"]["simulation"] is None
    assert result["counterexample"]["balance_cents"] is None
    assert result["counterexample"]["failures"][0]["property"] == "authorization"
    workspace = client.get("/api/workspace", headers=headers).json()
    assert workspace["plan"] == plan
    assert next(action for action in workspace["scenario"]["actions"]
                if action["id"] == "shift-payment")["approval_status"] == "approved"


INVALID_REQUESTS = [
    {"max_cases": value} for value in (0, 10001, True, 1.5, "2")
] + [
    {"time_limit_seconds": value} for value in (0, -1, 10.01)
] + [
    {"uncertainties": [amount("paycheck", value, 10_000_000_000)]}
    for value in (-1, True, 0.5, "1", 10_000_000_001)
] + [
    {"uncertainties": [amount("paycheck", 5, 4)]},
    {"uncertainties": [dates("paycheck", 2, 1)]},
    {"uncertainties": [dates("paycheck", -1, 1)]},
    {"uncertainties": [{**dates("paycheck"), "latest": "2026-02-30"}]},
    {"uncertainties": [amount("missing")]},
    {"uncertainties": [amount("rent")]},
    {"uncertainties": [amount("paycheck"), {**dates("paycheck"), "id": "amount-paycheck"}]},
    {"uncertainties": [amount("paycheck"), {**amount("paycheck"), "id": "second-amount"}]},
    {"uncertainties": [amount(str(index)) for index in range(9)]},
] + [
    {"uncertainties": [dict(kind="approval", id="decision", target_id="shift-payment",
        outcomes=outcomes, rationale="Synthetic decisions.")]}
    for outcomes in ([], ["approved", "approved"], ["not_required"], ["approved", "denied", "pending", "approved"])
]


@pytest.mark.parametrize("overrides", INVALID_REQUESTS)
def test_invalid_limits_and_dimensions_return_422_without_persistence_or_mutation(api, overrides):
    client, headers, plan = api
    before = client.get("/api/workspace", headers=headers).json()
    response = client.post("/api/verify", headers=headers,
        json={"plan_id": plan["id"], "revision": plan["revision"], **overrides})
    assert response.status_code == 422, response.text
    assert client.get("/api/verifications", headers=headers).json() == []
    assert client.get("/api/workspace", headers=headers).json() == before


def test_eight_dimensions_use_full_cartesian_product_and_are_order_independent():
    scenario = small_ledger()
    scenario.events = [FinancialEvent(id=f"pay-{index}", title="Explicit synthetic income", date=START,
        amount_cents=1, direction="income") for index in range(8)]
    plan = optimize(scenario, [])
    dimensions = [amount(event.id, 1, 2) for event in scenario.events]
    results = [verify_plan(scenario, [], plan, VerificationRequest(plan_id=plan.id,
        revision=plan.revision, uncertainties=ordered, time_limit_seconds=10))
        for ordered in (dimensions, list(reversed(dimensions)))]
    for result in results:
        assert result.status == "SAFE" and result.dimension_count == 8
        assert result.checked_cases == result.total_cases == 256 and result.coverage_complete
        assert result.worst_case_proven and result.worst_case.minimum_balance_cents == 8
    assert results[0].worst_case == results[1].worst_case
    assert results[0].worst_case_assignment == results[1].worst_case_assignment


@pytest.mark.parametrize("total", [10000, 10001])
def test_ten_thousand_case_boundary_never_marks_partial_search_safe(total, monkeypatch):
    import clausegraph.verification as verification

    scenario = small_ledger()
    scenario.events = scenario.events[:1]
    plan = optimize(scenario, [])
    # Freeze the cooperative clock to isolate the case boundary from machine speed.
    monkeypatch.setattr(verification.time, "monotonic", lambda: 0.0)
    result = verify_plan(scenario, [], plan, VerificationRequest(plan_id=plan.id,
        revision=plan.revision, uncertainties=[amount(low=0, high=total - 1)],
        max_cases=10000, time_limit_seconds=10))
    assert result.total_cases == total and result.checked_cases == 10000
    assert result.status == ("SAFE" if total == 10000 else "UNKNOWN")
    assert result.solver_status == ("EXHAUSTED" if total == 10000 else "CASE_LIMIT")
    assert result.coverage_complete == result.worst_case_proven == (total == 10000)


@pytest.mark.parametrize("first_tick,checked,status", [(10.0, 0, "UNKNOWN"), (9.999, 1, "UNSAFE")])
def test_ten_second_cooperative_boundary_preserves_only_completed_evidence(first_tick, checked, status, monkeypatch):
    import clausegraph.verification as verification

    scenario = small_ledger()
    plan = optimize(scenario, [])
    ticks = iter([0.0, first_tick, 10.0, 10.0])
    monkeypatch.setattr(verification.time, "monotonic", lambda: next(ticks))
    result = verify_plan(scenario, [], plan, VerificationRequest(plan_id=plan.id,
        revision=plan.revision, uncertainties=[amount(low=0, high=1)], time_limit_seconds=10))
    assert result.solver_status == "TIME_LIMIT" and result.status == status
    assert result.checked_cases == checked and result.total_cases == 2
    assert not result.coverage_complete and not result.worst_case_proven
    assert (result.counterexample is not None) == bool(checked)


def test_large_eight_dimension_domain_is_exact_and_bounded_by_case_budget():
    scenario = small_ledger()
    scenario.events = [FinancialEvent(id=f"pay-{index}", title="Explicit synthetic income", date=START,
        amount_cents=1, direction="income") for index in range(8)]
    plan = optimize(scenario, [])
    result = verify_plan(scenario, [], plan, VerificationRequest(plan_id=plan.id,
        revision=plan.revision, uncertainties=[amount(event.id, 0, 10_000_000_000)
            for event in scenario.events], max_cases=1))
    assert result.total_cases == 10_000_000_001 ** 8 and result.checked_cases == 1
    assert VerificationResult.model_validate_json(result.model_dump_json()).total_cases == result.total_cases
    assert result.status == "UNKNOWN" and result.solver_status == "CASE_LIMIT"
    assert not result.coverage_complete and not result.worst_case_proven
