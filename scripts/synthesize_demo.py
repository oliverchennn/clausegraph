"""Reproduce the separate synthetic fixed-schedule synthesis with no providers."""
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))


def main():
    # Windows OR-Tools import diagnostics belong on stderr, keeping stdout JSON.
    with redirect_stdout(sys.stderr):
        from clausegraph.engine import optimize
    from clausegraph.resilient_demo import load_resilient_demo
    from clausegraph.schemas import IncomeDateUncertainty, SynthesisRequest, VerificationRequest
    from clausegraph.synthesis import synthesize_plan
    from clausegraph.verification import verify_plan

    scenario, _, rules = load_resilient_demo()
    nominal = optimize(scenario, rules)
    bounds = [IncomeDateUncertainty(id="resilient-payday", event_id="resilient-paycheck",
        earliest="2026-09-03", latest="2026-09-05", rationale="Synthetic user-declared income delay range.")]
    failure = verify_plan(scenario, rules, nominal, VerificationRequest(plan_id=nominal.id, revision=1, uncertainties=bounds))
    result = synthesize_plan(scenario, rules, nominal, SynthesisRequest(plan_id=nominal.id, revision=1, uncertainties=bounds))
    assert [a.action_id for a in nominal.actions] == ["early-shift"]
    assert failure.status == "UNSAFE" and failure.worst_case.minimum_balance_cents == -5000
    assert result.status == "FOUND" and result.verification.status == "SAFE"
    assert [a.action_id for a in result.candidate.actions] == ["late-shift"]
    assert result.candidate.proposed.minimum_balance_cents == result.verification.worst_case.minimum_balance_cents == 4900
    print(json.dumps({"synthetic": True, "external_calls": 0, "adopted": False,
        "nominal": nominal.model_dump(mode="json"), "nominal_verification": failure.model_dump(mode="json"),
        "synthesis": result.model_dump(mode="json")}, indent=2))


if __name__ == "__main__":
    main()
