# Developer B: demo polish and rehearsal

## Assignment

The user assigned B to review A's completed history/deletion work, verify the next B task, and complete demo polish and rehearsal. Original task 2 is already merged; this task completes the outstanding row 4/5 presentation checks. It does not start the later history UI.

Branch: `codex/dev-b/demo-rehearsal`. Worktree: `.worktrees/dev-b-demo-rehearsal`.
Starting and required main commit: `f23133bd7828186edfd72caf367be99a3201d33d` (PR18), including B's PR8 and C's PR17. No unmerged contract is consumed. A's PR19 at `5b94f3433faa3447103bd69cf1f940a1868be2bb` is reviewed separately in a detached snapshot.

Allowed writes: this handoff and B-owned frontend presentation/styles/accessibility/browser tests, limited to reproduced demo blockers. A-owned manifests, locks, generated types, backend, scripts, fixtures, central docs, and other task handoffs remain outside this assignment.

After the user merged PR19, fetched and fast-forwarded both clean main and this task to `7088b81` before frontend checks. Exact implementation paths reserved for the reproduced keyboard defect: `frontend/src/components/ui.tsx`, `frontend/tests/review-queue.spec.ts`, and `frontend/tests/verification.spec.ts`, plus this handoff. No C write release exists for these paths.

## Acceptance

- Independently review PR19's history ordering/privacy tests and consumption guidance; record findings for A's merge coordination.
- Install from the existing frontend lock with Node 22.23.2/npm 10.9.8 and use shared Python 3.12 without modifying dependencies.
- Run typecheck, lint, build and the full real-API browser suite in this worktree with isolated ports/storage.
- Inspect desktop and mobile overview, evidence, review and verification views, including keyboard operation and error recovery.
- Rehearse the source-to-plan, eight-date Unsafe, six-date Safe, cash diagnostic and semantic-gate story against the three-minute cue sheet. Record measured operator timing separately from any human spoken presentation.
- Exercise the local fallback without external services, preserve bounded-proof and synthetic labels, and record exact checks, limits and artifacts.
- Publish for A review; A owns merge coordination and any central feature-freeze record.

## Isolation

Fetched origin with pruning before task creation. Clean main matched `f23133b`; historical and dirty worktrees were preserved. The existing pre-push hook was confirmed by `scripts/install_hooks.py`. B's application and tests use only this worktree, separate ports, disposable synthetic sessions, and blank provider credentials. No root `.env` is copied.

## Results

### Independent B review of PR19

Reviewed `5b94f3433faa3447103bd69cf1f940a1868be2bb`: storage tie-breaking, the eight parameterized history/privacy cases, related existing read/persistence/deletion paths, and the consumption contract. **No blocking findings; B recommends merge.** The descending ID tie-breaker stabilizes timestamp ties without inventing chronological meaning. Identity/revision, saved assumptions, independent list limits, chart read failure, and cross-session deletion semantics are accurately separated.

Independent command in the detached B review snapshot: `python -m pytest backend/tests/test_history_api.py -q -p no:cacheprovider --basetemp .data/b-review-pytest`: **8 passed, 8 PostgreSQL variants skipped, 2 existing dependency warnings in 13.46 seconds**. Local PostgreSQL is not configured; the exact-head PR CI reports passing PostgreSQL coverage and all required checks. GitHub reported PR19 open/mergeable at review time. Initial test setup hit the shared Windows temporary-directory ACL; using an isolated worktree base temp directory resolved the environment issue without source changes.

Reviewer: Developer B, this task. Review recommendation was also reported to the user when they asked whether PR19 could merge. A/user retains merge coordination.

### Demo checks

Pinned clean install, typecheck, lint, production build (145 kB first load) and all 11 existing browser tests passed on merged `7088b81` before the focus correction. Browser suite: 1.4 minutes on ports 8032/3032; offline scripts reproduced all documented synthetic proof/gate values. No external provider credentials or root app data were used.

Visual/keyboard inspection found a reproducible accessibility defect: these controlled dialogs have no Radix `Dialog.Trigger`, so Radix's default close autofocus has no trigger to return to. Closing source evidence left focus on the page body, interrupting keyboard continuation through the review queue/counterexample. The shared modal now remembers the focused opener before autofocus and restores it on close if it remains connected, without jumping the scroll position. Radix still manages initial focus and trapping. No financial state or API contract changes.

The two new focus assertions failed before the fix (mobile review queue with Escape; desktop counterexample with the close button). The final full real-API suite passed **11/11 in 1.2 minutes**, including both assertions, review/error preservation, stale revisions/sessions, source deletion, previews and Safe/Unsafe/Unknown behavior. Final desktop/mobile screenshots were inspected; the mobile review button visibly retains its focus ring after Escape. No clipped controls or horizontal overflow was observed in the exercised 1440x1000 desktop and 390x844 mobile surfaces. This is focused demo/accessibility sign-off, not a comprehensive assistive-technology audit.

### Timed operator rehearsal and local fallback

The ignored `.data/rehearsal.spec.ts` / `.data/rehearsal.config.ts` harness exercised the existing [three-minute demo](../../DEMO.md) with a preloaded synthetic session and explicit 0/35/80/120/160/180-second cues. **Two exploratory checks passed in 3.4 minutes**: the paced demo/fallback and mobile verification outage/retry. The measured cue sequence took **180.02 seconds**. These are automated operator timings with deliberate narration holds; no human spoken delivery was measured. The timed run preceded the focus fix; both affected evidence-return flows were then validated in the final browser suite.

