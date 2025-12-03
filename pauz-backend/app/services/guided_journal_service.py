"""
Guided Journal Service with FREE Google Gemini AI Generation
Uses Gemini for unique prompt generation while storing in SmartBucket (Raindrop)
"""
import os
from dotenv import load_dotenv
load_dotenv()
from typing import List, Optional
from sqlmodel import Session, select
import uuid
import base64
import json
import datetime
from fastapi import HTTPException

from app.models import GuidedJournal, Prompt, GuidedJournalEntry
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

# Raindrop for storage - NO FALLBACKS
try:
    from raindrop import Raindrop
except ImportError:
    Raindrop = None


class GuidedJournalService:
    def __init__(self):
        # Raindrop for storage ONLY - no local fallbacks
        api_key = os.getenv('AI_API_KEY')
        if not api_key:
            raise ValueError("AI_API_KEY required for SmartBucket storage")
        
        if not Raindrop:
            raise ImportError("Raindrop library required for SmartBucket storage")
            
        self.client = Raindrop(api_key=api_key)
        self.organization_name = os.getenv('RAINDROP_ORG', 'Loubna-HackathonApp')
        self.application_name = os.getenv('APPLICATION_NAME', 'pauz-journaling')
        
        print(f"✅ Raindrop SmartBucket client initialized for guided journals: {self.application_name}")
        
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

    def create_guided_journal(self, user_id: str, topic: str, prompts_data: list[dict]) -> dict:
        """Create a new guided journal with AI-generated prompts"""
        try:
            journal_id = str(uuid.uuid4())
            
            # Save to SmartBucket directly as dict
            journal_data = {
                "id": journal_id,
                "user_id": user_id,
                "topic": topic,
                "created_at": datetime.datetime.now().isoformat(),
                "prompts": prompts_data,
                "entries": [],
                "ai_generated": True
            }
            
            storage_service.save_guided_journal_data(user_id, journal_id, journal_data)
            
            print(f"✅ Created guided journal with AI prompts: {journal_id}")
            return journal_data

        except Exception as e:
            print(f"❌ Error creating guided journal: {e}")
            raise HTTPException(status_code=500, detail="Failed to create guided journal")

    def create_guided_journal_with_entries(self, user_id: str, topic: str, prompts_data: list[dict], entries_data: list[dict]) -> dict:
        """Create a new guided journal with prompts and entries using SmartBucket ONLY"""
        journal_id = str(uuid.uuid4())
        
        # Prepare journal data for SmartBucket
        journal_data = {
            "id": journal_id,
            "user_id": user_id,
            "topic": topic,
            "created_at": datetime.datetime.now().isoformat(),
            "prompts": prompts_data,
            "entries": entries_data,
            "ai_generated": True,
            "type": "guided_journal"
        }
        
        import base64
        
        try:
            # Try guided-journals bucket first (preferred)
            self.client.bucket.put(
                bucket_location={
                    "bucket": {
                        "name": "guided-journals",
                        "application_name": self.application_name
                    }
                },
                key=f"journal_{journal_id}",
                content=base64.b64encode(json.dumps(journal_data).encode()).decode(),
                content_type="application/json"
            )
            print(f"✅ Created guided journal in guided-journals SmartBucket: {journal_id}")
            return journal_data
            
        except Exception as bucket_error:
            print(f"⚠️ guided-journals bucket not available: {bucket_error}")
            print(f"🔄 Falling back to hints bucket...")
            
            # Fallback to hints bucket (which exists)
            try:
                self.client.bucket.put(
                    bucket_location={
                        "bucket": {
                            "name": "hints",
                            "application_name": self.application_name
                        }
                    },
                    key=f"guided_journal_{journal_id}",
                    content=base64.b64encode(json.dumps(journal_data).encode()).decode(),
                    content_type="application/json"
                )
                print(f"✅ Created guided journal in hints SmartBucket: {journal_id}")
                return journal_data
                
            except Exception as hints_error:
                print(f"❌ Both buckets failed: {hints_error}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"SmartBucket storage failed. Hints bucket error: {str(hints_error)}"
                )

    def get_user_guided_journals(self, user_id: str) -> list[dict]:
        """Retrieve all guided journals for a user from SmartBucket ONLY"""
        journals = []
        
        # Try guided-journals bucket first
        try:
            response = self.client.bucket.list(
                bucket_location={
                    "bucket": {
                        "name": "guided-journals",
                        "application_name": self.application_name
                    }
                }
            )
            
            for item in response.objects:
                if hasattr(item, 'key') and f"journal_" in item.key:
                    try:
                        content = self.client.bucket.get(
                            bucket_location={
                                "bucket": {
                                    "name": "guided-journals", 
                                    "application_name": self.application_name
                                }
                            },
                            key=item.key
                        )
                        
                        journal_data = json.loads(base64.b64decode(content.content).decode())
                        # Only return journals for this user and type guided_journal
                        if journal_data.get('user_id') == user_id and journal_data.get('type') == 'guided_journal':
                            journals.append(journal_data)
                    except Exception as item_error:
                        print(f"⚠️ Could not retrieve {item.key}: {item_error}")
                        
            print(f"✅ Retrieved {len(journals)} guided journals from guided-journals bucket for user {user_id}")
            
        except Exception as bucket_error:
            print(f"⚠️ guided-journals bucket not available: {bucket_error}")
            print(f"🔄 Checking hints bucket for guided journals...")
            
            # Fallback to hints bucket
            try:
                response = self.client.bucket.list(
                    bucket_location={
                        "bucket": {
                            "name": "hints",
                            "application_name": self.application_name
                        }
                    }
                )
                
                for item in response.objects:
                    if hasattr(item, 'key') and f"guided_journal_" in item.key:
                        try:
                            content = self.client.bucket.get(
                                bucket_location={
                                    "bucket": {
                                        "name": "hints", 
                                        "application_name": self.application_name
                                    }
                                },
                                key=item.key
                            )
                            
                            journal_data = json.loads(base64.b64decode(content.content).decode())
                            # Only return journals for this user and type guided_journal
                            if journal_data.get('user_id') == user_id and journal_data.get('type') == 'guided_journal':
                                journals.append(journal_data)
                        except Exception as item_error:
                            print(f"⚠️ Could not retrieve {item.key}: {item_error}")
                
                print(f"✅ Retrieved {len(journals)} guided journals from hints bucket for user {user_id}")
                
            except Exception as hints_error:
                print(f"❌ Both buckets failed: {hints_error}")
                raise HTTPException(
                    status_code=500,
                    detail=f"SmartBucket retrieval failed. Hints bucket error: {str(hints_error)}"
                )
        
        return journals

    def get_guided_journal_by_id(self, user_id: str, journal_id: str) -> Optional[dict]:
        """Retrieve a specific guided journal by ID from SmartBucket ONLY"""
        import base64
        
        # Try guided-journals bucket first
        try:
            content = self.client.bucket.get(
                bucket_location={
                    "bucket": {
                        "name": "guided-journals",
                        "application_name": self.application_name
                    }
                },
                key=f"journal_{journal_id}"
            )
            
            journal_data = json.loads(base64.b64decode(content.content).decode())
            
            # Verify this journal belongs to the user and is correct type
            if journal_data.get('user_id') == user_id and journal_data.get('type') == 'guided_journal':
                print(f"✅ Retrieved guided journal from guided-journals SmartBucket: {journal_id}")
                return journal_data
            else:
                print(f"❌ Journal {journal_id} does not belong to user {user_id} or wrong type")
                return None
                
        except Exception as bucket_error:
            print(f"⚠️ guided-journals bucket error: {bucket_error}")
            print(f"🔄 Checking hints bucket...")
            
            # Fallback to hints bucket
            try:
                content = self.client.bucket.get(
                    bucket_location={
                        "bucket": {
                            "name": "hints",
                            "application_name": self.application_name
                        }
                    },
                    key=f"guided_journal_{journal_id}"
                )
                
                journal_data = json.loads(base64.b64decode(content.content).decode())
                
                # Verify this journal belongs to the user and is correct type
                if journal_data.get('user_id') == user_id and journal_data.get('type') == 'guided_journal':
                    print(f"✅ Retrieved guided journal from hints SmartBucket: {journal_id}")
                    return journal_data
                else:
                    print(f"❌ Journal {journal_id} does not belong to user {user_id} or wrong type")
                    return None
                    
            except Exception as hints_error:
                print(f"❌ Both buckets failed: {hints_error}")
                return None

    def delete_guided_journal(self, user_id: str, journal_id: str) -> bool:
        """Delete a guided journal from SmartBucket"""
        import base64
        
        # Try guided-journals bucket first
        try:
            # Check if journal exists and belongs to user
            content = self.client.bucket.get(
                bucket_location={
                    "bucket": {
                        "name": "guided-journals",
                        "application_name": self.application_name
                    }
                },
                key=f"journal_{journal_id}"
            )
            
            journal_data = json.loads(base64.b64decode(content.content).decode())
            
            # Verify this journal belongs to the user and is correct type
            if journal_data.get('user_id') == user_id and journal_data.get('type') == 'guided_journal':
                # Delete the journal
                self.client.bucket.delete(
                    bucket_location={
                        "bucket": {
                            "name": "guided-journals",
                            "application_name": self.application_name
                        }
                    },
                    key=f"journal_{journal_id}"
                )
                print(f"✅ Deleted guided journal from guided-journals bucket: {journal_id}")
                return True
            else:
                print(f"❌ Journal {journal_id} does not belong to user {user_id} or wrong type")
                return False
                
        except Exception as bucket_error:
            print(f"⚠️ guided-journals bucket not accessible: {bucket_error}")
            print(f"🔄 Checking hints bucket...")
            
            # Fallback to hints bucket
            try:
                # Check if journal exists in hints bucket
                content = self.client.bucket.get(
                    bucket_location={
                        "bucket": {
                            "name": "hints",
                            "application_name": self.application_name
                        }
                    },
                    key=f"guided_journal_{journal_id}"
                )
                
                journal_data = json.loads(base64.b64decode(content.content).decode())
                
                # Verify this journal belongs to the user and is correct type
                if journal_data.get('user_id') == user_id and journal_data.get('type') == 'guided_journal':
                    # Delete the journal
                    self.client.bucket.delete(
                        bucket_location={
                            "bucket": {
                                "name": "hints",
                                "application_name": self.application_name
                            }
                        },
                        key=f"guided_journal_{journal_id}"
                    )
                    print(f"✅ Deleted guided journal from hints bucket: {journal_id}")
                    return True
                else:
                    print(f"❌ Journal {journal_id} does not belong to user {user_id} or wrong type")
                    return False
                    
            except Exception as hints_error:
                print(f"❌ Both buckets failed: {hints_error}")
                return False

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