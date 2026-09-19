# Work board

## ClauseGraph Verify delivery lanes

Root reopened isolated lanes from clean integration commit d5cd282. Engine `codex/verify-engine` / `.worktrees/verify-engine` completed 17a5743 (integrated as 151b424); API `codex/verify-api` / `.worktrees/verify-api` completed b12cec8 (integrated as d6a786b); frontend `codex/verify-frontend` / `.worktrees/verify-frontend` completed e0a3963 (integrated as a6a5cdb). Root owns uncertainty contracts, generated types, migration003, semantic eval, impossibility/cash demo, docs and final checks. Original lane checkouts are untouched. Latest work is governed by [verification handoff](handoffs/verification.md); the older assignments below are historical. No implementation agents remain assigned pending work after integration.

The active shared coordination board is the agent message channel. Each lane is claimed below; checkpoints and interface proposals must also be published live to integration. Separate worktrees prevent file clobbering. Integration order: foundation/contracts -> engine+fixtures -> API+worker -> UI -> integration/CI/deployment checks.

| Lane | Owner | Branch / checkout | Scope | State |
|---|---|---|---|---|
| Integration | root | codex/integration / current checkout | schemas, manifests/lockfiles, fixtures, migrations, CI, final tests | complete locally; external validation documented |
| Extraction/engine | engine agent | codex/engine / .worktrees/engine | engine.py, extraction.py, graph.py, tests/test_engine.py, tests/test_extraction.py, tests/test_graph.py, handoff | integrated; tests passing |
| API/infrastructure/integrations | API agent | codex/api / .worktrees/api | api.py, storage.py, providers.py, worker.py, config.py, tests/test_api.py, handoff | integrated; tests passing |
| Frontend | frontend agent | codex/frontend / .worktrees/frontend | frontend except package.json, lockfile, generated api-types.ts; browser test; handoff | integrated; build and browser tests passing |

Shared changes require a message to root before implementation. Engine/public APIs are specified in ARCHITECTURE.md. API response models generate the committed OpenAPI and TypeScript contracts. Root also owns Docker/deployment configuration and final verification. See docs/handoffs/integration.md and docs/RESUME.md for integrated status; lane handoffs preserve their narrower test scope.

## Next product work

Root implemented the judge-flow follow-up on `codex/judge-flow` on 2026-09-19. [HACKATHON_MVP.md](HACKATHON_MVP.md) records the acceptance criteria now covered by typed decision traces and side-effect-free side-by-side previews. OpenAPI/types, backend regression tests, clean frontend install/build and real-API desktop/mobile browser tests were refreshed. This judge-flow work is now merged with ClauseGraph Verify and the graph cycle refactor on codex/integration. Freeze the combined local flow and rehearse; live-provider/cloud validation remains separate. Preserve the earlier branch/worktree ownership records as historical integration evidence.
