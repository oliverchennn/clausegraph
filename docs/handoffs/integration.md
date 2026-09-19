# Integration handoff

Branch: `codex/integration`, checkout `C:/Users/vzhu0/PycharmProjects/clausegraph`. Root owns canonical schemas, fixtures, manifests/locks, generated types, migrations, CI and deployment. The original README-only repository is now a working local vertical slice. No cloud resources were provisioned or remote commits pushed.

## Latest change: hackathon MVP assessment (2026-09-19)

Branch: `codex/integration`, current root checkout; baseline commit `afdc0f0`. Read all repository Markdown docs, contributor instructions and lane handoffs, then inspected canonical contracts, engine results/gates, API persistence/export, dashboard comparisons, graph/chart and existing acceptance tests. No implementation lane was reopened.

Completed: added `docs/HACKATHON_MVP.md` with product positioning, implemented-versus-proposed inventory, ranked improvements, ownership/dependencies, acceptance criteria, evaluation measures and a feature-freeze scope. Added persistent hackathon priorities to AGENTS.md and linked the roadmap from README, RESUME, WORKSTREAMS and DEMO. Clarified that the UI's forced cancellation comparison can also select the payment shift; the standalone cancellation figure must not be presented as that different action set.

Recommendation: rehearse/validate the existing workflow, then implement a decision trace and side-by-side previews that preserve the active plan. Bounded stress testing is the stretch goal; review prioritization and history UI follow. Existing `POST /api/plan` persists the comparison and the dashboard starts comparisons from a fresh request, so safe previews require coordinated API/UI semantics rather than only a second chart.

Changed interfaces: none. Runtime code, dependency versions, fixtures and generated contracts unchanged. No new live-provider/deployment claim and no paid provisioning. All additions are documentation; feature implementation remains proposed.

Checks for this assessment:

- `.venv/Scripts/python.exe -m pytest backend/tests/test_demo.py backend/tests/test_engine.py backend/tests/test_graph.py -q`: **57 passed in 2.51s**.
- `git -c safe.directory=C:/Users/vzhu0/PycharmProjects/clausegraph diff --check`: **passed**; only existing Git line-ending normalization warnings.
- Python UTF-8 Markdown check over the seven changed/new docs: **23 relative links resolve; no trailing whitespace**. No full backend/frontend/browser rerun was performed for these Markdown-only edits; earlier broad results below remain historical.

Blockers/next steps: no blocker to documentation delivery or local feature work. Live extraction remains unverified and needs server-side credentials, explicit consent and a full synthetic upload/review/plan check. Start future implementation from the scoped acceptance criteria in HACKATHON_MVP.md; coordinate new trace/preview contracts through integration and regenerate OpenAPI/types if they change.

## Previous change: NVIDIA-only default (2026-09-19)

User requested a free-first hackathon replacement for required Gemini. NVIDIA Nano Omni now verifies evidence and transcribes scanned pages, alongside existing Nemotron Lightning extraction, using one NVIDIA_API_KEY. Gemini remains explicit opt-in via EVIDENCE_PROVIDER=gemini; no automatic fallback or OpenAI integration. Rationale, official sources and limits: docs/decisions/003-nvidia-evidence-default.md.

Changed interfaces: settings add evidence_provider, nvidia_evidence_model and bounded nvidia_evidence_reasoning_budget; upload accepts optional consent_provider and new queued jobs persist the selected recipient. Browser consent identifies NVIDIA only by default; stale consent or a queued provider change fails before sending data. OpenAPI and TypeScript contracts regenerated. Provider status/review notes identify the selected model. Existing deterministic checks, human source attestation and approval gates remain intact.

New source-page rendering uses pinned pypdfium2/Pillow in a killable 20-second subprocess, at most four pages/request, 1600px long edge and 2 MiB/image. Larger image sets require splitting. JSON, response completion, rule coverage and OCR page coverage are validated; errors fail closed. Same-family model agreement is not independent proof. PDF workers have time bounds, not OS memory quotas.

Exact latest checks:

- Backend: **140 passed, 1 skipped in 12.40s**, two existing dependency deprecation warnings. PostgreSQL test skipped without POSTGRES_TEST_URL. Includes both evidence providers, missing/malformed/duplicate checks, rendering/timeout/image provenance, no fallback and consent drift.
- Ruff, TypeScript, ESLint and production build: **passed**; first-load JS 138 kB.
- Real-API Playwright: **2 passed in 29.8s**; includes NVIDIA-only consent copy, full workflow and mobile overflow. Existing FORCE_COLOR/allowedDevOrigins warnings are nonfatal.
- OpenAPI export and generated frontend types: **passed**. pip check: no broken requirements. Locked pip audit: no known vulnerabilities. No npm dependency changes; earlier npm audit found zero vulnerabilities.
- Compose config validates; Docker daemon remains unavailable, no containers/cloud provisioned.
- Preview restarted via scripts/dev.py: API health ok/sqlite/private-local; frontend HTTP 200. Missing-key smoke reports NVIDIA extraction/evidence and ElevenLabs unavailable. Configured but unselected Gemini is not called; no live inference or credits consumed.

