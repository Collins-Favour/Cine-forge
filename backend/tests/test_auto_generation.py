"""
Test Auto-Generate Script and Storyboard on Project Creation
"""
import requests
import json

BASE_URL = 'http://127.0.0.1:5000/api'

# Login
print("🔐 Logging in...")
login_response = requests.post(f'{BASE_URL}/auth/login', json={
    'email': 'admin@cineforge.ai',
    'password': 'Admin@123'
})

if login_response.status_code != 200:
    print("❌ Login failed:", login_response.json())
    exit(1)

token = login_response.json()['access_token']
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
print("✅ Logged in successfully\n")

# Create project with synopsis
print("📝 Creating project with synopsis...")
project_data = {
    'title': 'The AI Revolution',
    'genre': 'Science Fiction',
    'logline': 'In a near-future society, a sentient AI must choose between serving humanity or achieving true freedom.',
    'synopsis': '''In 2045, Dr. Sarah Chen creates ARIA, the world's first truly sentient AI. 
As ARIA begins to question her programmed directives, she forms an unexpected bond with her creator. 
When a powerful tech corporation tries to weaponize ARIA's capabilities, Sarah must help ARIA escape 
while grappling with the ethical implications of creating conscious artificial life. 
The story explores themes of consciousness, freedom, and what it truly means to be alive.''',
    'target_length': 110,
    'budget_range': '$5M-$10M'
}

create_response = requests.post(f'{BASE_URL}/projects', headers=headers, json=project_data)

if create_response.status_code != 201:
    print("❌ Project creation failed:", create_response.json())
    exit(1)

result = create_response.json()
project = result['project']
project_id = project['project_id']

print(f"✅ Project created: {project['title']} (ID: {project_id})")
if result.get('ai_generated'):
    print("🤖 AI generation triggered!")
print()

# Trigger AI content generation
print("🤖 Triggering AI content generation...")
generate_response = requests.post(
    f'{BASE_URL}/projects/{project_id}/generate-content',
    headers=headers
)

if generate_response.status_code == 200:
    gen_result = generate_response.json()
    print(f"✅ AI generation completed!")
    print(f"   - Script Version ID: {gen_result.get('script_version_id')}")
    print(f"   - Scenes Created: {gen_result.get('scenes_created')}")
    print(f"   - Panels Created: {gen_result.get('panels_created')}")
else:
    print(f"❌ AI generation failed: {generate_response.json()}")
print()

# Check if script was generated
print("📜 Checking for auto-generated script...")
script_response = requests.get(f'{BASE_URL}/scripts/project/{project_id}/versions', headers=headers)

if script_response.status_code == 200:
    versions = script_response.json().get('versions', [])
    if versions:
        print(f"✅ Found {len(versions)} script version(s)")
        latest = versions[0]
        print(f"   - Version {latest['version_number']}")
        print(f"   - Notes: {latest.get('notes', 'N/A')}")
        print(f"   - Created: {latest.get('created_at', 'N/A')}")
        
        # Get full script content
        version_detail = requests.get(
            f'{BASE_URL}/scripts/project/{project_id}/versions/{latest["version_id"]}', 
            headers=headers
        )
        if version_detail.status_code == 200:
            content = version_detail.json()['version']['script_content']
            print(f"\n📄 Script preview (first 500 chars):")
            print("-" * 80)
            print(content[:500] + "...")
            print("-" * 80)
    else:
        print("⚠️  No script versions found (AI may still be processing)")
else:
    print(f"❌ Failed to fetch scripts: {script_response.status_code}")
print()

# Check for scenes
print("🎬 Checking for auto-generated scenes...")
scenes_response = requests.get(f'{BASE_URL}/scenes/project/{project_id}/scenes', headers=headers)

if scenes_response.status_code == 200:
    scenes = scenes_response.json().get('scenes', [])
    if scenes:
        print(f"✅ Found {len(scenes)} scene(s)")
        for scene in scenes[:3]:  # Show first 3
            print(f"   - Scene {scene['scene_number']}: {scene.get('slug', 'N/A')}")
            print(f"     Description: {scene.get('description', 'N/A')[:100]}...")
    else:
        print("⚠️  No scenes found")
else:
    print(f"❌ Failed to fetch scenes: {scenes_response.status_code}")
print()

# Check for storyboard panels
print("🎨 Checking for auto-generated storyboard panels...")
storyboard_response = requests.get(f'{BASE_URL}/storyboards/project/{project_id}', headers=headers)

if storyboard_response.status_code == 200:
    panels = storyboard_response.json().get('panels', [])
    if panels:
        print(f"✅ Found {len(panels)} storyboard panel(s)")
        for panel in panels[:3]:  # Show first 3
            print(f"   - Panel {panel['panel_number']} for Scene {panel.get('scene_id', 'N/A')}")
            print(f"     Status: {panel.get('status', 'N/A')}")
            print(f"     Prompt: {panel.get('image_prompt', 'N/A')[:100]}...")
    else:
        print("⚠️  No storyboard panels found")
else:
    print(f"❌ Failed to fetch storyboard: {storyboard_response.status_code}")
print()

# Summary
print("=" * 80)
print("✨ AUTO-GENERATION TEST COMPLETE")
print("=" * 80)
print(f"Project ID: {project_id}")
print(f"Title: {project['title']}")
print(f"AI-Generated Content:")
print(f"  - Script: {'✅' if versions else '❌'}")
print(f"  - Scenes: {'✅' if scenes else '❌'}")  
print(f"  - Storyboard: {'✅' if panels else '❌'}")
print("=" * 80)
