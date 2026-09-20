# C15 / solo orchestrator: final demo

## Assignment before implementation

The user authorized solo completion, urgent deployment and merge after green checks. Contributor identity is C in the dev-b lane. Fresh branch/worktree: `codex/dev-b/c-final-demo`, `.worktrees/dev-c-final-demo`, starting at merged C14 PR48 `1251201328dba747187414432ee8216c19f59b91`.

Allowed paths from `docs/DEV_C.md`: update `frontend/demo/presenter-cues.md`, `frontend/demo/fallback-runbook.md`, `frontend/demo/rehearsal-log.md`, `frontend/demo/consequence-demo.md`; add `frontend/tests/demo-story.spec.ts` and this handoff. No runtime, backend, shared state, central docs, fixtures, dependencies, provider calls or deployment changes belong to C15.

Acceptance: one honest source → review → nominal plan → bounded failure → cash diagnostic → original-domain no-solution → separately labelled resilient success/adoption → consequence story; desktop and 390px real-API regression; keyboard and recoverable failure; current offline fallback; automated timing kept distinct from human spoken rehearsal.

## Result

The cue sheet now describes six implemented beats totaling a proposed 180 seconds. It preserves the original problem's NO_SOLUTION outcome and switches explicitly to the separate three-document resilient fixture before showing a verified/adopted alternative. The final beat returns to a new original synthetic session for the $60 removal / same $480 accelerated debt consequence.

The desktop regression drives every beat through the real FastAPI application and asserts the returned financial/proof fields. The 390px pass injects one 503 only to exercise visible failure and keyboard retry, then checks the consequence stepper and horizontal layout. The runbook covers both offline reports, reset/recovery and exact acceptance values.

## Validation and limits

Pinned Node 22.23.2/npm 10.9.8 validation on the exact branch content:

- `npm ci`: 440 locked packages installed, 0 vulnerabilities.
- `npm run typecheck && npm run lint && npm run build`: pass.
- `npm run test:e2e -- demo-story.spec.ts`: 2 passed; desktop functional path 3.55 seconds without narration holds.
- Full `npm run test:e2e`: 66 passed in 2.0 minutes; desktop functional path 2.56 seconds in that run.
- `python scripts/verify_demo.py` and `python scripts/synthesize_demo.py`: pass; both emitted valid JSON fallback reports.
- `git diff --check`: pass before commit.

Final commit and remote CI are recorded on the pull request before merge. No human spoken run was available, so presentation timing remains unverified. No provider, cloud, real document or external financial action occurs in C15. Deployment is a separate user-authorized A/orchestrator action after this task merges.
