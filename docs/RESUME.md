# ClauseGraph current checkpoint

## Three-developer checkpoint: optional review and cleanup

Developer A owns backend/integration; Developer B owns frontend; Developer C is a separate part-time contributor for small, optional proofreading, bug reproduction and UI cleanup. A/B never wait for C's review, fixes or availability. This task changes documentation only and does not implement any C task or take over existing A/B work.

Fetched main for this task is `bd143a3`. PR5–PR7, B's [review validation PR8](https://github.com/vzhu08/clausegraph/pull/8), A's [NVIDIA/Brev PR9](https://github.com/vzhu08/clausegraph/pull/9) and [task synchronization PR10](https://github.com/vzhu08/clausegraph/pull/10) are merged. Their handoffs are historical records; retain the old branches and start new tasks from fetched main. Current documentation branch: `codex/dev-a/third-developer`; [task handoff](handoffs/dev-a/third-developer.md). Existing unmerged work, including the locally observed A brev-json-output task, is preserved and not reassigned here.

Read [WORKSTREAMS.md](WORKSTREAMS.md) for current ownership and [DEV_C.md](DEV_C.md) for C's task menu, start gates, report format and copyable prompt. C can start C1 read-only proofreading now. C has no permanent file ownership: the existing checker still accepts only dev-a/dev-b lanes. A future C UI fix needs a committed A assignment, B's exact-path release after its prerequisite merges, and a `codex/dev-b/c-<task>` branch/handoff identifying C. That delegation starts only after these coordination docs merge. C yields if B needs the files; no new dev-c tooling is claimed.

[NVIDIA_BREV.md](NVIDIA_BREV.md) explains hosted API keys, credits and optional private text inference. Hosted mode remains the browser default. The Brev backend/CLI consent contract is merged; its UI remains B's optional separately assigned follow-up. Live provider operation is not established by the setup or these docs. History, richer verification, advanced verification and feature-freeze rehearsal remain separate assignments.

## Existing baseline

Source/evidence/condition review, nominal planning, source-to-cash decision traces, nonmutating scenario previews and bounded fixed-plan verification are already implemented. Original synthetic values remain baseline-40000/50000 cents, approved shift5000/50000, denied shift-40000/50000, cancellation alone-82000/8000. No money is computed by language models or React. See [verification semantics](handoffs/verification.md), [integration history](handoffs/integration.md), [architecture](ARCHITECTURE.md) and [demo](DEMO.md).

Historical task checks: [B's PR8 handoff](handoffs/dev-b/review-guidance-finish.md) records typecheck/lint/build and 11 passing real-API browser tests; [A's PR9 handoff](handoffs/dev-a/nvidia-brev.md) records 282 backend tests with 1 local PostgreSQL skip and its earlier browser failures. The two queue failures were addressed in PR8. These records are not a fresh combined test run for this Markdown-only task, which reruns no application checks. The documentation handoff records its own validation.

## Run/check

Use Python3.12, Node22.23.2/npm10.9.8. Install backend with backend/requirements.txt constrained by backend/requirements.lock; frontend with npm ci. After bootstrap merges, activate the Python environment and run python scripts/install_hooks.py in each clone. Existing custom hooks are preserved; inspect/chaining is needed if core.hooksPath is configured. Windows local Python may require .venv/Scripts/python.exe; macOS/Linux .venv/bin/python.

Run python scripts/dev.py for the local stack. Do not duplicate running ports or run frontend dev/build/E2E against the same .next directory concurrently. Lane browser tests use distinct E2E_API_PORT/E2E_WEB_PORT and their own checkout. Full checks: backend pytest including PostgreSQL in CI, Ruff, OpenAPI/types drift, frontend typecheck/lint/build, browser flows, and Linux/Windows/macOS clean installs.

## Remaining limits

The review-queue failures from historical main `4e2725a` / [run35476332612](https://github.com/vzhu08/clausegraph/actions/runs/35476332612) are not outstanding assignments: PR8 resolved them and recorded all 11 browser tests passing. C should report a current regression only if it reproduces on its named snapshot. A/B still own required integration validation and rehearsal; C's second look is optional.

Live NVIDIA extraction/OCR, audio, cloud storage and deployment are not established by offline fixture tests. Synthetic live validation needs configured server-side credentials and explicit processing consent. No billing/provisioning or public real-data release is authorized by this increment. Keep provider failures visible and source/session deletion semantics intact.

The private repository's current plan cannot require checks before a GitHub merge; hooks/CI reduce accidental conflicts but A must follow the review/green-check rule. No workflow guarantees freedom from semantic conflicts. No force-push, discarded changes, public visibility change or account upgrade is needed.

Freeze after queue/demo delivery. Read-only history and richer bounded uncertainty controls follow later; robust synthesis/correlations/expense uncertainty need a separate specification.
