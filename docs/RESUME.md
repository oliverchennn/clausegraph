# ClauseGraph current checkpoint

## Merged application checkpoint: 2026-09-20 UTC

Developer A owns backend/integration; Developer B owns frontend; Developer C contributes optional proofreading, bug reproduction and UI cleanup. A/B never wait for C's availability. A's history/deletion and uncertainty validation are merged (PR19/PR20); B's task 5 demo/focus work is merged (PR21). The user assigned A the bounded integration/readiness record and confirmed B has started task 6's read-only plan/verification history. Consult the user before starting any further task.

Current merged application checkpoint: `a00af572cc20afea6893e0e261272bb919aed11f` ([PR21](https://github.com/oliverchennn/clausegraph/pull/21), including [PR20](https://github.com/oliverchennn/clausegraph/pull/20)). Earlier workflow, review queue, NVIDIA/Brev support, source-reference fixes and C's corrections remain included; duplicate PR14 remains closed. Historical branches and dirty worktrees are preserved. Current A task: `codex/dev-a/release-readiness`; [exact scope/results](handoffs/dev-a/release-readiness.md), [stable demo and history acceptance](DELIVERY_CHECKPOINT.md). No runtime or contract change is assigned. The user's local app was not restarted, so its loaded code is not inferred from the checkout's new HEAD.

Read [WORKSTREAMS.md](WORKSTREAMS.md) for current ownership and [DEV_C.md](DEV_C.md) for C's task menu and release protocol. C's merged handoffs record the owner's explicit exceptions for PR16/PR17; those patches do not create a standing release or permanent ownership. Future C work still follows the documented assignment rules. Other contributors' handoffs remain historical and unchanged.

[NVIDIA_BREV.md](NVIDIA_BREV.md) explains hosted and private text inference. Hosted NVIDIA remains the browser default because Brev-specific browser consent is still unimplemented. The [historical Brev retest](handoffs/dev-a/brev-live-retest.md) exercised five synthetic native-text clauses on the user's existing GPU: exact fields passed 3/5 and then 5/5 with unchanged code; citations and withholding of unreviewed execution passed 5/5 in both runs. This confirms working inference with observed variability, not general accuracy, OCR, or a full live browser workflow. No provider call was made in the readiness task.

## Existing baseline

Source/evidence/condition review, nominal planning, source-to-cash decision traces, nonmutating scenario previews and bounded fixed-plan verification are already implemented. Original synthetic values remain baseline-40000/50000 cents, approved shift5000/50000, denied shift-40000/50000, cancellation alone-82000/8000. No money is computed by language models or React. See [verification semantics](handoffs/verification.md), [integration history](handoffs/integration.md), [architecture](ARCHITECTURE.md) and [demo](DEMO.md).

[CI on the exact merged application checkpoint](https://github.com/oliverchennn/clausegraph/actions/runs/35486912817) passed 352 backend tests including PostgreSQL 17, 11 real-API Chromium tests, Ruff, generated OpenAPI/TypeScript drift, frontend typecheck/lint/build, and clean installs on Linux, Windows and macOS. This checks PR20 and PR21 together. A's fresh local history/uncertainty checks passed 45 tests with eight PostgreSQL variants skipped because no local disposable test URL is configured. Both offline scripts passed and their saved JSON reloaded with the expected outcomes.

The merged [history contract](HISTORY_CONTRACT.md) documents private history, assumptions, stable ordering and deletion beyond the displayed 30. The [uncertainty contract](UNCERTAINTY_CONTRACT.md) documents existing bounded semantics and limits without changing schemas. Earlier [integration](handoffs/dev-a/integration-validation.md), [history](handoffs/dev-a/history-contracts.md) and [uncertainty](handoffs/dev-a/uncertainty-limits.md) handoffs retain their original checks. A's current task adds a delivery record, not a history UI or advanced verification feature.

## Run/check

Use Python3.12, Node22.23.2/npm10.9.8. Install backend with backend/requirements.txt constrained by backend/requirements.lock; frontend with npm ci. After bootstrap merges, activate the Python environment and run python scripts/install_hooks.py in each clone. Existing custom hooks are preserved; inspect/chaining is needed if core.hooksPath is configured. Windows local Python may require .venv/Scripts/python.exe; macOS/Linux .venv/bin/python.

Run python scripts/dev.py for the local stack. Do not duplicate running ports or run frontend dev/build/E2E against the same .next directory concurrently. Lane browser tests use distinct E2E_API_PORT/E2E_WEB_PORT and their own checkout. Full checks: backend pytest including PostgreSQL in CI, Ruff, OpenAPI/types drift, frontend typecheck/lint/build, browser flows, and Linux/Windows/macOS clean installs.

## Remaining limits

The historical PR8 queue failures are resolved; PR17's historical ancestry-gate failure remains recorded in the integration handoff. B's [merged task 5 handoff](handoffs/dev-b/demo-rehearsal.md) now records a 180.02-second automated operator rehearsal, local fallback/outage checks and focused desktop/mobile sign-off. A's PR21 review found no blockers and independently passed 11 browser tests. Human spoken delivery remains unmeasured, and no global feature freeze is declared. The recorded demo baseline can be presented independently of B's active history follow-up; a later build including history needs its own merged validation.

Hosted NVIDIA evidence/OCR, audio, Tiger Data, cloud storage and deployment remain live-unverified. The limited historical Brev native-text results above do not establish them. Further live validation requires configured server-side credentials and explicit processing consent. No billing/provisioning or public real-data release is authorized by this increment. Keep provider failures visible and source/session deletion semantics intact.

The private repository's current plan cannot require checks before a GitHub merge; hooks/CI reduce accidental conflicts but A must follow the review/green-check rule. No workflow guarantees freedom from semantic conflicts. No force-push, discarded changes, public visibility change or account upgrade is needed.

Keep the selected demo checkpoint stable while B completes the explicitly assigned history UI. Its [review criteria](DELIVERY_CHECKPOINT.md#acceptance-for-b-task-6s-history-pr) cover read-only behavior, identity/revision labels, saved proof/assumptions, privacy and stale responses. Richer bounded controls and robust synthesis/correlations/expense uncertainty remain deferred; A stops after this readiness task and consults the user before new work.
