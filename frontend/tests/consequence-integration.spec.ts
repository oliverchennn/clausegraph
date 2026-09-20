import { expect, test } from "@playwright/test";

test("a same-revision plan replacement discards the delayed action preview", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");

  let release!: () => void;
  const held = new Promise<void>(resolve => { release = resolve; });
  let captured!: () => void;
  const intercepted = new Promise<void>(resolve => { captured = resolve; });
  await page.route("**/api/plan/preview", async route => {
    const response = await route.fetch();
    captured();
    await held;
    await route.fulfill({ response });
  });

  await page.getByTestId("action-cancel-phone").getByRole("button", { name: "Compare option alone" }).click();
  await intercepted;
  await page.getByRole("button", { name: "Save as recorded plan" }).click();
  await expect(page.getByText("Scenario recalculated using your selected assumptions.")).toBeVisible();
  release();

  await expect(page.getByTestId("scenario-comparison")).toHaveCount(0);
  await expect(page.getByTestId("consequence-walkthrough-slot")).toHaveCount(0);
});

test("draft edits clear an action walkthrough and generic previews never mount it", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByTestId("minimum-balance")).toContainText("$50");
  await page.getByTestId("action-cancel-phone").getByRole("button", { name: "Compare option alone" }).click();
  await expect(page.getByTestId("consequence-walkthrough-slot")).toHaveCount(1);

  await page.getByLabel("Scenario available cash").fill("2100.00");
  await expect(page.getByTestId("consequence-walkthrough-slot")).toHaveCount(0);
  await page.getByRole("button", { name: "Preview side by side" }).click();
  await expect(page.getByTestId("scenario-comparison")).toBeVisible();
  await expect(page.getByTestId("consequence-walkthrough-slot")).toHaveCount(0);
});
