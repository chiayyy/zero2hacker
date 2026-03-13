from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class UserAnalytics(Base):
    __tablename__ = "user_analytics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Skill progression
    current_skill_level = Column(String(50), default="beginner")
    skill_progression = Column(Text, nullable=True)  # JSON string
    strengths = Column(Text, nullable=True)  # JSON string
    weaknesses = Column(Text, nullable=True)  # JSON string

    # Learning patterns
    preferred_difficulty = Column(String(20), nullable=True)
    avg_session_duration = Column(Float, nullable=True)  # minutes
    peak_activity_hours = Column(Text, nullable=True)  # JSON string
    learning_velocity = Column(Float, nullable=True)  # challenges per week

    # Performance metrics
    total_challenges_attempted = Column(Integer, default=0)
    total_challenges_solved = Column(Integer, default=0)
    solve_rate = Column(Float, default=0.0)
    avg_solve_time = Column(Float, nullable=True)  # minutes
    fastest_solve_time = Column(Float, nullable=True)  # minutes

    # Category performance
    category_performance = Column(Text, nullable=True)  # JSON string
    favorite_categories = Column(Text, nullable=True)  # JSON string

    # Engagement metrics
    total_login_days = Column(Integer, default=0)
    consecutive_days = Column(Integer, default=0)
    last_login = Column(DateTime(timezone=True), nullable=True)
    total_time_spent = Column(Integer, default=0)  # minutes

    # AI recommendations
    recommended_challenges = Column(Text, nullable=True)  # JSON string
    recommended_topics = Column(Text, nullable=True)  # JSON string
    personalization_data = Column(Text, nullable=True)  # JSON string

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="analytics")


class SessionLog(Base):
    __tablename__ = "session_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Session details
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    device_type = Column(String(50), nullable=True)

    # Activity tracking
    pages_visited = Column(Text, nullable=True)  # JSON string
    challenges_viewed = Column(Text, nullable=True)  # JSON string
    actions_performed = Column(Text, nullable=True)  # JSON string

    # Performance data
    load_times = Column(Text, nullable=True)  # JSON string
    errors_encountered = Column(Text, nullable=True)  # JSON string

    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Integer, nullable=True)  # seconds

    # Relationships
    user = relationship("User", back_populates="session_logs")