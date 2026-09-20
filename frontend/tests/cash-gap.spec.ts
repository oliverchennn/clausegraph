import { expect, test, type Page } from "@playwright/test";

async function readApi<T>(page: Page, path: string): Promise<T> {
  return page.evaluate(async apiPath => {
    const response = await fetch(`/api${apiPath}`, { headers: { Authorization: `Bearer ${localStorage.getItem("clausegraph.session")}` } });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }, path);
}

async function verifyEightDateFailure(page: Page) {
  const panel = page.getByTestId("verification-panel");
  await panel.getByRole("button", { name: "Payday through Sep 28" }).click();
  const response = page.waitForResponse(item => item.url().endsWith("/api/verify") && item.request().method() === "POST");
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  expect((await (await response).json()).status).toBe("UNSAFE");
  await expect(page.getByTestId("verification-result").getByText("Unsafe", { exact: true })).toBeVisible();
  return panel;
}

test("proven cash buffer compares the same schedule, links evidence, and mutates nothing", async ({ page }, testInfo) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  const before = await readApi<{ revision: number; plan: { id: string; actions: unknown[] }; scenario: { opening_balance_cents: number } }>(page, "/workspace");
  const panel = await verifyEightDateFailure(page);
  const verificationsBefore = await readApi<unknown[]>(page, "/verifications");

  const response = page.waitForResponse(item => item.url().endsWith("/api/cash-gap") && item.request().method() === "POST");
  await panel.getByRole("button", { name: "Explain cash gap" }).click();
  const diagnostic = await (await response).json();
  expect(diagnostic.status).toBe("PROVEN_MINIMUM");
  expect(diagnostic.additional_opening_cash_cents).toBe(40000);
  expect(diagnostic.lower_bound_cents).toBe(40000);
  expect(diagnostic.minimality_proven).toBe(true);
  expect(diagnostic.is_funding).toBe(false);
  expect(diagnostic.limiting_date).toBe("2026-09-26");
  expect(diagnostic.limiting_event_ids).toContain("loan");
  expect(diagnostic.limiting_rule_ids).toContain("rule-loan");
  expect(diagnostic.minimality_witness).toMatchObject({ tested_additional_cents: 39999, status: "UNSAFE", coverage_complete: true });
  expect(diagnostic.baseline.fixed_actions).toEqual(before.plan.actions);
  expect(diagnostic.funded.fixed_actions).toEqual(before.plan.actions);
  expect(diagnostic.funded.status).toBe("SAFE");

  const result = page.getByTestId("cash-gap-diagnostic");
  await expect(result.getByText("Proven minimum", { exact: true })).toBeVisible();
  await expect(result).toContainText("$400.00");
  await expect(result).toContainText("Original fixed schedule");
  await expect(result).toContainText("Same actions and dates");
  await expect(result).toContainText("Proven worst-case minimum -$400.00");
  await expect(result).toContainText("Proven worst-case minimum $0.00");
  await expect(result).toContainText("One-cent check: $399.99 was unsafe");
  await expect(result).toContainText("Sep 26");
  await expect(result).toContainText("Hypothetical only—not funding, income, approval or permission");
  await expect(result.getByText(/Future obligations remain visible/)).toBeVisible();
  await result.screenshot({ path: testInfo.outputPath("cash-gap-proven.png") });

  const evidenceButton = result.getByRole("button", { name: "Open limiting evidence" });
  await evidenceButton.focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("dialog").getByRole("heading", { name: "Follow the evidence" })).toBeVisible();
  await expect(page.getByTestId("rule-rule-loan")).toBeVisible();
  await page.getByRole("button", { name: "Close dialog" }).click();
  await expect(evidenceButton).toBeFocused();

  const after = await readApi<typeof before>(page, "/workspace");
  expect(after).toEqual(before);
  expect(await readApi<unknown[]>(page, "/verifications")).toEqual(verificationsBefore);
  await page.reload();
  await expect(page.getByTestId("cash-gap-diagnostic")).not.toBeVisible();
  expect(await readApi<typeof before>(page, "/workspace")).toEqual(before);
  expect(errors).toEqual([]);
});

