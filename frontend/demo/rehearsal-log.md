# Rehearsal log

Human spoken timing and automated browser timing are different evidence. Only a person delivering all six beats aloud against a clock can establish the proposed 180-second presentation.

## Current runs

| Date | Run type | Commit | Presenter | Total | Coverage | Outcome / defects |
|---|---|---|---|---|---|---|
| 2026-09-20 | Automated functional browser | C15 branch (exact SHA in handoff) | Playwright | 3.55 s focused; 2.56 s inside full suite | Desktop complete six-beat control path | Real API; no narration holds; every product beat asserted |
| 2026-09-20 | Automated recovery | C15 branch (exact SHA in handoff) | Playwright | Not a timing rehearsal | 390px + keyboard + one injected 503/retry | Recovery succeeded; no horizontal overflow |
| _(not performed)_ | Human spoken | | | | | Presentation timing remains unverified |

Historical B timing of 180.02 seconds used scripted narration holds on `a00af57`; it predates the completed cash-gap, synthesis and consequence surfaces. Keep it as historical evidence only.

## Human run procedure

1. Record the exact deployed or local commit and confirm the process was restarted on it.
2. Start timing at the first spoken word and run all six beats in `presenter-cues.md`.
3. Record actual beat splits, total time, every missed caveat and any recovery used.
4. Do not convert an automated duration into a spoken result or pre-fill a successful human row.
