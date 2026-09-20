# Developer A: uncertainty explorer consumption specification

## Assignment before editing

The user requested the next task after cash-gap guards. Inspected clean main/worktrees, fetched origin with pruning, confirmed PR32 merged, and fast-forwarded clean main. Starting commit: `1a241436ad2b721ff68f24e8de58eeaf6ab3a6a0` (PR32). Fresh branch: `codex/dev-a/uncertainty-explorer-contract`; worktree: `.worktrees/dev-a-uncertainty-explorer-contract`. Existing worktrees/branches, user changes and services are preserved.

Stage 1 B UI/C11 deliveries are not merged. The assignment explicitly permits A to specify the next stage while the current UI finishes, while keeping feature implementation ordered. This task therefore completes the consumption audit/specification portion of A's `uncertainty-explorer-contract`: validate the existing backend data against B's controls and C12's bounded failure view, document exact count/coverage and witness semantics, identify any required additive contract work, and record exact future B paths. It does not start stage 2 runtime/UI implementation or declare the stage complete.

Required merged contracts: PR20 uncertainty validation (already in starting main), PR29 cash-gap `b5d9204a62ba854cfd82c1a8bf90ca90b0adf174`, PR30 incomplete-source guard `5e79c1d7b571a0c67bc0bb41e70cd0be405265e5`, PR31 assignment `8fa1279c61e702d82f2adb80729f082bfcbc892e`, and PR32 cash-gap guards above. No unmerged B/C work is consumed.

Allowed writes: `docs/UNCERTAINTY_EXPLORER.md` (new), `docs/UNCERTAINTY_CONTRACT.md`, `docs/HACKATHON_ASSIGNMENTS.md`, `docs/WORKSTREAMS.md`, `docs/RESUME.md`, and this handoff. Backend/frontend implementation, tests, generated contracts, dependencies, fixtures, scripts, C's assignment and all historical/peer handoffs remain unchanged. Local audit outputs may be stored under this worktree's ignored `.data/validation/`.

Acceptance: map controls and accessible failure details to actual generated fields; retain inclusive date/cent domains, multiple incomes, eight dimensions, 10000-case/10-second ceilings, no sampling and unchanged financial semantics. Specify exact or qualified huge counts without trusting rounded JSON numbers; distinguish full coverage, proof, observed witnesses and unavailable simulations. Define stale/session/history/evidence behavior, B-to-C handoff/release requirements and exact B paths without implementing/releasing C wiring prematurely. Validate factual claims against source and focused existing engine/API/privacy tests; check docs/ownership/current-main and unchanged contracts. Publish for B review and normal CI, then stop. No live calls, deployment or financial execution.

## Findings and validation

The existing generated contract is sufficient for a v1 table of the returned witness's dimensions, failures, events/evidence and future obligations, with a separately labeled worst permitted cash result. No backend/schema additions are necessary for this scope. The API retains one selected counterexample and one worst cash assignment, which can differ; it does not return every case's outcome or failure frequencies. A heatmap of safe/unsafe domain cells would require data that is not available and is outside this specified view.

Added [UNCERTAINTY_EXPLORER.md](../../UNCERTAINTY_EXPLORER.md): field mappings, control targets, null/coverage/proof labels, exact or qualified domain counts, case/time behavior, request/session/history identity, B-to-C interface requirements, exact future B paths and acceptance. The existing [bounded contract](../../UNCERTAINTY_CONTRACT.md) keeps its financial semantics and now links the specification, names current assignments and documents the merged source-processing gate. Shared docs record PR32 merged and the current specification task; stage 1 UI/C11 gates and C's existing path/release requirements are preserved.

The count design reconstructs a decimal cardinality from individually exact bounds using integer arithmetic, or explicitly qualifies a total outside JavaScript's safe range. It never converts the already-rounded parsed `total_cases` back to an allegedly exact integer. Preflight only counts the domain; all money/proof calculations remain backend-owned. B's browser implementation and typed C12 interface/release are still future work and require their named prerequisites.

## Source and real-API observations

