import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Search, Filter, FolderOpen, Users, Calendar, MoreVertical } from 'lucide-react'
import { useAuthStore } from '@store/authStore'
import { projectsApi } from '@services/apiServices'

export default function Projects() {
  const { user } = useAuthStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    try {
      setLoading(true)
      const response = await projectsApi.getProjects()
      setProjects(response.data.projects || [])
      setError(null)
    } catch (err) {
      console.error('Error fetching projects:', err)
      setError(err.response?.data?.error || 'Failed to load projects')
      setProjects([])
    } finally {
      setLoading(false)
    }
  }

  const statusColors = {
    concept: 'bg-purple-100 text-purple-700',
    'pre-production': 'bg-yellow-100 text-yellow-700',
    production: 'bg-blue-100 text-blue-700',
    'post-production': 'bg-orange-100 text-orange-700',
    completed: 'bg-green-100 text-green-700'
  }

  const statusLabels = {
    concept: 'Concept',
    'pre-production': 'Pre-Production',
    production: 'Production',
    'post-production': 'Post-Production',
    completed: 'Completed'
  }

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         (project.description || project.logline || '').toLowerCase().includes(searchQuery.toLowerCase())
    
    // Filter logic: 'active' means not completed, 'completed' means completed stage
    let matchesStatus = true
    if (filterStatus === 'active') {
      matchesStatus = project.production_stage !== 'completed'
    } else if (filterStatus === 'completed') {
      matchesStatus = project.production_stage === 'completed'
    } else if (filterStatus !== 'all') {
      matchesStatus = project.production_stage === filterStatus
    }
    
    return matchesSearch && matchesStatus
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto">
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-display font-bold text-dark-900 mb-2">Projects</h1>
          <p className="text-dark-600">Manage your film projects and collaborate with your team</p>
        </div>
        <Link
          to="/projects/new"
          className="btn-primary flex items-center gap-2 justify-center"
        >
          <Plus className="w-5 h-5" />
          <span>New Project</span>
        </Link>
      </div>

      {/* Filters */}
      <div className="card mb-6">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-400" />
            <input
              type="text"
              placeholder="Search projects..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input pl-10 w-full"
            />
          </div>

          {/* Status Filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-dark-600" />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="input min-w-[180px]"
            >
              <option value="all">All Projects</option>
              <option value="active">Active Projects</option>
              <option value="completed">Completed</option>
              <option value="concept">Concept</option>
              <option value="pre-production">Pre-Production</option>
              <option value="production">Production</option>
              <option value="post-production">Post-Production</option>
            </select>
          </div>
        </div>
      </div>

      {/* Projects Grid */}
      {filteredProjects.length === 0 ? (
        <div className="card text-center py-12">
          <FolderOpen className="w-16 h-16 text-dark-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-dark-900 mb-2">No projects found</h3>
          <p className="text-dark-600 mb-6">
            {searchQuery || filterStatus !== 'all' 
              ? 'Try adjusting your search or filters' 
              : 'Get started by creating your first project'}
          </p>
          {!searchQuery && filterStatus === 'all' && (
            <Link to="/projects/new" className="btn-primary inline-flex items-center gap-2">
              <Plus className="w-5 h-5" />
              <span>Create Project</span>
            </Link>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project) => (
            <Link
              key={project.project_id}
              to={`/projects/${project.project_id}`}
              className="card hover:shadow-xl transition-all duration-300 group"
            >
              {/* Thumbnail */}
              <div className="aspect-video bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg mb-4 flex items-center justify-center">
                <FolderOpen className="w-16 h-16 text-white/50 group-hover:scale-110 transition-transform" />
              </div>

              {/* Content */}
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="font-semibold text-lg text-dark-900 group-hover:text-primary-600 transition-colors line-clamp-1">
                    {project.title}
                  </h3>
                  <button className="text-dark-400 hover:text-dark-600 p-1">
                    <MoreVertical className="w-5 h-5" />
                  </button>
                </div>

                <p className="text-dark-600 text-sm line-clamp-2">{project.description || project.logline}</p>

                {/* Meta Info */}
                <div className="flex items-center gap-4 text-sm text-dark-500">
                  <div className="flex items-center gap-1">
                    <Users className="w-4 h-4" />
                    <span>{project.stats?.total_collaborators || project.collaborators || 0}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    <span>{new Date(project.updated_at).toLocaleDateString()}</span>
                  </div>
                </div>

                {/* Status & Genre */}
                <div className="flex items-center justify-between pt-3 border-t border-dark-200">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    statusColors[project.production_stage] || 'bg-gray-100 text-gray-700'
                  }`}>
                    {statusLabels[project.production_stage] || 'Unknown'}
                  </span>
                  <span className="text-xs text-dark-500">{project.genre || 'N/A'}</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
        <div className="card text-center">
          <div className="text-3xl font-bold text-primary-600 mb-1">{projects.length}</div>
          <div className="text-sm text-dark-600">Total Projects</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-blue-600 mb-1">
            {projects.filter(p => p.production_stage && p.production_stage !== 'completed').length}
          </div>
          <div className="text-sm text-dark-600">Active Projects</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-green-600 mb-1">
            {projects.filter(p => p.production_stage === 'completed').length}
          </div>
          <div className="text-sm text-dark-600">Completed</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-orange-600 mb-1">
            {projects.filter(p => p.production_stage === 'production').length}
          </div>
          <div className="text-sm text-dark-600">In Production</div>
        </div>
      </div>
    </div>
  )
}
