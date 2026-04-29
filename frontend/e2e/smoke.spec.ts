import { test, expect } from "@playwright/test";

test("home page renders TraceFind brand and CTA", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /TraceFind/i })).toBeVisible();
  await expect(page.getByRole("link", { name: /Sign in/i })).toBeVisible();
  await expect(page.getByRole("link", { name: /Report an item/i })).toBeVisible();
});

test("dashboard requires authentication", async ({ page }) => {
  await page.goto("/dashboard");
  // The Authenticator renders a sign-in form; either email field or "Sign In" header present.
  await expect(
    page.getByRole("heading", { name: /sign in/i }).or(page.getByLabel(/email/i))
  ).toBeVisible();
});
