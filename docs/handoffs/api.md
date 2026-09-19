# API/infrastructure/integrations handoff
Branch: codex/api; checkout `.worktrees/api`. Resumed implementation and completed 29 meaningful API/storage/worker/provider tests. Integration owner merges this lane; no live sponsor service is claimed tested.

Completed:
- Server-only Settings with explicit local SQLite/private-file fallback and production PostgreSQL/private Spaces requirements.
- SQLAlchemy Core metadata and transactional session snapshots; versioned documents/rules, explicit actual/projected event records, plan history and projected daily balances; leased PostgreSQL job queue with guarded worker completion and deletion support. Root owns migration generation using this metadata.
- Private original storage adapters for local files and Spaces; no public object URLs or bearer tokens in keys.
- Configurable httpx Nemotron extraction/entity linking and draft wording, Gemini consequential checks and PDF transcription, ElevenLabs transcription/narration. Bounded retries/timeouts and sanitized failures; no fixture fallback. Synthetic/minimal credential smoke requests are implemented but not live tested.
- FastAPI endpoint implementation for session/workspace/demo/intake/plan/upload/delete/review/jobs/SSE/providers/draft/evidence/audio. create_app supports injected Settings/Store/Providers/Originals. Provider/extraction work remains in a separate worker.
- Same-name changed uploads create document versions under one logical ID, preserve prior original keys, supersede obsolete jobs, and invalidate source-backed results. Upload snapshot/original-key/job metadata commits atomically. Multipart bodies are bounded before parsing for both Content-Length and streamed/chunked requests.
- Evidence confirmation requires an explicit note, accessible hash-matching original, and deterministic quote/amount/date/version/entity checks. Native text is re-read from the original; model-transcribed PDF pages require explicit original-page human confirmation. Mixed PDFs preserve native pages and only OCR unreadable pages. Every extracted rule is forced consequential.
- Known expense/actual events survive source deletion or replacement with dangling source IDs, forcing engine review rather than silently improving cash. Deleted-source titles become generic to remove extracted wording. Source deletion purges current and historical rules, originals, jobs and prior plan narratives; whole-session deletion clears all records and cached plans.
- Bounded 128-entry/10-minute session+revision+request plan cache. Monotonic reset revisions reject stale in-flight work. Lease ownership/expiry and session revision guard worker completion. Reviewed fact corrections update matching projected events/effects; pending candidate events compile from current reviewed source values.
- Workspace and scoped history chart points are read back from persisted daily_balances, preserving explicit projected labels separately from actual financial events.

Interfaces:
- `/api/sessions` POST SessionCreate -> Workspace (201); bearer=session_id.
- `/api/intake` POST -> Workspace; `/api/plan` POST -> PlanResult; `/api/rules/{id}` PATCH -> Workspace; multipart `/api/documents` file+consent -> UploadResponse (201).
- `/api/providers` GET and `/api/providers/smoke` POST -> list[ProviderStatus]; smoke cache avoids repeated paid requests within 30 seconds.
- `/api/audio/transcribe` multipart file+consent -> TranscriptResponse(facts_confirmed=false); `/api/audio/checklist` AudioRequest -> audio/mpeg.
- `/api/actions/{id}/draft` accepts optional DraftRequest; deterministic local draft by default, explicit consent for Nemotron.
- `/api/health` -> HealthResponse. DELETE session -> DeleteResponse. Evidence export -> Markdown.
- GET `/api/documents/{id}/original?version=N` -> authenticated original attachment. Optional version selects retained history; unavailable/corrupted originals fail closed. Synthetic originals are labeled fixture bytes.
- GET `/api/history` -> list[PlanResult], newest 30 session-private runs with persisted chart series. Existing canonical PlanResult includes assumptions added by integration.
- Metadata tables: sessions, document_versions, rule_versions, financial_events, scenario_runs, daily_balances, jobs. Root has approved design and is creating migrations.

Checks run (2026-09-19):
- `C:\Users\vzhu0\PycharmProjects\clausegraph\.venv\Scripts\python.exe -m pytest backend/tests/test_api.py -q` — **29 passed in 7.73s**. Two dependency deprecation warnings from Starlette TestClient/httpx/AnyIO; no failed checks.
- `C:\Users\vzhu0\PycharmProjects\clausegraph\.venv\Scripts\python.exe -m ruff check backend/clausegraph/api.py backend/clausegraph/config.py backend/clausegraph/providers.py backend/clausegraph/storage.py backend/clausegraph/worker.py backend/tests/test_api.py` — **passed**.
- Tests cover full mocked HTTP Nemotron/Gemini extraction→review→plan, no self-granted review/approval, missing provider+SSE, proof confirmation and original tampering, session isolation, duplicate uploads/version history, projected/actual persistence, chart readback/history/cache, approval denial/invalidation, edited facts, conditions, worker stale revision/lease expiry, superseded jobs, deletion/reset, bounded retries, schema rejection, short text and mixed PDFs, upload-size guards, audio consent/no automatic financial mutation, unsent drafts.
- No PostgreSQL, browser, or live sponsor checks run in this lane. Root owns PostgreSQL CI/browser/full integration and deployment validation.

Remaining / integration:
1. Integrate the engine agent's follow-up action/event evidence semantics, retained-expense unresolved state, and bounded PDF subprocess changes; then run complete backend suite. Current API tests passed against the prior engine checkpoint. Optimizer ValueError maps to HTTP422.
2. Root must regenerate OpenAPI/types for original/history endpoints. Docker/Compose/DigitalOcean/env/migrations and final sponsor docs now belong to root and are implemented in root shared commits.
3. Live credentials and external deployment validation remain unavailable. Model IDs are configurable; mocked envelopes verify adapter shape but cannot establish that a live account supports a configured model or schema.
4. Multiworker PostgreSQL leases use FOR UPDATE SKIP LOCKED but have not been exercised against a running PostgreSQL server here. SQLite is explicitly a local fallback. Rate limiting/identity federation beyond private bearer sessions is outside this vertical slice.
5. RuleReview intentionally cannot rewrite condition semantics or resolve ambiguous entities automatically; unsupported source provenance remains blocked. Image-only evidence is clearly human-attested, not independently proven by model agreement.

Live status: no sponsor credentials present per root, Docker daemon unavailable. No paid resources provisioned. Official API references consulted: NVIDIA structured generation https://docs.nvidia.com/nim/large-language-models/1.14.0/structured-generation.html; Gemini generateContent https://ai.google.dev/api/generate-content; ElevenLabs STT https://elevenlabs.io/docs/api-reference/speech-to-text/convert.
