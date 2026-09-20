import { expect, test, type Page } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";
import type { ProviderStatus, UploadResponse, Workspace } from "../src/lib/types";

const source = { name: "synthetic-consent-payment.txt", mimeType: "text/plain", buffer: Buffer.from("SYNTHETIC TEST ONLY. Payment of $123.45 is due 2026-09-28. This is an invented fixture.") };
const consentName = "I consent to external document processing.";

async function session(page: Page) {
  await page.goto("/");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  const token = await page.evaluate(() => localStorage.getItem("clausegraph.session")!);
  const headers = { Authorization: `Bearer ${token}` };
  const providers = await (await page.request.get("/api/providers", { headers })).json() as ProviderStatus[];
  const textId = providers.some(item => item.name === "Brev-hosted Nemotron") ? "brev" : "nvidia";
  const read = async () => (await (await page.request.get("/api/workspace", { headers })).json()) as Workspace;
  return { token, headers, providers, textId, read };
}

async function openUpload(page: Page) {
  await page.getByRole("button", { name: "Add documents", exact: true }).click();
  const dialog = page.getByRole("dialog");
  await dialog.getByLabel("Document file").setInputFiles(source);
  await expect(dialog.getByRole("checkbox", { name: consentName })).toBeEnabled();
  return dialog;
}

async function submit(page: Page) {
  const response = page.waitForResponse(item => item.url().endsWith("/api/documents") && item.request().method() === "POST");
  await page.getByRole("dialog").getByRole("button", { name: "Upload document", exact: true }).click();
  return response;
}

// Real API, storage, worker and source validation; only inference uses an explicit
// in-memory HTTP fixture. No worker socket can reach a provider or the user's VM.
function fixtureWorker(fail: boolean) {
  const repository = path.resolve(__dirname, "../..");
  const python = process.env.PYTHON_EXECUTABLE || [".venv/Scripts/python.exe", "../../.venv/Scripts/python.exe", ".venv/bin/python", "../../.venv/bin/python"].map(item => path.join(repository, item)).find(existsSync) || "python";
  execFileSync(python, ["-c", `
import runpy
import httpx
from clausegraph.config import Settings
from clausegraph.storage import Store, Originals
from clausegraph.providers import Providers
from clausegraph.worker import run_once
settings = Settings(_env_file=None, database_url="sqlite:///./.data/e2e.db", local_storage_path=".data/e2e-documents", evidence_provider="nvidia", nvidia_api_key="fixture-only-never-sent", gemini_api_key="", elevenlabs_api_key="", spaces_bucket="", spaces_access_key_id="", spaces_secret_access_key="", provider_retries=0)
handler = runpy.run_path("backend/tests/test_api.py")["transport_handler"]
transport = httpx.MockTransport(${fail ? 'lambda request: httpx.Response(503, json={"detail": "Synthetic provider outage"})' : "handler"})
store = Store(settings)
try:
    for _ in range(20):
        if not run_once(store, Originals(settings), Providers(settings, transport=transport)):
            break
    else:
        raise AssertionError("Unexpected queued fixture work")
finally:
    store.engine.dispose()
`], { cwd: repository, env: { ...process.env, PYTHONPATH: path.join(repository, "backend") }, timeout: 30_000, stdio: "pipe" });
}

test.afterEach(async ({ page }) => {
  const token = await page.evaluate(() => localStorage.getItem("clausegraph.session")).catch(() => null);
  if (token) await page.request.delete("/api/session", { headers: { Authorization: `Bearer ${token}` } });
});

test("native-only upload stays local and consent never carries into a reopened dialog", async ({ page }) => {
  const { read, textId } = await session(page);
  let dialog = await openUpload(page);
  await expect(dialog).toContainText(textId === "brev" ? "Brev-hosted Nemotron" : "NVIDIA · hosted Nemotron");
  await expect(dialog).toContainText("Evidence checks and scanned-page OCR");
  await expect(dialog).toContainText("NVIDIA · hosted Nemotron evidence");
  await dialog.getByRole("checkbox", { name: consentName }).check();
  await dialog.getByRole("button", { name: "Cancel", exact: true }).click();
  dialog = await openUpload(page);
  await expect(dialog.getByRole("checkbox", { name: consentName })).not.toBeChecked();
  const response = await submit(page);
  expect(response.status()).toBe(201);
  const uploaded = await response.json() as UploadResponse;
  expect(uploaded.job).toBeNull();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  const workspace = await read();
  expect(workspace.jobs).toHaveLength(0);
  expect(workspace.documents.find(item => item.id === uploaded.document.id)?.error).toContain("no provider was called");
  await expect(page.getByText("Document stored without external processing.", { exact: false })).toBeVisible();
});

