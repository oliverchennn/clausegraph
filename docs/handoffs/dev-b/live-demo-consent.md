# Developer B: destination-aware consent and demo closeout

## Assignment and isolation

The user explicitly assigned Dev B to begin the first task in the expanded plan while Dev A works on this machine. Scope: stage 0 `live-demo-consent`, as recorded in the assignment PR24 at `fab5900f10ea94accd2f80c942044a3adf2a354e`. PR24 was open at task start; the user instruction authorizes this bounded task. No unmerged runtime contract is consumed. Stop after this task's handoff/PR; no stage 1 implementation.

Starting main: `ca7cde59287e5456a9398965796c873152176491` (merged PR23). Branch: `codex/dev-b/live-demo-consent`. Worktree: `.worktrees/dev-b-live-demo-consent`. Fetched origin with pruning; main already matched fetched main. Existing A/B worktrees, root services and uncommitted work are preserved. Required consent contract: merged PR9 `af980e12b1120d960ecfe6e89d03d6bdb33e4c4a`, including named text consent on uploads and provider drafts; current main also includes PR11/13/15 provider fixes and PR19/20 history/verification contracts.

Allowed files: `frontend/src/app/page.tsx`, `frontend/src/app/globals.css`, new `frontend/src/components/processing-consent.tsx`, `frontend/src/components/upload-dialog.tsx`, `frontend/src/components/draft-dialog.tsx`, `frontend/tests/processing-consent.spec.ts`, existing `frontend/tests/workspace.spec.ts`, and this handoff. These are B-owned under the merged policy. No generated types, dependencies/locks, backend, fixtures, scripts, shared docs or peer handoffs are assigned. No C write release.

## Acceptance and planned checks

- Show text extraction/draft destination separately from evidence/OCR and original storage, including Brev plus hosted NVIDIA or Google evidence.
- Send explicit named text/evidence consent using existing contracts, preserve local uploads and default local unsent drafts, invalidate consent on changed destinations and reject stale requests.
- Make failures and fresh-consent re-upload recovery visible; preserve edited drafts on generation failure. Exercise supported review/recalculation through the real local API.
- Run pinned Node22.23.2/npm10.9.8 locked install, typecheck, lint, build and full Playwright suite using separate ports8126/3126 and worktree-local storage. Confirm the shared hook without replacement and run ownership/current-main checks.
- Inspect affected desktop/mobile and keyboard flows; prepare presenter cues. Distinguish fixture tests, actual live native/OCR calls, and human spoken rehearsal. No external provider call is authorized by this task alone; A owns live extraction closeout.

## Progress

Read the expanded assignments, merged consent implementation, verification/integration history and prior B handoffs. Existing ProviderStatus exposes provider names and models but no endpoint/route identifier; the UI can refresh and compare those disclosed fields and rely on backend named-provider/queued-route validation. End-to-end route binding beyond that requires an A-owned contract change, not guessed browser configuration.

Human presenter availability requested; no spoken rehearsal measured yet.

PR24 merged as `e65464c`; fetched and fast-forwarded this worktree to that commit while preserving the B frontend changes. The merged assignment and ownership rules were reread. The existing shared pre-push hook was confirmed without replacement. Locked install used the existing `.worktrees/.toolchain/node-v22.23.2-win-x64` runtime and installed 439 packages in this worktree only.

## Presenter cues for this increment

Keep the existing three-minute synthetic Verify story in `docs/DEMO.md` as the stable fallback. Preload the saved `.data/verify-demo.json` and `.data/eval-offline.json` reports before presenting. Both were regenerated locally in this task with no live flags; JSON parsed successfully. The first retains eight-case Unsafe, the separate best-schedule diagnostic and the same schedule with hypothetical cash; the second reports all five expected gate outcomes with no model accuracy measured.

Use this short consent/review segment outside that timed story, or substitute it deliberately when A's separately validated live session is ready:

1. **Source and recipients:** identify the fictional test source. Open Add documents and name text extraction, evidence/OCR and original storage separately. Brev text does not imply that evidence/OCR stays on the GPU. Configuration is not a connectivity or accuracy result.
2. **Explicit choice:** leave consent unchecked to demonstrate local native-text retention, or obtain explicit consent for the displayed recipients before starting the separately authorized live run. A model-generated replacement draft has its own consent; the default draft is local and unsent.
3. **Progress or failure:** show queued/running/completed or the actual error. A failed job uses Retry processing, the original file and fresh consent. Do not narrate a queued/completed job as accurate extraction. If a provider changes, review the refreshed recipients and consent again.
4. **Review before cash:** inspect the exact quote, version/page, amount/date, review status and third-party approval. Correct only source-supported facts; saving review recalculates through the backend. Consent and human review do not grant an extension or benefit approval.
5. **Bounded proof and history:** return to the merged Verify/History flow. Explain saved identities, assumptions and declared bounds; the nominal plan, fixed-plan check and hypothetical cash remain distinct. Cash-gap UI, uncertainty explorer and resilient synthesis are later stages, not delivered here.
6. **Fallback and close:** if live processing fails, label the locally computed synthetic reports and use the existing story. Nothing is paid, cancelled, applied for or sent. Delete disposable test sources/sessions after the demonstration.

