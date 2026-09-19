# Sponsor integration truth table

Implementation and live-test status will be updated during integration. No provider has been live-tested yet. Offline fixtures must always be labeled synthetic.

| Sponsor | Intended use | Configuration | Live status |
|---|---|---|---|
| NVIDIA Nemotron | primary typed clause extraction, entities, conditions | NVIDIA_API_KEY, NVIDIA_MODEL=nvidia/nemotron-3.5-lightning-30b-a3b, NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1 | not tested |
| Gemini | consequential evidence checks, image-only documents | GEMINI_API_KEY, GEMINI_MODEL=gemini-3.8-flash | not tested; ID configurable |
| Tiger Data | PostgreSQL records/jobs/events/scenarios/chart aggregates | DATABASE_URL | not tested |
| DigitalOcean | app/api/worker deployment, private Spaces originals | SPACES_ENDPOINT, SPACES_REGION, SPACES_BUCKET, SPACES_ACCESS_KEY_ID, SPACES_SECRET_ACCESS_KEY | not provisioned |
| ElevenLabs | optional confirmed spoken intake and narrated checklist | ELEVENLABS_API_KEY, ELEVENLABS_STT_MODEL=scribe_v2, ELEVENLABS_TTS_MODEL=eleven_multilingual_v2, ELEVENLABS_VOICE_ID | not tested |

No Solana, Presage or Snowflake integration. No paid resources provisioned.