Read canonical schemas, verifier gates/enumeration/witness construction, verification persistence/privacy behavior, generated types and existing B controls/history/overlay consumers. Existing tests already cover independent small-ledger oracles, multiple incomes, invalid dimensions/targets, every-cent boundaries, deterministic witness retention, unresolved/no-cash states, and private/stale/deleted history. No new runtime defect was reproduced in this consumption scope and no implementation or test files were changed.

An additional worktree-local synthetic ASGI/SQLite audit (`PYTHONPATH=backend python .data/validation/audit_uncertainty.py`) exercised the actual routes with provider transport forbidden. Every verification preserved the workspace and fixed actions and appeared in private verification history. Both disposable sessions were deleted successfully. Observations:

| Declared case | Observed backend result |
|---|---|
| Original payday September 21–26 | SAFE; 6/6; full coverage and proven worst case; no counterexample. |
| Original payday September 21–28 | UNSAFE; 8/8; witness payday September 27, failure September 26 at -40000 cents; rule-loan provenance and future device debt present. |
| Two dates × two amounts × three action approvals | UNSAFE; 12/12, full coverage but no proven cash worst case; authorization witness has null simulation/balance, while observed authorized minimum is 5000 cents. |
| First case of original eight-date range | UNKNOWN / CASE_LIMIT; 1/8, incomplete and unproven. |
| First case of September 27–28 | UNSAFE / CASE_LIMIT; 1/2 with concrete witness and incomplete coverage. |
| 90000–100000 cents, max_cases=1 | Exactly 10001 possible cases; UNKNOWN / CASE_LIMIT, 1 visited. |
| Eight incomes with full 0–10000000000 cent ranges | Exact Python/JSON product `10000000001 ** 8`; UNKNOWN / CASE_LIMIT, 1 visited. No eager enumeration of the domain. |

Raw responses, assertions and compact observations remain in ignored `.data/validation/`. These are synthetic backend observations, not browser count implementation, a throughput benchmark, live inference or human rehearsal. Existing clock-boundary tests isolate budget semantics using a synthetic clock; their passes do not promise that 10000 cases finish within a real time budget.

## Checks

Python 3.12.14 from the root `.venv`, running against this isolated worktree. `python scripts/install_hooks.py` succeeded using the existing managed hook.

| Command/check | Result |
|---|---|
| `python -m pytest backend/tests/test_uncertainty_limits.py backend/tests/test_verification.py backend/tests/test_verification_api.py backend/tests/test_history_api.py -q` | 106 passed, 8 PostgreSQL variants skipped in 24.47s; two existing Starlette/AnyIO deprecation warnings. |
| `PYTHONPATH=backend python .data/validation/audit_uncertainty.py` | Seven real-API observations above passed; no provider requests, unchanged workspaces/fixed actions, private history roundtrips and session deletion. |
| `create_app().openapi()` compared with parsed `docs/openapi.json` | Exact equality. Schemas and generated OpenAPI/TypeScript unchanged. |
| `python -m ruff check backend scripts` | Passed. |
| `git diff --check` | Passed; existing Windows line-ending notices only. |
| Pre-publication fetch/prune | Main still `1a24143`; no open peer PR observed at this check. |

No local PostgreSQL test URL is configured. No full backend/frontend/browser/install rerun is needed locally for this Markdown-only change; normal PR CI remains required and covers those checks. Final local validation passed: exactly six assigned A-owned documentation files, 53 resolving relative links, nine future B paths matching base ownership, unchanged runtime/generated/C/peer files, current-main ancestry and no whitespace/conflict markers. The installed pre-push hook checks the committed handoff and base policy during publication.

## Handoff and remaining gates

B reviews the proposed consumption mapping and exact future scope before merge. This task does not claim B sign-off or release `verify-plan.tsx` to C12. After stage 1 acceptance, B can implement the assigned controls and publish its typed interface/release; C12 follows A/B merges and its existing assignment. An additional backend need goes to A rather than being simulated by the frontend. No stage 2 runtime implementation, stage completion, robust synthesis or optional feature is authorized by this publication.

Stop after publishing this specification for B review/full CI. Preserve the original synthetic fallback and prior worktrees/services. No user-session access, external processing, paid resource, frontend change, financial execution or deployment occurred. Successful live extraction and human spoken rehearsal remain outstanding as already recorded.
