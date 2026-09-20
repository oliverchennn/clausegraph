import { expect, test, type Page } from "@playwright/test";

async function snapshot(page: Page) {
  const token = await page.evaluate(() => localStorage.getItem("clausegraph.session"));
  const headers = { Authorization: `Bearer ${token}` };
  return {
    workspace: await (await page.request.get("/api/workspace", { headers })).json(),
    plans: await (await page.request.get("/api/history", { headers })).json(),
    proofs: await (await page.request.get("/api/verifications", { headers })).json(),
  };
}

async function open(page: Page) {
  await page.goto("/");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  await page.getByRole("button", { name: "Open resilient example", exact: true }).click();
  await expect(page.locator(".demo-strip")).toContainText("three fixture documents");
  await page.getByRole("button", { name: "Payday Sep 3–5", exact: true }).click();
  return page.getByTestId("resilient-panel");
}

async function search(page: Page) {
  await page.getByRole("button", { name: "Find verified alternative", exact: true }).click();
  await expect(page.getByTestId("synthesis-result")).toContainText("Verified alternative found");
}

test("real candidate comparison is nonmutating and explicit adoption saves the exact schedule and proof", async ({ page }) => {
  const panel = await open(page);
  await page.getByRole("button", { name: "Verify fixed plan", exact: true }).click();
  await expect(page.getByTestId("verification-result")).toContainText("Unsafe");
  const before = await snapshot(page);
  expect(before.workspace.plan.actions[0].action_id).toBe("early-shift");
  await search(page);
  const unchanged = await snapshot(page);
  expect(unchanged).toEqual(before);
  await expect(panel.getByLabel("Current saved schedule")).toContainText("-$50.00");
  await expect(panel.getByLabel("Verified candidate schedule")).toContainText("$49.00");
  await expect(panel.getByLabel("Verified candidate schedule")).toContainText("$1.00");
  await expect(panel.getByTestId("candidate-proof")).toContainText("3 / 3 cases, complete coverage");
  await expect(page.getByLabel("Latest for resilient-payday")).toHaveValue("2026-09-05");
  let nominalCalls = 0;
  page.on("request", req => { if (new URL(req.url()).pathname === "/api/plan") nominalCalls += 1; });
  await panel.getByRole("button", { name: "Adopt verified schedule", exact: true }).click();
  await expect(page.getByTestId("minimum-balance")).toContainText("$49");
  await expect(page.getByTestId("verification-result")).toContainText("Verified Safe");
  await expect(page.locator(".solver-note")).toContainText("Verified fixed schedule · no optimum claimed");
  const after = await snapshot(page);
  expect(nominalCalls).toBe(0);
  expect(after.workspace.revision).toBe(before.workspace.revision);
  expect(after.workspace.plan.id).not.toBe(before.workspace.plan.id);
  expect(after.workspace.plan.actions.map((a: { action_id: string }) => a.action_id)).toEqual(["late-shift"]);
  expect(after.plans).toHaveLength(2);
  expect(after.proofs.some((proof: { plan_id: string; status: string }) => proof.plan_id === after.workspace.plan.id && proof.status === "SAFE")).toBe(true);
  await page.reload();
  await expect(page.getByTestId("minimum-balance")).toContainText("$49");
  await expect(page.getByLabel("Latest for resilient-payday")).toHaveValue("2026-09-05");
  await page.getByRole("tab", { name: "History", exact: true }).click();
  await expect(page.getByTestId("saved-history")).toContainText("Saved plans (2)");
  await page.getByTestId(`history-plan-${after.workspace.plan.id}`).click();
  await expect(page.getByTestId("saved-history")).toContainText("Verified fixed schedule · no optimization claim");
});

test("the original domain proves no solution and a case cutoff stays inconclusive", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  await page.getByRole("button", { name: "Payday through Sep 28", exact: true }).click();
  const before = await snapshot(page);
  await page.getByRole("button", { name: "Find verified alternative", exact: true }).click();
  await expect(page.getByTestId("synthesis-result")).toContainText("No solution in this declared domain");
  await expect(page.getByRole("button", { name: "Adopt verified schedule" })).toHaveCount(0);
  expect(await snapshot(page)).toEqual(before);
  await page.getByRole("button", { name: "Open resilient example", exact: true }).click();
  await page.getByRole("button", { name: "Payday Sep 3–5", exact: true }).click();
  await page.route("**/api/synthesis", route => route.continue({ postData: JSON.stringify({ ...route.request().postDataJSON(), max_case_checks: 1 }) }));
  await page.getByRole("button", { name: "Find verified alternative", exact: true }).click();
  await expect(page.getByTestId("synthesis-result")).toContainText("Search inconclusive");
  await expect(page.getByTestId("synthesis-result")).toContainText("CASE LIMIT");
  await expect(page.getByRole("button", { name: "Adopt verified schedule" })).toHaveCount(0);
});

