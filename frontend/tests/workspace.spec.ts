import { expect, test } from "@playwright/test";

test("complete synthetic plan, evidence, approval, scenario, document and privacy workflow", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  await expect(page.getByText("Its six fixture documents and starting financial details are fictional.", { exact: false })).toBeVisible();
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  await expect(page.getByTestId("ending-balance")).toHaveText("$500");
  await expect(page.getByTestId("action-claim-assistance")).toContainText("Not in plan");
  await expect(page.getByText("Device principal", { exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Why this plan?" })).toBeVisible();
  await expect(page.getByTestId("trace-change")).toContainText("$450 Installment moves from Sep 13 to Sep 26");
  await expect(page.getByTestId("decision-trace")).toContainText("03-payment-shift-approval.txt");

  // A denied-approval what-if is previewed beside the recorded plan without persisting it.
  await page.getByLabel("Payment extension approval assumption").selectOption("denied");
  const deniedPreviewResponse = page.waitForResponse(response => response.url().endsWith("/api/plan/preview") && response.request().method() === "POST");
  await page.getByRole("button", { name: "Preview side by side" }).click();
  const deniedPreview = await (await deniedPreviewResponse).json();
  expect(deniedPreview.proposed.minimum_balance_cents).toBe(-40000);
  await expect(page.getByTestId("active-minimum")).toHaveText("$50");
  await expect(page.getByTestId("candidate-minimum")).toHaveText("-$400");
  await expect(page.getByTestId("consequence-walkthrough-slot")).toHaveCount(0);
  await page.getByRole("button", { name: "Keep recorded plan" }).click();
  await page.getByLabel("Payment extension approval assumption").selectOption("recorded");

  // Read the precise clause, then persist a real denial rather than a hypothetical assumption.
  await page.getByTestId("action-shift-payment").getByRole("button", { name: "View evidence" }).click();
  let evidence = page.getByRole("dialog");
  await expect(page.getByTestId("rule-rule-shift").getByRole("blockquote")).toContainText("APPROVED: You may move");
  const rule = page.getByTestId("rule-rule-shift");
  await rule.getByLabel("Approval for Approved payment shift").selectOption("denied");
  await rule.getByRole("button", { name: "Save review & recalculate" }).click();
  await expect(rule.getByRole("button", { name: "Review saved" })).toBeVisible();
  await evidence.getByRole("button", { name: "Close dialog" }).click();
  await expect(page.getByTestId("minimum-balance")).toContainText("-$400");
  await expect(page.getByTestId("ending-balance")).toHaveText("$500");
  await expect(page.getByText("additional cash is required; this is a diagnostic", { exact: false })).toBeVisible();

  // An assumption is distinctly conditional and survives a browser reload.
  await page.getByLabel("Payment extension approval assumption").selectOption("approved");
  await page.getByRole("button", { name: "Save as recorded plan" }).click();
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  await expect(page.getByText("This scenario relies on approval assumptions.")).toBeVisible();
  await page.reload();
  await expect(page.getByLabel("Payment extension approval assumption")).toHaveValue("approved");
  await expect(page.getByText("This scenario relies on approval assumptions.")).toBeVisible();

  // Restore written approval; all actions still remain drafts and calculations only.
  await page.getByTestId("action-shift-payment").getByRole("button", { name: "View evidence" }).click();
  evidence = page.getByRole("dialog");
  await page.getByTestId("rule-rule-shift").getByLabel("Approval for Approved payment shift").selectOption("approved");
  await page.getByTestId("rule-rule-shift").getByRole("button", { name: "Save review & recalculate" }).click();
  await expect(page.getByTestId("rule-rule-shift").getByRole("button", { name: "Review saved" })).toBeVisible();
  const original = page.waitForEvent("download");
  await page.getByTestId("rule-rule-shift").getByRole("button", { name: "Download original source" }).click();
  expect((await original).suggestedFilename()).toContain("payment-shift");
  await evidence.getByRole("button", { name: "Close dialog" }).click();
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");

  // Forcing cancellation exposes the accelerated existing device debt in the actual solver result.
  const comparisonResponse = page.waitForResponse(response => response.url().endsWith("/api/plan/preview") && response.request().method() === "POST");
  await page.getByTestId("action-cancel-phone").getByRole("button", { name: "Compare option alone" }).click();
  const comparison = await (await comparisonResponse).json();
  expect(comparison.proposed.minimum_balance_cents).toBeLessThan(0);
  expect(comparison.proposed.ending_balance_cents).toBe(8000);
  await expect(page.getByTestId("scenario-comparison")).toBeVisible();
  await expect(page.getByTestId("consequence-walkthrough-slot")).toHaveCount(1);
  await expect(page.getByTestId("candidate-minimum")).toHaveText("-$820");
  await expect(page.getByTestId("candidate-ending")).toHaveText("$80");
  await expect(page.getByTestId("active-ending")).toHaveText("$500");
  await expect(page.getByTestId("ending-balance")).toHaveText("$500");
  await page.reload();
  await expect(page.getByTestId("scenario-comparison")).not.toBeVisible();
  await expect(page.getByTestId("consequence-walkthrough-slot")).toHaveCount(0);
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");

  await page.getByTestId("action-shift-payment").getByRole("button", { name: "Draft request" }).click();
  await expect(page.getByRole("dialog").getByText("Not sent", { exact: true })).toBeVisible();
  const draft = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download draft" }).click();
  expect((await draft).suggestedFilename()).toBe("clausegraph-request.txt");
  await page.getByRole("button", { name: "Close dialog" }).click();
  const summary = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download evidence summary" }).click();
  expect((await summary).suggestedFilename()).toBe("clausegraph-evidence.md");

  await page.getByRole("tab", { name: "Dependency graph" }).click();
  await expect(page.locator(".react-flow__node").first()).toBeVisible();
  await page.locator(".react-flow__node").filter({ hasText: "Approved payment shift" }).click();
  await expect(page.getByRole("dialog").getByRole("heading", { name: "Follow the evidence" })).toBeVisible();
  await page.getByRole("button", { name: "Close dialog" }).click();

  // Native-only upload is explicit about consent and deduplicates identical bytes.
  const upload = async () => {
    await page.getByRole("button", { name: "Add documents", exact: true }).click();
    await page.getByRole("dialog").locator('input[type="file"]').setInputFiles({ name: "synthetic-browser-note.txt", mimeType: "text/plain", buffer: Buffer.from("SYNTHETIC BROWSER TEST. Review pending. No financial obligations stated.") });
    await expect(page.getByRole("checkbox", { name: "I consent to external document processing." })).not.toBeChecked();
    await expect(page.getByRole("dialog")).toContainText("NVIDIA · hosted Nemotron");
    await expect(page.getByRole("dialog")).toContainText("Evidence checks and scanned-page OCR");
    await expect(page.getByRole("dialog")).not.toContainText("NVIDIA and Google");
    await page.getByRole("dialog").getByRole("button", { name: "Upload document" }).click();
    await expect(page.getByRole("dialog")).not.toBeVisible();
  };
  await upload();
  await expect(page.getByRole("heading", { name: "synthetic-browser-note.txt", exact: true })).toBeVisible();
  await upload();
  await expect(page.getByText("This document is already in your workspace. No duplicate was created.")).toBeVisible();
  await expect(page.getByRole("heading", { name: "synthetic-browser-note.txt", exact: true })).toHaveCount(1);

  await page.getByRole("tab", { name: "Overview", exact: true }).click();
  await page.getByRole("button", { name: "Edit financial picture" }).click();
  await page.getByRole("dialog").getByLabel("Available cash (USD)").fill("2100.00");
  await page.getByRole("button", { name: "Save & recalculate" }).click();
  await expect(page.getByTestId("minimum-balance")).toContainText("$150");
  await expect(page.getByTestId("ending-balance")).toHaveText("$600");

  await page.getByRole("button", { name: "Open settings" }).click();
  await page.getByRole("dialog").getByRole("button", { name: "Delete", exact: true }).click();
  await page.getByRole("button", { name: "Delete session permanently" }).click();
  await expect(page.getByRole("heading", { name: "Your session has been deleted" })).toBeVisible();
  expect(await page.evaluate(() => localStorage.getItem("clausegraph.session"))).toBeNull();
  expect(errors).toEqual([]);
});

test("mobile workspace is readable without horizontal overflow", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.getByRole("tab", { name: "Documents & facts" }).click();
  await expect(page.getByRole("heading", { name: "Your document library" })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.getByRole("button", { name: "Add documents", exact: true }).click();
  await expect(page.getByRole("dialog")).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});
