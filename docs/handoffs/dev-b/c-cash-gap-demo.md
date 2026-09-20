# Contributor C; ownership lane dev-b; B remains frontend owner

Task **C11 `c-cash-gap-demo`** (2 points) from [DEV_C.md](../../DEV_C.md).

Branch: `codex/dev-b/c-cash-gap-demo`. Worktree: `.worktrees/dev-c-cash-gap-demo`.
Base: `codex/dev-b/cash-gap-diagnostic-ui` (stage 1 B) with `codex/dev-b/c-demo-kit` (C10) merged in, both on top of main `8fa1279`.
Prerequisite contracts: A's cash-gap API merged as **PR29**; B's panel is the stage 1 B branch this stacks on.

Files: new `frontend/demo/cash-gap-demo.md`, new `frontend/tests/cash-gap-demo.spec.ts`, plus this handoff. Nothing else.

## Stacking, and what must merge first

C11's prerequisite is stage 1 **A and B**. A's half is merged; B's is not. C11 also writes into `frontend/demo/`, which C10 creates. So this branch sits on stage 1 B with C10 merged in — all three are dev-b lane, so the ownership check passes against main.

**Required merge order: C10 → `cash-gap-diagnostic-ui` → C11.** Merging C11 alone would carry the other two in with it.

## Deliverables

**`cash-gap-demo.md`** — the beat-4 presenter segment: the five steps in order, the two labels that must never blur (proven minimum versus inconclusive-after-cutoff), the denied-approval aside, and the limits to state under questioning. It says plainly that the segment is only runnable once stage 1 merges, and points at the saved-script fallback until then.

**`cash-gap-demo.spec.ts`** — a demo regression, deliberately distinct from `cash-gap.spec.ts`. That spec covers component behaviour and label discipline; this one walks the presenter's exact path in order and adds what a component test would not: **a reload at the end**, asserting the saved plan's revision, ID, actions and opening balance are all unchanged after the whole segment.

The second test pins the strongest spoken claim in the segment — *money does not buy an approval* — by asserting that a denied-approval diagnostic returns no amount, no lower bound, and renders no currency figure at all.

## Reuse, not recomputation

No frontend arithmetic and no duplicate oracle. Every asserted figure comes from the merged API response; A's backend suite keeps the independent small-ledger oracle and the one-cent-less minimality check, and this task does not re-derive them. The spec also asserts `funded.fixed_actions` equals `baseline.fixed_actions`, which is the contract's own statement that the schedule did not change.

## Checks and results

| Check | Result |
|---|---|
| `npx playwright test tests/cash-gap-demo.spec.ts` | **2 passed** |
| `npm run test:e2e` (full suite) | **36 passed** in 1.2 minutes — 28 baseline, 6 from stage 1 B, 2 new |
| Relative links resolve | 2/2 |
| `git diff --check` | Passed |
| `python scripts/check_workflow.py --require-current` | Passed |

Typecheck, lint and build were run on the stage 1 B base and are unchanged here: this task adds one Markdown file and one spec, no application code.

**Toolchain deviation.** Node `v24.2.0` / npm `11.3.0` against the pinned 22.23.2 / 10.9.8; `npm ci --engine-strict=false` from the existing lockfile with `frontend/.npmrc`, `package.json` and `package-lock.json` untouched. CI on the pinned toolchain remains authoritative.

Isolated ports 8043/3043, worktree-local storage, blank provider credentials. No provider call, deployment or outbound message; no other developer's services touched.

## Limits

- The segment describes on-screen behaviour that is real only after stage 1 B merges. Until then the runbook fallback applies, and the document says so at the top.
- This is presenter preparation and an automated regression. It is **not** a rehearsal: no human spoken run was performed, and [rehearsal-log.md](../../../frontend/demo/rehearsal-log.md) still has no rows.
- Beat 4's budget is 30 s in the cue sheet. That is a plan, not a measurement.
