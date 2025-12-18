import sqlite3

# Connect to the database
conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# Fetch all subscribers
cursor.execute("SELECT email, personality, language, timezone FROM subscribers;")
subscribers = cursor.fetchall()

inserted = 0
for email, personality, language, timezone in subscribers:
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO users (email, personality, language, timezone, active, created_at)
            VALUES (?, ?, ?, ?, 1, datetime('now'))
        """, (email, personality, language, timezone))
        inserted += 1
    except Exception as e:
        print(f"Failed to insert {email}: {e}")

conn.commit()
print(f"Inserted {inserted} users from subscribers table into users table.")
conn.close()
