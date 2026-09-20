import { expect, test, type Page } from "@playwright/test";
import type { PlanResult, VerificationRequest, VerificationResult, Workspace } from "../src/lib/types";

async function session(page: Page) {
  await page.goto("/");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  const token = await page.evaluate(() => localStorage.getItem("clausegraph.session")!);
  const headers = { Authorization: `Bearer ${token}` };
  const read = async <T,>(path: string): Promise<T> => {
    const response = await page.request.get(`/api${path}`, { headers });
    expect(response.ok(), await response.text()).toBeTruthy();
    return response.json();
  };
  const post = async <T,>(path: string, data: unknown): Promise<T> => {
    const response = await page.request.post(`/api${path}`, { headers, data });
    expect(response.ok(), await response.text()).toBeTruthy();
    return response.json();
  };
  return { token, headers, read, post };
}

test("history preserves server order and same-revision identity without saving or restoring a plan", async ({ page }) => {
  const { read, post } = await session(page);
  const first = (await read<Workspace>("/workspace")).plan!;
  const assumed = await post<PlanResult>("/plan", { opening_balance_cents: 240000 });
  expect(assumed.revision).toBe(first.revision);
  // Reactivating a cached older plan must not make the first history row 'active'.
  await post("/plan", first.assumptions);
  const before = await read<Workspace>("/workspace");
  const plans = await read<PlanResult[]>("/history");
  const browserWrites: string[] = [];
  page.on("request", request => { if (request.method() !== "GET" && /\/api\/(plan|verify)/.test(request.url())) browserWrites.push(request.url()); });
  await page.getByRole("tab", { name: "History", exact: true }).click();
  const history = page.getByTestId("saved-history");
  await expect(history.getByRole("heading", { name: "Saved plans (2)", exact: true })).toBeVisible();
  expect(await history.locator('[data-testid^="history-plan-"]').evaluateAll(nodes => nodes.map(node => node.getAttribute("data-testid")))).toEqual(plans.map(plan => `history-plan-${plan.id}`));
  await expect(page.getByTestId(`history-plan-${first.id}`)).toContainText("Active plan when refreshed");
  await expect(page.getByTestId(`history-plan-${assumed.id}`)).toContainText("Inactive plan · same input revision");
  await page.getByTestId(`history-plan-${assumed.id}`).click();
  const details = page.getByRole("region", { name: "Saved record details" });
  await expect(details).toContainText("$2,400.00 · hypothetical, not evidence of funding");
  await expect(details).toContainText("Nominal objective proven");
  await expect(details).toContainText("OPTIMAL");
  await expect(details.getByRole("img", { name: /Cash projection/ })).toBeVisible();
  await details.locator("summary").filter({ hasText: `${assumed.decision_traces![0].action_id} · ${assumed.decision_traces![0].execution_date}` }).click();
  await expect(details).toContainText(assumed.decision_traces![0].source_document_ids[0]);
  await expect(details.getByRole("button", { name: /evidence|restore|verify/i })).toHaveCount(0);
  await details.getByLabel("Saved proposed plan").locator("summary").filter({ hasText: "Beyond-horizon" }).click();
  await expect(details).toContainText("Device principal");
  await expect(history).toContainText("latest 30 available records in server order");
  expect(await read<Workspace>("/workspace")).toEqual(before);
  expect(await read<PlanResult[]>("/history")).toEqual(plans);
  expect(browserWrites).toEqual([]);
  await page.screenshot({ path: "test-results/history-desktop.png", fullPage: true });
});

