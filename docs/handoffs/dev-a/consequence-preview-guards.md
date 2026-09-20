# A / solo orchestrator: consequence preview guards

## Assignment and resumed work

The user authorizes this agent to complete all inactive contributors' required tasks, reviews, fixes and green sequential merges alone. No independent contributor review is claimed.

- Fresh branch/worktree: `codex/dev-a/consequence-preview-guards`, `.worktrees/dev-a-consequence-preview-guards`.
- Starting/fetched main: `e31d415433f3d80120ab3c00b805c20494e1bca6` (PR44). Root main was clean and fast-forwarded. PR44 merged the consumption documentation while this local session was interrupted; its existing handoff is preserved.
- Prerequisites: PR39 design, PR40 C12, PR41 synthesis `c420609`, PR42 UI `b53cb5c`, PR43 C13 `8d16764`, and PR44 documentation contract `e31d415`. PR43's PR run passed 463 backend and 59 browser tests without retries. Its paired push run exposed an existing review-queue response/reload test race, assigned for correction in the next frontend integration task.
- Preserved interrupted work: `.worktrees/dev-a-consequence-walkthrough-contract` remains untouched with its uncommitted API/schema/test and assignment. This new worktree carries forward only those three useful files; the identically named remote branch was already squash-merged and is not reused.
- Allowed paths: `backend/clausegraph/api.py`, `backend/clausegraph/schemas.py`, new `backend/tests/test_consequence_api.py`, generated `docs/openapi.json` and `frontend/src/lib/api-types.ts`, `docs/CONSEQUENCE_WALKTHROUGH.md`, current status in `docs/WORKSTREAMS.md`, `docs/RESUME.md`, `docs/HACKATHON_ASSIGNMENTS.md`, `docs/RESILIENT_PLAN_SPEC.md`, and this handoff. No frontend presentation, dependency, fixture, financial-engine or historical peer-handoff edits.
- Acceptance: preserve PR44's field mapping; add missing preview source-plan provenance and reject in-flight revision/plan/source/deletion races. Source-status changes must not reuse obsolete cached readiness. Preserve source-less previews, private nonmutation, existing engine effects/fees/debt/future obligations and conditional/blocker semantics. SQLite/PostgreSQL regressions, generated drift and full green CI before B consumes this follow-up.

## Results

The user subsequently narrowed scope for imminent submission: finish this in-progress task, verify the MVP and stop. B consequence integration/C14/C15 and optional #5/#6 are deferred, not delivered. This supersedes the earlier full-queue continuation. The existing review-queue browser test retry is not a demonstrated product defect; it passed PR43/44 full CI without retries and its deferred test-only cleanup is not required to ship.

Implemented the additive nullable `preview_source_plan_id`, final revision/active-plan/document-state checks and source-status-aware cache key. Deletion during computation returns 401 and clears any cache entry populated after deletion. No financial algorithm, fixture, approval, saved history or dependency change. Corrected the contract's fixed September 4 wording to use the actual returned execution date (September 1 by default).

Checks with Python 3.12.14, Node 22.23.2/npm 10.9.8:

- Locked `npm ci --no-audit --no-fund`: 439 packages installed, lock unchanged.
- Focused API/demo run: 19 passed / 10 PostgreSQL skips in 9.17s.
- Full backend: 449 passed / 34 PostgreSQL skips in 84.22s; CI runs those database variants.
- Final API rerun after deletion-cache cleanup: 10 passed / 10 PostgreSQL skips in 6.62s. Ruff passed.
- OpenAPI/TypeScript generation, frontend typecheck/lint/production build: passed.
- Core real-API browser smoke: `npm run test:e2e -- workspace.spec.ts resilient-plan-demo.spec.ts cash-gap-demo.spec.ts`, 6 passed in 1.1m using isolated ports 8156/3156. Covers evidence/review/approval, nominal planning, cancellation preview and nonmutation, cash-gap failure/retry, separate resilient adoption/history and 390px/privacy. Final full CI is recorded in the PR review before merge.

Same-agent orchestrator review confirms source identity is attached after cache copying, normal plan persistence retains null preview provenance, source-less previews remain supported, cash infeasibility is separate from authorization, and deletion/stale results fail closed. Full CI is required before merge; no independent reviewer is invented.

Resumption record: initial validation in the interrupted checkout hit an inaccessible host pytest temp directory, then a missing worktree `.data` parent; no application assertion ran for those setup failures. The next command was not executed because automatic approval review exhausted usage; the user explicitly resumed and normal approvals worked. Validation above used isolated worktree temp directories.
