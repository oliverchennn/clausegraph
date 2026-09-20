# Developer A: incomplete source processing and live test results

## Assignment and synchronization

Continuation of the user's authorized stage 0 hosted NVIDIA test. After the two synthetic fixtures, hosted extraction/evidence/OCR destination and quota implications were explained, the user said: "do you need me to turn the brev gpu on? if not do the test". The configured hosted route needs no Brev GPU. Stage 0 permits fixing reproduced blockers in A-owned code.

PR25's preparation commit `08f5102` was squash-merged as `c64b108` while the live tests and fix were running. The first synchronization exposed that merge; the pre-push hook blocked the stale branch. Its attempted merge was aborted, preserving the tested fix in local commit `40abb77` and all peer work. PR25's description was restored to its actual preparation scope after an attempted update raced with its merge. No old branch was republished or force-pushed.

Fresh branch: `codex/dev-a/incomplete-source-guard`; worktree: `.worktrees/dev-a-incomplete-source-guard`. Start: fetched `f5f93bd5085bbbd7cdb3663348a26b620c18631a` (PR27), including PR28's destination-aware browser consent, PR25's preparation record and PR26's trace wording correction. Clean root main was fast-forwarded. Historical handoffs, including `live-demo-closeout.md`, are unchanged. The new handoff was recorded before transferring the fix.

Allowed paths: `backend/clausegraph/api.py`, `backend/tests/test_api.py`, this handoff, `docs/EXTRACTION_CHECK.md`, `docs/DELIVERY_CHECKPOINT.md`, `docs/DEMO.md`, `docs/RESUME.md`, and `docs/WORKSTREAMS.md`. Required history/uncertainty/provider contracts are already merged in the starting commit; no new schema, generated type, frontend, dependency, engine arithmetic, original fixture, migration or deployment changes are assigned. This is the same bounded stage 0 correction, not a future-stage feature.

## Actual hosted results

Two requests ran on `08f5102` through the existing real local API/storage/worker/provider code. Both documents describe a fictional utility payment of 12345 cents due 2026-09-28. The observation runner used a dedicated SQLite database/private originals in the earlier worktree's ignored `.data/live-hosted`, a 120-second per-request timeout and zero retries. No prompts, provider payloads, schemas, models or destination settings were changed.

Destination: `https://integrate.api.nvidia.com/v1`; text model `nvidia/nemotron-3.5-lightning-30b-a3b`; evidence/OCR model `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`. Only the existing server-side key was read; it was not displayed or copied into reports.

| Fixture / stage | Request result | Worker elapsed |
|---|---|---|
| Native text -> extraction | Timeout after 120.250 seconds; failed job, no response or candidate rules. Evidence check never reached | 120.469 seconds |
| Scanned PDF -> OCR | HTTP 503 after 0.250 seconds; failed job before transcription/extraction, no OCR text or rules | 4.781 seconds including local PDF processing |

Neither request yielded an accuracy/citation score, correction, actual human review or a successful live browser flow. This records failures at that time, not general provider unavailability or a credential diagnosis. No GPU, alternative model, cloud storage, personal document or paid provisioning was used. The original scan was visually inspected using the PDF skill and Poppler: one legible image-only page with the expected amount/date and no extension/approval. Agent inspection is not human attestation of a model result.

## Reproduced defect and implementation

After each failed job, the original API could calculate an empty-ledger `confirmed` plan without a warning; the rule/action/event review queue was empty. No extracted money was compiled, but missing extraction incorrectly looked like confirmed financial completeness.

Saved and preview plans now become `unresolved` while a source is uploaded/extracting/failed, or has no current-version rule representation and is not ready. An explicit warning identifies incomplete source processing and states that displayed cash covers recorded facts only. No unknown amount is invented. Verification rejects such workspaces with HTTP 409 before computation/history persistence, including when an older saved plan was confirmed. After extraction, existing rule/evidence/approval gates continue to apply; supported review restores normal planning. Successful mocked recovery produces 87655 ending cents from 100000 opening cents and the source-backed 12345-cent bill.

The review queue remains rule/action/event guidance; an empty queue does not prove document processing is complete. Public schemas/generated types and nominal money/verification algorithms are unchanged. HTTP 409 uses the existing error surface; consumers should surface its upload/processing guidance. Historical saved results are not rewritten; recalculate the current plan after updating the application.

## Checks before synchronization

- Five new regression cases all failed against the original code and passed after the fix (4.43 seconds): no consent, queued/failed/empty extraction, session isolation, read-only preview/rejected verification, retry and supported-review recovery.
- Full backend on the initial fix: 348 passed, nine PostgreSQL-dependent skips, two existing Starlette/AnyIO warnings in 56.65 seconds. Ruff passed; app OpenAPI exactly matched committed OpenAPI.
- Locked Node 22.23.2/npm 10.9.8 install; all 19 then-existing real-API Chromium tests passed in 1.7 minutes on isolated ports 8055/3055. This predates merged B consent/trace changes; rerun their expanded browser suite on the fresh branch.
- Both real persisted live failure states were replayed locally with provider requests forbidden: confirmed -> unresolved; verification HTTP 409; successful source/original/history/session deletion; zero remaining test sessions and zero additional provider calls. Synthetic reports remain in the earlier worktree's ignored `.data/live-hosted/*-report.json`.
- Original fallback reports remain valid: eight-case UNSAFE, same fixed schedule SAFE with 40000 hypothetical extra cents, five expected semantic gate outcomes. No live result is substituted into them.

## Current acceptance and remaining gates

Transfer only the reviewed API/tests delta after verifying main made no intervening edits to those files. Preserve merged B/C changes and historical handoffs when refreshing shared status. Run backend/Ruff/contract checks and the current full browser suite, then documentation links, whitespace, ownership and current-main checks. Publish a fresh PR for B review and green CI; do not merge or start a later stage without those gates.

Successful hosted extraction remains outstanding after the timeout/503. Human source review, live browser inference and spoken rehearsal are not claimed. B's browser consent implementation is merged as PR28; its recorded simulated route tests do not establish live provider success. No user-service restart or deployment is part of this task.

## Final fresh-branch validation

- Verified no intervening main edits to the two backend paths before transferring the exact tested delta; all peer and historical handoffs remain unchanged.
- `python -m pytest backend/tests -q`: 348 passed, nine PostgreSQL-dependent skips, two existing warnings in 53.15 seconds. `python -m ruff check backend scripts`: passed. Root Python 3.12.14 environment; no disposable PostgreSQL URL is configured locally.
- `create_app().openapi()` exactly equals committed `docs/openapi.json`; no generated contract drift.
- Pinned Node 22.23.2/npm 10.9.8 `npm ci --no-audit --no-fund`: 439 packages in 37 seconds, lockfile unchanged.
- `TEXT_PROVIDER=nvidia E2E_API_PORT=8056 E2E_WEB_PORT=3056 npm run test:e2e`: all 28 real-API Chromium tests passed in 2.0 minutes, no retries. Includes B's nine newly merged consent cases, supported-review recovery, history, nominal/scenario/verification, privacy, keyboard and mobile checks. Synthetic HTTP fixtures supply inference in these browser tests; no additional live calls occurred.
- Eight A-owned changed/new paths, 51 resolving relative Markdown links, no trailing whitespace/conflict markers; `git diff --check` passed. Fetched again before publication; main remains the starting `f5f93bd`.

The fresh PR's CI provides final PostgreSQL, generated-type, frontend build and platform checks. B review and green CI are still required; no merge is claimed by this handoff. This task stops after publishing the tested correction and actual live results.
