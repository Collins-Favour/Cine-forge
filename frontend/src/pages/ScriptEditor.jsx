import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { 
  Save, Download, Share2, Sparkles, Eye, FileText, ChevronDown, Users, History, Clock, X,
  Undo, Redo, Search, Replace, Lock, Unlock, ZoomIn, ZoomOut, Moon, Sun,
  Copy, Printer, Settings, BookOpen, Film, MessageSquare, AlignLeft, Type, ArrowLeft
} from 'lucide-react'
import { scriptsApi } from '@services/apiServices'
import { SuccessModal, ErrorModal, PromptModal, ConfirmModal } from '@components/Modal'

export default function ScriptEditor() {
  const { id } = useParams()
  const navigate = useNavigate()
  const textareaRef = useRef(null)
  const [script, setScript] = useState('')
  const [scriptTitle, setScriptTitle] = useState('Untitled Script')
  const [project, setProject] = useState(null)
  const [versions, setVersions] = useState([])
  const [currentVersionId, setCurrentVersionId] = useState(null)
  const [currentVersionNumber, setCurrentVersionNumber] = useState(1)
  const [analyzing, setAnalyzing] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [analysis, setAnalysis] = useState(null)
  const [saving, setSaving] = useState(false)
  const [autoSaving, setAutoSaving] = useState(false)
  const [lastSaved, setLastSaved] = useState(null)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [loading, setLoading] = useState(true)
  const [characters, setCharacters] = useState([])
  const [showVersions, setShowVersions] = useState(false)
  const autoSaveTimerRef = useRef(null)
  
  // Professional features
  const [darkMode, setDarkMode] = useState(false)
  const [fontSize, setFontSize] = useState(12)
  const [isLocked, setIsLocked] = useState(false)
  const [showFind, setShowFind] = useState(false)
  const [findText, setFindText] = useState('')
  const [replaceText, setReplaceText] = useState('')
  const [cursorPosition, setCursorPosition] = useState({ line: 1, column: 1 })
  const undoStackRef = useRef([])
  const redoStackRef = useRef([])
  
  // Modal states
  const [showNewVersionModal, setShowNewVersionModal] = useState(false)
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [showErrorModal, setShowErrorModal] = useState(false)
  const [modalMessage, setModalMessage] = useState('')
  const [modalTitle, setModalTitle] = useState('')

  useEffect(() => {
    if (id) {
      fetchScriptData()
    }
  }, [id])

  // Auto-save functionality
  useEffect(() => {
    if (hasUnsavedChanges && script.trim()) {
      // Clear existing timer
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current)
      }
      
      // Set new timer for auto-save after 30 seconds of inactivity
      autoSaveTimerRef.current = setTimeout(() => {
        handleAutoSave()
      }, 30000)
    }

    return () => {
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current)
      }
    }
  }, [script, hasUnsavedChanges])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (isLocked && !(e.ctrlKey || e.metaKey)) return
      
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault()
        handleSave()
      }
      if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault()
        setShowFind(true)
      }
      if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
        e.preventDefault()
        handleUndo()
      }
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'z') {
        e.preventDefault()
        handleRedo()
      }
      // Formatting shortcuts
      if ((e.ctrlKey || e.metaKey) && ['1', '2', '3', '4', '5', '6'].includes(e.key)) {
        e.preventDefault()
        const formats = ['Scene Heading', 'Action', 'Character', 'Dialogue', 'Parenthetical', 'Transition']
        const index = parseInt(e.key) - 1
        applyFormatting(formats[index])
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [script, isLocked])

  const handleUndo = () => {
    if (undoStackRef.current.length > 1) {
      const currentState = undoStackRef.current.pop()
      redoStackRef.current.push(currentState)
      const previousState = undoStackRef.current[undoStackRef.current.length - 1]
      setScript(previousState)
      setHasUnsavedChanges(true)
    }
  }

  const handleRedo = () => {
    if (redoStackRef.current.length > 0) {
      const nextState = redoStackRef.current.pop()
      undoStackRef.current.push(nextState)
      setScript(nextState)
      setHasUnsavedChanges(true)
    }
  }

  const handleFindReplace = (replaceAll = false) => {
    if (!findText) return
    
    if (replaceAll) {
      const newScript = script.split(findText).join(replaceText)
      setScript(newScript)
      setHasUnsavedChanges(true)
      setModalTitle('Replace Complete')
      setModalMessage(`Replaced all occurrences of "${findText}"`)
      setShowSuccessModal(true)
    } else {
      const textarea = textareaRef.current
      const start = textarea.selectionStart
      const foundIndex = script.indexOf(findText, start)
      
      if (foundIndex !== -1) {
        textarea.focus()
        textarea.setSelectionRange(foundIndex, foundIndex + findText.length)
      } else {
        setModalTitle('Not Found')
        setModalMessage(`"${findText}" not found`)
        setShowErrorModal(true)
      }
    }
  }

  const fetchScriptData = async () => {
    setLoading(true)
    try {
      // Fetch project data first
      const { projectsApi } = await import('@services/apiServices')
      const projectResponse = await projectsApi.getProject(id)
      const projectData = projectResponse.data.project
      setProject(projectData)
      
      // Use project title as script title
      setScriptTitle(projectData.title || 'Untitled Script')
      
      // Fetch versions
      const versionsResponse = await scriptsApi.getScriptVersions(id)
      const versionsList = versionsResponse.data.versions || []
      setVersions(versionsList)

      // Load latest version if exists
      if (versionsList.length > 0) {
        const latest = versionsList[0]
        const contentResponse = await scriptsApi.getScriptVersion(id, latest.version_id, true)
        const versionData = contentResponse.data.version
        setScript(versionData.script_content || '')
        setCurrentVersionId(latest.version_id)
        setCurrentVersionNumber(latest.version_number)
        setLastSaved(versionData.saved_at ? new Date(versionData.saved_at) : null)
      }

      // Fetch characters
      const charactersResponse = await scriptsApi.getCharacters(id)
      setCharacters(charactersResponse.data.characters || [])
    } catch (err) {
      console.error('Error fetching script data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateScript = async () => {
    setGenerating(true)
    setModalTitle('Generating Script')
    setModalMessage('Please wait while AI generates your script from the project synopsis...')
    
    try {
      const { projectsApi } = await import('@services/apiServices')
      const response = await projectsApi.generateContent(id)
      
      if (response.data) {
        setModalTitle('Success!')
        setModalMessage(`Generated ${response.data.scenes_created || 0} scenes with script and storyboard panels!`)
        setShowSuccessModal(true)
        
        // Reload script data
        await fetchScriptData()
      }
    } catch (err) {
      console.error('Error generating script:', err)
      setModalTitle('Generation Failed')
      setModalMessage(err.response?.data?.error || 'Failed to generate script. Make sure your project has a synopsis.')
      setShowErrorModal(true)
    } finally {
      setGenerating(false)
    }
  }

  const loadVersion = async (versionId) => {
    try {
      const response = await scriptsApi.getScriptVersion(id, versionId, true)
      const versionData = response.data.version
      setScript(versionData.script_content || '')
      // Keep using project title, don't override with version name
      setCurrentVersionId(versionData.version_id)
      setCurrentVersionNumber(versionData.version_number)
      setLastSaved(versionData.saved_at ? new Date(versionData.saved_at) : null)
      setHasUnsavedChanges(false)
      setShowVersions(false)
    } catch (err) {
      console.error('Error loading version:', err)
      setModalTitle('Error Loading Version')
      setModalMessage('Failed to load script version. Please try again.')
      setShowErrorModal(true)
    }
  }

  const handleAnalyze = async () => {
    if (!script.trim()) {
      setModalTitle('No Content')
      setModalMessage('Please write some script content before analyzing.')
      setShowErrorModal(true)
      return
    }

    // Save current version first if there are unsaved changes
    if (hasUnsavedChanges) {
      await handleSave()
    }

    if (!currentVersionId) {
      setModalTitle('Save Required')
      setModalMessage('Please save the script before analyzing.')
      setShowErrorModal(true)
      return
    }
    
    setAnalyzing(true)
    try {
      const response = await scriptsApi.analyzeScript(id, currentVersionId)
      const analysisData = response.data.analysis
      
      // Transform backend analysis format to frontend format
      setAnalysis({
        synopsis: analysisData.synopsis || '',
        characters: analysisData.characters?.map(c => c.name || c) || [],
        locations: analysisData.scenes?.map(s => s.location || s).filter((v, i, a) => a.indexOf(v) === i) || [],
        scenes: analysisData.scenes?.length || 0,
        estimatedDuration: `${Math.ceil((analysisData.scenes?.length || 5) * 2)}-${Math.ceil((analysisData.scenes?.length || 5) * 2.5)} minutes`,
        themes: analysisData.themes?.join(', ') || 'Not analyzed',
        tone: analysisData.tone || 'Not analyzed',
        mood: analysisData.pacing || 'Moderate',
        pacing: analysisData.pacing || 'Moderate'
      })

      // Update characters list if new characters found
      if (analysisData.characters && Array.isArray(analysisData.characters)) {
        const newCharacters = analysisData.characters.filter(c => 
          typeof c === 'object' && c.name && !characters.some(existing => existing.character_name === c.name)
        )
        
        // Create new character entries
        for (const char of newCharacters) {
          try {
            await scriptsApi.createCharacter(id, {
              character_name: char.name,
              description: char.description || '',
              role_type: char.role || 'supporting'
            })
          } catch (err) {
            console.error('Error creating character:', err)
          }
        }
        
        // Refresh characters list
        const charactersResponse = await scriptsApi.getCharacters(id)
        setCharacters(charactersResponse.data.characters || [])
      }
    } catch (err) {
      console.error('Error analyzing script:', err)
      // Fallback to basic analysis
      const lines = script.split('\n').filter(l => l.trim())
      const sceneHeadings = lines.filter(l => l.match(/^(INT\.|EXT\.)/))
      const characterNames = [...new Set(lines.filter(l => l === l.toUpperCase() && l.length > 2 && l.length < 30))]
      
      setAnalysis({
        synopsis: 'AI analysis unavailable. Basic analysis shown.',
        characters: characterNames.slice(0, 10),
        locations: sceneHeadings.map(h => h.split('-')[0].trim()).slice(0, 10),
        scenes: sceneHeadings.length,
        estimatedDuration: `${Math.ceil(sceneHeadings.length * 2)}-${Math.ceil(sceneHeadings.length * 2.5)} minutes`,
        themes: 'AI analysis unavailable',
        tone: 'Unable to determine',
        mood: 'Unable to determine',
        pacing: 'Unable to determine'
      })
    } finally {
      setAnalyzing(false)
    }
  }

  const handleSave = async () => {
    if (!id || !script.trim()) return
    
    setSaving(true)
    try {
      const wordCount = script.split(/\s+/).filter(w => w).length
      const pageCount = Math.ceil(script.split('\n').length / 55)
      
      if (currentVersionId) {
        // Update existing version
        await scriptsApi.updateScriptVersion(id, currentVersionId, {
          script_content: script,
          version_name: scriptTitle
        })
      } else {
        // Create new version
        const response = await scriptsApi.createScriptVersion(id, {
          script_content: script,
          version_name: scriptTitle
        })
        
        setCurrentVersionId(response.data.version.version_id)
        setCurrentVersionNumber(response.data.version.version_number)
      }
      
      setLastSaved(new Date())
      setHasUnsavedChanges(false)
      
      // Show success message
      setModalTitle('Saved Successfully')
      setModalMessage('Your script has been saved.')
      setShowSuccessModal(true)
      
      // Refresh versions list
      const versionsResponse = await scriptsApi.getScriptVersions(id)
      setVersions(versionsResponse.data.versions || [])
    } catch (err) {
      console.error('Error saving script:', err)
      setModalTitle('Save Failed')
      setModalMessage('Failed to save script. Please try again.')
      setShowErrorModal(true)
    } finally {
      setSaving(false)
    }
  }

  const handleAutoSave = async () => {
    if (!id || !script.trim() || !hasUnsavedChanges) return
    
    setAutoSaving(true)
    try {
      const wordCount = script.split(/\s+/).filter(w => w).length
      const pageCount = Math.ceil(script.split('\n').length / 55)
      
      if (currentVersionId) {
        await scriptsApi.updateScriptVersion(id, currentVersionId, {
          script_content: script,
          version_name: scriptTitle
        })
        setLastSaved(new Date())
        setHasUnsavedChanges(false)
      }
    } catch (err) {
      console.error('Auto-save failed:', err)
    } finally {
      setAutoSaving(false)
    }
  }

  const handleScriptChange = (e) => {
    const newScript = e.target.value
    const textarea = e.target
    
    // Add to undo stack
    if (undoStackRef.current.length === 0 || undoStackRef.current[undoStackRef.current.length - 1] !== script) {
      undoStackRef.current.push(script)
      if (undoStackRef.current.length > 50) {
        undoStackRef.current.shift()
      }
    }
    redoStackRef.current = []
    
    // Update cursor position
    const textBeforeCursor = newScript.substring(0, textarea.selectionStart)
    const lines = textBeforeCursor.split('\n')
    setCursorPosition({
      line: lines.length,
      column: lines[lines.length - 1].length + 1
    })
    
    setScript(newScript)
    setHasUnsavedChanges(true)
  }

  const handleNewVersion = async () => {
    if (!script.trim()) {
      setModalTitle('Empty Script')
      setModalMessage('Cannot create a new version from empty script.')
      setShowErrorModal(true)
      return
    }

    setShowNewVersionModal(true)
  }

  const handleCreateVersion = async (versionName) => {
    setSaving(true)
    try {
      const response = await scriptsApi.createScriptVersion(id, {
        script_content: script,
        version_name: versionName
      })
      
      setCurrentVersionId(response.data.version.version_id)
      setCurrentVersionNumber(response.data.version.version_number)
      setScriptTitle(versionName)
      setLastSaved(new Date())
      setHasUnsavedChanges(false)
      
      // Refresh versions list
      const versionsResponse = await scriptsApi.getScriptVersions(id)
      setVersions(versionsResponse.data.versions || [])
      
      setModalTitle('Version Created')
      setModalMessage(`Version "${versionName}" created successfully!`)
      setShowSuccessModal(true)
    } catch (err) {
      console.error('Error creating version:', err)
      setModalTitle('Error Creating Version')
      setModalMessage('Failed to create new version. Please try again.')
      setShowErrorModal(true)
    } finally {
      setSaving(false)
    }
  }

  const applyFormatting = (formatType) => {
    const textarea = textareaRef.current
    if (!textarea) return

    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const selectedText = script.substring(start, end)
    let formattedText = selectedText

    switch (formatType) {
      case 'Scene Heading':
        formattedText = `INT. ${selectedText.toUpperCase() || 'LOCATION'} - DAY\n`
        break
      case 'Action':
        formattedText = `\n${selectedText}\n`
        break
      case 'Character':
        formattedText = `\n${selectedText.toUpperCase()}\n`
        break
      case 'Dialogue':
        formattedText = selectedText
        break
      case 'Parenthetical':
        formattedText = `(${selectedText})`
        break
      case 'Transition':
        formattedText = `${selectedText.toUpperCase()}:\n`
        break
    }

    const newScript = script.substring(0, start) + formattedText + script.substring(end)
    setScript(newScript)
    setHasUnsavedChanges(true)

    // Restore cursor position
    setTimeout(() => {
      textarea.focus()
      textarea.setSelectionRange(start + formattedText.length, start + formattedText.length)
    }, 0)
  }

  const handleExport = () => {
    const element = document.createElement('a')
    const file = new Blob([script], { type: 'text/plain' })
    element.href = URL.createObjectURL(file)
    element.download = `${scriptTitle}.txt`
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  const formatButtons = [
    { label: 'Scene Heading', hotkey: 'Ctrl+1' },
    { label: 'Action', hotkey: 'Ctrl+2' },
    { label: 'Character', hotkey: 'Ctrl+3' },
    { label: 'Dialogue', hotkey: 'Ctrl+4' },
    { label: 'Parenthetical', hotkey: 'Ctrl+5' },
    { label: 'Transition', hotkey: 'Ctrl+6' },
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-display font-bold text-dark-900 mb-2">Script Editor</h1>
          <p className="text-dark-600">Write and analyze your screenplay with AI assistance</p>
          {hasUnsavedChanges && (
            <p className="text-sm text-orange-600 mt-1 flex items-center gap-1">
              <Clock className="w-4 h-4" />
              Unsaved changes{autoSaving && ' - Auto-saving...'}
            </p>
          )}
        </div>
        <div className="flex flex-wrap gap-2">
          <button 
            onClick={handleNewVersion}
            className="btn-secondary flex items-center gap-2"
            disabled={saving}
          >
            <History className="w-5 h-5" />
            <span>New Version</span>
          </button>
          <button 
            onClick={handleExport}
            className="btn-secondary flex items-center gap-2"
          >
            <Download className="w-5 h-5" />
            <span>Export</span>
          </button>
          <button 
            onClick={handleSave}
            disabled={saving || !hasUnsavedChanges}
            className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Save className="w-5 h-5" />
            <span>{saving ? 'Saving...' : autoSaving ? 'Auto-saving...' : 'Save'}</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Editor */}
        <div className="lg:col-span-2 space-y-4">
          {/* Professional Toolbar */}
          <div className="card">
            <div className="space-y-3">
              {/* Top Controls Row */}
              <div className="flex items-center justify-between gap-4 pb-3 border-b border-dark-200">
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleUndo}
                    disabled={undoStackRef.current.length <= 1}
                    className="p-2 rounded hover:bg-dark-100 disabled:opacity-30 disabled:cursor-not-allowed"
                    title="Undo (Ctrl+Z)"
                  >
                    <Undo className="w-4 h-4" />
                  </button>
                  <button
                    onClick={handleRedo}
                    disabled={redoStackRef.current.length === 0}
                    className="p-2 rounded hover:bg-dark-100 disabled:opacity-30 disabled:cursor-not-allowed"
                    title="Redo (Ctrl+Shift+Z)"
                  >
                    <Redo className="w-4 h-4" />
                  </button>
                  <div className="w-px h-6 bg-dark-200 mx-1"></div>
                  <button
                    onClick={() => setShowFind(!showFind)}
                    className={`p-2 rounded hover:bg-dark-100 ${showFind ? 'bg-primary-100 text-primary-700' : ''}`}
                    title="Find & Replace (Ctrl+F)"
                  >
                    <Search className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setIsLocked(!isLocked)}
                    className="p-2 rounded hover:bg-dark-100"
                    title={isLocked ? 'Unlock Editing' : 'Lock Editing'}
                  >
                    {isLocked ? <Lock className="w-4 h-4 text-red-600" /> : <Unlock className="w-4 h-4" />}
                  </button>
                  <div className="w-px h-6 bg-dark-200 mx-1"></div>
                  <button
                    onClick={() => setFontSize(Math.max(10, fontSize - 1))}
                    className="p-2 rounded hover:bg-dark-100"
                    title="Decrease Font Size"
                  >
                    <ZoomOut className="w-4 h-4" />
                  </button>
                  <span className="text-sm font-mono text-dark-600 min-w-[3rem] text-center">{fontSize}pt</span>
                  <button
                    onClick={() => setFontSize(Math.min(18, fontSize + 1))}
                    className="p-2 rounded hover:bg-dark-100"
                    title="Increase Font Size"
                  >
                    <ZoomIn className="w-4 h-4" />
                  </button>
                  <div className="w-px h-6 bg-dark-200 mx-1"></div>
                  <button
                    onClick={() => setDarkMode(!darkMode)}
                    className="p-2 rounded hover:bg-dark-100"
                    title="Toggle Dark Mode"
                  >
                    {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
                  </button>
                </div>
                <div className="text-xs text-dark-600 font-mono">
                  Line {cursorPosition.line}, Col {cursorPosition.column}
                </div>
              </div>

              {/* Formatting Buttons Row */}
              <div className="flex items-center gap-2 flex-wrap">
                <button
                  onClick={() => navigate(`/projects/${id}`)}
                  className="btn-secondary flex items-center gap-2 px-3 py-1.5"
                  title="Back to Project"
                >
                  <ArrowLeft className="w-4 h-4" />
                </button>
                <span className="text-sm font-medium text-dark-700">Format:</span>
                {formatButtons.map((btn) => (
                  <button
                    key={btn.label}
                    onClick={() => applyFormatting(btn.label)}
                    disabled={isLocked}
                    className="px-3 py-1.5 text-sm rounded-lg bg-dark-100 hover:bg-primary-100 hover:text-primary-700 text-dark-700 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                    title={btn.hotkey}
                  >
                    {btn.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Find & Replace Bar */}
          {showFind && (
            <div className="card">
              <div className="space-y-2">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-semibold text-dark-900">Find & Replace</h4>
                  <button
                    onClick={() => setShowFind(false)}
                    className="p-1 rounded hover:bg-dark-100"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={findText}
                    onChange={(e) => setFindText(e.target.value)}
                    placeholder="Find..."
                    className="input flex-1 text-sm"
                  />
                  <button
                    onClick={() => handleFindReplace(false)}
                    className="btn-secondary text-sm px-3"
                    disabled={!findText}
                  >
                    Find Next
                  </button>
                </div>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={replaceText}
                    onChange={(e) => setReplaceText(e.target.value)}
                    placeholder="Replace with..."
                    className="input flex-1 text-sm"
                  />
                  <button
                    onClick={() => handleFindReplace(true)}
                    className="btn-primary text-sm px-3"
                    disabled={!findText}
                  >
                    Replace All
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Script Editor */}
          <div className="card min-h-[600px]">
            <textarea
              ref={textareaRef}
              value={script}
              onChange={handleScriptChange}
              disabled={isLocked}
              placeholder="INT. COFFEE SHOP - DAY\n\nJOHN sits at a corner table, nervously checking his watch. SARAH enters, scanning the room.\n\nSARAH\n(spotting him)\nSorry I'm late.\n\nJOHN\n(standing)\nNo worries. I ordered you a coffee.\n\nThey sit. An awkward silence.\n\nSARAH\nSo... about last night.\n\nJohn shifts uncomfortably.\n\nJOHN\nI think we need to talk."
              className={`w-full h-[550px] p-6 border rounded-lg font-mono resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 transition-colors ${
                darkMode 
                  ? 'bg-gray-900 text-gray-100 border-gray-700' 
                  : 'bg-white text-dark-900 border-dark-200'
              } ${isLocked ? 'cursor-not-allowed opacity-70' : ''}`}
              style={{ 
                fontFamily: 'Courier New, monospace', 
                lineHeight: '1.8',
                fontSize: `${fontSize}pt`
              }}
            />
          </div>

          {/* AI Generation Button */}
          {(!script || script.trim().length === 0) && (
            <button
              onClick={handleGenerateScript}
              disabled={generating || analyzing}
              className="btn-secondary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed mb-4"
            >
              <Sparkles className={`w-5 h-5 ${generating ? 'animate-spin' : ''}`} />
              <span>{generating ? 'Generating...' : 'Generate Script with AI'}</span>
            </button>
          )}

          {/* AI Analysis Button */}
          <button
            onClick={handleAnalyze}
            disabled={analyzing || !script.trim()}
            className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Sparkles className={`w-5 h-5 ${analyzing ? 'animate-spin' : ''}`} />
            <span>{analyzing ? 'Analyzing...' : 'Analyze Script with AI'}</span>
          </button>
        </div>

        {/* Sidebar - Analysis & Tools */}
        <div className="space-y-6">
          {/* Script Info */}
          <div className="card">
            <h3 className="text-lg font-semibold text-dark-900 mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-primary-600" />
              Script Info
            </h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-dark-700 mb-1">Title</label>
                <input
                  type="text"
                  value={scriptTitle}
                  disabled
                  className="input w-full bg-gray-50 cursor-not-allowed"
                  title="Script title is derived from project title"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-dark-700 mb-1">Version</label>
                <div className="relative">
                  <button
                    onClick={() => setShowVersions(!showVersions)}
                    className="w-full input flex items-center justify-between"
                  >
                    <span>Version {currentVersionNumber}</span>
                    <ChevronDown className={`w-4 h-4 transition-transform ${showVersions ? 'rotate-180' : ''}`} />
                  </button>
                  {showVersions && versions.length > 0 && (
                    <div className="absolute z-10 w-full mt-1 bg-white border border-dark-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                      {versions.map((version) => (
                        <button
                          key={version.version_id}
                          onClick={() => loadVersion(version.version_id)}
                          className={`w-full text-left px-4 py-3 hover:bg-dark-50 transition-colors border-b border-dark-100 last:border-b-0 ${
                            version.version_id === currentVersionId ? 'bg-primary-50 text-primary-700' : ''
                          }`}
                        >
                          <div className="font-medium text-sm">{version.version_name || `Version ${version.version_number}`}</div>
                          <div className="text-xs text-dark-500 mt-1">
                            {new Date(version.saved_at).toLocaleString()} • {version.word_count} words
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Characters */}
          {characters.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold text-dark-900 mb-4 flex items-center gap-2">
                <Users className="w-5 h-5 text-primary-600" />
                Characters ({characters.length})
              </h3>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {characters.map((char) => (
                  <div key={char.character_id} className="p-3 bg-dark-50 rounded-lg">
                    <div className="font-medium text-dark-900 text-sm">{char.character_name}</div>
                    {char.description && (
                      <div className="text-xs text-dark-600 mt-1">{char.description}</div>
                    )}
                    <div className="flex items-center gap-2 mt-2">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        char.role_type === 'protagonist' ? 'bg-primary-100 text-primary-700' :
                        char.role_type === 'antagonist' ? 'bg-red-100 text-red-700' :
                        'bg-dark-200 text-dark-700'
                      }`}>
                        {char.role_type}
                      </span>
                      {char.dialogue_count > 0 && (
                        <span className="text-xs text-dark-500">{char.dialogue_count} lines</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI Analysis Results */}
          {analysis && (
            <div className="card bg-gradient-to-br from-primary-50 to-primary-100 border-primary-200">
              <h3 className="text-lg font-semibold text-dark-900 mb-4 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-primary-600" />
                AI Analysis
              </h3>
              <div className="space-y-4">
                {analysis.synopsis && (
                  <div>
                    <div className="text-sm font-medium text-dark-700 mb-1">Synopsis</div>
                    <div className="text-sm text-dark-800 bg-white p-3 rounded-lg">{analysis.synopsis}</div>
                  </div>
                )}

                <div>
                  <div className="text-sm font-medium text-dark-700 mb-2">Characters Detected</div>
                  <div className="flex flex-wrap gap-2">
                    {analysis.characters.slice(0, 10).map((char, idx) => (
                      <span key={idx} className="px-3 py-1 bg-white rounded-full text-sm text-dark-700">
                        {typeof char === 'object' ? char.name : char}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <div className="text-sm font-medium text-dark-700 mb-2">Locations</div>
                  <div className="flex flex-wrap gap-2">
                    {analysis.locations.slice(0, 8).map((loc, idx) => (
                      <span key={idx} className="px-3 py-1 bg-white rounded-full text-sm text-dark-700">
                        {loc}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm font-medium text-dark-700">Scenes</div>
                    <div className="text-2xl font-bold text-primary-600">{analysis.scenes}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-dark-700">Duration</div>
                    <div className="text-sm font-semibold text-dark-900">{analysis.estimatedDuration}</div>
                  </div>
                </div>

                {analysis.themes && (
                  <div>
                    <div className="text-sm font-medium text-dark-700 mb-1">Themes</div>
                    <div className="text-sm text-dark-800 bg-white p-2 rounded">{analysis.themes}</div>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm font-medium text-dark-700 mb-1">Tone</div>
                    <div className="text-sm text-dark-800">{analysis.tone}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-dark-700 mb-1">Pacing</div>
                    <div className="text-sm text-dark-800">{analysis.pacing}</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Quick Actions */}
          <div className="card">
            <h3 className="text-lg font-semibold text-dark-900 mb-4">Quick Actions</h3>
            <div className="space-y-2">
              <button 
                onClick={() => navigate(`/projects/${id}/storyboard`)}
                className="w-full text-left px-4 py-3 rounded-lg bg-dark-100 hover:bg-primary-50 hover:border-primary-200 transition-colors border border-transparent"
              >
                <div className="font-medium text-dark-900">Open Storyboard</div>
                <div className="text-sm text-dark-600">Create visuals from script</div>
              </button>
              <button 
                onClick={() => navigate(`/projects/${id}`)}
                className="w-full text-left px-4 py-3 rounded-lg bg-dark-100 hover:bg-primary-50 hover:border-primary-200 transition-colors border border-transparent"
              >
                <div className="font-medium text-dark-900">Project Details</div>
                <div className="text-sm text-dark-600">View team and activity</div>
              </button>
              <button 
                onClick={handleExport}
                className="w-full text-left px-4 py-3 rounded-lg bg-dark-100 hover:bg-primary-50 hover:border-primary-200 transition-colors border border-transparent"
              >
                <div className="font-medium text-dark-900">Export Script</div>
                <div className="text-sm text-dark-600">Download as text file</div>
              </button>
            </div>
          </div>

          {/* Script Stats */}
          <div className="card">
            <h3 className="text-lg font-semibold text-dark-900 mb-4">Statistics</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-dark-600">Words</span>
                <span className="font-semibold text-dark-900">{script.split(/\s+/).filter(w => w).length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-dark-600">Characters</span>
                <span className="font-semibold text-dark-900">{script.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-dark-600">Pages</span>
                <span className="font-semibold text-dark-900">{Math.ceil(script.split('\n').length / 55)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-dark-600">Last Saved</span>
                <span className="font-semibold text-dark-900">
                  {lastSaved ? lastSaved.toLocaleTimeString() : 'Not saved'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Modals */}
      <PromptModal
        isOpen={showNewVersionModal}
        onClose={() => setShowNewVersionModal(false)}
        onSubmit={handleCreateVersion}
        title="Create New Version"
        message="Enter a name for this new version:"
        placeholder={`Version ${currentVersionNumber + 1}`}
        defaultValue={`Version ${currentVersionNumber + 1}`}
        submitText="Create"
      />

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
  )
}
