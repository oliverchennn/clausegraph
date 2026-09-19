# Extraction/engine handoff

Branch: `codex/engine`, checkout `.worktrees/engine`. Claimed through the live agent board. Shared root commits 6581b46, e66f31d and 47f7c16 were cherry-picked before this checkpoint.

## Completed

- `engine.py`: integer-cent daily simulation over [start, start+horizon), beyond-horizon debt retention, existing-debt acceleration, exclusive event writers, essential/historical-event protection, execution windows and dependency ordering. Bounded deterministic CP-SAT maximizes minimum cash, then minimizes fees, burden and execution dates; reports incomplete proof/timeouts honestly. Negative optimal liquidity is an explicit cash diagnostic, without inventing funding.
- Separate evidence, review, condition and approval gates; conditional assumptions never mutate persisted approvals. Unresolved or unsupported source-backed projected income is withheld from the baseline; explicit user-entered income without source rules and immutable actual income remain. Pending direct income needs an eligible claim action for conditional execution.
- `extraction.py`: native PDF/UTF-8 text/CSV extraction, PDF/page/text limits, exact page-local quote/version/offset checks, Decimal-to-cent literal validation, explicitly labeled USD/cents CSV columns, explicit date validation, model self-review/approval/condition resets, allowlisted compilation with provenance-backed amounts and dates.
- `graph.py`: typed evidence/rule/action/event/entity graph, source-bearing edges, contradictory same-identity clauses, ambiguous entities, missing references, rule/action cycles and explicit supersession.
- Regression tests cover demo arithmetic, approvals, unsupported benefits, source injection, exact provenance, horizon boundaries, relocation, essential protection, event collisions, dependencies, honest solver statuses and twelve exhaustive small-case solver comparisons.

## Interfaces

Public signatures match `docs/ARCHITECTURE.md` without engine-lane changes to canonical schemas. `validate_extraction` deep-copies results and leaves human review pending; it resets model-supplied condition resolution and approval. `compile_rules` retains all rules for review and filters executable actions/events. API must explicitly synchronize candidate action review/approval after reviewing its source rules. `simulate` checks structural ledger validity; evidence/approval authorization belongs to `optimize`.

Root added `RuleReview.conditions` and fixed payroll classification after proposals through the live channel. Root was advised to make remaining money fields strict integer contracts consistently.

## Exact checks

Using root `.venv/Scripts/python.exe`, cwd this checkout:

- `-m pytest backend/tests -q`: **65 passed in 2.15s** (2026-09-19).
- `-m ruff check backend/clausegraph/engine.py backend/clausegraph/extraction.py backend/clausegraph/graph.py backend/tests/test_engine.py backend/tests/test_extraction.py backend/tests/test_graph.py`: **All checks passed**.
- Earlier standalone demo optimization: OPTIMAL; baseline minimum -40000, proposed minimum 5000, ending 50000, only shift-payment selected.

## Remaining limitations / next steps

Checkpoint requested by user to pause/change models; no additional scope started. Root must integrate this lane commit and run API/browser/full-stack checks. Live provider execution and API worker review synchronization have not been exercised by this lane. Contradiction matching is conservative and based on normalized title/kind/parties; ambiguous account linking remains a review issue. Compilation and optimization both gate rules, while full action-cycle/contradiction enforcement occurs in optimizer; compiler-only consumers should not execute actions without optimization. Numeric/date matching proves literals are quoted, not semantic truth; human review and consequential provider verification remain required. Native image-only PDFs return empty text pages for the separate consent-gated vision workflow.
