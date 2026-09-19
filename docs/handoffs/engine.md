# Extraction/engine handoff

Branch: `codex/engine`, checkout `.worktrees/engine`. Re-claimed through the live agent board on resume. Integration checkpoint was merged (83db8ac), preserving canonical integration versions of shared files. Shared deployment/plan-assumption commits 1aab7e6 and 9691554 were subsequently cherry-picked. Integrate only the engine correction commit after the original 646d0ff checkpoint, not these shared/merge commits.

## Completed

- `engine.py`: integer-cent daily simulation over [start, start+horizon), beyond-horizon debt retention, existing-debt acceleration, exclusive event writers, essential/historical-event protection, execution windows and dependency ordering. Bounded deterministic CP-SAT maximizes minimum cash, then minimizes fees, burden and execution dates; reports incomplete proof/timeouts honestly. Negative optimal liquidity is an explicit cash diagnostic, without inventing funding.
- Separate evidence, review, condition and approval gates; conditional assumptions never mutate persisted approvals. Unresolved or unsupported source-backed projected income is withheld from the baseline; explicit user-entered income without source rules and immutable actual income remain. Pending direct income needs an eligible claim action for conditional execution.
- `extraction.py`: native PDF/UTF-8 text/CSV extraction, PDF/page/text limits, exact page-local quote/version/offset checks, Decimal-to-cent literal validation, explicitly labeled USD/cents CSV columns, explicit date validation, model self-review/approval/condition resets, allowlisted compilation with provenance-backed amounts and dates. PDF parsing now runs in a killable spawned process with a 20-second deadline, 20 MiB byte cap, 200-page cap and incremental 2-million-character limit.
- `graph.py`: typed evidence/rule/action/event/entity graph, source-bearing edges, contradictory same-identity clauses, ambiguous entities, missing references, rule/action cycles and explicit supersession.
- Regression tests cover demo arithmetic, approvals, unsupported benefits, source injection, exact provenance, horizon boundaries, relocation, essential protection, event collisions, dependencies, honest solver statuses and twelve exhaustive small-case solver comparisons.
- Resumed audit fixed concrete gaps: optimization independently revalidates each action's evidence/date/amount/fee and target-rule linkage; cancellation cannot omit evidenced debt acceleration or fees. Unreviewed/deleted-source expenses remain counted and prevent a confirmed plan, as do not-yet-materialized unresolved obligations. Explicit links expose contradictory obligation rules with different labels; duplicate obligation/due-date entries require review. Extreme monetary/burden magnitudes and overflowing calendars fail explicitly before solver overflow. Every PlanResult retains a deep copy of the normalized scenario assumptions.

## Interfaces

Public signatures match `docs/ARCHITECTURE.md` without engine-lane changes to canonical schemas. `validate_extraction` deep-copies results and leaves human review pending; it resets model-supplied condition resolution and approval. `compile_rules` retains all rules for review and filters executable actions/events. API must explicitly synchronize candidate action review/approval after reviewing its source rules. `simulate` checks structural ledger validity; evidence/approval authorization belongs to `optimize`.

`action_evidence_blocker(action, rules, events=None) -> str | None` is a reusable internal check used by compilation and optimization. Supplying events additionally checks exact target source/dependency linkage; source-free intake targets require a quoted monetary match. Conditional approval assumptions do not bypass this check. `extract_native` retains its public signature; callers need no change for subprocess isolation. Optimizer input ValueErrors (ambiguous income controls, invalid calendar) should map to API HTTP 422; API lane was notified.

Root added `RuleReview.conditions` and fixed payroll classification after proposals through the live channel. Root was advised to make remaining money fields strict integer contracts consistently.

## Exact checks

Using root `.venv/Scripts/python.exe`, cwd this checkout:

- `-m pytest backend/tests -q`: **81 passed, 1 skipped in 3.31s** (2026-09-19). The skip is PostgreSQL without POSTGRES_TEST_URL; this checkout does not yet include the API lane's new tests.
- `-m ruff check backend/clausegraph/engine.py backend/clausegraph/extraction.py backend/clausegraph/graph.py backend/tests/test_engine.py backend/tests/test_extraction.py backend/tests/test_graph.py`: **All checks passed**.
- Earlier standalone demo optimization: OPTIMAL; baseline minimum -40000, proposed minimum 5000, ending 50000, only shift-payment selected.

## Remaining limitations / next steps

Root must integrate this lane correction and run the updated API/browser/full-stack checks. Live provider execution and the API lane's revised review/deletion synchronization have not been exercised by this lane. Contradiction matching uses normalized title/kind/parties plus explicit event links; ambiguous account linking remains a review issue. Compilation and optimization both gate rules, cycles, contradictions and action effects; executing an action still requires optimization and explicit user follow-through outside the app. Literal matching and narrow operation cues do not prove semantic truth, so human review and consequential provider verification remain necessary. The conservative cue/fee parser can withhold valid unusual wording for review. Native image-only PDFs return empty text pages for the separate consent-gated vision workflow; process isolation provides a hard time bound but is not an OS memory quota.