test("candidate and delayed obsolete response clear when uncertainty bounds change", async ({ page }) => {
  const panel = await open(page);
  await search(page);
  await page.getByLabel("Latest for resilient-payday").fill("2026-09-04");
  await expect(panel.getByTestId("synthesis-result")).toHaveCount(0);
  let release: () => void = () => {};
  const gate = new Promise<void>(resolve => { release = resolve; });
  let fetched: () => void = () => {};
  const ready = new Promise<void>(resolve => { fetched = resolve; });
  await page.route("**/api/synthesis", async route => {
    const response = await route.fetch();
    fetched(); await gate;
    await route.fulfill({ response }).catch(() => {});
  });
  await panel.getByRole("button", { name: "Find verified alternative", exact: true }).click();
  await ready;
  await page.getByLabel("Latest for resilient-payday").fill("2026-09-05");
  release();
  await expect(panel.getByTestId("synthesis-result")).toHaveCount(0);
  await expect(panel.getByRole("button", { name: "Find verified alternative", exact: true })).toBeEnabled();
  expect((await snapshot(page)).workspace.plan.actions[0].action_id).toBe("early-shift");
});

test("stale adoption fails closed, clears the candidate and offers reload", async ({ page }) => {
  const panel = await open(page);
  await search(page);
  const token = await page.evaluate(() => localStorage.getItem("clausegraph.session"));
  const replacement = await page.request.post("/api/plan", { headers: { Authorization: `Bearer ${token}` }, data: { opening_balance_cents: 5001 } });
  expect(replacement.ok()).toBe(true);
  await panel.getByRole("button", { name: "Adopt verified schedule", exact: true }).click();
  await expect(panel.getByRole("alert")).toContainText("Workspace changed");
  await expect(panel.getByTestId("synthesis-result")).toHaveCount(0);
  expect((await snapshot(page)).workspace.plan.id).toBe((await replacement.json()).id);
});

test("scenario draft edits and failed searches discard a candidate, and retry uses the saved assumptions", async ({ page }) => {
  const panel = await open(page);
  await search(page);
  const before = await snapshot(page);
  await page.getByLabel("Scenario available cash").fill("60.00");
  await expect(panel.getByTestId("synthesis-result")).toHaveCount(0);
  await expect(page.getByLabel("Latest for resilient-payday")).toHaveValue("2026-09-05");
  await page.route("**/api/synthesis", route => route.fulfill({ status: 503, json: { detail: "Injected temporary search failure" } }));
  await panel.getByRole("button", { name: "Find verified alternative", exact: true }).click();
  await expect(panel.getByRole("alert")).toContainText("Injected temporary search failure");
  await expect(panel.getByRole("button", { name: "Adopt verified schedule", exact: true })).toHaveCount(0);
  await page.unroute("**/api/synthesis");
  await search(page);
  await expect(panel.getByLabel("Current saved schedule")).toContainText("$50.00");
  expect(await snapshot(page)).toEqual(before);
});

test("lost session during synthesis clears private UI and its token", async ({ page }) => {
  const panel = await open(page);
  await search(page);
  const token = await page.evaluate(() => localStorage.getItem("clausegraph.session"));
  expect((await page.request.delete("/api/session", { headers: { Authorization: `Bearer ${token}` } })).ok()).toBe(true);
  await panel.getByRole("button", { name: "Adopt verified schedule", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Let’s find your next step" })).toBeVisible();
  expect(await page.evaluate(() => localStorage.getItem("clausegraph.session"))).toBeNull();
  await expect(page.getByTestId("resilient-panel")).toHaveCount(0);
});

test("mobile candidate evidence and adoption are keyboard accessible", async ({ page }, info) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const panel = await open(page);
  const find = panel.getByRole("button", { name: "Find verified alternative", exact: true });
  await find.focus(); await page.keyboard.press("Enter");
  await expect(panel.getByTestId("candidate-proof")).toContainText("SAFE");
  const evidence = panel.getByRole("button", { name: "Evidence for late-shift", exact: true });
  await evidence.focus(); await page.keyboard.press("Enter");
  await expect(page.getByRole("dialog")).toContainText("APPROVED LATE OPTION");
  await page.keyboard.press("Escape");
  await expect(evidence).toBeFocused();
  await panel.screenshot({ path: info.outputPath("resilient-mobile.png") });
  expect(await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)).toBeLessThanOrEqual(0);
  const adopt = panel.getByRole("button", { name: "Adopt verified schedule", exact: true });
  await adopt.focus(); await page.keyboard.press("Enter");
  await expect(page.getByTestId("minimum-balance")).toContainText("$49");
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.getByTestId("verification-panel").screenshot({ path: info.outputPath("adopted-desktop.png") });
});
