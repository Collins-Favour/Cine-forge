import pytest


def test_update_collaborator_role_success(client, auth_headers, session):
    from models.user import User
    from models.project import ProjectCollaborator

    # Create a second user
    other = User(first_name='Other', last_name='User', email='other@example.com', username='other')
    other.set_password('password')
    session.add(other)
    session.commit()

    # Create a project as the authenticated user
    resp = client.post('/api/projects', headers=auth_headers, json={'title': 'Role Test Project'})
    assert resp.status_code == 201
    project = resp.json['project']
    project_id = project['project_id']

    # Add the second user as a collaborator
    add_resp = client.post(f'/api/projects/{project_id}/collaborators', headers=auth_headers, json={'user_id': other.user_id, 'role': 'writer'})
    assert add_resp.status_code == 201
    collab = add_resp.json['collaborator']
    collab_id = collab['collaboration_id']

    # Update collaborator role
    patch_resp = client.patch(f'/api/projects/{project_id}/collaborators/{collab_id}', headers=auth_headers, json={'role': 'editor'})
    assert patch_resp.status_code == 200
    assert patch_resp.json['collaborator']['role'] == 'editor'


def test_update_collaborator_invalid_role(client, auth_headers, session):
    from models.user import User

    other = User(first_name='Invalid', last_name='Role', email='inv@example.com', username='inv')
    other.set_password('password')
    session.add(other)
    session.commit()

    resp = client.post('/api/projects', headers=auth_headers, json={'title': 'Invalid Role Project'})
    assert resp.status_code == 201
    project_id = resp.json['project']['project_id']

    add_resp = client.post(f'/api/projects/{project_id}/collaborators', headers=auth_headers, json={'user_id': other.user_id, 'role': 'viewer'})
    assert add_resp.status_code == 201
    collab_id = add_resp.json['collaborator']['collaboration_id']

    # Attempt to set an invalid role
    bad_resp = client.patch(f'/api/projects/{project_id}/collaborators/{collab_id}', headers=auth_headers, json={'role': 'superhero'})
    assert bad_resp.status_code == 400


def test_cannot_change_owner_role(client, auth_headers, session):
    from models.project import ProjectCollaborator

    resp = client.post('/api/projects', headers=auth_headers, json={'title': 'Owner Change Test'})
    assert resp.status_code == 201
    project_id = resp.json['project']['project_id']

    # Find owner collaborator record
    owner = ProjectCollaborator.query.filter_by(project_id=project_id, role='owner').first()
    assert owner is not None

    # Attempt to change owner's role
    change_resp = client.patch(f'/api/projects/{project_id}/collaborators/{owner.collaboration_id}', headers=auth_headers, json={'role': 'writer'})
    assert change_resp.status_code == 403


def test_cannot_elevate_to_owner_via_patch(client, auth_headers, session):
    from models.user import User

    other = User(first_name='Elevate', last_name='User', email='elevate@example.com', username='elev')
    other.set_password('password')
    session.add(other)
    session.commit()

    resp = client.post('/api/projects', headers=auth_headers, json={'title': 'Elevate Test Project'})
    assert resp.status_code == 201
    project_id = resp.json['project']['project_id']

    add_resp = client.post(f'/api/projects/{project_id}/collaborators', headers=auth_headers, json={'user_id': other.user_id, 'role': 'viewer'})
    assert add_resp.status_code == 201
    collab_id = add_resp.json['collaborator']['collaboration_id']

    # Attempt to elevate to owner using PATCH should be forbidden
    elevate_resp = client.patch(f'/api/projects/{project_id}/collaborators/{collab_id}', headers=auth_headers, json={'role': 'owner'})
    assert elevate_resp.status_code == 403
