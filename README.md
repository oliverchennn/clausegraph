# ClauseGraph Verify

An evidence-backed emergency cash planner: uploaded clauses become reviewed rules, a dependency graph and a deterministic action plan. Verify the saved action schedule against every case in explicitly declared bounded uncertainties, or inspect the concrete counterexample that breaks it. It never sends requests, applies for benefits, cancels services or moves money.

## Hackathon focus

The MVP demonstrates a complete chain from **source clause → reviewed rule → dependency graph → constrained action schedule → cash projection**. Its novelty is reasoning over interacting clauses; its intended impact is helping people bridge cash timing gaps while preserving essentials; its technical depth is the evidence-gated rule compiler and deterministic solver. The synthetic demo moves minimum cash from −$400 to $50 without changing ending cash or claiming savings.

See [HACKATHON_MVP.md](docs/HACKATHON_MVP.md) for current scope and [the verification handoff](docs/handoffs/verification.md) for semantics and checks. Nominal CP-SAT planning and fixed-plan verification are separate operations. Verification exhaustively enumerates all dates, integer-cent amounts and approval outcomes in the declared model using the existing accounting/evidence gates. SAFE means only that every case passed within the displayed horizon; limits or unresolved facts yield UNKNOWN unless a concrete failure already proves UNSAFE. General robust schedule synthesis remains deferred.

The integrated dashboard also includes “Why this plan?” source/rule/event traces and side-by-side previews. Previews leave the recorded plan and its verification unchanged until explicitly applied.

## Run locally

Requires Python 3.12 and Node.js 22+. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt -c backend/requirements.lock
npm --prefix frontend ci
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
.\.venv\Scripts\python.exe scripts/dev.py
```

On macOS/Linux, substitute `.venv/bin/python` and `test -f .env || cp .env.example .env`. Open [localhost:3000](http://localhost:3000). Local mode uses SQLite/private local files; no credentials are needed for the clearly labeled synthetic demo. Never overwrite an already-configured `.env`. The API and worker read server-side keys from it. The worker is required for uploaded-document extraction.

To run processes separately:

```powershell
.\.venv\Scripts\python.exe -m uvicorn clausegraph.api:app --app-dir backend --port 8000 --no-access-log
# In another terminal, from the same repository root:
$env:PYTHONPATH = 'backend'
.\.venv\Scripts\python.exe -m clausegraph.worker
# In a third terminal:
npm --prefix frontend run dev
```

Alternatively, `docker compose up --build` starts local PostgreSQL, migration job, API, worker and frontend. Compose configuration has been validated; executing containers requires a running Docker daemon.

## Reproducible demonstration

Six documents in `fixtures/` are synthetic. Day 0 is September 1, 2026. The scenario starts with $2,000, pays $1,600 rent on day 7 and $800 other payments before a $900 paycheck on day 20.

| Scenario | Minimum cash | Ending cash |
|---|---:|---:|
| Baseline | −$400 | $500 |
| Approved $450 installment moved to day 25 | $50 | $500 |
| Shift approval denied | −$400 | $500 |
| Phone cancellation alone, accelerating device debt | −$820 | $80 |

The device's original $480 debt is relocated from day 80, not duplicated. Assistance without eligibility, approval and payment timing stays unresolved. The chart depicts projections, while ledger records separately track actual events.

Use **Why this plan?** to show the $450 installment moving from September 13 to September 26. Then choose **Compare option alone** on phone cancellation: the candidate shows −$820 minimum/$80 ending beside the untouched $50/$500 recorded plan. Scenario controls also support a non-persistent approval/date/cash preview. Applying any candidate is a separate explicit choice and still executes no real-world action.

Create a fresh demo via `python scripts/demo_session.py`. Reset only a selected session using `python scripts/demo_session.py --reset-session TOKEN` or the UI. This replaces that session's data; other sessions remain private. See [the three-minute script](docs/DEMO.md).

In **Verify plan**, declare paycheck dates September 21–28 inclusive. The saved $50 nominal-minimum plan fails on September 26 when payday is September 27: balance −$400. The chart overlays the concrete counterexample and the timeline links to source evidence. Restricting the declared range to September 21–26 verifies all six cases; changing an assumption is not mitigation for a broader range.

`python scripts/verify_demo.py` reproduces the eight-case failure, separately proves via CP-SAT that no permitted schedule can be safe at the allowed September 28 payday, and verifies the same schedule across all eight cases with $400 of **hypothetical additional opening cash**. This supplies a tight bounded cash diagnostic, not funding or a general synthesis API. Verification results and daily outcome points are stored privately in the existing database, exposed through `GET /api/verifications`, and purged on source/session deletion or demo reset.

`python scripts/eval_nemotron.py` runs five synthetic semantic-compiler cases without external requests, including two intentionally faulty outputs. It measures local gates, not model accuracy. `--live --consent-external` explicitly sends this synthetic corpus to configured NVIDIA and reports actual structured extraction/citation results with no fallback. Live Nemotron evaluation remains unverified here.

## Validation

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests -q
.\.venv\Scripts\python.exe -m ruff check backend scripts
.\.venv\Scripts\python.exe scripts/export_openapi.py
npm --prefix frontend run generate:types
npm --prefix frontend run typecheck
npm --prefix frontend run lint
npm --prefix frontend run build
# First browser-test setup:
cd frontend
npx playwright install chromium
npm run test:e2e
```

