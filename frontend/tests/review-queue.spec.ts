import { expect, test } from "@playwright/test";
import type { ReviewQueue, Workspace } from "../src/lib/types";

test("review guidance opens a source, preserves failed reviews and refreshes after a valid review", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  const token = await page.evaluate(() => localStorage.getItem("clausegraph.session"));
  const pending = await page.request.patch("/api/rules/rule-rent", { headers: { Authorization: `Bearer ${token}` }, data: { review_status: "pending" } });
  expect(pending.ok()).toBe(true);
  const pendingQueueResponse = page.waitForResponse(response => response.url().endsWith("/api/review-queue") && response.ok());
  await page.reload();
  const pendingQueue = await (await pendingQueueResponse).json() as ReviewQueue;
  expect(pendingQueue.items[0].priority).toBe(0);
  expect(pendingQueue.items[0].rule_ids).toContain("rule-rent");
  const queue = page.getByTestId("review-queue");
  await expect(queue.getByRole("article").first().getByRole("heading")).toHaveText(pendingQueue.items[0].title);
  await queue.getByRole("button", { name: `Review evidence for ${pendingQueue.items[0].title}`, exact: true }).click();
  const rule = page.getByTestId("rule-rule-rent");
  await expect(rule.getByRole("blockquote")).toContainText("$1,600");
  const evidenceReview = rule.getByRole("combobox", { name: "Evidence review", exact: true });
  await evidenceReview.selectOption("reviewed");
  await rule.getByRole("checkbox", { name: "I checked this rule against the original source." }).check();
  await rule.getByRole("button", { name: "Save review & recalculate" }).click();
  await expect(rule.getByRole("alert")).toContainText("Evidence confirmation requires a note");
  await expect(evidenceReview).toHaveValue("reviewed");
  const failedWorkspace = await (await page.request.get("/api/workspace", { headers: { Authorization: `Bearer ${token}` } })).json() as Workspace;
  expect(failedWorkspace.rules.find(item => item.id === "rule-rent")?.review_status).toBe("pending");
  await rule.getByRole("textbox", { name: "Review note", exact: true }).fill("Checked the synthetic lease quote and the original amount and date.");
  await rule.getByRole("button", { name: "Save review & recalculate" }).click();
  await expect(rule.getByRole("button", { name: "Review saved" })).toBeVisible();
  await page.getByRole("button", { name: "Close dialog" }).click();
  await expect(queue.getByRole("heading", { name: pendingQueue.items[0].title })).toHaveCount(0);
  await expect(queue).toContainText(/assistance/i);
  await expect(queue).toContainText("approval");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  await expect(page.getByTestId("action-claim-assistance")).toContainText("Not in plan");
  expect(errors).toEqual([]);
});

test("an older real queue response cannot replace review guidance for a newer revision", async ({ page }) => {
  let releaseOld: () => void = () => {};
  let oldReady: () => void = () => {};
  let oldFinished: () => void = () => {};
  const delivered = new Promise<void>(resolve => { oldFinished = resolve; });
  const delayed = new Promise<void>(resolve => { releaseOld = resolve; });
  const captured = new Promise<void>(resolve => { oldReady = resolve; });
  let first = true;
  await page.route("**/api/review-queue", async route => {
    if (!first) { await route.continue(); return; }
    first = false;
    const response = await route.fetch();
    oldReady();
    await delayed;
    // This is an actual server response, delayed to reproduce an in-flight race.
    await route.fulfill({ response }).catch(() => {});
    oldFinished();
  });
  try {
    await page.goto("/");
    await captured;
    await page.getByTestId("action-shift-payment").getByRole("button", { name: "View evidence for Move the $450 installment", exact: true }).click();
    const rule = page.getByTestId("rule-rule-shift");
    await rule.getByLabel("Approval for Approved payment shift").selectOption("denied");
    const nextQueueResponse = page.waitForResponse(response => response.url().endsWith("/api/review-queue") && response.ok());
    await rule.getByRole("button", { name: "Save review & recalculate" }).click();
    await expect(rule.getByRole("button", { name: "Review saved" })).toBeVisible();
    const nextQueue = await (await nextQueueResponse).json() as ReviewQueue;
    await page.getByRole("button", { name: "Close dialog" }).click();
    releaseOld();
    await delivered;
    await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve()))));
    const queue = page.getByTestId("review-queue");
    await expect(queue).toHaveAttribute("data-revision", String(nextQueue.revision));
    const more = queue.locator("summary");
    if (await more.count()) await more.click();
    await expect(queue).toContainText("Blocked by recorded facts");
    await expect(page.getByTestId("minimum-balance")).toContainText("-$400");
  } finally { releaseOld(); }
});

