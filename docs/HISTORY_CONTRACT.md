# Saved plan and verification history

This is the backend consumption contract for a separately assigned B history UI. It describes existing routes and the deterministic plan-ordering correction in A's [history-contracts task](handoffs/dev-a/history-contracts.md). B must start from main after that task merges. No new schema, pagination, restore operation or frontend implementation is included.

## Read routes and identity

| Route | Response | Ordering |
|---|---|---|
| `GET /api/history` | `PlanResult[]`, at most 30 | Persistence `created_at` descending, then plan `id` descending |
| `GET /api/verifications` | `VerificationResult[]`, at most 30 | Verification `generated_at` descending, then verification `id` descending |

Both routes require the private session bearer token, return only that session's records, and send `Cache-Control: no-store`. Missing, invalid or deleted sessions return 401. A successful empty array means no saved results for that route. Reads do not run the optimizer/verifier, save a result, change the active plan or increment the input revision.

Thirty is a response limit, not a retention limit. Older rows and chart points remain stored until an applicable deletion/reset. There is no cursor, total count or endpoint for retrieving the remaining entries. Present these lists as the latest 30 available records, not the entire session's history. Timestamp ties use IDs only to make selection stable; they do not establish a finer chronological order. Plan persistence time is not exposed separately from its `generated_at`, so preserve server ordering rather than sorting by displayed timestamps.

Use `id` as the plan identity. `revision` identifies the workspace inputs; several plans with different assumptions can share a revision. Verification records have their own `id` and refer to a plan through `plan_id` plus `revision`. The two history lists are independently limited, so a verification's plan may fall outside the returned plan list. Its stored nominal assumptions and fixed actions remain available in the verification record.

Saving a plan makes it active without incrementing the input revision. Saving the same cached plan again can reactivate its existing ID without moving its history position. Thus the first history row is not necessarily the active plan. Read `workspace.plan.id` and `workspace.revision` to identify current state. A scenario preview saves no history, even though its result may be cached for a later explicit plan save. Browsing history must not call `POST /api/plan` or `POST /api/verify`.

Input edits invalidate the active plan and increment the revision while retaining historical results, except for the privacy operations below. There is no restore/select-historical-plan API. `POST /api/verify` accepts only the current active plan ID and revision; a stale or foreign plan returns 409. The store rechecks both before persisting an in-flight result.

## Historical labels and financial meaning

Show each plan's saved revision, generation time, `assumptions`, state, solver status, objective proof flag and warnings. Display its stored baseline/proposed series, decision traces and beyond-horizon obligations. Never reconstruct past cash from today's rules or compute new money in the browser. An assumed opening balance remains hypothetical even if the saved plan state is `confirmed`; that state is not evidence of funding.

Show each verification's saved plan ID/revision, `nominal_assumptions`, uncertainty `assumptions`, fixed actions, horizon, status, solver termination, coverage, warnings and proof flags. A historical SAFE result concerns that fixed schedule and declared finite model only. UNSAFE needs its saved counterexample; UNKNOWN is not success. Keep nominal optimality separate from verification proof, and qualify worst-case/earliest-failure claims with their stored proof flags. [Verification semantics and limits](handoffs/verification.md) remain authoritative.

Old results are records of what was checked, not current approval, current evidence validity or permission to execute an action. A source/rule reference may no longer match current reviewed content after an edit. Label historical references accordingly; do not substitute today's source text as if it proved the older result. Synthetic results must remain visibly synthetic using the session context.

## Deletion and failure handling

| Operation | Effect on the affected session's history |
|---|---|
| `DELETE /api/documents/{id}` | Purges all saved plans, verifications and their chart points, including records beyond the latest 30; invalidates the active plan and advances revision |
| `POST /api/demo/reset` | Purges all old history/chart points and restores the synthetic workspace at a newer revision |
| `DELETE /api/session` | Deletes the private session and all its saved history/chart points; subsequent authenticated reads return 401 |

Source deletion clears the whole session's history because stored narratives may contain source content. It is not limited to records visibly linked to that document. Other sessions are unaffected, including when run IDs coincide. These operations also clear the affected session's in-memory plan cache. Source deletion preserves essential obligations with missing-evidence handling; deleting evidence never makes the debt disappear.

Chart money/date rows are authoritative on read; event provenance remains in the saved payload. An incomplete persisted chart fails with HTTP 500 rather than substituting duplicate JSON points, showing a partial success, or returning an empty history. Surface an error and allow a retry. A history read is not an atomic snapshot of both routes and workspace: concurrent edits/deletions can invalidate an in-flight response or make it fail.

B's UI must discard responses from an obsolete session or request generation, refresh the active workspace before classifying a record as current, and clear history selection/rendered data when deletion/reset starts or succeeds. Do not let an earlier successful response repopulate deleted history. Handle 401 as session loss, and handle a 409 from an explicitly requested verification as a stale-plan refresh. No server-side history read may trigger financial execution or external processing.

## Validation boundary

`backend/tests/test_history_api.py` exercises both routes using SQLite and, when `POSTGRES_TEST_URL` is supplied, the disposable CI PostgreSQL service. It covers authentication, nonmutation, plan identity versus revision, preview/cache behavior, stored assumptions, tied timestamps, newest-30 retention, durable chart readback, incomplete-chart errors, and source/reset/session deletion beyond the response limit with another session preserved. Existing API and verification tests cover proof states and in-flight save races.

These checks use synthetic fixtures and local/test databases. They do not validate a deployed service, live providers, a history UI or a timed demo rehearsal. Exact commands, results and pending review are in the task handoff.