test("saved SAFE, UNSAFE and incomplete UNKNOWN retain their assumptions and witnesses after input edits", async ({ page }) => {
  const { read, post, headers } = await session(page);
  const workspace = await read<Workspace>("/workspace");
  const verify = (latest: string, max_cases = 10000) => post<VerificationResult>("/verify", { plan_id: workspace.plan!.id, revision: workspace.revision, uncertainties: [{ id: "payday", kind: "income_date", event_id: "paycheck", earliest: "2026-09-21", latest, basis: "user_assumption", rationale: "Saved history browser test bounds" }], max_cases });
  const safe = await verify("2026-09-26");
  const unsafe = await verify("2026-09-28");
  const unknown = await verify("2026-09-28", 1);
  expect([safe.status, unsafe.status, unknown.status]).toEqual(["SAFE", "UNSAFE", "UNKNOWN"]);
  const edited = await page.request.patch("/api/rules/rule-shift", { headers, data: { review_status: "reviewed", approval_status: "denied" } });
  expect(edited.ok(), await edited.text()).toBeTruthy();
  await page.getByRole("tab", { name: "History", exact: true }).click();
  await expect(page.getByTestId(`history-verification-${safe.id}`)).toContainText("Historical input revision");
  await page.getByTestId(`history-verification-${safe.id}`).click();
  const details = page.getByRole("region", { name: "Saved record details" });
  await expect(details).toContainText("6 / 6");
  await expect(details).toContainText("$50.00");
  await expect(details).toContainText("Saved history browser test bounds");
  await page.getByTestId(`history-verification-${unsafe.id}`).click();
  await expect(details.getByRole("heading", { name: "Saved counterexample", exact: true })).toBeVisible();
  await expect(details).toContainText("payday: 2026-09-27");
  await expect(details).toContainText("2026-09-26");
  await expect(details).toContainText("Saved failing balance: -$400.00");
  await page.getByTestId(`history-verification-${unknown.id}`).click();
  await expect(details).toContainText("CASE_LIMIT");
  await expect(details).toContainText("Not proven");
  await expect(details.getByRole("heading", { name: "Saved counterexample", exact: true })).toHaveCount(0);
  expect((await read<Workspace>("/workspace")).plan).toBeNull();
});

