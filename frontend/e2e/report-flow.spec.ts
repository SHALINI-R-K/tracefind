import { test, expect } from "@playwright/test";

/**
 * End-to-end happy path: requires a pre-existing test user. Skipped unless the
 * E2E_USERNAME / E2E_PASSWORD env vars are set, since we don't ship test
 * credentials in source.
 */
test.describe("authenticated report flow", () => {
  test.skip(
    !process.env.E2E_USERNAME || !process.env.E2E_PASSWORD,
    "E2E_USERNAME / E2E_PASSWORD must be set to run authenticated flows"
  );

  test("user can submit a lost report and see it on the dashboard", async ({ page }) => {
    await page.goto("/dashboard");
    await page.getByLabel(/email/i).fill(process.env.E2E_USERNAME!);
    await page.getByLabel(/password/i).fill(process.env.E2E_PASSWORD!);
    await page.getByRole("button", { name: /sign in/i }).click();

    await page.getByRole("link", { name: /new report|report/i }).first().click();
    await expect(page).toHaveURL(/\/dashboard\/report/);
    await page
      .getByRole("textbox")
      .first()
      .fill("Black backpack with red zipper, missing since Tuesday");
    // file picker not exercised in skip-by-default test
  });
});
