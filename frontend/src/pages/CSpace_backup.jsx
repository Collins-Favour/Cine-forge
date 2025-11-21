import { useState, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import { Send, Paperclip, Smile, Search, Users, Hash, MoreVertical, Video, Phone, X, Mail, User as UserIcon } from 'lucide-react'
import { useAuthStore } from '@store/authStore'
import { cspaceApi, projectsApi } from '@services/apiServices'
import { SuccessModal, ErrorModal } from '@components/Modal'
import Modal from '@components/Modal'

export default function CSpace() {
  const { id } = useParams()
  const { user } = useAuthStore()
  const [selectedChannel, setSelectedChannel] = useState('general')
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState([])
  const [collaborators, setCollaborators] = useState([])
  const [selectedUser, setSelectedUser] = useState(null)
  const [showUserProfile, setShowUserProfile] = useState(false)
  const messagesEndRef = useRef(null)
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)
  
  // Modal states
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [showErrorModal, setShowErrorModal] = useState(false)
  const [modalTitle, setModalTitle] = useState('')
  const [modalMessage, setModalMessage] = useState('')

  useEffect(() => {
    if (id) {
      fetchData()
    }
  }, [id, selectedChannel])

  const fetchData = async () => {
    setLoading(true)
    await Promise.all([fetchMessages(), fetchCollaborators()])
    setLoading(false)
  }

  const fetchMessages = async () => {
    try {
      const response = await cspaceApi.getMessages(id, { channel: selectedChannel })
      const messagesData = response.data.messages || []
      
      // Transform backend data to frontend format
      const formattedMessages = messagesData.map(msg => ({
        id: msg.message_id,
        user: msg.user || { name: 'Unknown User', avatar: null },
        content: msg.message_content,
        timestamp: new Date(msg.sent_at),
        type: msg.message_type,
        isEdited: msg.is_edited,
        reactions: msg.reactions_count || 0
      }))
      
      setMessages(formattedMessages)
    } catch (err) {
      console.error('Error fetching messages:', err)
      setModalTitle('Connection Error')
      setModalMessage('Unable to load messages. Please check your connection.')
      setShowErrorModal(true)
    }
  }

  const fetchCollaborators = async () => {
    try {
      const response = await projectsApi.getCollaborators(id)
      const collabData = response.data.collaborators || []
      
      // Transform to user format
      const users = collabData.map(collab => ({
        id: collab.user_id,
        name: collab.name || 'Team Member',
        email: collab.email || '',
        avatar: collab.avatar_url,
        status: 'online', // TODO: Implement real-time presence
        role: collab.role
      }))
      
      setCollaborators(users)
    } catch (err) {
      console.error('Error fetching collaborators:', err)
    }
  }

  const handleUserClick = (clickedUser) => {
    setSelectedUser(clickedUser)
    setShowUserProfile(true)
  }

  const handleSendDirectMessage = (directUser) => {
    setShowUserProfile(false)
    setSelectedChannel(`dm-${directUser.id}`)
    setModalTitle('Direct Message')
    setModalMessage(`Starting conversation with ${directUser.name}`)
    setShowSuccessModal(true)
  }

  const channels = [
    { id: 'general', name: 'General', type: 'public', unread: 0 },
    { id: 'production', name: 'Production', type: 'public', unread: 3 },
    { id: 'creative', name: 'Creative Discussion', type: 'public', unread: 0 },
    { id: 'budget', name: 'Budget Planning', type: 'private', unread: 1 },
  ]

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!message.trim() || sending) return

    const messageContent = message
    setMessage('') // Clear input immediately
    setSending(true)

    const newMessage = {
      id: `temp-${Date.now()}`,
      user: { 
        name: user?.full_name || user?.first_name + ' ' + user?.last_name || user?.username || 'You', 
        avatar: user?.avatar_url 
      },
      content: messageContent,
      timestamp: new Date(),
      type: 'text',
      sending: true
    }

    // Optimistically add message to UI
    setMessages([...messages, newMessage])

    try {
      const response = await cspaceApi.sendMessage(id, {
        message_content: messageContent,
        message_type: 'text',
        channel: selectedChannel
      })

      // Update the temporary message with real data from server
      setMessages(prev => prev.map(msg => 
        msg.id === newMessage.id 
          ? {
              id: response.data.cspace_message.message_id,
              user: msg.user,
              content: msg.content,
              timestamp: new Date(response.data.cspace_message.sent_at),
              type: msg.type,
              sending: false
            }
          : msg
      ))
    } catch (err) {
      console.error('Error sending message:', err)
      
      // Remove the failed message
      setMessages(prev => prev.filter(msg => msg.id !== newMessage.id))
      
      setModalTitle('Send Failed')
      setModalMessage('Failed to send message. Please try again.')
      setShowErrorModal(true)
      
      // Restore the message text so user can retry
      setMessage(messageContent)
    } finally {
      setSending(false)
    }
  }

  const formatTime = (date) => {
    const now = new Date()
    const diff = now - date
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    return `${days}d ago`
  }

  const statusColors = {
    online: 'bg-green-500',
    away: 'bg-yellow-500',
    busy: 'bg-red-500',
    offline: 'bg-gray-400'
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-6">
      {/* Channels Sidebar */}
      <div className="w-64 shrink-0 hidden md:block">
        <div className="card h-full flex flex-col">
          <div className="p-4 border-b border-dark-200">
            <h2 className="font-semibold text-dark-900 flex items-center gap-2">
              <Hash className="w-5 h-5 text-primary-600" />
              Channels
            </h2>
          </div>

          <div className="flex-1 overflow-y-auto p-2">
            {channels.map((channel) => (
              <button
                key={channel.id}
                onClick={() => setSelectedChannel(channel.id)}
                className={`w-full text-left px-3 py-2 rounded-lg mb-1 transition-colors ${
                  selectedChannel === channel.id
                    ? 'bg-primary-100 text-primary-700'
                    : 'hover:bg-dark-100 text-dark-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium"># {channel.name}</span>
                  {channel.unread > 0 && (
                    <span className="px-2 py-0.5 bg-primary-500 text-white text-xs rounded-full">
                      {channel.unread}
                    </span>
                  )}
                </div>
              </button>
            ))}
          </div>

          <div className="p-4 border-t border-dark-200">
            <div className="text-sm text-dark-600 mb-2">Direct Messages</div>
            <button className="w-full text-left px-3 py-2 rounded-lg hover:bg-dark-100 text-dark-700 transition-colors">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm">Sarah Producer</span>
              </div>
            </button>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 card flex flex-col min-w-0">
        <div className="p-4 border-b border-dark-200 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Hash className="w-6 h-6 text-dark-600" />
            <div>
              <h2 className="font-semibold text-dark-900 capitalize">{selectedChannel}</h2>
              <p className="text-sm text-dark-600">{onlineUsers.length} members online</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button className="p-2 hover:bg-dark-100 rounded-lg transition-colors">
              <Phone className="w-5 h-5 text-dark-600" />
            </button>
            <button className="p-2 hover:bg-dark-100 rounded-lg transition-colors">
              <Video className="w-5 h-5 text-dark-600" />
            </button>
            <button className="p-2 hover:bg-dark-100 rounded-lg transition-colors">
              <Search className="w-5 h-5 text-dark-600" />
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => (
            <div key={msg.id} className="flex gap-3">
              <div className="w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center text-white font-semibold shrink-0">
                {msg.user.name.charAt(0)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-baseline gap-2 mb-1">
                  <span className="font-semibold text-dark-900">{msg.user.name}</span>
                  <span className="text-xs text-dark-500">{formatTime(msg.timestamp)}</span>
                </div>
                <p className="text-dark-700 break-words">{msg.content}</p>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 border-t border-dark-200">
          <form onSubmit={handleSendMessage} className="flex items-end gap-2">
            <div className="flex-1">
              <div className="relative">
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      handleSendMessage(e)
                    }
                  }}
                  placeholder={`Message #${selectedChannel}`}
                  className="input w-full pr-20 resize-none"
                  rows="1"
                  style={{ minHeight: '44px', maxHeight: '120px' }}
                />
                <div className="absolute right-2 bottom-2 flex items-center gap-1">
                  <button type="button" className="p-1.5 hover:bg-dark-100 rounded transition-colors">
                    <Paperclip className="w-5 h-5 text-dark-500" />
                  </button>
                  <button type="button" className="p-1.5 hover:bg-dark-100 rounded transition-colors">
                    <Smile className="w-5 h-5 text-dark-500" />
                  </button>
                </div>
              </div>
            </div>
            <button
              type="submit"
              disabled={!message.trim()}
              className="btn-primary px-4 py-2.5 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
        </div>
      </div>

      {/* Members Sidebar */}
      <div className="w-64 shrink-0 hidden lg:block">
        <div className="card h-full flex flex-col">
          <div className="p-4 border-b border-dark-200">
            <h2 className="font-semibold text-dark-900 flex items-center gap-2">
              <Users className="w-5 h-5 text-primary-600" />
              Team ({collaborators.length})
            </h2>
          </div>

          <div className="flex-1 overflow-y-auto p-2">
            {collaborators.map((member) => (
              <div
                key={member.id}
                onClick={() => handleUserClick(member)}
                className="flex items-center gap-3 p-3 rounded-lg hover:bg-primary-50 hover:border-primary-200 transition-colors cursor-pointer border border-transparent"
              >
                <div className="relative">
                  <div className="w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center text-white font-semibold">
                    {member.name.charAt(0)}
                  </div>
                  <div className={`absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 ${statusColors[member.status]} rounded-full border-2 border-white`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-dark-900 truncate">{member.name}</div>
                  <div className="text-xs text-dark-500 truncate capitalize">{member.role}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* User Profile Modal */}
      {selectedUser && (
        <Modal 
          isOpen={showUserProfile} 
          onClose={() => setShowUserProfile(false)} 
          title="Team Member Profile"
          size="md"
        >
          <div className="p-6">
            <div className="flex items-start gap-4 mb-6">
              <div className="relative">
                <div className="w-20 h-20 rounded-full bg-primary-500 flex items-center justify-center text-white text-2xl font-semibold">
                  {selectedUser.name.charAt(0)}
                </div>
                <div className={`absolute -bottom-1 -right-1 w-5 h-5 ${statusColors[selectedUser.status]} rounded-full border-3 border-white`} />
              </div>
              <div className="flex-1">
                <h3 className="text-xl font-semibold text-dark-900 mb-1">{selectedUser.name}</h3>
                <p className="text-primary-600 text-sm font-medium capitalize mb-2">{selectedUser.role}</p>
                {selectedUser.email && (
                  <p className="text-dark-600 text-sm flex items-center gap-2">
                    <Mail className="w-4 h-4" />
                    {selectedUser.email}
                  </p>
                )}
              </div>
            </div>

            <div className="space-y-3">
              <div className="p-3 bg-dark-50 rounded-lg">
                <div className="text-sm text-dark-600 mb-1">Status</div>
                <div className="flex items-center gap-2">
                  <div className={`w-2.5 h-2.5 ${statusColors[selectedUser.status]} rounded-full`} />
                  <span className="text-dark-900 font-medium capitalize">{selectedUser.status}</span>
                </div>
              </div>

              <div className="p-3 bg-dark-50 rounded-lg">
                <div className="text-sm text-dark-600 mb-1">Role</div>
                <div className="text-dark-900 font-medium capitalize">{selectedUser.role}</div>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => handleSendDirectMessage(selectedUser)}
                className="btn-primary flex-1 flex items-center justify-center gap-2"
              >
                <Send className="w-4 h-4" />
                Send Message
              </button>
              <button
                onClick={() => setShowUserProfile(false)}
                className="btn-secondary flex items-center justify-center gap-2 px-6"
              >
                Close
              </button>
            </div>
          </div>
        </Modal>
      )}

      {/* Modals */}
      <SuccessModal
        isOpen={showSuccessModal}
        onClose={() => setShowSuccessModal(false)}
        title={modalTitle}
        message={modalMessage}
      />

      <ErrorModal
        isOpen={showErrorModal}
        onClose={() => setShowErrorModal(false)}
        title={modalTitle}
        message={modalMessage}
      />
    </div>
  )
}
