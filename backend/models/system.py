"""
System Configuration Models
"""
from . import db
from datetime import datetime


class SystemSetting(db.Model):
    __tablename__ = 'system_settings'
    
    setting_id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text)
    setting_type = db.Column(db.Enum('string', 'number', 'boolean', 'json'), default='string')
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False, comment='Can be accessed by frontend')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_value(self):
        """Get typed value based on setting_type"""
        if self.setting_type == 'number':
            return int(self.setting_value) if self.setting_value else None
        elif self.setting_type == 'boolean':
            return self.setting_value.lower() == 'true' if self.setting_value else False
        elif self.setting_type == 'json':
            import json
            return json.loads(self.setting_value) if self.setting_value else None
        return self.setting_value
    
    def to_dict(self):
        """Serialize system setting to dictionary"""
        return {
            'setting_id': self.setting_id,
            'setting_key': self.setting_key,
            'setting_value': self.get_value(),
            'setting_type': self.setting_type,
            'description': self.description,
            'is_public': self.is_public,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<SystemSetting {self.setting_key}>'
