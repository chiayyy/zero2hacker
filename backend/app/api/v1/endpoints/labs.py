import json
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.models.user import User as UserModel
from app.models.lab import LabProgress
from app.utils.auth import get_current_user

router = APIRouter()

# Path to lab-exercises.json (relative to this file's location)
_LAB_DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "../../../../..",  # up to project root
    "frontend/src/data/lab-exercises.json"
)


def _load_lab_exercises() -> List[Dict[str, Any]]:
    try:
        with open(_LAB_DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


class LabProgressUpdate(BaseModel):
    unlocked_level: int = 1
    level_scores: Dict[str, List[float]] = {}
    total_completed: int = 0


@router.get("/")
async def list_labs(
    current_user: UserModel = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """List all available labs (derived from lab-exercises.json metadata)"""
    exercises = _load_lab_exercises()
    seen = set()
    labs = []
    for ex in exercises:
        lab_id = ex.get("labId")
        if ex.get("level") == 1 and lab_id and lab_id not in seen:
            seen.add(lab_id)
            base_title = ex.get("title", "").split("—")[0].strip()
            labs.append({
                "lab_id": lab_id,
                "title": base_title,
                "description": ex.get("description", ""),
                "category": ex.get("category", ""),
            })
    return labs


@router.get("/summary")
async def get_lab_summary(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get user's overall lab completion summary"""
    records = db.query(LabProgress).filter(
        LabProgress.user_id == current_user.id
    ).all()

    total_labs = len(records)
    total_completed = sum(r.total_completed for r in records)
    labs_at_max_level = sum(1 for r in records if r.unlocked_level >= 4)

    return {
        "total_labs_started": total_labs,
        "total_exercises_completed": total_completed,
        "labs_at_max_level": labs_at_max_level,
    }


@router.get("/{lab_id}/progress")
async def get_lab_progress(
    lab_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get user's progress for a specific lab"""
    record = db.query(LabProgress).filter(
        LabProgress.user_id == current_user.id,
        LabProgress.lab_id == lab_id
    ).first()

    if not record:
        return {
            "lab_id": lab_id,
            "unlocked_level": 1,
            "level_scores": {},
            "total_completed": 0,
        }

    return {
        "lab_id": record.lab_id,
        "unlocked_level": record.unlocked_level,
        "level_scores": record.level_scores or {},
        "total_completed": record.total_completed,
        "last_activity": record.last_activity.isoformat() if record.last_activity else None,
    }


@router.post("/{lab_id}/progress")
async def save_lab_progress(
    lab_id: str,
    progress: LabProgressUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Save/update user's progress for a specific lab"""
    record = db.query(LabProgress).filter(
        LabProgress.user_id == current_user.id,
        LabProgress.lab_id == lab_id
    ).first()

    if record:
        record.unlocked_level = progress.unlocked_level
        record.level_scores = progress.level_scores
        record.total_completed = progress.total_completed
    else:
        record = LabProgress(
            user_id=current_user.id,
            lab_id=lab_id,
            unlocked_level=progress.unlocked_level,
            level_scores=progress.level_scores,
            total_completed=progress.total_completed,
        )
        db.add(record)

    db.commit()
    db.refresh(record)

    return {
        "lab_id": record.lab_id,
        "unlocked_level": record.unlocked_level,
        "level_scores": record.level_scores,
        "total_completed": record.total_completed,
    }
