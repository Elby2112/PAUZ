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
        # Define the 10 life categories for holistic reflection
        self.life_categories = {
            "mind": {
                "title": "Mind",
                "aspects": ["thoughts", "mental clarity", "beliefs", "focus", "learning", "stress management", "creativity"]
            },
            "body": {
                "title": "Body", 
                "aspects": ["health", "energy", "movement", "nutrition", "sleep", "physical wellbeing", "body image"]
            },
            "heart": {
                "title": "Heart",
                "aspects": ["emotions", "feelings", "emotional health", "self-love", "vulnerability", "emotional expression"]
            },
            "friends": {
                "title": "Friends",
                "aspects": ["friendships", "social connections", "support systems", "community", "social activities", "belonging"]
            },
            "family": {
                "title": "Family", 
                "aspects": ["family relationships", "parental bonds", "siblings", "family dynamics", "traditions", "family support"]
            },
            "romance": {
                "title": "Romance",
                "aspects": ["love relationships", "partnership", "intimacy", "dating", "romantic fulfillment", "love language"]
            },
            "mission": {
                "title": "Mission",
                "aspects": ["purpose", "calling", "meaning", "contribution", "legacy", "life direction", "impact"]
            },
            "growth": {
                "title": "Growth",
                "aspects": ["personal development", "learning", "skills", "self-improvement", "evolution", "potential", "breakthroughs"]
            },
            "money": {
                "title": "Money",
                "aspects": ["finances", "abundance", "financial security", "money mindset", "prosperity", "resource management"]
            },
            "joy": {
                "title": "Joy",
                "aspects": ["happiness", "pleasure", "fun", "playfulness", "delight", "celebration", "life enjoyment"]
            }
        }
        
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

    def get_available_categories(self) -> dict:
        """Return all available life categories with their aspects"""
        return self.life_categories
    
    def generate_prompts(self, category: str, count: int = 9, user_context: str = "") -> list[dict]:
        """Main method - generate category-specific prompts"""
        return self.generate_real_prompts(category, count, user_context)
    
    def generate_real_prompts(self, category: str, count: int = 9, user_context: str = "") -> list[dict]:
        """
        Generate thoughtful prompts for specific life categories
        Focuses on what's going well, what needs improvement, and boundaries
        Progresses from simple awareness to deep transformation insights
        """
        # Validate category
        if category not in self.life_categories:
            raise ValueError(f"Invalid category. Choose from: {', '.join(self.life_categories.keys())}")
        
        category_info = self.life_categories[category]
        print(f"🌱 Generating {count} prompts for {category_info['title']} category")
        
        # Try Gemini first (FREE and excellent)
        if self.gemini_model:
            try:
                prompts = self._generate_category_prompts_with_gemini(category, category_info, count, user_context)
                if prompts:
                    return prompts
            except Exception as e:
                print(f"❌ Gemini generation failed: {e}")
        
        # Fallback to OpenAI
        if self.openai_client:
            try:
                prompts = self._generate_category_prompts_with_openai(category, category_info, count, user_context)
                if prompts:
                    return prompts
            except Exception as e:
                print(f"❌ OpenAI generation failed: {e}")
        
        # Ultimate fallback - intelligent category-specific prompts
        return self._generate_category_fallbacks(category, category_info, count)

    def _generate_category_prompts_with_gemini(self, category: str, category_info: dict, count: int, user_context: str) -> list[dict]:
        """Generate category-specific prompts using Google Gemini"""
        print(f"🤖 Using Gemini for {category_info['title']} category prompts...")
        
        aspects = category_info["aspects"]
        
        system_prompt = f"""You are a wise life coach who creates thoughtful journal prompts for the "{category_info['title']}" area of life. Your prompts help people reflect holistically on different aspects of this category.

Create exactly 9 prompts that follow this structure:

**Prompts 1-3 (What's Going Well):**
- Focus on appreciating strengths, successes, and positive aspects
- Celebrate what's working beautifully in this life area
- Encourage gratitude for positive developments

**Prompts 4-6 (What Needs Improvement):**
- Gently explore challenges and areas for growth
- Identify what's not working or needs attention
- Invite honest but compassionate reflection on struggles

**Prompts 7-9 (Boundaries & Commitments):**
- Explore what boundaries need to be set or maintained
- Consider what commitments to make or release
- Focus on actionable steps and empowerment

Aspects to consider: {', '.join(aspects)}

Your voice should be warm, encouraging, and insight-oriented. Use gentle language and create a safe space for honest self-reflection. Each prompt should be 1-2 sentences maximum."""

        user_prompt = f"""Generate exactly 9 journal prompts for the {category_info['title']} category.

{f"User context: {user_context}" if user_context else ""}

Focus on these aspects: {', '.join(aspects)}

Structure exactly as:
1-3: Celebrate what's going well in this life area
4-6: Gently explore what needs improvement  
7-9: Consider boundaries and commitments

Make each prompt specific to {category_info['title']} and its aspects."""

        response = self.gemini_model.generate_content(f"{system_prompt}\n\n{user_prompt}")
        prompts_text = response.text
        
        print(f"✅ Gemini generated {category_info['title']} prompts: {prompts_text[:100]}...")
        
        # Parse and store
        prompts = self._parse_ai_prompts(prompts_text, count, category, "gemini")
        self._store_generated_prompts(prompts, category)
        
        return prompts

    def _generate_category_prompts_with_openai(self, category: str, category_info: dict, count: int, user_context: str) -> list[dict]:
        """Generate category-specific prompts using OpenAI"""
        print(f"🤖 Using OpenAI for {category_info['title']} category prompts...")
        
        aspects = category_info["aspects"]
        
        system_prompt = f"""Create thoughtful journal prompts for the "{category_info['Title']}" area of life. Generate 9 prompts focused on holistic reflection.

Structure:
1-3: What's going well (celebrating strengths and successes)
4-6: What needs improvement (gentle exploration of challenges)
7-9: Boundaries & commitments (actionable steps and empowerment)

Aspects to consider: {', '.join(aspects)}

Use warm, encouraging language. Maximum 1-2 sentences per prompt."""

        user_prompt = f"""Generate exactly 9 journal prompts for {category_info['title']}.

{f"User context: {user_context}" if user_context else ""}

Focus on aspects: {', '.join(aspects)}

Follow structure: 1-3 celebrate wins, 4-6 explore challenges, 7-9 focus on boundaries/commitments."""

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
        print(f"✅ OpenAI generated {category_info['title']} prompts: {prompts_text[:100]}...")
        
        prompts = self._parse_ai_prompts(prompts_text, count, category, "openai")
        self._store_generated_prompts(prompts, category)
        
        return prompts

    def _generate_category_fallbacks(self, category: str, category_info: dict, count: int) -> list[dict]:
        """Generate intelligent category-specific fallback prompts"""
        print(f"🧠 Using intelligent {category_info['title']} category fallback prompts...")
        
        title = category_info["title"]
        aspects = category_info["aspects"]
        
        # Category-specific prompt templates for each section
        category_templates = {
            "mind": {
                "going_well": [
                    "What mental clarity or insight are you grateful for recently?",
                    "How has your mind served you beautifully this week?",
                    "What positive thought pattern have you cultivated lately?"
                ],
                "needs_improvement": [
                    "What mental habits might be holding you back right now?",
                    "Where could your mind use more rest or clarity?",
                    "What thought patterns no longer serve your highest good?"
                ],
                "boundaries": [
                    "What mental boundaries will protect your peace this week?",
                    "What commitment to your mental wellbeing feels important?",
                    "What will you say 'no' to protect your mental energy?"
                ]
            },
            "body": {
                "going_well": [
                    "How has your body shown strength or resilience lately?",
                    "What physical pleasure or comfort are you grateful for?",
                    "How have you honored your body's needs recently?"
                ],
                "needs_improvement": [
                    "What messages is your body sending that need attention?",
                    "Where could you be more gentle with your physical self?",
                    "What physical habits need more awareness or adjustment?"
                ],
                "boundaries": [
                    "What physical boundaries will honor your body's wisdom?",
                    "What commitment to your body's health feels urgent?",
                    "What will you give your body to show it love?"
                ]
            },
            "heart": {
                "going_well": [
                    "What emotion has brought you joy or comfort lately?",
                    "How has your heart shown its capacity for love?",
                    "What feeling are you most proud of experiencing recently?"
                ],
                "needs_improvement": [
                    "What emotion needs your gentle attention right now?",
                    "Where could you be more compassionate with your feelings?",
                    "What emotional pattern feels ready for healing?"
                ],
                "boundaries": [
                    "What emotional boundaries will protect your heart?",
                    "What commitment to your emotional health matters most?",
                    "What will you allow yourself to feel without judgment?"
                ]
            },
            "friends": {
                "going_well": [
                    "Which friendship has brought you unexpected joy lately?",
                    "How have you shown up beautifully for your friends?",
                    "What social connection fills your heart with gratitude?"
                ],
                "needs_improvement": [
                    "Which friendship needs more attention or honesty?",
                    "Where could you be a better friend to yourself and others?",
                    "What social dynamics feel draining or misaligned?"
                ],
                "boundaries": [
                    "What friendship boundaries need strengthening?",
                    "What commitment to your social life feels important?",
                    "Which connections will you nurture and which will you release?"
                ]
            },
            "family": {
                "going_well": [
                    "What family moment brought you warmth recently?",
                    "How have you grown in your family relationships?",
                    "What family connection feels particularly blessed?"
                ],
                "needs_improvement": [
                    "Which family relationship needs healing or understanding?",
                    "Where could you bring more compassion to family dynamics?",
                    "What family pattern is ready to evolve?"
                ],
                "boundaries": [
                    "What family boundaries will protect your wellbeing?",
                    "What commitment to your family relationships matters?",
                    "What will you give to and what will you withhold in family matters?"
                ]
            },
            "romance": {
                "going_well": [
                    "What romantic moment made your heart flutter recently?",
                    "How have you grown in your capacity for love?",
                    "What aspect of your romantic life feels truly blessed?"
                ],
                "needs_improvement": [
                    "What romantic pattern is ready for conscious evolution?",
                    "Where could you bring more honesty or vulnerability?",
                    "What romantic expectation needs releasing?"
                ],
                "boundaries": [
                    "What romantic boundaries will honor your heart's truth?",
                    "What commitment to your love life feels essential?",
                    "What will you no longer accept in romantic relationships?"
                ]
            },
            "mission": {
                "going_well": [
                    "How have you lived your purpose recently, even in small ways?",
                    "What meaningful impact have you made lately?",
                    "How has your life direction felt aligned and true?"
                ],
                "needs_improvement": [
                    "Where do you feel disconnected from your deeper purpose?",
                    "What fears are blocking your mission or calling?",
                    "How could you bring more meaning to your daily actions?"
                ],
                "boundaries": [
                    "What boundaries will protect your life's mission?",
                    "What commitment to your purpose feels non-negotiable?",
                    "What will you say 'yes' to and 'no' to for your calling?"
                ]
            },
            "growth": {
                "going_well": [
                    "How have you evolved or learned recently?",
                    "What personal breakthrough are you celebrating?",
                    "How have you stretched beyond your comfort zone?"
                ],
                "needs_improvement": [
                    "What area of growth feels stuck or stagnant?",
                    "Where are you resisting necessary change?",
                    "What skill or wisdom feels ready to develop?"
                ],
                "boundaries": [
                    "What boundaries will support your growth journey?",
                    "What commitment to your personal evolution feels urgent?",
                    "What will you invest in and what will you release for growth?"
                ]
            },
            "money": {
                "going_well": [
                    "How has money or abundance flowed beautifully to you?",
                    "What financial choice are you proud of recently?",
                    "How have you honored your relationship with prosperity?"
                ],
                "needs_improvement": [
                    "What money patterns need healing or awareness?",
                    "Where is scarcity thinking limiting your abundance?",
                    "What financial reality needs honest attention?"
                ],
                "boundaries": [
                    "What financial boundaries will honor your worth?",
                    "What commitment to your money health feels essential?",
                    "What will you invest in and what will you save for?"
                ]
            },
            "joy": {
                "going_well": [
                    "What moment of pure delight surprised you recently?",
                    "How have you cultivated more joy in your life?",
                    "What brings a smile to your face just thinking about it?"
                ],
                "needs_improvement": [
                    "Where has joy been absent or suppressed lately?",
                    "What blocks your access to playfulness and delight?",
                    "How could you invite more fun into your days?"
                ],
                "boundaries": [
                    "What boundaries will protect your capacity for joy?",
                    "What commitment to pleasure and play feels important?",
                    "What will you prioritize for your happiness?"
                ]
            }
        }
        
        # Get the templates for this category or use generic ones
        templates = category_templates.get(category, {
            "going_well": [
                f"What's going beautifully well in your {title} life?",
                f"How has {title} brought you blessings recently?",
                f"What aspect of {title} feels truly aligned?"
            ],
            "needs_improvement": [
                f"Where does {title} need more attention or care?",
                f"What challenges in {title} are ready for healing?",
                f"How could {title} serve you better?"
            ],
            "boundaries": [
                f"What boundaries will honor your {title} journey?",
                f"What commitment to {title} feels essential?",
                f"What will you say yes/no to for {title}?"
            ]
        })
        
        prompts = []
        all_templates = templates["going_well"] + templates["needs_improvement"] + templates["boundaries"]
        
        for i in range(min(count, len(all_templates))):
            template = all_templates[i]
            section = "going_well" if i < 3 else "needs_improvement" if i < 6 else "boundaries"
            
            prompts.append({
                "id": i + 1,
                "text": template,
                "category": category,
                "section": section,
                "generated_at": str(uuid.uuid4()),
                "type": "category_fallback"
            })
        
        # Fill remaining if needed
        while len(prompts) < count:
            section_index = len(prompts) % 3
            section = ["going_well", "needs_improvement", "boundaries"][section_index]
            
            generic_template = f"What reflection about {title} feels important to explore?"
            prompts.append({
                "id": len(prompts) + 1,
                "text": generic_template,
                "category": category,
                "section": section,
                "generated_at": str(uuid.uuid4()),
                "type": "category_fallback"
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
                            "application_name": self.application_name
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

    def get_user_guided_journals_count(self, user_id: str) -> int:
        """
        Get ONLY the count of guided journals for a user without fetching full data
        Optimized for stats loading performance
        """
        count = 0
        
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
            
            # Count only the keys that match the pattern
            for item in response.objects:
                if hasattr(item, 'key') and f"journal_" in item.key:
                    # We need to fetch the user_id from the metadata or key
                    # Since we can't get user_id without fetching, we'll try to count
                    # but verify user_id for a sample to ensure accuracy
                    if count == 0:  # Verify first item
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
                            if journal_data.get('user_id') == user_id and journal_data.get('type') == 'guided_journal':
                                count += 1
                            elif not journal_data.get('user_id') == user_id:
                                # Wrong user, this might not be our data
                                break
                        except Exception:
                            continue
                    else:
                        # Assume the rest are for the same user (optimistic counting)
                        count += 1
                        
            print(f"✅ Counted {count} guided journals in guided-journals bucket for user {user_id}")
            
        except Exception as bucket_error:
            print(f"⚠️ guided-journals bucket not available for counting: {bucket_error}")
            print(f"🔄 Checking hints bucket for guided journal count...")
            
            # Fallback to hints bucket counting
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
                        # Verify first item
                        if count == 0:
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
                                if journal_data.get('user_id') == user_id and journal_data.get('type') == 'guided_journal':
                                    count += 1
                            except Exception:
                                continue
                        else:
                            count += 1
                
                print(f"✅ Counted {count} guided journals in hints bucket for user {user_id}")
                
            except Exception as hints_error:
                print(f"❌ Both buckets failed for counting: {hints_error}")
                return 0
        
        return count

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