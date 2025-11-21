# Admin Features Documentation

## Overview
Complete admin panel implementation for CineForge AI with full user management, system settings, analytics, and security monitoring.

## Backend Implementation

### Routes Created
**File:** `backend/routes/admin.py`

#### Admin Dashboard
- **GET** `/api/admin/dashboard`
  - Returns: Total users, users by role, active projects, storage stats, recent users, recent activity
  - Auth: JWT required, admin role only

#### User Management
- **GET** `/api/admin/users`
  - Query params: page, per_page, search, role, status
  - Returns: Paginated user list with filtering
  
- **GET** `/api/admin/users/<user_id>`
  - Returns: Detailed user info, projects, collaborations, messages count, recent activity

- **PUT** `/api/admin/users/<user_id>`
  - Update user: role, email, first_name, last_name, is_active, is_verified

- **DELETE** `/api/admin/users/<user_id>`
  - Soft delete (sets is_active to False)

- **POST** `/api/admin/users/<user_id>/reset-password`
  - Admin password reset functionality

#### Project Management
- **GET** `/api/admin/projects`
  - Query params: page, per_page, search
  - Returns: All projects with pagination

- **DELETE** `/api/admin/projects/<project_id>`
  - Archive project (sets is_archived to True)

#### Analytics
- **GET** `/api/admin/analytics?days=30`
  - Returns: New users over time, new projects, messages, top creators

- **GET** `/api/admin/stats/overview`
  - Returns: Quick stats overview

#### Security Logs
- **GET** `/api/admin/security/logs`
  - Query params: page, per_page
  - Returns: Activity logs with user info, IP addresses, timestamps

#### System Settings
- **GET** `/api/admin/settings`
  - Returns: Current system settings

- **PUT** `/api/admin/settings`
  - Update: site_name, maintenance_mode, registration settings, file limits, feature flags

## Frontend Implementation

### Pages Created

#### 1. User Management (`UserManagement.jsx`)
**Route:** `/admin/users`

Features:
- Paginated user list with search and filtering
- Filter by role: student, filmmaker, professional, admin
- Filter by status: active, inactive, verified, unverified
- Quick stats: Total users, active users, verified users, admin count
- Actions: View details, reset password, delete user
- Export to CSV functionality
- Real-time refresh

**Components:**
- StatCard: Display user statistics
- User table with sortable columns
- Inline actions per user row

#### 2. User Detail (`UserDetail.jsx`)
**Route:** `/admin/users/:userId`

Features:
- View/edit user profile information
- Update role, email, name, active status, verified status
- View user stats: projects count, collaborations, messages
- Recent projects list
- Recent activity log
- Reset password
- Delete user with confirmation
- Navigate back to user list

#### 3. System Settings (`SystemSettings.jsx`)
**Route:** `/admin/settings`

Settings Categories:
- **General:** Site name, maintenance mode
- **User Registration:** Allow registration, require email verification
- **Storage & Files:** Max file size, storage per user limits
- **Platform Features:** AI features toggle, collaboration toggle

**Components:**
- SettingSection: Organized sections with icons
- SettingInput: Text/number inputs
- SettingToggle: Toggle switches for boolean settings

#### 4. Analytics (`Analytics.jsx`)
**Route:** `/admin/analytics`

Charts & Metrics:
- Time range selector: 7/30/90/365 days
- Key metrics cards: New users, projects, messages, engagement rate
- New users line chart (Recharts)
- New projects bar chart
- Message activity line chart
- Top project creators with progress bars
- Activity stats: Peak time, session duration, retention rate

**Libraries Used:**
- Recharts for data visualization
- Framer Motion for animations

#### 5. Security Logs (`SecurityLogs.jsx`)
**Route:** `/admin/security`

Features:
- Real-time activity monitoring
- Security stats dashboard
- Paginated log viewer
- Color-coded action types
- User information per log entry
- IP address tracking
- Timestamp display
- Search/filter functionality

#### 6. Admin Dashboard (`Dashboard.jsx`) - Updated
**Route:** `/admin/dashboard` (existing, now with more data)

Enhanced with:
- Quick action cards linking to all admin pages
- System health metrics
- Recent activity feed
- User statistics by role
- Recent users table

### API Services

**File:** `frontend/src/services/apiServices.js`

Added `adminApi` object:
```javascript
adminApi = {
  getDashboard()
  getUsers(params)
  getUserDetails(userId)
  updateUser(userId, data)
  deleteUser(userId)
  resetUserPassword(userId, newPassword)
  getAllProjects(params)
  deleteProject(projectId)
  getAnalytics(days)
  getStatsOverview()
  getSecurityLogs(params)
  getSettings()
  updateSettings(data)
}
```

### Routing

**File:** `frontend/src/App.jsx`

Added:
- AdminRoute component (checks user.role === 'admin')
- Routes:
  - `/admin/users` → UserManagement
  - `/admin/users/:userId` → UserDetail
  - `/admin/settings` → SystemSettings
  - `/admin/analytics` → Analytics
  - `/admin/security` → SecurityLogs

