# Resilient fixed-plan synthesis: v1 design

Status: **implemented and merged: engine/API/fixture PR41 (`c420609`), comparison/adoption PR42 (`b53cb5c`), C13 presenter segment and regression PR43 (`8d16764`)**. Design PR39 merged at `96b220e`; C12/stage 2 PR40 merged at `f85aa08`. PR43's PR CI passed 463 backend and 59 browser tests. The user replaced separate B review with recorded same-agent orchestrator review for this completion run; role references below describe original interface responsibilities. See the [design handoff](handoffs/dev-a/resilient-plan-spec.md) and [ordered assignments](HACKATHON_ASSIGNMENTS.md). Human spoken rehearsal and successful live extraction remain separately unverified.

## Product contract and objective

Find one permitted action/date schedule whose daily closing balance stays nonnegative under the saved nominal assumptions **and every assignment in the user's unchanged finite uncertainty domain**. Every assignment uses exactly the same selected actions and execution dates. The search may omit actions or choose different permitted dates; it may not add cash, alter evidence, record an approval, narrow uncertainty or execute anything externally.

V1 is a bounded feasibility search. Its objective is to find the first verified feasible schedule in the deterministic order below. It does **not** maximize worst-case cash or claim globally minimum fees/burden. Display nominal and worst-case cash, total action fees and burden so the user can compare alternatives. A found candidate is not advertised as the best plan. Nominal CP-SAT optimization and existing fixed-plan verification retain their separate APIs and guarantees.

Scope: the existing action/effect types and up to eight independent date, integer-cent amount and approval dimensions from [UNCERTAINTY_EXPLORER.md](UNCERTAINTY_EXPLORER.md). Bounds are inclusive; every cent counts. No correlations, uncertain expenses, probabilities, adaptive policies, intraday settlement or per-outcome reoptimization. Safety covers only the displayed horizon and declared model. Retain obligations after the horizon.

## Inputs and admissible schedules

`SynthesisRequest` identifies the active saved `plan_id` and input `revision`, contains the same uncertainty dimension union/rationales as `VerificationRequest`, and adds the budgets below. It does not accept a replacement scenario, opening balance, approval overrides or client-computed money. Use the active plan's stored `PlanRequest` as the nominal assumptions, including cash/income/horizon assumptions and action constraints; return them beside the uncertainty assumptions.

Reject malformed/unknown/duplicate targets and IDs with HTTP 422, using the existing uncertainty target rules. Reject `include_conditional=true` or nonempty `approval_overrides` in the saved nominal assumptions with a specific unsupported-input explanation. The user must save a plan based on recorded approvals before using v1 synthesis. This deliberately narrower confirmed-plan domain is visible in the UI; it is not an implicit favorable decision. An infeasible nominal plan can still be a search starting point if its inputs are resolved.

Construct the candidate domain on isolated copies of the effective nominal scenario:

1. Sort action IDs lexicographically. Each action has omission first, then every ISO execution date in ascending order in the intersection of its inclusive window and the half-open planning horizon.
2. Apply explicit `action_dates` as a date restriction, not forced selection, matching nominal controls. Forced actions cannot be omitted. Excluded actions can only be omitted. Reject unknown control IDs, duplicate forced/excluded IDs, overlapping force/exclude lists, and invalid explicit dates with 422 instead of silently relaxing controls.
3. Filter an action/date only when a shared deterministic gate proves it unavailable in the recorded nominal model: evidence/review/conditions/recorded approval, essential-service protection, impossible effect or date. Keep the exclusion reason. An unavailable forced action yields an empty admissible domain; missing or unresolved required ledger facts yield an inconclusive result, not a no-solution certificate.
4. Stream the Cartesian product with mixed-radix indices; do not materialize exponentially many schedules. The last sorted action varies fastest. Use the canonical action/date tuple as schedule identity, excluding generated IDs, runtime and timestamps. The saved nominal schedule has no special priority.
5. Enforce action dependencies (including same-day topological order), exclusions, writer collisions and obligation identity with the existing deterministic code. A structurally invalid tuple is refuted with its reason. Unresolved facts are never treated as satisfied.

Approval uncertainty still changes isolated copies in each hypothetical check. It never expands the candidate domain beyond actions permitted by **recorded** approvals. A currently approved action tested with denied/pending outcomes must pass those outcomes or be omitted. A singleton hypothetical `approved` outcome cannot authorize an action that is pending in the workspace. Source support, extraction confidence, review, conditions and third-party decisions remain separate.

