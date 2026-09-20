# NVIDIA hosted first; optional Brev GPU inference

Hosted NVIDIA is the default and needs no GPU VM. Brev credits fund your organization's GPU compute/storage; they do not configure ClauseGraph's hosted API credential. This task prepares configuration and tests adapters with mocked HTTP. No GPU has been provisioned and no live inference result is claimed.

## 1. Get the hosted NVIDIA key

Open [NVIDIA Build](https://build.nvidia.com), sign in, select the configured [Nemotron text model](https://build.nvidia.com/nvidia/nemotron-3.5-lightning-30b-a3b), then use **Get API Key**. Complete the developer-account prompts and copy the generated key into your local repository-root `.env`. Never paste it in a task, commit or browser environment variable. NVIDIA's [API quickstart](https://docs.api.nvidia.com/nim/docs/api-quickstart) documents this flow. If that model is unavailable to your account, select an available model deliberately and validate it; this code does not silently switch models.

Keep these local settings (replace only the key value):

```dotenv
TEXT_PROVIDER=nvidia
NVIDIA_API_KEY=your-private-key
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=nvidia/nemotron-3.5-lightning-30b-a3b
EVIDENCE_PROVIDER=nvidia
NVIDIA_EVIDENCE_MODEL=nvidia/nemotron-3-nano-omni-30b-a3b-reasoning
```

Use the `.env` in the checkout from which you run the backend. `python scripts/dev.py` runs the API and worker from that checkout and requires an installed frontend. Restart both API and worker after changing configuration. The synthetic demo still works with no key. A configured provider status is not evidence of connectivity or accuracy.

For an explicitly consented, quota-consuming check, run from that checkout with the Python environment activated:

```powershell
python scripts/eval_nemotron.py --live --consent-external
```

This sends five fictional native-text clauses to the selected text model and reports structured fields, citations and review gates. It does not test OCR. Follow [EXTRACTION_CHECK.md](EXTRACTION_CHECK.md) separately for the synthetic native/scanned end-to-end check. Leave off both flags for the offline fixture gate evaluation. A failed key/model/rate-limit response is an actual failure, never replaced by fixtures.

## 2. Prepare Brev credits and a compatible VM

In the [Brev console](https://brev.nvidia.com), select the correct organization, open **Billing / Credits** and redeem the credit code if it is not already reflected in the balance. Credits are shared across that organization. Check the displayed hourly price, remaining balance and resource limit before choosing Deploy. Auto recharge is a separate billing setting; this setup does not enable it. Stopping compute can leave storage charges. See [Brev billing](https://docs.nvidia.com/brev/guides/console-reference).

Choose a Nemotron NIM with a deployment image and GPU profile supported by its current [NIM support matrix](https://docs.nvidia.com/nim/large-language-models/latest/support-matrix.html). Do not assume a hosted catalog model name is also an available container image, or that a 30B model fits any GPU. Copy its pinned container tag/digest, check VRAM/disk/license requirements, then provision a VM only when ready to spend credits. This repository intentionally supplies no guessed image or GPU SKU.

Install the CLI using the [Brev quickstart](https://docs.nvidia.com/brev/getting-started/quickstart). On Windows, its documented path uses WSL. Authenticate and discover an instance you have already created:

```bash
brev login
brev refresh
brev list
brev shell YOUR_INSTANCE
nvidia-smi
```

On the GPU VM, copy this repository's `deploy/brev/` directory and create its ignored `.env` from `.env.example`. Set `NIM_IMAGE` to the selected pinned image. If the image needs registry/model-download credentials, create an NGC personal API key with the appropriate catalog permission and set `NGC_API_KEY` there. See [NIM installation/authentication](https://docs.nvidia.com/nim/large-language-models/latest/get-started/installation.html). Do not copy your application `.env` to the VM. A Brev account token manages infrastructure; an NGC download key and hosted inference key have different purposes.

From the copied repository root on the GPU VM, after selecting the image and accepting its terms:

```bash
# If registry authentication is required, enter the NGC key without echo/history:
read -rsp 'NGC download key: ' NGC_API_KEY; echo
export NGC_API_KEY
printf '%s' "$NGC_API_KEY" | docker login nvcr.io --username '$oauthtoken' --password-stdin
docker compose --env-file deploy/brev/.env -f deploy/brev/compose.yaml up -d
docker compose --env-file deploy/brev/.env -f deploy/brev/compose.yaml logs --tail 50
```

The template requires NVIDIA Container Toolkit and Docker Compose on the VM. It mounts a model cache and binds NIM only to the VM's loopback port8000. Download/startup may take time. This template has not been exercised on a GPU; use the selected image's instructions if its runtime needs extra settings. [NVIDIA's Brev NIM guide](https://docs.nvidia.com/brev/guides/inference-deployment/deploying-nims) explains deployment and API access.

## 3. Connect the optional text model

From the local machine (WSL on Windows), keep this terminal open:

```bash
brev port-forward YOUR_INSTANCE --port 18000:8000
```

Port18000 avoids ClauseGraph's local API port8000. [Brev port forwarding](https://docs.nvidia.com/brev/cli/connectivity) provides direct API access over SSH. Browser-authenticated public tunnel URLs are not suitable here. No inference bearer key is sent by ClauseGraph: the SSH tunnel provides access control. A download key does not secure a public NIM endpoint.

In a second terminal in the **same host/network namespace as the backend**, inspect the server's model list (no inference):

```powershell
Invoke-RestMethod http://127.0.0.1:18000/v1/models
```

For Linux/WSL use `curl http://127.0.0.1:18000/v1/models`. If the API/worker runs in Windows and the tunnel in WSL, first confirm this request works from Windows; otherwise run the backend in WSL alongside the tunnel. The supplied Docker Compose application stack uses another loopback namespace and is not supported for this optional local tunnel setup.

Copy the exact served `id` into the application's `.env`, then restart API and worker:

```dotenv
TEXT_PROVIDER=brev
BREV_NIM_BASE_URL=http://127.0.0.1:18000/v1
BREV_NIM_MODEL=exact-id-from-the-model-list
```

Leave `NVIDIA_BASE_URL` and `NVIDIA_API_KEY` unchanged: evidence checking and OCR still use the selected hosted NVIDIA model (or explicitly selected Gemini). Brev handles text extraction and optional drafts only. For structured extraction the adapter uses OpenAI-compatible `response_format.type=json_schema`, caps Nemotron reasoning at 2,048 tokens (and at most half the total response budget), and asks the model to select source-line IDs. Python resolves those IDs into original quotes, versions, pages and offsets; unknown IDs or model-authored provenance are rejected. A private response schema separates missing dates/amounts from explicitly described party/account, event-link or cash-direction conflicts. The public API contract is unchanged, and actual entity conflicts still block review/compilation. Plain-text drafts disable reasoning and do not force JSON. This targets the Nemotron 3.5 Lightning NIM/vLLM runtime; another NIM must support these parameters or fail explicitly. See [Nemotron reasoning budgets](https://docs.nvidia.com/nim/large-language-models/2.0.10/get-started/advanced/get-started-nemotron-3.5-lightning.html#control-thinking-budget) and [vLLM structured outputs](https://docs.vllm.ai/en/latest/features/structured_outputs/).

Schema-constrained output does not establish factual accuracy. The adapter still validates responses locally, preserves source text, rejects malformed/incomplete output and requires the existing evidence, review and approval gates. It does not repair model claims or fall back to hosted text inference. The [source-reference handoff](handoffs/dev-a/brev-source-references.md) records current checks and the earlier live failures; it is not an OCR or general model-accuracy claim.

## Consent contract and Developer B follow-up

Hosted uploads continue working as before. While `TEXT_PROVIDER=brev`, document processing requires `consent=true`, `consent_text_provider=brev` and the appropriate existing `consent_provider` for evidence/OCR. Uploads without external consent still retain native text locally. Provider drafts require `use_provider=true`, `consent=true`, `consent_text_provider=brev`; drafts are never sent. Queued jobs bind provider endpoints/models at enqueue and reject configuration changes before processing.

**The current browser has hosted-provider consent only. Keep `TEXT_PROVIDER=nvidia` for the browser demo until Developer B adds explicit Brev consent.** The optional Brev backend is usable via the consented synthetic CLI evaluation or an API client sending the named consent. Missing Brev consent returns409 before storage or inference. No frontend code is changed in this A task.

B's later task: read the generated contract after this PR merges, display the `Brev-hosted Nemotron` provider status plus the separate evidence recipient, send named text consent on upload/draft, and cover changed-provider consent errors. Do not edit backend or generated types in B's task. Revert to `TEXT_PROVIDER=nvidia` and restart both processes to return to hosted text inference; re-upload failed jobs with fresh consent. Close the tunnel and stop unused GPU compute in Brev when finished; stopping the NIM container alone does not stop VM billing.
