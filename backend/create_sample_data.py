#!/usr/bin/env python3
"""
Script to create sample categories and challenges in the database
with HCI-focused design principles
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.challenge import Challenge, DifficultyLevel, ChallengeStatus
from app.models.category import Category
from app.core.config import settings
from datetime import datetime
import json

def create_sample_data():
    """Create sample categories and challenges"""

    # Create database engine
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Create categories if they don't exist
        categories_data = [
            {
                "name": "Cryptography",
                "slug": "cryptography",
                "description": "Learn encryption, decryption, and cryptographic algorithms. Perfect for understanding how data is protected.",
                "icon": "key",
                "color": "#FF6B6B"
            },
            {
                "name": "Web Security",
                "slug": "web-security",
                "description": "Explore web application vulnerabilities and learn how to secure websites from common attacks.",
                "icon": "globe",
                "color": "#4ECDC4"
            },
            {
                "name": "Reverse Engineering",
                "slug": "reverse-engineering",
                "description": "Analyze and understand how software works by examining compiled code and binaries.",
                "icon": "code",
                "color": "#95E1D3"
            },
            {
                "name": "Forensics",
                "slug": "forensics",
                "description": "Investigate digital evidence, recover deleted files, and analyze system artifacts.",
                "icon": "search",
                "color": "#F38181"
            },
            {
                "name": "Network Security",
                "slug": "network-security",
                "description": "Learn about network protocols, packet analysis, and network-based attacks.",
                "icon": "network",
                "color": "#AA96DA"
            },
            {
                "name": "Steganography",
                "slug": "steganography",
                "description": "Discover hidden messages in images, audio, and other media files.",
                "icon": "image",
                "color": "#FCBAD3"
            }
        ]

        categories = {}
        for cat_data in categories_data:
            existing_cat = db.query(Category).filter(Category.name == cat_data["name"]).first()
            if existing_cat:
                categories[cat_data["name"]] = existing_cat
                print(f"Category '{cat_data['name']}' already exists")
            else:
                category = Category(**cat_data)
                db.add(category)
                db.commit()
                db.refresh(category)
                categories[cat_data["name"]] = category
                print(f"Created category: {cat_data['name']}")

        # Create comprehensive challenges with HCI focus
        challenges_data = [
            # BEGINNER CHALLENGES - Clear instructions, simple tasks
            {
                "title": "Caesar's Secret",
                "slug": "caesars-secret",
                "description": """Welcome to your first cryptography challenge!

The Caesar cipher is one of the oldest encryption methods, named after Julius Caesar who used it to protect military messages.

HOW IT WORKS:
Each letter in the message is shifted by a fixed number of positions in the alphabet.
For example, with a shift of 3:
- A becomes D
- B becomes E
- HELLO becomes KHOOR

YOUR TASK:
Download the challenge file and decode the encrypted message to find the flag.

The flag format is: FLAG{some_text_here}""",
                "category_id": categories["Cryptography"].id,
                "difficulty": DifficultyLevel.BEGINNER,
                "points": 50,
                "flag": "FLAG{caesar_was_here}",
                "hints": json.dumps([
                    "The cipher uses a letter shift. Try moving each letter backwards in the alphabet.",
                    "Common shift values are 3, 7, and 13. ROT13 (shift of 13) is very popular.",
                    "Online Caesar cipher decoders can help. Search for 'Caesar cipher decoder'."
                ]),
                "tags": json.dumps(["crypto", "cipher", "beginner", "classical"]),
                "files_url": "/static/challenges/caesar_cipher.txt",
                "estimated_time": 10,
                "learning_objectives": json.dumps([
                    "Understand how substitution ciphers work",
                    "Learn about the Caesar cipher encryption method",
                    "Practice basic cryptanalysis techniques"
                ])
            },
            {
                "title": "Base64 Basics",
                "slug": "base64-basics",
                "description": """Learn about Base64 encoding - one of the most common encoding schemes in computing!

WHAT IS BASE64?
Base64 is a method to encode binary data into ASCII text. It's widely used for:
- Email attachments
- Storing images in web pages
- API authentication tokens

HOW TO DECODE:
- Online: Search for "Base64 decoder"
- Command line: echo "encoded_text" | base64 -d
- Python: import base64; base64.b64decode("encoded_text")

YOUR TASK:
Download the file and decode the Base64 message to reveal the flag.

