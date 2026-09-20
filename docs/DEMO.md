# Three-minute ClauseGraph Verify demonstration

Use only the prominently labeled synthetic demo. No model calls or cloud credentials are needed for this flow. Reset a disposable synthetic session before rehearsing.

## 0:00–0:35 — source to nominal plan

Show the $2,000 **Available cash** and six synthetic sources. The unplanned path is the −$400 shown on screen as **Current path**. In **Why this plan?**, follow the source → clause → action → ledger effect chain and open its exact quote, page/version, separate evidence/review/approval states and execution deadline. CP-SAT moves the same $450 installment from September 13 to September 26: **Lowest projected balance** $50, **At the end of your plan** $500. This is timing relief, not savings. The unresolved assistance benefit remains excluded.

## 0:35–1:20 — declare what could change

Open Verify plan. The saved action schedule and dates stay fixed. Select the projected paycheck and explicitly declare September 21–28 inclusive as a user assumption, with a rationale. No probabilities are invented. Run verification. Explain that all eight dates are checked through the same evidence gates and integer-cent financial transitions used by the planner.

## 1:20–2:00 — show the exact failure

Show Unsafe, complete coverage, solver status and −$400 worst minimum. The first deterministic counterexample is payday September 27, with the first shortfall on September 26 at −$400. Follow the counterexample chart line and event timeline back to the installment/paycheck source evidence. The nominal plan remains saved unchanged. If approval uncertainty is enabled, denied/pending outcomes fail authorization; no unauthorized cash trace is presented as a permitted plan.

## 2:00–2:40 — state exactly what is proved

Use the September 21–26 preset and run again: Verified Safe for all six dates, within the displayed horizon and assumptions only. Say explicitly that narrowing the model does not fix the broader eight-date failure.

For the broader model, show the already-run output of `python scripts/verify_demo.py`: a separate CP-SAT optimization at the allowed September 28 payday proves the best permitted schedule still reaches −$400. Thus no schedule can be safe for every date in the eight-case model. The script verifies the same fixed schedule for all eight cases after adding $400 of hypothetical opening cash, establishing a tight bounded cash diagnostic. It does not create funding, submit an action, or claim general robust synthesis.

## 2:40–3:00 — distinguish the semantic model from the proof

Show `python scripts/eval_nemotron.py`: five native-text synthetic gate cases, including deliberately wrong date/amount candidates that are rejected. This is a local reproducibility check, not live Nemotron accuracy. Nemotron's role is prose → typed rule candidates, followed by source/human/approval gates; it never computes the money or verification result. The sponsor truth table labels missing/unverified services honestly. End with source review and a human action checklist; the app executes no payments, cancellations, applications or messages.

## Rehearsal commands and caveats

The integrated side-by-side preview is a useful optional detour: **Compare option alone** on phone cancellation shows baseline, recorded plan and cancellation-only candidate (−$820 minimum/$80 ending). **Keep recorded plan** and reload preserve the saved plan; **Use this preview as plan** explicitly applies it and invalidates any prior Verify result. **Preview side by side** also compares cash/payday/approval controls without changing recorded approvals. Verification always checks the saved plan rather than an unsaved preview.

- `python scripts/verify_demo.py` — complete synthetic verification, no-safe-schedule proof, and hypothetical cash diagnostic.
- `python scripts/eval_nemotron.py` — five offline semantic gate cases, zero external calls.
- `python scripts/eval_nemotron.py --live --consent-external` — only with explicit processing consent and the selected text provider configured; hosted NVIDIA or optional private Brev sends the synthetic corpus and may consume quota/compute. See [setup and consent](NVIDIA_BREV.md). The [historical Brev retest](handoffs/dev-a/brev-live-retest.md) recorded 3/5 then 5/5 exact structured fields from identical code, prompt and validators: unexplained run-to-run variability, not an improvement between runs. Citation validation passed 5/5 and unreviewed execution was withheld 5/5 in both runs, which is the point of the gates. It is separate from this offline demonstration and is not a general accuracy claim.
- `npm --prefix frontend run test:e2e` — real local API browser coverage, including verification and original workflows.

SAFE is bounded to the declared Cartesian product and daily closing balances over the shown horizon. Large ranges/time limits and unresolved evidence produce Unknown unless a concrete failure is found. Future obligations remain represented beyond the horizon; they are not savings. General robust synthesis, intraday settlement, correlations and hidden obligations are outside this implementation.

Delivery checkpoints: [`ca7cde5`](DELIVERY_CHECKPOINT.md) includes the merged history UI and green combined CI with 19 browser tests; the earlier `a00af57` checkpoint remains available for the original story. B's [task 5 handoff](handoffs/dev-b/demo-rehearsal.md) records a 180.02-second automated operator run with narration holds, local fallback/outage recovery and focused desktop/mobile sign-off on its original build. Human spoken delivery remains unmeasured; perform that rehearsal separately on the chosen presentation build. No global feature freeze is declared.

The [checkpoint procedure](DELIVERY_CHECKPOINT.md#reproduce-and-prepare-the-local-fallback) explains how to preserve an isolated demo and regenerate the saved synthetic reports without an app/API dependency. A reproduced both reports during [stage 0 preparation](handoffs/dev-a/live-demo-closeout.md). Preload them before presenting; if switching to fallback, identify them as previously computed synthetic results. The user's local app was not restarted. B's destination-aware consent UI is merged in PR28; either configured text route still requires explicit consent, including its separate evidence/OCR destination. The synthetic story itself needs no provider calls. The consented native timeout and OCR HTTP 503 are recorded separately in [EXTRACTION_CHECK.md](EXTRACTION_CHECK.md).