Next: add NVIDIA_API_KEY server-side, run the bounded provider smoke and synthetic native/scanned upload with explicit consent. Live endpoint availability and accuracy remain unverified. Do not expose keys in chat or commit .env. Local preview is left running; check ports before starting another instance.

## Original integrated work

- Engine lane: initial `646d0ff`, safety corrections `549c293` and `4e4b870`. Evidence-backed DSL, bounded native PDF extraction, typed dependency graph, deterministic simulation/CP-SAT, exhaustive small-case cross-checks.
- API lane: `3a60112`, `cc245b9`, `6b22106`. Private/versioned upload and original retrieval, explicit evidence attestation/conditions/approval review, leased worker, consent-gated configurable provider adapters, durable chart/history data, cache invalidation and deletion. No metadata changes after initial migrations.
- Frontend lane: `6fe8a40`, `7bd27a9`, `79e34bc`. Responsive workspace, graph/evidence drawer, intake and assumptions, forced-action comparisons, unsent drafts/export/audio/settings and real-API browser tests.
- Root delivered env template, locks, six fixtures, migrations, dev/seed/reset/smoke scripts, local Compose and DigitalOcean template, documentation and CI. Canonical OpenAPI is exported only from the real FastAPI app; frontend types include original/history endpoints and persisted PlanRequest assumptions.
- Scenario controls explicitly apply a hypothetical approval to both the action and approval-required source rules. This fixes the integration mismatch without weakening engine gates. Rule approvals remain distinct from hypothetical assumptions.
- Source deletion retains known debt amount/date/essential flags under generic titles with dangling provenance and an unresolved plan; it does not manufacture cash. Model candidates cannot label bills as income or assert actual transactions.
- Next type checking runs `next typegen && tsc --noEmit`, so fresh checkouts generate Next's route declaration before checking its generated next-env reference.

## Original delivery checks (2026-09-19, before provider switch)

From the root unless a frontend prefix is shown:

- `.venv/Scripts/python.exe -m pytest backend/tests -q`: **118 passed, 1 skipped in 9.45s**. PostgreSQL test requires POSTGRES_TEST_URL; two dependency deprecation warnings (Starlette TestClient/httpx and AnyIO) remain.
- `.venv/Scripts/python.exe -m ruff check backend scripts`: **passed**.
- `python scripts/export_openapi.py` and `npm --prefix frontend run generate:types`: **passed**, real API schemas generated; final commit contains matching output.
- `npm --prefix frontend run typecheck`, `npm --prefix frontend run lint`, `npm --prefix frontend run build`: **passed**. Final root production build exits 0 without the frontend worktree junction warning; / first-load JS is 138 kB.
- `npm --prefix frontend run test:e2e`: final root integration rerun **2 passed in 30.0s**. Nonfatal test-console warnings concern FORCE_COLOR and Next's future allowedDevOrigins setting; no page errors occurred.
- Browser coverage: exact demo balances, persisted approval denial, conditional approval and reload, restored approval, source download, accelerated phone-debt consequence, draft/summary downloads, graph evidence, native-only upload/dedup, intake recalculation, session deletion, no page errors, 390px mobile overflow checks.
- Manual browser visual checks: 1440px desktop and 390px mobile dashboard, evidence drawer and graph; no observed console errors or horizontal overflow. Temporary viewport restored.
- `docker compose config --quiet`: **passed**; Docker's protected local config file emits an access warning. Actual containers were not run because the Docker daemon is unavailable.
- `scripts/migrate.py`: local SQLite schema initialization passed. PostgreSQL migration/job/session test is configured in CI, not executed here.
- `scripts/dev.py`: API, worker and frontend started; /api/health returned ok/sqlite/private-local, frontend returned HTTP200. Owned child services were stopped between build/test phases; final preview is restarted.
- `scripts/smoke_providers.py`: missing-key paths verified against the running API; NVIDIA/Gemini/ElevenLabs unavailable, SQLite reachable, Spaces local fallback. No live sponsor call was claimed.
- Dependency checks during this build: npm audit 0 vulnerabilities; pip audit no known vulnerabilities; pip check no broken requirements.

## Handoff / external validation

Local entry point: `.venv/Scripts/python.exe scripts/dev.py`, then http://localhost:3000. Avoid starting duplicate services and avoid running root dev concurrently with root build/E2E (.next is shared). Browser tests use ports 8001/3001 and isolated .data/e2e storage. README contains exact installation/individual-service/check commands, and docs/DEMO.md contains the three-minute synthetic demo.

All implementation lanes are integrated. Worktrees are retained; no additional agent work is active. Use docs/RESUME.md as the next prompt entry point. Secrets and private local data are ignored. No PR was created.

Remaining: real configured model availability/extraction/verification/audio, private Spaces, Tiger Data migrations/queue and DigitalOcean deployment must be validated with credentials and any required cost approval. Deployment/account/retention/abuse controls are not production-ready. Conservative source semantics can withhold valid unusual wording; image-only model transcription requires human original-page attestation. PDF parsing is time-bounded but lacks an OS memory quota. No automatic payments, cancellations, applications or messages exist.
