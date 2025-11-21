"""
Export and File Storage Models
"""
from . import db
from datetime import datetime


class ProjectExport(db.Model):
    __tablename__ = 'project_exports'
    
    export_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False, index=True)
    export_type = db.Column(
        db.Enum('storyboard_pdf', 'script_pdf', 'checklist_pdf', 'full_package'),
        nullable=False,
        index=True
    )
    file_url = db.Column(db.String(500))
    file_size_kb = db.Column(db.Integer)
    generated_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    download_count = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        """Serialize project export to dictionary"""
        return {
            'export_id': self.export_id,
            'project_id': self.project_id,
            'export_type': self.export_type,
            'file_url': self.file_url,
            'file_size_kb': self.file_size_kb,
            'generated_by': self.generated_by,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'download_count': self.download_count,
        }
    
    def __repr__(self):
        return f'<ProjectExport {self.export_type}>'


class UploadedFile(db.Model):
    __tablename__ = 'uploaded_files'
    
    file_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id', ondelete='SET NULL'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(100))
    file_url = db.Column(db.String(500), nullable=False)
    file_size_kb = db.Column(db.Integer)
    upload_purpose = db.Column(db.String(100), comment='reference, storyboard, script, etc.')
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Serialize uploaded file to dictionary"""
        return {
            'file_id': self.file_id,
            'project_id': self.project_id,
            'user_id': self.user_id,
            'file_name': self.file_name,
            'file_type': self.file_type,
            'file_url': self.file_url,
            'file_size_kb': self.file_size_kb,
            'upload_purpose': self.upload_purpose,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
        }
    
    def __repr__(self):
        return f'<UploadedFile {self.file_name}>'
