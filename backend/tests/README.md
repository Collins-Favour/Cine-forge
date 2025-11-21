# Backend Test README

## Running Tests

### All Tests

```bash
# Using Python
pytest tests/ -v

# Using PowerShell script
.\run_tests.ps1

# Using Bash script
./run_tests.sh
```

### Specific Test Categories

```bash
# Unit tests only
pytest tests/ -m unit

# Integration tests only
pytest tests/ -m integration

# E2E tests only
pytest tests/ -m e2e

# Specific test file
pytest tests/test_routes/test_auth.py -v
```

### With Coverage

```bash
pytest tests/ --cov=. --cov-report=html --cov-report=term-missing
```

Open `htmlcov/index.html` to view coverage report.

## Test Structure

```
tests/
├── conftest.py           # Test fixtures and configuration
├── requirements.txt      # Test dependencies
├── test_models/         # Model unit tests
│   ├── test_user.py
│   └── test_project.py
└── test_routes/         # API integration tests
    ├── test_auth.py
    ├── test_projects.py
    └── test_scripts.py
```

## Writing Tests

### Model Test Example

```python
def test_user_creation(session):
    user = User(full_name='Test', email='test@example.com')
    session.add(user)
    session.commit()
    
    assert user.id is not None
    assert user.email == 'test@example.com'
```

### Route Test Example

```python
def test_login(client):
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 200
    assert 'access_token' in response.json
```

## Test Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Slow running tests

## Fixtures

- `app` - Flask application instance
- `client` - Test client for API requests
- `session` - Database session
- `auth_headers` - Authentication headers for protected routes

## CI/CD Integration

```yaml
- run: pip install -r tests/requirements.txt
- run: pytest tests/ --cov=. --cov-report=xml
```
