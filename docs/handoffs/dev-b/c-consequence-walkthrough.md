# C14 / solo orchestrator: consequence walkthrough

## Assignment before implementation

The user explicitly approved solo completion and urgent deployment. Contributor identity is C in the existing dev-b lane. Fresh branch/worktree: `codex/dev-b/c-consequence-walkthrough`, `.worktrees/dev-c-consequence-walkthrough`. It was created at PR46 `1bfe9cd`, left untouched while B's identity correction completed, then fast-forwarded to merged prerequisite PR47 `7aa03b740793ec6e35897e512903fe4ef50568e6`.

Other prerequisites: stage 3 through PR43 `8d167648`; A contract/guards PR44 `e31d415` and PR45 `620f3a1`; B graph/state seam PR46 `1bfe9cd`. Allowed files: new `frontend/src/components/consequence-walkthrough.tsx`, `frontend/src/components/consequence-steps.tsx`, `frontend/tests/consequence-walkthrough.spec.ts`, `frontend/demo/consequence-demo.md`, this handoff, and only the released placeholder import/body in `frontend/src/app/page.tsx`. No backend/generated/shared-state/style/dependency/central-doc changes.

Acceptance: accessible source -> reviewed rule -> dependency -> effect -> cash sequence; exact evidence and graph callbacks; cancellation's removed $60 service charge and single accelerated $480 existing device debt; retained/brought-forward future obligations; blocked action with no fabricated cash; nonmutation; keyboard arrows/Home/End and 390px readability; real-API tests and honest presenter segment.

## Result

Implemented five linked steps over B's typed props and A's returned `DecisionTrace`. The UI only joins IDs and formats server-returned cents/dates. Evidence, human review and approval remain separate. Removed, shifted, accelerated, added and fee effects have explicit wording; shift/acceleration is timing, not savings. Recorded and preview cash values and beyond-horizon lists remain attached to their own simulations.

Blocked actions show their returned exclusion and no action-specific cash panel. Cancellation shows the source-backed $60 removal and the same $480 device obligation moving earlier exactly once. Navigation uses roving focus with Left/Right/Home/End plus Previous/Next controls; the released responsive classes produce a one-column mobile list. Evidence and graph actions reuse B callbacks.

## Validation and limits

Pinned Node 22.23.2/npm 10.9.8 validation on the exact branch head:

- `npm ci`: pass.
- `npm run typecheck`, `npm run lint`, `npm run build`: pass.
- `npm run test:e2e -- consequence-walkthrough.spec.ts`: 3 passed.
- Full `npm run test:e2e`: all three new walkthrough tests passed; 63/64 overall passed. The only failure was the documented pre-existing `history.spec.ts` refresh-button detach flake.
- Isolated rerun of that exact history scenario: 1 passed in 2.8 seconds.
- `git diff --check`: pass.

Remote CI is the merge gate and is recorded on the pull request. The presenter timing is proposed; no human spoken run, provider call, live extraction, external financial action or deployment occurs in C14. C15 follows only after this merges.
