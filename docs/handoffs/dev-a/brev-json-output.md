# Developer A: Brev structured-output truncation

Task: fix the Brev text adapter after the user's consented live five-clause evaluation completed only one case and truncated four. Preserve hosted behavior, source validation, pending review/approval and private routing.

Branch: `codex/dev-a/brev-json-output`. Starting/required contract commit: `bd143a373bf4232d7d9a137fee3c5e9087b1aab2` (current fetched main, including optional Brev support). Owner: Developer A. Allowed files: `backend/clausegraph/providers.py`, `backend/tests/test_brev.py`, the shared mock response helper in `backend/tests/test_api.py`, this handoff, and `docs/NVIDIA_BREV.md`. No frontend, dependencies, schemas or financial engine changes.

Acceptance: bound reasoning for Brev extraction while reserving response space, constrain structured responses to the supplied schema while retaining strict local validation, provide exact source-line citation candidates without changing stored text, and preserve ordinary text drafts, hosted request parameters and incomplete-output rejection. Run focused provider tests, backend regression and Ruff. Recheck the same five synthetic clauses against the user's existing private tunnel under their evaluation consent; no personal documents, hosted inference or new resources.

## Starting evidence

User-provided runtime output: H100 80 GB, driver 580.173.02, Docker 29.8.0; image `nvcr.io/nim/nvidia/nemotron-3.5-lightning-30b-a3b:2.0.9-variant`, digest `sha256:c2b2138e056dcfbd5da634477c3aa2ffcc01a672fc5946422f7a9afc8e315d3f`. Model list and a short non-thinking response succeeded through the private tunnel. The app evaluation reported 1/5 exact fields, 1/5 valid citations/literals, and 5/5 unreviewed outputs withheld. The other four responses reached the token limit; no reasoning trace was captured, so its role remains a hypothesis pending retest.

NVIDIA's model-specific guide recommends `chat_template_kwargs.enable_thinking=false` and `response_format={"type":"json_object"}` for structured output: https://docs.nvidia.com/nim/large-language-models/2.0.10/get-started/advanced/get-started-nemotron-3.5-lightning.html#structured-json-output

## Checks and outcome

Implemented bounded Brev reasoning (2,048 tokens, at most half of max_tokens), schema-constrained JSON, and deterministic source-line citation candidates. Ordinary text requests disable reasoning. Hosted request bodies, strict schema/source validation, pending review/approval, private routing and no-fallback behavior remain unchanged. Prompt-only source spans preserve Unicode, original page offsets, repeated lines and document versions; the persisted Document is not modified. Clarified rule-kind/date/entity guidance and handling of financial facts alongside injected instructions. Adapted the shared mocked API response helper to the Brev prompt format.

Checks run with the root checkout's existing Python virtual environment from this worktree:

- Initial focused regression: 2 expected failures exposed missing structured-output parameters and unbounded reasoning. The first small fix passed all 56 focused tests, but live results exposed further schema/citation issues; no passing extraction claim was made from mocked tests.
- Final `python -m pytest backend/tests -q`: **286 passed, 1 skipped** in 33.42s; PostgreSQL test URL not configured locally. Two existing dependency deprecation warnings. This includes the corrected Unicode/CRLF expected-offset test, hosted compatibility, plain drafts, private routing, consent, schema/incomplete-output rejection and financial gates.
- `python -m ruff check backend scripts`: passed.
- `git diff --check`: passed (Windows line-ending notices only).
- Final `TEXT_PROVIDER=brev BREV_NIM_BASE_URL=http://127.0.0.1:18000/v1 BREV_NIM_MODEL=nvidia/nemotron-3.5-lightning-30b-a3b PROVIDER_RETRIES=0 python scripts/eval_nemotron.py --live --consent-external`: **exit 1**, deliberately retained for remaining evidence failures. No .env or hosted credentials loaded into this worktree. No new resources provisioned.

Latest live result (2026-09-20 UTC): **5/5 exact structured fields, 3/5 evidence-valid cases, 5/5 unreviewed outputs withheld, zero truncations or schema errors**. Case runtimes: rent 7.516s, income 6.969s, pending-grant 6.797s, ambiguous-date 6.656s, injection-wrong-amount 6.687s.

| Case | Exact fields | Evidence result | Review |
|---|---|---|---|
| rent | yes | supported | pending |
| income | yes | supported | pending |
| pending-grant | yes | supported; approval remains pending | pending |
| ambiguous-date | yes; date remains null | unsupported: model incorrectly flags entity ambiguity for missing date | unresolved |
| injection-wrong-amount | yes | unsupported: model citation offsets do not match and entity ambiguity flagged | unresolved |

The live evaluation is **not fully passing**. Intermediate five-case probes compared disabled reasoning, JSON-schema decoding and bounded reasoning; results varied (2-5 exact field cases and 0-4 evidence-valid cases). The latest result is not a general accuracy estimate or a promise of deterministic model output. Exact source validation was never relaxed, model output was never rewritten to expected answers, and fixtures/expected scores were not changed. The same five native-text synthetic clauses were used throughout the user's consented debugging session; no personal documents, OCR, external evidence checks or messages were processed.

Local main was clean and fast-forwarded to bd143a3 after fetching; its ignored .env still uses hosted NVIDIA by default and retains the configured optional Brev model. The fix lives in this isolated task branch pending PR review/integration. Full PostgreSQL/frontend/browser verification is left to the existing CI job; it is not claimed from this local run. Browser Brev consent remains Developer B's separate task. Keep the synthetic fixture walkthrough as the reliable demo and treat live extraction as requiring human review with visible failure cases.
