# API/infrastructure/integrations handoff
Branch: codex/api; checkout `.worktrees/api`. Paused at user's model-change/save-credit request; this is an implementation checkpoint, not a validated deliverable.

Completed in this checkpoint:
- Server-only Settings with explicit local SQLite/private-file fallback and production PostgreSQL/private Spaces requirements.
- SQLAlchemy Core metadata and transactional session snapshots; versioned documents/rules, explicit actual/projected event records, plan history and projected daily balances; leased PostgreSQL job queue with guarded worker completion and deletion support. Root owns migration generation using this metadata.
- Private original storage adapters for local files and Spaces; no public object URLs or bearer tokens in keys.
- Configurable httpx Nemotron extraction/entity linking and draft wording, Gemini consequential checks and PDF transcription, ElevenLabs transcription/narration. Bounded retries/timeouts and sanitized failures; no fixture fallback. Synthetic/minimal credential smoke requests are implemented but not live tested.
- FastAPI endpoint implementation for session/workspace/demo/intake/plan/upload/delete/review/jobs/SSE/providers/draft/evidence/audio. create_app supports injected Settings/Store/Providers/Originals. Provider/extraction work remains in a separate worker.

Interfaces:
- `/api/sessions` POST SessionCreate -> Workspace (201); bearer=session_id.
- `/api/intake` POST -> Workspace; `/api/plan` POST -> PlanResult; `/api/rules/{id}` PATCH -> Workspace; multipart `/api/documents` file+consent -> UploadResponse (201).
- `/api/providers` GET and `/api/providers/smoke` POST -> list[ProviderStatus]; smoke cache avoids repeated paid requests within 30 seconds.
- `/api/audio/transcribe` multipart file+consent -> TranscriptResponse(facts_confirmed=false); `/api/audio/checklist` AudioRequest -> audio/mpeg.
- `/api/actions/{id}/draft` accepts optional DraftRequest; deterministic local draft by default, explicit consent for Nemotron.
- `/api/health` -> HealthResponse. DELETE session -> DeleteResponse. Evidence export -> Markdown.
- Metadata tables: sessions, document_versions, rule_versions, financial_events, scenario_runs, daily_balances, jobs. Root has approved design and is creating migrations.

Checks run:
- `C:\Users\vzhu0\PycharmProjects\clausegraph\.venv\Scripts\python.exe -m py_compile backend/clausegraph/config.py backend/clausegraph/storage.py backend/clausegraph/providers.py backend/clausegraph/worker.py backend/clausegraph/api.py` — PASS (2026-09-19).
- No API, worker, provider transport, PostgreSQL, browser, or live sponsor tests run yet. Do not describe this checkpoint as working or integration-tested.

Remaining / limitations (resume here):
1. Cherry-pick shared `ca62083` (RuleReview.evidence_confirmed) and latest dependency checkpoint from root. Implement explicit evidence confirmation with required human note and exact deterministic quote/numeric support; current disputed evidence cannot be approved. Add authenticated GET `/api/documents/{id}/original` for source review. Synthetic source fallback can use fixture bytes/pages.
2. Integrate engine/extraction/graph lane before runtime tests; currently those modules are absent in this checkout. Review synchronization of action approvals and compile_rules; test approved/denied demo approval, custom fact edits, conditions, and rejection.
3. Force consequential=true for all extracted candidate rules (currently model-supplied consequential=false can bypass Gemini verification). Namespace and validate provider responses with mocked httpx transport; verify model schema compatibility live only when credentials exist.
4. Current deduplication is per-session SHA256 and provider smoke caching only. Add explicit revision/request plan-result cache or per-session extraction model/prompt cache. New upload of changed same-name logical document currently gets new ID/version=1; implement version lineage preserving prior originals and source reference invalidation. `set_original` currently updates all versions matching ID, so it must be narrowed before lineage is introduced.
5. Add API isolation, deletion, consent, uploads, duplicate hash, stale revision/lease, provider failure/SSE and actual/projected persistence tests. Check transactional atomicity around upload enqueue/delete/reset and parallel requests; stale worker completion is guarded but these edges are unverified.
6. Add Dockerfiles, Compose, DigitalOcean configuration, .env.example and deployment docs. These were not started. Root controls manifests, migrations, CI, fixtures and generated types.
7. Export canonical OpenAPI with root after API is runtime importable and regenerate frontend types.

Live status: no sponsor credentials present per root, Docker daemon unavailable. No paid resources provisioned. Official API references consulted: NVIDIA structured generation https://docs.nvidia.com/nim/large-language-models/1.14.0/structured-generation.html; Gemini generateContent https://ai.google.dev/api/generate-content; ElevenLabs STT https://elevenlabs.io/docs/api-reference/speech-to-text/convert.
