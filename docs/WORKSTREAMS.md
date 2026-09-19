# Two-developer work board

This is the current assignment and ownership record. The original engine/API/frontend lane branches and old handoffs are historical. Start from freshly fetched main; PR4 is merged as 9858956.

## Exclusive lanes

| Developer | Owns | Task handoffs |
|---|---|---|
| A: backend/integration | backend, shared schemas/generated types, dependencies/locks, migrations, fixtures, scripts, CI/deployment, shared docs | One new file per task under handoffs/dev-a/ |
| B: frontend/demo experience | frontend components/state/style/accessibility/browser tests, excluding A's manifests/generated types/.npmrc/Dockerfile | One new file per task under handoffs/dev-b/ |

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

## Active assignments

- A workflow: codex/dev-a/review-workflow, base9858956; owned files from A policy only. Deliver workflow/checks/toolchain and shared roadmap. Handoff: [review-workflow](handoffs/dev-a/review-workflow.md).
- A queue: starts on a fresh codex/dev-a/review-queue branch after workflow integration. Own backend/contracts/tests and shared feature docs; no frontend implementation edits.
- B guidance: codex/dev-b/review-guidance, base9858956. Own frontend excluding shared files, plus `handoffs/dev-b/review-guidance.md`. Audit/refactor may proceed immediately; merge workflow and backend contract commits from main before final API wiring/validation. The handoff link becomes available when B's PR merges.

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
