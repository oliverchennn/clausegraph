# Developer A: hackathon assignment refresh

## Assignment

User requested an update to A/B assignments: finish worthwhile remaining work, then deliver curated ideas #2, #3, #1 and #4 in that order; #5 only if time permits and #6 at still lower priority. This task changes coordination documentation only, not feature implementation or peer handoffs.

Starting commit: `ca7cde5` (merged PR23). Branch: `codex/dev-a/hackathon-assignments`. Worktree: `.worktrees/dev-a-hackathon-assignments`. Fetched origin with pruning, confirmed no open PRs, fast-forwarded clean local main, and preserved existing worktrees and services.

Allowed paths: `AGENTS.md`, `docs/WORKSTREAMS.md`, `docs/HACKATHON_MVP.md`, `docs/RESUME.md`, new `docs/HACKATHON_ASSIGNMENTS.md`, and this handoff. Required contracts: merged PR19 history and PR20 uncertainty validation, included in the starting commit. No backend, frontend, generated contracts, dependencies, fixtures, historical handoffs or deployment edits.

Acceptance: reconcile PR19-23 completion; specify remaining live/demo closeout; record #2 -> #3 -> #1 -> #4 with lane ownership, prerequisites, acceptance and stop conditions; explicitly make #5/#6 optional; preserve evidence, consent, privacy and proof invariants; check links, ownership, whitespace and stale current-assignment language.

## Results and checks

Added `docs/HACKATHON_ASSIGNMENTS.md` with lane-specific task names, prerequisites, acceptance cases, proof boundaries and optional-stage activation. Updated the work board, resume, MVP priorities and contributor contract to remove obsolete assignments/freeze language and consistently point to the user-authorized queue. Required order is closeout -> #2 -> #3 -> #1 -> #4; #5 is time-permitting and #6 lower priority. New stages remain explicitly unimplemented. Historical A/B handoffs and application files are unchanged.

- `git diff --check`: passed.
- Python documentation check: all six changed/new paths are A-owned under the base ownership policy; all 36 local Markdown links resolve; no conflict markers.
- Current-assignment search: no obsolete active-history/deferred-required-feature claims remain in the edited current documents. Historical delivery records and contracts retain their original context.
- `python scripts/install_hooks.py`: confirmed the existing shared hook without replacement. `python scripts/check_workflow.py --require-current`: passed lane ownership, task handoff, conflict markers and current-main ancestry.
- No application tests were rerun for documentation-only changes. No live provider calls, service restarts, deployment or feature implementation occurred.

The assignment branch will be committed and published for B review; required PR CI and independent review are not claimed by these local checks. Do not merge without the repository's review/green-check procedure. This task stops after the documentation handoff; A/B implementation proceeds in their own sessions from merged assignments.
