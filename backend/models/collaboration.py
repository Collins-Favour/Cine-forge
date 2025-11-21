"""
Collaboration and C-Space Models
"""
from . import db
from datetime import datetime


class CSpaceMessage(db.Model):
    __tablename__ = 'cspace_messages'
    
    message_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    parent_message_id = db.Column(db.Integer, db.ForeignKey('cspace_messages.message_id', ondelete='CASCADE'), comment='For threaded replies')
    channel = db.Column(db.String(50), default='general', index=True, comment='Channel name (general, production, creative, budget, etc.)')
    message_type = db.Column(db.Enum('text', 'annotation', 'feedback', 'approval', 'file'), default='text')
    message_content = db.Column(db.Text, nullable=False)
    
    # Attachments and references
    attached_file_url = db.Column(db.String(500))
    attached_thumbnail = db.Column(db.String(500))
    referenced_scene_id = db.Column(db.Integer, db.ForeignKey('scenes.scene_id', ondelete='SET NULL'))
    referenced_panel_id = db.Column(db.Integer, db.ForeignKey('storyboard_panels.panel_id', ondelete='SET NULL'))
    
    # Annotations for visual feedback
    annotation_data = db.Column(db.JSON, comment='Coordinates and markup data for image annotations')
    
    # Status
    is_resolved = db.Column(db.Boolean, default=False)
    is_pinned = db.Column(db.Boolean, default=False)
    is_edited = db.Column(db.Boolean, default=False)
    edited_at = db.Column(db.DateTime)
    
    sent_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    reactions = db.relationship('MessageReaction', backref='message', lazy='dynamic', cascade='all, delete-orphan')
    replies = db.relationship('CSpaceMessage', backref=db.backref('parent', remote_side=[message_id]), lazy='dynamic')
    
    def to_dict(self, include_replies=False):
        """Serialize message to dictionary"""
        data = {
            'message_id': self.message_id,
            'project_id': self.project_id,
            'user_id': self.user_id,
            'parent_message_id': self.parent_message_id,
            'channel': self.channel,
            'message_type': self.message_type,
            'message_content': self.message_content,
            'attached_file_url': self.attached_file_url,
            'attached_thumbnail': self.attached_thumbnail,
            'referenced_scene_id': self.referenced_scene_id,
            'referenced_panel_id': self.referenced_panel_id,
            'annotation_data': self.annotation_data,
            'is_resolved': self.is_resolved,
            'is_pinned': self.is_pinned,
            'is_edited': self.is_edited,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'reactions_count': self.reactions.count(),
        }
        
        if include_replies:
            data['replies'] = [reply.to_dict() for reply in self.replies.all()]
        
        return data
    
    def __repr__(self):
        return f'<CSpaceMessage {self.message_id}>'


class MessageReaction(db.Model):
    __tablename__ = 'message_reactions'
    
    reaction_id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('cspace_messages.message_id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    reaction_type = db.Column(db.String(50), nullable=False, comment='emoji or reaction name')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('message_id', 'user_id', 'reaction_type', name='unique_message_user_reaction'),
    )
    
    def to_dict(self):
        """Serialize reaction to dictionary"""
        return {
            'reaction_id': self.reaction_id,
            'message_id': self.message_id,
            'user_id': self.user_id,
            'reaction_type': self.reaction_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<MessageReaction {self.reaction_type}>'
