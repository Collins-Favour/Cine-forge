"""
Utility Validators
"""
import re
from typing import Tuple


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength
    Returns: (is_valid, message)
    """
    if len(password) < 8:
        return False, 'Password must be at least 8 characters long'
    
    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter'
    
    if not re.search(r'[a-z]', password):
        return False, 'Password must contain at least one lowercase letter'
    
    if not re.search(r'[0-9]', password):
        return False, 'Password must contain at least one digit'
    
    return True, 'Password is valid'


def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username format
    Returns: (is_valid, message)
    """
    if len(username) < 3:
        return False, 'Username must be at least 3 characters long'
    
    if len(username) > 50:
        return False, 'Username must not exceed 50 characters'
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, 'Username can only contain letters, numbers, hyphens, and underscores'
    
    return True, 'Username is valid'