test("latest-30 lists can retain a verification whose plan is outside the returned plans", async ({ page }) => {
  const { read, post } = await session(page);
  const workspace = await read<Workspace>("/workspace");
  const checked = await post<VerificationResult>("/verify", { plan_id: workspace.plan!.id, revision: workspace.revision, uncertainties: [] });
  for (let index = 1; index <= 31; index++) await post("/plan", { opening_balance_cents: 200000 + index });
  const plans = await read<PlanResult[]>("/history");
  expect(plans).toHaveLength(30);
  expect(plans.some(plan => plan.id === checked.plan_id)).toBe(false);
  await page.getByRole("tab", { name: "History", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Saved plans (30)", exact: true })).toBeVisible();
  await page.getByTestId(`history-verification-${checked.id}`).click();
  await expect(page.getByRole("region", { name: "Saved record details" })).toContainText("associated plan is outside the returned plan list");
  await expect(page.getByRole("region", { name: "Saved record details" })).toContainText(`${checked.fixed_actions[0].action_id} · ${checked.fixed_actions[0].execution_date}`);
});

test("partial authorization counterexamples and very large coverage totals keep their proof limits", async ({ page }) => {
  const { read, post } = await session(page);
  const workspace = await read<Workspace>("/workspace");
  const partial = await post<VerificationResult>("/verify", { plan_id: workspace.plan!.id, revision: workspace.revision, uncertainties: [{ id: "approval", kind: "approval", target_id: "shift-payment", outcomes: ["approved", "denied", "pending"], basis: "user_assumption", rationale: "Finite approval outcomes" }], max_cases: 2 });
  expect(partial.status).toBe("UNSAFE");
  expect(partial.coverage_complete).toBe(false);
  expect(partial.counterexample?.simulation).toBeNull();
  const large = await post<VerificationResult>("/verify", { plan_id: workspace.plan!.id, revision: workspace.revision, uncertainties: [
    { id: "amount", kind: "income_amount", event_id: "paycheck", minimum_cents: 0, maximum_cents: 10000000000, basis: "user_assumption", rationale: "Large finite domain for coverage display" },
    { id: "date", kind: "income_date", event_id: "paycheck", earliest: "2026-09-21", latest: "9999-12-31", basis: "user_assumption", rationale: "Beyond-horizon dates remain modeled" },
  ], max_cases: 1, time_limit_seconds: 5 } satisfies VerificationRequest);
  expect(Number.isSafeInteger(large.total_cases)).toBe(false);
  await page.getByRole("tab", { name: "History", exact: true }).click();
  await page.getByTestId(`history-verification-${partial.id}`).click();
  const details = page.getByRole("region", { name: "Saved record details" });
  await expect(details).toContainText("Failing date in this case");
  await expect(details).toContainText("No permitted cash balance for this invalid schedule");
  await expect(details).toContainText("Not proven");
  await page.getByTestId(`history-verification-${large.id}`).click();
  await expect(details).toContainText("Total exceeds exact browser integer precision");
  await expect(details).toContainText("every cent $0.00 through $100,000,000.00, inclusive");
});

test("history read failures retry honestly, external resets invalidate in-flight reads, and empty lists stay read-only", async ({ page }) => {
  const { post, read } = await session(page);
  await page.route("**/api/history", route => route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "Persisted chart is incomplete" }) }));
  await page.getByRole("tab", { name: "History", exact: true }).click();
  await expect(page.getByTestId("saved-history").getByRole("alert")).toContainText("Persisted chart is incomplete");
  await expect(page.getByText("No saved plans in this session.")).not.toBeVisible();
  await page.unroute("**/api/history");
  await page.getByRole("button", { name: "Try history again" }).click();
  await expect(page.getByRole("heading", { name: "Saved plans (1)", exact: true })).toBeVisible();
  await page.route("**/api/history", async route => {
    const response = await route.fetch();
    await post("/demo/reset", {});
    await route.fulfill({ response });
  });
  await page.getByRole("button", { name: "Refresh history" }).click();
  await expect(page.getByTestId("saved-history").getByRole("alert")).toContainText("workspace changed during this read");
  await page.unroute("**/api/history");
  await page.getByRole("button", { name: "Try history again" }).click();
  await expect(page.getByText("No saved plans in this session.")).toBeVisible();
  await expect(page.getByText("No saved verifications in this session.")).toBeVisible();
  expect((await read<Workspace>("/workspace")).plan).toBeNull();
});

test("reset clears selection at start and a delayed obsolete history response cannot repopulate it", async ({ page }) => {
  const { read } = await session(page);
  const old = (await read<Workspace>("/workspace")).plan!;
  await page.getByRole("tab", { name: "History", exact: true }).click();
  await page.getByTestId(`history-plan-${old.id}`).click();
  await expect(page.getByRole("heading", { name: "Saved plan details", exact: true })).toBeVisible();
  let releaseHistory!: () => void;
  let started!: () => void;
  const historyStarted = new Promise<void>(resolve => { started = resolve; });
  const holdHistory = new Promise<void>(resolve => { releaseHistory = resolve; });
  await page.route("**/api/history", async route => {
    const response = await route.fetch(); started();
    await holdHistory;
    await route.fulfill({ response }).catch(() => {});
  }, { times: 1 });
  await page.getByRole("button", { name: "Refresh history" }).click();
  await historyStarted;
  await expect(page.getByText("Loading saved history…")).toBeVisible();
  let releaseReset!: () => void;
  const holdReset = new Promise<void>(resolve => { releaseReset = resolve; });
  await page.route("**/api/demo/reset", async route => { const response = await route.fetch(); await holdReset; await route.fulfill({ response }); });
  await page.getByRole("button", { name: "Open settings" }).click();
  page.once("dialog", dialog => dialog.accept());
  await page.getByRole("dialog").getByRole("button", { name: "Reset", exact: true }).click();
  await expect(page.getByTestId("saved-history")).toHaveCount(0);
  releaseHistory(); releaseReset();
  await expect(page.getByRole("dialog")).not.toBeVisible();
  await expect(page.getByRole("heading", { name: "Saved plans (1)", exact: true })).toBeVisible();
  await expect(page.getByTestId(`history-plan-${old.id}`)).toHaveCount(0);
  await expect(page.getByRole("heading", { name: "Saved plan details", exact: true })).toHaveCount(0);
});

