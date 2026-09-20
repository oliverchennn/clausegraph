# Developer B: stage 2 uncertainty explorer UI

Stage 2, idea #3 controls half. Implements against A's merged consumption specification [UNCERTAINTY_EXPLORER.md](../../UNCERTAINTY_EXPLORER.md) (PR33).

Branch: `codex/dev-b/uncertainty-explorer-ui`. Worktree: `.worktrees/dev-b-uncertainty-ui`.
Base: `codex/dev-b/cash-gap-diagnostic-ui` (stage 1 B), with `origin/main` `dd77765` merged in after A's PR32/PR33 landed mid-task.
Required prerequisite commits: `dd77765` (PR33 specification), `1a24143` (PR32 cash-gap guards).

**Contributor note:** carried out by the contributor acting as Developer C at the repository owner's direction, to unblock C12. B-lane work needing B's normal review; no ownership claimed.

## A specification landed mid-task

PR33 merged while this was in progress and renamed the required paths. The work was preserved in a WIP commit and then reworked to the specification:

- Count, validation and date helpers moved to **`frontend/src/lib/uncertainty.ts`**, the path A names for "typed shared consumption interface, draft validation and exact domain-count helpers; no cash arithmetic".
- The spec file was renamed to **`frontend/tests/uncertainty.spec.ts`**, A's named path.
- Date cardinality was reimplemented to A's stated requirement: UTC Gregorian day ordinals computed arithmetically, with full ISO validation including month/day ranges and years below 100.

**One deviation to flag.** The controls render from a new `frontend/src/components/uncertainty-controls.tsx`, which is not in A's path table — A lists `verify-plan.tsx` for the controls. The component is new, B-lane and imported only by `verify-plan.tsx`, so no existing shared file was touched outside the table, but A named these paths deliberately. **If A wants the controls inlined into `verify-plan.tsx`, say so and it moves**; nothing else changes.

## What it does

Up to eight declared dimensions of any mix — income date, income amount, approval outcomes — each with its own target, bounds and rationale, added and removed individually.

**Exact counts, per A's specification.** `exactCaseCount` multiplies domain cardinalities as `BigInt` and renders the full decimal string. Nothing passes through `Number`, and no count is derived from a parsed `total_cases`, which A notes can be irreversibly rounded by ordinary JSON parsing. Dates use proleptic Gregorian ordinals computed with integer arithmetic rather than `Date`, so local time, DST and the year 0–99 remapping cannot shift a count.

Above the 10000-case budget the panel warns that the run cannot be exhausted and will report incomplete coverage rather than Safe. Beyond `Number.MAX_SAFE_INTEGER` it additionally says the exact count exceeds JavaScript's exact integer range. No bound is silently narrowed and no budget raised to obtain Safe.

**Draft validation.** `draftBlockers` refuses submission for a duplicate property of a target, a duplicate identifier, a blank rationale, or any empty/invalid domain. An invalid draft has no valid count and cannot submit, as the specification requires.

**Stale state.** Every edit clears the displayed result: a result belongs to the bounds that produced it and is removed rather than relabelled.

## Released wiring section for C12

In `frontend/src/components/verify-plan.tsx`, marked `RELEASED TO C12`:

- **Mount point:** `<div data-testid="failure-view-slot" className="failure-view-slot">`, inside the result block, above the cash-gap panel.
- **Component:** `FailureViewSlot` — a placeholder B ships so the seam, props and selector merge and are testable. **C12 replaces this component body only.**
- **Typed props:** `{ verification: VerificationResult; onEvidence: (ruleIds: string[]) => void }`.
- **Stable selector:** `data-testid="failure-view-slot"`.
- **Release SHA:** this task's merge commit.

The release covers the slot and that component body. It does **not** cover the form, the request, dimension state, the stale-clearing effect, or anything else in `verify-plan.tsx`. Per A's specification, C12 consumes `counterexample`, its `failures`, `assignment` and evidence IDs — there is no list of all evaluated cases, and C12 must not imply the witness is the complete set of failures.

B reclaims this section by recording it in a later B handoff.

## Merge-order note

Replacing the old controls changed two accessible names, so `verification.spec.ts` and `cash-gap.spec.ts` were updated here. **`frontend/tests/cash-gap-demo.spec.ts` on the C11 branch uses the same removed approval select** and is not in this branch. If C11 merges before this task, that spec needs `getByLabel("Verification approval outcomes").selectOption({ index: 1 })` → `getByTestId("add-approval").click()`.

## Checks and results

| Check | Result |
|---|---|
| `npm run typecheck` | Passed |
| `npm run lint` | Passed, no warnings |
| `npm run build` | Passed |
| `npx playwright test tests/uncertainty.spec.ts` | **10 passed** |
| `npm run test:e2e` (full suite) | **44 passed** in 1.3 minutes |
| `git diff --check` | Passed |
| `python scripts/check_workflow.py --require-current` | Passed |

Coverage: add/remove to the eight-dimension cap; an inclusive $100 range counting 10001 with the budget warning; an 80,000,000,008-case product rendered in full precision with no exponent form; duplicate targets blocking submission; declared combinations matching the backend (24 cases, 2 dimensions) with fixed schedule and revision preserved; edits clearing the result; keyboard operation at 390px with zero horizontal overflow; DST, leap-day, non-leap-century and singleton date ranges; inverted bounds yielding a zero count and a disabled submit; and a blank rationale blocking submission.

**Pre-existing flake, not from this work:** `history.spec.ts:179` failed once under full-suite load and passed on two isolated re-runs. It also flaked before these changes. Recorded for B rather than patched here.

**Toolchain deviation.** Node `v24.2.0` / npm `11.3.0` against the 22.23.2 / 10.9.8 pin; `npm ci --engine-strict=false` from the existing lockfile with `.npmrc`, `package.json` and `package-lock.json` untouched. CI on the pinned toolchain remains authoritative.

## Limits

- Controls only. C12 owns the failure view; this task stops at a placeholder.
- The preflight count is browser-side feedback computed from declared bounds, exactly as A's specification permits. The server remains the authority and no proof status is derived from it.
- Approval outcome combinations are offered as four fixed valid subsets rather than a free multi-select, so every option is a non-empty subset of the contract's three outcomes.
- `page.tsx` was not touched; no change to shared result identity was needed.
