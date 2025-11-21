import api from './api'

export const authService = {
  register: async (userData) => {
    const response = await api.post('/auth/register', userData)
    return response.data
  },

  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials)
    return response.data
  },

  logout: async () => {
    const response = await api.post('/auth/logout')
    return response.data
  },

  refreshToken: async () => {
    const response = await api.post('/auth/refresh')
    return response.data
  },

  forgotPassword: async (email) => {
    const response = await api.post('/auth/forgot-password', { email })
    return response.data
  },

  resetPassword: async (token, password) => {
    const response = await api.post('/auth/reset-password', { token, password })
    return response.data
  },

  verifyEmail: async (token) => {
    const response = await api.post('/auth/verify-email', { token })
    return response.data
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me')
    return response.data
  },
}

export const projectService = {
  getAll: async () => {
    const response = await api.get('/projects')
    return response.data
  },

  getById: async (id) => {
    const response = await api.get(`/projects/${id}`)
    return response.data
  },

  create: async (projectData) => {
    const response = await api.post('/projects', projectData)
    return response.data
  },

  update: async (id, projectData) => {
    const response = await api.put(`/projects/${id}`, projectData)
    return response.data
  },

  delete: async (id) => {
    const response = await api.delete(`/projects/${id}`)
    return response.data
  },

  getCollaborators: async (id) => {
    const response = await api.get(`/projects/${id}/collaborators`)
    return response.data
  },

  addCollaborator: async (id, collaboratorData) => {
    const response = await api.post(`/projects/${id}/collaborators`, collaboratorData)
    return response.data
  },

  removeCollaborator: async (id, userId) => {
    const response = await api.delete(`/projects/${id}/collaborators/${userId}`)
    return response.data
  },
}

export const scriptService = {
  getVersions: async (projectId) => {
    const response = await api.get(`/scripts/${projectId}/versions`)
    return response.data
  },

  getVersion: async (projectId, versionId) => {
    const response = await api.get(`/scripts/${projectId}/versions/${versionId}`)
    return response.data
  },

  createVersion: async (projectId, versionData) => {
    const response = await api.post(`/scripts/${projectId}/versions`, versionData)
    return response.data
  },

  updateVersion: async (projectId, versionId, versionData) => {
    const response = await api.put(`/scripts/${projectId}/versions/${versionId}`, versionData)
    return response.data
  },

  analyzeScript: async (projectId, versionId) => {
    const response = await api.post(`/scripts/${projectId}/versions/${versionId}/analyze`)
    return response.data
  },

  getCharacters: async (projectId) => {
    const response = await api.get(`/scripts/${projectId}/characters`)
    return response.data
  },

  createCharacter: async (projectId, characterData) => {
    const response = await api.post(`/scripts/${projectId}/characters`, characterData)
    return response.data
  },
}

export const sceneService = {
  getAll: async (projectId) => {
    const response = await api.get(`/scenes/${projectId}`)
    return response.data
  },

  getById: async (projectId, sceneId) => {
    const response = await api.get(`/scenes/${projectId}/${sceneId}`)
    return response.data
  },

  create: async (projectId, sceneData) => {
    const response = await api.post(`/scenes/${projectId}`, sceneData)
    return response.data
  },

  update: async (projectId, sceneId, sceneData) => {
    const response = await api.put(`/scenes/${projectId}/${sceneId}`, sceneData)
    return response.data
  },

  delete: async (projectId, sceneId) => {
    const response = await api.delete(`/scenes/${projectId}/${sceneId}`)
    return response.data
  },

  generateSuggestions: async (projectId, sceneId) => {
    const response = await api.post(`/scenes/${projectId}/${sceneId}/suggestions`)
    return response.data
  },
}

export const storyboardService = {
  getPanels: async (projectId) => {
    const response = await api.get(`/storyboards/${projectId}/panels`)
    return response.data
  },

  getPanel: async (projectId, panelId) => {
    const response = await api.get(`/storyboards/${projectId}/panels/${panelId}`)
    return response.data
  },

  createPanel: async (projectId, panelData) => {
    const response = await api.post(`/storyboards/${projectId}/panels`, panelData)
    return response.data
  },

  updatePanel: async (projectId, panelId, panelData) => {
    const response = await api.put(`/storyboards/${projectId}/panels/${panelId}`, panelData)
    return response.data
  },

  deletePanel: async (projectId, panelId) => {
    const response = await api.delete(`/storyboards/${projectId}/panels/${panelId}`)
    return response.data
  },

  generateImage: async (projectId, panelId) => {
    const response = await api.post(`/storyboards/${projectId}/panels/${panelId}/generate`)
    return response.data
  },

  getVisualStyles: async (projectId) => {
    const response = await api.get(`/storyboards/${projectId}/visual-styles`)
    return response.data
  },
}

export const collaborationService = {
  getMessages: async (projectId, params) => {
    const response = await api.get(`/collaboration/${projectId}/messages`, { params })
    return response.data
  },

  sendMessage: async (projectId, messageData) => {
    const response = await api.post(`/collaboration/${projectId}/messages`, messageData)
    return response.data
  },

  addReaction: async (projectId, messageId, emoji) => {
    const response = await api.post(`/collaboration/${projectId}/messages/${messageId}/reactions`, { emoji })
    return response.data
  },

  getNotifications: async () => {
    const response = await api.get('/collaboration/notifications')
    return response.data
  },

  markAsRead: async (notificationId) => {
    const response = await api.put(`/collaboration/notifications/${notificationId}/read`)
    return response.data
  },
}

export const userService = {
  getProfile: async (userId) => {
    const response = await api.get(`/users/${userId}`)
    return response.data
  },

  updateProfile: async (userId, userData) => {
    const response = await api.put(`/users/${userId}`, userData)
    return response.data
  },

  getDashboard: async (userId) => {
    const response = await api.get(`/users/${userId}/dashboard`)
    return response.data
  },

  searchUsers: async (query) => {
    const response = await api.get('/users/search', { params: { q: query } })
    return response.data
  },
}
