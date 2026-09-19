# ClauseGraph Verify integration handoff

Branch: `codex/integration`, current root checkout. Started from clean d5cd282; existing lane checkouts and user changes preserved. This is the current delivery record; older product assessments in integration/HACKATHON_MVP are historical.

## Completed and interfaces

- Root-owned canonical Pydantic contracts add user-assumed income date/cent ranges and finite approval outcomes, verification requests/results, witnesses and evidence-linked events. All ranges are closed, integer-valued and explicit. Generated OpenAPI and TypeScript include `POST /api/verify` and `GET /api/verifications`.
- Engine lane 17a5743 integrated as 151b424; API lane b12cec8 integrated as d6a786b; frontend lane e0a3963 integrated as a6a5cdb. Each committed its own handoff with the substantive changes. No dependencies changed.
- `verify_plan` holds saved action IDs/dates fixed. It reuses the optimizer's ledger preparation, evidence/approval/dependency gates and canonical event materialization/simulation. Existing CP-SAT continues nominal optimization. No generated code, LLM arithmetic or alternate money semantics.
- Rigorous finite exhaustive checking visits every declared date, integer cent and approval outcome. This is model checking rather than sampled stress testing. A second SMT arithmetic implementation was unnecessary for the bounded MVP. SAFE needs full coverage and resolved facts; a concrete violation proves UNSAFE; otherwise UNKNOWN. Runtime/coverage/proof flags expose partial results honestly.
- Counterexamples show the exact assignment, earliest failing date (globally earliest only after complete enumeration), meaningful cash balance, failures and event/action/rule provenance. Unauthorized schedules have no permitted cash projection. Worst-balance assignment may differ from the earliest-failure assignment. Essential payments, original debt identity and future obligations remain preserved by shared transitions.
- API requires the current plan ID and revision, then locks/rechecks them atomically before history persistence. Verification never changes the active plan. SQLite/PostgreSQL tables `verification_runs` and `verification_points` match migration003. History is session-scoped and source/session deletion/reset purges narratives and points.
- Dashboard adds explicit assumptions, Safe/Unsafe/Unknown, case/runtime/horizon details, proof-qualified worst minimum, evidence-linked counterexample timeline and chart overlay. Results clear when form, plan or revision changes. Nominal CP-SAT optimality is labeled separately. The UI exposes one date interval and one action approval dimension; the API supports eight dimensions including cent ranges.
- Root adds `scripts/verify_demo.py`, five-clause `scripts/eval_nemotron.py` and corpus/tests, PostgreSQL history integration coverage, migration003 and current docs/demo. Fixed an existing privacy-test flake: random empty directories starting with `v` no longer count as undeleted original files. Browser selector corrected to account for the solver label's nested runtime text. Windows OR-Tools loader diagnostics go to stderr so the demo report is valid JSON on stdout.

## Synthetic proof/demo

Original arithmetic unchanged: baseline minimum/end −40000/50000 cents; approved shift 5000/50000; denied shift −40000/50000; cancellation alone −82000/8000. All six original evidence fixtures remain untouched.

`python scripts/verify_demo.py` checks all eight September 21–28 payday assignments. The nominal minimum is 5000; earliest deterministic counterexample payday September 27 fails September 26 at −40000 cents. At the allowed September 28 assignment, separate CP-SAT reoptimization proves the best permitted minimum is −40000. Therefore no schedule is safe for the full declared range. Verifying the identical schedule with 40000 additional hypothetical opening cents passes all eight cases, establishing a tight bounded cash diagnostic. No funding is created. General robust schedule synthesis is explicitly not implemented. The UI's September 21–26 preset verifies six cases; narrowing assumptions does not resolve the broader model's failure.

## Exact validation (2026-09-19)

Use `.venv/Scripts/python.exe` in place of `python` on this Windows checkout; bare `python` is unavailable in the sandbox PATH.

