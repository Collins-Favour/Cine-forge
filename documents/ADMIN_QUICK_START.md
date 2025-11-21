# CINEFORGE AI - Admin Quick Start

## 🚀 Get Admin Access in 5 Minutes

### Step 1: Create Admin Account (First Time Only)

**Option A: Using Python (Recommended)**
```bash
cd backend
python -c "
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
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
    print('✅ Admin created successfully!')
"
```

**Option B: Using Database Directly**
```sql
-- Connect to your PostgreSQL database
INSERT INTO users (email, password_hash, first_name, last_name, role, verified)
VALUES (
  'admin@cineforge.ai',
  'scrypt:32768:8:1$...',  -- Use werkzeug to generate this
  'Admin',
  'User',
  'admin',
  true
);
```

### Step 2: Login to CineForge

1. **Open Browser:** `http://localhost:3000/login`
2. **Enter Credentials:**
   - Email: `admin@cineforge.ai`
   - Password: `Admin@123`
3. **Click Login**

### Step 3: Access Admin Panel

**Direct URLs:**
- Dashboard: `http://localhost:3000/admin/users`
- User Management: `http://localhost:3000/admin/users`
- System Settings: `http://localhost:3000/admin/settings`
- Analytics: `http://localhost:3000/admin/analytics`
- Security Logs: `http://localhost:3000/admin/security`

**Or navigate via menu:**
1. After login, look for "Admin Panel" in navigation
2. Click to access admin features

---

## 🔧 Essential Admin Tasks

### View All Users
```
Navigate to: /admin/users
- See all registered users
- Search by name/email
- Filter by role
- Sort by date
```

### Create New User
```
1. Go to /admin/users
2. Click "Add New User"
3. Fill form:
   - First/Last Name
   - Email (unique)
   - Password
   - Role (filmmaker/investor/actor/crew_member/admin)
4. Click "Create User"
```

### Edit User Details
```
1. Go to /admin/users
2. Click on user row
3. Edit fields
4. Click "Save Changes"
```

### Reset User Password
```
1. Go to /admin/users/:userId
2. Click "Reset Password"
3. Choose:
   - Generate new password
   - Send reset email
   - Set custom password
4. Confirm action
```

### Delete User
```
1. Go to /admin/users
2. Click user row
3. Click "Delete User"
4. Confirm deletion
```

### View Analytics
```
Navigate to: /admin/analytics
- User growth charts
- Project statistics
- Engagement metrics
- Top creators
- Export reports
```

### Check Security Logs
```
Navigate to: /admin/security
- View all activity
- Filter by date/user/action
- Monitor security events
- Export logs
```

### Update System Settings
```
Navigate to: /admin/settings
- Site name
- Maintenance mode
- Registration settings
- File upload limits
- Email configuration
- Click "Save Settings"
```

---

## 📋 Admin Credentials Cheat Sheet

| Environment | URL | Email | Password |
|------------|-----|-------|----------|
| **Development** | http://localhost:3000 | admin@cineforge.ai | Admin@123 |
| **Staging** | https://staging.cineforge.ai | Set custom | Set custom |
| **Production** | https://cineforge.ai | Set custom | Set custom |

⚠️ **IMPORTANT:** Change default password immediately in production!

---

## 🔑 API Access (for scripts/automation)

### Get Admin Token
```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@cineforge.ai",
    "password": "Admin@123"
  }'

# Response:
# {
#   "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "user": { ... }
# }
```

### Use Admin Token
```bash
# Example: Get all users
curl -X GET http://127.0.0.1:5000/api/admin/users \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Example: Get dashboard stats
curl -X GET http://127.0.0.1:5000/api/admin/dashboard \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🆘 Troubleshooting

### Problem: Can't access admin panel (403 Forbidden)

**Solution 1: Check user role**
```sql
SELECT user_id, email, role FROM users WHERE email = 'admin@cineforge.ai';
-- role must be exactly 'admin' (lowercase)
```

**Solution 2: Update role**
```sql
UPDATE users SET role = 'admin' WHERE email = 'admin@cineforge.ai';
```

**Solution 3: Clear browser cache**
```javascript
// In browser console
localStorage.clear();
// Then login again
```

### Problem: Wrong password

**Reset password via database:**
```python
from werkzeug.security import generate_password_hash

