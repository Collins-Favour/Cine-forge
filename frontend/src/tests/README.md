# Frontend Test README

## Running Tests

### Unit Tests (Vitest)

```bash
# Run all unit tests
npm test

# Run with UI
npm run test:ui

# Run with coverage
npm run test:coverage

# Watch mode
npm test -- --watch
```

### E2E Tests (Playwright)

```bash
# Install Playwright browsers (first time only)
npx playwright install

# Run E2E tests
npm run test:e2e

# Run with UI mode
npm run test:e2e:ui

# Run specific browser
npx playwright test --project=chromium
```

## Test Structure

```
src/tests/
├── setup.js              # Test setup and global mocks
├── unit/                 # Unit tests
│   ├── Landing.test.jsx
│   ├── Login.test.jsx
│   ├── authStore.test.js
│   └── helpers.test.js
└── e2e/                  # End-to-end tests
    ├── landing.spec.js
    ├── auth.spec.js
    └── projects.spec.js
```

## Writing Tests

### Unit Tests Example

```javascript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

describe('Component', () => {
  it('renders correctly', () => {
    render(<Component />)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })
})
```

### E2E Tests Example

```javascript
import { test, expect } from '@playwright/test'

test('should navigate', async ({ page }) => {
  await page.goto('/')
  await page.click('text=Login')
  await expect(page).toHaveURL(/.*login/)
})
```

## Coverage Reports

After running `npm run test:coverage`, open `coverage/index.html` in your browser to view detailed coverage reports.

## CI/CD Integration

Tests can be run in CI/CD pipelines:

```yaml
- run: npm test -- --run
- run: npm run test:e2e
```
