import pytest
from models.user import User

def test_user_creation(session):
    """Test user model creation."""
    user = User(
        full_name='John Doe',
        email='john@example.com',
        username='johndoe',
        role='filmmaker'
    )
    user.set_password('password123')
    
    session.add(user)
    session.commit()
    
    assert user.id is not None
    assert user.full_name == 'John Doe'
    assert user.email == 'john@example.com'
    assert user.username == 'johndoe'
    assert user.check_password('password123')
    assert not user.check_password('wrongpassword')

def test_user_to_dict(session):
    """Test user serialization."""
    user = User(
        full_name='Jane Doe',
        email='jane@example.com',
        username='janedoe',
        role='actor'
    )
    session.add(user)
    session.commit()
    
    user_dict = user.to_dict()
    
    assert user_dict['full_name'] == 'Jane Doe'
    assert user_dict['email'] == 'jane@example.com'
    assert user_dict['role'] == 'actor'
    assert 'password_hash' not in user_dict

def test_user_roles(session):
    """Test different user roles."""
    roles = ['filmmaker', 'investor', 'actor', 'crew_member', 'admin']
    
    for role in roles:
        user = User(
            full_name=f'Test {role}',
            email=f'{role}@example.com',
            username=f'test{role}',
            role=role
        )
        session.add(user)
    
    session.commit()
    
    assert session.query(User).count() == len(roles)
