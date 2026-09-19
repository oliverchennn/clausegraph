# Sponsor integration truth table

The synthetic demonstration performs no sponsor inference calls. Native extraction, the rule compiler and all financial arithmetic run locally. Provider adapters are real HTTP integrations, but configured credentials and a successful request are separate facts. No cloud provider has been live-tested in this environment.

| Sponsor | Implemented use | Configuration | Actual live-test status |
|---|---|---|---|
| NVIDIA Nemotron | Lightning extracts clauses/entities/actions and drafts; Nano Omni checks evidence and transcribes unreadable PDF pages by default | NVIDIA_API_KEY, NVIDIA_MODEL=nvidia/nemotron-3.5-lightning-30b-a3b, EVIDENCE_PROVIDER=nvidia, NVIDIA_EVIDENCE_MODEL=nvidia/nemotron-3-nano-omni-30b-a3b-reasoning | catalog lists Omni free prototype endpoint; protocol/rasterization tested locally with mocks, no live inference |
| Gemini (optional) | opt-in consequential evidence checks and PDF vision; not required by the default stack | EVIDENCE_PROVIDER=gemini, GEMINI_API_KEY, GEMINI_MODEL=gemini-3.8-flash | supported adapter tested with mocks; no live call; no automatic fallback |
| Tiger Data | PostgreSQL versioned records, leased jobs, financial events, scenario histories, daily chart series and actual/projected aggregates | DATABASE_URL with sslmode=require | no database credentials; explicit SQLite local fallback tested; PostgreSQL CI test provided |
| DigitalOcean | frontend/API/worker app specification; private Spaces storage adapter and authenticated source downloads | SPACES_ENDPOINT, SPACES_REGION, SPACES_BUCKET, SPACES_ACCESS_KEY_ID, SPACES_SECRET_ACCESS_KEY | no credentials/resources; local private-file storage tested; deployment template only |
| ElevenLabs | scribe_v2 audio transcription requiring manual fact confirmation; eleven_multilingual_v2 checklist narration | ELEVENLABS_API_KEY, ELEVENLABS_STT_MODEL, ELEVENLABS_TTS_MODEL, ELEVENLABS_VOICE_ID | key missing; no live transcription or speech generated |

No Solana, Presage, Snowflake or OpenAI integration. No paid resources provisioned. [SteelHacks tracks](https://steelhacks.org/tracks) explicitly allow Nemotron as a model-output judge; [MLH prizes](https://www.mlh.com/events/steelhacks-xiii/prizes) also list Gemini. Gemini has a free tier too; the NVIDIA-only default minimizes required accounts, not a claimed accuracy advantage. See [the decision and limits](decisions/003-nvidia-evidence-default.md).

## Judge-visible demonstration

Open the synthetic workspace and its six sources, then follow docs/DEMO.md. The data-mode banner is separate from Settings → Connected services. The settings panel exposes unavailable/local/configured states and provider errors; configuration alone is not proof of a live call. Show the exact integer-cent acceptance arithmetic and source-driven approval change without implying that offline fixtures were extracted by a sponsor model.

With real keys supplied server-side, `python scripts/smoke_providers.py` creates and deletes a synthetic session and makes minimal requests for extraction, the explicitly selected evidence model, and configured audio. Calls consume quota and may consume credits. The latest missing-key smoke reports NVIDIA extraction/evidence and ElevenLabs unavailable; the configured but unselected Gemini key was not used. A successful smoke response is only a credential/connectivity check; a full extraction/verification or audio workflow needs its own test. Unselected Gemini credentials never trigger a request.

For a live demonstration, upload only synthetic evidence, explicitly authorize external processing, run the worker, inspect job progress, review every consequential rule, then calculate. Model agreement does not prove correctness, and provider outputs never approve themselves. Original pages, exact quotes/offsets, financial amounts/dates, condition resolution, review and third-party approval remain inspectable.

## Integration references

Adapters follow [NVIDIA structured generation](https://docs.nvidia.com/nim/large-language-models/1.14.0/structured-generation.html), [Nano Omni inference](https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-nano-omni-30b-a3b-reasoning-infer), optional [Gemini generateContent](https://ai.google.dev/api/generate-content), and [ElevenLabs speech-to-text](https://elevenlabs.io/docs/api-reference/speech-to-text/convert). Deployment/storage configuration follows the official references linked in docs/DEPLOYMENT.md. Provider model IDs remain configurable because endpoint availability must be verified with the actual account.
