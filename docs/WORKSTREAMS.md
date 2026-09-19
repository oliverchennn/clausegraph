# Work board

The active shared coordination board is the agent message channel. Each lane is claimed below; checkpoints and interface proposals must also be published live to integration. Separate worktrees prevent file clobbering. Integration order: foundation/contracts -> engine+fixtures -> API+worker -> UI -> integration/CI/deployment checks.

| Lane | Owner | Branch / checkout | Scope | State |
|---|---|---|---|---|
| Integration | root | codex/integration / current checkout | schemas, manifests/lockfiles, fixtures, migrations, CI, final tests | complete locally; external validation documented |
| Extraction/engine | engine agent | codex/engine / .worktrees/engine | engine.py, extraction.py, graph.py, tests/test_engine.py, tests/test_extraction.py, tests/test_graph.py, handoff | integrated; tests passing |
| API/infrastructure/integrations | API agent | codex/api / .worktrees/api | api.py, storage.py, providers.py, worker.py, config.py, tests/test_api.py, handoff | integrated; tests passing |
| Frontend | frontend agent | codex/frontend / .worktrees/frontend | frontend except package.json, lockfile, generated api-types.ts; browser test; handoff | integrated; build and browser tests passing |

Shared changes require a message to root before implementation. Engine/public APIs are specified in ARCHITECTURE.md. API response models generate the committed OpenAPI and TypeScript contracts. Root also owns Docker/deployment configuration and final verification. See docs/handoffs/integration.md and docs/RESUME.md for integrated status; lane handoffs preserve their narrower test scope.

## Next product work

Root completed the documentation assessment on 2026-09-19; no implementation lane was reopened. [HACKATHON_MVP.md](HACKATHON_MVP.md) defines the hackathon scope and acceptance criteria. Delivery order: rehearse/validate the current flow, then decision trace (frontend/engine) and side-by-side previews (frontend/API); bounded stress tests are a stretch goal. These are recommendations, not active assignments. Root coordinates any new trace/preview contracts and generated types before lane implementation. Preserve the current branch/worktree ownership and integrated delivery records.
