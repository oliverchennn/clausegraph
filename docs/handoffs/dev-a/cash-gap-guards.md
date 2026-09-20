# Developer A: cash-gap integration guards

## Assignment before implementation

The user requested the next Developer A task. Synchronized clean root main and fetched/pruned origin; PR29 (cash-gap contract), PR30 (incomplete-source guard), and PR31 (35/35/30 assignments) are merged. Stage 1 B UI/C11 integration is still pending, so this task supports the current cash-gap stage rather than starting stage 2 implementation. Inspection found that `/api/cash-gap` omits PR30's incomplete-source gate and checks the current plan only before computation. Reproduce and correct these bounded API integration gaps before B consumes the result.

Starting commit: `8fa1279c61e702d82f2adb80729f082bfcbc892e` (PR31). Branch: `codex/dev-a/cash-gap-guards`; worktree: `.worktrees/dev-a-cash-gap-guards`. Required merged contracts: PR29 `b5d9204a62ba854cfd82c1a8bf90ca90b0adf174`, PR30 `5e79c1d7b571a0c67bc0bb41e70cd0be405265e5`; both are ancestors of the start. Existing branches, worktrees, uncommitted work and running services are preserved.

Allowed files: `backend/clausegraph/api.py`, `backend/tests/test_cash_gap_api.py`, `docs/WORKSTREAMS.md`, `docs/RESUME.md`, and this handoff. No financial algorithm, schema/generated type, storage schema, dependency, fixture, frontend implementation or peer handoff changes are assigned.

Acceptance: incomplete uploaded/extracting/failed/unrepresented sources reject the cash diagnostic before computation; represented sources retain normal evidence/review gates; another session's incomplete sources do not block this session. A revision change, replaced or absent active plan, source/session deletion or reset during computation must withhold the stale result. Rejections and successful diagnostics must not mutate the saved plan, workspace or either history. Preserve the eight-date 40000-cent proof and original offline fallback. Record red-before/green-after regressions, full backend/Ruff, schema drift, documentation/ownership/current-main checks and required CI. Publish a fresh PR for B review, then stop; no self-merge, later stage, provider call or deployment.

## Results

Reused the existing `incomplete_sources` predicate at `/api/cash-gap`, before its engine call. Uploaded, extracting, failed, empty-extraction and old-version-only sources now return HTTP 409 with processing/recalculation guidance. This applies even to a historical plan labeled confirmed. Represented sources awaiting human review still reach the existing conservative engine gates; this API check does not conflate processing completion with evidence validity, review or approval.

After computation, the endpoint rereads the private workspace and checks input revision plus active plan ID/revision. In-flight input edits, same-revision plan replacement/removal, source deletion and demo reset discard the result with HTTP 409; session deletion returns HTTP 401. It does not save diagnostic/verification history, adopt a plan, overwrite a concurrent edit or change opening cash. Another session's changes do not invalidate this session's diagnostic.

The final read checks changes observed before the response is returned; it is not a lock spanning network delivery or a substitute for B's request/session/plan/assumption invalidation. No schema, generated type, money calculation, proof algorithm, budget or solver behavior changed. B consumes the existing response/error contract after merge and should show the 409 guidance without presenting a stale cash amount.

## Validation

Python 3.12.14 from the existing root `.venv`; tests use this isolated checkout and disposable SQLite databases. Hook installer succeeded with the existing managed hook. No local PostgreSQL test URL is configured.

| Check | Result |
|---|---|
| New regressions against unchanged API | 12 failed, 8 passed in the endpoint suite (8.51s). Failures included `PROVEN_MINIMUM` with incomplete sources, `NOT_REQUIRED` after an unprocessed upload, and success after all six in-flight mutations. A test's initial session-delete status expectation was corrected to the existing HTTP 200 contract before this red run. |
| `python -m pytest backend/tests/test_cash_gap_api.py backend/tests/test_cash_gap.py -q` after correction | 33 passed in 9.40s; includes 14 added cases and stronger whole-workspace/history nonmutation assertions. |
| `python -m pytest backend/tests -q` | 381 passed, 9 PostgreSQL skips in 54.56s; two existing Starlette/AnyIO deprecation warnings. |
| `python -m ruff check backend scripts` | Passed. |
| Canonical `create_app().openapi()` versus `docs/openapi.json` | Exact match; schemas/generated types untouched. |
| `python scripts/verify_demo.py` | Valid JSON; original eight-date UNSAFE result, 40000 hypothetical cents and identical schedule SAFE preserved. |
| `python scripts/eval_nemotron.py` (offline) | Valid JSON; five expected semantic-gate results pass, no live inference. |
| Pre-publication synchronization | Fetched/pruned again; main remains `8fa1279`, no open peer PR at that check. |

Reports are in ignored `.data/validation/`. Frontend source/contracts are unchanged; browser/build/platform and PostgreSQL validation remain the normal full PR CI checks, not claimed as locally rerun. Final local checks passed: exactly five assigned A-owned paths under the fetched base policy, 31 resolving relative documentation links, unchanged canonical/generated contracts, current-main ancestry, no conflict markers/trailing whitespace, and `git diff --check`. The installed pre-push hook also enforces the committed handoff/ownership/current-main checks during publication.

## Handoff and limits

Publish this correction for B's independent review and full CI. No merge is authorized until those gates pass. The current assignment stops at this PR; stage 1 UI/C11 remain pending, and stage 2 feature implementation has not started. Preserve PR29/30's historical handoffs and the 35/35/30 split. No live provider requests, external documents, paid resources, user-service restarts, frontend writes or deployments occurred. Successful live extraction and human spoken rehearsal remain outstanding as previously recorded.
