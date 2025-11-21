"""
AI Processing and Analytics Models
"""
from . import db
from datetime import datetime


class AIProcessingLog(db.Model):
    __tablename__ = 'ai_processing_logs'
    
    log_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    operation_type = db.Column(
        db.Enum('script_analysis', 'scene_breakdown', 'image_generation', 'mood_suggestion', 'location_suggestion'),
        nullable=False,
        index=True
    )
    input_data = db.Column(db.JSON)
    output_data = db.Column(db.JSON)
    ai_model = db.Column(db.String(100), comment='GPT-4, Gemini, Stable Diffusion, etc.')
    processing_time_ms = db.Column(db.Integer)
    tokens_used = db.Column(db.Integer)
    cost_estimate = db.Column(db.Numeric(10, 6))
    status = db.Column(db.Enum('pending', 'processing', 'completed', 'failed'), default='pending')
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Serialize AI processing log to dictionary"""
        return {
            'log_id': self.log_id,
            'project_id': self.project_id,
            'user_id': self.user_id,
            'operation_type': self.operation_type,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'ai_model': self.ai_model,
            'processing_time_ms': self.processing_time_ms,
            'tokens_used': self.tokens_used,
            'cost_estimate': float(self.cost_estimate) if self.cost_estimate else None,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<AIProcessingLog {self.operation_type}>'


class UsageAnalytics(db.Model):
    __tablename__ = 'usage_analytics'
    
    analytics_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    event_type = db.Column(db.String(100), nullable=False, index=True)
    event_data = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Serialize usage analytics to dictionary"""
        return {
            'analytics_id': self.analytics_id,
            'user_id': self.user_id,
            'event_type': self.event_type,
            'event_data': self.event_data,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<UsageAnalytics {self.event_type}>'
