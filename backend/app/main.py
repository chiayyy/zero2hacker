from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from contextlib import asynccontextmanager
from pathlib import Path

from app.core.config import settings
from app.api.v1.router import api_router
from app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown


app = FastAPI(
    title="Zero2Hacker CTF Platform",
    description="AI-driven adaptive CTF platform for cybersecurity education",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Mount static files for challenge resources at /files to avoid CRA dev proxy conflict
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/files", StaticFiles(directory=str(static_path)), name="static")

# Security
security = HTTPBearer()


@app.get("/")
async def root():
    return {
        "message": "Welcome to Zero2Hacker CTF Platform",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "zero2hacker-backend"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False
    )