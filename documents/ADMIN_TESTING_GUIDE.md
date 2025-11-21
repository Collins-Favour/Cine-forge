# Admin Features - Complete Testing Guide

## 🎯 Step-by-Step Testing Instructions

### Prerequisites
- ✅ Backend running on `http://127.0.0.1:5000`
- ✅ Frontend running on `http://localhost:3000`
- ✅ Database is seeded with test data
- ✅ Admin account exists

---

## 🚀 PART 1: Creating Admin Account

### Method 1: Python Script (Easiest)

```bash
# Step 1: Open terminal in backend directory
cd backend

# Step 2: Run Python interactive shell
python

# Step 3: Paste this code
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Check if admin already exists
    existing = User.query.filter_by(email='admin@cineforge.ai').first()
    if existing:
        print(f"Admin already exists: {existing.email}")
    else:
        admin = User(
            first_name='Admin',
            last_name='User',
            email='admin@cineforge.ai',
            password_hash=generate_password_hash('Admin@123'),
            role='admin',
            verified=True
        )
        db.session.add(admin)
        db.session.commit()
        print(f"✅ Admin created: {admin.email}")
        print(f"   Password: Admin@123")
        print(f"   Role: {admin.role}")
        print(f"   ID: {admin.user_id}")

# Step 4: Exit Python shell
exit()
```

**Expected Output:**
```
✅ Admin created: admin@cineforge.ai
   Password: Admin@123
   Role: admin
   ID: 1
```

### Method 2: Direct Database (Alternative)

```sql
-- Connect to your database
psql -d cineforge_db -U your_user

-- Create admin user
INSERT INTO users (
    email, 
    password_hash, 
    first_name, 
    last_name, 
    role, 
    verified,
    created_at
) VALUES (
    'admin@cineforge.ai',
    'scrypt:32768:8:1$YourHashHere',  -- Generate using werkzeug
    'Admin',
    'User',
    'admin',
    true,
    NOW()
);

-- Verify creation
SELECT user_id, email, role, verified FROM users WHERE email = 'admin@cineforge.ai';
```

---

## 🔐 PART 2: Testing Login

### Step 1: Open Login Page

```
URL: http://localhost:3000/login
```

**What you should see:**
- Login form with email and password fields
- "Login" button
- "Don't have an account? Register" link

### Step 2: Enter Admin Credentials

```
Email: admin@cineforge.ai
Password: Admin@123
```

**Click "Login" button**

### Step 3: Verify Login Success

**Expected behavior:**
1. Page redirects to `/dashboard`
2. You see navigation bar with your name
3. ✨ **Admin Panel** link appears in navigation (key indicator!)
4. No error messages

**If login fails:**
- Check backend console for errors
- Verify user exists: `SELECT * FROM users WHERE email = 'admin@cineforge.ai';`
- Verify password hash is correct
- Check backend logs: `tail -f backend/logs/app.log`

### Step 4: Check Admin Access

**In browser console (F12):**
```javascript
// Check if token exists
const token = localStorage.getItem('token');
console.log('Token exists:', !!token);

// Check user data
const user = JSON.parse(localStorage.getItem('user') || '{}');
console.log('User email:', user.email);
console.log('User role:', user.role);
console.log('Is admin:', user.role === 'admin');
```

**Expected output:**
```javascript
Token exists: true
User email: admin@cineforge.ai
User role: admin
Is admin: true
```

---

## 👥 PART 3: Testing User Management

### Test 3.1: View All Users

**Steps:**
1. Click "Admin Panel" in navigation
2. Or navigate to: `http://localhost:3000/admin/users`

**Expected:**
- List of all users displayed
- Search bar at top
- Pagination if >20 users
- Each user shows:
  - Name
  - Email
  - Role badge
  - Created date
  - Action buttons (View, Edit, Delete)

**Try this:**
- Use search bar: Type user's email
- Filter by role: Select dropdown
- Click page numbers to navigate
- Sort by clicking column headers

### Test 3.2: View User Details

**Steps:**
1. From users list, click any user row
2. Or navigate to: `http://localhost:3000/admin/users/2` (use valid ID)

**Expected:**
- Full user profile displayed
- Statistics: Total projects, scripts, activity
- Recent projects list
- Recent activity log
- Edit button
- Delete button
- Reset password button

