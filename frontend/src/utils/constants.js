export const ROLES = {
  FILMMAKER: 'filmmaker',
  INVESTOR: 'investor',
  ACTOR: 'actor',
  CREW_MEMBER: 'crew_member',
  ADMIN: 'admin',
}

export const PROJECT_STATUS = {
  PLANNING: 'planning',
  PRE_PRODUCTION: 'pre-production',
  PRODUCTION: 'production',
  POST_PRODUCTION: 'post-production',
  COMPLETED: 'completed',
  ON_HOLD: 'on-hold',
}

export const SCENE_TYPES = {
  INTERIOR: 'interior',
  EXTERIOR: 'exterior',
}

export const TIME_OF_DAY = {
  DAY: 'day',
  NIGHT: 'night',
  DAWN: 'dawn',
  DUSK: 'dusk',
}

export const MESSAGE_TYPES = {
  TEXT: 'text',
  IMAGE: 'image',
  FILE: 'file',
  SYSTEM: 'system',
}

export const NOTIFICATION_TYPES = {
  COMMENT: 'comment',
  MENTION: 'mention',
  COLLABORATION: 'collaboration',
  PROJECT_UPDATE: 'project_update',
  SYSTEM: 'system',
}

export const AI_MODELS = {
  GROQ: 'groq',
  GEMINI: 'gemini',
}

export const FILE_UPLOAD_LIMITS = {
  MAX_SIZE: 10 * 1024 * 1024, // 10MB
  ACCEPTED_TYPES: {
    IMAGE: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
    VIDEO: ['video/mp4', 'video/webm'],
    DOCUMENT: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
  },
}

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  PROJECTS: '/projects',
  PROJECT_DETAILS: '/projects/:id',
  SCRIPT_EDITOR: '/projects/:id/script',
  STORYBOARD: '/projects/:id/storyboard',
  C_SPACE: '/projects/:id/c-space',
  SETTINGS: '/settings',
}
