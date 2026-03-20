"""Run the activity_log migration to support system-level events."""
from app import create_app
from models import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        # Check if ip_address column already exists
        result = db.session.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'activity_log' AND column_name = 'ip_address'"
        ))
        has_ip = result.fetchone() is not None

        # Check if project_id is nullable
        result = db.session.execute(text(
            "SELECT is_nullable FROM information_schema.columns "
            "WHERE table_name = 'activity_log' AND column_name = 'project_id'"
        ))
        row = result.fetchone()
        project_nullable = row and row[0] == 'YES'

        if not project_nullable:
            print("Making project_id nullable...")
            db.session.execute(text("ALTER TABLE activity_log ALTER COLUMN project_id DROP NOT NULL"))
            print("Done.")
        else:
            print("project_id is already nullable.")

        # Check if user_id is nullable
        result = db.session.execute(text(
            "SELECT is_nullable FROM information_schema.columns "
            "WHERE table_name = 'activity_log' AND column_name = 'user_id'"
        ))
        row = result.fetchone()
        user_nullable = row and row[0] == 'YES'

        if not user_nullable:
            print("Making user_id nullable...")
            db.session.execute(text("ALTER TABLE activity_log ALTER COLUMN user_id DROP NOT NULL"))
            print("Done.")
        else:
            print("user_id is already nullable.")

        if not has_ip:
            print("Adding ip_address column...")
            db.session.execute(text("ALTER TABLE activity_log ADD COLUMN ip_address VARCHAR(45)"))
            print("Done.")
        else:
            print("ip_address column already exists.")

        # Add index on activity_type if not exists
        result = db.session.execute(text(
            "SELECT 1 FROM pg_indexes WHERE tablename = 'activity_log' AND indexname = 'idx_activity_type'"
        ))
        if not result.fetchone():
            print("Adding index on activity_type...")
            db.session.execute(text("CREATE INDEX idx_activity_type ON activity_log (activity_type)"))
            print("Done.")
        else:
            print("idx_activity_type index already exists.")

        db.session.commit()
        print("\nMigration completed successfully!")

        # Verify
        result = db.session.execute(text(
            "SELECT column_name, is_nullable, data_type "
            "FROM information_schema.columns "
            "WHERE table_name = 'activity_log' ORDER BY ordinal_position"
        ))
        print("\nCurrent activity_log schema:")
        for r in result:
            print(f"  {r[0]}: nullable={r[1]}, type={r[2]}")

    except Exception as e:
        db.session.rollback()
        print(f"Migration error: {e}")
        import traceback
        traceback.print_exc()
