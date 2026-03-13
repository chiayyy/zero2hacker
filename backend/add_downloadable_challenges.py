"""
Script to add downloadable CTF challenges to the database
These challenges require external tools to solve
"""

from sqlalchemy import create_engine, text
from app.core.config import settings

# Challenge data for downloadable files
downloadable_challenges = [
    {
        "title": "Metadata Hunter",
        "slug": "metadata-hunter",
        "description": "An image file has been intercepted from a suspect's computer. Intelligence suggests there's a hidden message in the file. Download the image and examine it carefully - sometimes secrets hide in plain sight, just not where you'd expect to look.",
        "category_id": 6,  # Steganography
        "difficulty": "easy",
        "points": 150,
        "flag": "FLAG{metadata_matters}",
        "hints": '["Think about what information is stored alongside the image data", "Try using the strings command or exiftool", "Check the PNG chunks for text data"]',
        "files_url": "http://localhost:8000/static/challenges/mysterious_image.png",
        "learning_objectives": '["Understanding file metadata", "Using forensic tools", "PNG file structure"]',
        "tools_required": '["strings", "exiftool", "pngcheck"]'
    },
    {
        "title": "Binary Secrets",
        "slug": "binary-secrets",
        "description": "A mysterious binary file was found on a compromised server. Your mission is to extract any readable information from this file. Sometimes, the simplest tools reveal the biggest secrets.",
        "category_id": 3,  # Reversing
        "difficulty": "easy",
        "points": 150,
        "flag": "FLAG{strings_reveal_secrets}",
        "hints": '["Binary files often contain readable text", "The strings command extracts readable characters", "Look for anything that looks like a flag format"]',
        "files_url": "http://localhost:8000/static/challenges/mystery_program.bin",
        "learning_objectives": '["Using strings command", "Basic reverse engineering", "Binary file analysis"]',
        "tools_required": '["strings", "hexdump"]'
    },
    {
        "title": "Polyglot Puzzle",
        "slug": "polyglot-puzzle",
        "description": "This image looks innocent, but our analysts suspect there's more to it than meets the eye. Download the file and investigate - could there be something hidden within or beyond the image data?",
        "category_id": 4,  # Forensics
        "difficulty": "medium",
        "points": 250,
        "flag": "FLAG{hidden_archive_found}",
        "hints": '["A file can be valid in multiple formats at once", "Try tools like binwalk to scan for embedded files", "Check if there is data after the image ends"]',
        "files_url": "http://localhost:8000/static/challenges/innocent_picture.bmp",
        "learning_objectives": '["Polyglot files", "File carving", "Using binwalk"]',
        "tools_required": '["binwalk", "foremost", "dd"]'
    },
    {
        "title": "Memory Analysis",
        "slug": "memory-analysis",
        "description": "A memory dump has been captured from a target system. Somewhere in this hex dump lies the information we need. Can you decode the raw memory data and find the hidden flag?",
        "category_id": 4,  # Forensics
        "difficulty": "medium",
        "points": 200,
        "flag": "FLAG{hex_dump_decoded}",
        "hints": '["The flag is encoded in hexadecimal", "Look at the ASCII column for readable text", "Convert hex bytes to ASCII characters"]',
        "files_url": "http://localhost:8000/static/challenges/memory_dump.txt",
        "learning_objectives": '["Reading hex dumps", "Hex to ASCII conversion", "Memory forensics basics"]',
        "tools_required": '["xxd", "hex editor", "CyberChef"]'
    },
    {
        "title": "Audio Forensics",
        "slug": "audio-forensics",
        "description": "An audio file was recovered from a suspect's device. While it sounds like a simple tone, forensic analysis suggests there might be hidden data. Download the file and investigate beyond what you can hear.",
        "category_id": 4,  # Forensics
        "difficulty": "medium",
        "points": 200,
        "flag": "FLAG{audio_secrets_revealed}",
        "hints": '["Audio files can contain more than just sound", "Try using strings on the audio file", "Check for data appended after the audio content"]',
        "files_url": "http://localhost:8000/static/challenges/secret_audio.wav",
        "learning_objectives": '["Audio file structure", "File analysis beyond content", "WAV format understanding"]',
        "tools_required": '["strings", "exiftool", "Audacity"]'
    },
    {
        "title": "Layer Cake",
        "slug": "layer-cake",
        "description": "An encrypted transmission has been intercepted. Our cryptanalysts have determined that the message has been encoded multiple times for extra security. Peel back all the layers to reveal the secret.",
        "category_id": 1,  # Cryptography
        "difficulty": "easy",
        "points": 150,
        "flag": "FLAG{decode_all_layers}",
        "hints": '["The message uses base64 encoding", "It has been encoded 5 times", "Keep decoding until you see readable text"]',
        "files_url": "http://localhost:8000/static/challenges/encoded_transmission.txt",
        "learning_objectives": '["Base64 encoding", "Multi-layer encoding", "Using CyberChef"]',
        "tools_required": '["base64", "CyberChef", "Python"]'
    },
    {
        "title": "File Identity Crisis",
        "slug": "file-identity-crisis",
        "description": "This file claims to be a text document, but something seems off. In the world of forensics, you can't always trust file extensions. Investigate the true nature of this file to find the flag.",
        "category_id": 4,  # Forensics
        "difficulty": "easy",
        "points": 150,
        "flag": "FLAG{file_signatures_matter}",
        "hints": '["File extensions can lie", "Use the file command to check the true type", "Look at the magic bytes (first few bytes of the file)"]',
        "files_url": "http://localhost:8000/static/challenges/not_what_it_seems.txt",
        "learning_objectives": '["File signatures/magic bytes", "Using file command", "Understanding file types"]',
        "tools_required": '["file", "hexdump", "xxd"]'
    },
    {
        "title": "Agency Protocol",
        "slug": "agency-protocol",
        "description": "A classified document has been leaked, but the intelligence is encoded using the agency's standard rotation protocol. The document contains a hint about the encoding method. Decode the message to retrieve the flag.",
        "category_id": 1,  # Cryptography
        "difficulty": "easy",
        "points": 100,
        "flag": "FLAG{rotation_cipher_solved}",
        "hints": '["The document mentions rotation and the number 13", "ROT13 rotates each letter by 13 positions", "Use tr command: tr A-Za-z N-ZA-Mn-za-m"]',
        "files_url": "http://localhost:8000/static/challenges/classified_report.txt",
        "learning_objectives": '["ROT13 cipher", "Simple substitution ciphers", "Using tr command"]',
        "tools_required": '["tr", "CyberChef", "rot13 decoder"]'
    }
]

