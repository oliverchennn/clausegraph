# A / solo orchestrator: resilient-plan-engine

## Assignment before implementation

- User authorizes one agent to complete all inactive A/B/C work, reviews and green sequential merges; record reviews as same-agent orchestration, not independent B sign-off.
- Branch/worktree: `codex/dev-a/resilient-plan-engine`, `.worktrees/dev-a-resilient-plan-engine`.
- Starting/fetched main: `f85aa08bc127d2900d26345963b5a1421a6294fd` (PR40). Root main was clean; preserve all historical worktrees and peer handoffs.
- Required merges: reviewed synthesis design/solo reassignment PR39 `96b220e5c4298df83a822846cb13e1dfbb234c86`; C12/stage 2 completion PR40 `f85aa08bc127d2900d26345963b5a1421a6294fd`. PR40 CI 35499343638 passed 390 backend and 51 browser tests plus full checks. Stage 1 and B controls precede these as recorded centrally.
- Allowed files: new `backend/clausegraph/synthesis.py`, `backend/clausegraph/resilient_demo.py`, `backend/tests/test_synthesis.py`, `backend/tests/test_synthesis_api.py`, `scripts/synthesize_demo.py`, `fixtures/resilient/01-obligation.txt`, `fixtures/resilient/02-paycheck.txt`, `fixtures/resilient/03-payment-options.txt`; targeted edits to `backend/clausegraph/schemas.py`, `api.py`, `storage.py` (and `engine.py`/`verification.py` only if shared-helper reuse requires it); generated `docs/openapi.json` and `frontend/src/lib/api-types.ts`; this handoff and `docs/RESILIENT_PLAN_SPEC.md`, `docs/WORKSTREAMS.md`, `docs/RESUME.md` for current implementation/consumption status. No frontend UI, dependency, lock or migration edits are planned.

## Acceptance

Implement the reviewed fixed-schedule domain, first-feasible enumeration and global budgets; separate found-and-verified/no-solution/inconclusive outcomes; retain recorded approvals, all obligations and source gates. Use the existing fixed-plan verifier, no per-outcome optimization. Nonmutating private API plus atomic, revalidated explicit adoption with same-revision active-plan checks. New separate synthetic fixture and offline script demonstrate nominal failure versus a fixed safe alternative; original fixture values stay unchanged.

Independent small-domain arithmetic/oracle tests, malformed/huge/empty/cutoff cases, approvals/conditions/essential/debt invariants, API nonmutation/privacy/races, rollback and deletion on SQLite and PostgreSQL. Generated contract drift, Ruff/backend suite, frontend compatibility and full CI before merge. B-lane comparison/adoption/C13 work follows this merged contract.

## Reviewed implementation clarification

Domain construction can hit a limit before its exact tuple count exists; `total_candidate_tuples` is nullable in that case, never a fabricated zero. Cost totals are nullable when domain preparation ends before a trustworthy bounded comparison is available. Normal results carry backend totals. A shared nominal precheck counts toward the global case budget and is reused for the empty schedule. These clarify honest work reporting without relaxing the reviewed guarantees.

## Results

Scope clarification before the final report edit: `scripts/verify_demo.py` is also allowed to update its repository-wide synthesis availability flag. Its original impossibility certificate and money computations remain unchanged; it must say that this report does not invoke synthesis and point to the separate success script.

- Implemented first-feasible mixed-radix search with recorded-permission/action constraints, shared time/case budgets, exact domain strings, example refutations and separate FOUND/NO_SOLUTION/INCONCLUSIVE claims. Uses existing deterministic gates, ledger and fixed-plan verifier; no per-outcome nominal optimization or new money model.
- Added backwards-compatible nominal/resilient provenance and FIXED_VERIFIED status. Search is private and nonmutating. Explicit adoption reconstructs and rechecks the exact tuple, compares canonical contents and atomically saves its plan/series/proof under a conditional database write lock. Replacement-plan/readiness/revision/deletion races reject; repeated adoption is stale.
- Separate three-source synthetic fixture: nominal early shift has minimum 5000 cents but fails the September 3–5 income range; the fixed late shift incurs a real 100-cent fee and has nominal/verified minimum 4900 cents. Original six documents and engine/verifier files are untouched. Demo variant is explicit and preserved on reset.
- 43 focused engine tests include a separate integer arithmetic oracle, exact evidence, same-day dependency order, writer collisions, essential/supersession/timing gates, original beyond-horizon debt, malformed/huge/empty domains and cutoffs. Fifteen API scenarios run on SQLite and PostgreSQL in CI: preview nonmutation, explicit adoption, spoofed inputs, privacy, stale races, concurrent adoption, transaction failure after proof insert and deletion/reset.
- Local Python3.12: `python -m ruff check backend scripts` passed; `python -m pytest backend/tests -q` **439 passed, 24 skipped** in 78.87s. The 24 PostgreSQL variants await CI because no local test URL is configured. Existing test-client deprecation warnings remain.
- Generated OpenAPI and TypeScript from canonical schemas. Locked Node22.23.2/npm10.9.8 install, typecheck, lint and production build passed. Full remote CI is required before merge.
- Both offline scripts ran and their redirected JSON reloaded. Separate synthesis: FOUND/SAFE/4900 cents. Original verification: UNSAFE, impossibility certificate true, minimum extra hypothetical cash 40000 cents. Windows DLL import diagnostics go to stderr so the new report remains JSON.
- Same-agent orchestrator review covered proof labels, shared budgets, recorded approvals, fingerprint exclusion of nondeterministic identifiers, atomicity/privacy and existing demo regressions. Review found and fixed canonical synthetic-source hashing across Windows newline styles. This is not independent B approval.
- No provider calls, paid provisioning, external execution, or user-service restarts. UI comparison/adoption/C13 follows this contract's green merge; no browser synthesis delivery is claimed yet. Human/live verification limits remain as recorded centrally.
