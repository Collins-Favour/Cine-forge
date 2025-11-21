import { test, expect } from '@playwright/test'

test.describe('Project Management E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login')
    await page.fill('input[placeholder="you@example.com"]', 'test@example.com')
    await page.fill('input[placeholder="••••••••"]', 'password123')
    await page.click('button:has-text("Sign In")')
    await expect(page).toHaveURL(/.*dashboard/, { timeout: 10000 })
  })

  test('should create a new project', async ({ page }) => {
    // Navigate to projects
    await page.click('text=Projects')
    await expect(page).toHaveURL(/.*projects/)

    // Click new project button
    await page.click('button:has-text("New Project")')
    
    // Fill project form
    await page.fill('input[name="title"]', 'Test Film Project')
    await page.fill('textarea[name="description"]', 'This is a test film project')
    await page.selectOption('select[name="genre"]', 'Drama')
    
    // Submit
    await page.click('button:has-text("Create Project")')
    
    // Should see project in list
    await expect(page.locator('text=Test Film Project')).toBeVisible({ timeout: 5000 })
  })

  test('should view project details', async ({ page }) => {
    await page.goto('/projects')
    
    // Click on first project
    await page.click('.project-card:first-child')
    
    // Should navigate to project details
    await expect(page).toHaveURL(/.*projects\/\d+/)
    await expect(page.locator('h1')).toBeVisible()
  })

  test('should navigate to different project sections', async ({ page }) => {
    await page.goto('/projects')
    await page.click('.project-card:first-child')
    
    // Script section
    await page.click('text=Script')
    await expect(page).toHaveURL(/.*script/)
    
    // Storyboard section
    await page.click('text=Storyboard')
    await expect(page).toHaveURL(/.*storyboard/)
    
    // C-Space section
    await page.click('text=C-Space')
    await expect(page).toHaveURL(/.*c-space/)
  })
})
