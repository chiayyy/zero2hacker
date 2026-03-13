from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(enum.Enum):
    STUDENT = "student"
    EDUCATOR = "educator"
    ADMIN = "admin"


class SkillLevel(enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String(128), unique=True, index=True, nullable=True)  # Optional for local auth
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # For local authentication
    display_name = Column(String(100), nullable=True)

    # Profile information
    role = Column(String(20), default="student")
    skill_level = Column(String(20), default="beginner")
    experience_months = Column(Integer, default=0)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)

    # Learning preferences
    preferred_categories = Column(Text, nullable=True)  # JSON string
    learning_style = Column(String(50), nullable=True)  # visual, kinesthetic, etc.

    # Gamification
    total_points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    badges = Column(Text, nullable=True)  # JSON string
    streak_days = Column(Integer, default=0)
    last_activity = Column(DateTime(timezone=True), nullable=True)

    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    challenge_attempts = relationship("ChallengeAttempt", back_populates="user")
    analytics = relationship("UserAnalytics", back_populates="user", uselist=False)
    session_logs = relationship("SessionLog", back_populates="user")
    ratings = relationship("ChallengeRating", back_populates="user")
    generated_challenges = relationship("Challenge", back_populates="generated_for_user")