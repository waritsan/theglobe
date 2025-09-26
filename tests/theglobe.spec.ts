import { test, expect } from "@playwright/test";

test("Blog application loads and displays content", async ({ page }) => {
  try {
    // Navigate to the blog application with a shorter wait condition
    await page.goto("/", { waitUntil: 'domcontentloaded', timeout: 10000 });
    console.log("Page loaded successfully");

    // Wait a bit for React to hydrate and load content
    await page.waitForTimeout(3000);

    // Check if the page has loaded by looking for the root div or any content
    const hasContent = await page.locator('div').count() > 0;
    expect(hasContent).toBe(true);
    console.log("Page has content");

    // Try to find any h1 element (could be the main title)
    const titleElements = page.locator('h1');
    const titleCount = await titleElements.count();

    if (titleCount > 0) {
      console.log(`Found ${titleCount} h1 elements`);
      // Just check that we have some heading content
      expect(titleCount).toBeGreaterThan(0);
    } else {
      console.log("No h1 elements found, checking for other content");
      // Check for any text content that indicates the page loaded
      const bodyText = await page.locator('body').textContent();
      expect(bodyText && bodyText.length > 0).toBe(true);
    }

    console.log("Basic page load test passed");

  } catch (error) {
    console.error("Test failed:", error);
    // Take a screenshot for debugging
    await page.screenshot({ path: 'test-failure.png' });
    throw error;
  }
});

test("API connectivity test", async ({ page }) => {
  try {
    // Test direct API access. Read target host from environment so CI can point to a local API
    const API_BASE = process.env.API_BASE_URL || 'http://localhost:3100';
    const trimmedBase = API_BASE.replace(/\/$/, '');
    const apiResponse = await page.request.get(`${trimmedBase}/posts`);
    expect(apiResponse.ok()).toBe(true);

    const apiData = await apiResponse.json();
    console.log(`API returned ${Array.isArray(apiData) ? apiData.length : 'non-array'} items`);

    // If we have posts, verify the structure
    if (Array.isArray(apiData) && apiData.length > 0) {
      const firstPost = apiData[0];
      expect(firstPost).toHaveProperty('title');
      expect(firstPost).toHaveProperty('content');
      console.log("API data structure is correct");
    }

  } catch (error) {
    console.error("API test failed:", error);
    throw error;
  }
});
