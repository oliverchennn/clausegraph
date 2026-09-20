# Developer A: stage 1 cash-gap diagnostic contract

## Assignment

Stage 1, idea #2 from [HACKATHON_ASSIGNMENTS](../../HACKATHON_ASSIGNMENTS.md): generalize the bounded cash diagnostic in `scripts/verify_demo.py` into a private, nonmutating API workflow for the current saved fixed schedule and explicitly declared uncertainty. V1 is scoped to additional opening cash only. This is the contract half; `cash-gap-diagnostic-ui` is B's separate task and starts after this merges.

Branch: `codex/dev-a/cash-gap-diagnostic`. Worktree: `.worktrees/dev-a-cash-gap-diagnostic`.
Starting and required main commit: `f5f93bdd` (PR27), with stage 0 PR25 and PR28 merged.
Required contract changes: this task provides them; none consumed.

Allowed writes used: `backend/clausegraph/{schemas,api,cash_gap}.py`, `backend/tests/test_cash_gap*.py`, `docs/openapi.json`, `frontend/src/lib/api-types.ts` (A-owned generated types) and this handoff. No engine, verifier, storage, fixture, script, dependency, lockfile, CI or frontend presentation file changed.

**Contributor note:** this task was carried out by the contributor who has been acting as Developer C, at the repository owner's explicit direction after C's own queue was exhausted (C7 delivered; C8/C9 gated). It is A-lane work in an A-lane branch and needs A's normal review; C's involvement grants no ownership.

## What was built

`POST /api/cash-gap` answers one question: holding the saved actions and execution dates fixed, how much explicitly hypothetical additional opening cash would the declared bounded model need?

