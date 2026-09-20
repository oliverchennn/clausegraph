# Cross-document consequence walkthrough contract

## Status and scope

The latest submission cutoff defers B integration, C14 and C15. Finish only the in-progress preview guards; the dedicated walkthrough remains planned. Existing decision traces and action-only comparisons are available in the submission MVP.

PR44 (`e31d415`) supplies the stage 4 field mapping. The follow-up [preview guard task](handoffs/dev-a/consequence-preview-guards.md) adds one missing identity field and backend freshness checks; all financial/provenance data below otherwise reuse existing contracts. B owns shared selection, graph/evidence integration and stale state. C14 owns the dedicated walkthrough and its real-API acceptance; C15 follows only after stage 4 merges.

The walkthrough explains one nonmutating action-only `POST /api/plan/preview` result. It is not a new solver, a recommendation, an execution flow or a substitute for evidence review. React must join identifiers and format backend-returned values only. All event mutation and cash arithmetic remain in the deterministic engine.

## Existing data mapping

| Walkthrough step | Canonical source | Consumption rule |
|---|---|---|
| Source | `DecisionTrace.source_document_ids`, `Rule.evidence`, `Workspace.documents` | Resolve the preview trace's exact document/rule IDs. Open the existing evidence drawer; never copy a quote from an action description. |
| Reviewed rule | `DecisionTrace.source_rule_ids`, each `Rule.review_status`, `evidence_status`, `approval_status` | Keep evidence support, human review and third-party approval as separate statuses. Missing IDs or non-reviewed rules remain visibly unresolved. |
| Dependency | `Rule.dependencies`, `Action.requires`, and `Workspace.graph.edges` | Show only recorded relationships. A rule dependency is not an approval, and a graph edge is not proof of cash feasibility. |
| Proposed action | `PlanResult.actions`, selected `Action`, and `DecisionTrace.execution_date` | Label the action as a preview until the user explicitly applies it. The preview never executes a cancellation, payment, application or message. |
| Deterministic effects | `DecisionTrace.changes[]` | Render returned `remove`, `shift`, `accelerate`, `add` and `fee` changes. Use `before`/`after` event identity, amount and date verbatim; do not recompute or duplicate an obligation. |
| Cash consequence | preview `PlanResult.proposed`, recorded `PlanResult.proposed`, and `Simulation.daily` | Compare server-returned minimum/ending balances and the relevant returned daily rows. Never derive money from document text or sum effects in the browser. |
| Future obligations | `Simulation.beyond_horizon` and warnings | Keep the exact obligation visible. A moved date is timing, not savings; an accelerated debt is the same existing obligation, not a new charge. |
| Blocker | `PlanResult.excluded_actions[action_id]`, graph issues, and absent trace | Explain why a forced action was excluded. Without a trace, do not attach the plan's unrelated cash projection to that blocked action. |

The original synthetic cancellation example is the required acceptance case. Its preview trace shows the $60 service event removed and the same $480 device-principal event moved from November 20 to the returned execution date (September 1 by default, or September 4 when explicitly requested). The engine returns a preview minimum of -$820 and ending balance of $80, compared with the recorded plan's $50 minimum and $500 ending balance. These are established synthetic engine results, not estimates or savings claims.

## Preview identity and readiness

`POST /api/plan/preview` returns the additive nullable `PlanResult.preview_source_plan_id`: the saved plan active when computation began, or null if no saved plan exists. It performs no workspace, history or daily-series write. After computing or loading an immutable cache entry, the route re-reads the private session and rejects changes to its revision, active plan ID, or document ID/version/status snapshot with HTTP 409; deletion returns 401. A source-status change also changes the cache key because worker failure can occur without a revision increment. A preview annotation never enters the cached plan or a later nominal save. Existing source-less previews remain supported.

B must compare this field and the returned revision with the captured source identity before displaying an action comparison. It must also discard late responses when local session/plan/revision, comparison selection or nominal draft changes; backend response freshness is not a subscription to future edits. On 401 clear private UI; on 409 show refresh/retry guidance and no stale walkthrough. The field is provenance, not an adoption credential. Existing explicit nominal application still recalculates, while resilient adoption retains its separate exact-schedule API.

## Result rules

