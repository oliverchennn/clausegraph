import importlib.util
from pathlib import Path


def test_judge_demo_proves_failure_and_tight_hypothetical_cash_requirement():
    path = Path(__file__).resolve().parents[2] / "scripts/verify_demo.py"
    spec = importlib.util.spec_from_file_location("verify_demo", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.run_demo()
    verification = result["verification"]
    assert result["nominal_minimum_cents"] == 5000
    assert verification["status"] == "UNSAFE"
    assert verification["checked_cases"] == verification["total_cases"] == 8
    assert verification["worst_case_proven"]
    assert verification["counterexample"]["earliest_failing_date"] == "2026-09-26"
    assert verification["counterexample"]["balance_cents"] == -40000
    assert verification["counterexample"]["assignment"] == [{"dimension_id": "payday", "value": "2026-09-27"}]
    assert result["no_safe_schedule_in_declared_model_proven"]
    assert result["minimum_extra_opening_cash_cents"] == 40000
    assert result["same_schedule_with_extra_cash"]["status"] == "SAFE"
    assert result["same_schedule_with_extra_cash"]["worst_case"]["minimum_balance_cents"] == 0
    assert result["same_schedule_with_extra_cash"]["fixed_actions"] == verification["fixed_actions"]
