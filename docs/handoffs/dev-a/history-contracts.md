# Developer A: history and deletion contract validation

## Assignment

The user's "Start next task" continues A's ordered work after merged integration-validation PR18. This is row 6's backend validation of the existing plan/verification history and deletion contracts. It does not assign B's history UI, rehearsal, richer uncertainty controls or robust synthesis.

Branch: `codex/dev-a/history-contracts`. Worktree: `.worktrees/dev-a-history-contracts`.
Starting and required main commit: `f23133bd7828186edfd72caf367be99a3201d33d` (PR18); no unmerged dependencies. The local test app on ports 3000/8000 remains on main and is not used for these tests.

Allowed files: `backend/clausegraph/storage.py`, `backend/clausegraph/api.py`, `backend/tests/test_history_api.py`, `backend/tests/test_api.py`, `backend/tests/test_verification_api.py`, `backend/tests/test_postgres.py`, this handoff, `docs/HISTORY_CONTRACT.md`, `docs/WORKSTREAMS.md` and `docs/RESUME.md`. Runtime edits are limited to defects demonstrated by history/deletion validation. No public schema/API expansion, migration, dependency, frontend or other contributor handoff edits are assigned.

## Acceptance

- Document authenticated read-only history routes, newest-30 behavior, retained older records, plan IDs versus revisions, assumption/proof labels, and read failures.
- Verify historical results survive active-plan replacement/input revisions without becoming current permissions; previews and reads do not save history or change the active plan.
- Verify source deletion, reset and session deletion remove private history and chart data while preserving another session; cover records beyond the returned 30.
- Verify persistence/order and relevant behavior across SQLite and the CI PostgreSQL test service. No connection to the user's configured cloud database or local test app.
- Add meaningful regression coverage for uncovered contract behavior and fix only reproduced backend defects. Run affected/full backend tests, Ruff, schema drift, ownership and documentation checks; publish for B review.

## Initial state

Fetched origin with pruning; clean main already matched `f23133b`. Historical worktrees and all existing changes are preserved. Existing verification API tests cover stored proof states, revision races, newest-30 verification history and basic deletion isolation. Plan-history ordering currently has no tie breaker, unlike verification history; the contract audit will test this alongside cross-revision and beyond-limit deletion behavior.

## Results

Implemented one reproduced runtime correction: `Store.history` now orders equal persistence timestamps by descending plan ID, matching verification history's deterministic tie handling. The new tied-timestamp test failed before this change (returned insertion order), then passed in the full suite. This stabilizes which records fall within the newest-30 response without claiming chronological meaning for IDs.

Added eight history contract cases, each parameterized for SQLite and the disposable PostgreSQL CI service. They cover authenticated/nonmutating reads, plan identity versus revision, saved assumptions and stale verification rejection, preview/cache behavior, durable chart readback and missing-row failure, retention beyond 30, and full source/reset/session purges with another session preserved. Tests create and delete only their own synthetic sessions. PostgreSQL setup reads only explicit `POSTGRES_TEST_URL`, never the user's configured cloud database.

Published consumption guidance in [HISTORY_CONTRACT.md](../../HISTORY_CONTRACT.md), including independent history limits, inactive same-revision results, hypothetical opening cash, historical proof limits, deletion invalidation and stale-response handling. Updated only A's current board/checkpoint and this task handoff. No API/schema/generated-type, migration, dependency, financial engine or frontend change was needed.

| Check | Result |
|---|---|
| Baseline `python -m pytest backend/tests/test_verification_api.py backend/tests/test_api.py -q` | 48 passed in 12.96s |
| Regression before fix: `python -m pytest backend/tests/test_history_api.py -q` | 1 failed (plan timestamp ties), 7 passed, 8 PostgreSQL variants skipped in 12.35s |
| Final `python -m pytest backend/tests -q` | 306 passed, 9 skipped in 41.44s; two existing Starlette/AnyIO deprecation warnings |
| `python -m ruff check backend scripts` | Passed |
| Compare `app.openapi()` with parsed `docs/openapi.json` | Exact equality; no public contract drift |
| `git diff --check` | Passed; existing Windows line-ending notices only |

Commands use the shared Python 3.12.14 environment at the root `.venv/Scripts/python.exe`. The nine local skips are the existing PostgreSQL integration test and the eight new history variants because no local `POSTGRES_TEST_URL` is configured. CI runs them against PostgreSQL 17, plus schema/type drift, frontend typecheck/lint/build, real-API browser tests and Linux/Windows/macOS clean installs. Final CI results belong to the PR's exact commit; a local skip is not PostgreSQL evidence.

Fetched origin with pruning again before publication; main remains `f23133b`. The root local test app on ports 3000/8000 remains untouched. No live providers, user sessions, cloud resources or paid provisioning were used. Existing dirty worktrees are preserved.

## Review and stop condition

A self-review found no further defect within the assigned contract scope. B's independent review and green CI are required before merge; neither is claimed by the implementation commit. This task does not implement B's history UI, complete B's rehearsal/visual sign-off, add uncertainty controls or start robust synthesis. Stop here and publish for review.
