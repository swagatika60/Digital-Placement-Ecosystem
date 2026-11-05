"""
One-time migration: add the new columns to the existing users table.

Run: python migrate_add_columns.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "app", "placement.db")

COLUMNS_TO_ADD = [
    ("password_reset_token", "VARCHAR(256)"),
    ("password_reset_expiry", "DATETIME"),
    ("email_verified", "BOOLEAN DEFAULT 0"),
    ("verification_token", "VARCHAR(256)"),
    ("verification_sent_at", "DATETIME"),
]


def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH} — skipping (will be created on first run).")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get existing columns
    cursor.execute("PRAGMA table_info(users)")
    existing = {row[1] for row in cursor.fetchall()}

    added = 0
    for col_name, col_type in COLUMNS_TO_ADD:
        if col_name not in existing:
            sql = f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"
            print(f"  Adding column: {col_name}")
            cursor.execute(sql)
            added += 1
        else:
            print(f"  Column exists: {col_name}")

    conn.commit()
    conn.close()

    if added:
        print(f"\n✅ Migration complete — added {added} column(s) to users table.")
    else:
        print("\n✅ All columns already present — no migration needed.")


if __name__ == "__main__":
    migrate()
