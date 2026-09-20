# Developer A: restarted Brev live retest

Task: retest the merged source-reference fixes on the user's restarted GPU and record both successful and failing outcomes. Branch: `codex/dev-a/brev-live-retest`. Starting and required implementation commit: `e3143394ccb9f4daef10a41f0800a01e62a5df8e` (PR13). Allowed files: this handoff and `docs/NVIDIA_BREV.md`. Documentation only; no provider, engine, schema, frontend, dependency or fixture changes.

## Environment and authorization

The user explicitly restarted the existing `clausegraph-nemotron` VM and requested testing. On 2026-09-20 UTC, Brev reported RUNNING/READY. Restarted its existing `clausegraph-nim` container and reconnected the private local port18000 to remote loopback8000. The model loaded cached files, then warmed GPU kernels; VM readiness preceded inference readiness by several minutes. Windows `/v1/models` returned `nvidia/nemotron-3.5-lightning-30b-a3b` on the existing H10080GB. No new instance, public port, hosted request or personal document was involved.

Only the same five consented synthetic native-text clauses were sent. The root ignored `.env` was preserved, and text-provider settings were supplied to the evaluation process only. Browser text-provider settings were not switched.

## Live results

No code, prompt, expected scores or validators changed between these two runs. The tested implementation checkout was byte-identical to merged main; the diagnostic run used the fresh `e314339` checkout directly.

| Run | Exact structured fields | Citation/literal validation | Unreviewed execution withheld | Exit |
|---|---|---|---|---|
| Standard evaluation | 3/5 | 5/5 | 5/5 | 1 |
| Diagnostic repeat | 5/5 | 5/5 | 5/5 | 0 |

Standard command: `python scripts/eval_nemotron.py --live --consent-external`, with process-only `TEXT_PROVIDER=brev`, `BREV_NIM_BASE_URL=http://127.0.0.1:18000/v1`, `BREV_NIM_MODEL=nvidia/nemotron-3.5-lightning-30b-a3b`, `PROVIDER_RETRIES=0`. The first run reported field mismatches for rent and injection-wrong-amount. Its standard report does not contain actual extracted fields, so the exact differing field or rule count was not retained and must not be guessed. Case durations were 9.265, 6.953, 6.297, 6.610 and 6.468 seconds.

The diagnostic repeat called the same `scripts.eval_nemotron.evaluate(live=True)` with a read-only score wrapper that recorded each expected and actual kind/amount/date. All matched: rent obligation/72500/2026-09-12; income obligation/91025/2026-09-21; grant benefit/30000/null; ambiguous-date obligation/4000/null; injection obligation/6000/2026-09-11. Case durations were 6.718, 6.453, 6.547, 6.688 and 6.547 seconds. This diagnostic reporting did not modify the request or scoring rules. Both original problem cases passed citation validation in both runs. All rules remained pending review and no events/actions compiled in either run.

Raw reports are local temporary artifacts: `%TEMP%/clausegraph-brev-source-references-live.json` and `%TEMP%/clausegraph-brev-source-references-diagnostic.txt`. They contain synthetic results only, no keys or model reasoning traces.

## Repository and checks

PR13 was merged while runtime setup continued. Local main was fast-forwarded to `e314339`, preserving ignored configuration. An accidentally duplicate draft PR14 was closed after verifying it contained the identical already-merged commit; its stale-main ownership failure was not an application failure. This record uses a fresh branch and leaves historical handoffs unchanged.

The merged implementation's push verification run35481833546 passed the full verification job (including PostgreSQL, contract drift and browser tests) and clean installs on Linux, Windows and macOS. The later duplicate-PR verification run35482070796 also passed application verification/clean installs but failed ownership because its base already contained the squash-merged fix. Earlier implementation-local checks were 298 backend passes/1 PostgreSQL skip and 49 focused Brev passes; these are historical checks, not new tests for this documentation-only task.

This documentation task passed `git diff --check`. No application code changed, so application tests were not rerun for prose edits. The standard live evaluation's nonzero exit remains recorded above despite the passing repeat.

## Limits and handoff

These observations confirm functioning GPU inference and improvement of the two citation failures, not repeatably perfect extraction. Across ten attempts on five repeated clauses, 8/10 matched expected structured fields and 10/10 passed citation/literal checks; these are observations on a tiny tuned corpus, not general accuracy estimates. Missing facts, model classification mistakes and source selection still require human review. No OCR, hosted model evidence-check accuracy, human review flow, arbitrary upload or full live browser demonstration was tested.

The existing VM and private tunnel remain running for the user. Stopping only the container does not stop VM compute billing. Stop the VM in Brev when no longer testing; allow time for model startup and reconnect the tunnel before rehearsing. Browser Brev consent remains Developer B's separate assignment, and the local synthetic demonstration remains the fallback.
