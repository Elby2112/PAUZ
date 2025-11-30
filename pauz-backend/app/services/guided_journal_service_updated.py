"""
Updated Guided Journal Service with Pure Raindrop AI Integration
"""
import os
from dotenv import load_dotenv
load_dotenv()
from typing import List, Optional
from sqlmodel import Session, select
import uuid
import base64
import json
from fastapi import HTTPException

from app.models import GuidedJournal, Prompt, GuidedJournalEntry
from app.services.storage_service import storage_service
from app.database import get_session

# Raindrop AI import
try:
    from raindrop import Raindrop
    api_key = os.getenv('AI_API_KEY')
    organization_name = os.getenv('RAINDROP_ORG', 'Loubna-HackathonApp')
    application_name = os.getenv('APPLICATION_NAME', 'pauz-journaling')
    
    raindrop_client = Raindrop(api_key=api_key) if api_key else Raindrop()
    print(f"✅ Raindrop client initialized for app: {application_name}")

except ImportError as e:
    print(f"❌ Raindrop import failed: {e}")
    raindrop_client = None
except Exception as e:
    print(f"⚠️ Raindrop initialization failed: {e}")
    raindrop_client = None


class GuidedJournalService:
    def __init__(self):
        self.client = raindrop_client
        self.app_name = os.getenv('APPLICATION_NAME', 'pauz-journaling')

    def initialize_prompt_library(self):
        """Initialize the prompt library with high-quality content"""
        if not self.client:
            return False
        
        prompts = [
            {"id": "mindfulness-1", "topic": "mindfulness", "text": "What does being present feel like for you right now?"},
            {"id": "mindfulness-2", "topic": "mindfulness", "text": "Describe a moment today when you felt fully aware and engaged."},
            {"id": "mindfulness-3", "topic": "mindfulness", "text": "How can you create more space for mindfulness in your daily routine?"},
            {"id": "gratitude-1", "topic": "gratitude", "text": "List three things you're grateful for today and why they matter."},
            {"id": "gratitude-2", "topic": "gratitude", "text": "Who made a positive impact on your life recently, and how?"},
            {"id": "gratitude-3", "topic": "gratitude", "text": "Describe a simple pleasure you almost overlooked today."},
            {"id": "stress-1", "topic": "stress", "text": "What's weighing on your mind right now, and what can you control?"},
            {"id": "stress-2", "topic": "stress", "text": "Describe your stress using weather metaphors - what kind of storm is it?"},
            {"id": "stress-3", "topic": "stress", "text": "What small action could bring you a moment of relief right now?"},
            {"id": "growth-1", "topic": "growth", "text": "What did you learn about yourself this week?"},
            {"id": "growth-2", "topic": "growth", "text": "Describe a recent failure and what it taught you."},
            {"id": "growth-3", "topic": "growth", "text": "What part of your past self do you miss, and what part have you outgrown?"},
            {"id": "relationships-1", "topic": "relationships", "text": "Who in your life truly sees you, and how does that feel?"},
            {"id": "relationships-2", "topic": "relationships", "text": "Describe a recent meaningful conversation and its impact on you."},
            {"id": "relationships-3", "topic": "relationships", "text": "What relationship pattern are you working to change?"},
            {"id": "career-1", "topic": "career", "text": "What part of your work makes you feel most alive?"},
            {"id": "career-2", "topic": "career", "text": "Describe a moment when you felt truly in your element professionally."},
            {"id": "career-3", "topic": "career", "text": "What impact do you want to make through your work?"}
        ]
        
        stored_count = 0
        for prompt in prompts:
            try:
                self.client.bucket.put(
                    bucket_location={
                        "bucket": {
                            "name": "journal-prompts",
                            "application_name": self.app_name
                        }
                    },
                    key=prompt["id"],
                    content=base64.b64encode(json.dumps(prompt).encode()).decode(),
                    content_type="application/json"
                )
                stored_count += 1
            except Exception as e:
                print(f"⚠️ Could not store prompt {prompt['id']}: {e}")
        
        print(f"✅ Initialized prompt library with {stored_count} prompts")
        return stored_count > 0

    def generate_prompts(self, topic: str, count: int = 9) -> list[dict]:
        """
        Generate AI-powered prompts using Raindrop semantic search
        """
        if not self.client:
            raise Exception("❌ Raindrop client not available")
        
        print(f"🤖 Finding {count} best prompts for: {topic}")
        
        try:
            # Use semantic search to find relevant prompts
            response = self.client.query.search(
                input=f"{topic} personal reflection journal feelings thoughts",
                bucket_locations=[{
                    "bucket": {
                        "name": "journal-prompts",
                        "application_name": self.app_name
                    }
                }],
                request_id=f"prompts-{uuid.uuid4()}"
            )
            
            prompts = []
            if hasattr(response, 'results') and response.results:
                for result in response.results:
                    try:
                        # Parse the JSON content
                        prompt_data = json.loads(base64.b64decode(result.text).decode())
                        
                        # Filter for relevant prompts
                        prompt_text = prompt_data.get("text", result.text)
                        prompt_topic = prompt_data.get("topic", "general")
                        
                        # Relevance check
                        if (prompt_topic.lower() in topic.lower() or 
                            topic.lower() in prompt_text.lower() or
                            any(word in prompt_text.lower() for word in topic.lower().split())):
                            
                            prompts.append({
                                "id": len(prompts) + 1,
                                "text": prompt_text,
                                "score": getattr(result, 'score', 0),
                                "topic": prompt_topic
                            })
                    except:
                        # If parsing fails, check if raw text looks like a prompt
                        text = result.text.strip()
                        if (len(text) > 20 and 
                            not text.startswith("Generate") and 
                            not text.startswith("Topic:") and
                            ("?" in text or "Describe" in text or "What" in text)):
                            prompts.append({
                                "id": len(prompts) + 1,
                                "text": text,
                                "score": getattr(result, 'score', 0),
                                "topic": "general"
                            })
                
                # Sort by relevance score
                prompts.sort(key=lambda x: x['score'], reverse=True)
                final_prompts = prompts[:count]
                
                # If not enough prompts found, initialize library and try again
                if len(final_prompts) < count:
                    print(f"📚 Only found {len(final_prompts)} prompts, initializing library...")
                    self.initialize_prompt_library()
                    
                    # Try search again
                    response2 = self.client.query.search(
                        input=f"{topic} personal reflection journal",
                        bucket_locations=[{
                            "bucket": {
                                "name": "journal-prompts",
                                "application_name": self.app_name
                            }
                        }],
                        request_id=f"prompts-second-{uuid.uuid4()}"
                    )
                    
                    if hasattr(response2, 'results') and response2.results:
                        for result in response2.results:
                            try:
                                prompt_data = json.loads(base64.b64decode(result.text).decode())
                                if len(final_prompts) < count:
                                    final_prompts.append({
                                        "id": len(final_prompts) + 1,
                                        "text": prompt_data.get("text", result.text),
                                        "score": getattr(result, 'score', 0),
                                        "topic": prompt_data.get("topic", "general")
                                    })
                            except:
                                continue
                
                # Fill remaining slots with topic-specific fallbacks
                while len(final_prompts) < count:
                    fallback_prompts = [
                        f"What does {topic} mean to you right now?",
                        f"Describe your experience with {topic} today.",
                        f"How has {topic} affected your life recently?",
                        f"What would you like to change about {topic}?",
                        f"When did you first become aware of {topic}?",
                        f"How do you feel when you think about {topic}?",
                        f"What questions do you have about {topic}?",
                        f"Describe your relationship with {topic}.",
                        f"What insights have you gained about {topic}?"
                    ]
                    
                    next_prompt = fallback_prompts[len(final_prompts) % len(fallback_prompts)]
                    final_prompts.append({
                        "id": len(final_prompts) + 1,
                        "text": next_prompt,
                        "score": 0.1,
                        "topic": topic
                    })
                
                print(f"📝 Successfully generated {len(final_prompts)} prompts")
                return final_prompts[:count]
                
            else:
                # Initialize library and use fallbacks
                print("📚 No existing prompts found, initializing library...")
                self.initialize_prompt_library()
                
                fallback_prompts = [
                    f"What does {topic} mean to you right now?",
                    f"Describe your experience with {topic} today.",
                    f"How has {topic} affected your life recently?"
                ]
                
                return [
                    {"id": i + 1, "text": prompt, "score": 0.5, "topic": topic}
                    for i, prompt in enumerate(fallback_prompts[:count])
                ]
                
        except Exception as e:
            print(f"❌ Error generating prompts: {e}")
            raise Exception(f"AI prompt generation failed: {e}")

    def create_guided_journal(self, user_id: str, topic: str, prompts_data: list[dict]) -> GuidedJournal:
        """Create a new guided journal with prompts"""
        try:
            journal = GuidedJournal(
                id=str(uuid.uuid4()),
                user_id=user_id,
                topic=topic
            )

            prompts = []
            for prompt_data in prompts_data:
                prompt = Prompt(
                    text=prompt_data['text'],
                    guided_journal_id=journal.id
                )
                prompts.append(prompt)

            # Save to SmartBucket
            journal_data = {
                "id": journal.id,
                "user_id": journal.user_id,
                "topic": journal.topic,
                "created_at": journal.created_at.isoformat(),
                "prompts": [p.model_dump() for p in prompts],
                "entries": []
            }
            
            storage_service.save_guided_journal_data(user_id, journal.id, journal_data)
            
            print(f"✅ Created guided journal: {journal.id}")
            return journal

        except Exception as e:
            print(f"❌ Error creating guided journal: {e}")
            raise HTTPException(status_code=500, detail="Failed to create guided journal")

    def get_user_guided_journals(self, user_id: str) -> list[GuidedJournal]:
        """Retrieve all guided journals for a user"""
        try:
            journals = storage_service.get_user_guided_journals(user_id)
            return journals
        except Exception as e:
            print(f"❌ Error getting user journals: {e}")
            return []

    def get_guided_journal_by_id(self, user_id: str, journal_id: str) -> Optional[GuidedJournal]:
        """Retrieve a specific guided journal by ID"""
        try:
            journal = storage_service.get_guided_journal_data(user_id, journal_id)
            return journal
        except Exception as e:
            print(f"❌ Error getting journal by ID: {e}")
            return None

    def add_guided_journal_entry(self, user_id: str, journal_id: str, prompt_id: int, response_text: str) -> Optional[GuidedJournalEntry]:
        """Add an entry to a guided journal"""
        try:
            journal_data = storage_service.get_guided_journal_data(user_id, journal_id)
            if not journal_data:
                return None

            entry = GuidedJournalEntry(
                id=str(uuid.uuid4()),
                guided_journal_id=journal_id,
                prompt_id=prompt_id,
                response=response_text
            )

            if 'entries' not in journal_data:
                journal_data['entries'] = []
            
            journal_data['entries'].append({
                "id": entry.id,
                "prompt_id": entry.prompt_id,
                "response": entry.response,
                "created_at": entry.created_at.isoformat()
            })

            storage_service.save_guided_journal_data(user_id, journal_id, journal_data)
            
            print(f"✅ Added entry to journal: {journal_id}")
            return entry

        except Exception as e:
            print(f"❌ Error adding journal entry: {e}")
            return None


# Initialize the service
guided_journal_service = GuidedJournalService()