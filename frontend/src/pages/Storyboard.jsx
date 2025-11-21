import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Plus, Image as ImageIcon, Download, Share2, Grid3x3, List, Sparkles, Move, Trash2 } from 'lucide-react'
import { storyboardsApi, projectsApi } from '@services/apiServices'

export default function Storyboard() {
  const { id } = useParams()
  const [viewMode, setViewMode] = useState('grid')
  const [selectedPanel, setSelectedPanel] = useState(null)
  const [panels, setPanels] = useState([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [showErrorModal, setShowErrorModal] = useState(false)
  const [modalMessage, setModalMessage] = useState('')

  useEffect(() => {
    if (id) {
      fetchStoryboard()
    }
  }, [id])

  const fetchStoryboard = async () => {
    try {
      setLoading(true)
      const response = await storyboardsApi.getStoryboards(id)
      const panelsData = response.data.panels || []
      setPanels(panelsData)
    } catch (err) {
      console.error('Error fetching storyboard:', err)
      setPanels([])
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateStoryboard = async () => {
    try {
      setGenerating(true)
      setModalMessage('Generating storyboard with AI...')
      setShowErrorModal(true)
      
      const response = await projectsApi.generateContent(id)
      
      setModalMessage(`Storyboard generated successfully! Created ${response.data.panels_created} panels.`)
      setShowErrorModal(true)
      
      // Refresh the storyboard data
      await fetchStoryboard()
    } catch (err) {
      console.error('Error generating storyboard:', err)
      const errorMsg = err.response?.data?.error || err.response?.data?.message || 'Failed to generate storyboard'
      setModalMessage(errorMsg)
      setShowErrorModal(true)
    } finally {
      setGenerating(false)
    }
  }

  const handleGenerateAI = async (panelId) => {
    const panel = panels.find(p => p.id === panelId || p.panel_id === panelId)
    if (!panel) return
    
    try {
      const response = await storyboardsApi.generatePanelImage(panelId, {
        description: panel.description,
        shot_type: panel.shot_type || panel.shot
      })
      
      // Update panel with generated image
      setPanels(panels.map(p => 
        (p.id === panelId || p.panel_id === panelId) 
          ? { ...p, image_url: response.data.image_url, image: response.data.image_url }
          : p
      ))
    } catch (err) {
      console.error('Error generating AI image:', err)
      setModalMessage('Failed to generate image. Please try again.')
      setShowErrorModal(true)
    }
  }

  const handleAddPanel = async () => {
    // For now, just add mock panel locally
    // TODO: Implement backend panel creation when scenes are available
    const newPanel = {
      id: Date.now(),
      sceneNumber: `${panels.length + 1}A`,
      shot: 'Medium Shot',
      description: 'New panel description',
      notes: '',
      image: null,
      duration: '5s'
    }
    setPanels([...panels, newPanel])
  }

  const handleDeletePanel = async (panelId) => {
    try {
      if (typeof panelId === 'number' && panelId > 1000000) {
        // It's a temporary ID, just remove locally
        setPanels(panels.filter(p => p.id !== panelId))
      } else {
        // It's a real panel ID, delete from backend
        await storyboardsApi.deletePanel(panelId)
        setPanels(panels.filter(p => (p.id !== panelId && p.panel_id !== panelId)))
      }
    } catch (err) {
      console.error('Error deleting panel:', err)
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
    <div className="max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-display font-bold text-dark-900 mb-2">Storyboard</h1>
          <p className="text-dark-600">Visualize your scenes with AI-generated storyboards</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button className="btn-secondary flex items-center gap-2">
            <Download className="w-5 h-5" />
            <span>Export</span>
          </button>
          {panels.length === 0 && (
            <button 
              onClick={handleGenerateStoryboard} 
              disabled={generating}
              className="btn-secondary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Sparkles className={`w-5 h-5 ${generating ? 'animate-spin' : ''}`} />
              <span>{generating ? 'Generating...' : 'Generate with AI'}</span>
            </button>
          )}
          <button onClick={handleAddPanel} className="btn-primary flex items-center gap-2">
            <Plus className="w-5 h-5" />
            <span>Add Panel</span>
          </button>
        </div>
      </div>

      <div className="card mb-6">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-dark-700">View:</span>
            <div className="flex items-center gap-1 p-1 bg-dark-100 rounded-lg">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded transition-colors ${
                  viewMode === 'grid' ? 'bg-white text-primary-600 shadow' : 'text-dark-600 hover:text-dark-900'
                }`}
              >
                <Grid3x3 className="w-5 h-5" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded transition-colors ${
                  viewMode === 'list' ? 'bg-white text-primary-600 shadow' : 'text-dark-600 hover:text-dark-900'
                }`}
              >
                <List className="w-5 h-5" />
              </button>
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm text-dark-600">
            <span>{panels.length} Panels</span>
            <span>•</span>
            <span>Est. Duration: {panels.reduce((sum, p) => sum + parseInt(p.duration), 0)}s</span>
          </div>
        </div>
      </div>

      {/* Grid View */}
      {viewMode === 'grid' && (
        <>
          {panels.length === 0 ? (
            <div className="card text-center py-12">
              <ImageIcon className="w-16 h-16 text-dark-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-dark-900 mb-2">No storyboard panels yet</h3>
              <p className="text-dark-600 mb-6">
                Generate storyboard panels with AI or add them manually
              </p>
              {panels.length === 0 && (
                <button 
                  onClick={handleGenerateStoryboard} 
                  disabled={generating}
                  className="btn-primary inline-flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Sparkles className={`w-5 h-5 ${generating ? 'animate-spin' : ''}`} />
                  <span>{generating ? 'Generating...' : 'Generate with AI'}</span>
                </button>
              )}
            </div>
          ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {panels.map((panel) => {
          const panelId = panel.panel_id || panel.id
          const panelImage = panel.image_url || panel.image
          return (
            <div
            key={panelId}
            className={`card hover:shadow-xl transition-all duration-300 cursor-pointer ${
              selectedPanel === panelId ? 'ring-2 ring-primary-500' : ''
            }`}
            onClick={() => setSelectedPanel(panelId)}
          >
            <div className="aspect-video bg-gradient-to-br from-dark-100 to-dark-200 rounded-lg mb-4 flex items-center justify-center group relative overflow-hidden">
              {panelImage ? (
                <img src={panelImage} alt={panel.description} className="w-full h-full object-cover" />
              ) : (
                <>
                  <ImageIcon className="w-16 h-16 text-dark-400" />
                  <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleGenerateAI(panelId)
                      }}
                      className="btn-primary flex items-center gap-2"
                    >
                      <Sparkles className="w-5 h-5" />
                      <span>Generate with AI</span>
                    </button>
                  </div>
                </>
              )}
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-semibold">
                  Scene {panel.scene_number || panel.sceneNumber || panelId}
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDeletePanel(panelId)
                  }}
                  className="p-1 text-dark-400 hover:text-red-600 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
              <div>
                <div className="text-xs font-medium text-dark-500 mb-1">{panel.shot_type || panel.shot}</div>
                <p className="text-sm text-dark-700 line-clamp-2">{panel.description}</p>
              </div>
              {panel.notes && (
                <div className="pt-2 border-t border-dark-200">
                  <div className="text-xs text-dark-500">{panel.notes}</div>
                </div>
              )}
              <div className="flex items-center justify-between pt-2 border-t border-dark-200">
                <span className="text-xs text-dark-500">Duration</span>
                <span className="text-sm font-semibold text-dark-900">
                  {panel.duration_seconds ? `${panel.duration_seconds}s` : (panel.duration || '5s')}
                </span>
              </div>
            </div>
          </div>
          )
        })}
        <button
          onClick={handleAddPanel}
          className="card min-h-[300px] flex flex-col items-center justify-center gap-4 hover:bg-dark-50 hover:border-primary-300 transition-all duration-300 group"
        >
          <div className="w-16 h-16 rounded-full bg-primary-100 flex items-center justify-center group-hover:bg-primary-200 transition-colors">
            <Plus className="w-8 h-8 text-primary-600" />
          </div>
          <div className="text-center">
            <div className="font-semibold text-dark-900 mb-1">Add New Panel</div>
            <div className="text-sm text-dark-600">Click to create a new storyboard panel</div>
          </div>
        </button>
        </div>
          )}
        </>
      )}

      {/* List View */}
      {viewMode === 'list' && (
        <>
          {panels.length === 0 ? (
            <div className="card text-center py-12">
              <ImageIcon className="w-16 h-16 text-dark-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-dark-900 mb-2">No storyboard panels yet</h3>
              <p className="text-dark-600 mb-6">
                Generate storyboard panels with AI or add them manually
              </p>
              {panels.length === 0 && (
                <button 
                  onClick={handleGenerateStoryboard} 
                  disabled={generating}
                  className="btn-primary inline-flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Sparkles className={`w-5 h-5 ${generating ? 'animate-spin' : ''}`} />
                  <span>{generating ? 'Generating...' : 'Generate with AI'}</span>
                </button>
              )}
            </div>
          ) : (
        <div className="space-y-4">
          {panels.map((panel) => {
            const panelId = panel.panel_id || panel.id
            const panelImage = panel.image_url || panel.image
            return (
              <div
                key={panelId}
                className={`card hover:shadow-lg transition-all duration-300 cursor-pointer ${
                  selectedPanel === panelId ? 'ring-2 ring-primary-500' : ''
                }`}
                onClick={() => setSelectedPanel(panelId)}
              >
                <div className="flex gap-6">
                  {/* Image */}
                  <div className="w-64 shrink-0">
                    <div className="aspect-video bg-gradient-to-br from-dark-100 to-dark-200 rounded-lg flex items-center justify-center group relative overflow-hidden">
                      {panelImage ? (
                        <img src={panelImage} alt={panel.description} className="w-full h-full object-cover" />
                      ) : (
                        <>
                          <ImageIcon className="w-12 h-12 text-dark-400" />
                          <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                handleGenerateAI(panelId)
                              }}
                              className="btn-primary flex items-center gap-2 text-sm"
                            >
                              <Sparkles className="w-4 h-4" />
                              <span>Generate</span>
                            </button>
                          </div>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Content */}
                  <div className="flex-1 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-semibold">
                        Scene {panel.scene_number || panel.sceneNumber || panelId}
                      </span>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-dark-500">
                          {panel.duration_seconds ? `${panel.duration_seconds}s` : (panel.duration || '5s')}
                        </span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDeletePanel(panelId)
                          }}
                          className="p-1 text-dark-400 hover:text-red-600 transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-dark-700 mb-1">{panel.shot_type || panel.shot}</div>
                      <p className="text-dark-700">{panel.description}</p>
                    </div>
                    {panel.notes && (
                      <div className="pt-3 border-t border-dark-200">
                        <div className="text-sm text-dark-600">{panel.notes}</div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
          
          {/* Add Panel Button */}
          <button
            onClick={handleAddPanel}
            className="card flex items-center gap-4 py-6 hover:bg-dark-50 hover:border-primary-300 transition-all duration-300 group"
          >
            <div className="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center group-hover:bg-primary-200 transition-colors">
              <Plus className="w-6 h-6 text-primary-600" />
            </div>
            <div className="text-left">
              <div className="font-semibold text-dark-900">Add New Panel</div>
              <div className="text-sm text-dark-600">Click to create a new storyboard panel</div>
            </div>
          </button>
        </div>
          )}
        </>
      )}

      {/* Error Modal */}
      {showErrorModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold text-dark-900 mb-2">Error</h3>
            <p className="text-dark-700 mb-6">{modalMessage}</p>
            <div className="flex justify-end">
              <button
                onClick={() => setShowErrorModal(false)}
                className="btn-primary"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
