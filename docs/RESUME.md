# ClauseGraph current checkpoint

## Merged application checkpoint: 2026-09-20 UTC

Remaining required work is rebalanced to approximately **A 35% / B 35% / C 30%**. A owns backend/integration; B leads frontend state/shared integration; C owns assigned frontend views and demo delivery. Fetched main is `e65464c` (PR24), with the PR19-23 application baseline merged. The user reports A/B's first tasks and all previous C assignments done; PR25/28 and C follow-ups PR26/27 are published but still open at this refresh. Preserve these tasks and their handoffs; publication is not integration.

The [A/B/C assignments](HACKATHON_ASSIGNMENTS.md) retain closeout -> **#2 cash-gap -> #3 uncertainty -> #1 resilient synthesis -> #4 consequences**, with #5 time-permitting and #6 lower priority. A/B finish integration of existing closeout/consent work before their next stage tasks. C starts **C10 demo kit**, then C11 cash-gap demo, C12 uncertainty failure view, C13 resilient-plan demo, C14 consequence walkthrough and C15 final rehearsal/fallback, following [DEV_C.md](DEV_C.md). The old optional-only review queue and prompt limits are retired. One task/fresh worktree at a time; new exact C paths are delegated and existing shared files need B's merged release. This refresh assigns work, not implemented features.

The previously validated application checkpoint `a00af57` and its [delivery record](DELIVERY_CHECKPOINT.md) remain historical evidence. B's [history handoff](handoffs/dev-b/history-ui.md) records its implementation and 19 passing local browser tests; stage 0 checks the combined merged checkpoint's CI. Existing worktrees and the user's running app were preserved, so the running app's version is not inferred from Git HEAD.

Read [WORKSTREAMS.md](WORKSTREAMS.md) for current PR heads, ownership and integration order. C's historical PR16/17 exceptions remain historical; new C10-C15 authorization is the exact-path delegation in this reassignment, within the existing dev-b lane. C's required deliverables count toward stage completion; its extra review does not replace required A/B mutual review. Peer handoffs remain unchanged.

[NVIDIA_BREV.md](NVIDIA_BREV.md) explains hosted/private text inference. Brev browser consent is implemented in open PR28, not yet in this main checkpoint. The [historical Brev retest](handoffs/dev-a/brev-live-retest.md) passed 3/5 then 5/5 exact fields with unchanged code; citations/unreviewed withholding passed 5/5 both times. This is observed variability, not an improvement or general accuracy/OCR/full-browser result. A's local PR25 continuation reports hosted native timeout/OCR503 and an incomplete-source empty-plan confirmation defect under active repair. Do not overwrite that work or claim live success; A records the final fix/check evidence in its own handoff. No provider call occurs in this reassignment task.

## Existing baseline

Source/evidence/condition review, nominal planning, source-to-cash decision traces, nonmutating scenario previews and bounded fixed-plan verification are already implemented. Original synthetic values remain baseline-40000/50000 cents, approved shift5000/50000, denied shift-40000/50000, cancellation alone-82000/8000. No money is computed by language models or React. See [verification semantics](handoffs/verification.md), [integration history](handoffs/integration.md), [architecture](ARCHITECTURE.md) and [demo](DEMO.md).

[Historical CI on checkpoint `a00af57`](https://github.com/oliverchennn/clausegraph/actions/runs/35486912817) passed 352 backend tests including PostgreSQL 17, 11 real-API Chromium tests, Ruff, generated OpenAPI/TypeScript drift, frontend typecheck/lint/build, and clean installs on Linux, Windows and macOS. This checks PR20 and PR21 together. A's fresh local history/uncertainty checks passed 45 tests with eight PostgreSQL variants skipped because no local disposable test URL is configured. Both offline scripts passed and their saved JSON reloaded with the expected outcomes.

The merged [history contract](HISTORY_CONTRACT.md) documents private history, assumptions, stable ordering and deletion beyond the displayed 30. The [uncertainty contract](UNCERTAINTY_CONTRACT.md) documents existing bounded semantics and limits without changing schemas. Earlier [integration](handoffs/dev-a/integration-validation.md), [history](handoffs/dev-a/history-contracts.md) and [uncertainty](handoffs/dev-a/uncertainty-limits.md) handoffs retain their original checks. PR22 added the delivery record and PR23 added the history UI. Advanced diagnostics, richer uncertainty controls, synthesis and consequence walkthrough remain assigned future work.

## Run/check

Use Python3.12, Node22.23.2/npm10.9.8. Install backend with backend/requirements.txt constrained by backend/requirements.lock; frontend with npm ci. After bootstrap merges, activate the Python environment and run python scripts/install_hooks.py in each clone. Existing custom hooks are preserved; inspect/chaining is needed if core.hooksPath is configured. Windows local Python may require .venv/Scripts/python.exe; macOS/Linux .venv/bin/python.

Run python scripts/dev.py for the local stack. Do not duplicate running ports or run frontend dev/build/E2E against the same .next directory concurrently. Lane browser tests use distinct E2E_API_PORT/E2E_WEB_PORT and their own checkout. Full checks: backend pytest including PostgreSQL in CI, Ruff, OpenAPI/types drift, frontend typecheck/lint/build, browser flows, and Linux/Windows/macOS clean installs.

## Remaining limits

The historical PR8 queue failures are resolved; PR17's historical ancestry-gate failure remains recorded in the integration handoff. B's [merged task 5 handoff](handoffs/dev-b/demo-rehearsal.md) now records a 180.02-second automated operator rehearsal, local fallback/outage checks and focused desktop/mobile sign-off. A's PR21 review found no blockers and independently passed 11 browser tests. Human spoken delivery remains unmeasured, and no global feature freeze is declared. History is now merged; stage 0 verifies the combined checkpoint while preserving the recorded fallback.

Hosted NVIDIA evidence/OCR, audio, Tiger Data, cloud storage and deployment remain live-unverified. The limited historical Brev native-text results above do not establish them. Further live validation requires configured server-side credentials and explicit processing consent. No billing/provisioning or public real-data release is authorized by this increment. Keep provider failures visible and source/session deletion semantics intact.

The private repository's current plan cannot require checks before a GitHub merge; hooks/CI reduce accidental conflicts but A must follow the review/green-check rule. No workflow guarantees freedom from semantic conflicts. No force-push, discarded changes, public visibility change or account upgrade is needed.

Keep the recorded fallback stable during the [required expansion stages](HACKATHON_ASSIGNMENTS.md). The earlier freeze/deferred-feature order is superseded by this explicit user assignment. General robust synthesis still needs its reviewed specification; correlations, uncertain expenses and adaptive schedules remain outside v1. Optional #5/#6 never displace required delivery or human rehearsal. No implementation, provider call, service restart or deployment is part of this documentation refresh.
