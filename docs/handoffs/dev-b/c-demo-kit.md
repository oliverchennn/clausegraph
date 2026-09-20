# Contributor C; ownership lane dev-b; B remains frontend owner

Task **C10 `c-demo-kit`** (6 points) from the merged reassignment in [DEV_C.md](../../DEV_C.md).

Branch: `codex/dev-b/c-demo-kit`. Worktree: `.worktrees/dev-c-demo-kit`.
Starting and required main commit: `8fa1279c61e702d82f2adb80729f082bfcbc892e` (PR31), whose application baseline includes PR25/PR28 stage 0, PR29 cash-gap contract and PR30 incomplete-source guard.
Required contract changes: none. Markdown only.

Allowed files used, exactly as delegated: new `frontend/demo/presenter-cues.md`, `frontend/demo/fallback-runbook.md`, `frontend/demo/rehearsal-log.md`, plus this handoff. Nothing else was touched — no shared doc, no component, no test, no script.

## Deliverables

**`presenter-cues.md`** — the six-beat proposed 180-second script (30+30+35+30+30+25), a runnable-versus-proposed status table, nine judge questions with honest answers, and a short "do not say" list. Every beat covering unmerged work is marked **proposed** in the table, in the beat heading and in the instruction to say it aloud.

**`fallback-runbook.md`** — the isolated synthetic setup, the two offline report commands, session reset, the acceptance table each saved report must satisfy, and the mid-demo failure procedure. All commands are quoted from existing docs; no new script, dependency or live call is introduced. `--live --consent-external` is explicitly excluded from the fallback.

**`rehearsal-log.md`** — an empty log with an explicit run-type taxonomy (automated operator / human spoken / fallback drill), recording instructions, and the current status: no human spoken run has ever been performed, so presentation readiness is **not** established.

## Status honesty

The three capability states are kept apart throughout:

- **Runnable at `8fa1279`:** beats 1–3 — source review with separate evidence/review/approval fields, nominal plan and decision trace, fixed-plan verification with counterexample.
- **API merged, no presenter UI:** beat 4, the cash-gap diagnostic. `POST /api/cash-gap` is merged (PR29) and the offline script reproduces the number, but B's `cash-gap-diagnostic-ui` is not merged, so the cue sheet directs the presenter to the saved script output and says the on-screen surface is still to come.
- **Proposed:** beats 5 and 6 — resilient synthesis (stage 3) and the consequence walkthrough (stage 4).

Timing is labelled as a plan, not a measurement. B's historical **180.02 s** figure is cited as an *automated operator* run on the older `a00af57` baseline and explicitly not as spoken delivery. No timing was invented, and the log deliberately ships with zero rows because this task had no presenter.

## Checks and results

Markdown-only task, so no application rerun for prose — but every factual claim was verified against merged source rather than copied from prose.

| Check | Result |
|---|---|
| Relative links resolve | 9/9 resolve (scripted check across all three files) |
| Beat budgets total 180 s | Cue sheet 30+30+35+30+30+25 = **180**; rehearsal-log reference table independently sums to **180** |
| Every cited command exists | `scripts/verify_demo.py`, `scripts/eval_nemotron.py`, `scripts/dev.py`, `scripts/demo_session.py` all present; `--reset-session` is a real flag |
| Cited API claims exist | `/api/cash-gap` present in `api.py`; `is_funding` present in `schemas.py` |
| Acceptance table matches a real run | `python scripts/verify_demo.py`: nominal minimum **5000**; **UNSAFE 8/8 complete**; counterexample payday **2026-09-27**, first shortfall **2026-09-26** at **−40000**; no-safe-schedule proven with best minimum **−40000** at the allowed September 28 payday; **40000** extra opening cents → **SAFE**; robust synthesis **false** |
| Semantic gate row matches a real run | `python scripts/eval_nemotron.py`: `case_count` 5, `structured_exact_count` 3, `citation_literal_valid_count` 3, `unreviewed_withheld_count` 5, `model_accuracy_measured` false. The row was rewritten to cite these counters rather than prose |
| `git diff --check` | Passed |
| `python scripts/check_workflow.py --require-current` | Passed: lane ownership, task handoff, conflict markers, current main |

### Toolchain note — the frontend environment now works on this host

Earlier C tasks recorded that frontend checks could not run here. That is resolved and worth recording for C11–C15, which require real-API browser tests:

- `npm ci --engine-strict=false` installs from the existing lockfile without editing `frontend/.npmrc` (an A-owned file) or touching `package.json` / `package-lock.json` — both confirmed unmodified by `git status`.
- The Playwright Chromium browser was installed into the user-level cache.
- **The existing browser suite passes in full on this host: 28/28 in 1.1 minutes** on ports 8041/3041 with isolated storage and blank provider credentials.

The remaining deviation is the runtime version: Node **v24.2.0** / npm **11.3.0** against the pinned 22.23.2 / 10.9.8. Suite behavior matched expectations, but CI on the pinned toolchain remains authoritative.

No provider call, upload, deployment or outbound message. No other developer's checkout, branch, service, session, ports or `.next` directory was touched.

## Limits and handback

- This is preparation, not rehearsal. **No human spoken run was performed**, so presentation readiness is explicitly not claimed. That gate needs a presenter and belongs to C15.
- Beats 4–6 narrate work that is not merged. Until stages 1B–4 land, a real run will either come in under 180 s or spend that time describing proposed behavior; the log asks the presenter to record which actually happened.
- The cue sheet will need updating as each stage merges — beat 4 when B's cash-gap UI lands, beats 5 and 6 at stages 3 and 4. C15 (`c-final-demo`) is the assigned task that reconciles all three files against the integrated build.
- C owns these three files; B retains all shared frontend state, forms and integration. If B needs them, C stops, preserves the diff and reports handback.
