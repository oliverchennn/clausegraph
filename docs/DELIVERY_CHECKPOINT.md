# Demo checkpoint and history acceptance

## Stable application checkpoint

Use commit [`a00af572cc20afea6893e0e261272bb919aed11f`](https://github.com/oliverchennn/clausegraph/commit/a00af572cc20afea6893e0e261272bb919aed11f) as the reproducible synthetic demo baseline. It includes A's history/deletion contracts (PR19), A's uncertainty validation (PR20), and B's dialog focus correction and demo handoff (PR21). This is a recorded checkpoint, not a new tag, deployment or global feature freeze.

[CI for this exact merged commit](https://github.com/oliverchennn/clausegraph/actions/runs/35486912817) passed 352 backend tests including PostgreSQL 17, 11 real-API Chromium tests, Ruff, generated OpenAPI/TypeScript drift, frontend typecheck/lint/build, and clean installs on Linux, Windows and macOS. A's [readiness handoff](handoffs/dev-a/release-readiness.md) records fresh local contract and fallback checks. Earlier PR validation remains historical evidence.

B's [merged task 5 handoff](handoffs/dev-b/demo-rehearsal.md) records desktop/mobile sign-off, outage/retry recovery, offline fallback and a 180.02-second automated operator run with narration holds. A independently reviewed PR21 and passed all 11 browser tests on its exact head. Human spoken delivery has not been measured; the automated timing is not that sign-off.

B is now implementing task 6's read-only history UI in a separate worktree. That UI is absent from this checkpoint. Presenting this baseline does not depend on finishing history. If history is included in a later presentation build, review and validate its merged commit using the criteria below. Richer uncertainty controls and task 8's advanced design remain separate, unstarted follow-ups.

## Reproduce and prepare the local fallback

Preserve current working trees and user data. For an exact demo, use a separate checkout of the recorded commit with Python 3.12, Node 22.23.2/npm 10.9.8 and locked dependencies. Configure any app run with isolated SQLite/private local files and blank provider credentials; do not copy a cloud-configured `.env` or reuse another developer's ports, sessions or `.next` directory. This readiness task did not restart the user's existing local app, so a checkout update alone does not establish that a running process loaded this commit.

From the isolated checkout, these existing commands work without the app, database service or live providers:

```text
python scripts/verify_demo.py
python scripts/eval_nemotron.py
```

Run them before the presentation and save the JSON stdout as UTF-8 files. This task generated and reloaded `.data/fallback/verify-demo.json` and `.data/fallback/semantic-gates.json` in its own worktree. These are ignored local artifacts, not repository fixtures; recreate them from the commands when preparing another machine. Generated IDs, timestamps and runtimes vary; the assertions below are the acceptance values.

| Saved output | Required synthetic result |
|---|---|
| Nominal plan | Minimum 5000 cents; original end balance 50000 cents |
| Eight-date fixed-plan check | UNSAFE, 8/8 complete; payday 2026-09-27 gives first shortfall 2026-09-26 at -40000 cents |
| Separate no-safe-schedule certificate | At the allowed September 28 payday, nominal optimization proves the best permitted minimum is -40000 cents; no fixed schedule can survive the entire declared range |
| Same fixed schedule with 40000 extra opening cents | SAFE for all eight cases; extra cash is hypothetical, not funding; general robust synthesis remains unimplemented |
| Five semantic gate cases | All five expected gate outcomes pass; three supported fixture candidates and two deliberately faulty candidates; unreviewed execution withheld 5/5; no live model accuracy measured |

Follow [DEMO.md](DEMO.md) and B's presenter cues. Preload the synthetic session and open the saved reports before starting the timer. If the browser/API becomes unavailable, show the previously computed reports and any prepared screenshots, identify them as saved synthetic results, and retain the same assumption/horizon limits. Provider/internet loss does not require a live call or `--live` option. An error or UNKNOWN result must never be presented as SAFE.

Before declaring presentation readiness, perform a human spoken three-minute run using the chosen build and demonstrate switching to the saved fallback. Record that outcome separately. This document does not declare it complete or authorize cloud provisioning, public real-data deployment or a new feature.

## Acceptance for B task 6's history PR

These are review criteria for the already assigned read-only UI, based on [HISTORY_CONTRACT.md](HISTORY_CONTRACT.md) and [verification semantics](handoffs/verification.md). They introduce no new endpoint, schema or implementation assignment. A should review the exact submitted head, confirm current-main ancestry and green CI, and inspect B's committed handoff and browser evidence.

| Area | Concrete acceptance case |
|---|---|
| Read-only behavior | Opening, switching and closing history makes read requests only; the saved plan ID/actions, workspace revision and saved result counts remain unchanged. No automatic plan save, verification run or restore action |
| Identity and current state | Save two plans at one revision, then reactivate an older cached plan. Label the active plan by workspace plan ID and revision, never by list position or revision alone; distinguish results from older input revisions |
| Stored assumptions | Show each plan's saved cash/income/approval assumptions and each verification's nominal plus uncertainty assumptions. Hypothetical opening cash remains hypothetical even with a confirmed plan or SAFE check |
| Saved proof and cash | Preserve SAFE/UNSAFE/UNKNOWN, termination, coverage, proof qualifiers, counterexamples and future obligations. Unauthorized schedules may have no cash trace. Render stored money; never recalculate a historical result from current rules |
| Independent limits | Preserve server order and describe the latest 30 per list. A verification may reference a plan outside the returned plan list; retain its own stored details without inventing a missing record or total count |
| Empty versus failure | A successful empty list is distinct from loading, 500/503 and retry states. Missing persisted points must surface an error. A 401 clears private-session state rather than displaying another session's results |
| Source/reset/session deletion | Populate histories, including older retained rows. Deletion/reset clears selected and displayed history and any frontend copies; delayed earlier responses must not restore it. Source deletion clears all session history while essential obligations remain in the current workspace |
| Session and revision races | Delay a real history response, switch sessions (even at equal revision), or mutate/reset the workspace. Discard obsolete responses and refresh current-state labels. Never leak another session's records or mislabel an old result as current |
| Evidence and presentation | Keep synthetic/historical labels, source references and unavailable-source states honest. Current source text/review is not proof of the saved historical result. Keyboard open/close/focus and 390px layout remain usable |
| Existing demo | Source review, scenario preview, fixed-plan verification, error recovery and the PR21 focus regression still pass after history is added |

Reuse existing backend tests for retention and purge semantics; B's browser tests should demonstrate UI behavior and stale-response handling. B must request any contract/dependency change from A before consuming it. C review remains optional. Any implementation beyond the assigned history UI, including restore, pagination, uncertainty controls or robust synthesis, requires a separate user-approved task.
