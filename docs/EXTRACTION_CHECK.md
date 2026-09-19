# Synthetic extraction check

This is a prepared validation procedure, not a claim of live success. Run `python scripts/prepare_extraction_demo.py` to create a native text document, an image-only scanned PDF and expected fields under ignored `.data/extraction-demo`. Preparation is local and refuses to overwrite existing files. Use a new `--output` directory for another set. Both sources describe a fictional utility payment of12345 cents due2026-09-28. The original six financial-demo fixtures are unchanged.

## Before a live run

Use only these synthetic documents in a new private session. A server-side NVIDIA_API_KEY and an explicitly consented NVIDIA upload are required. Start API and worker with the configured provider; never paste keys into reports or the browser. A missing key is a visible blocked check, not a reason to substitute fixture results. No live request is part of fixture generation or ordinary CI.

## Repeat for native text and scanned PDF

1. Create a fresh blank private workspace. Upload the selected synthetic file and explicitly consent to the named provider. Run one file at a time so the result and latency are attributable.
2. Observe queued -> running -> completed or failed. Record provider/model/configuration, date, elapsed time and any failure. A completed job alone is not accuracy evidence.
3. Compare extracted kind, amount, date, direction, source quote/page/version and approval state with expected.json. For the scan also inspect OCR text against the visible original. Record every omission, mismatch, withheld rule and human correction.
4. Confirm unreviewed candidates remain withheld from confirmed planning. Open the review queue and source; correct only source-supported facts and complete human review. A utility obligation does not imply approval of a payment extension.
5. Recalculate through the normal UI, confirm integer-cent cash accounting and source links, and verify the refreshed queue. Record resulting behavior rather than assuming successful extraction makes a safe plan.
6. Exercise a visible failure without external data: upload without consent in another blank session and confirm no provider job is sent and the source still needs review. Existing protocol tests separately cover unavailable/malformed provider responses.
7. Delete each test source/session and verify its evidence and historical narratives are removed, while conservative retained expenses are handled by the established deletion flow.

Report native and scanned outcomes separately. Two documents of one synthetic clause are a reproducible demo check, not a representative accuracy benchmark. The existing five-case semantic fixture evaluation is separate from OCR and human-review validation. Missing credentials leave the live portion unverified; they do not block the synthetic financial demonstration.
