-- 0000_initial_schema_sqlite.sql
-- SQLite-compatible database schema for PAUZ Journaling Application

-- Users table
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    picture TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Free Journals table
CREATE TABLE free_journals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    content TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Hints table for AI-generated suggestions
CREATE TABLE hints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    hint_text TEXT NOT NULL,
    ai_type TEXT DEFAULT 'intelligent_fallback',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Garden table for mood tracking
CREATE TABLE garden (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    mood TEXT NOT NULL,
    note TEXT,
    flower_type TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Guided Journals table
CREATE TABLE guided_journals (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prompts table for guided journaling
CREATE TABLE prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    guided_journal_id TEXT NOT NULL,
    prompt_type TEXT DEFAULT 'ai_generated',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Guided Journal Entries table
CREATE TABLE guided_journal_entries (
    id TEXT PRIMARY KEY,
    guided_journal_id TEXT NOT NULL,
    prompt_id INTEGER NOT NULL,
    response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_free_journals_user_id ON free_journals(user_id);
CREATE INDEX idx_free_journals_session_id ON free_journals(session_id);
CREATE INDEX idx_hints_user_id ON hints(user_id);
CREATE INDEX idx_hints_session_id ON hints(session_id);
CREATE INDEX idx_garden_user_id ON garden(user_id);
CREATE INDEX idx_garden_mood ON garden(mood);
CREATE INDEX idx_guided_journals_user_id ON guided_journals(user_id);
CREATE INDEX idx_prompts_guided_journal_id ON prompts(guided_journal_id);
CREATE INDEX idx_guided_journal_entries_guided_journal_id ON guided_journal_entries(guided_journal_id);