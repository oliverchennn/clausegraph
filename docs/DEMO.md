# Three-minute demonstration

Use synthetic documents only. Run the API and frontend using README commands, then open the workspace. Do not imply sponsor requests happened when the interface says offline/unavailable.

Frame the demo around one question: **which documented action gets this person through the cash gap, and what could make it fail?** Show novelty through interacting clauses, impact through the change in minimum cash, and technical depth by following evidence into a permitted solver action. These are the product priorities in [HACKATHON_MVP.md](HACKATHON_MVP.md), not claims about an official judging rubric. The sequence below uses the implemented decision trace and side-by-side preview; bounded stress testing remains a stretch feature.

## 0:00–0:35 — establish the problem
Open the labeled synthetic demo. Show $2,000 opening cash, $1,600 rent on day 7, $800 other payments before day 20, and $900 paycheck on day 20. The baseline minimum is −$400, with $500 remaining at the end. Dates use September 1, 2026 as day 0.

## 0:35–1:10 — follow the evidence
Start at **Why this plan?** Show the visible source → clause → action → ledger-effect chain: the same $450 installment moves from September 13 to September 26, minimum cash changes from −$400 to $50, and ending cash stays $500. Open exact evidence from the trace to show quote, source page/version and separate reviewed/approved states. Explain that the payment was moved, not saved. No message or cancellation is sent.

## 1:10–1:45 — expose a bad interaction
On **Cancel phone service**, choose **Compare option alone**. The three-column preview keeps the no-action baseline and recorded plan visible while the candidate applies cancellation and excludes other options. Cancelling removes a $60 payment but accelerates the existing $480 device principal: the candidate falls to −$820 minimum/$80 ending while the recorded plan remains $50/$500. The original device debt is relocated once, never duplicated. Close the preview with **Keep recorded plan**; reload also leaves the recorded plan intact.

## 1:45–2:20 — change an approval
Set the payment-extension scenario control to denied and choose **Preview side by side**. The candidate returns to −$400 while the recorded plan stays $50. Point out the exact changed-assumption label, then keep the recorded plan. If desired, persist a real denial in rule review to demonstrate invalidation: the shortfall diagnostic identifies the first negative date and $400 additional cash required without adding fictitious funding. Hypothetical approval never updates recorded approval.

## 2:20–2:45 — show review and privacy
Open the assistance guide. Eligibility and date are unresolved, so its possible $300 benefit is excluded. Demonstrate an editable fact and explicit condition review. Point out consent before external processing, the private session, and deletion controls. Upload the same synthetic document twice to show per-session deduplication.

## 2:45–3:00 — finish with an executable checklist
Open the draft request and download the evidence summary. Narration uses ElevenLabs only when configured and explicitly requested. Sponsor status shows what is configured/live versus synthetic. The next step is a person confirming the request; the app never submits it.
