# Contributor C; ownership lane dev-a; A remains owner

**Contributor C patch inside Developer A's lane.** A remains the owner of `docs/DEMO.md` and of all shared documentation, and may reclaim or reimplement this immediately. This claims no ownership and is not a `dev-c` lane.

Branch: `codex/dev-a/c-demo-wording`. Worktree: `.worktrees/dev-a-c-demo-wording`.
Starting and required main commit: `e3143394ccb9f4daef10a41f0800a01e62a5df8e` (PR13).
Required contract changes: none. Markdown only.

## Why this is a second branch

The finding it fixes is in `docs/DEMO.md`, and `.github/ownership.json` maps `docs/*` to **dev-a** while `frontend/*` maps to **dev-b**. `scripts/check_workflow.py` derives a single lane from the branch name and rejects any changed path outside it, so the frontend corrections and this documentation correction cannot share one branch without failing the lane check. The companion branch is `codex/dev-b/c-ui-findings`.

## Authorization status — read this before merging

No committed A assignment or B release authorizes a C write task; `docs/DEV_C.md` records C5 as **WAIT / unassigned**. The repository owner instructed C directly, in session, to fix every finding from C's C1–C3 report after C explained that the documented procedure blocks it. DEV_C.md also excludes shared docs from C's scope entirely, so this branch is outside it by definition. A may prefer to fold this wording into A's own next shared-doc commit and close this branch; nothing depends on it.

## Finding fixed

**C1 finding 3 — the demo script named numbers by labels that are not on screen.** `docs/DEMO.md` told the presenter to show "the $2,000 opening cash", "the baseline minimum" and then "minimum $50, ending $500". The UI shows those four numbers as **Available cash**, **Current path**, **Lowest projected balance** and **At the end of your plan**; "baseline" and "opening cash" appear nowhere in the interface. A presenter following a three-minute script had to translate mid-demo.

The 0:00–0:35 section now names the on-screen labels:

- "Show the $2,000 **Available cash** … The unplanned path is the −$400 shown on screen as **Current path**."
- "… **Lowest projected balance** $50, **At the end of your plan** $500."

Nothing else changed. No number, no claim, no ordering and no caveat was altered, and "This is timing relief, not savings" is untouched.

`README.md` was deliberately left alone. Its `Minimum cash` / `Ending cash` table headers are column names for a scenario comparison, not a script read while looking at the screen, so they are not the same defect.

## Checks and results

- `git diff --check`: passed.
- Read back the edited section in full; the two replaced sentences are the only changes, and the −$400 is correctly attributed to **Current path** rather than to the planned minimum.
- `python scripts/check_workflow.py`: see PR; lane, handoff and conflict-marker checks.
- No application check was rerun: this changes one Markdown file and no runtime code, dependency, configuration, financial logic, CI code or ownership policy. Existing product checks remain attributed to their own task handoffs.

## Limits

- Wording only. It cannot change what any claim means, and no money was recomputed.
- C did not rehearse the demo against a running UI; the label names were read from `frontend/src/components/overview-metrics.tsx` and `frontend/src/app/page.tsx` at `e314339`. A presenter should confirm them on screen during the real rehearsal, which remains A/B's own task.
- The companion branch changes the badge on that same metric card from "Essentials protected" to "Cash stays nonnegative". That badge is not quoted in `DEMO.md`, so the two branches do not conflict and can merge in either order.
