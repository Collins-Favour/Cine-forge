"""Check if profile picture is stored in database"""
import sys
sys.path.insert(0, '..')

from models import User, db
from app import create_app

app = create_app()

with app.app_context():
    user = User.query.filter_by(email='admin@cineforge.ai').first()
    
    if user:
        print(f"User: {user.first_name} {user.last_name}")
        print(f"Has profile_pic_url: {user.profile_pic_url is not None}")
        
        if user.profile_pic_url:
            print(f"URL length: {len(user.profile_pic_url)}")
            print(f"URL prefix: {user.profile_pic_url[:100]}")
            
            # Check if it's a valid data URI
            if user.profile_pic_url.startswith('data:image/'):
                print("✅ Valid data URI format")
                
                # Get the user dict
                user_dict = user.to_dict(include_email=True)
                print(f"\nUser dict keys: {user_dict.keys()}")
                print(f"Has profile_pic_url in dict: {'profile_pic_url' in user_dict}")
                print(f"Dict profile_pic_url length: {len(user_dict.get('profile_pic_url', ''))}")
            else:
                print("❌ Not a valid data URI format")
        else:
            print("No profile picture stored")
    else:
        print("User not found")
