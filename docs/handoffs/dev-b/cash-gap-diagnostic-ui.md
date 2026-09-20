# Developer B: cash-gap diagnostic UI

## Assignment before implementation

The user requested every Developer B assignment from the most recent pull. Freshly fetched `origin/main` is `8fa1279c61e702d82f2adb80729f082bfcbc892e` (PR31), which assigns B's current stage 1 task before the still-gated stages 2–4. This task starts from that exact commit on `codex/dev-b/cash-gap-diagnostic-ui` in `.worktrees/dev-b-cash-gap-diagnostic-ui`; existing branches, worktrees, services and local configuration remain untouched.

Required merged prerequisites at start were PR29's cash-gap API/generated contract at `b5d9204a62ba854cfd82c1a8bf90ca90b0adf174`, PR30's incomplete-source guard at `5e79c1d7b571a0c67bc0bb41e70cd0be405265e5`, and PR31's assignment at the starting SHA. B independently reviewed A's follow-up PR32 with no blocking findings and 33 focused local passes. During implementation PR32 merged as `1a24143`; this branch then fast-forwarded to that exact latest `origin/main` before final validation. The guard changes no schema or cash arithmetic.

Allowed paths are `frontend/src/lib/types.ts`, new `frontend/src/components/cash-gap-diagnostic.tsx`, `frontend/src/components/verify-plan.tsx`, `frontend/src/app/globals.css`, new `frontend/tests/cash-gap.spec.ts`, and this handoff. No generated types, backend, dependency/lock, central documentation, C-assigned view/demo path, deployment or provider work is assigned.

Acceptance: request the private nonmutating `/api/cash-gap` diagnostic only for the current saved fixed plan and the exact displayed verification assumptions; compare the original fixed schedule with the same schedule under an explicitly hypothetical opening-cash assumption; show proof-qualified amount/lower-bound labels, limiting date/evidence, one-cent witness, coverage, blockers and warnings without implying funding or changing/adopting a plan. Authorization/evidence failures must remain separate from cash shortfalls, incomplete coverage must remain inconclusive, future obligations stay visible, and session/revision/plan/assumption changes abort and clear stale diagnostics. Cover the eight-date 40000-cent result, evidence navigation, unchanged workspace/reload, authorization failure, incomplete result, stale response suppression, keyboard focus and 390px layout through real API/browser tests. Run typecheck, lint, build, focused/full browser checks and the normal ownership/ancestry/diff checks before publication.

## Results

Added a typed, private `/api/cash-gap` request beside failed fixed-plan verification results. The request reuses the exact displayed verification assumptions and current plan/session/revision identity; the component owns one abort controller and is keyed inside the already session/revision/plan-keyed verifier, so input changes unmount and abort it before a stale response can render. API failures display their existing guidance without retaining a prior amount.

The result presents the original fixed schedule beside the same actions/dates under only the returned hypothetical opening-cash assumption. It distinguishes proven minimum, verified-sufficient but nonminimal, lower-bound-only, not-repairable and inconclusive outcomes. It displays server-returned coverage, worst-case or observed balance labels, limiting date/events, exact evidence navigation, the one-cent witness, non-cash blocker explanations, warnings and beyond-horizon obligations. There is no apply/adopt path: repeated copy states that the amount is not funding, income, approval or permission and that recorded opening cash and the saved plan remain unchanged. No financial value is calculated in React.

The real-API browser coverage proves the original eight-date example returns a 40000-cent minimum, the 39999-cent witness fails, the funded comparison is safe, `rule-loan` opens through keyboard activation, workspace/history stay unchanged and reload does not persist this diagnostic. A 390px path checks authorization cannot be repaired with cash and a real case-limited response remains inconclusive with no amount; the page has no horizontal overflow. A delayed request is aborted and suppressed when assumptions change, and completed diagnostics clear on same-revision plan replacement, revision/evidence change and new session identity. Desktop and 390px screenshots were inspected from the passing focused run; labels, hierarchy, wrapping and evidence control were readable.

## Validation

Pinned Node 22.23.2/npm 10.9.8 and the existing locked dependency tree were used. The worktree-only dependency symlink was removed before publication. Tests used isolated SQLite/browser ports and made no provider request.

| Check | Result |
|---|---|
| `npm run typecheck && npm run lint` | Passed. |
| `npm run build` | Passed; optimized production build completed. |
| `E2E_API_PORT=8128 E2E_WEB_PORT=3128 npm run test:e2e -- tests/cash-gap.spec.ts` | 3 passed; produced inspected desktop/mobile screenshots. |
| `E2E_API_PORT=8129 E2E_WEB_PORT=3129 npm run test:e2e` | 31 passed, including all existing history, consent, review, verification and workspace regressions. |
| Post-PR32 `python -m pytest backend/tests/test_cash_gap_api.py backend/tests/test_cash_gap.py -q` | 33 passed; two existing dependency deprecation warnings. |
| Post-PR32 focused browser reruns on ports 8130/3130 and 8131/3131 | 3 passed each against the latest merged guard; the final run includes corrected incomplete-result wording. |

Final ownership/current-main, `git diff --check` and GitHub CI are recorded at publication. Full PostgreSQL/backend, clean-install matrix and generated drift remain CI checks because this task changes only B-owned frontend and handoff paths. No live provider, private real-data, deployment or cloud action occurred.

## Handoff and limits

Publish for A's review and normal green integration, then stop this task. C11 starts only after this B implementation merges; its assigned `frontend/demo/cash-gap-demo.md` and `frontend/tests/cash-gap-demo.spec.ts` remain untouched. Stage 2 B work remains gated on A's merged uncertainty-explorer contract, stage 3 on the reviewed synthesis spec/contracts and stage 4 on the provenance contract. No interface for those unmerged stages was invented here.
