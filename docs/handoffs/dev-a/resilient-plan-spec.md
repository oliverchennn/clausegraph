# A handoff: resilient-plan-spec

## Assignment and starting point

- Contributor: A; branch `codex/dev-a/resilient-plan-spec`; isolated checkout `.worktrees/dev-a-resilient-plan-spec`.
- Starting/fetched main: `2e7653718ff7fac27158789deff965775da408a1` (PR35), 2026-09-20. Root main was clean; existing worktrees and changes were preserved.
- User request: finish all A tasks. Continue eligible A work without restarting delivered tasks; retain lane ownership, ordered implementation and independent B review.
- Allowed files: this handoff, `docs/RESILIENT_PLAN_SPEC.md`, `docs/WORKSTREAMS.md`, `docs/RESUME.md`, `docs/HACKATHON_ASSIGNMENTS.md`, `docs/HACKATHON_MVP.md`, `docs/DELIVERY_CHECKPOINT.md`, `docs/DEMO.md`.
- Merged prerequisites: PR33 explorer contract `dd77765f8fb5bd6b4e89b5472c3f860a0dad5860`; PR34 cash-gap UI `c00d39573464d916ea3712c42a766df0a791fb0a`; PR37 C10 kit `c82319c9b25bd2f2662290cada614df76e4b38d3`; PR36 C11 demo/tests `8f6c627e9d825a07630658d6d906e2772690a6b0`; PR35 controls `2e7653718ff7fac27158789deff965775da408a1`.
- Assignment permits specifying the next stage while the current UI finishes. C12 is still required for stage 2 acceptance; the released `FailureViewSlot` is empty. Separate B design review and merge are required before synthesis implementation. No frontend or runtime changes are assigned here.

## Acceptance and validation plan

Specify the finite schedule domain, deterministic objective/order, common ledger and independent verifier, approval/evidence semantics, budget/proof states, request identity, nonmutating preview and atomic explicit adoption. Define a separate synthetic success case without changing the original demo. Specify executable engine/API/oracle/privacy tests for the subsequent engine task and exact A/B/C interfaces.

Consolidate merged PRs and exact main CI evidence centrally; retain historical handoffs and failed live/human status. Validate local Markdown links, scope/ownership/conflict checks, whitespace, and the proposed numeric example with deterministic code. The docs-only task does not require redundant application test runs; its PR still receives normal full CI and B review.

## Work and results

Completed the separate `RESILIENT_PLAN_SPEC.md` design: first-feasible deterministic fixed-schedule search, nominal-plus-declared-case scope, recorded-approval eligibility, shared accounting/independent verification, global budgets and exact counts, proof states, nonmutating preview, atomic revalidated adoption, plan/history provenance and a separately labeled synthetic success example. It names the proposed schema/API changes and A/B/C checks and handoffs; these are not implemented interfaces.

Consolidated PR33/34/35/36/37 delivery, duplicate PR38 closure and C12's actual empty seam in the allowed central docs. Preserved contributor handoffs, original demo fixtures, branch history, live failure records and unmeasured human rehearsal. Updated the central demo to use the merged cash-gap UI under unchanged bounds.

Validation on 2026-09-20:

- Re-fetched origin before creating the task; no open PRs at task start or the review recheck. Main remained `2e7653718ff7fac27158789deff965775da408a1`.
- Read exact merged-main CI [35497142151](https://github.com/oliverchennn/clausegraph/actions/runs/35497142151): 390 backend passes, two existing warnings, 29.34 seconds; 46 real-API browser passes, 2.3 minutes; Ruff, generated contract drift, frontend checks and all three clean-install platforms passed. These are main's application results, not local tests of an unimplemented synthesis engine.
- Python 3.12 inline relative-link check: **83 links passed across all eight task documents**. Corrected the C11 source link to `frontend/demo/cash-gap-demo.md`.
- Independent integer-cent arithmetic, three schedules by three income dates: omission always -5000/5000; early shift 5000/5000 nominal and -5000/5000 delayed; late shift always 4900/4900. This validates the proposed table, not source extraction, a new fixture loader or synthesis implementation.
- `git diff --check`: passed. Reviewed allowed paths and source claims against the merged implementation, including C12's `FailureViewSlot` returning null.
- Root Python 3.12 environment: `python scripts/install_hooks.py` confirmed the existing managed hook; no custom hook was overwritten. The current-main workflow check passed before commit; the final commit is also checked by the normal pre-push hook and PR CI.

Published [PR39](https://github.com/oliverchennn/clausegraph/pull/39). The committed-change workflow check and managed pre-push hook both passed on initial head `89810b064f8c6c0e5321d014e427fae237e0620a`. Final design inspection added explicit backend-computed comparison cost fields and the existing numeric magnitude limits, so B need not invent money calculations. Normal PR CI validates the final head; B's review is still pending.

No runtime change, dependency update, provider call, deployment or user-service restart occurred. Full application CI and independent B design review remain normal PR requirements; no self-review is substituted for B.

## Remaining gates

B design review is pending. C12 is not delivered. The engine task and subsequent consequence contract remain ordered work; this design does not claim either is implemented. Optional #5/#6 are not activated.
