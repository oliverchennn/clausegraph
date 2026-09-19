# Hackathon MVP priorities

## Current delivery: ClauseGraph Verify (2026-09-19)

This section supersedes the historical assessment below. The requested bounded verification workflow is implemented, rather than stretch scope: explicit user-assumed date/cent ranges and approval outcomes; exhaustive fixed-plan checking through canonical accounting/evidence gates; SAFE/UNSAFE/UNKNOWN with complete assumptions, horizon, limits, witness and proof-qualified worst cash; revision-bound API; dashboard assumptions, timeline/evidence links and chart overlay; private SQLite/PostgreSQL verification history and outcome points; reproducible semantic gate evaluation. Cent ranges are API-only; the UI exposes income dates and approval outcomes.

The chain is **prose → typed candidate → source/human/approval gates → nominal CP-SAT plan → bounded model → proof or counterexample**. The verifier checks every discrete assignment in the declared Cartesian product, without probabilities or sampling. The default five-second cooperative budget and 10,000-case cap yield UNKNOWN when incomplete unless a concrete failure already proves UNSAFE. It never re-optimizes the saved actions/dates.

The original $50 nominal minimum becomes −$400 on September 26 when payday is September 27. `python scripts/verify_demo.py` checks all eight September 21–28 dates, separately proves no permitted schedule can be safe at the allowed September 28 assignment, then verifies the unchanged schedule after adding $400 of hypothetical opening cash. This is a tight bounded diagnostic, not funding. The six-date September 21–26 UI preset verifies only that narrower model.

General robust synthesis, uncertain expense timing, correlation constraints and adaptive action policies are deferred. The inspected checkout lacked standalone nonmutating comparisons and decision traces; existing comparisons are preserved and verification adds its own event/evidence trace. Broad P1 comparison/history work remains separate scope. Daily closing balances exclude intraday liquidity; the guarantee excludes unmodeled obligations and dates beyond the displayed horizon, while future debt stays visible.

No configured NVIDIA key, PostgreSQL/Tiger Data URL, Spaces service or DigitalOcean token was found. Optional Gemini is configured but unselected and untested. No live model accuracy, cloud deployment, hypertable or performance claims are made. See [the verification handoff](handoffs/verification.md), [architecture](ARCHITECTURE.md) and [revised demo](DEMO.md) for current contracts, checks and limits.

## Historical pre-upgrade assessment

The sections below preserve the earlier assessment and its proposed statuses. The current delivery section above is authoritative for implementation claims.

Updated 2026-09-19 after reviewing AGENTS.md, all lane handoffs, architecture, demo, deployment and sponsor records, and the current engine/API/UI. This is a product assessment and implementation roadmap. Features marked proposed are not implemented by this documentation change. These priorities reflect the user's requested emphasis, not a verified official judging rubric.

## Product thesis and demo promise

ClauseGraph turns fragmented financial documents into an evidence-backed action plan that accounts for how contract clauses interact. The first user is someone with a near-term cash shortfall who needs to know which documented options can bridge it while preserving essential expenses.

The distinguishing workflow is **source clause → reviewed rule → dependency graph → constrained action schedule → deterministic cash projection**. A judge should be able to follow that chain, change one approval and see the result change. The language models extract and check candidate facts; deterministic code evaluates money and the solver chooses permitted actions. Human review and third-party approval remain separate gates.

| Emphasis | What the demo should demonstrate | Evidence available today |
|---|---|---|
| Novelty | Reason across clauses and expose interacting consequences | Cancelling a $60 phone payment also accelerates an existing $480 device debt; the graph links the action to its sources and effects. This is a product differentiator, not a claim of being first or unique in the market. |
| Impact | Help a person bridge a timing gap without hiding obligations | Moving an approved $450 installment changes the synthetic minimum from −$400 to $50; ending cash stays $500. This is $450 of improvement in minimum liquidity, not $450 of savings or measured customer impact. |
| Technical depth | Make a constrained decision from uncertain source material | Typed extraction, evidence checks, an allowlisted event language, dependency/contradiction checks, integer-cent simulation, bounded CP-SAT, versioned evidence and invalidation. Show their effect on one decision rather than listing technologies. |

