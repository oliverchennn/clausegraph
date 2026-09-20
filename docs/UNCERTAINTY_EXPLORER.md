# Uncertainty explorer consumption specification

## Status and delivery gate

This is A's stage 2 consumption specification, audited against merged `1a24143` (PR32). The backend already supports the required dimensions and bounded witness data. This task adds no API fields, algorithms or frontend behavior. B's controls and C12's view remain assigned future implementation. Stage 1's B UI/C11 acceptance still precedes stage 2 implementation; A may prepare this specification while that work finishes.

The [bounded uncertainty contract](UNCERTAINTY_CONTRACT.md) remains authoritative for domains and proof semantics. Use the existing generated `VerificationRequest` and `VerificationResult` contracts. No additional backend field is required for the v1 view specified here. B reviews this mapping before consumption; a requirement for more data returns to A as a scoped contract request. This specification is not B's release of existing files to C.

## Supported experience and data limits

The v1 explorer edits up to eight independent amount, date and approval dimensions, then inspects the backend's selected failing assignment and its evidence. A table of that assignment's dimensions, failure reasons and events is supported. The result retains **one counterexample** and **one worst permitted cash simulation**; these can concern different assignments. There is no list of every evaluated case, failure frequency, per-case status map, success count or failure probability. Do not construct a colored domain grid or imply that the displayed witness is the complete set of failures.

Changing the dimensions starts a different bounded check of the same saved schedule. It does not repair the previous failure or establish that the original domain was safe. Selecting a result/detail/evidence item is read-only: no recalculation, plan adoption, approval update or provider request. Nominal optimization, fixed-plan verification, cash-gap diagnostics and future synthesis remain separate operations.

| UI need | Existing source | Consumption rule |
|---|---|---|
| Income choices | `workspace.scenario.events` | Known projected income events on/after the horizon start; exclude actual income and expenses. Multiple events can be varied independently. |
| Approval choices | `workspace.scenario.actions` and `workspace.rules` | Distinguish action/rule labels and IDs. Reject IDs ambiguous across both collections. The API allows known targets even when they do not affect a selected action; explain that such a dimension may change only the case count. |
| Per-dimension controls | `VerificationRequest.uncertainties` discriminated by `kind` | Stable unique `id`, unique `(kind, event_id/target_id)`, explicit `basis=user_assumption` and rationale. A date and amount for the same income are distinct valid properties. |
| Saved schedule/context | `result.fixed_actions`, `nominal_assumptions`, `plan_id`, `revision`, horizon fields | Display result-owned actions/dates/assumptions; never label a new nominal plan with an older check. Approval assumptions remain hypothetical even after SAFE. |
| Coverage and status | `status`, `solver_status`, `checked_cases`, `coverage_complete`, `statement`, `warnings` | Server proof fields govern labels. `checked_cases` counts visited assignments, including ones without cash simulations. It is not a count of safe cases. |
| Failing assignment | `counterexample.assignment` | Join `dimension_id` to this result's `assumptions.uncertainties`, not the edited form. Render amounts as cents/currency, dates as ISO dates and approval outcomes as explicit hypotheses. Preserve fallback IDs when a title is unavailable. |
| Failure reasons/date | `counterexample.failures`, `earliest_failing_date`, nullable `balance_cents` | Use “Failure date in this witness” for v1. Never infer the earliest possible cash failure solely from full enumeration when some cases lack resolved cash facts. Null balance/date means unavailable, not zero/today. |
| Failure evidence | `failures[].source_rule_ids` and optional `action_id` | Navigate through B's existing evidence callback. Missing IDs remain visibly unavailable; an empty list does not assert supported evidence. |
| Witness cash/events | `counterexample.simulation`, `counterexample.events` | Use only returned cash rows and returned event amounts/dates. `events[].action_ids` links to `result.fixed_actions`; event `source_rule_ids` links to rules/evidence. Do not replace a hypothetical payday with today's nominal event. |
| Worst permitted balance | `worst_case`, `worst_case_assignment`, `worst_case_proven` | Keep its assignment attached. If unproven, label it observed among fully evaluated authorized cases. It is not necessarily the selected counterexample's balance. Null means no permitted cash result is available. |
| Future obligations | Each simulation's `beyond_horizon` plus warnings | Retain the obligations beside the corresponding witness/worst result. Do not insert them into displayed daily cash, discard them, or call a deferral savings. |

