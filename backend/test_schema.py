from app.core.database import SessionLocal
from app.models.challenge import Challenge as ChallengeModel, ChallengeStatus
from app.schemas.challenge import ChallengeResponse

db = SessionLocal()
chal = db.query(ChallengeModel).filter(ChallengeModel.status == ChallengeStatus.ACTIVE).first()

if chal:
    print(f'Challenge found: {chal.title}')
    print(f'Status: {chal.status}')
    print(f'Hints (raw): {repr(chal.hints)}')
    print(f'Tags (raw): {repr(chal.tags)}')

    try:
        schema_obj = ChallengeResponse.model_validate(chal)
        print('Schema validation SUCCESS')
        print(f'Hints (schema): {schema_obj.hints}')
        print(f'Tags (schema): {schema_obj.tags}')
    except Exception as e:
        print(f'Schema validation FAILED: {type(e).__name__}: {e}')
else:
    print('No active challenges found')

db.close()
