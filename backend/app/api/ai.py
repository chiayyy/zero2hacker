"""
AI endpoints for Zero2Hacker CTF Platform
Provides AI-powered hints, feedback, and chatbot assistance
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.services.ai_service import AIService
from app.services.challenge_service import ChallengeService
from app.utils.auth import get_current_user
from app.models.user import User as UserModel


router = APIRouter()


# Request/Response Models
class HintRequest(BaseModel):
    challenge_id: int = Field(..., description="ID of the challenge")
    hint_level: int = Field(default=1, ge=1, le=5, description="Hint level (1-5, progressive)")
    include_context: bool = Field(default=True, description="Include user's previous attempts in context")


class HintResponse(BaseModel):
    hint: str
    hint_level: int
    is_ai_generated: bool
    challenge_id: int


class FeedbackRequest(BaseModel):
    challenge_id: int
    attempt: str
    is_correct: bool


class FeedbackResponse(BaseModel):
    feedback: str
    is_ai_generated: bool
    encouragement: str


class ChatbotRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    challenge_id: Optional[int] = Field(default=None, description="Current challenge context")
    conversation_history: list[Dict[str, str]] = Field(default_factory=list, max_items=10)


class ChatbotResponse(BaseModel):
    response: str
    is_ai_generated: bool
    suggestions: list[str] = Field(default_factory=list)


# Endpoints
@router.post("/hint", response_model=HintResponse)
async def get_ai_hint(
    request: HintRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate personalized AI hint for a challenge

    The hint is adaptive based on:
    - User's skill level
    - Previous attempts
    - Hint level requested
    - Challenge difficulty
    """
    try:
        ai_service = AIService(db)
        challenge_service = ChallengeService(db)

        # Get challenge details
        challenge = challenge_service.get_challenge_by_id(request.challenge_id)
        if not challenge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Challenge not found"
            )

        # Get user's progress
        attempts = challenge_service.get_user_attempts(current_user.id, request.challenge_id)

        user_progress = {
            "total_attempts": len(attempts),
            "last_attempt_time": attempts[0].started_at.isoformat() if attempts else None,
            "hints_used": attempts[0].hints_used if attempts else 0
        }

        # Generate personalized hint
        hint = await ai_service.generate_personalized_hint(
            user_id=current_user.id,
            challenge_id=request.challenge_id,
            user_progress=user_progress,
            hint_level=request.hint_level
        )

        if not hint:
            # Fallback to static hints if AI fails
            static_hint = challenge_service.get_hint(
                current_user.id,
                request.challenge_id,
                request.hint_level
            )
            if static_hint:
                return HintResponse(
                    hint=static_hint,
                    hint_level=request.hint_level,
                    is_ai_generated=False,
                    challenge_id=request.challenge_id
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate hint"
            )

        return HintResponse(
            hint=hint,
            hint_level=request.hint_level,
            is_ai_generated=True,
            challenge_id=request.challenge_id
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] AI hint generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}"
        )


@router.post("/feedback", response_model=FeedbackResponse)
async def get_ai_feedback(
    request: FeedbackRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate personalized feedback on a challenge attempt

    Provides:
    - Analysis of what went right/wrong
    - Suggestions for improvement
    - Encouragement and next steps
    """
    try:
        ai_service = AIService(db)

        # Generate feedback
        feedback = await ai_service.generate_feedback(
            user_id=current_user.id,
            challenge_id=request.challenge_id,
            user_attempt=request.attempt,
            is_correct=request.is_correct
        )

        if not feedback:
            feedback = "Great effort! Keep practicing and learning."

        # Generate encouragement based on result
        if request.is_correct:
            encouragement = "Excellent work! You've mastered this challenge."
        else:
            encouragement = "Don't give up! Every attempt is a learning opportunity."

        return FeedbackResponse(
            feedback=feedback,
            is_ai_generated=True,
            encouragement=encouragement
        )

    except Exception as e:
        print(f"[ERROR] AI feedback generation failed: {str(e)}")
        # Fallback to generic feedback
        return FeedbackResponse(
            feedback="Keep practicing! Learning cybersecurity takes time and persistence.",
            is_ai_generated=False,
            encouragement="You're making progress!"
        )


@router.post("/chatbot", response_model=ChatbotResponse)
async def chatbot_conversation(
    request: ChatbotRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI chatbot for general CTF assistance

    Features:
    - Answers questions about challenges
    - Explains cybersecurity concepts
    - Provides guidance without spoiling solutions
    - Context-aware based on current challenge
    """
    try:
        ai_service = AIService(db)
        challenge_service = ChallengeService(db)

        # Build context
        context = f"User skill level: {current_user.skill_level}\n"
        context += f"User message: {request.message}\n"

        if request.challenge_id:
            challenge = challenge_service.get_challenge_by_id(request.challenge_id)
            if challenge:
                context += f"\nCurrent challenge: {challenge.title}\n"
                context += f"Category: {challenge.category.name if challenge.category else 'Unknown'}\n"
                context += f"Difficulty: {challenge.difficulty}\n"

        # Add conversation history
        if request.conversation_history:
            context += "\nConversation history:\n"
            for msg in request.conversation_history[-5:]:  # Last 5 messages
                context += f"{msg.get('role', 'user')}: {msg.get('content', '')}\n"

        # System prompt for chatbot
        system_prompt = """You are an expert cybersecurity instructor and CTF mentor.

        Your role:
        - Help students learn cybersecurity concepts
        - Provide guidance without giving away solutions directly
        - Explain concepts clearly and encourage critical thinking
        - Be supportive and educational
        - Keep responses concise (2-3 paragraphs max)

        Rules:
        - NEVER provide the full solution or flag
        - Guide with questions and hints
        - Explain concepts when asked
        - Encourage independent problem-solving
        - Be encouraging and supportive
        """

        # Generate response
        response_text = await ai_service._call_ollama(
            "llama3",
            context,
            system_prompt
        )

        if not response_text or response_text.startswith("Error"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate chatbot response"
            )

        # Generate suggestions
        suggestions = [
            "Tell me more about this topic",
            "Can you explain that differently?",
            "What should I try next?"
        ]

        return ChatbotResponse(
            response=response_text,
            is_ai_generated=True,
            suggestions=suggestions
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Chatbot failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chatbot error: {str(e)}"
        )


@router.get("/status")
async def get_ai_status(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI service status and available models"""
    try:
        ai_service = AIService(db)
        status_info = ai_service.get_models_status()
        return {
            "status": "healthy",
            "ai_enabled": True,
            **status_info
        }
    except Exception as e:
        return {
            "status": "error",
            "ai_enabled": False,
            "error": str(e)
        }
