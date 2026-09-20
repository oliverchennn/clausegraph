# Developer C: small reviews and cleanup

C has less time and a smaller token budget than A/B. Work on **one small task per session**, normally for 20–30 minutes and never more than 45 minutes without a new assignment. Prefer a useful short report over a broad audit. These are task directions, not completed checks or implemented fixes.

## Start here

1. Read [AGENTS](../AGENTS.md), [WORKSTREAMS](WORKSTREAMS.md), [HACKATHON_MVP](HACKATHON_MVP.md), [RESUME](RESUME.md), the relevant completed task handoff and the [verification limits](handoffs/verification.md). Use historical records for context, not current authorization.
2. The agent inspects Git status/worktrees and task/PR state, fetches origin with pruning and preserves all existing work. Use a separate clone or a detached worktree of fetched main for read-only tasks, such as `.worktrees/dev-c-c1` created with `git worktree add --detach .worktrees/dev-c-c1 origin/main`. Record the exact commit reviewed. Do not change another developer's checkout, branch, running services or private session. If freshness cannot be verified, say so.
3. Start **C1**. Afterward pick only one ready item below, or stop. An active assignment or unpublished push does not mean an owner's work is finished; use the named merged commit. If a prerequisite is unfinished, select another ready read-only task. A/B do not wait for C.
4. Return the report in the current task for the developers to share. No repository edits or commits are needed for C1–C4/C6. A consolidates shared docs when useful; B owns UI follow-ups. An optional report does not require a new issue, message to someone else or PR.

C is never a mandatory reviewer. A/B keep their existing required checks and mutual review process, even when C helps. No feature, contract, merge, rehearsal or release may depend on C finishing. A/B own urgent fixes that cannot wait; C's absence is not a blocker.

## Small task menu