test("consented upload, failed worker, fresh-consent retry and supported review use the real pipeline", async ({ page }) => {
  const { read } = await session(page);
  let dialog = await openUpload(page);
  await dialog.getByRole("checkbox", { name: consentName }).check();
  const response = await submit(page);
  expect(response.status()).toBe(201);
  const first = await response.json() as UploadResponse;
  expect(first.job?.status).toBe("queued");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  fixtureWorker(true);
  const card = page.locator(".document-card").filter({ has: page.getByRole("heading", { name: source.name, exact: true }) });
  await expect(card.getByRole("alert")).toContainText("HTTP 503");
  await expect(card.getByRole("button", { name: "Retry processing", exact: true })).toBeVisible();
  await card.getByRole("button", { name: "Retry processing", exact: true }).click();
  dialog = page.getByRole("dialog");
  await expect(dialog).toContainText("choose the original file again and give fresh processing consent");
  await dialog.getByLabel("Document file").setInputFiles(source);
  await expect(dialog.getByRole("checkbox", { name: consentName })).not.toBeChecked();
  await dialog.getByRole("checkbox", { name: consentName }).check();
  const retryResponse = await submit(page);
  const retried = await retryResponse.json() as UploadResponse;
  expect(retried.duplicate).toBe(true);
  expect(retried.document.id).toBe(first.document.id);
  expect(retried.job?.id).not.toBe(first.job?.id);
  await expect(page.getByRole("dialog")).toHaveCount(0);
  fixtureWorker(false);
  await expect(card.getByRole("button", { name: "1 extracted facts" })).toBeVisible();
  await expect(card.getByRole("button", { name: "Retry processing", exact: true })).toHaveCount(0);
  const pending = await read();
  const rule = pending.rules.find(item => item.title === "Fixture payment")!;
  expect(rule.review_status).toBe("pending");
  expect(rule.approval_status).toBe("not_required");
  expect(pending.plan?.proposed.ending_balance_cents).toBe(50000);
  await card.getByRole("button", { name: "1 extracted facts" }).click();
  const editor = page.getByTestId(`rule-${rule.id}`);
  await expect(editor.getByRole("blockquote")).toContainText("$123.45");
  await editor.getByRole("combobox", { name: "Evidence review", exact: true }).selectOption("reviewed");
  await editor.getByLabel("Amount (USD)", { exact: false }).fill("999.00");
  await editor.getByRole("button", { name: "Save review & recalculate" }).click();
  await expect(editor.getByRole("alert")).toContainText("Unsupported or disputed evidence");
  await editor.getByLabel("Amount (USD)", { exact: false }).fill("123.45");
  await editor.getByRole("button", { name: "Save review & recalculate" }).click();
  await expect(editor.getByRole("button", { name: "Review saved" })).toBeVisible();
  const reviewed = await read();
  expect(reviewed.plan?.proposed.ending_balance_cents).toBe(37655);
  expect(reviewed.rules.find(item => item.id === rule.id)?.approval_status).toBe("not_required");
  await page.getByRole("button", { name: "Close dialog" }).click();
  await page.getByRole("tab", { name: "Overview", exact: true }).click();
  await expect(page.getByTestId("ending-balance")).toContainText("$376.55");
  await expect(page.getByTestId("review-queue")).not.toContainText("Fixture payment");
});

test("text, evidence and model changes revoke upload consent before any document POST", async ({ page }) => {
  const { providers } = await session(page);
  let current = structuredClone(providers);
  await page.route("**/api/providers", route => route.fulfill({ json: current }));
  const dialog = await openUpload(page);
  let posts = 0;
  page.on("request", request => { if (request.url().endsWith("/api/documents") && request.method() === "POST") posts++; });
  for (const change of ["text", "evidence", "model"]) {
    await dialog.getByRole("checkbox", { name: consentName }).check();
    current = structuredClone(current);
    if (change === "text") current[0].name = current[0].name === "Brev-hosted Nemotron" ? "NVIDIA Nemotron" : "Brev-hosted Nemotron";
    if (change === "evidence") current[1].name = "Gemini";
    if (change === "model") current[0].model = "synthetic-changed-model";
    await dialog.getByRole("button", { name: "Upload document", exact: true }).click();
    await expect(dialog.getByRole("alert")).toContainText("consent again; nothing was sent");
    await expect(dialog.getByRole("checkbox", { name: consentName })).not.toBeChecked();
    expect(posts).toBe(0);
  }
  await expect(dialog).toContainText("Google · Gemini");
  await expect(dialog).toContainText("synthetic-changed-model");
});

