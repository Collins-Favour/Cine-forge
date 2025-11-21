"""
Utility Helper Functions
"""
from models import db, ActivityLog
from datetime import datetime


def log_activity(project_id, user_id, activity_type, description, entity_type=None, entity_id=None, metadata=None):
    """Log activity to database"""
    activity = ActivityLog(
        project_id=project_id,
        user_id=user_id,
        activity_type=activity_type,
        activity_description=description,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata=metadata
    )
    db.session.add(activity)
    return activity


def paginate_query(query, page=1, per_page=20):
    """Paginate a SQLAlchemy query"""
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return {
        'items': pagination.items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }


def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def calculate_script_stats(script_content):
    """Calculate script statistics"""
    word_count = len(script_content.split())
    page_count = max(1, word_count // 250)  # Approximately 250 words per page
    estimated_runtime = page_count  # 1 page = 1 minute (rough estimate)
    
    return {
        'word_count': word_count,
        'page_count': page_count,
        'estimated_runtime': estimated_runtime
    }
