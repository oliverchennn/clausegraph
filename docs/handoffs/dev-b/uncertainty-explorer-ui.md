# Developer B: stage 2 uncertainty explorer UI

Stage 2, idea #3 controls half from [HACKATHON_ASSIGNMENTS](../../HACKATHON_ASSIGNMENTS.md). Owns the dimension controls, the request, selection and stale-state invalidation, and **releases the `verify-plan.tsx` wiring section to C12**. It deliberately does not implement C's failure view.

Branch: `codex/dev-b/uncertainty-explorer-ui`. Worktree: `.worktrees/dev-b-uncertainty-ui`.
Base: `codex/dev-b/cash-gap-diagnostic-ui` (stage 1 B) on main `8fa1279`, so the two `verify-plan.tsx` changes compose instead of conflicting.
Required contract commits: none. This half consumes no new field, which is why it does not wait on A's stage 2 contract.

Files: new `frontend/src/components/uncertainty-controls.tsx`, new `frontend/tests/uncertainty-explorer.spec.ts`, plus `verify-plan.tsx`, `types.ts`, `globals.css`, two existing specs updated for the replaced controls, and this handoff.

**Contributor note:** carried out by the contributor acting as Developer C at the repository owner's direction, to unblock C12. B-lane work needing B's normal review; no ownership claimed.

## What replaced the old form

The panel previously offered one hardcoded payday range plus one optional approval. It now owns up to eight declared dimensions of any mix: income date, income amount and approval outcomes, each with its own target, bounds and rationale, added and removed individually.

**Exact preflight count.** `exactCaseCount` multiplies domain sizes in `BigInt` and renders the full decimal string. A product can far exceed JavaScript's safe integer range, and a rounded count must never be displayed as exact — so nothing here passes through `Number`. An inclusive $100 amount range contributes 10001 values, and when the product exceeds the 10000-case budget the panel warns that the check will stop early and report incomplete coverage rather than returning Safe.

**Duplicate feedback.** Two dimensions may not declare the same property of the same target. Duplicates are flagged inline with `role="alert"` and block submission before a request is sent, while the server keeps its own validation.

**Stale state.** Every edit clears the displayed result. A result belongs to the exact bounds that produced it, so changing a bound removes it rather than relabelling it.

No user bound is ever silently narrowed to obtain Safe, and the budget is never raised for the same purpose.

### `BigInt` literals and the build target

`1n` literals fail the project's TypeScript target. The code uses `BigInt(1)` rather than changing `tsconfig.json`: a target bump is a shared build decision that does not belong in a feature task.

## Released wiring section for C12

In `frontend/src/components/verify-plan.tsx`, marked with a `RELEASED TO C12` comment:

- **Mount point:** `<div data-testid="failure-view-slot" className="failure-view-slot">`, inside the result block and above the cash-gap panel.
- **Component:** `FailureViewSlot`, a placeholder B ships so the seam, props and selector are merged and testable before C12 lands. **C12 replaces this component body only.**
- **Typed props:** `{ verification: VerificationResult; onEvidence: (ruleIds: string[]) => void }`.
- **Stable selector:** `data-testid="failure-view-slot"`.
- **Release SHA:** this task's merge commit. The release covers the slot and that component body. It does **not** cover the form, the request, the dimension state, the stale-clearing effect or any other part of `verify-plan.tsx`.

The placeholder intentionally reads only `verification.counterexample`, which exists today, so this branch stays independent of A's stage 2 contract. C12 consumes `evaluated_failures`, `failure_count`, `failures_truncated` and `total_cases_exact` once that contract merges.

B reclaims this section by recording it in a later B handoff. Until then, B avoids C12's assigned files.

## Merge-order note for existing specs

Replacing the old controls changed two accessible names, so two merged specs were updated here: `verification.spec.ts` (`Latest verification payday` → `Latest for payday`; the approval select → `add-approval`) and `cash-gap.spec.ts` (approval select → `add-approval`).

**`frontend/tests/cash-gap-demo.spec.ts` on the C11 branch uses the same removed approval select.** It is not in this branch, so it cannot be fixed here. If C11 merges before this task, that spec needs the same one-line change (`getByLabel("Verification approval outcomes").selectOption({ index: 1 })` → `getByTestId("add-approval").click()`). Recorded so it is not discovered as a surprise CI failure.

## Checks and results

| Check | Result |
|---|---|
| `npm run typecheck` | Passed |
| `npm run lint` | Passed, no warnings |
| `npm run build` | Passed |
| `npx playwright test tests/uncertainty-explorer.spec.ts` | **7 passed** |
| `npm run test:e2e` (full suite) | **41 passed** in 1.3 minutes |
| `git diff --check` | Passed |
| `python scripts/check_workflow.py --require-current` | Passed |

New coverage: add/remove up to the eight-dimension limit with the add buttons disabling at the cap; an inclusive $100 range counting 10001 values and warning about the 10000-case cap; an 80,000,000,008-case product rendered in full precision with no exponent form; a duplicate target flagged and blocking submission; declared combinations matching the backend (24 cases, 2 dimensions) with the fixed schedule and workspace revision preserved; editing a bound clearing the previous result; and keyboard add/remove at 390px with zero horizontal overflow.

**Toolchain deviation.** Node `v24.2.0` / npm `11.3.0` against the 22.23.2 / 10.9.8 pin; `npm ci --engine-strict=false` from the existing lockfile with `.npmrc`, `package.json` and `package-lock.json` untouched. CI on the pinned toolchain remains authoritative.

## Limits

- Controls only. The failure view is C12's, and this task deliberately stops at a placeholder.
- The preflight count mirrors the backend's arithmetic in the browser for feedback before sending; the server remains the authority, and no displayed proof status is derived from it.
- Outcome combinations for an approval dimension are offered as a fixed set of four useful choices rather than free multi-select, which keeps every option a valid non-empty subset of the contract's three outcomes.
- `total_cases_exact` from A's stage 2 contract is not consumed here; the preflight count is computed from the declared bounds locally, as the contract explicitly permits.
