import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { 
  ArrowLeft, 
  Edit, 
  Share2, 
  Trash2, 
  FileText, 
  Film, 
  Image, 
  Users, 
  MessageSquare,
  Calendar,
  Clock,
  DollarSign,
  Tag,
  MoreVertical,
  Plus,
  Play,
  Settings as SettingsIcon
} from 'lucide-react'
import { projectsApi } from '@services/apiServices'
import { userService } from '@services'
import Modal, { SuccessModal, ErrorModal, ConfirmModal } from '@components/Modal'

export default function ProjectDetails() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(true)
  const [project, setProject] = useState(null)
  const [collaborators, setCollaborators] = useState([])
  const [activity, setActivity] = useState([])
  const [error, setError] = useState(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [showInviteModal, setShowInviteModal] = useState(false)
  const [inviting, setInviting] = useState(false)
  const [showInviteSuccess, setShowInviteSuccess] = useState(false)
  const [showInviteError, setShowInviteError] = useState(false)
  const [inviteMessage, setInviteMessage] = useState('')
  const [inviteEmail, setInviteEmail] = useState('')
  const [inviteRole, setInviteRole] = useState('viewer')
  const [selectedCollaboratorId, setSelectedCollaboratorId] = useState(null)
  const [showRemoveConfirm, setShowRemoveConfirm] = useState(false)
  const [showCollaboratorMenu, setShowCollaboratorMenu] = useState(false)
  const [selectedCollaborator, setSelectedCollaborator] = useState(null)
  const [showTransferConfirm, setShowTransferConfirm] = useState(false)
  const [transferring, setTransferring] = useState(false)

  useEffect(() => {
    fetchProjectData()
  }, [id])

  const fetchProjectData = async () => {
    try {
      setLoading(true)
      
      // Fetch project details
      const projectResponse = await projectsApi.getProject(id)
      setProject(projectResponse.data.project)
      
      // Fetch collaborators
      try {
        const collabResponse = await projectsApi.getCollaborators(id)
        setCollaborators(collabResponse.data.collaborators || [])
      } catch (err) {
        console.error('Error fetching collaborators:', err)
        setCollaborators([])
      }
      
      // Fetch activity
      try {
        const activityResponse = await projectsApi.getActivity(id)
        setActivity(activityResponse.data.activities || [])
      } catch (err) {
        console.error('Error fetching activity:', err)
        setActivity([])
      }
      
      setError(null)
    } catch (err) {
      console.error('Error fetching project:', err)
      setError(err.response?.data?.error || 'Failed to load project')
      setProject(null)
      setCollaborators([])
      setActivity([])
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    try {
      setDeleting(true)
      await projectsApi.deleteProject(id)
      navigate('/projects')
    } catch (err) {
      console.error('Error deleting project:', err)
      setError(err.response?.data?.error || 'Failed to delete project')
      setShowDeleteConfirm(false)
    } finally {
      setDeleting(false)
    }
  }

  const stageColors = {
    concept: 'bg-purple-100 text-purple-700',
    'pre-production': 'bg-yellow-100 text-yellow-700',
    production: 'bg-blue-100 text-blue-700',
    'post-production': 'bg-orange-100 text-orange-700',
    completed: 'bg-green-100 text-green-700'
  }

  const roleColors = {
    owner: 'bg-red-100 text-red-700',
    director: 'bg-blue-100 text-blue-700',
    writer: 'bg-purple-100 text-purple-700',
    editor: 'bg-green-100 text-green-700',
    viewer: 'bg-gray-100 text-gray-700'
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now - date
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (hours < 1) return 'Just now'
    if (hours < 24) return `${hours}h ago`
    if (days < 7) return `${days}d ago`
    return date.toLocaleDateString()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-dark-900 mb-4">Project not found</h2>
        <Link to="/projects" className="btn-primary">
          Back to Projects
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Link to="/projects" className="inline-flex items-center gap-2 text-dark-600 hover:text-dark-900 mb-4">
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Projects</span>
        </Link>

        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
          {/* Project Info */}
          <div className="flex-1">
            <div className="flex items-start gap-4">
              {/* Thumbnail */}
              <div className="w-32 h-20 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center shrink-0">
                <Film className="w-12 h-12 text-white/50" />
              </div>

              <div className="flex-1">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h1 className="text-3xl font-display font-bold text-dark-900 mb-2">
                      {project.title}
                    </h1>
                    <p className="text-dark-600 mb-3">{project.logline}</p>
                    <div className="flex flex-wrap items-center gap-3 text-sm">
                      <span className={`px-3 py-1 rounded-full font-medium ${stageColors[project.production_stage]}`}>
                        {project.production_stage.replace('-', ' ').toUpperCase()}
                      </span>
                      <div className="flex items-center gap-1 text-dark-600">
                        <Tag className="w-4 h-4" />
                        <span>{project.genre}</span>
                      </div>
                      <div className="flex items-center gap-1 text-dark-600">
                        <Clock className="w-4 h-4" />
                        <span>{project.target_length} min</span>
                      </div>
                      <div className="flex items-center gap-1 text-dark-600">
                        <DollarSign className="w-4 h-4" />
                        <span>{project.budget_range}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-wrap gap-2">
            <button onClick={() => navigate(`/projects/${id}/edit`)} className="btn-secondary flex items-center gap-2">
              <Edit className="w-5 h-5" />
              <span>Edit</span>
            </button>
            <button onClick={() => setShowInviteModal(true)} className="btn-secondary flex items-center gap-2">
              <Share2 className="w-5 h-5" />
              <span>Share</span>
            </button>
            <button onClick={() => navigate(`/projects/${id}/settings`)} className="btn-secondary flex items-center gap-2">
              <SettingsIcon className="w-5 h-5" />
              <span className="sr-only">Settings</span>
            </button>
            <button 
              onClick={() => setShowDeleteConfirm(true)}
              className="btn-secondary text-red-600 hover:bg-red-50"
            >
              <Trash2 className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <Link 
          to={`/projects/${id}/script`}
          className="card hover:shadow-lg transition-all duration-300 group"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center group-hover:bg-blue-200 transition-colors">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <div className="font-semibold text-dark-900">Script</div>
              <div className="text-sm text-dark-600">v{project.stats?.latest_script_version || 1}</div>
            </div>
          </div>
        </Link>

        <Link 
          to={`/projects/${id}/storyboard`}
          className="card hover:shadow-lg transition-all duration-300 group"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-purple-100 flex items-center justify-center group-hover:bg-purple-200 transition-colors">
              <Image className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <div className="font-semibold text-dark-900">Storyboard</div>
              <div className="text-sm text-dark-600">{project.stats?.total_scenes || 0} scenes</div>
            </div>
          </div>
        </Link>

        <Link 
          to={`/projects/${id}/c-space`}
          className="card hover:shadow-lg transition-all duration-300 group"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-green-100 flex items-center justify-center group-hover:bg-green-200 transition-colors">
              <MessageSquare className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <div className="font-semibold text-dark-900">C-Space</div>
              <div className="text-sm text-dark-600">Collaborate</div>
            </div>
          </div>
        </Link>

        <button className="card hover:shadow-lg transition-all duration-300 group text-left">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-orange-100 flex items-center justify-center group-hover:bg-orange-200 transition-colors">
              <Play className="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <div className="font-semibold text-dark-900">Preview</div>
              <div className="text-sm text-dark-600">Watch</div>
            </div>
          </div>
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-dark-200 mb-6">
        <div className="flex gap-6">
          {['overview', 'team', 'activity'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 font-medium capitalize transition-colors ${
                activeTab === tab
                  ? 'text-primary-600 border-b-2 border-primary-600'
                  : 'text-dark-600 hover:text-dark-900'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Synopsis */}
          <div className="lg:col-span-2 space-y-6">
            <div className="card">
              <h3 className="text-lg font-semibold text-dark-900 mb-4">Synopsis</h3>
              <p className="text-dark-700 leading-relaxed">{project.synopsis}</p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="card text-center">
                <div className="text-3xl font-bold text-primary-600 mb-1">{project.stats?.total_scenes || 0}</div>
                <div className="text-sm text-dark-600">Scenes</div>
              </div>
              <div className="card text-center">
                <div className="text-3xl font-bold text-purple-600 mb-1">{project.stats?.total_characters || 0}</div>
                <div className="text-sm text-dark-600">Characters</div>
              </div>
              <div className="card text-center">
                <div className="text-3xl font-bold text-green-600 mb-1">{project.stats?.total_collaborators || 0}</div>
                <div className="text-sm text-dark-600">Team Members</div>
              </div>
              <div className="card text-center">
                <div className="text-3xl font-bold text-blue-600 mb-1">v{project.stats?.latest_script_version || 1}</div>
                <div className="text-sm text-dark-600">Script Version</div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Project Details */}
            <div className="card">
              <h3 className="text-lg font-semibold text-dark-900 mb-4">Project Details</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-dark-600">Created</span>
                  <span className="font-medium text-dark-900">{formatDate(project.created_at)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-dark-600">Last Updated</span>
                  <span className="font-medium text-dark-900">{formatDate(project.updated_at)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-dark-600">Status</span>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${stageColors[project.production_stage]}`}>
                    {project.production_stage.replace('-', ' ')}
                  </span>
                </div>
              </div>
            </div>

            {/* Team Section */}
            <div className="card">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-dark-900">Team</h3>
                <button onClick={() => setActiveTab('team')} className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                  View All
                </button>
              </div>
              <div className="space-y-2">
                {collaborators.slice(0, 3).map((collab) => (
                  <div key={collab.collaboration_id || collab.user_id} className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-primary-500 flex items-center justify-center text-white text-sm font-semibold">
                      {(collab.user?.username || collab.user?.first_name || 'U').charAt(0).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-dark-900 truncate">{collab.user?.username || `${collab.user?.first_name || ''} ${collab.user?.last_name || ''}`.trim() || 'Unknown User'}</div>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${roleColors[collab.role]}`}>
                      {collab.role}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
      {/* Invite Modal - enter email and choose role. Resolves user via /users/search then adds collaborator by user_id */}
      <Modal isOpen={showInviteModal} onClose={() => setShowInviteModal(false)} title="Invite Team Member" size="md">
        <div className="p-6 space-y-4">
          <p className="text-sm text-dark-700">Enter the email address of the person you want to invite and select a role.</p>
          <div>
            <label className="block text-sm font-medium text-dark-700 mb-1">Email</label>
            <input type="email" value={inviteEmail} onChange={(e) => setInviteEmail(e.target.value)} placeholder="name@example.com" className="input w-full" />
          </div>
          <div>
            <label className="block text-sm font-medium text-dark-700 mb-1">Role</label>
            <select value={inviteRole} onChange={(e) => setInviteRole(e.target.value)} className="input w-full">
              <option value="viewer">Viewer</option>
              <option value="writer">Writer</option>
              <option value="editor">Editor</option>
              <option value="director">Director</option>
              <option value="owner">Owner</option>
            </select>
          </div>
          <div className="flex justify-end gap-3">
            <button onClick={() => setShowInviteModal(false)} className="btn-secondary">Cancel</button>
            <button
              onClick={async () => {
                if (!inviteEmail || inviteEmail.length < 3) return setInviteMessage('Please enter a valid email');
                try {
                  setInviting(true)
                  // Send invite by email; backend will verify the user exists and create notification
                  await projectsApi.addCollaborator(id, { email: inviteEmail, role: inviteRole })
                  const collabResponse = await projectsApi.getCollaborators(id)
                  setCollaborators(collabResponse.data.collaborators || [])
                  setInviteMessage('Invitation sent successfully')
                  setShowInviteModal(false)
                  setShowInviteSuccess(true)
                } catch (err) {
                  console.error('Error inviting collaborator:', err)
                  setInviteMessage(err.response?.data?.error || 'Failed to send invitation')
                  setShowInviteError(true)
                } finally {
                  setInviting(false)
                }
              }}
              className="btn-primary"
              disabled={inviting}
            >
              {inviting ? 'Inviting...' : 'Invite'}
            </button>
          </div>
        </div>
      </Modal>

      <SuccessModal isOpen={showInviteSuccess} onClose={() => setShowInviteSuccess(false)} title="Invitation Sent" message={inviteMessage} />
      <ErrorModal isOpen={showInviteError} onClose={() => setShowInviteError(false)} title="Invitation Failed" message={inviteMessage} />

      {/* Collaborator Options Modal (View profile, Message, Remove) */}
      <Modal isOpen={showCollaboratorMenu} onClose={() => { setShowCollaboratorMenu(false); setSelectedCollaborator(null) }} title={selectedCollaborator ? (selectedCollaborator.user?.username || 'Collaborator') : 'Collaborator'} size="sm">
          <div className="p-6 space-y-3">
          <button onClick={() => {
            const uid = selectedCollaborator?.user?.user_id || selectedCollaborator?.user?.id
            if (uid) {
              setShowCollaboratorMenu(false)
              navigate(`/admin/users/${uid}`)
            }
          }} className="w-full text-left px-4 py-3 rounded-lg hover:bg-dark-50">View Profile</button>

          <button onClick={() => {
            const uid = selectedCollaborator?.user?.user_id || selectedCollaborator?.user?.id
            setShowCollaboratorMenu(false)
            if (uid) navigate(`/projects/${id}/c-space?user=${uid}`)
            else navigate(`/projects/${id}/c-space`)
          }} className="w-full text-left px-4 py-3 rounded-lg hover:bg-dark-50">Message</button>

          {/* Role change control */}
          <div className="pt-2">
            <label className="block text-sm font-medium text-dark-700 mb-2">Change Role</label>
            <div className="flex gap-2">
              <select value={selectedCollaborator?.role || ''} onChange={(e) => setSelectedCollaborator({ ...selectedCollaborator, role: e.target.value })} className="input flex-1">
                <option value="director">Director</option>
                <option value="writer">Writer</option>
                <option value="editor">Editor</option>
                <option value="viewer">Viewer</option>
              </select>
              <button
                onClick={async () => {
                  if (!selectedCollaborator) return
                  const collabId = selectedCollaborator.collaboration_id || selectedCollaboratorId
                  const newRole = selectedCollaborator.role
                  if (!collabId) return
                  try {
                    await projectsApi.updateCollaborator(id, collabId, { role: newRole })
                    const collabResponse = await projectsApi.getCollaborators(id)
                    setCollaborators(collabResponse.data.collaborators || [])
                    setShowCollaboratorMenu(false)
                    setInviteMessage('Role updated successfully')
                    setShowInviteSuccess(true)
                  } catch (err) {
                    console.error('Error updating role:', err)
                    setInviteMessage(err.response?.data?.error || 'Failed to update role')
                    setShowInviteError(true)
                  }
                }}
                className="btn-primary"
              >
                Save
              </button>
            </div>
          </div>

          {/* Make Owner action */}
          {selectedCollaborator && selectedCollaborator.role !== 'owner' && (
            <div className="pt-3">
              <button
                onClick={() => setShowTransferConfirm(true)}
                className="w-full text-left px-4 py-3 rounded-lg bg-yellow-50 text-yellow-800 hover:bg-yellow-100"
              >
                Make Owner
              </button>
            </div>
          )}

          <button onClick={() => { setShowCollaboratorMenu(false); setShowRemoveConfirm(true) }} className="w-full text-left px-4 py-3 rounded-lg text-red-600 hover:bg-red-50">Remove from Project</button>
        </div>
      </Modal>

      {/* Remove Collaborator Confirm */}
      <ConfirmModal
        isOpen={showRemoveConfirm}
        onClose={() => { setShowRemoveConfirm(false); setSelectedCollaboratorId(null) }}
        onConfirm={async () => {
          try {
            await projectsApi.removeCollaborator(id, selectedCollaboratorId)
            const collabResponse = await projectsApi.getCollaborators(id)
            setCollaborators(collabResponse.data.collaborators || [])
            setShowRemoveConfirm(false)
            setInviteMessage('Collaborator removed successfully')
            setShowInviteSuccess(true)
          } catch (err) {
            console.error('Error removing collaborator:', err)
            setInviteMessage(err.response?.data?.error || 'Failed to remove collaborator')
            setShowInviteError(true)
          } finally {
            setSelectedCollaboratorId(null)
          }
        }}
        title="Remove Collaborator"
        message="Are you sure you want to remove this collaborator from the project?"
        confirmText="Remove"
        variant="danger"
      />

      {/* Transfer Ownership Confirm */}
      <ConfirmModal
        isOpen={showTransferConfirm}
        onClose={() => { setShowTransferConfirm(false) }}
        onConfirm={async () => {
          try {
            setTransferring(true)
            const collabId = selectedCollaborator?.collaboration_id || selectedCollaboratorId
            if (!collabId) throw new Error('Collaborator not selected')
            await projectsApi.transferOwner(id, collabId)
            const collabResponse = await projectsApi.getCollaborators(id)
            setCollaborators(collabResponse.data.collaborators || [])
            setShowTransferConfirm(false)
            setShowCollaboratorMenu(false)
            setInviteMessage('Ownership transferred successfully')
            setShowInviteSuccess(true)
          } catch (err) {
            console.error('Error transferring ownership:', err)
            setInviteMessage(err.response?.data?.error || 'Failed to transfer ownership')
            setShowInviteError(true)
          } finally {
            setTransferring(false)
          }
        }}
        title="Transfer Ownership"
        message="Are you sure you want to make this collaborator the project owner? This will transfer ownership to them."
        confirmText={transferring ? 'Transferring...' : 'Transfer Ownership'}
        variant="warning"
      />

      {activeTab === 'team' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {collaborators.map((collab) => (
            <div key={collab.user_id} className="card hover:shadow-lg transition-all duration-300">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-primary-500 flex items-center justify-center text-white font-semibold">
                    {(collab.user?.username || collab.user?.first_name || 'U').charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <div className="font-semibold text-dark-900">{collab.user?.username || `${collab.user?.first_name || ''} ${collab.user?.last_name || ''}`.trim() || 'Unknown User'}</div>
                    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${roleColors[collab.role]}`}>
                      {collab.role}
                    </span>
                  </div>
                </div>
                      <button onClick={() => { setSelectedCollaboratorId(collab.collaboration_id || collab.user?.user_id); setSelectedCollaborator(collab); setShowCollaboratorMenu(true) }} className="text-dark-400 hover:text-dark-600">
                        <MoreVertical className="w-5 h-5" />
                      </button>
              </div>
              <div className="flex gap-2">
                <button className="btn-secondary flex-1 text-sm">
                  <MessageSquare className="w-4 h-4" />
                </button>
                <button className="btn-secondary flex-1 text-sm">
                  View Profile
                </button>
              </div>
            </div>
          ))}

          {/* Add Member Card */}
          <button onClick={() => setShowInviteModal(true)} className="card hover:bg-dark-50 hover:border-primary-300 transition-all duration-300 flex flex-col items-center justify-center min-h-[180px] group">
            <div className="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center group-hover:bg-primary-200 transition-colors mb-3">
              <Plus className="w-6 h-6 text-primary-600" />
            </div>
            <div className="font-semibold text-dark-900 mb-1">Invite Team Member</div>
            <div className="text-sm text-dark-600">Add collaborators to project</div>
          </button>
        </div>
      )}

      {activeTab === 'activity' && (
        <div className="card">
          <h3 className="text-lg font-semibold text-dark-900 mb-6">Recent Activity</h3>
          <div className="space-y-4">
            {activity.map((activityItem) => (
              <div key={activityItem.activity_id} className="flex gap-4 pb-4 border-b border-dark-200 last:border-0 last:pb-0">
                <div className="w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center text-white font-semibold shrink-0">
                  {(activityItem.user_name || 'U').charAt(0)}
                </div>
                <div className="flex-1">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <span className="font-semibold text-dark-900">{activityItem.user_name}</span>
                      <span className="text-dark-700"> {activityItem.activity_description || activityItem.description}</span>
                    </div>
                    <span className="text-sm text-dark-500 whitespace-nowrap">
                      {formatDate(activityItem.created_at)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold text-dark-900 mb-2">Delete Project</h3>
            <p className="text-dark-700 mb-6">
              Are you sure you want to delete "{project?.title}"? This action cannot be undone.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                disabled={deleting}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium disabled:opacity-50"
              >
                {deleting ? 'Deleting...' : 'Delete Project'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
