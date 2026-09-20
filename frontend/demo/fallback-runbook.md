# Fallback runbook — complete isolated synthetic story

The fallback uses repository scripts and fictional fixtures only. It makes no provider call and needs no cloud service. Restart every process after changing commits; a checked-out SHA does not prove a running process loaded it.

## Prepare before presenting

Use Python 3.12, Node 22.23.2 and npm 10.9.8. From a clean checkout of the presentation commit:

```bash
python scripts/verify_demo.py
```

```bash
python scripts/synthesize_demo.py
```

Save stdout under ignored `.data/fallback/` paths. Call them **previously computed synthetic results**, never live results. Then start the local application:

```bash
python scripts/dev.py
```

Create a fresh baseline session before the timer. The browser story itself needs no provider credential.

## Results that must match

| Segment | Required synthetic result |
|---|---|
| Nominal original | Minimum 5,000 cents; ending 50,000 cents; same $450 obligation shifted |
| Fixed original plan | UNSAFE, complete 8/8; September 27 witness; September 26 shortfall at −40,000 cents |
| Cash diagnostic | 40,000 additional opening cents; proven minimum; one cent less fails; `is_funding: false` |
| Original synthesis | NO_SOLUTION with exhausted declared domain; do not imply broader impossibility |
| Separate resilient example | Nominal fixed plan UNSAFE at −5,000 cents; candidate SAFE 3/3 at 4,900 cents; $1 fee |
| Cancellation preview | Saved $50/$500; preview −$820/$80; $60 removed; same $480 device debt moved earlier exactly once |

If saved output disagrees, regenerate it from the exact presentation commit. IDs, timestamps and runtimes may vary; the financial and proof fields above may not.

## Browser recovery

1. If a request fails, leave the error visible, retry once, and never show stale cash or proof as current.
2. If the browser remains unavailable, switch to both saved JSON reports and label them previously computed.
3. If the original example has changed, use **Settings & privacy → Reset synthetic demo** for that private session, or create a new synthetic session. Never reset a shared or unknown session.
4. If the resilient example is open when the consequence beat begins, use **Open original example**.
5. On a narrow screen, use the walkthrough list and Left/Right/Home/End keyboard controls.

The C15 browser regression exercises a temporary diagnostic failure followed by a successful keyboard retry at 390px. That establishes UI recovery mechanics, not cloud availability.

## Explicitly outside this fallback

- No live NVIDIA, ElevenLabs, Tiger Data or Spaces result.
- No real financial document or external-processing consent.
- No human spoken timing.
- No payment, cancellation, application, approval or message.
