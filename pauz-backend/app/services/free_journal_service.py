"""
Free Journal Service with FREE Google Gemini AI Generation
Uses Gemini for unique hint generation while using Raindrop for storage
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

# Import Google Gemini for FREE AI generation
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Import OpenAI as backup
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class FreeJournalService:
    def __init__(self):
        # Raindrop for storage
        api_key = os.getenv('AI_API_KEY')
        self.client = Raindrop(api_key=api_key) if api_key else None
        self.organization_name = os.getenv('RAINDROP_ORG', 'Loubna-HackathonApp')
        self.application_name = os.getenv('APPLICATION_NAME', 'pauz-journaling')
        
        # Try Gemini first (FREE)
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        if self.gemini_api_key and GEMINI_AVAILABLE and self.gemini_api_key != 'your-gemini-api-key-here':
            try:
                genai.configure(api_key=self.gemini_api_key)
                # Use gemini-2.5-flash which is available and powerful
                self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                print("✅ Google Gemini client initialized for FREE AI hints")
            except Exception as e:
                print(f"⚠️ Gemini initialization failed: {e}")
                self.gemini_model = None
        else:
            self.gemini_model = None
        
        # Fallback to OpenAI
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key and OPENAI_AVAILABLE and self.openai_api_key != 'your-openai-api-key-here':
            try:
                self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
                print("✅ OpenAI client initialized as backup for hints")
            except Exception as e:
                print(f"⚠️ OpenAI initialization failed: {e}")
                self.openai_client = None
        else:
            self.openai_client = None
        
        # ElevenLabs for transcription
        self.elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

    def generate_real_hint(self, current_content: str = "") -> str:
        """
        Generate unique, contextual writing hints using FREE Google Gemini
        Every call generates a different, thoughtful suggestion
        """
        print("💡 Generating unique AI hint...")
        
        # Try Gemini first (FREE)
        if self.gemini_model:
            try:
                hint = self._generate_hint_with_gemini(current_content)
                if hint:
                    self._store_generated_hint(hint, current_content, "gemini")
                    return hint
            except Exception as e:
                print(f"❌ Gemini hint failed: {e}")
        
        # Fallback to OpenAI
        if self.openai_client:
            try:
                hint = self._generate_hint_with_openai(current_content)
                if hint:
                    self._store_generated_hint(hint, current_content, "openai")
                    return hint
            except Exception as e:
                print(f"❌ OpenAI hint failed: {e}")
        
        # Intelligent fallback
        hint = self._generate_intelligent_fallback_hint(current_content)
        self._store_generated_hint(hint, current_content, "intelligent_fallback")
        return hint

    def _generate_hint_with_gemini(self, current_content: str = "") -> str:
        """Generate hint using Google Gemini"""
        print("🤖 Using Google Gemini for hints...")
        
        if not current_content:
            system_prompt = "You are a gentle, intuitive writing coach. Create one thoughtful, encouraging prompt to help someone begin journaling. Make it inviting, specific, and easy to respond to. Keep it to one sentence."
            user_prompt = "Generate one thoughtful writing prompt for someone starting to journal. Make it gentle and inviting."
        else:
            system_prompt = "You are a deeply empathetic writing coach who creates thoughtful, insightful questions to help people go deeper in their journaling. Your questions should be encouraging, specific to what they've written, and invite authentic reflection. Keep to one sentence."
            user_prompt = f"""Someone is journaling and has written: "{current_content}"