Remember: Base64 is ENCODING, not ENCRYPTION - it provides no security!""",
                "category_id": categories["Cryptography"].id,
                "difficulty": DifficultyLevel.BEGINNER,
                "points": 50,
                "flag": "FLAG{base64_decoding_rocks}",
                "hints": json.dumps([
                    "Base64 encoded strings often end with = or == padding",
                    "Copy the encoded string and use any online Base64 decoder",
                    "In Python: import base64; print(base64.b64decode('your_string').decode())"
                ]),
                "tags": json.dumps(["crypto", "encoding", "base64", "beginner"]),
                "files_url": "/static/challenges/base64_challenge.txt",
                "estimated_time": 5,
                "learning_objectives": json.dumps([
                    "Understand the difference between encoding and encryption",
                    "Learn to recognize and decode Base64",
                    "Use command-line tools for decoding"
                ])
            },
            {
                "title": "Hidden in Plain Sight",
                "slug": "hidden-in-plain-sight",
                "description": """Welcome to steganography - the art of hiding messages!

Unlike encryption which makes data unreadable, steganography hides the existence of the message entirely.

CHALLENGE TYPE: Text-based steganography

Sometimes secret messages are hidden in plain text using patterns that aren't immediately obvious.

YOUR TASK:
Download the text file and look carefully at its contents. The flag is hidden using a simple technique.

TIPS FOR SUCCESS:
- Read the text carefully
- Look for patterns
- Pay attention to the structure
- The first letters might be important...

The flag format is: FLAG{word_word}""",
                "category_id": categories["Steganography"].id,
                "difficulty": DifficultyLevel.BEGINNER,
                "points": 75,
                "flag": "FLAG{steganography_rocks}",
                "hints": json.dumps([
                    "Look at the first letter of each line",
                    "Read the first letters from top to bottom",
                    "The hidden message will spell out the flag"
                ]),
                "tags": json.dumps(["steganography", "text", "hidden", "beginner"]),
                "files_url": "/static/challenges/hidden_message.txt",
                "estimated_time": 10,
                "learning_objectives": json.dumps([
                    "Understand the concept of steganography",
                    "Learn acrostic text hiding techniques",
                    "Develop attention to detail skills"
                ])
            },

            # MEDIUM CHALLENGES - More complex, multiple steps
            {
                "title": "XOR Warriors",
                "slug": "xor-warriors",
                "description": """Master the XOR operation - a fundamental building block of modern cryptography!

WHAT IS XOR?
XOR (exclusive OR) is a binary operation:
- 0 XOR 0 = 0
- 0 XOR 1 = 1
- 1 XOR 0 = 1
- 1 XOR 1 = 0

KEY PROPERTY:
A XOR B XOR B = A
This means XOR encryption can be reversed using the same key!

YOUR MISSION:
The challenge file contains a hex-encoded message that was XOR'd with a single-byte key.

APPROACH:
1. Convert hex to bytes
2. Try XOR with all possible single-byte keys (0-255)
3. Look for readable output starting with "FLAG"

This technique is called a "brute force" attack on single-byte XOR.""",
                "category_id": categories["Cryptography"].id,
                "difficulty": DifficultyLevel.MEDIUM,
                "points": 150,
                "flag": "FLAG{xor_is_your_friend}",
                "hints": json.dumps([
                    "The key is a single printable ASCII character (32-126)",
                    "Write a script to try all 256 possible keys",
                    "Check if the decrypted result starts with 'FLAG' and is printable text"
                ]),
                "tags": json.dumps(["crypto", "xor", "bruteforce", "medium"]),
                "files_url": "/static/challenges/xor_challenge.txt",
                "estimated_time": 20,
                "learning_objectives": json.dumps([
                    "Understand XOR encryption fundamentals",
                    "Learn brute-force attack methodology",
                    "Practice writing cryptanalysis scripts"
                ])
            },
            {
                "title": "SQL Injection 101",
                "slug": "sql-injection-101",
                "description": """SQL Injection is one of the most common and dangerous web vulnerabilities!

WHAT IS SQL INJECTION?
When user input is inserted directly into SQL queries without proper validation, attackers can manipulate the query logic.

EXAMPLE:
A login form might use:
SELECT * FROM users WHERE username='$user' AND password='$pass'

If you enter: admin' --
The query becomes:
SELECT * FROM users WHERE username='admin' -- ' AND password='...'

The -- comments out the rest, bypassing the password check!

YOUR MISSION:
Visit the challenge URL and find a way to bypass the login form.

COMMON TECHNIQUES:
- ' OR '1'='1
- admin' --
- ' OR 1=1 --

Think about how the input becomes part of the SQL query!

