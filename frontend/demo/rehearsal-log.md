# Rehearsal log

One entry per rehearsal. **Do not pre-fill timings.** A row exists only after the run it describes actually happened, and the run type must say who or what produced the timing.

Run types:

- **Automated operator** — a Playwright-driven pass with scripted narration holds. Useful for checking that controls reach the right state in roughly the right order. It is **not** a spoken-delivery measurement.
- **Human spoken** — a person presenting aloud against a clock. This is the only run that establishes presentation readiness.
- **Fallback drill** — deliberately losing the browser or API mid-run and switching to the saved reports.

## Entries

| Date | Run type | Commit | Presenter | Total | Per-beat actual | Outcome and defects |
|---|---|---|---|---|---|---|
| _(none recorded by this task)_ | | | | | | |

## Status at the time of writing

- **Automated operator:** recorded previously at **180.02 s** by B on the `a00af57` baseline, in [B's demo handoff](../../docs/handoffs/dev-b/demo-rehearsal.md). That run predates the current merged UI and the six-beat script in [presenter-cues.md](presenter-cues.md); it is historical evidence, not a measurement of the current story.
- **Human spoken:** **never performed.** No presenter has run this aloud against a clock. Presentation readiness is therefore **not** established.
- **Fallback drill:** exercised by B as part of the same historical automated run; not re-run against the current merged UI.

This task prepared the materials. It could not perform a human spoken run because that needs a presenter, and inventing a timing would defeat the purpose of the log.

## How to record a run

1. Note the exact commit you are presenting from, and whether the app process was restarted after checking it out.
2. Start the timer at the first spoken word, not at page load.
3. Record the actual per-beat marks you hit, not the planned budgets from the cue sheet. Deviation is the useful signal.
4. Record every defect with an owner: A for backend, contracts or financial logic; B for frontend state, forms and shared integration; C for the assigned demo views and materials.
5. If a beat covers a proposed feature, record whether the presenter said "proposed" out loud. This is the single easiest thing to get wrong under time pressure.
6. Record what was **not** exercised. An unrun check is not a passing check.

## Beat budget reference

Planned, from [presenter-cues.md](presenter-cues.md). Totals 180 s.

| Beat | Planned | Runnable at `8fa1279`? |
|---|---|---|
| 1 source → reviewed rule | 30 s | Yes |
| 2 nominal plan and trace | 30 s | Yes |
| 3 declare bounds, Unsafe counterexample | 35 s | Yes |
| 4 cash-gap diagnostic | 30 s | API only; presenter UI proposed |
| 5 resilient alternative | 30 s | Proposed |
| 6 consequences and limits | 25 s | Walkthrough proposed; numbers runnable via preview |

Beats 4–6 depend on work that is not merged. Until it is, a human run will either be shorter than 180 s or will spend that time narrating proposed behavior — record which one actually happened.
