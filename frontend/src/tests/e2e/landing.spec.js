import { test, expect } from '@playwright/test'

test.describe('Landing Page E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should load landing page successfully', async ({ page }) => {
    await expect(page).toHaveTitle(/CineForge AI/i)
    await expect(page.locator('text=CineForge AI')).toBeVisible()
  })

  test('should navigate to login page', async ({ page }) => {
    await page.click('text=Sign In')
    await expect(page).toHaveURL(/.*login/)
    await expect(page.locator('text=Welcome Back')).toBeVisible()
  })

  test('should navigate to register page', async ({ page }) => {
    await page.click('text=Get Started')
    await expect(page).toHaveURL(/.*register/)
    await expect(page.locator('text=Create Account')).toBeVisible()
  })

  test('should display feature sections', async ({ page }) => {
    await expect(page.locator('text=AI-Powered Analysis')).toBeVisible()
    await expect(page.locator('text=Visual Storyboards')).toBeVisible()
    await expect(page.locator('text=Real-time Collaboration')).toBeVisible()
  })

  test('should have smooth scroll to sections', async ({ page }) => {
    await page.click('a[href="#features"]')
    await page.waitForTimeout(500)
    const featuresSection = page.locator('#features')
    await expect(featuresSection).toBeInViewport()
  })
})
