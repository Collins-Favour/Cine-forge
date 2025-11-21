import pytest
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from config import TestingConfig
from models import db

@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    app = create_app('testing')
    return app

@pytest.fixture(scope='session')
def _db(app):
    """Create database for the tests."""
    with app.app_context():
        db.create_all()
        yield db
        db.session.close()
        db.drop_all()

@pytest.fixture(scope='function')
def session(_db):
    """Create a new database session for a test."""
    # Use a transactional connection and a scoped session bound to that connection
    from sqlalchemy.orm import sessionmaker, scoped_session

    connection = _db.engine.connect()
    transaction = connection.begin()

    SessionFactory = sessionmaker(bind=connection)
    scoped = scoped_session(SessionFactory)

    # Attach the scoped session to the db object for app code that expects `db.session`
    _db.session = scoped

    try:
        yield scoped
    finally:
        scoped.remove()
        transaction.rollback()
        connection.close()

@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers(client, session):
    """Create authentication headers for testing."""
    from models.user import User
    
    # Create test user
    user = User(
        username='testuser',
        email='test@example.com',
        first_name='Test',
        last_name='User',
        role='filmmaker'
    )
    user.set_password('password123')
    session.add(user)
    session.commit()
    
    # Login
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}
