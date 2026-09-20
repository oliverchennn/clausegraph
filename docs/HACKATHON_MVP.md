# Hackathon MVP priorities

## Current product

ClauseGraph connects source clause -> reviewed rule -> dependency -> permitted action -> integer-cent cash consequence. The existing baseline includes source review, nominal CP-SAT planning, selected-action decision traces, nonmutating side-by-side previews and bounded fixed-plan verification. Preserve those workflows; do not rebuild them as proposed features.

Synthetic acceptance values remain: baseline minimum/end -40000/50000 cents; approved shift5000/50000; denied shift-40000/50000; cancellation alone-82000/8000. Deferral is timing, not savings. Verification is exhaustive over declared bounds, not a probability or an unbounded guarantee. SAFE requires complete resolved coverage; a concrete counterexample proves UNSAFE; incomplete checks otherwise produce UNKNOWN. Future debt remains visible.

## Required increment: review guidance and demo polish

This is a split backlog: A owns backend/integration, B owns frontend, and C contributes optional small reviews and cleanup. The backend queue, frontend guidance/validation (through PR8) and hosted NVIDIA/optional Brev setup (PR9) are merged. Demo polish, rehearsal and any further implementation require their own assignments; do not execute the entire roadmap automatically. C adds a second look after the relevant A/B work is merged; C's tasks are never a dependency for A/B delivery or feature freeze.

Follow the three-developer coordination rules and ordered A/B assignments in [WORKSTREAMS.md](WORKSTREAMS.md). C's bounded proofreading, bug reproduction and UI inspection tasks are in [DEV_C.md](DEV_C.md); UI corrections require an explicit assignment and B's release of exact files. No broad refactor, new integration, contract work or mandatory review is assigned to C. Queue priorities remain essential obligations and missing obligation facts, blockers on candidate actions, other pending review. Ranking never promises a dollar benefit. Source support, human review, conditions and third-party approval remain distinct.

Acceptance: select a queue item -> inspect exact evidence -> save a supported correction/review -> see the recalculated plan and refreshed queue. Missing sources and denied/pending approvals stay honest. Stale session/revision responses are discarded. No queue task grants approval or sends a request. Empty queue does not mean financial safety.

Polish loading/errors/empty states and keyboard/mobile access. Rehearse the existing three-minute synthetic story with a local fallback. Validate live extraction separately using synthetic native/scanned documents, configured server-side credentials and explicit external-processing consent; record failures and limits as well as successes. A provider smoke is connectivity evidence, not extraction accuracy.

## Freeze and ordered follow-ups

Freeze after review guidance, demo polish and integrated checks. Only demo-blocking fixes enter before presentation. Later: (1) read-only history with revision/assumption labels and deletion semantics, (2) amount ranges/multiple uncertainty UI using existing bounded API, (3) a separate specification for robust synthesis, correlations or uncertain expense timing. History and richer controls are not in the required increment.

Defer bank aggregation, automated payments/cancellations/applications/messages, broad benefits discovery, generalized recurrence, new providers and infrastructure rewrites. Public real-data deployment needs separate privacy/recovery/operational work. No paid provisioning or provider-accuracy claims from offline fixtures.

Current delivery/checks are in [RESUME.md](RESUME.md); [verification semantics](handoffs/verification.md) and [integration history](handoffs/integration.md) are historical evidence. Shared docs are A-owned; each agent records its own task handoff.
