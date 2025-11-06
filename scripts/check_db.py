import sqlite3

conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables in database:')
for table in tables:
    print(f'  {table[0]}')

print()

# Check reminders table structure
cursor.execute("PRAGMA table_info(reminders)")
columns = cursor.fetchall()
print('Reminders table columns:')
for col in columns:
    print(f'  {col[1]} ({col[2]})')

print()

# Check current reminders
cursor.execute("SELECT * FROM reminders LIMIT 5")
reminders = cursor.fetchall()
print(f'Sample reminders ({len(reminders)} shown):')
for reminder in reminders:
    print(f'  {reminder}')

conn.close()