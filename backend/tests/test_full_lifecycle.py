import requests

base = 'http://127.0.0.1:5000/api'

print("=== COMPLETE PROJECT LIFECYCLE TEST ===\n")

# Login
r = requests.post(f'{base}/auth/login', json={'email': 'test@gmail.com', 'password': 'Test@123'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# 1. Get initial project count
r = requests.get(f'{base}/projects', headers=headers)
initial_count = len(r.json()['projects'])
print(f"📊 Initial projects: {initial_count}")

# 2. Create new project
print("\n🎬 Creating new project...")
new_project = {
    'title': 'My Second Film',
    'logline': 'An inspiring story about dreams',
    'synopsis': 'A young filmmaker pursues their passion against all odds.',
    'genre': 'Drama',
    'target_length': 90,
    'budget_range': '$100K - $500K'
}

r = requests.post(f'{base}/projects', json=new_project, headers=headers)
if r.status_code == 201:
    created_project = r.json()['project']
    project_id = created_project['project_id']
    print(f"✅ Created: {created_project['title']} (ID: {project_id})")
else:
    print(f"❌ Failed: {r.json()}")
    exit(1)

# 3. Verify it appears in list
r = requests.get(f'{base}/projects', headers=headers)
after_create_count = len(r.json()['projects'])
print(f"📊 Projects after create: {after_create_count} (expected: {initial_count + 1})")

# 4. Get project details
r = requests.get(f'{base}/projects/{project_id}', headers=headers)
if r.status_code == 200:
    project = r.json()
    print(f"✅ Can access project: {project['title']}")
    print(f"   Genre: {project['genre']}")
    print(f"   Stage: {project['production_stage']}")
else:
    print(f"❌ Can't access project: {r.json()}")

# 5. Delete project
print(f"\n🗑️  Deleting project {project_id}...")
r = requests.delete(f'{base}/projects/{project_id}', headers=headers)
if r.status_code == 200:
    print(f"✅ {r.json()['message']}")
else:
    print(f"❌ Delete failed: {r.json()}")
    exit(1)

# 6. Verify it's removed from list
r = requests.get(f'{base}/projects', headers=headers)
after_delete_count = len(r.json()['projects'])
print(f"📊 Projects after delete: {after_delete_count} (expected: {initial_count})")

# 7. Try to access deleted project
r = requests.get(f'{base}/projects/{project_id}', headers=headers)
if r.status_code == 200:
    project = r.json()
    if project['is_archived']:
        print(f"✅ Project is archived (soft delete)")
    else:
        print(f"⚠️  Project still accessible but not archived")
else:
    print(f"❌ Can't access deleted project (expected): {r.status_code}")

print("\n🎉 FULL LIFECYCLE TEST COMPLETE")
