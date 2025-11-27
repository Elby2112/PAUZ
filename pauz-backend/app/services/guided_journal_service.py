import os
from typing import List, Optional
import uuid
# from raindrop import Raindrop # Replaced with mock for now
from app.models.guided_journal import GuidedJournal, Prompt, GuidedJournalEntry
from app.services.storage_service import storage_service

# Mock AI client for testing purposes
class MockResponse:
    def __init__(self, text):
        self.text = text

class Raindrop:
    def __init__(self, api_key: str):
        print("Using Mock Raindrop client for AI text generation.")
        pass

    def generate(self, prompts: str):
        print(f"Mock Raindrop client received prompt: {prompts}")
        # Return a generic mock response
        return MockResponse("This is a mock AI generated response. Please configure a real AI client.")

class GuidedJournalService:
    def __init__(self):
        self.client = Raindrop(api_key=os.getenv("AI_API_KEY"))

    def generate_prompts(self, topic: str) -> list[dict]:
        """
        Generates 6 prompts for a given topic using an AI model.
        """
        prompt = f"Generate 6 creative and insightful journal prompts about '{topic}'. The prompts should be returned as a numbered list."
        response = self.client.generate(prompts=prompt)
        prompts_text = response.text.split('\n')
        prompts_list = [p.strip() for p in prompts_text if p.strip()]
        prompts_list = [p.split('. ', 1)[1] if '. ' in p else p for p in prompts_list]

        return [{"id": i + 1, "text": prompt_text} for i, prompt_text in enumerate(prompts_list)]

    def create_guided_journal(self, user_id: str, topic: str, prompts_data: List[dict]) -> GuidedJournal:
        """
        Creates a new GuidedJournal object in memory and saves it to the SmartBucket.
        """
        journal_id = str(uuid.uuid4())
        prompts = [Prompt(id=p_data["id"], text=p_data["text"], guided_journal_id=journal_id) for p_data in prompts_data]
        
        guided_journal = GuidedJournal(
            id=journal_id,
            user_id=user_id,
            topic=topic,
            prompts=prompts,
            entries=[] # Entries list starts empty
        )
        
        storage_service.save_guided_journal(guided_journal)
        return guided_journal

    def get_guided_journal_by_id(self, user_id: str, journal_id: str) -> Optional[GuidedJournal]:
        """
        Retrieves a guided journal by its ID from the SmartBucket.
        """
        return storage_service.get_guided_journal(user_id=user_id, journal_id=journal_id)

    def get_user_guided_journals(self, user_id: str) -> List[GuidedJournal]:
        """
        Retrieves all guided journals for a user from the SmartBucket.
        """
        journal_keys = storage_service.get_user_journal_keys(user_id)
        journals = []
        for key in journal_keys:
            # Extract journal_id from key 'user_{user_id}/journal_{journal_id}'
            journal_id = key.split('/')[-1].replace('journal_', '')
            journal = self.get_guided_journal_by_id(user_id, journal_id)
            if journal:
                journals.append(journal)
        return journals

    def add_guided_journal_entry(self, user_id: str, journal_id: str, prompt_id: int, response_text: str) -> Optional[GuidedJournalEntry]:
        """
        Adds an entry to a journal by fetching from SmartBucket, modifying, and saving back.
        """
        guided_journal = self.get_guided_journal_by_id(user_id, journal_id)
        if not guided_journal:
            return None # Journal not found

        # Create the new entry
        new_entry = GuidedJournalEntry(
            id=str(uuid.uuid4()),
            guided_journal_id=journal_id,
            prompt_id=prompt_id,
            response=response_text
        )

        # Append to the entries list
        guided_journal.entries.append(new_entry)
        
        # Save the updated journal back to the SmartBucket
        storage_service.save_guided_journal(guided_journal)

        return new_entry

guided_journal_service = GuidedJournalService()