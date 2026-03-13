from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.models.user import User as UserModel
from app.models.analytics import UserAnalytics as UserAnalyticsModel
from app.schemas.user import UserCreate, UserUpdate
from typing import Optional
import json


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> Optional[UserModel]:
        """Get user by ID"""
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()

    def get_user_by_firebase_uid(self, firebase_uid: str) -> Optional[UserModel]:
        """Get user by Firebase UID"""
        return self.db.query(UserModel).filter(UserModel.firebase_uid == firebase_uid).first()

    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Get user by email"""
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def get_user_by_username(self, username: str) -> Optional[UserModel]:
        """Get user by username"""
        return self.db.query(UserModel).filter(UserModel.username == username).first()

    def create_user(self, user_data: UserCreate) -> UserModel:
        """Create a new user"""
        # Convert preferred_categories list to JSON string
        preferred_categories_json = None
        if user_data.preferred_categories:
            preferred_categories_json = json.dumps(user_data.preferred_categories)

        user = UserModel(
            firebase_uid=user_data.firebase_uid,
            email=user_data.email,
            username=user_data.username,
            display_name=user_data.display_name,
            role=user_data.role.value if hasattr(user_data.role, 'value') else user_data.role,
            skill_level=user_data.skill_level.value if hasattr(user_data.skill_level, 'value') else user_data.skill_level,
            experience_months=user_data.experience_months,
            bio=user_data.bio,
            preferred_categories=preferred_categories_json,
            learning_style=user_data.learning_style,
            is_active=True,
            is_verified=False
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # Create user analytics record
        skill_level_val = user_data.skill_level.value if hasattr(user_data.skill_level, 'value') else user_data.skill_level
        analytics = UserAnalyticsModel(
            user_id=user.id,
            current_skill_level=skill_level_val
        )
        self.db.add(analytics)
        self.db.commit()

        return user

    def update_user(self, user_id: int, user_update: UserUpdate) -> UserModel:
        """Update user information"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        update_data = user_update.dict(exclude_unset=True)

        # Convert preferred_categories list to JSON string
        if 'preferred_categories' in update_data:
            if update_data['preferred_categories']:
                update_data['preferred_categories'] = json.dumps(update_data['preferred_categories'])
            else:
                update_data['preferred_categories'] = None

        for field, value in update_data.items():
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def update_last_activity(self, user_id: int) -> None:
        """Update user's last activity timestamp"""
        user = self.get_user_by_id(user_id)
        if user:
            user.last_activity = func.now()
            self.db.commit()

    def increment_user_points(self, user_id: int, points: int) -> UserModel:
        """Add points to user and potentially level up"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        user.total_points += points

        # Simple leveling system: every 1000 points = 1 level
        new_level = (user.total_points // 1000) + 1
        if new_level > user.level:
            user.level = new_level

        self.db.commit()
        self.db.refresh(user)
        return user

    def update_streak(self, user_id: int) -> UserModel:
        """Update user's daily streak"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        # Logic for updating streak would go here
        # For now, just increment by 1
        user.streak_days += 1

        self.db.commit()
        self.db.refresh(user)
        return user

    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user account"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        user.is_active = False
        self.db.commit()
        return True

    def verify_user(self, user_id: int) -> bool:
        """Verify user account"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        user.is_verified = True
        self.db.commit()
        return True