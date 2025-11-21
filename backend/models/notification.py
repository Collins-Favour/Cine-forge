"""
Notification Models
"""
from . import db
from datetime import datetime


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    notification_type = db.Column(
        db.Enum('collaboration_invite', 'message', 'task_assigned', 'generation_complete', 'mention', 'system'),
        nullable=False
    )
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text)
    link_url = db.Column(db.String(500))
    is_read = db.Column(db.Boolean, default=False, index=True)
    read_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Serialize notification to dictionary"""
        return {
            'notification_id': self.notification_id,
            'user_id': self.user_id,
            'notification_type': self.notification_type,
            'title': self.title,
            'message': self.message,
            'link_url': self.link_url,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<Notification {self.notification_type}>'