### Security

**Access Control:**
- Backend: `check_admin()` function validates user role on every request
- Frontend: `AdminRoute` wrapper prevents non-admin access
- JWT authentication required for all admin endpoints
- 403 Forbidden returned for non-admin users

**Soft Delete:**
- Users are deactivated (is_active = False) instead of hard deletion
- Projects are archived (is_archived = True) instead of deletion
- Preserves data integrity and audit trail

## User Interface Features

### Modal Integration
All admin pages use the modal system:
- ✅ SuccessModal: Operation confirmations
- ❌ ErrorModal: Error notifications
- ❓ ConfirmModal: Delete confirmations
- 📝 PromptModal: Password reset input

### Responsive Design
- Mobile-friendly tables with horizontal scroll
- Collapsible sidebars
- Touch-optimized buttons
- Adaptive grid layouts

### Loading States
- Skeleton loaders
- Spinner animations
- Disabled buttons during operations
- Optimistic UI updates

## Database Schema

### Users Table
Fields used by admin:
- user_id, username, email
- first_name, last_name, profile_pic_url, bio
- role (enum: student, filmmaker, professional, admin)
- is_active, is_verified
- last_login, created_at, updated_at

### Activity Logs (Optional)
For security logging:
- log_id, user_id, action, description
- ip_address, user_agent
- created_at

## Installation & Setup

### Backend
1. Register admin blueprint:
```python
# backend/app.py
from routes.admin import admin_bp
app.register_blueprint(admin_bp, url_prefix='/api/admin')
```

2. No additional dependencies required

### Frontend
1. Install chart library (if not already):
```bash
npm install recharts
```

2. All components already use existing dependencies:
   - react-query for data fetching
   - framer-motion for animations
   - lucide-react for icons

## Usage

### Creating an Admin User
```python
# In Flask shell or migration
user = User.query.filter_by(email='admin@example.com').first()
user.role = 'admin'
db.session.commit()
```

### Accessing Admin Panel
1. Login as admin user
2. Navigate to `/admin/users` or click admin links in dashboard
3. Only users with role='admin' can access admin routes

## Testing

### Admin Access
- ✅ Non-admin users redirected to dashboard
- ✅ Admin routes require authentication
- ✅ CRUD operations validated

### User Management
- ✅ List users with pagination
- ✅ Filter by role and status
- ✅ Update user information
- ✅ Reset passwords
- ✅ Delete (deactivate) users

### Analytics
- ✅ Charts render with data
- ✅ Time range selector works
- ✅ Empty state handling

### Settings
- ✅ Settings load and update
- ✅ Toggle switches function
- ✅ Save confirmation

## Future Enhancements

### Potential Additions
1. **Bulk Operations:** Select multiple users for bulk actions
2. **Advanced Filters:** Date ranges, custom queries
3. **Email Notifications:** Email users on admin actions
4. **Audit Trail:** Detailed log of all admin actions
5. **Role Permissions:** Granular permission system
6. **Data Export:** Export analytics to PDF/Excel
7. **Real-time Updates:** WebSocket notifications for admin events
8. **User Impersonation:** Login as user for support
9. **System Backups:** Database backup management
10. **API Rate Limiting:** Configure rate limits per user/role

## API Response Examples

### GET /api/admin/dashboard
```json
{
  "total_users": 150,
  "users_by_role": {
    "filmmaker": 80,
    "student": 50,
    "professional": 15,
    "admin": 5
  },
  "active_projects": 234,
  "storage_used": 117.0,
  "system_alerts": 0,
  "recent_users": [...]
}
```

### GET /api/admin/users
```json
{
  "users": [...],
  "total": 150,
  "page": 1,
  "per_page": 20,
  "pages": 8
}
```

### GET /api/admin/analytics?days=30
```json
{
  "new_users": [
    {"date": "2025-11-01", "count": 5},
    {"date": "2025-11-02", "count": 8}
  ],
  "new_projects": [...],
  "messages": [...],
  "top_creators": [...]
}
```

## Error Handling

### Backend Errors
- 403: Admin access required
- 404: User/project not found
- 400: Invalid data/email in use
- 500: Server error

### Frontend Handling
- ErrorModal shows user-friendly messages
- Failed operations don't corrupt state
- Network errors caught and displayed
- Validation before API calls

## Performance Optimizations

### Backend
- Pagination on all list endpoints
- Database indexes on user_id, email, role
- Eager loading of relationships
- Query result caching (optional)

### Frontend
- React Query caching
- Lazy loading of charts
- Debounced search inputs
- Optimistic UI updates
- Virtual scrolling for large lists (future)

## Conclusion

The admin panel is now fully functional with:
- ✅ Complete user management CRUD
- ✅ System settings configuration
- ✅ Analytics and reporting
- ✅ Security and activity logging
- ✅ Professional UI with modals
- ✅ Mobile responsive design
- ✅ Secure role-based access control

All features integrate seamlessly with the existing CineForge AI application architecture.
