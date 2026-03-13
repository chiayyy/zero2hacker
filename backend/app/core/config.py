from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Zero2Hacker CTF Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "*"]

    # Firebase
    FIREBASE_PROJECT_ID: str = "zero2hacker-ctf"
    FIREBASE_PRIVATE_KEY_ID: str = ""
    FIREBASE_PRIVATE_KEY: str = ""
    FIREBASE_CLIENT_EMAIL: str = ""
    FIREBASE_CLIENT_ID: str = ""
    FIREBASE_AUTH_URI: str = "https://accounts.google.com/o/oauth2/auth"
    FIREBASE_TOKEN_URI: str = "https://oauth2.googleapis.com/token"

    # Database
    DATABASE_URL: str = "sqlite:///./zero2hacker.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # AI/Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODELS: List[str] = ["llama3", "mistral", "codellama"]

    # Docker
    DOCKER_SOCKET: str = "/var/run/docker.sock"
    CHALLENGE_NETWORK: str = "ctf-challenges"

    # Challenge settings
    MAX_CHALLENGE_RUNTIME: int = 3600  # 1 hour
    MAX_CONCURRENT_CHALLENGES: int = 100

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()