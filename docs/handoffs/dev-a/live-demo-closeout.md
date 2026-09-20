# Developer A: live demo closeout

## Assignment

The user asked Dev A to read the updated assignments and begin the next task. Scope is stage 0 `live-demo-closeout` in PR24's `docs/HACKATHON_ASSIGNMENTS.md` at `fab5900f10ea94accd2f80c942044a3adf2a354e`. PR24 was open at task start. It subsequently merged as `e65464cbe2648a2bd43d42829eda75d321476580`; fetched origin again and fast-forwarded clean main and this branch before shared-status edits. This task did not merge PR24 or consume an unmerged runtime contract. Stop after this bounded closeout handoff/PR; live validation remains pending consent.

Branch: `codex/dev-a/live-demo-closeout`. Worktree: `.worktrees/dev-a-live-demo-closeout`. Starting commit: `ca7cde59287e5456a9398965796c873152176491` (merged PR23). Origin was fetched with pruning; clean local main already matched. Existing worktrees, configuration, user data and services are preserved. Required merged contracts are PR19 history (`7088b812c1da4169b1ad4b4d668bf2536e68e43d`), PR20 uncertainty (`c32f0c8b7c81be1ed2da00ac19a18b414489f499`) and existing provider/consent routes, all in the starting commit.

Allowed tracked paths: this handoff, `docs/EXTRACTION_CHECK.md`, `docs/DELIVERY_CHECKPOINT.md`, `docs/DEMO.md`, `docs/RESUME.md`, and `docs/WORKSTREAMS.md`. Coordinate shared status edits with PR24 rather than overwrite its assignment update. Ignored `.data/` artifacts may contain isolated synthetic setup, validation scripts and reports. No runtime blocker has been observed; any necessary A-owned runtime fix must first name exact paths and regression checks here. No frontend, peer handoff, dependency, generated contract, original fixture, deployment or future-stage changes are assigned.

## Acceptance and validation plan

- Verify exact merged-history CI and recorded independent A review; distinguish this checkpoint from earlier demo evidence.
- Reproduce the offline financial and semantic gate reports; prepare separate native-text and image-only PDF synthetic sources in an isolated local setup.
- Check only configuration presence and selected model/destination without disclosing credentials. External processing requires explicit consent for those destinations; record unavailable native/OCR checks separately.
- Where authorized and available, exercise upload, worker, extraction, review, recalculation, withheld execution and source/session deletion. Record actual fields/citations, corrections and latency; distinguish agent-operated API/browser validation from actual human review or spoken rehearsal.
- Validate missing-consent/failure paths locally with no external transmission. Preserve synthetic labels, integer-cent money, evidence/review/approval separation and conservative source deletion.
- Refresh the demo/checkpoint procedure and current status, check links/whitespace/ownership, publish for B review and green CI. No live success or human rehearsal is assumed from configuration, prior retests or mocked tests.

## Results

Local preparation and checkpoint verification are complete. Live processing of the two prepared fixtures is outstanding: the user was asked for explicit consent to hosted NVIDIA text extraction and evidence/OCR, and no answer has arrived. The roadmap explicitly requires destination-specific processing consent. No external call has been made by this task, and no actual human source review, live browser flow or spoken rehearsal is claimed.

The selected existing configuration is hosted NVIDIA at `https://integrate.api.nvidia.com/v1`, with text model `nvidia/nemotron-3.5-lightning-30b-a3b` and evidence/OCR model `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`. Credential presence and endpoint equality were checked without displaying secrets. Connectivity, latency and extraction accuracy have not been tested. No Brev or alternative provider was substituted.

| Check | Result |
|---|---|
| Exact merged PR23 [CI 35488606919](https://github.com/oliverchennn/clausegraph/actions/runs/35488606919), head `ca7cde59287e5456a9398965796c873152176491` | Green: 352 backend tests in 39.69 seconds including PostgreSQL 17; 19 real-API browser tests in 2.0 minutes; Ruff, OpenAPI/TypeScript drift, frontend typecheck/lint/build and Linux/Windows/macOS clean installs |
| [Recorded independent A review of PR23](https://github.com/oliverchennn/clausegraph/pull/23), exact head `150809d2db82ef216859189467994beaad832739` | No blockers; 19 independent real-API browser passes in 2.1 minutes, desktop/mobile screenshot inspection and ownership/current-main checks. Historical review evidence, not a new browser run in this task |
| `python scripts/install_hooks.py` | Confirmed existing shared hook without replacement |
| `python -m pytest backend/tests/test_history_api.py backend/tests/test_uncertainty_limits.py backend/tests/test_api.py backend/tests/test_brev.py backend/tests/test_extraction_demo.py -q` | 130 passed, 8 PostgreSQL variants skipped, 2 existing Starlette/AnyIO warnings in 41.16 seconds |
| `python scripts/verify_demo.py` and saved JSON assertions | Passed: nominal minimum 5000; UNSAFE 8/8 at worst -40000; separate no-safe-schedule certificate; same schedule SAFE 8/8 with 40000 extra hypothetical opening cents |
| `python scripts/eval_nemotron.py` and saved JSON assertions | Five expected fixture gate outcomes passed; unreviewed execution withheld 5/5; no model accuracy measured |
| `python scripts/prepare_extraction_demo.py --output .data/extraction-demo` | Prepared fictional utility bill, 12345 cents due 2026-09-28, as native text and one-page image-only PDF; PDF verified as one image and zero embedded-text characters; original six financial fixtures unchanged |
| Isolated `.data/local-check.py`, real ASGI/storage/worker with rejecting mock HTTP transport | Both prepared files uploaded without consent: review required, no job or provider call, no compiled rules/events; source/original retrieval revoked, histories empty, session deletion returned 401 on later reads |

Local commands use root `.venv/Scripts/python.exe` (Python 3.12.14). No disposable `POSTGRES_TEST_URL` is configured; PostgreSQL results above come from exact merged CI. Tests use mock provider transport and do not measure live inference. The first ignored local runner lacked a Windows multiprocessing main guard, causing PDF setup to fail; the guard was added and the two-file check passed. This was a validation-harness issue, not an observed application defect; no runtime fix was needed.

Saved synthetic reports are in this worktree's ignored `.data/fallback/verify-demo.json`, `.data/fallback/semantic-gates.json` and `.data/local-check-ready/report.json`. Fixture preparation refuses to overwrite existing files. Local setup uses a dedicated SQLite database and private original-file directory; no user database, cloud storage, running app or other worktree was used. The fallback reports were parsed and their proof/money expectations asserted after saving.

Shared records now distinguish the validated history checkpoint from earlier rehearsal evidence and from pending live native/OCR checks. The extraction procedure names separate text/evidence consent, isolated settings and truthful agent-operated versus human review labels. No interfaces, dependencies, generated files, original fixtures, financial arithmetic or B/C files changed.

Documentation validation: all six changed/new paths are A-owned under the fetched base policy; all 47 relative Markdown links resolve; no trailing whitespace or conflict markers. `git diff --check` passed with existing Windows line-ending normalization notices. No full local frontend rerun was needed for these documentation-only edits; exact merged CI and independent historical review are explicitly attributed above.

## Remaining gates

This preparation record may be published as a draft while consent is pending. Live native/OCR results, source-supported corrections, live latency and actual human review must be recorded only after the authorized runs occur. B's destination-aware consent UI and human presenter coordination remain B's separate assignment. No future-stage feature starts in this task. B review and green PR CI remain required before merging this record; they are not claimed by the local checks.
