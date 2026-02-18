"""
List all users in the database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from models import db, User
from config import Config

# Create minimal Flask app
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    users = User.query.all()
    
    print("=" * 80)
    print(f"USERS IN DATABASE (Total: {len(users)})")
    print("=" * 80)
    
    for user in users:
        print(f"\nUser ID: {user.user_id}")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Role: {user.role}")
        print(f"  Active: {user.is_active}")
        print(f"  Verified: {user.is_verified}")
        print(f"  Created: {user.created_at}")
        print(f"  Last Login: {user.last_login}")
    
    print("\n" + "=" * 80)
    print("Use these credentials to login (email + password you set)")
    print("=" * 80)
