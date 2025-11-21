# Project ID Field Mismatch - FIXED

## Issue
Frontend was using `project.id` but backend returns `project.project_id`, causing:
- Links to `/projects/undefined`
- 404 errors on all project detail requests
- C-Space, Scripts, Storyboards failing to load

## Root Cause
Backend API consistently returns `project_id` field (snake_case), but frontend components were using `id` field from old mock data.

## Files Fixed

### 1. frontend/src/pages/Projects.jsx
- ✅ Line 30: Changed mock data from `id` to `project_id`
- ✅ Line 186: Changed key from `project.id` to `project.project_id`
- ✅ Line 187: Changed link from `/projects/${project.id}` to `/projects/${project.project_id}`

### 2. frontend/src/pages/roles/filmmaker/Dashboard.jsx
- ✅ Line 92: Changed key from `project.id` to `project.project_id`
- ✅ Line 145: Changed link from `/projects/${project.id}` to `/projects/${project.project_id}`

### 3. frontend/src/pages/roles/investor/Dashboard.jsx
- ✅ Line 91: Changed key from `project.id` to `project.project_id`
- ✅ Line 158: Changed link from `/projects/${project.id}` to `/projects/${project.project_id}`

### 4. frontend/src/pages/roles/crew/Dashboard.jsx
- ✅ Line 120: Changed key from `project.id` to `project.project_id`
- ✅ Line 220: Changed link from `/projects/${project.id}` to `/projects/${project.project_id}`

## Result
✅ All project links now work correctly
✅ Project details pages load properly
✅ C-Space, Scripts, Storyboards, and all other project features accessible
✅ No more `/api/projects/undefined` errors

## Test
Click any project card → Should navigate to project details with correct ID
Example: Project ID 1 → `/projects/1` instead of `/projects/undefined`
