# Backend Tests

This folder contains all test files for the CineForge AI backend.

## Test Organization

### Unit Tests (pytest-based)
- `test_routes/` - API endpoint tests
- `test_models/` - Database model tests
- `test_all_roles.py` - Tests all 7 user roles
- `test_auto_collaborator.py` - Tests automatic owner collaboration
- `test_collab_response.py` - Tests collaborator response format
- `test_login_detail.py` - Tests authentication endpoints

### Integration Tests (API-based)
- `test_activity_endpoint.py` - Tests project activity logging
- `test_all_dashboards.py` - Tests dashboard data for all roles
- `test_create_delete.py` - Tests project create/delete lifecycle
- `test_filmmaker.py` - Tests filmmaker-specific functionality
- `test_frontend_compatibility.py` - Validates frontend/backend contract
- `test_full_lifecycle.py` - Complete project lifecycle test
- `test_project_7_complete.py` - Comprehensive project 7 endpoint tests
- `test_user_projects.py` - Tests user project access and permissions

## Running Tests

### Run all pytest tests:
```bash
pytest
```

### Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

### Run specific test file:
```bash
pytest tests/test_all_roles.py
```

### Run integration tests (API must be running):
```bash
# Start backend first
python app.py

# In another terminal
python tests/test_frontend_compatibility.py
python tests/test_full_lifecycle.py
```

## Test Data

Tests use the following test accounts:
- `test@gmail.com` / `Test@123` (filmmaker)
- `filmmaker@test.com` / `Test@123` (filmmaker)
- `director@test.com` / `Test@123` (filmmaker)
- `admin@cineforge.ai` / `Admin@123` (admin)
- `investor@test.com` / `Test@123` (investor)
- `actor@test.com` / `Test@123` (actor)
- `cinematographer@test.com` / `Test@123` (crew_member)

## Configuration

Test configuration is in `conftest.py` and `pytest.ini`.

See `requirements.txt` for test dependencies.
