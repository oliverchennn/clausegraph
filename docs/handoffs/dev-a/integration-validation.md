# Developer A: merged application integration validation

## Assignment

The user selected the next unfinished A task: integration checks and updated delivery documentation after merging C's PR16 and PR17.

Branch: `codex/dev-a/integration-validation`. Worktree: `.worktrees/dev-a-integration-validation`.
Starting and required main commit: `79dced51de547ecaefa4da6d9f3aee4f8ed05234` (PR16), including PR17 at `eb81eab490140bfff3b4b6aae1ea681aa98926ff`, PR15's live retest, and B's merged PR8 review guidance.

Allowed writes: this handoff, `docs/RESUME.md`, `docs/WORKSTREAMS.md`, `docs/HACKATHON_MVP.md`, `docs/DEMO.md`, and `docs/SPONSORS.md`. Generated `docs/openapi.json` and `frontend/src/lib/api-types.ts` may be regenerated only to check for drift; report any unexpected contract change. No new features, dependency changes, other contributor handoff edits, or B-owned implementation changes are assigned.

## Acceptance checks

- Fresh isolated checkout with Python 3.12, Node 22.23.2 and npm 10.9.8; clean frontend install from the existing lockfile and preserved workflow hook.
- Backend tests and Ruff; canonical OpenAPI/TypeScript generation without drift; frontend typecheck, lint, production build and complete real-API Playwright suite on isolated local ports.
- Offline verification demo and semantic gate evaluation. No live inference, external document processing, provisioning or production data use.
- Update central delivery records to distinguish current merged functionality, exact validation, historical live synthetic results, and outstanding B rehearsal/optional work.
- Whitespace, documentation links, base-policy ownership/current-main checks; publish for B review without claiming review or merge.

## Initial inspection

Root main fast-forwarded from `6d07014` to `79dced5`; all historical worktrees and their existing changes were preserved. Original A workflow task is already merged as PR5. Its 18 regression tests passed on the current root checkout in 11.11 seconds.

C's PR17 CI application verification and Linux/Windows/macOS clean installs passed. The overall PR run [35482761943](https://github.com/vzhu08/clausegraph/actions/runs/35482761943) failed only the current-main ancestry gate: its head did not contain PR15's newer main commit. This historical failure is not a claim that the merged application's checks failed or that all pre-merge gates passed.

## Validation on 2026-09-20 UTC

Commands ran from this isolated worktree using the shared Python `3.12.14` virtual environment and the repository-local Node `22.23.2` / npm `10.9.8` installation. In the table, `python` denotes `C:/Users/vzhu0/PycharmProjects/clausegraph/.venv/Scripts/python.exe`; npm commands ran in `frontend`. No root `.env` was copied. Browser servers used disposable worktree SQLite storage and ports 8021/3021 with provider credentials blank.

| Check | Result |
|---|---|
| `python scripts/install_hooks.py` | Existing ClauseGraph pre-push hook preserved; no custom hooks path configured |
| `npm ci --no-audit --no-fund` | Passed; 439 packages in 47 seconds, existing lockfile unchanged |
| `python -m pip check` | No broken requirements |
| `python -m pytest backend/tests -q` | 298 passed, 1 PostgreSQL skip, 2 existing dependency deprecation warnings in 39.65 seconds |
| `python -m ruff check backend scripts` | Passed |
| `python scripts/export_openapi.py`; `npm run generate:types`; `git diff --exit-code -- docs/openapi.json frontend/src/lib/api-types.ts` | Passed, zero contract drift |
| `npm run typecheck`; `npm run lint`; `npm run build` | Passed; static `/`, 145 kB first-load JavaScript |
| `E2E_API_PORT=8021 E2E_WEB_PORT=3021 npm run test:e2e` (PowerShell environment variables) | 11 passed in 1.3 minutes; actual local API and Chromium |
| `python scripts/verify_demo.py` | Complete 8/8 UNSAFE model; first failure 2026-09-26 at -40000 cents; separate nominal optimization proves no safe schedule in that declared model; same fixed schedule SAFE in 8/8 with 40000 hypothetical opening cents |
| `python scripts/eval_nemotron.py` | All 5 expected fixture gate outcomes passed: 3 supported candidates, 2 deliberately incorrect candidates rejected, 5/5 withheld pending review; no model accuracy measured |
| `git diff --check`; six-document UTF-8/link/base-ownership inspection | Passed; all 32 relative links resolve, all changed documents belong to A, no conflict markers or trailing whitespace |

Pre-publication fetch confirmed `origin/main` remains `79dced5`, identical to this task's starting application commit. The installed pre-push hook reruns current-main, ownership and task-handoff checks during publication.

The full browser suite covers review saves and retry/mobile/keyboard behavior, stale revision/session rejection, deleted evidence, Safe/Unsafe/Unknown verification, approval uncertainty, preview preservation and application, scenario edits, privacy deletion and mobile overflow. Next.js development-origin and NO_COLOR/FORCE_COLOR notices were nonfatal; no application failure was observed. These checks do not constitute a timed presenter rehearsal or comprehensive visual/accessibility audit.

Two focused exploratory Chromium checks also passed in 21.4 seconds using ignored `.data/integration-validation.spec.ts` and `.data/integration-validation.config.ts`: `E2E_API_PORT=8021 E2E_WEB_PORT=3021 npx playwright test --config ../.data/integration-validation.config.ts` from frontend. Injecting a stale queue and a synthetic workspace 503 showed the error next to its refresh button, preserved the saved plan, avoided a stale queue refetch, and recovered after retry. Applying and reloading a cash preview retained the assumption label while recorded cash remained 200000 cents and the plan assumption was 210000 cents. The temporary harness's first launch looked for package.json under `.data`; setting its frontend server cwd fixed that harness error before either test ran. These exploratory files are local artifacts, not additions to B's regression suite.

Exact merged base [CI run 35483115189](https://github.com/oliverchennn/clausegraph/actions/runs/35483115189) passed application verification (including PostgreSQL 17, contract drift, build and browsers) and clean installs on Linux, Windows and macOS. Ownership is skipped on push runs by design; the new documentation PR must pass its own base-policy check. GitHub now resolves the existing origin URL to the private repository `oliverchennn/clausegraph`; no remote or visibility setting was changed.

## Delivery and remaining work

Updated RESUME, WORKSTREAMS, HACKATHON_MVP, DEMO and SPONSORS to describe merged PR8/PR9/PR11/PR13/PR15/PR16/PR17, current checks, and the historical Brev live result including both the failed and passing runs. No source, schema, dependency, fixture, financial rule or other contributor's handoff changed.

B's timed three-minute demo, local fallback rehearsal and final desktop/mobile visual sign-off remain unrecorded. Brev browser consent is a separate optional assignment. Hosted evidence/OCR, audio, cloud storage/deployment and live Tiger Data remain unverified; current offline checks do not extend the limited historical Brev claims. History/richer uncertainty UI and robust synthesis remain deferred. No provider call, external document processing, paid provisioning or real-world financial action occurred in this task.

Requires B review before merge. The documentation PR's checks are reported in GitHub; no review, merge or feature freeze is claimed.
