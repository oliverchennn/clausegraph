# Developer A: bounded uncertainty contract validation

## Assignment and isolation

The user explicitly authorized A's next task while a separate B session reviews PR19, provided it can proceed safely. This is work-board row 7's validation of the existing uncertainty limits. It does not assign B's amount-range/multiple-dimension UI or row 8's robust synthesis specification.

Starting and required contract commit: `f23133bd7828186edfd72caf367be99a3201d33d` (merged PR18), freshly fetched with pruning. PR19 is open at `5b94f3433faa3447103bd69cf1f940a1868be2bb`, with green CI and B review in progress per the user. This task neither depends on nor changes PR19's branch/files. Main and all prior worktrees are preserved; the user's local app stays running separately.

During work the user reported merging PR19 and assigned B task 5's demo work. Fetched and confirmed PR19's merge `7088b812c1da4169b1ad4b4d668bf2536e68e43d`, then fast-forwarded this task and clean main without altering the new task files. This merged commit is the final validation base. B's demo work remains separate; no B history/uncertainty UI assignment is implied. No GitHub review record was present when the merge was inspected, so this handoff does not claim a published B review.

Branch: `codex/dev-a/uncertainty-limits`. Worktree: `.worktrees/dev-a-uncertainty-limits`.

Allowed files: `backend/clausegraph/verification.py`, `backend/clausegraph/schemas.py`, new `backend/tests/test_uncertainty_limits.py`, new `docs/UNCERTAINTY_CONTRACT.md`, this handoff, and generated `docs/openapi.json` / `frontend/src/lib/api-types.ts` only if a demonstrated schema validation defect requires regeneration. Runtime/schema edits require a reproduced defect within the existing bounded contract. Shared progress docs touched by PR19, storage, API routing, other handoffs, frontend presentation, dependencies, migrations and fixtures are excluded.

After PR19 merged, extend the documentation-only scope to A-owned `docs/WORKSTREAMS.md` and `docs/RESUME.md` so the current assignments reflect the user's update (A uncertainty validation; B task 5 demo). The temporary exclusion protected the review snapshot; the merged content is retained and no historical handoff is edited.

## Acceptance checks

- Validate closed date/integer-cent ranges, approval outcomes, unique dimensions/targets, maximum eight dimensions, maximum 10,000 cases and 10-second cooperative budget.
- Check combined dimensions and interactions with saved nominal assumptions against independently expected cash results. Verify full coverage versus case/time limits, retained counterexamples and honest proof flags.
- Exercise HTTP validation/nonmutation and document request limits, target restrictions, Cartesian-product semantics, witness labels and frontend consumption constraints.
- Fix only demonstrated verification/validation defects; preserve deterministic integer cents, source/review/approval gates, fixed action IDs/dates, future obligations and SAFE/UNSAFE/UNKNOWN semantics.
- Run baseline/targeted/full backend checks, Ruff, schema drift or regeneration, documentation links, ownership/current-main checks and full CI. Use synthetic data and isolated test databases; no live providers or user sessions.
- Publish a separate PR for B review, then stop. Fetch main again before publication and incorporate any intervening merged work normally; never consume PR19 before merge or alter its reviewed snapshot.

## Results

Completed 37 new synthetic validation cases in `backend/tests/test_uncertainty_limits.py`. No runtime or public-schema defect was reproduced in this scope, so the verifier, schemas, generated types, dependencies and migrations are unchanged.

- Three small-ledger oracles independently calculate cash for amount-only, date-only and combined uncertainty while both nominal income assumptions are saved. They verify exact worst daily rows, retained request/nominal labels and input immutability.
- Real API checks preserve the uncertain payday witness through history, retain the active nominal plan, and combine date/amount/approval domains without presenting unauthorized schedules as proven cash results.
- Twenty-six invalid HTTP requests check bounds, strict cents/case types, duplicate IDs/properties, invalid dates/targets/outcomes and more than eight dimensions. Every rejection leaves the workspace and verification history unchanged.
- Eight binary dimensions exhaust 256 assignments in either request order. Exactly 10,000 cases complete; a 10,001-case safe prefix returns UNKNOWN/CASE_LIMIT. Synthetic clock boundaries at 10 seconds distinguish no evidence from a retained concrete UNSAFE witness. Tests freeze the clock only to isolate case/time semantics, not to claim throughput.
- Eight maximum-size cent ranges retain the exact arbitrary-precision case product through backend JSON serialization, while the case budget stops after one assignment. The contract warns that ordinary JavaScript numbers cannot display such counts exactly.

[UNCERTAINTY_CONTRACT.md](../../UNCERTAINTY_CONTRACT.md) documents existing request/target limits, inclusive ranges, Cartesian combinations, inherited nominal assumptions, lazy enumeration, cooperative timing, proof labels and frontend limits. Shared board/checkpoint updates record merged PR19 and the user's active B task 5 assignment. No B implementation or historical handoff was edited.

| Check | Result |
|---|---|
| Baseline `python -m pytest backend/tests/test_verification.py backend/tests/test_verification_api.py -q` | 61 passed in 8.21s |
| Initial new contract cases | 32 passed in 16.35s; no runtime change required |
| Full suite before PR19 integration | 335 passed, 1 PostgreSQL skip in 55.96s |
| Full suite on merged `7088b81`: `python -m pytest backend/tests -q` | 343 passed, 9 PostgreSQL skips in 64.62s |
| Final `python -m pytest backend/tests/test_uncertainty_limits.py -q` after adding large-count JSON roundtrip assertion | 37 passed in 18.39s |
| `python -m ruff check backend scripts` | Passed after the final test assertion |
| Compare `app.openapi()` against parsed `docs/openapi.json` after PR19 merge | Exact equality; generated contracts unchanged |
| Resolve relative links in all changed docs; `git diff --check` | Passed; existing Windows line-ending notices only |

Commands use Python 3.12.14 in the root `.venv/Scripts/python.exe`. Test runs emit two existing Starlette/AnyIO deprecation warnings. No local disposable `POSTGRES_TEST_URL` is configured; the nine skips are the existing PostgreSQL test and PR19's eight PostgreSQL history variants. Full CI runs those checks on PostgreSQL 17, plus generated-contract drift, frontend typecheck/lint/build/browser tests and clean installs on Linux, Windows and macOS. Final CI results are recorded on the PR for its exact commit.

## Review and remaining limits

A self-review found no defect in the validated bounded contract. B's independent review and green CI remain required before merge and are not claimed by this implementation record. The user reported PR19's merge; no published review record was present when inspected.

These are synthetic contract checks, not a performance benchmark, general robust-synthesis proof, live-provider validation or demo rehearsal. Large products can remain UNKNOWN, the time budget is cooperative, and guarantees remain limited to the declared model and horizon. The user's local services were not restarted and no user session, cloud database or provider was used. A stops at this task; B continues the separate demo assignment.
