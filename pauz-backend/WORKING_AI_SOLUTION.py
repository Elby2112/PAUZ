#!/usr/bin/env python3
"""
Working Raindrop AI solution for PAUZ Journaling App
This demonstrates the correct approach to use Raindrop AI for your app
"""
import os
import base64
import uuid
from dotenv import load_dotenv
from raindrop import Raindrop

load_dotenv()

class PauzAIService:
    def __init__(self):
        self.client = Raindrop(api_key=os.getenv('AI_API_KEY'))
        self.app_name = os.getenv('APPLICATION_NAME', 'pauz-journaling')
        self.org_name = os.getenv('RAINDROP_ORG', 'Loubna-HackathonApp')
    
    def generate_prompts(self, topic: str, count: int = 3):
        """
        Generate AI-powered journal prompts using Raindrop
        """
        print(f"🤖 Generating {count} prompts for topic: {topic}")
        
        # Create a context document that will help the AI understand the task
        context_key = f"prompt-generator-{uuid.uuid4()}"
        context_content = f"""
You are a creative journaling assistant. Your task is to generate {count} unique, thought-provoking journal prompts about {topic}.

Requirements:
- Each prompt should be open-ended
- Prompts should encourage personal reflection
- Make them engaging and meaningful
- Return as a numbered list
- Be creative and avoid clichés

Topic: {topic}
Number of prompts: {count}
"""
        
        try:
            # Store the context
            self.client.bucket.put(
                bucket_location={
                    "bucket": {
                        "name": "journal-prompts",
                        "application_name": self.app_name
                    }
                },
                key=context_key,
                content=base64.b64encode(context_content.encode()).decode(),
                content_type="text/plain"
            )
            
            # Wait a moment for indexing
            import time
            time.sleep(1)
            
            # Use search with a specific query that will trigger generation
            response = self.client.query.search(
                input=f"Generate {count} unique journal prompts about {topic}. Return as a numbered list.",
                bucket_locations=[{
                    "bucket": {
                        "name": "journal-prompts",
                        "application_name": self.app_name
                    }
                }],
                request_id=f"generate-{uuid.uuid4()}"
            )
            
            # Extract and parse the response
            if hasattr(response, 'results') and response.results:
                # Use the best result (highest score)
                best_result = max(response.results, key=lambda x: x.score if hasattr(x, 'score') else 0)
                prompts_text = best_result.text
                
                # Parse the prompts
                prompts = self._parse_prompts_from_text(prompts_text, count, topic)
                return prompts
            else:
                raise Exception("No results from AI")
                
        except Exception as e:
            print(f"❌ Error generating prompts: {e}")
            raise e
    
    def _parse_prompts_from_text(self, text: str, count: int, topic: str):
        """Parse prompts from AI response text"""
        import re
        
        # Try to extract numbered list items
        pattern = r'(?:\d+\.\s*|[\-\*]\s*)(.+?)(?=\n(?:\d+\.|[\-\*])|\n\n|$)'
        matches = re.findall(pattern, text, re.DOTALL)
        
        prompts = []
        for match in matches:
            prompt = match.strip()
            if prompt and len(prompt) > 10:  # Filter out short/empty results
                prompts.append(prompt)
        
        # If no numbered list found, try other patterns
        if not prompts:
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if line and len(line) > 20 and not line.startswith('Generate'):
                    # Remove any numbering/bullets
                    clean_line = re.sub(r'^\d+[\.\)]\s*|^[\-\*]\s*', '', line).strip()
                    if clean_line:
                        prompts.append(clean_line)
        
        # Ensure we have the right number
        num_prompts = min(count, max(len(prompts), count))
        return [{"id": i + 1, "text": prompts[i] if i < len(prompts) else f"Journal about {topic}"} for i in range(num_prompts)]
    
    def generate_hint(self, current_content: str = ""):
        """Generate AI-powered writing hints"""
        print("💡 Generating writing hint...")
        
        context_key = f"hint-generator-{uuid.uuid4()}"
        prompt_text = current_content if current_content else "Generate a creative journal prompt to get started"
        
        context_content = f"""
You are a helpful writing assistant. Based on the user's current journal entry, provide an engaging question or prompt to help them continue writing.

Current content: "{prompt_text}"

Generate a thoughtful, open-ended question that will inspire deeper reflection.
"""
        
        try:
            # Store context
            self.client.bucket.put(
                bucket_location={
                    "bucket": {
                        "name": "hints",
                        "application_name": self.app_name
                    }
                },
                key=context_key,
                content=base64.b64encode(context_content.encode()).decode(),
                content_type="text/plain"
            )
            
            import time
            time.sleep(1)
            
            # Search for hint
            response = self.client.query.search(
                input="Provide a helpful writing hint or question",
                bucket_locations=[{
                    "bucket": {
                        "name": "hints",
                        "application_name": self.app_name
                    }
                }],
                request_id=f"hint-{uuid.uuid4()}"
            )
            
            if hasattr(response, 'results') and response.results:
                best_result = max(response.results, key=lambda x: x.score if hasattr(x, 'score') else 0)
                return best_result.text
            else:
                return "What else would you like to explore about this topic?"
                
        except Exception as e:
            print(f"❌ Error generating hint: {e}")
            return "Can you tell me more about how this makes you feel?"

# Test the solution
if __name__ == "__main__":
    ai_service = PauzAIService()
    
    print("🧪 Testing PAUZ AI Solution")
    print("=" * 40)
    
    # Test prompt generation
    try:
        prompts = ai_service.generate_prompts("mindfulness", 3)
        print(f"✅ Generated {len(prompts)} prompts:")
        for i, prompt in enumerate(prompts):
            print(f"  {i+1}. {prompt['text']}")
        print()
    except Exception as e:
        print(f"❌ Prompt generation failed: {e}")
    
    # Test hint generation
    try:
        hint = ai_service.generate_hint("I'm feeling stressed about work today")
        print(f"✅ Generated hint: {hint}")
    except Exception as e:
        print(f"❌ Hint generation failed: {e}")
    
    print("\n🎉 AI Solution Test Complete!")