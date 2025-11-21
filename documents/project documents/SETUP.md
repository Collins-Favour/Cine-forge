# CineForge AI - Setup & Run Guide

## Prerequisites

- **Python 3.12+**
- **Node.js 18+**
- **MySQL 8.0+**
- **Redis** (optional, for real-time features)

## Backend Setup

### 1. Database Setup

```bash
# Create database
mysql -u root -p
CREATE DATABASE cineforge_db;
exit

# Import schema
Get-Content "database\schema.sql" | mysql -u root -p cineforge_db
```

### 2. Environment Configuration

Create `backend\.env`:

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production

# Database
DATABASE_URL=mysql+pymysql://root:password@localhost/cineforge_db

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-here

# AI API Keys
GROQ_API_KEY=your-groq-api-key
GEMINI_API_KEY=your-gemini-api-key

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# CORS
FRONTEND_URL=http://localhost:3000
```

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Run Backend

```bash
python app.py
# Server runs on http://localhost:5000
```

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Environment Configuration

Already configured in `.env`:

```env
VITE_API_URL=http://localhost:5000/api
VITE_SOCKET_URL=http://localhost:5000
```

### 3. Run Frontend

```bash
npm run dev
# App runs on http://localhost:3000
```

## Running Both Servers

### Option 1: Two Terminals

**Terminal 1 (Backend):**
```bash
cd backend
python app.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

### Option 2: PowerShell Script

Create `start-dev.ps1`:

```powershell
# Start Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python app.py"

# Wait for backend to start
Start-Sleep -Seconds 3

# Start Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "✅ CineForge AI is starting..." -ForegroundColor Green
Write-Host "Backend: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
```

Run: `.\start-dev.ps1`

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html
```

### Frontend Tests

```bash
cd frontend

# Unit tests
npm test

# E2E tests (install browsers first)
npx playwright install
npm run test:e2e
```

## Production Build

### Backend

```bash
cd backend
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Frontend

```bash
cd frontend
npm run build
# Output in dist/

# Preview production build
npm run preview
```

## Troubleshooting

### Backend not connecting to database

1. Check MySQL is running: `mysql -u root -p`
2. Verify database exists: `SHOW DATABASES;`
3. Check DATABASE_URL in `.env`

### Frontend can't connect to backend

1. Ensure backend is running on port 5000
2. Check console for CORS errors
3. Verify VITE_API_URL in `.env`

### Port already in use

```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Change port in backend/app.py:
app.run(port=5001)
```

## Quick Start (Development)

```bash
# 1. Start backend (Terminal 1)
cd backend
python app.py

# 2. Start frontend (Terminal 2)
cd frontend
npm run dev

# 3. Open browser
http://localhost:3000
```

## Default Credentials

After running the app, register with any email or use test accounts if seeded.

## API Documentation

Once backend is running:
- Swagger/OpenAPI: `http://localhost:5000/api/docs` (if configured)
- API endpoints available at: `http://localhost:5000/api`

## Project Structure

```
CINEFORGE AI/
├── backend/          # Flask API
│   ├── models/       # Database models
│   ├── routes/       # API endpoints
│   ├── services/     # Business logic
│   ├── utils/        # Helpers
│   └── tests/        # Backend tests
├── frontend/         # React app
│   └── src/
│       ├── pages/    # Route pages
│       ├── components/ # UI components
│       ├── services/ # API calls
│       ├── store/    # State management
│       └── tests/    # Frontend tests
└── database/         # SQL schema
```

## Need Help?

- Check logs in terminal
- Review `.env` configuration
- Ensure all dependencies installed
- Verify ports 3000 and 5000 are available
