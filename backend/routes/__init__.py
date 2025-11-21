"""
Routes Package Initializer
"""
from .auth import auth_bp
from .users import users_bp
from .projects import projects_bp
from .admin import admin_bp

__all__ = [
    'auth_bp',
    'users_bp',
    'projects_bp',
    'admin_bp'
]
