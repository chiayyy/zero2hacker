#!/usr/bin/env python3
"""
Script to create an admin user in the database
"""
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User, UserRole, SkillLevel
from app.core.config import settings

def create_admin_user():
    """Create an admin user in the database"""

    # Create database engine
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Admin user details
        admin_data = {
            "firebase_uid": "admin_firebase_uid_12345",  # Dummy Firebase UID
            "email": "admin@zero2hacker.com",
            "username": "admin",
            "display_name": "Administrator",
            "role": "admin",  # Use string value instead of enum
            "skill_level": "expert",  # Use string value instead of enum
            "is_active": True,
            "is_verified": True,
            "total_points": 0,
            "level": 1
        }

        # Check if admin user already exists
        existing_user = db.query(User).filter(
            (User.email == admin_data["email"]) |
            (User.username == admin_data["username"])
        ).first()

        if existing_user:
            print(f"User already exists!")
            print(f"  - Email: {existing_user.email}")
            print(f"  - Username: {existing_user.username}")
            print(f"  - Role: {existing_user.role}")

            # Update to admin if not already
            if existing_user.role != "admin":
                existing_user.role = "admin"
                existing_user.is_verified = True
                db.commit()
                print(f"\nSUCCESS: User upgraded to ADMIN role!")
            else:
                print(f"\nSUCCESS: User is already an ADMIN!")

            return existing_user

        # Create new admin user
        admin_user = User(**admin_data)
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("SUCCESS: Admin user created successfully!")
        print(f"\nAdmin credentials:")
        print(f"  - Email: {admin_user.email}")
        print(f"  - Username: {admin_user.username}")
        print(f"  - Role: {admin_user.role}")
        print(f"\nNote: You'll need to register this email in Firebase to login.")

        return admin_user

    except Exception as e:
        db.rollback()
        print(f"ERROR: Error creating admin user: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
