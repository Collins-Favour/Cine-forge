import pytest
import json

def test_register_success(client):
    """Test successful user registration."""
    response = client.post('/api/auth/register', json={
        'full_name': 'New User',
        'email': 'newuser@example.com',
        'username': 'newuser',
        'password': 'password123',
        'role': 'filmmaker'
    })
    
    assert response.status_code == 201
    data = response.json
    assert 'access_token' in data
    assert data['user']['email'] == 'newuser@example.com'

def test_register_duplicate_email(client, session):
    """Test registration with duplicate email."""
    from models.user import User
    
    user = User(
        full_name='Existing User',
        email='existing@example.com',
        username='existing',
        role='filmmaker'
    )
    session.add(user)
    session.commit()
    
    response = client.post('/api/auth/register', json={
        'full_name': 'New User',
        'email': 'existing@example.com',
        'username': 'newuser',
        'password': 'password123',
        'role': 'filmmaker'
    })
    
    assert response.status_code == 400

def test_login_success(client, session):
    """Test successful login."""
    from models.user import User
    
    user = User(
        full_name='Login User',
        email='login@example.com',
        username='loginuser',
        role='filmmaker'
    )
    user.set_password('password123')
    session.add(user)
    session.commit()
    
    response = client.post('/api/auth/login', json={
        'email': 'login@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 200
    data = response.json
    assert 'access_token' in data
    assert data['user']['email'] == 'login@example.com'

def test_login_wrong_password(client, session):
    """Test login with wrong password."""
    from models.user import User
    
    user = User(
        full_name='Test User',
        email='test@example.com',
        username='testuser',
        role='filmmaker'
    )
    user.set_password('password123')
    session.add(user)
    session.commit()
    
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401

def test_get_current_user(client, auth_headers):
    """Test getting current user info."""
    response = client.get('/api/auth/me', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json
    assert data['email'] == 'test@example.com'