The three-minute demo in [DEMO.md](DEMO.md) remains the delivery target. Keep the synthetic workflow reliable without credentials. Separately demonstrate one real provider-backed extraction on synthetic evidence once that workflow has passed validation.

## What already exists and where utility is missing

| Area | Implemented evidence | Improvement opportunity |
|---|---|---|
| Evidence and review | Exact quotes/page/version, original downloads, independent evidence/review/approval fields, condition review | Focus the graph and cash chart on the same decision; guide the user to the blocker that matters next. |
| Solver and simulation | Dependencies, essential-service protection, dated actions, cash-gap diagnostics, beyond-horizon obligations, honest solver status | Explain how changed events produce the cash delta and how fragile the selected plan is. |
| Scenarios | Opening cash, income date, approval assumptions and forced-action comparisons; typed `PlanRequest` also supports income amount and exclusions | Preserve the primary plan and compare alternatives side by side under explicit, comparable assumptions. |
| History | Session-private `GET /api/history`, saved assumptions/revisions and persisted chart points | There is no history browser in the current dashboard; use it later for inspecting changes. |
| Extraction | Native parsing, queued NVIDIA extraction plus evidence/OCR adapter, visible errors and consent | Successful live extraction and accuracy are still unverified in the handoff. A mock or provider smoke alone does not close this gap. |
| Delivery | Synthetic fixtures, real-API browser flow, local launcher and deployment template | Rehearse the complete story; record measured results and tested limitations. Cloud deployment is not required to prove the core idea. |

Code anchors: [schemas](../backend/clausegraph/schemas.py), [engine](../backend/clausegraph/engine.py), [API](../backend/clausegraph/api.py), [dashboard](../frontend/src/app/page.tsx), [graph](../frontend/src/components/dependency-graph.tsx), [chart](../frontend/src/components/cash-chart.tsx), [demo assertions](../backend/tests/test_demo.py).

## Delivery order and scope cap

Effort below is relative implementation risk, not a time promise. Preserve the existing stack and dependencies unless a concrete requirement justifies a change.

| Order | Deliverable | Status | Utility / demo value | Effort and owner |
|---|---|---|---|---|
| P0 | Rehearsed synthetic flow plus a recorded live extraction check when credentials/consent are available | Synthetic flow implemented; live workflow unverified | Establishes that both the decision engine and the claimed model integration work | Small rehearsal; live-provider uncertainty. Integration/API |
| P1a | Decision trace linking clauses, changed events and the cash chart | Proposed; source graph and balances exist | Makes novelty and technical depth immediately inspectable | Medium. Frontend + engine, integration for contracts |
| P1b | Side-by-side alternatives that preserve the primary plan | Proposed; individual comparison and history exist | Helps users choose and gives judges an instant before/after | Medium. Frontend + API, integration for contracts |
| P2a | Bounded plan stress test | Proposed; individual what-if inputs exist | Adds a useful answer to “Will this still work if payday moves?” | Medium/high. Engine + API + frontend |
| P2b | Prioritized review queue with a specific next step | Proposed; rules, blockers and review controls exist | Makes a blocked plan actionable without inventing eligibility | Medium. Frontend first; engine for structured blockers |
| P3 | Revision-aware history and change summary | Proposed UI; history endpoint exists | Explains what changed after new evidence or an approval change | Small/medium for inspection; larger for safe restoration. Frontend/API |

**Recommended hackathon scope: complete P0 and P1a/P1b, then freeze features and rehearse.** If time remains, implement P2a as the single stretch feature. P2b/P3 can follow; none is required to finish the existing MVP. Credential delays should not prevent local P1 work, but do prevent claiming live extraction has been verified.

## P1a: Follow a decision from source to cash