test("authorization failures and incomplete coverage never become funding claims", async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  const panel = page.getByTestId("verification-panel");
  await panel.getByLabel("Verification approval outcomes").selectOption("shift-payment");
  const verifyResponse = page.waitForResponse(item => item.url().endsWith("/api/verify") && item.request().method() === "POST");
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  expect((await (await verifyResponse).json()).status).toBe("UNSAFE");
  const blockedResponse = page.waitForResponse(item => item.url().endsWith("/api/cash-gap") && item.request().method() === "POST");
  await panel.getByRole("button", { name: "Explain cash gap" }).click();
  const blocked = await (await blockedResponse).json();
  expect(blocked.status).toBe("NOT_REPAIRABLE_WITH_CASH");
  expect(blocked.additional_opening_cash_cents).toBeNull();
  expect(blocked.funded).toBeNull();
  expect(blocked.blocking_properties).toContain("authorization");
  let result = page.getByTestId("cash-gap-diagnostic");
  await expect(result.getByText("Cash cannot repair", { exact: true })).toBeVisible();
  await expect(result).toContainText("No cash amount established");
  await expect(result).toContainText("Cash cannot grant permission");
  await expect(result).toContainText("No verified cash comparison");
  await expect(result).not.toContainText("Verified-sufficient fixed-schedule buffer");

  await panel.getByLabel("Verification approval outcomes").selectOption("");
  await panel.getByRole("button", { name: "Payday through Sep 28" }).click();
  const unsafeResponse = page.waitForResponse(item => item.url().endsWith("/api/verify") && item.request().method() === "POST");
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  expect((await (await unsafeResponse).json()).status).toBe("UNSAFE");
  await page.route("**/api/cash-gap", route => route.continue({ postData: JSON.stringify({ ...route.request().postDataJSON(), max_cases: 1 }) }));
  const incompleteResponse = page.waitForResponse(item => item.url().endsWith("/api/cash-gap") && item.request().method() === "POST");
  await panel.getByRole("button", { name: "Explain cash gap" }).click();
  const incomplete = await (await incompleteResponse).json();
  expect(incomplete.status).toBe("INCONCLUSIVE");
  expect(incomplete.additional_opening_cash_cents).toBeNull();
  expect(incomplete.baseline.coverage_complete).toBe(false);
  result = page.getByTestId("cash-gap-diagnostic");
  await expect(result.getByText("Inconclusive", { exact: true })).toBeVisible();
  await expect(result).toContainText("No cash amount established");
  await expect(result).toContainText("1 / 8 cases checked · incomplete coverage");
  await expect(result).toContainText("Observed minimum $50.00; worst case not proven");
  await expect(result).not.toContainText("invalid schedule");
  await expect(page.getByText("Proven minimum", { exact: true })).not.toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await result.screenshot({ path: testInfo.outputPath("cash-gap-mobile-inconclusive.png") });
});

test("assumption, plan, revision, and session changes clear cash diagnostics and abort stale responses", async ({ page }) => {
  await page.goto("/");
  const panel = await verifyEightDateFailure(page);
  let intercepted!: () => void;
  let release!: () => void;
  const interceptedPromise = new Promise<void>(resolve => { intercepted = resolve; });
  const releasePromise = new Promise<void>(resolve => { release = resolve; });
  await page.route("**/api/cash-gap", async route => {
    intercepted();
    await releasePromise;
    await route.continue().catch(() => undefined);
  });
  await panel.getByRole("button", { name: "Explain cash gap" }).click();
  await interceptedPromise;
  await panel.getByLabel("Latest verification payday").fill("2026-09-26");
  release();
  await expect(page.getByTestId("verification-result")).not.toBeVisible();
  await expect(page.getByTestId("cash-gap-diagnostic")).not.toBeVisible();
  await page.unroute("**/api/cash-gap");

  await panel.getByRole("button", { name: "Payday through Sep 28" }).click();
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  await expect(page.getByTestId("verification-result").getByText("Unsafe", { exact: true })).toBeVisible();
  await panel.getByRole("button", { name: "Explain cash gap" }).click();
  await expect(page.getByTestId("cash-gap-diagnostic")).toBeVisible();

  await page.getByLabel("Scenario available cash").fill("2100.00");
  await page.getByRole("button", { name: "Preview side by side" }).click();
  await page.getByRole("button", { name: "Use this preview as plan" }).click();
  await expect(page.getByTestId("cash-gap-diagnostic")).not.toBeVisible();

  const changedPlanPanel = await verifyEightDateFailure(page);
  await changedPlanPanel.getByRole("button", { name: "Explain cash gap" }).click();
  await expect(page.getByTestId("cash-gap-diagnostic")).toBeVisible();
  await page.getByTestId("action-shift-payment").getByRole("button", { name: /View evidence/ }).click();
  const rule = page.getByTestId("rule-rule-shift");
  await rule.getByLabel("Approval for Approved payment shift").selectOption("denied");
  await rule.getByRole("button", { name: "Save review & recalculate" }).click();
  await expect(rule.getByRole("button", { name: "Review saved" })).toBeVisible();
  await page.getByRole("button", { name: "Close dialog" }).click();
  await expect(page.getByTestId("cash-gap-diagnostic")).not.toBeVisible();

  const previousSession = await page.evaluate(() => localStorage.getItem("clausegraph.session"));
  await page.getByRole("button", { name: "Start my own plan" }).click();
  await expect(page.getByText("Set up my financial picture", { exact: true })).toBeVisible();
  expect(await page.evaluate(() => localStorage.getItem("clausegraph.session"))).not.toBe(previousSession);
  await expect(page.getByTestId("cash-gap-diagnostic")).not.toBeVisible();
});
