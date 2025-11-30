# check_schema_detailed.py
import sqlite3
import os


def check_database_schema():
    # Use the same database path as your app
    database_url = os.getenv("DATABASE_URL", "sqlite:///./pauz.db")

    # Extract the SQLite file path
    if database_url.startswith("sqlite:///"):
        db_file = database_url.replace("sqlite:///", "")
    else:
        db_file = "pauz.db"  # default

    print(f"Checking database file: {db_file}")
    print(f"File exists: {os.path.exists(db_file)}")

    if not os.path.exists(db_file):
        print("❌ Database file does not exist!")
        return

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("\n📊 All tables in database:")
    for table in tables:
        print(f"  - {table[0]}")

    # Check freejournal table specifically
    print(f"\n🔍 Checking freejournal table...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='freejournal'")
    freejournal_exists = cursor.fetchone()

    if freejournal_exists:
        cursor.execute("PRAGMA table_info(freejournal)")
        columns = cursor.fetchall()
        print("FreeJournal table columns:")
        if columns:
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
        else:
            print("  No columns found (empty table)")
    else:
        print("❌ freejournal table does not exist!")

    conn.close()


if __name__ == "__main__":
    check_database_schema()