"""
Test database schema initialization and integrity.
"""
import sqlite3
import pytest


def test_db_schema_subscribers_table(test_db):
    """Test that subscribers table exists with correct schema."""
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    # Check table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='subscribers'")
    assert cursor.fetchone() is not None, "subscribers table should exist"
    
    # Check columns
    cursor.execute("PRAGMA table_info(subscribers)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    
    assert 'email' in columns
    assert 'location' in columns
    assert 'lat' in columns
    assert 'lon' in columns
    assert 'timezone' in columns
    assert 'personality' in columns
    assert 'language' in columns
    assert 'updated_at' in columns
    assert 'last_sent_date' in columns
    
    conn.close()


def test_db_schema_countdowns_table(test_db):
    """Test that countdowns table exists with correct schema."""
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    # Check table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='countdowns'")
    assert cursor.fetchone() is not None, "countdowns table should exist"
    
    # Check columns
    cursor.execute("PRAGMA table_info(countdowns)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    
    assert 'id' in columns
    assert 'email' in columns
    assert 'name' in columns
    assert 'date' in columns
    assert 'yearly' in columns
    assert 'message_before' in columns
    
    conn.close()


def test_db_schema_inbox_log_table(test_db):
    """Test that inbox_log table exists for deduplication."""
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    # Check table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inbox_log'")
    assert cursor.fetchone() is not None, "inbox_log table should exist"
    
    # Check columns
    cursor.execute("PRAGMA table_info(inbox_log)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    
    assert 'uid' in columns
    assert 'from_email' in columns
    assert 'received_at' in columns
    
    conn.close()


def test_db_insert_subscriber(test_db):
    """Test inserting a subscriber into the database."""
    conn = sqlite3.connect(test_db)
    
    # Insert subscriber
    conn.execute("""
        INSERT INTO subscribers (email, location, lat, lon, timezone, personality, language, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, ('test@example.com', 'Bratislava', 48.1486, 17.1077, 'Europe/Bratislava', 'neutral', 'en', '2025-12-16T05:00:00'))
    conn.commit()
    
    # Verify insertion
    cursor = conn.execute("SELECT * FROM subscribers WHERE email = ?", ('test@example.com',))
    row = cursor.fetchone()
    
    assert row is not None
    assert row[0] == 'test@example.com'
    assert row[1] == 'Bratislava'
    assert row[5] == 'neutral'
    assert row[6] == 'en'
    
    conn.close()


def test_db_update_subscriber(test_db):
    """Test updating subscriber with UPSERT logic."""
    conn = sqlite3.connect(test_db)
    
    # Insert initial subscriber
    conn.execute("""
        INSERT INTO subscribers (email, location, lat, lon, timezone, personality, language, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, ('test@example.com', 'Bratislava', 48.1486, 17.1077, 'Europe/Bratislava', 'neutral', 'en', '2025-12-16T05:00:00'))
    conn.commit()
    
    # Update with UPSERT
    conn.execute("""
        INSERT INTO subscribers (email, location, lat, lon, timezone, personality, language, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET
            location=excluded.location,
            personality=excluded.personality,
            updated_at=excluded.updated_at
    """, ('test@example.com', 'Prague', 50.0755, 14.4378, 'Europe/Prague', 'cute', 'sk', '2025-12-16T06:00:00'))
    conn.commit()
    
    # Verify update
    cursor = conn.execute("SELECT location, personality, language FROM subscribers WHERE email = ?", ('test@example.com',))
    row = cursor.fetchone()
    
    assert row[0] == 'Prague'
    assert row[1] == 'cute'
    
    conn.close()


def test_db_delete_subscriber(test_db):
    """Test deleting a subscriber from the database."""
    conn = sqlite3.connect(test_db)
    
    # Insert subscriber
    conn.execute("""
        INSERT INTO subscribers (email, location, lat, lon, timezone, personality, language, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, ('test@example.com', 'Bratislava', 48.1486, 17.1077, 'Europe/Bratislava', 'neutral', 'en', '2025-12-16T05:00:00'))
    conn.commit()
    
    # Delete subscriber
    cursor = conn.execute("DELETE FROM subscribers WHERE email = ?", ('test@example.com',))
    conn.commit()
    
    assert cursor.rowcount == 1
    
    # Verify deletion
    cursor = conn.execute("SELECT * FROM subscribers WHERE email = ?", ('test@example.com',))
    assert cursor.fetchone() is None
    
    conn.close()


def test_db_inbox_log_deduplication(test_db):
    """Test inbox_log prevents duplicate message processing."""
    conn = sqlite3.connect(test_db)
    
    # Insert first log
    conn.execute("""
        INSERT INTO inbox_log (uid, from_email, received_at)
        VALUES (?, ?, ?)
    """, ('UID123', 'user@example.com', '2025-12-16T05:00:00'))
    conn.commit()
    
    # Try to insert duplicate (should fail due to PRIMARY KEY)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("""
            INSERT INTO inbox_log (uid, from_email, received_at)
            VALUES (?, ?, ?)
        """, ('UID123', 'user@example.com', '2025-12-16T05:01:00'))
        conn.commit()
    
    conn.close()
