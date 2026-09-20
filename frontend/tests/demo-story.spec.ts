import { expect, test } from "@playwright/test";

test("the complete judge story runs from source to bounded consequence", async ({ page }, testInfo) => {
  const started = Date.now();
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  await expect(page.locator(".demo-strip")).toContainText("six fixture documents");
  await expect(page.getByRole("heading", { name: "Why this plan?" })).toBeVisible();
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  await expect(page.getByTestId("ending-balance")).toContainText("$500");

  await page.getByTestId("action-shift-payment").getByRole("button", { name: /View evidence/ }).click();
  const reviewedRule = page.getByTestId("rule-rule-shift");
  await expect(reviewedRule).toContainText("APPROVED: You may move");
  await expect(reviewedRule.getByLabel("Approval for Approved payment shift")).toHaveValue("approved");
  await page.getByRole("button", { name: "Close dialog" }).click();

  const originalToken = await page.evaluate(() => localStorage.getItem("clausegraph.session"));
  const originalHeaders = { Authorization: `Bearer ${originalToken}` };
  const original = await (await page.request.get("/api/workspace", { headers: originalHeaders })).json();
  const verifier = page.getByTestId("verification-panel");
  await verifier.getByRole("button", { name: "Payday through Sep 28" }).click();
  const verificationResponse = page.waitForResponse(response => response.url().endsWith("/api/verify") && response.request().method() === "POST");
  await verifier.getByRole("button", { name: "Verify fixed plan" }).click();
  const unsafe = await (await verificationResponse).json();
  expect([unsafe.status, unsafe.checked_cases, unsafe.counterexample.balance_cents]).toEqual(["UNSAFE", 8, -40000]);
  await expect(page.getByTestId("verification-result")).toContainText("8 / 8");

  const cashResponse = page.waitForResponse(response => response.url().endsWith("/api/cash-gap") && response.request().method() === "POST");
  await verifier.getByRole("button", { name: "Explain cash gap" }).click();
  const cash = await (await cashResponse).json();
  expect([cash.status, cash.additional_opening_cash_cents, cash.is_funding]).toEqual(["PROVEN_MINIMUM", 40000, false]);
  await expect(page.getByTestId("cash-gap-diagnostic")).toContainText("Proven fixed-schedule buffer");

  const noSolutionResponse = page.waitForResponse(response => response.url().endsWith("/api/synthesis") && response.request().method() === "POST");
  await verifier.getByRole("button", { name: "Find verified alternative" }).click();
  const noSolution = await (await noSolutionResponse).json();
  expect([noSolution.status, noSolution.search_exhausted]).toEqual(["NO_SOLUTION", true]);
  expect(await (await page.request.get("/api/workspace", { headers: originalHeaders })).json()).toEqual(original);

  await page.getByRole("button", { name: "Open resilient example", exact: true }).click();
  await expect(page.locator(".demo-strip")).toContainText("three fixture documents");
  const resilient = page.getByTestId("verification-panel");
  await resilient.getByRole("button", { name: "Payday Sep 3–5" }).click();
  await resilient.getByRole("button", { name: "Verify fixed plan" }).click();
  await expect(page.getByTestId("verification-result")).toContainText("Unsafe");
  const foundResponse = page.waitForResponse(response => response.url().endsWith("/api/synthesis") && response.request().method() === "POST");
  await resilient.getByRole("button", { name: "Find verified alternative" }).click();
  const found = await (await foundResponse).json();
  expect(found.status).toBe("FOUND");
  expect([found.verification.status, found.verification.checked_cases, found.verification.coverage_complete]).toEqual(["SAFE", 3, true]);
  await expect(page.getByTestId("candidate-proof")).toContainText("Independent fixed-plan verification: SAFE");
  await resilient.getByRole("button", { name: "Adopt verified schedule" }).click();
  await expect(page.getByTestId("minimum-balance")).toContainText("$49");
  await expect(page.getByTestId("verification-result")).toContainText("Verified Safe");

  await page.getByRole("button", { name: "Open original example", exact: true }).click();
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  const previewResponse = page.waitForResponse(response => response.url().endsWith("/api/plan/preview") && response.request().method() === "POST");
  await page.getByTestId("action-cancel-phone").getByRole("button", { name: "Compare option alone" }).click();
  const preview = await (await previewResponse).json();
  expect([preview.proposed.minimum_balance_cents, preview.proposed.ending_balance_cents]).toEqual([-82000, 8000]);
  const walkthrough = page.getByTestId("consequence-walkthrough");
  const source = walkthrough.getByRole("button", { name: /1 · Source/ });
  await source.focus();
  await page.keyboard.press("End");
  await expect(walkthrough.getByRole("button", { name: /5 · Cash consequence/ })).toBeFocused();
  await expect(walkthrough.getByTestId("cash-consequence")).toContainText("Minimum -$820 · Ending $80");

  const elapsedMs = Date.now() - started;
  await testInfo.attach("automated-functional-timing.json", {
    body: Buffer.from(JSON.stringify({ elapsedMs, kind: "automated functional browser run; no narration holds" }, null, 2)),
    contentType: "application/json",
  });
  console.log(`C15 desktop automated functional run: ${(elapsedMs / 1000).toFixed(2)}s (not spoken timing)`);
  expect(errors).toEqual([]);
});

test("the 390px keyboard route recovers from a temporary diagnostic outage", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  const verifier = page.getByTestId("verification-panel");
  await verifier.getByRole("button", { name: "Payday through Sep 28" }).click();
  await verifier.getByRole("button", { name: "Verify fixed plan" }).click();
  await expect(page.getByTestId("verification-result")).toContainText("Unsafe");

  let first = true;
  await page.route("**/api/cash-gap", async route => {
    if (!first) return route.continue();
    first = false;
    await route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ detail: "Temporary demo diagnostic outage." }) });
  });
  const explain = verifier.getByRole("button", { name: "Explain cash gap" });
  await explain.focus();
  await page.keyboard.press("Enter");
  await expect(verifier.getByRole("alert")).toContainText("Temporary demo diagnostic outage");
  await explain.focus();
  await page.keyboard.press("Enter");
  await expect(page.getByTestId("cash-gap-diagnostic")).toContainText("$400");

  await page.getByTestId("action-cancel-phone").getByRole("button", { name: "Compare option alone" }).click();
  const walkthrough = page.getByTestId("consequence-walkthrough");
  const source = walkthrough.getByRole("button", { name: /1 · Source/ });
  await source.focus();
  await page.keyboard.press("ArrowRight");
  await expect(walkthrough.getByRole("button", { name: /2 · Reviewed rule/ })).toBeFocused();
  await page.keyboard.press("End");
  await expect(walkthrough.getByRole("button", { name: /5 · Cash consequence/ })).toBeFocused();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});
