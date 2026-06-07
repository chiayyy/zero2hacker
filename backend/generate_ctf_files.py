"""
CTF Challenge File Generator
Generates proper challenge files for each challenge type.
Run: python generate_ctf_files.py
"""

import sqlite3
import os
import struct
import wave
import random
import hashlib
import zipfile
import io
from pathlib import Path
from PIL import Image, PngImagePlugin

BASE = Path(__file__).parent
STATIC = BASE / "static" / "challenges"
STATIC.mkdir(parents=True, exist_ok=True)

DB = BASE / "zero2hacker.db"
conn = sqlite3.connect(str(DB))

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def set_file_url(challenge_id: int, url: str):
    conn.execute("UPDATE challenges SET files_url=? WHERE id=?", (url, challenge_id))
    conn.commit()
    print(f"  [DB] Challenge {challenge_id} ->{url}")

def clear_file_url(challenge_id: int):
    conn.execute("UPDATE challenges SET files_url=NULL WHERE id=?", (challenge_id,))
    conn.commit()
    print(f"  [DB] Challenge {challenge_id} ->NULL (no file)")


# ─────────────────────────────────────────────────────────────
# 1. PNG WITH LSB STEGANOGRAPHY
#    Hides flag in least-significant bit of Red channel pixels
# ─────────────────────────────────────────────────────────────
def make_lsb_png(filepath: Path, flag: str):
    """Embed flag in LSB of a PNG image."""
    img = Image.new("RGB", (256, 256), color=(0, 0, 0))
    pixels = img.load()

    # Create a gradient so the image looks real
    for x in range(256):
        for y in range(256):
            pixels[x, y] = (x, y, (x + y) % 256)

    # Encode flag as bits into LSB of Red channel, row by row
    message = flag + "\x00"  # null terminator
    bits = []
    for ch in message:
        b = ord(ch)
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)

    idx = 0
    for y in range(256):
        for x in range(256):
            if idx >= len(bits):
                break
            r, g, b_val = pixels[x, y]
            r = (r & 0xFE) | bits[idx]
            pixels[x, y] = (r, g, b_val)
            idx += 1
        if idx >= len(bits):
            break

    img.save(str(filepath), "PNG")
    print(f"  [FILE] LSB PNG ->{filepath.name} (flag in LSB of red channel)")


# ─────────────────────────────────────────────────────────────
# 2. PNG WITH METADATA (EXIF/text chunk)
# ─────────────────────────────────────────────────────────────
def make_metadata_png(filepath: Path, flag: str):
    """Hide flag in PNG metadata Comment field."""
    img = Image.new("RGB", (300, 300))
    pixels = img.load()
    for x in range(300):
        for y in range(300):
            pixels[x, y] = ((x * 3) % 256, (y * 2) % 256, ((x + y) * 2) % 256)

    meta = PngImagePlugin.PngInfo()
    meta.add_text("Comment", f"Author: CTF Challenge System | Version: 1.0 | {flag}")
    meta.add_text("Description", "Challenge image - investigate all properties carefully")
    meta.add_text("Software", "Zero2Hacker CTF Platform v5.0")

    img.save(str(filepath), "PNG", pnginfo=meta)
    print(f"  [FILE] Metadata PNG ->{filepath.name} (flag in Comment text chunk)")


