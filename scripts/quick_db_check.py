import sqlite3

conn = sqlite3.connect('app.db')
cursor = conn.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = [row[0] for row in cursor.fetchall()]
print("Tables in app.db:", tables)

# Check users table schema if it exists
if 'users' in tables:
    cursor = conn.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    print("\nUsers table columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
conn.close()
