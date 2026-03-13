from fastapi import APIRouter
from app.api.v1.endpoints import auth, challenges, users, analytics, ai_engine, labs

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(challenges.router, prefix="/challenges", tags=["Challenges"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(ai_engine.router, prefix="/ai", tags=["AI Engine"])
api_router.include_router(labs.router, prefix="/labs", tags=["Labs"])