"""Fix enum values in the database"""
import sqlite3

# Connect to the database
conn = sqlite3.connect('zero2hacker.db')
cursor = conn.cursor()

# Fix difficulty and status columns to use uppercase enum values
cursor.execute("""
    UPDATE challenges
    SET difficulty = UPPER(difficulty),
        status = UPPER(status)
    WHERE difficulty IS NOT NULL
""")

print(f"Updated {cursor.rowcount} challenges")

# Verify the changes
cursor.execute("SELECT id, title, difficulty, status FROM challenges")
rows = cursor.fetchall()

print("\nChallenges in database:")
for row in rows:
    print(f"  ID {row[0]}: {row[1]} - {row[2]} ({row[3]})")

conn.commit()
conn.close()

print("\n✓ Database enum values fixed!")
