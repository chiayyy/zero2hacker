#!/usr/bin/env python3
"""
Set docker_port for all challenges so the frontend shows the Launch button.
Run from: backend/
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.challenge import Challenge

PORT_MAP = {
    "sql":     8080,
    "xss":     8085,
    "cookie":  8087,
    "caesar":  8081,
    "base64":  8086,
    "hidden":  8082,
    "packet":  8083,
    "deleted": 8084,
}

db = SessionLocal()
challenges = db.query(Challenge).all()

updated = 0
for c in challenges:
    combined = (c.title + " " + (c.slug or "")).lower()
    for keyword, port in PORT_MAP.items():
        if keyword in combined:
            if c.docker_port != port:
                c.docker_port = port
                print(f"  [{port}] {c.title}")
                updated += 1
            break

db.commit()
db.close()
print(f"\nDone. Updated {updated} challenge(s).")
