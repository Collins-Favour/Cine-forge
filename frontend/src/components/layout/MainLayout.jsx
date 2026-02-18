import { Outlet, Link, useLocation } from 'react-router-dom'
import { 
  Film, 
  LayoutDashboard, 
  FolderOpen, 
  MessageSquare, 
  Settings, 
  LogOut,
  Menu,
  X,
  Bell,
  Users,
  Activity
} from 'lucide-react'
import { useState } from 'react'
import { useQuery } from 'react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuthStore } from '@store/authStore'
import api from '@services/api'

export default function MainLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [notificationsOpen, setNotificationsOpen] = useState(false)
  const location = useLocation()
  const { user, logout } = useAuthStore()

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    ...(user?.role === 'admin' 
      ? [
          { name: 'User Management', href: '/admin/users', icon: Users },
          { name: 'Project Management', href: '/admin/projects', icon: FolderOpen }
        ]
      : [{ name: 'Projects', href: '/projects', icon: FolderOpen }]
    ),
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

  const isActive = (path) => location.pathname === path

  // Fetch notifications
  const { data: notificationsData } = useQuery(
    'notifications',
    async () => {
      const response = await api.get('/collaboration/notifications?unread_only=true')
      return response.data
    },
    {
      enabled: !!user?.user_id,
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  )

  const notifications = notificationsData?.notifications || []
  const unreadCount = notifications.length

  const handleNotificationClick = async (notification) => {
    // Mark as read
    try {
      await api.post(`/collaboration/notifications/${notification.notification_id}/read`)
      
      // Only redirect if it's not a collaboration invite (those have action buttons)
      if (notification.notification_type !== 'collaboration_invite') {
        window.location.href = notification.link_url || '/dashboard'
      }
    } catch (error) {
      console.error('Error marking notification as read:', error)
    }
  }

  const handleInvitationResponse = async (notification, response) => {
    try {
      const actionData = JSON.parse(notification.action_data || '{}')
      const { collaboration_id, project_id } = actionData
      
      await api.post(`/projects/${project_id}/collaborators/${collaboration_id}/respond`, {
        response: response
      })
      
      // Mark notification as read
      await api.post(`/collaboration/notifications/${notification.notification_id}/read`)
      
      // Refresh notifications
      window.location.reload()
    } catch (error) {
      console.error('Error responding to invitation:', error)
      alert(error.response?.data?.error || 'Failed to respond to invitation')
    }
  }

  return (
    <div className="min-h-screen bg-dark-50">
      {/* Mobile Sidebar Backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-dark-100 border-r border-dark-200 transform transition-transform duration-300 lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-6 border-b border-dark-200">
            <Link to="/" className="flex items-center gap-2">
              <Film className="w-8 h-8 text-primary-500" />
              <span className="text-xl font-display font-bold gradient-text">CineForge AI</span>
            </Link>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-dark-600 hover:text-dark-900"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                    isActive(item.href)
                      ? 'bg-primary-500 text-white'
                      : 'text-dark-700 hover:bg-dark-200'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{item.name}</span>
                </Link>
              )
            })}
          </nav>

          {/* User Profile */}
          <div className="p-4 border-t border-dark-200">
            <div className="flex items-center gap-3 p-3 rounded-lg bg-dark-200 mb-2">
              <div className="w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center text-white font-bold">
                {user?.full_name?.charAt(0) || 'U'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-dark-900 truncate">{user?.full_name}</p>
                <p className="text-xs text-dark-600 truncate">{user?.email}</p>
              </div>
            </div>
            <button
              onClick={logout}
              className="flex items-center gap-2 w-full px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <LogOut className="w-5 h-5" />
              <span className="font-medium">Logout</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="lg:pl-64">
        {/* Top Bar */}
        <header className="sticky top-0 z-30 bg-dark-100/80 backdrop-blur-xl border-b border-dark-200">
          <div className="flex items-center justify-between h-16 px-4 sm:px-6">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden text-dark-600 hover:text-dark-900"
            >
              <Menu className="w-6 h-6" />
            </button>
            <div className="flex-1 lg:flex-none" />
            
            {/* Notifications */}
            <div className="relative">
              <button
                onClick={() => setNotificationsOpen(!notificationsOpen)}
                className="relative p-2 text-dark-600 hover:text-dark-900 hover:bg-dark-200 rounded-lg transition-colors"
              >
                <Bell className="w-6 h-6" />
                {unreadCount > 0 && (
                  <span className="absolute top-1 right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-bold">
                    {unreadCount}
                  </span>
                )}
              </button>

              {/* Notifications Dropdown */}
              <AnimatePresence>
                {notificationsOpen && (
                  <>
                    <div
                      className="fixed inset-0 z-40"
                      onClick={() => setNotificationsOpen(false)}
                    />
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-dark-200 z-50 max-h-96 overflow-y-auto"
                    >
                      <div className="p-4 border-b border-dark-200">
                        <h3 className="font-semibold text-dark-900">Notifications</h3>
                      </div>
                      
                      {notifications.length === 0 ? (
                        <div className="p-8 text-center text-dark-600">
                          <Bell className="w-12 h-12 mx-auto mb-3 opacity-30" />
                          <p>No new notifications</p>
                        </div>
                      ) : (
                        <div className="divide-y divide-dark-200">
                          {notifications.map((notification) => {
                            const isInvite = notification.notification_type === 'collaboration_invite'
                            
                            return (
                              <div
                                key={notification.notification_id}
                                className="p-4"
                              >
                                <div className={!isInvite ? 'cursor-pointer hover:bg-dark-50' : ''} onClick={() => !isInvite && handleNotificationClick(notification)}>
                                  <p className="font-medium text-dark-900 mb-1">
                                    {notification.title}
                                  </p>
                                  <p className="text-sm text-dark-600 mb-2">
                                    {notification.message}
                                  </p>
                                  <p className="text-xs text-dark-500 mb-2">
                                    {new Date(notification.created_at).toLocaleDateString()}
                                  </p>
                                </div>
                                
                                {isInvite && (
                                  <div className="flex gap-2 mt-3">
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation()
                                        handleInvitationResponse(notification, 'accept')
                                      }}
                                      className="flex-1 px-3 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-sm font-medium"
                                    >
                                      Accept
                                    </button>
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation()
                                        handleInvitationResponse(notification, 'decline')
                                      }}
                                      className="flex-1 px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors text-sm font-medium"
                                    >
                                      Decline
                                    </button>
                                  </div>
                                )}
                              </div>
                            )
                          })}
                        </div>
                      )}
                    </motion.div>
                  </>
                )}
              </AnimatePresence>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
