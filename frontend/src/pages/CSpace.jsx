import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { Send, Paperclip, Smile, Search, Users, Hash, MoreVertical, Mail, MessageSquare, ArrowLeft, Settings, FileText, File, Download } from 'lucide-react'
import { useAuthStore } from '@store/authStore'
import { cspaceApi, projectsApi } from '@services/apiServices'
import { SuccessModal, ErrorModal } from '@components/Modal'
import Modal from '@components/Modal'
import socketService from '@services/socketService'
import CSpaceInbox from '../components/CSpaceInbox'

export default function CSpace() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuthStore()
  
  console.log('CSpace rendering, project id:', id)
  
  const [selectedChannel, setSelectedChannel] = useState('general')
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState([])
  const [collaborators, setCollaborators] = useState([])
  const [selectedUser, setSelectedUser] = useState(null)
  const [showUserProfile, setShowUserProfile] = useState(false)
  const [typingUsers, setTypingUsers] = useState([])
  const [showEmojiPicker, setShowEmojiPicker] = useState(false)
  const [attachedFile, setAttachedFile] = useState(null)
  const messagesEndRef = useRef(null)
  const typingTimeoutRef = useRef(null)
  const fileInputRef = useRef(null)
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [hasError, setHasError] = useState(false)
  
  // Modal states
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [showErrorModal, setShowErrorModal] = useState(false)
  const [modalTitle, setModalTitle] = useState('')
  const [modalMessage, setModalMessage] = useState('')
  const [currentProject, setCurrentProject] = useState(null)

  useEffect(() => {
    // If no project ID, inbox view will be shown - no need to set loading or messages
    if (!id) {
      setLoading(false)
      return
    }
    fetchData()
  }, [id, selectedChannel])

  const fetchData = async () => {
    setLoading(true)
    await Promise.all([fetchMessages(), fetchCollaborators(), fetchCurrentProject()])
    setLoading(false)
  }

  const fetchCurrentProject = async () => {
    if (!id) return
    
    try {
      const response = await projectsApi.getProject(id)
      setCurrentProject(response.data)
    } catch (err) {
      console.error('Error fetching current project:', err)
    }
  }

  const fetchMessages = async () => {
    if (!id) return
    
    try {
      const response = await cspaceApi.getMessages(id, { channel: selectedChannel })
      const messagesData = response.data.messages || []
      
      // Transform backend data to frontend format
      const formattedMessages = messagesData.map(msg => {
        // msg.user is the serialized User from backend (user_id, username, first_name, last_name, profile_pic_url)
        const u = msg.user || {}
        const displayName = u.username || (u.first_name && u.last_name ? `${u.first_name} ${u.last_name}` : 'Unknown User')
        return {
          id: msg.message_id,
          user: { name: displayName, avatar: u.profile_pic_url || null, user_id: u.user_id },
          content: msg.message_content,
          timestamp: new Date(msg.sent_at),
          type: msg.message_type,
          message_type: msg.message_type,
          attached_file_url: msg.attached_file_url,
          attached_thumbnail: msg.attached_thumbnail,
          isEdited: msg.is_edited,
          reactions: msg.reactions_count || 0
        }
      })
      
      // Reverse to show oldest first
      setMessages(formattedMessages.reverse())
    } catch (err) {
      console.error('Error fetching messages:', err)
      setModalTitle('Connection Error')
      setModalMessage('Unable to load messages. Please check your connection.')
      setShowErrorModal(true)
    }
  }

  const fetchCollaborators = async () => {
    if (!id) return
    
    try {
      const response = await projectsApi.getCollaborators(id)
      const collabData = response.data.collaborators || []
      
      // Transform to user format
      const users = collabData.map(collab => {
        const u = collab.user || {}
        const displayName = u.username || (u.first_name && u.last_name ? `${u.first_name} ${u.last_name}` : 'Team Member')
        return ({
          id: u.user_id || collab.user_id,
          name: displayName,
          email: u.email || '',
          avatar: u.profile_pic_url || collab.avatar_url || null,
          status: 'online', // TODO: Implement real-time presence
          role: collab.role
        })
      })
      
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
    { id: 'production', name: 'Production', type: 'public', unread: 0 },
    { id: 'creative', name: 'Creative Discussion', type: 'public', unread: 0 },
    { id: 'budget', name: 'Budget Planning', type: 'private', unread: 0 },
  ]

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // SocketIO real-time connection
  useEffect(() => {
    if (!id) return

    // Connect to socket
    socketService.connect()

    // Join the project room
    socketService.joinProject(id)

    // Listen for new messages
    const handleNewMessage = (data) => {
      console.log('Received new message:', data)
      
      // Transform incoming socket message to UI format
      const u = data.user || {}
      const displayName = u.username || (u.first_name && u.last_name ? `${u.first_name} ${u.last_name}` : 'Unknown User')
      
      const newMsg = {
        id: data.message.message_id,
        user: { 
          name: displayName, 
          avatar: u.profile_pic_url || null, 
          user_id: u.user_id 
        },
        content: data.message.message_content,
        timestamp: new Date(data.message.sent_at),
        type: data.message.message_type,
        message_type: data.message.message_type,
        attached_file_url: data.message.attached_file_url,
        attached_thumbnail: data.message.attached_thumbnail,
        isEdited: false,
        reactions: 0
      }

      // Add message to UI (with duplicate prevention)
      setMessages(prev => {
        // Check if message already exists by ID
        const existsById = prev.some(msg => msg.id === newMsg.id)
        if (existsById) {
          console.log('Message already exists, skipping:', newMsg.id)
          return prev
        }
        
        // If message is from current user, it was already added optimistically
        // We should have updated the temp message in the REST API response
        // So if socket arrives for current user's message, check if we already have it
        if (newMsg.user.user_id === user?.user_id) {
          // Check if we already have this message content
          const alreadyHasContent = prev.some(msg => 
            msg.content === newMsg.content &&
            msg.user.user_id === newMsg.user.user_id &&
            Math.abs(new Date(msg.timestamp) - new Date(newMsg.timestamp)) < 5000 // Within 5 seconds
          )
          
          if (alreadyHasContent) {
            console.log('Message from current user already exists, skipping socket duplicate')
            return prev
          }
        }
        
        // Add new message
        console.log('Adding new message:', newMsg.id)
        return [...prev, newMsg]
      })
    }

    // Listen for typing indicators
    const handleUserTyping = (data) => {
      const typingUserName = data.username || 'Someone'
      setTypingUsers(prev => {
        if (!prev.includes(typingUserName)) {
          return [...prev, typingUserName]
        }
        return prev
      })
    }

    const handleUserStoppedTyping = (data) => {
      const typingUserName = data.username || 'Someone'
      setTypingUsers(prev => prev.filter(name => name !== typingUserName))
    }

    socketService.on('new_message', handleNewMessage)
    socketService.on('user_typing', handleUserTyping)
    socketService.on('user_stopped_typing', handleUserStoppedTyping)
    
    // Handle socket errors
    const handleSocketError = (data) => {
      console.error('Socket error:', data)
      setModalTitle('Connection Error')
      setModalMessage(data.message || 'A connection error occurred')
      setShowErrorModal(true)
    }
    socketService.on('error', handleSocketError)

    // Cleanup on unmount
    return () => {
      socketService.off('new_message', handleNewMessage)
      socketService.off('user_typing', handleUserTyping)
      socketService.off('user_stopped_typing', handleUserStoppedTyping)
      socketService.off('error', handleSocketError)
      socketService.leaveProject(id)
    }
  }, [id])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleTyping = () => {
    if (!id) return
    
    // Emit typing event
    socketService.sendTyping(id, true)

    // Clear previous timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current)
    }

    // Set new timeout to send stop typing after 2 seconds of inactivity
    typingTimeoutRef.current = setTimeout(() => {
      socketService.sendTyping(id, false)
    }, 2000)
  }

  const handleEmojiSelect = (emoji) => {
    setMessage(prev => prev + emoji)
    setShowEmojiPicker(false)
  }

  const handleFileAttach = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file size (10MB max)
    if (file.size > 10 * 1024 * 1024) {
      setModalTitle('File Too Large')
      setModalMessage('File size must be less than 10MB')
      setShowErrorModal(true)
      return
    }

    setAttachedFile(file)
  }

  const removeAttachment = () => {
    setAttachedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if ((!message.trim() && !attachedFile) || sending) return

    const messageContent = message
    const fileToSend = attachedFile
    setMessage('') // Clear input immediately
    setAttachedFile(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
    setSending(true)

    const newMessage = {
      id: `temp-${Date.now()}`,
      user: {
        name: user?.username || (user?.first_name && user?.last_name ? `${user.first_name} ${user.last_name}` : 'You'),
        avatar: user?.profile_pic_url || user?.avatar_url || null,
        user_id: user?.user_id
      },
      content: messageContent || '📎 Attachment',
      timestamp: new Date(),
      type: fileToSend ? 'file' : 'text',
      message_type: fileToSend ? 'file' : 'text',
      attached_file_url: null,
      attached_thumbnail: null,
      sending: true
    }

    // Optimistically add message to UI
    setMessages([...messages, newMessage])

    try {
      if (!id) {
        throw new Error('Please select a project to send messages')
      }

      let attachedFileUrl = null
      let attachedThumbnail = null

      // Upload file if attached
      if (fileToSend) {
        try {
          const formData = new FormData()
          formData.append('file', fileToSend)
          formData.append('project_id', id)
          
          const uploadResponse = await cspaceApi.uploadFile(formData)
          attachedFileUrl = uploadResponse.data.file_url
          attachedThumbnail = uploadResponse.data.thumbnail_url
        } catch (uploadErr) {
          console.error('File upload failed:', uploadErr)
          setModalTitle('Upload Failed')
          setModalMessage('Failed to upload file. Sending message without attachment.')
          setShowErrorModal(true)
        }
      }
      
      // Send message via REST API (backend will handle SocketIO broadcast)
      const response = await cspaceApi.sendMessage(id, {
        message_content: messageContent || '📎 Attachment',
        message_type: attachedFileUrl ? 'file' : 'text',
        channel: selectedChannel,
        attached_file_url: attachedFileUrl,
        attached_thumbnail: attachedThumbnail
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
              message_type: response.data.cspace_message.message_type,
              attached_file_url: response.data.cspace_message.attached_file_url,
              attached_thumbnail: response.data.cspace_message.attached_thumbnail,
              sending: false
            }
          : msg
      ))

      // Message sent successfully (socket will notify others)
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

  if (loading && messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  // Show instructions if no project selected
  if (!id) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-display font-bold text-dark-900 mb-2">Collaboration Space</h1>
          <p className="text-dark-600">Real-time messaging and collaboration with your team</p>
        </div>

        <div className="card p-8 text-center">
          <div className="w-20 h-20 mx-auto mb-6 bg-primary-100 rounded-full flex items-center justify-center">
            <MessageSquare className="w-10 h-10 text-primary-600" />
          </div>
          
          <h2 className="text-2xl font-semibold text-dark-900 mb-3">
            Select a Project to Collaborate
          </h2>
          
          <p className="text-dark-600 mb-8 max-w-xl mx-auto">
            Collaboration spaces are project-specific. Navigate to a project first, then access C-Space to chat with your team members.
          </p>

          <div className="bg-dark-50 rounded-lg p-6 max-w-2xl mx-auto text-left mb-8">
            <h3 className="font-semibold text-dark-900 mb-4">How to access C-Space:</h3>
            <ol className="space-y-3 text-dark-700">
              <li className="flex gap-3">
                <span className="font-semibold text-primary-600">1.</span>
                <span>Go to the <strong>Projects</strong> page</span>
              </li>
              <li className="flex gap-3">
                <span className="font-semibold text-primary-600">2.</span>
                <span>Select a project or create a new one</span>
              </li>
              <li className="flex gap-3">
                <span className="font-semibold text-primary-600">3.</span>
                <span>Inside the project, click <strong>C-Space</strong> or <strong>Collaboration</strong></span>
              </li>
              <li className="flex gap-3">
                <span className="font-semibold text-primary-600">4.</span>
                <span>Start chatting with your team members!</span>
              </li>
            </ol>
          </div>

          <div className="flex justify-center gap-4">
            <Link to="/projects" className="btn-primary inline-flex items-center gap-2">
              <Users className="w-5 h-5" />
              Go to Projects
            </Link>
            <Link to="/dashboard" className="btn-secondary inline-flex items-center gap-2">
              Back to Dashboard
            </Link>
          </div>
        </div>

        {/* Features Preview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <div className="card text-center p-6">
            <div className="w-12 h-12 mx-auto mb-4 bg-primary-100 rounded-lg flex items-center justify-center">
              <MessageSquare className="w-6 h-6 text-primary-600" />
            </div>
            <h3 className="font-semibold text-dark-900 mb-2">Real-time Chat</h3>
            <p className="text-sm text-dark-600">Instant messaging with team members</p>
          </div>

          <div className="card text-center p-6">
            <div className="w-12 h-12 mx-auto mb-4 bg-accent-purple rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-white" />
            </div>
            <h3 className="font-semibold text-dark-900 mb-2">Team Presence</h3>
            <p className="text-sm text-dark-600">See who's online and available</p>
          </div>

          <div className="card text-center p-6">
            <div className="w-12 h-12 mx-auto mb-4 bg-accent-pink rounded-lg flex items-center justify-center">
              <Hash className="w-6 h-6 text-white" />
            </div>
            <h3 className="font-semibold text-dark-900 mb-2">Channels</h3>
            <p className="text-sm text-dark-600">Organized discussions by topic</p>
          </div>
        </div>
      </div>
    )
  }

  // Show inbox view when no project is selected
  if (!id) {
    return <CSpaceInbox />
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      {/* Project Header */}
      {currentProject && (
        <div className="card mb-4 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link 
                to="/c-space"
                className="text-dark-500 hover:text-dark-700 transition-colors"
                title="Back to C-Space Inbox"
              >
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <div>
                <h1 className="font-semibold text-lg text-dark-900">{currentProject.title}</h1>
                <p className="text-sm text-dark-600">{currentProject.production_stage} • {collaborators.length} members</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Link 
                to={`/projects/${id}`}
                className="text-dark-500 hover:text-dark-700 transition-colors"
                title="Project Details"
              >
                <Settings className="w-5 h-5" />
              </Link>
            </div>
          </div>
        </div>
      )}

      <div className="flex flex-1 gap-6">
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
                <span className="text-sm">Click team members →</span>
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
              <p className="text-sm text-dark-600">{collaborators.length} team members</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button className="p-2 hover:bg-dark-100 rounded-lg transition-colors" title="Search messages">
              <Search className="w-5 h-5 text-dark-600" />
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <MessageSquare className="w-16 h-16 text-dark-300 mb-4" />
              <p className="text-dark-600 text-lg font-medium">No messages yet</p>
              <p className="text-dark-500 text-sm">Be the first to start the conversation!</p>
            </div>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className={`flex gap-3 ${msg.sending ? 'opacity-50' : ''}`}>
                <div className="w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center text-white font-semibold shrink-0">
                  {msg.user.name.charAt(0)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-baseline gap-2 mb-1">
                    <span className="font-semibold text-dark-900">{msg.user.name}</span>
                    <span className="text-xs text-dark-500">{formatTime(msg.timestamp)}</span>
                    {msg.isEdited && <span className="text-xs text-dark-400">(edited)</span>}
                    {msg.sending && <span className="text-xs text-dark-400">(sending...)</span>}
                  </div>
                  <p className="text-dark-700 break-words">{msg.content}</p>
                  
                  {/* Display attachment if present */}
                  {msg.attached_file_url && (
                    <div className="mt-2">
                      {msg.message_type === 'file' && (msg.attached_file_url.match(/\.(jpg|jpeg|png|gif|webp)$/i) || msg.attached_file_url.startsWith('data:image/')) ? (
                        <img 
                          src={msg.attached_file_url.startsWith('/') ? `http://localhost:5000${msg.attached_file_url}` : msg.attached_file_url} 
                          alt="Attachment" 
                          className="max-w-sm rounded-lg border border-dark-200 cursor-pointer hover:opacity-90"
                          onClick={() => window.open(msg.attached_file_url.startsWith('/') ? `http://localhost:5000${msg.attached_file_url}` : msg.attached_file_url, '_blank')}
                        />
                      ) : (
                        <a 
                          href={msg.attached_file_url.startsWith('/') ? `http://localhost:5000${msg.attached_file_url}` : msg.attached_file_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          download
                          className="inline-flex items-center gap-2 px-3 py-2 bg-dark-50 rounded-lg border border-dark-200 hover:bg-dark-100 transition-colors"
                        >
                          {msg.attached_file_url.match(/\.(pdf|doc|docx|txt)$/i) ? (
                            <FileText className="w-4 h-4 text-primary-600" />
                          ) : (
                            <File className="w-4 h-4 text-primary-600" />
                          )}
                          <span className="text-sm text-dark-700">
                            {msg.attached_file_url.split('/').pop() || 'View Attachment'}
                          </span>
                          <Download className="w-4 h-4 text-dark-500" />
                        </a>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          {typingUsers.length > 0 && (
            <div className="flex gap-3 opacity-60">
              <div className="w-10 h-10 rounded-full bg-dark-300 flex items-center justify-center text-white font-semibold shrink-0">
                •••
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-dark-600 italic text-sm">
                  {typingUsers.length === 1 
                    ? `${typingUsers[0]} is typing...`
                    : `${typingUsers.slice(0, 2).join(', ')}${typingUsers.length > 2 ? ` and ${typingUsers.length - 2} others` : ''} are typing...`
                  }
                </p>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 border-t border-dark-200">
          {/* Attached file preview */}
          {attachedFile && (
            <div className="mb-3 flex items-center gap-2 p-2 bg-dark-50 rounded-lg border border-dark-200">
              <Paperclip className="w-4 h-4 text-dark-600" />
              <span className="text-sm text-dark-700 flex-1 truncate">{attachedFile.name}</span>
              <span className="text-xs text-dark-500">{(attachedFile.size / 1024).toFixed(1)} KB</span>
              <button
                type="button"
                onClick={removeAttachment}
                className="text-red-500 hover:text-red-700 text-sm font-medium"
              >
                Remove
              </button>
            </div>
          )}

          <form onSubmit={handleSendMessage} className="flex items-end gap-2">
            {/* Hidden file input */}
            <input
              ref={fileInputRef}
              type="file"
              onChange={handleFileChange}
              className="hidden"
              accept="image/*,.pdf,.doc,.docx,.txt,.mp4,.mov,.avi,.mp3,.wav"
            />
            <div className="flex-1">
              <div className="relative">
                <textarea
                  value={message}
                  onChange={(e) => {
                    setMessage(e.target.value)
                    handleTyping()
                  }}
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
                  disabled={sending}
                />
                <div className="absolute right-2 bottom-2 flex items-center gap-1">
                  <button 
                    type="button" 
                    onClick={handleFileAttach}
                    className="p-1.5 hover:bg-dark-100 rounded transition-colors" 
                    title="Attach file"
                  >
                    <Paperclip className="w-5 h-5 text-dark-500" />
                  </button>
                  <div className="relative">
                    <button 
                      type="button" 
                      onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                      className="p-1.5 hover:bg-dark-100 rounded transition-colors" 
                      title="Add emoji"
                    >
                      <Smile className="w-5 h-5 text-dark-500" />
                    </button>
                    
                    {/* Simple emoji picker */}
                    {showEmojiPicker && (
                      <div className="absolute bottom-full right-0 mb-2 bg-white rounded-lg shadow-lg border border-dark-200 p-3 grid grid-cols-8 gap-1 z-10">
                        {['😀', '😂', '😍', '🤔', '👍', '👎', '🎬', '🎥', '📽️', '🎞️', '✅', '❌', '⭐', '💡', '🔥', '💪', '🙌', '👏', '🎉', '🎊', '💯', '✨', '🚀', '💬', '📝', '📌', '🎯', '💼', '📊', '📈', '⚡', '🔔'].map((emoji) => (
                          <button
                            key={emoji}
                            type="button"
                            onClick={() => handleEmojiSelect(emoji)}
                            className="text-2xl hover:bg-dark-100 rounded p-1 transition-colors"
                          >
                            {emoji}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
            <button
              type="submit"
              disabled={(!message.trim() && !attachedFile) || sending}
              className="btn-primary px-4 py-2.5 disabled:opacity-50 disabled:cursor-not-allowed"
              title="Send message"
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
            {collaborators.length === 0 ? (
              <div className="text-center p-4 text-dark-500 text-sm">
                Loading team members...
              </div>
            ) : (
              collaborators.map((member) => (
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
              ))
            )}
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
                <div className="text-sm text-dark-600 mb-1">Role in Project</div>
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
    </div>
  )
}
