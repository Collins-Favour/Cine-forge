"""
Project Models
"""
from . import db
from datetime import datetime
import json


class Project(db.Model):
    __tablename__ = 'projects'
    
    project_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    logline = db.Column(db.Text)
    synopsis = db.Column(db.Text)
    genre = db.Column(db.String(100), index=True)
    target_length = db.Column(db.Integer, comment='Target film length in minutes')
    budget_range = db.Column(db.String(50))
    production_stage = db.Column(
        db.Enum('concept', 'pre-production', 'production', 'post-production', 'completed'),
        default='concept',
        index=True
    )
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    thumbnail_url = db.Column(db.Text)  # Changed to Text to support base64-encoded images
    is_public = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    collaborators = db.relationship('ProjectCollaborator', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    script_versions = db.relationship('ScriptVersion', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    characters = db.relationship('Character', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    scenes = db.relationship('Scene', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    visual_styles = db.relationship('VisualStyle', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    messages = db.relationship('CSpaceMessage', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    activities = db.relationship('ActivityLog', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    exports = db.relationship('ProjectExport', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    budget_items = db.relationship('BudgetItem', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    ai_logs = db.relationship('AIProcessingLog', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_stats=False, stats_data=None):
        """
        Serialize project to dictionary
        
        Args:
            include_stats: Whether to include statistics
            stats_data: Pre-computed stats dict to avoid N+1 queries
                       Format: {'total_scenes': int, 'total_characters': int, 
                               'total_collaborators': int, 'latest_script_version': int}
        """
        data = {
            'project_id': self.project_id,
            'title': self.title,
            'logline': self.logline,
            'synopsis': self.synopsis,
            'genre': self.genre,
            'target_length': self.target_length,
            'budget_range': self.budget_range,
            'production_stage': self.production_stage,
            'created_by': self.created_by,
            'thumbnail_url': self.thumbnail_url,
            'is_public': self.is_public,
            'is_archived': self.is_archived,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_stats:
            if stats_data:
                # Use pre-computed stats to avoid N+1 queries
                data['stats'] = stats_data
            else:
                # Fallback to lazy loading (slower)
                latest_version = self.script_versions.order_by(db.desc('version_number')).first()
                data['stats'] = {
                    'total_scenes': self.scenes.count(),
                    'total_characters': self.characters.count(),
                    'total_collaborators': self.collaborators.count(),
                    'latest_script_version': latest_version.version_number if latest_version else 0
                }
        
        return data
    
    def __repr__(self):
        return f'<Project {self.title}>'


class ProjectCollaborator(db.Model):
    __tablename__ = 'project_collaborators'
    
    collaboration_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    role = db.Column(db.Enum('owner', 'director', 'writer', 'editor', 'viewer'), default='viewer', nullable=False)
    permissions = db.Column(db.JSON, comment='Custom permissions')
    invited_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'))
    invitation_status = db.Column(db.Enum('pending', 'accepted', 'declined'), default='accepted')
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('project_id', 'user_id', name='unique_project_user'),
    )
    
    def get_permissions(self):
        """Get permissions as dictionary"""
        if self.permissions:
            return json.loads(self.permissions) if isinstance(self.permissions, str) else self.permissions
        return {}
    
    def set_permissions(self, permissions_dict):
        """Set permissions from dictionary"""
        self.permissions = permissions_dict
    
    def to_dict(self):
        """Serialize collaborator to dictionary"""
        return {
            'collaboration_id': self.collaboration_id,
            'project_id': self.project_id,
            'user_id': self.user_id,
            'role': self.role,
            'permissions': self.get_permissions(),
            'invitation_status': self.invitation_status,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
        }
    
    def __repr__(self):
        return f'<ProjectCollaborator {self.user_id} - {self.role}>'


class ActivityLog(db.Model):
    __tablename__ = 'activity_log'
    
    activity_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    activity_type = db.Column(db.String(100), nullable=False)
    activity_description = db.Column(db.Text)
    entity_type = db.Column(db.String(50), comment='scene, panel, message, etc.')
    entity_id = db.Column(db.Integer)
    activity_metadata = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Serialize activity to dictionary"""
        return {
            'activity_id': self.activity_id,
            'project_id': self.project_id,
            'user_id': self.user_id,
            'activity_type': self.activity_type,
            'activity_description': self.activity_description,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'metadata': self.activity_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<ActivityLog {self.activity_type}>'
