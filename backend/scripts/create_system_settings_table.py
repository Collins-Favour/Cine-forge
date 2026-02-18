"""
Create system_settings table
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from models import db
from config import Config

# Create minimal Flask app
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    try:
        from sqlalchemy import text
        with db.engine.connect() as conn:
            # Check if table exists
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = 'system_settings'
            """))
            exists = result.fetchone()[0] > 0
            
            if not exists:
                # Create the table
                conn.execute(text("""
                    CREATE TABLE system_settings (
                        setting_id INT AUTO_INCREMENT PRIMARY KEY,
                        setting_key VARCHAR(100) NOT NULL UNIQUE,
                        setting_value TEXT,
                        setting_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string',
                        description TEXT,
                        is_public BOOLEAN DEFAULT FALSE COMMENT 'Can be accessed by frontend',
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_setting_key (setting_key)
                    )
                """))
                conn.commit()
                print("✅ Successfully created system_settings table")
                
                # Insert default settings
                conn.execute(text("""
                    INSERT INTO system_settings (setting_key, setting_value, setting_type, description) VALUES
                    ('site_name', 'CineForge AI', 'string', 'Site name displayed in header'),
                    ('maintenance_mode', 'false', 'boolean', 'Enable maintenance mode'),
                    ('allow_registration', 'true', 'boolean', 'Allow new user registrations'),
                    ('require_email_verification', 'true', 'boolean', 'Require email verification'),
                    ('max_file_size', '100', 'number', 'Maximum file size in MB'),
                    ('max_storage_per_user', '5000', 'number', 'Maximum storage per user in MB'),
                    ('ai_features_enabled', 'true', 'boolean', 'Enable AI features'),
                    ('collaboration_enabled', 'true', 'boolean', 'Enable collaboration features')
                """))
                conn.commit()
                print("✅ Successfully inserted default settings")
            else:
                print("ℹ️  Table 'system_settings' already exists")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