No human presenter has supplied a spoken run in this task. No new automated three-minute timing is substituted for spoken rehearsal. Actual native live extraction, scanned/OCR live results and their latency/accuracy report remain A's stage-0 closeout; this B task uses explicit local provider fixtures only.

## Implementation and review notes

Extracted upload and draft dialogs from the workspace. Shared consent presentation resolves only the provider names defined by the merged API, rejects incomplete/ambiguous recipient lists, and shows the selected text model, separate evidence/OCR model and local/Spaces storage. It reads provider status when opened and immediately before an external request. Consent is tied to the disclosed names, models and configured state, scoped to the dialog/session, and cleared on file selection, successful processing, or API409. Changed provider/model snapshots stop before POST; failed status reads cannot authorize external processing. Dialog closure aborts status reads. Backend409 refreshes recipients but never automatically retries processing.

Uploads send both `consent_text_provider` and `consent_provider` with explicit external consent. Unchecked consent retains the existing local native-text path; configured cloud original storage requires consent. Workspace busy state still clears displayed history while upload mutates sources. Failed jobs now offer re-upload instructions and a fresh dialog. Document cards use the newest job, so an old failure does not reappear after a completed retry. A CSS specificity correction prevents the visually hidden file input's generic 100% width from overflowing the dialog (observed 586px scroll width inside a 560px dialog before the fix).

Draft requests still open the backend's local template by default. The optional model control names its text recipient and discloses the actual action/source fields sent. It requests an explicitly consented replacement, preserves the current subject/body on failures, resets consent after success, and labels generated content and unsent state. Session/revision changes clear open drafts. Explicit input labels keep the editor accessible. No outgoing message, approval, calculation or API/schema change was introduced.

The existing ProviderStatus contract does not expose the endpoint URL or a route-consent token. This implementation can compare provider/model disclosures and send the existing named consent; it cannot atomically pin a browser request to a hidden endpoint/model change between the final status read and POST. Queued work retains the backend's existing route fingerprint check. Any stronger atomic browser route-binding guarantee requires an A-owned contract, and is not claimed here.

## Validation and delivery

Python3.12.14 is the existing root virtual environment; Node22.23.2/npm10.9.8 are the existing pinned local runtime. All API/frontend processes used this worktree's SQLite database/documents and ports8126/3126; Playwright stopped its servers afterward. No root `.env`, user's session, running application, VM or external inference was used. Other contributors' checkouts were not edited. Latest synchronization confirmed main remains `e65464c`; concurrent PR25/26/27 do not overlap this task's paths.

| Check | Result |
|---|---|
| `npm ci --no-audit --no-fund` | Passed; 439 locked packages; lockfile unchanged |
| `npm run typecheck`; `npm run lint` | Passed; final production build also checked types/lint |
| `npm run build` | Passed; static `/`, 152kB first-load JS |
| `TEXT_PROVIDER=nvidia E2E_API_PORT=8126 E2E_WEB_PORT=3126 npm run test:e2e` | **28 passed in 2.3m**; all 19 prior tests and nine new consent cases |
| Same ports, `TEXT_PROVIDER=brev BREV_NIM_MODEL=synthetic-no-network-model BREV_NIM_BASE_URL=http://127.0.0.1:18999/v1 npm run test:e2e -- processing-consent.spec.ts` | **9 passed in 55.4s**; actual Brev API consent validation, all inference intercepted in memory |
| `python scripts/verify_demo.py`; `python scripts/eval_nemotron.py` | Passed; saved valid JSON, 8/8 Unsafe, 40000 hypothetical extra cents -> same schedule 8/8 Safe, all five expected fixture gate outcomes |
| Visual/keyboard checks | Inspected 1440px desktop and 390px mobile upload/draft screenshots, including scrolled footers. Consent, action buttons, Escape and restored opener focus work without horizontal overflow |
| Intended-path ownership and `git diff --check` | Eight B-owned paths; passed, with normal CRLF notices only |

The nine new browser cases cover local/no-consent retention; per-dialog consent reset; real consented upload, mocked provider outage, real failed-job recovery/dedup, mocked extraction/evidence HTTP and real source validation; pending review withholding; rejection of an unsupported correction; supported correction/recalculation to 37655 ending cents; pre-POST text/evidence/model changes; actual server409 for text/evidence uploads and drafts; missing/ambiguous status recovery; local/optional drafts and preservation on failure; mobile/keyboard/footer reachability. The worker test reuses the existing backend HTTP fixture handler through `httpx.MockTransport`; this is neither a live provider run nor extraction accuracy evidence. No backend file was changed.

Exploratory test failures were corrected: Chromium does not expose this multipart file body through `postData()`, so persisted job/no-job behavior and actual API consent rejection are checked instead; exact text-label selectors for compound labels were replaced by accessible controls, and draft fields have explicit labels. The hidden-input overflow and stale failed-job display were fixed before the final green runs. Existing Next development-origin, color-environment and dependency-deprecation notices were nonfatal.

Screenshots remain ignored under `frontend/test-results/processing-consent-Brev-pl-5d3c0-ile-and-keyboard-navigation-chromium/`; saved fallback reports are under `.data/`. Human spoken rehearsal and live native/scanned/OCR results remain outstanding and explicitly separate. No general accuracy, stronger atomic route consent, public deployment, payments, cancellation, applications or outgoing messages are claimed. A owns review/merge and updates to shared progress docs. Stop after this task's publication.
