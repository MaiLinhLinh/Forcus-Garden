"""
Migration: Thêm column actual_duration_secs vào bảng sessions
Chạy script này một lần để migrate database.
"""
import sys
sys.path.insert(0, 'Code_base')

from database.db_config import get_db
from sqlalchemy import text

print("Running migration: Add actual_duration_secs column to sessions table...")

db = get_db()
try:
    # Thêm column actual_duration_secs
    db.execute(text("""
        ALTER TABLE sessions ADD COLUMN actual_duration_secs INTEGER DEFAULT 0
    """))

    # Update existing records: tính actual_duration_secs từ actual_duration_mins
    db.execute(text("""
        UPDATE sessions SET actual_duration_secs = actual_duration_mins * 60
        WHERE actual_duration_secs = 0
    """))

    db.commit()
    print("✓ Migration successful!")
    print("  - Added column: actual_duration_secs")
    print("  - Updated existing records")

except Exception as e:
    db.rollback()
    print(f"✗ Migration failed: {e}")
    print("  Note: Column might already exist. That's OK if you've run this before.")
finally:
    db.close()
