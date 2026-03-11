"""
Scene Models
"""
from . import db
from datetime import datetime


class Scene(db.Model):
    __tablename__ = 'scenes'
    
    scene_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False, index=True)
    scene_number = db.Column(db.Integer, nullable=False, index=True)
    slug = db.Column(db.String(255), comment='Scene heading/slug line')
    description = db.Column(db.Text)
    location = db.Column(db.String(255), index=True)
    time_of_day = db.Column(db.Enum('dawn', 'day', 'dusk', 'night', 'golden-hour'), default='day')
    interior_exterior = db.Column(db.Enum('INT', 'EXT', 'INT/EXT'), default='INT')
    page_length = db.Column(db.Numeric(4, 2), comment='Scene length in pages')
    estimated_duration = db.Column(db.Integer, comment='Estimated duration in seconds')
    narrative_purpose = db.Column(db.Text)
    emotional_tone = db.Column(db.String(100))
    pacing = db.Column(db.Enum('slow', 'medium', 'fast'), default='medium')
    
    # AI-generated suggestions
    location_suggestion = db.Column(db.Text)
    mood_suggestion = db.Column(db.Text)
    lighting_suggestion = db.Column(db.Text)
    cinematography_notes = db.Column(db.Text)
    sound_design_notes = db.Column(db.Text)
    
    # Metadata
    is_action_scene = db.Column(db.Boolean, default=False)
    is_dialogue_heavy = db.Column(db.Boolean, default=False)
    vfx_required = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    characters = db.relationship('SceneCharacter', backref='scene', lazy='dynamic', cascade='all, delete-orphan')
    storyboard_panels = db.relationship('StoryboardPanel', backref='scene', lazy='dynamic', cascade='all, delete-orphan')
    checklist_items = db.relationship('ChecklistItem', backref='scene', lazy='dynamic', cascade='all, delete-orphan')
    budget_items = db.relationship('BudgetItem', backref='scene', lazy='dynamic')
    
    def to_dict(self, include_relationships=False, relationship_data=None):
        """
        Serialize scene to dictionary
        
        Args:
            include_relationships: Whether to include relationships
            relationship_data: Pre-loaded relationship data to avoid N+1 queries
                              Format: {'characters': [...], 'panels_count': int, 
                                      'checklist_items_count': int}
        """
        data = {
            'scene_id': self.scene_id,
            'project_id': self.project_id,
            'scene_number': self.scene_number,
            'slug': self.slug,
            'description': self.description,
            'location': self.location,
            'time_of_day': self.time_of_day,
            'interior_exterior': self.interior_exterior,
            'page_length': float(self.page_length) if self.page_length else None,
            'estimated_duration': self.estimated_duration,
            'narrative_purpose': self.narrative_purpose,
            'emotional_tone': self.emotional_tone,
            'pacing': self.pacing,
            'location_suggestion': self.location_suggestion,
            'mood_suggestion': self.mood_suggestion,
            'lighting_suggestion': self.lighting_suggestion,
            'cinematography_notes': self.cinematography_notes,
            'sound_design_notes': self.sound_design_notes,
            'is_action_scene': self.is_action_scene,
            'is_dialogue_heavy': self.is_dialogue_heavy,
            'vfx_required': self.vfx_required,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_relationships:
            if relationship_data:
                # Use pre-loaded data to avoid N+1 queries  
                data.update(relationship_data)
            else:
                # Fallback to lazy loading (slower)
                data['characters'] = [sc.to_dict() for sc in self.characters.all()]
                data['panels_count'] = self.storyboard_panels.count()
                data['checklist_items_count'] = self.checklist_items.count()
        
        return data
    
    def __repr__(self):
        return f'<Scene {self.scene_number}>'


class VisualStyle(db.Model):
    __tablename__ = 'visual_styles'
    
    style_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False, index=True)
    style_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    reference_images = db.Column(db.JSON, comment='Array of reference image URLs')
    color_palette = db.Column(db.JSON, comment='Hex color codes')
    mood_keywords = db.Column(db.JSON, comment='Keywords for AI generation')
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Serialize visual style to dictionary"""
        return {
            'style_id': self.style_id,
            'project_id': self.project_id,
            'style_name': self.style_name,
            'description': self.description,
            'reference_images': self.reference_images,
            'color_palette': self.color_palette,
            'mood_keywords': self.mood_keywords,
            'is_primary': self.is_primary,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<VisualStyle {self.style_name}>'
