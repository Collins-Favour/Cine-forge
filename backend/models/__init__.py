"""
Database Models Package
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models
from .user import User, UserSession
from .project import Project, ProjectCollaborator, ActivityLog
from .script import ScriptVersion, Character, SceneCharacter
from .scene import Scene, VisualStyle
from .storyboard import StoryboardPanel
from .checklist import ChecklistItem, BudgetItem
from .collaboration import CSpaceMessage, MessageReaction
from .ai import AIProcessingLog, UsageAnalytics
from .notification import Notification
from .export import ProjectExport, UploadedFile
from .system import SystemSetting

__all__ = [
    'db',
    'User',
    'UserSession',
    'Project',
    'ProjectCollaborator',
    'ActivityLog',
    'ScriptVersion',
    'Character',
    'SceneCharacter',
    'Scene',
    'VisualStyle',
    'StoryboardPanel',
    'ChecklistItem',
    'BudgetItem',
    'CSpaceMessage',
    'MessageReaction',
    'AIProcessingLog',
    'UsageAnalytics',
    'Notification',
    'ProjectExport',
    'UploadedFile',
    'SystemSetting'
]
