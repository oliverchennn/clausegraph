import { expect, test } from "@playwright/test";

test("the resilient story preserves the impossible original case and explicitly adopts a separate verified alternative", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  const originalToken = await page.evaluate(() => localStorage.getItem("clausegraph.session"));
  const originalHeaders = { Authorization: `Bearer ${originalToken}` };
  const original = await (await page.request.get("/api/workspace", { headers: originalHeaders })).json();

  await page.getByRole("button", { name: "Payday through Sep 28", exact: true }).click();
  const noSolution = page.waitForResponse(response => response.url().endsWith("/api/synthesis") && response.request().method() === "POST");
  await page.getByRole("button", { name: "Find verified alternative", exact: true }).click();
  const exhausted = await (await noSolution).json();
  expect(exhausted.status).toBe("NO_SOLUTION");
  expect(exhausted.search_exhausted).toBe(true);
  await expect(page.getByTestId("synthesis-result")).toContainText("No solution in this declared domain");

  await page.getByRole("button", { name: "Open resilient example", exact: true }).click();
  await expect(page.locator(".demo-strip")).toContainText("three fixture documents");
  const token = await page.evaluate(() => localStorage.getItem("clausegraph.session"));
  expect(token).not.toBe(originalToken);
  const headers = { Authorization: `Bearer ${token}` };
  await page.getByRole("button", { name: "Payday Sep 3–5", exact: true }).click();
  const nominal = await (await page.request.get("/api/workspace", { headers })).json();
  const checked = page.waitForResponse(response => response.url().endsWith("/api/verify") && response.request().method() === "POST");
  await page.getByRole("button", { name: "Verify fixed plan", exact: true }).click();
  const failure = await (await checked).json();
  expect(failure.status).toBe("UNSAFE");
  expect(failure.coverage_complete).toBe(true);
  expect(failure.worst_case.minimum_balance_cents).toBe(-5000);

  const searched = page.waitForResponse(response => response.url().endsWith("/api/synthesis") && response.request().method() === "POST");
  await page.getByRole("button", { name: "Find verified alternative", exact: true }).click();
  const found = await (await searched).json();
  expect(found.status).toBe("FOUND");
  expect(found.assumptions.uncertainties).toEqual(failure.assumptions.uncertainties);
  expect(found.verification.status).toBe("SAFE");
  expect(found.verification.coverage_complete).toBe(true);
  expect(found.verification.fixed_actions).toEqual(found.candidate.actions);
  expect(found.candidate.actions.map((action: { action_id: string; execution_date: string }) => [action.action_id, action.execution_date])).toEqual([["late-shift", "2026-09-01"]]);
  expect(found.candidate_costs.total_action_fees_cents).toBe(100);
  expect(found.verification.worst_case.minimum_balance_cents).toBe(4900);
  expect(await (await page.request.get("/api/workspace", { headers })).json()).toEqual(nominal);
  expect(await (await page.request.get("/api/history", { headers })).json()).toHaveLength(1);
  const panel = page.getByTestId("resilient-panel");
  await panel.getByRole("button", { name: "Evidence for late-shift", exact: true }).click();
  await expect(page.getByRole("dialog")).toContainText("APPROVED LATE OPTION");
  await page.keyboard.press("Escape");

  const adopted = page.waitForResponse(response => response.url().endsWith("/api/synthesis/adopt") && response.request().method() === "POST");
  await panel.getByRole("button", { name: "Adopt verified schedule", exact: true }).click();
  const saved = await (await adopted).json();
  expect(saved.plan.actions).toEqual(found.candidate.actions);
  expect(saved.plan.proposed).toEqual(found.candidate.proposed);
  expect(saved.verification.assumptions.uncertainties).toEqual(failure.assumptions.uncertainties);
  expect(saved.verification.plan_id).toBe(saved.plan.id);
  await expect(page.getByTestId("minimum-balance")).toContainText("$49");
  await expect(page.getByTestId("verification-result")).toContainText("Verified Safe");
  await page.reload();
  await expect(page.getByTestId("minimum-balance")).toContainText("$49");
  const durable = await (await page.request.get("/api/workspace", { headers })).json();
  expect(durable.plan.id).toBe(saved.plan.id);
  const history = await (await page.request.get("/api/verifications", { headers })).json();
  expect(history.some((proof: { id: string; plan_id: string; status: string }) => proof.id === saved.verification.id && proof.plan_id === saved.plan.id && proof.status === "SAFE")).toBe(true);
  expect(await (await page.request.get("/api/workspace", { headers: originalHeaders })).json()).toEqual(original);
  expect(errors).toEqual([]);
});
