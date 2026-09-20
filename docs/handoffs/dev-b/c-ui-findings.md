# Contributor C; ownership lane dev-b; B remains owner

**Contributor C patch inside B's existing lane.** B remains the owner of every file below and may reclaim any of them immediately. This is not a `dev-c` lane and claims no new ownership.

Branch: `codex/dev-b/c-ui-findings`. Worktree: `.worktrees/dev-b-c-ui-findings`.
Starting and required main commit: `e3143394ccb9f4daef10a41f0800a01e62a5df8e` (PR13).
Required contract changes: none. No schema, generated type, manifest, lockfile, backend, script, CI or shared-doc change.

## Authorization status — read this before merging

**The DEV_C.md gate for a C write task was not satisfied.** There is no committed A assignment naming these paths and no B release of them; `docs/DEV_C.md` records C5 as **WAIT / unassigned** with "There is no currently released C5 task." The repository owner instructed C directly, in session, to branch and fix every finding from C's C1–C3 report, after C explained that the documented procedure blocks it. This patch therefore exists on the owner's explicit override, not on a released assignment.

Consequences A and B should weigh:
- It exceeds the documented C5 budget of one issue and at most two released frontend files: it covers five findings across five source files plus two browser specs.
- It edits `frontend/src/app/page.tsx` and `frontend/src/app/globals.css`, both excluded from C by default in DEV_C.md because of overlap risk.
- A or B may close this in favour of implementing the corrections directly. Nothing here is a prerequisite for any A/B task.

No open A/B task appears to touch these paths: PR13 (the current head) is backend-only, and B's last frontend task PR8 is merged. C confirmed this from fetched main, not from any reservation mechanism — a file release was never granted here, so there is nothing protecting these paths.

## Findings fixed

Reported by C against `9570a94`; rebased onto `e314339`, which changed no file touched here.

### 1. An assumed opening balance was displayed as recorded fact
`frontend/src/components/overview-metrics.tsx`. Saving a scenario with an **Available cash** override stores it on `plan.assumptions` and leaves `workspace.scenario.opening_balance_cents` untouched, and an opening-cash override alone leaves `include_conditional: false`, so `plan.state` can stay `confirmed`. The headline card showed that hypothetical with the foot "Starting balance" and no marker, beside an **Edit financial picture** button that edits the other value.

Before: `Starting balance`. After, only when a saved override differs from the recorded picture: `Assumed starting balance · recorded $X`. Unchanged when there is no override. Honors the AGENTS invariant that assumptions are labeled conditional, and matches the treatment `verify-plan.tsx` already gives nominal assumptions.

### 2. "Essentials protected" tied an unconditional guarantee to a cash test
`frontend/src/components/overview-metrics.tsx`. The badge rendered "Essentials protected" only when `minimum_balance_cents >= 0 && state === "confirmed"`, implying by omission that conditional plans or plans with a shortfall might not protect essentials. Essentials preservation is an unconditional hard guard in `engine.py` (`_action_changes` rejects any action removing a protected essential service, and raises "Essential expenses cannot be silently removed"), so it holds for every producible plan.

Before: `Essentials protected`. After: `Cash stays nonnegative`. Label only — the `isProtected` condition and badge tone are unchanged, and `page.tsx` already states the essentials claim accurately and separately.

### 3. The review queue's refresh-failure branch was unreachable
`frontend/src/components/review-queue.tsx` and `frontend/src/app/page.tsx`. `onRefresh` was bound to `page.tsx`'s `run()` helper, which catches errors and never rethrows, so `await onRefresh()` always resolved: the component's `catch` and its "The workspace could not be refreshed." message were dead code. A failed **Refresh workspace** then bumped `retry` anyway, refetched, still mismatched the revision, and re-showed the same generic stale message, while the real error surfaced only in the page-level "Something needs attention" alert far from the button that failed.

After: `onRefresh` propagates rejections; a failed refresh sets a separate `refreshError` rendered with `role="alert"` inside the stale panel, above its own **Refresh workspace** button, and no longer triggers a refetch that is guaranteed to stay stale. Queue-load failures keep their existing separate message and **Try again** path. The panel already owned the busy state for this button, so dropping `run()` here loses no feedback.

