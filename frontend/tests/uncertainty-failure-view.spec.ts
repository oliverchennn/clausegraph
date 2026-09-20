import { expect, test, type Page } from "@playwright/test";

async function open(page: Page, last = 28) {
  await page.goto("/");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  const panel = page.getByTestId("verification-panel");
  await panel.getByRole("button", { name: `Payday through Sep ${last}` }).click();
  return panel;
}

test("a real failure witness has separate coverage, source navigation and worst cash", async ({ page }, info) => {
  const panel = await open(page);
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  const view = page.getByTestId("uncertainty-failure-view");
  await expect(view.getByLabel("Evaluated and unchecked cases")).toContainText("8 of 8");
  await expect(view.getByTestId("unchecked-cases")).toHaveText("0");
  await expect(view.getByTestId("witness-details")).toContainText("2026-09-27");
  await expect(view.getByTestId("witness-details")).toContainText("2026-09-26");
  await expect(view.getByTestId("witness-details")).toContainText("-$400.00");
  await expect(view.getByRole("table")).toContainText("nonnegative balance");
  const source = view.getByRole("button", { name: "Evidence for failure 1", exact: true });
  await source.focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("dialog").getByRole("heading", { name: "Follow the evidence" })).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(source).toBeFocused();
  await view.getByText("Proven worst cash within these bounds", { exact: true }).click();
  await expect(view.getByTestId("worst-permitted-cash")).toContainText("Minimum: -$400.00");
  await view.screenshot({ path: info.outputPath("failure-desktop.png") });
  await panel.getByLabel("Latest for payday").fill("2026-09-26");
  await expect(view).toHaveCount(0);
});

test("approval failure has no substituted cash and remains usable as a mobile list", async ({ page }, info) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const panel = await open(page);
  await panel.getByTestId("add-approval").click();
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  const view = page.getByTestId("uncertainty-failure-view");
  await expect(view.getByTestId("witness-no-cash")).toBeVisible();
  await expect(view.getByRole("table")).toBeHidden();
  const failures = view.getByRole("list", { name: "Properties violated by this witness" });
  await expect(failures).toContainText("authorization");
  await expect(view.getByTestId("witness-details")).not.toContainText("Balance at the witness failure");
  const source = failures.getByRole("button", { name: "Evidence for failure 1", exact: true });
  await source.focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.keyboard.press("Escape");
  await view.screenshot({ path: info.outputPath("failure-mobile.png") });
  expect(await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)).toBeLessThanOrEqual(0);
});

test("safe and incomplete unknown results never invent a failure or exhaustive claim", async ({ page }) => {
  const panel = await open(page, 26);
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  const view = page.getByTestId("uncertainty-failure-view");
  await expect(view).toContainText("All declared cases passed");
  await expect(view.getByTestId("witness-details")).toHaveCount(0);
  await page.route("**/api/verify", route => route.continue({ postData: JSON.stringify({ ...route.request().postDataJSON(), max_cases: 1 }) }));
  await panel.getByRole("button", { name: "Payday through Sep 28" }).click();
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  await expect(view).toContainText("safety remains unknown");
  await expect(view.getByTestId("unchecked-cases")).toHaveText("7");
  await expect(view.getByTestId("witness-details")).toHaveCount(0);
  await expect(view.getByTestId("worst-permitted-cash")).toContainText("worst case not proven");
});

test("a partial unsafe witness still proves failure and huge unchecked counts remain exact", async ({ page }) => {
  const panel = await open(page);
  await panel.getByTestId("add-income-amount").click();
  await panel.getByLabel("Minimum cents for amount-1").fill("0");
  await panel.getByLabel("Maximum cents for amount-1").fill("10000000000");
  await panel.getByLabel("Latest for payday").fill("9999-12-30");
  await page.route("**/api/verify", route => route.continue({ postData: JSON.stringify({ ...route.request().postDataJSON(), max_cases: 1 }) }));
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  const view = page.getByTestId("uncertainty-failure-view");
  await expect(view).toContainText("This witness proves a failure");
  await expect(view.getByTestId("unchecked-cases")).toHaveText("29121790002912178");
  await expect(view.getByTestId("witness-details")).toBeVisible();
});

test("presentation fixture: complete but unresolved coverage is not safe", async ({ page }) => {
  const panel = await open(page, 26);
  // Only this response-label edge is a presentation fixture; other cases use the real API result.
  await page.route("**/api/verify", async route => {
    const response = await route.fetch();
    const body = await response.json();
    await route.fulfill({ response, json: { ...body, status: "UNKNOWN", worst_case: null, worst_case_proven: false, statement: "Required ledger facts remain unresolved." } });
  });
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  const view = page.getByTestId("uncertainty-failure-view");
  await expect(view).toContainText("Complete coverage does not establish safety");
  await expect(view.getByTestId("unchecked-cases")).toHaveText("0");
  await expect(view).not.toContainText("All declared cases passed");
  await view.getByText("Observed permitted cash only · worst case not proven", { exact: true }).click();
  await expect(view).toContainText("Missing cash is not zero");
});
