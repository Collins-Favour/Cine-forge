import pytest

def test_create_project(client, auth_headers):
    """Test creating a new project."""
    response = client.post('/api/projects', 
        headers=auth_headers,
        json={
            'title': 'Test Project',
            'description': 'A test project',
            'genre': 'Drama',
            'target_audience': 'Adults',
            'estimated_budget': 100000
        }
    )
    
    assert response.status_code == 201
    data = response.json
    assert data['title'] == 'Test Project'
    assert data['genre'] == 'Drama'

def test_get_projects(client, auth_headers):
    """Test getting all projects."""
    # Create a project first
    client.post('/api/projects', 
        headers=auth_headers,
        json={
            'title': 'Project 1',
            'description': 'First project',
            'genre': 'Action'
        }
    )
    
    response = client.get('/api/projects', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json
    assert len(data['projects']) > 0

def test_get_project_by_id(client, auth_headers):
    """Test getting a specific project."""
    # Create a project
    create_response = client.post('/api/projects', 
        headers=auth_headers,
        json={
            'title': 'Specific Project',
            'description': 'A specific test project',
            'genre': 'Comedy'
        }
    )
    project_id = create_response.json['id']
    
    response = client.get(f'/api/projects/{project_id}', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json
    assert data['title'] == 'Specific Project'

def test_update_project(client, auth_headers):
    """Test updating a project."""
    # Create a project
    create_response = client.post('/api/projects', 
        headers=auth_headers,
        json={
            'title': 'Original Title',
            'description': 'Original description',
            'genre': 'Drama'
        }
    )
    project_id = create_response.json['id']
    
    # Update the project
    response = client.put(f'/api/projects/{project_id}',
        headers=auth_headers,
        json={
            'title': 'Updated Title',
            'description': 'Updated description'
        }
    )
    
    assert response.status_code == 200
    data = response.json
    assert data['title'] == 'Updated Title'

def test_delete_project(client, auth_headers):
    """Test deleting a project."""
    # Create a project
    create_response = client.post('/api/projects', 
        headers=auth_headers,
        json={
            'title': 'To Be Deleted',
            'description': 'This project will be deleted',
            'genre': 'Horror'
        }
    )
    project_id = create_response.json['id']
    
    # Delete the project
    response = client.delete(f'/api/projects/{project_id}', headers=auth_headers)
    
    assert response.status_code == 200
    
    # Verify it's deleted
    get_response = client.get(f'/api/projects/{project_id}', headers=auth_headers)
    assert get_response.status_code == 404
