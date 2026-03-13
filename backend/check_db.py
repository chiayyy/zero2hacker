from app.core.database import SessionLocal
from app.models.challenge import Challenge

db = SessionLocal()
challenges = db.query(Challenge).all()

print(f'Total challenges: {len(challenges)}')
for c in challenges:
    print(f'{c.id}. {c.title}: status={repr(c.status)}, type={type(c.status).__name__}')

db.close()
