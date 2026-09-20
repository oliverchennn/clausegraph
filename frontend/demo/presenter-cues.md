# Presenter cues — proposed six-beat, 180-second judge story

**Status: proposed script, not measured delivery.** Beat budgets below are a plan. The only measured timing in this repository is B's automated operator run of **180.02 seconds** with deliberate narration holds, recorded in [B's demo handoff](../../docs/handoffs/dev-b/demo-rehearsal.md). No human spoken run has been measured. Record one in [rehearsal-log.md](rehearsal-log.md) before claiming presentation readiness.

Source baseline for every claim here: merged `8fa1279`, whose application state includes the cash-gap diagnostic API (PR29) and the incomplete-source guard (PR30).

## What is runnable today versus proposed

Say "proposed" out loud for any beat marked proposed. Do not show a placeholder and imply it works.

| Beat | Capability | Status at `8fa1279` |
|---|---|---|
| 1–3 | Source review, nominal plan, decision trace, fixed-plan verification, counterexample | **Runnable in the browser** |
| 4 | Cash-gap diagnostic | **API merged, no UI.** `POST /api/cash-gap` returns the result; the presenter surface is B's stage 1 task. Show the saved script output instead |
| 5 | Resilient alternative schedule | **Proposed.** Stage 3 is not implemented; a reviewed design is required first |
| 6 | Consequence walkthrough | **Proposed.** Stage 4 is not implemented. The existing **Compare option alone** preview shows the cancellation numbers today |

Also runnable and available as optional detours outside the three minutes: the review queue, read-only plan/verification history, destination-aware processing consent, and the dependency graph.

## The six beats

Budgets total **180 seconds**: 30 + 30 + 35 + 30 + 30 + 25.

### Beat 1 — 0:00–0:30 — a source becomes a reviewed rule (runnable)

Open the synthetic session. The **Synthetic demo** badge and strip are on screen; say the documents and figures are fictional.

Show **Available cash $2,000** and the six sources. Open one rule's evidence: exact quote, page and version, and the separate evidence, human-review and approval states. Say that these are four different fields and the app never collapses them.

### Beat 2 — 0:30–1:00 — the plan, and why (runnable)

**Lowest projected balance** reads **$50** against a **Current path** of **−$400**; **At the end of your plan** stays **$500**.

Open **Why this plan?** and follow source → clause → action → ledger effect. The same **$450** installment moves from **September 13** to **September 26**. Say the line that matters: *timing relief, not savings* — the money is still owed, the date moved. Deterministic code computes every cent; no model arithmetic.

### Beat 3 — 1:00–1:35 — declare what could change, then break the plan (runnable)

Open **Verify plan**. The saved actions and execution dates stay fixed. Declare the paycheck as arriving any date **September 21–28 inclusive**, with a written rationale. No probabilities are invented; this is a user assumption.

Run it. **Unsafe**, all eight cases checked. The counterexample is payday **September 27**, first shortfall **September 26**, balance **−$400**. Follow the red line and the event timeline back to the installment and paycheck evidence. The saved plan is unchanged.

### Beat 4 — 1:35–2:05 — how much cash would actually close it (API merged; presenter UI proposed)

The bounded diagnostic answers: holding this exact schedule, **$400** of explicitly hypothetical additional opening cash makes all eight cases safe — and **one cent less still fails**, so it is a proven minimum within the declared model.

Say plainly: *this is a diagnostic, not funding.* It is not income, not an approval, and it changes no obligation.

Show the saved `verify_demo.py` output for this beat until B's cash-gap UI merges. State that the number comes from the merged API and the offline script, and that the on-screen presentation is still to come.

### Beat 5 — 2:05–2:35 — a schedule that survives (proposed)

**Say "proposed" first.** The intended step is a search for one permitted fixed schedule that survives every declared assignment, with three honest outcomes: found and independently verified, proved impossible, or inconclusive within budget.

What is proven **today** is the impossibility half: a separate CP-SAT optimization at the allowed September 28 payday shows the best permitted schedule still reaches **−$400**, so no schedule survives the whole eight-date range. Reoptimizing separately per outcome is not a resilient schedule, and this repository does not implement robust synthesis.

### Beat 6 — 2:35–3:00 — consequences, and the limits (walkthrough proposed; numbers runnable)

**Say "proposed" for the walkthrough view.** The numbers are real today via **Compare option alone** on phone cancellation: **−$820** minimum and **$80** ending. Removing the $60 service makes the existing **$480** device debt due immediately — relocated from day 80, not duplicated, and not new money.

Close on the bounds, in one breath: SAFE means every case in the declared range and horizon, nothing wider. A concrete failure gives **Unsafe**, even if coverage is incomplete; otherwise limits or unresolved evidence give **Unknown**, never Safe. Future obligations stay on the books. The app executes no payments, cancellations, applications or messages.

## Judge questions and honest answers

**"Is this SAFE a proof?"** Within the declared Cartesian product and the displayed horizon, yes — it is exhaustive enumeration over that finite model, with the same evidence gates and integer-cent transitions the planner uses. Outside those bounds it claims nothing. A concrete witness proves Unsafe even before enumeration completes; without one, a cutoff or unresolved fact returns Unknown.

**"Did the model compute the money?"** No. Nemotron turns prose into typed rule candidates, which then pass source, human-review and approval gates. Deterministic code computes every cent in integer USD. A model never writes a balance.

**"So the $400 is funding?"** No. It is a bounded diagnostic that says how large the gap is on this exact schedule. No money was obtained, no approval invented, no obligation changed. That distinction is enforced in the contract: the response carries `is_funding: false` and a warning on every result.

**"Why not just move more payments?"** That is the resilient-synthesis question, and it is deliberately not implemented. What is proven is the negative: at the allowed September 28 payday, even the best permitted schedule reaches −$400, so no fixed schedule survives the full range.

**"Is the deferral a saving?"** No. The installment moved from September 13 to September 26; ending cash is unchanged at $500. Acceleration is the mirror image — cancelling the phone pulls the existing $480 device debt earlier. Neither creates or destroys money.

**"How accurate is the extraction?"** Unmeasured, and deliberately so. The historical Brev retest recorded 3/5 then 5/5 exact structured fields from identical code and prompts — run-to-run variability, not improvement. Citation validation held at 5/5 and unreviewed execution was withheld 5/5 in both runs. That variability is exactly why the gates exist.

**"Is any of this real data?"** No. Six synthetic fixtures, labeled in the UI, with no live provider call in this flow.

**"What happens if evidence is missing?"** It stays unresolved and cannot enter a confirmed plan. Adding cash does not repair it either — the diagnostic returns `NOT_REPAIRABLE_WITH_CASH` for authorization or evidence failures rather than a cash amount.

## Do not say

- Any timing claim as if a human had rehearsed it. Automated timing is automated timing.
- "Verified" for anything except a bounded fixed-plan verification result.
- "Saved" or "saving" for a deferral or an acceleration.
- That a proposed beat is implemented, or that a saved report is a live result.
