"""
Authentication Routes
Handles user registration, login, logout, password reset
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt
)
from models import db, User, UserSession
from utils.validators import validate_email, validate_password
from utils.decorators import validate_request
from utils.helpers import log_activity
from utils.logger import get_logger
from datetime import datetime, timedelta
from collections import defaultdict
import secrets
import time

auth_bp = Blueprint('auth', __name__)
logger = get_logger('cineforge.auth')

# --- Simple in-memory rate limiter (no Redis dependency) ---
_rate_limit_store = defaultdict(list)
RATE_LIMIT_WINDOW = 60       # seconds
RATE_LIMIT_MAX_ATTEMPTS = 10  # max attempts per IP per window

def _check_rate_limit(ip_address):
    """
    Check if IP has exceeded rate limit.
    Returns True if allowed, False if rate-limited.
    """
    now = time.time()
    # Clean old entries
    _rate_limit_store[ip_address] = [
        t for t in _rate_limit_store[ip_address] if now - t < RATE_LIMIT_WINDOW
    ]
    
    if len(_rate_limit_store[ip_address]) >= RATE_LIMIT_MAX_ATTEMPTS:
        return False
    
    _rate_limit_store[ip_address].append(now)
    return True


@auth_bp.route('/register', methods=['POST'])
@validate_request(['username', 'email', 'password'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Rate limiting
    if not _check_rate_limit(request.remote_addr):
        logger.warning(f"Rate limit exceeded for registration from IP {request.remote_addr}")
        return jsonify({'error': 'Too many requests. Please wait before trying again.'}), 429
    
    logger.info(f"Registration attempt for email={data.get('email')}, username={data.get('username')}")
    
    # Validate email format
    if not validate_email(data['email']):
        logger.info(f"Registration rejected: invalid email format ({data.get('email')})")
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Validate password strength
    is_valid, message = validate_password(data['password'])
    if not is_valid:
        logger.info(f"Registration rejected: weak password for {data.get('email')}")
        return jsonify({'error': message}), 400
    
    # Check if user exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 409
    
    # Handle full_name field for backward compatibility
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    
    # If full_name is provided instead of first_name/last_name, split it
    if not first_name and not last_name and data.get('full_name'):
        name_parts = data['full_name'].strip().split(None, 1)
        first_name = name_parts[0] if len(name_parts) > 0 else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        first_name=first_name,
        last_name=last_name,
        role=data.get('role', 'filmmaker')
    )
    user.set_password(data['password'])
    user.verification_token = secrets.token_urlsafe(32)
    
    db.session.add(user)
    db.session.commit()
    
    logger.info(f"User registered successfully: id={user.user_id}, email={user.email}, username={user.username}")
    
    # Log registration activity
    log_activity(None, user.user_id, 'register', f'New user registered: {user.username}',
                 entity_type='user', entity_id=user.user_id, ip_address=request.remote_addr)
    db.session.commit()
    
    # Create JWT tokens for immediate login after registration
    access_token = create_access_token(identity=str(user.user_id))
    refresh_token = create_refresh_token(identity=str(user.user_id))
    
    # TODO: Send verification email
    
    return jsonify({
        'message': 'Registration successful',
        'user': user.to_dict(include_email=True),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201


@auth_bp.route('/login', methods=['POST'])
@validate_request(['email', 'password'])
def login():
    """User login"""
    data = request.get_json()
    
    # Rate limiting
    if not _check_rate_limit(request.remote_addr):
        logger.warning(f"Rate limit exceeded for login from IP {request.remote_addr}")
        return jsonify({'error': 'Too many login attempts. Please wait before trying again.'}), 429
    
    logger.info(f"Login attempt for email={data.get('email')} from IP={request.remote_addr}")
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        logger.warning(f"Failed login attempt for email={data.get('email')} from IP={request.remote_addr}")
        # Log failed login attempt
        log_activity(None, user.user_id if user else None, 'login_failed',
                     f'Failed login attempt for {data.get("email")}',
                     entity_type='auth', ip_address=request.remote_addr)
        db.session.commit()
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if not user.is_active:
        logger.warning(f"Login attempt on deactivated account: user_id={user.user_id}")
        log_activity(None, user.user_id, 'login_deactivated',
                     f'Login attempt on deactivated account: {user.username}',
                     entity_type='auth', ip_address=request.remote_addr)
        db.session.commit()
        return jsonify({'error': 'Account is deactivated'}), 403
    
    # Update last login
    user.last_login = datetime.utcnow()
    
    # Create JWT tokens
    access_token = create_access_token(identity=str(user.user_id))
    refresh_token = create_refresh_token(identity=str(user.user_id))
    
    # Create session
    session = UserSession(
        user_id=user.user_id,
        session_token=secrets.token_urlsafe(32),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    
    db.session.add(session)
    
    # Log successful login
    log_activity(None, user.user_id, 'login',
                 f'User logged in: {user.username}',
                 entity_type='auth', ip_address=request.remote_addr)
    db.session.commit()
    
    logger.info(f"User logged in successfully: user_id={user.user_id}, email={user.email}")
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict(include_email=True)
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    user_id = get_jwt_identity()
    
    # Verify the user still exists and is active
    user = User.query.get(int(user_id))
    if not user:
        logger.warning(f"Token refresh failed: user {user_id} not found")
        return jsonify({'error': 'User not found', 'error_code': 'user_not_found'}), 401
    
    if not user.is_active:
        logger.warning(f"Token refresh failed: user {user_id} is deactivated")
        return jsonify({'error': 'Account is deactivated', 'error_code': 'account_deactivated'}), 403
    
    access_token = create_access_token(identity=user_id)
    
    logger.info(f"Token refreshed for user_id={user_id}")
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict(include_email=True)
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout - clean up sessions"""
    user_id = get_jwt_identity()
    
    try:
        # Clean up expired/old sessions for this user
        UserSession.query.filter(
            UserSession.user_id == int(user_id),
            UserSession.expires_at < datetime.utcnow()
        ).delete()
        
        # Log logout activity
        log_activity(None, int(user_id), 'logout', 'User logged out',
                     entity_type='auth', ip_address=request.remote_addr)
        db.session.commit()
        
        logger.info(f"User logged out: user_id={user_id}")
    except Exception as e:
        logger.error(f"Error during logout cleanup for user {user_id}: {e}")
        db.session.rollback()
    
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/forgot-password', methods=['POST'])
@validate_request(['email'])
def forgot_password():
    """Request password reset"""
    data = request.get_json()
    
    # Rate limiting
    if not _check_rate_limit(request.remote_addr):
        logger.warning(f"Rate limit exceeded for password reset from IP {request.remote_addr}")
        return jsonify({'error': 'Too many requests. Please wait before trying again.'}), 429
    
    user = User.query.filter_by(email=data['email']).first()
    
    if user:
        user.reset_token = secrets.token_urlsafe(32)
        user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        
        logger.info(f"Password reset requested for user_id={user.user_id}")
        # TODO: Send reset email
    
    # Always return success to prevent email enumeration
    return jsonify({'message': 'If the email exists, a reset link has been sent'}), 200


@auth_bp.route('/reset-password', methods=['POST'])
@validate_request(['token', 'new_password'])
def reset_password():
    """Reset password with token"""
    data = request.get_json()
    
    user = User.query.filter_by(reset_token=data['token']).first()
    
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        return jsonify({'error': 'Invalid or expired reset token'}), 400
    
    # Validate new password
    is_valid, message = validate_password(data['new_password'])
    if not is_valid:
        return jsonify({'error': message}), 400
    
    user.set_password(data['new_password'])
    user.reset_token = None
    user.reset_token_expiry = None
    db.session.commit()
    
    logger.info(f"Password reset completed for user_id={user.user_id}")
    
    return jsonify({'message': 'Password reset successful'}), 200


@auth_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """Verify user email"""
    user = User.query.filter_by(verification_token=token).first()
    
    if not user:
        return jsonify({'error': 'Invalid verification token'}), 400
    
    user.is_verified = True
    user.verification_token = None
    db.session.commit()
    
    logger.info(f"Email verified for user_id={user.user_id}")
    
    return jsonify({'message': 'Email verified successfully'}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict(include_email=True)}), 200
