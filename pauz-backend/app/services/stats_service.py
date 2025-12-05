"""
Optimized Stats Service for Fast Profile Loading
Uses caching and efficient queries to improve performance
"""
import time
from typing import Dict, Optional
from sqlmodel import Session, select, func
from app.models import Garden, FreeJournal, User
from app.services.guided_journal_service import guided_journal_service

class StatsService:
    def __init__(self):
        # Simple in-memory cache (for production, use Redis)
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def _is_cache_valid(self, user_id: str) -> bool:
        """Check if cached data is still valid"""
        if user_id not in self.cache:
            return False
        
        cached_time = self.cache[user_id].get('timestamp', 0)
        return (time.time() - cached_time) < self.cache_ttl
    
    def _update_cache(self, user_id: str, stats: dict):
        """Update cache with fresh data"""
        self.cache[user_id] = {
            'stats': stats,
            'timestamp': time.time()
        }
    
    def _get_guided_journal_count_optimized(self, user_id: str) -> int:
        """Get only the count of guided journals without fetching full data"""
        try:
            print(f"🔍 Getting guided journal COUNT for user: {user_id}")
            
            # Use the new optimized count method
            count = guided_journal_service.get_user_guided_journals_count(user_id)
            print(f"✅ Found {count} guided journals (optimized)")
            return count
            
        except Exception as e:
            print(f"❌ Error getting guided journal count: {e}")
            return 0
    
    def get_user_stats_optimized(self, user_id: str, db: Session) -> Dict:
        """
        Get all user stats in one optimized query with caching
        """
        # Check cache first
        if self._is_cache_valid(user_id):
            print(f"📋 Using cached stats for user: {user_id}")
            return self.cache[user_id]['stats']
        
        print(f"🔄 Computing fresh stats for user: {user_id}")
        start_time = time.time()
        
        # Get all counts in parallel (optimized queries)
        try:
            # Free journals count (fast DB query)
            free_journal_count = db.scalar(
                select(func.count()).where(FreeJournal.user_id == user_id)
            ) or 0
            
            # Garden flowers count (fast DB query)
            garden_count = db.scalar(
                select(func.count()).where(Garden.user_id == user_id)
            ) or 0
            
            # Guided journals count (slow SmartBucket call - needs optimization)
            guided_journal_count = self._get_guided_journal_count_optimized(user_id)
            
            # Calculate total
            total_journals = free_journal_count + guided_journal_count
            
            stats = {
                "total_journals": total_journals,
                "total_free_journals": free_journal_count,
                "total_guided_journals": guided_journal_count,
                "total_flowers": garden_count,
                "user_info": None  # Will be populated by route
            }
            
            # Cache the results
            self._update_cache(user_id, stats)
            
            end_time = time.time()
            print(f"✅ Stats computed in {end_time - start_time:.2f}s for user {user_id}")
            print(f"📊 Results: {stats}")
            
            return stats
            
        except Exception as e:
            print(f"❌ Error computing stats: {e}")
            # Return empty stats on error
            return {
                "total_journals": 0,
                "total_free_journals": 0,
                "total_guided_journals": 0,
                "total_flowers": 0,
                "user_info": None
            }
    
    def invalidate_user_cache(self, user_id: str):
        """Invalidate cache for a specific user (call this when data changes)"""
        if user_id in self.cache:
            del self.cache[user_id]
            print(f"🗑️ Cache invalidated for user: {user_id}")

# Create singleton instance
stats_service = StatsService()