New contracts in `schemas.py`: `CashGapRequest` (mirrors `VerificationRequest`'s dimensions and budget), `MinimalityWitness`, and `CashGapDiagnostic`.

`cash_gap.diagnose_cash_gap` reuses `verify_plan` unchanged, so every canonical ledger, evidence, authorization and accounting gate applies to every candidate. The algorithm:

1. Verify the saved plan as-is. Already `SAFE` → `NOT_REQUIRED`, 0 cents.
2. If the counterexample carries any failure property other than `nonnegative_balance` — authorization, evidence, accounting, essential services, dependencies — stop at `NOT_REPAIRABLE_WITH_CASH`. Money does not repair those.
3. Otherwise take the observed worst minimum as the candidate buffer, and **verify that candidate** against the same bounds rather than asserting it arithmetically.
4. If the candidate verifies `SAFE` and the baseline worst case was proven, verify one cent less. Only if that actually fails is the result `PROVEN_MINIMUM`.

Statuses are deliberately distinct: `NOT_REQUIRED`, `PROVEN_MINIMUM`, `SUFFICIENT_NOT_PROVEN_MINIMAL`, `NOT_REPAIRABLE_WITH_CASH`, `INCONCLUSIVE`. `additional_opening_cash_cents` is only ever a verified-sufficient amount; `lower_bound_cents` is separately an amount the model already proves insufficient. `is_funding` is a constant `false` in the contract and the first warning on every response says an amount is a bounded diagnostic, not funding, income, an approval or a change to any obligation.

`limiting_date`, `limiting_event_ids` and `limiting_rule_ids` link the buffer to the date, events and source rules that drive it, so B can put evidence beside the number.

The endpoint is session-scoped, revision-guarded and **persists nothing** — it follows `/api/plan/preview`, not `/api/verify`. The verifications it runs internally never enter saved verification history.

### One defect found and fixed during development

The first implementation concluded `NOT_REPAIRABLE_WITH_CASH` whenever no shortfall appeared in the evaluated cases. Under a case or time cutoff that is wrong: "no shortfall seen yet" is not "no shortfall exists". `test_case_cutoff_never_becomes_an_exact_minimum` caught it; incomplete coverage now returns `INCONCLUSIVE`.

## Acceptance criteria

| Criterion | Where | Result |
|---|---|---|
| Independent small-ledger oracle | `test_independent_small_ledger_oracle` | Passes; brute-forces the true buffer over the declared payday product for four ledgers |
| Zero-gap case | `test_zero_gap_case_requires_nothing` | `NOT_REQUIRED`, 0 cents |
| Eight-date example gives a proven 40000-cent buffer and verifies the same schedule | `test_eight_date_synthetic_proves_the_forty_thousand_cent_buffer` | `PROVEN_MINIMUM` 40000; funded run `SAFE` with identical action IDs and execution dates |
| One cent less fails when minimality is claimed | same test | Witness at 39999 is `UNSAFE`, earliest failing date 2026-09-26 |
| Case/time cutoff does not become an exact minimum | `test_case_cutoff_...`, `test_time_cutoff_...` | `INCONCLUSIVE`, amount `None`, `minimality_proven` false |
| Denied/pending authorization never becomes cash-repair success | `test_denied_approval_is_never_repaired_by_cash` | `NOT_REPAIRABLE_WITH_CASH`, `authorization` in `blocking_properties` |
| Unresolved evidence never becomes cash-repair success | `test_unresolved_evidence_is_never_repaired_by_cash` | Never `PROVEN_MINIMUM`; amount `None` |
| API privacy / nonmutation / stale-result | `test_cash_gap_api.py` | 401 without a session; 409 for another session's plan, a stale revision and a post-intake plan; workspace revision, scenario, plan and verification history all unchanged |
| Future obligations stay visible | `test_future_obligations_stay_visible_in_the_funded_check` | Device principal retained in `beyond_horizon`; deferral warning preserved |
| Amounts are diagnostics, never funding | `test_amount_is_labeled_a_diagnostic_and_never_funding` | `is_funding` false; warning present; inputs unmutated |

`test_inputs_are_never_mutated` additionally round-trips the scenario, rules and plan to confirm the diagnostic mutates nothing it is given.

## Checks and results

| Check | Result |
|---|---|
| `python -m pytest backend/tests -q` | **362 passed, 9 skipped** (PostgreSQL variants skipped; no local PostgreSQL) |
| `python -m pytest backend/tests/test_cash_gap.py backend/tests/test_cash_gap_api.py -q` | 19 passed |
| `python -m ruff check backend scripts` | All checks passed |
| `python scripts/export_openapi.py` | Exported; re-running produces an identical file, so no drift |
| `npm run generate:types` | Regenerated `api-types.ts`; `CashGapDiagnostic`, `CashGapRequest`, `MinimalityWitness` present |
| `npm run typecheck` | Passed — the regenerated types break no existing frontend code |
| `npm run lint` | Passed |
| `npm run build` | Passed; `/` static, 152 kB first-load JS |
| `git diff --check` | Passed |
| `python scripts/check_workflow.py --require-current` | Passed: lane ownership, task handoff, conflict markers, current main |

**Toolchain deviation.** Backend checks ran on the shared root `.venv` Python 3.12.0, which matches the pin. Frontend checks did **not**: this host has Node `v24.2.0` / npm `11.3.0` against the `22.23.2` / `10.9.8` pin, so `npm ci` refuses with `EBADENGINE`. `frontend/node_modules` was symlinked to the root checkout's existing install for the duration of the checks and removed before committing; `frontend/package.json` and `frontend/package-lock.json` are untouched. CI's frontend result is authoritative.

**Not run — `npm run test:e2e`.** The Playwright browser cache is empty and installing Chromium would be installing tooling. No browser test exercises this endpoint yet, which is expected: the stage 1 acceptance criterion "real-API browser checks cover these labels and evidence links" belongs to B's `cash-gap-diagnostic-ui` task, which consumes this contract.

No provider request, upload, deployment, dev server or outbound message. No other developer's checkout, branch, service, session or `.next` directory was touched.

## Limits and what is deliberately not here

- **V1 is additional opening cash only.** No search for new permissions, no clause edits, no combinations of repairs, as the assignment scopes.
- **No claim about all possible schedules.** This diagnoses one saved fixed schedule. The separate CP-SAT impossibility certificate in `scripts/verify_demo.py` is untouched and remains the demo's offline fallback; an impossibility claim still needs that certificate and must not be inferred from one failed fixed plan.
- A `PROVEN_MINIMUM` is proven **only within the declared bounded model and displayed horizon**, exactly as `verify_plan`'s SAFE is. Outside those bounds it establishes nothing.
- The candidate is derived from the observed worst minimum and then verified. Because a fixed schedule shifts uniformly with opening cash, one candidate suffices; if the verifier's semantics ever stop being uniform in opening cash, this derivation needs revisiting and the minimality witness would catch it.
- B consumes this only after it merges. B adds its own type aliases in `frontend/src/lib/types.ts`; A stops at the generated `api-types.ts`.