# ─────────────────────────────────────────────────────────────
# 3. WAV WITH LSB STEGANOGRAPHY
# ─────────────────────────────────────────────────────────────
def make_lsb_wav(filepath: Path, flag: str):
    """Embed flag in LSB of WAV audio samples."""
    sample_rate = 44100
    duration = 3  # seconds
    num_samples = sample_rate * duration

    # Generate sine wave audio (440 Hz)
    import math
    samples = []
    for i in range(num_samples):
        val = int(32767 * math.sin(2 * math.pi * 440 * i / sample_rate))
        samples.append(val)

    # Encode flag bits into LSB of samples
    message = flag + "\x00"
    bits = []
    for ch in message:
        b = ord(ch)
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)

    for i, bit in enumerate(bits):
        if i < len(samples):
            samples[i] = (samples[i] & ~1) | bit

    # Write WAV
    with wave.open(str(filepath), 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        raw = struct.pack(f'<{num_samples}h', *samples)
        wf.writeframes(raw)

    print(f"  [FILE] LSB WAV ->{filepath.name} (flag in LSB of audio samples)")


# ─────────────────────────────────────────────────────────────
# 4. BINARY WITH STRINGS (reverse engineering via `strings`)
# ─────────────────────────────────────────────────────────────
def make_strings_binary(filepath: Path, flag: str):
    """Create binary where flag is visible via `strings` command."""
    # Fake ELF-like binary header + junk + flag as null-terminated string
    elf_magic = b'\x7fELF\x02\x01\x01\x00' + b'\x00' * 8
    random.seed(42)
    junk1 = bytes([random.randint(0, 255) for _ in range(512)])
    # Embed some fake strings to make it look real
    fake_strings = (
        b"main\x00"
        b"printf\x00"
        b"strcmp\x00"
        b"Enter the secret key: \x00"
        b"Access Denied!\x00"
        b"Checking credentials...\x00"
    )
    flag_bytes = flag.encode() + b'\x00'
    # XOR the flag slightly so it's not immediately obvious — students use strings, see hint
    padding = bytes([random.randint(0x20, 0x7e) for _ in range(128)])
    junk2 = bytes([random.randint(0, 255) for _ in range(256)])

    data = elf_magic + junk1 + fake_strings + padding + flag_bytes + junk2
    filepath.write_bytes(data)
    print(f"  [FILE] Strings binary ->{filepath.name} (flag visible via `strings`)")


# ─────────────────────────────────────────────────────────────
# 5. BINARY WITH XOR-OBFUSCATED FLAG (reverse engineering)
# ─────────────────────────────────────────────────────────────
def make_xor_binary(filepath: Path, flag: str, xor_key: int = 0xAB):
    """Binary where flag is XOR-encoded. Must reverse the XOR to get flag."""
    xored = bytes([b ^ xor_key for b in flag.encode()])
    random.seed(99)
    junk1 = bytes([random.randint(0, 255) for _ in range(256)])
    # Embed hint
    hint = f"XOR key: 0x{xor_key:02X} — decode the secret block below\x00".encode()
    length_marker = struct.pack('<I', len(xored))  # 4-byte little-endian length
    junk2 = bytes([random.randint(0, 255) for _ in range(128)])

    data = junk1 + b'SECRETBLOCK\x00' + length_marker + xored + hint + junk2
    filepath.write_bytes(data)
    print(f"  [FILE] XOR binary ->{filepath.name} (flag XORed with 0x{xor_key:02X})")


# ─────────────────────────────────────────────────────────────
# 6. HASH FILE (crypto — crack the hash)
# ─────────────────────────────────────────────────────────────
def make_hash_file(filepath: Path, flag: str):
    """
    Flag is FLAG{password_abc123}.
    Create a file with MD5 and SHA256 hashes of common passwords.
    The flag's inner value 'abc123' can be cracked from MD5.
    """
    password = "abc123"
    md5 = hashlib.md5(password.encode()).hexdigest()
    sha256 = hashlib.sha256(password.encode()).hexdigest()
    sha1 = hashlib.sha1(password.encode()).hexdigest()

    content = f"""=== INTERCEPTED CREDENTIALS ===
Target System: internal.corp.local
Date: 2024-03-15 03:42:17 UTC

User: admin
MD5:    {md5}
SHA1:   {sha1}
SHA256: {sha256}

User: backup_svc
MD5:    {hashlib.md5(b'backup2024').hexdigest()}
SHA1:   {hashlib.sha1(b'backup2024').hexdigest()}
SHA256: {hashlib.sha256(b'backup2024').hexdigest()}

NOTE: Hashes extracted from /etc/shadow equivalent.
Crack the admin password hash to obtain the flag.
Flag format: FLAG{{<cracked_password>}}
"""
    filepath.write_text(content)
    print(f"  [FILE] Hash file ->{filepath.name} (crack MD5 of '{password}' ->{md5})")


# ─────────────────────────────────────────────────────────────
# 7. PCAP FILE (network forensics)
#    Minimal valid PCAP with HTTP containing the flag
# ─────────────────────────────────────────────────────────────
def make_pcap(filepath: Path, flag: str):
    """Create minimal PCAP with HTTP traffic hiding the flag."""

    def pcap_global_header():
        # magic, ver_major, ver_minor, thiszone, sigfigs, snaplen, network(1=ethernet)
        return struct.pack('<IHHiIII', 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)

    def pcap_packet(data: bytes, ts_sec=1710000000, ts_usec=0):
        return struct.pack('<IIII', ts_sec, ts_usec, len(data), len(data)) + data

    def ethernet_ip_tcp(payload: bytes, ts_sec=1710000000):
        # Ethernet header (dst, src, type=0x0800)
        eth = b'\xff\xff\xff\xff\xff\xff' + b'\x00\x0c\x29\xaa\xbb\xcc' + b'\x08\x00'
        # IP header (minimal, no options)
        ip_len = 20 + 20 + len(payload)
        ip = struct.pack('>BBHHHBBH4s4s',
            0x45, 0, ip_len, 1, 0, 64, 6,  # TTL=64, proto=TCP
            0,  # checksum (0 = not computed)
            b'\xc0\xa8\x01\x64',  # src 192.168.1.100
            b'\xc0\xa8\x01\x01',  # dst 192.168.1.1
        )
        # TCP header (src=12345, dst=80, seq=1, ack=1, flags=PSH+ACK)
        tcp = struct.pack('>HHIIBBHHH',
            12345, 80, 1, 1,
            0x50, 0x18,  # data offset=5, flags=PSH+ACK
            65535, 0, 0  # window, checksum, urgent
        )
        return pcap_packet(eth + ip + tcp + payload, ts_sec)

    # HTTP GET request (client ->server)
    http_req = (
        b"GET /login HTTP/1.1\r\n"
        b"Host: internal.corp.local\r\n"
        b"User-Agent: Mozilla/5.0\r\n"
        b"Connection: keep-alive\r\n\r\n"
    )
    # HTTP response with flag in a Set-Cookie or custom header
    http_resp = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: text/html\r\n"
        b"Server: Apache/2.4.51\r\n"
        b"X-Debug-Token: " + flag.encode() + b"\r\n"
        b"Set-Cookie: session=eyJ1c2VyIjoiYWRtaW4ifQ==; Path=/\r\n"
        b"\r\n"
        b"<html><body>Login successful</body></html>\r\n"
    )

    pcap_data = (
        pcap_global_header() +
        ethernet_ip_tcp(http_req, ts_sec=1710000000) +
        ethernet_ip_tcp(http_resp, ts_sec=1710000001)
    )
    filepath.write_bytes(pcap_data)
    print(f"  [FILE] PCAP ->{filepath.name} (flag in X-Debug-Token HTTP header)")


