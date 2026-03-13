from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class DifficultyLevel(enum.Enum):
    BEGINNER = "beginner"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class ChallengeStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    RETIRED = "retired"
    MAINTENANCE = "maintenance"


class AttemptStatus(enum.Enum):
    IN_PROGRESS = "in_progress"
    SOLVED = "solved"
    FAILED = "failed"
    TIMEOUT = "timeout"


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    short_description = Column(String(500), nullable=True)

    # Challenge metadata
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    difficulty = Column(Enum(DifficultyLevel, native_enum=False, length=20), nullable=False)
    points = Column(Integer, nullable=False)
    estimated_time = Column(Integer, nullable=True)  # minutes

    # Content
    flag = Column(String(255), nullable=False)
    hints = Column(Text, nullable=True)  # JSON string
    solution = Column(Text, nullable=True)
    writeup = Column(Text, nullable=True)

    # Files and resources
    files_url = Column(String(500), nullable=True)
    docker_image = Column(String(255), nullable=True)
    docker_port = Column(Integer, nullable=True)
    container_config = Column(Text, nullable=True)  # JSON string

    # AI-related fields
    generated_by_ai = Column(Boolean, default=False)
    ai_model_used = Column(String(100), nullable=True)
    generation_prompt = Column(Text, nullable=True)
    quality_score = Column(Float, nullable=True)

    # Personalization
    generated_for_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Adaptive learning
    prerequisite_challenges = Column(Text, nullable=True)  # JSON string
    learning_objectives = Column(Text, nullable=True)  # JSON string
    tags = Column(Text, nullable=True)  # JSON string

    # Status and metrics
    status = Column(Enum(ChallengeStatus, native_enum=False, length=20), default=ChallengeStatus.DRAFT)
    solve_count = Column(Integer, default=0)
    attempt_count = Column(Integer, default=0)
    average_rating = Column(Float, nullable=True)
    average_solve_time = Column(Float, nullable=True)  # minutes

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    category = relationship("Category", back_populates="challenges")
    attempts = relationship("ChallengeAttempt", back_populates="challenge")
    ratings = relationship("ChallengeRating", back_populates="challenge")
    generated_for_user = relationship("User", back_populates="generated_challenges", foreign_keys=[generated_for_user_id])


class ChallengeAttempt(Base):
    __tablename__ = "challenge_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)

    # Attempt details
    status = Column(Enum(AttemptStatus, native_enum=False, length=20), default=AttemptStatus.IN_PROGRESS)
    flag_submitted = Column(String(255), nullable=True)
    is_correct = Column(Boolean, default=False)
    points_earned = Column(Integer, default=0)

    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    time_spent = Column(Integer, nullable=True)  # seconds

    # Learning analytics
    hints_used = Column(Integer, default=0)
    hint_requests = Column(Text, nullable=True)  # JSON string
    container_actions = Column(Text, nullable=True)  # JSON string
    progress_snapshots = Column(Text, nullable=True)  # JSON string

    # Relationships
    user = relationship("User", back_populates="challenge_attempts")
    challenge = relationship("Challenge", back_populates="attempts")


class ChallengeRating(Base):
    __tablename__ = "challenge_ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)

    # Ratings (1-5 scale)
    difficulty_rating = Column(Integer, nullable=True)
    quality_rating = Column(Integer, nullable=True)
    enjoyment_rating = Column(Integer, nullable=True)

    # Feedback
    feedback = Column(Text, nullable=True)
    suggested_improvements = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="ratings")
    challenge = relationship("Challenge", back_populates="ratings")