import { expect, test } from "@playwright/test";

const PAYDAY_THROUGH_28 = "Payday through Sep 28";

async function runUnsafeVerification(page: import("@playwright/test").Page) {
  await page.goto("/");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  const panel = page.getByTestId("verification-panel");
  await panel.getByRole("button", { name: PAYDAY_THROUGH_28 }).click();
  const verified = page.waitForResponse(r => r.url().endsWith("/api/verify") && r.request().method() === "POST");
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  expect((await (await verified).json()).status).toBe("UNSAFE");
  return panel;
}

test("the diagnostic explains the buffer, its evidence and that the saved plan is untouched", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  const panel = await runUnsafeVerification(page);
  const before = await page.evaluate(async () => {
    const response = await fetch("/api/workspace", { headers: { Authorization: `Bearer ${localStorage.getItem("clausegraph.session")}` } });
    return response.json();
  });

  const diagnosed = page.waitForResponse(r => r.url().endsWith("/api/cash-gap") && r.request().method() === "POST");
  await panel.getByTestId("cash-gap-run").click();
  const body = await (await diagnosed).json();
  expect(body.status).toBe("PROVEN_MINIMUM");
  expect(body.additional_opening_cash_cents).toBe(40000);
  expect(body.minimality_proven).toBe(true);
  expect(body.is_funding).toBe(false);

  const result = page.getByTestId("cash-gap-result");
  await expect(page.getByTestId("cash-gap-status")).toHaveText("Proven minimum for this schedule");
  await expect(page.getByTestId("cash-gap-amount")).toContainText("$400");
  await expect(page.getByTestId("cash-gap-amount")).toContainText("proven minimum for this fixed schedule");
  await expect(page.getByTestId("cash-gap-not-funding")).toContainText("not funding");
  await expect(page.getByTestId("cash-gap-limiting-date")).toHaveText("2026-09-26");
  // The original schedule and the same schedule under the cash assumption, side by side.
  await expect(page.getByTestId("cash-gap-compare")).toContainText("UNSAFE");
  await expect(page.getByTestId("cash-gap-compare")).toContainText("SAFE");
  await expect(result).toContainText("Complete · 8 of 8 cases");

  // Evidence for the limiting date reaches the real source drawer.
  await page.getByTestId("cash-gap-evidence").click();
  await expect(page.getByRole("dialog").getByRole("heading", { name: "Follow the evidence" })).toBeVisible();
  await page.getByRole("button", { name: "Close dialog" }).click();

  // Nothing was written: same revision, same plan, no saved verification beyond the one we ran.
  const after = await page.evaluate(async () => {
    const response = await fetch("/api/workspace", { headers: { Authorization: `Bearer ${localStorage.getItem("clausegraph.session")}` } });
    return response.json();
  });
  expect(after.revision).toBe(before.revision);
  expect(after.plan).toEqual(before.plan);
  expect(after.scenario.opening_balance_cents).toBe(before.scenario.opening_balance_cents);
  expect(errors).toEqual([]);
});

test("a denied approval is reported as unrepairable by cash rather than as an amount", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  const panel = page.getByTestId("verification-panel");
  await panel.getByLabel("Verification approval outcomes").selectOption({ index: 1 });
  const verified = page.waitForResponse(r => r.url().endsWith("/api/verify") && r.request().method() === "POST");
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  expect((await (await verified).json()).status).toBe("UNSAFE");

  const diagnosed = page.waitForResponse(r => r.url().endsWith("/api/cash-gap") && r.request().method() === "POST");
  await panel.getByTestId("cash-gap-run").click();
  const body = await (await diagnosed).json();
  expect(body.status).toBe("NOT_REPAIRABLE_WITH_CASH");
  expect(body.additional_opening_cash_cents).toBeNull();

  await expect(page.getByTestId("cash-gap-status")).toHaveText("Cash cannot repair this");
  await expect(page.getByTestId("cash-gap-amount")).toContainText("No amount established");
  await expect(page.getByTestId("cash-gap-blockers")).toContainText("authorization");
  await expect(page.getByTestId("cash-gap-blockers")).toContainText("never repaired by adding money");
});

test("an incomplete check is labelled inconclusive and never as an exact minimum", async ({ page }) => {
  const panel = await runUnsafeVerification(page);
  // Force a case cutoff on the diagnostic request only; the verification above was complete.
  await page.route("**/api/cash-gap", async route => {
    const payload = JSON.parse(route.request().postData() || "{}");
    await route.continue({ postData: JSON.stringify({ ...payload, max_cases: 2 }) });
  });
  const diagnosed = page.waitForResponse(r => r.url().endsWith("/api/cash-gap") && r.request().method() === "POST");
  await panel.getByTestId("cash-gap-run").click();
  const body = await (await diagnosed).json();
  expect(body.status).toBe("INCONCLUSIVE");
  expect(body.additional_opening_cash_cents).toBeNull();
  expect(body.minimality_proven).toBe(false);

  await expect(page.getByTestId("cash-gap-status")).toHaveText("Inconclusive · coverage stopped early");
  await expect(page.getByTestId("cash-gap-amount")).toContainText("No amount established");
  await expect(page.getByTestId("cash-gap-result")).toContainText("Incomplete · 2 of 8 cases checked");
});

test("a failed diagnostic is retryable and reports no amount", async ({ page }) => {
  const panel = await runUnsafeVerification(page);
  let recovered = false;
  await page.route("**/api/cash-gap", async route => {
    if (recovered) { await route.continue(); return; }
    await route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ detail: "Diagnostic unavailable." }) });
  });
  await panel.getByTestId("cash-gap-run").click();
  await expect(panel.getByRole("alert")).toContainText("Diagnostic unavailable");
  await expect(page.getByTestId("cash-gap-result")).toHaveCount(0);
  recovered = true;
  await panel.getByRole("button", { name: "Try again" }).click();
  await expect(page.getByTestId("cash-gap-amount")).toContainText("$400");
});

test("changing the declared assumptions clears a stale diagnostic", async ({ page }) => {
  const panel = await runUnsafeVerification(page);
  await panel.getByTestId("cash-gap-run").click();
  await expect(page.getByTestId("cash-gap-amount")).toContainText("$400");
  // Re-verify on the narrower preset: the previous diagnostic belonged to the old result.
  await panel.getByRole("button", { name: "Payday through Sep 26" }).click();
  await expect(page.getByTestId("cash-gap-result")).toHaveCount(0);
  const verified = page.waitForResponse(r => r.url().endsWith("/api/verify") && r.request().method() === "POST");
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  expect((await (await verified).json()).status).toBe("SAFE");
  // A safe fixed-plan result offers no gap to diagnose at all.
  await expect(page.getByTestId("cash-gap")).toHaveCount(0);
});

test("the diagnostic is readable and keyboard reachable at 390px", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const panel = await runUnsafeVerification(page);
  await panel.getByTestId("cash-gap-run").focus();
  await expect(panel.getByTestId("cash-gap-run")).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.getByTestId("cash-gap-amount")).toContainText("$400");
  // No horizontal overflow introduced by the comparison grid at mobile width.
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(0);
  const box = await page.getByTestId("cash-gap-result").boundingBox();
  expect(box!.width).toBeLessThanOrEqual(390);
});
