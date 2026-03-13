"""
Seed script to create sample CTF challenges
"""
import asyncio
import json
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.challenge import Challenge
from app.models.category import Category
from app.models.user import User
from datetime import datetime


def create_categories(db: Session):
    """Create challenge categories"""
    categories = [
        {
            "name": "Web Exploitation",
            "slug": "web",
            "description": "Web application security vulnerabilities",
            "icon": "globe",
            "color": "#3B82F6",
            "sort_order": 1
        },
        {
            "name": "Cryptography",
            "slug": "crypto",
            "description": "Encryption, decryption, and crypto challenges",
            "icon": "lock",
            "color": "#8B5CF6",
            "sort_order": 2
        },
        {
            "name": "Reverse Engineering",
            "slug": "reverse",
            "description": "Binary analysis and reverse engineering",
            "icon": "code",
            "color": "#EF4444",
            "sort_order": 3
        },
        {
            "name": "Forensics",
            "slug": "forensics",
            "description": "Digital forensics and file analysis",
            "icon": "search",
            "color": "#10B981",
            "sort_order": 4
        },
        {
            "name": "OSINT",
            "slug": "osint",
            "description": "Open Source Intelligence gathering",
            "icon": "eye",
            "color": "#F59E0B",
            "sort_order": 5
        }
    ]

    created_categories = {}
    for cat_data in categories:
        # Check by both slug and name
        existing = db.query(Category).filter(
            (Category.slug == cat_data["slug"]) | (Category.name == cat_data["name"])
        ).first()
        if not existing:
            category = Category(**cat_data, is_active=True)
            db.add(category)
            db.flush()
            created_categories[cat_data["slug"]] = category.id
            print(f"Created category: {cat_data['name']}")
        else:
            created_categories[cat_data["slug"]] = existing.id
            print(f"Category already exists: {cat_data['name']}")

    db.commit()
    return created_categories


