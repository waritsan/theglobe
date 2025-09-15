import { test, expect } from "@playwright/test";
import { v4 as uuidv4 } from "uuid";

test("Create and delete item test", async ({ page }) => {
  await page.goto("/", { waitUntil: 'networkidle' });

  await expect(page.locator("text=My List").first()).toBeVisible({ timeout: 10000 });

  await expect(page.locator("text=This list is empty.").first()).toBeVisible({ timeout: 10000 });

  const guid = uuidv4();
  console.log(`Creating item with text: ${guid}`);

  await page.locator('[placeholder="Add an item"]').focus();
  await page.locator('[placeholder="Add an item"]').fill(guid);
  await page.locator('[placeholder="Add an item"]').press("Enter");

  console.log(`Deleting item with text: ${guid}`);
  await expect(page.locator(`text=${guid}`).first()).toBeVisible({ timeout: 10000 });

  // Click the item to select it
  await page.locator(`text=${guid}`).first().click();

  // Wait for and click the delete button (assuming it's always in a menu now)
  await page.waitForSelector('button[role="menuitem"]:has-text("Delete")', { timeout: 5000 });
  await page.locator('button[role="menuitem"]:has-text("Delete")').click();

  await expect(page.locator(`text=${guid}`).first()).toBeHidden({ timeout: 10000 });

  // Additional assertion: Verify the list is empty again
  await expect(page.locator("text=This list is empty.").first()).toBeVisible({ timeout: 10000 });
});
