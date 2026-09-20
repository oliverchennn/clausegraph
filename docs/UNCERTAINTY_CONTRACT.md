# Bounded uncertainty contract

This documents the existing backend contract for a future, separately assigned B task covering amount ranges and multiple uncertainty controls. B is currently assigned task 5's demo work per the user; this document does not change that assignment. A's [uncertainty-limits handoff](handoffs/dev-a/uncertainty-limits.md) records the validation scope and results. No new API fields, controls or robust synthesis are introduced.

## Request and allowed domains

`POST /api/verify` requires the private session bearer token and the current saved `plan_id` plus `revision`. Missing/invalid sessions return 401; an absent or stale active plan returns 409. Invalid request fields or semantic targets return 422 without saving a verification or changing the workspace. The store rechecks the active plan/revision before saving an in-flight result. Results are available through the existing private `GET /api/verifications` route.

| Input | Existing constraint |
|---|---|
| `uncertainties` | Zero to eight dimensions; omitted means check the single nominal assignment |
| Each dimension | Unique `id` of 1–80 characters; `rationale` of 1–1000 characters; `basis` is `user_assumption` |
| `income_amount` | Known projected income `event_id`; inclusive integer-cent `minimum_cents` and `maximum_cents`, each 0–10,000,000,000; minimum must not exceed maximum |
| `income_date` | Known projected income `event_id`; inclusive explicit ISO-date `earliest` and `latest`; earliest must not exceed latest or precede the horizon start |
| `approval` | Known, unambiguous action or rule `target_id`; one to three distinct outcomes drawn from `approved`, `denied`, `pending` |
| `max_cases` | Strict integer 1–10,000, default 10,000 |
| `time_limit_seconds` | Greater than zero and at most 10 seconds, default 5; cooperative budget |

Money bounds and case counts reject booleans, numeric strings and fractional numbers. Income dimensions cannot target expenses, actual events, unknown events or historical projected income. A single projected income may have one date dimension and one amount dimension; the same property cannot be declared twice under different IDs. Approval dimensions for an action and its source rule are distinct. Changing an action's assumed approval does not automatically approve its source rule. `not_required` is not an allowed uncertain outcome and cannot remove a required approval.

The date range is not capped at the horizon end. Income occurring at or after the exclusive end remains in `beyond_horizon` and contributes no cash to the displayed daily balances. Singleton ranges are valid and count as one assignment. A known approval target need not affect a selected action; such a dimension may leave the result unchanged while increasing case count.

## Combination and saved assumptions

Dimensions form a Cartesian product: every integer cent, calendar date and declared approval outcome is enumerated in combination. A two-cent range, two-date range and three approval outcomes produce 12 cases. Eight two-value dimensions produce 256 cases. These are exhaustive finite checks, not samples, probabilities, correlations or source-derived confidence intervals.

The saved plan's opening balance, horizon, nominal income assumptions and fixed action IDs/dates form the starting model. Declared dimensions replace their own nominal income/approval values for each case. Undeclared nominal assumptions remain in effect. The result retains both `nominal_assumptions` and the verification `assumptions`, so the UI must show hypothetical opening cash and assumed approvals even when a bounded check returns SAFE. No request records a third-party decision, mutates the saved plan or reoptimizes its actions.

Bounds do not repair missing source validity, human review or unresolved conditions. Assuming an income date does not excuse an unsupported amount; assuming its amount does not excuse an unsupported date. Both declared values still require any attached source to support the income direction and remaining necessary facts. Existing evidence and essential-obligation gates remain in force.

Input order does not change the search result. Enumeration sorts dimensions by `(kind, id)`, visits lower cents/dates first, and sorts approval outcomes lexically. IDs therefore can affect which equally early witness is retained. A witness is a concrete assignment, not a likelihood ranking.

## Limits and interpretation

The case budget limits work, not the size of the declared domain. The backend counts the full product using arbitrary-precision integers and enumerates lazily. Eight maximum-size amount ranges contain `10,000,000,001 ** 8` cases; only the allowed prefix is evaluated before a budget stops the run. There is no guarantee that 10,000 cases finish within the time budget.

The clock is checked before each case. A case already running can finish after the budget; the setting is not a hard HTTP deadline or per-case preemption. A run that completes every case can still report EXHAUSTED if its final case crossed the nominal time limit. Runtime and actual coverage remain visible.

| Result | Required interpretation |
|---|---|
| SAFE | Every declared case was checked and necessary facts were resolved; guarantee is only for the fixed schedule, daily closing balances, model and horizon shown |
| UNSAFE | At least one concrete assignment violates a safety property; a valid counterexample remains UNSAFE even if a later case/time cutoff prevents full coverage |
| UNKNOWN | No conclusive violation was found, but coverage is incomplete or necessary facts remain unresolved; never label this safe |
| `coverage_complete` | All declared assignments were visited; it does not alone prove a meaningful cash minimum for unauthorized or unresolved cases |
| `worst_case_proven` | The stored worst cash result is proven over the declared model; otherwise label it as observed among fully evaluated authorized cases |

`solver_status` distinguishes EXHAUSTED, CASE_LIMIT, TIME_LIMIT and INVALID_MODEL. Do not infer completeness from `checked_cases > 0`, a favorable observed minimum, or successful HTTP status. An authorization counterexample can have no simulation and no balance; render its failure reason rather than inventing a cash projection. Keep nominal optimizer status separate from fixed-plan verification. Use "found failure" for a witness unless the stated coverage and resolution support a stronger earliest-failure claim.

`total_cases` is an integer in the API, but very large products exceed JavaScript's exact integer range. B must not present a rounded JavaScript number as an exact case count or derive proof status from floating-point ratios. Use the server's coverage/proof fields and qualify large counts (or calculate a display count with exact integer arithmetic from the declared bounds). Cash remains backend-computed integer cents.

## Frontend handoff and scope

Use existing generated contracts only after this validation task is merged. Keep ranges and rationales visibly labeled as user assumptions; show saved nominal assumptions alongside verification dimensions. Do not silently narrow a large range or raise budgets to obtain SAFE. Reject unsupported targets and duplicate properties early for usability while preserving server validation. Clear stale results when the request, active plan, revision or private session changes; a historical result never authorizes today's action.

The backend already supports these dimensions; richer frontend controls are still unimplemented and require B's separate assignment. Correlated uncertainty, uncertain expenses, adaptive schedules and general robust synthesis remain outside this contract and require a separate specification. Validation here uses synthetic data and isolated databases, with no live-provider or deployed-service claim. [Verification semantics](handoffs/verification.md) and [history semantics](HISTORY_CONTRACT.md) provide the related contracts.