| Cue | Observed completion from start | Result shown |
|---|---|---|
| 0:00 source / nominal plan | 0.95 s | Exact approved clause, separate gates, $2,000 opening / -$400 current path / $50 lowest / $500 ending |
| 0:35 broader bounds | 35.67 s | Eight dates, 2026-09-21 through 2026-09-28, all checked; Unsafe |
| 1:20 counterexample | 81.17 s | Payday 2026-09-27, first shortfall 2026-09-26, -$400; red chart and event evidence |
| 2:00 narrower model / diagnostic | 120.99 s | Six-date Safe; separate offline no-safe-schedule proof and $400 hypothetical cash diagnostic |
| 2:40 semantics / limits | 160.13 s | Five offline expected gate outcomes pass; unreviewed execution withheld 5/5; no model accuracy measured |
| 3:00 stop | 180.02 s | Saved plan ID, revision and actions unchanged |

All non-local browser network requests were blocked; **zero external requests and zero page errors** occurred. The backend ran with blank provider credentials. A synthetic 503 on verification displayed its error, showed no safety result, preserved the nominal $50 plan, and succeeded on retry. The full suite separately covers queue retry, denied/pending approvals and incomplete verification.

Local fallback was rehearsed by opening precomputed script results in a separate browser page with no app/API dependency. `scripts/verify_demo.py` reproduced 8/8 Unsafe, a separate optimal nominal result of -40000 cents at the allowed September 28 assignment, and the same fixed schedule Safe for 8/8 after adding 40000 hypothetical opening cents. `scripts/eval_nemotron.py` reproduced all five expected synthetic gate outcomes (three supported candidates, two deliberately wrong candidates rejected). These are saved calculations, not funding or live model accuracy.

Artifacts remain local and ignored in this worktree: `.data/verify-demo.json`, `.data/eval-offline.json`, `.data/rehearsal-results/` (timing JSON; desktop/mobile evidence, Unsafe/Safe, chart, outage and fallback screenshots), and `frontend/test-results/` (final regression screenshots). The temporary browser tab was closed and its viewport override reset. Test-owned servers exit with Playwright; the user's root app and A's separate task were not stopped.

### Presenter cues and fallback procedure

Use a fresh synthetic session; preload the page and the two offline reports before starting the timer. At desktop size, scroll past the review queue to the three cash metrics and decision trace. Keep the graph and cancellation comparison as optional detours outside the three-minute story.

1. **0:00–0:35:** Identify the synthetic scenario and available cash. Open exact evidence and point to the approval, review and source fields separately. The same $450 installment moves from September 13 to September 26; $50 is the lowest projected balance and $500 is the ending balance. Say “timing relief, not savings.” Close the drawer and continue from its restored opener.
2. **0:35–1:20:** Use the September 28 preset, explain the inclusive user-assumed dates, and run fixed-plan verification. Neither the saved actions nor their execution dates change.
3. **1:20–2:00:** Show all eight cases checked, the September 27 paycheck witness, September 26 shortfall and -$400 balance. Follow one event evidence link and return to the chart.
4. **2:00–2:40:** Use the September 26 preset and explain Safe for these six dates only. Narrowing assumptions does not solve the broader failure. Show the saved offline report: a separate nominal optimization proves no permitted schedule survives every broad-range date; $400 extra hypothetical opening cash makes the same fixed schedule pass the declared eight-case check. It creates no funding.
5. **2:40–3:00:** Show the offline gate report. Candidates become typed rules only after evidence/human/approval gates; deterministic code computes money. State the finite bounds/horizon, retained future debt and absence of executed financial actions. This is not a live provider accuracy demonstration.

If internet/provider access is unavailable, the local synthetic flow remains available. If the browser/API fails, immediately show the saved fallback screenshots and JSON reports; label them as previously computed synthetic results and use the same limits above. Do not turn an error/Unknown into Safe. The scripts can regenerate the fallback without starting the app: `python scripts/verify_demo.py` and `python scripts/eval_nemotron.py` from this worktree, where `python` is the repository's Python 3.12 environment. Do not use `--live` for this fallback. No additional installs or provider setup belong in the timed presentation.

### Final validation and handoff

All npm commands use the existing Node 22.23.2/npm 10.9.8 runtime at `.worktrees/.toolchain/node-v22.23.2-win-x64`, with this task's own `frontend/node_modules`. Python is the shared root `.venv/Scripts/python.exe` (3.12). No dependency, lockfile, generated contract, backend, central progress document or peer handoff changed.

| Check | Result |
|---|---|
| `npm ci --no-audit --no-fund` | Passed; 439 packages, unchanged lockfile |
| Final `npm run typecheck`; `npm run lint` | Passed |
| Final `npm run build` | Passed; static `/`, 145 kB first-load JavaScript |
| `E2E_API_PORT=8032 E2E_WEB_PORT=3032 npm run test:e2e` | 11 passed in 1.2 minutes, after focus fix |
| Same ports, `node node_modules/@playwright/test/cli.js test --config ../.data/rehearsal.config.ts` from frontend | 2 passed in 3.4 minutes; paced operator/fallback and outage recovery before focus fix |
| `python scripts/verify_demo.py`; `python scripts/eval_nemotron.py` | Passed with the synthetic results above |
| `git diff --check` | Passed; existing line-ending normalization notices only |

Next.js development-origin and color-environment notices were nonfatal. Backend application logic was unchanged; independent PR19 tests and its green CI are recorded above rather than claiming a new full backend run in B's task. A owns review/merge and central freeze documentation. Human spoken rehearsal, live-provider validation, history UI and richer uncertainty controls are not claimed or started by this task.