Note: This is a simulated challenge - the flag is: FLAG{sql_injection_master}""",
                "category_id": categories["Web Security"].id,
                "difficulty": DifficultyLevel.MEDIUM,
                "points": 100,
                "flag": "FLAG{sql_injection_master}",
                "hints": json.dumps([
                    "Try adding a single quote ' to see if you get an error",
                    "Use: ' OR '1'='1 to make the condition always true",
                    "Try: admin' -- to comment out the password check"
                ]),
                "tags": json.dumps(["web", "sql", "injection", "authentication"]),
                "estimated_time": 15,
                "learning_objectives": json.dumps([
                    "Understand how SQL injection works",
                    "Learn to identify vulnerable input fields",
                    "Know how to prevent SQL injection in your code"
                ])
            },
            {
                "title": "Cookie Monster",
                "slug": "cookie-monster",
                "description": """Web cookies store session information - but what if they're not secure?

ABOUT COOKIES:
Cookies are small pieces of data stored in your browser. They're used for:
- Session management
- User preferences
- Tracking

SECURITY CONCERNS:
- Cookies without HttpOnly flag can be stolen via XSS
- Cookies without Secure flag are sent over HTTP
- Predictable session IDs can be guessed

YOUR CHALLENGE:
Examine how cookies are being used to manage user roles. The flag is hidden in an insecure cookie implementation.

TOOLS YOU'LL NEED:
- Browser Developer Tools (F12)
- Look at Application > Cookies
- Try modifying cookie values

Simulated flag: FLAG{cookies_are_not_secure}""",
                "category_id": categories["Web Security"].id,
                "difficulty": DifficultyLevel.MEDIUM,
                "points": 125,
                "flag": "FLAG{cookies_are_not_secure}",
                "hints": json.dumps([
                    "Open Developer Tools (F12) and go to Application > Cookies",
                    "Look for cookies that might control user privileges",
                    "Try changing the cookie value - can you become admin?"
                ]),
                "tags": json.dumps(["web", "cookies", "session", "authentication"]),
                "estimated_time": 15,
                "learning_objectives": json.dumps([
                    "Understand web cookie security",
                    "Learn to use browser developer tools",
                    "Recognize insecure session management"
                ])
            },

            # HARD CHALLENGES - Complex, require research
            {
                "title": "Hash Cracker",
                "slug": "hash-cracker",
                "description": """Cryptographic hash functions are one-way functions - or are they?

ABOUT HASHES:
Hash functions take input and produce a fixed-size output (digest):
- MD5: 128 bits (32 hex characters)
- SHA-1: 160 bits (40 hex characters)
- SHA-256: 256 bits (64 hex characters)

PROPERTIES:
- Deterministic: Same input = same output
- One-way: Cannot reverse to get input
- Collision-resistant: Hard to find two inputs with same hash

CRACKING HASHES:
While you can't reverse a hash mathematically, you can:
- Use rainbow tables (pre-computed hashes)
- Try dictionary attacks
- Use online hash crackers

YOUR CHALLENGE:
Crack these MD5 hashes to find the flag components:

Hash 1: 5f4dcc3b5aa765d61d8327deb882cf99
Hash 2: e99a18c428cb38d5f260853678922e03

Combine: FLAG{word1_word2}""",
                "category_id": categories["Cryptography"].id,
                "difficulty": DifficultyLevel.HARD,
                "points": 200,
                "flag": "FLAG{password_abc123}",
                "hints": json.dumps([
                    "These are MD5 hashes of common passwords",
                    "Try online MD5 cracking tools like crackstation.net",
                    "The passwords are common dictionary words"
                ]),
                "tags": json.dumps(["crypto", "hash", "md5", "cracking"]),
                "estimated_time": 25,
                "learning_objectives": json.dumps([
                    "Understand cryptographic hash functions",
                    "Learn about hash cracking techniques",
                    "Recognize weak password risks"
                ])
            },
            {
                "title": "Packet Detective",
                "slug": "packet-detective",
                "description": """Network forensics involves analyzing captured network traffic to find evidence.

ABOUT PACKET CAPTURE:
Network packets contain headers and data. Tools like Wireshark can capture and analyze this traffic.

COMMON PROTOCOLS TO ANALYZE:
- HTTP: Web traffic (look for POST data, cookies)
- FTP: File transfers (often unencrypted!)
- DNS: Domain lookups
- TCP: Connection data

YOUR MISSION:
A network capture file contains evidence of data exfiltration.
Find the stolen flag hidden in the network traffic.

ANALYSIS TIPS:
1. Open the pcap in Wireshark
2. Use filters like: http, ftp, tcp.port == 80
3. Follow TCP streams to see full conversations
4. Export objects from HTTP traffic