| ID / budget | Read or inspect | Deliverable and completion condition |
|---|---|---|
| C1 — 20 min, ready | [DEMO](DEMO.md), README's synthetic story, and wording in `frontend/src/components/overview-metrics.tsx` / `verify-plan.tsx` | At most 3 concrete wording inconsistencies, each with file/line, current text, suggested text and rationale; or no findings in the inspected scope. Check synthetic labeling, deferral versus savings, conditional versus confirmed, and bounded SAFE/UNSAFE/UNKNOWN wording. No financial recalculation or edits. |
| C2 — 30 min, ready after merged PR8 | `frontend/src/components/review-queue.tsx` and existing `frontend/tests/review-queue.spec.ts`; [B's completed handoff](handoffs/dev-b/review-guidance-finish.md) | Inspect empty, failed-load/retry and keyboard navigation states on the recorded merged snapshot. Report one reproducible problem or clearly state which states were checked and which were not. Do not reopen the two historical failures as current without reproducing them. |
| C3 — 30 min, after B finishes the selected surface | Choose **one** of `evidence-drawer.tsx`, `action-card.tsx`, `scenario-comparison.tsx` in `frontend/src/components/` | At 390px and desktop, inspect focus visibility, keyboard reachability, label clarity, clipping and overflow. Give the viewport, steps, expected/actual behavior and a screenshot if available. Wait until B's named change to that surface merges; no styling sweep or shared CSS edits. |
| C4 — 30 min, after owner handoff | One A/B-reported bug and the owner's named merged reproducer commit; read only the relevant source/test | Reproduce once, reduce the steps and identify a likely source location if evidence supports it. Route backend/contracts/financial defects to A, UI/state/test defects to B. If unreproduced or setup exceeds the budget, report attempts and limits; do not guess a root cause or start a fix. |
| C5 — 45 min, **WAIT / unassigned** | One released B-owned UI surface, at most 2 frontend files plus C's own handoff | Correct one typo, accessible label, focus indication or local overflow issue after the write-release procedure below. No feature, state/API refactor, global style pass, dependency change or financial/consent meaning change. Exact checks must pass before merge; otherwise hand back the patch/report. |
| C6 — 20 min, after A/B name the rehearsal commit | [DEMO](DEMO.md) against the local synthetic UI at that commit | Check that the script matches available controls, source-to-action explanation, displayed results and conditional/verification labels. Return at most 3 discrepancies or scoped no-findings. Optional second look only; A/B do their own required rehearsal without waiting. |

For browser work, use only an isolated synthetic local session with provider credentials disabled. Use the pinned toolchain and existing lockfiles. Do not run dev/build/E2E against another developer's `.next`, storage or ports; use distinct `E2E_API_PORT` / `E2E_WEB_PORT` when running existing browser tests. If no isolated environment is ready within the task budget, do a static review and label it **not browser-verified**. Do not spend the session installing new tooling or fixing infrastructure.

No live provider requests, cloud provisioning, private user-data access or real-world payments/cancellations/applications/messages are part of these tasks. Preserve the financial and consent invariants in AGENTS; wording cleanup cannot change what a claim means.

## One small UI fix without new ownership rules

The current [policy](../.github/ownership.json) and [checker](../scripts/check_workflow.py) accept only dev-a/dev-b lanes. There is no dev-c lane or C-owned source directory. The supported route is an **explicit C contribution within B's existing lane**, after this coordination documentation has merged. A/B's core work takes priority throughout.

1. **A assigns; B releases after finishing.** A records a C task ID, contributor C, one issue, exact allowed files (no globs), starting main SHA, required contract/prerequisite merge SHAs, acceptance checks and an expiry date/time or stop condition in an A-owned committed task handoff. B records release of those paths in B's own committed handoff, after the related B feature PR merges. A can link that B record in the assignment. The assignment/release records must be reachable from fetched main before C writes. No reply or an unmerged record is not a release. There is no currently released C5 task.
2. **Check for overlap before editing.** C confirms no open A/B task still changes those files and that the release has not expired. Read-only reviews can proceed on a fixed snapshot during unrelated work. A released file is not a lock on B: B can reclaim it immediately by telling C and recording the change in B's next handoff update. Chat is useful for immediate notice; it does not replace the durable record.
3. **Use an honest lane/task name.** From freshly fetched main, C creates `codex/dev-b/c-<task>` in `.worktrees/dev-c-<task>` and writes `docs/handoffs/dev-b/c-<task>.md`. The handoff and PR explicitly say **Contributor C; ownership lane dev-b; B remains owner** and link the A assignment/B release. Do not use another developer's active branch or handoff. Do not create `codex/dev-c/...`, alter the checker/policy or disable hooks to publish.
4. **Keep the patch disposable.** One issue, at most 2 explicitly released frontend files plus the handoff. A browser regression test counts toward that limit. Files such as `page.tsx`, `globals.css` and shared `ui.tsx` are excluded by default because of overlap risk; prefer a small local component. Schemas/generated types, manifests/locks, fixtures, backend, scripts, CI, shared docs and A/B handoffs are always excluded. Expanded scope becomes a report to the owner, not a larger C task.
5. **Validate and hand back.** Record exact before/after behavior, checks/results and limits in C's handoff. Run `git diff --check`, frontend typecheck/lint, the relevant existing browser test for focus/layout/interaction changes and a focused visual check at desktop/390px. Production build and the normal complete CI/ownership/ancestry checks are still required before merge. Avoid new tests that merely repeat a typo correction. If this exceeds C's budget, preserve the work and mark checks unrun; do not waive checks or delay A/B.
6. **Yield on change.** Before push/review, fetch main and recheck release and touched files. If A/B needs a file, a prerequisite changes, the release expires or a conflict appears, C stops editing, preserves its diff/branch and reports handback. C does not resolve overlaps with active A/B work or ask them to wait. A may close/defer the optional patch, or the owner can implement the needed correction in its own task. If an unrelated main update merges cleanly, C may incorporate it and run affected checks within budget.
7. **A integrates when convenient.** A reviews and merges only an assigned, current, green B-lane PR. C's own review is never a gate. A/B continue other work regardless of whether C's patch is ready. After merge, retire the branch; a new C fix needs a new assignment/release. After feature freeze, only demo-blocking fixes qualify, and the owner takes over if C is unavailable.

This protocol reduces shared-file overlap without pretending that branch checks enforce file reservations. If future independent dev-c ownership is wanted, A must separately change and merge the policy/checker/tests first; it is not needed for the review tasks or the explicit B-lane procedure above.

## Short report format

```text
C task: C1 / C2 / C3 / C4 / C6
Reviewed commit and prerequisite PR:
Scope and time spent:
Finding (at most 3): file:line or screen, steps, expected, actual, evidence
Suggested wording/fix or likely cause (label unconfirmed inference):
Owner: A or B; impact: correctness / demo / polish
Checks performed and result; checks not run / setup limits:
Changed files: none
Next: owner triage or optional exact-path C5 assignment; A/B need not wait
```

Return scoped no-findings if appropriate; do not manufacture improvements to fill a quota. A serious issue can block the affected feature on its merits, but its owner must resolve or reassign it without depending on C.

## Copyable first-session prompt

> You are Developer C on ClauseGraph, a part-time contributor with a small time/token budget. Read AGENTS.md, docs/WORKSTREAMS.md and docs/DEV_C.md plus their required context. Perform the repository's task-start synchronization yourself and preserve all existing work. Start C1 only: spend up to 20 minutes proofreading the documented synthetic demo and its visible financial/verification wording on a recorded merged-main snapshot. Return at most three exact findings using the short report format, or scoped no-findings. Do not edit repository files, implement tasks, run live providers or send messages to others. A/B never wait for your review. Stop after the report; C5 UI fixes need the separate committed A assignment/B path release described in DEV_C.md.
