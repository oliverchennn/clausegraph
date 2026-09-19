# Verification frontend handoff

Branch: `codex/verify-frontend`. Checkout: `.worktrees/verify-frontend`. Scope: frontend code and browser acceptance tests; canonical contracts and dependencies remain owned by integration.

## Completed

Added a compact Verify plan panel below the existing cash chart. The form declares an event-specific projected-income date interval and an optional selected-action approval set (approved/denied/pending), all with an explicit user-assumption rationale. Synthetic date presets cover September 21–28 and September 21–26. No uncertain date or outcome is inferred from evidence. The saved action list and execution dates remain fixed and link to the existing evidence drawer.

The result separates SAFE, UNSAFE and UNKNOWN, displays the exact declared assumptions and nominal overrides, inclusive/exclusive horizon, checked/total cases, dimension count, full coverage, solver/runtime status, and revision. Worst-case cash is displayed only when both full coverage and `worst_case_proven` hold. A counterexample presents its assignment, earliest failure (or the encountered failure when coverage is incomplete), server event ledger with evidence/action links, and a red overlay on the existing chart. Unauthorized schedules without a simulation never get a cash overlay. All amounts and balances are server-provided; React only formats them.

Changing the form removes the result and aborts a pending request. Changes to session, revision, or saved plan invalidate results and reset the form. Switching dashboard tabs retains the result's displayed bounds. The nominal solver label now says “Nominal optimum proven,” and the original chart insight explicitly describes the nominal plan. Existing dashboard architecture, synthetic labels and evidence/review flows remain intact.

## Contract

`POST /api/verify` sends canonical `VerificationRequest` (`plan_id`, `revision`, `uncertainties`, `max_cases: 10000`, `time_limit_seconds: 5`) and consumes canonical `VerificationResult`. Aliases import from integration-generated OpenAPI types. Root copied draft `schemas.py` and generated `api-types.ts` into this worktree solely for compilation; neither is included in this lane commit.

No manifests, lockfiles, third-party providers, or live-service configuration changed.

## Checks

- `cd frontend; npm run typecheck`: passed against the current generated verification contract.
- `cd frontend; npm run lint`: passed without warnings.
- `cd frontend; npm run build`: compiled successfully and exited 0. The worktree's shared `node_modules` junction produced the existing Windows EPERM standalone symlink-copy warning; root's physical-dependency build is required for final packaging validation.
- Added three real API Playwright tests in `frontend/tests/verification.spec.ts`: unsafe interval/counterexample/evidence/overlay, safe interval and plan/revision invalidation; approval uncertainty with no unauthorized projection and mobile overflow; UNKNOWN under a deterministic one-case budget. The last test adjusts only the outgoing case budget, then uses the actual FastAPI/verifier response.
- Browser tests are pending root integration at this checkpoint, per integration-owner instruction, because this lane intentionally does not copy the engine/API implementation into its checkout. Existing browser tests remain unchanged. Integration must run `npm run test:e2e` and record actual results.

## Remaining limitations / next steps

The UI exposes one projected-income date interval and one action approval dimension per run. Additional income amount dimensions are supported by the API but have no form controls here. Verification history retrieval and robust synthesis UI are outside this lane. Results are discarded on page reload; no old result is presented as newly checked. The UI asserts safety only inside the displayed model and horizon. Root should run integrated browser/production checks, inspect desktop/mobile rendering, and update the final handoff with those results.
