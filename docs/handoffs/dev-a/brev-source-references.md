# Developer A: Brev source references and entity issues

Task: fix the two remaining live extraction failures without weakening evidence or financial gates. Developer A owns this backend follow-up. Branch: `codex/dev-a/brev-source-references`. Starting/required main: `9570a947cb2786230e92ad76ecd70d72f95365f2`, including merged PR11 and PR12. Allowed files: `backend/clausegraph/providers.py`, `backend/tests/test_brev.py`, the mock response helper in `backend/tests/test_api.py`, `docs/NVIDIA_BREV.md`, and this handoff. No public schemas, generated types, frontend, dependencies, fixture expectations or engine changes.

The previous fix was merged while this follow-up was being tested. Pre-push rejected stale ancestry. The unpushed follow-up commit `15a612a` remains preserved on its historical branch. Only its implementation/tests/setup guidance were applied to this fresh main checkout; the old task handoff remains unchanged. No force push, reset or discarded contributor work.

## Implementation

The private Brev response selects `evidence_span_ids`. Python resolves them against the current document to immutable original quotes, versions, pages and character offsets. Unknown IDs, empty references and model-authored provenance fail locally. No fuzzy matching or offset repair. Unicode/CRLF and repeated-line tests exercise the resolved public Evidence objects and confirm that source documents remain unchanged.

Explicit `entity_match_issues` describe sourced party/account conflicts, multiple existing-event matches or unclear cash direction. Missing dates/amounts remain nullable facts. Actual issues map to the existing entity-ambiguity gate; invalid issue categories are rejected rather than silently cleared. The model still must select relevant passages and classify facts correctly. Hosted requests and public contracts are preserved, and all evidence/review/approval/consent/financial gates still apply.

## Validation

Before transfer (same implementation): focused Brev tests **49 passed** in 4.42s; full backend **298 passed, 1 PostgreSQL skip** in 34.22s, two existing dependency warnings; Ruff passed; in-memory public OpenAPI matched the checked-in contract. Tests cover unknown/cross-document source IDs, attempted forged evidence/approval, fractional or incorrect amounts, unsupported dates, genuine entity conflicts, missing dates and unchanged stored source text.

The previous implementation's live result was 5/5 exact fields but 3/5 evidence-valid cases, with all five withheld from execution. That is historical evidence in [brev-json-output.md](brev-json-output.md), not validation of this follow-up.

The user explicitly restarted the existing GPU and requested a retest. Brev refresh succeeded; the instance currently reports STARTING. Once available, restart its existing `clausegraph-nim` container, reopen the private loopback tunnel and rerun only the same consented five synthetic native-text clauses. No new resources, hosted inference, personal documents or external messages are authorized by this retest. Live result pending.

## Remaining limits

Live outcome and integrated CI pending. Browser Brev consent remains a separate B assignment. No general accuracy or OCR claim follows from this five-case corpus. A non-passing model response stays blocked; do not alter expected fixture scores or validators to report success.
