"""
Admin Routes
Handles admin dashboard, user management, system settings, and analytics
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Project, CSpaceMessage, ActivityLog, UsageAnalytics
from models.system import SystemSetting
from sqlalchemy import func, desc
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)


def check_admin():
    """Check if current user is admin"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return None
    return user


@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_admin_dashboard():
    """Get admin dashboard statistics"""
    admin_user = check_admin()
    if not admin_user:
        return jsonify({'error': 'Admin access required'}), 403
    
    # Total users
    total_users = User.query.filter_by(is_active=True).count()
    
    # Users by role
    users_by_role = db.session.query(
        User.role, func.count(User.user_id)
    ).filter_by(is_active=True).group_by(User.role).all()
    
    users_by_role_dict = {role: count for role, count in users_by_role}
    
    # Active projects
    active_projects = Project.query.filter_by(is_archived=False).count()
    
    # Storage calculation (mock for now)
    storage_used = round(Project.query.count() * 0.5, 2)  # Mock: 0.5GB per project
    
    # System alerts (mock)
    system_alerts = 0
    
    # Recent users (last 10)
    recent_users = User.query.order_by(desc(User.created_at)).limit(10).all()
    
    # Recent activity
    recent_activity = []
    try:
        activities = ActivityLog.query.order_by(desc(ActivityLog.created_at)).limit(10).all()
        recent_activity = [
            {
                'description': f"{a.user.username if a.user else 'User'} {a.action}",
                'timestamp': a.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for a in activities
        ]
    except:
        pass
    
    return jsonify({
        'total_users': total_users,
        'users_by_role': users_by_role_dict,
        'active_projects': active_projects,
        'storage_used': storage_used,
        'system_alerts': system_alerts,
        'recent_users': [
            {
                'id': u.user_id,
                'full_name': f"{u.first_name or ''} {u.last_name or ''}".strip() or u.username,
                'email': u.email,
                'role': u.role,
                'is_active': u.is_active,
                'is_verified': u.is_verified,
                'created_at': u.created_at.isoformat() if u.created_at else None
            } for u in recent_users
        ],
        'recent_activity': recent_activity
    }), 200


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Get all users with pagination and filtering"""
    admin_user = check_admin()
    if not admin_user:
        return jsonify({'error': 'Admin access required'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    status_filter = request.args.get('status', '')
    
    query = User.query
    
    # Search filter
    if search:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%')
            )
        )
    
    # Role filter
    if role_filter:
        query = query.filter_by(role=role_filter)
    
    # Status filter
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)
    elif status_filter == 'verified':
        query = query.filter_by(is_verified=True)
    elif status_filter == 'unverified':
        query = query.filter_by(is_verified=False)
    
    # Pagination
    pagination = query.order_by(desc(User.created_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'users': [
            {
                'user_id': u.user_id,
                'username': u.username,
                'email': u.email,
                'full_name': f"{u.first_name or ''} {u.last_name or ''}".strip() or u.username,
                'role': u.role,
                'is_active': u.is_active,
                'is_verified': u.is_verified,
                'last_login': u.last_login.isoformat() if u.last_login else None,
                'created_at': u.created_at.isoformat() if u.created_at else None,
                'profile_pic_url': u.profile_pic_url
            } for u in pagination.items
        ],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_details(user_id):
    """Get detailed user information"""
    admin_user = check_admin()
    if not admin_user:
        return jsonify({'error': 'Admin access required'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user's projects
    projects = Project.query.filter_by(created_by=user_id).all()
    
    # Get user's collaborations
    from models import ProjectCollaborator
    collaborations = ProjectCollaborator.query.filter_by(user_id=user_id).all()
    
    # Get user's messages count
    messages_count = CSpaceMessage.query.filter_by(user_id=user_id).count()
    
    # Get recent activity
    activity = []
    try:
        activities = ActivityLog.query.filter_by(user_id=user_id)\
            .order_by(desc(ActivityLog.created_at)).limit(20).all()
        activity = [
            {
                'action': a.action,
                'description': a.description,
                'timestamp': a.created_at.isoformat()
            } for a in activities
        ]
    except:
        pass
    
    return jsonify({
        'user': {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'bio': user.bio,
            'role': user.role,
            'is_active': user.is_active,
            'is_verified': user.is_verified,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'profile_pic_url': user.profile_pic_url
        },
        'stats': {
            'projects_count': len(projects),
            'collaborations_count': len(collaborations),
            'messages_count': messages_count
        },
        'projects': [
            {
                'project_id': p.project_id,
                'project_name': p.project_name,
                'created_at': p.created_at.isoformat() if p.created_at else None
            } for p in projects[:10]
        ],
        'recent_activity': activity
    }), 200


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update user details (admin only)"""
    admin_user = check_admin()
    if not admin_user:
        return jsonify({'error': 'Admin access required'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    if 'role' in data and data['role'] in ['student', 'filmmaker', 'professional', 'admin']:
        user.role = data['role']
    
    if 'is_active' in data:
        user.is_active = bool(data['is_active'])
    
    if 'is_verified' in data:
        user.is_verified = bool(data['is_verified'])
    
    if 'email' in data:
        # Check if email already exists
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.user_id != user_id:
            return jsonify({'error': 'Email already in use'}), 400
        user.email = data['email']
    
    if 'first_name' in data:
        user.first_name = data['first_name']
    
    if 'last_name' in data:
        user.last_name = data['last_name']
    
    db.session.commit()
    
    return jsonify({
        'message': 'User updated successfully',
        'user': user.to_dict(include_email=True)
    }), 200


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete user (admin only)"""
    admin_user = check_admin()
    if not admin_user:
        return jsonify({'error': 'Admin access required'}), 403
    
    if admin_user.user_id == user_id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Soft delete - just deactivate
    user.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'}), 200


@admin_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@jwt_required()
def admin_reset_password(user_id):
    """Admin reset user password"""
    admin_user = check_admin()
    if not admin_user:
        return jsonify({'error': 'Admin access required'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    new_password = data.get('new_password')
    
    if not new_password or len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'message': 'Password reset successfully'}), 200


@admin_bp.route('/projects', methods=['GET'])
@jwt_required()
def get_all_projects():
    """Get all projects with pagination"""
    admin_user = check_admin()
    if not admin_user:
        return jsonify({'error': 'Admin access required'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    
    query = Project.query
    
    if search:
        query = query.filter(Project.project_name.ilike(f'%{search}%'))
    
    pagination = query.order_by(desc(Project.updated_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Include creator info for each project
    projects_data = []
    for p in pagination.items:
        project_dict = p.to_dict()
        creator = User.query.get(p.created_by)
        project_dict['creator'] = {
            'user_id': creator.user_id,
            'username': creator.username,
            'email': creator.email
        } if creator else None
        projects_data.append(project_dict)
    
    return jsonify({
        'projects': projects_data,
        'total': pagination.total,
        'page': page,
        'pages': pagination.pages
    }), 200


@admin_bp.route('/projects/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """Delete project (admin only)"""
    admin_user = check_admin()
    if not admin_user:
        return jsonify({'error': 'Admin access required'}), 403
    
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Archive instead of delete
    project.is_archived = True
    db.session.commit()
    
    return jsonify({'message': 'Project deleted successfully'}), 200


@admin_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    """Get platform analytics"""
    admin_user = check_admin()
    if not admin_user:
        return jsonify({'error': 'Admin access required'}), 403
    
    # Get date range from query params
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # New users over time
    new_users = db.session.query(
        func.date(User.created_at).label('date'),
        func.count(User.user_id).label('count')
    ).filter(User.created_at >= start_date)\
     .group_by(func.date(User.created_at))\
     .all()
    
    # New projects over time
    new_projects = db.session.query(
        func.date(Project.created_at).label('date'),
        func.count(Project.project_id).label('count')
    ).filter(Project.created_at >= start_date)\
     .group_by(func.date(Project.created_at))\
     .all()
    
    # Messages over time
    messages_over_time = db.session.query(
        func.date(CSpaceMessage.sent_at).label('date'),
        func.count(CSpaceMessage.message_id).label('count')
    ).filter(CSpaceMessage.sent_at >= start_date)\
     .group_by(func.date(CSpaceMessage.sent_at))\
     .all()
    
    # Top users by projects
    top_creators = db.session.query(
        User.username,
        User.user_id,
        func.count(Project.project_id).label('project_count')
    ).join(Project, User.user_id == Project.created_by)\
     .group_by(User.user_id)\
     .order_by(desc('project_count'))\
     .limit(10).all()
    
    return jsonify({
        'new_users': [
            {'date': str(date), 'count': count} for date, count in new_users
        ],
        'new_projects': [
            {'date': str(date), 'count': count} for date, count in new_projects
        ],
        'messages': [
            {'date': str(date), 'count': count} for date, count in messages_over_time
        ],
        'top_creators': [
            {'username': username, 'user_id': user_id, 'projects': count}
            for username, user_id, count in top_creators
        ]
    }), 200


@admin_bp.route('/security/logs', methods=['GET'])
@jwt_required()
def get_security_logs():
    """Get security and activity logs"""
    admin_user = check_admin()
    if not admin_user:
        return jsonify({'error': 'Admin access required'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    try:
        logs = ActivityLog.query.order_by(desc(ActivityLog.created_at))\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'logs': [
                {
                    'id': log.id,
                    'user_id': log.user_id,
                    'username': log.user.username if log.user else 'Unknown',
                    'action': log.action,
                    'description': log.description,
                    'ip_address': log.ip_address if hasattr(log, 'ip_address') else None,
                    'timestamp': log.created_at.isoformat()
                } for log in logs.items
            ],
            'total': logs.total,
            'page': page,
            'pages': logs.pages
        }), 200
    except Exception as e:
        # If ActivityLog doesn't exist, return mock data
        return jsonify({
            'logs': [],
            'total': 0,
            'page': 1,
            'pages': 0
        }), 200


@admin_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_system_settings():
    """Get system settings"""
    admin_user = check_admin()
    if not admin_user:
        return jsonify({'error': 'Admin access required'}), 403
    
    # Get all settings from database
    settings = {}
    db_settings = SystemSetting.query.all()
    
    for setting in db_settings:
        settings[setting.setting_key] = setting.get_value()
    
    # Set defaults if not in database
    defaults = {
        'site_name': 'CineForge AI',
        'maintenance_mode': False,
        'allow_registration': True,
        'require_email_verification': True,
        'max_file_size': 100,
        'max_storage_per_user': 5000,
        'ai_features_enabled': True,
        'collaboration_enabled': True
    }
    
    for key, default_value in defaults.items():
        if key not in settings:
            settings[key] = default_value
    
    return jsonify({'settings': settings}), 200


@admin_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_system_settings():
    """Update system settings"""
    admin_user = check_admin()
    if not admin_user:
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    # Update each setting in database
    for key, value in data.items():
        # Determine type
        if isinstance(value, bool):
            setting_type = 'boolean'
            str_value = 'true' if value else 'false'
        elif isinstance(value, (int, float)):
            setting_type = 'number'
            str_value = str(value)
        else:
            setting_type = 'string'
            str_value = str(value)
        
        # Update or create setting
        setting = SystemSetting.query.filter_by(setting_key=key).first()
        if setting:
            setting.setting_value = str_value
            setting.setting_type = setting_type
            setting.updated_at = datetime.utcnow()
        else:
            setting = SystemSetting(
                setting_key=key,
                setting_value=str_value,
                setting_type=setting_type
            )
            db.session.add(setting)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Settings updated successfully',
        'settings': data
    }), 200


@admin_bp.route('/stats/overview', methods=['GET'])
@jwt_required()
def get_stats_overview():
    """Get quick stats overview"""
    admin_user = check_admin()
    if not admin_user:
        return jsonify({'error': 'Admin access required'}), 403
    
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_projects = Project.query.count()
    active_projects = Project.query.filter_by(is_archived=False).count()
    total_messages = CSpaceMessage.query.count()
    
    # Users this month
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    new_users_this_month = User.query.filter(User.created_at >= month_start).count()
    
    return jsonify({
        'total_users': total_users,
        'active_users': active_users,
        'total_projects': total_projects,
        'active_projects': active_projects,
        'total_messages': total_messages,
        'new_users_this_month': new_users_this_month
    }), 200
