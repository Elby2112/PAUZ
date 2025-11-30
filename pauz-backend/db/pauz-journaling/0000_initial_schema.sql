-- 0000_initial_schema.sql
-- Initial database schema for PAUZ Journaling Application
-- Creates all necessary tables for the application

-- Enable UUID extension if using PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    picture VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Free Journals table
CREATE TABLE free_journals (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255) NOT NULL,
    content TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint for user sessions
    UNIQUE(user_id, session_id)
);

-- Hints table for AI-generated suggestions
CREATE TABLE hints (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255) NOT NULL REFERENCES free_journals(session_id) ON DELETE CASCADE,
    hint_text TEXT NOT NULL,
    ai_type VARCHAR(50) DEFAULT 'intelligent_fallback', -- gemini, openai, intelligent_fallback
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Garden table for mood tracking
CREATE TABLE garden (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mood VARCHAR(50) NOT NULL, -- happy, sad, anxious, calm, reflective
    note TEXT,
    flower_type VARCHAR(50) NOT NULL, -- sunflower, bluebell, lavender, lotus, chamomile
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Guided Journals table
CREATE TABLE guided_journals (
    id VARCHAR(255) PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    topic VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Prompts table for guided journaling
CREATE TABLE prompts (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    guided_journal_id VARCHAR(255) NOT NULL REFERENCES guided_journals(id) ON DELETE CASCADE,
    prompt_type VARCHAR(50) DEFAULT 'ai_generated', -- ai_generated, template, fallback
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Guided Journal Entries table
CREATE TABLE guided_journal_entries (
    id VARCHAR(255) PRIMARY KEY DEFAULT uuid_generate_v4(),
    guided_journal_id VARCHAR(255) NOT NULL REFERENCES guided_journals(id) ON DELETE CASCADE,
    prompt_id INTEGER NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
    response TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance optimization
CREATE INDEX idx_free_journals_user_id ON free_journals(user_id);
CREATE INDEX idx_free_journals_session_id ON free_journals(session_id);
CREATE INDEX idx_free_journals_created_at ON free_journals(created_at);

CREATE INDEX idx_hints_user_id ON hints(user_id);
CREATE INDEX idx_hints_session_id ON hints(session_id);
CREATE INDEX idx_hints_created_at ON hints(created_at);

CREATE INDEX idx_garden_user_id ON garden(user_id);
CREATE INDEX idx_garden_mood ON garden(mood);
CREATE INDEX idx_garden_created_at ON garden(created_at);

CREATE INDEX idx_guided_journals_user_id ON guided_journals(user_id);
CREATE INDEX idx_guided_journals_created_at ON guided_journals(created_at);

CREATE INDEX idx_prompts_guided_journal_id ON prompts(guided_journal_id);
CREATE INDEX idx_guided_journal_entries_guided_journal_id ON guided_journal_entries(guided_journal_id);
CREATE INDEX idx_guided_journal_entries_created_at ON guided_journal_entries(created_at);

-- Create trigger functions for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_free_journals_updated_at 
    BEFORE UPDATE ON free_journals 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_guided_journals_updated_at 
    BEFORE UPDATE ON guided_journals 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert some default flower types for garden
INSERT INTO garden (user_id, mood, note, flower_type, created_at) VALUES
('system', 'happy', 'Default happy mood mapping', 'sunflower', NOW()),
('system', 'sad', 'Default sad mood mapping', 'bluebell', NOW()),
('system', 'anxious', 'Default anxious mood mapping', 'lavender', NOW()),
('system', 'calm', 'Default calm mood mapping', 'lotus', NOW()),
('system', 'reflective', 'Default reflective mood mapping', 'chamomile', NOW());