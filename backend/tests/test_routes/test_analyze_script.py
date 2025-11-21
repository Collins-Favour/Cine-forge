import pytest


def test_analyze_script_creates_ai_log(client, auth_headers, session, monkeypatch):
    """POST to the analyze endpoint should call GroqService (mocked),
    return analysis and create an AIProcessingLog entry."""
    # Monkeypatch the GroqService used by the routes.scripts module
    from routes import scripts as scripts_module

    class MockGroqService:
        def analyze_script(self, script_content):
            return {
                'synopsis': 'Mock synopsis',
                'characters': [],
                'scenes': [],
                'themes': [],
                'tone': 'mock-tone',
                'pacing': 'mock-pacing'
            }

    monkeypatch.setattr(scripts_module, 'GroqService', MockGroqService)

    # Create a project as the authenticated user
    resp = client.post('/api/projects', headers=auth_headers, json={'title': 'AI Analyze Project'})
    assert resp.status_code == 201
    project = resp.json['project']
    project_id = project['project_id']

    # Create a script version for the project
    create_resp = client.post(f'/api/scripts/project/{project_id}/versions', headers=auth_headers,
                              json={'script_content': 'INT. ROOM - DAY\nA simple test scene.'})
    assert create_resp.status_code == 201
    version = create_resp.json['version']
    version_id = version['version_id']

    # Call the analyze endpoint
    analyze_resp = client.post(f'/api/scripts/project/{project_id}/versions/{version_id}/analyze', headers=auth_headers)
    assert analyze_resp.status_code == 200
    assert 'analysis' in analyze_resp.json
    assert analyze_resp.json['analysis']['synopsis'] == 'Mock synopsis'

    # Verify AIProcessingLog was created
    from models import AIProcessingLog

    log = AIProcessingLog.query.filter_by(project_id=project_id, operation_type='script_analysis').order_by(AIProcessingLog.created_at.desc()).first()
    assert log is not None
    assert isinstance(log.output_data, dict)
    assert log.output_data.get('synopsis') == 'Mock synopsis'
