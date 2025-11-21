import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { projectsApi } from '@services/apiServices'

export default function ProjectSettings() {
  const { id } = useParams()
  const [project, setProject] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => { fetchProject() }, [id])

  const fetchProject = async () => {
    try {
      setLoading(true)
      const resp = await projectsApi.getProject(id)
      const p = resp.data || resp.data?.project || resp
      setProject(p)
    } catch (err) {
      console.error('Error loading project settings', err)
      setError(err.response?.data?.error || 'Failed to load project')
    } finally { setLoading(false) }
  }

  const togglePublic = async () => {
    try {
      setSaving(true)
      await projectsApi.updateProject(id, { is_public: !project.is_public })
      setProject(prev => ({ ...prev, is_public: !prev.is_public }))
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update')
    } finally { setSaving(false) }
  }

  if (loading) return (<div className="flex items-center justify-center h-48">Loading...</div>)

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <Link to={`/projects/${id}`} className="inline-flex items-center gap-2 text-dark-600 hover:text-dark-900 mb-4">
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Project</span>
        </Link>
        <h1 className="text-2xl font-semibold">Project Settings</h1>
      </div>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">{error}</div>}

      <div className="card">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium">Public Project</h3>
              <p className="text-sm text-dark-600">If enabled, non-collaborators can view this project.</p>
            </div>
            <div>
              <button onClick={togglePublic} className="btn-secondary">{project.is_public ? 'Make Private' : 'Make Public'}</button>
            </div>
          </div>

          <div>
            <h3 className="font-medium">Project Owner</h3>
            <p className="text-sm text-dark-600">Owner: {project.created_by}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
