# ClauseGraph current checkpoint

## Merged application checkpoint: 2026-09-20 UTC

Developer A owns backend/integration; Developer B owns frontend; Developer C contributes optional proofreading, bug reproduction and UI cleanup. A/B never wait for C's availability. Integration validation is merged in PR18 and history/deletion validation in PR19. The user assigned A the next bounded task: validate the existing uncertainty limits, and confirmed B is actively working on task 5's demo in a separate session.

Current merged base: `7088b812c1da4169b1ad4b4d668bf2536e68e43d` ([PR19](https://github.com/oliverchennn/clausegraph/pull/19)). Workflow, review queue and B's [PR8](https://github.com/vzhu08/clausegraph/pull/8) guidance are merged, as are NVIDIA/Brev support and source-reference fixes (PR9/PR11/PR13), the live retest record (PR15), and C's UI corrections and demo wording (PR17/PR16). Duplicate PR14 was closed because PR13 already contained its implementation. Historical branches and dirty worktrees are preserved. Current A task: `codex/dev-a/uncertainty-limits`; [exact validation and limits](handoffs/dev-a/uncertainty-limits.md), [uncertainty contract](UNCERTAINTY_CONTRACT.md). The local app for user testing remains in its separate checkout and was not restarted by this task.

Read [WORKSTREAMS.md](WORKSTREAMS.md) for current ownership and [DEV_C.md](DEV_C.md) for C's task menu and release protocol. C's merged handoffs record the owner's explicit exceptions for PR16/PR17; those patches do not create a standing release or permanent ownership. Future C work still follows the documented assignment rules. Other contributors' handoffs remain historical and unchanged.

[NVIDIA_BREV.md](NVIDIA_BREV.md) explains hosted and private text inference. Hosted NVIDIA remains the browser default because Brev-specific browser consent is still unimplemented. The [historical Brev retest](handoffs/dev-a/brev-live-retest.md) exercised five synthetic native-text clauses on the user's existing GPU: exact fields passed 3/5 and then 5/5 with unchanged code; citations and withholding of unreviewed execution passed 5/5 in both runs. This confirms working inference with observed variability, not general accuracy, OCR, or a full live browser workflow. No provider call was made in the current integration task.

## Existing baseline

Source/evidence/condition review, nominal planning, source-to-cash decision traces, nonmutating scenario previews and bounded fixed-plan verification are already implemented. Original synthetic values remain baseline-40000/50000 cents, approved shift5000/50000, denied shift-40000/50000, cancellation alone-82000/8000. No money is computed by language models or React. See [verification semantics](handoffs/verification.md), [integration history](handoffs/integration.md), [architecture](ARCHITECTURE.md) and [demo](DEMO.md).

PR18 integration validation: 298 backend tests passed, with one PostgreSQL test skipped because no local test URL was configured; all 11 real-API Chromium tests passed. Pinned-toolchain clean install, Ruff, dependency consistency, OpenAPI/TypeScript drift, frontend typecheck/lint/production build and both offline demonstration scripts passed. [PR18 CI](https://github.com/oliverchennn/clausegraph/actions/runs/35483758987) passed application verification including PostgreSQL 17 and clean installs on Linux, Windows and macOS. See the [integration handoff](handoffs/dev-a/integration-validation.md) for commands and limits. B's PR8 and earlier A/C results remain historical evidence; they are not new results for the history task.

[PR19 CI](https://github.com/oliverchennn/clausegraph/actions/runs/35485152723) passed 315 backend tests including PostgreSQL 17 and 11 real-API browser tests, plus generated-contract, frontend and platform checks. Its [history contract](HISTORY_CONTRACT.md) documents private history, assumptions, stable ordering and deletion beyond the displayed 30. A's current uncertainty task adds synthetic validation and documentation; no runtime or public schema defect was found in its checked scope.

## Run/check

Use Python3.12, Node22.23.2/npm10.9.8. Install backend with backend/requirements.txt constrained by backend/requirements.lock; frontend with npm ci. After bootstrap merges, activate the Python environment and run python scripts/install_hooks.py in each clone. Existing custom hooks are preserved; inspect/chaining is needed if core.hooksPath is configured. Windows local Python may require .venv/Scripts/python.exe; macOS/Linux .venv/bin/python.

Run python scripts/dev.py for the local stack. Do not duplicate running ports or run frontend dev/build/E2E against the same .next directory concurrently. Lane browser tests use distinct E2E_API_PORT/E2E_WEB_PORT and their own checkout. Full checks: backend pytest including PostgreSQL in CI, Ruff, OpenAPI/types drift, frontend typecheck/lint/build, browser flows, and Linux/Windows/macOS clean installs.

## Remaining limits

The historical PR8 queue failures are resolved. C's PR17 application verification and all three platform clean installs passed, but its PR run failed the current-main ancestry gate. That historical gate failure remains recorded in the integration handoff. B's timed three-minute rehearsal, local fallback rehearsal and final desktop/mobile visual sign-off have no published completion record; automated browser coverage is not a timed rehearsal. Feature freeze is not declared.

Hosted NVIDIA evidence/OCR, audio, Tiger Data, cloud storage and deployment remain live-unverified. The limited historical Brev native-text results above do not establish them. Further live validation requires configured server-side credentials and explicit processing consent. No billing/provisioning or public real-data release is authorized by this increment. Keep provider failures visible and source/session deletion semantics intact.

The private repository's current plan cannot require checks before a GitHub merge; hooks/CI reduce accidental conflicts but A must follow the review/green-check rule. No workflow guarantees freedom from semantic conflicts. No force-push, discarded changes, public visibility change or account upgrade is needed.

Freeze after queue/demo delivery. A's uncertainty validation covers inclusive ranges, combined dimensions, nominal assumptions, invalid requests, case/time cutoffs and proof labels using the existing API. History UI and richer bounded uncertainty controls remain separately assigned follow-ups after B's current demo work; robust synthesis/correlations/expense uncertainty need a separate specification.
