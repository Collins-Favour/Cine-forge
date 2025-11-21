import pytest
from models.project import Project
from models.user import User

def test_project_creation(session):
    """Test project model creation."""
    user = User(
        full_name='Project Owner',
        email='owner@example.com',
        username='owner',
        role='filmmaker'
    )
    session.add(user)
    session.commit()
    
    project = Project(
        title='Test Film',
        description='A test film project',
        genre='Drama',
        status='planning',
        owner_id=user.id
    )
    session.add(project)
    session.commit()
    
    assert project.id is not None
    assert project.title == 'Test Film'
    assert project.owner_id == user.id

def test_project_to_dict(session):
    """Test project serialization."""
    user = User(
        full_name='Test User',
        email='test@example.com',
        username='testuser',
        role='filmmaker'
    )
    session.add(user)
    session.commit()
    
    project = Project(
        title='Another Film',
        description='Another test film',
        genre='Action',
        owner_id=user.id
    )
    session.add(project)
    session.commit()
    
    project_dict = project.to_dict()
    
    assert project_dict['title'] == 'Another Film'
    assert project_dict['genre'] == 'Action'
    assert 'owner_id' in project_dict
