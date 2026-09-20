import { expect, test } from "@playwright/test";
import { dayOrdinal, draftBlockers, exactCaseCount } from "../src/lib/uncertainty";
import type { Uncertainty } from "../src/lib/types";

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

test("counts beyond JavaScript's safe integer range stay exact", async ({ page }, testInfo) => {
  const panel = await open(page);
  await panel.getByTestId("add-income-amount").click();
  await panel.getByLabel("Minimum cents for amount-1").fill("0");
  await panel.getByLabel("Maximum cents for amount-1").fill("10000000000");
  await panel.getByTestId("add-income-date").click();
  await panel.getByLabel("Latest for date-1").fill("9999-12-30");
  await panel.getByLabel("Earliest for date-1").fill("2026-09-21");
  // Python datetime independently gives 2,912,179 inclusive dates here.
  // This odd product actually exceeds MAX_SAFE_INTEGER and rounds as Number.
  const expected = "29121790002912179";
  expect(BigInt(expected)).toBeGreaterThan(BigInt(Number.MAX_SAFE_INTEGER));
  expect(BigInt(Number(expected)).toString()).not.toBe(expected);
  const shown = (await panel.getByTestId("preflight-count").innerText()).replace(/\s+/g, " ");
  // Rendered in full precision: no exponent form, no grouping, no truncation.
  expect(shown).toContain(expected);
  expect(shown).not.toMatch(/e\+?\d/i);
  await expect(panel.getByTestId("huge-count")).toBeVisible();
  // A one-case real API cutoff keeps this regression fast without narrowing bounds.
  await page.route("**/api/verify", async route => {
    const body = JSON.parse(route.request().postData() || "{}");
    await route.continue({ postData: JSON.stringify({ ...body, max_cases: 1 }) });
  });
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  const result = page.getByTestId("verification-result");
  await expect(result.locator(".verification-facts")).toContainText(`1 / ${expected}`);
  await result.locator(".verification-facts").screenshot({ path: testInfo.outputPath("large-result-count.png") });
  await expect(result).toContainText("bounded check incomplete");
  await panel.getByRole("button", { name: "Explain cash gap" }).click();
  await expect(page.getByTestId("cash-gap-diagnostic").getByLabel("Fixed schedule cash comparison")).toContainText(`1 / ${expected}`);
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

test("the controls are keyboard operable at 390px without horizontal overflow", async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const panel = await open(page);
  await panel.getByTestId("add-income-date").focus();
  await page.keyboard.press("Enter");
  await expect(panel.getByTestId("dimension-count")).toHaveText("1 / 8 dimensions");
  await panel.screenshot({ path: testInfo.outputPath("uncertainty-mobile.png") });
  await panel.getByRole("button", { name: "Remove date-1" }).focus();
  await page.keyboard.press("Enter");
  await expect(panel.getByTestId("dimension-count")).toHaveText("0 / 8 dimensions");
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(0);
});

test("date cardinality is exact across DST, leap day and years below 100", () => {
  const cases: [string, string, string][] = [
    // US DST spring-forward: a 23-hour local day must not lose a date.
    ["2026-03-01", "2026-03-31", "31"],
    // Leap day: 2028 is a leap year, so February has 29 days.
    ["2028-02-01", "2028-03-01", "30"],
    // Non-leap century.
    ["2100-02-01", "2100-03-01", "29"],
    ["0004-02-28", "0004-03-01", "3"],
    ["0099-12-31", "0100-01-01", "2"],
    // Single day is one assignment, not zero.
    ["2026-09-21", "2026-09-21", "1"],
  ];
  for (const [earliest, latest, expected] of cases) {
    expect((dayOrdinal(latest)! - dayOrdinal(earliest)! + BigInt(1)).toString()).toBe(expected);
  }
  for (const invalid of ["0000-01-01", "2026-02-29", "2026-04-31", "2026-13-01", "2026-09-00", "2026-9-1"]) expect(dayOrdinal(invalid)).toBeNull();
});

test("an invalid draft has no valid count and cannot be submitted", async ({ page }) => {
  const panel = await open(page);
  await panel.getByTestId("add-income-date").click();
  // Latest before earliest: an empty domain, not a silent reordering.
  await panel.getByLabel("Earliest for date-1").fill("2026-09-28");
  await panel.getByLabel("Latest for date-1").fill("2026-09-21");
  await expect(panel.getByTestId("preflight-count")).toContainText("Invalid draft");
  await expect(panel.getByRole("button", { name: "Verify fixed plan" })).toBeDisabled();
  await panel.getByLabel("Latest for date-1").fill("2026-09-28");
  await expect(panel.getByRole("button", { name: "Verify fixed plan" })).toBeEnabled();
});

test("a blank rationale blocks submission", async ({ page }) => {
  const panel = await open(page);
  await panel.getByTestId("add-approval").click();
  await panel.getByLabel("Rationale for approval-1").fill("");
  await expect(panel.getByRole("button", { name: "Verify fixed plan" })).toBeDisabled();
  await expect(panel.getByTestId("preflight-count")).toContainText("no valid case count");
});

test("invalid cents and historical dates have no valid preflight count", async ({ page }) => {
  const panel = await open(page);
  await panel.getByTestId("add-income-amount").click();
  await panel.getByLabel("Maximum cents for amount-1").fill("10000000001");
  await expect(panel.getByTestId("preflight-count")).toContainText("Invalid draft");
  await expect(panel.getByRole("button", { name: "Verify fixed plan" })).toBeDisabled();
  await panel.getByRole("button", { name: "Remove amount-1" }).click();
  await panel.getByTestId("add-income-date").click();
  await panel.getByLabel("Earliest for date-1").fill("2026-08-31");
  await expect(panel.getByTestId("preflight-count")).toContainText("cannot precede the horizon start");
  await expect(panel.getByRole("button", { name: "Verify fixed plan" })).toBeDisabled();
});

test("zero dimensions is one case and duplicate IDs or a ninth dimension are invalid", () => {
  expect(exactCaseCount([])).toBe(BigInt(1));
  const dimensions: Uncertainty[] = Array.from({ length: 9 }, (_, index) => ({
    id: `dimension-${index}`, kind: "approval", basis: "user_assumption", rationale: "Explicit hypothetical outcome.",
    target_id: `target-${index}`, outcomes: ["approved"],
  }));
  expect(draftBlockers(dimensions)).toContain("At most 8 dimensions may be declared.");
  dimensions[1].id = dimensions[0].id;
  expect(draftBlockers(dimensions.slice(0, 2))).toContain("Dimension identifiers must be unique.");
});
