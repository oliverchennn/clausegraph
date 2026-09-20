# Hackathon A/B/C assignments

User-approved priority order, 2026-09-20: finish important existing work, then **#2 cash-gap explanation -> #3 uncertainty explorer -> #1 resilient-plan synthesis -> #4 consequence walkthrough**. **#5 document changes is time-permitting; #6 review by decision impact is lower priority still.** Numbers refer to the curated ideas, not execution order. This is assignment scope, not a claim that these features exist.

## Execution and ownership

- User-directed remaining effort is approximately **A 35% / B 35% / C 30%**. A owns deterministic backend/contracts/generated types, fixtures/scripts, shared docs and integration. B owns frontend state/forms, shared primitives and integration. C implements assigned frontend views and owns demo materials/rehearsals/tests through explicit dev-b delegations in [DEV_C.md](DEV_C.md). C's assigned deliverables are required; C's additional review is optional.
- Required stages below are authorized as a queue. Each developer takes one bounded lane task at a time and stops after its handoff/PR; the next task starts in a fresh worktree only when its prerequisites are merged. This authorization does not permit implementing another lane, skipping stages or changing financial guarantees. B may prepare read-only UX work while awaiting A's contract merge.
- Starting base was `e65464c`; refreshed main is `5e79c1d`, including PR25-28, PR29's cash-gap API/contracts and PR30's incomplete-source guard/live failure record. The previous C queue is complete per the user. Do not repeat completed tasks or rewrite peer handoffs. B can consume the merged cash-gap contract; its UI/demo are still pending. See [WORKSTREAMS](WORKSTREAMS.md) for merge SHAs and remaining limits.
- Every task starts from freshly fetched `origin/main`. Before implementation, record actual starting SHA, exact allowed files, required merged contract/release SHAs and checks in your own new lane handoff. C uses `docs/handoffs/dev-b/c-<task>.md` and the exact path delegation below; B records releases of existing shared paths in B's own handoff. Historical handoffs are unchanged.
- A merges contracts before B/C consume generated types. Stage completion means reviewed, green, sequentially merged assigned A/B/C deliverables and A's delivery record. Preserve a working synthetic fallback. A may specify the next stage while the current UI finishes, but feature implementation stays ordered. C10's baseline demo kit can proceed alongside closeout; provider/human blockers do not halt independent local work.
- External calls still require configured server-side credentials and explicit processing consent for the selected destination. This roadmap grants no paid provisioning, public real-data deployment, messages, financial execution or invented approvals. Missing credentials or a human presenter must be recorded as outstanding, not simulated as success; those external dependencies do not block independent local stages.

## Remaining-effort allocation

These 100 relative effort points cover remaining required work, not hours, past contributions or equal numbers of tasks. Re-estimate openly if implementation changes the balance; retain the approximate split and never weaken correctness to hit a percentage.

| Remaining package | A | B | C | C's concrete share |
|---|---:|---:|---:|---|
| Closeout integration and demo preparation | 2 | 2 | 6 | C10 usable presenter kit, fallback runbook and rehearsal record |
| Stage 1: cash-gap explanation | 8 | 5 | 2 | C11 cash-gap demo segment and focused browser regression |
| Stage 2: uncertainty explorer | 3 | 9 | 5 | C12 accessible failure/coverage view, evidence navigation and tests |
| Stage 3: resilient-plan synthesis | 15 | 14 | 3 | C13 fixed-schedule comparison/adoption demo and tests |
| Stage 4: consequences and final presentation | 7 | 5 | 14 | C14 walkthrough implementation (10), C15 integrated demo/fallback/rehearsal (4) |
| **Total / approximate share** | **35** | **35** | **30** | Mostly frontend and demo delivery |

## Developer C: required frontend/demo queue

The previous C1-C9 queue and small prompt/time/file limits are retired by this user instruction. Assign **C10 -> C11 -> C12 -> C13 -> C14 -> C15**, one bounded task at a time. [DEV_C.md](DEV_C.md) records exact paths, prerequisites, acceptance and a copyable C10 prompt. Start C10 once this assignment merges; do not wait for unfinished feature contracts to prepare the merged baseline story. Later feature beats stay proposed until merged.