| Command/check | Result |
|---|---|
| Baseline `python -m pytest backend/tests -q` | 140 passed, 1 skipped in 11.39s |
| Baseline `npm --prefix frontend run test:e2e` | 2 passed in 26.9s |
| Final `python -m pytest backend/tests -q` | 204 passed, 1 skipped in 15.71s; two existing Starlette/AnyIO deprecation warnings |
| `python -m ruff check backend scripts` |Passed |
| `npm --prefix frontend run typecheck` and `run lint` |Passed |
| `npm --prefix frontend run build` |Passed; physical root dependencies, no worktree symlink warning; first-load JS 142 kB |
| Final `npm --prefix frontend run test:e2e` | 5 passed in 31.3s; actual FastAPI and Chromium, no mocked responses |
| `python scripts/export_openapi.py`; `npm --prefix frontend run generate:types` |Passed; regenerated canonical contracts |
| `python scripts/migrate.py` |SQLite schema initialized successfully |
| `python scripts/verify_demo.py` |Eight-case UNSAFE, no-safe-schedule certificate, same schedule with hypothetical cash SAFE |
| `python scripts/eval_nemotron.py` |Five fixture gate cases pass: 3 exact supported outputs, 2 intentionally wrong outputs rejected, 5/5 withheld pending review; not live model accuracy |
| Final targeted demo/eval tests after stdout cleanup | 3 passed in 1.75s; Ruff passed |
| `git diff --check` |Passed; existing CRLF normalization notices only |

The 48 verifier tests include ten independently computed small finite-ledger oracles, every-cent/date enumeration, deterministic witnesses, timeout/case-limit UNKNOWN and retained UNSAFE witnesses, pending/denied approvals, conditional assumptions, field-specific evidence checks, essential preservation, horizon boundaries, future debt/acceleration uniqueness, and fixed verification versus reoptimization. Thirteen API tests cover no mutation/reoptimization, session isolation, stale plan/revision and in-flight races, newest 30 history, authoritative persisted points and deletion/reset. Browser coverage includes Safe/Unsafe/Unknown, action/evidence links, unchanged nominal plan, form/revision invalidation and 390px layout. Desktop and mobile verification screenshots were visually inspected; no horizontal overflow or clipped result layout. Screenshot artifacts live in ignored frontend/test-results.

The first integrated browser run passed 4/5; the failure was an exact-text selector matching a parent with additional runtime text, before entering the verification flow. The selector was corrected and the full five-test run passed. An API lane run exposed the preexisting random-directory privacy-test flake described above; the corrected full suite passed.

## Sponsor truth and limits

No external calls, deployment or paid provisioning occurred. NVIDIA/ElevenLabs, PostgreSQL/Tiger Data, Spaces and DigitalOcean token configuration are unavailable. An optional Gemini key exists but remains unselected and untested. The existing optional provider smoke/evidence/OCR adapters are preserved; no silent fallback. The new local eval reports fixture metrics separately from its explicit `--live --consent-external` mode, which fails closed without NVIDIA credentials. It covers native text only, not OCR or full extraction/review accuracy.

Verification history uses the existing database and private-session deletion semantics. No Tiger-specific hypertable, continuous aggregate, meaningful performance benchmark or live deployment is claimed. The 60-day bounded workload does not justify a fabricated large dataset or second database. PostgreSQL migration/history tests are supplied for CI but skipped locally without POSTGRES_TEST_URL. DigitalOcean/Spaces remain templates/adapters; domain setup is deferred until a real deployment exists.

Default 5-second cooperative budget, maximum 10 seconds / 10,000 cases / 8 dimensions. Large cent ranges may return UNKNOWN. Bounds are user assumptions; source-derived range extraction, correlated uncertainties, uncertain expense timing, adaptive policies and general robust synthesis are deferred. Guarantees concern daily closing balances only within the declared model/horizon; unknown real-world facts, intraday settlement and later dates are excluded. Unresolved conditions never default true. The model never sends messages, executes payments/cancellations/applications or grants external approval.

Next: supply authorized server-side NVIDIA credentials for the synthetic live eval and upload→worker→review workflow; supply an approved PostgreSQL/Tiger Data service and private Spaces/App Platform resources for live migration/health/worker/deletion testing. Rehearse [the three-minute demo](../DEMO.md). No further core feature work is required for this bounded local demo.
