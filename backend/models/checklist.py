"""
Checklist and Budget Models
"""
from . import db
from datetime import datetime


class ChecklistItem(db.Model):
    __tablename__ = 'checklist_items'
    
    item_id = db.Column(db.Integer, primary_key=True)
    scene_id = db.Column(db.Integer, db.ForeignKey('scenes.scene_id', ondelete='CASCADE'), nullable=False, index=True)
    category = db.Column(
        db.Enum('props', 'wardrobe', 'location', 'cast', 'equipment', 'vfx', 'sound', 'other'),
        nullable=False,
        index=True
    )
    item_text = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.Enum('low', 'medium', 'high', 'critical'), default='medium')
    is_completed = db.Column(db.Boolean, default=False, index=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'))
    due_date = db.Column(db.Date)
    completed_at = db.Column(db.DateTime)
    completed_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Serialize checklist item to dictionary"""
        return {
            'item_id': self.item_id,
            'scene_id': self.scene_id,
            'category': self.category,
            'item_text': self.item_text,
            'description': self.description,
            'priority': self.priority,
            'is_completed': self.is_completed,
            'assigned_to': self.assigned_to,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'completed_by': self.completed_by,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<ChecklistItem {self.item_text}>'


class BudgetItem(db.Model):
    __tablename__ = 'budget_items'
    
    budget_item_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False, index=True)
    scene_id = db.Column(db.Integer, db.ForeignKey('scenes.scene_id', ondelete='SET NULL'), index=True)
    category = db.Column(db.String(100), nullable=False, index=True)
    item_name = db.Column(db.String(255), nullable=False)
    estimated_cost = db.Column(db.Numeric(10, 2))
    actual_cost = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.String(10), default='USD')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Serialize budget item to dictionary"""
        return {
            'budget_item_id': self.budget_item_id,
            'project_id': self.project_id,
            'scene_id': self.scene_id,
            'category': self.category,
            'item_name': self.item_name,
            'estimated_cost': float(self.estimated_cost) if self.estimated_cost else None,
            'actual_cost': float(self.actual_cost) if self.actual_cost else None,
            'currency': self.currency,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<BudgetItem {self.item_name}>'
