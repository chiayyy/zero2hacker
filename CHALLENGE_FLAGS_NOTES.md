# Zero2Hacker CTF — All Flags & Solution Steps

> Admin reference only. Total: 28 challenges, 3980 points.

---

## CRYPTOGRAPHY

| # | Title | Difficulty | Points | Flag |
|---|-------|-----------|--------|------|
| 1 | Caesar's Secret | BEGINNER | 50 | `FLAG{caesar_was_here}` |
| 2 | Base64 Basics | BEGINNER | 50 | `FLAG{base64_decoding_rocks}` |
| 19 | XOR Chaos | BEGINNER | 60 | `FLAG{XORSECRET_F4632A}` |
| 26 | Base64 Bonanza (Caesar lab) | BEGINNER | 40 | `FLAG{ENCODED_1A2632}` |
| 27 | Caesar's Secret (Caesar lab) | BEGINNER | 50 | `FLAG{HIDDEN_D96BE5}` |
| 28 | Base64 Bonanza (Caesar lab) | BEGINNER | 40 | `FLAG{ENCODED_4CC419}` |
| 18 | Agency Protocol | EASY | 100 | `FLAG{rotation_cipher_solved}` |
| 16 | Layer Cake | EASY | 150 | `FLAG{decode_all_layers}` |
| 4 | XOR Warriors | MEDIUM | 150 | `FLAG{xor_is_your_friend}` |
| 7 | Hash Cracker | HARD | 200 | `FLAG{password_abc123}` |

### Steps
- **Caesar / ROT13** — shift letters backwards; try all 25 shifts or use ROT13
- **Base64** — decode with `base64.b64decode()` in Python or any online tool
- **XOR** — brute-force all 256 single-byte keys; correct key reveals `FLAG{`
- **Layer Cake** — base64-decode 5 times in a loop
- **Hash Cracker** — paste MD5 hash into crackstation.net

---

## WEB SECURITY

| # | Title | Difficulty | Points | Flag |
|---|-------|-----------|--------|------|
| 5 | SQL Injection 101 | MEDIUM | 100 | `FLAG{sql_injection_master}` |
| 6 | Cookie Monster | MEDIUM | 125 | `FLAG{cookies_are_not_secure}` |
| 20 | Reflected Mayhem (Base64 lab) | BEGINNER | 75 | `FLAG{XSSWIN_32D869}` |
| 21 | Reflected Mayhem (Base64 lab) | BEGINNER | 75 | `FLAG{XSSWIN_70E519}` |
| 22 | Reflected Mayhem (Base64 lab) | HARD | 200 | `FLAG{XSSWIN_E77A2E}` |
| 25 | Reflected Mayhem (SQL lab) | MEDIUM | 150 | `FLAG{XSSWIN_AB576F}` |

### Steps
- **SQL Injection** — input `' OR '1'='1` or `admin' --` in the login field
- **Cookie Monster** — F12 → Application → Cookies → change role/value to `admin`
- **XSS (Reflected Mayhem)** — inject `<script>alert(1)</script>` in the search box; flag appears on success

---

## FORENSICS

| # | Title | Difficulty | Points | Flag |
|---|-------|-----------|--------|------|
| 17 | File Identity Crisis | EASY | 150 | `FLAG{file_signatures_matter}` |
| 14 | Memory Analysis | MEDIUM | 200 | `FLAG{hex_dump_decoded}` |
| 15 | Audio Forensics | MEDIUM | 200 | `FLAG{audio_secrets_revealed}` |
| 13 | Polyglot Puzzle | MEDIUM | 250 | `FLAG{hidden_archive_found}` |
| 10 | Memory Forensics | EXPERT | 350 | `FLAG{forensics_expert}` |

### Steps
- **File Identity Crisis** — run `file not_what_it_seems.txt`; check magic bytes
- **Memory Analysis** — look at hex dump ASCII column; convert hex to ASCII
- **Audio Forensics** — run `strings secret_audio.wav`; look for appended data
- **Polyglot Puzzle** — run `binwalk innocent_picture.bmp`; extract embedded archive
- **Memory Forensics** — use Volatility: `imageinfo` → `strings` → find flag

---

## REVERSE ENGINEERING

| # | Title | Difficulty | Points | Flag |
|---|-------|-----------|--------|------|
| 12 | Binary Secrets | EASY | 150 | `FLAG{strings_reveal_secrets}` |
| 9 | Binary Basics | HARD | 250 | `FLAG{reverse_engineering_ninja}` |
| 24 | Hidden in Plain Sight (SQL lab) | HARD | 170 | `FLAG{STEGMASTER_CCA2A6}` |
| 23 | Magic Bytes (SQL lab) | EXPERT | 220 | `FLAG{FILEDETECTIVE_B26556}` |

### Steps
- **Binary Secrets** — run `strings mystery_program.bin | grep FLAG`
- **Binary Basics** — run `strings filename | grep FLAG`
- **Hidden in Plain Sight** — run `exiftool` on file; check `Comment` field
- **Magic Bytes** — check first bytes with `xxd`; identify true file type

---

## STEGANOGRAPHY

| # | Title | Difficulty | Points | Flag |
|---|-------|-----------|--------|------|
| 3 | Hidden in Plain Sight | BEGINNER | 75 | `FLAG{steganography_rocks}` |
| 11 | Metadata Hunter | EASY | 150 | `FLAG{metadata_matters}` |

### Steps
- **Hidden in Plain Sight** — read the first letter of each line top to bottom
- **Metadata Hunter** — run `strings mysterious_image.png` or `exiftool mysterious_image.png`

---

## NETWORK SECURITY

| # | Title | Difficulty | Points | Flag |
|---|-------|-----------|--------|------|
| 8 | Packet Detective | HARD | 200 | `FLAG{wireshark_wizard}` |

### Steps
- **Packet Detective** — open pcap in Wireshark; filter `http`; Follow TCP Stream

---

## Summary

| Category | Challenges | Points |
|----------|-----------|--------|
| Cryptography | 10 | 890 |
| Web Security | 6 | 725 |
| Forensics | 5 | 1150 |
| Reverse Engineering | 4 | 790 |
| Steganography | 2 | 225 |
| Network Security | 1 | 200 |
| **Total** | **28** | **3980** |

---

## File Status
- All 17 challenges with files: **OK**
- Challenges 5,6,7,8,9,10,20,21,22,25: **No file needed** (text/interactive based)
- Challenge 24 file: **Created** (PNG with flag in metadata)
