import { expect, test } from "@playwright/test";

test("fixed-plan verification exposes a counterexample, proves bounded safety, and invalidates changed inputs", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  await expect(page.getByText("Nominal optimum proven", { exact: true })).toBeVisible();
  const initial = await page.evaluate(async () => {
    const response = await fetch("/api/workspace", { headers: { Authorization: `Bearer ${localStorage.getItem("clausegraph.session")}` } });
    return response.json();
  });
  const panel = page.getByTestId("verification-panel");
  await panel.getByRole("button", { name: "Payday through Sep 28" }).click();
  const unsafeResponse = page.waitForResponse(response => response.url().endsWith("/api/verify") && response.request().method() === "POST");
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  const unsafe = await (await unsafeResponse).json();
  expect(unsafe.status).toBe("UNSAFE");
  expect(unsafe.counterexample.earliest_failing_date).toBe("2026-09-26");
  expect(unsafe.counterexample.balance_cents).toBe(-40000);
  expect(unsafe.fixed_actions).toEqual(initial.plan.actions);
  expect(unsafe.checked_cases).toBe(8);
  expect(unsafe.coverage_complete).toBe(true);
  const result = page.getByTestId("verification-result");
  await expect(result.getByText("Unsafe", { exact: true })).toBeVisible();
  await expect(result).toContainText("Earliest failing date: 2026-09-26");
  await expect(result).toContainText("Balance: -$400");
  await expect(page.getByTestId("verification-worst-balance")).toHaveText("-$400");
  await expect(page.getByRole("img", { name: /Cash projection.*Counterexample minimum/ })).toBeVisible();
  await expect(result).toContainText("8 / 8");
  await expect(result).toContainText("2026-09-21 through 2026-09-28, inclusive");
  await result.getByRole("button", { name: "Event evidence", exact: true }).first().click();
  await expect(page.getByRole("dialog").getByRole("heading", { name: "Follow the evidence" })).toBeVisible();
  await page.getByRole("button", { name: "Close dialog" }).click();
  await page.getByRole("tab", { name: "Documents & facts" }).click();
  await page.getByRole("tab", { name: "Overview", exact: true }).click();
  await expect(panel.getByLabel("Latest verification payday")).toHaveValue("2026-09-28");
  await expect(result.getByText("Unsafe", { exact: true })).toBeVisible();

  await panel.getByRole("button", { name: "Payday through Sep 26" }).click();
  await expect(result).not.toBeVisible();
  await expect(page.getByRole("img", { name: /Cash projection.*Counterexample minimum/ })).not.toBeVisible();
  const safeResponse = page.waitForResponse(response => response.url().endsWith("/api/verify") && response.request().method() === "POST");
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  const safe = await (await safeResponse).json();
  expect(safe.status).toBe("SAFE");
  expect(safe.checked_cases).toBe(6);
  expect(safe.worst_case_proven).toBe(true);
  await expect(result.getByText("Verified Safe", { exact: true })).toBeVisible();
  await expect(result).toContainText("6 / 6");
  await expect(result).toContainText("Applies only to the declared bounds");
  await expect(page.getByTestId("verification-worst-balance")).toHaveText("$50");
  const unchanged = await page.evaluate(async () => {
    const response = await fetch("/api/workspace", { headers: { Authorization: `Bearer ${localStorage.getItem("clausegraph.session")}` } });
    return response.json();
  });
  expect(unchanged.plan.id).toBe(initial.plan.id);
  expect(unchanged.revision).toBe(initial.revision);
  expect(unchanged.plan.actions).toEqual(initial.plan.actions);

  // A new nominal plan invalidates the prior bounded result even at the same input revision.
  await page.getByLabel("Scenario available cash").fill("2100.00");
  await page.getByRole("button", { name: "Recalculate scenario" }).click();
  await expect(page.getByTestId("minimum-balance")).toContainText("$150");
  await expect(result).not.toBeVisible();
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  await expect(result.getByText("Verified Safe", { exact: true })).toBeVisible();

  // Recorded evidence changes the workspace revision and removes the old result.
  await page.getByTestId("action-shift-payment").getByRole("button", { name: "View evidence", exact: true }).click();
  const shift = page.getByTestId("rule-rule-shift");
  await shift.getByLabel("Approval for Approved payment shift").selectOption("denied");
  await shift.getByRole("button", { name: "Save review & recalculate" }).click();
  await expect(shift.getByRole("button", { name: "Review saved" })).toBeVisible();
  await page.getByRole("button", { name: "Close dialog" }).click();
  await expect(result).not.toBeVisible();
  expect(errors).toEqual([]);
});

test("approval uncertainty stays hypothetical and invalid schedules have no cash overlay", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  const panel = page.getByTestId("verification-panel");
  await panel.getByLabel("Verification approval outcomes").selectOption("shift-payment");
  const response = page.waitForResponse(item => item.url().endsWith("/api/verify") && item.request().method() === "POST");
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  const result = await (await response).json();
  expect(result.status).toBe("UNSAFE");
  expect(result.counterexample.failures.some((failure: { property: string }) => failure.property === "authorization")).toBe(true);
  expect(result.counterexample.simulation).toBeNull();
  await expect(page.getByTestId("verification-result").getByText("Unsafe", { exact: true })).toBeVisible();
  await expect(page.getByTestId("verification-worst-balance")).toHaveText("Not proven");
  await expect(page.getByRole("img", { name: /Cash projection.*Counterexample minimum/ })).not.toBeVisible();
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});

test("an incomplete real verification response remains Unknown", async ({ page }) => {
  // Lower the real server's case budget to deterministically exercise incomplete coverage.
  // The request still reaches FastAPI and the actual verifier; no response is mocked.
  await page.route("**/api/verify", route => route.continue({ postData: JSON.stringify({ ...route.request().postDataJSON(), max_cases: 1 }) }));
  await page.goto("/");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  const panel = page.getByTestId("verification-panel");
  await panel.getByRole("button", { name: "Payday through Sep 28" }).click();
  const response = page.waitForResponse(item => item.url().endsWith("/api/verify") && item.request().method() === "POST");
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  const result = await (await response).json();
  expect(result.status).toBe("UNKNOWN");
  expect(result.solver_status).toBe("CASE_LIMIT");
  expect(result.coverage_complete).toBe(false);
  await expect(page.getByTestId("verification-result").getByText("Unknown", { exact: true })).toBeVisible();
  await expect(page.getByTestId("verification-result")).toContainText("1 / 8");
  await expect(page.getByTestId("verification-worst-balance")).toHaveText("Not proven");
  await expect(page.getByText("Verified Safe", { exact: true })).not.toBeVisible();
});
