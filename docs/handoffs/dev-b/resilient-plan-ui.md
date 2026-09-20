# Solo orchestrator / B lane: resilient-plan-ui

## Assignment before implementation

The user confirms other developers are inactive and authorizes this agent to complete all remaining implementation, reviews, fixes and green sequential merges. Follow the merged solo override; this is same-agent orchestration, not independent A/B approval. Preserve all prior worktrees and handoffs.

- Branch/worktree: `codex/dev-b/resilient-plan-ui`, `.worktrees/dev-b-resilient-plan-ui`.
- Starting/fetched main and required engine contract: `c420609fe8157bfa6d475106ba3eaae07e1fa996` (PR41). Clean root main fast-forwarded before creating this checkout. Engine head `974b502` passed PR CI 35500807913 and push CI 35500791826: 463 backend tests including PostgreSQL and 51 browser tests, plus complete contract/frontend/platform checks.
- Prior prerequisites: reviewed design PR39 `96b220e5c4298df83a822846cb13e1dfbb234c86`; C12/stage 2 PR40 `f85aa08bc127d2900d26345963b5a1421a6294fd`.
- Allowed files: new `frontend/src/components/resilient-plan.tsx`, `frontend/tests/resilient-plan.spec.ts`; targeted `frontend/src/components/verify-plan.tsx`, `frontend/src/app/page.tsx`, `frontend/src/components/saved-history.tsx`, `frontend/src/lib/types.ts`; this handoff. Component styles remain scoped. No backend, generated type, dependency/lock or central-document edits. C13's presenter segment/test follows the merged UI.

## Acceptance and interface

Consume the merged synthesis API with unchanged current uncertainty bounds. Compare backend nominal/worst-case cash, fees, burden and fixed action/date lists; expose evidence, bounded counters, restrictions and found/no-solution/inconclusive claims. Search saves nothing. Explicit adoption sends only the original request, tuple and fingerprint; use the returned saved plan/proof together without nominal recalculation. Invalidate candidates and delayed requests on bounds/source identity changes; fail closed on errors and clear private state on 401. Preserve current proof after adoption, label FIXED_VERIFIED distinctly, and expose an explicit separate synthetic demo choice without changing the default original fixture. Keep reset/history semantics accurate.

Validate pinned locked install, typecheck/lint/build, focused real-API browser flows including no-solution/cutoff/errors/stale races/adoption/history and keyboard/390px layout, then full CI. Inspect screenshots and record same-agent review. No live provider call or human spoken rehearsal is claimed.

## Results

Narrow scope addition before compatibility fixes: `frontend/tests/workspace.spec.ts` may update the obsolete exact six-document banner assertion to the explicit original-fixture wording; `frontend/src/components/cash-chart.tsx` may label the saved projection as the nominal case so a synthesized schedule is not described as a nominally optimized plan. No chart arithmetic changes.

CI-discovered scope addition before fixing it: `frontend/tests/cash-gap.spec.ts` may wait for the initial saved plan before its authorization/nonmutation snapshot. PR CI 35501891379 ran 57/58 browser tests successfully but this existing test captured `plan: null` during startup and later compared it with the completed plan. Push CI 35501875921 passed all58; the failure is an initialization race, not evidence that cash diagnostics mutate a saved plan. Preserve the full equality assertion and establish its required ready-state precondition.

The corrected cash-gap regression passed **5/5 repeated real-API runs in 39.0s** (`npm run test:e2e -- cash-gap.spec.ts --grep "authorization failures" --repeat-each 5`). No application logic changed for this fix; full CI reruns on the new head before merge.

- Added a separate bounded search panel using the unchanged uncertainty draft and saved nominal assumptions. Displays fixed action/date comparison, backend fee/burden totals and proof-qualified cash, exact domain strings, actual work, exclusion/refutation detail and retained future obligations. FOUND requires the returned complete SAFE proof; no-solution is scoped to the declared domain, and cutoffs remain inconclusive.
- Preview is nonmutating. Explicit adoption posts only the original request/tuple/fingerprint and installs the returned saved plan and proof together, with no nominal optimization. Distinct FIXED_VERIFIED/current/history labels avoid optimum claims. Reload preserves the adopted schedule and uncertainty bounds through provenance; durable proofs remain in history.
- Full uncertainty drafts, unsaved nominal-control edits, source plan/revision/session changes and unmounts discard candidates and abort delayed responses. 401 clears private workspace/token; errors discard candidates and offer saved-state reload. Bounds are disabled during adoption. The explicit three-document resilient example leaves the original six-source example as the default; reset text tracks the current variant.
- Pinned Node22.23.2/npm10.9.8 `npm ci` passed. Final typecheck, lint and production build passed after browser/label polish. No dependency or generated-contract change.
- Real API/Chromium compatibility run: `npm run test:e2e -- resilient-plan.spec.ts verification.spec.ts history.spec.ts workspace.spec.ts` **19 passed in 1.7m**. After screenshot spacing and scenario-draft invalidation fixes, `npm run test:e2e -- resilient-plan.spec.ts` **7 passed in 40.4s**; final typecheck/lint passed. Isolated ports8153/3153, Python3.12; no provider requests.
- Browser cases establish unchanged history until adoption, unchanged bounds, exact adopted tuple/proof, zero nominal solve calls on adoption, reload/history labels, real no-solution/case-limit, delayed obsolete response rejection, 409 replacement-plan failure, 401 privacy clearing, injected search failure/retry, keyboard evidence focus restoration/adoption and no horizontal overflow at390px. The injected fault and reduced work budget are explicit; successful financial results come from the real API.
- Visually inspected mobile comparison and desktop adopted-proof screenshots in ignored `frontend/test-results`. Fixed helper-rendered action/date text spacing under scoped CSS, then rechecked the mobile image; labels, totals, dates and focus outlines are readable.
- Same-agent orchestrator review covered private/stale state, nominal-case versus solver labels, candidate proof qualification, nonmutating preview and explicit exact-tuple adoption. This is not independent A review. Full remote CI must pass before merge. C13's dedicated presenter segment/demo regression is next; no human/live outcome is claimed.