CI checks schema drift, lint, types, engine/API tests, a production build and browser flow. `POSTGRES_TEST_URL` enables an isolated PostgreSQL migration/queue test; CI provides PostgreSQL 17. Local verification results are recorded in [the integration handoff](docs/handoffs/integration.md).

## Providers and deployment

The synthetic demo makes no model calls. Real uploads can extract native PDF/text/CSV locally. External extraction, evidence checking and scanned-page transcription default to NVIDIA and require consent plus only `NVIDIA_API_KEY`: Lightning extracts, while `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` checks evidence and reads scanned pages. Set `EVIDENCE_PROVIDER=gemini` and `GEMINI_API_KEY` only to explicitly opt into Google verification/OCR. No OpenAI key is needed and there is no automatic paid-provider fallback. See [the model decision](docs/decisions/003-nvidia-evidence-default.md) for SteelHacks/free-endpoint sources and tradeoffs.

NVIDIA image processing accepts at most four source pages per request; split larger scans. Native PDF text limits are unchanged. Both model passes can make correlated mistakes: agreement never replaces exact-source checks or human review. Missing credentials and failed verification remain visible and do not silently switch to fixtures. ElevenLabs speech is optional and requires fact confirmation. Model IDs/base URLs are configurable; check account availability using `python scripts/smoke_providers.py` (configured calls consume quota and may consume provider credits).

[SPONSORS.md](docs/SPONSORS.md) records implementation and actual live-test status. [DEPLOYMENT.md](docs/DEPLOYMENT.md) explains Tiger Data, private Spaces, migrations and the DigitalOcean App Platform template. No paid resources have been provisioned. Keep populated `.env` files and session bearer tokens private.

## Architecture and collaboration

Pydantic/OpenAPI is canonical; generated TypeScript types drive the frontend. CP-SAT uses integer cents and explicit dates, preserves essential services and reports feasible/optimal/timeout status. Exact quotes, human review, approval and model confidence are separate. A small allowlisted event-transformation language executes reviewed rules; document content is never evaluated as code.

Read [AGENTS.md](AGENTS.md), [ARCHITECTURE.md](docs/ARCHITECTURE.md), [WORKSTREAMS.md](docs/WORKSTREAMS.md) and lane handoffs before edits. This prototype uses private anonymous bearer sessions; account recovery, operational retention policies and production abuse controls require further product work before a public real-data rollout.
