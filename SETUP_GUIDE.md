# Zero2Hacker CTF Platform - Setup Guide

This guide will help you set up and run the Zero2Hacker CTF platform locally.

## Prerequisites

- Python 3.8+
- Node.js 16+ and npm
- Git

## Quick Start (Development Mode)

The platform includes development authentication bypass that allows you to run the application locally without Firebase configuration.

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# The backend is already configured to use SQLite for development
# Database will be created automatically on first run

# Create admin account
python create_admin.py

# Start backend server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be running at: http://localhost:8000
API Documentation: http://localhost:8000/docs

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will be running at: http://localhost:3000

## Development Authentication

The platform includes development authentication endpoints that bypass Firebase for local testing:

###Register a New User (Development)

```bash
POST http://localhost:8000/api/v1/auth/dev-register
```

Parameters:
- `email` (required): User email
- `username` (required): Username (3-50 characters)
- `display_name` (optional): Display name
- `skill_level` (optional): beginner|intermediate|advanced|expert (default: beginner)

Example:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/dev-register?email=user@example.com&username=johndoe&display_name=John%20Doe&skill_level=beginner"
```

### Login (Development)

```bash
POST http://localhost:8000/api/v1/auth/dev-login
```

Parameters:
- `email` (required): User email

Example:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/dev-login?email=admin@zero2hacker.com"
```

### Default Admin Account

After running `python create_admin.py`, you can login with:
- Email: `admin@zero2hacker.com`
- Username: `admin`
- Role: admin

## Environment Configuration

### Backend Configuration

The backend `.env` file is already configured for development:

```env
# Database (SQLite for development)
DATABASE_URL=sqlite:///./zero2hacker.db

# Environment
ENVIRONMENT=development

# Service URLs (optional for basic development)
REDIS_URL=redis://localhost:6379
OLLAMA_BASE_URL=http://localhost:11434

# Security
SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_HOSTS=["http://localhost:3000","http://127.0.0.1:3000"]
```

### Frontend Configuration

The frontend `.env` file includes development mode:

```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000/api/v1

# Application Configuration
REACT_APP_ENVIRONMENT=development
REACT_APP_DEV_MODE=true
```

## Firebase Setup (Production)

For production use, you'll need to configure Firebase Authentication:

### 1. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select an existing one
3. Enable Authentication > Sign-in method > Email/Password

### 2. Get Firebase Configuration

1. In Firebase Console, go to Project Settings
2. Under "Your apps", add a Web app
3. Copy the Firebase configuration

### 3. Update Frontend Environment

Update `frontend/.env` with your Firebase credentials:

```env
REACT_APP_FIREBASE_API_KEY=your-api-key
REACT_APP_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your-project-id
REACT_APP_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
REACT_APP_FIREBASE_APP_ID=your-app-id
REACT_APP_FIREBASE_MEASUREMENT_ID=your-measurement-id

# Disable development mode for production
REACT_APP_DEV_MODE=false
```

### 4. Update Backend Environment

Update `backend/.env`:

```env
ENVIRONMENT=production

# Add Firebase Admin SDK credentials
FIREBASE_SERVICE_ACCOUNT_KEY=/path/to/serviceAccountKey.json
```

### 5. Download Service Account Key

1. In Firebase Console, go to Project Settings > Service Accounts
2. Click "Generate new private key"
3. Save the JSON file securely
4. Update the path in backend `.env`

## Database Management

### Reset Database

To reset the database and start fresh:

```bash
# Stop the backend server
# Delete the database file
cd backend
rm zero2hacker.db

# Recreate admin account
python create_admin.py

# Restart backend server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### View Database

The SQLite database can be viewed using tools like:
- [DB Browser for SQLite](https://sqlitebrowser.org/)
- [SQLite Viewer VSCode Extension](https://marketplace.visualstudio.com/items?itemName=alexcvzz.vscode-sqlite)

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Backend Issues

**Error: Module not found**
```bash
cd backend
pip install -r requirements.txt
```

**Error: Database locked**
- Stop all backend server instances
- Delete `zero2hacker.db`
- Restart server

### Frontend Issues

**Error: Cannot find module**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Error: Port 3000 is already in use**
```bash
# Kill process on port 3000
# Windows:
netstat -ano | findstr :3000
taskkill /F /PID <PID>

# Linux/Mac:
lsof -ti:3000 | xargs kill
```

## Development Workflow

1. Start backend server (port 8000)
2. Start frontend development server (port 3000)
3. Access application at http://localhost:3000
4. Use dev-login/dev-register endpoints for authentication
5. API docs available at http://localhost:8000/docs

## Project Structure

```
zero2hacker-ctf/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core configuration
│   │   ├── models/        # Database models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── services/      # Business logic
│   ├── create_admin.py    # Admin user creation script
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Backend configuration
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── contexts/      # React contexts
│   │   ├── pages/         # Page components
│   │   └── services/      # API services
│   ├── public/
│   └── .env              # Frontend configuration
└── SETUP_GUIDE.md        # This file
```

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Firebase Authentication](https://firebase.google.com/docs/auth)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

## Support

For issues or questions, please check the API documentation at http://localhost:8000/docs or review the error logs in the terminal.
