import { PlaywrightTestConfig } from "@playwright/test";
import devices from "@playwright/test";
import fs from "fs";
import { join } from "path";
import dotenv from "dotenv";

/**
 * See https://playwright.dev/docs/test-configuration.
 */
const config: PlaywrightTestConfig = {
  testDir: ".",
  /* Maximum time one test can run for. Using 2 hours per test */
  timeout: 30000,
  expect: {
    /**
     * Maximum time expect() should wait for the condition to be met.
     * For example in `await expect(locator).toHaveText();`
     */
    timeout: 60 * 60 * 1000,
  },
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: "html",
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Maximum time each action such as `click()` can take. Defaults to 0 (no limit). */
    actionTimeout: 0,
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: getBaseURL(),

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: "on-first-retry",
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
      },
    },
  ],
};

function getBaseURL() {
  // For testing, prefer localhost or a test environment over production
  if (process.env.CI) {
    // In CI, use the configured environment or default to localhost:3000
    return process.env.REACT_APP_WEB_BASE_URL || "http://localhost:3000";
  }

  // For local development/testing, default to localhost
  // Only use production URL if explicitly set via TEST_PRODUCTION=true
  if (process.env.TEST_PRODUCTION === 'true') {
    console.log("⚠️  WARNING: Running tests against PRODUCTION environment!");
    return process.env.REACT_APP_WEB_BASE_URL || "https://zealous-tree-02461c100.1.azurestaticapps.net";
  }

  // Default to localhost for local testing
  console.log("Running tests against localhost (development mode)");
  return "http://localhost:5173";
}

export default config;
