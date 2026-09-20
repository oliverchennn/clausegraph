import { expect, test } from "@playwright/test";

test("cancellation follows exact evidence through one relocated debt and unchanged saved state", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  const token = await page.evaluate(() => localStorage.getItem("clausegraph.session"));
  const headers = { Authorization: `Bearer ${token}` };
  const before = await (await page.request.get("/api/workspace", { headers })).json();
  const historyBefore = await (await page.request.get("/api/history", { headers })).json();

  const preview = page.waitForResponse(response => response.url().endsWith("/api/plan/preview") && response.request().method() === "POST");
  await page.getByTestId("action-cancel-phone").getByRole("button", { name: "Compare option alone" }).click();
  const result = await (await preview).json();
  expect(result.preview_source_plan_id).toBe(before.plan.id);
  expect(result.proposed.minimum_balance_cents).toBe(-82000);
  expect(result.proposed.ending_balance_cents).toBe(8000);
  const [removed, accelerated] = result.decision_traces[0].changes;
  expect([removed.operation, removed.before.id, removed.before.amount_cents]).toEqual(["remove", "phone", 6000]);
  expect([accelerated.operation, accelerated.before.id, accelerated.after.id]).toEqual(["accelerate", "device", "device"]);
  expect(accelerated.before.obligation_id).toBe(accelerated.after.obligation_id);
  expect(accelerated.before.amount_cents).toBe(48000);
  expect(accelerated.after.amount_cents).toBe(48000);
  expect(result.proposed.daily.flatMap((day: { event_ids: string[] }) => day.event_ids).filter((id: string) => id === "device")).toHaveLength(1);
  expect(result.proposed.beyond_horizon.some((event: { id: string }) => event.id === "device")).toBe(false);

  const walkthrough = page.getByTestId("consequence-walkthrough");
  await expect(walkthrough).toContainText("02-phone-and-device.txt");
  const sourceStep = walkthrough.getByRole("button", { name: /1 · Source/ });
  await sourceStep.focus();
  await page.keyboard.press("ArrowRight");
  await expect(walkthrough.getByRole("button", { name: /2 · Reviewed rule/ })).toHaveAttribute("aria-current", "step");
  await page.keyboard.press("End");
  await expect(walkthrough.getByRole("button", { name: /5 · Cash consequence/ })).toHaveAttribute("aria-current", "step");
  await expect(walkthrough.getByTestId("cash-consequence")).toContainText("Minimum -$820 · Ending $80");
  await expect(walkthrough.getByTestId("cash-consequence")).toContainText("Before this preview: $480 Device principal on Nov 20");
  await walkthrough.getByRole("button", { name: /4 · Proposed effect/ }).click();
  await expect(walkthrough.getByTestId("effect-remove")).toContainText("$60 Phone service on Sep 11 is removed");
  await expect(walkthrough.getByTestId("effect-accelerate")).toContainText("$480 Device principal moves earlier from Nov 20 to Sep 1");

  await walkthrough.getByRole("button", { name: /1 · Source/ }).click();
  await walkthrough.getByRole("button", { name: "Open exact evidence" }).click();
  await expect(page.getByRole("dialog")).toContainText("the existing $480.00 device balance becomes due on the cancellation date");
  await page.getByRole("dialog").getByRole("button", { name: "Close dialog" }).click();
  await walkthrough.getByRole("button", { name: "View linked graph path" }).click();
  await expect(page.getByRole("tab", { name: "Dependency graph" })).toHaveAttribute("data-state", "active");
  await expect(page.getByText(/Highlighting the 3 rules behind the selected consequence/)).toBeVisible();
  await expect(page.locator(".graph-node-highlighted").first()).toBeVisible();

  expect(await (await page.request.get("/api/workspace", { headers })).json()).toEqual(before);
  expect(await (await page.request.get("/api/history", { headers })).json()).toEqual(historyBefore);
  expect(errors).toEqual([]);
});

test("a blocked claim gets reasons and evidence but no fabricated cash consequence", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  const preview = page.waitForResponse(response => response.url().endsWith("/api/plan/preview") && response.request().method() === "POST");
  await page.getByTestId("action-claim-assistance").getByRole("button", { name: "Compare option alone" }).click();
  const result = await (await preview).json();
  expect(result.decision_traces).toEqual([]);
  expect(result.excluded_actions["claim-assistance"]).toContain("approval is pending");
  const walkthrough = page.getByTestId("consequence-walkthrough");
  await expect(walkthrough.getByRole("alert")).toContainText("Transformation blocked");
  await walkthrough.getByRole("button", { name: /5 · Cash consequence/ }).click();
  await expect(walkthrough).toContainText("Cash projection withheld");
  await expect(walkthrough.getByTestId("cash-consequence")).toHaveCount(0);
  await expect(page.getByTestId("candidate-minimum")).toHaveText("-$400");
});

test("the consequence path is readable and keyboard operable at 390px", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  await page.getByTestId("action-cancel-phone").getByRole("button", { name: "Compare option alone" }).click();
  const walkthrough = page.getByTestId("consequence-walkthrough");
  await expect(walkthrough).toBeVisible();
  const source = walkthrough.getByRole("button", { name: /1 · Source/ });
  await source.focus();
  await page.keyboard.press("End");
  await expect(walkthrough.getByRole("button", { name: /5 · Cash consequence/ })).toBeFocused();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});
