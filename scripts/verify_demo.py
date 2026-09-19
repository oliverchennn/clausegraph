"""Synthetic bounded verification demo and a CP-SAT impossibility certificate."""
import json
import sys
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from clausegraph.demo import load_demo  # noqa: E402
# OR-Tools 9.12 emits Windows DLL-loader messages during import. Keep the
# reproducible report's stdout valid JSON while retaining diagnostics on stderr.
with redirect_stdout(sys.stderr):
    from clausegraph.engine import optimize
from clausegraph.schemas import IncomeDateUncertainty, PlanRequest, VerificationRequest  # noqa: E402
from clausegraph.verification import verify_plan  # noqa: E402


def run_demo() -> dict:
    scenario, _, rules = load_demo()
    nominal = optimize(scenario, rules)
    uncertainty = IncomeDateUncertainty(
        id="payday", event_id="paycheck", earliest=date(2026, 9, 21), latest=date(2026, 9, 28),
        rationale="Synthetic user assumption: the projected paycheck may arrive on any date September 21–28 inclusive.",
    )
    request = VerificationRequest(plan_id=nominal.id, revision=nominal.revision, uncertainties=[uncertainty])
    verification = verify_plan(scenario, rules, nominal, request)
    # This is a separate nominal optimization at a concrete allowed assignment.
    # If even its proven optimum is negative, no fixed robust schedule can be safe.
    witness = optimize(scenario, rules, PlanRequest(income_date=uncertainty.latest))
    impossible = witness.objective_proven and witness.solver_status == "OPTIMAL" and witness.state == "infeasible"
    cash = witness.proposed.additional_cash_required_cents if impossible else None
    funded_verification = None
    if cash is not None:
        # Verify the SAME action schedule with explicitly hypothetical extra cash;
        # do not add income, claim funding, or synthesize new permissions.
        funded = nominal.model_copy(deep=True)
        funded.assumptions.opening_balance_cents = scenario.opening_balance_cents + cash
        funded_verification = verify_plan(scenario, rules, funded, request)
    tight = impossible and funded_verification is not None and funded_verification.status == "SAFE"
    return {
        "mode": "synthetic_no_external_calls",
        "nominal_minimum_cents": nominal.proposed.minimum_balance_cents,
        "verification": verification.model_dump(mode="json"),
        "no_safe_schedule_in_declared_model_proven": impossible,
        "proof": {
            "allowed_payday_assignment": uncertainty.latest.isoformat(),
            "operation": "separate_nominal_optimization_at_one_allowed_assignment",
            "solver_status": witness.solver_status, "objective_proven": witness.objective_proven,
            "best_possible_minimum_cents_at_assignment": witness.proposed.minimum_balance_cents,
            "reason": "If every permitted schedule fails at one allowed assignment, no schedule is safe for every assignment.",
        },
        "minimum_extra_opening_cash_cents": cash if tight else None,
        "extra_cash_is_hypothetical_not_funding": True,
        "same_schedule_with_extra_cash": funded_verification.model_dump(mode="json") if funded_verification else None,
        "robust_synthesis_implemented": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
