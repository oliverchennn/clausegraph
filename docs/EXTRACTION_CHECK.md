# Synthetic extraction check

This is a prepared validation procedure, not a claim of live success. Run `python scripts/prepare_extraction_demo.py` to create a native text document, an image-only scanned PDF and expected fields under ignored `.data/extraction-demo`. Preparation is local and refuses to overwrite existing files. Use a new `--output` directory for another set. Both sources describe a fictional utility payment of12345 cents due2026-09-28. The original six financial-demo fixtures are unchanged.

## Before a live run

Use only these synthetic documents in a new private session. Confirm explicit processing consent for the actual text destination and the separate evidence/OCR destination before sending either file. The hosted route uses a server-side NVIDIA_API_KEY; the existing Brev text route uses its private tunnel/model while evidence/OCR still uses its separately configured provider. Brev browser runs wait for B's destination-aware consent UI. A roadmap assignment, configured credential or prior consent for a different corpus/destination is not consent for this run.

Start API and worker from the same isolated checkout with matching provider/model settings, a dedicated SQLite database and private local original-file directory. Keep cloud storage disabled and use unused local ports. Do not copy another checkout's full `.env`, reuse its sessions, or restart its services. Read only the required server-side provider settings; never paste keys into reports or the browser. A missing key or pending consent is a blocked live check, not a reason to substitute fixture results. No live request is part of fixture generation or ordinary CI.

## Repeat for native text and scanned PDF

1. Create a fresh blank private workspace. Upload the selected synthetic file and explicitly consent to the named provider. Run one file at a time so the result and latency are attributable.
2. Observe queued -> running -> completed or failed. Record both providers, exact models/destinations, date, elapsed time, timeout/retry settings and any failure. Record what was actually observed; synchronous worker execution does not establish that a browser displayed every intermediate state. A completed job alone is not accuracy evidence.
3. Compare extracted kind, amount, date, direction, source quote/page/version and approval state with expected.json. For the scan also inspect OCR text against the visible original. Record every omission, mismatch, withheld rule and human correction.
4. Confirm unreviewed candidates remain withheld from confirmed planning. Open the review queue and original; correct only source-supported facts and complete human review. For image-only pages, keep the original-page human attestation outstanding until a person checks the scan. Record agent-operated or scripted review-path tests as such, not as actual human review. A utility obligation does not imply approval of a payment extension.
5. Recalculate through the normal UI, confirm integer-cent cash accounting and source links, and verify the refreshed queue. Record resulting behavior rather than assuming successful extraction makes a safe plan.
6. Exercise a visible failure without external data: upload without consent in another blank session and confirm no provider job is sent and the source still needs review. Existing protocol tests separately cover unavailable/malformed provider responses.
7. Delete each test source/session and verify its evidence and historical narratives are removed, while conservative retained expenses are handled by the established deletion flow.

Report native and scanned outcomes separately. Two documents of one synthetic clause are a reproducible demo check, not a representative accuracy benchmark. The existing five-case semantic fixture evaluation is separate from OCR and human-review validation. Missing credentials leave the live portion unverified; they do not block the synthetic financial demonstration.

## Stage 0 preparation at the merged history checkpoint

A's [closeout handoff](handoffs/dev-a/live-demo-closeout.md) records preparation on application commit `ca7cde5`, subsequently updated with documentation-only PR24 (`e65464c`). Both generated files passed local upload-without-consent checks: no job, no provider request, no compiled events, review required, and successful source/original/session deletion. These checks use the real local API/storage/worker with a rejecting mock transport, not live inference. The PDF contains one image and zero embedded-text characters.

| Measurement | Current result |
|---|---|
| Native text extraction/evidence | Not run; explicit consent for the two fixtures and selected hosted NVIDIA destination is pending |
| Scanned PDF OCR/extraction/evidence | Not run; same consent gate, followed by original-page human verification |
| Exact selected models | Text: `nvidia/nemotron-3.5-lightning-30b-a3b`; evidence/OCR: `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` |
| Selected destination | Hosted NVIDIA, `https://integrate.api.nvidia.com/v1`; credential presence checked, connectivity not claimed |
| Human source review / live browser / spoken rehearsal | Not performed in this preparation task |

The prepared sources and local reports are ignored artifacts in A's isolated worktree under `.data/extraction-demo`, `.data/local-check-ready` and `.data/fallback`. Regenerate them on another machine. Do not infer live success from the passing local gates or the historical five-clause Brev retest.
