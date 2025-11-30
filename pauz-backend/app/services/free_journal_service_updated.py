"""
Updated Free Journal Service with Pure Raindrop AI Integration
"""
import os
import uuid
import base64
import json
from typing import Optional, List
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
load_dotenv()

from raindrop import Raindrop
from sqlmodel import Session, select
from app.models import FreeJournal, Hint
from app.database import get_session
from fastapi import Depends
from app.services.garden_service import garden_service
from app.services.storage_service import storage_service
from app.utils import pdf_generator


class FreeJournalService:
    def __init__(self):
        api_key = os.getenv('AI_API_KEY')
        self.client = Raindrop(api_key=api_key) if api_key else None
        self.organization_name = os.getenv('RAINDROP_ORG', 'Loubna-HackathonApp')
        self.application_name = os.getenv('APPLICATION_NAME', 'pauz-journaling')
        self.elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
    
    def initialize_hints_library(self):
        """Initialize the hints library with helpful suggestions"""
        if not self.client:
            return False
        
        hints = [
            {"id": "starter-1", "category": "starter", "text": "What's on your mind today?"},
            {"id": "starter-2", "category": "starter", "text": "How are you feeling right now?"},
            {"id": "starter-3", "category": "starter", "text": "What would you like to explore?"},
            {"id": "continuation-1", "category": "continuation", "text": "Can you tell me more about how this makes you feel?"},
            {"id": "continuation-2", "category": "continuation", "text": "What else would you like to explore about this topic?"},
            {"id": "continuation-3", "category": "continuation", "text": "How has this been showing up in your life recently?"},
            {"id": "continuation-4", "category": "continuation", "text": "What surprised you about this experience?"},
            {"id": "continuation-5", "category": "continuation", "text": "If you could give advice to someone in this situation, what would you say?"},
            {"id": "reflection-1", "category": "reflection", "text": "What answer feels most true for you?"},
            {"id": "reflection-2", "category": "reflection", "text": "What might be underneath these feelings?"},
            {"id": "reflection-3", "category": "reflection", "text": "What makes this moment so special?"}
        ]
        
        stored_count = 0
        for hint in hints:
            try:
                self.client.bucket.put(
                    bucket_location={
                        "bucket": {
                            "name": "hints",
                            "application_name": self.application_name
                        }
                    },
                    key=hint["id"],
                    content=base64.b64encode(json.dumps(hint).encode()).decode(),
                    content_type="application/json"
                )
                stored_count += 1
            except Exception as e:
                print(f"⚠️ Could not store hint {hint['id']}: {e}")
        
        print(f"✅ Initialized hints library with {stored_count} hints")
        return stored_count > 0

    def create_free_journal_session(self, user_id: str, db: Session = Depends(get_session)) -> FreeJournal:
        """Create a new Free Journal session"""
        session_id = str(uuid.uuid4())
        free_journal = FreeJournal(user_id=user_id, session_id=session_id)
        db.add(free_journal)
        db.commit()
        db.refresh(free_journal)
        return free_journal

    def get_free_journal_by_session_id(self, session_id: str, user_id: str, db: Session = Depends(get_session)) -> Optional[FreeJournal]:
        """Retrieve a Free Journal by session ID and user ID"""
        return db.exec(
            select(FreeJournal).where(
                FreeJournal.session_id == session_id, FreeJournal.user_id == user_id
            )
        ).first()

    def save_user_content(self, session_id: str, user_id: str, content: str, db: Session = Depends(get_session)) -> FreeJournal:
        """Save user content to the free journal"""
        free_journal = self.get_free_journal_by_session_id(session_id, user_id, db)
        if not free_journal:
            raise ValueError("Free Journal session not found.")
        
        free_journal.content = content
        db.add(free_journal)
        db.commit()
        db.refresh(free_journal)
        return free_journal

    def generate_hints(self, session_id: str, current_content: str, user_id: str, db: Session = Depends(get_session)) -> Hint:
        """Generate AI-powered writing hints"""
        if not self.client:
            raise Exception("❌ Raindrop client not available")
        
        # Determine hint category based on content
        if not current_content:
            category = "starter"
            search_query = "journal starter prompts beginning writing getting started"
        else:
            category = "continuation"
            search_query = f"writing hints journal continuation {current_content[:50]}"
        
        print(f"💡 Generating {category} hint...")
        
        try:
            # Search for relevant hints
            response = self.client.query.search(
                input=search_query,
                bucket_locations=[{
                    "bucket": {
                        "name": "hints",
                        "application_name": self.application_name
                    }
                }],
                request_id=f"hint-{uuid.uuid4()}"
            )
            
            hint_text = None
            if hasattr(response, 'results') and response.results:
                best_result = max(response.results, key=lambda x: getattr(x, 'score', 0))
                
                try:
                    hint_data = json.loads(base64.b64decode(best_result.text).decode())
                    hint_text = hint_data.get("text", best_result.text)
                except:
                    hint_text = best_result.text
            else:
                # Initialize hints library if no results
                print("📚 No hints found, initializing library...")
                self.initialize_hints_library()
                
                # Use contextual fallbacks
                if category == "starter":
                    fallback_hints = [
                        "What's on your mind today?",
                        "How are you feeling right now?", 
                        "What would you like to explore?"
                    ]
                else:
                    fallback_hints = [
                        "Can you tell me more about how this makes you feel?",
                        "What else would you like to explore about this topic?",
                        "How has this been showing up in your life recently?"
                    ]
                
                hint_text = fallback_hints[hash(current_content) % len(fallback_hints)]
            
            # Store the hint
            hint = Hint(user_id=user_id, session_id=session_id, hint_text=hint_text)
            db.add(hint)
            db.commit()
            db.refresh(hint)
            
            return hint
            
        except Exception as e:
            print(f"❌ Error generating hint: {e}")
            # Use intelligent fallback
            if category == "starter":
                fallback = "What's on your mind today?"
            else:
                fallback = "Can you tell me more about how this makes you feel?"
            
            hint = Hint(user_id=user_id, session_id=session_id, hint_text=fallback)
            db.add(hint)
            db.commit()
            db.refresh(hint)
            return hint

    def get_hints_for_session(self, session_id: str, user_id: str, db: Session = Depends(get_session)) -> List[Hint]:
        """Retrieve all hints for a session"""
        return db.exec(
            select(Hint).where(
                Hint.session_id == session_id, Hint.user_id == user_id
            )
        ).all()

    def transcribe_audio(self, session_id: str, user_id: str, audio_file: bytes, db: Session = Depends(get_session)) -> FreeJournal:
        """Upload audio to SmartBucket, transcribe it, and append to journal"""
        # Upload audio to storage (keeping Vultr as requested)
        audio_id = str(uuid.uuid4())
        storage_service.upload_audio(user_id=user_id, audio_id=audio_id, audio_data=audio_file)

        # Transcribe using ElevenLabs
        response = self.elevenlabs_client.speech_to_text.convert(audio=audio_file)
        transcribed_text = response.text

        free_journal = self.get_free_journal_by_session_id(session_id, user_id, db)
        if not free_journal:
            raise ValueError("Free Journal session not found.")
        
        if free_journal.content:
            free_journal.content += "\n" + transcribed_text
        else:
            free_journal.content = transcribed_text

        db.add(free_journal)
        db.commit()
        db.refresh(free_journal)
        
        return free_journal

    def analyze_mood_advanced(self, content: str):
        """Advanced mood analysis using keyword detection and patterns"""
        content_lower = content.lower()
        
        # Enhanced mood analysis with more keywords
        mood_keywords = {
            "happy": {
                "words": ["happy", "joy", "excited", "grateful", "optimistic", "cheerful", "wonderful", "amazing", "delighted", "pleased", "thrilled", "blessed"],
                "flower": "sunflower"
            },
            "sad": {
                "words": ["sad", "disappointed", "grief", "melancholy", "blue", "down", "upset", "hurt", "sorrowful", "depressed", "mournful"],
                "flower": "bluebell"
            },
            "anxious": {
                "words": ["anxious", "worried", "stressed", "nervous", "tense", "overwhelmed", "afraid", "fearful", "restless", "uneasy"],
                "flower": "lavender"
            },
            "calm": {
                "words": ["calm", "peaceful", "relaxed", "serene", "tranquil", "centered", "balanced", "still", "quiet", "content"],
                "flower": "lotus"
            },
            "reflective": {
                "words": ["reflective", "thoughtful", "contemplative", "pensive", "introspective", "curious", "wondering", "considering"],
                "flower": "chamomile"
            }
        }
        
        # Calculate mood scores
        mood_scores = {}
        for mood, data in mood_keywords.items():
            score = sum(1 for word in data["words"] if word in content_lower)
            mood_scores[mood] = score
        
        # Determine primary mood
        if any(mood_scores.values()):
            primary_mood = max(mood_scores, key=mood_scores.get)
        else:
            primary_mood = "reflective"
        
        # Generate insights based on content analysis
        insights = []
        
        if len(content) > 200:
            insights.append("You've expressed yourself with depth and clarity.")
        if len(content) > 100:
            insights.append("Your thoughts flow freely when you write.")
            
        if any(word in content_lower for word in ["feel", "feeling", "emotion", "emotional"]):
            insights.append("You're in touch with your emotional landscape.")
        if any(word in content_lower for word in ["think", "realize", "understand", "insight", "learned"]):
            insights.append("You're gaining valuable insights through reflection.")
        if any(word in content_lower for word in ["grateful", "thankful", "appreciate", "blessed"]):
            insights.append("Gratitude is bringing positive energy to your awareness.")
        if any(word in content_lower for word in ["family", "friend", "relationship", "connection"]):
            insights.append("Relationships are an important part of your journey.")
        if any(word in content_lower for word in ["work", "job", "career", "professional"]):
            insights.append("Your work life is influencing your current state.")
        if any(word in content_lower for word in ["challenge", "difficult", "struggle", "overcome"]):
            insights.append("You're navigating challenges with courage.")
        
        if not insights:
            insights.append("Journaling is helping you process your experiences.")
        
        # Generate follow-up questions
        next_questions = []
        if primary_mood == "happy":
            next_questions = ["What made this moment so joyful?", "How can you cultivate more of this feeling?"]
        elif primary_mood == "sad":
            next_questions = ["What do you need in this moment?", "Who can support you?"]
        elif primary_mood == "anxious":
            next_questions = ["What's one small step you can take?", "What would feel calming right now?"]
        elif primary_mood == "calm":
            next_questions = ["How can you extend this peaceful feeling?", "What practices help you stay centered?"]
        else:
            next_questions = ["What deeper truth is emerging?", "How does this reflection serve you?"]
        
        return {
            "mood": primary_mood,
            "insights": insights,
            "summary": content[:150] + "..." if len(content) > 150 else content,
            "nextQuestions": next_questions,
            "flower_type": mood_keywords[primary_mood]["flower"]
        }

    def reflect_with_ai(self, session_id: str, user_id: str, db: Session = Depends(get_session)) -> dict:
        """Analyze journal content with AI and update garden"""
        free_journal = self.get_free_journal_by_session_id(session_id, user_id, db)
        if not free_journal:
            raise ValueError("Free Journal session not found.")
        
        if not free_journal.content:
            raise ValueError("No content to analyze")
        
        print("🧠 Analyzing journal content...")
        
        # Use our advanced mood analysis
        analysis = self.analyze_mood_advanced(free_journal.content)
        
        # Create garden entry with flower mapping
        garden_service.create_garden_entry(
            user_id=user_id,
            mood=analysis["mood"],
            note=analysis["summary"],
            flower_type=analysis["flower_type"],
            db=db
        )

        return analysis

    def export_to_pdf(self, session_id: str, user_id: str, db: Session = Depends(get_session)) -> str:
        """Export a free journal to PDF"""
        free_journal = self.get_free_journal_by_session_id(session_id, user_id, db)
        if not free_journal:
            raise ValueError("Free Journal session not found.")
        
        hints = self.get_hints_for_session(session_id, user_id, db)
        
        pdf_bytes = pdf_generator.generate_pdf_free_journal(free_journal, hints)
        pdf_url = storage_service.upload_pdf(f"free_journal_{session_id}", pdf_bytes)
        return pdf_url

free_journal_service = FreeJournalService()