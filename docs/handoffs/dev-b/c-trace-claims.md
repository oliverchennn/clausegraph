# Contributor C; ownership lane dev-b; B remains owner

**Contributor C patch inside B's existing lane.** B owns `frontend/src/components/decision-trace.tsx` and may reclaim it immediately. No `dev-c` lane or new ownership is claimed.

Branch: `codex/dev-b/c-trace-claims`. Worktree: `.worktrees/dev-b-c-trace-claims`.
Starting and required main commit: `e65464cbe2648a2bd43d42829eda75d321476580` (PR24).
Required contract changes: none. No schema, generated type, manifest, lockfile, backend, script, CI, fixture or shared-doc change.

## Authorization status — read before merging

**No C write release exists.** `docs/DEV_C.md` at this commit states plainly: "No C write release is granted: any later tiny implementation still needs the exact-path A assignment/B release procedure below, and is not a good use of this prompt budget by default." C7 is a read-only review assignment whose deliverable is a report. The repository owner instructed C in session to finish the assigned task and fix the issues it surfaced, after C had explained the same constraint in the previous session; that session's equivalent patches were merged as PR16/PR17. This patch therefore exists on the owner's explicit override.

Overlap check against fetched main: no open A/B task touches this file. Stage 0 (`live-demo-closeout`, `live-demo-consent`) has no handoff on main yet and no remote task branch exists. B's merged `demo-rehearsal` handoff reserved `ui.tsx`, `review-queue.spec.ts` and `verification.spec.ts` — `decision-trace.tsx` is not among them. This is an observation from main, not a reservation: nothing protects this path, and B outranks it.

Scope is deliberately one source file plus this handoff.

## Findings fixed

Both from C's C7 judge-story review of `e65464c`. Neither repeats C's delivered C1/C5 findings.

### 1. The decision trace called planner arithmetic "verified"

Step 4 rendered `N verified change(s)`. These are deterministic planner-computed ledger effects; nothing has verified them. The word collides with the product's own ClauseGraph **Verify** feature, whose bounded fixed-plan check is the only thing that issues a verdict — and which, in the demo story, reports this very plan **Unsafe** roughly eighty seconds later. A judge reading "2 verified changes" in the 0:00–0:35 beat is being told the opposite of the story's punchline.

Before: `2 verified changes`. After: `2 computed changes`. The step is already labelled "4 · Ledger effect", and the panel footer already says the projection is recomputed from these changes with no model-generated arithmetic, so no information is lost.

### 2. Step 2 collapsed evidence validity and human review into one verdict

The clause step rendered a single span: `Evidence supported` when every rule's `evidence_status` was `supported`, otherwise `Review required`. Two problems. It reports a human-review outcome from an evidence field, contradicting the AGENTS invariant that "Evidence validity, extraction confidence, human review, and third-party approval are separate fields". And it flattens three distinct evidence states — `unchecked`, `disputed`, `unsupported` (`schemas.py`) — into the word "Review required", which names none of them. `docs/DEMO.md` sends the presenter through this step at 0:00–0:35 to show "separate evidence/review/approval states"; the evidence drawer does separate them, this step did not.

After: two spans. Evidence reports its own weakest status by name (`Evidence supported` / `Evidence unsupported` / `Evidence disputed` / `Evidence unchecked`), and human review is stated separately as `Human reviewed` / `Human review pending` from `review_status`. Approval remains where it already is, in the evidence drawer and action cards; this step does not restate it.

No condition governing plan state, money or authorization changed — these are labels computed from fields already present on the rules.

## Checks and results

Toolchain deviation, unchanged from C's previous session and still the main limit:

- The pinned toolchain is absent on this host: Node `v24.2.0` / npm `11.3.0` against the `22.23.2` / `10.9.8` pin, so `npm ci` refuses with `EBADENGINE`. No version manager and no `.worktrees/.toolchain` exist here. C installed nothing.
- `frontend/node_modules` was symlinked to the root checkout's existing install for the duration of the checks and removed before committing. `frontend/package.json` and `frontend/package-lock.json` are untouched.

| Check | Result |
|---|---|
| `npm run typecheck` | passed |
| `npm run lint` | passed, no warnings |
| `npm run build` | passed; `/` static, 150 kB first-load JS — the current main baseline including PR23's history UI, not a delta from this change |
| `git diff --check` | passed |
| `python scripts/check_workflow.py --require-current` | passed: lane ownership, task handoff, conflict markers, current main |

**Not run — `npm run test:e2e`.** The Playwright browser cache is empty and installing Chromium would be installing tooling. No existing spec asserts either changed string (`workspace.spec.ts` asserts the `trace-change` per-change text and the source document name, both untouched), so no selector update was needed — but that is a static read, and **these strings are not browser-verified**. All checks above ran under Node 24, so CI is authoritative.

No backend test, provider request, upload, deployment, dev server or outbound message. No other developer's checkout, branch, service, session or `.next` directory was touched.

## Limits and handback

- Both changes are label-only and move claims in the conservative direction; no money, authorization, evidence gate or plan state is recomputed.
- Finding 2 adds a second line to the clause step. C did not view it rendered, so B should confirm the step-2 layout still reads cleanly at desktop and 390 px — the one visual risk here.
- C's review is not a substitute for A/B review. If B needs this file, C yields immediately. A may close this patch and reimplement instead.
