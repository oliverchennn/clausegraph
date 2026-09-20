# Reassigned C12: uncertainty failure view

- Contributor: solo orchestrator, user-authorized to complete inactive A/B/C work and perform recorded reviews; ownership lane dev-b.
- Branch/worktree: `codex/dev-b/uncertainty-failure-view`, `.worktrees/dev-b-uncertainty-failure-view`.
- Starting/fetched main: `2e7653718ff7fac27158789deff965775da408a1` (PR35). Main and this checkout were clean. Existing worktrees/peer handoffs are preserved.
- Prerequisites: PR33 contract `dd77765f8fb5bd6b4e89b5472c3f860a0dad5860`, PR34 cash UI `c00d39573464d916ea3712c42a766df0a791fb0a`, PR36 C11 `8f6c627e9d825a07630658d6d906e2772690a6b0`, PR35 controls/interface release `2e7653718ff7fac27158789deff965775da408a1`. The direct user reassignment supersedes waiting for C; PR39 records that instruction centrally.
- Allowed files: this handoff; new `frontend/src/components/uncertainty-failure-view.tsx`, `frontend/tests/uncertainty-failure-view.spec.ts`; `frontend/src/components/verify-plan.tsx` only the released import/FailureViewSlot body/comment. No form/state or canonical contract edits.
- Interface: `{ verification: VerificationResult; onEvidence: (ruleIds: string[]) => void }`; existing `failure-view-slot` selector and parent identity/stale clearing. Preserve the existing counterexample timeline.

## Acceptance

Accessible witness failure table/details with mobile list, exact evaluated/unchecked counts, separate proven/observed worst cash, no invented probability/all-case failure list, explicit no-cash authorization outcomes, source links, Safe/Unsafe/Unknown and stale clearing. Money is rendered from backend values only. Test keyboard/mobile and main states against the real API; isolate any presentation-only response fixtures explicitly. Pinned Node22.23.2/npm10.9.8, typecheck/lint/build, focused browser regressions and full CI before merge.

## Results

Implemented the typed failure view and replaced only the released placeholder body/import. It displays exact evaluated/unchecked combinations using the existing BigInt domain helper; no failure-frequency map is invented. One witness includes assignments, violations and evidence links. A separate section labels proven versus observed permitted cash and preserves future obligations. Unknown with complete coverage remains unresolved; authorization failures show no substituted cash. Desktop table switches to a mobile list with native keyboard-accessible details/buttons.

Pinned Node22.23.2/npm10.9.8 `npm ci --no-audit --no-fund`, `npm run typecheck`, `npm run lint`, `npm run build`: passed. Python3.12 API, TEXT_PROVIDER=nvidia with blank provider keys, isolated API/web ports 8152/3152. `npm run test:e2e -- uncertainty-failure-view.spec.ts uncertainty.spec.ts verification.spec.ts cash-gap-demo.spec.ts`: **23 passed in 1.4 minutes**. Five new regressions cover cash/approval witnesses, mobile/keyboard evidence return focus, Safe/partial Unknown, partial Unsafe with exact huge counts, and complete-but-unresolved labeling. Only the last label edge uses an explicitly identified presentation response fixture; the other scenarios consume the real API with case-limit-only request overrides where needed.

Inspected generated desktop and 390px screenshots: readable table/list, visible focus, no clipping or horizontal overflow. `git diff --check`: passed. Orchestrator review (same agent under explicit user authorization) confirmed no form/request ownership change, no financial arithmetic, no global earliest-failure or probability claim, and no missing-cash substitution. The old timeline and parent stale clearing remain covered. Full CI/current-main checks still precede merge. Release expires on this task merge; shared request/form ownership is preserved. No provider calls or user-service restarts occurred.
