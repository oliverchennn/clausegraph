# ClauseGraph resume / delivery checkpoint

## Latest: ClauseGraph Verify

Bounded fixed-plan verification is implemented on `codex/integration`; do not restart scaffolding or treat it as proposed stretch work. Read [handoffs/verification.md](handoffs/verification.md) for current contracts, lane commits, exact 204-test / 5-browser-test validation, sponsor status and limitations. API/UI expose declared uncertainty, SAFE/UNSAFE/UNKNOWN, exact counterexamples and evidence-linked cash overlays without changing the saved nominal plan. `python scripts/verify_demo.py` demonstrates the eight-case failure, proves no safe schedule exists for that declared model, and verifies the fixed schedule with hypothetical extra opening cash. `python scripts/eval_nemotron.py` is a local fixture gate evaluation, not live model accuracy. General robust synthesis and live cloud validation remain deferred. The following sections are historical delivery records.

The local vertical slice is implemented and integrated on `codex/integration` in `C:/Users/vzhu0/PycharmProjects/clausegraph`. Do not restart scaffolding. Read AGENTS.md and docs/handoffs/integration.md for the current verification record. Latest runtime change: NVIDIA Nano Omni now replaces required Gemini for verification/OCR; see docs/decisions/003-nvidia-evidence-default.md. Only NVIDIA_API_KEY is required for the default document pipeline. Gemini remains explicit opt-in, no OpenAI adapter or automatic paid fallback.

## Product direction (2026-09-19)

The latest documentation assessment establishes a hackathon MVP focused on novelty, user impact and technical depth. Read [HACKATHON_MVP.md](HACKATHON_MVP.md) before selecting new work; AGENTS.md now carries this priority. Recommended scope: validate/rehearse the existing end-to-end flow, then add a decision trace and side-by-side previews that preserve the primary plan. Bounded stress testing is the stretch goal. These are proposed additions, not newly implemented functions. Existing backend demo/engine/graph checks were rerun: **57 passed in 2.51s**. No runtime or contract changes in this assessment.

## What works

- Six clearly synthetic documents; deterministic integer-cent simulation and CP-SAT optimization. Baseline minimum −40000 cents; approved shift minimum 5000 and ending 50000; denied shift minimum −40000; phone cancellation alone minimum −82000 and ending 8000.
- Next.js responsive dashboard, cash chart, evidence/condition review, editable intake, dependency graph, approval/date/cash scenarios, conditional labels, unsent drafts, downloads, privacy controls and optional audio UI.
- Private FastAPI bearer sessions, versioned originals, document deduplication, bounded uploads/PDF parsing, PostgreSQL-compatible leased worker, consent-gated extraction/verification, durable plan assumptions/history/chart series, deletion and conservative retained obligations.
- Configurable real HTTP adapters for Nemotron extraction + Nano Omni verification/OCR, optional Gemini, ElevenLabs and private Spaces. Missing credentials are visible failures, not synthetic provider success. NVIDIA image requests use at most four locally rendered source pages; split larger scans. Jobs bind consent to the selected evidence provider.
- README, env template, dependency locks, migrations, seed/reset CLI, local launcher, provider smoke CLI, Compose, DigitalOcean template, CI and three-minute demo.

## Current verification

- Latest backend: **140 passed, 1 skipped in 12.40s**; provider-switch results are recorded in docs/handoffs/integration.md. PostgreSQL check skips without POSTGRES_TEST_URL. Two Starlette/AnyIO dependency deprecation warnings remain.
- TypeScript, ESLint and production build passed. Real-API Playwright workflow and mobile overflow checks: **2 passed in 29.8s**.
- Browser visually checked at desktop 1440px and mobile 390px: dashboard, evidence drawer and dependency graph; no observed console errors or horizontal overflow. Temporary viewport override restored.
- npm audit: 0 vulnerabilities; pip audit: no known vulnerabilities; pip check: no broken requirements (run during this build).
- Compose configuration validates. Docker daemon unavailable, so no containers or cloud deployment were executed.
- Latest missing-key smoke: NVIDIA extraction/evidence and ElevenLabs unavailable, local SQLite reachable, private local storage active. Configured but unselected Gemini was not called. Preview restarted; API health OK and frontend HTTP 200.

## Run and restart

Dependencies already exist in `.venv` and `frontend/node_modules`.
```powershell
.\.venv\Scripts\python.exe scripts/dev.py
```
Open http://localhost:3000. This starts API port 8000, worker and frontend port 3000. Do not start a duplicate if those ports are already serving ClauseGraph. The delivery preview is left running when available; verify current process state rather than relying on old tool session IDs. README contains fresh-install, individual-service, validation and Docker commands. Populated .env and local .data are ignored.

## Remaining external validation / limitations

NVIDIA and ElevenLabs keys, Tiger Data connection and Spaces bucket are not configured. A Gemini key is configured but is not selected or used by the default pipeline. No live extraction/audio/cloud-storage call has succeeded here; mocked protocol tests are not live validation. Next: supply NVIDIA_API_KEY server-side, run the bounded provider smoke, then test a synthetic upload with explicit processing consent. Explicitly authorize any paid resources before deployment. Smoke calls consume configured provider quota and may consume credits.
PostgreSQL migration/queue integration is configured in CI but not locally executed. DigitalOcean spec is a template needing repository/secrets/account validation. Account recovery, operational retention policy and production abuse controls remain prototype limitations; do not publicly process real financial data yet.
Conservative literal/operation and entity checks can withhold valid unusual clauses for human review. Native PDF parsing has a killable time bound, not an OS memory quota. No payments, cancellations, applications or outbound messages are executed.

## Branches and handoff

PR #1 squash-merged integration through `29e7426` into main as `b547df2`, preserving the same files under a new commit. PR #2's duplicate-history conflicts were reconciled by merging main back into integration while preserving the current code. The local safety branch `codex/backup-integration-before-pr2-fix` retains user commit `34014a2` before that repair. This backup is a recovery reference, not a new implementation lane.

After future squash merges, fetch origin and create the next feature branch from `origin/main`. If continuing an existing branch is necessary, merge refreshed main into it first and inspect the result. Avoid pulling divergent main blindly, replaying already-squashed commits, or force-pushing to solve this ancestry issue. Local `main` can lag the remote; use the refreshed remote reference as the new-branch starting point. Preserve lane worktrees and any uncommitted work.

Root owns contracts/locks/migrations/fixtures/CI/deployment. Engine/API/frontend lanes use separate .worktrees directories; their implementation commits are integrated. Agents completed their bounded lanes; no further delegation is required. Preserve worktrees and user files.
Git may require a per-command `-c safe.directory=C:/Users/vzhu0/PycharmProjects/clausegraph` override due sandbox ownership. Do not set a global trust override or cherry-pick shared foundation commits again.
Canonical schema: backend/clausegraph/schemas.py. After interface changes run `python scripts/export_openapi.py` then `npm --prefix frontend run generate:types`. Browser tests start isolated API port 8001/frontend port 3001; do not run the root dev frontend concurrently with root build/E2E because they share .next.
The original detailed request remains at `C:/Users/vzhu0/.codex/attachments/cc5944a0-5a53-4bd4-8a13-811a7cd0fe46/Pasted text.txt`. Its explicit Next/FastAPI/DigitalOcean repository stack takes precedence over Sites; no Sites project was created.
