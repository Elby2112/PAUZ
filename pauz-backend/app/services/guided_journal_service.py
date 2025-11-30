"""
Guided Journal Service with FREE Google Gemini AI Generation
Uses Gemini for unique prompt generation while storing in Raindrop
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

# Raindrop for storage
try:
    from raindrop import Raindrop
    api_key = os.getenv('AI_API_KEY')
    application_name = os.getenv('APPLICATION_NAME', 'pauz-journaling')
    
    raindrop_client = Raindrop(api_key=api_key) if api_key else None
    print(f"✅ Raindrop client initialized for app: {application_name}")
except Exception as e:
    print(f"⚠️ Raindrop initialization failed: {e}")
    raindrop_client = None


class GuidedJournalService:
    def __init__(self):
        self.client = raindrop_client
        self.app_name = os.getenv('APPLICATION_NAME', 'pauz-journaling')
        
        # Try Gemini first (FREE)
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        if self.gemini_api_key and GEMINI_AVAILABLE and self.gemini_api_key != 'your-gemini-api-key-here':
            try:
                genai.configure(api_key=self.gemini_api_key)
                # Use gemini-2.5-flash which is available and powerful
                self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                print("✅ Google Gemini client initialized for FREE AI generation")
            except Exception as e:
                print(f"⚠️ Gemini initialization failed: {e}")
                self.gemini_model = None
        else:
            self.gemini_model = None
            if not self.gemini_api_key:
                print("⚠️ GEMINI_API_KEY not found")
            elif self.gemini_api_key == 'your-gemini-api-key-here':
                print("⚠️ Please add your Gemini API key to .env")
        
        # Fallback to OpenAI
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key and OPENAI_AVAILABLE and self.openai_api_key != 'your-openai-api-key-here':
            try:
                self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
                print("✅ OpenAI client initialized as backup")
            except Exception as e:
                print(f"⚠️ OpenAI initialization failed: {e}")
                self.openai_client = None
        else:
            self.openai_client = None

    def generate_real_prompts(self, topic: str, count: int = 9, user_context: str = "") -> list[dict]:
        """
        Generate unique, thoughtful prompts using FREE Google Gemini AI
        Every call generates different, original prompts
        """
        print(f"🧠 Generating {count} unique prompts for: {topic}")
        
        # Try Gemini first (FREE and excellent)
        if self.gemini_model:
            try:
                prompts = self._generate_with_gemini(topic, count, user_context)
                if prompts:
                    return prompts
            except Exception as e:
                print(f"❌ Gemini generation failed: {e}")
        
        # Fallback to OpenAI
        if self.openai_client:
            try:
                prompts = self._generate_with_openai(topic, count, user_context)
                if prompts:
                    return prompts
            except Exception as e:
                print(f"❌ OpenAI generation failed: {e}")
        
        # Ultimate fallback - intelligent prompts
        return self._generate_intelligent_fallbacks(topic, count)

    def _generate_with_gemini(self, topic: str, count: int, user_context: str) -> list[dict]:
        """Generate prompts using Google Gemini"""
        print("🤖 Using Google Gemini for prompt generation...")
        
        system_prompt = """You are a deeply empathetic and intuitive journaling therapist. Your role is to create profound, thought-provoking journal prompts that help people explore their inner world with curiosity and compassion.

Your prompts should:
- Be open-ended and invite deep reflection
- Help users explore their inner world with curiosity and compassion
- Avoid clichés and generic questions
- Be psychologically insightful and emotionally intelligent
- Encourage authentic self-expression
- Be different from each other in perspective and approach
- Feel personal and meaningful to someone genuinely reflecting
- Maximum 1-2 sentences per prompt"""

        user_prompt = f"""Generate {count} unique, profound journal prompts about "{topic}".

{f"User context: {user_context}" if user_context else ""}

Generate the prompts as a numbered list. Each prompt should be unique, thoughtful, and emotionally intelligent.

Example style:
1. What part of yourself needs attention right now?
2. How has your relationship with silence evolved over time?
3. What story are you telling yourself about this situation?"""

        response = self.gemini_model.generate_content(f"{system_prompt}\n\n{user_prompt}")
        prompts_text = response.text
        
        print(f"✅ Gemini generated: {prompts_text[:100]}...")
        
        # Parse and store
        prompts = self._parse_ai_prompts(prompts_text, count, topic, "gemini")
        self._store_generated_prompts(prompts, topic)
        
        return prompts

    def _generate_with_openai(self, topic: str, count: int, user_context: str) -> list[dict]:
        """Generate prompts using OpenAI as backup"""
        print("🤖 Using OpenAI for prompt generation...")
        
        system_prompt = """You are a deeply empathetic and intuitive journaling therapist. Create profound, thought-provoking journal prompts that help people explore their inner world with curiosity and compassion.

Your prompts should be open-ended, avoid clichés, be psychologically insightful, and encourage authentic self-expression. Maximum 1-2 sentences per prompt."""

        user_prompt = f"""Generate {count} unique, profound journal prompts about "{topic}".

{f"User context: {user_context}" if user_context else ""}

