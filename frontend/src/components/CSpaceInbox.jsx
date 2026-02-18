import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { MessageSquare, Users, Hash, Search, Plus, Clock } from 'lucide-react'
import { useAuthStore } from '@store/authStore'
import { projectsApi } from '@services/apiServices'

export default function CSpaceInbox() {
  console.log('CSpaceInbox component rendering')
  const { user } = useAuthStore()
  const navigate = useNavigate()
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchProjectsWithChats()
  }, [])

  const fetchProjectsWithChats = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await projectsApi.getProjects()
      const allProjects = Array.isArray(response.data.projects) ? response.data.projects : []
      
      console.log('📬 CSpace Inbox: Loaded projects for user', user?.user_id, ':', allProjects.length)
      
      // Only show projects that have collaborators (potential for chat)
      const projectsWithChats = allProjects.filter(project => 
        project.stats?.total_collaborators > 0 || project.created_by === user?.user_id
      )
      
      console.log('💬 Projects with chat capability:', projectsWithChats.length)
      
      setProjects(projectsWithChats)
    } catch (err) {
      console.error('❌ Error fetching projects:', err)
      const errorMsg = err.response?.data?.error || 'Unable to load project chats. Please try again.'
      setError(errorMsg)
      setProjects([])
    } finally {
      setLoading(false)
    }
  }

  const filteredProjects = projects.filter(project =>
    project.title.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const getLastActivityTime = (project) => {
    // Mock last activity - in real implementation, this would come from the API
    const now = new Date()
    const randomHours = Math.floor(Math.random() * 72) // Random activity within 3 days
    const lastActivity = new Date(now.getTime() - (randomHours * 60 * 60 * 1000))
    return lastActivity
  }

  const formatTime = (date) => {
    const now = new Date()
    const diffInHours = (now - date) / (1000 * 60 * 60)
    
    if (diffInHours < 1) {
      return 'Just now'
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h ago`
    } else {
      return `${Math.floor(diffInHours / 24)}d ago`
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-display font-bold text-dark-900 mb-2">C-Space Inbox</h1>
          <p className="text-dark-600">Access all your project conversations in one place</p>
        </div>
        <Link
          to="/projects"
          className="btn-secondary flex items-center gap-2 justify-center"
        >
          <Plus className="w-5 h-5" />
          <span>Browse Projects</span>
        </Link>
      </div>

      {/* Search */}
      <div className="card mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-400" />
          <input
            type="text"
            placeholder="Search project chats..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input pl-10 w-full"
          />
        </div>
      </div>

      {/* Chat List */}
      {filteredProjects.length === 0 ? (
        <div className="card text-center py-12">
          <MessageSquare className="w-16 h-16 text-dark-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-dark-900 mb-2">No project chats found</h3>
          <p className="text-dark-600 mb-6">
            {searchQuery 
              ? 'Try adjusting your search terms' 
              : 'Join or create a project to start collaborating with your team'}
          </p>
          {!searchQuery && (
            <Link to="/projects" className="btn-primary inline-flex items-center gap-2">
              <Plus className="w-5 h-5" />
              <span>Browse Projects</span>
            </Link>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {filteredProjects.map((project) => {
            const lastActivity = getLastActivityTime(project)
            const isOwner = project.created_by === user?.user_id
            
            return (
              <Link
                key={project.project_id}
                to={`/projects/${project.project_id}/c-space`}
                className="card hover:shadow-lg transition-all duration-200 group cursor-pointer"
              >
                <div className="flex items-center gap-4">
                  {/* Project Avatar */}
                  <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Hash className="w-6 h-6 text-white" />
                  </div>

                  {/* Project Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-dark-900 group-hover:text-primary-600 transition-colors truncate">
                        {project.title}
                      </h3>
                      {isOwner && (
                        <span className="bg-yellow-100 text-yellow-700 text-xs px-2 py-1 rounded-full">
                          Owner
                        </span>
                      )}
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm text-dark-500">
                      <div className="flex items-center gap-1">
                        <Users className="w-4 h-4" />
                        <span>{project.stats?.total_collaborators || 0} members</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <span className="w-1 h-1 bg-dark-300 rounded-full"></span>
                        <span>{project.production_stage}</span>
                      </div>
                    </div>

                    {/* Mock last message preview */}
                    <p className="text-sm text-dark-600 mt-2 line-clamp-1">
                      {isOwner ? "You: Let's discuss the next scenes..." : "Team member: Great work on the script!"}
                    </p>
                  </div>

                  {/* Time and unread indicator */}
                  <div className="text-right flex-shrink-0">
                    <div className="flex items-center gap-2 text-xs text-dark-500 mb-1">
                      <Clock className="w-3 h-3" />
                      <span>{formatTime(lastActivity)}</span>
                    </div>
                    
                    {/* Mock unread indicator */}
                    {Math.random() > 0.7 && (
                      <div className="bg-primary-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center ml-auto">
                        {Math.floor(Math.random() * 9) + 1}
                      </div>
                    )}
                  </div>
                </div>
              </Link>
            )
          })}
        </div>
      )}

      {/* Help text */}
      <div className="mt-8 p-4 bg-blue-50 rounded-lg">
        <p className="text-blue-800 text-sm">
          <strong>Tip:</strong> Click on any project chat to join the conversation. You can switch between 
          different channels like #general, #production, and #creative within each project.
        </p>
      </div>
    </div>
  )
}