C remains in the existing dev-b lane (`codex/dev-b/c-<task>`), with its own handoff. New exact paths are delegated by this assignment; existing `verify-plan.tsx`/`page.tsx` wiring requires B's committed release after B's prerequisite work merges. B supplies typed state/callbacks, C owns its views/tests, A owns all financial calculations/contracts and central-doc consolidation. No checker/ownership-policy change or extra dev-c lane is needed. C's required work can gate its stage, but C is never a required independent reviewer. If C is unavailable, A explicitly reassigns the remaining deliverable.

## Stage 0: close the important remaining gaps

Already delivered: A's history and uncertainty validation (PR19/20), B's automated rehearsal/focus/fallback work (PR21), A's release record (PR22), and B's read-only history UI (PR23). Do not reopen these as unfinished implementation.

The initial A/B closeout tasks are merged in PR25/28; C's PR26/27 and the PR30 incomplete-source guard/live failure record are also merged. Do not repeat them. The descriptions below retain acceptance obligations, not new assignments to rebuild delivered work. Native timeout/OCR503 are recorded failures; successful extraction, actual human review and spoken delivery remain outstanding. Independent local stages can continue, and PR29's stage 1 backend contract is already merged.

**A — `live-demo-closeout`:** Verify the merged history checkpoint's CI/review evidence, refresh current shared status, and exercise one complete consented synthetic upload -> worker -> extraction -> human review -> recalculation flow using the selected existing provider. Follow [EXTRACTION_CHECK.md](EXTRACTION_CHECK.md): record native and scanned-document results separately, exact model/destination, field/citation errors, corrections, latency, withheld execution and deletion. Prepare the isolated local setup and fixtures even if live access is unavailable. Reproduce and fix only blockers to this flow in A-owned code, with regressions. Do not broaden into audio, new providers, cloud infrastructure or a general accuracy benchmark.

**B — `live-demo-consent` integration:** Preserve PR28's destination-aware upload/draft consent, separate text/evidence/OCR/storage disclosures, provider-change handling and review/recalculation tests. Preserve the merged behavior and resolve any newly reproduced owned defects. Inspect affected desktop/mobile and keyboard flows. Hand existing presenter cues and known limitations to C through the merged handoff; C owns continued presenter preparation/human rehearsal coordination. No extra external processing or generated-type edits.

**C — C10 `c-demo-kit`:** Build the baseline presenter kit, fallback runbook and rehearsal log in the assigned `frontend/demo/` paths. Keep A's live results separate from synthetic demo evidence, and future controls explicitly proposed. Prepare an actual spoken rehearsal when a presenter is available; never substitute automated timing. A consolidates shared-doc claims.

**Acceptance:** a reproducible report distinguishes local fixture tests, live native extraction, live OCR and human spoken rehearsal. No unavailable test is called passed. A records a usable offline checkpoint and resolves the observed incomplete-source correctness blocker; C records actual or outstanding human rehearsal. Brev consent must merge before a Brev browser live run; existing authorized hosted runs can proceed independently. Record infrastructure/provider access blockers and continue the locally executable queue.

## Stage 1: idea #2 — explain the minimum cash change

**Backend delivery:** PR29 (`b5d9204`) merged the [cash-gap API and generated contracts](handoffs/dev-a/cash-gap-diagnostic.md). Preserve this implementation and its recorded validation; the A description below states its scope, not work to repeat. B's UI and C11's integrated demo remain pending.

**A — `cash-gap-diagnostic`:** Generalize the useful bounded cash diagnostic in `scripts/verify_demo.py` into a private, nonmutating API workflow for the current saved fixed schedule and explicitly declared uncertainty. Scope v1 to additional opening cash; do not search for new permissions, arbitrary clause edits or combinations of repairs. Reuse canonical ledger/evidence/authorization checks. Distinguish a proven minimum for this fixed schedule from an observed lower bound or inconclusive result. Any cash candidate must be checked against the same bounds; missing evidence or unauthorized schedules cannot be repaired with money. Link the limiting date, events and rules. A claim about all possible schedules needs a separate valid certificate and must not be inferred from one failed fixed plan. Merge documented contracts/generated types before B starts consumption.

