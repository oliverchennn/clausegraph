# Two-developer work board

This is the current assignment and ownership record. **A is your agent (this task); B is your friend's agent in a separate session/clone.** Each works only its assignment. The roadmap is a work split, not an instruction for A to execute both lanes or all future tasks. The original engine/API/frontend lane branches and old handoffs are historical. Start from freshly fetched main; PR4 is merged as 9858956.

## Exclusive lanes

| Developer | Owns | Task handoffs |
|---|---|---|
| A: your agent — backend/integration | backend, shared schemas/generated types, dependencies/locks, migrations, fixtures, scripts, CI/deployment, shared docs | One new file per task under handoffs/dev-a/ |
| B: your friend's agent — frontend/demo experience | frontend components/state/style/accessibility/browser tests, excluding A's manifests/generated types/.npmrc/Dockerfile | One new file per task under handoffs/dev-b/ |

The first match in [.github/ownership.json](../.github/ownership.json) controls files. One implementation agent per developer. No editing another developer's task handoff. Unassigned paths fail checks until an A-owned policy PR is merged.

## Ordered delivery

| Order | Developer A | Developer B | Gate |
|---|---|---|---|
| 1 | Workflow rules, base-policy CI, pre-push hook, pinned toolchain | Read-only demo audit, then install checks | Bootstrap merged and guards validated |
| 2 | Read-only review queue API/shared blocker descriptions/generated contracts | Extract overview/review presentation while preserving behavior | Backend contract PR merged before API consumption |
| 3 | Queue/gate regression tests; prepare synthetic provider checks | Next-review UI, evidence controls, stale-response and browser coverage | Source -> valid review -> updated plan works |
| 4 | Fix observed backend problems and record actual validation | Loading/errors/empty states, keyboard/mobile clarity | Complete synthetic story and failure state work |
| 5 | Full integration checks, sequential green merges, shared delivery record | Three-minute rehearsal and local fallback | Feature freeze; only demo-blocking fixes |
| 6: later | Validate existing history/delete contracts | Read-only plan/verification history, revision labels | Separate future task |
| 7: later | Validate existing uncertainty limits | Amount ranges and multiple uncertainty controls | Separate future task |
| 8: later | Specify robust synthesis/correlations/expense uncertainty | Participate in UX specification | Separate design before implementation |

## Current handoff and next independent work

| Owner | Current state | Next task | Do not edit |
|---|---|---|---|
| A: this agent | Workflow PR5 merged on main3799876. Completed the current backend/contracts/tests in [PR6](https://github.com/vzhu08/clausegraph/pull/6), code commit1adf5fb on codex/dev-a/review-queue; stopping after publication. PR remains unmerged for review. | Review B's eventual PR and fix specifically reported backend problems. Provider checks need credentials/consent; no next feature starts automatically. | B frontend source, browser tests or B handoff |
| B: friend's agent | [Draft PR7](https://github.com/vzhu08/clausegraph/pull/7), commit0838e4b on codex/dev-b/review-guidance, contains the frontend work already started before the user clarified the split. It is a handoff, not a finished feature. | Take over the draft, review/refine queue UX, integrate the merged A contract, run types/lint/build and all browser tests, and finish keyboard/mobile/demo polish. | Schemas, generated types, manifests/locks, CI, shared docs or A handoffs |

**Immediate coordination:** the friend reviews PR6; after review and green checks, A/user merges it. B then merges updated main into its existing draft branch and completes PR7. Do not merge PR7 while its contract dependency or UI validation remains incomplete. Only workflow PR5 is merged so far.

A's current handoff: [review-queue](handoffs/dev-a/review-queue.md). Workflow history: [review-workflow](handoffs/dev-a/review-workflow.md). B's own handoff is docs/handoffs/dev-b/review-guidance.md on its draft branch; it lists exact changed files,5 earlier passing regression tests and the new queue tests that have NOT run. B is responsible for confirming every draft behavior; nothing in that branch is claimed delivered.

### Friend's agent startup

Fetch origin, then check out the existing remote codex/dev-b/review-guidance task branch in a separate clone/worktree. This continues the same task; do not create a competing frontend implementation from scratch. Read AGENTS, this board and the B task handoff. Install Node22.23.2/npm10.9.8 and the Python environment; install the local hook in that clone. Confirm the A review-queue PR is merged, then merge freshly fetched origin/main into the B branch before final contract consumption and validation. Do not copy generated types or invent a parallel response schema.

B's minimum completion checks: queue navigation and evidence review, failed-save preservation, stale session/revision responses, recorded denied/pending decisions, missing/deleted sources, an empty private session, keyboard access, mobile overflow, and the existing preview/verification flows. Report exact results in B's task handoff and open/update its PR. A reviews and integrates it only after those checks pass.

A's next session reads its current handoff and reviews B's reported changes; it does not resume the whole roadmap. Shared contracts stay with A, UI behavior with B. A updates shared delivery docs only after B's feature is actually integrated.

## Per-task process

1. Commit or preserve existing work. Fetch origin and create a new task worktree/branch from origin/main; never reuse a squash-merged branch.
2. Record starting commit, allowed paths, required contract commit and acceptance checks in your new handoff. Use PR links and handoffs across separate developer sessions.
3. Stay inside your lane. Shared contract/dependency changes go through A first; use separate PRs rather than a mixed-lane commit.
4. Update only your task handoff with exact checks and limits. A consolidates shared docs; B does not append to DEMO, RESUME, HACKATHON_MVP, SPONSORS or this board.
5. Before publishing, fetch/merge main. The pre-push hook checks ancestry, lane ownership, handoff and conflict markers. Publish with git push -u origin HEAD.
6. Review and merge sequentially: A integrates B's reviewed green PR; A's PR gets B review first. After squash merge, retire the branch and create the next one from updated main.

## Install and limits

Use Python3.12, Node22.23.2 and npm10.9.8. Run python scripts/install_hooks.py from an activated virtual environment after bootstrap. Existing pre-push hooks are backed up and chained; an existing core.hooksPath causes a non-destructive stop with chaining instructions. Each clone installs independently; linked worktrees share the repository hook. With a custom hook, fetch origin/main then invoke the base branch's scripts/check_workflow.py with --require-current and each actual pushed SHA/branch; do not silently replace existing hooks.

CI runs the trusted base checker/policy. During the first bootstrap only, the candidate checker is reviewed and tested because no base policy exists. A branch-name/path policy is an accidental-conflict guard, not proof of author identity. GitHub required-check enforcement is unavailable for this private repository's current plan. A must follow the agreed green-check/review rule; do not change visibility or billing.
