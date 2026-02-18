import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { motion } from 'framer-motion'
import { 
  ArrowLeft, 
  Search, 
  FolderOpen, 
  Trash2, 
  Eye, 
  Users,
  Calendar,
  Tag,
  AlertCircle,
  RefreshCw
} from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import api from '@services/api'
import Modal, { ConfirmModal } from '@components/Modal'
import toast from 'react-hot-toast'

export default function ProjectManagement() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [selectedProject, setSelectedProject] = useState(null)

  const { data, isLoading, refetch, isFetching } = useQuery(
    ['admin-projects', page, search],
    async () => {
      const response = await api.get('/admin/projects', {
        params: { page, per_page: 20, search }
      })
      return response.data
    }
  )

  const deleteMutation = useMutation(
    (projectId) => api.delete(`/admin/projects/${projectId}`),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('admin-projects')
        toast.success('Project archived successfully')
        setShowDeleteConfirm(false)
        setSelectedProject(null)
      },
      onError: (error) => {
        const errorMsg = error.response?.data?.error || 'Failed to delete project'
        toast.error(errorMsg)
        console.error('Delete project error:', error)
      }
    }
  )

  const handleDeleteClick = (project) => {
    setSelectedProject(project)
    setShowDeleteConfirm(true)
  }

  const handleDeleteConfirm = () => {
    if (selectedProject) {
      deleteMutation.mutate(selectedProject.project_id)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const stageColors = {
    concept: 'bg-purple-100 text-purple-700',
    'pre-production': 'bg-yellow-100 text-yellow-700',
    production: 'bg-blue-100 text-blue-700',
    'post-production': 'bg-orange-100 text-orange-700',
    completed: 'bg-green-100 text-green-700'
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/admin/dashboard')}
            className="btn-secondary flex items-center gap-2 px-3 py-2"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-3xl font-display font-bold text-dark-900 mb-2">
              Project Management
            </h1>
            <p className="text-dark-600">View and manage all platform projects</p>
          </div>
        </div>
        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="btn-secondary flex items-center gap-2"
          title="Refresh projects"
        >
          <RefreshCw className={`w-4 h-4 ${isFetching ? 'animate-spin' : ''}`} />
          <span className="hidden sm:inline">Refresh</span>
        </button>
      </div>

      {/* Search */}
      <div className="card mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-400" />
          <input
            type="text"
            placeholder="Search projects by name..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(1)
            }}
            className="w-full pl-10 pr-4 py-3 border border-dark-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-6 mb-6">
        <div className="card">
          <div className="text-sm text-dark-600 mb-1">Total Projects</div>
          <div className="text-2xl font-bold text-dark-900">{data?.total || 0}</div>
        </div>
        <div className="card">
          <div className="text-sm text-dark-600 mb-1">Current Page</div>
          <div className="text-2xl font-bold text-dark-900">{page} of {data?.pages || 1}</div>
        </div>
        <div className="card">
          <div className="text-sm text-dark-600 mb-1">Showing</div>
          <div className="text-2xl font-bold text-dark-900">{data?.projects?.length || 0} projects</div>
        </div>
      </div>

      {/* Projects List */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : data?.projects?.length === 0 ? (
        <div className="card text-center py-12">
          <FolderOpen className="w-16 h-16 text-dark-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-dark-900 mb-2">No projects found</h3>
          <p className="text-dark-600">
            {search ? 'Try adjusting your search criteria' : 'No projects have been created yet'}
          </p>
        </div>
      ) : (
        <>
          <div className="card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-dark-200">
                    <th className="text-left py-4 px-4 font-semibold text-dark-900">Project</th>
                    <th className="text-left py-4 px-4 font-semibold text-dark-900">Owner</th>
                    <th className="text-left py-4 px-4 font-semibold text-dark-900">Stage</th>
                    <th className="text-left py-4 px-4 font-semibold text-dark-900">Genre</th>
                    <th className="text-left py-4 px-4 font-semibold text-dark-900">Created</th>
                    <th className="text-left py-4 px-4 font-semibold text-dark-900">Updated</th>
                    <th className="text-right py-4 px-4 font-semibold text-dark-900">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data?.projects?.map((project) => (
                    <motion.tr
                      key={project.project_id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="border-b border-dark-100 hover:bg-dark-50 transition-colors"
                    >
                      <td className="py-4 px-4">
                        <div>
                          <div className="font-medium text-dark-900">{project.project_name}</div>
                          {project.logline && (
                            <div className="text-sm text-dark-600 line-clamp-1">{project.logline}</div>
                          )}
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div className="text-sm">
                          <div className="text-dark-900">{project.creator?.username || 'Unknown'}</div>
                          <div className="text-dark-600">{project.creator?.email || ''}</div>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${stageColors[project.production_stage] || 'bg-gray-100 text-gray-700'}`}>
                          {project.production_stage?.replace('-', ' ').toUpperCase() || 'N/A'}
                        </span>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-1 text-sm text-dark-600">
                          <Tag className="w-4 h-4" />
                          <span>{project.genre || 'N/A'}</span>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-1 text-sm text-dark-600">
                          <Calendar className="w-4 h-4" />
                          <span>{formatDate(project.created_at)}</span>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div className="text-sm text-dark-600">
                          {formatDate(project.updated_at)}
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center justify-end gap-2">
                          <Link
                            to={`/projects/${project.project_id}`}
                            className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                            title="View project"
                          >
                            <Eye className="w-4 h-4" />
                          </Link>
                          <button
                            onClick={() => handleDeleteClick(project)}
                            disabled={deleteMutation.isLoading}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            title="Archive project"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Pagination */}
          {data?.pages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-6">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <span className="text-dark-600">
                Page {page} of {data?.pages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(data?.pages, p + 1))}
                disabled={page === data?.pages}
                className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        isOpen={showDeleteConfirm}
        onClose={() => {
          setShowDeleteConfirm(false)
          setSelectedProject(null)
        }}
        onConfirm={handleDeleteConfirm}
        title="Archive Project"
        message={
          <div className="space-y-3">
            <div className="flex items-start gap-2 text-amber-600 bg-amber-50 p-3 rounded-lg">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold">Warning: This will archive the project</p>
                <p className="text-sm mt-1">The project will be hidden from users but not permanently deleted.</p>
              </div>
            </div>
            <p className="text-dark-700">
              Are you sure you want to archive <span className="font-semibold">"{selectedProject?.project_name}"</span>?
            </p>
          </div>
        }
        confirmText={deleteMutation.isLoading ? 'Archiving...' : 'Archive Project'}
        cancelText="Cancel"
        variant="danger"
      />
    </div>
  )
}
