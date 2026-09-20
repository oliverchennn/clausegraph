# Three-developer work board

**Solo completion override, 2026-09-20:** the user confirms other developers are inactive and reassigns all remaining reviews, fixes and required deliveries to this agent. Follow the current override in [AGENTS](../AGENTS.md): use the existing ownership lanes, finish required stages sequentially, record same-agent orchestrator reviews honestly and merge green PRs without waiting for B/C. The allocation below records the earlier division of work, not current staffing. C12 and the later frontend/demo tasks are reassigned, not waived.

The user rebalanced remaining required work on 2026-09-20 to approximately **A 35% / B 35% / C 30%**. A owns backend/integration; B leads frontend state/shared integration; C delivers assigned frontend views and demo materials. The old optional-only C queue is retired. Each developer uses its own session/checkout and one bounded task at a time.

## Ownership and contribution lanes

| Developer | Responsibility | Handoff/output |
|---|---|---|
| A / 35% | Financial logic, backend/API, schemas/generated types, dependencies/locks, fixtures/scripts, CI/deployment, central docs, merges | `docs/handoffs/dev-a/<task>.md` |
| B / 35% | Request/state/forms, nominal/resilient comparison/adoption, shared graph/evidence/shell integration, browser regressions | `docs/handoffs/dev-b/<task>.md` |
| C / 30% | Demo kit/rehearsals, uncertainty failure view, consequence walkthrough, focused real-API demo tests | `frontend/demo/` and `docs/handoffs/dev-b/c-<task>.md` |

The first match in [.github/ownership.json](../.github/ownership.json) remains authoritative. Only dev-a/dev-b executable lanes exist. C contributes in B's lane using `codex/dev-b/c-<task>`. [DEV_C](DEV_C.md) delegates exact new frontend/demo paths and requires B's release for existing shared files. No blanket frontend permission, A-owned edits or guard bypass. B/C do not edit central docs or peer handoffs.

