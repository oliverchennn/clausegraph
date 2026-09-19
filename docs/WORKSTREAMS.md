# Work board

The active shared coordination board is the agent message channel. Each lane is claimed below; checkpoints and interface proposals must also be published live to integration. Separate worktrees prevent file clobbering. Integration order: foundation/contracts -> engine+fixtures -> API+worker -> UI -> integration/CI/deployment checks.

| Lane | Owner | Branch / checkout | Scope | State |
|---|---|---|---|---|
| Integration | root | codex/integration / current checkout | schemas, manifests/lockfiles, fixtures, migrations, CI, final tests | active |
| Extraction/engine | engine agent | codex/engine / .worktrees/engine | engine.py, extraction.py, graph.py, tests/test_engine.py, tests/test_extraction.py, tests/test_graph.py, handoff | assigned |
| API/infrastructure/integrations | API agent | codex/api / .worktrees/api | api.py, storage.py, providers.py, worker.py, config.py, tests/test_api.py, Docker/deploy, handoff | assigned |
| Frontend | frontend agent | codex/frontend / .worktrees/frontend | frontend except package.json, lockfile, generated api-types.ts; browser test; handoff | assigned |

Shared changes require a message to root before implementation. Engine/public APIs are specified in ARCHITECTURE.md. API lane must expose canonical models through response_model. Root creates demo.py. Root will export OpenAPI and generate TS after API integration; frontend may use generated aliases from contract-only schema export meanwhile.
