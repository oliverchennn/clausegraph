# Developer B: stage 1 cash-gap diagnostic UI

Stage 1, idea #2 consumer half from [HACKATHON_ASSIGNMENTS](../../HACKATHON_ASSIGNMENTS.md). A's `cash-gap-diagnostic` contract merged as PR29; this consumes it.

Branch: `codex/dev-b/cash-gap-diagnostic-ui`. Worktree: `.worktrees/dev-b-cash-gap-ui`.
Starting and required main commit: `8fa1279c61e702d82f2adb80729f082bfcbc892e` (PR31), including the merged PR29 contract.
Required contract commits: PR29 (`b5d9204`) — merged before this work began; no unmerged contract is consumed.

Files: new `frontend/src/components/cash-gap-panel.tsx`, new `frontend/tests/cash-gap.spec.ts`, plus `frontend/src/components/verify-plan.tsx` (mount only), `frontend/src/lib/types.ts` (two aliases), `frontend/src/app/globals.css` (scoped styles) and this handoff. No backend, schema, generated type, manifest, lockfile or script changed.

**Contributor note:** carried out by the contributor acting as Developer C, at the repository owner's direction, to unblock C11. It is B-lane work in a B-lane branch and needs B's normal review; no ownership is claimed.

## What it does

When a fixed-plan verification returns anything other than SAFE, the panel offers a bounded diagnostic. It posts the **same declared uncertainties, case cap and time budget** that produced the displayed verification, so the diagnostic answers a question about the result on screen rather than a different model.

It renders, straight from the contract and never recomputed in the browser:

- the backend `status` as the headline label — the UI has no proof logic of its own;
- the verified-sufficient amount with an explicit qualifier, `proven minimum for this fixed schedule` or `verified sufficient; not proven minimal`;
- when no amount is established, "No amount established" plus the proven `lower_bound_cents` floor if one exists;
- the original schedule beside the same schedule under the cash assumption, both by status and worst minimum;
- coverage as complete or incomplete with exact case counts;
- the limiting date and a button into the real evidence drawer for the limiting rules;
- `blocking_properties` when the failure is authorization or evidence, with the explicit line that those are never repaired by money;
- every backend warning verbatim.

A persistent line states the amount is a diagnostic, not funding — no money obtained, no approval granted, no obligation changed. The panel never renders an amount for a non-cash blocker, and never labels an incomplete check as a minimum.

**Stale clearing.** An effect keyed on session, workspace revision, plan ID and verification ID aborts any in-flight request and drops the displayed diagnostic. A diagnostic belongs to exactly one verification result; re-verifying replaces the result, so the old diagnostic disappears rather than being relabelled. A SAFE result unmounts the panel entirely.

**Nonmutation.** `/api/cash-gap` persists nothing, and the test asserts the workspace revision, saved plan and scenario opening balance are identical before and after.

### A shared-primitive note for B

`Badge` in `ui.tsx` does not spread extra props, so a `data-testid` placed on it is silently dropped. Rather than change a shared primitive this task does not own, the test id sits on a wrapping `span`. Worth knowing before the next component test.

## Checks and results

Run in this worktree with isolated storage, ports 8042/3042 and blank provider credentials.

| Check | Result |
|---|---|
| `npm run typecheck` | Passed |
| `npm run lint` | Passed |
| `npm run build` | Passed; `/` static, 153 kB first-load JS |
| `npx playwright test tests/cash-gap.spec.ts` | **6 passed** |
| `npm run test:e2e` (full suite) | **33 passed** in 1.1 minutes — 28 pre-existing plus 6 new, with one pre-existing count unchanged |
| `git diff --check` | Passed |
| `python scripts/check_workflow.py --require-current` | Passed |

New browser coverage: the proven $400 buffer with its comparison, evidence link and untouched saved plan; a denied approval reported as `NOT_REPAIRABLE_WITH_CASH` with no amount; a forced case cutoff reported as `INCONCLUSIVE` with no amount and honest counts; a 503 that is retryable and shows no result; assumption changes clearing a stale diagnostic and a SAFE result removing the panel; and a 390px keyboard run asserting zero horizontal overflow.

**Toolchain deviation.** Node `v24.2.0` / npm `11.3.0` against the pinned 22.23.2 / 10.9.8. `npm ci --engine-strict=false` installs from the existing lockfile without editing `frontend/.npmrc` (A-owned) — `package.json` and `package-lock.json` confirmed unmodified. The Playwright Chromium browser was installed into the user-level cache. The full suite passes here, but CI on the pinned toolchain remains authoritative.

No provider call, upload, deployment or outbound message. No other developer's checkout, services, ports or `.next` directory was touched.

## Limits

- V1 is additional opening cash only, matching the contract. No permission search, clause edit or combined repair.
- The panel appears only for a non-SAFE fixed-plan result; there is no gap to diagnose otherwise.
- Backend `warnings` render verbatim and are not deduplicated against the verification panel's own warnings, so a reader may see a repeated deferral note. Cosmetic, deliberately not filtered — dropping backend warnings in the UI would be the worse failure.
- Stage 1's acceptance also names an independent small-ledger oracle and a one-cent-less check. Those live in A's merged backend suite (`test_cash_gap.py`); this task asserts the labels reach the screen correctly rather than re-deriving the arithmetic.
