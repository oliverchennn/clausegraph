# Verification engine handoff

Branch: `codex/verify-engine`; checkout `.worktrees/verify-engine`. Root assigned this lane through the live agent board. This lane owns `engine.py`, `verification.py`, `test_verification.py` and this handoff. Canonical schema additions are root-owned and deliberately excluded from this commit.

## Implemented

`verify_plan(scenario, rules, plan, request) -> VerificationResult` checks the saved action IDs and execution dates without invoking optimization. `check_fixed_plan(...) -> FixedPlanCheck` exposes its concrete-state check for deterministic diagnostics. Required approval outcomes are concretized only on deep copies; pending and denied never authorize execution. Explicit nominal approval overrides remain displayed hypothetical assumptions; merely enabling a conditional nominal plan does not authorize an unresolved action.

The solver is an exhaustive finite model checker. This choice reuses the existing executable financial semantics and adds no solver dependency: every calendar date in a closed date interval, every integer cent in a closed amount interval and every declared finite approval outcome is checked. Mixed-radix enumeration avoids allocating large ranges. Dimension order and assignments are deterministic. On full coverage, the counterexample has the earliest failing date among the evaluated cases, with the first lexicographic assignment breaking ties. Incomplete searches disclose that earlier failures may exist.

Nominal CP-SAT and verification share `_prepare_ledger`, `_gates`, evidence validators, `_action_changes`, `_materialize` and `simulate`. The refactor preserves nominal optimizer behavior. All accounting still comes from the existing integer-cent materialization/simulation. Verification adds field-specific evidence validation so an uncertain income date cannot excuse an unsupported amount, or an uncertain amount an unsupported date. Unreviewed/missing ledger evidence prevents SAFE, even when the optimizer conservatively withholds that income. Essential protections, unique event writers, prerequisite ordering, mutually exclusive actions, execution windows and retained future debt use the existing canonical checks.

## Contracts and statuses

The root-owned uncertainty contract accepts user assumptions with a rationale; this MVP does not claim that a model inferred or verified source-backed ranges. Event-specific income dimensions can address multiple projected income events. Actual/historical income, expense targets, unknown targets and income dates preceding the horizon are rejected. The horizon is the nominal saved plan's `[start, start + horizon_days)` interval. Plan ID/revision must match.

`SAFE` requires complete coverage and fully resolved facts in every case. A concrete safety violation yields `UNSAFE` even if a later time/case limit interrupts enumeration. With no witness, incomplete or unresolved work yields `UNKNOWN`. Runtime status independently reports `EXHAUSTED`, `TIME_LIMIT`, `CASE_LIMIT` or `INVALID_MODEL`. The deadline is checked between cases. Unauthorized schedules have no permitted cash simulation or fabricated balance. The reported worst case is proven only when all states are fully simulated; partial/invalid coverage explicitly labels any observed balance as limited to evaluated authorized states.

Counterexamples include the exact assignment, failure property/date, available balance and simulation, materialized events, action IDs and source rule IDs. Future events remain present, including device principal relocated exactly once on cancellation. The result retains a deep copy of the nominal assumptions, bounded request and fixed actions. API/history/frontend integration is owned by the other lanes; this lane makes no persistence, sponsor, deployment or live-provider claim.

## Exact checks (2026-09-19)

Using root `.venv/Scripts/python.exe`, `PYTHONPATH=backend`, cwd this checkout:

- `-m pytest backend/tests/test_engine.py backend/tests/test_demo.py -q` immediately after the shared-ledger refactor: **52 passed in 1.88s**.
- `-m pytest backend/tests/test_verification.py backend/tests/test_engine.py backend/tests/test_demo.py -q`: **100 passed in 2.96s**.
- `-m pytest backend/tests -q`: **188 passed, 1 skipped in 11.25s**. PostgreSQL test skipped without `POSTGRES_TEST_URL`; two existing dependency deprecation warnings. This checkout does not yet contain the new API-lane tests.
- `-m ruff check backend/clausegraph/engine.py backend/clausegraph/verification.py backend/tests/test_verification.py`: **passed**.

The 48 verifier tests include ten independent small-ledger exhaustive oracles, safe/unsafe full ranges, deterministic earliest witnesses, every-cent enumeration, huge-domain bounded memory, timeout before any proof and after a concrete witness, case limits, pending/denied action and rule approvals, conditional nominal assumptions, input immutability/JSON roundtrip, source-field masking, horizon boundaries, multiple incomes, essential preservation, dependency/window failures, duplicate actions/debt, cancellation principal relocation and fixed verification versus reoptimization. Existing synthetic demo arithmetic is unchanged.

## Limitations / next steps

Root must integrate the schemas and lane commits, regenerate contracts and run API/browser/full-stack checks. Enumeration is intentionally bounded to the request's maximum 10,000 cases and time budget, with no claim beyond declared assumptions/horizon. Monetary ranges have one-cent granularity and can exhaust the budget quickly. No payment-date uncertainty, symbolic interval compression, generalized robust action synthesis, probabilities or real-world guarantee is implemented. Root is developing a separate bounded demo diagnostic; this module itself never reoptimizes or invents funding. A removed/nonessential payment is allowed only through the existing evidence-backed action semantics. Missing or contradictory facts remain review blockers rather than assumed truth.
