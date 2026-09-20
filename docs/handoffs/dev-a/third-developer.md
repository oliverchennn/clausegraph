# Developer A: third-developer coordination docs

## Assignment

Document Developer C's small, optional review/debugging/UI cleanup tasks without implementing any of them. A and B must never depend on C's availability, review or delivery. Preserve their existing work and the financial/privacy invariants.

Branch: `codex/dev-a/third-developer`. Worktree: `.worktrees/dev-a-third-developer`. Starting and required main commit: `bd143a373bf4232d7d9a137fee3c5e9087b1aab2` (PR10). Required contract changes: none.

Allowed files: `AGENTS.md`, `README.md`, `.github/pull_request_template.md`, `docs/WORKSTREAMS.md`, `docs/RESUME.md`, `docs/HACKATHON_MVP.md`, new `docs/DEV_C.md`, and this handoff. Markdown only; no application code, ownership JSON, workflow/checker code, dependencies, generated contracts or other developers' handoffs.

## Synchronization and constraints

Inspected all worktrees and recent PR states; fetched origin with pruning. Clean root main already matched origin/main. Created a fresh task branch/worktree. Existing dirty worktrees, including A's unmerged `brev-json-output` work, remain untouched. PR8 (B review validation), PR9 (NVIDIA/Brev setup) and PR10 (task-start synchronization) are merged; do not present their old blockers as current assignments.

The executable ownership policy/checker recognizes `dev-a` and `dev-b` lanes only. C has no permanent source ownership. Read-only C reports can start immediately. Future explicitly delegated UI fixes use the existing B lane, identify C as the contributor, and require a committed exact-path assignment and B release after the prerequisite work merges. No `dev-c` branch support or guard changes are claimed.

## Acceptance checks

- C has an immediately usable starter prompt, small task queue, explicit start gates, time limits and report format.
- A/B never wait for C; required reviews stay A/B; C yields overlapping work and optional unfinished tasks can be skipped.
- C's future fixes require exact paths, an integrated baseline, owner release, isolated checkout, normal checks and A integration; no shared-doc or contract edits.
- Documentation links, whitespace, conflict markers and changed-path ownership pass against the fetched base policy.
- Record exact results before handoff. No application tests or implementation tasks are required for Markdown-only changes.

## Completion

Added the C starter prompt, six optional tasks (20–45 minutes), immediate read-only assignments and a gated two-file UI cleanup task. Updated contributor rules, work board, README, PR template and scope/checkpoint links. C's reviews are never required, A/B can reclaim work immediately, and C's optional patches do not change source ownership or block delivery. Corrected stale shared-doc references to the merged PR8/PR9/PR10 work without changing historical handoffs.

Checks on the documentation tree:

- `git diff --check`: passed (only existing LF/CRLF normalization notices).
- Python UTF-8/Markdown validation: all 8 changed/new paths are Markdown and A-owned under fetched main's policy; 51 relative links resolve; no BOM, trailing whitespace or conflict markers.
- Base-checker functions accept the documented `codex/dev-b/c-ui-copy` lane and assign its example handoff and UI component to dev-b. No new lane or checker support is implied.
- Starting HEAD matches fetched origin/main `bd143a3`; original worktrees and dirty changes remain preserved.
- Application tests are not rerun: no runtime code, dependencies, configuration, financial logic, CI code or ownership JSON changed. Existing product checks remain attributed to their historical task handoffs.

Limits: the file release is a coordination rule, not an automated reservation. C can start a read-only report now; writing requires these docs merged plus its own committed A assignment/B release. B review remains required for this A documentation PR; no reviewer approval or merge is claimed here. No C assignment was implemented.
