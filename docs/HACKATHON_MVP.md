# Hackathon MVP priorities

## Current product

ClauseGraph connects source clause -> reviewed rule -> dependency -> permitted action -> integer-cent cash consequence. The existing baseline includes source review, nominal CP-SAT planning, selected-action decision traces, nonmutating side-by-side previews and bounded fixed-plan verification. Preserve those workflows; do not rebuild them as proposed features.

Synthetic acceptance values remain: baseline minimum/end -40000/50000 cents; approved shift5000/50000; denied shift-40000/50000; cancellation alone-82000/8000. Deferral is timing, not savings. Verification is exhaustive over declared bounds, not a probability or an unbounded guarantee. SAFE requires complete resolved coverage; a concrete counterexample proves UNSAFE; incomplete checks otherwise produce UNKNOWN. Future debt remains visible.

## Required increment: review guidance and demo polish

This is a split backlog: A is the user's agent, B the friend's independent agent. A finishes the current backend queue contract and stops. B takes over the draft UI, validates it and completes demo polish. Later rows require their own assigned task; do not execute the entire roadmap automatically.

Follow the ordered two-developer assignments in [WORKSTREAMS.md](WORKSTREAMS.md). Establish ownership/CI/pre-push/toolchain first, merge the read-only review queue backend contract, then ship the frontend guidance. Queue priorities: essential obligations and missing obligation facts, blockers on candidate actions, other pending review. Ranking never promises a dollar benefit. Source support, human review, conditions and third-party approval remain distinct.

Acceptance: select a queue item -> inspect exact evidence -> save a supported correction/review -> see the recalculated plan and refreshed queue. Missing sources and denied/pending approvals stay honest. Stale session/revision responses are discarded. No queue task grants approval or sends a request. Empty queue does not mean financial safety.

Polish loading/errors/empty states and keyboard/mobile access. Rehearse the existing three-minute synthetic story with a local fallback. Validate live extraction separately using synthetic native/scanned documents, configured server-side credentials and explicit external-processing consent; record failures and limits as well as successes. A provider smoke is connectivity evidence, not extraction accuracy.

## Freeze and ordered follow-ups

Freeze after review guidance, demo polish and integrated checks. Only demo-blocking fixes enter before presentation. Later: (1) read-only history with revision/assumption labels and deletion semantics, (2) amount ranges/multiple uncertainty UI using existing bounded API, (3) a separate specification for robust synthesis, correlations or uncertain expense timing. History and richer controls are not in the required increment.

Defer bank aggregation, automated payments/cancellations/applications/messages, broad benefits discovery, generalized recurrence, new providers and infrastructure rewrites. Public real-data deployment needs separate privacy/recovery/operational work. No paid provisioning or provider-accuracy claims from offline fixtures.

Current delivery/checks are in [RESUME.md](RESUME.md); [verification semantics](handoffs/verification.md) and [integration history](handoffs/integration.md) are historical evidence. Shared docs are A-owned; each agent records its own task handoff.
