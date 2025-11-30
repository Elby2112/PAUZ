#!/usr/bin/env python3
"""
Database Migration Script for PAUZ Journaling App
Handles applying database schema migrations in order
"""
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class DatabaseMigrator:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self.migrations_dir = Path("db/pauz-journaling")
        
        if not self.db_url:
            print("❌ DATABASE_URL not found in environment variables")
            sys.exit(1)
        
        if not self.migrations_dir.exists():
            print(f"❌ Migrations directory not found: {self.migrations_dir}")
            sys.exit(1)
        
        self.connection = self._get_connection()

    def _get_connection(self):
        """Get database connection"""
        try:
            # Parse DATABASE_URL for psycopg2
            if self.db_url.startswith("postgresql://"):
                return psycopg2.connect(self.db_url)
            elif self.db_url.startswith("sqlite://"):
                print("⚠️ SQLite detected - migrations work best with PostgreSQL")
                # For SQLite, we'd need different logic
                print("💡 Consider using PostgreSQL for production")
                return None
            else:
                raise ValueError(f"Unsupported database URL format: {self.db_url}")
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            sys.exit(1)

    def _ensure_migrations_table(self):
        """Create schema_migrations table if it doesn't exist"""
        with self.connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version VARCHAR(4) PRIMARY KEY,
                    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            self.connection.commit()
            print("✅ Migrations tracking table ready")

    def _get_applied_migrations(self):
        """Get list of already applied migration versions"""
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT version FROM schema_migrations ORDER BY version")
            return [row['version'] for row in cursor.fetchall()]

    def _get_pending_migrations(self):
        """Get list of pending migration files"""
        applied = self._get_applied_migrations()
        
        # Get all migration files
        migration_files = []
        for file_path in sorted(self.migrations_dir.glob("*.sql")):
            version = file_path.stem.split('_')[0]
            if version not in applied:
                migration_files.append((file_path, version))
        
        return sorted(migration_files, key=lambda x: x[1])

    def _apply_migration(self, file_path, version):
        """Apply a single migration file"""
        print(f"🔄 Applying migration {version}: {file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            with self.connection.cursor() as cursor:
                # Execute the migration
                cursor.execute(sql_content)
                
                # Record the migration as applied
                cursor.execute(
                    "INSERT INTO schema_migrations (version) VALUES (%s)",
                    (version,)
                )
                
                self.connection.commit()
                print(f"✅ Migration {version} applied successfully")
                
        except Exception as e:
            self.connection.rollback()
            print(f"❌ Migration {version} failed: {e}")
            raise e

    def migrate(self, target_version=None):
        """Run pending migrations up to target version"""
        if not self.connection:
            print("❌ No database connection available")
            return False
        
        self._ensure_migrations_table()
        
        pending = self._get_pending_migrations()
        
        if not pending:
            print("✅ No pending migrations")
            return True
        
        print(f"📋 Found {len(pending)} pending migrations")
        
        for file_path, version in pending:
            if target_version and version > target_version:
                print(f"⏭️ Skipping migration {version} (target: {target_version})")
                continue
            
            self._apply_migration(file_path, version)
        
        print("🎉 All migrations applied successfully!")
        return True

    def status(self):
        """Show migration status"""
        if not self.connection:
            print("❌ No database connection available")
            return
        
        self._ensure_migrations_table()
        
        applied = self._get_applied_migrations()
        pending = self._get_pending_migrations()
        
        print("\n📊 Migration Status:")
        print(f"✅ Applied migrations: {len(applied)}")
        for version in applied:
            print(f"   ✓ {version}")
        
        print(f"⏳ Pending migrations: {len(pending)}")
        for file_path, version in pending:
            print(f"   ○ {version} - {file_path.name}")
        
        if not pending:
            print("🎉 Database is up to date!")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="PAUZ Database Migrations")
    parser.add_argument("--version", help="Migrate up to specific version")
    parser.add_argument("--status", action="store_true", help="Show migration status")
    
    args = parser.parse_args()
    
    migrator = DatabaseMigrator()
    
    try:
        if args.status:
            migrator.status()
        else:
            success = migrator.migrate(target_version=args.version)
            if not success:
                sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)
    finally:
        if migrator.connection:
            migrator.connection.close()

if __name__ == "__main__":
    main()