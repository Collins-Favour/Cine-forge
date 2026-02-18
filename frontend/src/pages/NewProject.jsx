import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Loader } from 'lucide-react'
import { projectsApi } from '@services/apiServices'

export default function NewProject() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [formData, setFormData] = useState({
    title: '',
    logline: '',
    synopsis: '',
    genre: '',
    target_length: '',
    budget_range: ''
  })

  const genres = [
    'Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary',
    'Drama', 'Fantasy', 'Horror', 'Mystery', 'Romance', 'Sci-Fi',
    'Thriller', 'Western', 'Other'
  ]

  const budgetRanges = [
    'Under $100K',
    '$100K - $500K',
    '$500K - $1M',
    '$1M - $5M',
    '$5M - $20M',
    '$20M+'
  ]

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!formData.title.trim()) {
      setError('Project title is required')
      return
    }

    try {
      setLoading(true)
      setError(null)
      
      console.log('📤 Creating project with data:', formData)
      
      const response = await projectsApi.createProject({
        ...formData,
        target_length: formData.target_length ? parseInt(formData.target_length) : null
      })
      
      console.log('✅ Project created successfully:', response.data)
      
      // Navigate to the new project
      const projectId = response.data.project.project_id
      navigate(`/projects/${projectId}`)
    } catch (err) {
      console.error('❌ Error creating project:', err)
      console.error('Error response:', err.response?.data)
      
      const errorMessage = err.response?.data?.error || 
                          err.response?.data?.message || 
                          err.message || 
                          'Failed to create project. Please try again.'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <Link 
          to="/projects" 
          className="inline-flex items-center gap-2 text-dark-600 hover:text-dark-900 mb-4"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Projects</span>
        </Link>
        <h1 className="text-3xl font-bold text-dark-900">Create New Project</h1>
        <p className="text-dark-600 mt-2">
          Start your filmmaking journey by setting up a new project
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="card">
        <div className="space-y-6">
          {/* Title */}
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-dark-900 mb-2">
              Project Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="e.g., The Last Sunset"
              className="input"
              required
            />
          </div>

          {/* Logline */}
          <div>
            <label htmlFor="logline" className="block text-sm font-medium text-dark-900 mb-2">
              Logline
            </label>
            <input
              type="text"
              id="logline"
              name="logline"
              value={formData.logline}
              onChange={handleChange}
              placeholder="One sentence that captures your story"
              className="input"
            />
            <p className="text-sm text-dark-500 mt-1">
              A brief, compelling summary of your story (1-2 sentences)
            </p>
          </div>

          {/* Synopsis */}
          <div>
            <label htmlFor="synopsis" className="block text-sm font-medium text-dark-900 mb-2">
              Synopsis
            </label>
            <textarea
              id="synopsis"
              name="synopsis"
              value={formData.synopsis}
              onChange={handleChange}
              placeholder="Provide a detailed overview of your story..."
              rows={6}
              className="input"
            />
            <p className="text-sm text-dark-500 mt-1">
              A detailed description of your project's story and vision
            </p>
          </div>

          {/* Genre and Target Length Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Genre */}
            <div>
              <label htmlFor="genre" className="block text-sm font-medium text-dark-900 mb-2">
                Genre
              </label>
              <select
                id="genre"
                name="genre"
                value={formData.genre}
                onChange={handleChange}
                className="input"
              >
                <option value="">Select a genre</option>
                {genres.map(genre => (
                  <option key={genre} value={genre}>{genre}</option>
                ))}
              </select>
            </div>

            {/* Target Length */}
            <div>
              <label htmlFor="target_length" className="block text-sm font-medium text-dark-900 mb-2">
                Target Length (minutes)
              </label>
              <input
                type="number"
                id="target_length"
                name="target_length"
                value={formData.target_length}
                onChange={handleChange}
                placeholder="e.g., 120"
                min="1"
                className="input"
              />
            </div>
          </div>

          {/* Budget Range */}
          <div>
            <label htmlFor="budget_range" className="block text-sm font-medium text-dark-900 mb-2">
              Budget Range
            </label>
            <select
              id="budget_range"
              name="budget_range"
              value={formData.budget_range}
              onChange={handleChange}
              className="input"
            >
              <option value="">Select budget range</option>
              {budgetRanges.map(range => (
                <option key={range} value={range}>{range}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-4 mt-8 pt-6 border-t border-dark-200">
          <Link
            to="/projects"
            className="btn-secondary"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={loading}
            className="btn-primary inline-flex items-center gap-2"
          >
            {loading && <Loader className="w-5 h-5 animate-spin" />}
            <span>{loading ? 'Creating...' : 'Create Project'}</span>
          </button>
        </div>
      </form>
    </div>
  )
}
