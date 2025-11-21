import { test, expect } from '@playwright/test'

test.describe('Authentication Flow E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should complete full registration flow', async ({ page }) => {
    // Navigate to register
    await page.click('text=Get Started')
    await expect(page).toHaveURL(/.*register/)

    // Fill registration form
    await page.fill('input[placeholder="John Doe"]', 'Test User')
    await page.fill('input[placeholder="you@example.com"]', 'testuser@example.com')
    await page.fill('input[placeholder="johndoe"]', 'testuser')
    await page.fill('input[placeholder="••••••••"]', 'password123')
    
    // Submit form
    await page.click('button:has-text("Create Account")')
    
    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*dashboard/, { timeout: 10000 })
  })

  test('should complete full login flow', async ({ page }) => {
    // Navigate to login
    await page.click('text=Sign In')
    await expect(page).toHaveURL(/.*login/)

    // Fill login form
    await page.fill('input[placeholder="you@example.com"]', 'test@example.com')
    await page.fill('input[placeholder="••••••••"]', 'password123')
    
    // Submit form
    await page.click('button:has-text("Sign In")')
    
    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*dashboard/, { timeout: 10000 })
  })

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login')
    
    await page.fill('input[placeholder="you@example.com"]', 'wrong@example.com')
    await page.fill('input[placeholder="••••••••"]', 'wrongpassword')
    
    await page.click('button:has-text("Sign In")')
    
    // Should show error toast
    await expect(page.locator('text=/Invalid credentials|error/i')).toBeVisible({ timeout: 5000 })
  })

  test('should toggle password visibility', async ({ page }) => {
    await page.goto('/login')
    
    const passwordInput = page.locator('input[placeholder="••••••••"]')
    const toggleButton = page.locator('button').filter({ has: page.locator('svg') }).last()
    
    // Initially password type
    await expect(passwordInput).toHaveAttribute('type', 'password')
    
    // Click toggle
    await toggleButton.click()
    await expect(passwordInput).toHaveAttribute('type', 'text')
    
    // Click again
    await toggleButton.click()
    await expect(passwordInput).toHaveAttribute('type', 'password')
  })
})