**B — `cash-gap-diagnostic-ui`:** Show the required hypothetical buffer, limiting date and evidence beside the failed fixed-plan result. Compare the original schedule with the same schedule under the explicit cash assumption, without replacing the active plan or implying money was obtained. Explain authorization/evidence blockers separately and render incomplete checks honestly. Clear stale results on session, revision, plan or assumption changes.

**C — C11 `c-cash-gap-demo`:** After merged A/B implementation, deliver the focused cash-gap presenter segment and real-API browser story, including unchanged saved plan/reload and proof/authorization wording. This takes demo production off B; B retains core UI/state acceptance.

**Acceptance:** independent small-ledger oracle; zero-gap case; original eight-date synthetic example gives a proven 40000-cent fixed-schedule buffer and verifies the same schedule; one cent less fails when minimality is claimed; case/time cutoff does not become an exact minimum; denied/pending authorization and unresolved evidence never become cash-repair success. API privacy/nonmutation/stale-result tests and real-API browser checks cover these labels and evidence links. Keep future obligations visible. Additional-money values are diagnostics, never funding.

## Stage 2: idea #3 — interactive uncertainty explorer

**A — `uncertainty-explorer-contract`:** Preserve [UNCERTAINTY_CONTRACT.md](UNCERTAINTY_CONTRACT.md), validate B's consumption needs and provide any missing backend result data for visualizing evaluated failures. Keep financial calculations on the backend. Document exact versus partial coverage, large-count representation and budget behavior. No silent sampling, endpoint-only approximation, increased limits or unproved shortcut may yield an exhaustive safety claim. An algorithm change requires its own proof rationale and oracle tests before consumption.

**B — `uncertainty-explorer-ui`:** Own add/remove controls for up to eight date/amount/approval dimensions, rationales, duplicate feedback, exact preflight count/budget warnings, multiple incomes and approval targets. Own requests, selection and stale-state invalidation; preserve nominal assumptions, fixed schedule identity and preview nonmutation. Merge supported typed result/evidence callbacks, then release the exact `verify-plan.tsx` wiring section for C12 in B's handoff. Do not also implement C's failure view.

**C — C12 `c-uncertainty-failure-view`:** Implement the bounded accessible counterexample table/details and evidence navigation, with a mobile/list alternative and visibly unknown partial/unchecked coverage. Consume backend results through B's merged interface; wire only the released section and test keyboard/mobile, no-cash authorization failures and stale-result clearing. This view is part of the stage gate.

**Acceptance:** combined date/amount/approval cases match the backend; every inclusive cent counts; a $100-wide inclusive amount range has 10001 values before other dimensions and warns about the 10000-case cap. Verify counts above JavaScript's safe integer range are exact or explicitly qualified, not rounded as exact. Test duplicates, invalid targets, eight-dimension limit, stale responses, Safe/Unsafe/Unknown, authorization failures without cash traces, keyboard/mobile controls and existing history regressions. Do not narrow user bounds to obtain Safe.

## Stage 3: idea #1 — find a resilient plan

**A — `resilient-plan-spec`, then `resilient-plan-engine`:** First commit and review a separate design with B before implementation. Define bounded domains, objective/tie-breaking, candidate-schedule search, shared ledger reuse, result proof/termination states, budgets, API identity/nonmutation, and explicit adoption semantics. Then implement search for **one permitted fixed action/date schedule that survives every declared assignment**. V1 uses existing action types and bounded supported uncertainty; no adaptive policies, correlations or uncertain expenses. Nominal optimization, fixed-plan verification and synthesis remain separate operations. Reoptimizing separately for each outcome is not a resilient schedule. Exhaustion/timeouts without a solution are inconclusive unless impossibility is actually proved.

**B — `resilient-plan-ui`:** Review the design's user-facing claims, then consume merged contracts to compare nominal and resilient candidates with fixed dates, assumptions, evidence, costs/burden and verification. Never silently replace the saved nominal plan. Support the spec's explicit adoption flow and invalidate stale candidates. Clearly distinguish found-and-verified, proved impossible and inconclusive outcomes.

**C — C13 `c-resilient-plan-demo`:** After A/B merge, turn A's new synthetic fixture into the fixed-schedule comparison/adoption presenter segment and browser regression. Show unchanged bounds, independent verification and honest no-solution/cutoff fallback. Preserve the original fixture's separate impossibility result.

