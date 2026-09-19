# Developer A: NVIDIA hosted setup and optional Brev

Task: explain NVIDIA API-key setup, prepare optional Brev-hosted Nemotron, and update environment configuration. Hosted NVIDIA remains the default. No VM provisioning, spending, live inference or frontend implementation is authorized by this setup task.

Branch: codex/dev-a/nvidia-brev. Starting/required main commit: 4e2725a (includes PR6 backend contract and PR7 frontend snapshot). Owner: Developer A, user's agent. Allowed paths: backend configuration/providers/API/worker/schemas and tests; scripts/eval_nemotron.py; .env.example and ignored local .env; deploy/brev/; generated docs/openapi.json and frontend/src/lib/api-types.ts; shared setup/workstream/resume docs; this handoff. No dependencies or B-owned source changes.

Interfaces: preserve hosted defaults; optional text_provider=brev uses a loopback SSH tunnel without forwarding NVIDIA credentials. Evidence/OCR retains its selected hosted provider. Brev upload/draft requires explicit text-provider consent; queued work rejects changed routing. Regenerate API contracts for optional consent fields. B owns any future consent UI and consumes this contract only after merge.

Acceptance checks: mocked hosted/Brev routing, credential separation, missing configuration, provider failures, consent mismatch, queued route changes, strict extraction gates; full backend regression/Ruff; generated contract drift and frontend types. Validate setup templates without provisioning. Record results below before commit.

## Completed

Hosted NVIDIA stays the default. Added optional private Brev text routing, separate hosted evidence/OCR, named upload/draft consent and queued route/model pinning. No hosted API key or environment proxy reaches the Brev tunnel. No automatic fallback. Existing local schema validation/review/approval/financial gates remain intact. Regenerated OpenAPI and TypeScript for the optional consent fields. The synthetic CLI evaluation reports the actual selected provider/model.

Added docs/NVIDIA_BREV.md, a manual GPU-VM compose template with a required image selection and loopback binding, and environment examples. Updated both root and task-worktree ignored .env files with missing Brev settings only, preserving existing values. A hosted NVIDIA credential is present; its value was neither printed nor live-tested. The files remain ignored. No populated env file or private credential is staged; the scan excludes the existing public local-only example password.

Updated shared roadmap/checkpoint to reflect PR6/PR7 already merged and require fresh branches. B can work on current demo polish independently. Optional Brev UI must show both processing recipients and send named text consent after this contract merges; until then browser uploads remain in hosted mode. No B source, browser test, handoff, lockfile or dependency changed.

## Exact validation

- Focused pytest: backend/tests/test_brev.py, test_evidence_providers.py, test_semantic_eval.py:55 passed in6.28s, all HTTP mocked.
- Full python -m pytest backend/tests -q:282 passed,1 PostgreSQL skip in39.62s; two existing dependency deprecation warnings. No PostgreSQL test URL configured locally.
- Ruff backend/scripts:passed. OpenAPI equals runtime schema; regenerated TypeScript equals checked-in output.
- Node22.23.2/npm10.9.8: npm ci --no-audit --no-fund succeeded (439 packages). Initial sandbox cache access returned EPERM; retry with approved cache access succeeded without lock changes.
- npm run typecheck, npm run lint, npm run build:passed.
- Real-API npm run test:e2e on ports8127/3127 with hosted provider keys disabled:9 passed,2 failed in3.0m. Failures at review-queue.spec.ts:22 (Evidence review select locator) and :87 (missing queue error alert) exactly match starting-main CI run35476332612. The five workspace/verification regression flows passed. B owns investigation/fixes; no full green verification claimed.
- python scripts/eval_nemotron.py without live flags:offline fixture gates passed;3 exact fixture candidates,2 deliberately faulty candidates,all5 unreviewed outputs withheld. No model accuracy measured.
- docker compose --env-file deploy/brev/.env.example -f deploy/brev/compose.yaml config --quiet with an explicit validation-only image placeholder:passed. Only configuration parsed; no image pull/container/VM. Local Docker config access warnings did not prevent syntax validation.
- git diff --check:passed. All20 staged paths match Developer A ownership from origin/main's policy; populated env files are ignored and private-credential scan passed.

## Remaining limits and handoff

Live GPU/model compatibility, hosted credential validity, extraction accuracy and OCR remain unverified. User chooses a supported pinned Nemotron image/GPU before any provisioning. Brev requires an already-running private SSH tunnel in the backend's network namespace; the app's Docker Compose stack is not supported for that optional loopback route. Local API/worker and the synthetic CLI are supported. NIM JSON is requested in the prompt and strictly validated locally, not claimed to use every backend's constrained-decoding dialect.

Publish this A branch for the friend's review without merging failing checks. Remote PostgreSQL/multiplatform checks run in CI and are not claimed here. Full verification remains blocked by the two pre-existing B browser failures. B starts codex/dev-b/demo-polish from fetched main with a new B handoff, handles those failures first, then optionally implements Brev consent after this contract is merged. No remaining roadmap features begin automatically.
