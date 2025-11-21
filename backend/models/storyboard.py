"""
Storyboard Models
"""
from . import db
from datetime import datetime


class StoryboardPanel(db.Model):
    __tablename__ = 'storyboard_panels'
    
    panel_id = db.Column(db.Integer, primary_key=True)
    scene_id = db.Column(db.Integer, db.ForeignKey('scenes.scene_id', ondelete='CASCADE'), nullable=False, index=True)
    panel_number = db.Column(db.Integer, nullable=False, index=True)
    
    # Image generation prompts
    image_prompt = db.Column(db.Text, nullable=False)
    negative_prompt = db.Column(db.Text)
    style_reference = db.Column(db.String(255), comment='Art style: realistic, animated, sketch, etc.')
    
    # Generated images
    generated_image_url = db.Column(db.String(500))
    thumbnail_url = db.Column(db.String(500))
    manual_image_url = db.Column(db.String(500), comment='User-uploaded alternative')
    
    # Generation metadata
    ai_model_used = db.Column(db.String(100), comment='Stable Diffusion, DALL-E, Midjourney')
    generation_settings = db.Column(db.JSON, comment='Model parameters used')
    generation_timestamp = db.Column(db.DateTime)
    
    # Panel details
    camera_angle = db.Column(db.String(100))
    shot_type = db.Column(
        db.Enum('close-up', 'medium', 'wide', 'establishing', 'over-shoulder', 'pov'),
        default='medium'
    )
    movement = db.Column(db.String(255), comment='Pan, tilt, dolly, etc.')
    notes = db.Column(db.Text)
    
    # Status
    status = db.Column(db.Enum('pending', 'generating', 'completed', 'failed'), default='pending', index=True)
    is_approved = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Serialize storyboard panel to dictionary"""
        return {
            'panel_id': self.panel_id,
            'scene_id': self.scene_id,
            'panel_number': self.panel_number,
            'image_prompt': self.image_prompt,
            'negative_prompt': self.negative_prompt,
            'style_reference': self.style_reference,
            'generated_image_url': self.generated_image_url,
            'thumbnail_url': self.thumbnail_url,
            'manual_image_url': self.manual_image_url,
            'ai_model_used': self.ai_model_used,
            'generation_settings': self.generation_settings,
            'generation_timestamp': self.generation_timestamp.isoformat() if self.generation_timestamp else None,
            'camera_angle': self.camera_angle,
            'shot_type': self.shot_type,
            'movement': self.movement,
            'notes': self.notes,
            'status': self.status,
            'is_approved': self.is_approved,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<StoryboardPanel {self.panel_id}>'
