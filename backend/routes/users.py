"""
User Routes
Handles user profile management, preferences, and account settings
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Project, UsageAnalytics
from utils.decorators import validate_request
from sqlalchemy import func

users_bp = Blueprint('users', __name__)


@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current logged-in user profile"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict(include_email=True)}), 200


@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get user profile by ID"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    current_user_id = int(get_jwt_identity())
    include_email = (current_user_id == user_id)
    
    return jsonify({'user': user.to_dict(include_email=include_email)}), 200


@users_bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
def profile():
    """Get or update user profile"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if request.method == 'GET':
        return jsonify({'user': user.to_dict(include_email=True)}), 200
    
    # PUT - Update profile
    data = request.get_json()
    
    # Update allowed fields
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'email' in data:
        user.email = data['email']
    if 'phone' in data:
        user.phone = data['phone']
    if 'location' in data:
        user.location = data['location']
    if 'bio' in data:
        user.bio = data['bio']
    if 'profile_pic_url' in data:
        user.profile_pic_url = data['profile_pic_url']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': user.to_dict(include_email=True)
    }), 200


@users_bp.route('/change-password', methods=['POST'])
@jwt_required()
@validate_request(['current_password', 'new_password'])
def change_password():
    """Change user password"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    data = request.get_json()
    
    if not user.check_password(data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    user.set_password(data['new_password'])
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'}), 200


@users_bp.route('/dashboard', methods=['GET'])
@users_bp.route('/<int:user_id>/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard(user_id=None):
    """Get user dashboard statistics"""
    current_user_id = int(get_jwt_identity())
    
    # Use provided user_id or current user
    target_user_id = user_id if user_id else current_user_id
    
    # Get all projects user has access to (via collaborations)
    from models import ProjectCollaborator
    
    # Get all project IDs user is collaborating on (includes owned projects since owners are auto-added as collaborators)
    collaborated_project_ids = [pc.project_id for pc in ProjectCollaborator.query.filter_by(
        user_id=target_user_id,
        invitation_status='accepted'
    ).all()]
    
    # Get all projects (deduplicated)
    all_projects = Project.query.filter(
        Project.project_id.in_(collaborated_project_ids),
        Project.is_archived == False
    ).all() if collaborated_project_ids else []
    
    total_projects = len(all_projects)
    
    # Count collaborations (excluding owned projects)
    owned_project_ids = [p.project_id for p in Project.query.filter_by(
        created_by=target_user_id,
        is_archived=False
    ).all()]
    collaborations_count = len([pid for pid in collaborated_project_ids if pid not in owned_project_ids])
    
    # Sort by updated_at and get recent projects
    all_projects.sort(key=lambda x: x.updated_at, reverse=True)
    recent_projects = all_projects[:5]
    
    # Count active projects (in production stages)
    active_statuses = ['pre-production', 'production', 'post-production']
    active_projects = sum(1 for p in all_projects if p.production_stage in active_statuses)
    
    # Get storyboard count (mock for now)
    total_storyboards = 0  # TODO: Add storyboard model
    
    return jsonify({
        'total_projects': total_projects,
        'active_projects': active_projects,
        'collaborations': collaborations_count,
        'total_storyboards': total_storyboards,
        'recent_projects': [p.to_dict() for p in recent_projects]
    }), 200


@users_bp.route('/search', methods=['GET'])
@jwt_required()
def search_users():
    """Search users by username or email"""
    query = request.args.get('q', '')
    
    if len(query) < 2:
        return jsonify({'error': 'Query too short'}), 400
    
    users = User.query.filter(
        db.or_(
            User.username.ilike(f'%{query}%'),
            User.email.ilike(f'%{query}%')
        ),
        User.is_active == True
    ).limit(10).all()
    
    return jsonify({
        'users': [u.to_dict() for u in users]
    }), 200


@users_bp.route('/notifications', methods=['PUT'])
@jwt_required()
def update_notifications():
    """Update notification preferences"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    # Store notification preferences (could be in separate table)
    # For now, just return success
    
    return jsonify({'message': 'Notification preferences updated'}), 200


@users_bp.route('/deactivate', methods=['POST'])
@jwt_required()
def deactivate_account():
    """Deactivate user account"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    user.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Account deactivated successfully'}), 200


@users_bp.route('/upload-avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    """Upload user avatar/profile picture"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if file is in request
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if file_ext not in allowed_extensions:
        return jsonify({'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, WEBP'}), 400
    
    try:
        # Read file data and convert to base64 for storage
        import base64
        file_data = file.read()
        
        # Validate file size (5MB max)
        if len(file_data) > 5 * 1024 * 1024:
            return jsonify({'error': 'File size exceeds 5MB limit'}), 400
        
        # Create data URI
        mime_type = f"image/{file_ext if file_ext != 'jpg' else 'jpeg'}"
        base64_data = base64.b64encode(file_data).decode('utf-8')
        data_uri = f"data:{mime_type};base64,{base64_data}"
        
        # Update user profile picture
        user.profile_pic_url = data_uri
        db.session.commit()
        
        return jsonify({
            'message': 'Avatar uploaded successfully',
            'profile_pic_url': data_uri,
            'user': user.to_dict(include_email=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to upload avatar: {str(e)}'}), 500
