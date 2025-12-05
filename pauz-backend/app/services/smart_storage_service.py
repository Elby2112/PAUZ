"""
SmartStorage Service - Organized Storage for PAUZ Hackathon
Uses existing working bucket with organized key structure
"""

import os
import base64
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class SmartStorageService:
    """
    SmartStorage Service for organized data management
    Uses journal-prompts bucket with organized key structure
    """
    
    def __init__(self):
        # Initialize Raindrop client
        try:
            from raindrop import Raindrop
            api_key = os.getenv('AI_API_KEY')
            app_name = os.getenv('APPLICATION_NAME')
            
            if not api_key or not app_name:
                raise ValueError("Missing AI_API_KEY or APPLICATION_NAME")
            
            self.client = Raindrop(api_key=api_key)
            self.bucket_name = "journal-prompts"  # Working bucket
            self.app_name = app_name
            
            print(f"✅ SmartStorage initialized with bucket: {self.bucket_name}")
            
        except ImportError:
            print("❌ Raindrop library not available")
            self.client = None
        except Exception as e:
            print(f"❌ SmartStorage initialization failed: {e}")
            self.client = None
    
    def _make_key(self, category: str, user_id: str, identifier: str) -> str:
        """Create organized key structure"""
        return f"{category}/{user_id}/{identifier}"
    
    def store_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Store user profile data"""
        if not self.client:
            return False
        
        try:
            key = self._make_key("user-profiles", user_id, "profile")
            content = json.dumps(profile_data, default=str)
            encoded_content = base64.b64encode(content.encode()).decode('utf-8')
            
            self.client.bucket.put(
                bucket_location={
                    "bucket": {
                        "name": self.bucket_name,
                        "application_name": self.app_name
                    }
                },
                key=key,
                content=encoded_content,
                content_type="application/json"
            )
            print(f"✅ Stored user profile for {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to store user profile: {e}")
            return False
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile data"""
        if not self.client:
            return None
        
        try:
            key = self._make_key("user-profiles", user_id, "profile")
            
            response = self.client.bucket.get(
                bucket_location={
                    "bucket": {
                        "name": self.bucket_name,
                        "application_name": self.app_name
                    }
                },
                key=key
            )
            
            # Handle response properly - it might be bytes or a response object
            if hasattr(response, 'content'):
                content_bytes = response.content
            else:
                content_bytes = response
            
            decoded_content = base64.b64decode(content_bytes).decode('utf-8')
            profile_data = json.loads(decoded_content)
            return profile_data
            
        except Exception as e:
            print(f"❌ Failed to get user profile: {e}")
            return None
    
    def store_free_journal(self, user_id: str, session_id: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """Store free journal entry"""
        if not self.client:
            return False
        
        try:
            journal_data = {
                "content": content,
                "created_at": datetime.now().isoformat(),
                "session_id": session_id,
                "metadata": metadata or {}
            }
            
            key = self._make_key("free-journals", user_id, session_id)
            content_json = json.dumps(journal_data, default=str)
            encoded_content = base64.b64encode(content_json.encode()).decode('utf-8')
            
            self.client.bucket.put(
                bucket_location={
                    "bucket": {
                        "name": self.bucket_name,
                        "application_name": self.app_name
                    }
                },
                key=key,
                content=encoded_content,
                content_type="application/json"
            )
            print(f"✅ Stored free journal for {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to store free journal: {e}")
            return False
    
    def store_voice_recording(self, user_id: str, session_id: str, audio_data: bytes) -> bool:
        """Store voice recording"""
        if not self.client:
            return False
        
        try:
            key = self._make_key("voice-recordings", user_id, session_id)
            encoded_audio = base64.b64encode(audio_data).decode('utf-8')
            
            self.client.bucket.put(
                bucket_location={
                    "bucket": {
                        "name": self.bucket_name,
                        "application_name": self.app_name
                    }
                },
                key=key,
                content=encoded_audio,
                content_type="audio/wav"
            )
            print(f"✅ Stored voice recording for {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to store voice recording: {e}")
            return False
    
    def store_guided_journal(self, user_id: str, journal_id: str, journal_data: Dict[str, Any]) -> bool:
        """Store guided journal session"""
        if not self.client:
            return False
        
        try:
            journal_data["updated_at"] = datetime.now().isoformat()
            
            key = self._make_key("guided-journals", user_id, journal_id)
            content_json = json.dumps(journal_data, default=str)
            encoded_content = base64.b64encode(content_json.encode()).decode('utf-8')
            
            self.client.bucket.put(
                bucket_location={
                    "bucket": {
                        "name": self.bucket_name,
                        "application_name": self.app_name
                    }
                },
                key=key,
                content=encoded_content,
                content_type="application/json"
            )
            print(f"✅ Stored guided journal for {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to store guided journal: {e}")
            return False
    
    def store_ai_prompt(self, user_id: str, prompt_type: str, prompt_data: Dict[str, Any]) -> bool:
        """Store AI-generated prompt"""
        if not self.client:
            return False
        
        try:
            prompt_data["generated_at"] = datetime.now().isoformat()
            
            key = self._make_key("ai-prompts", user_id, f"{prompt_type}_{datetime.now().timestamp()}")
            content_json = json.dumps(prompt_data, default=str)
            encoded_content = base64.b64encode(content_json.encode()).decode('utf-8')
            
            self.client.bucket.put(
                bucket_location={
                    "bucket": {
                        "name": self.bucket_name,
                        "application_name": self.app_name
                    }
                },
                key=key,
                content=encoded_content,
                content_type="application/json"
            )
            print(f"✅ Stored AI prompt for {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to store AI prompt: {e}")
            return False
    
    def store_garden_data(self, user_id: str, garden_data: Dict[str, Any]) -> bool:
        """Store garden visualization data"""
        if not self.client:
            return False
        
        try:
            garden_data["updated_at"] = datetime.now().isoformat()
            
            key = self._make_key("garden-system", user_id, "current_garden")
            content_json = json.dumps(garden_data, default=str)
            encoded_content = base64.b64encode(content_json.encode()).decode('utf-8')
            
            self.client.bucket.put(
                bucket_location={
                    "bucket": {
                        "name": self.bucket_name,
                        "application_name": self.app_name
                    }
                },
                key=key,
                content=encoded_content,
                content_type="application/json"
            )
            print(f"✅ Stored garden data for {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to store garden data: {e}")
            return False
    
    def store_user_analytics(self, user_id: str, analytics_data: Dict[str, Any]) -> bool:
        """Store user analytics data"""
        if not self.client:
            return False
        
        try:
            analytics_data["recorded_at"] = datetime.now().isoformat()
            
            key = self._make_key("user-analytics", user_id, f"daily_{datetime.now().strftime('%Y_%m_%d')}")
            content_json = json.dumps(analytics_data, default=str)
            encoded_content = base64.b64encode(content_json.encode()).decode('utf-8')
            
            self.client.bucket.put(
                bucket_location={
                    "bucket": {
                        "name": self.bucket_name,
                        "application_name": self.app_name
                    }
                },
                key=key,
                content=encoded_content,
                content_type="application/json"
            )
            print(f"✅ Stored analytics for {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to store analytics: {e}")
            return False
    
    def list_user_data(self, user_id: str, category: str) -> List[Dict[str, Any]]:
        """List all data for a user in a category"""
        # This is a simplified version - in production you'd use bucket list
        print(f"📋 Listing {category} for user {user_id}")
        return []

# Global instance
smart_storage_service = SmartStorageService()