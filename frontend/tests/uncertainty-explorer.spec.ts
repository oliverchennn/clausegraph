import { expect, test } from "@playwright/test";

async function open(page: import("@playwright/test").Page) {
  await page.goto("/");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  return page.getByTestId("verification-panel");
}

test("dimensions can be added and removed up to the contract limit of eight", async ({ page }) => {
  const panel = await open(page);
  await expect(panel.getByTestId("dimension-count")).toHaveText("0 / 8 dimensions");
  await panel.getByTestId("add-income-date").click();
  await panel.getByTestId("add-income-amount").click();
  await expect(panel.getByTestId("dimension-count")).toHaveText("2 / 8 dimensions");
  // Approval targets exist in the synthetic scenario; fill to the limit.
  for (let index = 0; index < 6; index += 1) await panel.getByTestId("add-approval").click();
  await expect(panel.getByTestId("dimension-count")).toHaveText("8 / 8 dimensions");
  await expect(panel.getByTestId("add-approval")).toBeDisabled();
  await expect(panel.getByTestId("add-income-date")).toBeDisabled();
  await panel.getByRole("button", { name: "Remove date-1" }).click();
  await expect(panel.getByTestId("dimension-count")).toHaveText("7 / 8 dimensions");
  await expect(panel.getByTestId("add-income-date")).toBeEnabled();
});

test("an inclusive $100 amount range counts 10001 values and warns about the case cap", async ({ page }) => {
  const panel = await open(page);
  await panel.getByTestId("add-income-amount").click();
  await panel.getByLabel("Minimum cents for amount-1").fill("0");
  await panel.getByLabel("Maximum cents for amount-1").fill("10000");
  // Every inclusive cent counts: 0..10000 is 10001 values, one above the budget.
  await expect(panel.getByTestId("preflight-count")).toContainText("10001");
  await expect(panel.getByTestId("budget-warning")).toContainText("Above the 10000-case budget");
  await expect(panel.getByTestId("budget-warning")).toContainText("will not return Safe");
});

test("counts beyond JavaScript's safe integer range stay exact", async ({ page }) => {
  const panel = await open(page);
  await panel.getByTestId("add-income-amount").click();
  await panel.getByLabel("Minimum cents for amount-1").fill("0");
  await panel.getByLabel("Maximum cents for amount-1").fill("10000000000");
  await panel.getByTestId("add-income-date").click();
  await panel.getByLabel("Latest for date-1").fill("2026-09-28");
  await panel.getByLabel("Earliest for date-1").fill("2026-09-21");
  // 8 dates x 10,000,000,001 cents, computed with BigInt rather than as a float.
  const expected = (BigInt(8) * BigInt("10000000001")).toString();
  expect(expected).toBe("80000000008");
  const shown = (await panel.getByTestId("preflight-count").innerText()).replace(/\s+/g, " ");
  // Rendered in full precision: no exponent form, no grouping, no truncation.
  expect(shown).toContain(expected);
  expect(shown).not.toMatch(/e\+?\d/i);
});

test("a duplicate property of the same target is rejected before sending", async ({ page }) => {
  const panel = await open(page);
  await panel.getByTestId("add-income-date").click();
  await panel.getByTestId("add-income-date").click();
  await expect(panel.getByTestId("duplicate-date-2")).toContainText("already declared");
  await expect(panel.getByRole("button", { name: "Verify fixed plan" })).toBeDisabled();
  await panel.getByRole("button", { name: "Remove date-2" }).click();
  await expect(panel.getByRole("button", { name: "Verify fixed plan" })).toBeEnabled();
});

test("declared combinations match the backend and the fixed schedule is preserved", async ({ page }) => {
  const panel = await open(page);
  const before = await page.evaluate(async () => {
    const response = await fetch("/api/workspace", { headers: { Authorization: `Bearer ${localStorage.getItem("clausegraph.session")}` } });
    return response.json();
  });
  await panel.getByRole("button", { name: "Payday through Sep 28" }).click();
  await panel.getByTestId("add-approval").click();
  // 8 dates x 3 approval outcomes = 24 cases, and the browser count must agree.
  await expect(panel.getByTestId("preflight-count")).toContainText("24");
  const verified = page.waitForResponse(r => r.url().endsWith("/api/verify") && r.request().method() === "POST");
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  const body = await (await verified).json();
  expect(body.total_cases).toBe(24);
  expect(body.dimension_count).toBe(2);
  expect(body.fixed_actions).toEqual(before.plan.actions);
  // Nominal assumptions survive alongside the declared dimensions.
  expect(body.nominal_assumptions).toBeTruthy();
  const after = await page.evaluate(async () => {
    const response = await fetch("/api/workspace", { headers: { Authorization: `Bearer ${localStorage.getItem("clausegraph.session")}` } });
    return response.json();
  });
  expect(after.revision).toBe(before.revision);
  expect(after.plan.actions).toEqual(before.plan.actions);
});

test("editing a declared bound clears the previous result rather than relabelling it", async ({ page }) => {
  const panel = await open(page);
  await panel.getByRole("button", { name: "Payday through Sep 28" }).click();
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  await expect(page.getByTestId("verification-result")).toBeVisible();
  await panel.getByLabel("Latest for payday").fill("2026-09-26");
  await expect(page.getByTestId("verification-result")).toHaveCount(0);
});

test("the controls are keyboard operable at 390px without horizontal overflow", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const panel = await open(page);
  await panel.getByTestId("add-income-date").focus();
  await page.keyboard.press("Enter");
  await expect(panel.getByTestId("dimension-count")).toHaveText("1 / 8 dimensions");
  await panel.getByRole("button", { name: "Remove date-1" }).focus();
  await page.keyboard.press("Enter");
  await expect(panel.getByTestId("dimension-count")).toHaveText("0 / 8 dimensions");
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(0);
});