Generate as a numbered list. Each prompt should be unique, thoughtful, and emotionally intelligent."""

        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.8
        )

        prompts_text = response.choices[0].message.content
        print(f"✅ OpenAI generated: {prompts_text[:100]}...")
        
        prompts = self._parse_ai_prompts(prompts_text, count, topic, "openai")
        self._store_generated_prompts(prompts, topic)
        
        return prompts

    def _generate_intelligent_fallbacks(self, topic: str, count: int) -> list[dict]:
        """Generate intelligent fallback prompts when AI is not available"""
        print("🧠 Using intelligent fallback prompts...")
        
        base_templates = [
            f"What aspect of {topic} deserves your deepest curiosity right now?",
            f"How has {topic} shaped your understanding of yourself?",
            f"What would happen if you met {topic} with complete compassion?",
            f"What hidden wisdom might {topic} be offering you?",
            f"How does {topic} live in your body and your breath?",
            f"What story about {topic} is ready to be told?",
            f"What would your wisest self say about {topic}?",
            f"How can you approach {topic} with fresh eyes?",
            f"What transformation is {topic} inviting you into?"
        ]
        
        prompts = []
        for i in range(min(count, len(base_templates))):
            prompts.append({
                "id": i + 1,
                "text": base_templates[i],
                "topic": topic,
                "generated_at": str(uuid.uuid4()),
                "type": "intelligent_fallback"
            })
        
        # Fill remaining if needed
        while len(prompts) < count:
            prompts.append({
                "id": len(prompts) + 1,
                "text": f"Tell me more about your relationship with {topic}",
                "topic": topic,
                "generated_at": str(uuid.uuid4()),
                "type": "intelligent_fallback"
            })
        
        return prompts[:count]

    def generate_prompts(self, topic: str, count: int = 9) -> list[dict]:
        """Main method - generate real AI prompts"""
        return self.generate_real_prompts(topic, count)

    def _parse_ai_prompts(self, response_text: str, count: int, topic: str, ai_type: str) -> list[dict]:
        """Parse AI response into structured prompts"""
        import re
        
        prompts = []
        
        # Try to extract numbered list first
        numbered_pattern = r'(?:\d+\.|\d+\))\s*(.+?)(?=\n(?:\d+\.|\d+\))|\n\n|$)'
        matches = re.findall(numbered_pattern, response_text, re.DOTALL)
        
        for i, match in enumerate(matches):
            prompt_text = match.strip()
            if prompt_text and len(prompt_text) > 10:
                prompts.append({
                    "id": i + 1,
                    "text": prompt_text,
                    "topic": topic,
                    "generated_at": str(uuid.uuid4()),
                    "type": f"{ai_type}_generated"
                })
        
        # Alternative parsing if needed
        if len(prompts) < count:
            lines = response_text.split('\n')
            for line in lines:
                line = line.strip()
                if (line and len(line) > 15 and 
                    not line.startswith('Generate') and 
                    not line.startswith('You are') and
                    ('?' in line or 'your' in line or 'what' in line.lower() or 'how' in line.lower())):
                    
                    prompts.append({
                        "id": len(prompts) + 1,
                        "text": line,
                        "topic": topic,
                        "generated_at": str(uuid.uuid4()),
                        "type": f"{ai_type}_generated"
                    })
        
        # Ensure we have enough prompts
        while len(prompts) < count:
            fallback_prompts = [
                f"What aspect of {topic} deserves your deepest curiosity right now?",
                f"How has {topic} shaped your understanding of yourself?",
                f"What would happen if you met {topic} with complete compassion?"
            ]
            
            prompts.append({
                "id": len(prompts) + 1,
                "text": fallback_prompts[len(prompts) % len(fallback_prompts)],
                "topic": topic,
                "generated_at": str(uuid.uuid4()),
                "type": "fallback"
            })
        
        return prompts[:count]

    def _store_generated_prompts(self, prompts: list, topic: str):
        """Store AI-generated prompts in Raindrop for tracking"""
        if not self.client:
            return
        
        try:
            for prompt in prompts:
                prompt_data = {
                    "id": f"ai-generated-{uuid.uuid4()}",
                    "topic": topic,
                    "text": prompt["text"],
                    "generated_at": prompt["generated_at"],
                    "type": prompt.get("type", "ai_generated")
                }
                
                self.client.bucket.put(
                    bucket_location={
                        "bucket": {
                            "name": "journal-prompts",
                            "application_name": self.app_name
                        }
                    },
                    key=prompt_data["id"],
                    content=base64.b64encode(json.dumps(prompt_data).encode()).decode(),
                    content_type="application/json"
                )
            
            print(f"✅ Stored {len(prompts)} unique AI prompts in Raindrop")
            
        except Exception as e:
            print(f"⚠️ Could not store prompts in Raindrop: {e}")

    def create_guided_journal(self, user_id: str, topic: str, prompts_data: list[dict]) -> GuidedJournal:
        """Create a new guided journal with AI-generated prompts"""
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
                "entries": [],
                "ai_generated": True
            }
            
            storage_service.save_guided_journal_data(user_id, journal.id, journal_data)
            
            print(f"✅ Created guided journal with AI prompts: {journal.id}")
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