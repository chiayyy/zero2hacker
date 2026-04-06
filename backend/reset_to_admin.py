#!/usr/bin/env python3
"""
Reset database: delete all users and related data, then create a fresh admin account.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bcrypt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.user import User

DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Delete all related data first (foreign keys)
    db.execute(text("DELETE FROM challenge_attempts"))
    db.execute(text("DELETE FROM user_analytics"))
    db.execute(text("DELETE FROM session_logs"))
    db.execute(text("DELETE FROM challenge_ratings"))
    db.execute(text("DELETE FROM users"))
    db.commit()
    print("Cleared all users and related data.")

    # Hash the admin password
    password = "admin1234"
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    # Create admin user
    admin = User(
        firebase_uid="admin_local_uid",
        email="admin@gmail.com",
        username="admin",
        display_name="Administrator",
        password_hash=password_hash,
        role="admin",
        skill_level="expert",
        is_active=True,
        is_verified=True,
        total_points=0,
        level=1,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    print("\nAdmin account created:")
    print(f"  Email:    admin@gmail.com")
    print(f"  Password: admin1234")
    print(f"  Role:     {admin.role}")

except Exception as e:
    db.rollback()
    print(f"ERROR: {e}")
    raise
finally:
    db.close()
