# Backend Scripts

This folder contains utility scripts for database setup, migrations, and testing.

## Database Migrations

- `add_activity_metadata_column.py` - Adds activity_metadata JSON column to activity_log table
- `add_channel_column.py` - Adds channel support to messaging system
- `fix_roles_migration.py` - Migrates user roles enum from 4 to 7 values

## User Management

- `create_admin.py` - Creates initial admin user account
- `create_test_users.py` - Creates test users for all 7 roles
- `fix_admin_password.py` - Resets admin password

## Test Data Generation

- `create_test_projects.py` - Creates sample projects for testing
- `create_project_for_test_user.py` - Creates a project for specific test user
- `seed_test_project.py` - Seeds a complete test project with scenes, characters, etc.

## Debugging Tools

- `check_project_7_response.py` - Checks API response structure for project 7
- `check_project_visibility.py` - Verifies project access permissions
- `check_user_access.py` - Checks user's project access and collaborations
- `debug_project_7.py` - Comprehensive debugging for project 7 endpoints
- `get_cspace_urls.py` - Extracts C-Space (collaboration) URLs

## Usage

Run scripts from the backend directory:

```bash
python scripts/script_name.py
```

Most scripts require the Flask app context and will automatically load environment variables from `.env`.
