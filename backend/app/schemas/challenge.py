from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import json


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class ChallengeStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    RETIRED = "retired"
    MAINTENANCE = "maintenance"


class AttemptStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    SOLVED = "solved"
    FAILED = "failed"
    TIMEOUT = "timeout"


class ChallengeBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str
    short_description: Optional[str] = Field(None, max_length=500)
    category_id: int
    difficulty: DifficultyLevel
    points: int = Field(..., ge=1)
    estimated_time: Optional[int] = Field(None, ge=1)
    hints: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None


class ChallengeCreate(ChallengeBase):
    flag: str
    files_url: Optional[str] = None
    docker_image: Optional[str] = None
    docker_port: Optional[int] = None
    container_config: Optional[Dict[str, Any]] = None
    solution: Optional[str] = None
    writeup: Optional[str] = None


class ChallengeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    points: Optional[int] = None
    estimated_time: Optional[int] = None
    hints: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    status: Optional[ChallengeStatus] = None


class ChallengeResponse(ChallengeBase):
    id: int
    slug: str
    status: ChallengeStatus
    solve_count: int
    attempt_count: int
    average_rating: Optional[float] = None
    average_solve_time: Optional[float] = None
    generated_by_ai: bool
    ai_model_used: Optional[str] = None
    quality_score: Optional[float] = None
    files_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    @field_validator('hints', 'tags', 'learning_objectives', mode='before')
    @classmethod
    def parse_json_fields(cls, v):
        """Convert JSON strings to lists"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, ValueError):
                return None
        return v

    class Config:
        from_attributes = True


class Challenge(ChallengeResponse):
    pass


class ChallengeAttemptCreate(BaseModel):
    challenge_id: int
    flag_submitted: Optional[str] = None


class ChallengeAttemptResponse(BaseModel):
    id: int
    user_id: int
    challenge_id: int
    status: AttemptStatus
    is_correct: bool
    points_earned: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    time_spent: Optional[int] = None
    hints_used: int

    class Config:
        from_attributes = True


class ChallengeAttempt(ChallengeAttemptResponse):
    pass


class ChallengeRatingCreate(BaseModel):
    challenge_id: int
    difficulty_rating: Optional[int] = Field(None, ge=1, le=5)
    quality_rating: Optional[int] = Field(None, ge=1, le=5)
    enjoyment_rating: Optional[int] = Field(None, ge=1, le=5)
    feedback: Optional[str] = None
    suggested_improvements: Optional[str] = None