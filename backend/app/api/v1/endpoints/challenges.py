from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.challenge import (
    ChallengeResponse, ChallengeCreate, ChallengeUpdate,
    ChallengeAttemptCreate, ChallengeAttemptResponse,
    ChallengeRatingCreate
)
from app.services.challenge_service import ChallengeService
from app.utils.auth import get_current_user, get_current_admin_user

router = APIRouter()


@router.get("/", response_model=List[ChallengeResponse])
async def get_challenges(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category_id: Optional[int] = None,
    difficulty: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get list of challenges with filtering and pagination"""
    challenge_service = ChallengeService(db)
    challenges = challenge_service.get_challenges(
        skip=skip,
        limit=limit,
        category_id=category_id,
        difficulty=difficulty,
        status=status
    )
    return challenges


@router.get("/{challenge_id}", response_model=ChallengeResponse)
async def get_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get challenge by ID"""
    challenge_service = ChallengeService(db)
    challenge = challenge_service.get_challenge_by_id(challenge_id)

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    return challenge


@router.get("/{challenge_id}/download-file")
async def download_challenge_file(
    challenge_id: int,
    db: Session = Depends(get_db)
):
    """Download the challenge resource file with proper attachment header"""
    challenge_service = ChallengeService(db)
    challenge = challenge_service.get_challenge_by_id(challenge_id)

    if not challenge or not challenge.files_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No file for this challenge")

    # files_url is like /files/challenges/foo.txt — strip /files/ to get relative path
    relative = challenge.files_url.lstrip("/")
    if relative.startswith("files/"):
        relative = relative[len("files/"):]

    base = Path(__file__).resolve().parents[4] / "static"
    file_path = base / relative

    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File not found on server")

    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        headers={"Content-Disposition": f'attachment; filename="{file_path.name}"'}
    )


@router.post("/", response_model=ChallengeResponse)
async def create_challenge(
    challenge_data: ChallengeCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Create a new challenge (admin only)"""
    challenge_service = ChallengeService(db)
    challenge = challenge_service.create_challenge(challenge_data)
    return challenge


@router.put("/{challenge_id}", response_model=ChallengeResponse)
async def update_challenge(
    challenge_id: int,
    challenge_update: ChallengeUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Update challenge (admin only)"""
    challenge_service = ChallengeService(db)
    challenge = challenge_service.update_challenge(challenge_id, challenge_update)

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    return challenge


@router.delete("/{challenge_id}")
async def delete_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Delete challenge (admin only)"""
    challenge_service = ChallengeService(db)
    success = challenge_service.delete_challenge(challenge_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    return {"message": "Challenge deleted successfully"}


@router.post("/{challenge_id}/attempts", response_model=ChallengeAttemptResponse)
async def submit_challenge_attempt(
    challenge_id: int,
    attempt_data: ChallengeAttemptCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Submit a challenge attempt"""
    challenge_service = ChallengeService(db)

    # Verify challenge exists
    challenge = challenge_service.get_challenge_by_id(challenge_id)
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    # Create attempt
    attempt = challenge_service.create_attempt(
        user_id=current_user.id,
        challenge_id=challenge_id,
        flag_submitted=attempt_data.flag_submitted
    )

    return attempt


@router.get("/{challenge_id}/attempts", response_model=List[ChallengeAttemptResponse])
async def get_challenge_attempts(
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get user's attempts for a specific challenge"""
    challenge_service = ChallengeService(db)
    attempts = challenge_service.get_user_attempts(current_user.id, challenge_id)
    return attempts


@router.post("/{challenge_id}/rating")
async def rate_challenge(
    challenge_id: int,
    rating_data: ChallengeRatingCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Rate a challenge"""
    challenge_service = ChallengeService(db)

    # Verify challenge exists
    challenge = challenge_service.get_challenge_by_id(challenge_id)
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    # Create or update rating
    rating = challenge_service.create_or_update_rating(
        user_id=current_user.id,
        challenge_id=challenge_id,
        rating_data=rating_data
    )

    return {"message": "Rating submitted successfully"}


@router.get("/{challenge_id}/start")
async def start_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Start a challenge (create container if needed)"""
    challenge_service = ChallengeService(db)

    challenge = challenge_service.get_challenge_by_id(challenge_id)
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    # Start challenge container if needed
    container_info = challenge_service.start_challenge_container(
        user_id=current_user.id,
        challenge_id=challenge_id
    )

    return {
        "message": "Challenge started successfully",
        "container_info": container_info
    }


@router.post("/{challenge_id}/hint")
async def get_hint(
    challenge_id: int,
    hint_level: int = 1,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get a hint for the challenge"""
    challenge_service = ChallengeService(db)

    hint = challenge_service.get_hint(
        user_id=current_user.id,
        challenge_id=challenge_id,
        hint_level=hint_level
    )

    if not hint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hint not available"
        )

    return {"hint": hint}


@router.get("/recommended/", response_model=List[ChallengeResponse])
async def get_recommended_challenges(
    limit: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get AI-recommended challenges for the user"""
    challenge_service = ChallengeService(db)
    challenges = challenge_service.get_recommended_challenges(
        user_id=current_user.id,
        limit=limit
    )
    return challenges