Percentages estimate remaining effort, not task counts or past work. The [100-point allocation](HACKATHON_ASSIGNMENTS.md#remaining-effort-allocation) totals 35/35/30. C's assigned deliverables are required; optional C review is not a merge gate. A/B retain mutual reviews and each contributor validates their changes. A records any needed reassignment rather than silently dropping work.

## Confirmed checkpoint and in-flight work

Freshly synchronized main is `2e7653718ff7fac27158789deff965775da408a1` (PR35). Stage 1 is delivered; stage 2's A contract and B controls are delivered, while C12's failure view remains absent. These are completed merged deliveries:

| PR | Contributor / merge commit | Delivered scope and limits |
|---|---|---|
| [25](https://github.com/oliverchennn/clausegraph/pull/25) | A closeout / `c64b108` | Local/checkpoint preparation; the later live failure record and correctness fix are delivered in PR30. |
| [28](https://github.com/oliverchennn/clausegraph/pull/28) | B consent / `22f6a2c` | Destination-aware consent and browser coverage. Human spoken rehearsal remains unmeasured. |
| [26](https://github.com/oliverchennn/clausegraph/pull/26) | C trace claims / `1edf405` | Decision-trace wording correction and C's handoff. |
| [27](https://github.com/oliverchennn/clausegraph/pull/27) | C Brev wording / `f5f93bd` | Historical-variability wording and C's handoff. |
| [29](https://github.com/oliverchennn/clausegraph/pull/29) | A-lane cash-gap contract / `b5d9204` | Private nonmutating API/generated types and backend tests; carried out by C under a separate explicit A-lane assignment, not standing C ownership. UI/demo subsequently merged below. |
| [30](https://github.com/oliverchennn/clausegraph/pull/30) | A incomplete-source guard / `5e79c1d` | Plans stay unresolved during incomplete processing; verification rejects with HTTP 409. Authorized native timeout/OCR503 recorded without claiming successful live extraction. |
| [32](https://github.com/oliverchennn/clausegraph/pull/32) | A cash-gap guards / `1a24143` | Cash diagnostics also reject incomplete processing and discard results when the session, input revision or active plan changes during computation. |
| [33](https://github.com/oliverchennn/clausegraph/pull/33) | A explorer contract / `dd77765` | Existing API consumption, exact counts and proof-qualified witness/worst-case semantics. |
| [34](https://github.com/oliverchennn/clausegraph/pull/34) | B cash-gap UI / `c00d395` | Nonmutating hypothetical cash comparison, evidence/blockers and stale-state handling. |
| [37](https://github.com/oliverchennn/clausegraph/pull/37) | C10 presenter kit / `c82319c` | Baseline presenter cues, fallback runbook and honest outstanding human rehearsal. |
| [36](https://github.com/oliverchennn/clausegraph/pull/36) | C11 cash-gap demo / `8f6c627` | Presenter segment and real-API regression, including retry coverage retained from duplicate PR38. |
| [35](https://github.com/oliverchennn/clausegraph/pull/35) | B uncertainty controls / `2e76537` | Eight dimensions, exact large counts, validation/stale state and typed C12 seam. The seam is empty; it is not the C12 view. |

Do not restart these tasks. PR31 reconciles their delivery records with the new allocation. A continues normal green/reviewed sequential integration for future PRs. Historical handoffs remain unchanged. C1-C9 are closed/superseded per the user; no missing C reports or checks are invented.

The stale-PR audit merged only useful changes and closed [PR38](https://github.com/oliverchennn/clausegraph/pull/38) as a duplicate of PR34 after retaining its retry regression in PR36. Historical branches/worktrees and original handoffs were preserved. A's integration records for [C10](handoffs/dev-b/c-demo-kit-integration.md), [C11](handoffs/dev-b/c-cash-gap-demo-integration.md) and [uncertainty controls](handoffs/dev-b/uncertainty-explorer-ui-integration.md) identify exact reviewed heads and conflict resolutions.

A's current [resilient-plan-spec](handoffs/dev-a/resilient-plan-spec.md) task proposes the [separate synthesis design](RESILIENT_PLAN_SPEC.md) and consolidates these delivery records. B design review and merge are pending. The request to finish all A tasks authorizes continued eligible A work; it does not mark C12 complete or waive design review. After this design, two named A implementation/contract tasks remain: `resilient-plan-engine` after stage 2 acceptance and reviewed design, then `consequence-walkthrough-contract` in stage 4. Optional #5/#6 remain unactivated.

The [delivery checkpoint](DELIVERY_CHECKPOINT.md) now records exact merged-main CI for `2e76537`: 390 backend tests including PostgreSQL and 46 real-API browser tests, plus frontend/generated-contract/platform checks. Historical checkpoints retain their original counts. Authorized native timeout (120.250 seconds) and OCR HTTP 503 (0.250 seconds) remain failures, recorded in the [PR30 handoff](handoffs/dev-a/incomplete-source-guard.md); successful live inference remains outstanding. The [B demo handoff](handoffs/dev-b/demo-rehearsal.md) records historical 180.02-second automated operator timing, not human delivery or timing of this larger build. C10 preserves the outstanding spoken rehearsal. A owns live/correctness evidence; C owns presenter preparation.

## Ordered required work

| Stage | A | B | C | Completion gate |
|---|---|---|---|---|
| 0: closeout | Guard fix/live failure record merged in PR30; retain fallback and live limits | Consent merged | C10 kit merged in PR37; human rehearsal outstanding | Local closeout delivered; successful live/human flow remains explicitly outstanding |
| 1: cash-gap #2 | PR29 contract and PR32 guards merged | UI merged in PR34 | C11 demo/tests merged in PR36 | Delivered, including truthful cash/authorization labels and saved-plan nonmutation |
| 2: uncertainty #3 | Contract merged in PR33 | Controls and C12 interface/release merged in PR35 | C12 failure view/wiring/tests still required | Controls accepted; stage awaits C12's accessible bounded failure view |
| 3: resilient #1 | Design proposed for B review; engine waits for reviewed design and stage 2 | Design review, then comparison/adoption | C13 follows A/B merge | One fixed permitted schedule survives unchanged bounds; independent verification; honest cutoff |
| 4: consequences #4 | `consequence-walkthrough-contract` | `consequence-integration` graph/evidence callbacks and shell release | C14 walkthrough, then C15 final demo | Removed charge/accelerated debt/future obligations visible; integrated fallback/rehearsal |

Detailed acceptance/effort is in [HACKATHON_ASSIGNMENTS](HACKATHON_ASSIGNMENTS.md); C's exact files, prerequisites and prompt are in [DEV_C](DEV_C.md). The queue authorizes the next fresh task only after prerequisites, not skipping stages or taking another lane. C10 runs alongside closeout; subsequent C tasks follow named merges. Missing human/provider availability remains outstanding without blocking independent local implementation.

Optional #5 document impact and lower-priority #6 review impact retain their order. A/B/C record remaining implementation/integration/rehearsal capacity before activation; C has no optional feature assignment now. Optional work never displaces the required story.

## Per-task process

1. Inspect status/worktrees and task/PR state; fetch/prune and fast-forward clean main where possible. Preserve dirty/divergent work, never silently reset/clean/stash, and never reuse squash-merged task branches.
2. Use a fresh lane branch/worktree. C uses `codex/dev-b/c-<task>` in `.worktrees/dev-c-<task>`. Record identity, starting SHA, exact paths, prerequisite merge SHAs, interfaces/releases and checks in your own handoff before implementation.
3. Merge A contracts before B/C consume generated types. New C paths are delegated by this merged assignment; existing shared paths need B's committed release. B first publishes supported data/callbacks; C then implements/wires its view after release. Never import missing/unmerged components.
4. Stay within scope. A handles shared contracts/docs, B shared state/primitives, C assigned feature/demo surfaces. Use separate local storage/ports and preserve the user's app.
5. Update only your handoff before publishing; fetch/merge main and rerun affected checks. C overlap/reclaim triggers preserved handback/reassignment, not overwrite or dropped required work. Stop after each handoff/PR.
6. A reviews/integrates current green B-lane PRs including C's; A's PRs need B review. Optional C review does not substitute. Full CI/ownership/ancestry checks remain required; local application checks scale to changes.

## Install and enforcement limits

Use Python3.12, Node22.23.2/npm10.9.8 and locked installs. Run `python scripts/install_hooks.py` in the activated environment; preserve/chain custom hooks. Linked worktrees share hooks. Use distinct E2E_API_PORT/E2E_WEB_PORT and worktree-local `.next`/storage.

CI uses the trusted base checker/policy; the bootstrap exception is historical. Checks do not enforce identity or same-lane reservations; committed assignments/releases remain necessary. The private GitHub plan cannot enforce required checks: follow review/green-check rules without changing billing/visibility. No live call, deployment or implementation is performed by this refresh.
