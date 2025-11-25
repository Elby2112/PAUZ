import os
from typing import List, Optional
from raindrop import Raindrop
from sqlmodel import Session, select
from app.models.guided_journal import GuidedJournal, Prompt, GuidedJournalEntry
from app.database import get_session
from fastapi import Depends

class GuidedJournalService:
    def __init__(self):
        self.client = Raindrop(api_key=os.getenv("AI_API_KEY"))

    def generate_prompts(self, topic: str) -> list[dict]:
        """
        Generates 6 prompts for a given topic using an AI model.
        """
        prompt = f"Generate 6 creative and insightful journal prompts about '{topic}'. The prompts should be returned as a numbered list."
        
        response = self.client.generate(prompts=prompt)
        
        prompts = response.split('\n')
        prompts = [p.strip() for p in prompts if p.strip()]
        prompts = [p.split('. ', 1)[1] if '. ' in p else p for p in prompts]

        return [{"id": i, "text": prompt_text} for i, prompt_text in enumerate(prompts)]

    def create_guided_journal(self, user_id: str, topic: str, prompts_data: List[dict], db: Session = Depends(get_session)) -> GuidedJournal:
        guided_journal = GuidedJournal(user_id=user_id, topic=topic)
        db.add(guided_journal)
        db.commit()
        db.refresh(guided_journal)

        for p_data in prompts_data:
            prompt = Prompt(text=p_data["text"], guided_journal_id=guided_journal.id)
            db.add(prompt)
        db.commit()
        return guided_journal

    def get_guided_journal_by_id(self, guided_journal_id: str, db: Session = Depends(get_session)) -> Optional[GuidedJournal]:
        return db.exec(select(GuidedJournal).where(GuidedJournal.id == guided_journal_id)).first()

    def get_user_guided_journals(self, user_id: str, db: Session = Depends(get_session)) -> List[GuidedJournal]:
        return db.exec(select(GuidedJournal).where(GuidedJournal.user_id == user_id)).all()

    def add_guided_journal_entry(self, guided_journal_id: str, prompt_id: int, response_text: str, db: Session = Depends(get_session)) -> GuidedJournalEntry:
        guided_journal_entry = GuidedJournalEntry(guided_journal_id=guided_journal_id, prompt_id=prompt_id, response=response_text)
        db.add(guided_journal_entry)
        db.commit()
        db.refresh(guided_journal_entry)
        return guided_journal_entry

guided_journal_service = GuidedJournalService()