for (const mismatch of ["text", "evidence"]) test(`a server-side ${mismatch} mismatch refreshes recipients and requires renewed consent`, async ({ page }) => {
  const { providers, read, textId } = await session(page);
  const stale = structuredClone(providers);
  if (mismatch === "text") stale[0].name = textId === "brev" ? "NVIDIA Nemotron" : "Brev-hosted Nemotron";
  else stale[1].name = "Gemini";
  let useStale = true;
  await page.route("**/api/providers", route => route.fulfill({ json: useStale ? stale : providers }));
  const dialog = await openUpload(page);
  await dialog.getByRole("checkbox", { name: consentName }).check();
  page.on("request", request => { if (request.url().endsWith("/api/documents") && request.method() === "POST") useStale = false; });
  const response = await submit(page);
  expect(response.status()).toBe(409);
  await expect(dialog.getByRole("alert")).toContainText(mismatch === "text" ? "Text provider changed" : "Evidence provider changed");
  await expect(dialog.getByRole("checkbox", { name: consentName })).not.toBeChecked();
  await expect(dialog).toContainText(textId === "brev" ? "Brev-hosted Nemotron" : "NVIDIA · hosted Nemotron");
  expect((await read()).documents).toHaveLength(6);
  await dialog.getByRole("checkbox", { name: consentName }).check();
  expect((await submit(page)).status()).toBe(201);
});

test("unavailable or ambiguous destinations disable external consent with a usable refresh", async ({ page }) => {
  const { providers } = await session(page);
  let mode = "outage";
  await page.route("**/api/providers", route => mode === "outage" ? route.fulfill({ status: 503, json: { detail: "Synthetic status outage" } }) : route.fulfill({ json: mode === "ambiguous" ? [...providers, { ...providers[0], name: providers[0].name === "Brev-hosted Nemotron" ? "NVIDIA Nemotron" : "Brev-hosted Nemotron" }] : providers }));
  await page.getByRole("button", { name: "Add documents", exact: true }).click();
  const dialog = page.getByRole("dialog");
  await expect(dialog.getByRole("alert")).toContainText("could not be loaded");
  await expect(dialog.getByRole("checkbox", { name: consentName })).toBeDisabled();
  mode = "ambiguous";
  await dialog.getByRole("button", { name: "Refresh destinations" }).click();
  await expect(dialog.getByRole("alert")).toContainText("incomplete or ambiguous");
  await expect(dialog.getByRole("checkbox", { name: consentName })).toBeDisabled();
  mode = "ready";
  await dialog.getByRole("button", { name: "Refresh destinations" }).click();
  await expect(dialog.getByRole("checkbox", { name: consentName })).toBeEnabled();
  await expect(dialog.getByRole("checkbox", { name: consentName })).not.toBeChecked();
});

test("drafts start local; external errors preserve edits and mismatches revoke consent", async ({ page }) => {
  const { providers, textId, read } = await session(page);
  const before = await read();
  await page.getByTestId("action-shift-payment").getByRole("button", { name: "Draft request" }).click();
  const dialog = page.getByRole("dialog");
  await expect(dialog).toContainText("Local template draft. No external model was called");
  await dialog.getByLabel("Message", { exact: true }).fill("Keep my handwritten edits.");
  await dialog.locator("summary").filter({ hasText: "Optional:" }).click();
  const generate = dialog.getByRole("button", { name: "Generate replacement draft" });
  const consent = dialog.getByRole("checkbox", { name: "I consent to external draft generation." });
  await expect(generate).toBeDisabled();
  await expect(dialog).not.toContainText("Evidence checks and scanned-page OCR");
  let failure = true;
  let payload: unknown;
  // Explicit HTTP failure/success fixture for optional generation, no external call.
  await page.route("**/api/actions/*/draft", async route => {
    payload = route.request().postDataJSON();
    await route.fulfill(failure ? { status: 503, json: { detail: "Synthetic generation outage" } } : { json: { action_id: "shift-payment", subject: "Fixture replacement", body: "Synthetic model response. Review before use.", sent: false } });
  });
  await consent.check();
  await generate.click();
  await expect(dialog.getByRole("alert")).toContainText("Synthetic generation outage");
  await expect(dialog.getByLabel("Message", { exact: true })).toHaveValue("Keep my handwritten edits.");
  expect(payload).toEqual({ use_provider: true, consent: true, consent_text_provider: textId });
  const changed = structuredClone(providers);
  changed[0].name = textId === "brev" ? "NVIDIA Nemotron" : "Brev-hosted Nemotron";
  await page.route("**/api/providers", route => route.fulfill({ json: changed }));
  await generate.click();
  await expect(dialog.getByRole("alert")).toContainText("consent again");
  await expect(consent).not.toBeChecked();
  await page.unroute("**/api/providers");
  await dialog.getByRole("button", { name: "Refresh destinations" }).click();
  await consent.check();
  failure = false;
  await generate.click();
  await expect(dialog.getByLabel("Message", { exact: true })).toHaveValue("Synthetic model response. Review before use.");
  await expect(dialog).toContainText("Provider-generated draft");
  await expect(dialog.getByText("Not sent", { exact: true })).toBeVisible();
  await expect(consent).not.toBeChecked();
  expect((await read()).plan?.id).toBe(before.plan?.id);
});

