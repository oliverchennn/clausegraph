# Resume ClauseGraph after the model switch

The user requested a pause after the immediate dependency checkpoint to save credits. Do not restart scaffolding or re-read unrelated skills. Continue the original build request when the user says resume.

## Original request and boundaries
The complete user brief is in `C:/Users/vzhu0/.codex/attachments/cc5944a0-5a53-4bd4-8a13-811a7cd0fe46/Pasted text.txt`. It asks for a working Next.js/TypeScript/Tailwind + FastAPI/Pydantic/NetworkX/OR-Tools evidence-backed emergency planner, six synthetic documents, exact acceptance arithmetic, live configurable Nemotron/Gemini/ElevenLabs adapters, Tiger Data PostgreSQL jobs/history, private DigitalOcean Spaces and deployment config. No paid provisioning. No automated payments, cancellations, applications or messages. Finish implementation/testing, not architecture alone.

Read AGENTS.md, ARCHITECTURE.md, WORKSTREAMS.md and lane handoffs. Sites workflow was inspected initially but deliberately not used: this user explicitly requires the repository's Next.js/FastAPI/DigitalOcean stack. Do not initialize Sites or provision hosting.

## Repository and isolated lanes
- Main working checkout: `C:/Users/vzhu0/PycharmProjects/clausegraph`, branch `codex/integration`.
- Engine checkout: `.worktrees/engine`, branch `codex/engine`.
- API checkout: `.worktrees/api`, branch `codex/api`.
- Frontend checkout: `.worktrees/frontend`, branch `codex/frontend`.
- Each lane has its own implementation checkpoint and handoff. Read each handoff **inside its worktree** until it is integrated; root copies still contain initial assignments.
- Agents were told to stop after a small checkpoint and not continue features. Reuse agents only if they still exist, otherwise spawn bounded lane tasks and preserve their files.
- Root owns shared schemas, manifests, lockfiles, fixtures, migrations, CI and generated API types. Cherry-pick only lane implementation commits, not their copies of shared integration commits. Shared foundation commits already exist on integration.
- Git requires a per-command safe-directory override in this sandbox: `git -c safe.directory=C:/Users/vzhu0/PycharmProjects/clausegraph ...`. Use each exact checkout path for worktree commands. Git metadata writes required escalation, already authorized as part of this workflow.

## Completed integration foundation
- Canonical Pydantic contracts in `backend/clausegraph/schemas.py`, OpenAPI exporter and initial generated TS types.
- Canonical dates use `Date` alias to prevent collision with `date` field names.
- `RuleReview` now includes `conditions` and `evidence_confirmed`. Human approval, evidence validity, confidence and review remain separate.
- Integer monetary inputs now strict, including fees and rule review amounts.
- Six synthetic text/CSV documents in fixtures; `clausegraph.demo.load_demo()` returns scenario/documents/rules with exact quote offsets.
- Day 0 = 2026-09-01, rent160000 day7, phone6000 day10, loan45000 day12, utilities12000 day15, groceries17000 day18, income90000 day20, device48000 day80.
- Approved `shift-payment` moves installment to day25. `cancel-phone` removes6000 and relocates existing device48000 once. `claim-assistance` remains unresolved and excluded. `rule-shift` controls approval. Payroll is an employer obligation, not an unapproved benefit.
- Expected baseline minimum -40000, ending50000; shifted minimum5000, ending50000; phone cancellation alone minimum -82000, ending8000.
- SQL migrations in `migrations/` generated from current API-lane SQLAlchemy metadata, plus actual/projected event aggregate view. `scripts/migrate.py` applies checksum-tracked PostgreSQL migrations; SQLite dev uses metadata.
- CI schema drift/lint/types/build/pytest/Playwright workflow, seed/reset CLI and three-minute demo script.

## Environment and exact checks already run
- Shared Python venv: `.venv/Scripts/python.exe` (Python 3.12.14).
- Node v24.12.0, npm11.6.2. Root `frontend/node_modules` installed. Frontend lane may use a junction to it; preserve it.
- Python dependency pins updated after audit: FastAPI0.141.1, Starlette1.6.0, pypdf6.19.0, python-multipart0.0.32, pytest9.1.1, pytest-asyncio1.4.0. Direct requirements + transitive constraints lock are in backend. `pip-audit` is installed only as a local check tool, not an app dependency.
- Frontend: Next15.5.25, ESLint9.39.5, Playwright1.63.0, PostCSS8.5.28 override. Other pins in package.json/lock.
- `npm audit`: **0 vulnerabilities**.
- `.venv/Scripts/python.exe -m pip_audit --no-deps --disable-pip -r backend/requirements.lock --format columns`: **No known vulnerabilities found**.
- `.venv/Scripts/python.exe -m pip check`: **No broken requirements found**.
- `.venv/Scripts/python.exe -m pytest backend/tests/test_demo.py -q -k 'not complete_demo and not cancelling'`: **6 passed, 2 deselected**.
- Initial canonical OpenAPI export and openapi-typescript generation passed. These generated files are provisional and must be regenerated from the final API; latest review properties are not yet all in generated types.
- No NVIDIA/Gemini/ElevenLabs/Spaces/DATABASE_URL credential environment names were found. No live sponsor request or deployment occurred.
- Docker CLI exists but daemon is not running. PostgreSQL integration test is added and skips without `POSTGRES_TEST_URL`; CI has PostgreSQL17 service. Do not claim Tiger Data/PostgreSQL/Spaces tested locally.

## Next execution order
1. Inspect final lane handoffs/commits and cherry-pick their implementation checkpoints into integration. Keep user data/changes untouched.
2. Resume missing lane work from those handoffs. API/storage/worker and frontend may still be incomplete; do not present this checkpoint as a finished app.
3. Check all schemas/interfaces agree (conditions/evidence review, original source download, session response Workspace). Regenerate OpenAPI + frontend types. Verify migration columns against storage metadata.
4. Run meaningful engine/API/fixture tests. Engine acceptance and exhaustive enumeration are required. Validate per-session dedup, contradictory clauses/cycles, unsupported benefits, date boundaries, approval invalidation and deletion.
5. Complete UI/API integration; typecheck, lint and production build. Run the complete browser test against the real local API, inspect desktop/mobile layouts, fix runtime failures. Start API/worker/frontend as needed, keeping secrets server-side.
6. Finalize README exact run commands, .env.example, Docker Compose and DigitalOcean deployment configuration, docs/SPONSORS.md truthful integration/live-test matrix, docs/DEMO.md. Test credential smoke endpoint (missing status is not success). No paid resources without approval.
7. Update all handoffs and final check results in the same commit. Report what works, remaining external validation, and exact run commands.

No user-facing browser or running development server has been started by integration at this pause.