test("queue loading failures are retryable and mobile review is keyboard accessible", async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 390, height: 844 });
  let failQueue = true;
  await page.route("**/api/review-queue", async route => {
    if (failQueue) {
      await route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ detail: "Synthetic queue outage" }) });
      return;
    }
    await route.continue();
  });
  await page.goto("/");
  const queue = page.getByTestId("review-queue");
  await expect(queue.getByRole("alert")).toContainText("Review tasks could not be loaded");
  failQueue = false;
  await queue.getByRole("button", { name: "Try again" }).click();
  await expect(queue.getByRole("button", { name: /^Review evidence for/ }).first()).toBeVisible();
  const review = queue.getByRole("button", { name: /^Review evidence for/ }).first();
  await review.focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("dialog").getByRole("heading", { name: "Follow the evidence" })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(review).toBeFocused();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await queue.screenshot({ path: testInfo.outputPath("review-queue-mobile.png") });
  await page.getByRole("button", { name: "Start my own plan" }).click();
  await expect(queue).toContainText("No listed review tasks remain");
  await expect(queue).toContainText("does not mean the plan is financially safe");
});

test("missing obligation fields remain editable and unsupported corrections are rejected", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  // Shape one existing workspace response to exercise a null-fact editor state.
  // Saving still reaches the actual backend source validator; this is not an extraction test.
  await page.route("**/api/workspace", async route => {
    const response = await route.fetch();
    const workspace = await response.json() as Workspace;
    const rent = workspace.rules.find(rule => rule.id === "rule-rent")!;
    rent.amount_cents = null; rent.due_date = null;
    await route.fulfill({ response, json: workspace });
  }, { times: 1 });
  await page.reload();
  await page.getByRole("tab", { name: "Documents & facts" }).click();
  await page.getByRole("button", { name: "Review Protect housing", exact: true }).click();
  const rule = page.getByTestId("rule-rule-rent");
  await expect(rule.getByLabel("Amount (USD)", { exact: false })).toHaveValue("");
  await expect(rule.getByLabel("Due date", { exact: false })).toHaveValue("");
  await rule.getByLabel("Amount (USD)", { exact: false }).fill("999.00");
  await rule.getByLabel("Due date", { exact: false }).fill("2026-09-08");
  await rule.getByRole("button", { name: "Save review & recalculate" }).click();
  await expect(rule.getByRole("alert")).toContainText("Unsupported or disputed evidence");
  await rule.getByLabel("Amount (USD)", { exact: false }).fill("1600.00");
  await rule.getByRole("button", { name: "Save review & recalculate" }).click();
  await expect(rule.getByRole("button", { name: "Review saved" })).toBeVisible();
});

test("deleted supporting evidence remains visible as a blocker and remaining items expand by keyboard", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  const token = await page.evaluate(() => localStorage.getItem("clausegraph.session"));
  const deleted = await page.request.delete("/api/documents/doc-1", { headers: { Authorization: `Bearer ${token}` } });
  expect(deleted.ok()).toBe(true);
  await page.reload();
  const queue = page.getByTestId("review-queue");
  await expect(queue.getByRole("article").first()).toContainText("Supporting source evidence is missing or unavailable");
  await queue.getByRole("button", { name: "Add supporting document" }).first().click();
  await expect(page.getByRole("dialog").getByRole("heading", { name: "Add your documents" })).toBeVisible();
  await expect(page.getByRole("dialog").getByRole("checkbox", { name: "I consent to external document processing." })).not.toBeChecked();
  await page.getByRole("button", { name: "Close dialog" }).click();
  const more = queue.locator("summary");
  await expect(more).toBeVisible();
  await more.focus();
  await page.keyboard.press("Enter");
  await expect(queue.getByRole("button", { name: /Review evidence for .*assistance/i }).first()).toBeVisible();
});

test("switching sessions discards a delayed queue even when revisions match", async ({ page }) => {
  let releaseOld: () => void = () => {};
  let oldReady: () => void = () => {};
  let oldFinished: () => void = () => {};
  const delivered = new Promise<void>(resolve => { oldFinished = resolve; });
  const delayed = new Promise<void>(resolve => { releaseOld = resolve; });
  const captured = new Promise<void>(resolve => { oldReady = resolve; });
  let first = true;
  await page.route("**/api/review-queue", async route => {
    if (!first) { await route.continue(); return; }
    first = false;
    const response = await route.fetch();
    oldReady();
    await delayed;
    await route.fulfill({ response }).catch(() => {});
    oldFinished();
  });
  try {
    await page.goto("/");
    await captured;
    const originalSession = await page.evaluate(() => localStorage.getItem("clausegraph.session"));
    await page.getByRole("button", { name: "Start my own plan" }).click();
    const queue = page.getByTestId("review-queue");
    await expect(queue).toContainText("No listed review tasks remain");
    expect(await page.evaluate(() => localStorage.getItem("clausegraph.session"))).not.toBe(originalSession);
    releaseOld();
    await delivered;
    await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve()))));
    await expect(queue.getByRole("article")).toHaveCount(0);
    await expect(queue).toContainText("No listed review tasks remain");
  } finally { releaseOld(); }
});