# ─────────────────────────────────────────────────────────────
# 8. BMP POLYGLOT (BMP + ZIP appended)
# ─────────────────────────────────────────────────────────────
def make_polyglot_bmp(filepath: Path, flag: str):
    """BMP file with a ZIP archive appended. Use binwalk/foremost to extract."""
    # Create BMP in memory
    img = Image.new("RGB", (100, 100), color=(128, 64, 192))
    pixels = img.load()
    for x in range(100):
        for y in range(100):
            pixels[x, y] = (x * 2, y * 2, 200)
    buf = io.BytesIO()
    img.save(buf, format="BMP")
    bmp_data = buf.getvalue()

    # Create ZIP in memory containing flag.txt
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("flag.txt", f"Congratulations! You found the hidden archive!\n{flag}\n")
        zf.writestr("README.txt", "This file was hidden inside a BMP image.\nUse binwalk or foremost to extract archives from binary files.\n")
    zip_data = zip_buf.getvalue()

    filepath.write_bytes(bmp_data + zip_data)
    print(f"  [FILE] Polyglot BMP+ZIP ->{filepath.name} (extract with binwalk/foremost/unzip)")


# ─────────────────────────────────────────────────────────────
# 9. FILE WITH WRONG MAGIC BYTES (file identity crisis)
# ─────────────────────────────────────────────────────────────
def make_wrong_magic(filepath: Path, flag: str):
    """A PNG file saved with .txt extension. Check magic bytes to identify."""
    img = Image.new("RGB", (150, 150))
    pixels = img.load()
    for x in range(150):
        for y in range(150):
            pixels[x, y] = ((x + y) % 256, x % 256, y % 256)

    meta = PngImagePlugin.PngInfo()
    meta.add_text("Flag", flag)
    meta.add_text("Hint", "This isn't what it appears to be. Check the magic bytes.")

    buf = io.BytesIO()
    img.save(buf, "PNG", pnginfo=meta)
    png_data = buf.getvalue()

    # Save as .png extension but description says .txt, so student must identify
    filepath.write_bytes(png_data)
    print(f"  [FILE] Wrong magic ->{filepath.name} (PNG data, flag in metadata)")


