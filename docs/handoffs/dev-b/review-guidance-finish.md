# Developer B: review guidance completion

Branch: `codex/dev-b/review-guidance-finish`

Starting commit: `4e2725a9405a75b07cbcedf81e2428d2a80e7bdd` (`origin/main`).

## Assignment

Finish and validate the review-guidance frontend that was merged from draft PR7. The backend review-queue contract from PR6 is already present in the starting commit.

Allowed writes are this handoff plus Developer B-owned frontend presentation, state, styles, accessibility, and browser tests. Do not edit frontend manifests or locks, generated API types, `.npmrc`, `Dockerfile`, backend code, fixtures, scripts, CI, shared documentation, or Developer A handoffs.

## Acceptance checks

- Review-queue navigation opens the correct evidence and preserves a failed review before a valid save refreshes the workspace.
- Loading failures are retryable and the mobile review flow is keyboard accessible without horizontal overflow.
- Stale revision and stale session responses cannot replace current queue guidance.
- Recorded denied/pending decisions, missing/deleted sources, missing fact inputs, and an empty private session remain distinct and understandable.
- Existing preview and verification flows continue to pass.
- Run frontend typecheck, lint, production build, and the complete Playwright suite with pinned Node/npm versions.

## Initial evidence

On the starting commit, typecheck, lint, and production build pass. The complete browser suite reports 9 passed and 2 failed: the primary evidence-review workflow times out locating the review control, and the one-shot aborted queue request does not produce the expected retry state. These failures will be reproduced and resolved without provider credentials.

## Completed work

- Replaced ambiguous implicit-label selectors with exact accessible role/name selectors for the evidence-review combobox and review-note textbox. The retained failure snapshot showed both controls in the accessibility tree; the original selectors were the failure point.
- Made the queue-failure scenario deterministic across React development Strict Mode. The route now returns a synthetic `503` until the test explicitly enables recovery and presses **Try again**, rather than aborting only the discarded first effect request.
- Added the repository root's shared POSIX virtual environment to Playwright's Python candidates. Required macOS/Linux worktrees can now run the documented browser-test command without a manual `PYTHON_EXECUTABLE` override, matching the existing shared Windows worktree lookup.

## Final validation

All checks ran from this task worktree with Node `22.23.2`, npm `10.9.8`, Python `3.12`, blank provider credentials, isolated SQLite storage, and local ports only.

- `npm ci --no-audit --no-fund`: passed, 440 packages installed from the existing lockfile; no manifest or lockfile changes.
- `npm run typecheck`: passed.
- `npm run lint`: passed.
- `npm run build`: passed; `/` is a static route with 145 kB first-load JavaScript.
- `E2E_API_PORT=8005 E2E_WEB_PORT=3005 npm run test:e2e`: **11 passed in 21.3 seconds**. This includes all six queue scenarios, all three fixed-plan verification scenarios, the full synthetic workspace flow, and the mobile overflow regression.
- `git diff --check`: passed.

No external provider call, live extraction, document upload, audio generation, deployment, or other key-dependent behavior was exercised. Synthetic fixtures remain clearly separate from live-provider validation.
