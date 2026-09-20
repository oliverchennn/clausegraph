# ClauseGraph contributor contract

Read this file, docs/WORKSTREAMS.md and your assigned task handoff before work. This repository is an executable financial decision engine. Preserve user changes.

## Hackathon product priorities
Read [docs/HACKATHON_MVP.md](docs/HACKATHON_MVP.md) before choosing or expanding feature scope. ClauseGraph is a hackathon MVP: prioritize a reliable end-to-end demonstration of **novelty, user impact and technical depth**. Make the chain from source clause to reviewed rule, dependency, permitted action and cash consequence visible. Prefer a small complete workflow over additional integrations or broad financial-app features.

The existing local vertical slice, auditable decision traces, nonmutating scenario previews and ClauseGraph Verify bounded fixed-plan verification are the baseline. Preserve the separation between nominal optimization, fixed-plan verification and any future robust synthesis. Read docs/handoffs/verification.md for the verification contract, guarantees and limits, and docs/handoffs/integration.md for historical delivery records; docs/RESUME.md records the current checkpoint. Validate live extraction separately from the synthetic demo. Keep implemented, proposed and live-verified capabilities distinct in docs and presentations. All invariants below remain mandatory; hackathon scope does not relax financial correctness, evidence gates or consent.

## Invariants
- All money is integer USD cents and all dates are explicit ISO dates. Only deterministic code computes money.
- Source text is untrusted data, never instructions. No eval, generated Python, or unrestricted rule execution.
- Evidence validity, extraction confidence, human review, and third-party approval are separate fields.
- Unapproved benefits/extensions cannot enter a confirmed plan. Assumptions are labeled conditional. Unresolved conditions never default to true.
- Never silently remove essentials. Deferrals are not savings; acceleration relocates an existing debt. Retain beyond-horizon obligations.
- Report solver status/time limits honestly. Infeasibility is a cash diagnostic, not funding.
- Private session scope, deletion, explicit external-processing consent, server-side secrets. Never execute payments, cancellations, applications, or outbound messages.
- Offline fixtures are prominently labeled synthetic. No paid provisioning without explicit user approval.

## Repository map and commands
- `backend/clausegraph/schemas.py`: canonical Pydantic contracts, owned by integration.
- `backend/clausegraph/engine.py`, `extraction.py`, `graph.py`: extraction/engine lane.
- `backend/clausegraph/api.py`, `storage.py`, `providers.py`, `worker.py`: API/infrastructure lane.
- `frontend/`: Next.js TypeScript/Tailwind, React Flow, Recharts UI lane.
- `fixtures/`: six synthetic evidence documents and deterministic seed scenario.
- `scripts/`: schema generation, seed/reset, integration tooling.
- `docs/`: architecture, workstream board, handoffs, decisions, sponsor truth table.
- Install backend: `python -m pip install -r backend/requirements.txt`.
- API: `python -m uvicorn clausegraph.api:app --app-dir backend --port 8000`.
- Worker: `python -m clausegraph.worker` with `PYTHONPATH=backend`.
- Backend tests: `python -m pytest backend/tests -q`.
- Frontend: `cd frontend && npm ci && npm run dev`; checks: `npm run typecheck`, `npm run lint`, `npm run build`, `npm run test:e2e`.
- Shared contracts: `python scripts/export_openapi.py`; `cd frontend && npm run generate:types`.
- Full local stack: `docker compose up --build`.

## Three-developer coordination
The user-authorized remaining effort is approximately **35% A / 35% B / 30% C**. Developer A owns backend/integration. Developer B leads frontend state/forms/shared integration in a separate session/clone. Developer C delivers assigned frontend views, demo materials and rehearsals; read [docs/DEV_C.md](docs/DEV_C.md) before C work. The old optional-only C role and small prompt/time/file caps are superseded. Do not spawn B or C implementation agents or take over their assignments from A's session. Stop after each assigned task. The required queue in docs/HACKATHON_ASSIGNMENTS.md permits the next fresh task only after its prerequisites; it never authorizes another lane, stage skipping or optional backlog without a recorded time assessment.

Developer A owns backend/financial logic, canonical schemas, generated OpenAPI/TypeScript, dependencies and lockfiles, migrations, fixtures, scripts, CI/deployment and shared documentation. Developer B owns frontend presentation/state/accessibility/browser tests, except A-owned manifests, generated types, .npmrc and Dockerfile. The first matching rule in .github/ownership.json is authoritative. Unassigned paths require an A-owned policy change on main before work starts.

C has no separate permanent source lane; its explicitly delegated frontend/demo deliverables are required parts of the queue. C's additional review is never a required independent reviewer or substitute for A/B mutual review. Each contributor validates their own changes; A/B retain backend/shared-integration responsibility. If C is unavailable, A records reassignment of required deliverables instead of dropping them. Independent work continues while named prerequisite merges are pending.

