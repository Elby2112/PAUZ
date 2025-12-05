"""
Voice Assistant Routes
Handles welcome greetings, guidance, and interactive voice features using PAUZ Voice Service with ongoing conversation
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlmodel import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import json
import base64

from app.services.voice_service import voice_service
from app.services.pauz_voice_service import pauz_voice_service
from app.models import User
from app.database import get_session
from app.dependencies import get_current_user

router = APIRouter()

class WelcomeRequest(BaseModel):
    user_context: Optional[Dict[str, Any]] = None
    time_of_day: Optional[str] = None

class GuidanceRequest(BaseModel):
    question: str
    context: Optional[str] = None

class VoiceResponse(BaseModel):
    success: bool
    audio_data: Optional[str] = None
    content_type: Optional[str] = None
    text: str
    voice_profile: str
    metadata: Optional[Dict[str, Any]] = None

class VoiceQueryResponse(BaseModel):
    success: bool
    audio_data: Optional[str] = None
    content_type: Optional[str] = None
    user_transcription: Optional[str] = None
    assistant_response: Optional[str] = None
    voice_profile: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

def get_time_based_greeting() -> str:
    """Get appropriate greeting based on current time"""
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 22:
        return "Good evening"
    else:
        return "Hello"

def get_personalized_welcome(user: User, user_context: Optional[Dict] = None) -> str:
    """Generate personalized welcome message using PAUZ Voice Service"""
    try:
        return pauz_voice_service.generate_welcome(str(user.id), user_context)
    except Exception as e:
        print(f"❌ PAUZ Voice welcome failed, using fallback: {e}")
        # Simple fallback
        greeting = get_time_based_greeting()
        if user_context and user_context.get("is_returning_user"):
            return f"{greeting}! Welcome back to PAUZ. Ready to continue your journaling journey?"
        else:
            return f"{greeting}! Welcome to PAUZ. I'm here to help you start journaling with free writing or guided prompts."

def get_guidance_response(question: str, context: Optional[str] = None, user_context: Optional[Dict] = None, conversation_history: Optional[list] = None, user_id: Optional[str] = None) -> str:
    """Generate intelligent response using PAUZ Voice Service with conversation memory"""
    try:
        return pauz_voice_service.generate_response(
            user_input=question,
            user_id=user_id or "anonymous",
            user_context=user_context
        )
    except Exception as e:
        print(f"❌ PAUZ Voice response failed, using fallback: {e}")
        # Emergency fallback with basic app knowledge
        question_lower = question.lower().strip()
        if any(word in question_lower for word in ["what can i do", "help", "options", "features"]):
            return "You can choose FreeJournal to write freely with hints and voice recording, or GuidedJournal for category-based prompts in Mind, Body, Heart, Friends, Family, Romance, Growth, Mission, Money, or Joy. What interests you?"
        elif any(word in question_lower for word in ["stuck", "blocked", "don't know"]):
            return "Try FreeJournal with the Hint button for ideas, or pick a GuidedJournal category. You can also record yourself talking instead of writing!"
        else:
            return "I'm here to help with your PAUZ journaling journey. You can ask me about FreeJournal, GuidedJournal categories, the Garden feature, or get writing hints!"

@router.post("/welcome", response_model=VoiceResponse)
async def welcome_voice_route(
    request: WelcomeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate personalized welcome voice greeting for the user
    """
    try:
        # Check if voice service is available
        if not voice_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Voice service not available. Please check your configuration."
            )
        
        # Generate personalized welcome text
        welcome_text = get_personalized_welcome(current_user, request.user_context)
        
        # Convert to speech using welcome voice profile
        voice_result = voice_service.text_to_speech(
            text=welcome_text,
            voice_profile="welcome"
        )
        
        if not voice_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Voice generation failed: {voice_result.get('error', 'Unknown error')}"
            )
        
        return VoiceResponse(
            success=True,
            audio_data=voice_result["audio_data"],
            content_type=voice_result["content_type"],
            text=welcome_text,
            voice_profile="welcome",
            metadata={
                "greeting_type": "personalized_welcome",
                "time_of_day": get_time_based_greeting(),
                "user_id": current_user.id
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Welcome voice generation failed: {str(e)}"
        )

@router.get("/welcome-simple", response_model=VoiceResponse)
async def welcome_simple_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Simple welcome endpoint that generates greeting without requiring request body
    Perfect for frontend auto-play on assistant open
    """
    try:
        if not voice_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Voice service not available. Please check your configuration."
            )
        
        # Get user context for personalization
        try:
            from app.models import FreeJournal, GuidedJournal
            total_free_journals = db.query(FreeJournal).filter(FreeJournal.user_id == current_user.id).count()
            total_guided_journals = db.query(GuidedJournal).filter(GuidedJournal.user_id == current_user.id).count()
            total_journals = total_free_journals + total_guided_journals
            
            user_context = {
                "total_journals": total_journals,
                "is_returning_user": total_journals > 0
            }
        except:
            user_context = None
        
        # Generate welcome text
        welcome_text = get_personalized_welcome(current_user, user_context)
        
        # Convert to speech
        voice_result = voice_service.text_to_speech(
            text=welcome_text,
            voice_profile="welcome"
        )
        
        if not voice_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Voice generation failed: {voice_result.get('error', 'Unknown error')}"
            )
        
        return VoiceResponse(
            success=True,
            audio_data=voice_result["audio_data"],
            content_type=voice_result["content_type"],
            text=welcome_text,
            voice_profile="welcome",
            metadata={
                "response_type": "smart_memory_welcome",
                "time_of_day": get_time_based_greeting(),
                "user_id": current_user.id
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simple welcome failed: {str(e)}"
        )
    """
    Generate personalized welcome voice greeting for the user
    """
    try:
        # Check if voice service is available
        if not voice_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Voice service not available. Please check your configuration."
            )
        
        # Generate personalized welcome text
        welcome_text = get_personalized_welcome(current_user, request.user_context)
        
        # Convert to speech using welcome voice profile
        voice_result = voice_service.text_to_speech(
            text=welcome_text,
            voice_profile="welcome"
        )
        
        if not voice_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Voice generation failed: {voice_result.get('error', 'Unknown error')}"
            )
        
        return VoiceResponse(
            success=True,
            audio_data=voice_result["audio_data"],
            content_type=voice_result["content_type"],
            text=welcome_text,
            voice_profile="welcome",
            metadata={
                "greeting_type": "personalized_welcome",
                "time_of_day": get_time_based_greeting(),
                "user_id": current_user.id
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Welcome voice generation failed: {str(e)}"
        )

@router.post("/guidance", response_model=VoiceResponse)
async def guidance_voice_route(
    request: GuidanceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Generate intelligent guidance response to user questions using Gemini AI
    """
    try:
        if not voice_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Voice service not available. Please check your configuration."
            )
        
        # Get user context for better responses
        try:
            user_context_data = await get_user_context_route(current_user, db)
            user_context = {
                "total_journals": user_context_data["total_journals"],
                "is_returning_user": user_context_data["is_returning_user"],
                "last_journal_days_ago": user_context_data["last_journal_days_ago"]
            }
        except:
            user_context = None
        
        # Generate intelligent response using SmartMemory + Gemini
        guidance_text = get_guidance_response(
            question=request.question, 
            context=request.context,
            user_context=user_context,
            user_id=str(current_user.id)
        )
        
        # Convert to speech using guide voice profile
        voice_result = voice_service.text_to_speech(
            text=guidance_text,
            voice_profile="guide"
        )
        
        if not voice_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Voice generation failed: {voice_result.get('error', 'Unknown error')}"
            )
        
        return VoiceResponse(
            success=True,
            audio_data=voice_result["audio_data"],
            content_type=voice_result["content_type"],
            text=guidance_text,
            voice_profile="guide",
            metadata={
                "question": request.question,
                "response_type": "smart_memory_guidance",
                "user_id": current_user.id,
                "has_user_context": user_context is not None
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Guidance voice generation failed: {str(e)}"
        )

@router.get("/user-context")
async def get_user_context_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Get user context for personalized greetings
    """
    try:
        # Import here to avoid circular imports
        from app.models import FreeJournal, GuidedJournal
        
        # Get user statistics
        total_free_journals = db.query(FreeJournal).filter(FreeJournal.user_id == current_user.id).count()
        total_guided_journals = db.query(GuidedJournal).filter(GuidedJournal.user_id == current_user.id).count()
        total_journals = total_free_journals + total_guided_journals
        
        # Get last journal date
        last_journal = None
        last_free = db.query(FreeJournal).filter(FreeJournal.user_id == current_user.id).order_by(FreeJournal.created_at.desc()).first()
        last_guided = db.query(GuidedJournal).filter(GuidedJournal.user_id == current_user.id).order_by(GuidedJournal.created_at.desc()).first()
        
        if last_free or last_guided:
            last_date = max(last_free.created_at if last_free else datetime.min, 
                           last_guided.created_at if last_guided else datetime.min)
            days_since_last = (datetime.now() - last_date).days
        else:
            days_since_last = None
        
        return {
            "total_journals": total_journals,
            "total_free_journals": total_free_journals,
            "total_guided_journals": total_guided_journals,
            "last_journal_days_ago": days_since_last,
            "is_returning_user": total_journals > 0,
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user context: {str(e)}"
        )

@router.get("/memory-stats")
async def get_memory_stats_route(
    current_user: User = Depends(get_current_user)
):
    """
    Get user's conversation statistics and personalization data
    """
    try:
        from app.services.pauz_voice_service import pauz_voice_service
        
        # Get user-specific conversation stats
        conversation = pauz_voice_service.get_or_create_conversation(str(current_user.id))
        
        return {
            "user_memory": {
                "conversation_count": len([msg for msg in conversation if msg["role"] == "user"]),
                "messages_in_conversation": len(conversation),
                "has_conversation_history": len(conversation) > 0
            },
            "memory_available": True,
            "service_type": "pauz_voice_service"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation stats: {str(e)}"
        )

@router.post("/voice-query", response_model=VoiceQueryResponse)
async def voice_query_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
    audio: UploadFile = File(...)
):
    """
    Complete voice-to-voice conversation endpoint
    Takes user audio input, transcribes it, generates response, and returns audio
    """
    try:
        if not voice_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Voice service not available. Please check your configuration."
            )
        
        # Read the uploaded audio file
        audio_content = await audio.read()
        
        if not audio_content:
            raise HTTPException(
                status_code=400,
                detail="No audio data provided"
            )
        
        # Get user context for personalized responses
        try:
            user_context_endpoint = "/voice-assistant/user-context"
            from fastapi import Request
            # We'll create a minimal context here since we can't easily call our own endpoint
            from app.models import FreeJournal, GuidedJournal
            total_free_journals = db.query(FreeJournal).filter(FreeJournal.user_id == current_user.id).count()
            total_guided_journals = db.query(GuidedJournal).filter(GuidedJournal.user_id == current_user.id).count()
            total_journals = total_free_journals + total_guided_journals
            
            user_context = {
                "total_journals": total_journals,
                "is_returning_user": total_journals > 0,
                "user_id": current_user.id
            }
        except:
            user_context = None
        
        # Process voice-to-voice conversation
        result = voice_service.voice_to_voice_conversation(
            audio_data=audio_content,
            user_context=user_context
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Voice query failed: {result.get('error', 'Unknown error')}"
            )
        
        return VoiceQueryResponse(
            success=True,
            audio_data=result["audio_data"],
            content_type=result["content_type"],
            user_transcription=result["user_transcription"],
            assistant_response=result["assistant_response"],
            voice_profile=result["voice_profile"],
            metadata=result["metadata"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice query processing failed: {str(e)}"
        )