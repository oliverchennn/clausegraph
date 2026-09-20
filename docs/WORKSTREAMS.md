# Three-developer work board

This is the current assignment and ownership record. **A owns backend/integration, B owns frontend, and C contributes optional small reviews and cleanup.** Each works only its assignment in a separate session/checkout. The roadmap does not authorize any agent to execute all lanes or future tasks. Original lane branches and old handoffs are historical; start from freshly fetched main.

## Ownership and contribution lanes

| Developer | Responsibility | Handoff/output |
|---|---|---|
| A: backend/integration | Backend, shared schemas/generated types, dependencies/locks, migrations, fixtures, scripts, CI/deployment, shared docs, merge coordination | One new file per task under handoffs/dev-a/ |
| B: frontend/demo experience | Frontend components/state/style/accessibility/browser tests, excluding A's manifests/generated types/.npmrc/Dockerfile | One new file per task under handoffs/dev-b/ |
| C: part-time review and small cleanup | Proofread merged work, reproduce one reported bug, inspect one UI surface; optionally fix a small released B-owned surface | Read-only report by default; explicitly delegated patches use `handoffs/dev-b/c-<task>.md` |

The first match in [.github/ownership.json](../.github/ownership.json) controls files. The checker still supports only dev-a/dev-b implementation lanes; these docs add a contributor, not executable dev-c branch support. C has no permanent source ownership. Do not use a codex/dev-c branch, bypass guards or edit shared files as C. C-authored UI patches use explicitly assigned B-lane tasks; [DEV_C.md](DEV_C.md) defines the release and checks.

One implementation agent per developer and one active C assignment. No editing another contributor's handoff. Unassigned paths fail checks until an A-owned policy PR is merged. A/B never depend on C's review, fixes or availability; their required validation and mutual reviews remain their responsibility.

## Ordered delivery for A and B

| Order | Developer A | Developer B | Gate |
|---|---|---|---|
| 1 | Workflow rules, base-policy CI, pre-push hook, pinned toolchain | Read-only demo audit, then install checks | Bootstrap merged and guards validated |
| 2 | Read-only review queue API/shared blocker descriptions/generated contracts | Extract overview/review presentation while preserving behavior | Backend contract PR merged before API consumption |
| 3 | Queue/gate regression tests; prepare synthetic provider checks | Next-review UI, evidence controls, stale-response and browser coverage | Source -> valid review -> updated plan works |
| 4 | Fix observed backend problems and record actual validation | Loading/errors/empty states, keyboard/mobile clarity | Complete synthetic story and failure state work |
| 5 | Full integration checks, sequential green merges, shared delivery record | Three-minute rehearsal and local fallback | Feature freeze; only demo-blocking fixes |
| 6: A merged | Validate existing history/delete contracts | Read-only plan/verification history, revision labels | A's PR19 merged; B UI still requires its own assignment |
| 7: A assigned | Validate existing uncertainty limits | Amount ranges and multiple uncertainty controls | A's separate uncertainty-limits task; B UI still requires its own assignment |
| 8: later | Specify robust synthesis/correlations/expense uncertainty | Participate in UX specification | Separate design before implementation |

C works alongside this sequence only on the optional queue below. No row, contract merge, review or rehearsal requires C to finish. If C finds a correctness defect, the owning developer triages it and can fix it immediately; the defect must not be held for C.

## Confirmed checkpoint and current assignments

Checkpoint: fetched main `7088b81` after the user merged A's [history PR19](https://github.com/oliverchennn/clausegraph/pull/19). The [history-contracts handoff](handoffs/dev-a/history-contracts.md) and PR CI record that delivery's checks; integration PR18 remains historical evidence. The user assigned A the bounded [uncertainty-limits task](handoffs/dev-a/uncertainty-limits.md) and confirmed B is working on task 5's demo. Historical handoffs retain their original results.

