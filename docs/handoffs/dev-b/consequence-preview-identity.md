# Developer B: consequence preview identity completion

## Assignment before implementation

User-approved solo completion remains active. Fresh branch/worktree `codex/dev-b/consequence-preview-identity`, `.worktrees/dev-b-consequence-preview-identity`, starts at merged main `1bfe9cdfcd21b4f18e9dcb6134f87e7a5e7c1b1b` (PR46). Required contracts: PR45 stale-preview guards `620f3a1` and PR46 integration `1bfe9cd`. This bounded correction owns `frontend/src/app/page.tsx`, new `frontend/tests/consequence-integration.spec.ts`, and this handoff only. C14 remains untouched until this merges.

Acceptance: consume `preview_source_plan_id`; reject delayed results after session/revision/plan changes or a newer request; clear comparisons on draft changes; handle backend 401/409 without stale private content; preserve generic/action preview behavior and the C14 seam.

## Result

The shared preview helper captures private session, workspace revision and saved plan ID, binds each request to a monotonically increasing generation, and accepts a response only when both current local identity and returned `preview_source_plan_id`/revision still match. A newer request, workspace replacement or draft edit invalidates the generation. HTTP 401 uses the existing private-session loss path; HTTP 409 becomes refresh/retry guidance with no comparison.

Focused real-API tests delay an actual backend response, replace the saved plan at the same revision, and prove the obsolete action comparison/walkthrough never appears. They also prove a scenario draft clears an existing action walkthrough and a generic preview never mounts the action-only seam. Exact checks and the external GitHub Actions billing limit are recorded before integration.

## Validation

- Pinned Node 22.23.2/npm 10.9.8 locked install: passed.
- `npm run typecheck`, `npm run lint`, `npm run build`: passed.
- `E2E_API_PORT=8157 E2E_WEB_PORT=3157 npm run test:e2e -- consequence-integration.spec.ts workspace.spec.ts`: **4 passed**, real local API/Chromium, including the same-revision delayed-response race and desktop/mobile baseline.
- `git diff --check`: passed. GitHub-hosted jobs currently cannot start because the repository account reports a payment/spending-limit block; this task does not relabel that infrastructure failure as a test result.

No provider, live extraction, external financial operation, deployment or human rehearsal occurred.
