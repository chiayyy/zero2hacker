import sqlite3

conn = sqlite3.connect('./zero2hacker.db')
cursor = conn.cursor()
cursor.execute('SELECT id, title, status FROM challenges LIMIT 5')
rows = cursor.fetchall()

print(f'Total challenges: {len(rows)}')
for r in rows:
    print(f'{r[0]}. {r[1]}: status={repr(r[2])}')

conn.close()