Simulated flag: FLAG{wireshark_wizard}""",
                "category_id": categories["Network Security"].id,
                "difficulty": DifficultyLevel.HARD,
                "points": 200,
                "flag": "FLAG{wireshark_wizard}",
                "hints": json.dumps([
                    "Download Wireshark if you don't have it",
                    "Filter by HTTP and look at the data",
                    "Right-click on a packet and select 'Follow TCP Stream'"
                ]),
                "tags": json.dumps(["network", "pcap", "wireshark", "forensics"]),
                "estimated_time": 30,
                "learning_objectives": json.dumps([
                    "Learn basic packet analysis skills",
                    "Understand common network protocols",
                    "Use Wireshark for network forensics"
                ])
            },
            {
                "title": "Binary Basics",
                "slug": "binary-basics",
                "description": """Reverse engineering helps us understand how software works!

ABOUT REVERSE ENGINEERING:
When you only have a compiled program (no source code), reverse engineering lets you:
- Understand program behavior
- Find security vulnerabilities
- Analyze malware

TOOLS OF THE TRADE:
- strings: Extract readable text from binaries
- objdump: Disassemble code
- Ghidra/IDA: Advanced disassemblers
- gdb: Debugger

YOUR CHALLENGE:
A simple program checks for a password. The password is hidden in the binary.

APPROACH:
1. Run 'strings' on the binary to find readable text
2. Look for suspicious strings that might be passwords or flags
3. The flag is stored as a simple string constant

For this simulated challenge: FLAG{reverse_engineering_ninja}""",
                "category_id": categories["Reverse Engineering"].id,
                "difficulty": DifficultyLevel.HARD,
                "points": 250,
                "flag": "FLAG{reverse_engineering_ninja}",
                "hints": json.dumps([
                    "Use the 'strings' command: strings filename | grep FLAG",
                    "The flag might be stored as a readable string in the binary",
                    "Look for patterns like FLAG{ or common password strings"
                ]),
                "tags": json.dumps(["reversing", "binary", "strings", "beginner-re"]),
                "estimated_time": 20,
                "learning_objectives": json.dumps([
                    "Learn to use the 'strings' utility",
                    "Understand how data is stored in binaries",
                    "Introduction to reverse engineering concepts"
                ])
            },

            # EXPERT CHALLENGES
            {
                "title": "Memory Forensics",
                "slug": "memory-forensics",
                "description": """Analyze computer memory to find hidden evidence!

ABOUT MEMORY FORENSICS:
RAM contains a wealth of information:
- Running processes
- Network connections
- Encryption keys
- Recently typed text

TOOLS:
- Volatility: The go-to memory analysis framework
- Rekall: Alternative memory forensics tool

COMMON VOLATILITY PLUGINS:
- pslist: Show running processes
- netscan: Show network connections
- hashdump: Extract password hashes
- filescan: Find files in memory

YOUR MISSION:
A memory dump contains evidence of a compromised system.
Use forensic tools to extract the flag.

Simulated flag: FLAG{forensics_expert}""",
                "category_id": categories["Forensics"].id,
                "difficulty": DifficultyLevel.EXPERT,
                "points": 350,
                "flag": "FLAG{forensics_expert}",
                "hints": json.dumps([
                    "Install Volatility for memory analysis",
                    "First identify the memory profile with 'volatility imageinfo'",
                    "Try 'volatility strings' to find readable text"
                ]),
                "tags": json.dumps(["forensics", "memory", "volatility", "expert"]),
                "estimated_time": 45,
                "learning_objectives": json.dumps([
                    "Learn memory forensics fundamentals",
                    "Use Volatility framework",
                    "Extract evidence from memory dumps"
                ])
            }
        ]

        for chal_data in challenges_data:
            existing_chal = db.query(Challenge).filter(Challenge.slug == chal_data["slug"]).first()
            if existing_chal:
                # Update existing challenge
                for key, value in chal_data.items():
                    if key != 'category_id':
                        setattr(existing_chal, key, value)
                # Ensure status is ACTIVE
                existing_chal.status = ChallengeStatus.ACTIVE
                db.commit()
                print(f"Updated challenge: {chal_data['title']}")
            else:
                challenge = Challenge(**chal_data)
                challenge.status = ChallengeStatus.ACTIVE  # Set status to ACTIVE
                db.add(challenge)
                db.commit()
                db.refresh(challenge)
                print(f"Created challenge: {chal_data['title']} ({chal_data['difficulty']}, {chal_data['points']} points)")

        print("\n=== SUCCESS: Sample data created successfully! ===")
        print(f"Categories: {len(categories_data)}")
        print(f"Challenges: {len(challenges_data)}")

    except Exception as e:
        db.rollback()
        print(f"ERROR: Error creating sample data: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