test("Brev plus Google disclosures and local drafts fit desktop/mobile and keyboard navigation", async ({ page }, testInfo) => {
  const { providers } = await session(page);
  const disclosed = structuredClone(providers);
  disclosed[0] = { ...disclosed[0], name: "Brev-hosted Nemotron", model: "synthetic-private-nemotron", configured: true };
  disclosed[1] = { ...disclosed[1], name: "Gemini", model: "synthetic-google-evidence", configured: true };
  await page.route("**/api/providers", route => route.fulfill({ json: disclosed }));
  const opener = page.getByRole("button", { name: "Add documents", exact: true });
  for (const width of [1440, 390]) {
    await page.setViewportSize({ width, height: width === 390 ? 844 : 1000 });
    await opener.focus(); await page.keyboard.press("Enter");
    const dialog = page.getByRole("dialog");
    await dialog.getByLabel("Document file").setInputFiles(source);
    const consent = dialog.getByRole("checkbox", { name: consentName });
    await expect(consent).toBeEnabled();
    await expect(dialog).toContainText("Brev-hosted Nemotron");
    await expect(dialog).toContainText("Google · Gemini");
    await consent.focus(); await page.keyboard.press("Space");
    await expect(consent).toBeChecked();
    expect(await dialog.evaluate(node => node.scrollWidth <= node.clientWidth)).toBe(true);
    const overflow = await page.evaluate(() => ({ width: innerWidth, scroll: document.documentElement.scrollWidth, outside: [...document.querySelectorAll("body *")].filter(node => node.getBoundingClientRect().right > innerWidth + 1).slice(0, 5).map(node => node.className) }));
    expect(overflow.scroll, JSON.stringify(overflow)).toBeLessThanOrEqual(overflow.width);
    await dialog.screenshot({ path: testInfo.outputPath(`consent-${width}.png`) });
    await page.keyboard.press("Tab");
    await expect(dialog.getByRole("button", { name: "Cancel", exact: true })).toBeFocused();
    await page.keyboard.press("Tab");
    await expect(dialog.getByRole("button", { name: "Upload document", exact: true })).toBeFocused();
    await dialog.screenshot({ path: testInfo.outputPath(`consent-footer-${width}.png`) });
    await page.keyboard.press("Escape");
    await expect(opener).toBeFocused();
  }
  await page.getByTestId("action-shift-payment").getByRole("button", { name: "Draft request" }).click();
  const draft = page.getByRole("dialog");
  await draft.locator("summary").click();
  await expect(draft.getByRole("checkbox", { name: "I consent to external draft generation." })).not.toBeChecked();
  expect(await draft.evaluate(node => node.scrollWidth <= node.clientWidth)).toBe(true);
  await draft.screenshot({ path: testInfo.outputPath("draft-mobile.png") });
  await draft.getByRole("checkbox", { name: "I consent to external draft generation." }).focus();
  await page.keyboard.press("Tab");
  await expect(draft.getByRole("button", { name: "Download draft" })).toBeFocused();
  await draft.screenshot({ path: testInfo.outputPath("draft-footer-mobile.png") });
});

test("real draft API rejects stale named consent and preserves the local message", async ({ page }) => {
  const { providers, textId } = await session(page);
  const stale = structuredClone(providers);
  stale[0].name = textId === "brev" ? "NVIDIA Nemotron" : "Brev-hosted Nemotron";
  let changed = false;
  await page.route("**/api/providers", route => route.fulfill({ json: changed ? providers : stale }));
  await page.getByTestId("action-shift-payment").getByRole("button", { name: "Draft request" }).click();
  const dialog = page.getByRole("dialog");
  await dialog.getByLabel("Message", { exact: true }).fill("Preserve this local draft.");
  await dialog.locator("summary").click();
  const consent = dialog.getByRole("checkbox", { name: "I consent to external draft generation." });
  await consent.check();
  page.on("request", request => {
    if (request.url().endsWith("/draft") && request.postDataJSON()?.use_provider) changed = true;
  });
  const response = page.waitForResponse(item => item.url().endsWith("/draft") && item.status() === 409);
  await dialog.getByRole("button", { name: "Generate replacement draft" }).click();
  await response;
  await expect(dialog.getByRole("alert")).toContainText("Text provider changed");
  await expect(consent).not.toBeChecked();
  await expect(dialog.getByLabel("Message", { exact: true })).toHaveValue("Preserve this local draft.");
  await expect(dialog.getByRole("button", { name: "Generate replacement draft" })).toBeDisabled();
});
