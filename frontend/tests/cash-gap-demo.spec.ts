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
  await panel.getByTestId("cash-gap-run").click();
  const diagnostic = await (await diagnosed).json();
  expect(diagnostic.status).toBe("PROVEN_MINIMUM");
  expect(diagnostic.additional_opening_cash_cents).toBe(40000);
  expect(diagnostic.minimality_proven).toBe(true);
  await expect(page.getByTestId("cash-gap-amount")).toContainText("$400");
  await expect(page.getByTestId("cash-gap-amount")).toContainText("proven minimum for this fixed schedule");

  // Step 3: the disclaimer is on screen, not only in the presenter's mouth.
  await expect(page.getByTestId("cash-gap-not-funding")).toContainText("not funding");
  expect(diagnostic.is_funding).toBe(false);

  // Step 4: same schedule, both ways round.
  await expect(page.getByTestId("cash-gap-compare")).toContainText("UNSAFE");
  await expect(page.getByTestId("cash-gap-compare")).toContainText("SAFE");
  expect(diagnostic.funded.fixed_actions).toEqual(diagnostic.baseline.fixed_actions);

  // Step 5: evidence for the limiting date, then back out.
  await expect(page.getByTestId("cash-gap-limiting-date")).toHaveText("2026-09-26");
  await page.getByTestId("cash-gap-evidence").click();
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
  await panel.getByLabel("Verification approval outcomes").selectOption({ index: 1 });
  const verified = page.waitForResponse(r => r.url().endsWith("/api/verify") && r.request().method() === "POST");
  await panel.getByRole("button", { name: "Verify fixed plan" }).click();
  await (await verified).json();

  const diagnosed = page.waitForResponse(r => r.url().endsWith("/api/cash-gap") && r.request().method() === "POST");
  await panel.getByTestId("cash-gap-run").click();
  const diagnostic = await (await diagnosed).json();
  // The presenter line "money does not buy an approval" must be literally true on screen.
  expect(diagnostic.status).toBe("NOT_REPAIRABLE_WITH_CASH");
  expect(diagnostic.additional_opening_cash_cents).toBeNull();
  expect(diagnostic.lower_bound_cents).toBeNull();
  await expect(page.getByTestId("cash-gap-amount")).not.toContainText("$");
  await expect(page.getByTestId("cash-gap-blockers")).toContainText("authorization");
});
