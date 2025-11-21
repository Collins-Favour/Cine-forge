import { useEffect } from 'react'
import { useAuthStore } from '@store/authStore'
import socketService from '@services/socketService'

export function useSocket() {
  const { isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (isAuthenticated) {
      socketService.connect()
    }

    return () => {
      socketService.disconnect()
    }
  }, [isAuthenticated])

  return socketService
}
