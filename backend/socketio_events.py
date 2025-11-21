"""
SocketIO Event Handlers
Real-time communication for C-Space collaboration
"""
from flask_socketio import emit, join_room, leave_room, rooms
from flask_jwt_extended import decode_token
from models import db, CSpaceMessage, User
from datetime import datetime


def register_events(socketio):
    """Register all SocketIO event handlers"""
    
    @socketio.on('connect')
    def handle_connect(auth):
        """Handle client connection"""
        try:
            # Verify JWT token
            if auth and 'token' in auth:
                token = auth['token']
                decoded = decode_token(token)
                user_id = decoded['sub']
                
                emit('connected', {'message': 'Connected successfully', 'user_id': user_id})
            else:
                return False  # Reject connection
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        print('Client disconnected')
    
    @socketio.on('join_project')
    def handle_join_project(data):
        """Join a project room for real-time updates"""
        project_id = data.get('project_id')
        if project_id:
            room = f'project_{project_id}'
            join_room(room)
            emit('joined_project', {'project_id': project_id, 'room': room})
    
    @socketio.on('leave_project')
    def handle_leave_project(data):
        """Leave a project room"""
        project_id = data.get('project_id')
        if project_id:
            room = f'project_{project_id}'
            leave_room(room)
            emit('left_project', {'project_id': project_id})
    
    @socketio.on('send_message')
    def handle_send_message(data):
        """Handle new C-Space message"""
        try:
            # Create message in database
            message = CSpaceMessage(
                project_id=data['project_id'],
                user_id=data['user_id'],
                message_content=data['message_content'],
                message_type=data.get('message_type', 'text'),
                parent_message_id=data.get('parent_message_id'),
                referenced_scene_id=data.get('referenced_scene_id'),
                referenced_panel_id=data.get('referenced_panel_id')
            )
            db.session.add(message)
            db.session.commit()
            
            # Get user info
            user = User.query.get(data['user_id'])
            
            # Broadcast to project room
            room = f'project_{data["project_id"]}'
            emit('new_message', {
                'message': message.to_dict(),
                'user': user.to_dict() if user else None
            }, room=room)
            
        except Exception as e:
            print(f"Message error: {e}")
            emit('error', {'message': 'Failed to send message'})
    
    @socketio.on('typing')
    def handle_typing(data):
        """Handle typing indicator"""
        room = f'project_{data["project_id"]}'
        emit('user_typing', {
            'user_id': data['user_id'],
            'username': data.get('username')
        }, room=room, include_self=False)
    
    @socketio.on('stop_typing')
    def handle_stop_typing(data):
        """Handle stop typing indicator"""
        room = f'project_{data["project_id"]}'
        emit('user_stopped_typing', {
            'user_id': data['user_id']
        }, room=room, include_self=False)
    
    @socketio.on('ai_generation_update')
    def handle_ai_update(data):
        """Broadcast AI generation progress"""
        room = f'project_{data["project_id"]}'
        emit('ai_progress', {
            'status': data['status'],
            'progress': data.get('progress', 0),
            'entity_type': data.get('entity_type'),
            'entity_id': data.get('entity_id')
        }, room=room)
