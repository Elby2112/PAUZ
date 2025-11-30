#!/usr/bin/env python3
"""
SQLite-compatible Migration Script for Testing
"""
import os
import sys
import sqlite3
from pathlib import Path

class SQLiteMigrator:
    def __init__(self, db_path="test_database.db"):
        self.db_path = db_path
        self.migrations_dir = Path("db/pauz-journaling")
        self.connection = sqlite3.connect(self.db_path)
        
    def _ensure_migrations_table(self):
        """Create schema_migrations table"""
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self.connection.commit()
        print("✅ Migrations tracking table ready")

    def _get_applied_migrations(self):
        """Get list of applied migrations"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT version FROM schema_migrations ORDER BY version")
        return [row[0] for row in cursor.fetchall()]

    def _get_pending_migrations(self):
        """Get pending migrations"""
        applied = self._get_applied_migrations()
        pending = []
        
        for file_path in sorted(self.migrations_dir.glob("*.sql")):
            version = file_path.stem.split('_')[0]
            if version not in applied:
                pending.append((file_path, version))
        
        return sorted(pending, key=lambda x: x[1])

    def _apply_sqlite_migration(self, file_path, version):
        """Apply migration with SQLite adaptations"""
        print(f"🔄 Applying SQLite migration {version}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print(f"🔍 Original SQL preview:\n{sql_content[:500]}...")
        
        # Use the SQLite file directly if it exists
        if file_path.name.endswith('_sqlite.sql'):
            sqlite_sql = sql_content
        else:
            sqlite_sql = self._convert_postgres_to_sqlite(sql_content)
        
        print(f"🔍 Converted SQL preview:\n{sqlite_sql[:500]}...")
        
        cursor = self.connection.cursor()
        
        try:
            # Execute the migration
            cursor.executescript(sqlite_sql)
            
            # Record as applied
            cursor.execute(
                "INSERT INTO schema_migrations (version) VALUES (?)",
                (version,)
            )
            
            self.connection.commit()
            print(f"✅ Migration {version} applied successfully")
            
        except Exception as e:
            self.connection.rollback()
            print(f"❌ Migration {version} failed: {e}")
            raise e

    def _convert_postgres_to_sqlite(self, sql):
        """Convert PostgreSQL SQL to SQLite"""
        # Remove PostgreSQL-specific extensions
        sql_lines = sql.split('\n')
        converted_lines = []
        skip_trigger_block = False
        
        for line in sql_lines:
            line = line.strip()
            
            # Skip PostgreSQL extensions
            if line.startswith('CREATE EXTENSION'):
                continue
            if line.startswith('CREATE OR REPLACE FUNCTION'):
                skip_trigger_block = True
                continue
            if skip_trigger_block and line.startswith('$$ language'):
                skip_trigger_block = False
                continue
            if skip_trigger_block:
                continue
            if line.startswith('CREATE TRIGGER'):
                continue
            if line.startswith('DROP TRIGGER'):
                continue
            
            # Convert PostgreSQL specifics to SQLite
            line = line.replace("VARCHAR(255)", "TEXT")
            line = line.replace("VARCHAR(50)", "TEXT")
            line = line.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
            line = line.replace("WITH TIME ZONE", "")
            line = line.replace("ON DELETE CASCADE", "")
            line = line.replace("DEFAULT uuid_generate_v4()", "")
            line = line.replace("DEFAULT NOW()", "DEFAULT CURRENT_TIMESTAMP")
            line = line.replace("TIMESTAMP  DEFAULT", "TIMESTAMP DEFAULT")
            
            # Remove function calls in UNIQUE constraints
            if "UNIQUE(user_id, session_id)" in line:
                continue  # Skip this line for SQLite
            
            converted_lines.append(line)
        
        return '\n'.join(converted_lines)

    def migrate(self):
        """Run migrations"""
        self._ensure_migrations_table()
        
        pending = self._get_pending_migrations()
        
        if not pending:
            print("✅ No pending migrations")
            return True
        
        for file_path, version in pending:
            self._apply_sqlite_migration(file_path, version)
        
        print("🎉 All SQLite migrations applied!")
        return True

    def status(self):
        """Show migration status"""
        self._ensure_migrations_table()
        
        applied = self._get_applied_migrations()
        pending = self._get_pending_migrations()
        
        print("\n📊 SQLite Migration Status:")
        print(f"✅ Applied: {len(applied)}")
        for version in applied:
            print(f"   ✓ {version}")
        
        print(f"⏳ Pending: {len(pending)}")
        for file_path, version in pending:
            print(f"   ○ {version} - {file_path.name}")

if __name__ == "__main__":
    migrator = SQLiteMigrator()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        migrator.status()
    else:
        migrator.migrate()