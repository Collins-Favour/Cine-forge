"""
Script and Character Models
"""
from . import db
from datetime import datetime


class ScriptVersion(db.Model):
    __tablename__ = 'script_versions'
    
    version_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False, index=True)
    script_content = db.Column(db.Text, nullable=False)
    version_number = db.Column(db.Integer, nullable=False, default=1, index=True)
    version_name = db.Column(db.String(100))
    word_count = db.Column(db.Integer)
    page_count = db.Column(db.Integer)
    estimated_runtime = db.Column(db.Integer, comment='Estimated runtime in minutes')
    changes_summary = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self, include_content=False):
        """Serialize script version to dictionary"""
        data = {
            'version_id': self.version_id,
            'project_id': self.project_id,
            'version_number': self.version_number,
            'version_name': self.version_name,
            'word_count': self.word_count,
            'page_count': self.page_count,
            'estimated_runtime': self.estimated_runtime,
            'changes_summary': self.changes_summary,
            'created_by': self.created_by,
            'saved_at': self.saved_at.isoformat() if self.saved_at else None,
        }
        
        if include_content:
            data['script_content'] = self.script_content
        
        return data
    
    def __repr__(self):
        return f'<ScriptVersion {self.version_number}>'


class Character(db.Model):
    __tablename__ = 'characters'
    
    character_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False, index=True)
    character_name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    role_type = db.Column(db.Enum('protagonist', 'antagonist', 'supporting', 'minor'), default='supporting')
    age_range = db.Column(db.String(50))
    gender = db.Column(db.String(50))
    personality_traits = db.Column(db.JSON)
    dialogue_count = db.Column(db.Integer, default=0)
    first_appearance = db.Column(db.Integer, comment='Scene number of first appearance')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    scene_appearances = db.relationship('SceneCharacter', backref='character', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Serialize character to dictionary"""
        return {
            'character_id': self.character_id,
            'project_id': self.project_id,
            'character_name': self.character_name,
            'description': self.description,
            'role_type': self.role_type,
            'age_range': self.age_range,
            'gender': self.gender,
            'personality_traits': self.personality_traits,
            'dialogue_count': self.dialogue_count,
            'first_appearance': self.first_appearance,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<Character {self.character_name}>'


class SceneCharacter(db.Model):
    __tablename__ = 'scene_characters'
    
    scene_character_id = db.Column(db.Integer, primary_key=True)
    scene_id = db.Column(db.Integer, db.ForeignKey('scenes.scene_id', ondelete='CASCADE'), nullable=False, index=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.character_id', ondelete='CASCADE'), nullable=False, index=True)
    dialogue_lines = db.Column(db.Integer, default=0)
    is_main_focus = db.Column(db.Boolean, default=False)
    
    __table_args__ = (
        db.UniqueConstraint('scene_id', 'character_id', name='unique_scene_character'),
    )
    
    def to_dict(self):
        """Serialize scene character to dictionary"""
        return {
            'scene_character_id': self.scene_character_id,
            'scene_id': self.scene_id,
            'character_id': self.character_id,
            'dialogue_lines': self.dialogue_lines,
            'is_main_focus': self.is_main_focus,
        }
    
    def __repr__(self):
        return f'<SceneCharacter scene:{self.scene_id} char:{self.character_id}>'
