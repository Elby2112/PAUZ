from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from sqlmodel import Session
from app.services.free_journal_service import free_journal_service
from app.services.voice_service import voice_service
from app.services.stats_service import stats_service
from app.services.journal_loading_service import journal_loading_service
from app.models import FreeJournal, Hint, User
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from app.dependencies import get_current_user
from app.database import get_session

router = APIRouter()

class SaveContentRequest(BaseModel):
    content: str

class HintsRequest(BaseModel):
    current_content: str

class FreeJournalResponse(BaseModel):
    id: Optional[int]
    user_id: str
    session_id: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True # To allow mapping from SQLModel to Pydantic

class HintResponse(BaseModel):
    id: Optional[int]
    user_id: str
    session_id: str
    hint_text: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[dict])
def get_all_user_journals_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
    start_date: Optional[str] = Query(None, description="Filter journals from this date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter journals until this date (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Search in journal content"),
    limit: Optional[int] = Query(None, description="Limit number of results"),
    sort_by: Optional[str] = Query("created_at", description="Sort by field (created_at, updated_at)"),
    order: Optional[str] = Query("desc", description="Sort order (asc, desc)"),
    previews_only: bool = Query(True, description="Return previews only for faster loading")
):
    """
    Retrieves all Free Journal sessions for the current user with optional filtering.
    - previews_only=True (default): Returns lightweight previews with caching (fast)
    - previews_only=False: Returns full journal content (slower, for detailed view)
    """
    if previews_only:
        # Use optimized preview service with caching
        journals = journal_loading_service.get_user_free_journals_preview(
            user_id=current_user.id, 
            db=db,
            start_date=start_date,
            end_date=end_date,
            search=search,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
    else:
        # Use original service for full content
        journals = free_journal_service.get_all_user_journals(
            user_id=current_user.id, 
            db=db,
            start_date=start_date,
            end_date=end_date,
            search=search,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
    
    return journals

@router.post("/", response_model=FreeJournalResponse)
def create_free_journal_session_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Creates a new Free Journal session for the current user.
    """
    free_journal = free_journal_service.create_free_journal_session(current_user.id, db)
    return free_journal

@router.get("/{session_id}", response_model=FreeJournalResponse)
def get_free_journal_session_route(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Retrieves a specific Free Journal session for the current user.
    """
    free_journal = free_journal_service.get_free_journal_by_session_id(session_id, current_user.id, db)
    if not free_journal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Free Journal session not found.")
    return free_journal

@router.delete("/{session_id}")
def delete_free_journal_session_route(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Deletes a specific Free Journal session for the current user.
    """
    try:
        success = free_journal_service.delete_free_journal_session(session_id, current_user.id, db)
        if success:
            # Invalidate both stats and journal loading cache for this user
            stats_service.invalidate_user_cache(current_user.id)
            journal_loading_service.invalidate_user_cache(current_user.id)
            return {"message": "Journal deleted successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Free Journal session not found.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/{session_id}/save", response_model=FreeJournalResponse)
def save_user_content_route(
    session_id: str, 
    data: SaveContentRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Saves user content to a specific Free Journal session.
    """
    try:
        # ⭐ FIXED: Check for empty content before attempting to save
        if not data.content or not data.content.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Cannot save empty journal content."
            )
        
        free_journal = free_journal_service.save_user_content(session_id, current_user.id, data.content, db)
        
        # Invalidate both stats and journal loading cache for this user
        stats_service.invalidate_user_cache(current_user.id)
        journal_loading_service.invalidate_user_cache(current_user.id)
        
        return free_journal
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/{session_id}/hints", response_model=HintResponse)
def get_hints_route(
    session_id: str, 
    data: HintsRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Generates hints for the user based on current content and saves them.
    """
    hint = free_journal_service.generate_hints(session_id, data.current_content, current_user.id, db)
    return hint

@router.get("/{session_id}/hints", response_model=List[HintResponse])
def get_session_hints_route(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Retrieves all hints for a given Free Journal session.
    """
    hints = free_journal_service.get_hints_for_session(session_id, current_user.id, db)
    return hints


@router.post("/{session_id}/hints/{hint_id}/voice")
def voice_hint_route(
    session_id: str,
    hint_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Converts a specific hint to speech using ElevenLabs API.
    Returns audio data that can be played by the frontend.
    """
    try:
        # Get the hint text
        hints = free_journal_service.get_hints_for_session(session_id, current_user.id, db)
        
        # Find the specific hint by ID
        target_hint = None
        for hint in hints:
            if hint.id == hint_id:
                target_hint = hint
                break
        
        if not target_hint:
            raise HTTPException(status_code=404, detail="Hint not found")
        
        # Convert hint text to speech
        voice_result = voice_service.text_to_speech(
            text=target_hint.text,
            voice_profile="hints"
        )
        
        if not voice_result["success"]:
            raise HTTPException(
                status_code=500, 
                detail=f"Voice generation failed: {voice_result.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "audio_data": voice_result["audio_data"],
            "content_type": voice_result["content_type"],
            "hint_id": hint_id,
            "text": target_hint.text,
            "voice_profile": "hints"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice hint generation failed: {str(e)}"
        )


@router.post("/text-to-voice")
def text_to_voice_route(
    data: dict
):
    """
    Generic endpoint to convert any text to speech.
    No authentication required since this is a utility endpoint.
    """
    try:
        text = data.get("text", "")
        voice_profile = data.get("voice_profile", "hints")
        
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Check if voice service is available
        if not voice_service.is_available():
            raise HTTPException(
                status_code=503, 
                detail="Voice service not available. ElevenLabs API key not configured."
            )
        
        # Convert text to speech
        voice_result = voice_service.text_to_speech(
            text=text,
            voice_profile=voice_profile
        )
        
        if not voice_result["success"]:
            error_detail = voice_result.get('error', 'Unknown error')
            if "API key" in error_detail:
                raise HTTPException(
                    status_code=503, 
                    detail="ElevenLabs API key issue. Please check your configuration."
                )
            else:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Voice generation failed: {error_detail}"
                )
        
        return {
            "success": True,
            "audio_data": voice_result["audio_data"],
            "content_type": voice_result["content_type"],
            "text": text,
            "voice_profile": voice_profile
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text-to-voice conversion failed: {str(e)}"
        )


@router.get("/voices/available")
def get_available_voices_route(
    current_user: User = Depends(get_current_user)
):
    """
    Get list of available voices from ElevenLabs.
    Useful for voice settings and testing.
    """
    try:
        voices_result = voice_service.get_available_voices()
        
        if not voices_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch voices: {voices_result.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "voices": voices_result["voices"],
            "total_count": voices_result["total_count"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch available voices: {str(e)}"
        )


@router.post("/{session_id}/voice", response_model=FreeJournalResponse)
async def transcribe_voice_route(
        session_id: str,
        audio_file: UploadFile = File(...),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_session)
):
    """
    Transcribes audio and appends it to the free journal content.
    """
    print(f"🎤 Voice route called for session: {session_id}")

    # Validate file
    if not audio_file:
        raise HTTPException(status_code=400, detail="No audio file provided")

    # Check file type
    allowed_content_types = ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/m4a', 'audio/flac', 'audio/ogg']
    if audio_file.content_type not in allowed_content_types:
        print(f"⚠️ Unsupported content type: {audio_file.content_type}")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format. Supported: {', '.join([ct.split('/')[1] for ct in allowed_content_types])}"
        )

    try:
        audio_bytes = await audio_file.read()
        print(f"📊 Received audio file: {len(audio_bytes)} bytes, type: {audio_file.content_type}")

        free_journal = free_journal_service.transcribe_audio(session_id, current_user.id, audio_bytes, db)
        
        # Invalidate both stats and journal loading cache for this user
        stats_service.invalidate_user_cache(current_user.id)
        journal_loading_service.invalidate_user_cache(current_user.id)
        
        return free_journal

    except ValueError as e:
        print(f"❌ Value error in voice route: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        print(f"❌ Unexpected error in voice route: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )

@router.post("/{session_id}/reflect")
def reflect_with_ai_route(
    session_id: str, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Analyzes the journal content with AI and updates the garden entry.
    """
    try:
        reflection = free_journal_service.reflect_with_ai(session_id, current_user.id, db)
        
        # Invalidate both stats and journal loading cache for this user
        stats_service.invalidate_user_cache(current_user.id)
        journal_loading_service.invalidate_user_cache(current_user.id)
        
        return reflection
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/{session_id}/export")
def export_free_journal_route(
    session_id: str, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Exports a free journal to PDF.
    """
    try:
        pdf_url = free_journal_service.export_to_pdf(session_id, current_user.id, db)
        return {"pdfUrl": pdf_url}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))