def add_challenges():
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        for challenge in downloadable_challenges:
            # Check if challenge already exists
            result = conn.execute(
                text("SELECT id FROM challenges WHERE slug = :slug"),
                {"slug": challenge["slug"]}
            )
            existing = result.fetchone()

            if existing:
                print(f"Challenge '{challenge['title']}' already exists, updating...")
                conn.execute(
                    text("""
                        UPDATE challenges SET
                            title = :title,
                            description = :description,
                            category_id = :category_id,
                            difficulty = :difficulty,
                            points = :points,
                            flag = :flag,
                            hints = :hints,
                            files_url = :files_url,
                            learning_objectives = :learning_objectives,
                            status = 'published'
                        WHERE slug = :slug
                    """),
                    challenge
                )
            else:
                print(f"Adding new challenge: {challenge['title']}")
                conn.execute(
                    text("""
                        INSERT INTO challenges (
                            title, slug, description, category_id, difficulty,
                            points, flag, hints, files_url, learning_objectives, status
                        ) VALUES (
                            :title, :slug, :description, :category_id, :difficulty,
                            :points, :flag, :hints, :files_url, :learning_objectives, 'published'
                        )
                    """),
                    challenge
                )

        conn.commit()
        print("\nAll downloadable challenges added successfully!")

        # Display all challenges
        print("\n=== All Challenges in Database ===")
        result = conn.execute(text("""
            SELECT c.id, c.title, c.difficulty, c.points, c.files_url, cat.name as category
            FROM challenges c
            LEFT JOIN categories cat ON c.category_id = cat.id
            ORDER BY c.id
        """))

        for row in result:
            file_status = "HAS FILE" if row[4] else "No file"
            print(f"{row[0]:2}. [{row[5]}] {row[1]} ({row[2]}, {row[3]} pts) - {file_status}")


if __name__ == "__main__":
    add_challenges()
