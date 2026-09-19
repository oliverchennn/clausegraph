# ClauseGraph current checkpoint

## Two-developer checkpoint: NVIDIA/Brev setup

Developer A is this agent; Developer B is the friend's agent in a separate session/clone. The roadmap assigns future work to those two agents; it does not authorize this session to implement every task. The user separately requested hosted NVIDIA configuration and optional Brev preparation. A handles this backend/config/docs task only; no GPU provisioning, live processing or B implementation is included.

Workflow PR5, backend [PR6](https://github.com/vzhu08/clausegraph/pull/6) and frontend snapshot [PR7](https://github.com/vzhu08/clausegraph/pull/7) are merged; this task starts at main4e2725a. Their task handoffs are historical records. Retire those squash-merged branches. New A branch: codex/dev-a/nvidia-brev; [current handoff](handoffs/dev-a/nvidia-brev.md). B starts its own fresh demo-polish task from main to validate and refine the UI. Previous unrun checks are not implied passing merely by merge.

Read [WORKSTREAMS.md](WORKSTREAMS.md) for ownership and the friend's startup sequence. [NVIDIA_BREV.md](NVIDIA_BREV.md) explains hosted API keys, credits and optional private text inference. Hosted mode remains the browser default. Brev backend/CLI support requires named consent; its UI is B's optional follow-up after A's contract merges. The local NVIDIA key is present but has not been validated. History, richer verification, advanced verification and feature-freeze rehearsal remain future assignments.

## Existing baseline

Source/evidence/condition review, nominal planning, source-to-cash decision traces, nonmutating scenario previews and bounded fixed-plan verification are already implemented. Original synthetic values remain baseline-40000/50000 cents, approved shift5000/50000, denied shift-40000/50000, cancellation alone-82000/8000. No money is computed by language models or React. See [verification semantics](handoffs/verification.md), [integration history](handoffs/integration.md), [architecture](ARCHITECTURE.md) and [demo](DEMO.md).

The previously delivered merge passed206 backend tests with1 local PostgreSQL skip and5 real-API browser tests; remote Linux CI also passed. Those are historical checks, not results for new unmerged work. Task handoffs record exact new results; the final delivery will consolidate them here.

## Run/check

Use Python3.12, Node22.23.2/npm10.9.8. Install backend with backend/requirements.txt constrained by backend/requirements.lock; frontend with npm ci. After bootstrap merges, activate the Python environment and run python scripts/install_hooks.py in each clone. Existing custom hooks are preserved; inspect/chaining is needed if core.hooksPath is configured. Windows local Python may require .venv/Scripts/python.exe; macOS/Linux .venv/bin/python.

Run python scripts/dev.py for the local stack. Do not duplicate running ports or run frontend dev/build/E2E against the same .next directory concurrently. Lane browser tests use distinct E2E_API_PORT/E2E_WEB_PORT and their own checkout. Full checks: backend pytest including PostgreSQL in CI, Ruff, OpenAPI/types drift, frontend typecheck/lint/build, browser flows, and Linux/Windows/macOS clean installs.

## Remaining limits

Starting main4e2725a has two failing review-queue browser cases in [run35476332612](https://github.com/vzhu08/clausegraph/actions/runs/35476332612): review/source completion and queue error/retry/keyboard state. B's next fresh task resolves and verifies those. A's NVIDIA/Brev adapter tests do not establish frontend acceptance.

Live NVIDIA extraction/OCR, audio, cloud storage and deployment are not established by offline fixture tests. Synthetic live validation needs configured server-side credentials and explicit processing consent. No billing/provisioning or public real-data release is authorized by this increment. Keep provider failures visible and source/session deletion semantics intact.

The private repository's current plan cannot require checks before a GitHub merge; hooks/CI reduce accidental conflicts but A must follow the review/green-check rule. No workflow guarantees freedom from semantic conflicts. No force-push, discarded changes, public visibility change or account upgrade is needed.

Freeze after queue/demo delivery. Read-only history and richer bounded uncertainty controls follow later; robust synthesis/correlations/expense uncertainty need a separate specification.
