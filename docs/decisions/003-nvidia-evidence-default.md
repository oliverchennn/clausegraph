# NVIDIA-first evidence checks for SteelHacks XIII

Date: 2026-09-19. User requested the best hackathon-funded replacement for required Gemini, preferring free tools to OpenAI.

## Decision

Keep Nemotron Lightning for typed extraction. Default evidence verification and PDF-page transcription to `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` through the same NVIDIA API key. `EVIDENCE_PROVIDER=gemini` explicitly restores the existing Google adapter; there is no automatic provider fallback. No OpenAI account or paid resources are needed for this path.

This is a cost/setup/track-fit choice, not an accuracy benchmark claim. SteelHacks' [Nemotron track](https://steelhacks.org/tracks) explicitly welcomes model-output judging in a larger pipeline. NVIDIA's [Omni catalog](https://build.nvidia.com/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning) currently lists a free endpoint, while the older Nano 12B v2 VL free endpoint is deprecated. Its [model card](https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-nano-omni-30b-a3b-reasoning) covers document intelligence, English OCR, image/text input and JSON output. Account quotas/availability still require a smoke test; free prototype access is not an unlimited production guarantee.

## Alternatives

- Gemini is **also** a listed [MLH prize sponsor](https://www.mlh.com/events/steelhacks-xiii/prizes), and Google offers a [rate-limited free tier](https://ai.google.dev/gemini-api/docs/billing). Keeping it is reasonable for cross-provider diversity, native PDF support or the Gemini prize. It is optional, not excluded for supposedly requiring payment.
- DigitalOcean inference could use eligible credits, but credit applicability/account entitlements require verification. Reusing the already-needed NVIDIA key is simpler for this prototype.
- Snowflake's trial/model APIs are another eligible option, but are unnecessary for this replacement; Tiger Data remains the database.
- OpenAI can support the task, but adds no needed capability for this free-first change. No OpenAI integration was added.

## Safety and bounds

Two passes within the Nemotron family can share failure modes. Agreement never constitutes proof, human review, condition satisfaction or third-party approval. Exact evidence/money/date checks, deterministic optimization, source-page attestation and explicit consent remain unchanged. Verifier model identity is recorded in review notes. Invalid JSON, refusals, truncation, missing/duplicate/unknown rule checks and provider errors fail closed. No hidden retry to another provider occurs.

The browser declares the selected provider with upload consent and the API rejects a stale selection. Queued jobs retain that provider and fail without sending data if server configuration changes before execution. Retrying then requires renewed consent.

Omni consumes image parts rather than PDF inlineData. Local pypdfium2/Pillow rasterization uses a killable 20-second subprocess, four source images maximum per request, 1600px long edge, 2 MiB/image and 20 MiB PDF cap. Only unreadable native pages are transcribed; mixed-PDF native text is preserved. Verification receives original rendered evidence pages when OCR was used. Larger scanned/evidence-page sets must be split, not silently truncated. Native text-only processing retains its existing document limits. OCR page numbering must match exactly; the transcribed content still requires human comparison with the original.

The documented hosted Omni request uses image_url and a bounded reasoning_budget. JSON is requested through a schema-bearing prompt then Pydantic-validated; undocumented guided_json parameters are not assumed supported. Mocks validate protocol/error behavior, not live model accuracy. No live-provider key or paid resource was used during implementation.
