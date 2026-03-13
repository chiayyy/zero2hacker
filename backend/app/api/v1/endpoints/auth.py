from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService
from app.utils.auth import get_current_user, hash_password, verify_password, create_access_token
import uuid

router = APIRouter()
security = HTTPBearer()


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    display_name: Optional[str] = None
    skill_level: str = "beginner"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


@router.post("/register", response_model=TokenResponse)
async def register_user(
    register_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new user with email and password"""
    # Check if user already exists
    existing_user = db.query(UserModel).filter(
        (UserModel.email == register_data.email) |
        (UserModel.username == register_data.username)
    ).first()

    if existing_user:
        if existing_user.email == register_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

    # Create new user
    new_user = UserModel(
        firebase_uid=f"local_{uuid.uuid4().hex[:12]}",
        email=register_data.email,
        username=register_data.username,
        password_hash=hash_password(register_data.password),
        display_name=register_data.display_name or register_data.username,
        skill_level=register_data.skill_level,
        role="student",
        is_active=True,
        is_verified=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create access token
    access_token = create_access_token(user_id=new_user.id, email=new_user.email)

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login user with email and password"""
    # Find user by email
    user = db.query(UserModel).filter(UserModel.email == login_data.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not user.password_hash or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    # Update last activity
    user_service = UserService(db)
    user_service.update_last_activity(user.id)

    # Create access token
    access_token = create_access_token(user_id=user.id, email=user.email)

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserModel = Depends(get_current_user)
):
    """Get current user information"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    user_service = UserService(db)
    updated_user = user_service.update_user(current_user.id, user_update)
    return updated_user


@router.post("/logout")
async def logout_user(
    current_user: UserModel = Depends(get_current_user)
):
    """Logout user (client should clear token)"""
    return {"message": "Successfully logged out"}


@router.post("/verify-token")
async def verify_token(
    current_user: UserModel = Depends(get_current_user)
):
    """Verify if token is valid"""
    return {"valid": True, "user_id": current_user.id}