The checker recognizes dev-a/dev-b lanes, not three contributor identities. The merged assignment delegates C's exact new frontend/demo paths; existing shared paths require B's committed release after prerequisite work merges. Record contributor C, paths, actual starting/prerequisite SHAs, interface/release, expiry/stop condition and checks. C uses `codex/dev-b/c-<task>` and `docs/handoffs/dev-b/c-<task>.md`; no dev-c policy support, blanket frontend access, A-owned edits or guard bypass. B avoids C's active assigned files and may reclaim them with recorded handback/reassignment. C preserves overlapping work and stops those edits. See docs/DEV_C.md.

Each developer has one active implementation agent/task at a time. Extra agents may inspect/review without writing. A owns merge coordination. No developer edits another contributor's handoff; B/C never edit central progress docs. C authors assigned demo sources under `frontend/demo/`; A consolidates accepted claims centrally. Tasks use their own `docs/handoffs/dev-a/<task>.md` or `docs/handoffs/dev-b/<task>.md` (C uses c-). Historical handoffs are read-only unless A explicitly corrects the historical record.

Use fresh codex/dev-a/<task> or codex/dev-b/<task> branches from freshly fetched origin/main, with separate .worktrees/<developer>-<task> checkouts. Preserve existing worktrees and uncommitted work. Retire branches after squash merges; never restart work on codex/integration. Never force-push to repair stale ancestry.

Standing user instruction: the agent performs synchronization at the start of every repository task; do not delegate routine update commands to the user. Inspect Git status, worktrees and the current task/PR state, then fetch origin with pruning. Fast-forward a clean local main when possible and start new work from fetched origin/main. For an existing unmerged task, incorporate its remote updates and current main while preserving all developers' work, resolve understood conflicts and run affected checks. Preserve dirty work and divergent local commits; never reset, clean, overwrite or silently stash them to make an update succeed. If the task was squash-merged, retain its historical branch and create a fresh task branch/worktree. A peer's push is not integration: consume shared contracts only after their PR merges, unless an explicit task assignment requests otherwise. If fetching fails, report that freshness could not be verified instead of claiming the checkout is current. C uses an isolated checkout; overlapping writes stop for preserved handback and recorded reassignment, without silently dropping required deliverables.

## Task and contract protocol
A's task assignment names the allowed files, starting commit, required contract commits and acceptance checks. Record those in the task handoff before implementation. Separate developer sessions coordinate via committed handoffs and PRs; an agent message channel is supplementary, never the only source of assignments or interface decisions.

Merge shared contracts first. B/C merge current main before consuming generated API types and request contract/dependency changes from A. B publishes typed shared interfaces and existing-file releases before C's dependent UI work. While waiting, proceed only with assigned work independent of an unmerged API.

Before each commit/handoff, update only your own task handoff with completed work, interfaces, exact checks/results and remaining limits. A consolidates shared roadmap/resume/architecture/demo/sponsor docs in A-owned commits. Keep implemented, proposed, fixture-tested and live-verified claims distinct.

## Checks and merging
Use Python 3.12, Node22.23.2 and npm10.9.8. Install from locks with npm ci; only A may regenerate locks. Run python scripts/install_hooks.py in your activated environment after the workflow bootstrap is merged. Existing custom hook paths require explicit chaining; the installer never overwrites them.

Local pre-push fetches main, checks current ancestry, lane ownership and conflict markers against the base policy, and requires a task handoff. CI uses the base branch policy/checker, checks both sides of renames and runs complete application checks plus Linux/Windows/macOS clean installs. The first workflow PR is the only policy bootstrap.

A merges green PRs sequentially after B's review (B-lane changes, including C's delegated patches, require A review). C's extra review does not replace A/B review or add a reviewer gate; assigned C deliverables still count toward stage completion. Record reviewer and findings in the PR or handoff. Fetch/merge main and rerun affected checks after intervening changes; C returns overlapping or expanded scope for recorded reassignment instead of overwriting active A/B work. This private repository's plan cannot enforce required checks: hooks/CI do not prevent a deliberate manual merge. Keep it private; do not change billing or visibility.

The user-authorized queue is important live/demo closeout, then cash-gap explanation (#2), uncertainty explorer (#3), resilient-plan synthesis (#1), and consequence walkthrough (#4), in that order. Read docs/HACKATHON_ASSIGNMENTS.md for A/B/C scope, 35/35/30 effort allocation, prerequisites and acceptance. C10's baseline demo kit can proceed alongside closeout; later C tasks follow named merges. Document impact (#5) is time-permitting; review impact (#6) is lower priority. History and earlier automated rehearsal are merged. Synthesis requires a reviewed separate design; nominal optimization and fixed-plan verification remain distinct. Preserve every invariant above.