Generate ONE thoughtful question or prompt to help them continue writing deeper. Make it specific to what they've written, encouraging, and open-ended."""

        response = self.gemini_model.generate_content(f"{system_prompt}\n\n{user_prompt}")
        hint_text = response.text.strip()
        
        print(f"✅ Gemini hint: {hint_text}")
        return hint_text

    def _generate_hint_with_openai(self, current_content: str = "") -> str:
        """Generate hint using OpenAI"""
        print("🤖 Using OpenAI for hints...")
        
        if not current_content:
            system_prompt = "You are a gentle, intuitive writing coach. Create one thoughtful, encouraging prompt to help someone begin journaling. Make it inviting and specific. Keep to one sentence."
            user_prompt = "Generate one thoughtful writing prompt for someone starting to journal."
        else:
            system_prompt = "You are a deeply empathetic writing coach who creates thoughtful, insightful questions to help people go deeper in their journaling. Make it encouraging and specific. Keep to one sentence."
            user_prompt = f"""Someone is journaling and has written: "{current_content}"

Generate ONE thoughtful question or prompt to help them continue writing deeper."""

        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )

        hint_text = response.choices[0].message.content.strip()
        print(f"✅ OpenAI hint: {hint_text}")
        return hint_text

    def _generate_intelligent_fallback_hint(self, current_content: str = "") -> str:
        """Generate intelligent hints without AI based on context"""
        import random
        
        if not current_content:
            starter_hints = [
                "What feels most present in your awareness right now?",
                "What story is wanting to be told through you today?",
                "If your body could speak, what would it say?",
                "What emotion is asking for your attention?",
                "What truth is waiting to be discovered here?",
                "What part of yourself needs compassion right now?",
                "How can you meet this moment with kindness?",
                "What wisdom is your heart holding?",
                "What does your intuition want you to know?",
                "How are you really, beneath all the shoulds?"
            ]
            return random.choice(starter_hints)
        
        # Analyze content for intelligent contextual hints
        content_lower = current_content.lower()
        
        # Emotional cues
        if any(word in content_lower for word in ["sad", "depressed", "down", "blue"]):
            return "What gentleness does this part of you need most right now?"
        
        if any(word in content_lower for word in ["happy", "joy", "grateful", "excited"]):
            return "What makes this moment so precious and alive for you?"
        
        if any(word in content_lower for word in ["anxious", "worried", "stressed", "nervous"]):
            return "What would happen if you breathed into this feeling instead of away from it?"
        
        if any(word in content_lower for word in ["angry", "frustrated", "annoyed", "mad"]):
            return "What important boundary or need is this anger protecting?"
        
        # Content cues
        if "work" in content_lower or "job" in content_lower:
            return "How does your work connect to your deeper values and purpose?"
        
        if "family" in content_lower or "friend" in content_lower:
            return "What role do these relationships play in your growth right now?"
        
        if "love" in content_lower or "relationship" in content_lower:
            return "How does this connection help you understand yourself better?"
        
        # General continuation hints
        continuation_hints = [
            "What else wants to be expressed about this?",
            "How does this resonate in your body and breath?",
            "What wisdom is hidden beneath these words?",
            "If you could speak to this part of yourself, what would you ask?",
            "What unexpected insight is emerging here?",
            "How does this connect to your larger life journey?",
            "What would your future self tell you about this?",
            "What medicine does this experience offer you?",
            "How can you meet this with more compassion?",
            "What transformation is this moment inviting?"
        ]
        
        return random.choice(continuation_hints)

    def _store_generated_hint(self, hint_text: str, context: str, ai_type: str):
        """Store generated hint in Raindrop for tracking"""
        if not self.client:
            return
        
        try:
            hint_data = {
                "id": f"hint-{uuid.uuid4()}",
                "text": hint_text,
                "context": context[:100],  # Store first 100 chars of context
                "generated_at": str(uuid.uuid4()),
                "type": f"{ai_type}_generated" if ai_type != "intelligent_fallback" else "intelligent_fallback"
            }
            
            self.client.bucket.put(
                bucket_location={
                    "bucket": {
                        "name": "hints",
                        "application_name": self.application_name
                    }
                },
                key=hint_data["id"],
                content=base64.b64encode(json.dumps(hint_data).encode()).decode(),
                content_type="application/json"
            )
            
        except Exception as e:
            print(f"⚠️ Could not store hint in Raindrop: {e}")

    def delete_free_journal_session(self, session_id: str, user_id: str, db: Session = Depends(get_session)) -> bool:
        """Delete a Free Journal session"""
        free_journal = self.get_free_journal_by_session_id(session_id, user_id, db)
        if not free_journal:
            return False
        
        db.delete(free_journal)
        db.commit()
        return True

    def analyze_mood_with_gemini(self, content: str) -> dict:
        """Use Gemini for advanced mood analysis and reflection"""
        if self.gemini_model:
            print("🧠 Analyzing mood with Gemini...")
            try:
                system_prompt = """You are an empathetic emotional intelligence coach. Analyze the journal entry and provide:

1. The primary emotion/mood (choose one: happy, sad, anxious, calm, reflective)
2. 2-3 deep insights about what this reveals
3. A brief summary of the entry
4. 2-3 thoughtful follow-up questions

Respond in JSON format with keys: mood, insights, summary, nextQuestions"""

                user_prompt = f"""Analyze the following journal entry for emotional insights and provide gentle guidance:

{content}"""

                response = self.gemini_model.generate_content(f"{system_prompt}\n\n{user_prompt}")
                response_text = response.text.strip()
                
                try:
                    import json
                    # Clean up response text to extract JSON
                    if "```json" in response_text:
                        json_start = response_text.find("```json") + 7
                        json_end = response_text.find("```", json_start)
                        json_text = response_text[json_start:json_end].strip()
                    elif "{" in response_text and "}" in response_text:
                        json_start = response_text.find("{")
                        json_end = response_text.rfind("}") + 1
                        json_text = response_text[json_start:json_end]
                    else:
                        json_text = response_text
                    
                    analysis = json.loads(json_text)
                    
                    # Ensure required fields
                    analysis.setdefault('mood', 'reflective')
                    analysis.setdefault('insights', ['Journaling helps you process your experiences.'])
                    analysis.setdefault('summary', content[:100] + "..." if len(content) > 100 else content)
                    analysis.setdefault('nextQuestions', ['What would you like to explore further?'])
                    
                    # Add flower mapping
                    flower_mapping = {
                        "happy": "sunflower",
                        "sad": "bluebell",
                        "anxious": "lavender", 
                        "calm": "lotus",
                        "reflective": "chamomile"
                    }
                    analysis['flower_type'] = flower_mapping.get(analysis['mood'], 'wildflower')
                    
                    print(f"✅ Gemini analysis: {analysis['mood']} mood")
                    return analysis
                    
                except json.JSONDecodeError as e:
                    print(f"⚠️ Gemini response not valid JSON: {e}")
                    return self._analyze_mood_advanced(content)
                    
            except Exception as e:
                print(f"❌ Gemini mood analysis failed: {e}")
                return self._analyze_mood_advanced(content)
        
        return self._analyze_mood_advanced(content)

    def get_all_user_journals(self, 
                          user_id: str, 
                          db: Session = Depends(get_session),
                          start_date: Optional[str] = None,
                          end_date: Optional[str] = None,
                          search: Optional[str] = None,
                          limit: Optional[int] = None,
                          sort_by: str = "created_at",
                          order: str = "desc") -> List[FreeJournal]:
        """Retrieve all Free Journal sessions for a user with filtering"""
        query = select(FreeJournal).where(FreeJournal.user_id == user_id)
        
        # Date filtering
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                query = query.where(FreeJournal.created_at >= start_dt)
            except ValueError:
                pass  # Invalid date format, ignore
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                query = query.where(FreeJournal.created_at <= end_dt)
            except ValueError:
                pass  # Invalid date format, ignore
        
        # Search in content
        if search:
            query = query.where(FreeJournal.content.ilike(f"%{search}%"))
        
        # Sorting
        if order.lower() == "asc":
            query = query.order_by(getattr(FreeJournal, sort_by).asc())
        else:
            query = query.order_by(getattr(FreeJournal, sort_by).desc())
        
        # Apply limit
        if limit:
            query = query.limit(limit)
        
        return db.exec(query).all()

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
        print(f"💡 Generating hint for session {session_id}")
        
        # Generate unique hint
        hint_text = self.generate_real_hint(current_content)
        
        # Store the hint
        hint = Hint(user_id=user_id, session_id=session_id, hint_text=hint_text)
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

    def transcribe_audio(self, session_id: str, user_id: str, audio_file: bytes,
                         db: Session = Depends(get_session)) -> FreeJournal:
        """Upload audio to storage, transcribe it, and append to journal"""
        try:
            print(f"🎤 Starting transcription for session {session_id}, user {user_id}")
            print(f"📊 Audio file size: {len(audio_file)} bytes")

            # Validate audio file
            if not audio_file or len(audio_file) == 0:
                raise ValueError("Audio file is empty")

            if len(audio_file) > 25 * 1024 * 1024:  # 25MB limit
                raise ValueError("Audio file too large (max 25MB)")

            # Upload audio to storage
            audio_id = str(uuid.uuid4())
            print(f"📁 Uploading audio to storage with ID: {audio_id}")

            try:
                storage_service.upload_audio(user_id=user_id, audio_id=audio_id, audio_data=audio_file)
                print("✅ Audio uploaded to storage successfully")
            except Exception as storage_error:
                print(f"⚠️ Storage upload failed: {storage_error}")
                # Continue with transcription even if storage fails

            # Transcribe using ElevenLabs
            print("🔊 Starting ElevenLabs transcription...")
            try:
                from io import BytesIO
                # Create a file-like object from bytes
                audio_file_obj = BytesIO(audio_file)
                
                response = self.elevenlabs_client.speech_to_text.convert(
                    model_id="scribe_v1",
                    file=audio_file_obj
                )
                transcribed_text = response.text
                print(f"✅ Transcription successful: {len(transcribed_text)} characters")
                print(f"📝 Transcribed text: {transcribed_text[:100]}...")
            except Exception as elevenlabs_error:
                print(f"❌ ElevenLabs transcription failed: {elevenlabs_error}")
                # Fallback: Return empty transcription but don't fail
                transcribed_text = "[Audio recorded but transcription failed]"

            # Get or create free journal
            free_journal = self.get_free_journal_by_session_id(session_id, user_id, db)
            if not free_journal:
                print(f"❌ Free Journal not found for session {session_id}")
                raise ValueError("Free Journal session not found.")

            # Append transcribed text
            if transcribed_text and transcribed_text != "[Audio recorded but transcription failed]":
                if free_journal.content:
                    free_journal.content += "\n" + transcribed_text
                else:
                    free_journal.content = transcribed_text
            else:
                # Add a placeholder if transcription failed
                placeholder = "\n[Voice recording - transcription unavailable]"
                if free_journal.content:
                    free_journal.content += placeholder
                else:
                    free_journal.content = placeholder

            db.add(free_journal)
            db.commit()
            db.refresh(free_journal)

            print(f"✅ Journal updated successfully with transcription")
            return free_journal

        except Exception as e:
            print(f"❌ Critical error in transcribe_audio: {e}")
            raise

    def _analyze_mood_advanced(self, content: str) -> dict:
        """Advanced mood analysis with keyword patterns"""
        content_lower = content.lower()
        
        # Enhanced mood analysis
        mood_keywords = {
            "happy": ["happy", "joy", "excited", "grateful", "optimistic", "cheerful", "wonderful", "amazing", "delighted", "pleased", "thrilled", "blessed"],
            "sad": ["sad", "disappointed", "grief", "melancholy", "blue", "down", "upset", "hurt", "sorrowful", "depressed", "mournful"],
            "anxious": ["anxious", "worried", "stressed", "nervous", "tense", "overwhelmed", "afraid", "fearful", "restless", "uneasy"],
            "calm": ["calm", "peaceful", "relaxed", "serene", "tranquil", "centered", "balanced", "still", "quiet", "content"],
            "reflective": ["reflective", "thoughtful", "contemplative", "pensive", "introspective", "curious", "wondering", "considering"]
        }
        
        mood_scores = {}
        for mood, keywords in mood_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            mood_scores[mood] = score
        
        primary_mood = max(mood_scores, key=mood_scores.get) if any(mood_scores.values()) else "reflective"
        
        # Generate insights
        insights = []
        if len(content) > 200:
            insights.append("You've expressed yourself with depth and clarity.")
        if any(word in content_lower for word in ["feel", "feeling", "emotion"]):
            insights.append("You're in touch with your emotional landscape.")
        if any(word in content_lower for word in ["think", "realize", "understand"]):
            insights.append("You're gaining valuable insights through reflection.")
        if any(word in content_lower for word in ["grateful", "thankful", "appreciate"]):
            insights.append("Gratitude is bringing positive energy to your awareness.")
        
        if not insights:
            insights.append("Journaling is helping you process your experiences.")
        
        # Follow-up questions
        next_questions = []
        if primary_mood == "happy":
            next_questions = ["What made this moment so joyful?", "How can you cultivate more of this feeling?"]
        elif primary_mood == "sad":
            next_questions = ["What do you need in this moment?", "Who can support you?"]
        elif primary_mood == "anxious":
            next_questions = ["What's one small step you can take?", "What would feel calming right now?"]
        else:
            next_questions = ["What deeper truth is emerging?", "How does this reflection serve you?"]
        
        flower_mapping = {
            "happy": "sunflower",
            "sad": "bluebell",
            "anxious": "lavender",
            "calm": "lotus",
            "reflective": "chamomile"
        }
        
        return {
            "mood": primary_mood,
            "insights": insights,
            "summary": content[:150] + "..." if len(content) > 150 else content,
            "nextQuestions": next_questions,
            "flower_type": flower_mapping.get(primary_mood, "wildflower")
        }

    def reflect_with_ai(self, session_id: str, user_id: str, db: Session = Depends(get_session)) -> dict:
        """Analyze journal content with AI and update garden"""
        free_journal = self.get_free_journal_by_session_id(session_id, user_id, db)
        if not free_journal:
            raise ValueError("Free Journal session not found.")
        
        if not free_journal.content:
            raise ValueError("No content to analyze")
        
        # Use AI for mood analysis
        analysis = self.analyze_mood_with_gemini(free_journal.content)
        
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