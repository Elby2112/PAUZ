"""
Optimized Journal Loading Service
Provides fast journal listing with previews and caching
"""
import time
from typing import List, Dict, Optional
from sqlmodel import Session, select, func
from datetime import datetime
from app.models import FreeJournal
from app.services.guided_journal_service import guided_journal_service

class JournalLoadingService:
    def __init__(self):
        # Cache for journal listings (5 minute TTL like stats)
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def _is_cache_valid(self, user_id: str, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        full_key = f"{user_id}:{cache_key}"
        if full_key not in self.cache:
            return False
        
        cached_time = self.cache[full_key].get('timestamp', 0)
        return (time.time() - cached_time) < self.cache_ttl
    
    def _update_cache(self, user_id: str, cache_key: str, data: any):
        """Update cache with fresh data"""
        full_key = f"{user_id}:{cache_key}"
        self.cache[full_key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def get_user_guided_journals_preview(self, user_id: str) -> List[Dict]:
        """
        Get lightweight preview of guided journals (no full content)
        Optimized for list view performance
        """
        cache_key = "guided_journals_preview"
        
        # Check cache first
        if self._is_cache_valid(user_id, cache_key):
            print(f"📋 Using cached guided journal preview for user: {user_id}")
            return self.cache[f"{user_id}:{cache_key}"]['data']
        
        print(f"🔄 Computing guided journal preview for user: {user_id}")
        start_time = time.time()
        
        try:
            # Get full journals (we have to for now due to SmartBucket limitations)
            guided_journals = guided_journal_service.get_user_guided_journals(user_id)
            
            # Create lightweight preview versions
            previews = []
            for journal in guided_journals:
                preview = {
                    "id": journal.get("id"),
                    "topic": journal.get("topic"),
                    "created_at": journal.get("created_at"),
                    "entry_count": len(journal.get("entries", [])),
                    "prompt_count": len(journal.get("prompts", [])),
                    # Only include first entry preview, not full content
                    "has_content": len(journal.get("entries", [])) > 0,
                    "preview_text": self._get_journal_preview(journal)
                }
                previews.append(preview)
            
            # Sort by created_at descending
            previews.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            # Cache the results
            self._update_cache(user_id, cache_key, previews)
            
            end_time = time.time()
            print(f"✅ Guided journal preview computed in {end_time - start_time:.3f}s")
            
            return previews
            
        except Exception as e:
            print(f"❌ Error getting guided journal preview: {e}")
            return []
    
    def _get_journal_preview(self, journal: Dict) -> str:
        """Generate a short preview of journal content"""
        entries = journal.get("entries", [])
        if not entries:
            return "No entries yet"
        
        # Get first entry and truncate
        first_entry = entries[0].get("response", "")
        if len(first_entry) > 100:
            return first_entry[:100] + "..."
        return first_entry
    
    def get_user_free_journals_preview(self, user_id: str, db: Session, 
                                     start_date: Optional[str] = None,
                                     end_date: Optional[str] = None,
                                     search: Optional[str] = None,
                                     limit: Optional[int] = None,
                                     sort_by: str = "created_at",
                                     order: str = "desc") -> List[Dict]:
        """
        Get lightweight preview of free journals (no full content)
        Optimized for list view performance
        """
        # Create cache key based on filters
        cache_parts = [f"free_journals_preview"]
        if start_date:
            cache_parts.append(f"from_{start_date}")
        if end_date:
            cache_parts.append(f"to_{end_date}")
        if search:
            cache_parts.append(f"search_{search[:20]}")
        if limit:
            cache_parts.append(f"limit_{limit}")
        cache_parts.append(f"sort_{sort_by}_{order}")
        cache_key = "_".join(cache_parts)
        
        # Check cache first
        if self._is_cache_valid(user_id, cache_key):
            print(f"📋 Using cached free journal preview for user: {user_id}")
            return self.cache[f"{user_id}:{cache_key}"]['data']
        
        print(f"🔄 Computing free journal preview for user: {user_id}")
        start_time = time.time()
        
        try:
            # Build optimized query - only select needed columns
            query = select(
                FreeJournal.id,
                FreeJournal.session_id,
                FreeJournal.created_at,
                FreeJournal.updated_at,
                # Only get first 100 characters of content for preview
                func.substring(FreeJournal.content, 1, 100).label("content_preview")
            ).where(
                FreeJournal.user_id == user_id
            )
            
            # Date filtering
            if start_date:
                try:
                    start_dt = datetime.fromisoformat(start_date)
                    query = query.where(FreeJournal.created_at >= start_dt)
                except ValueError:
                    pass
            
            if end_date:
                try:
                    end_dt = datetime.fromisoformat(end_date)
                    query = query.where(FreeJournal.created_at <= end_dt)
                except ValueError:
                    pass
            
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
            
            # Execute query
            results = db.exec(query).all()
            
            # Convert to list of dicts
            previews = []
            for result in results:
                content_preview = result.content_preview or ""
                if len(content_preview) == 100:  # Likely truncated
                    content_preview += "..."
                
                preview = {
                    "id": result.id,
                    "session_id": result.session_id,
                    "created_at": result.created_at,
                    "updated_at": result.updated_at,
                    "content_preview": content_preview,
                    "word_count": len(content_preview.split()) if content_preview else 0
                }
                previews.append(preview)
            
            # Cache the results
            self._update_cache(user_id, cache_key, previews)
            
            end_time = time.time()
            print(f"✅ Free journal preview computed in {end_time - start_time:.3f}s")
            
            return previews
            
        except Exception as e:
            print(f"❌ Error getting free journal preview: {e}")
            return []
    
    def invalidate_user_cache(self, user_id: str):
        """Invalidate all cache for a specific user"""
        keys_to_remove = []
        for key in self.cache.keys():
            if key.startswith(f"{user_id}:"):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.cache[key]
        
        print(f"🗑️ Invalidated {len(keys_to_remove)} journal cache entries for user: {user_id}")

# Create singleton instance
journal_loading_service = JournalLoadingService()