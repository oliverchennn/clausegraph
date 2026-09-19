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
| A: this agent | PR5 workflow, [PR6](https://github.com/vzhu08/clausegraph/pull/6) backend and [PR7](https://github.com/vzhu08/clausegraph/pull/7) frontend snapshot are now merged; current task starts at main4e2725a. User separately assigned hosted NVIDIA setup and optional Brev preparation. | Finish only backend/config/setup docs on codex/dev-a/nvidia-brev. No GPU launch/live request. Publish the optional consent contract for B; later review B's reported work. | B frontend source, browser tests or B handoff |
| B: friend's agent | The previous frontend snapshot is on main. Its original handoff records checks/limitations at that historical point; merging alone does not establish those missing checks. | Start a fresh B task from fetched main, finish queue/demo validation and polish. Optional later Brev consent UI consumes A's merged contract; hosted mode works in parallel now. | Schemas, generated types, manifests/locks, CI, shared docs or A handoffs |

**Immediate coordination:** retire both squash-merged feature branches. A and B create separate fresh tasks from fetched main. B can validate/polish the hosted-provider demo while A prepares Brev. Merge A's new optional consent contract before B consumes it. B reviews A's PR; A reviews B's PR; merge sequentially after green checks.

A's current handoff: [nvidia-brev](handoffs/dev-a/nvidia-brev.md). Historical handoffs: [review-queue](handoffs/dev-a/review-queue.md), [review-workflow](handoffs/dev-a/review-workflow.md), and B's docs/handoffs/dev-b/review-guidance.md. Each developer writes a new task handoff; never rewrite the other developer's history. A's optional setup and exact B consent follow-up are in [NVIDIA_BREV.md](NVIDIA_BREV.md).

### Friend's agent startup

Fetch origin, then create codex/dev-b/demo-polish from origin/main in a separate clone/worktree. The old review-guidance branch was squash-merged; do not reuse it. Read AGENTS, this board and the historical B handoff, then create your own demo-polish handoff. Install Node22.23.2/npm10.9.8 and the Python environment; install the local hook in that clone. The review queue contract is already on main. Keep hosted NVIDIA for current UI work; an optional Brev consent task must wait for A's new contract merge. Do not copy generated types or invent a parallel response schema.

B's minimum completion checks: queue navigation and evidence review, failed-save preservation, stale session/revision responses, recorded denied/pending decisions, missing/deleted sources, an empty private session, keyboard access, mobile overflow, and the existing preview/verification flows. Report exact results in B's task handoff and open/update its PR. A reviews and integrates it only after those checks pass.

Confirmed starting-main blocker: [CI run35476332612](https://github.com/vzhu08/clausegraph/actions/runs/35476332612) at4e2725a fails two review-queue browser cases: source/review completion times out at `selectOption`, and loading-failure retry/keyboard coverage cannot find the expected alert. B owns investigating these before further UI features. This failure predates the NVIDIA/Brev branch; no green full verification is claimed.

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
