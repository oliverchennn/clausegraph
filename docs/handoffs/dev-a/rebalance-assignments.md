# Developer A: rebalance A/B/C assignments

## Assignment before editing

The user reports A/B's first tasks and C's previous assignments done, asks for more C work (mostly frontend/demo), and requests an approximate 35% A / 35% B / 30% C split. This is a coordination-document task, not authorization to implement the new features in this session.

Starting commit: `e65464cbe2648a2bd43d42829eda75d321476580` (merged PR24). Branch: `codex/dev-a/rebalance-assignments`; worktree: `.worktrees/dev-a-rebalance-assignments`. Fetched origin with pruning, confirmed clean main already current, and created this fresh isolated branch. Preserved all existing worktrees and unpublished changes, including A's ongoing closeout continuation.

Allowed files: `AGENTS.md`, `docs/HACKATHON_ASSIGNMENTS.md`, `docs/DEV_C.md`, `docs/WORKSTREAMS.md`, `docs/HACKATHON_MVP.md`, `docs/RESUME.md`, and this handoff. Required contract baseline: PR19 history and PR20 uncertainty, already merged; no runtime contracts change. No application, policy/checker, dependency, generated file, fixture or peer handoff edits.

Observed PR state: A's PR25 and B's PR28 are open, with published heads `08f5102` and `428b9f7`; C's PR26/27 are open at `d42f2b9` / `59d5646`. Treat previous work as delivered/pending integration, not absent or merged. A's local closeout handoff additionally reports live provider failures and an incomplete-source correctness blocker under active repair; do not overwrite that continuation or claim live success. The user's report closes the old C queue without inventing unpublished report/check evidence.

Acceptance: allocate relative remaining effort totaling 35/35/30; assign C substantial exact-path frontend/demo deliverables with prerequisites, interfaces and checks; remove obsolete optional-only/prompt limits; preserve two executable lanes, required reviews and all financial/consent invariants; keep feature order and pending PR integration explicit; validate links, ownership, whitespace, effort totals and current wording. Publish for B review and normal CI; stop after this assignment update.

## Results and checks

Rebalanced 100 estimated remaining-effort points to 35/35/30. C10-C15 now cover the presenter kit, cash-gap demo, uncertainty failure view, resilient-plan demo, consequence walkthrough and final rehearsal/fallback. Exact C paths, prerequisites, shared-file releases, checks and a next prompt are recorded. Existing two-lane enforcement and A/B required reviews remain intact; no feature implementation or peer handoff edits.

Initial checks passed: seven A-owned files; 46 relative links/anchors; allocation totals 35/35/30; six C tasks total 30; all 16 exact planned frontend paths match dev-b ownership under the base policy; no conflict markers/trailing whitespace; `git diff --check` passed. No runtime tests rerun for prose. Hook installer ran successfully without a custom-hook conflict.

The pre-publication fetch found PR28/25/26/27 had merged while this edit was underway, advancing main to `f5f93bd`. Preserve this completed draft in a commit, merge current main normally, retain the newly merged closeout evidence and refresh PR status before publication. Final merge/validation results follow.

## Current-main integration and final validation

Preserved the draft as `a37a77d`, then merged `origin/main` at `f5f93bd5085bbbd7cdb3663348a26b620c18631a` without rebase, reset or stash. Resolved only RESUME/WORKSTREAMS documentation conflicts: retained A's exact PR23 CI/review and local preparation evidence, updated the four PRs to their actual merge commits, and retained the new 35/35/30 allocation. The merged preparation's pending-consent wording is explicitly historical relative to A's separately authorized local continuation. No repeated consent request or live-success claim was introduced. All incoming runtime and peer handoff files match fetched main.

Final documentation checks passed: exactly seven A-owned changed paths against current main, 47 relative links/anchors, 35/35/30 totals, six C tasks totaling 30, 16 proposed frontend paths permitted by the base dev-b policy, byte-equivalent financial invariant text, no conflict markers/trailing whitespace and `git diff --check`. The obsolete active-queue/open-PR wording scan returned no matches. No application tests were rerun for this docs-only diff; normal PR CI and independent B review remain required before merge.
