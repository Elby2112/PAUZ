import os
from typing import List, Optional
from raindrop import Raindrop
from sqlmodel import Session, select
from app.models.journal import Journal, Prompt, JournalEntry
from app.database import get_session
from fastapi import Depends

class JournalService:
    def __init__(self):
        self.client = Raindrop(api_key=os.getenv("AI_API_KEY"))

    def generate_prompts(self, topic: str) -> list[dict]:
        """
        Generates 9 prompts for a given topic using an AI model.
        """
        prompt = f"Generate 9 creative and insightful journal prompts about '{topic}'. The prompts should be returned as a numbered list."
        
        response = self.client.generate(prompts=prompt)
        
        prompts = response.split('\n')
        prompts = [p.strip() for p in prompts if p.strip()]
        prompts = [p.split('. ', 1)[1] if '. ' in p else p for p in prompts]

        return [{"id": i, "text": prompt_text} for i, prompt_text in enumerate(prompts)]

    def create_journal(self, user_id: str, topic: str, prompts_data: List[dict], db: Session = Depends(get_session)) -> Journal:
        journal = Journal(user_id=user_id, topic=topic)
        db.add(journal)
        db.commit()
        db.refresh(journal)

        for p_data in prompts_data:
            prompt = Prompt(text=p_data["text"], journal_id=journal.id)
            db.add(prompt)
        db.commit()
        db.refresh(journal) # Refresh to load relationships

        return journal

    def get_journal_by_id(self, journal_id: str, db: Session = Depends(get_session)) -> Optional[Journal]:
        return db.exec(select(Journal).where(Journal.id == journal_id)).first()

    def get_user_journals(self, user_id: str, db: Session = Depends(get_session)) -> List[Journal]:
        return db.exec(select(Journal).where(Journal.user_id == user_id)).all()

    def add_journal_entry(self, journal_id: str, prompt_id: int, response_text: str, db: Session = Depends(get_session)) -> JournalEntry:
        journal_entry = JournalEntry(journal_id=journal_id, prompt_id=prompt_id, response=response_text)
        db.add(journal_entry)
        db.commit()
        db.refresh(journal_entry)
        return journal_entry

journal_service = JournalService()