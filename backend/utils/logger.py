"""
Logging configuration for CineForge AI Backend
Provides structured logging with file rotation and console output
"""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime


def setup_logging(app=None, log_level=None):
    """
    Configure application-wide logging with file and console handlers.
    
    Args:
        app: Flask app instance (optional - for app-specific config)
        log_level: Override log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Determine log level
    if log_level is None:
        env = os.getenv('FLASK_ENV', 'development')
        if env == 'production':
            log_level = logging.WARNING
        elif env == 'testing':
            log_level = logging.DEBUG
        else:
            log_level = logging.DEBUG
    elif isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper(), logging.DEBUG)
    
    # Create logs directory
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # --- Formatters ---
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)-25s | %(funcName)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    error_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s\n'
            '  → File: %(pathname)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # --- Handlers ---
    
    # Console handler (always active)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(simple_formatter)
    
    # Main application log (rotating, 10MB max, keep 5 backups)
    app_log_file = os.path.join(log_dir, 'cineforge.log')
    app_file_handler = RotatingFileHandler(
        app_log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8'
    )
    app_file_handler.setLevel(log_level)
    app_file_handler.setFormatter(detailed_formatter)
    
    # Error-only log (separate file for easy monitoring)
    error_log_file = os.path.join(log_dir, 'errors.log')
    error_file_handler = RotatingFileHandler(
        error_log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8'
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(error_formatter)
    
    # Auth-specific log
    auth_log_file = os.path.join(log_dir, 'auth.log')
    auth_file_handler = RotatingFileHandler(
        auth_log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8'
    )
    auth_file_handler.setLevel(logging.DEBUG)
    auth_file_handler.setFormatter(detailed_formatter)
    
    # API requests log
    api_log_file = os.path.join(log_dir, 'api.log')
    api_file_handler = RotatingFileHandler(
        api_log_file, maxBytes=10 * 1024 * 1024, backupCount=3, encoding='utf-8'
    )
    api_file_handler.setLevel(logging.INFO)
    api_file_handler.setFormatter(detailed_formatter)
    
    # --- Configure Root Logger ---
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers to avoid duplicates on reload
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(app_file_handler)
    root_logger.addHandler(error_file_handler)
    
    # --- Configure Named Loggers ---
    
    # Auth logger
    auth_logger = logging.getLogger('cineforge.auth')
    auth_logger.addHandler(auth_file_handler)
    auth_logger.setLevel(logging.DEBUG)
    
    # API logger
    api_logger = logging.getLogger('cineforge.api')
    api_logger.addHandler(api_file_handler)
    api_logger.setLevel(logging.DEBUG)
    
    # Database logger
    db_logger = logging.getLogger('cineforge.db')
    db_logger.setLevel(logging.INFO)
    
    # SocketIO logger
    socketio_logger = logging.getLogger('cineforge.socketio')
    socketio_logger.setLevel(logging.INFO)
    
    # AI services logger
    ai_logger = logging.getLogger('cineforge.ai')
    ai_logger.setLevel(logging.DEBUG)
    
    # Quiet noisy third-party loggers
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('socketio').setLevel(logging.WARNING)
    logging.getLogger('engineio').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    # Log startup
    root_logger.info("=" * 60)
    root_logger.info("CineForge AI Backend - Logging initialized")
    root_logger.info(f"  Log Level: {logging.getLevelName(log_level)}")
    root_logger.info(f"  Log Directory: {log_dir}")
    root_logger.info(f"  Environment: {os.getenv('FLASK_ENV', 'development')}")
    root_logger.info("=" * 60)
    
    return root_logger


def get_logger(name):
    """
    Get a named logger for a specific module.
    
    Usage:
        from utils.logger import get_logger
        logger = get_logger(__name__)
        
        logger.info("Something happened")
        logger.error("Something broke", exc_info=True)
        logger.warning("Watch out")
        logger.debug("Debug details")
    
    Named loggers:
        cineforge.auth    - Authentication events (login, register, token)
        cineforge.api     - API requests and responses
        cineforge.db      - Database operations
        cineforge.socketio - WebSocket events
        cineforge.ai      - AI service operations
    """
    return logging.getLogger(name)


class RequestLogger:
    """
    Middleware to log all API requests and responses.
    Attach to Flask app with app.before_request / app.after_request.
    """
    
    def __init__(self):
        self.logger = get_logger('cineforge.api')
    
    def log_request(self):
        """Log incoming request"""
        from flask import request
        self.logger.info(
            f"→ {request.method} {request.path} "
            f"[IP: {request.remote_addr}] "
            f"[Agent: {request.user_agent.string[:50]}...]"
        )
    
    def log_response(self, response):
        """Log outgoing response"""
        from flask import request
        
        # Color-code by status
        status = response.status_code
        if status < 300:
            self.logger.info(f"← {request.method} {request.path} → {status}")
        elif status < 400:
            self.logger.info(f"← {request.method} {request.path} → {status} (redirect)")
        elif status < 500:
            self.logger.warning(f"← {request.method} {request.path} → {status} (client error)")
        else:
            self.logger.error(f"← {request.method} {request.path} → {status} (server error)")
        
        return response
