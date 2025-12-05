"""
SmartSQL Service - User Analytics for PAUZ Hackathon
"""

import os
import sqlite3
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv()

class SmartSQLService:
    """
    SmartSQL Service for user analytics and metadata
    Uses SQLite for hackathon (can be upgraded to distributed SQL later)
    """
    
    def __init__(self):
        self.db_path = "smart_analytics.db"
        self.init_database()
        print(f"✅ SmartSQL initialized: {self.db_path}")
    
    def init_database(self):
        """Initialize analytics database with tables"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                preferences TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Journal metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS journal_metadata (
                entry_id TEXT PRIMARY KEY,
                user_id TEXT,
                journal_type TEXT,  -- 'free' or 'guided'
                session_id TEXT,
                word_count INTEGER,
                has_audio BOOLEAN DEFAULT FALSE,
                mood_score TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                date DATE,
                journals_written INTEGER DEFAULT 0,
                total_words INTEGER DEFAULT 0,
                voice_sessions INTEGER DEFAULT 0,
                dominant_mood TEXT,
                session_time_minutes INTEGER DEFAULT 0,
                storage_used_bytes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, date)
            )
        ''')
        
        # AI performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT,
                prompt_type TEXT,
                success_rate REAL DEFAULT 0.0,
                response_time_ms INTEGER DEFAULT 0,
                user_satisfaction INTEGER DEFAULT 0,
                date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Daily summary table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_summary (
                date DATE PRIMARY KEY,
                total_users INTEGER DEFAULT 0,
                total_journals INTEGER DEFAULT 0,
                total_words INTEGER DEFAULT 0,
                total_voice_sessions INTEGER DEFAULT 0,
                avg_session_time REAL DEFAULT 0.0,
                most_common_mood TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def upsert_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Insert or update user profile"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_profiles 
                (user_id, name, email, preferences, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                user_id,
                profile_data.get('name'),
                profile_data.get('email'),
                profile_data.get('preferences', '{}') if isinstance(profile_data.get('preferences'), str) else json.dumps(profile_data.get('preferences', {}))
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Failed to upsert user profile: {e}")
            return False
    
    def record_journal_entry(self, user_id: str, entry_id: str, journal_type: str, 
                           session_id: str, content: str, has_audio: bool = False, 
                           mood_score: Optional[Dict] = None) -> bool:
        """Record journal entry metadata"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            word_count = len(content.split()) if content else 0
            mood_json = json.dumps(mood_score) if mood_score else None
            
            cursor.execute('''
                INSERT OR REPLACE INTO journal_metadata 
                (entry_id, user_id, journal_type, session_id, word_count, has_audio, mood_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (entry_id, user_id, journal_type, session_id, word_count, has_audio, mood_json))
            
            conn.commit()
            conn.close()
            
            # Update user analytics
            self.update_user_analytics(user_id, word_count, has_audio)
            return True
            
        except Exception as e:
            print(f"❌ Failed to record journal entry: {e}")
            return False
    
    def update_user_analytics(self, user_id: str, word_count: int = 0, 
                           has_voice: bool = False, session_minutes: int = 0,
                           mood: Optional[str] = None, storage_bytes: int = 0) -> bool:
        """Update user daily analytics"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = date.today()
            
            # Check if analytics exist for today
            cursor.execute('''
                SELECT journals_written, total_words, voice_sessions, session_time_minutes, storage_used_bytes
                FROM user_analytics 
                WHERE user_id = ? AND date = ?
            ''', (user_id, today))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                journals, words, voices, minutes, storage = existing
                cursor.execute('''
                    UPDATE user_analytics 
                    SET journals_written = journals_written + 1,
                        total_words = total_words + ?,
                        voice_sessions = voice_sessions + ?,
                        session_time_minutes = session_time_minutes + ?,
                        storage_used_bytes = storage_used_bytes + ?,
                        dominant_mood = COALESCE(?, dominant_mood)
                    WHERE user_id = ? AND date = ?
                ''', (word_count, 1 if has_voice else 0, session_minutes, storage_bytes, mood, user_id, today))
            else:
                # Insert new record
                cursor.execute('''
                    INSERT INTO user_analytics 
                    (user_id, date, journals_written, total_words, voice_sessions, 
                     session_time_minutes, storage_used_bytes, dominant_mood)
                    VALUES (?, ?, 1, ?, ?, ?, ?, ?)
                ''', (user_id, today, word_count, 1 if has_voice else 0, session_minutes, storage_bytes, mood))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Failed to update user analytics: {e}")
            return False
    
    def get_user_analytics(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get user analytics for the last N days"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT date, journals_written, total_words, voice_sessions, 
                       session_time_minutes, dominant_mood, storage_used_bytes
                FROM user_analytics 
                WHERE user_id = ? 
                ORDER BY date DESC 
                LIMIT ?
            ''', (user_id, days))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'date': row[0],
                    'journals_written': row[1],
                    'total_words': row[2],
                    'voice_sessions': row[3],
                    'session_time_minutes': row[4],
                    'dominant_mood': row[5],
                    'storage_used_bytes': row[6]
                })
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"❌ Failed to get user analytics: {e}")
            return []
    
    def get_user_summary(self, user_id: str) -> Dict[str, Any]:
        """Get complete user summary"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get profile
            cursor.execute('''
                SELECT name, email, preferences, created_at FROM user_profiles WHERE user_id = ?
            ''', (user_id,))
            profile = cursor.fetchone()
            
            # Get lifetime stats
            cursor.execute('''
                SELECT SUM(journals_written), SUM(total_words), SUM(voice_sessions),
                       SUM(session_time_minutes), MAX(date), COUNT(DISTINCT date)
                FROM user_analytics WHERE user_id = ?
            ''', (user_id,))
            stats = cursor.fetchone()
            
            # Get recent activity
            cursor.execute('''
                SELECT date, journals_written, dominant_mood 
                FROM user_analytics WHERE user_id = ? 
                ORDER BY date DESC LIMIT 7
            ''', (user_id,))
            recent = cursor.fetchall()
            
            conn.close()
            
            return {
                'profile': {
                    'name': profile[0] if profile else None,
                    'email': profile[1] if profile else None,
                    'preferences': profile[2] if profile else {},
                    'joined_date': profile[3] if profile else None
                },
                'lifetime_stats': {
                    'total_journals': stats[0] or 0,
                    'total_words': stats[1] or 0,
                    'total_voice_sessions': stats[2] or 0,
                    'total_session_minutes': stats[3] or 0,
                    'last_active_date': stats[4],
                    'active_days': stats[5] or 0
                },
                'recent_activity': [
                    {
                        'date': row[0],
                        'journals': row[1],
                        'mood': row[2]
                    } for row in recent
                ]
            }
            
        except Exception as e:
            print(f"❌ Failed to get user summary: {e}")
            return {}
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics for all users"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total users
            cursor.execute('SELECT COUNT(DISTINCT user_id) FROM user_profiles')
            total_users = cursor.fetchone()[0]
            
            # Today's activity
            today = date.today()
            cursor.execute('''
                SELECT COUNT(DISTINCT user_id), SUM(journals_written), 
                       SUM(total_words), SUM(voice_sessions)
                FROM user_analytics WHERE date = ?
            ''', (today,))
            today_stats = cursor.fetchone()
            
            # This week's activity
            cursor.execute('''
                SELECT COUNT(DISTINCT user_id), SUM(journals_written), 
                       SUM(total_words), SUM(voice_sessions)
                FROM user_analytics WHERE date >= date('now', '-7 days')
            ''')
            week_stats = cursor.fetchone()
            
            # Most common moods
            cursor.execute('''
                SELECT dominant_mood, COUNT(*) as count
                FROM user_analytics 
                WHERE dominant_mood IS NOT NULL 
                AND date >= date('now', '-7 days')
                GROUP BY dominant_mood 
                ORDER BY count DESC 
                LIMIT 5
            ''')
            mood_stats = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_users': total_users or 0,
                'today': {
                    'active_users': today_stats[0] or 0,
                    'journals_written': today_stats[1] or 0,
                    'total_words': today_stats[2] or 0,
                    'voice_sessions': today_stats[3] or 0
                },
                'week': {
                    'active_users': week_stats[0] or 0,
                    'journals_written': week_stats[1] or 0,
                    'total_words': week_stats[2] or 0,
                    'voice_sessions': week_stats[3] or 0
                },
                'top_moods': [
                    {'mood': row[0], 'count': row[1]} for row in mood_stats
                ]
            }
            
        except Exception as e:
            print(f"❌ Failed to get dashboard stats: {e}")
            return {}

# Global instance
smart_sql_service = SmartSQLService()