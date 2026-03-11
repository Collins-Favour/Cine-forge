"""
CineForge AI - Main Application Entry Point
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_migrate import Migrate
from config import config
from utils.logger import setup_logging, get_logger, RequestLogger
import os
import signal
import sys
import traceback

# Initialize logging FIRST
setup_logging()
logger = get_logger('cineforge.app')

# Initialize extensions
jwt = JWTManager()
socketio = SocketIO()
migrate = Migrate()

def create_app(config_name=None):
    """Application factory pattern"""
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    logger.info(f"Creating app with config: {config_name}")
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    from models import db
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    
    # --- JWT Error Callbacks (CRITICAL - prevents crashes on bad tokens) ---
    register_jwt_callbacks(app)
    
    # CORS configuration - Allow all methods including OPTIONS for preflight
    CORS(app, 
         resources={
             r"/api/*": {
                 "origins": app.config['CORS_ORIGINS'],
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                 "allow_headers": ["Content-Type", "Authorization", "Accept"],
                 "expose_headers": ["Content-Type", "Authorization"],
                 "supports_credentials": True,
                 "max_age": 3600
             }
         })
    
    # Add explicit OPTIONS handler for all routes
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin and origin in app.config['CORS_ORIGINS']:
            response.headers.add('Access-Control-Allow-Origin', origin)
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,PATCH')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    
    # --- Request/Response Logging ---
    request_logger = RequestLogger()
    app.before_request(request_logger.log_request)
    app.after_request(request_logger.log_response)
    
    # --- SocketIO initialization (with Redis fallback) ---
    try:
        socketio.init_app(
            app,
            cors_allowed_origins=app.config['CORS_ORIGINS'],
            message_queue=app.config['SOCKETIO_MESSAGE_QUEUE'],
            async_mode=app.config['SOCKETIO_ASYNC_MODE']
        )
        logger.info("SocketIO initialized with Redis message queue")
    except Exception as e:
        logger.warning(f"Redis not available for SocketIO, falling back to no message queue: {e}")
        socketio.init_app(
            app,
            cors_allowed_origins=app.config['CORS_ORIGINS'],
            async_mode=app.config['SOCKETIO_ASYNC_MODE']
        )
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register socketio events
    register_socketio_events(app)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'app': app.config['APP_NAME'],
            'version': app.config['VERSION']
        }), 200
    
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Welcome to CineForge AI API',
            'version': app.config['VERSION'],
            'documentation': '/api/docs'
        }), 200
    
    # Serve uploaded files
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        from flask import send_from_directory
        upload_folder = app.config['UPLOAD_FOLDER']
        return send_from_directory(upload_folder, filename)
    
    logger.info(f"CineForge AI app created successfully (config: {config_name})")
    
    return app


def register_jwt_callbacks(app):
    """Register JWT error handlers to prevent crashes and return proper JSON errors"""
    auth_logger = get_logger('cineforge.auth')
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        auth_logger.warning(f"Expired token used by user {jwt_payload.get('sub', 'unknown')}")
        return jsonify({
            'error': 'Token has expired',
            'error_code': 'token_expired',
            'message': 'Please log in again or refresh your token'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        auth_logger.warning(f"Invalid token received: {error_string}")
        return jsonify({
            'error': 'Invalid token',
            'error_code': 'token_invalid',
            'message': 'The provided token is not valid'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error_string):
        auth_logger.info(f"Missing token on protected route: {error_string}")
        return jsonify({
            'error': 'Authorization required',
            'error_code': 'token_missing',
            'message': 'A valid access token is required'
        }), 401
    
    @jwt.needs_fresh_token_loader
    def needs_fresh_token_callback(jwt_header, jwt_payload):
        auth_logger.info(f"Fresh token needed for user {jwt_payload.get('sub', 'unknown')}")
        return jsonify({
            'error': 'Fresh token required',
            'error_code': 'fresh_token_required',
            'message': 'Please re-authenticate'
        }), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        auth_logger.warning(f"Revoked token used by user {jwt_payload.get('sub', 'unknown')}")
        return jsonify({
            'error': 'Token has been revoked',
            'error_code': 'token_revoked',
            'message': 'Please log in again'
        }), 401
    
    @jwt.token_verification_failed_loader
    def token_verification_failed_callback(jwt_header, jwt_payload):
        auth_logger.error(f"Token verification failed for user {jwt_payload.get('sub', 'unknown')}")
        return jsonify({
            'error': 'Token verification failed',
            'error_code': 'token_verification_failed',
            'message': 'The token could not be verified'
        }), 401


def register_blueprints(app):
    """Register Flask blueprints"""
    from routes.auth import auth_bp
    from routes.projects import projects_bp
    from routes.scripts import scripts_bp
    from routes.scenes import scenes_bp
    from routes.storyboards import storyboards_bp
    from routes.collaboration import collaboration_bp
    from routes.ai import ai_bp
    from routes.users import users_bp
    from routes.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(projects_bp, url_prefix='/api/projects')
    app.register_blueprint(scripts_bp, url_prefix='/api/scripts')
    app.register_blueprint(scenes_bp, url_prefix='/api/scenes')
    app.register_blueprint(storyboards_bp, url_prefix='/api/storyboards')
    app.register_blueprint(collaboration_bp, url_prefix='/api/collaboration')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')


def register_error_handlers(app):
    """Register error handlers with logging"""
    error_logger = get_logger('cineforge.app')
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        error_logger.error(f"Internal server error: {error}", exc_info=True)
        # Rollback any pending DB transactions to prevent corrupt state
        try:
            from models import db
            db.session.rollback()
        except Exception:
            pass
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden'}), 403
    
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({'error': 'Unprocessable entity'}), 422
    
    @app.errorhandler(429)
    def rate_limited(error):
        error_logger.warning(f"Rate limit exceeded from {request.remote_addr}")
        return jsonify({'error': 'Too many requests, please slow down'}), 429
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Catch-all handler to prevent server crashes from unhandled exceptions"""
        error_logger.critical(
            f"UNHANDLED EXCEPTION: {type(error).__name__}: {error}\n"
            f"  Request: {request.method} {request.path}\n"
            f"  IP: {request.remote_addr}",
            exc_info=True
        )
        # Rollback any pending DB transactions
        try:
            from models import db
            db.session.rollback()
        except Exception:
            pass
        return jsonify({'error': 'An unexpected error occurred'}), 500


def register_socketio_events(app):
    """Register SocketIO events"""
    try:
        from socketio_events import register_events
        register_events(socketio)
        logger.info("SocketIO events registered successfully")
    except Exception as e:
        logger.error(f"Failed to register SocketIO events: {e}", exc_info=True)


def graceful_shutdown(signum, frame):
    """Handle shutdown signals gracefully to prevent abrupt termination"""
    sig_name = signal.Signals(signum).name
    logger.info(f"Received signal {sig_name} — shutting down gracefully...")
    
    try:
        from models import db
        db.session.remove()
        logger.info("Database sessions cleaned up")
    except Exception as e:
        logger.warning(f"Error cleaning up DB sessions: {e}")
    
    logger.info("CineForge AI Backend stopped.")
    sys.exit(0)


if __name__ == '__main__':
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)
    
    try:
        app = create_app()
        
        logger.info("Starting CineForge AI Backend on 0.0.0.0:5000")
        
        # Run with SocketIO
        socketio.run(
            app,
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True,
            log_output=True
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user (KeyboardInterrupt)")
    except Exception as e:
        logger.critical(f"SERVER CRASHED: {type(e).__name__}: {e}", exc_info=True)
        logger.critical("Stack trace:\n" + traceback.format_exc())
        sys.exit(1)
