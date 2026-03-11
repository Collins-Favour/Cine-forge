import io from 'socket.io-client'
import { useAuthStore } from '@store/authStore'

class SocketService {
    constructor() {
        this.socket = null
        this.connected = false
    }

    connect() {
        const token = useAuthStore.getState().token
        const user = useAuthStore.getState().user
        const socketUrl =
            import.meta.env.VITE_SOCKET_URL || 'http://localhost:5000'

        console.log('🔌 Socket connecting...', { 
            socketUrl, 
            hasToken: !!token, 
            user: user ? { user_id: user.user_id, username: user.username } : null 
        })

        this.socket = io(socketUrl, {
            auth: { token },
            transports: ['websocket', 'polling'],
        })

        this.socket.on('connect', () => {
            this.connected = true
            console.log('✅ Socket connected successfully', {
                socketId: this.socket.id,
                user: user ? { user_id: user.user_id, username: user.username } : null
            })
        })

        this.socket.on('disconnect', (reason) => {
            this.connected = false
            console.log('❌ Socket disconnected', { reason })
        })

        this.socket.on('connect_error', (error) => {
            console.error('🚫 Socket connection error:', error)
        })

        this.socket.on('error', (error) => {
            console.error('⚠️ Socket error:', error)
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
        const user = useAuthStore.getState().user
        const userId = user?.user_id

        this.emit('send_message', {
            project_id: projectId,
            user_id: userId,
            ...messageData
        })
    }

    sendTyping(projectId, isTyping) {
        // Get user_id and username from auth store
        const user = useAuthStore.getState().user
        const userId = user?.user_id
        const username = user?.username || (user?.first_name && user?.last_name ? `${user.first_name} ${user.last_name}` : 'Someone')

        if (isTyping) {
            this.emit('typing', {
                project_id: projectId,
                user_id: userId,
                username: username
            })
        } else {
            this.emit('stop_typing', {
                project_id: projectId,
                user_id: userId
            })
        }
    }
}

export default new SocketService()