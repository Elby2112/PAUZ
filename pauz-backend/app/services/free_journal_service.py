import os
import uuid
from typing import Optional, List
from raindrop import Raindrop
import elevenlabs
import json
from sqlmodel import Session, select
from app.models.free_journal import FreeJournal
from app.models.hint import Hint
from app.models.garden import Garden
from app.database import get_session
from fastapi import Depends
from app.services.garden_service import garden_service # Will be updated later
from app.services.storage_service import storage_service
from app.utils import pdf_generator
from datetime import datetime


class FreeJournalService:
    def __init__(self):
        self.client = Raindrop(api_key=os.getenv("AI_API_KEY"))
        elevenlabs.set_api_key(os.getenv("ELEVENLABS_API_KEY"))
    
    def create_free_journal_session(self, user_id: str, db: Session = Depends(get_session)) -> FreeJournal:
        """
        Creates a new Free Journal session and saves it to the database.
        """
        session_id = str(uuid.uuid4())
        free_journal = FreeJournal(user_id=user_id, session_id=session_id)
        db.add(free_journal)
        db.commit()
        db.refresh(free_journal)
        return free_journal

    def get_free_journal_by_session_id(self, session_id: str, user_id: str, db: Session = Depends(get_session)) -> Optional[FreeJournal]:
        """
        Retrieves a Free Journal by session ID and user ID.
        """
        return db.exec(
            select(FreeJournal).where(
                FreeJournal.session_id == session_id, FreeJournal.user_id == user_id
            )
        ).first()

    def save_user_content(self, session_id: str, user_id: str, content: str, db: Session = Depends(get_session)) -> FreeJournal:
        """
        Saves user content to the free journal in the database.
        """
        free_journal = self.get_free_journal_by_session_id(session_id, user_id, db)
        if not free_journal:
            # This should ideally be handled by a higher layer (route) raising HTTPException
            raise ValueError("Free Journal session not found.")
        
        free_journal.content = content
        db.add(free_journal)
        db.commit()
        db.refresh(free_journal)
        return free_journal

    def generate_hints(self, session_id: str, current_content: str, user_id: str, db: Session = Depends(get_session)) -> Hint:
        """
        Generates hints for the user and saves them to the database.
        """
        if not current_content:
            prompt_text = "Generate a creative and insightful journal prompt to get someone started with writing."
        else:
            prompt_text = f"The user has written the following in their journal:\n\n{current_content}\n\nGenerate a question or prompt to help them continue writing."

        response = self.client.generate(prompts=prompt_text)
        hint_text = response.text
        
        hint = Hint(user_id=user_id, session_id=session_id, hint_text=hint_text)
        db.add(hint)
        db.commit()
        db.refresh(hint)
        
        return hint

    def get_hints_for_session(self, session_id: str, user_id: str, db: Session = Depends(get_session)) -> List[Hint]:
        """
        Retrieves all hints for a given session and user.
        """
        return db.exec(
            select(Hint).where(
                Hint.session_id == session_id, Hint.user_id == user_id
            )
        ).all()

    def transcribe_audio(self, session_id: str, user_id: str, audio_file: bytes, db: Session = Depends(get_session)) -> FreeJournal:
        """
        Transcribes audio using ElevenLabs (simulated) and appends it to the journal content.
        """
        # This is a placeholder for the actual transcription.
        transcribed_text = "This is a simulated transcription of the audio file."

        free_journal = self.get_free_journal_by_session_id(session_id, user_id, db)
        if not free_journal:
            raise ValueError("Free Journal session not found.")
        
        free_journal.content += "\n" + transcribed_text
        db.add(free_journal)
        db.commit()
        db.refresh(free_journal)
        
        return free_journal

    def reflect_with_ai(self, session_id: str, user_id: str, db: Session = Depends(get_session)) -> dict:
        """
        Analyzes the journal content with AI and updates the garden entry.
        """
        free_journal = self.get_free_journal_by_session_id(session_id, user_id, db)
        if not free_journal:
            raise ValueError("Free Journal session not found.")
        
        prompt = f"Analyze the following journal entry and provide: 1. The overall mood (e.g., happy, sad, reflective, calm). 2. Key insights from the entry. 3. A few questions to prompt further reflection. Return the response as a JSON object with keys 'mood', 'insights', and 'nextQuestions'.\n\n{free_journal.content}"
        
        response = self.client.generate(prompts=prompt)
        response_text = response.text
        
        try:
            response_json = json.loads(response_text)
            mood = response_json.get("mood")
            insights = response_json.get("insights")
            next_questions = response_json.get("nextQuestions")
        except json.JSONDecodeError:
            mood = "unknown"
            insights = "Could not parse AI response."
            next_questions = []

        # Map mood to flower type
        flower_mapping = {
            "happy": "sunflower",
            "sad": "bluebell",
            "reflective": "lotus",
            "calm": "lavender"
        }
        flower_type = flower_mapping.get(mood.lower(), "wildflower")

        # Assuming garden_service has a create_garden_entry method
        garden_service.create_garden_entry(
            user_id=user_id,
            mood=mood,
            note=insights,
            flower_type=flower_type,
            db=db
        )

        return {
            "mood": mood,
            "insights": insights,
            "nextQuestions": next_questions
        }

    def export_to_pdf(self, session_id: str, user_id: str, db: Session = Depends(get_session)) -> str:
        """
        Exports a free journal to PDF.
        """
        free_journal = self.get_free_journal_by_session_id(session_id, user_id, db)
        if not free_journal:
            raise ValueError("Free Journal session not found.")
        
        hints = self.get_hints_for_session(session_id, user_id, db)
        
        pdf_bytes = pdf_generator.generate_pdf_free_journal(free_journal, hints) # New function in pdf_generator
        pdf_url = storage_service.upload_pdf(f"free_journal_{session_id}", pdf_bytes)
        return pdf_url

free_journal_service = FreeJournalService()