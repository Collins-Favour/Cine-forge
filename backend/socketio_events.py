"""
SocketIO Event Handlers
Real-time communication for C-Space collaboration
"""
from flask_socketio import emit, join_room, leave_room, rooms
from flask_jwt_extended import decode_token
from models import db, CSpaceMessage, User
from utils.logger import get_logger
from datetime import datetime

logger = get_logger('cineforge.socketio')


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
                
                # Join user to their personal notification room
                user_room = f'user_{user_id}'
                join_room(user_room)
                
                logger.info(f'User {user_id} connected and joined room {user_room}')
                emit('connected', {'message': 'Connected successfully', 'user_id': user_id})
            else:
                logger.warning("WebSocket connection rejected: no auth token provided")
                return False  # Reject connection
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}", exc_info=True)
            return False
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        logger.info('Client disconnected')
    
    @socketio.on('join_project')
    def handle_join_project(data):
        """Join a project room for real-time updates"""
        try:
            project_id = data.get('project_id')
            if project_id:
                room = f'project_{project_id}'
                join_room(room)
                logger.info(f"Client joined project room: {room}")
                emit('joined_project', {'project_id': project_id, 'room': room})
        except Exception as e:
            logger.error(f"Error joining project room: {e}", exc_info=True)
    
    @socketio.on('leave_project')
    def handle_leave_project(data):
        """Leave a project room"""
        try:
            project_id = data.get('project_id')
            if project_id:
                room = f'project_{project_id}'
                leave_room(room)
                logger.info(f"Client left project room: {room}")
                emit('left_project', {'project_id': project_id})
        except Exception as e:
            logger.error(f"Error leaving project room: {e}", exc_info=True)
    
    @socketio.on('send_message')
    def handle_send_message(data):
        """Broadcast message to project room (message already saved via REST API)"""
        try:
            # Get user info
            from models import User
            user = User.query.get(data['user_id'])
            
            # Broadcast to project room (don't save to DB, REST API already did)
            room = f'project_{data["project_id"]}'
            emit('new_message', {
                'message': data,
                'user': user.to_dict() if user else None
            }, room=room)
            
            logger.debug(f"Message broadcast to room {room} from user {data.get('user_id')}")
            
        except Exception as e:
            logger.error(f"Message broadcast error: {e}", exc_info=True)
            emit('error', {'message': 'Failed to broadcast message'})
    
    @socketio.on('typing')
    def handle_typing(data):
        """Handle typing indicator"""
        try:
            room = f'project_{data["project_id"]}'
            emit('user_typing', {
                'user_id': data['user_id'],
                'username': data.get('username')
            }, room=room, include_self=False)
        except Exception as e:
            logger.error(f"Typing indicator error: {e}")
    
    @socketio.on('stop_typing')
    def handle_stop_typing(data):
        """Handle stop typing indicator"""
        try:
            room = f'project_{data["project_id"]}'
            emit('user_stopped_typing', {
                'user_id': data['user_id']
            }, room=room, include_self=False)
        except Exception as e:
            logger.error(f"Stop typing indicator error: {e}")
    
    @socketio.on('ai_generation_update')
    def handle_ai_update(data):
        """Broadcast AI generation progress"""
        try:
            room = f'project_{data["project_id"]}'
            emit('ai_progress', {
                'status': data['status'],
                'progress': data.get('progress', 0),
                'entity_type': data.get('entity_type'),
                'entity_id': data.get('entity_id')
            }, room=room)
        except Exception as e:
            logger.error(f"AI update broadcast error: {e}")
