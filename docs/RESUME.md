# ClauseGraph resume / delivery checkpoint

The local vertical slice is implemented and integrated on `codex/integration` in `C:/Users/vzhu0/PycharmProjects/clausegraph`. Do not restart scaffolding. Read AGENTS.md and docs/handoffs/integration.md for the current verification record.

## What works

- Six clearly synthetic documents; deterministic integer-cent simulation and CP-SAT optimization. Baseline minimum −40000 cents; approved shift minimum 5000 and ending 50000; denied shift minimum −40000; phone cancellation alone minimum −82000 and ending 8000.
- Next.js responsive dashboard, cash chart, evidence/condition review, editable intake, dependency graph, approval/date/cash scenarios, conditional labels, unsent drafts, downloads, privacy controls and optional audio UI.
- Private FastAPI bearer sessions, versioned originals, document deduplication, bounded uploads/PDF parsing, PostgreSQL-compatible leased worker, consent-gated extraction/verification, durable plan assumptions/history/chart series, deletion and conservative retained obligations.
- Configurable real HTTP adapters for Nemotron/Gemini/ElevenLabs and private Spaces. Missing credentials are visible failures, not synthetic provider success.
- README, env template, dependency locks, migrations, seed/reset CLI, local launcher, provider smoke CLI, Compose, DigitalOcean template, CI and three-minute demo.

## Current verification

- Integrated backend: **118 passed, 1 skipped**; Ruff passed. PostgreSQL check skips without POSTGRES_TEST_URL. Two Starlette/AnyIO dependency deprecation warnings remain.
- TypeScript, ESLint and production build passed. Real-API Playwright workflow and mobile overflow checks passed; final integration handoff records the exact last run.
- Browser visually checked at desktop 1440px and mobile 390px: dashboard, evidence drawer and dependency graph; no observed console errors or horizontal overflow. Temporary viewport override restored.
- npm audit: 0 vulnerabilities; pip audit: no known vulnerabilities; pip check: no broken requirements (run during this build).
- Compose configuration validates. Docker daemon unavailable, so no containers or cloud deployment were executed.
- Missing-key smoke was run against the API: NVIDIA/Gemini/ElevenLabs unavailable, local SQLite reachable, private local storage active.

## Run and restart

Dependencies already exist in `.venv` and `frontend/node_modules`.
```powershell
.\.venv\Scripts\python.exe scripts/dev.py
```
Open http://localhost:3000. This starts API port 8000, worker and frontend port 3000. Do not start a duplicate if those ports are already serving ClauseGraph. The delivery preview is left running when available; verify current process state rather than relying on old tool session IDs. README contains fresh-install, individual-service, validation and Docker commands. Populated .env and local .data are ignored.

## Remaining external validation / limitations

No live sponsor credentials, Tiger Data connection or Spaces bucket are configured. No live extraction/audio/cloud-storage call has succeeded here; mocked protocol tests are not live validation. Supply credentials server-side and explicitly authorize any paid resources before deployment. Smoke calls may consume configured provider credits; use synthetic documents with explicit processing consent for a live extraction test.
PostgreSQL migration/queue integration is configured in CI but not locally executed. DigitalOcean spec is a template needing repository/secrets/account validation. Account recovery, operational retention policy and production abuse controls remain prototype limitations; do not publicly process real financial data yet.
Conservative literal/operation and entity checks can withhold valid unusual clauses for human review. Native PDF parsing has a killable time bound, not an OS memory quota. No payments, cancellations, applications or outbound messages are executed.

## Branches and handoff

Root owns contracts/locks/migrations/fixtures/CI/deployment. Engine/API/frontend lanes use separate .worktrees directories; their implementation commits are integrated. Agents completed their bounded lanes; no further delegation is required. Preserve worktrees and user files.
Git may require a per-command `-c safe.directory=C:/Users/vzhu0/PycharmProjects/clausegraph` override due sandbox ownership. Do not set a global trust override or cherry-pick shared foundation commits again.
Canonical schema: backend/clausegraph/schemas.py. After interface changes run `python scripts/export_openapi.py` then `npm --prefix frontend run generate:types`. Browser tests start isolated API port 8001/frontend port 3001; do not run the root dev frontend concurrently with root build/E2E because they share .next.
The original detailed request remains at `C:/Users/vzhu0/.codex/attachments/cc5944a0-5a53-4bd4-8a13-811a7cd0fe46/Pasted text.txt`. Its explicit Next/FastAPI/DigitalOcean repository stack takes precedence over Sites; no Sites project was created.
