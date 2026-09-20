# Three-minute ClauseGraph Verify demonstration

Use only the prominently labeled synthetic demo. No model calls or cloud credentials are needed for this flow. Reset a disposable synthetic session before rehearsing.

Current implemented build: `2e76537`; see the [exact CI checkpoint](DELIVERY_CHECKPOINT.md). The timings below are a proposed three-minute script, not a measured human run. C10's [presenter cues](../frontend/demo/presenter-cues.md) and C11's [cash-gap segment](../frontend/demo/cash-gap-demo.md) provide supporting material. The dedicated C12 failure view, resilient search/adoption and consequence walkthrough remain future work; do not present them as controls that already exist.

## 0:00–0:35 — source to nominal plan

Show the $2,000 **Available cash** and six synthetic sources. The unplanned path is the −$400 shown on screen as **Current path**. In **Why this plan?**, follow the source → clause → action → ledger effect chain and open its exact quote, page/version, separate evidence/review/approval states and execution deadline. CP-SAT moves the same $450 installment from September 13 to September 26: **Lowest projected balance** $50, **At the end of your plan** $500. This is timing relief, not savings. The unresolved assistance benefit remains excluded.

## 0:35–1:20 — declare what could change

Open Verify plan. The saved action schedule and dates stay fixed. Use **Payday through Sep 28**, or add an income-date dimension for the projected paycheck with September 21–28 inclusive and a rationale. Confirm eight exact cases, then **Verify fixed plan**. The merged controls support up to eight date/amount/approval dimensions; keep this primary story to one dimension. No probabilities are invented. All eight dates use the same evidence gates and integer-cent financial transitions as the planner.

## 1:20–2:00 — show the exact failure

Show Unsafe, complete coverage, solver status and −$400 worst minimum. The first deterministic counterexample is payday September 27, with the first shortfall on September 26 at −$400. Follow the counterexample chart line and event timeline back to the installment/paycheck source evidence. The nominal plan remains saved unchanged. If approval uncertainty is enabled, denied/pending outcomes fail authorization; no unauthorized cash trace is presented as a permitted plan.

## 2:00–2:40 — state exactly what is proved

Keep September 21–28 unchanged and select **Explain cash gap**. Show the proven $400 fixed-schedule buffer, same schedule, complete eight-case funded check and one-cent minimality witness. Open limiting evidence and point out the retained future device debt. The saved plan and available cash are unchanged: this is a hypothetical diagnostic, not funding or an adopted plan.

For the separate all-schedules claim, use the already-run output of `python scripts/verify_demo.py`: nominal CP-SAT optimization at the allowed September 28 payday proves the best permitted minimum is still −$400. This separate certificate, not the failure of one fixed schedule, establishes that no schedule survives the original eight-date model. General synthesis remains unimplemented. The six-date Safe preset is an optional detour: explicitly say that narrowing bounds does not fix the broader failure.

## 2:40–3:00 — distinguish the semantic model from the proof

Show `python scripts/eval_nemotron.py`: five native-text synthetic gate cases, including deliberately wrong date/amount candidates that are rejected. This is a local reproducibility check, not live Nemotron accuracy. Nemotron's role is prose → typed rule candidates, followed by source/human/approval gates; it never computes the money or verification result. The sponsor truth table labels missing/unverified services honestly. End with source review and a human action checklist; the app executes no payments, cancellations, applications or messages.

## Rehearsal commands and caveats

The integrated side-by-side preview is a useful optional detour: **Compare option alone** on phone cancellation shows baseline, recorded plan and cancellation-only candidate (−$820 minimum/$80 ending). **Keep recorded plan** and reload preserve the saved plan; **Use this preview as plan** explicitly applies it and invalidates any prior Verify result. **Preview side by side** also compares cash/payday/approval controls without changing recorded approvals. Verification always checks the saved plan rather than an unsaved preview.

- `python scripts/verify_demo.py` — complete synthetic verification, no-safe-schedule proof, and hypothetical cash diagnostic.
- `python scripts/eval_nemotron.py` — five offline semantic gate cases, zero external calls.
- `python scripts/eval_nemotron.py --live --consent-external` — only with explicit processing consent and the selected text provider configured; hosted NVIDIA or optional private Brev sends the synthetic corpus and may consume quota/compute. See [setup and consent](NVIDIA_BREV.md). The [historical Brev retest](handoffs/dev-a/brev-live-retest.md) recorded 3/5 then 5/5 exact structured fields from identical code, prompt and validators: unexplained run-to-run variability, not an improvement between runs. Citation validation passed 5/5 and unreviewed execution was withheld 5/5 in both runs, which is the point of the gates. It is separate from this offline demonstration and is not a general accuracy claim.
- `npm --prefix frontend run test:e2e` — real local API browser coverage, including verification and original workflows.

SAFE is bounded to the declared Cartesian product and daily closing balances over the shown horizon. Large ranges/time limits and unresolved evidence produce Unknown unless a concrete failure is found. Future obligations remain represented beyond the horizon; they are not savings. General robust synthesis, intraday settlement, correlations and hidden obligations are outside this implementation.

The current [`2e76537` checkpoint](DELIVERY_CHECKPOINT.md) has green combined CI with 46 browser tests. Earlier `ca7cde5` and `a00af57` checkpoints remain available for their historical stories. B's [task 5 handoff](handoffs/dev-b/demo-rehearsal.md) records a 180.02-second automated operator run with narration holds, local fallback/outage recovery and focused desktop/mobile sign-off on its original build. Human spoken delivery remains unmeasured; perform that rehearsal separately on the chosen presentation build. No global feature freeze is declared.

The [checkpoint procedure](DELIVERY_CHECKPOINT.md#reproduce-and-prepare-the-local-fallback) explains how to preserve an isolated demo and regenerate the saved synthetic reports without an app/API dependency. A reproduced both reports during [stage 0 preparation](handoffs/dev-a/live-demo-closeout.md). Preload them before presenting; if switching to fallback, identify them as previously computed synthetic results. The user's local app was not restarted. B's destination-aware consent UI is merged in PR28; either configured text route still requires explicit consent, including its separate evidence/OCR destination. The synthetic story itself needs no provider calls. The consented native timeout and OCR HTTP 503 are recorded separately in [EXTRACTION_CHECK.md](EXTRACTION_CHECK.md).
