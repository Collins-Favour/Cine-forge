"""
Utility Decorators
"""
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from models import ProjectCollaborator
from utils.logger import get_logger

logger = get_logger('cineforge.api')


def validate_request(required_fields):
    """Validate that required fields are present in request"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'Request body is required'}), 400
            
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return jsonify({
                    'error': 'Missing required fields',
                    'missing_fields': missing_fields
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def project_permission_required(required_role):
    """
    Check if user has required permission for project
    Roles hierarchy: viewer < editor < writer < director < owner
    Admins bypass all permission checks
    """
    role_hierarchy = {
        'viewer': 0,
        'editor': 1,
        'writer': 2,
        'director': 3,
        'owner': 4
    }
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                identity = get_jwt_identity()
                if identity is None:
                    return jsonify({'error': 'Authentication required'}), 401
                user_id = int(identity)
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid JWT identity: {e}")
                return jsonify({'error': 'Invalid authentication token'}), 401
            
            project_id = kwargs.get('project_id')
            
            if not project_id:
                return jsonify({'error': 'Project ID required'}), 400
            
            # Check if user is admin - admins have access to all projects
            from models import User
            user = User.query.get(user_id)
            if not user:
                logger.warning(f"User {user_id} from JWT not found in database")
                return jsonify({'error': 'User not found'}), 401
            
            if user.role == 'admin':
                return f(*args, **kwargs)
            
            # Check if user is collaborator
            collaboration = ProjectCollaborator.query.filter_by(
                project_id=project_id,
                user_id=user_id
            ).first()
            
            if not collaboration:
                logger.info(f"Access denied: user {user_id} has no access to project {project_id}")
                return jsonify({'error': 'Access denied'}), 403
            
            # Check role hierarchy
            user_role_level = role_hierarchy.get(collaboration.role, 0)
            required_role_level = role_hierarchy.get(required_role, 0)
            
            if user_role_level < required_role_level:
                logger.info(
                    f"Insufficient permissions: user {user_id} has role '{collaboration.role}' "
                    f"but needs '{required_role}' for project {project_id}"
                )
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
