# Verification API and persistence handoff

Branch: `codex/verify-api`; checkout `.worktrees/verify-api`. API/infrastructure lane owns `api.py`, `storage.py` and `tests/test_verification_api.py`. Integration owns canonical verification schemas, migrations, generated API types and final merged checks. The verification engine is a separate lane.

## Implemented interfaces

- `POST /api/verify`: authenticated `VerificationRequest` to `VerificationResult`. Requires the requested plan ID and revision to match the session's current saved plan. Calls `verification.verify_plan(scenario, rules, plan, request)` without running the nominal optimizer or replacing the active plan. Invalid declared models raised as `ValueError` return HTTP 422; stale or replaced plans return HTTP 409. A session deleted during calculation returns HTTP 401.
- `GET /api/verifications`: authenticated newest 30 results for that session, including their declared assumptions, fixed actions, coverage, solver/runtime status, worst-case series and counterexamples. Runs from older input revisions remain historical results carrying that revision; they cannot authorize verification of an old active plan.
- `Store.save_verification`: acquires a conditional session write lock by updating the revision to its existing value, then rechecks the saved plan ID and revision under that lock. This closes same-revision plan replacement races on SQLite and PostgreSQL while leaving the session JSON and active plan unchanged. Inserts the result and chart points in one transaction.
- `Store.verifications`: rehydrates worst-case daily balances from persisted points while preserving event IDs from the typed result. Missing chart points fail closed. Results retain their original SAFE/UNSAFE/UNKNOWN state.

## Persistence and privacy

`verification_runs` stores `(session_id, id)` as its composite key, `plan_id`, `revision`, `status`, typed result `payload` JSON and `created_at`. `verification_points` stores `(session_id, run_id, series, event_date)` as its composite key, integer `balance_cents`, `income_cents`, `expense_cents` and explicit `kind`. The implemented series is `worst_case`, and every point is projected. Both tables reference the private session with cascading deletion. The API also explicitly deletes both tables for SQLite's local fallback.

Source deletion clears all verification narratives and points for the session, matching existing plan-history privacy behavior. Demo reset and whole-session deletion also clear them. Another session's runs are retained. No source originals, keys, credentials or bearer tokens are included in chart rows. No extra snapshots of deleted source text are retained.

Verification is a separate operation and history from nominal planning. It does not invoke providers, mutate recorded approvals, execute actions or send messages. Uncertainty provenance and bounded guarantees are defined by the canonical schemas and engine; this lane does not infer financial semantics.

## Sponsor audit, 2026-09-19

The audit inspected source, `docs/SPONSORS.md`, migrations, App Platform configuration and effective settings using only configuration-presence booleans. No credentials were printed and no external request or resource provisioning was performed.

- **Tiger Data/PostgreSQL:** SQLAlchemy PostgreSQL persistence, migrations, job leasing and a plain SQL daily financial-event aggregate view are implemented. Verification adds two PostgreSQL-compatible run/time-series tables alongside the SQLite fallback; integration supplies the matching migration. No configured PostgreSQL URL or disposable `POSTGRES_TEST_URL` was available. No Tiger service, Timescale hypertable, continuous aggregate, live database run or performance benchmark was verified. A PostgreSQL-compatible schema does not establish a Tiger-specific integration.
- **DigitalOcean:** App Platform frontend/API/worker/migration-job YAML remains a template with repository and secret placeholders. The private Spaces adapter is implemented; local private files remain the available fallback. Effective Spaces configuration and process DigitalOcean token variables were absent. No deployment, bucket, domain, worker pickup or cloud deletion flow was verified, and no paid service was provisioned.
- **Model configuration:** effective root settings had no NVIDIA or ElevenLabs key; a Gemini key was present. Key presence establishes configuration only. The default selected evidence provider remained NVIDIA. This lane made no provider smoke or inference request and does not claim live Gemini validity.

## Checks and limitations

- Before edits: root `.venv/Scripts/python.exe -m pytest backend/tests/test_api.py -q` from this worktree: **34 passed in 6.82s**, two existing Starlette/AnyIO deprecation warnings.
- Root `.venv/Scripts/python.exe -m ruff check backend/clausegraph/api.py backend/clausegraph/storage.py backend/tests/test_verification_api.py`: **passed**.
- Root `.venv/Scripts/python.exe -m pytest backend/tests/test_verification_api.py backend/tests/test_api.py -q`: **47 passed in 10.22s**, two existing Starlette/AnyIO deprecation warnings. This includes 13 new verification API cases using the real engine checkpoint. Coverage includes SAFE/UNSAFE/UNKNOWN, exact counterexample/history preservation, no nominal optimizer call, unchanged raw session snapshot, wrong/stale/foreign plans, changes during calculation, persisted chart readback and missing-point rejection, newest-30 history, and source/reset/session deletion isolation.
- `git -c safe.directory=C:/Users/vzhu0/PycharmProjects/clausegraph/.worktrees/verify-api diff --check`: **passed**, existing CRLF normalization notices only.

An earlier combined run hit an existing deletion-test flake: `rglob("v*")` matched an empty randomly named document directory beginning with `v`, although the private version file had been deleted. The next full targeted run passed. This was reported to integration for correction of the existing assertion; no unrelated file-store behavior was changed here. A first new-test run also exposed and corrected a test setup issue where the no-optimizer guard covered creation of the second session's nominal plan; the guard now applies only during verification.

Validation used uncommitted copies of integration's canonical `schemas.py` and the engine lane's `engine.py`/`verification.py`; those are testing dependencies and excluded from this lane commit. Integration must merge the canonical contracts and engine, apply migration 003, regenerate OpenAPI/types from these routes and run the complete merged checks.

PostgreSQL locking and migration compatibility must be exercised by integration CI or against an explicitly supplied disposable database; this lane's execution uses SQLite. The API returns only the latest 30 verification records but preserves older records until the existing source/reset/session deletion boundaries. There is no new retention policy, public deployment claim or robust-synthesis endpoint.