- Workflow PR5, review queue [PR6](https://github.com/vzhu08/clausegraph/pull/6) and frontend snapshot [PR7](https://github.com/vzhu08/clausegraph/pull/7) are merged.
- B's [PR8](https://github.com/vzhu08/clausegraph/pull/8) is merged as `147e657`. Its [handoff](handoffs/dev-b/review-guidance-finish.md) records typecheck/lint/build and all 11 browser tests passing on that task. The two earlier queue failures are historical, not an outstanding assignment to C.
- A's [PR9](https://github.com/vzhu08/clausegraph/pull/9) is merged as `af980e1`; [NVIDIA_BREV.md](NVIDIA_BREV.md) describes the optional consent contract. This does not establish live provider accuracy or authorize provisioning.
- Task-start synchronization PR10 and C's operating rules PR12 are merged. Original A task 1 (workflow bootstrap, PR5) is complete; do not restart it as unfinished work.
- Brev output/source fixes PR11/PR13 and [live retest PR15](https://github.com/vzhu08/clausegraph/pull/15) are merged. Repeated five-clause tests scored 3/5 then 5/5 exact fields, with 5/5 valid citations and unreviewed outputs withheld in both. Browser consent remains unimplemented; no general accuracy or OCR claim follows.
- C's [UI PR17](https://github.com/vzhu08/clausegraph/pull/17) (`eb81eab`) and [demo wording PR16](https://github.com/vzhu08/clausegraph/pull/16) (`79dced5`) are merged. Their handoffs record owner-directed exceptions to the normal release procedure; those exceptions do not assign future C work. PR17's application checks passed, while its current-main ancestry gate failed before merge.

| Contributor | Next permitted work | Start condition / exclusions |
|---|---|---|
| A | Current user assignment: validate existing bounded uncertainty limits | `codex/dev-a/uncertainty-limits`, started from `f23133b` and updated to merged `7088b81`; exact paths/checks in its handoff and guidance in [UNCERTAINTY_CONTRACT.md](UNCERTAINTY_CONTRACT.md). No frontend or robust synthesis work |
| B | User-confirmed active task 5: demo polish/rehearsal | Separate B session/task from current main. Keep generated types/manifests with A. History, richer uncertainty controls and optional Brev consent UI require separate assignments |
| C | No active write assignment; optional ready read-only review | PR16/PR17 findings are delivered. Name a merged snapshot for any new review; a future C5 patch needs a new release |

The merged [history contract](HISTORY_CONTRACT.md) and A's uncertainty validation do not complete or replace B's active rehearsal/visual sign-off. History presentation and richer uncertainty controls remain separately assigned B follow-ups. A stops after uncertainty validation rather than proceeding to row 8.

Historical handoffs remain unchanged: A's [review-queue](handoffs/dev-a/review-queue.md), [review-workflow](handoffs/dev-a/review-workflow.md), [nvidia-brev](handoffs/dev-a/nvidia-brev.md), [task-sync](handoffs/dev-a/task-sync.md), and B's [review-guidance](handoffs/dev-b/review-guidance.md) / [review-guidance-finish](handoffs/dev-b/review-guidance-finish.md). New work gets a new handoff. Merged-task checks are historical evidence, not fresh full-stack results for later commits.

## C's optional queue

Take one task per session; stop at its time limit and return useful partial findings. Details, candidate surfaces, acceptance criteria and a copyable startup prompt are in [DEV_C.md](DEV_C.md).

| ID | Small task | Start condition | Limit / output |
|---|---|---|---|
| C1 | Proofread the three-minute demo and visible financial/verification wording | Ready on merged main; read-only | 20 minutes; at most 3 wording findings with exact locations |
| C2 | Inspect review-queue empty/error/retry text and keyboard focus | PR8 already merged; inspect a fixed snapshot, never another developer's running session | 30 minutes; reproducible findings or no findings in checked scope |
| C3 | Inspect one selected drawer/card at 390px and desktop with keyboard | Review the merged version after B finishes changes to that surface; if still active, choose C1/C2 instead | 30 minutes; one surface, screenshots/steps where available |
| C4 | Reproduce one bug reported by A or B; narrow its likely cause | Owner supplies a report and a merged reproducer commit after its task finishes | 30 minutes; expected/actual result and owner routing, no fix |
| C5 | One typo, label, focus or local overflow correction | WAIT: this workflow is merged, A assigns exact paths, B's work is merged and B releases those paths | 45 minutes; at most 2 frontend files plus C's handoff, one issue |
| C6 | Proofread the final demo flow against the displayed result | A/B name a merged rehearsal commit after their demo changes finish | 20 minutes; optional notes, never a release gate |

Dependencies run from completed A/B work to C only. C may be absent, stop early or skip a task without holding a feature, merge or demo. No-response means no C write release, not a reason for A/B to wait. If no task is ready, C reports that and stops; do not expand into history, integrations or verification features.

## Per-task process

1. The agent inspects status/worktrees and task/PR state, preserves existing work, fetches origin with pruning and fast-forwards clean main when possible. Never reuse a squash-merged branch.
2. A/B implementation tasks use fresh lane branches/worktrees. C read-only tasks use a separate clone or detached worktree of fetched main and return reports without commits. For C write tasks, first follow DEV_C.md, then use `codex/dev-b/c-<task>` in `.worktrees/dev-c-<task>`.
3. Record starting commit, allowed paths, required merged contracts and acceptance checks in the implementation handoff. C also records contributor identity, release links and expiry/stop condition. Handoffs/PRs are authoritative; chat supplements them.
4. Stay inside the assignment. Shared contract/dependency changes go through A. C reports expanded or backend/state/financial problems to the owner; it does not take them on. B and C do not append to DEMO, RESUME, HACKATHON_MVP, SPONSORS or this board.
5. Before publishing, update only your handoff and fetch/merge main. The hook checks ancestry, lane ownership, handoff and conflict markers. C stops on overlap or owner reclaim; it does not reserve files against B or repair conflicts with active A/B work.
6. Review and merge sequentially: A integrates B-lane reviewed green PRs (including C's explicit delegations); A's PR gets B review first. C's additional review is optional. If C cannot refresh a patch, leave it unmerged/close it and continue A/B work; owners can implement a needed fix in their own tasks.

## Install and limits

Use Python3.12, Node22.23.2 and npm10.9.8. Run python scripts/install_hooks.py from an activated virtual environment. Existing pre-push hooks are backed up and chained; an existing core.hooksPath causes a non-destructive stop with chaining instructions. Each clone installs independently; linked worktrees share the repository hook. With a custom hook, fetch origin/main then invoke the base branch's scripts/check_workflow.py with --require-current and each actual pushed SHA/branch; do not silently replace existing hooks.

CI runs the trusted base checker/policy. The original bootstrap exception is historical, not available to C. A branch-name/path policy guards against accidental conflicts, not author identity or concurrent edits within one lane; C's exact-path release and handback are required in addition to checks. GitHub required-check enforcement is unavailable for this private repository's current plan. A must follow the green-check/review rule; do not change visibility or billing. These procedures reduce overlap; they do not promise that Git or semantic conflicts are impossible.
