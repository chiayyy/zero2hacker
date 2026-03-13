from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy import and_, or_
from app.models.challenge import (
    Challenge as ChallengeModel,
    ChallengeAttempt as ChallengeAttemptModel,
    ChallengeRating as ChallengeRatingModel,
    AttemptStatus,
    ChallengeStatus
)
from app.models.user import User as UserModel
from app.schemas.challenge import ChallengeCreate, ChallengeUpdate, ChallengeRatingCreate
from typing import List, Optional, Dict, Any
import json
import re
import hashlib
from datetime import datetime


class ChallengeService:
    def __init__(self, db: Session):
        self.db = db

    def get_challenges(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        difficulty: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[ChallengeModel]:
        """Get challenges with filtering"""
        query = self.db.query(ChallengeModel)

        # Apply filters
        if category_id:
            query = query.filter(ChallengeModel.category_id == category_id)
        if difficulty:
            query = query.filter(ChallengeModel.difficulty == difficulty)
        if status:
            query = query.filter(ChallengeModel.status == status)
        else:
            # Default to only active challenges for non-admin users
            query = query.filter(ChallengeModel.status == ChallengeStatus.ACTIVE)

        results = query.offset(skip).limit(limit).all()
        print(f"[DEBUG] get_challenges: Found {len(results)} challenges")
        if results:
            print(f"[DEBUG] First challenge: id={results[0].id}, title={results[0].title}, status={results[0].status}")
        return results

    def get_challenge_by_id(self, challenge_id: int) -> Optional[ChallengeModel]:
        """Get challenge by ID"""
        return self.db.query(ChallengeModel).filter(ChallengeModel.id == challenge_id).first()

    def get_challenge_by_slug(self, slug: str) -> Optional[ChallengeModel]:
        """Get challenge by slug"""
        return self.db.query(ChallengeModel).filter(ChallengeModel.slug == slug).first()

    def create_challenge(self, challenge_data: ChallengeCreate) -> ChallengeModel:
        """Create a new challenge"""
        # Generate slug from title
        slug = self._generate_slug(challenge_data.title)

        # Convert lists to JSON strings
        hints_json = json.dumps(challenge_data.hints) if challenge_data.hints else None
        tags_json = json.dumps(challenge_data.tags) if challenge_data.tags else None
        learning_objectives_json = json.dumps(challenge_data.learning_objectives) if challenge_data.learning_objectives else None
        container_config_json = json.dumps(challenge_data.container_config) if challenge_data.container_config else None

        challenge = ChallengeModel(
            title=challenge_data.title,
            slug=slug,
            description=challenge_data.description,
            short_description=challenge_data.short_description,
            category_id=challenge_data.category_id,
            difficulty=challenge_data.difficulty,
            points=challenge_data.points,
            estimated_time=challenge_data.estimated_time,
            flag=challenge_data.flag,
            hints=hints_json,
            solution=challenge_data.solution,
            writeup=challenge_data.writeup,
            files_url=challenge_data.files_url,
            docker_image=challenge_data.docker_image,
            docker_port=challenge_data.docker_port,
            container_config=container_config_json,
            tags=tags_json,
            learning_objectives=learning_objectives_json,
            status=ChallengeStatus.ACTIVE.name
        )

        self.db.add(challenge)
        self.db.commit()
        self.db.refresh(challenge)
        return challenge

    def update_challenge(self, challenge_id: int, challenge_update: ChallengeUpdate) -> Optional[ChallengeModel]:
        """Update challenge"""
        challenge = self.get_challenge_by_id(challenge_id)
        if not challenge:
            return None

        update_data = challenge_update.dict(exclude_unset=True)

        # Convert lists to JSON strings
        if 'hints' in update_data and update_data['hints']:
            update_data['hints'] = json.dumps(update_data['hints'])
        if 'tags' in update_data and update_data['tags']:
            update_data['tags'] = json.dumps(update_data['tags'])

        # Update slug if title changed
        if 'title' in update_data:
            update_data['slug'] = self._generate_slug(update_data['title'])

        for field, value in update_data.items():
            setattr(challenge, field, value)

        challenge.updated_at = func.now()
        self.db.commit()
        self.db.refresh(challenge)
        return challenge

    def delete_challenge(self, challenge_id: int) -> bool:
        """Delete challenge"""
        challenge = self.get_challenge_by_id(challenge_id)
        if not challenge:
            return False

        self.db.delete(challenge)
        self.db.commit()
        return True

    def calculate_dynamic_score(self, challenge: ChallengeModel, time_spent_seconds: int,
                                attempt_number: int, hints_used: int) -> int:
        """
        Calculate dynamic score based on multiple factors:
        - Base points from challenge difficulty
        - Time bonus/penalty (faster = more points)
        - Attempt penalty (first try = bonus, multiple attempts = penalty)
        - Hint penalty (using hints reduces score)
        """
        base_points = challenge.points

        # Time multiplier (assuming estimated_time is in minutes)
        if challenge.estimated_time and time_spent_seconds > 0:
            estimated_seconds = challenge.estimated_time * 60
            time_ratio = time_spent_seconds / estimated_seconds

            if time_ratio <= 0.5:  # Solved in half the estimated time or less
                time_multiplier = 1.5
            elif time_ratio <= 1.0:  # Solved within estimated time
                time_multiplier = 1.2
            elif time_ratio <= 2.0:  # Took up to 2x estimated time
                time_multiplier = 1.0
            elif time_ratio <= 3.0:  # Took up to 3x estimated time
                time_multiplier = 0.8
            else:  # Took more than 3x estimated time
                time_multiplier = 0.6
        else:
            time_multiplier = 1.0  # No time data, use base points

        # Attempt multiplier
        if attempt_number == 1:
            attempt_multiplier = 1.2  # 20% bonus for first attempt
        elif attempt_number == 2:
            attempt_multiplier = 1.0  # No penalty
        elif attempt_number == 3:
            attempt_multiplier = 0.9  # 10% penalty
        else:
            attempt_multiplier = max(0.7, 1.0 - (attempt_number * 0.05))  # Max 30% penalty

        # Hint penalty
        hint_multiplier = max(0.5, 1.0 - (hints_used * 0.15))  # 15% per hint, min 50% of points

        # Calculate final score
        final_score = int(base_points * time_multiplier * attempt_multiplier * hint_multiplier)

        # Ensure minimum 10% of base points
        min_points = int(base_points * 0.1)
        return max(min_points, final_score)

    def create_attempt(self, user_id: int, challenge_id: int, flag_submitted: Optional[str] = None) -> ChallengeAttemptModel:
        """Create a challenge attempt"""
        challenge = self.get_challenge_by_id(challenge_id)
        if not challenge:
            return None

        # Check if flag is correct
        is_correct = False
        points_earned = 0

        if flag_submitted:
            is_correct = self._verify_flag(challenge.flag, flag_submitted)
            if is_correct:
                # Use dynamic scoring instead of fixed points
                status = AttemptStatus.SOLVED
            else:
                status = AttemptStatus.FAILED
        else:
            status = AttemptStatus.IN_PROGRESS

        # Count previous attempts for this user on this challenge
        attempt_count = self.db.query(ChallengeAttemptModel).filter(
            and_(
                ChallengeAttemptModel.user_id == user_id,
                ChallengeAttemptModel.challenge_id == challenge_id
            )
        ).count()

        # Check for existing attempt
        existing_attempt = self.db.query(ChallengeAttemptModel).filter(
            and_(
                ChallengeAttemptModel.user_id == user_id,
                ChallengeAttemptModel.challenge_id == challenge_id,
                ChallengeAttemptModel.status == AttemptStatus.IN_PROGRESS
            )
        ).first()

        if existing_attempt:
            # Update existing attempt
            existing_attempt.flag_submitted = flag_submitted
            existing_attempt.is_correct = is_correct
            existing_attempt.status = status
            if is_correct or status == AttemptStatus.FAILED:
                existing_attempt.completed_at = func.now()
                time_spent = int((datetime.now() - existing_attempt.started_at).total_seconds())
                existing_attempt.time_spent = time_spent

                # Calculate dynamic score if correct
                if is_correct:
                    points_earned = self.calculate_dynamic_score(
                        challenge=challenge,
                        time_spent_seconds=time_spent,
                        attempt_number=attempt_count + 1,  # +1 because this is the current attempt
                        hints_used=existing_attempt.hints_used
                    )
                existing_attempt.points_earned = points_earned

            self.db.commit()
            self.db.refresh(existing_attempt)
            attempt = existing_attempt
        else:
            # Create new attempt
            attempt = ChallengeAttemptModel(
                user_id=user_id,
                challenge_id=challenge_id,
                status=status,
                flag_submitted=flag_submitted,
                is_correct=is_correct,
                points_earned=0  # Will be calculated below if correct
            )

            if is_correct or status == AttemptStatus.FAILED:
                attempt.completed_at = func.now()
                attempt.time_spent = 0  # Immediate solve

                # Calculate dynamic score if correct
                if is_correct:
                    points_earned = self.calculate_dynamic_score(
                        challenge=challenge,
                        time_spent_seconds=0,  # Immediate solve
                        attempt_number=attempt_count + 1,  # +1 for this new attempt
                        hints_used=0  # New attempt, no hints yet
                    )
                    attempt.points_earned = points_earned

            self.db.add(attempt)
            self.db.commit()
            self.db.refresh(attempt)

        # Update challenge statistics
        if is_correct:
            challenge.solve_count += 1
            # Update user points
            from app.services.user_service import UserService
            user_service = UserService(self.db)
            user_service.increment_user_points(user_id, points_earned)

        challenge.attempt_count += 1
        self.db.commit()

        return attempt

    def get_user_attempts(self, user_id: int, challenge_id: Optional[int] = None) -> List[ChallengeAttemptModel]:
        """Get user's attempts"""
        query = self.db.query(ChallengeAttemptModel).filter(ChallengeAttemptModel.user_id == user_id)

        if challenge_id:
            query = query.filter(ChallengeAttemptModel.challenge_id == challenge_id)

        return query.order_by(ChallengeAttemptModel.started_at.desc()).all()

    def create_or_update_rating(self, user_id: int, challenge_id: int, rating_data: ChallengeRatingCreate) -> ChallengeRatingModel:
        """Create or update challenge rating"""
        existing_rating = self.db.query(ChallengeRatingModel).filter(
            and_(
                ChallengeRatingModel.user_id == user_id,
                ChallengeRatingModel.challenge_id == challenge_id
            )
        ).first()

        if existing_rating:
            # Update existing rating
            for field, value in rating_data.dict(exclude_unset=True).items():
                if field != 'challenge_id':
                    setattr(existing_rating, field, value)
            self.db.commit()
            self.db.refresh(existing_rating)
            rating = existing_rating
        else:
            # Create new rating
            rating = ChallengeRatingModel(
                user_id=user_id,
                challenge_id=challenge_id,
                **rating_data.dict(exclude={'challenge_id'})
            )
            self.db.add(rating)
            self.db.commit()
            self.db.refresh(rating)

        # Update challenge average rating
        self._update_challenge_rating(challenge_id)

        return rating

    def get_hint(self, user_id: int, challenge_id: int, hint_level: int = 1) -> Optional[str]:
        """Get hint for challenge"""
        challenge = self.get_challenge_by_id(challenge_id)
        if not challenge or not challenge.hints:
            return None

        try:
            hints = json.loads(challenge.hints)
            if hint_level <= len(hints):
                # Track hint usage
                self._track_hint_usage(user_id, challenge_id, hint_level)
                return hints[hint_level - 1]
        except (json.JSONDecodeError, IndexError):
            pass

        return None

    def start_challenge_container(self, user_id: int, challenge_id: int) -> Optional[Dict[str, Any]]:
        """Start challenge container (placeholder for Docker integration)"""
        challenge = self.get_challenge_by_id(challenge_id)
        if not challenge or not challenge.docker_image:
            return None

        # This would integrate with Docker to start a container
        # For now, return placeholder data
        return {
            "container_id": f"ctf_{challenge_id}_{user_id}",
            "port": challenge.docker_port or 8080,
            "url": f"http://localhost:{challenge.docker_port or 8080}"
        }

    def get_recommended_challenges(self, user_id: int, limit: int = 10) -> List[ChallengeModel]:
        """Get AI-recommended challenges (placeholder implementation)"""
        # This would use AI/ML to recommend challenges based on user's skill level and progress
        # For now, return recent unsolved challenges
        solved_challenge_ids = self.db.query(ChallengeAttemptModel.challenge_id).filter(
            and_(
                ChallengeAttemptModel.user_id == user_id,
                ChallengeAttemptModel.is_correct == True
            )
        ).subquery()

        return self.db.query(ChallengeModel).filter(
            and_(
                ChallengeModel.status == ChallengeStatus.ACTIVE,
                ~ChallengeModel.id.in_(solved_challenge_ids)
            )
        ).order_by(ChallengeModel.created_at.desc()).limit(limit).all()

    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title"""
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')

        # Ensure uniqueness
        base_slug = slug
        counter = 1
        while self.get_challenge_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def _verify_flag(self, correct_flag: str, submitted_flag: str) -> bool:
        """Verify if submitted flag is correct"""
        # Remove common flag formats and compare
        correct_clean = correct_flag.strip().lower()
        submitted_clean = submitted_flag.strip().lower()

        # Handle different flag formats
        if correct_clean.startswith('flag{') and correct_clean.endswith('}'):
            correct_clean = correct_clean[5:-1]
        if submitted_clean.startswith('flag{') and submitted_clean.endswith('}'):
            submitted_clean = submitted_clean[5:-1]

        return correct_clean == submitted_clean

    def _update_challenge_rating(self, challenge_id: int):
        """Update challenge average rating"""
        avg_rating = self.db.query(func.avg(ChallengeRatingModel.quality_rating)).filter(
            ChallengeRatingModel.challenge_id == challenge_id
        ).scalar()

        challenge = self.get_challenge_by_id(challenge_id)
        if challenge:
            challenge.average_rating = avg_rating
            self.db.commit()

    def _track_hint_usage(self, user_id: int, challenge_id: int, hint_level: int):
        """Track hint usage for analytics"""
        attempt = self.db.query(ChallengeAttemptModel).filter(
            and_(
                ChallengeAttemptModel.user_id == user_id,
                ChallengeAttemptModel.challenge_id == challenge_id,
                ChallengeAttemptModel.status == AttemptStatus.IN_PROGRESS
            )
        ).first()

        if attempt:
            attempt.hints_used = max(attempt.hints_used, hint_level)
            self.db.commit()