1. A walkthrough is current only while private session ID, workspace revision, recorded plan ID and the selected preview remain current. Closing/replacing a comparison, applying it, resetting/deleting/switching the session, changing reviewed evidence or replacing the plan clears the walkthrough.
2. An action-only preview fixes `force_action_ids` to the selected action and excludes the other known actions. The saved plan and histories stay unchanged until the existing explicit apply control succeeds.
3. A trace belongs to the preview result and selected action. If `excluded_actions[action_id]` is present or no matching trace exists, show the blocker and no action-specific cash timeline. Do not present the candidate plan's fallback ledger as though the blocked transformation occurred.
4. Evidence and graph navigation are read-only callbacks. Evidence edits use the existing review flow and invalidate the preview through the workspace revision. Graph highlighting may select only nodes/edges supported by returned rule IDs.
5. For `remove`, show the original charge and its disappearance. For `accelerate`, show the same event/obligation, unchanged amount and earlier date. For `shift`, explicitly call the change timing rather than savings. For `fee`/`add`, show the returned event as a new cash item.
6. `beyond_horizon` remains attached to the corresponding recorded or preview simulation. A removed charge cannot hide an unrelated future obligation. If an accelerated event moves into the horizon, the before event may disappear from `beyond_horizon` because the same obligation now appears in the computed ledger.
7. Existing essential-service, evidence, approval, dependency and duplicate-obligation gates stay authoritative. The walkthrough never fabricates a permitted trace for a blocked transformation.
8. Cash infeasibility alone does not block an action: a selected action with a returned trace may have negative cash. Label that shortfall honestly. Conversely `unresolved` source/ledger state is not a confirmed permitted cash outcome. Conditional actions and approval assumptions must remain prominently conditional even if the numerical projection is feasible.

## B integration assignment

B's `consequence-integration` may edit the following paths plus its handoff:

| Path | Scope |
|---|---|
| `frontend/src/app/page.tsx` | Retain selected action identity with the preview; clear it with comparison state; provide the C14 placeholder props and evidence/graph callbacks. |
| `frontend/src/components/dependency-graph.tsx` | Highlight only returned rule-linked nodes/edges and preserve existing evidence navigation. |
| `frontend/src/app/globals.css` | Shared walkthrough shell/step/mobile styles released to C14. |
| `frontend/src/lib/types.ts` | Local props alias over existing generated types; no generated contract edit. |
| `frontend/tests/workspace.spec.ts` | Integration regression for preview identity, graph focus, nonmutation and invalidation. |
| `frontend/tests/consequence-integration.spec.ts` | Focused real-API race, session-loss and graph integration regressions. |
| `frontend/tests/review-queue.spec.ts` | Correct the observed initial-response/reload race from PR43's paired push run; preserve review assertions. |
| `docs/handoffs/dev-b/consequence-integration.md` | Actual base/prerequisite SHAs, exact interface, released page section, checks and limits. |

B publishes a typed placeholder in `page.tsx` and releases only that function body/import plus the mounted call to C14. The props must include the current `workspace`, recorded `plan`, selected action ID, candidate preview, `onEvidence(ruleIds)` and `onGraph(ruleIds)`. B owns request/state/graph behavior; C14 must not issue preview requests or calculate financial values.

## C14 and C15 acceptance

C14 consumes the merged B seam and creates only its assigned component, step, test, demo and handoff paths. It renders an accessible source -> reviewed rule -> dependency -> proposed effect -> cash sequence, supports next/previous keyboard operation, provides a readable 390px list layout, opens exact evidence, and navigates to the highlighted graph. Its real-API regression must verify the cancellation values and returned event identities/dates, unchanged workspace/history before apply, blocked-action behavior with no fabricated trace, and no duplicate device debt.

C15 follows the merged A/B/C14 stage. It assembles the complete synthetic judge flow and recovery artifacts, checks desktop and 390px keyboard paths, and records automated timing separately. A human spoken run and successful live provider extraction may be recorded only if actually performed; their absence does not justify weakening or skipping the synthetic application checks.

## Limits

This contract does not add document-change impact, review prioritization, live provider calls, cloud deployment, external execution or adaptive policies. The dependency graph remains an evidence-navigation aid, not a proof engine. The walkthrough explains one returned preview; it does not assert that cancellation is advisable or that the preview is robust across uncertainty.