**Verify:**
- All data displays correctly
- Stats match database
- Activity is recent

### Test 3.3: Create New User

**Steps:**
1. On `/admin/users` page
2. Click "Add New User" button
3. Fill form:
   ```
   First Name: Test
   Last Name: User
   Email: test@example.com
   Password: Test@123
   Role: filmmaker
   ```
4. Click "Create User"

**Expected:**
- Success modal appears
- User added to list
- Can find user by searching email
- User appears in database:
  ```sql
  SELECT * FROM users WHERE email = 'test@example.com';
  ```

### Test 3.4: Edit User

**Steps:**
1. Click on test user you created
2. Click "Edit" button
3. Change first name to "Updated"
4. Change role to "investor"
5. Click "Save Changes"

**Expected:**
- Success message
- Changes reflected immediately
- Database updated:
  ```sql
  SELECT first_name, role FROM users WHERE email = 'test@example.com';
  -- Should show: first_name = 'Updated', role = 'investor'
  ```

### Test 3.5: Reset User Password

**Steps:**
1. On user detail page
2. Click "Reset Password" button
3. Choose "Generate New Password"
4. Copy the generated password
5. Logout from admin
6. Try logging in as test user with new password

**Expected:**
- New password generated
- Can login with new password
- Old password no longer works

### Test 3.6: Delete User

**Steps:**
1. Navigate to test user detail page
2. Click "Delete User" button
3. Confirm deletion in modal
4. Check users list

**Expected:**
- User removed from list
- Confirmation modal appears
- User deleted from database:
  ```sql
  SELECT * FROM users WHERE email = 'test@example.com';
  -- Should return 0 rows
  ```

---

## ⚙️ PART 4: Testing System Settings

### Test 4.1: View Settings

**Steps:**
1. Navigate to: `http://localhost:3000/admin/settings`

**Expected:**
- Settings form displayed
- Categories:
  - General (site name, maintenance mode)
  - Registration (enabled/disabled, verification)
  - File Uploads (max size, allowed types)
  - Features (AI enabled, storage limits)

### Test 4.2: Update Settings

**Steps:**
1. Change "Site Name" to "CineForge Pro"
2. Toggle "Maintenance Mode" to ON
3. Change "Max File Size" to 150 MB
4. Click "Save Settings"

**Expected:**
- Success message
- Settings saved to database
- Changes take effect immediately

**Verify:**
1. Refresh page - new site name appears
2. Try accessing site as regular user - maintenance message shown
3. Check database:
   ```sql
   SELECT * FROM system_settings;
   ```

### Test 4.3: Maintenance Mode

**Steps:**
1. Enable maintenance mode
2. Open new incognito window
3. Try accessing site as non-admin user

**Expected:**
- Non-admin users see "Site Under Maintenance" message
- Admin can still access (bypass maintenance mode)
- All API calls from non-admin return 503

---

## 📊 PART 5: Testing Analytics

### Test 5.1: View Analytics Dashboard

**Steps:**
1. Navigate to: `http://localhost:3000/admin/analytics`

**Expected:**
- Multiple charts displayed:
  - User Growth Over Time (line chart)
  - Projects by Status (pie chart)
  - Role Distribution (bar chart)
  - Feature Usage (horizontal bars)
- Statistics cards:
  - Total Users
  - Active Projects
  - Total Scripts
  - Storage Used
- Top Creators table
- Recent Activity feed

### Test 5.2: Date Range Filter

**Steps:**
1. On analytics page
2. Set date range: Last 30 days
3. Click "Apply"

**Expected:**
- Charts update with filtered data
- Stats recalculated for period
- URL updates with date params

### Test 5.3: Export Analytics

**Steps:**
1. Click "Export Report" button
2. Choose format: CSV

**Expected:**
- CSV file downloads
- Contains all analytics data
- Properly formatted
- Can open in Excel

**Verify CSV contains:**
- User counts by date
- Project counts by status
- Role distribution
- Feature usage stats

---

## 🔒 PART 6: Testing Security Logs

### Test 6.1: View Security Logs

**Steps:**
1. Navigate to: `http://localhost:3000/admin/security`