# ─────────────────────────────────────────────────────────────
# 10. MEMORY DUMP (forensics)
# ─────────────────────────────────────────────────────────────
def make_memory_dump(filepath: Path, flag: str):
    """Simulated memory dump with flag at a specific address."""
    random.seed(7)

    def heap_block(data: bytes) -> bytes:
        size = len(data) + random.randint(8, 64)
        header = struct.pack('<QQ', size, 0x1)  # size, flags
        padding = bytes([random.randint(0, 255) for _ in range(size - len(data))])
        return header + data + padding

    # Simulate memory regions
    stack_garbage = bytes([random.randint(0, 255) for _ in range(1024)])
    heap_strings = (
        heap_block(b"username=admin\x00") +
        heap_block(b"session_token=a3f9b2c1d4e5\x00") +
        heap_block(b"database_host=db.internal\x00") +
        heap_block(b"[PROCESS: ctf_server PID:1337]\x00") +
        heap_block(flag.encode() + b'\x00') +
        heap_block(b"kernel_version=5.15.0\x00")
    )
    more_garbage = bytes([random.randint(0, 255) for _ in range(2048)])
    env_vars = (
        b"PATH=/usr/local/bin:/usr/bin:/bin\x00"
        b"HOME=/root\x00"
        b"SHELL=/bin/bash\x00"
        b"SECRET_KEY=not_the_flag_keep_looking\x00"
        b"TERM=xterm-256color\x00"
    )

    dump = stack_garbage + heap_strings + more_garbage + env_vars + more_garbage[:512]
    filepath.write_bytes(dump)
    print(f"  [FILE] Memory dump ->{filepath.name} (flag embedded in simulated heap)")


# ─────────────────────────────────────────────────────────────
# 11. XOR ENCODED FILE (crypto challenge)
# ─────────────────────────────────────────────────────────────
def make_xor_file(filepath: Path, flag: str, key: int = 0x42):
    """Text file with XOR-encoded content. Decode with key 0x42."""
    plaintext = f"TOP SECRET TRANSMISSION\nDecryption key: 0x{key:02X}\nPayload: {{encoded_below}}\n\nMission briefing:\nAgent, the following data has been encrypted using a simple XOR cipher.\nApply the key to each byte to reveal the secret.\n\n--- BEGIN ENCODED DATA ---\n"
    encoded = bytes([b ^ key for b in flag.encode()])
    hex_dump = ' '.join(f'{b:02X}' for b in encoded)
    footer = "\n--- END ENCODED DATA ---\n"

    content = plaintext.encode() + hex_dump.encode() + footer.encode()
    filepath.write_bytes(content)
    print(f"  [FILE] XOR file ->{filepath.name} (flag XORed with 0x{key:02X}, shown as hex)")


# ─────────────────────────────────────────────────────────────
# 12. HEX DUMP FILE (memory analysis)
# ─────────────────────────────────────────────────────────────
def make_hex_dump(filepath: Path, flag: str):
    """File with hex dump format. Flag visible as ASCII in hex dump."""
    random.seed(55)

    def hex_line(offset: int, data: bytes) -> str:
        hex_part = ' '.join(f'{b:02x}' for b in data)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data)
        return f"{offset:08x}  {hex_part:<47}  |{ascii_part}|"

    lines = [
        "Memory dump analysis - Target: PID 4721",
        f"Timestamp: 2024-03-15 09:23:44 UTC",
        "=" * 65,
        "",
    ]
    offset = 0
    # Random data before flag
    for _ in range(16):
        chunk = bytes([random.randint(0, 255) for _ in range(16)])
        lines.append(hex_line(offset, chunk))
        offset += 16
    # Flag data
    flag_bytes = flag.encode()
    for i in range(0, len(flag_bytes), 16):
        chunk = flag_bytes[i:i+16]
        lines.append(hex_line(offset, chunk))
        offset += 16
    # More random data after
    for _ in range(16):
        chunk = bytes([random.randint(0, 255) for _ in range(16)])
        lines.append(hex_line(offset, chunk))
        offset += 16

    lines += ["", "=" * 65, "End of dump segment"]
    filepath.write_text('\n'.join(lines))
    print(f"  [FILE] Hex dump ->{filepath.name} (flag visible as ASCII in hex dump)")


# ─────────────────────────────────────────────────────────────
# MAIN: Generate all files & update DB
# ─────────────────────────────────────────────────────────────

challenges = {row[0]: row for row in conn.execute(
    "SELECT id, title, difficulty, flag, files_url, (SELECT name FROM categories WHERE id=category_id) FROM challenges"
).fetchall()}

print("\n=== CTF Challenge File Generator ===\n")

# ── CRYPTO ──────────────────────────────────────────────────

# Simple encode/decode — NO FILE, flag/challenge in description
for cid in [1, 2, 19, 26, 27, 28, 30, 31, 32, 16, 18]:
    if cid in challenges:
        print(f"\n[Crypto #{cid}] {challenges[cid][1]} — no file needed (text decode)")
        clear_file_url(cid)

