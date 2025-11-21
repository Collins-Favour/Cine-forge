import { useState, useEffect } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { ArrowLeft, Loader } from 'lucide-react'
import { projectsApi } from '@services/apiServices'

export default function ProjectEdit() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [formData, setFormData] = useState({
    title: '',
    logline: '',
    synopsis: '',
    genre: '',
    target_length: '',
    budget_range: ''
  })

  useEffect(() => {
    fetchProject()
  }, [id])

  const fetchProject = async () => {
    try {
      setLoading(true)
      const resp = await projectsApi.getProject(id)
      const project = resp.data || resp.data?.project || resp
      setFormData({
        title: project.title || '',
        logline: project.logline || '',
        synopsis: project.synopsis || '',
        genre: project.genre || '',
        target_length: project.target_length || '',
        budget_range: project.budget_range || ''
      })
    } catch (err) {
      console.error('Error loading project for edit', err)
      setError(err.response?.data?.error || 'Failed to load project')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      setSaving(true)
      await projectsApi.updateProject(id, {
        ...formData,
        target_length: formData.target_length ? parseInt(formData.target_length) : null
      })
      navigate(`/projects/${id}`)
    } catch (err) {
      console.error('Error updating project:', err)
      setError(err.response?.data?.error || 'Failed to update project')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return (<div className="flex items-center justify-center h-48"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600"></div></div>)

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <Link to={`/projects/${id}`} className="inline-flex items-center gap-2 text-dark-600 hover:text-dark-900 mb-4">
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Project</span>
        </Link>
        <h1 className="text-3xl font-bold text-dark-900">Edit Project</h1>
      </div>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">{error}</div>}

      <form onSubmit={handleSubmit} className="card">
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-dark-900 mb-2">Project Title</label>
            <input name="title" value={formData.title} onChange={handleChange} className="input" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-dark-900 mb-2">Logline</label>
            <input name="logline" value={formData.logline} onChange={handleChange} className="input" />
          </div>
          <div>
            <label className="block text-sm font-medium text-dark-900 mb-2">Synopsis</label>
            <textarea name="synopsis" value={formData.synopsis} onChange={handleChange} rows={6} className="input" />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-dark-900 mb-2">Genre</label>
              <input name="genre" value={formData.genre} onChange={handleChange} className="input" />
            </div>
            <div>
              <label className="block text-sm font-medium text-dark-900 mb-2">Target Length (minutes)</label>
              <input type="number" name="target_length" value={formData.target_length} onChange={handleChange} className="input" />
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-4 mt-8 pt-6 border-t border-dark-200">
          <Link to={`/projects/${id}`} className="btn-secondary">Cancel</Link>
          <button type="submit" className="btn-primary inline-flex items-center gap-2" disabled={saving}>
            {saving && <Loader className="w-5 h-5 animate-spin" />}
            <span>{saving ? 'Saving...' : 'Save Changes'}</span>
          </button>
        </div>
      </form>
    </div>
  )
}
