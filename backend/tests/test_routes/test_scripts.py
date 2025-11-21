import pytest

def test_create_script_version(client, auth_headers, session):
    """Test creating a script version."""
    from models.project import Project
    from models.user import User
    
    # Get the test user
    user = session.query(User).filter_by(email='test@example.com').first()
    
    # Create a project
    project = Project(
        title='Script Test Project',
        description='For script testing',
        owner_id=user.id
    )
    session.add(project)
    session.commit()
    
    response = client.post(f'/api/scripts/{project.id}/versions',
        headers=auth_headers,
        json={
            'version_number': 1,
            'content': 'INT. OFFICE - DAY\n\nJohn sits at his desk.',
            'notes': 'First draft'
        }
    )
    
    assert response.status_code == 201
    data = response.json
    assert data['version_number'] == 1

def test_get_script_versions(client, auth_headers, session):
    """Test getting all script versions."""
    from models.project import Project
    from models.user import User
    
    user = session.query(User).filter_by(email='test@example.com').first()
    project = Project(title='Test', description='Test', owner_id=user.id)
    session.add(project)
    session.commit()
    
    # Create versions
    client.post(f'/api/scripts/{project.id}/versions',
        headers=auth_headers,
        json={'version_number': 1, 'content': 'Version 1'}
    )
    
    response = client.get(f'/api/scripts/{project.id}/versions', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json
    assert len(data['versions']) > 0

def test_analyze_script(client, auth_headers, session):
    """Test AI script analysis."""
    from models.project import Project
    from models.script import ScriptVersion
    from models.user import User
    
    user = session.query(User).filter_by(email='test@example.com').first()
    project = Project(title='Test', description='Test', owner_id=user.id)
    session.add(project)
    session.commit()
    
    script = ScriptVersion(
        project_id=project.id,
        version_number=1,
        content='INT. COFFEE SHOP - DAY\n\nALICE and BOB meet.',
        created_by=user.id
    )
    session.add(script)
    session.commit()
    
    response = client.post(f'/api/scripts/{project.id}/versions/{script.id}/analyze',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json
    assert 'analysis' in data
