from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import json


class UserAnalyticsResponse(BaseModel):
    id: int
    user_id: int
    current_skill_level: str
    preferred_difficulty: Optional[str] = None
    avg_session_duration: Optional[float] = None
    learning_velocity: Optional[float] = None
    total_challenges_attempted: int
    total_challenges_solved: int
    solve_rate: float
    avg_solve_time: Optional[float] = None
    fastest_solve_time: Optional[float] = None
    total_login_days: int
    consecutive_days: int
    last_login: Optional[datetime] = None
    total_time_spent: int
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    category_performance: Optional[Dict[str, Any]] = None
    favorite_categories: Optional[List[str]] = None
    recommended_challenges: Optional[List[int]] = None
    recommended_topics: Optional[List[str]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_validator('strengths', 'weaknesses', 'favorite_categories', 'recommended_topics', mode='before')
    @classmethod
    def parse_json_str_list(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return None
        return v

    @field_validator('recommended_challenges', mode='before')
    @classmethod
    def parse_json_int_list(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return None
        return v

    @field_validator('category_performance', mode='before')
    @classmethod
    def parse_json_dict(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return None
        return v

    class Config:
        from_attributes = True


class UserAnalytics(UserAnalyticsResponse):
    pass


class SessionLogCreate(BaseModel):
    session_id: str
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    device_type: Optional[str] = None


class SessionLogResponse(BaseModel):
    id: int
    user_id: int
    session_id: str
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    device_type: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration: Optional[int] = None
    pages_visited: Optional[List[str]] = None
    challenges_viewed: Optional[List[int]] = None
    actions_performed: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True


class SessionLog(SessionLogResponse):
    pass


class LearningProgressResponse(BaseModel):
    total_challenges: int
    solved_challenges: int
    current_streak: int
    points_earned: int
    skill_progression: Dict[str, Any]
    recent_activity: List[Dict[str, Any]]
    category_breakdown: Dict[str, Dict[str, Any]]


class LeaderboardEntry(BaseModel):
    user_id: int
    username: str
    display_name: Optional[str] = None
    total_points: int
    level: int
    solve_count: int
    rank: int
    avatar_url: Optional[str] = None