# Contributor C; ownership lane dev-a; A remains owner

**Contributor C patch inside Developer A's lane.** A owns `docs/DEMO.md` and all shared documentation and may reclaim or reimplement this immediately. No ownership is claimed and this is not a `dev-c` lane.

Branch: `codex/dev-a/c-brev-variability`. Worktree: `.worktrees/dev-a-c-brev-variability`.
Starting and required main commit: `e65464cbe2648a2bd43d42829eda75d321476580` (PR24).
Required contract changes: none. Markdown only, one sentence.

## Why a second branch

`.github/ownership.json` maps `docs/*` to **dev-a** and `frontend/*` to **dev-b**, and `scripts/check_workflow.py` derives one lane from the branch name and rejects any path outside it. This documentation fix cannot share a branch with the frontend fix from the same review. Companion branch: `codex/dev-b/c-trace-claims`.

## Authorization status — read before merging

No A assignment or B release authorizes a C write task; `docs/DEV_C.md` at this commit states "No C write release is granted", and DEV_C.md excludes shared docs from C's scope entirely. The repository owner instructed C in session to finish the assigned task and fix the issues it surfaced; the equivalent patch last session merged as PR16. A may prefer to fold this wording into A's own next shared-doc commit and close this branch. Nothing depends on it.

## Finding fixed

**C7 finding 3 — the demo's Brev retest line read as a progression rather than as variability.** `docs/DEMO.md` said the retest "passed 3/5 then 5/5 exact fields". Two problems, both against A's own record in [`brev-live-retest.md`](brev-live-retest.md):

- That handoff states "No code, prompt, expected scores or validators changed between these two runs", and its own PR title is "Record restarted Brev live results and remaining variability". The 3/5 → 5/5 difference is unexplained nondeterminism of the same model on the same input, not an improvement. "3/5 then 5/5" invites a judge to infer that something was fixed between the runs.
- The 3/5 run exited 1. Describing it as having "passed" is inaccurate; the handoff also notes the differing field was not retained and "must not be guessed".

The line now records the variability explicitly, and adds the two results that were stable across both runs — citation validation 5/5 and unreviewed execution withheld 5/5. Those are the load-bearing numbers for the demo's actual argument: the model is gated precisely because its field extraction varies. Presented this way the honesty strengthens the story rather than weakening it.

No number was changed or added beyond what the retest handoff already records. The surrounding consent, provider and "not a general accuracy claim" wording is untouched.

## Checks and results

- `git diff --check`: passed.
- Cross-read every figure against `docs/handoffs/dev-a/brev-live-retest.md`: Standard evaluation 3/5 exact structured fields, 5/5 citation, 5/5 execution withheld, exit 1; Diagnostic repeat 5/5, 5/5, 5/5, exit 0. The new sentence asserts nothing beyond that table and its stated caveat.
- `python scripts/check_workflow.py --require-current`: passed — lane ownership, task handoff, conflict markers, current main.
- No application check rerun: one Markdown sentence, no runtime code, dependency, configuration, financial logic, CI code or ownership policy. Existing product checks remain attributed to their own task handoffs.

## Limits

- Wording only; it changes no claim's underlying evidence and recomputes no money.
- C did not re-run the live Brev evaluation and makes no new provider claim. The retest remains historical, and live operation is still not established by it.
- The companion branch changes `decision-trace.tsx` step labels. `DEMO.md` does not quote those strings, so the two branches do not conflict and can merge in either order.
