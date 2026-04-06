#!/usr/bin/env python3
"""
Unlock all labs and challenges for admin, grant all points.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.user import User
from app.models.challenge import Challenge, ChallengeAttempt
from app.models.lab import LabProgress

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

LAB_IDS = ["lab-caesar", "lab-base64", "lab-hash", "lab-password", "lab-pw-hero", "lab-validation"]
MAX_LEVEL = 4

try:
    # Get admin user
    admin = db.query(User).filter(User.email == "admin@gmail.com").first()
    if not admin:
        print("ERROR: admin@gmail.com not found")
        sys.exit(1)

    print(f"Found admin: id={admin.id}, email={admin.email}")

    # --- Unlock all labs ---
    for lab_id in LAB_IDS:
        existing = db.query(LabProgress).filter(
            LabProgress.user_id == admin.id,
            LabProgress.lab_id == lab_id
        ).first()
        if existing:
            existing.unlocked_level = MAX_LEVEL
            existing.total_completed = MAX_LEVEL
            existing.level_scores = {str(i): [100] for i in range(1, MAX_LEVEL + 1)}
        else:
            db.add(LabProgress(
                user_id=admin.id,
                lab_id=lab_id,
                unlocked_level=MAX_LEVEL,
                total_completed=MAX_LEVEL,
                level_scores={str(i): [100] for i in range(1, MAX_LEVEL + 1)},
            ))
        print(f"  Lab unlocked: {lab_id} (level {MAX_LEVEL})")

    db.commit()

    # --- Solve all challenges ---
    challenges = db.query(Challenge).all()
    total_points = 0
    solved = 0

    for ch in challenges:
        existing = db.query(ChallengeAttempt).filter(
            ChallengeAttempt.user_id == admin.id,
            ChallengeAttempt.challenge_id == ch.id
        ).first()
        if existing:
            existing.status = "solved"
            existing.is_correct = True
            existing.points_earned = ch.points
            existing.completed_at = datetime.now(timezone.utc)
        else:
            db.add(ChallengeAttempt(
                user_id=admin.id,
                challenge_id=ch.id,
                status="solved",
                flag_submitted=ch.flag,
                is_correct=True,
                points_earned=ch.points,
                completed_at=datetime.now(timezone.utc),
                time_spent=60,
                hints_used=0,
            ))
        total_points += ch.points
        solved += 1

    db.commit()

    # --- Update admin total_points and level ---
    admin.total_points = total_points
    admin.level = 99
    db.commit()

    print(f"\nDone!")
    print(f"  Challenges solved: {solved}")
    print(f"  Total points:      {total_points}")
    print(f"  Labs unlocked:     {len(LAB_IDS)} (all levels {MAX_LEVEL})")
    print(f"  User level:        99")

except Exception as e:
    db.rollback()
    print(f"ERROR: {e}")
    raise
finally:
    db.close()
