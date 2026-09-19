# Three-minute ClauseGraph Verify demonstration

Use only the prominently labeled synthetic demo. No model calls or cloud credentials are needed for this flow. Reset a disposable synthetic session before rehearsing.

## 0:00–0:35 — source to nominal plan

Show the $2,000 opening cash and six synthetic sources. The baseline minimum is −$400. In **Why this plan?**, follow the source → clause → action → ledger effect chain and open its exact quote, page/version, separate evidence/review/approval states and execution deadline. CP-SAT moves the same $450 installment from September 13 to September 26: minimum $50, ending $500. This is timing relief, not savings. The unresolved assistance benefit remains excluded.

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
- `python scripts/eval_nemotron.py --live --consent-external` — only with an authorized configured NVIDIA key; sends the synthetic corpus and may consume quota. No live result is claimed in this delivery.
- `npm --prefix frontend run test:e2e` — real local API browser coverage, including verification and original workflows.

SAFE is bounded to the declared Cartesian product and daily closing balances over the shown horizon. Large ranges/time limits and unresolved evidence produce Unknown unless a concrete failure is found. Future obligations remain represented beyond the horizon; they are not savings. General robust synthesis, intraday settlement, correlations and hidden obligations are outside this implementation.