# XOR Warriors (MEDIUM) — proper XOR encoded file
print(f"\n[Crypto #4] XOR Warriors — generating XOR file")
p = STATIC / "xor_warriors.bin"
make_xor_file(p, challenges[4][3], key=0x42)
set_file_url(4, "/files/challenges/xor_warriors.bin")

# Hash Cracker (HARD) — hash file
print(f"\n[Crypto #7] Hash Cracker — generating hash file")
p = STATIC / "hash_cracker.txt"
make_hash_file(p, challenges[7][3])
set_file_url(7, "/files/challenges/hash_cracker.txt")

# ── FORENSICS ───────────────────────────────────────────────

# File Identity Crisis (EASY) — wrong magic bytes
print(f"\n[Forensics #17] File Identity Crisis — generating wrong-magic file")
p = STATIC / "not_what_it_seems.png"
make_wrong_magic(p, challenges[17][3])
set_file_url(17, "/files/challenges/not_what_it_seems.png")

# Memory Analysis (MEDIUM) — hex dump
print(f"\n[Forensics #14] Memory Analysis — generating hex dump")
p = STATIC / "memory_dump.txt"
make_hex_dump(p, challenges[14][3])
set_file_url(14, "/files/challenges/memory_dump.txt")

# Polyglot Puzzle (MEDIUM) — BMP + ZIP
print(f"\n[Forensics #13] Polyglot Puzzle — generating polyglot BMP")
p = STATIC / "innocent_picture.bmp"
make_polyglot_bmp(p, challenges[13][3])
set_file_url(13, "/files/challenges/innocent_picture.bmp")

# Audio Forensics (MEDIUM) — LSB WAV
print(f"\n[Forensics #15] Audio Forensics — generating LSB WAV")
p = STATIC / "secret_audio.wav"
make_lsb_wav(p, challenges[15][3])
set_file_url(15, "/files/challenges/secret_audio.wav")

# Memory Forensics (EXPERT) — memory dump
print(f"\n[Forensics #10] Memory Forensics — generating memory dump")
p = STATIC / "memory_forensics.bin"
make_memory_dump(p, challenges[10][3])
set_file_url(10, "/files/challenges/memory_forensics.bin")

# ── STEGANOGRAPHY ────────────────────────────────────────────

# Hidden in Plain Sight (BEGINNER) — LSB PNG
print(f"\n[Steg #3] Hidden in Plain Sight — generating LSB PNG")
p = STATIC / "hidden_message.png"
make_lsb_png(p, challenges[3][3])
set_file_url(3, "/files/challenges/hidden_message.png")

# Metadata Hunter (EASY) — metadata PNG
print(f"\n[Steg #11] Metadata Hunter — generating metadata PNG")
p = STATIC / "mysterious_image.png"
make_metadata_png(p, challenges[11][3])
set_file_url(11, "/files/challenges/mysterious_image.png")

# ── REVERSE ENGINEERING ──────────────────────────────────────

# Binary Secrets (EASY) — strings binary
print(f"\n[RE #12] Binary Secrets — generating strings binary")
p = STATIC / "mystery_program.bin"
make_strings_binary(p, challenges[12][3])
set_file_url(12, "/files/challenges/mystery_program.bin")

# Binary Basics (HARD) — XOR binary
print(f"\n[RE #9] Binary Basics — generating XOR binary")
p = STATIC / "binary_basics.bin"
make_xor_binary(p, challenges[9][3], xor_key=0x37)
set_file_url(9, "/files/challenges/binary_basics.bin")

# ── NETWORK SECURITY ─────────────────────────────────────────

# Packet Detective (HARD) — PCAP
print(f"\n[Net #8] Packet Detective — generating PCAP")
p = STATIC / "network_capture.pcap"
make_pcap(p, challenges[8][3])
set_file_url(8, "/files/challenges/network_capture.pcap")

# ── CLEANUP: generated duplicates ───────────────────────────
print("\n[Cleanup] Removing duplicate/unnecessary generated challenges")
for cid in [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]:
    if cid in challenges:
        clear_file_url(cid)

conn.close()

print("\n=== Done! All CTF files generated. ===\n")
print("Summary:")
print("  Crypto  : XOR Warriors (xor file), Hash Cracker (hash file)")
print("  Forensics: File Identity Crisis, Memory Analysis, Polyglot BMP, Audio Forensics, Memory Forensics")
print("  Steg    : Hidden in Plain Sight (LSB PNG), Metadata Hunter (metadata PNG)")
print("  RE      : Binary Secrets (strings), Binary Basics (XOR binary)")
print("  Network : Packet Detective (PCAP)")
print("  No file : All simple crypto encode/decode + web security challenges")
