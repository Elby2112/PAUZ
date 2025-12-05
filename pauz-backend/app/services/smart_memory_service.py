"""
SmartMemory Service - AI Caching for PAUZ Hackathon
"""

import os
import json
import time
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class SmartMemoryService:
    """
    SmartMemory Service for AI response caching and user personalization
    Uses in-memory caching with optional persistence
    """
    
    def __init__(self):
        # In-memory cache
        self.cache = {}
        self.cache_timestamps = {}
        self.cache_hit_count = {}
        self.cache_miss_count = 0
        
        # Cache settings
        self.default_ttl = 3600  # 1 hour
        self.ai_response_ttl = 86400  # 24 hours for AI responses
        self.user_preference_ttl = 604800  # 1 week for preferences
        
        print("✅ SmartMemory initialized with in-memory caching")
    
    def _generate_cache_key(self, category: str, identifier: str, params: Optional[Dict] = None) -> str:
        """Generate cache key"""
        key_data = f"{category}:{identifier}"
        if params:
            # Sort params to ensure consistent keys
            sorted_params = json.dumps(params, sort_keys=True)
            key_data += f":{sorted_params}"
        
        # Use hash for consistent length keys
        return hashlib.md5(key_data.encode()).hexdigest()[:16]
    
    def _is_cache_valid(self, key: str, ttl: Optional[int] = None) -> bool:
        """Check if cache entry is still valid"""
        if key not in self.cache_timestamps:
            return False
        
        age = time.time() - self.cache_timestamps[key]
        max_age = ttl or self.default_ttl
        
        return age < max_age
    
    def cache_ai_response(self, prompt_type: str, prompt: str, response: str, 
                         effectiveness_score: float = 0.0, ttl: Optional[int] = None) -> bool:
        """Cache AI response for prompts"""
        
        try:
            cache_key = self._generate_cache_key(
                "ai_response", 
                prompt_type, 
                {"prompt": prompt[:100]}  # First 100 chars for key
            )
            
            cache_data = {
                "response": response,
                "prompt_type": prompt_type,
                "effectiveness_score": effectiveness_score,
                "created_at": datetime.now().isoformat(),
                "prompt": prompt
            }
            
            self.cache[cache_key] = cache_data
            self.cache_timestamps[cache_key] = time.time()
            
            # Initialize hit counter
            if cache_key not in self.cache_hit_count:
                self.cache_hit_count[cache_key] = 0
            
            print(f"✅ Cached AI response for {prompt_type}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to cache AI response: {e}")
            return False
    
    def get_cached_ai_response(self, prompt_type: str, prompt: str) -> Optional[str]:
        """Get cached AI response"""
        
        try:
            cache_key = self._generate_cache_key(
                "ai_response", 
                prompt_type, 
                {"prompt": prompt[:100]}
            )
            
            if not self._is_cache_valid(cache_key, self.ai_response_ttl):
                self.cache_miss_count += 1
                return None
            
            # Update hit count
            self.cache_hit_count[cache_key] = self.cache_hit_count.get(cache_key, 0) + 1
            
            cached_data = self.cache[cache_key]
            print(f"✅ Retrieved cached AI response for {prompt_type} (hit #{self.cache_hit_count[cache_key]})")
            return cached_data["response"]
            
        except Exception as e:
            print(f"❌ Failed to get cached AI response: {e}")
            self.cache_miss_count += 1
            return None
    
    def cache_user_preference(self, user_id: str, preference_type: str, value: Any) -> bool:
        """Cache user preference"""
        
        try:
            cache_key = self._generate_cache_key("user_preference", user_id, {"type": preference_type})
            
            cache_data = {
                "value": value,
                "preference_type": preference_type,
                "user_id": user_id,
                "updated_at": datetime.now().isoformat()
            }
            
            self.cache[cache_key] = cache_data
            self.cache_timestamps[cache_key] = time.time()
            
            print(f"✅ Cached user preference: {preference_type} for {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to cache user preference: {e}")
            return False
    
    def get_user_preference(self, user_id: str, preference_type: str) -> Optional[Any]:
        """Get cached user preference"""
        
        try:
            cache_key = self._generate_cache_key("user_preference", user_id, {"type": preference_type})
            
            if not self._is_cache_valid(cache_key, self.user_preference_ttl):
                return None
            
            cached_data = self.cache[cache_key]
            print(f"✅ Retrieved user preference: {preference_type} for {user_id}")
            return cached_data["value"]
            
        except Exception as e:
            print(f"❌ Failed to get user preference: {e}")
            return None
    
    def cache_personalization_data(self, user_id: str, personalization_data: Dict[str, Any]) -> bool:
        """Cache user personalization data"""
        
        try:
            cache_key = self._generate_cache_key("personalization", user_id)
            
            cache_data = {
                "user_id": user_id,
                "data": personalization_data,
                "updated_at": datetime.now().isoformat()
            }
            
            self.cache[cache_key] = cache_data
            self.cache_timestamps[cache_key] = time.time()
            
            print(f"✅ Cached personalization data for {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to cache personalization data: {e}")
            return False
    
    def get_personalization_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached personalization data"""
        
        try:
            cache_key = self._generate_cache_key("personalization", user_id)
            
            if not self._is_cache_valid(cache_key, self.user_preference_ttl):
                return None
            
            cached_data = self.cache[cache_key]
            print(f"✅ Retrieved personalization data for {user_id}")
            return cached_data["data"]
            
        except Exception as e:
            print(f"❌ Failed to get personalization data: {e}")
            return None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        
        total_hits = sum(self.cache_hit_count.values())
        total_requests = total_hits + self.cache_miss_count
        hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
        
        # Cache size analysis
        cache_size = len(self.cache)
        total_memory_usage = len(json.dumps(self.cache))
        
        # Most popular cache keys
        popular_keys = sorted(
            self.cache_hit_count.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        return {
            "total_cache_entries": cache_size,
            "total_memory_bytes": total_memory_usage,
            "cache_hits": total_hits,
            "cache_misses": self.cache_miss_count,
            "hit_rate_percent": round(hit_rate, 2),
            "popular_keys": popular_keys,
            "cache_categories": self._analyze_cache_categories()
        }
    
    def _analyze_cache_categories(self) -> Dict[str, int]:
        """Analyze cache by categories"""
        
        categories = {"ai_response": 0, "user_preference": 0, "personalization": 0}
        
        for key in self.cache:
            if "ai_response" in key:
                categories["ai_response"] += 1
            elif "user_preference" in key:
                categories["user_preference"] += 1
            elif "personalization" in key:
                categories["personalization"] += 1
        
        return categories
    
    def clear_expired_cache(self) -> int:
        """Clear expired cache entries"""
        
        current_time = time.time()
        expired_keys = []
        
        for key, timestamp in self.cache_timestamps.items():
            if current_time - timestamp > self.default_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
            del self.cache_timestamps[key]
            if key in self.cache_hit_count:
                del self.cache_hit_count[key]
        
        print(f"🧹 Cleared {len(expired_keys)} expired cache entries")
        return len(expired_keys)
    
    def clear_user_cache(self, user_id: str) -> int:
        """Clear all cache entries for a specific user"""
        
        user_keys = []
        for key in self.cache:
            if user_id in key or (self.cache[key].get("user_id") == user_id):
                user_keys.append(key)
        
        for key in user_keys:
            del self.cache[key]
            if key in self.cache_timestamps:
                del self.cache_timestamps[key]
            if key in self.cache_hit_count:
                del self.cache_hit_count[key]
        
        print(f"🧹 Cleared {len(user_keys)} cache entries for user {user_id}")
        return len(user_keys)

# Global instance
smart_memory_service = SmartMemoryService()