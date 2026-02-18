"""
CineForge AI - Main Application Entry Point
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_migrate import Migrate
from config import config
import os

# Initialize extensions
jwt = JWTManager()
socketio = SocketIO()
migrate = Migrate()

def create_app(config_name=None):
    """Application factory pattern"""
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    from models import db
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    
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
    
    # SocketIO initialization
    socketio.init_app(
        app,
        cors_allowed_origins=app.config['CORS_ORIGINS'],
        message_queue=app.config['SOCKETIO_MESSAGE_QUEUE'],
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
    
    return app


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
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden'}), 403


def register_socketio_events(app):
    """Register SocketIO events"""
    from socketio_events import register_events
    register_events(socketio)


if __name__ == '__main__':
    app = create_app()
    
    # Run with SocketIO
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True
    )
