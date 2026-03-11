"""
Collaboration and C-Space Routes
Handles real-time messaging, comments, and team collaboration
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, CSpaceMessage, MessageReaction, Notification
from utils.decorators import validate_request, project_permission_required
from utils.helpers import paginate_query
from utils.logger import get_logger
from datetime import datetime

logger = get_logger('cineforge.api')
collaboration_bp = Blueprint('collaboration', __name__)


@collaboration_bp.route('/project/<int:project_id>/messages', methods=['GET'])
@jwt_required()
@project_permission_required('viewer')
def get_messages(project_id):
    """Get C-Space messages for project"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    channel = request.args.get('channel', 'general')
    
    query = CSpaceMessage.query.filter_by(
        project_id=project_id, 
        parent_message_id=None,
        channel=channel
    ).order_by(CSpaceMessage.sent_at.desc())
    
    result = paginate_query(query, page, per_page)
    
    messages_with_users = []
    for msg in result['items']:
        msg_data = msg.to_dict(include_replies=True)
        from models import User
        user = User.query.get(msg.user_id)
        msg_data['user'] = user.to_dict() if user else None
        messages_with_users.append(msg_data)
    
    return jsonify({
        'messages': messages_with_users,
        'pagination': result['pagination']
    }), 200


@collaboration_bp.route('/project/<int:project_id>/messages', methods=['POST'])
@jwt_required()
@project_permission_required('viewer')
@validate_request(['message_content'])
def create_message(project_id):
    """Create new C-Space message"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    message = CSpaceMessage(
        project_id=project_id,
        user_id=user_id,
        message_content=data['message_content'],
        message_type=data.get('message_type', 'text'),
        channel=data.get('channel', 'general'),
        parent_message_id=data.get('parent_message_id'),
        attached_file_url=data.get('attached_file_url'),
        attached_thumbnail=data.get('attached_thumbnail'),
        referenced_scene_id=data.get('referenced_scene_id'),
        referenced_panel_id=data.get('referenced_panel_id'),
        annotation_data=data.get('annotation_data')
    )
    
    db.session.add(message)
    db.session.commit()
    
    # Get sender info for broadcasting
    from models import ProjectCollaborator, User
    sender = User.query.get(user_id)
    
    # Broadcast message via SocketIO
    from flask import current_app
    socketio = current_app.extensions.get('socketio')
    if socketio:
        room = f'project_{project_id}'
        socketio.emit('new_message', {
            'message': message.to_dict(),
            'user': sender.to_dict() if sender else None
        }, room=room)
    
    # Notify project collaborators (except sender)
    collaborators = ProjectCollaborator.query.filter_by(project_id=project_id)\
        .filter(ProjectCollaborator.user_id != user_id).all()
    
    for collab in collaborators:
        notification = Notification(
            user_id=collab.user_id,
            notification_type='message',
            title=f'New message from {sender.username}',
            message=data['message_content'][:100],
            link_url=f'/projects/{project_id}/c-space'
        )
        db.session.add(notification)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Message sent successfully',
        'cspace_message': message.to_dict()
    }), 201


@collaboration_bp.route('/messages/<int:message_id>', methods=['PUT'])
@jwt_required()
def update_message(message_id):
    """Edit message"""
    user_id = int(get_jwt_identity())
    message = CSpaceMessage.query.get(message_id)
    
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    if message.user_id != user_id:
        return jsonify({'error': 'Cannot edit others messages'}), 403
    
    data = request.get_json()
    
    if 'message_content' in data:
        message.message_content = data['message_content']
        message.is_edited = True
        message.edited_at = datetime.utcnow()
    
    if 'is_resolved' in data:
        message.is_resolved = data['is_resolved']
    
    if 'is_pinned' in data:
        message.is_pinned = data['is_pinned']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Message updated',
        'cspace_message': message.to_dict()
    }), 200


@collaboration_bp.route('/messages/<int:message_id>', methods=['DELETE'])
@jwt_required()
def delete_message(message_id):
    """Delete message"""
    user_id = int(get_jwt_identity())
    message = CSpaceMessage.query.get(message_id)
    
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    if message.user_id != user_id:
        # Check if user is project owner
        from models import ProjectCollaborator
        collab = ProjectCollaborator.query.filter_by(
            project_id=message.project_id,
            user_id=user_id,
            role='owner'
        ).first()
        
        if not collab:
            return jsonify({'error': 'Cannot delete others messages'}), 403
    
    db.session.delete(message)
    db.session.commit()
    
    return jsonify({'message': 'Message deleted'}), 200


@collaboration_bp.route('/messages/<int:message_id>/reactions', methods=['POST'])
@jwt_required()
@validate_request(['reaction_type'])
def add_reaction(message_id):
    """Add reaction to message"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    message = CSpaceMessage.query.get(message_id)
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    # Check if reaction already exists
    existing = MessageReaction.query.filter_by(
        message_id=message_id,
        user_id=user_id,
        reaction_type=data['reaction_type']
    ).first()
    
    if existing:
        return jsonify({'error': 'Reaction already added'}), 409
    
    reaction = MessageReaction(
        message_id=message_id,
        user_id=user_id,
        reaction_type=data['reaction_type']
    )
    
    db.session.add(reaction)
    db.session.commit()
    
    return jsonify({
        'message': 'Reaction added',
        'reaction': reaction.to_dict()
    }), 201


