import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,

      login: (user, token, refreshToken = null) => {
        set({ user, token, refreshToken, isAuthenticated: true })
        localStorage.setItem('token', token)
        if (refreshToken) {
          localStorage.setItem('refresh_token', refreshToken)
        }
      },

      logout: () => {
        // Fire-and-forget logout call (don't wait/block)
        const token = get().token
        if (token) {
          try {
            const baseURL = import.meta.env.VITE_API_URL || '/api'
            fetch(`${baseURL}/auth/logout`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
              },
            }).catch(() => {}) // Silently ignore errors
          } catch (e) {
            // Ignore
          }
        }
        
        set({ user: null, token: null, refreshToken: null, isAuthenticated: false })
        localStorage.removeItem('token')
        localStorage.removeItem('refresh_token')
      },

      setToken: (token) => {
        set({ token })
        localStorage.setItem('token', token)
      },

      updateUser: (userData) => {
        set((state) => ({ user: { ...state.user, ...userData } }))
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
