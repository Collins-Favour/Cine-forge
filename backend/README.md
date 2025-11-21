# CineForge AI Backend

Flask-based backend API for CineForge AI script-to-visual platform.

## Project Structure

```
backend/
├── app.py                 # Application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── models/               # SQLAlchemy database models
│   ├── __init__.py
│   ├── user.py          # User and authentication
│   ├── project.py       # Project management
│   ├── script.py        # Script versions and characters
│   ├── scene.py         # Scene management
│   ├── storyboard.py    # Storyboard panels
│   ├── checklist.py     # Production checklists
│   ├── collaboration.py # C-Space messaging
│   ├── ai.py            # AI processing logs
│   ├── notification.py  # User notifications
│   ├── export.py        # File exports
│   └── system.py        # System settings
├── routes/              # API route handlers
│   ├── __init__.py
│   ├── auth.py          # Authentication endpoints
│   ├── users.py         # User management
│   ├── projects.py      # Project CRUD
│   ├── scripts.py       # Script management
│   ├── scenes.py        # Scene management
│   ├── storyboards.py   # Storyboard generation
│   ├── collaboration.py # C-Space collaboration
│   └── ai.py            # AI processing
├── services/            # Business logic layer
│   ├── __init__.py
│   ├── groq_service.py  # Groq AI integration
│   └── gemini_service.py # Gemini AI integration
├── utils/               # Utility functions
│   ├── __init__.py
│   ├── validators.py    # Input validation
│   ├── decorators.py    # Custom decorators
│   └── helpers.py       # Helper functions
└── socketio_events.py   # Real-time SocketIO events
```

## Setup

### Prerequisites
- Python 3.12+
- MySQL 8.0+
- Redis (for Celery task queue)

### Installation

1. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (`.env`):
```
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=mysql+pymysql://root:password@localhost/cineforge_ai
GROQ_API_KEY=your-groq-key
GEMINI_API_KEY=your-gemini-key
REDIS_URL=redis://localhost:6379/0
```

4. Initialize database:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

5. Run application:
```bash
python app.py
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user

### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create project
- `GET /api/projects/<id>` - Get project details
- `PUT /api/projects/<id>` - Update project
- `DELETE /api/projects/<id>` - Archive project

### Real-time (SocketIO)
- `connect` - Establish WebSocket connection
- `join_project` - Join project room
- `send_message` - Send C-Space message
- `ai_generation_update` - AI progress updates

## Database Models

24 tables covering:
- User management & authentication
- Project & collaboration
- Script versions & characters
- Scene breakdown & analysis
- Storyboard generation
- Production checklists
- Budget tracking
- Real-time messaging
- AI processing logs
- Notifications & analytics

## Development

Run in development mode:
```bash
export FLASK_ENV=development
python app.py
```

Run tests:
```bash
pytest
```

## License

COLLINS LICENSE - See LICENSE file for details.
