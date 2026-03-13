from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.user import UserResponse
from app.schemas.analytics import LeaderboardEntry, LearningProgressResponse
from app.services.user_service import UserService
from app.services.analytics_service import AnalyticsService
from app.utils.auth import get_current_user, get_current_admin_user

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get list of users (admin only)"""
    # Implementation would go here
    return []


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get user by ID (users can only see their own profile unless admin)"""
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this profile"
        )

    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.get("/{user_id}/progress", response_model=LearningProgressResponse)
async def get_user_progress(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get user's learning progress"""
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this progress"
        )

    analytics_service = AnalyticsService(db)
    progress = analytics_service.get_user_progress(user_id)

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress data not found"
        )

    return progress


@router.get("/leaderboard/", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    limit: int = Query(50, ge=1, le=100),
    timeframe: str = Query("all", regex="^(daily|weekly|monthly|all)$"),
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get leaderboard"""
    analytics_service = AnalyticsService(db)
    leaderboard = analytics_service.get_leaderboard(
        limit=limit,
        timeframe=timeframe,
        category_id=category_id
    )
    return leaderboard