Add a “Why this plan?” view focused on a selected action. Highlight its source documents, rules, dependencies and affected events; expose the exact evidence drawer from that view. Selecting an affected date on the chart should show its income/expense events and evidence links. Include an accessible event list so the explanation works without navigating the graph.

Show the installment at its original date and its new date with the same amount. For phone cancellation, show the removed $60 payment and the $480 debt moved from its future date. Retain future obligations visibly. Derive explanations and amounts from server-side event transformations, not generated financial reasoning.

Reuse `DailyBalance.event_ids`, `Action.effects`, graph `rule_ids`, source versions and existing original downloads. The current API does not expose a complete materialized before/after event trace; integration should add a bounded typed trace if needed. Do not reimplement money calculations in React. An LLM-written action description is not proof of causation or optimality.

Acceptance:

- One selection connects source quote → rule → action → before/after event → affected balance, with no missing evidence links treated as verified.
- The approved shift displays minimum −$400 → $50 and ending cash $500 → $500; it says the payment moved rather than claiming savings.
- Acceleration uses the same device obligation once. Missing/deleted evidence remains unresolved.
- Show solver status and whether the objective was proven; a valid trace does not imply all alternatives were proven inferior.

## P1b: Compare alternatives without losing the plan

Pin the recorded plan beside a candidate. Show minimum and ending cash, first shortfall, required cash diagnostic, selected actions, future obligations and assumptions. For the synthetic story, offer recorded approval, denied approval and forced phone cancellation with explicit labels. The baseline ledger with no actions is a separate comparator from the optimized plan.

Current `POST /api/plan` persists its result as `workspace.plan`. The dashboard's “Compare this option” also constructs a fresh request rather than carrying forward all current assumptions. A client-only second card would therefore leave reload/persistence behavior misleading. Add an explicit preview calculation path that preserves the active plan; share optimization, authorization and revision checks with normal planning. Bind previews to the input revision and invalidate stale comparisons after review, intake, upload or deletion. Apply a candidate only through an explicit user choice. Regenerate OpenAPI/types for interface changes.

Acceptance:

- Opening, closing and reloading a preview leave the primary plan intact; preview failures leave it intact too.
- Hold all unchanged inputs constant and show the changed assumptions. Hypothetical approval never updates recorded approval.
- Distinguish **cancellation alone** from **forcing cancellation while letting the optimizer also shift the installment**. The −$820 minimum/$80 ending example is cancellation alone; do not attach those numbers to a different action set.
- Cash deltas come from the server. Do not sum per-action “benefits” when dependencies interact. Compare like-for-like dates/horizons, or visibly identify the mismatch.

## P2a: Test how much disruption the plan can absorb

Start with at most five explicitly labeled cases: current inputs, income 3 days later, income 7 days later, income reduced by $100 (only when the amount allows it), and pending/denied extension. These are user-visible hypothetical stresses, not predicted probabilities. Use deterministic integer-cent inputs and server-side calculations.

Offer two distinct questions: “Does the current action schedule still work?” holds selected actions and dates fixed; “Can a revised plan help?” reruns optimization. Revalidate the fixed schedule's authorization and execution windows in every case before simulation, because `simulate` alone is not an approval gate. If an approval is denied, label the schedule invalid rather than simulating it as permitted. Do not quietly substitute a different action schedule into a result labeled current-plan resilience.

Use the P1b preview path so batch runs do not overwrite the active plan or flood normal plan history. Give the batch a total time budget rather than five unrestricted solver budgets; return status, elapsed time and unknown results honestly. Reuse individual engine results and stop on a changed workspace revision. Current income controls require exactly one projected income event; disable these presets and explain that limitation for multiple-income scenarios until event-specific controls exist.

Acceptance:

- Each row shows exact assumptions, schedule validity, minimum cash, cash-gap diagnostic and solver status; unresolved/unknown results never receive a passing label.
- Results agree with the corresponding individual engine calls. No persisted approvals or actual events change.
- Report “passes these tested cases” rather than a probability or guarantee. Claim a latest safe payday only if the full stated date range was evaluated; isolated samples do not establish a threshold.

