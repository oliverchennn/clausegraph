# Fallback runbook — isolated synthetic demo, no providers

Every command here already exists in the repository. This runbook adds no setup script, no dependency and no live call. Commands are quoted from [DELIVERY_CHECKPOINT.md](../../docs/DELIVERY_CHECKPOINT.md), [DEMO.md](../../docs/DEMO.md) and [README.md](../../README.md) at merged `8fa1279`.

Ground rules, all from existing policy: use an isolated checkout with its own SQLite file and blank provider credentials; never copy a cloud-configured `.env`; never reuse another developer's ports, sessions or `.next` directory. The synthetic story needs no provider call at all.

## Before the presentation

Pinned toolchain: Python 3.12, Node 22.23.2, npm 10.9.8, locked dependencies.

Generate the two offline reports and keep them open in a separate browser tab or editor:

```bash
python scripts/verify_demo.py
```

```bash
python scripts/eval_nemotron.py
```

Save each JSON stdout as a UTF-8 file under an ignored local path such as `.data/fallback/`. These are local artifacts, not repository fixtures — regenerate them on any machine you present from. Generated IDs, timestamps and runtimes vary between runs; the values in the acceptance table below are what must hold.

Start the app for the live portion:

```bash
python scripts/dev.py
```

Open a fresh synthetic session at the printed local address and leave it loaded before the timer starts. Scroll past the review queue so the three cash metrics and the decision trace are in view.

## Resetting between runs

Reset only the session you are using, never a shared store:

```bash
python scripts/demo_session.py --reset-session TOKEN
```

`python scripts/demo_session.py` creates a fresh demo session instead. The Settings dialog has the same reset, which replaces that session's data and leaves other sessions untouched.

## Acceptance values for the saved reports

If a saved report disagrees with this table, the report is stale — regenerate it rather than presenting it.

| Saved output | Required synthetic result |
|---|---|
| Nominal plan | Minimum 5000 cents; ending balance 50000 cents |
| Eight-date fixed-plan check | UNSAFE, 8/8 complete; payday 2026-09-27 gives first shortfall 2026-09-26 at −40000 cents |
| Separate no-safe-schedule certificate | At the allowed September 28 payday, nominal optimization proves the best permitted minimum is −40000 cents; no fixed schedule survives the whole declared range |
| Same fixed schedule with 40000 extra opening cents | SAFE for all eight cases; the extra cash is hypothetical, not funding; robust synthesis remains unimplemented |
| Five semantic gate cases | `case_count` 5, `structured_exact_count` 3, `citation_literal_valid_count` 3, `unreviewed_withheld_count` 5, `model_accuracy_measured` false. The three supported fixture candidates match exactly; the two deliberately faulty candidates are rejected. No model accuracy is measured |

## If the browser or API fails mid-demo

1. Switch to the saved reports and any prepared screenshots.
2. Say out loud that these are **previously computed synthetic results**, not a live run.
3. Keep the same assumption and horizon limits you would have stated on screen.
4. Never present an error or an Unknown result as Safe.

Losing internet or a provider does **not** require any live call or a `--live` flag. The synthetic story never needed one. `python scripts/eval_nemotron.py --live --consent-external` is explicitly **not** part of this runbook or any fallback: it sends the synthetic corpus to a configured provider and may consume quota.

## What this runbook does not establish

- No live extraction, OCR, audio, deployment or provider accuracy result.
- No human spoken rehearsal. That is recorded separately in [rehearsal-log.md](rehearsal-log.md).
- No feature freeze, tag or deployment.
- Running a checkout does not prove a running process loaded that commit; restart the app after changing checkouts.
