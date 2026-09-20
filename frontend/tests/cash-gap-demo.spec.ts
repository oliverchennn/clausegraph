import { expect, test } from "@playwright/test";

/**
 * Demo regression for beat 4: the exact path a presenter walks, in order.
 * Label discipline and component behaviour are covered by cash-gap.spec.ts;
 * this guards the story surviving end to end, including a reload.
 */
test("the beat-4 story runs: failure, explanation, evidence, untouched saved plan, reload", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");

  const saved = await page.evaluate(async () => {
    const response = await fetch("/api/workspace", { headers: { Authorization: `Bearer ${localStorage.getItem("clausegraph.session")}` } });
    return response.json();
  });

  // Beat 3 hand-off: the failure the presenter arrives holding.
  const panel = page.getByTestId("verification-panel");
  await panel.getByRole("button", { name: "Payday through Sep 28" }).click();
  const verified = page.waitForResponse(r => r.url().endsWith("/api/verify") && r.request().method() === "POST");
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  const unsafe = await (await verified).json();
  expect(unsafe.status).toBe("UNSAFE");
  expect(unsafe.counterexample.earliest_failing_date).toBe("2026-09-26");
  expect(unsafe.counterexample.balance_cents).toBe(-40000);

  // Step 1-2: the question and the proof-qualified answer.
  const diagnosed = page.waitForResponse(r => r.url().endsWith("/api/cash-gap") && r.request().method() === "POST");
  await panel.getByRole("button", { name: "Explain cash gap" }).click();
  const diagnostic = await (await diagnosed).json();
  expect(diagnostic.status).toBe("PROVEN_MINIMUM");
  expect(diagnostic.additional_opening_cash_cents).toBe(40000);
  expect(diagnostic.minimality_proven).toBe(true);
  const result = page.getByTestId("cash-gap-diagnostic");
  await expect(result.locator(".cash-gap-amount")).toContainText("$400");
  await expect(result.locator(".cash-gap-amount")).toContainText("Proven fixed-schedule buffer");

  // Step 3: the disclaimer is on screen, not only in the presenter's mouth.
  await expect(result.locator(".cash-gap-amount")).toContainText("not funding");
  expect(diagnostic.is_funding).toBe(false);

  // Step 4: same schedule, both ways round.
  await expect(result.getByLabel("Fixed schedule cash comparison")).toContainText("Unsafe");
  await expect(result.getByLabel("Fixed schedule cash comparison")).toContainText("Verified Safe");
  expect(diagnostic.funded.fixed_actions).toEqual(diagnostic.baseline.fixed_actions);

  // Step 5: evidence for the limiting date, then back out.
  expect(diagnostic.limiting_date).toBe("2026-09-26");
  await expect(result.locator(".cash-gap-limits")).toContainText("Sep 26");
  await result.getByRole("button", { name: "Open limiting evidence" }).click();
  await expect(page.getByRole("dialog").getByRole("heading", { name: "Follow the evidence" })).toBeVisible();
  await page.getByRole("button", { name: "Close dialog" }).click();

  // The saved plan survived the whole segment, and survives a reload.
  await page.reload();
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  const after = await page.evaluate(async () => {
    const response = await fetch("/api/workspace", { headers: { Authorization: `Bearer ${localStorage.getItem("clausegraph.session")}` } });
    return response.json();
  });
  expect(after.revision).toBe(saved.revision);
  expect(after.plan.id).toBe(saved.plan.id);
  expect(after.plan.actions).toEqual(saved.plan.actions);
  expect(after.scenario.opening_balance_cents).toBe(saved.scenario.opening_balance_cents);
  expect(errors).toEqual([]);
});

test("the denied-approval aside reports no amount at all", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  const panel = page.getByTestId("verification-panel");
  await panel.getByTestId("add-approval").click();
  const verified = page.waitForResponse(r => r.url().endsWith("/api/verify") && r.request().method() === "POST");
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  await (await verified).json();

  const diagnosed = page.waitForResponse(r => r.url().endsWith("/api/cash-gap") && r.request().method() === "POST");
  await panel.getByRole("button", { name: "Explain cash gap" }).click();
  const diagnostic = await (await diagnosed).json();
  // The presenter line "money does not buy an approval" must be literally true on screen.
  expect(diagnostic.status).toBe("NOT_REPAIRABLE_WITH_CASH");
  expect(diagnostic.additional_opening_cash_cents).toBeNull();
  expect(diagnostic.lower_bound_cents).toBeNull();
  const result = page.getByTestId("cash-gap-diagnostic");
  await expect(result.locator(".cash-gap-amount")).not.toContainText("$");
  await expect(result.locator(".cash-gap-blockers")).toContainText("authorization");
  await expect(result).toContainText("not authorized in at least one declared case");
});

// Preserve PR38's useful recovery regression while retaining PR34's reviewed UI.
test("a failed cash-gap request can be retried without showing an amount from the error", async ({ page }) => {
  await page.goto("/");
  const panel = page.getByTestId("verification-panel");
  await panel.getByRole("button", { name: "Payday through Sep 28" }).click();
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  const explain = panel.getByRole("button", { name: "Explain cash gap" });
  await expect(explain).toBeVisible();
  let recovered = false;
  await page.route("**/api/cash-gap", async route => {
    if (recovered) return route.continue();
    await route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ detail: "Diagnostic unavailable." }) });
  });
  await explain.click();
  await expect(panel.getByRole("alert")).toContainText("Diagnostic unavailable");
  await expect(page.getByTestId("cash-gap-diagnostic")).toHaveCount(0);
  recovered = true;
  await explain.click();
  await expect(page.getByTestId("cash-gap-diagnostic").locator(".cash-gap-amount")).toContainText("$400");
  await expect(panel.getByRole("alert")).toHaveCount(0);
});