The nominal case is an additional required case even when it lies outside the supplied uncertainty domain. Therefore the precise no-solution claim is restricted to the recorded-permission candidate domain, saved nominal assumptions, action constraints, displayed horizon and supplied uncertainty domain. It makes no statement about future approvals, other actions, extra cash or adaptive policies.

## Shared accounting and independent verification

Place search orchestration in `backend/clausegraph/synthesis.py`. Reuse `engine._effective_scenario`, the gate/effect/ledger helpers, and `verification.check_fixed_plan`; do not implement another money calculator. A small extraction of common fixed-schedule rendering from `optimize` is acceptable, provided nominal behavior and regression values remain unchanged.

For each structurally admissible candidate:

- Check the concrete recorded nominal schedule with `check_fixed_plan`. A conclusive permission/accounting/cash failure refutes the candidate. An unresolved result cannot prove rejection or safety.
- Build a transient canonical plan from those exact selected actions, their topological order, backend simulations and decision traces. Invoke the existing `verify_plan` against the original dimensions and a remaining time/case allowance. Never call `optimize` for each assignment.
- A `SAFE` result with complete resolved coverage independently validates the candidate. A concrete `UNSAFE` counterexample refutes it even if coverage stopped. `UNKNOWN` leaves it unresolved. Do not turn incomplete observed cash into a proven worst case.
- Return a candidate only after nominal success and complete `SAFE` verification. Keep the independent verification object, actual fixed actions, evidence-linked traces and retained future obligations in the response.

"Independent" here means that search proposes a schedule and the existing fixed-plan verifier checks it; it is not a claim of an independently implemented financial semantics. The engine tests additionally use a small arithmetic/brute-force oracle independent of these helpers.

## Budgets, counts and proof states

Implemented defaults/hard maximums: `max_candidates=1000/10000`, `max_case_checks=10000/10000`, `time_limit_seconds=5/10`. The case budget is shared across the entire request and counts each nominal `check_fixed_plan` plus every assignment checked by `verify_plan`. The time limit covers domain preparation, rendering and verification as well as search. Check the monotonic deadline between bounded units and pass only the remaining duration into verification. This is a cooperative deadline, not a promise to interrupt a single Python operation at an exact millisecond.

Reuse the nominal planner's limits of 100 actions and 10000 action/date options, and its safe input magnitude checks (aggregate ledger/effect money plus fees and aggregate burden each at most 10^12). Exceeding a work/representation limit produces `INCONCLUSIVE`/`MODEL_LIMIT`, never proof of impossibility. Do not pre-expand large cent/date products. Domain construction must account for its work and check the deadline. No sampling or monotonic/endpoint shortcut is included in v1.

Return `total_candidate_tuples` and `uncertainty_cases_per_candidate` as decimal strings so JavaScript can display exact products. The tuple count is null if bounded domain construction stops before it is known. A shared empty-schedule nominal precheck counts toward the case budget and is reused when enumerating that tuple. Return bounded actual work counters as integers: `visited_candidate_tuples`, `refuted_candidate_tuples`, `unresolved_candidate_tuples`, `nominal_checks`, `uncertainty_checks`. Explain that the theoretical product includes structurally invalid combinations. A refuted tuple needs only one conclusive failure; proving no solution does not require simulating every assignment of an already refuted tuple.

| Result status | Termination | Required evidence and permitted statement |
|---|---|---|
| `FOUND` | `VERIFIED_CANDIDATE` | One nominally permitted/safe schedule and independent `SAFE`, complete verification of all supplied cases. Search can stop immediately; no optimality claim. |
| `NO_SOLUTION` | `EXHAUSTED` | Entire declared finite candidate domain conclusively refuted, no unresolved tuples or ledger facts. State that no schedule in this specific admissible domain survives the nominal case plus all declared cases. |
| `INCONCLUSIVE` | `CANDIDATE_LIMIT`, `CASE_LIMIT`, `TIME_LIMIT`, `MODEL_LIMIT`, or `UNRESOLVED` | No verified candidate returned; work cutoff or unresolved facts prevent the no-solution claim. Visiting every tuple is insufficient if any remains unresolved. |

`candidate` and `verification` are present only for `FOUND`. Include a clearly labeled example refutation for other statuses, when available; one witness against one schedule is not a certificate against all schedules. Return warnings, active source identity, nominal assumptions, exact uncertainty request, domain restrictions, actual counters/runtime and `search_exhausted`. A found candidate remains valid even when other schedules were not examined; do not equate search exhaustion with verification coverage. There is no synthesis `OPTIMAL` label.

