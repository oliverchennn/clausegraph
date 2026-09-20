# Cash-gap segment — presenter notes

Covers **beat 4** of [presenter-cues.md](presenter-cues.md): 30 seconds, from the failed verification to a number the judges can trust.

**Status:** runnable end to end once stage 1 merges. A's diagnostic API merged as PR29; B's panel is `cash-gap-diagnostic-ui`. Before both are on main, use the saved `verify_demo.py` output described in [fallback-runbook.md](fallback-runbook.md) and say the on-screen surface is still to come.

## The 30 seconds

You arrive holding an **Unsafe** result: eight cases checked, payday September 27, first shortfall September 26, balance **−$400**.

1. **Ask the question out loud.** "The plan fails. How big is the hole, exactly?" Press **Diagnose the cash gap**.
2. **Read the headline.** **$400**, labelled *proven minimum for this fixed schedule*. Say what proven means here: that amount verifies safe across all eight cases, and **one cent less still fails**. It is a proof about this schedule inside the declared bounds — not a claim about every possible schedule.
3. **Say the disclaimer before anyone asks.** "This is a diagnostic, not funding." No money was obtained, no approval granted, no obligation changed. The panel says it on screen; say it anyway.
4. **Show the comparison.** The saved schedule as recorded is UNSAFE; the same schedule under the assumed cash is SAFE. Same actions, same dates — only the declared opening cash moved.
5. **Land on evidence.** Open **Evidence behind the limiting date** for September 26. The $450 installment and its source rule are what drive the number. Close the drawer and point out the saved plan is still exactly as it was.

## The two labels that must never blur

Judges will probe this, and it is the most interesting thing in the segment.

| What happened | What the panel says | What you say |
|---|---|---|
| Every declared case checked, amount verified, one cent less fails | **Proven minimum for this schedule** | "Proven within the declared bounds and horizon." |
| Coverage stopped at a case or time cutoff | **Inconclusive · coverage stopped early** | "We stopped early, so there is no minimum to report — only a floor we already know is not enough." |

A cutoff never becomes a minimum. If you see "Inconclusive", do not describe an amount.

## When cash is the wrong question

Set the approval dropdown to vary the payment extension and verify again. The diagnostic returns **Cash cannot repair this**, with `authorization` listed as the blocker and **no amount at all**.

This is the line worth delivering slowly: *money does not buy an approval.* A denied or pending third-party decision, or unresolved evidence, is not a funding problem, and the system refuses to answer it with a number. That refusal is a feature — it is the difference between a planner and a wish.

## Reuse, not recomputation

Every figure in this segment comes from the merged backend: the amount, the minimality claim, the coverage counts, the limiting date and the blocking properties. The browser computes no money, and this segment adds no arithmetic of its own. A's backend suite already owns the independent small-ledger oracle and the one-cent-less check; the demo does not re-derive them.

## Limits to state if asked

- Proven means proven **within the declared Cartesian product and displayed horizon**. Outside those bounds it claims nothing.
- V1 diagnoses additional opening cash only. It does not search for new permissions, edit clauses, or combine repairs.
- It says nothing about whether a *different* schedule would survive. That is the resilient-synthesis question in beat 5, which is proposed and unimplemented.
- The synthetic fixtures are fictional and labelled as such in the UI.