# In Python shell
new_hash = generate_password_hash('NewPassword@123')
print(new_hash)

# Then in SQL:
# UPDATE users SET password_hash = 'PASTE_HASH_HERE' WHERE email = 'admin@cineforge.ai';
```

### Problem: Admin routes show 404

**Fix:**
1. Check frontend is running: `http://localhost:3000`
2. Verify `App.jsx` has admin routes
3. Refresh browser (Ctrl+F5)
4. Check browser console for errors

### Problem: Backend returns 401 Unauthorized

**Fix:**
1. Login again to get fresh token
2. Check token not expired (tokens expire after 24h)
3. Verify backend is running: `http://127.0.0.1:5000`
4. Check Authorization header format: `Bearer TOKEN`

---

## 🎯 Most Common Admin Actions

### Check how many users
```
GET /api/admin/dashboard
Look at: stats.total_users
```

### See recent activity
```
GET /api/admin/security/logs?limit=10
```

### Find user by email
```
GET /api/admin/users?search=john@example.com
```

### Make someone admin
```
PUT /api/admin/users/:id
Body: { "role": "admin" }
```

### Export all users
```
GET /api/admin/users?limit=1000
Save response to CSV
```

### Check system health
```
GET /api/admin/dashboard
View: storage_used, active_projects, etc.
```

---

## 📱 Admin Panel Features Overview

### User Management (`/admin/users`)
- ✅ View all users
- ✅ Search & filter
- ✅ Pagination
- ✅ Create new users
- ✅ Edit user details
- ✅ Delete users
- ✅ Reset passwords
- ✅ Change roles
- ✅ View user projects
- ✅ View user activity

### User Details (`/admin/users/:userId`)
- ✅ Full profile view
- ✅ Edit all fields
- ✅ User statistics
- ✅ Project list
- ✅ Recent activity
- ✅ Quick actions

### System Settings (`/admin/settings`)
- ✅ Site configuration
- ✅ Maintenance mode
- ✅ Registration settings
- ✅ File upload limits
- ✅ Feature toggles
- ✅ Email settings

### Analytics (`/admin/analytics`)
- ✅ User growth charts
- ✅ Project statistics
- ✅ Engagement metrics
- ✅ Role distribution
- ✅ Top creators
- ✅ Export reports

### Security Logs (`/admin/security`)
- ✅ Activity timeline
- ✅ Filter by date/user/action
- ✅ Severity levels
- ✅ IP tracking
- ✅ Audit trail
- ✅ Export logs

---

## 🔒 Security Best Practices

1. **Change Default Password**
   ```
   First login → Settings → Security → Update Password
   ```

2. **Use Strong Passwords**
   - Minimum 12 characters
   - Mix of upper/lower/numbers/symbols
   - Don't reuse passwords

3. **Enable 2FA** (when available)
   ```
   Settings → Security → Two-Factor Authentication → Enable
   ```

4. **Regular Audits**
   ```
   Weekly: Check security logs
   Monthly: Review user list
   Quarterly: Export full audit
   ```

5. **Limit Admin Accounts**
   - Only give admin to trusted personnel
   - Use least privilege principle
   - Remove admin from inactive users

6. **Monitor Access**
   ```
   Check security logs for:
   - Failed login attempts
   - Admin access from new IPs
   - Unusual activity patterns
   ```

---

## 📞 Need Help?

**Full Documentation:** `documents/ADMIN_COMPLETE_GUIDE.md`

**Quick Checks:**
- ✅ Backend running: `http://127.0.0.1:5000`
- ✅ Frontend running: `http://localhost:3000`
- ✅ Database connected: Check backend logs
- ✅ Admin role set: Check SQL query above

**Common Commands:**
```bash
# Start backend
cd backend && python app.py

# Start frontend
cd frontend && npm run dev

# Check logs
tail -f backend/logs/app.log
```

---

**Last Updated:** November 13, 2025
