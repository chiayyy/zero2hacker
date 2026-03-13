from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    STUDENT = "student"
    EDUCATOR = "educator"
    ADMIN = "admin"


class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    display_name: Optional[str] = Field(None, max_length=100)
    role: UserRole = UserRole.STUDENT
    skill_level: SkillLevel = SkillLevel.BEGINNER
    experience_months: int = Field(0, ge=0)
    bio: Optional[str] = None
    preferred_categories: Optional[List[str]] = None
    learning_style: Optional[str] = None


class UserCreate(UserBase):
    firebase_uid: str
    password: Optional[str] = None


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    skill_level: Optional[SkillLevel] = None
    experience_months: Optional[int] = None
    preferred_categories: Optional[List[str]] = None
    learning_style: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    id: int
    firebase_uid: str
    avatar_url: Optional[str] = None
    total_points: int
    level: int
    badges: Optional[List[str]] = None
    streak_days: int
    last_activity: Optional[datetime] = None
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class User(UserResponse):
    pass