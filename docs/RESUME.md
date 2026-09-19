# ClauseGraph current checkpoint

## Two-developer increment

PR4 is merged on main as9858956. The next required delivery is review guidance plus demo polish, following [WORKSTREAMS.md](WORKSTREAMS.md). The workflow bootstrap introduces separate A/B file ownership, per-task handoffs, trusted-base CI checks, local pre-push checks and Node22.23.2/npm10.9.8. See [A workflow handoff](handoffs/dev-a/review-workflow.md) for current checks. Review queue implementation is the next contract-first task; do not claim it shipped from this bootstrap record.

A owns backend/contracts/dependencies/CI/shared docs and merges reviewed green PRs sequentially. B owns frontend/browser tests and its own task handoffs. Do not edit central docs from B. Every new task starts from freshly fetched origin/main on codex/dev-a/<task> or codex/dev-b/<task>; separate worktrees; retire squash-merged branches. Historical codex/integration and original engine/API/frontend worktrees are preserved, not active assignments.

## Existing baseline

Source/evidence/condition review, nominal planning, source-to-cash decision traces, nonmutating scenario previews and bounded fixed-plan verification are already implemented. Original synthetic values remain baseline-40000/50000 cents, approved shift5000/50000, denied shift-40000/50000, cancellation alone-82000/8000. No money is computed by language models or React. See [verification semantics](handoffs/verification.md), [integration history](handoffs/integration.md), [architecture](ARCHITECTURE.md) and [demo](DEMO.md).

The previously delivered merge passed206 backend tests with1 local PostgreSQL skip and5 real-API browser tests; remote Linux CI also passed. Those are historical checks, not results for new unmerged work. Task handoffs record exact new results; the final delivery will consolidate them here.

## Run/check

Use Python3.12, Node22.23.2/npm10.9.8. Install backend with backend/requirements.txt constrained by backend/requirements.lock; frontend with npm ci. After bootstrap merges, activate the Python environment and run python scripts/install_hooks.py in each clone. Existing custom hooks are preserved; inspect/chaining is needed if core.hooksPath is configured. Windows local Python may require .venv/Scripts/python.exe; macOS/Linux .venv/bin/python.

Run python scripts/dev.py for the local stack. Do not duplicate running ports or run frontend dev/build/E2E against the same .next directory concurrently. Lane browser tests use distinct E2E_API_PORT/E2E_WEB_PORT and their own checkout. Full checks: backend pytest including PostgreSQL in CI, Ruff, OpenAPI/types drift, frontend typecheck/lint/build, browser flows, and Linux/Windows/macOS clean installs.

## Remaining limits

Live NVIDIA extraction/OCR, audio, cloud storage and deployment are not established by offline fixture tests. Synthetic live validation needs configured server-side credentials and explicit processing consent. No billing/provisioning or public real-data release is authorized by this increment. Keep provider failures visible and source/session deletion semantics intact.

The private repository's current plan cannot require checks before a GitHub merge; hooks/CI reduce accidental conflicts but A must follow the review/green-check rule. No workflow guarantees freedom from semantic conflicts. No force-push, discarded changes, public visibility change or account upgrade is needed.

Freeze after queue/demo delivery. Read-only history and richer bounded uncertainty controls follow later; robust synthesis/correlations/expense uncertainty need a separate specification.