Authorization and other structural failures may produce a counterexample with no simulation, no balance and no event trace. Show the supplied failure reason/evidence and omit the cash overlay. Another authorized assignment may still have an observed `worst_case`; never attach that cash to the unauthorized witness. Fully visited but unresolved evidence can instead yield UNKNOWN with no counterexample. Preserve its warnings without inventing a failure row or safe trace.

## Exact case counts and budgets

Each individual amount bound is at most 10000000000 cents, safely representable as a JavaScript integer. Their Cartesian product may not be. Backend `total_cases` is an arbitrary-precision integer serialized as a JSON number; ordinary browser JSON parsing can round it irreversibly. Converting the parsed total to a string or `BigInt` does not recover the original integer.

For exact display, B computes **domain cardinality only** from validated bounds with integer arithmetic. This is not a frontend cash calculation. Convert operands to arbitrary-precision integers before products; retain the result as a decimal string for display. For a saved result, derive it from `result.assumptions`, never from the current form. Use UTC Gregorian calendar-day ordinals for dates, avoiding local-time/DST differences; validate the entire ISO date, including month/day and years below 100. Keep arbitrary-precision display state out of JSON request bodies.

| Dimension | Inclusive cardinality |
|---|---|
| Amount | `maximum_cents - minimum_cents + 1` |
| Date | `ordinal(latest) - ordinal(earliest) + 1` |
| Approval | Number of distinct declared outcomes |
| Combined domain | Product of dimension cardinalities; zero dimensions means one case |

If exact arithmetic is unavailable, a safe-integer total may be displayed exactly; otherwise say “Total exceeds JavaScript's exact integer range” and show the exact checked count plus backend coverage/status. Never format a rounded large total as exact, round a coverage fraction to 100%, or use the preflight count as proof of safety. An invalid draft has no valid count and cannot submit.

Examples: 90000–100000 cents contains **10001** assignments ($100 of width, inclusive); two cents × two dates × three approval outcomes contains **12**; eight binary dimensions contains **256**; eight full amount ranges contains exactly `10000000001 ** 8` assignments. These are cardinalities, not probabilities or throughput promises.

Preflight compares the exact product with the chosen `max_cases`. Keep defaults 10000 cases/5 seconds and ceilings 10000/10 seconds. Explain a product over the case cap cannot be exhausted in that run, but may still yield a conclusive UNSAFE witness. A product under the cap can time out or retain unresolved facts. Enumeration is a deterministic prefix, not a representative sample; no silent bound reduction, endpoint-only approximation or automatic budget increase is allowed. Timing is cooperative, checked before each case; it is not a hard HTTP deadline.

## Result states to preserve

| Response state | Required presentation |
|---|---|
| SAFE, complete/resolved | Every declared assignment checked for this fixed schedule/model/horizon. Keep nominal hypothetical assumptions and guarantee limits visible. |
| UNSAFE, complete | A concrete witness violates a property. Display its reasons and permitted cash, if any; completeness alone does not prove a cash worst case. |
| UNSAFE, incomplete | Found failure, incomplete coverage. Unvisited assignments remain unchecked; the witness still proves UNSAFE. |
| UNKNOWN, incomplete | No conclusive violation found in the visited prefix; unchecked assignments are unknown. |
| UNKNOWN, complete | Every assignment visited, but necessary facts unresolved. “Full coverage” must not become “safe.” |
| INVALID_MODEL or no simulation | Show server status/warnings, unavailable cash and corrective guidance. Do not substitute nominal cash or an empty success result. |
| HTTP 401/409/422 or transport error | No new verification result. Handle session loss, stale/incomplete-source guidance, validation errors or retry respectively. |

Nominal CP-SAT `objective_proven` does not establish any verification claim. The minimum of the selected witness is not a minimum across all schedules. Cash-gap nested results remain separately labeled hypothetical-opening-cash diagnostics; they do not update the active plan or appear in verification history merely because the user viewed them.

## Request identity, history and B-to-C interface

