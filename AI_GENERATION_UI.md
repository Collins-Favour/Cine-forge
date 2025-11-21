# AI Generation UI - Manual Trigger Buttons

## Overview
Added manual "Generate with AI" buttons to both Scripts and Storyboards pages, allowing users to trigger AI content generation using project synopsis.

## Changes Made

### 1. ScriptEditor.jsx
**Location**: `frontend/src/pages/ScriptEditor.jsx`

**New Function** (added after `fetchScriptData`):
```javascript
const handleGenerateScript = async () => {
  try {
    setAnalyzing(true)
    const response = await projectsApi.generateContent(id)
    
    setModalMessage(`Script generated successfully! Created ${response.data.scenes_created} scenes.`)
    setShowSuccessModal(true)
    
    // Reload script data
    await fetchScriptData()
  } catch (err) {
    console.error('Error generating script:', err)
    const errorMsg = err.response?.data?.error || 'Failed to generate script'
    setModalMessage(errorMsg)
    setShowErrorModal(true)
  } finally {
    setAnalyzing(false)
  }
}
```

**UI Button** (added before "Analyze Script with AI" button):
- Only shows when script is empty
- Disabled during generation
- Shows "Generating..." state with spinning Sparkles icon
- Uses `btn-secondary` styling

### 2. Storyboard.jsx
**Location**: `frontend/src/pages/Storyboard.jsx`

**Import Added**:
```javascript
import { storyboardsApi, projectsApi } from '@services/apiServices'
```

**New State**:
```javascript
const [generating, setGenerating] = useState(false)
```

**New Function** (added after `fetchStoryboard`):
```javascript
const handleGenerateStoryboard = async () => {
  try {
    setGenerating(true)
    setModalMessage('Generating storyboard with AI...')
    setShowErrorModal(true)
    
    const response = await projectsApi.generateContent(id)
    
    setModalMessage(`Storyboard generated successfully! Created ${response.data.panels_created} panels.`)
    setShowErrorModal(true)
    
    await fetchStoryboard()
  } catch (err) {
    console.error('Error generating storyboard:', err)
    const errorMsg = err.response?.data?.error || 'Failed to generate storyboard'
    setModalMessage(errorMsg)
    setShowErrorModal(true)
  } finally {
    setGenerating(false)
  }
}
```

**UI Button** (added next to "Add Panel" button):
- Only shows when panels array is empty
- Disabled during generation
- Shows "Generating..." state with spinning Sparkles icon
- Uses `btn-secondary` styling

## User Flow

### Script Generation
1. User creates a project with synopsis/title
2. User navigates to Scripts page
3. If script is empty, "Generate Script with AI" button appears
4. User clicks button
5. Backend calls Groq AI to analyze synopsis
6. Script content and scenes are created
7. Success modal shows number of scenes created
8. Script data reloads automatically

### Storyboard Generation
1. User creates a project with synopsis/title (and optionally generates script first)
2. User navigates to Storyboards page
3. If no panels exist, "Generate with AI" button appears
4. User clicks button
5. Backend generates script (if not exists), then calls Gemini AI for prompts
6. Storyboard panels are created
7. Success modal shows number of panels created
8. Storyboard data reloads automatically

## Backend Endpoint
Both buttons call the same endpoint:
```
POST /api/projects/<project_id>/generate-content
```

**Requirements**:
- User must have 'writer' or 'owner' permission on project
- Project must have synopsis or logline

**Response**:
```json
{
  "message": "Content generated successfully",
  "script_version_id": 123,
  "scenes_created": 5,
  "panels_created": 15
}
```

## Error Handling
Both implementations handle:
- Missing synopsis (shows user-friendly error message)
- API failures (displays error from backend)
- Network issues (generic failure message)
- Loading states (disabled buttons during generation)

## Testing Steps
1. Start backend: `cd backend && python app.py`
2. Start frontend: `cd frontend && npm run dev`
3. Create a new project with synopsis
4. Navigate to Scripts → click "Generate Script with AI"
5. Wait for generation to complete
6. Navigate to Storyboards → click "Generate with AI"
7. Verify panels are created

## Notes
- Buttons only appear when content is empty (non-intrusive)
- Generation uses same backend logic as automatic generation
- Loading states prevent duplicate requests
- Success modals provide feedback with counts
- Errors are displayed in user-friendly format
