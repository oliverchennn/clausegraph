# Three-minute demonstration

Use synthetic documents only. Run the API and frontend using README commands, then open the workspace. Do not imply sponsor requests happened when the interface says offline/unavailable.

Frame the demo around one question: **which documented action gets this person through the cash gap, and what could make it fail?** Show novelty through interacting clauses, impact through the change in minimum cash, and technical depth by following evidence into a permitted solver action. These are the product priorities in [HACKATHON_MVP.md](HACKATHON_MVP.md), not claims about an official judging rubric. The sequence below uses implemented features; the proposed trace/comparison/stress-test additions are not prerequisites.

## 0:00–0:35 — establish the problem
Open the labeled synthetic demo. Show $2,000 opening cash, $1,600 rent on day 7, $800 other payments before day 20, and $900 paycheck on day 20. The baseline minimum is −$400, with $500 remaining at the end. Dates use September 1, 2026 as day 0.

## 0:35–1:10 — follow the evidence
Open the recommended payment-shift action and its evidence drawer. Show the exact quote, source page/version, separate reviewed/approved states, and execution deadline. The $450 installment moves to day 25; minimum cash becomes $50 and ending cash stays $500. Explain that the payment was moved, not saved. No message or cancellation is sent.

## 1:10–1:45 — expose a bad interaction
Inspect the phone cancellation graph and source clause. Cancelling removes a $60 payment but accelerates the existing $480 device principal. Compare that scenario: cash worsens by $420 over this horizon. The original device debt is relocated once, never duplicated. Housing, utilities and food remain protected.

The current comparison forces cancellation but permits other eligible actions, including the installment shift. Show its actual selected actions and computed balances. The README's −$820 minimum is **cancellation alone**, not necessarily this optimized forced-action comparison. Recalculate using recorded assumptions before the next approval-change step.

## 1:45–2:20 — change an approval
Set the installment shift approval to denied in rule review, then recalculate. The minimum returns to −$400. The shortfall diagnostic identifies the first negative date and the $400 additional cash required, without adding fictitious funding. Re-enable approved after the comparison. Pending/denied assumptions belong only in labeled conditional scenarios.

## 2:20–2:45 — show review and privacy
Open the assistance guide. Eligibility and date are unresolved, so its possible $300 benefit is excluded. Demonstrate an editable fact and explicit condition review. Point out consent before external processing, the private session, and deletion controls. Upload the same synthetic document twice to show per-session deduplication.

## 2:45–3:00 — finish with an executable checklist
Open the draft request and download the evidence summary. Narration uses ElevenLabs only when configured and explicitly requested. Sponsor status shows what is configured/live versus synthetic. The next step is a person confirming the request; the app never submits it.
