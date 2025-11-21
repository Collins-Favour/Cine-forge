import { describe, it, expect } from 'vitest'
import { useAuthStore } from '@store/authStore'

describe('Auth Store', () => {
  it('initializes with correct default state', () => {
    const state = useAuthStore.getState()
    
    expect(state.user).toBeNull()
    expect(state.token).toBeNull()
    expect(state.isAuthenticated).toBe(false)
  })

  it('logs in user correctly', () => {
    const user = {
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
      role: 'filmmaker'
    }
    const token = 'test-token-123'
    
    useAuthStore.getState().login(user, token)
    
    const state = useAuthStore.getState()
    expect(state.user).toEqual(user)
    expect(state.token).toBe(token)
    expect(state.isAuthenticated).toBe(true)
  })

  it('logs out user correctly', () => {
    // Login first
    useAuthStore.getState().login({ id: 1 }, 'token')
    
    // Then logout
    useAuthStore.getState().logout()
    
    const state = useAuthStore.getState()
    expect(state.user).toBeNull()
    expect(state.token).toBeNull()
    expect(state.isAuthenticated).toBe(false)
  })

  it('updates user data correctly', () => {
    useAuthStore.getState().login({ id: 1, name: 'Old Name' }, 'token')
    
    useAuthStore.getState().updateUser({ name: 'New Name' })
    
    const state = useAuthStore.getState()
    expect(state.user.name).toBe('New Name')
    expect(state.user.id).toBe(1)
  })
})
