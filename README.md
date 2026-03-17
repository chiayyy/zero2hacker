# Zero2Hacker: AI-Personalized CTF Platform

An AI-driven Capture The Flag (CTF) platform for cybersecurity education with personalized, adaptive challenges.

## Features
- AI-driven adaptive challenge generation
- Multi-level difficulty progression (Beginner → Expert)
- Categories: Crypto, Web Security, Network, Steganography
- Real-time leaderboards and learning analytics
- Lab environment for hands-on practice
- Gamification system

## Tech Stack
- **Backend**: FastAPI (Python) + SQLite
- **Frontend**: React + TypeScript + Tailwind CSS
- **AI**: Ollama (LLaMA 3, Mistral, CodeLlama) — optional
- **Auth**: JWT (dev mode, no Firebase needed locally)

---

## Quick Start (Local Setup)

### Prerequisites
- Python 3.8+
- Node.js 16+ and npm
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/chiayyy/zero2hacker.git
cd zero2hacker
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env       # Windows
cp .env.example .env         # Mac/Linux

# Create the admin account (also initializes the database)
python create_admin.py

# Start the backend server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend runs at: **http://localhost:8000**  
API Docs: **http://localhost:8000/docs**

### 3. Frontend Setup

Open a **new terminal**:

```bash
cd frontend

# Set up environment variables
copy .env.example .env       # Windows
cp .env.example .env         # Mac/Linux

# Install dependencies
npm install

# Start the development server
npm start
```

Frontend runs at: **http://localhost:3000**

---

## Default Login

After running `python create_admin.py`, log in with:

| Field    | Value                  |
|----------|------------------------|
| Email    | admin@zero2hacker.com  |
| Password | admin123               |

Or register a new account at http://localhost:3000/register

---

## Troubleshooting

**Backend won't start**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend won't start**
```bash
cd frontend
rm -rf node_modules
npm install
```

**Port already in use (Windows)**
```bash
netstat -ano | findstr :3000
taskkill /F /PID <PID>
```

**Reset the database**
```bash
cd backend
del zero2hacker.db        # Windows
rm zero2hacker.db         # Mac/Linux
python create_admin.py
```

---

## Project Structure

```
zero2hacker/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/             # API endpoints
│   │   ├── core/            # Config and security
│   │   ├── models/          # Database models
│   │   └── services/        # Business logic
│   ├── create_admin.py      # Admin setup script
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment template
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── pages/           # Page views
│   │   ├── contexts/        # React contexts
│   │   └── lib/             # Lab utilities
│   └── .env.example         # Environment template
└── SETUP_GUIDE.md           # Detailed setup guide
```

---

## License
MIT License