## P2b: Tell the user what to review next

Turn the existing count of unreviewed facts into a queue with blocker type, source link and a specific next step: verify an amount against the original, resolve a stated condition, or record an actual third-party decision. Keep evidence validity, confidence, human review and approval separate in the queue.

Prioritize unresolved essential obligations and blockers on useful actions before optional unrelated clauses. Begin with a transparent deterministic ordering. A later conditional preview can estimate the change in minimum cash if approval were obtained, but only when evidence, amount, date and other conditions are already valid. Never assume unknown eligibility or timing to produce a dollar value. When several blockers interact, label the joint scenario; do not attribute its full delta to each fact.

Acceptance: one click opens the right rule/source; saving review recalculates; assistance with unknown eligibility/date stays excluded; no queue action self-grants approval or submits a request. Avoid a new confidence score that obscures the underlying blocker.

## P3: Inspect what changed between runs

Expose existing history with timestamp, revision, assumptions and status. Start with viewing recorded results and comparing metrics. A new revision may have different evidence, so show the revision mismatch and do not claim an exact source/action diff without the matching snapshots. Rich diffs may require additional provenance storage.

Restoring assumptions must recalculate against current evidence; it must not restore an old result as a newly confirmed plan. Preserve existing source-deletion privacy semantics, including removal of historical narratives. Do not broaden retained sensitive data just to add a history screen.

## Evidence of success and feature freeze

Use the existing synthetic acceptance scenario as the reliable demo, and create a small separate set of synthetic evaluation documents with varied wording and native/scanned formats before making extraction-quality claims. Define expected fields and approval/condition states before running them. Record unsupported cases and failures, not only successful examples.

| Measure | How to verify / report |
|---|---|
| Financial correctness | Existing demo assertions: baseline minimum −40000/end 50000 cents; approved shift 5000/50000; denied shift −40000/50000; cancellation alone −82000/8000. Future debt is preserved or relocated once. |
| Decision safety | Unapproved benefits never enter confirmed plans; unresolved sources and timeouts remain visible; essentials stay counted. Use engine/graph/API regression tests. |
| Trace and comparison quality | Every displayed change can be followed to its source/event; previews preserve the active plan and are invalidated on input changes. Add targeted browser/API tests when implemented. |
| Extraction quality | On the separate synthetic set, report exact amount/date/direction matches, valid citations, withheld/invalid outputs, human corrections and total documents/rules. Log model/configuration and distinguish mocks from live runs; do not infer accuracy from model agreement. |
| Responsiveness | Measure extraction latency separately from solve/preview latency on named hardware/model settings. Use actual samples; do not promise a percentile from a tiny demo set. |
| User comprehension | In a short practice session, ask someone to explain why the shift helps and why cancellation hurts. Record observed confusion/time to find the supporting clause; do not present practice feedback as proven real-world impact. |

For live extraction, use synthetic content, server-side credentials and explicit processing consent. Complete upload → worker → extraction/checks → human review → recalculation, including a visible failure case. Follow [SPONSORS.md](SPONSORS.md) for truthful integration reporting; a successful smoke request is only connectivity evidence.

Stop feature work once the chosen flow is coherent. Run checks appropriate to implemented changes, regenerate contracts when changed, and rehearse the three-minute sequence from a clean synthetic session with a local fallback. Update the integration handoff with exact results and remaining limitations.

## Defer beyond this hackathon

Bank aggregation, automated payments/cancellations/applications/messages, broad benefits discovery, generalized recurring-event engines, multi-user case management, new model providers and infrastructure rewrites add scope without improving the central demonstration enough. Keep existing audio optional. Authentication recovery, retention operations, rate limits and deployment hardening belong on the path to a public real-data release; the local synthetic demo does not establish production readiness.

Review checkpoint: existing demo/engine/graph tests passed **57 tests in 2.51s** on 2026-09-19. No runtime code, shared contracts, dependencies or external services were changed during this assessment. See [handoffs/integration.md](handoffs/integration.md) for the full handoff and earlier broader validation.
