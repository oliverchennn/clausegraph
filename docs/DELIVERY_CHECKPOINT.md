# Demo checkpoints and history acceptance

## Current cash-gap and uncertainty-controls checkpoint

Commit [`2e7653718ff7fac27158789deff965775da408a1`](https://github.com/oliverchennn/clausegraph/commit/2e7653718ff7fac27158789deff965775da408a1) includes PR34 cash-gap UI, PR37 C10 presenter kit, PR36 C11 demo/tests and PR35 multi-dimension uncertainty controls, as well as the earlier API guards and contracts. [CI on this exact merged main commit](https://github.com/oliverchennn/clausegraph/actions/runs/35497142151) passed **390 backend tests in 29.34 seconds** (including PostgreSQL; two existing warnings) and **46 real-API Chromium tests in 2.3 minutes**, Ruff, generated OpenAPI/TypeScript drift, frontend typecheck/lint/build and Linux/Windows/macOS clean installs. The PR-only ownership job is intentionally skipped on main.

Independent A review and conflict resolution are recorded in the [C10 integration handoff](handoffs/dev-b/c-demo-kit-integration.md), [C11 integration handoff](handoffs/dev-b/c-cash-gap-demo-integration.md) and [uncertainty UI integration handoff](handoffs/dev-b/uncertainty-explorer-ui-integration.md). PR38 was closed as duplicate cash-gap implementation, with its useful retry coverage retained in PR36. Original contributor handoffs and historical branches are preserved.

Use this checkpoint for the current implemented cash-gap story and uncertainty controls. C12's dedicated failure view remains an empty released seam; synthesis/adoption and consequence walkthrough are not implemented. The [synthesis specification](RESILIENT_PLAN_SPEC.md) is a proposed design awaiting B review. No successful live extraction or human spoken rehearsal is inferred from CI. The [C10 presenter kit](../frontend/demo/presenter-cues.md), [fallback runbook](../frontend/demo/fallback-runbook.md) and [C11 cash-gap segment](../frontend/demo/cash-gap-demo.md) are source material; preserve their historical/proposed labels when using the current [demo script](DEMO.md).

The earlier exact checkpoints below remain reproducible history. This update does not restart the user's app, deploy a service or change stored sessions. Reproduce the chosen commit in an isolated checkout using the fallback procedure below.

## Validated application checkpoint with history

Commit [`ca7cde59287e5456a9398965796c873152176491`](https://github.com/oliverchennn/clausegraph/commit/ca7cde59287e5456a9398965796c873152176491) includes PR23's read-only history UI and all earlier baseline work. [CI on this exact merged commit](https://github.com/oliverchennn/clausegraph/actions/runs/35488606919) passed 352 backend tests in 39.69 seconds, including PostgreSQL 17; 19 real-API Chromium tests in 2.0 minutes; Ruff, generated OpenAPI/TypeScript drift, frontend typecheck/lint/build, and clean installs on Linux, Windows and macOS. The PR-only ownership job is intentionally skipped on main.

[A's recorded PR23 review](https://github.com/oliverchennn/clausegraph/pull/23) found no blockers on exact head `150809d2db82ef216859189467994beaad832739`, independently passed all 19 real-API browser tests and inspected desktop/mobile history screenshots. This is distinct from B's implementation checks. The historical review criteria below remain useful regression criteria; history is delivered.

A's [stage 0 closeout handoff](handoffs/dev-a/live-demo-closeout.md) records fresh local preparation: 130 existing focused tests passed, eight PostgreSQL variants skipped without a disposable test URL; both fallback scripts passed and their saved reports parsed; both native/scanned no-consent uploads stayed local and were deleted. PR24 (`e65464c`) subsequently changed assignment documents only; it did not change the tested runtime. No new live provider, human source-review or spoken-rehearsal success is claimed. [EXTRACTION_CHECK.md](EXTRACTION_CHECK.md) records the subsequently consented native timeout and OCR HTTP 503. Neither produced rules or a successful live flow. The [follow-up API fix](handoffs/dev-a/incomplete-source-guard.md) prevents incomplete processing from producing a confirmed plan or verification result; that fix is not part of the earlier recorded checkpoint.

This historical commit is a reproducible history-UI baseline; use the newer checkpoint above for the expanded cash-gap/uncertainty story. Preserve the isolated setup and fallback procedure below. The earlier `a00af57` baseline and its rehearsal evidence remain valid historical records. No checkpoint is a deployment or a global feature freeze.

## Earlier recorded demo checkpoint

Use commit [`a00af572cc20afea6893e0e261272bb919aed11f`](https://github.com/oliverchennn/clausegraph/commit/a00af572cc20afea6893e0e261272bb919aed11f) as the reproducible synthetic demo baseline. It includes A's history/deletion contracts (PR19), A's uncertainty validation (PR20), and B's dialog focus correction and demo handoff (PR21). This is a recorded checkpoint, not a new tag, deployment or global feature freeze.

[CI for this exact merged commit](https://github.com/oliverchennn/clausegraph/actions/runs/35486912817) passed 352 backend tests including PostgreSQL 17, 11 real-API Chromium tests, Ruff, generated OpenAPI/TypeScript drift, frontend typecheck/lint/build, and clean installs on Linux, Windows and macOS. A's [readiness handoff](handoffs/dev-a/release-readiness.md) records fresh local contract and fallback checks. Earlier PR validation remains historical evidence.

B's [merged task 5 handoff](handoffs/dev-b/demo-rehearsal.md) records desktop/mobile sign-off, outage/retry recovery, offline fallback and a 180.02-second automated operator run with narration holds. A independently reviewed PR21 and passed all 11 browser tests on its exact head. Human spoken delivery has not been measured; the automated timing is not that sign-off.

The history UI is absent from this earlier checkpoint and is now delivered in the validated `ca7cde5` checkpoint above. The [expanded assignment queue](HACKATHON_ASSIGNMENTS.md) governs later cash diagnostics, uncertainty controls, reviewed synthesis design and consequence work; those features are not claimed by either checkpoint.

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

These were the review criteria for the read-only UI delivered in PR23, based on [HISTORY_CONTRACT.md](HISTORY_CONTRACT.md) and [verification semantics](handoffs/verification.md). They remain regression guidance and introduce no new endpoint, schema or implementation assignment. The exact submitted head, independent A review and merged CI are recorded above.

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

Reuse existing backend tests for retention and purge semantics and B's browser tests for UI behavior and stale-response handling. B must request any contract/dependency change from A before consuming it. C review remains optional. Follow the separate scopes and prerequisites in [HACKATHON_ASSIGNMENTS.md](HACKATHON_ASSIGNMENTS.md) for further implementation; this history acceptance record authorizes no additional feature.

Current integration context: PR28 merged destination-aware browser consent, PR25 merged this preparation record, and PR26/27 corrected trace claims and Brev variability wording. Their historical handoffs remain unchanged. New checks for the incomplete-source fix and the current merged frontend belong to its separate follow-up handoff; do not apply the earlier 19-test checkpoint count to that expanded UI.
