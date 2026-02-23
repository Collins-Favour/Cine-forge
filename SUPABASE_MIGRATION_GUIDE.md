# 🚀 CINEFORGE AI - Migration from XAMPP to Supabase

This guide will help you migrate from XAMPP (MySQL) to Supabase (PostgreSQL).

## 📋 Table of Contents
- [Why Supabase?](#why-supabase)
- [Prerequisites](#prerequisites)
- [Step-by-Step Migration](#step-by-step-migration)
- [Testing the Migration](#testing-the-migration)
- [Troubleshooting](#troubleshooting)
- [Additional Features](#additional-features)

---

## 🎯 Why Supabase?

**Benefits over XAMPP:**
- ✅ **Cloud-hosted** - No need for local MySQL server
- ✅ **PostgreSQL** - More powerful and standards-compliant than MySQL
- ✅ **Built-in features** - Authentication, Storage, Real-time subscriptions
- ✅ **Free tier** - 500MB database, unlimited API requests
- ✅ **Automatic backups** - Daily backups included
- ✅ **Scalability** - Easy to scale as your app grows
- ✅ **Modern tooling** - Great dashboard, CLI tools, migrations support

---

## 📦 Prerequisites

Before starting, make sure you have:
- [ ] A Supabase account (free tier is fine)
- [ ] Python 3.8+ installed
- [ ] Git (optional, for version control)

---

## 🔧 Step-by-Step Migration

### Step 1: Create a Supabase Project

1. **Sign up for Supabase**
   - Go to [https://app.supabase.com](https://app.supabase.com)
   - Click "New Project"
   - Choose your organization
   - Fill in project details:
     - **Name:** `cineforge-ai` (or your preferred name)
     - **Database Password:** Create a strong password (SAVE THIS!)
     - **Region:** Choose closest to you or your users
     - **Pricing Plan:** Free tier is sufficient to start

2. **Wait for project initialization** (takes ~2 minutes)

---

### Step 2: Get Your Database Connection String

1. In your Supabase dashboard, go to **Settings** > **Database**
2. Scroll down to **Connection string** section
3. Select **URI** tab
4. Copy the connection string (looks like this):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.yourproject.supabase.co:5432/postgres
   ```
5. Replace `[YOUR-PASSWORD]` with the database password you created

**For Production (recommended):** Use Connection Pooling:
- Go to **Settings** > **Database** > **Connection Pooling**
- Copy the pooler connection string (port 6543)
- It looks like:
  ```
  postgresql://postgres:[YOUR-PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres
  ```

---

### Step 3: Update Your Local Environment

1. **Create a `.env` file** (copy from `.env.example`):
   ```bash
   cd "C:\Users\Kaptain\Documents\CINEFORGE AI"
   copy .env.example .env
   ```

2. **Edit `.env` file** and update these values:
   ```env
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.yourproject.supabase.co:5432/postgres
   SECRET_KEY=your-unique-secret-key-here
   JWT_SECRET_KEY=your-unique-jwt-secret-here
   ```

3. **Update your Python dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

   This will install `psycopg2-binary` (PostgreSQL driver) instead of `PyMySQL`.

---

### Step 4: Create Database Schema in Supabase

You have **two options**:

#### Option A: Using Supabase SQL Editor (Recommended)

1. In Supabase dashboard, go to **SQL Editor**
2. Click **New Query**
3. Open the file: `database/schema_postgresql.sql`
4. Copy the entire content
5. Paste it into the Supabase SQL Editor
6. Click **Run** (or press `Ctrl+Enter` / `Cmd+Enter`)
7. Wait for execution to complete (should see "Success" message)

#### Option B: Using Supabase CLI

1. **Install Supabase CLI**:
   ```bash
   npm install -g supabase
   ```

2. **Login to Supabase**:
   ```bash
   supabase login
   ```

3. **Link your project**:
   ```bash
   cd "C:\Users\Kaptain\Documents\CINEFORGE AI"
   supabase link --project-ref your-project-ref
   ```

4. **Run migration**:
   ```bash
   supabase db push --db-url "your-connection-string" < database/schema_postgresql.sql
   ```

---

### Step 5: Migrate Existing Data (if applicable)

If you have existing data in MySQL that you want to migrate:

#### Option 1: Export and Import Manually

1. **Export data from MySQL** (from XAMPP):
   ```bash
   # Open XAMPP MySQL admin or use command line
   mysqldump -u root cineforge_ai > cineforge_backup.sql
   ```

2. **Convert MySQL dump to PostgreSQL format**:
   - Use a tool like [pgloader](https://pgloader.io/) or
   - Manually edit the SQL file to match PostgreSQL syntax
   - Or use online converters

3. **Import to Supabase**:
   - Use Supabase SQL Editor to run INSERT statements

#### Option 2: Use Python Script (Recommended for large datasets)

Create a migration script: `backend/migrate_to_supabase.py`

```python
"""
Migrate data from MySQL to PostgreSQL/Supabase
"""
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# Old MySQL connection
mysql_engine = create_engine('mysql+pymysql://root:@localhost/cineforge_ai')

# New PostgreSQL connection
postgres_engine = create_engine(os.getenv('DATABASE_URL'))

# Add your migration logic here
# Example: Copy users table
with mysql_engine.connect() as mysql_conn:
    users = mysql_conn.execute("SELECT * FROM users")
    with postgres_engine.connect() as pg_conn:
        for user in users:
            pg_conn.execute(
                "INSERT INTO users (...) VALUES (...)",
                user
            )
```

---

### Step 6: Create Admin User

Run the admin creation script:

```bash
cd backend
python create_default_admin.py
```

Or create manually in Supabase SQL Editor:

```sql
-- Create admin user
INSERT INTO users (username, email, password_hash, role, is_active, is_verified)
VALUES (
    'admin',
    'admin@cineforge.ai',
    -- Generate hash using bcrypt in Python:
    -- from flask_bcrypt import generate_password_hash
    -- generate_password_hash('your-password').decode('utf-8')
    '$2b$12$your-hashed-password-here',
    'admin',
    TRUE,
    TRUE
);
```

---

### Step 7: Test the Connection

1. **Test database connection**:
   ```bash
   cd backend
   python test_db_connection.py
   ```

2. **Start the Flask application**:
   ```bash
   python app.py
   ```

3. **Check for errors** in terminal output

---

### Step 8: Update Frontend Configuration (if needed)

If your frontend has any direct database references:

1. Update API endpoints (should already be using your Flask backend)
2. No changes needed if using REST API properly

---

## 🧪 Testing the Migration

### Test Checklist:

- [ ] **Database connection works**
  ```bash
  python backend/test_db_connection.py
  ```

- [ ] **Can create a user**
  - Register a new user through the frontend/API

- [ ] **Can login**
  - Login with the new user credentials

- [ ] **Can create a project**
  - Create a new film project

- [ ] **Can add scenes**
  - Add scenes to the project

- [ ] **Can upload files**
  - Test profile picture upload

- [ ] **Real-time features work**
  - Test C-Space chat functionality

---

## 🐛 Troubleshooting

### Common Issues:

#### 1. Connection Error: "FATAL: password authentication failed"
**Solution:** 
- Double-check your database password in `.env`
- Make sure you replaced `[YOUR-PASSWORD]` with actual password
- Password should NOT be in square brackets

#### 2. Error: "psycopg2.OperationalError: could not connect"
**Solution:**
- Check your internet connection
- Verify the host URL in connection string
- Make sure Supabase project is active

#### 3. SSL Connection Error
**Solution:**
Add `?sslmode=require` to your DATABASE_URL:
```env
DATABASE_URL=postgresql://postgres:password@host:5432/postgres?sslmode=require
```

#### 4. Schema Creation Fails
**Solution:**
- Run schema creation in smaller chunks
- Check Supabase logs in Dashboard > Database > Logs
- Make sure you're using `schema_postgresql.sql`, not the MySQL version

#### 5. Migration Performance is Slow
**Solution:**
- Use connection pooling (port 6543)
- Batch your INSERT statements
- Consider using COPY command for bulk imports

#### 6. JSON/JSONB Column Errors
**Solution:**
PostgreSQL uses `JSONB` (binary JSON) which is more efficient:
- The schema already uses `JSONB`
- When inserting, use proper JSON: `'{"key": "value"}'::jsonb`

---

## 🚀 Additional Features

### Enable Row Level Security (RLS)

Supabase supports Row Level Security for fine-grained access control:

```sql
-- Enable RLS on users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only update their own profile
CREATE POLICY users_update_own ON users
    FOR UPDATE
    USING (auth.uid()::text = user_id::text);

-- Policy: Anyone can view active users
CREATE POLICY users_select_active ON users
    FOR SELECT
    USING (is_active = true);
```

### Use Supabase Storage for File Uploads

Instead of local file storage:

1. **Create a storage bucket** in Supabase:
   - Dashboard > Storage > New Bucket
   - Name: `cineforge-uploads`
   - Public: Yes (or No for private files)

2. **Update your file upload code**:
   ```python
   from supabase import create_client
   
   supabase = create_client(
       os.getenv('SUPABASE_URL'),
       os.getenv('SUPABASE_KEY')
   )
   
   # Upload file
   supabase.storage.from_('cineforge-uploads').upload(
       'path/to/file.jpg',
       file_data
   )
   ```

### Enable Real-time Subscriptions

Supabase provides real-time updates:

```javascript
// In your frontend
const { data, error } = await supabase
  .from('cspace_messages')
  .select('*')
  .eq('project_id', projectId)
  .order('sent_at', { ascending: false })

// Subscribe to new messages
const subscription = supabase
  .from('cspace_messages')
  .on('INSERT', payload => {
    console.log('New message:', payload.new)
  })
  .subscribe()
```

### Set Up Automatic Backups

Supabase provides daily automatic backups on paid plans. For free tier:

1. **Manual backups via CLI**:
   ```bash
   supabase db dump -f backup.sql
   ```

2. **Schedule regular dumps** (Windows Task Scheduler):
   - Create a batch file with the dump command
   - Schedule it to run daily/weekly

---

## 📚 Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy PostgreSQL Dialect](https://docs.sqlalchemy.org/en/14/dialects/postgresql.html)
- [Supabase Python Client](https://github.com/supabase-community/supabase-py)

---

## ✅ Migration Complete!

You've successfully migrated from XAMPP to Supabase! 🎉

**Next Steps:**
1. Test all features thoroughly
2. Update any documentation
3. Consider enabling additional Supabase features
4. Set up monitoring and alerts
5. Plan for scaling as your user base grows

**Need Help?**
- Check Supabase Community: https://github.com/supabase/supabase/discussions
- PostgreSQL Community: https://www.postgresql.org/community/

---

## 🔄 Rollback Plan (Just in Case)

If you need to rollback to XAMPP:

1. **Keep XAMPP installed** (don't uninstall yet)
2. **Revert `requirements.txt`**:
   ```
   PyMySQL==1.1.0  # Instead of psycopg2-binary
   ```
3. **Revert `config.py`**:
   ```python
   SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/cineforge_ai'
   ```
4. **Reinstall old dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Load your MySQL backup** if you created one

---

**Good luck with your migration! 🚀**
