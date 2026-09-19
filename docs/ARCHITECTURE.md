# Architecture and contract v1

One Next.js frontend calls a modular FastAPI API; one worker imports the same Python modules. PostgreSQL stores session snapshots, versioned document/rule data, financial events, scenario runs and leased jobs. SQLite is an explicitly local development fallback. Private local files or private DigitalOcean Spaces hold originals. Production uses Tiger Data PostgreSQL via DATABASE_URL.

## Processing pipeline
Upload validates PDF/text/CSV size/type, hashes bytes per session and records native page text with quote offsets. Worker extracts typed candidates via Nemotron. Consequential candidates receive Gemini evidence verification; native text absence enables vision only with explicit external-processing consent. Exact quote/amount validation precedes human review. Model agreement alone never marks a rule reviewed. Provider failures surface on jobs; there is no silent live-to-fixture fallback.

Reviewed rules compile into an allowlisted DSL: add an evidenced event, remove a specified payment, shift a specified event, or accelerate an existing obligation. Conditions support eq/gte/lte/exists, but unresolved facts block compilation. Graph edges are requires/triggers/excludes/supersedes/supports; NetworkX checks dependencies/cycles and contradictions. Extraction does not authorize execution.

## Canonical contracts and endpoints
`backend/clausegraph/schemas.py` owns API shapes; FastAPI OpenAPI is exported to `docs/openapi.json` and openapi-typescript generates `frontend/src/lib/api-types.ts`. Frontend imports aliases from generated schemas. All money is integer cents, all dates ISO dates. Evidence offsets are page-local, end-exclusive. Every PlanResult persists its typed PlanRequest as `assumptions`, so scenario history and restored UI controls disclose the inputs that produced the result.

Endpoints use `/api`: POST `/sessions` creates an empty session (body `{demo: bool}`; UI explicitly requests synthetic demo); bearer token returned as session_id. GET `/workspace`, POST `/demo/reset`, POST `/intake`, POST `/plan` (PlanRequest -> PlanResult), POST `/documents` multipart file + consent bool (UploadResponse), DELETE `/documents/{id}`, PATCH `/rules/{id}` (RuleReview -> Workspace), GET `/jobs/{id}`, GET `/jobs/{id}/events` SSE, POST `/actions/{id}/draft` (DraftResponse), GET `/evidence/export` Markdown attachment, GET `/providers`, POST `/providers/smoke`, DELETE `/session`. All except health/session creation require `Authorization: Bearer <session_id>`. Session IDs are unguessable bearer credentials; local UI stores only this token. Audio endpoints POST `/audio/transcribe` (file -> text/facts_confirmed:false), POST `/audio/checklist` (-> audio/mpeg), never auto-apply transcription. CORS origins allowlisted.

## Engine interface
`simulate(scenario: Scenario, selected: dict[str,date] | None = None) -> Simulation`.
`optimize(scenario: Scenario, rules: list[Rule], request: PlanRequest | None = None, revision: int = 1) -> PlanResult`.
`build_graph(scenario: Scenario, rules: list[Rule], documents: list[Document]) -> DependencyGraph`.
`extract_native(content: bytes, filename: str, media_type: str) -> list[DocumentPage]`.
`validate_extraction(result: ExtractionResult, document: Document) -> ExtractionResult`.
`compile_rules(result: ExtractionResult) -> ExtractionResult` gates reviewed/supported rules and actions.
`load_demo() -> tuple[Scenario, list[Document], list[Rule]]` in `clausegraph.demo` owned by integration. Start 2026-09-01; day N means start + N days. Events: rent160000 day7; phone6000 day10; loan45000 day12; utilities12000 day15; groceries17000 day18; income90000 day20; device48000 day80. Approved shift moves loan day12 to25; cancel phone removes6000 and accelerates existing device48000. Confirmed baseline min -40000 / end50000; shifted min5000 / end50000.

## Solver
CP-SAT selects actions and execution dates within deadlines, approved/reviewed evidence, dependency ordering, exclusions, essential-service constraints. Lexicographic objectives: seek nonnegative daily balances; maximize minimum daily balance; minimize fees then burden and execute deterministically. Run phases within a bounded deadline, expose FEASIBLE vs OPTIMAL honestly. If nonnegative impossible, maximize minimum to calculate minimum extra cash diagnostic. Any forced forbidden action returns unresolved/infeasible with explanation. Action effects on a shared event conflict unless modeled explicitly; avoid double counting. Date boundaries use [start,start+horizon) and retain all future obligations. Conditional assumptions can only affect a clearly labeled conditional result. Persisted approvals require explicit review endpoint. Plans invalidated by uploads/reviews/deletion/intake and revision checks guard worker results.
