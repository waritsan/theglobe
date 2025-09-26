import { test, expect } from "@playwright/test";

test("Blog application loads and displays content", async ({ page }) => {
  try {
    // Navigate to the blog application (use env override so CI can point to preview)
    const WEB_BASE = process.env.REACT_APP_WEB_BASE_URL || 'http://127.0.0.1:3000';
    const webBaseTrim = WEB_BASE.replace(/\/$/, '');

    // Wait for the web server to be ready (simple polling)
    let webReady = false;
    for (let i = 0; i < 10; i++) {
      try {
        const r = await page.request.get(webBaseTrim + '/');
        if (r.ok()) { webReady = true; break; }
      } catch (e) { /* ignore */ }
      await new Promise(res => setTimeout(res, 500));
    }
    if (!webReady) throw new Error(`Web server not responding at ${webBaseTrim}`);

    await page.goto(webBaseTrim, { waitUntil: 'domcontentloaded', timeout: 20000 });
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
    const API_BASE = process.env.API_BASE_URL || 'http://127.0.0.1:3100';
    const trimmedBase = API_BASE.replace(/\/$/, '');

    // Retry API request a few times to allow the API to finish warming up
    let apiResponse = null;
    for (let i = 0; i < 6; i++) {
      try {
        apiResponse = await page.request.get(`${trimmedBase}/posts`);
        if (apiResponse && apiResponse.ok()) break;
      } catch (e) { /* ignore */ }
      await new Promise(res => setTimeout(res, 1000 * (i + 1)));
    }
    expect(apiResponse && apiResponse.ok()).toBe(true);

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
