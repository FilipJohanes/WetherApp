#!/usr/bin/env python3
"""
Add password reset tokens table to database
"""

import sqlite3
import os
from pathlib import Path

def add_password_reset_table():
    """Add password_reset_tokens table to database."""
    # Get database path
    db_path = os.getenv("APP_DB_PATH", "app.db")
    
    # Resolve path relative to script location
    if not os.path.isabs(db_path):
        script_dir = Path(__file__).parent.parent
        db_path = script_dir / db_path
    
    print(f"Using database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if table already exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='password_reset_tokens'
    """)
    
    if cursor.fetchone():
        print("✓ password_reset_tokens table already exists")
    else:
        # Create password reset tokens table
        cursor.execute("""
            CREATE TABLE password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                token TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                used INTEGER DEFAULT 0,
                FOREIGN KEY (email) REFERENCES users(email)
            )
        """)
        
        # Create index on token for fast lookup
        cursor.execute("""
            CREATE INDEX idx_reset_token ON password_reset_tokens(token)
        """)
        
        # Create index on email for cleanup
        cursor.execute("""
            CREATE INDEX idx_reset_email ON password_reset_tokens(email)
        """)
        
        conn.commit()
        print("✓ Created password_reset_tokens table with indexes")
    
    conn.close()
    print("✓ Database migration complete")

if __name__ == "__main__":
    add_password_reset_table()