def create_easy_challenges(db: Session, categories: dict):
    """Create easy-level CTF challenges"""
    challenges = [
        {
            "title": "Basic XSS",
            "slug": "basic-xss",
            "category_slug": "web",
            "difficulty": "beginner",
            "points": 50,
            "estimated_time": 15,
            "short_description": "Find and exploit a simple Cross-Site Scripting vulnerability",
            "description": """
# Basic XSS Challenge

This challenge contains a simple web page with a search form that's vulnerable to Cross-Site Scripting (XSS).

## Objective
Find the XSS vulnerability and inject a script to retrieve the flag.

## Learning Objectives
- Understand what XSS is
- Learn how to identify XSS vulnerabilities
- Practice basic JavaScript injection

## Hints Available
- Hint 1: Look at how the search input is displayed on the page
- Hint 2: Try injecting a simple `<script>` tag
- Hint 3: Check the HTML source code for the flag location

Good luck!
            """,
            "flag": "FLAG{xss_1s_ev3rywh3re}",
            "hints": [
                "The search input is reflected directly in the HTML without sanitization",
                "Try using <script>alert('XSS')</script> to test",
                "The flag is stored in a JavaScript variable called 'secretFlag'"
            ],
            "tags": ["xss", "web", "javascript", "beginner"],
            "learning_objectives": [
                "Understand Cross-Site Scripting vulnerabilities",
                "Learn basic HTML injection techniques",
                "Practice JavaScript payload creation"
            ],
            "status": "active"
        },
        {
            "title": "Caesar Cipher",
            "slug": "caesar-cipher",
            "category_slug": "crypto",
            "difficulty": "beginner",
            "points": 50,
            "estimated_time": 10,
            "short_description": "Decode a message encrypted with the Caesar cipher",
            "description": """
# Caesar Cipher Challenge

The ancient Caesar cipher is one of the simplest encryption techniques. Can you crack it?

## Encrypted Message
```
SYNT{fvzcyr_pnrfne_fuvsg}
```

## Objective
Decrypt the message to find the flag.

## Learning Objectives
- Understand substitution ciphers
- Learn about the Caesar cipher
- Practice frequency analysis

## Hints Available
- Hint 1: The Caesar cipher shifts each letter by a fixed number
- Hint 2: Try different shift values (ROT13 is common)
- Hint 3: Use an online ROT13 decoder or write your own

Good luck!
            """,
            "flag": "FLAG{simple_caesar_shift}",
            "hints": [
                "Caesar cipher shifts letters by a fixed amount",
                "Try ROT13 (shift of 13)",
                "You can use online tools like rot13.com"
            ],
            "tags": ["crypto", "caesar", "rot13", "beginner"],
            "learning_objectives": [
                "Understand classical ciphers",
                "Learn about rotation ciphers",
                "Practice decryption techniques"
            ],
            "status": "active"
        },
        {
            "title": "Hidden in Plain Sight",
            "slug": "hidden-in-plain-sight",
            "category_slug": "forensics",
            "difficulty": "beginner",
            "points": 50,
            "estimated_time": 20,
            "short_description": "Find the hidden message in an image file",
            "description": """
# Hidden in Plain Sight

Something is hidden in this seemingly ordinary image. Can you find it?

## Objective
Extract the hidden flag from the provided image file.

## Learning Objectives
- Learn about steganography
- Understand metadata analysis
- Practice file examination techniques

## Tools You Might Need
- exiftool (for metadata)
- strings command
- hex editor

## Hints Available
- Hint 1: Sometimes secrets hide in the metadata
- Hint 2: Try using 'strings' command on the image
- Hint 3: Check the EXIF data with exiftool

Download the image from the challenge page.

Good luck!
            """,
            "flag": "FLAG{st3g4n0gr4phy_1s_fun}",
            "hints": [
                "Metadata can contain hidden information",
                "Use 'exiftool image.jpg' to view metadata",
                "The flag might be in a comment field"
            ],
            "tags": ["forensics", "steganography", "metadata", "beginner"],
            "learning_objectives": [
                "Learn about image metadata",
                "Understand steganography basics",
                "Practice file analysis"
            ],
            "status": "active",
            "files_url": "/static/challenges/hidden_image.jpg"
        },
        {
            "title": "SQL Injection 101",
            "slug": "sql-injection-101",
            "category_slug": "web",
            "difficulty": "easy",
            "points": 100,
            "estimated_time": 30,
            "short_description": "Exploit a SQL injection vulnerability to access restricted data",
            "description": """
# SQL Injection 101

This login form is vulnerable to SQL injection. Can you bypass authentication?

## Objective
Use SQL injection to log in as admin and retrieve the flag.

## Learning Objectives
- Understand SQL injection vulnerabilities
- Learn how to identify injection points
- Practice basic SQL syntax

## Hints Available
- Hint 1: Try entering ' OR '1'='1 in the username field
- Hint 2: You want to make the SQL query always return true
- Hint 3: Comment out the rest of the query with --

Access the challenge at the provided URL.

Good luck!
            """,
            "flag": "FLAG{sql_1nj3ct10n_m4st3r}",
            "hints": [
                "SQL injection uses malicious SQL code in inputs",
                "Try: admin' OR '1'='1'-- in the username",
                "The goal is to bypass the password check"
            ],
            "tags": ["sql", "injection", "web", "easy"],
            "learning_objectives": [
                "Understand SQL injection attacks",
                "Learn SQL syntax and queries",
                "Practice authentication bypass"
            ],
            "status": "active"
        },
        {
            "title": "Base64 Bonanza",
            "slug": "base64-bonanza",
            "category_slug": "crypto",
            "difficulty": "beginner",
            "points": 50,
            "estimated_time": 5,
            "short_description": "Decode a Base64 encoded message",
            "description": """
# Base64 Bonanza

The flag has been encoded using Base64. Decode it to reveal the secret!

## Encoded Message
```
RkxBR3tiNHMzNjRfaXNfbjB0X2VuY3J5cHQxb259
```

## Objective
Decode the Base64 string to get the flag.

## Learning Objectives
- Understand Base64 encoding
- Learn the difference between encoding and encryption
- Practice using decoding tools

## Tools
- Online: base64decode.org
- Command line: `echo "string" | base64 -d`
- Python: `import base64; base64.b64decode(string)`

Good luck!
            """,
            "flag": "FLAG{b4s364_is_n0t_encrypt1on}",
            "hints": [
                "Base64 is an encoding scheme, not encryption",
                "Use an online Base64 decoder",
                "The string ends with '=' padding characters (sometimes)"
            ],
            "tags": ["crypto", "encoding", "base64", "beginner"],
            "learning_objectives": [
                "Understand encoding vs encryption",
                "Learn Base64 encoding scheme",
                "Practice decoding techniques"
            ],
            "status": "active"
        },
        {
            "title": "Cookie Monster",
            "slug": "cookie-monster",
            "category_slug": "web",
            "difficulty": "easy",
            "points": 75,
            "estimated_time": 20,
            "short_description": "Manipulate cookies to gain admin access",
            "description": """
# Cookie Monster

This website uses cookies for authentication. Can you manipulate them to become an admin?

## Objective
Modify your session cookie to gain administrative privileges and view the flag.

## Learning Objectives
- Understand HTTP cookies
- Learn about session management
- Practice cookie manipulation

## Tools
- Browser DevTools (F12)
- EditThisCookie extension
- Burp Suite (optional)

## Hints Available
- Hint 1: Check your current cookie value in DevTools
- Hint 2: Look for a 'role' or 'isAdmin' cookie
- Hint 3: Try changing the cookie value to 'admin' or 'true'

Access the challenge website to begin.

Good luck!
            """,
            "flag": "FLAG{c00k13s_ar3_t4sty}",
            "hints": [
                "Open browser DevTools (F12) and go to Application > Cookies",
                "Look for cookies like 'role' or 'user_type'",
                "Try changing the value to 'admin' and refresh"
            ],
            "tags": ["web", "cookies", "session", "easy"],
            "learning_objectives": [
                "Understand cookie-based authentication",
                "Learn about session management",
                "Practice client-side security testing"
            ],
            "status": "active"
        }
    ]

    created_count = 0
    for challenge_data in challenges:
        category_id = categories.get(challenge_data.pop("category_slug"))

        # Convert lists to JSON strings
        if "hints" in challenge_data and isinstance(challenge_data["hints"], list):
            challenge_data["hints"] = json.dumps(challenge_data["hints"])
        if "tags" in challenge_data and isinstance(challenge_data["tags"], list):
            challenge_data["tags"] = json.dumps(challenge_data["tags"])
        if "learning_objectives" in challenge_data and isinstance(challenge_data["learning_objectives"], list):
            challenge_data["learning_objectives"] = json.dumps(challenge_data["learning_objectives"])

        existing = db.query(Challenge).filter(Challenge.slug == challenge_data["slug"]).first()
        if not existing:
            challenge = Challenge(
                **challenge_data,
                category_id=category_id,
                generated_by_ai=False,
                solve_count=0,
                attempt_count=0,
                created_at=datetime.utcnow()
            )
            db.add(challenge)
            created_count += 1
            print(f"Created challenge: {challenge_data['title']}")
        else:
            print(f"Challenge already exists: {challenge_data['title']}")

    db.commit()
    print(f"\nCreated {created_count} new challenges")


def main():
    """Main function to seed the database"""
    print("Starting database seeding...")

    db = SessionLocal()
    try:
        # Create categories first
        categories = create_categories(db)

        # Create challenges
        create_easy_challenges(db, categories)

        print("\nDatabase seeding completed successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
