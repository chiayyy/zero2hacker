import sqlite3

conn = sqlite3.connect('./zero2hacker.db')
cursor = conn.cursor()

# Update challenge status from ACTIVE to active
cursor.execute("UPDATE challenges SET status = 'active' WHERE status = 'ACTIVE'")
cursor.execute("UPDATE challenges SET status = 'draft' WHERE status = 'DRAFT'")
cursor.execute("UPDATE challenges SET status = 'retired' WHERE status = 'RETIRED'")
cursor.execute("UPDATE challenges SET status = 'maintenance' WHERE status = 'MAINTENANCE'")

# Update difficulty levels
cursor.execute("UPDATE challenges SET difficulty = 'beginner' WHERE difficulty = 'BEGINNER'")
cursor.execute("UPDATE challenges SET difficulty = 'easy' WHERE difficulty = 'EASY'")
cursor.execute("UPDATE challenges SET difficulty = 'medium' WHERE difficulty = 'MEDIUM'")
cursor.execute("UPDATE challenges SET difficulty = 'hard' WHERE difficulty = 'HARD'")
cursor.execute("UPDATE challenges SET difficulty = 'expert' WHERE difficulty = 'EXPERT'")

conn.commit()

# Verify changes
cursor.execute('SELECT id, title, status, difficulty FROM challenges LIMIT 5')
rows = cursor.fetchall()

print('Updated challenges:')
for r in rows:
    print(f'{r[0]}. {r[1]}: status={repr(r[2])}, difficulty={repr(r[3])}')

conn.close()
print('\nDatabase enum values fixed!')
