# Developer B: read-only history UI (task 6)

## Assignment and scope

User approved B task 6 after confirming PR20 and PR21 were merged. This implements the history presentation described by A's merged `docs/HISTORY_CONTRACT.md` and roadmap row 6; it does not start row 7 or 8.

Branch: `codex/dev-b/history-ui`; isolated worktree: `.worktrees/dev-b-history-ui`.
Starting main: `a00af572cc20afea6893e0e261272bb919aed11f` (PR21). Required history contract: `7088b812c1da4169b1ad4b4d668bf2536e68e43d` (PR19). PR20 uncertainty guidance is also merged as `c32f0c8b7c81be1ed2da00ac19a18b414489f499`.

Allowed files: `frontend/src/components/saved-history.tsx`, `frontend/src/app/page.tsx`, `frontend/src/app/globals.css`, `frontend/src/lib/api.ts`, `frontend/tests/history.spec.ts`, and this handoff. Existing generated contracts, manifests/locks, backend, fixtures, scripts and shared documentation remain A-owned. No C paths are released by this task.

## Acceptance

- Read both authenticated history routes without running or restoring a plan; preserve server ordering and explain the independent latest-30 limits.
- Distinguish plan IDs from revisions and active from inactive same-revision records using a refreshed workspace.
- Show saved plan assumptions, solver/proof state, warnings, cash series, decision traces and future obligations; show verification assumptions, fixed actions, coverage/proof flags and saved witnesses without substituting current evidence.
- Clear displayed records/selection on session changes and privacy operations; discard obsolete requests, surface incomplete-read errors with retry, and handle session loss.
- Verify real API persistence/nonmutation, proof and revision labels, privacy races, errors/empty/loading states, keyboard navigation and 390px layout. Run typecheck, lint, build, full browser tests and ownership/current-main checks before publication.

## Implementation

Added a History workspace tab and navigation item. It loads `/workspace`, both history routes in parallel, then `/workspace` again before publishing the records. Changed revision/active-plan identity during the read produces a retryable error instead of classifying a mixed snapshot as current. Lists retain server order and use full record IDs; the first row is never assumed to be the active plan. Active labels explicitly mean "when refreshed"; this is not a live subscription or an atomic server snapshot.

Plan details render saved nominal overrides, conditional state, solver status/runtime and objective proof, baseline/proposed chart and daily balances, retained future obligations, action explanations, before/after decision traces and warnings. Verification details render stored nominal and uncertainty assumptions, fixed actions, finite horizon, coverage/termination, saved counterexamples and cash, worst-case assignment and proof qualifiers. Totals beyond JavaScript's exact integer precision are explicitly qualified. Missing associated plans do not hide the verification's independent records.

History never calls a calculation/save/restore endpoint. Historical references display saved IDs and saved event content, without resolving them against current rules/documents. An assumed opening balance remains explicitly hypothetical even when state is confirmed. Privacy confirmation text now names history deletion. History unmounts at workspace-operation start, clearing selection/data and aborting its requests; it remounts with a fresh read afterward. Session/revision/active-plan identity changes also replace the component. A typed API error permits 401 to clear the unavailable private session rather than treating it as empty history.

## Validation and limits

All local commands use the shared Python3.12.14 environment and pinned Node22.23.2/npm10.9.8. `npm ci --no-audit --no-fund` installed 439 locked packages; existing dependency deprecation notices were not dependency changes. Existing shared pre-push hook was confirmed by `scripts/install_hooks.py` without replacing custom hooks.

- Typecheck and ESLint: passed.
- Production build: passed; first-load JS149kB.
- Eight new real-API browser cases cover identity/order/nonmutation, saved proof states after input edits, latest-30 independent lists, partial authorization witnesses, large counts, failed/empty reads, concurrent reset detection, deletion/reset/session replacement races, 401, keyboard selection and 390px overflow. Initial test runs caught incorrect fixture IDs/execution-date expectations and a missing required review field in test setup; those test inputs were corrected to the existing contract.
- Final `npm run test:e2e` with `E2E_API_PORT=8116` and `E2E_WEB_PORT=3116`: **19 passed in 1.7m** (eight history cases plus all 11 existing browser cases). Final typecheck/lint also passed after the test-fixture corrections.
- Inspected desktop1280px and mobile390px saved-plan screenshots, including persisted cash charts, trace details and future obligations. Keyboard selection and mobile overflow checks passed. Screenshots are ignored artifacts under `frontend/test-results/history-desktop.png` and `history-mobile.png`.
- `git diff --cached --check`: passed. Fetched origin again before publication: main remained `a00af57`; A's open release-readiness PR22 changes shared docs independently. Final commit ownership/current-main and CI results will be recorded on the PR; A's review is still required.

The stack uses only this worktree's synthetic SQLite database/documents and ports8116/3116. User sessions, A's worktree, the user's running local app and cloud services are not used. No provider processing or live extraction is claimed. Browser failure and race tests inject HTTP failures or delay actual responses; successful financial/history content comes from the real local API.

Thirty remains a response limit, not retention or pagination. No history restore, delete-one-record, new API/schema, money calculation, richer uncertainty controls or robust synthesis was added. Shared roadmap/checkpoint docs remain A-owned. Stop after publishing this task for A review; do not start task7 without a separate assignment.
