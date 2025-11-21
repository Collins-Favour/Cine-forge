# CINEFORGE AI - Complete Admin Guide

**Version:** 1.0  
**Last Updated:** November 13, 2025  
**Status:** Production Ready

---

## Table of Contents
1. [Admin Login & Access](#admin-login--access)
2. [Admin Dashboard Overview](#admin-dashboard-overview)
3. [User Management](#user-management)
4. [System Settings](#system-settings)
5. [Analytics & Reporting](#analytics--reporting)
6. [Security & Audit Logs](#security--audit-logs)
7. [API Reference](#api-reference)
8. [Troubleshooting](#troubleshooting)

---

## Admin Login & Access

### Creating Your First Admin Account

#### Method 1: Database Direct Creation (Recommended for Initial Setup)
```python
# Run this in your Python terminal or create a script
from backend.app import app, db
from backend.models import User
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
    print(f"Admin created: {admin.email}")
```

#### Method 2: Via Backend API (After First Admin Exists)
```bash
curl -X POST http://127.0.0.1:5000/api/admin/users \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "New",
    "last_name": "Admin",
    "email": "newadmin@cineforge.ai",
    "password": "SecurePass@123",
    "role": "admin"
  }'
```

### Login Process

#### Step 1: Navigate to Login Page
- **URL:** `http://localhost:3000/login`
- **Credentials:**
  - Email: `admin@cineforge.ai`
  - Password: `Admin@123` (or your custom password)

#### Step 2: Verify Admin Role
After login, check if you have admin access:
- Look for "Admin Panel" or "Admin" link in navigation
- Admin users should see additional menu items
- Dashboard should show admin-specific options

#### Step 3: Access Admin Panel
- **Direct URL:** `http://localhost:3000/admin/users`
- **From Dashboard:** Click "Admin Panel" or navigate via menu

### Default Admin Credentials

| Environment | Email | Password | Notes |
|------------|-------|----------|-------|
| Development | `admin@cineforge.ai` | `Admin@123` | Change immediately in production |
| Production | Custom | Custom | Set via environment variables |

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- Special characters recommended

---

## Admin Dashboard Overview

### Access Routes

| Page | Route | Description |
|------|-------|-------------|
| User Management | `/admin/users` | View, edit, delete users |
| User Details | `/admin/users/:userId` | Detailed user profile |
| System Settings | `/admin/settings` | Platform configuration |
| Analytics | `/admin/analytics` | Usage statistics & charts |
| Security Logs | `/admin/security` | Audit trail & activity logs |

### Quick Stats Dashboard

The admin dashboard displays:
- **Total Users** - All registered users
- **Active Projects** - Projects in development
- **Total Scenes** - Scenes across all projects
- **Storage Used** - Platform storage consumption
- **Recent Activity** - Latest user actions
- **System Health** - Server status indicators

---

## User Management

### Viewing Users

#### User List Features
- **Search:** Filter by name, email, or role
- **Pagination:** 20 users per page
- **Quick Actions:** Edit, Delete, Reset Password
- **Role Badges:** Visual role identification
- **Status Indicators:** Active, Verified, Banned

#### User Roles
1. **Admin** - Full platform access
2. **Filmmaker** - Create projects, scripts, storyboards
3. **Investor** - View projects, financials
4. **Actor** - View scripts, submit auditions
5. **Crew Member** - Assigned project access

### Creating Users

**Via Admin Panel:**
1. Navigate to `/admin/users`
2. Click "Add New User" button
3. Fill in details:
   - First Name, Last Name
   - Email (must be unique)
   - Password (auto-generated or custom)
   - Role selection
   - Verification status
4. Click "Create User"

**API Endpoint:**
```bash
POST /api/admin/users
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "password": "SecurePass@123",
  "role": "filmmaker",
  "verified": true
}
```

### Editing Users

1. Click user row or "Edit" button
2. Navigate to `/admin/users/:userId`
3. Modify fields:
   - **Profile Info:** Name, email, phone, location, bio
   - **Role:** Change user role (affects permissions)
   - **Status:** Active, banned, verified
   - **Subscription:** Plan tier and expiration
4. Click "Save Changes"

**Editable Fields:**
- first_name, last_name
- email (triggers re-verification)
- phone, location, bio
- role (admin, filmmaker, investor, actor, crew_member)
- verified (email verification status)
- subscription_tier (free, basic, pro, enterprise)
- subscription_expires_at (date)

### Deleting Users

**Soft Delete (Recommended):**
- User account deactivated
- Data preserved for 30 days
- Can be restored

**Hard Delete:**
- Permanent deletion
- All user data removed
- Projects transferred or deleted

**Process:**
1. Select user
2. Click "Delete User"
3. Confirm deletion in modal
4. Choose soft or hard delete
5. Data cascade: Projects, Scripts, Messages

### Resetting Passwords

**Via Admin Panel:**
1. Go to user details page
2. Click "Reset Password" button
3. Choose method:
   - **Generate New:** System creates secure password
   - **Send Email:** User receives reset link
   - **Set Custom:** Admin sets specific password
4. Copy/share new credentials securely

**API Endpoint:**
```bash
POST /api/admin/users/:id/reset-password
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "new_password": "NewSecure@Pass123",
  "notify_user": true
}
```

### Bulk Actions

- **Export Users:** CSV download with filters
- **Bulk Delete:** Select multiple users
- **Bulk Role Change:** Update multiple user roles
- **Send Announcements:** Email all users

---

## System Settings

### Platform Configuration

#### General Settings

| Setting | Description | Default | Options |
|---------|-------------|---------|---------|
| Site Name | Platform display name | "CineForge AI" | Text |
| Maintenance Mode | Block user access | Off | On/Off |
| Registration | Allow new signups | Enabled | Enabled/Disabled |
| Email Verification | Require email verify | Required | Required/Optional |

#### File Upload Limits

```json
{
  "max_file_size_mb": 100,
  "allowed_file_types": [".pdf", ".jpg", ".png", ".mp4", ".mov"],
  "storage_quota_per_user_gb": 10,
  "max_project_files": 500
}
```

#### AI Features

- **AI Script Analysis:** Enable/Disable
- **AI Storyboard Generation:** Enable/Disable
- **AI Character Detection:** Enable/Disable
- **API Rate Limits:** Requests per minute
- **Model Selection:** GPT-4, Claude, etc.

#### Security Settings

```json
{
  "session_timeout_minutes": 60,
  "max_login_attempts": 5,
  "lockout_duration_minutes": 30,
  "require_2fa_for_admins": true,
  "password_expiry_days": 90
}
```

#### Email Settings

```json
{
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_user": "noreply@cineforge.ai",
  "from_name": "CineForge AI",
  "support_email": "support@cineforge.ai"
}
```

### Updating Settings

1. Navigate to `/admin/settings`
2. Modify values in form
3. Click "Save Settings"
4. Settings applied immediately
5. Restart required for some changes (indicated)

**API Endpoint:**
```bash
PUT /api/admin/settings
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "site_name": "CineForge AI",
  "maintenance_mode": false,
  "registration_enabled": true,
  "max_file_size_mb": 100
}
```

---

## Analytics & Reporting

### Dashboard Metrics

#### User Metrics
- **Total Users:** All-time registrations
- **Active Users:** 30-day active
- **New Registrations:** By day/week/month
- **User Growth Rate:** Percentage change
- **Role Distribution:** Pie chart

#### Project Metrics
- **Total Projects:** All projects
- **Active Projects:** In development
- **Completed Projects:** Finished
- **Scripts Created:** Total script count
- **Average Project Size:** Scripts per project

#### Engagement Metrics
- **Daily Active Users (DAU)**
- **Monthly Active Users (MAU)**
- **Average Session Duration**
- **Feature Usage:** Script editor, storyboard, AI
- **Collaboration Stats:** Messages, shared projects

### Charts & Visualizations

**Available Charts:**
1. **User Growth Over Time** - Line chart
2. **Project Creation Trend** - Bar chart
3. **Role Distribution** - Pie chart
4. **Feature Usage** - Horizontal bar chart
5. **Top Creators** - Leaderboard table
6. **Storage Usage** - Progress bars

### Exporting Reports

**Export Formats:**
- CSV (Data tables)
- PDF (Full report with charts)
- JSON (API data)

**Example Export:**
```bash
GET /api/admin/analytics/export?format=csv&start_date=2025-01-01&end_date=2025-12-31
Authorization: Bearer <admin_token>
```

### Custom Reports

Create custom analytics queries:
```sql
-- Example: Users by role and creation date
SELECT role, DATE(created_at) as date, COUNT(*) as count
FROM users
WHERE created_at >= '2025-01-01'
GROUP BY role, DATE(created_at)
ORDER BY date DESC
```

---

## Security & Audit Logs

### Activity Log

The security logs track all significant actions:

#### Logged Events

| Event Type | Description | Severity |
|------------|-------------|----------|
| user.login | Successful login | Info |
| user.logout | User logout | Info |
| user.register | New registration | Info |
| user.delete | User deletion | Warning |
| user.update | Profile changes | Info |
| admin.access | Admin panel access | Warning |
| password.reset | Password reset | Warning |
| project.create | New project | Info |
| project.delete | Project deletion | Warning |
| settings.update | System settings change | Critical |
| security.lockout | Account locked | Critical |

### Viewing Logs

1. Navigate to `/admin/security`
2. Filter by:
   - **Date Range:** Custom start/end dates
   - **User:** Specific user ID or email
   - **Action:** Event type
   - **Severity:** Info, Warning, Critical
3. Sort by timestamp (newest first)
4. Pagination: 50 logs per page

### Log Entry Details

Each log contains:
```json
{
  "log_id": 12345,
  "timestamp": "2025-11-13T15:30:00Z",
  "user_id": 42,
  "user_email": "user@example.com",
  "action": "project.delete",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "details": {
    "project_id": 789,
    "project_name": "My Film"
  },
  "severity": "warning"
}
```

### Security Alerts

**Automatic Alerts for:**
- Multiple failed login attempts (5+)
- Admin access from new IP
- Bulk user deletions (10+)
- Settings changes in production
- Unusual API usage patterns
- Large file uploads (>100MB)

### Compliance & Retention

- **Retention Period:** 90 days (configurable)
- **GDPR Compliance:** User data export/deletion
- **Audit Trail:** Immutable log entries
- **Backup:** Daily log backups

---

## API Reference

### Authentication

All admin endpoints require JWT token with admin role:

```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "admin@cineforge.ai",
  "password": "Admin@123"
}

Response:
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

### Admin Endpoints

#### Dashboard
```bash
GET /api/admin/dashboard
Authorization: Bearer <admin_token>

Response: {
  "stats": {
    "total_users": 150,
    "active_projects": 45,
    "total_scenes": 320,
    "storage_used_gb": 125.5
  },
  "recent_activity": [...]
}
```

#### User Management
```bash
# List users
GET /api/admin/users?page=1&limit=20&search=john&role=filmmaker

# Get user details
GET /api/admin/users/:id

# Update user
PUT /api/admin/users/:id
Body: { "first_name": "John", "role": "filmmaker" }

# Delete user
DELETE /api/admin/users/:id

# Reset password
POST /api/admin/users/:id/reset-password
Body: { "new_password": "NewPass@123" }
```

#### Projects
```bash
# List all projects
GET /api/admin/projects?page=1&limit=20

# Delete project
DELETE /api/admin/projects/:id
```

#### Analytics
```bash
# Get analytics data
GET /api/admin/analytics?start_date=2025-01-01&end_date=2025-12-31

# Overview stats
GET /api/admin/analytics/overview
```

#### Security Logs
```bash
# Get logs
GET /api/admin/security/logs?page=1&limit=50&action=user.login&start_date=2025-11-01
```

#### Settings
```bash
# Get settings
GET /api/admin/settings

# Update settings
PUT /api/admin/settings
Body: { "maintenance_mode": true, "site_name": "CineForge" }
```

### Error Responses

```json
{
  "error": "Unauthorized",
  "message": "Admin access required",
  "status": 403
}

Common Status Codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized (no token)
- 403: Forbidden (not admin)
- 404: Not Found
- 500: Server Error
```

---

## Troubleshooting

### Common Issues

#### Cannot Access Admin Panel

**Problem:** "Access Denied" or redirect to dashboard

**Solutions:**
1. Check user role in database:
   ```sql
   SELECT user_id, email, role FROM users WHERE email = 'admin@cineforge.ai';
   ```
2. Verify role is exactly `'admin'` (case-sensitive)
3. Clear browser cache and localStorage
4. Re-login with admin credentials
5. Check JWT token payload:
   ```javascript
   // In browser console
   const token = localStorage.getItem('token');
   const payload = JSON.parse(atob(token.split('.')[1]));
   console.log(payload.role); // Should be 'admin'
   ```

#### Admin Routes Return 404

**Problem:** Routes like `/admin/users` show "Page Not Found"

**Solutions:**
1. Verify frontend is running: `http://localhost:3000`
2. Check `App.jsx` has admin routes registered
3. Clear React Router cache (refresh page)
4. Check browser console for JS errors
5. Verify AdminRoute component exists

#### Backend Admin Endpoints Return 403

**Problem:** API calls to `/api/admin/*` fail

**Solutions:**
1. Check JWT token is valid and not expired
2. Verify token has admin role
3. Check backend logs for errors:
   ```bash
   # In backend directory
   tail -f logs/app.log
   ```
4. Verify `check_admin()` function in `admin.py`
5. Test with curl:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" http://127.0.0.1:5000/api/admin/dashboard
   ```

#### Changes Not Saving

**Problem:** Admin settings or user edits don't persist

**Solutions:**
1. Check browser Network tab for API errors
2. Verify database connection in backend
3. Check for validation errors in API response
4. Ensure backend is running: `http://127.0.0.1:5000`
5. Check database write permissions
6. Verify no database transaction conflicts

#### Admin User Cannot Login

**Problem:** Correct credentials rejected

**Solutions:**
1. Reset password via database:
   ```python
   from werkzeug.security import generate_password_hash
   user.password_hash = generate_password_hash('NewPassword@123')
   db.session.commit()
   ```
2. Check email is verified: `verified = True`
3. Check account not banned
4. Verify password hash format in database
5. Check backend logs for authentication errors

### Debug Mode

Enable verbose logging:

**Backend (`backend/app.py`):**
```python
app.config['DEBUG'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True

# Add detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Frontend (Browser Console):**
```javascript
// Check auth state
console.log(localStorage.getItem('token'));
console.log(localStorage.getItem('user'));

// Check admin access
import { useAuthStore } from '@store/authStore';
const { user } = useAuthStore();
console.log('User role:', user.role);
console.log('Is admin:', user.role === 'admin');
```

### Performance Issues

If admin panel is slow:
1. **Database Indexing:**
   ```sql
   CREATE INDEX idx_users_role ON users(role);
   CREATE INDEX idx_users_created_at ON users(created_at);
   CREATE INDEX idx_activity_logs_timestamp ON activity_logs(timestamp);
   ```

2. **Enable Caching:**
   ```python
   from flask_caching import Cache
   cache = Cache(app, config={'CACHE_TYPE': 'simple'})
   
   @app.route('/api/admin/dashboard')
   @cache.cached(timeout=60)  # Cache for 1 minute
   def dashboard():
       ...
   ```

3. **Pagination:** Always use pagination for large datasets
4. **Lazy Loading:** Load data on demand, not all at once
5. **Database Connection Pool:** Configure SQLAlchemy pool

### Getting Help

**Support Channels:**
- GitHub Issues: Report bugs
- Documentation: Check this guide first
- Backend Logs: `backend/logs/app.log`
- Frontend Console: Browser DevTools
- Database: Direct SQL queries for debugging

**Information to Provide:**
- Error message (full text)
- Steps to reproduce
- Browser and version
- Backend logs (relevant lines)
- Database query that failed
- Expected vs actual behavior

---

## Best Practices

### Security

1. **Change Default Password:** Immediately after setup
2. **Enable 2FA:** For all admin accounts
3. **Audit Regularly:** Review security logs weekly
4. **Limit Admin Accounts:** Only trusted personnel
5. **Use Strong Passwords:** 16+ characters, mixed case, symbols
6. **Rotate Credentials:** Every 90 days
7. **Monitor Access:** Track login times and IPs
8. **Backup Database:** Daily automated backups

### User Management

1. **Verify Users:** Always verify email before activation
2. **Document Changes:** Add notes when editing users
3. **Soft Delete:** Use soft delete for user removal
4. **Role Changes:** Log all role modifications
5. **Password Resets:** Send secure links, don't set directly
6. **Bulk Actions:** Use with caution, test on small sets first

### System Maintenance

1. **Regular Updates:** Keep dependencies updated
2. **Monitor Storage:** Set alerts at 80% capacity
3. **Database Cleanup:** Archive old logs monthly
4. **Performance Testing:** Load test before major releases
5. **Backup Strategy:** 3-2-1 rule (3 copies, 2 mediums, 1 offsite)
6. **Disaster Recovery:** Test restoration procedures quarterly

---

## Appendix

### Admin Role Permissions Matrix

| Feature | Admin | Filmmaker | Investor | Actor | Crew |
|---------|-------|-----------|----------|-------|------|
| View All Users | ✅ | ❌ | ❌ | ❌ | ❌ |
| Edit Users | ✅ | ❌ | ❌ | ❌ | ❌ |
| Delete Users | ✅ | ❌ | ❌ | ❌ | ❌ |
| View Analytics | ✅ | 📊 Own | 📊 Own | ❌ | ❌ |
| System Settings | ✅ | ❌ | ❌ | ❌ | ❌ |
| Security Logs | ✅ | ❌ | ❌ | ❌ | ❌ |
| Create Projects | ✅ | ✅ | ❌ | ❌ | ❌ |
| Delete Any Project | ✅ | 📁 Own | ❌ | ❌ | ❌ |
| AI Features | ✅ | ✅ | ✅ | ✅ | ✅ |
| Export Data | ✅ | 📁 Own | 📁 Own | 📁 Own | 📁 Own |

Legend: ✅ Full Access | ❌ No Access | 📊 Own Data Only | 📁 Own Projects Only

### Database Schema Reference

**Users Table:**
```sql
CREATE TABLE users (
  user_id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  role VARCHAR(50) DEFAULT 'filmmaker',
  verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  subscription_tier VARCHAR(50) DEFAULT 'free',
  subscription_expires_at TIMESTAMP
);
```

### Configuration Files

**Backend `.env`:**
```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost:5432/cineforge
JWT_SECRET_KEY=your-jwt-secret
ADMIN_EMAIL=admin@cineforge.ai
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

**Frontend `.env`:**
```env
VITE_API_URL=http://127.0.0.1:5000/api
VITE_APP_NAME=CineForge AI
```

---

**Document End**

For updates to this guide, check the repository or contact the development team.