**Expected:**
- Timeline of activities
- Each log entry shows:
  - Timestamp
  - User (name + email)
  - Action (color-coded)
  - IP address
  - Details
- Pagination (50 logs per page)

### Test 6.2: Filter Logs

**Steps:**
1. Select action type: "user.login"
2. Set date range: Today
3. Click "Filter"

**Expected:**
- Only login events shown
- Within today's date range
- Count updates

### Test 6.3: Search Logs

**Steps:**
1. Enter user email in search
2. Click "Search"

**Expected:**
- Only logs for that user
- All action types
- Chronological order

### Test 6.4: Export Logs

**Steps:**
1. Set filters (optional)
2. Click "Export Logs"
3. Choose CSV format

**Expected:**
- CSV downloads
- Contains filtered logs
- All fields included

---

## 🔍 PART 7: Testing API Endpoints

### Test 7.1: Get JWT Token

```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@cineforge.ai",
    "password": "Admin@123"
  }'
```

**Expected response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": 1,
    "email": "admin@cineforge.ai",
    "role": "admin",
    "first_name": "Admin",
    "last_name": "User"
  }
}
```

**Copy the token for next tests**

### Test 7.2: Get Admin Dashboard

```bash
curl -X GET http://127.0.0.1:5000/api/admin/dashboard \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected response:**
```json
{
  "stats": {
    "total_users": 15,
    "active_projects": 8,
    "total_scenes": 42,
    "storage_used_gb": 5.2
  },
  "recent_activity": [...]
}
```

### Test 7.3: Get Users List

```bash
curl -X GET "http://127.0.0.1:5000/api/admin/users?page=1&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected response:**
```json
{
  "users": [
    {
      "user_id": 1,
      "email": "admin@cineforge.ai",
      "first_name": "Admin",
      "last_name": "User",
      "role": "admin",
      "created_at": "2025-11-13T10:00:00Z"
    },
    ...
  ],
  "total": 15,
  "page": 1,
  "limit": 10
}
```

### Test 7.4: Create User via API

```bash
curl -X POST http://127.0.0.1:5000/api/admin/users \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "API",
    "last_name": "Test",
    "email": "apitest@example.com",
    "password": "Test@123",
    "role": "filmmaker"
  }'
```

**Expected response:**
```json
{
  "message": "User created successfully",
  "user": {
    "user_id": 16,
    "email": "apitest@example.com",
    "role": "filmmaker"
  }
}
```

### Test 7.5: Update User via API

```bash
curl -X PUT http://127.0.0.1:5000/api/admin/users/16 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Updated",
    "role": "investor"
  }'
```

**Expected response:**
```json
{
  "message": "User updated successfully",
  "user": {
    "user_id": 16,
    "first_name": "Updated",
    "role": "investor"
  }
}
```

### Test 7.6: Delete User via API

```bash
curl -X DELETE http://127.0.0.1:5000/api/admin/users/16 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected response:**
```json
{
  "message": "User deleted successfully"
}
```

### Test 7.7: Get Analytics

```bash
curl -X GET "http://127.0.0.1:5000/api/admin/analytics?start_date=2025-01-01&end_date=2025-12-31" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected response:**
```json
{
  "user_growth": [...],
  "project_stats": {...},
  "engagement": {...}
}
```

### Test 7.8: Get Security Logs

```bash
curl -X GET "http://127.0.0.1:5000/api/admin/security/logs?page=1&limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected response:**
```json
{
  "logs": [
    {
      "log_id": 1,
      "timestamp": "2025-11-13T15:30:00Z",
      "user_id": 1,
      "action": "user.login",
      "ip_address": "127.0.0.1",
      "details": {...}
    },
    ...
  ],
  "total": 500,
  "page": 1
}
```

---

## ✅ PART 8: Verification Checklist

### Frontend Checks

- [ ] Login page accessible
- [ ] Admin can login with correct credentials
- [ ] Admin Panel link appears after login
- [ ] `/admin/users` route accessible
- [ ] `/admin/users/:id` route accessible
- [ ] `/admin/settings` route accessible
- [ ] `/admin/analytics` route accessible
- [ ] `/admin/security` route accessible
- [ ] Non-admin users redirected from admin routes
- [ ] All admin pages load without errors
- [ ] Navigation between admin pages works
- [ ] Modals display properly
- [ ] Forms validate input
- [ ] Success/error messages show correctly