test("source and session deletion clear displayed history; 401 is session loss", async ({ page }) => {
  const { read } = await session(page);
  const old = (await read<Workspace>("/workspace")).plan!;
  await page.getByRole("tab", { name: "History", exact: true }).click();
  await page.getByTestId(`history-plan-${old.id}`).click();
  await page.getByRole("tab", { name: "Documents & facts" }).click();
  page.once("dialog", dialog => dialog.accept());
  await page.getByRole("button", { name: "Delete 03-payment-shift-approval.txt", exact: true }).click();
  await expect(page.getByRole("heading", { name: "03-payment-shift-approval.txt", exact: true })).toHaveCount(0);
  await page.getByRole("tab", { name: "History", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Saved plans (1)", exact: true })).toBeVisible();
  await expect(page.getByTestId(`history-plan-${old.id}`)).toHaveCount(0);
  await page.getByRole("button", { name: "Open settings" }).click();
  await page.getByRole("dialog").getByRole("button", { name: "Delete", exact: true }).click();
  await page.getByRole("button", { name: "Delete session permanently" }).click();
  await expect(page.getByRole("heading", { name: "Your session has been deleted" })).toBeVisible();
  await expect(page.getByTestId("saved-history")).toHaveCount(0);
  await page.getByRole("button", { name: "Explore synthetic demo" }).click();
  await expect(page.getByTestId("saved-history")).toBeVisible();
  await page.route("**/api/verifications", route => route.fulfill({ status: 401, contentType: "application/json", body: JSON.stringify({ detail: "Invalid session" }) }));
  await page.getByRole("button", { name: "Refresh history" }).click();
  await expect(page.getByText("This private session is no longer available.", { exact: false })).toBeVisible();
  await expect(page.getByTestId("saved-history")).toHaveCount(0);
  expect(await page.evaluate(() => localStorage.getItem("clausegraph.session"))).toBeNull();
});

test("mobile history supports keyboard selection without overflow and discards a prior session response", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const { read } = await session(page);
  const old = (await read<Workspace>("/workspace")).plan!;
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.getByRole("tab", { name: "History", exact: true }).click();
  const record = page.getByTestId(`history-plan-${old.id}`);
  await record.focus(); await page.keyboard.press("Enter");
  await expect(record).toHaveAttribute("aria-expanded", "true");
  await expect(page.getByRole("heading", { name: "Saved plan details", exact: true })).toBeVisible();
  await expect(page.getByRole("img", { name: /Cash projection/ })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.screenshot({ path: "test-results/history-mobile.png", fullPage: true });
  let release!: () => void;
  let started!: () => void;
  const requested = new Promise<void>(resolve => { started = resolve; });
  const held = new Promise<void>(resolve => { release = resolve; });
  await page.route("**/api/history", async route => { const response = await route.fetch(); started(); await held; await route.fulfill({ response }).catch(() => {}); }, { times: 1 });
  await page.getByRole("button", { name: "Refresh history" }).click();
  await requested;
  await page.getByRole("button", { name: "Start my own plan" }).click();
  await expect(page.getByTestId("saved-history")).not.toContainText("Synthetic demo records");
  release();
  await expect(page.getByTestId("saved-history")).toContainText("Private session records");
  await expect(page.getByTestId(`history-plan-${old.id}`)).toHaveCount(0);
  expect(errors).toEqual([]);
});