B owns dimension state, validation/preflight counts, submission, selection and stale-response rejection. Scope each request to private session, active plan ID/revision, the full dimension/budget snapshot and a request generation. Abort superseded work and reject late responses even if cancellation races with completion. Dimension, rationale, budget, session, input revision and active-plan changes clear current verification, cash-gap and selected failure details together. A plan can change without changing the revision. A preview leaves the saved schedule untouched; applying it invalidates old results.

`POST /api/verify` saves a private verification record only after rechecking current plan/revision. The cash-gap endpoint persists nothing. On deletion/reset/session loss, clear rendered references immediately so a late read cannot restore deleted content. Keep history read-only and result-owned; historical rule IDs must not silently resolve to today's edited source text as proof. Follow [history semantics](HISTORY_CONTRACT.md). Incomplete source processing produces HTTP 409; an empty review queue does not remove that gate.

B publishes the typed C12 interface in its merged handoff: nullable current result, result-owned dimension/target labels, selection key and callback, evidence callback accepting rule IDs, stable browser selectors, and the exact import/render/callback wiring section released in `verify-plan.tsx`. C receives the result and callbacks without owning requests, form state or financial calculations. The exact TypeScript shape is B's responsibility using generated types. Do not import C's component before it exists on main. C's assigned new paths and release expiry remain those in [DEV_C.md](DEV_C.md); this document creates no additional C permission.

## Future B assignment and acceptance

After stage 1 acceptance and this specification's review/merge, B's `uncertainty-explorer-ui` may edit only the following paths plus its own handoff. New paths are named here so the eventual starting/prerequisite SHAs can be recorded before implementation.

| Allowed B path | Scope |
|---|---|
| `frontend/src/components/verify-plan.tsx` | Controls, requests, coverage/selection integration and eventual C12 wiring release; preserve existing result behavior until C's component merges. |
| `frontend/src/lib/uncertainty.ts` (new) | Typed shared consumption interface, draft validation and exact domain-count helpers; no cash arithmetic. |
| `frontend/src/lib/types.ts` | Local aliases of existing generated uncertainty/result types. |
| `frontend/src/app/page.tsx` | Shared result identity, invalidation and existing evidence callbacks only. |
| `frontend/src/app/globals.css` | Styles for B's controls/coverage integration only. |
| `frontend/tests/uncertainty.spec.ts` (new) | B's real-API controls/count/identity/error acceptance. |
| `frontend/tests/verification.spec.ts`, `frontend/tests/history.spec.ts` | Affected selectors and regression coverage. |
| `docs/handoffs/dev-b/uncertainty-explorer-ui.md` | Actual starting/prerequisite SHAs, interface, C wiring release and exact checks. |

B does not implement C's `uncertainty-failure-view.tsx` or its test file. If a required existing shared file falls outside the table, record an explicit assignment change before editing. Generated `api-types.ts`, manifests, locks and dependencies remain A-owned.

Acceptance is the existing stage 2 assignment, with these concrete checks:

- Multiple incomes, combined amount/date/approval, singleton ranges, zero/eight/nine dimensions, duplicate IDs/properties, invalid targets/dates and independent action/rule approvals. Include date arithmetic across DST/leap day and valid years below 100 when implementing exact counts.
- 10001-cent and eight full-range products: exact decimal display from bounds or explicit large-count qualification. Both preflight and a loaded result use the correct snapshot; budget cutoff never becomes SAFE.
- Safe, unsafe, unknown, zero checked cases, incomplete UNSAFE, and full-coverage/no-cash authorization. Worst-assignment and witness labels remain distinct; cash and evidence come from the appropriate backend result.
- Stale submission/response, same-revision plan replacement, input edits, session switch, source/session deletion, reset and history reload. Preserve preview nonmutation and clear both verification and cash-gap state when their assumptions change.
- B validates controls on keyboard/390px and existing history regressions. C12 validates its accessible table/details, evidence links and no-cash failure states after the named merges/release. Each runs required frontend/browser checks with the pinned toolchain; A reviews the B-lane PRs.

Source/API observations and checks are in A's [task handoff](handoffs/dev-a/uncertainty-explorer-contract.md). They are synthetic engine/API evidence, not a completed explorer, browser acceptance, live inference or human rehearsal.