Return backend-computed `nominal_costs` and, only when found, `candidate_costs`, each with integer `total_action_fees_cents` and `total_action_burden`. Totals are null when domain preparation fails before a trustworthy bounded comparison is available. Sum the actual selected action metadata, not event balances or deferred principal; these are comparison values, not search objectives. B formats these values and never computes financial totals from effects. The candidate's nominal simulation and complete verified worst case supply the cash comparison; the saved nominal plan's own uncertainty result must be labeled separately and never inferred from the candidate's proof.

Invalid request/unsupported saved assumptions return 422. Stale input revision or changed active plan/incomplete source processing returns 409. Missing/deleted private sessions follow existing authentication/not-found behavior. An unexpected internal error is an error response, not `NO_SOLUTION` or a partial candidate.

## API, plan representation and adoption

Implemented operations:

| Operation | Request and result | Mutation |
|---|---|---|
| `POST /api/synthesis` | `SynthesisRequest` -> `SynthesisResult` | None: no active-plan replacement, revision change, new history entry or verification persistence. Recheck active plan ID/revision/session/source readiness after computation. |
| `POST /api/synthesis/adopt` | Original synthesis request, selected action/date tuple, preview fingerprint -> `SynthesisAdoptionResult` containing saved plan and saved verification | Explicit user action. Reconstruct and revalidate the exact tuple and all its assumptions; atomically replace active plan and persist its verification only on success. |

The response fingerprint is SHA-256 of canonical server-rendered content: source plan ID/revision, nominal assumptions, full uncertainty request/budgets, fixed action/date tuple, traces and money results. Exclude IDs/timestamps/runtime that naturally vary between checks. This binds the preview contents for comparison; it is **not** an authorization credential. Session authentication and fresh deterministic validation provide authorization. Adoption accepts no client ledger, approval decision, proof flag or balance.

An adoption request may carry a recomputed fingerprint; treat every request as untrusted and fully validate domain membership, nominal gates and all uncertainty cases. This intentionally avoids a new persistent candidate cache or trusting a prior proof. Even an independently constructed tuple can be accepted only if it meets exactly the displayed contract and its recomputed preview fingerprint. Revalidation cutoff/unknown returns 409 with a retry explanation and no writes. Do not rerun nominal optimization and save a different schedule.

Add a backwards-compatible default `generation_mode="nominal"` to `PlanResult`, with a `resilient` alternative and optional synthesis provenance (`source_plan_id`, fingerprint, uncertainty request). Add a distinct `solver_status="FIXED_VERIFIED"` for a constructed resilient plan. It has `objective_proven=false` and `solver_wall_time_seconds=0` because no CP-SAT solve produced it; actual synthesis and verification runtimes belong to their own result fields. Its `state="confirmed"` requires the successful recorded nominal gates and nominal cash check. The bounded `SAFE` evidence remains a separate verification, not a new meaning for confirmed. B must adapt current-plan, preview and history solver labels when consuming these additions.

The preview includes this complete typed `PlanResult` and independent `VerificationResult`; preview IDs are transient. Adoption creates a new saved plan ID and a verification referencing that new ID, with identical schedule/assumptions/financial output. Return both together. Original nominal plan/history remains available subject to existing retention and deletion rules. Input revision stays unchanged because adopting a plan does not alter evidence or intake; active plan ID changes and invalidates previous UI results.

Before adoption's write, acquire the same conditional row/write lock used by `Store.save_verification` on SQLite and PostgreSQL. Inside one transaction recheck session existence, input revision, active source plan ID and source readiness, then persist the plan, daily series and verification together. Refactor persistence helpers narrowly if needed; calling today's separate `mutate` and `save_verification` is not atomic enough. Concurrent same-revision plan replacement, source deletion, reset or session deletion must fail closed. A repeated adoption after successful replacement is stale; refresh rather than apply twice. Do not hold a database transaction throughout the bounded search.

No new table is required if existing JSON plan/history storage carries the added provenance and the existing verification tables hold the proof. Source/session deletion and demo reset must purge all corresponding plan/verification history and traces. Preserve source unavailability behavior, private-session isolation, server-side secrets and consent. Synthesis performs no model/provider requests.

## Separate synthetic success fixture

Preserve the original six sources and all their regression values, including the eight-date no-safe-schedule result. Add a separate clearly synthetic `fixtures/resilient/` corpus with reviewed exact evidence for these facts, plus its own loader. Do not edit the original approval clause to make that example succeed.

Use dates in September 2026, a seven-day horizon starting September 1, opening cash 5000 cents, one 10000-cent expense due September 2 and one 10000-cent projected income nominally due September 3. Two mutually exclusive, already-approved payment options can be executed only on September 1:

