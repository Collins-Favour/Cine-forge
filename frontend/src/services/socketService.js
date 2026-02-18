import io from 'socket.io-client'
import { useAuthStore } from '@store/authStore'

class SocketService {
    constructor() {
        this.socket = null
        this.connected = false
    }

    connect() {
        const token = useAuthStore.getState().token
        const socketUrl =
            import.meta.env.VITE_SOCKET_URL || 'http://localhost:5000'

        this.socket = io(socketUrl, {
            auth: { token },
            transports: ['websocket', 'polling'],
        })

        this.socket.on('connect', () => {
            this.connected = true
            console.log('Socket connected')
        })

        this.socket.on('disconnect', () => {
            this.connected = false
            console.log('Socket disconnected')
        })

        this.socket.on('error', (error) => {
            console.error('Socket error:', error)
        })

        return this.socket
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect()
            this.socket = null
            this.connected = false
        }
    }

    emit(event, data) {
        if (this.socket && this.connected) {
            this.socket.emit(event, data)
        }
    }

    on(event, callback) {
        if (this.socket) {
            this.socket.on(event, callback)
        }
    }

    off(event, callback) {
        if (this.socket) {
            this.socket.off(event, callback)
        }
    }

    // Project-specific methods
    joinProject(projectId) {
        this.emit('join_project', { project_id: projectId })
    }

    leaveProject(projectId) {
        this.emit('leave_project', { project_id: projectId })
    }

    sendMessage(projectId, messageData) {
        // Get user_id from auth store
        const userId = useAuthStore.getState().user?.user_id

        this.emit('send_message', {
            project_id: projectId,
            user_id: userId,
            ...messageData
        })
    }

    sendTyping(projectId, isTyping) {
        // Get user_id from auth store
        const userId = useAuthStore.getState().user?.user_id

        this.emit('typing', {
            project_id: projectId,
            user_id: userId,
            is_typing: isTyping
        })
    }
}

export default new SocketService()