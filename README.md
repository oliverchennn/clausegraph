# ClauseGraph

An evidence-backed emergency cash planner: uploaded clauses become reviewed rules, a dependency graph and a deterministic action plan. It never sends requests, applies for benefits, cancels services or moves money.

## Run locally

Requires Python 3.12 and Node.js 22+. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt -c backend/requirements.lock
npm --prefix frontend ci
Copy-Item .env.example .env
.\.venv\Scripts\python.exe scripts/dev.py
```

On macOS/Linux, substitute `.venv/bin/python` and `cp .env.example .env`. Open [localhost:3000](http://localhost:3000). Local mode uses SQLite/private local files; no credentials are needed for the clearly labeled synthetic demo. Never overwrite an already-configured `.env`. The API and worker read server-side keys from it. The worker is required for uploaded-document extraction.

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

Create a fresh demo via `python scripts/demo_session.py`. Reset only a selected session using `python scripts/demo_session.py --reset-session TOKEN` or the UI. This replaces that session's data; other sessions remain private. See [the three-minute script](docs/DEMO.md).

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

The synthetic demo makes no model calls. Real uploads can extract native PDF/text/CSV locally; external extraction requires consent and configured Nemotron/Gemini credentials. Missing credentials and failed verification are visible and do not silently switch to fixtures. ElevenLabs speech is optional and requires fact confirmation. Model IDs/base URLs are configurable; availability must be smoke-tested with your account using `python scripts/smoke_providers.py` (configured live calls may consume credits).

[SPONSORS.md](docs/SPONSORS.md) records implementation and actual live-test status. [DEPLOYMENT.md](docs/DEPLOYMENT.md) explains Tiger Data, private Spaces, migrations and the DigitalOcean App Platform template. No paid resources have been provisioned. Keep populated `.env` files and session bearer tokens private.

## Architecture and collaboration

Pydantic/OpenAPI is canonical; generated TypeScript types drive the frontend. CP-SAT uses integer cents and explicit dates, preserves essential services and reports feasible/optimal/timeout status. Exact quotes, human review, approval and model confidence are separate. A small allowlisted event-transformation language executes reviewed rules; document content is never evaluated as code.

Read [AGENTS.md](AGENTS.md), [ARCHITECTURE.md](docs/ARCHITECTURE.md), [WORKSTREAMS.md](docs/WORKSTREAMS.md) and lane handoffs before edits. This prototype uses private anonymous bearer sessions; account recovery, operational retention policies and production abuse controls require further product work before a public real-data rollout.
