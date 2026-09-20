# Three-developer work board

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

Started at `e65464c`; refreshed main is `f5f93bd` after PR28/25/26/27 merged during this edit. The user reports A/B's first tasks and all previous C work done. These are completed merged deliveries:

| PR | Contributor / merge commit | Delivered scope and limits |
|---|---|---|
| [25](https://github.com/oliverchennn/clausegraph/pull/25) | A closeout / `c64b108` | Local/checkpoint preparation. A's separate local continuation records native timeout/OCR503 and an incomplete-source plan-confirmation blocker under repair; require its fix/checks for closeout. |
| [28](https://github.com/oliverchennn/clausegraph/pull/28) | B consent / `22f6a2c` | Destination-aware consent and browser coverage. Human spoken rehearsal remains unmeasured. |
| [26](https://github.com/oliverchennn/clausegraph/pull/26) | C trace claims / `1edf405` | Decision-trace wording correction and C's handoff. |
| [27](https://github.com/oliverchennn/clausegraph/pull/27) | C Brev wording / `f5f93bd` | Historical-variability wording and C's handoff. |

Do not restart these tasks. This branch incorporates their merged work and reconciles shared-doc overlap while preserving closeout evidence and the new allocation. A continues normal green/reviewed sequential integration for future PRs. Historical handoffs remain unchanged. C1-C9 are closed/superseded per the user; no missing C reports or checks are invented.

The [delivery checkpoint](DELIVERY_CHECKPOINT.md) retains A's verification of exact PR23 CI: 352 backend tests including PostgreSQL, 19 browser tests, frontend/contract/platform checks and independent review. The merged [closeout handoff](handoffs/dev-a/live-demo-closeout.md) adds 130 focused local passes/eight PostgreSQL skips, reproduced fallback reports and native/scanned consent/deletion checks. Its pending-consent statement predates A's authorized local live continuation; failed attempts are not a success claim. The [B demo handoff](handoffs/dev-b/demo-rehearsal.md) records 180.02-second automated operator timing, not human delivery. A owns current live/correctness evidence; C owns presenter preparation. External blockers stay explicit while independent local work proceeds.

## Ordered required work

| Stage | A | B | C | Completion gate |
|---|---|---|---|---|
| 0: closeout | Finish observed blocker and live/fallback record | Preserve merged consent; handle newly reproduced shared UI defects | C10 demo kit after assignment merge, using current main | Working fallback; truthful live/human status; no false confirmed plan from missing extraction |
| 1: cash-gap #2 | `cash-gap-diagnostic` | `cash-gap-diagnostic-ui` state/explanation | C11 cash-gap demo/test after A/B merge | Proven versus observed/incomplete; cash cannot repair authorization; unchanged saved plan |
| 2: uncertainty #3 | `uncertainty-explorer-contract` | `uncertainty-explorer-ui` controls/count/request/selection/stale state | C12 failure view and released wiring/tests | Exact inclusive domains/counts; accessible failures; honest Safe/Unsafe/Unknown |
| 3: resilient #1 | Reviewed `resilient-plan-spec`, then `resilient-plan-engine` | Design review, comparison and explicit adoption | C13 resilient-plan demo/test | One fixed permitted schedule survives unchanged bounds; independent verification; honest cutoff |
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