### 4. The global focus ring failed WCAG 2.2 SC 1.4.11
`frontend/src/app/globals.css`. The ring was `#99b2ff`, **2.07:1** against the white cards and **1.96:1** against the `--background` page — below the 3:1 non-text contrast minimum. `.review-queue :focus-visible` already overrode it with `#587ac2` at **4.22:1**, so only the surface B validated most recently was compliant.

After: the global ring is `#587ac2`, and the now-identical `.review-queue` override is removed. Verified against the dark sidebar too, where `#587ac2` gives **3.67:1** — still above 3:1, so no surface regresses. Ratios computed from the hex values with the WCAG relative-luminance formula, not measured on a rendered page.

### 5. Three controls per action card shared identical accessible names
`frontend/src/components/action-card.tsx`. Every card emitted "View evidence", "Compare option alone" and "Draft request" with no per-action context, so a keyboard or screen-reader user met three identical "Compare option alone" buttons. `review-queue.tsx` already solves this with a per-item `aria-label`, and the existing specs had to scope through test ids to disambiguate.

After: `View evidence for <title>`, `Compare option alone · <title>`, `Draft request for <title>`. Each keeps the visible text as a prefix, satisfying WCAG 2.5.3 Label in Name; visible labels are unchanged, so `docs/DEMO.md`'s references to **Compare option alone** stay accurate.

Two specs pinned the old names with `exact: true` and were updated to the new full name: `frontend/tests/review-queue.spec.ts` and `frontend/tests/verification.spec.ts`. The four selectors in `frontend/tests/workspace.spec.ts` pass no `exact`, and Playwright's lax matcher is `normalized.toLowerCase().includes(selector)` — verified in the installed `playwright-core` source, not assumed — so they still match the new names by substring. No new test was added.

## Checks and results

Run from this worktree. Toolchain deviation, stated plainly because it is the main limit on this patch:

- **The pinned toolchain is not present on this host.** Node is `v24.2.0` and npm `11.3.0`; `package.json` pins `22.23.2`/`10.9.8`. `npm ci` therefore refuses outright with `EBADENGINE`, and no version manager or `.worktrees/.toolchain` is available. C did not install Node or any other tooling.
- To run checks at all, `frontend/node_modules` was **symlinked** to the root checkout's existing install and removed again before committing. Nothing was installed, and `frontend/package.json` / `frontend/package-lock.json` are untouched — confirmed with `git status`.

| Check | Result |
|---|---|
| `npm run typecheck` (`next typegen && tsc --noEmit`) | passed |
| `npm run lint` (`eslint .`) | passed, no warnings |
| `npm run build` | passed; `/` static, 146 kB first-load JS (B's PR8 record: 145 kB) |
| `git diff --check` | passed |
| `python scripts/check_workflow.py` | see PR; lane, handoff and conflict-marker checks |
| Focus-ring contrast | computed: `#587ac2` = 4.22:1 on white, 3.67:1 on the sidebar; old `#99b2ff` = 2.07:1 |

**Not run — `npm run test:e2e`.** The Playwright browser cache is empty and installing Chromium would have meant installing tooling. **The two updated selectors and the C2 refresh behavior are therefore not browser-verified**; their correctness rests on reading the component, the wiring and the Playwright matcher source. This is the one thing B or A should re-run before merging, and it is the reason this patch should not be merged on C's word alone. Every check above ran under Node 24, not the pinned Node 22.23.2, so CI's result is authoritative.

No backend test, no provider request, no upload, no deployment, no dev server and no outbound message. No other developer's checkout, branch, service, session or `.next` directory was touched.

## Limits and handback

- Findings 1 and 2 change what a displayed claim means, in the safer direction; no money is recomputed and no financial or consent logic is touched.
- Finding 3 changes behavior, not only wording, and is the change most in need of the unrun browser suite.
- Finding 4 is a shared-style change. It is deliberately the smallest possible one — a colour already present in the file — but it affects every focusable element, so B should sanity-check it visually at desktop and 390 px.
- C's own review is not a substitute for A/B review. If B needs any of these files, C yields immediately: stop editing, preserve the branch, hand back. A may close this patch and reimplement instead.
- C did not verify at 390 px in a browser; layout claims in the report were static reads of `globals.css`.
