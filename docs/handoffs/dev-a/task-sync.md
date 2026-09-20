# Developer A: automatic task-start synchronization

Task: record the user's standing instruction that the agent handles Git synchronization before every new repository task, rather than asking the user to run update commands. GPU/account guidance is requested in chat only; no deployment or application implementation belongs to this task.

Branch: codex/dev-a/task-sync. Starting/required main commit: af980e12b1120d960ecfe6e89d03d6bdb33e4c4a. Allowed files: AGENTS.md and this handoff. No interface/dependency change; no B-owned files.

Checks before implementation: root main was clean; fetched origin with pruning, fast-forward synchronization reported already up to date, and a fresh task worktree/branch was created from origin/main. Existing branches/worktrees and ignored environment files preserved.

Acceptance: contributor contract explicitly assigns automatic fetch/state inspection/current-main synchronization to the agent; prohibits discarding local changes, reusing squash-merged branches or treating an unmerged peer branch as merged. Documentation diff and base ownership checks will be recorded before handoff. No runtime tests needed for this documentation-only change.

Completed: added the standing task-start synchronization instruction to AGENTS.md, including handling dirty/divergent work safely and reporting failed fetches honestly. git diff --check passed; both allowed paths passed ownership validation against origin/main's policy; current-main ancestry passed. No application tests rerun because no runtime code, configuration or dependency changed. Publish for review; no merge or GPU provisioning performed.
