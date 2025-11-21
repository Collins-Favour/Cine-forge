import api from './api'

// Project APIs
export const projectsApi = {
        // Get all projects for current user
        getProjects: (params = {}) => {
                const queryParams = new URLSearchParams(params).toString()
                return api.get(`/projects${queryParams ? `?${queryParams}` : ''}`)
  },

  // Get single project by ID
  getProject: (projectId) => {
    return api.get(`/projects/${projectId}`)
  },

  // Create new project
  createProject: (data) => {
    return api.post('/projects', data)
  },

  // Update project
  updateProject: (projectId, data) => {
    return api.put(`/projects/${projectId}`, data)
  },

  // Delete project
  deleteProject: (projectId) => {
    return api.delete(`/projects/${projectId}`)
  },

  // Get project collaborators
  getCollaborators: (projectId) => {
    return api.get(`/projects/${projectId}/collaborators`)
  },

  // Add collaborator
  addCollaborator: (projectId, data) => {
    return api.post(`/projects/${projectId}/collaborators`, data)
  },

  // Remove collaborator
  removeCollaborator: (projectId, collaborationId) => {
    return api.delete(`/projects/${projectId}/collaborators/${collaborationId}`)
  },

  // Update collaborator (role, permissions)
  updateCollaborator: (projectId, collaborationId, data) => {
    return api.patch(`/projects/${projectId}/collaborators/${collaborationId}`, data)
  },

  // Generate AI content (script and storyboard) from project synopsis
  generateContent: (projectId) => {
    return api.post(`/projects/${projectId}/generate-content`)
  },

  // Transfer ownership to a collaborator
  transferOwner: (projectId, collaborationId) => {
    return api.post(`/projects/${projectId}/transfer-owner`, { collaboration_id: collaborationId })
  },

  // Get project activity
  getActivity: (projectId, params = {}) => {
    const queryParams = new URLSearchParams(params).toString()
    return api.get(`/projects/${projectId}/activity${queryParams ? `?${queryParams}` : ''}`)
  },
}

// Script APIs
export const scriptsApi = {
  // Get script versions for project
  getScriptVersions: (projectId) => {
    return api.get(`/scripts/project/${projectId}/versions`)
  },

  // Get specific script version
  getScriptVersion: (projectId, versionId, includeContent = false) => {
    return api.get(`/scripts/project/${projectId}/versions/${versionId}`)
  },

  // Create new script version
  createScriptVersion: (projectId, data) => {
    return api.post(`/scripts/project/${projectId}/versions`, data)
  },

  // Update script version
  updateScriptVersion: (projectId, versionId, data) => {
    return api.put(`/scripts/project/${projectId}/versions/${versionId}`, data)
  },

  // Analyze script with AI
  analyzeScript: (projectId, versionId) => {
    return api.post(`/scripts/project/${projectId}/versions/${versionId}/analyze`)
  },

  // Get characters for project
  getCharacters: (projectId) => {
    return api.get(`/scripts/project/${projectId}/characters`)
  },

  // Create character
  createCharacter: (projectId, data) => {
    return api.post(`/scripts/project/${projectId}/characters`, data)
  },

  // Update character
  updateCharacter: (projectId, characterId, data) => {
    return api.put(`/scripts/project/${projectId}/characters/${characterId}`, data)
  },

  // Delete character
  deleteCharacter: (projectId, characterId) => {
    return api.delete(`/scripts/project/${projectId}/characters/${characterId}`)
  },
}

// Scenes APIs
export const scenesApi = {
  // Get all scenes for a project
  getScenes: (projectId) => {
    return api.get(`/scenes/project/${projectId}/scenes`)
  },

  // Get specific scene
  getScene: (projectId, sceneId) => {
    return api.get(`/scenes/project/${projectId}/scenes/${sceneId}`)
  },

  // Create new scene
  createScene: (projectId, data) => {
    return api.post(`/scenes/project/${projectId}/scenes`, data)
  },

  // Update scene
  updateScene: (projectId, sceneId, data) => {
    return api.put(`/scenes/project/${projectId}/scenes/${sceneId}`, data)
  },

  // Delete scene
  deleteScene: (projectId, sceneId) => {
    return api.delete(`/scenes/project/${projectId}/scenes/${sceneId}`)
  },

  // Analyze scene with AI
  analyzeScene: (projectId, sceneId) => {
    return api.post(`/scenes/project/${projectId}/scenes/${sceneId}/analyze`)
  },

  // Add character to scene
  addCharacterToScene: (projectId, sceneId, data) => {
    return api.post(`/scenes/project/${projectId}/scenes/${sceneId}/characters`, data)
  },

  // Remove character from scene
  removeCharacterFromScene: (projectId, sceneId, sceneCharacterId) => {
    return api.delete(`/scenes/project/${projectId}/scenes/${sceneId}/characters/${sceneCharacterId}`)
  },
}