**Acceptance:** a new separately labeled synthetic fixture has a nominal schedule that fails and a different fixed schedule that survives; independent brute-force small cases verify search and proof claims. Cover no-solution, cutoff, authorization, essential obligations, debt identity, future obligations and privacy/revision races. Independently verify a returned candidate through the existing fixed-plan checker. Preserve the original demo fixtures and regression values. B's real-API demo shows the actual changed schedule and why it helps, rather than changing the uncertainty bounds.

## Stage 4: idea #4 — cross-document consequence walkthrough

**A — `consequence-walkthrough-contract`:** Reuse existing graph, scenario preview, decision traces and canonical event effects. Supply only missing typed provenance/result data needed to explain a proposed action across documents. Include removed charges, shifted/accelerated debt, fees, dependencies, blockers and beyond-horizon obligations. Blocked transformations have explanations, not fabricated permitted cash projections.

**B — `consequence-integration`:** Own shared graph highlighting, evidence-drawer callbacks, selected plan/verification context and preview/request/stale state. Publish the typed interface and release only `page.tsx` import/mount/callback wiring to C14 after integration hooks merge. Retain shared-primitives/regression ownership; C implements the walkthrough instead of duplicating B work.

**C — C14 `c-consequence-walkthrough`:** Build the action-focused source quote -> reviewed rule -> dependency -> proposed effect -> cash timeline view, using B's hooks and A's backend results. Include cancellation's accelerated device debt and retained obligations, keyboard steps and readable mobile/list presentation. Own its focused real-API tests and presenter segment.

**C — C15 `c-final-demo`:** After stage 4 integration, assemble the complete judge story, integrated browser rehearsal, saved synthetic fallback and recovery instructions. Facilitate actual human spoken rehearsal when available and record it separately from automated timing. A updates central delivery/demo records from C's artifacts; defects go to their assigned owners.

**Acceptance:** the existing cancellation example exposes both the removed service charge and accelerated existing debt, with exact source links and established cash values. No debt is duplicated or hidden beyond the horizon; deferral is labeled timing rather than savings. Existing preview and trace behavior remains intact, blocked actions remain blocked, and UI never calculates new financial consequences. Rehearse the combined story and update the stable fallback after integration.

## Optional queue: only after required stages

**Idea #5 — document-change impact, if time permits.** A first specifies explicit document replacement, reviewed semantic differences, supersession/version rules, affected-action invalidation and privacy/history behavior. B presents old/new clauses and changed plan implications without substituting current evidence into historical results. Acceptance includes conflicting documents, human confirmation of supersession, obsolete plan invalidation and source deletion. Existing `supersedes` support is a foundation, not delivery of this workflow. No automatic legal interpretation or assumption that the last upload wins.

**Idea #6 — review by decision impact, lower priority than #5.** Only consider after #5 is accepted or explicitly skipped for lack of feasibility. A specifies bounded hypothetical comparisons that identify review items or related blocker groups that could affect feasibility; B presents the rationale and conditional consequences within the existing queue. Preserve essential/missing-obligation urgency. Acceptance covers interacting blockers, no false approval, no promised dollar benefit, honest budget limits and current-session/revision isolation. Do not call a hypothetical favorable outcome an expected gain.

A/B/C assess remaining implementation, integration and rehearsal time before activating either optional item; A records the decision in the board. No additional C feature is assigned by this optional menu. Absent a clear margin, stop at the integrated required story.

## Checks and presentation

Use the pinned toolchain, ownership and review/merge protocol in [WORKSTREAMS.md](WORKSTREAMS.md). Runtime stages require independent engine/API or real-API browser regressions plus full CI. A owns schema/type drift/backend/database checks; B and C each run typecheck/lint/build and browser/accessibility checks for their changes, with B responsible for shared integration. C10's prose-only validation checks links/commands/claims/timing, not redundant runtime tests. Record exact commands, commits, failures and limits in each handoff.

The target story is: **source -> review -> nominal plan -> concrete failure -> minimum cash diagnostic -> resilient alternative where one exists -> evidence-linked consequences**. Keep proposed, implemented, fixture-tested and live-verified claims distinct. Human spoken rehearsal and recorded local fallback are required presentation work; optional features never displace them. Bank aggregation, outbound execution, broad benefits discovery, extra providers and infrastructure rewrites remain out of scope.