@collaboration_bp.route('/messages/<int:message_id>/reactions/<int:reaction_id>', methods=['DELETE'])
@jwt_required()
def remove_reaction(message_id, reaction_id):
    """Remove reaction from message"""
    user_id = int(get_jwt_identity())
    
    reaction = MessageReaction.query.filter_by(
        reaction_id=reaction_id,
        message_id=message_id,
        user_id=user_id
    ).first()
    
    if not reaction:
        return jsonify({'error': 'Reaction not found'}), 404
    
    db.session.delete(reaction)
    db.session.commit()
    
    return jsonify({'message': 'Reaction removed'}), 200


@collaboration_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get user notifications"""
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    
    logger.debug(f"Fetching notifications for user_id: {user_id}, unread_only: {unread_only}")
    
    query = Notification.query.filter(Notification.user_id == user_id)
    
    if unread_only:
        query = query.filter_by(is_read=False)
    
    query = query.order_by(Notification.created_at.desc())
    
    result = paginate_query(query, page, per_page)
    
    notifications_list = [n.to_dict() for n in result['items']]
    logger.debug(f"Returning {len(notifications_list)} notifications to user {user_id}")
    
    if notifications_list:
        logger.debug(f"   First notification: {notifications_list[0].get('title', 'N/A')}")
    
    return jsonify({
        'notifications': notifications_list,
        'pagination': result['pagination']
    }), 200


@collaboration_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    """Mark notification as read"""
    user_id = int(get_jwt_identity())
    
    notification = Notification.query.filter_by(
        notification_id=notification_id,
        user_id=user_id
    ).first()
    
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    notification.mark_as_read()
    db.session.commit()
    
    return jsonify({'message': 'Notification marked as read'}), 200


@collaboration_bp.route('/notifications/read-all', methods=['POST'])
@jwt_required()
def mark_all_notifications_read():
    """Mark all notifications as read"""
    user_id = int(get_jwt_identity())
    
    Notification.query.filter_by(user_id=user_id, is_read=False)\
        .update({'is_read': True, 'read_at': datetime.utcnow()})
    
    db.session.commit()
    
    return jsonify({'message': 'All notifications marked as read'}), 200


@collaboration_bp.route('/project/<int:project_id>/upload-file', methods=['POST'])
@jwt_required()
@project_permission_required('viewer')
def upload_file(project_id):
    """Upload file for C-Space messages"""
    import os
    from werkzeug.utils import secure_filename
    from config import Config
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file size (10MB max)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    if file_size > 10 * 1024 * 1024:  # 10MB
        return jsonify({'error': 'File size must be less than 10MB'}), 400
    
    # Allowed file extensions
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'doc', 'docx', 'txt', 'mp4', 'mov', 'avi', 'mp3', 'wav'}
    
    filename = secure_filename(file.filename)
    file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    if file_ext not in allowed_extensions:
        return jsonify({'error': f'File type .{file_ext} not allowed. Allowed types: {', '.join(allowed_extensions)}'}), 400
    
    # Create unique filename
    user_id = int(get_jwt_identity())
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    unique_filename = f"project_{project_id}_user_{user_id}_{timestamp}_{filename}"
    
    # Ensure upload directory exists
    upload_folder = os.path.join(Config.UPLOAD_FOLDER, 'cspace', str(project_id))
    os.makedirs(upload_folder, exist_ok=True)
    
    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)
    
    # Generate URL (relative path)
    file_url = f"/uploads/cspace/{project_id}/{unique_filename}"
    
    # Generate thumbnail for images
    thumbnail_url = None
    image_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    if file_ext in image_extensions:
        thumbnail_url = file_url  # For now, use same URL; could generate actual thumbnail
    
    return jsonify({
        'message': 'File uploaded successfully',
        'file_url': file_url,
        'thumbnail_url': thumbnail_url,
        'filename': unique_filename,
        'original_filename': filename,
        'file_size': file_size,
        'file_type': file_ext
    }), 200
