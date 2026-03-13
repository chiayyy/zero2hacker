import sqlite3

conn = sqlite3.connect('./zero2hacker.db')
cursor = conn.cursor()

# Revert challenge status from lowercase to uppercase
cursor.execute("UPDATE challenges SET status = 'ACTIVE' WHERE status = 'active'")
cursor.execute("UPDATE challenges SET status = 'DRAFT' WHERE status = 'draft'")
cursor.execute("UPDATE challenges SET status = 'RETIRED' WHERE status = 'retired'")
cursor.execute("UPDATE challenges SET status = 'MAINTENANCE' WHERE status = 'maintenance'")

# Revert difficulty levels to uppercase
cursor.execute("UPDATE challenges SET difficulty = 'BEGINNER' WHERE difficulty = 'beginner'")
cursor.execute("UPDATE challenges SET difficulty = 'EASY' WHERE difficulty = 'easy'")
cursor.execute("UPDATE challenges SET difficulty = 'MEDIUM' WHERE difficulty = 'medium'")
cursor.execute("UPDATE challenges SET difficulty = 'HARD' WHERE difficulty = 'hard'")
cursor.execute("UPDATE challenges SET difficulty = 'EXPERT' WHERE difficulty = 'expert'")

# Revert attempt status to uppercase
cursor.execute("UPDATE challenge_attempts SET status = 'IN_PROGRESS' WHERE status = 'in_progress'")
cursor.execute("UPDATE challenge_attempts SET status = 'SOLVED' WHERE status = 'solved'")
cursor.execute("UPDATE challenge_attempts SET status = 'FAILED' WHERE status = 'failed'")
cursor.execute("UPDATE challenge_attempts SET status = 'TIMEOUT' WHERE status = 'timeout'")

conn.commit()

# Verify changes
cursor.execute('SELECT id, title, status, difficulty FROM challenges LIMIT 5')
rows = cursor.fetchall()

print('Reverted challenges:')
for r in rows:
    print(f'{r[0]}. {r[1]}: status={repr(r[2])}, difficulty={repr(r[3])}')

conn.close()
print('\nDatabase enum values reverted to uppercase!')
