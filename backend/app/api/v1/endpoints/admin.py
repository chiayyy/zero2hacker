from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel

from app.core.database import get_db
from app.models.user import User as UserModel
from app.models.challenge import Challenge, ChallengeAttempt
from app.models.lab import LabProgress
from app.utils.auth import get_current_admin_user

router = APIRouter()


# ---------- Response schemas ----------

class AdminUserEntry(BaseModel):
    id: int
    email: str
    username: str
    display_name: Optional[str]
    role: str
    skill_level: str
    total_points: int
    level: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_activity: Optional[datetime]
    challenges_solved: int
    challenges_attempted: int

    class Config:
        from_attributes = True


class ChallengeResetResponse(BaseModel):
    message: str
    user_id: int
    challenge_id: int


class UserToggleResponse(BaseModel):
    message: str
    user_id: int
    is_active: bool


class AdminChallengeEntry(BaseModel):
    id: int
    title: str
    difficulty: str
    points: int
    category_id: int

    class Config:
        from_attributes = True


# ---------- Endpoints ----------

@router.get("/users", response_model=List[AdminUserEntry])
async def list_all_users(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """List all users with activity stats (admin only)"""
    users = db.query(UserModel).order_by(UserModel.created_at.desc()).all()

    result = []
    for user in users:
        solved = db.query(func.count(ChallengeAttempt.id)).filter(
            ChallengeAttempt.user_id == user.id,
            ChallengeAttempt.is_correct == True
        ).scalar() or 0

        attempted = db.query(func.count(ChallengeAttempt.id)).filter(
            ChallengeAttempt.user_id == user.id
        ).scalar() or 0

        result.append(AdminUserEntry(
            id=user.id,
            email=user.email,
            username=user.username,
            display_name=user.display_name,
            role=user.role,
            skill_level=user.skill_level,
            total_points=user.total_points,
            level=user.level,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            last_activity=user.last_activity,
            challenges_solved=solved,
            challenges_attempted=attempted,
        ))

    return result


@router.patch("/users/{user_id}/toggle-active", response_model=UserToggleResponse)
async def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Activate or deactivate a user account (admin only)"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = not user.is_active
    db.commit()

    action = "activated" if user.is_active else "deactivated"
    return UserToggleResponse(
        message=f"User {user.username} has been {action}",
        user_id=user.id,
        is_active=user.is_active
    )


@router.delete("/users/{user_id}/reset-challenge/{challenge_id}", response_model=ChallengeResetResponse)
async def reset_user_challenge(
    user_id: int,
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Reset a specific challenge attempt for a user (admin only)"""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    # Find existing attempt
    attempt = db.query(ChallengeAttempt).filter(
        ChallengeAttempt.user_id == user_id,
        ChallengeAttempt.challenge_id == challenge_id
    ).first()

    if not attempt:
        raise HTTPException(status_code=404, detail="No attempt found for this user and challenge")

    # Deduct points if it was solved
    if attempt.is_correct and attempt.points_earned:
        user.total_points = max(0, user.total_points - attempt.points_earned)

    # Delete the attempt
    db.delete(attempt)
    db.commit()

    return ChallengeResetResponse(
        message=f"Challenge '{challenge.title}' reset for user '{user.username}'",
        user_id=user_id,
        challenge_id=challenge_id
    )


@router.get("/challenges", response_model=List[AdminChallengeEntry])
async def list_challenges_for_admin(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """List all challenges for admin use (id + title only)"""
    challenges = db.query(Challenge).order_by(Challenge.id).all()
    return challenges


@router.get("/users/{user_id}/attempts")
async def get_user_attempts(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get all challenge attempts for a specific user"""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    attempts = db.query(ChallengeAttempt, Challenge).join(
        Challenge, ChallengeAttempt.challenge_id == Challenge.id
    ).filter(ChallengeAttempt.user_id == user_id).all()

    return [
        {
            "attempt_id": a.id,
            "challenge_id": c.id,
            "challenge_title": c.title,
            "difficulty": c.difficulty,
            "points": c.points,
            "status": a.status,
            "is_correct": a.is_correct,
            "points_earned": a.points_earned,
            "started_at": a.started_at,
            "completed_at": a.completed_at,
        }
        for a, c in attempts
    ]
