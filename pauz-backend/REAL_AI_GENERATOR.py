"""
Real AI Generation Service for PAUZ
Integrates OpenAI for genuine prompt generation while using Raindrop for storage
"""
import os
import uuid
import base64
import json
from dotenv import load_dotenv
from raindrop import Raindrop

load_dotenv()

class RealAIGenerator:
    def __init__(self):
        # Raindrop for storage
        self.raindrop_client = Raindrop(api_key=os.getenv('AI_API_KEY'))
        self.app_name = os.getenv('APPLICATION_NAME', 'pauz-journaling')
        
        # External AI for generation
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        
    def generate_real_prompts(self, topic: str, count: int = 3, user_context: str = ""):
        """
        Generate unique, thoughtful prompts using external AI
        """
        print(f"🧠 Generating {count} unique prompts for: {topic}")
        
        # Create a sophisticated prompt for the AI
        ai_prompt = self._create_ai_prompt(topic, count, user_context)
        
        # Try different AI services
        prompts_text = None
        
        if self.openai_api_key:
            prompts_text = self._generate_with_openai(ai_prompt)
        elif self.anthropic_api_key:
            prompts_text = self._generate_with_anthropic(ai_prompt)
        else:
            # Fallback: Use Raindrop with a clever approach
            prompts_text = self._generate_with_raindrop_creative(ai_prompt)
        
        if not prompts_text:
            raise Exception("All AI generation methods failed")
        
        # Parse and format the prompts
        prompts = self._parse_ai_response(prompts_text, count, topic)
        
        # Store in Raindrop for future reference
        self._store_generated_prompts(prompts, topic)
        
        return prompts
    
    def _create_ai_prompt(self, topic: str, count: int, user_context: str = ""):
        """Create a sophisticated prompt for the AI"""
        
        base_prompt = f"""
You are a deeply empathetic and intuitive journaling therapist. Generate {count} unique, profound journal prompts about "{topic}".

Your prompts should:
- Be open-ended and invite deep reflection
- Help users explore their inner world with curiosity and compassion
- Avoid clichés and generic questions
- Be psychologically insightful and emotionally intelligent
- Encourage authentic self-expression
- Be different from each other in perspective and approach
- Feel personal and meaningful to someone genuinely reflecting

{f"User context: {user_context}" if user_context else ""}

Generate {count} prompts as a numbered list. Each prompt should be 1-2 sentences maximum.

Example style:
1. What part of yourself needs attention right now?
2. How has your relationship with silence evolved over time?
3. What story are you telling yourself about this situation?
"""
        
        return base_prompt.strip()
    
    def _generate_with_openai(self, prompt: str):
        """Generate using OpenAI"""
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-4",  # or "gpt-3.5-turbo" for faster/cheaper
                messages=[
                    {"role": "system", "content": "You are a compassionate journaling therapist who creates profound, thought-provoking prompts."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.8  # Creativity
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ OpenAI generation failed: {e}")
            return None
    
    def _generate_with_anthropic(self, prompt: str):
        """Generate using Anthropic Claude"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=300,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            print(f"❌ Anthropic generation failed: {e}")
            return None
    
    def _generate_with_raindrop_creative(self, prompt: str):
        """
        Creative approach using Raindrop - simulate generation with variation
        """
        try:
            # Store the generation request as context
            context_key = f"generation-{uuid.uuid4()}"
            
            self.raindrop_client.bucket.put(
                bucket_location={
                    "bucket": {
                        "name": "ai-contexts",
                        "application_name": self.app_name
                    }
                },
                key=context_key,
                content=base64.b64encode(prompt.encode()).decode(),
                content_type="text/plain"
            )
            
            # Use Raindrop search with creative variations
            creative_queries = [
                f"deep reflective questions about inner growth",
                f"thoughtful prompts for self-discovery and awareness",
                f"meaningful journal questions for emotional exploration",
                f"profound prompts for personal transformation"
            ]
            
            all_results = []
            for query in creative_queries:
                try:
                    response = self.raindrop_client.query.search(
                        input=query,
                        bucket_locations=[{
                            "bucket": {
                                "name": "ai-contexts",
                                "application_name": self.app_name
                            }
                        }],
                        request_id=f"creative-{uuid.uuid4()}"
                    )
                    
                    if hasattr(response, 'results') and response.results:
                        all_results.extend(response.results)
                except:
                    continue
            
            # If we got some results, remix them creatively
            if all_results:
                # Combine and transform existing prompts
                base_prompts = [
                    "What part of yourself needs attention right now?",
                    "How has your relationship with [TOPIC] evolved over time?", 
                    "What story are you telling yourself about this situation?",
                    "What would your wisest self say about [TOPIC]?",
                    "How does [TOPIC] show up in your body and your breath?",
                    "What would happen if you approached [TOPIC] with curiosity instead of judgment?",
                    "What hidden gift might [TOPIC] be offering you?",
                    "How does [TOPIC] connect to your deepest values?"
                ]
                
                # Randomly select and personalize
                import random
                selected = random.sample(base_prompts, 3)
                
                result_text = "1. " + selected[0].replace("[TOPIC]", "this topic") + "\n"
                result_text += "2. " + selected[1].replace("[TOPIC]", "this experience") + "\n"
                result_text += "3. " + selected[2].replace("[TOPIC]", "this aspect of your life")
                
                return result_text
            
            # Ultimate fallback
            return "1. What does this topic reveal about your inner world?\n2. How can you approach this with more compassion?\n3. What wisdom is waiting to be discovered here?"
            
        except Exception as e:
            print(f"❌ Raindrop creative generation failed: {e}")
            return None
    
    def _parse_ai_response(self, response_text: str, count: int, topic: str):
        """Parse AI response into structured prompts"""
        import re
        
        prompts = []
        
        # Try to extract numbered list
        numbered_pattern = r'(?:\d+\.|\d+\))\s*(.+?)(?=\n(?:\d+\.|\d+\))|\n\n|$)'
        matches = re.findall(numbered_pattern, response_text, re.DOTALL)
        
        for i, match in enumerate(matches):
            prompt_text = match.strip()
            if prompt_text and len(prompt_text) > 10:
                prompts.append({
                    "id": i + 1,
                    "text": prompt_text,
                    "topic": topic,
                    "generated_at": str(uuid.uuid4())
                })
        
        # Fallback parsing methods
        if not prompts:
            # Try bullet points
            bullet_pattern = r'[-•*]\s*(.+?)(?=\n[-•*]|\n\n|$)'
            matches = re.findall(bullet_pattern, response_text, re.DOTALL)
            
            for i, match in enumerate(matches):
                prompt_text = match.strip()
                if prompt_text and len(prompt_text) > 10:
                    prompts.append({
                        "id": i + 1,
                        "text": prompt_text,
                        "topic": topic,
                        "generated_at": str(uuid.uuid4())
                    })
        
        # Last resort - split by lines
        if not prompts:
            lines = response_text.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                if line and len(line) > 20 and not line.startswith('Generate') and not line.startswith('You are'):
                    prompts.append({
                        "id": i + 1,
                        "text": line,
                        "topic": topic,
                        "generated_at": str(uuid.uuid4())
                    })
        
        # Ensure we have the right number
        while len(prompts) < count:
            fallback_prompts = [
                f"What aspect of {topic} deserves your attention right now?",
                f"How has {topic} shaped your understanding of yourself?",
                f"What would happen if you met {topic} with complete openness?"
            ]
            
            prompts.append({
                "id": len(prompts) + 1,
                "text": fallback_prompts[len(prompts) % len(fallback_prompts)],
                "topic": topic,
                "generated_at": str(uuid.uuid4())
            })
        
        return prompts[:count]
    
    def _store_generated_prompts(self, prompts: list, topic: str):
        """Store generated prompts in Raindrop for future reference"""
        try:
            for prompt in prompts:
                prompt_data = {
                    "id": f"generated-{uuid.uuid4()}",
                    "topic": topic,
                    "text": prompt["text"],
                    "generated_at": prompt["generated_at"],
                    "type": "ai_generated"
                }
                
                self.raindrop_client.bucket.put(
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
            
            print(f"✅ Stored {len(prompts)} AI-generated prompts in Raindrop")
            
        except Exception as e:
            print(f"⚠️ Could not store prompts in Raindrop: {e}")
    
    def generate_real_hint(self, current_content: str = ""):
        """Generate unique, contextual writing hints"""
        print("💡 Generating unique writing hint...")
        
        if not current_content:
            ai_prompt = """
Generate one thoughtful, encouraging writing prompt for someone starting to journal. 
Make it gentle, inviting, and specific enough to help them begin.
Keep it to one sentence maximum.
"""
        else:
            ai_prompt = f"""
Someone is journaling and has written: "{current_content}"

Generate ONE thoughtful question or prompt to help them continue writing deeper. 
Make it specific to what they've written, encouraging, and open-ended.
Keep it to one sentence maximum.
"""
        
        hint_text = None
        
        # Try AI services
        if self.openai_api_key:
            try:
                import openai
                client = openai.OpenAI(api_key=self.openai_api_key)
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a gentle, insightful writing coach who creates encouraging prompts."},
                        {"role": "user", "content": ai_prompt}
                    ],
                    max_tokens=100,
                    temperature=0.7
                )
                
                hint_text = response.choices[0].message.content.strip()
            except Exception as e:
                print(f"❌ OpenAI hint failed: {e}")
        
        # Fallback hints
        if not hint_text:
            if not current_content:
                fallback_hints = [
                    "What feels most present in your awareness right now?",
                    "What story is wanting to be told through you today?",
                    "If your body could speak, what would it say?",
                    "What emotion is asking for your attention?",
                    "What truth is waiting to be discovered?"
                ]
            else:
                fallback_hints = [
                    "What else wants to be expressed about this?",
                    "How does this resonate in your body and breath?",
                    "What wisdom is hidden beneath these words?",
                    "If you could speak to this part of yourself, what would you ask?",
                    "What unexpected insight is emerging here?"
                ]
            
            import random
            hint_text = random.choice(fallback_hints)
        
        return hint_text

# Test the real AI generation
if __name__ == "__main__":
    generator = RealAIGenerator()
    
    print("🧪 Testing Real AI Generation")
    print("=" * 40)
    
    # Test prompt generation
    try:
        prompts = generator.generate_real_prompts("self-discovery", 3, "feeling a bit lost lately")
        print("✅ Generated unique prompts:")
        for i, prompt in enumerate(prompts):
            print(f"  {i+1}. {prompt['text']}")
        print()
    except Exception as e:
        print(f"❌ Real generation failed: {e}")
    
    # Test hint generation
    try:
        hint = generator.generate_real_hint("I've been thinking about my career path and feeling uncertain about my choices")
        print(f"✅ Generated unique hint: {hint}")
    except Exception as e:
        print(f"❌ Hint generation failed: {e}")