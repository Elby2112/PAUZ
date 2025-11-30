# PAUZ Journaling Database Migrations

This directory contains database migrations for the PAUZ journaling application.

## Directory Structure

```
db/pauz-journaling/
├── 0000_initial_schema.sql     # Initial database schema
├── 0001_add_indexes.sql         # Additional indexes (future)
├── 0002_add_new_feature.sql     # Feature additions (future)
└── ...                          # Additional migrations
```

## Migration Files

### Naming Convention
- Format: `XXXX_description.sql`
- XXXX: 4-digit sequential number (0001, 0002, etc.)
- description: Brief description of changes

### File Format
- Each migration file contains SQL statements
- Files are executed in numerical order
- Use PostgreSQL-specific features for best performance

## Applied Migrations Tracking

Create a table to track applied migrations:

```sql
CREATE TABLE schema_migrations (
    version VARCHAR(4) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Running Migrations

### Development
```bash
# Apply all migrations
python scripts/migrate.py

# Apply specific migration
python scripts/migrate.py --version 0001
```

### Production
Migrations should be applied automatically during deployment through the Raindrop framework.

## Rollback Strategy

Always create corresponding rollback files:
```
0001_add_feature.sql    # Forward migration
0001_add_feature_down.sql # Rollback migration
```

## Current Schema

The initial schema includes:
- ✅ Users table with Google OAuth integration
- ✅ Free Journals with session management
- ✅ AI-powered Hints with type tracking
- ✅ Garden mood tracking with flower mapping
- ✅ Guided Journals with prompts and entries
- ✅ Proper indexes and constraints
- ✅ Updated_at triggers for audit trails

## Database Connection

Configure your DATABASE_URL in `.env`:
```bash
# Development (SQLite)
DATABASE_URL=sqlite:///./database.db

# Production (PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/pauz
```

## Notes

- All tables use CASCADE deletes for data integrity
- UUIDs are used for primary keys where appropriate
- Timestamps use WITH TIME ZONE for consistency
- Indexes are optimized for common query patterns
- System records use 'system' as user_id for defaults