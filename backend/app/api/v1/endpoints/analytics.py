from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.analytics import UserAnalyticsResponse, SessionLogCreate, SessionLogResponse
from app.services.analytics_service import AnalyticsService
from app.utils.auth import get_current_user, get_current_admin_user

router = APIRouter()


@router.get("/user/{user_id}", response_model=UserAnalyticsResponse)
async def get_user_analytics(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get user analytics data"""
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this analytics data"
        )

    analytics_service = AnalyticsService(db)
    analytics = analytics_service.get_user_analytics(user_id)

    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analytics data not found"
        )

    return analytics


@router.post("/session", response_model=SessionLogResponse)
async def create_session_log(
    session_data: SessionLogCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Create a new session log"""
    analytics_service = AnalyticsService(db)
    session_log = analytics_service.create_session_log(
        user_id=current_user.id,
        session_data=session_data
    )
    return session_log


@router.put("/session/{session_id}")
async def update_session_log(
    session_id: str,
    session_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Update session log with activity data"""
    analytics_service = AnalyticsService(db)
    success = analytics_service.update_session_log(
        session_id=session_id,
        user_id=current_user.id,
        session_data=session_data
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    return {"message": "Session updated successfully"}


@router.get("/dashboard")
async def get_dashboard_data(
    timeframe: str = Query("7d", regex="^(1d|7d|30d|90d|1y)$"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get dashboard analytics data (admin only)"""
    analytics_service = AnalyticsService(db)
    dashboard_data = analytics_service.get_dashboard_data(timeframe)
    return dashboard_data


@router.get("/performance/challenges")
async def get_challenge_performance(
    challenge_id: Optional[int] = None,
    timeframe: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get challenge performance analytics (admin only)"""
    analytics_service = AnalyticsService(db)
    performance_data = analytics_service.get_challenge_performance(
        challenge_id=challenge_id,
        timeframe=timeframe
    )
    return performance_data


@router.get("/insights/skill-progression")
async def get_skill_progression_insights(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get skill progression insights"""
    target_user_id = user_id if current_user.role == "admin" else current_user.id

    analytics_service = AnalyticsService(db)
    insights = analytics_service.get_skill_progression_insights(target_user_id)
    return insights


@router.get("/recommendations/personalized")
async def get_personalized_recommendations(
    limit: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get personalized learning recommendations"""
    analytics_service = AnalyticsService(db)
    recommendations = analytics_service.get_personalized_recommendations(
        user_id=current_user.id,
        limit=limit
    )
    return recommendations