"""
Admin Routes
Handles admin dashboard, user management, system settings, and analytics
"""
from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Project, CSpaceMessage, ActivityLog, UsageAnalytics
from models.system import SystemSetting
from utils.logger import get_logger
from utils.helpers import log_activity
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import csv
import io

logger = get_logger('cineforge.api')
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
    """Get admin dashboard statistics - optimized for instant loading"""
    admin_user = check_admin()
    if not admin_user:
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # Use efficient aggregation queries
        # Total users
        total_users = db.session.query(func.count(User.user_id)).filter_by(is_active=True).scalar() or 0
        
        # Users by role - single query
        users_by_role = dict(
            db.session.query(User.role, func.count(User.user_id))
            .filter_by(is_active=True)
            .group_by(User.role)
            .all()
        )
        
        # Active projects count - single query
        active_projects = db.session.query(func.count(Project.project_id)).filter_by(is_archived=False).scalar() or 0
        
        # Storage calculation (mock for now)
        storage_used = round(active_projects * 0.5, 2)  # Mock: 0.5GB per project
        
        # System alerts (mock)
        system_alerts = 0
        
        # Recent users (last 10) - optimized with selected columns only
        recent_users = db.session.query(
            User.user_id,
            User.username,
            User.first_name,
            User.last_name,
            User.email,
            User.role,
            User.is_active,
            User.is_verified,
            User.created_at
        ).order_by(desc(User.created_at)).limit(10).all()
        
        # Recent activity - optimized with limit and eager loading
        recent_activity = []
        try:
            activities = db.session.query(
                ActivityLog.activity_description,
                ActivityLog.created_at,
                User.username
            ).join(User, ActivityLog.user_id == User.user_id, isouter=True)\
             .order_by(desc(ActivityLog.created_at))\
             .limit(10).all()
            
            recent_activity = [
                {
                    'description': f"{username or 'User'} - {desc}",
                    'timestamp': created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else ''
                } for desc, created_at, username in activities
            ]
        except Exception as e:
            logger.warning(f"Activity log error: {e}")
            recent_activity = []
        
        return jsonify({
            'total_users': total_users,
            'users_by_role': users_by_role,
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
    except Exception as e:
        logger.error(f"Dashboard error: {e}", exc_info=True)
        # Return basic data even if there's an error
        return jsonify({
            'total_users': 0,
            'users_by_role': {},
            'active_projects': 0,
            'storage_used': 0,
            'system_alerts': 0,
            'recent_users': [],
            'recent_activity': []
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
                'action': a.activity_type,
                'description': a.activity_description,
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
                'project_name': p.title,
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


@admin_bp.route('/users/<int:user_id>/deactivate', methods=['PATCH'])
@jwt_required()
def deactivate_user(user_id):
    """Deactivate user (admin only)"""
    admin_user = check_admin()
    if not admin_user:
        return jsonify({'error': 'Admin access required'}), 403
    
    if admin_user.user_id == user_id:
        return jsonify({'error': 'Cannot deactivate your own account'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Deactivate user
    user.is_active = False
    log_activity(None, admin_user.user_id, 'account_deactivated',
                 f'Admin deactivated user: {user.username} (ID: {user_id})',
                 entity_type='user', entity_id=user_id, ip_address=request.remote_addr)
    db.session.commit()
    
    return jsonify({'message': 'User deactivated successfully'}), 200


@admin_bp.route('/users/<int:user_id>/activate', methods=['PATCH'])
@jwt_required()
def activate_user(user_id):
    """Activate/reactivate user (admin only)"""
    admin_user = check_admin()
    if not admin_user:
        return jsonify({'error': 'Admin access required'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Activate user
    user.is_active = True
    log_activity(None, admin_user.user_id, 'account_activated',
                 f'Admin activated user: {user.username} (ID: {user_id})',
                 entity_type='user', entity_id=user_id, ip_address=request.remote_addr)
    db.session.commit()
    
    return jsonify({'message': 'User activated successfully'}), 200


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Permanently delete user from database (admin only)"""
    admin_user = check_admin()
    if not admin_user:
        return jsonify({'error': 'Admin access required'}), 403
    
    if admin_user.user_id == user_id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Permanently delete user from database
    # Note: Related records will be handled by cascade rules in the database schema
    username = user.username
    db.session.delete(user)
    log_activity(None, admin_user.user_id, 'user_deleted',
                 f'Admin permanently deleted user: {username} (ID: {user_id})',
                 entity_type='user', entity_id=user_id, ip_address=request.remote_addr)
    db.session.commit()
    
    return jsonify({'message': 'User permanently deleted'}), 200


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
    log_activity(None, admin_user.user_id, 'password_reset',
                 f'Admin reset password for user: {user.username} (ID: {user_id})',
                 entity_type='user', entity_id=user_id, ip_address=request.remote_addr)
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
        query = query.filter(Project.title.ilike(f'%{search}%'))
    
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
    log_type = request.args.get('type', '')  # filter by activity_type
    
    try:
        query = ActivityLog.query
        
        # Optional log type filter
        if log_type:
            query = query.filter(ActivityLog.activity_type.ilike(f'%{log_type}%'))
        
        logs = query.order_by(desc(ActivityLog.created_at))\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'logs': [
                {
                    'id': log.activity_id,
                    'user_id': log.user_id,
                    'username': log.user.username if log.user else 'System',
                    'action': log.activity_type,
                    'description': log.activity_description,
                    'ip_address': log.ip_address,
                    'entity_type': log.entity_type,
                    'project_id': log.project_id,
                    'timestamp': log.created_at.isoformat() if log.created_at else None
                } for log in logs.items
            ],
            'total': logs.total,
            'page': page,
            'pages': logs.pages
        }), 200
    except Exception as e:
        logger.error(f"Security logs error: {e}", exc_info=True)
        return jsonify({
            'logs': [],
            'total': 0,
            'page': 1,
            'pages': 0
        }), 200


@admin_bp.route('/security/stats', methods=['GET'])
@jwt_required()
def get_security_stats():
    """Get security statistics for the admin dashboard"""
    admin_user = check_admin()
    if not admin_user:
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Total events
        total_events = db.session.query(func.count(ActivityLog.activity_id)).scalar() or 0
        
        # Security alerts (failed logins, deactivations, etc.)
        security_alerts = db.session.query(func.count(ActivityLog.activity_id)).filter(
            ActivityLog.activity_type.in_(['login_failed', 'account_deactivated', 'rate_limit_exceeded'])
        ).scalar() or 0
        
        # Active users today (unique users who logged in today)
        active_users_today = db.session.query(func.count(func.distinct(ActivityLog.user_id))).filter(
            ActivityLog.activity_type == 'login',
            ActivityLog.created_at >= today_start
        ).scalar() or 0
        
        # Failed logins today
        failed_logins = db.session.query(func.count(ActivityLog.activity_id)).filter(
            ActivityLog.activity_type == 'login_failed',
            ActivityLog.created_at >= today_start
        ).scalar() or 0
        
        # Events today
        events_today = db.session.query(func.count(ActivityLog.activity_id)).filter(
            ActivityLog.created_at >= today_start
        ).scalar() or 0
        
        # Recent registrations today
        registrations_today = db.session.query(func.count(ActivityLog.activity_id)).filter(
            ActivityLog.activity_type == 'register',
            ActivityLog.created_at >= today_start
        ).scalar() or 0
        
        return jsonify({
            'total_events': total_events,
            'security_alerts': security_alerts,
            'active_users_today': active_users_today,
            'failed_logins': failed_logins,
            'events_today': events_today,
            'registrations_today': registrations_today
        }), 200
    except Exception as e:
        logger.error(f"Security stats error: {e}", exc_info=True)
        return jsonify({
            'total_events': 0,
            'security_alerts': 0,
            'active_users_today': 0,
            'failed_logins': 0,
            'events_today': 0,
            'registrations_today': 0
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
    """Get quick stats overview - optimized"""
    admin_user = check_admin()
    if not admin_user:
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # Use scalar queries for efficiency
        total_users = db.session.query(func.count(User.user_id)).scalar() or 0
        active_users = db.session.query(func.count(User.user_id)).filter_by(is_active=True).scalar() or 0
        total_projects = db.session.query(func.count(Project.project_id)).scalar() or 0
        active_projects = db.session.query(func.count(Project.project_id)).filter_by(is_archived=False).scalar() or 0
        total_messages = db.session.query(func.count(CSpaceMessage.message_id)).scalar() or 0
        
        # Users this month
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_users_this_month = db.session.query(func.count(User.user_id))\
            .filter(User.created_at >= month_start).scalar() or 0
        
        return jsonify({
            'total_users': total_users,
            'active_users': active_users,
            'total_projects': total_projects,
            'active_projects': active_projects,
            'total_messages': total_messages,
            'new_users_this_month': new_users_this_month
        }), 200
    except Exception as e:
        logger.error(f"Stats overview error: {e}", exc_info=True)
        return jsonify({
            'total_users': 0,
            'active_users': 0,
            'total_projects': 0,
            'active_projects': 0,
            'total_messages': 0,
            'new_users_this_month': 0
        }), 200


@admin_bp.route('/export/users', methods=['GET'])
@jwt_required()
def export_users_csv():
    """Export all users to CSV"""
    admin_user = check_admin()
    if not admin_user:
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # Get all users
        users = User.query.order_by(User.created_at.desc()).all()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'User ID', 'Username', 'Email', 'First Name', 'Last Name',
            'Role', 'Is Active', 'Is Verified', 'Created At', 'Last Login'
        ])
        
        # Write data
        for user in users:
            writer.writerow([
                user.user_id,
                user.username,
                user.email,
                user.first_name or '',
                user.last_name or '',
                user.role,
                'Yes' if user.is_active else 'No',
                'Yes' if user.is_verified else 'No',
                user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else '',
                user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never'
            ])
        
        # Create response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=users_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
    except Exception as e:
        logger.error(f"Export users error: {e}", exc_info=True)
        return jsonify({'error': 'Failed to export users'}), 500


@admin_bp.route('/export/analytics', methods=['GET'])
@jwt_required()
def export_analytics_csv():
    """Export analytics report to CSV"""
    admin_user = check_admin()
    if not admin_user:
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get analytics data
        new_users = db.session.query(
            func.date(User.created_at).label('date'),
            func.count(User.user_id).label('count')
        ).filter(User.created_at >= start_date)\
         .group_by(func.date(User.created_at))\
         .all()
        
        new_projects = db.session.query(
            func.date(Project.created_at).label('date'),
            func.count(Project.project_id).label('count')
        ).filter(Project.created_at >= start_date)\
         .group_by(func.date(Project.created_at))\
         .all()
        
        messages_over_time = db.session.query(
            func.date(CSpaceMessage.sent_at).label('date'),
            func.count(CSpaceMessage.message_id).label('count')
        ).filter(CSpaceMessage.sent_at >= start_date)\
         .group_by(func.date(CSpaceMessage.sent_at))\
         .all()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write analytics summary
        writer.writerow(['CineForge AI - Analytics Report'])
        writer.writerow(['Date Range:', f'Last {days} days'])
        writer.writerow(['Generated:', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        
        # New Users section
        writer.writerow(['New Users by Date'])
        writer.writerow(['Date', 'Count'])
        for date, count in new_users:
            writer.writerow([str(date), count])
        writer.writerow([])
        
        # New Projects section
        writer.writerow(['New Projects by Date'])
        writer.writerow(['Date', 'Count'])
        for date, count in new_projects:
            writer.writerow([str(date), count])
        writer.writerow([])
        
        # Messages section
        writer.writerow(['Messages by Date'])
        writer.writerow(['Date', 'Count'])
        for date, count in messages_over_time:
            writer.writerow([str(date), count])
        
        # Create response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=analytics_report_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
    except Exception as e:
        logger.error(f"Export analytics error: {e}", exc_info=True)
        return jsonify({'error': 'Failed to export analytics'}), 500


@admin_bp.route('/export/projects', methods=['GET'])
@jwt_required()
def export_projects_csv():
    """Export all projects to CSV"""
    admin_user = check_admin()
    if not admin_user:
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # Get all projects with creator info
        projects = db.session.query(
            Project.project_id,
            Project.title,
            Project.genre,
            Project.production_stage,
            Project.is_archived,
            Project.created_at,
            User.username
        ).join(User, Project.created_by == User.user_id)\
         .order_by(Project.created_at.desc()).all()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Project ID', 'Title', 'Genre', 'Production Stage',
            'Creator', 'Status', 'Created At'
        ])
        
        # Write data
        for proj_id, title, genre, stage, archived, created_at, username in projects:
            writer.writerow([
                proj_id,
                title,
                genre or 'N/A',
                stage or 'concept',
                username,
                'Archived' if archived else 'Active',
                created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else ''
            ])
        
        # Create response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=projects_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
    except Exception as e:
        logger.error(f"Export projects error: {e}", exc_info=True)
        return jsonify({'error': 'Failed to export projects'}), 500