// Storyboard APIs
export const storyboardsApi = {
  // Get storyboards for project
  getStoryboards: (projectId) => {
    return api.get(`/storyboards/project/${projectId}`)
  },

  // Get single storyboard
  getStoryboard: (storyboardId) => {
    return api.get(`/storyboards/${storyboardId}`)
  },

  // Create storyboard
  createStoryboard: (data) => {
    return api.post('/storyboards', data)
  },

  // Update storyboard
  updateStoryboard: (storyboardId, data) => {
    return api.put(`/storyboards/${storyboardId}`, data)
  },

  // Get panels for storyboard
  getPanels: (storyboardId) => {
    return api.get(`/storyboards/${storyboardId}/panels`)
  },

  // Create panel
  createPanel: (data) => {
    return api.post('/storyboards/panels', data)
  },

  // Update panel
  updatePanel: (panelId, data) => {
    return api.put(`/storyboards/panels/${panelId}`, data)
  },

  // Delete panel
  deletePanel: (panelId) => {
    return api.delete(`/storyboards/panels/${panelId}`)
  },

  // Generate panel image with AI
  generatePanelImage: (panelId, data) => {
    return api.post(`/storyboards/panels/${panelId}/generate`, data)
  },
}

// C-Space (Collaboration) APIs
export const cspaceApi = {
  // Get messages for project
  getMessages: (projectId, params = {}) => {
    const queryParams = new URLSearchParams(params).toString()
    return api.get(`/collaboration/project/${projectId}/messages${queryParams ? `?${queryParams}` : ''}`)
  },

  // Send message
  sendMessage: (projectId, data) => {
    return api.post(`/collaboration/project/${projectId}/messages`, data)
  },

  // Edit message
  updateMessage: (messageId, data) => {
    return api.put(`/collaboration/messages/${messageId}`, data)
  },

  // Delete message
  deleteMessage: (messageId) => {
    return api.delete(`/collaboration/messages/${messageId}`)
  },

  // Add reaction to message
  addReaction: (messageId, data) => {
    return api.post(`/collaboration/messages/${messageId}/reactions`, data)
  },

  // Remove reaction
  removeReaction: (messageId, reactionId) => {
    return api.delete(`/collaboration/messages/${messageId}/reactions/${reactionId}`)
  },

  // Upload file
  uploadFile: (projectId, formData) => {
    return api.post(`/collaboration/upload/${projectId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
}

// User APIs
export const usersApi = {
  // Get current user profile
  getProfile: () => {
    return api.get('/users/profile')
  },

  // Update user profile
  updateProfile: (data) => {
    return api.put('/users/profile', data)
  },

  // Change password
  changePassword: (data) => {
    return api.post('/users/change-password', data)
  },

  // Update notification settings
  updateNotifications: (data) => {
    return api.put('/users/notifications', data)
  },

  // Upload avatar
  uploadAvatar: (formData) => {
    return api.post('/users/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
}

// Admin APIs
export const adminApi = {
  // Dashboard
  getDashboard: () => {
    return api.get('/admin/dashboard')
  },

  // User Management
  getUsers: (params = {}) => {
    const queryParams = new URLSearchParams(params).toString()
    return api.get(`/admin/users${queryParams ? `?${queryParams}` : ''}`)
  },

  getUserDetails: (userId) => {
    return api.get(`/admin/users/${userId}`)
  },

  updateUser: (userId, data) => {
    return api.put(`/admin/users/${userId}`, data)
  },

  deleteUser: (userId) => {
    return api.delete(`/admin/users/${userId}`)
  },

  resetUserPassword: (userId, newPassword) => {
    return api.post(`/admin/users/${userId}/reset-password`, { new_password: newPassword })
  },

  // Project Management
  getAllProjects: (params = {}) => {
    const queryParams = new URLSearchParams(params).toString()
    return api.get(`/admin/projects${queryParams ? `?${queryParams}` : ''}`)
  },

  deleteProject: (projectId) => {
    return api.delete(`/admin/projects/${projectId}`)
  },

  // Analytics
  getAnalytics: (days = 30) => {
    return api.get(`/admin/analytics?days=${days}`)
  },

  getStatsOverview: () => {
    return api.get('/admin/stats/overview')
  },

  // Security Logs
  getSecurityLogs: (params = {}) => {
    const queryParams = new URLSearchParams(params).toString()
    return api.get(`/admin/security/logs${queryParams ? `?${queryParams}` : ''}`)
  },

  // Settings
  getSettings: () => {
    return api.get('/admin/settings')
  },

  updateSettings: (data) => {
    return api.put('/admin/settings', data)
  },
}

// Export all
export default {
  projects: projectsApi,
  scripts: scriptsApi,
  scenes: scenesApi,
  storyboards: storyboardsApi,
  cspace: cspaceApi,
  users: usersApi,
  admin: adminApi,
}