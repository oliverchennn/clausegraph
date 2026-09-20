# Developer B: consequence walkthrough integration

## Assignment before implementation

User-approved solo completion continues. Fresh branch/worktree: `codex/dev-b/consequence-integration`, `.worktrees/dev-b-consequence-integration`, from merged main `e31d415433f3d80120ab3c00b805c20494e1bca6` (PR44). Prerequisites: complete stage 3 through PR43 `8d167648`; A's stage 4 contract PR44 `e31d415`. Allowed files are `frontend/src/app/page.tsx`, `frontend/src/components/dependency-graph.tsx`, `frontend/src/app/globals.css`, `frontend/src/lib/types.ts`, affected existing `frontend/tests/workspace.spec.ts` if needed, and this handoff. No backend/generated/dependency/C14 component/demo/test or central-doc edits.

Acceptance: retain the selected action with its nonmutating preview; clear stale identity with comparison state; publish typed C14 props and the exact page mount; wire existing evidence and graph navigation; highlight only returned rule-linked graph nodes/edges; provide shared responsive walkthrough styles; preserve current plan/history and existing comparison/graph behavior.

## Delivered interface and release

`ConsequenceWalkthroughProps` provides `{ workspace, recorded, candidate, actionId, onEvidence, onGraph }` using only existing generated contracts. Action-only previews retain `actionId`; generic scenario previews do not mount the walkthrough. The slot is scoped to current comparison state and graph focus clears when that state closes or invalidates.

`DependencyGraph` accepts optional `highlightRuleIds`. It highlights exact rule nodes and nodes/edges connected through matching `edge.rule_ids`, without changing evidence clicks or graph data. The graph tab displays a removable status message while a consequence path is focused.

**Released to C14 after this task merges:** in `frontend/src/app/page.tsx`, C14 may replace only `ConsequenceWalkthroughSlot`'s body/import and the marked mounted call without changing comparison/request/tab state or prop types. Stable wrapper: `data-testid="consequence-walkthrough-slot"`. Shared `.consequence-*` responsive classes in `globals.css` are ready for the assigned new components; C14 does not own that shared stylesheet.

## Validation and limits

- Pinned Node 22.23.2/npm 10.9.8 `npm ci --no-audit --no-fund`: passed from the unchanged lock.
- `npm run typecheck`, `npm run lint`, `npm run build`: passed.
- `E2E_API_PORT=8156 E2E_WEB_PORT=3156 npm run test:e2e -- workspace.spec.ts`: 2 passed against the real local API/Chromium, including action-only slot identity, generic-preview exclusion, preview nonmutation, reload invalidation and the existing 390px path.
- `git diff --check`: passed. Full exact-head CI remains the merge gate.

No money is calculated in the browser; no new API, provider call, live inference, external execution, deployment or human rehearsal occurs in this task. C14 owns the actual walkthrough, accessibility interaction, real-API acceptance and presenter segment after this green merge.