| Schedule | Effect and fee | Nominal minimum/end | Worst minimum/end for income September 3–5 inclusive |
|---|---|---:|---:|
| Omit both | Keep September 2 expense | -5000 / 5000 cents | -5000 / 5000 cents |
| `early-shift` | Same expense moved to September 3; zero fee | 5000 / 5000 cents | -5000 / 5000 cents |
| `late-shift` | Same expense moved to September 5; 100-cent fee on September 1 | 4900 / 4900 cents | 4900 / 4900 cents |

Nominal optimization selects `early-shift` because its nominal minimum is higher. It fails when income arrives September 4 or 5. The fixed `late-shift` schedule survives all three dates without narrowing bounds, adding cash, changing approval or duplicating the expense. The date/amount facts and approved fee must be supported by the new fixture evidence. The separate corpus/loader, arithmetic oracle and offline script now reproduce this table. API adoption is tested separately; browser comparison/adoption remains the next task.

For a real-API demo, extend `SessionCreate` with `demo_variant: "baseline" | "resilient"`, default `baseline`; a nonbaseline variant with `demo=false` is invalid. Store the variant on synthetic workspaces, and preserve it on demo reset. Existing sessions/default resets keep the original six-source behavior. B owns the explicit demo selector and its labeling. Never replace a user's existing session automatically. This API addition is part of the engine contract review, not an instruction to C to synthesize backend fixtures.

## Implementation split and checks

A's next fresh `resilient-plan-engine` task, **after the gates**, owns `backend/clausegraph/synthesis.py`, targeted shared engine/verification/schema/API/storage/demo changes, focused backend tests, `fixtures/resilient/`, generated OpenAPI/TypeScript, and its own handoff/central records. Record exact files and starting/prerequisite SHAs before implementation; no dependency or migration change is expected. Changes to this reviewed design require recorded B review of the changed guarantee.

B reviews these concrete decisions before implementation: first-feasible semantics/order, confirmed-input restriction, nominal-plus-uncertainty scope, status/counter presentation, `FIXED_VERIFIED`/provenance handling in current and historical plans, nonmutating search, revalidated atomic adoption and explicit separate synthetic selector. After A's engine/contracts merge, B owns requests/state/comparison/adoption, invalidating on session/revision/plan or any input change. Clear candidates on failure/401/409; discard delayed obsolete responses. Keep current nominal results and uncertainty bounds visible, with no auto-adopt.

C12 remains the stage 2 failure-view task through B's existing release. C13 follows merged A/B synthesis and owns its new presenter segment and real-API demonstration/tests. C14/C15 follow the ordered consequence and final-demo work. This design does not grant A ownership of those frontend deliverables.

Required engine acceptance:

- Independent small-domain exhaustive oracle: every returned tuple matches the constraints and all cases; `NO_SOLUTION` agrees with exhaustive refutation; deterministic ordering is stable, including forced/omitted actions and same-day dependencies.
- Separate synthetic fixture: nominal `early-shift` fails, `late-shift` passes unchanged bounds; unchanged original fixture still has its separate impossibility proof and original money values. Exact evidence/fee/debt identity is checked.
- Empty dimension list (one nominal uncertainty assignment), no actions, zero admissible candidates, invalid targets, huge products, final-budget-unit success, case/candidate/time limits, unresolved evidence and partially refuted domains. No cutoff/unknown becomes impossible; a found candidate never contains a partial SAFE claim.
- Pending/denied action and rule approval, singleton hypothetical approved outcomes, unresolved conditions, supersession, missing obligations, essential protection, duplicated/written debts, effect timing, fees and beyond-horizon obligations. No fabricated authorized cash trace.
- API nonmutation and no provider calls; 401/409/422; same-revision active-plan changes and stale responses; forged tuple/fingerprint/proof/money rejected or fully reconstructed and verified; no automatic adoption.
- Atomic adoption, unchanged tuple, new plan/proof identities, retained nominal history, JSON compatibility with old plans, correct `FIXED_VERIFIED` label, source/reset/session deletion and cross-session isolation. Run races and rollback/failure injection on SQLite and PostgreSQL.
- Existing nominal/verifier/cash-gap regressions, full backend/CI, generated contract drift and platform installs. B/C then validate actual comparison/adoption, keyboard/mobile, history and synthetic demo flows with the real local API.

Acceptance is a small complete workflow, not additional integrations. Optional document-change/review-impact work remains unactivated. Live extraction and human spoken rehearsal retain their separately recorded limits.
