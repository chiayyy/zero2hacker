from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class LabProgress(Base):
    __tablename__ = "lab_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    lab_id = Column(String(100), nullable=False, index=True)
    unlocked_level = Column(Integer, default=1)
    level_scores = Column(JSON, default=dict)   # rolling window scores per level
    total_completed = Column(Integer, default=0)
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
