# The Globe Blog Application Tests

The included [Playwright](https://playwright.dev/) smoke tests will verify that The Globe blog application loads correctly and can connect to the API.

## Run Tests

The endpoint it hits will be discovered in this order:

1. **Local Development (Default):** `http://127.0.0.1:5173`
2. **CI Environment:** Uses `REACT_APP_WEB_BASE_URL` environment variable
3. **Production Testing:** Set `TEST_PRODUCTION=true` to test against production

### Local Testing (Recommended)

```bash
# Start Vite dev server on port 5173 (recommended)
cd ../src/web
npm run dev -- --port 5173

# Run tests against Vite (default port 5173)
cd ../tests
npx playwright test

# Or override the web base URL if needed
# REACT_APP_WEB_BASE_URL=http://127.0.0.1:5173 npx playwright test
```

### Production Testing (Use with Caution)

```bash
# Run tests against production environment
TEST_PRODUCTION=true npx playwright test
```

⚠️ **Warning:** Running tests against production can:
- Affect real users
- Create noise in production logs
- Potentially modify production data
- Impact application performance

Only use `TEST_PRODUCTION=true` when specifically testing production deployments.

To run the tests:

1. CD to /tests
1. Run `npm i && npx playwright install`
1. Run `npx playwright test`

You can use the `--headed` flag to open a browser when running the tests.

## Debug Tests

Add the `--debug` flag to run with debugging enabled. You can find out more info here: https://playwright.dev/docs/next/test-cli#reference

```bash
npx playwright test --debug
```

More debugging references: https://playwright.dev/docs/debug and https://playwright.dev/docs/trace-viewer