### Backend Checks

- [ ] Admin endpoints return 200 for admin users
- [ ] Admin endpoints return 403 for non-admin users
- [ ] JWT token required for all admin routes
- [ ] Token validation works correctly
- [ ] Role check works (admin vs non-admin)
- [ ] CRUD operations work (Create, Read, Update, Delete)
- [ ] Database updates persist
- [ ] Error handling works (try invalid requests)
- [ ] Pagination works correctly
- [ ] Search/filter works
- [ ] Analytics calculations accurate
- [ ] Security logs created for actions
- [ ] Settings changes apply correctly

### Database Checks

```sql
-- Verify admin user
SELECT * FROM users WHERE role = 'admin';

-- Check user counts
SELECT role, COUNT(*) FROM users GROUP BY role;

-- Recent activity
SELECT * FROM activity_logs ORDER BY timestamp DESC LIMIT 10;

-- System settings
SELECT * FROM system_settings;
```

### Security Checks

- [ ] Non-admin cannot access admin routes
- [ ] Expired tokens rejected
- [ ] Invalid tokens rejected
- [ ] SQL injection prevented (try: `' OR '1'='1`)
- [ ] XSS prevented (try: `<script>alert(1)</script>`)
- [ ] CSRF protection works
- [ ] Password hashing works (check database)
- [ ] Sensitive data not exposed in responses
- [ ] Rate limiting works (make 100 requests)
- [ ] Session timeout works

---

## 🐛 Common Issues & Solutions

### Issue: Can't login as admin

**Solution:**
```python
# Verify in Python
from app import app, db
from models import User

with app.app_context():
    admin = User.query.filter_by(email='admin@cineforge.ai').first()
    print(f"Exists: {admin is not None}")
    if admin:
        print(f"Role: {admin.role}")
        print(f"Verified: {admin.verified}")
```

### Issue: Admin routes return 403

**Solution:**
```javascript
// Check token in browser console
const token = localStorage.getItem('token');
const payload = JSON.parse(atob(token.split('.')[1]));
console.log('Token role:', payload.role);
// Should be 'admin'
```

### Issue: Database connection error

**Solution:**
```bash
# Check database status
psql -d cineforge_db -c "SELECT 1;"

# Check backend .env
cat backend/.env | grep DATABASE_URL
```

### Issue: Frontend won't start

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Issue: Changes not saving

**Solution:**
1. Check browser Network tab for API errors
2. Check backend logs: `tail -f backend/logs/app.log`
3. Verify database permissions
4. Check for validation errors in API response

---

## 📈 Performance Testing

### Load Test: 100 Users

```bash
# Install Apache Bench
apt-get install apache2-utils

# Test login endpoint
ab -n 100 -c 10 -p login.json -T application/json \
  http://127.0.0.1:5000/api/auth/login

# Test admin dashboard
ab -n 100 -c 10 -H "Authorization: Bearer TOKEN" \
  http://127.0.0.1:5000/api/admin/dashboard
```

**Expected:**
- < 200ms average response time
- 0% failed requests
- Consistent throughput

### Database Performance

```sql
-- Check slow queries
EXPLAIN ANALYZE SELECT * FROM users WHERE role = 'admin';

-- Check index usage
SELECT * FROM pg_stat_user_indexes;

-- Check table sizes
SELECT 
  relname as table_name,
  pg_size_pretty(pg_total_relation_size(relid)) as size
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC;
```

---

## 🎉 Success Criteria

**Admin panel is fully functional if:**

✅ Admin can login with credentials
✅ All admin routes accessible
✅ Can view all users
✅ Can create new users
✅ Can edit existing users
✅ Can delete users
✅ Can reset passwords
✅ Analytics displays correctly
✅ Security logs show activities
✅ Settings can be modified
✅ All API endpoints work
✅ Non-admin users blocked
✅ Database updates persist
✅ No console errors
✅ Responsive design works

**If all checks pass, your admin panel is production-ready! 🚀**

---

**Testing completed by:** _________________  
**Date:** _________________  
**Version:** 1.0  
**Status:** _________________
