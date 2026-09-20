# Developer A: consequence walkthrough consumption contract

## Assignment before editing

User-directed solo completion remains active. Main was clean, fetched with pruning and fast-forwarded to `8d167648f6d731cc8ca1a9f42afd4661b4aead91` (PR43). Fresh branch/worktree: `codex/dev-a/consequence-walkthrough-contract`, `.worktrees/dev-a-consequence-walkthrough-contract`. Required prerequisites are the complete stage 3 engine/UI/demo merges: PR41 `c420609fe8157bfa6d475106ba3eaae07e1fa996`, PR42 `b53cb5ce194b5b11ab2775a4e9add0da394ab9b5`, and PR43 `8d167648f6d731cc8ca1a9f42afd4661b4aead91`.

Allowed writes are the new `docs/CONSEQUENCE_WALKTHROUGH.md` and this A handoff. The task audits canonical provenance/results, defines B's exact shared integration paths and C14/C15 consumption rules, and adds runtime fields only if the existing contract is insufficient. It does not implement frontend behavior, modify fixtures/generated contracts, call providers, deploy or perform any external financial action.

## Findings

The current `Workspace`, `PlanResult` and `DecisionTrace` contracts are sufficient. Exact source documents/rules, separate evidence/review/approval states, dependencies, selected fixed action/date, deterministic `EventChange` objects, server-computed simulations, exclusions, graph issues and beyond-horizon obligations are already present. No additive backend/schema/type generation change is justified.

The existing original synthetic cancellation preview establishes the required story: remove the $60 phone-service event, accelerate the same $480 device-principal obligation from 2026-11-20 to the 2026-09-04 execution date, and return -82000/8000 cents minimum/ending balance versus the recorded 5000/50000 cents. A blocked forced action has an exclusion reason and no matching decision trace; the frontend must not attribute the fallback candidate ledger to it.

Added `docs/CONSEQUENCE_WALKTHROUGH.md` with field mappings, proof/identity/staleness rules, exact future B paths, the C14 interface/release, C14/C15 acceptance and limits. B can now implement against merged existing contracts without schema churn.

## Validation

- Audited `backend/clausegraph/schemas.py`, `engine.py`, `api.py`, `demo.py`, graph construction, generated frontend aliases and the current page/trace/comparison/evidence consumers.
- Existing real-API `frontend/tests/workspace.spec.ts` already asserts the cancellation preview's -$820 minimum, $80 ending balance, unchanged recorded $500 ending balance and reload non-persistence.
- Source inspection confirms `_action_changes` moves an existing obligation rather than adding a duplicate and `_decision_trace` returns exact before/after events and source provenance.
- Documentation-only checks: relative links reviewed, ownership remains dev-a, `git diff --check` passes, runtime/generated/dependency files remain unchanged.

No provider, private user data, live extraction, human rehearsal, deployment or financial execution occurred. B's integration, C14 implementation and C15 final presentation remain required sequential tasks.
