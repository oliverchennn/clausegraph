# Developer A: integration and release readiness

## Assignment

The user approved the proposed bounded integration/readiness task after PR20 and PR21 merged and B started task 6's read-only history UI. Verify the combined merged checkpoint and offline fallback, refresh shared delivery records, and prepare history review criteria. This does not start another feature or declare the history UI delivered.

Branch: `codex/dev-a/release-readiness`. Worktree: `.worktrees/dev-a-release-readiness`.
Starting and required merged commit: `a00af572cc20afea6893e0e261272bb919aed11f` (PR21), including PR19's history contracts and PR20's uncertainty validation. Fetched origin with pruning; clean main already matches. Existing worktrees, B's in-progress files and the user's running services are preserved.

Allowed tracked files: this handoff, new `docs/DELIVERY_CHECKPOINT.md`, `docs/WORKSTREAMS.md`, `docs/RESUME.md`, `docs/HACKATHON_MVP.md`, and `docs/DEMO.md`. Ignored local validation artifacts may be generated in this worktree's `.data/`. No runtime, API/schema, dependency, frontend, fixture, migration, peer handoff or deployment changes are assigned. Stop and report any defect requiring implementation outside this documentation task.

## Acceptance

- Confirm full CI for the combined merged application, with backend/PostgreSQL, generated contracts, frontend/browser and platform checks. Distinguish prior PR evidence from this exact checkpoint.
- Run existing history/uncertainty contract tests locally and reproduce the two offline demo reports with pinned Python. Preserve deterministic money, bounded proof labels and synthetic/live distinctions; no provider calls, cloud database, user-session reset or paid provisioning.
- Record a reproducible demo checkpoint and fallback procedure, with B's delivered automated rehearsal/visual evidence and the remaining human spoken rehearsal clearly distinguished.
- Update shared records: A6/A7 merged, B5 delivered, B6 actively assigned, task 8 deferred. Keep history APIs stable and avoid editing B's frontend work.
- Prepare review criteria for B's history PR using the merged contract, including identity/revision, saved assumptions, proof labels, read-only behavior, source/reset/session purges, error/empty states and stale-response isolation.
- Check documentation links, stale delivery claims, whitespace and ownership; publish a documentation PR for B review and green CI. No next task starts without consulting the user.

## Results

Recorded `a00af57` as the reproducible application checkpoint in [DELIVERY_CHECKPOINT.md](../../DELIVERY_CHECKPOINT.md). The checkpoint distinguishes existing demo delivery from B's active history UI and defines concrete review cases for history identity, assumptions, proof, read-only behavior, independent list limits, privacy/deletion, errors and stale responses. It changes no contract and adds no new B assignment.

Updated only the assigned shared docs and this handoff. A6/A7 are delivered in PR19/PR20; B5 is delivered in PR21; B6 is active per the user. B's 180.02-second automated operator timing, fallback/outage checks and focused desktop/mobile sign-off are credited to its merged handoff. Human spoken delivery remains unmeasured. No tag, deployment or global feature freeze was created.

| Check | Exact result |
|---|---|
| [Merged-main CI 35486912817](https://github.com/oliverchennn/clausegraph/actions/runs/35486912817), head `a00af572cc20afea6893e0e261272bb919aed11f` | All applicable jobs passed: 352 backend tests in 43.28s, including PostgreSQL 17; 11 real-API browser tests in 1.2m; Ruff, OpenAPI/TypeScript drift, frontend typecheck/lint/build, and Linux/Windows/macOS clean installs. The PR-only ownership job is intentionally skipped on main |
| `python -m pytest backend/tests/test_history_api.py backend/tests/test_uncertainty_limits.py -q` | 45 passed, 8 PostgreSQL variants skipped in 29.03s; two existing Starlette/AnyIO deprecation warnings |
| `python scripts/verify_demo.py` | Passed: nominal minimum 5000; 8/8 UNSAFE with first shortfall 2026-09-26 at -40000 cents for payday 2026-09-27; separate no-safe-schedule certificate; identical schedule SAFE 8/8 with 40000 extra hypothetical opening cents |
| `python scripts/eval_nemotron.py` | Passed all five expected fixture gate outcomes; three supported candidates, two deliberate errors rejected, unreviewed execution withheld 5/5; no model accuracy measured |
| Saved fallback JSON readback | Both reports parsed and matched expected outcomes; stored in ignored `.data/fallback/verify-demo.json` and `.data/fallback/semantic-gates.json` |
| Compare `app.openapi()` with parsed `docs/openapi.json` | Exact equality; no generated contract change |
| Changed-doc relative links and heading anchors | All resolved |
| Stale delivery-claim search; `git diff --check` | No obsolete B5/A7 status claims in changed central docs; whitespace passed with existing Windows normalization notices |

Local commands use Python 3.12.14 in the root `.venv/Scripts/python.exe`; no local `POSTGRES_TEST_URL` is configured. Full backend/frontend validation is taken from the exact merged-main CI above rather than rerunning unchanged application suites for documentation edits. This PR's CI remains the final check for its own commit. Existing locked Node 22.23.2/npm 10.9.8 requirements are unchanged.

## Review and limits

A self-review checked the delivery claims against CI logs, prior handoffs and freshly generated reports. B review and green PR CI are still required before merging this documentation task; neither is claimed by the implementation commit. A's earlier independent PR21 review is recorded on that PR, with 11 browser tests passing in 1.3m; it is distinct from this task's merged-main evidence.

No external provider call, cloud database access, user-session reset, service restart or provisioning occurred. Ignored fallback reports are local artifacts that another machine must regenerate. B's source work, task handoff and interfaces are untouched. The stable baseline can be demonstrated without the history follow-up; including history later requires its own merged acceptance. Human spoken rehearsal and live-provider/deployment validation remain separate. Stop after publishing this record and consult the user before any next task.
