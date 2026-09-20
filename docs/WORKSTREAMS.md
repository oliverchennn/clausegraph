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

The user approved this expanded queue on 2026-09-20. [HACKATHON_ASSIGNMENTS.md](HACKATHON_ASSIGNMENTS.md) is the detailed assignment scope, including lane tasks, acceptance checks and limits. The order below supersedes the earlier freeze-after-review-guidance roadmap. Feature numbers refer to the curated ideas, not execution order.

| Stage | Developer A | Developer B | Completion gate |
|---|---|---|---|
| 0: closeout | Verify merged history checkpoint; run consented synthetic live extraction/review/recalculation; record native/OCR results separately | Existing Brev destination-aware browser consent; live-flow UI checks; presenter cues and human spoken rehearsal | Working local fallback; actual live/rehearsal results or explicit external blockers, never invented success |
| 1: idea #2 | Fixed-schedule minimum hypothetical cash diagnostic, proof-qualified API and evidence | Cash-gap explanation, unchanged-schedule comparison and blocked/incomplete states | Proven versus observed results distinguished; no cash repair of authorization/evidence failures |
| 2: idea #3 | Validate existing uncertainty contracts; supply missing backend visualization data | Amount/date/approval dimensions, multiple incomes, case-budget preview and failure exploration | Inclusive/exact domains; honest Safe/Unsafe/Unknown and large counts |
| 3: idea #1 | Reviewed robust-synthesis design, then bounded resilient-schedule search | Design review, then nominal/resilient comparison and explicit adoption | One fixed schedule survives all declared assignments; no per-outcome reoptimization presented as robust |
| 4: idea #4 | Missing consequence/provenance contract data using the existing engine | Cross-document consequence walkthrough linked to graph/evidence/cash | Cancellation debt acceleration and retained obligations are visible; integrated rehearsal/fallback |
| Optional: idea #5 | Specify document replacement/diff/impact semantics | Reviewed old/new clauses and affected-plan presentation | Only if time remains after required work and rehearsal |
| Lowest: idea #6 | Specify bounded hypothetical review-impact comparisons | Explain conditional review priority | Only after #5 is accepted or explicitly skipped; never promised benefit or approval |

Each developer takes one bounded task at a time, records exact files and current starting/contract SHAs in its own new handoff, and stops after publishing it. The required queue is user-authorized; start the next fresh task only after its stage/contract gates are met. Do not execute another developer's lane or skip ahead. Optional activation requires an explicit remaining-time assessment recorded by A/B. Missing provider access or a human presenter remains outstanding but does not block independent local stages. A/B never wait on C.

## Confirmed checkpoint and current assignments

Freshly fetched main is `e65464c` (documentation-only PR24); the application checkpoint remains `ca7cde5` (PR23). PR19/20 delivered A's history and bounded uncertainty validation, PR21 delivered B's automated rehearsal/focus/fallback work, PR22 delivered A's readiness record, and PR23 delivered B's read-only history UI. Earlier workflow, review queue, provider support and C corrections remain merged. These tasks are complete, not pending assignments.

The [delivery checkpoint](DELIVERY_CHECKPOINT.md) and existing handoffs retain historical checks at their original commits. B's [history handoff](handoffs/dev-b/history-ui.md) records 19 passing local browser tests; B's [demo handoff](handoffs/dev-b/demo-rehearsal.md) records automated 180.02-second operator timing, not human spoken delivery. A verified exact merged-history CI: 352 backend tests including PostgreSQL, 19 browser tests, frontend/contract/platform checks, and the recorded independent PR23 review. A's [stage 0 handoff](handoffs/dev-a/live-demo-closeout.md) adds 130 fresh focused local passes (eight PostgreSQL skips), both reproduced fallback reports, and prepared native/scanned local consent/deletion checks. Explicit consent for live processing of the two hosted NVIDIA fixtures remains pending; no live or human rehearsal success is claimed.

| Contributor | Next assigned task | Boundaries |
|---|---|---|
| A | Current stage 0 `live-demo-closeout`: local preparation/checkpoint validated; live consent pending | A-owned backend/contracts/shared docs only; preserve baseline and independent local progress if live access is blocked |
| B | Stage 0 `live-demo-consent`, then the ordered B tasks above | B-owned frontend/browser tests only; consume only merged contracts; coordinate actual human rehearsal rather than claiming automation measured it |
| C | C7 judge-story review now; C8 after stages 1/2; optional C9 after stage 4 | Two prompts, third only if available; bounded read-only reports per [DEV_C.md](DEV_C.md). No write assignment or required-review gate |

Hosted native/evidence/OCR and the full live browser workflow remain unverified by the prior five-clause Brev native-text tests (3/5 then 5/5 exact fields). Browser Brev consent remains unfinished until stage 0 is implemented. Human spoken rehearsal remains outstanding. No live accuracy, deployment or new-feature delivery is claimed by this assignment update.

Historical task handoffs are read-only records. The [new assignment document](HACKATHON_ASSIGNMENTS.md) defines future work; each owner creates its own task handoff before implementation. Stage 0 preparation does not start a future-stage feature or send instructions to another session.

## C's optional queue

Current user assignment: **C7 -> C8, with C9 only if a third prompt remains**, as defined in [DEV_C.md](DEV_C.md). C7 is the immediate story/wording pass; C8 waits for merged cash-gap/uncertainty work; C9 is an optional final consequence check. Preserve the prompt budget; do not run the legacy menu below as extra work. Take one task per session; stop at its time limit and return useful partial findings. Details, candidate surfaces, acceptance criteria and a copyable startup prompt are in [DEV_C.md](DEV_C.md).

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
