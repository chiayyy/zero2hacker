"""
Script to create CTF challenge files with hidden flags
These challenges require users to use external tools to find the flags
"""

import os
import struct
import base64
import zipfile
import wave
import array

# Create challenges directory if not exists
CHALLENGES_DIR = os.path.join(os.path.dirname(__file__), 'static', 'challenges')
os.makedirs(CHALLENGES_DIR, exist_ok=True)

def create_png_with_hidden_flag():
    """
    Challenge 1: PNG image with flag hidden in metadata (tEXt chunk)
    Tool needed: exiftool, strings, or pngcheck
    Flag: FLAG{metadata_matters}
    """
    # Create a simple valid PNG (1x1 red pixel)
    # PNG signature
    png_signature = b'\x89PNG\r\n\x1a\n'

    # IHDR chunk (image header)
    width = 100
    height = 100
    bit_depth = 8
    color_type = 2  # RGB
    ihdr_data = struct.pack('>IIBBBBB', width, height, bit_depth, color_type, 0, 0, 0)
    ihdr_crc = 0x6d0f8d7b  # Pre-calculated for this data
    ihdr_chunk = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)

    # Create simple red image data (uncompressed for simplicity)
    import zlib
    raw_data = b''
    for y in range(height):
        raw_data += b'\x00'  # Filter byte
        for x in range(width):
            # Create a gradient pattern
            r = (x * 255 // width) & 0xFF
            g = (y * 255 // height) & 0xFF
            b = 128
            raw_data += bytes([r, g, b])

    compressed_data = zlib.compress(raw_data)
    idat_crc = zlib.crc32(b'IDAT' + compressed_data) & 0xffffffff
    idat_chunk = struct.pack('>I', len(compressed_data)) + b'IDAT' + compressed_data + struct.pack('>I', idat_crc)

    # tEXt chunk with hidden flag
    flag = "FLAG{metadata_matters}"
    text_data = b'Comment\x00' + flag.encode() + b'\x00Hidden in plain sight - check the metadata!'
    text_crc = zlib.crc32(b'tEXt' + text_data) & 0xffffffff
    text_chunk = struct.pack('>I', len(text_data)) + b'tEXt' + text_data + struct.pack('>I', text_crc)

    # IEND chunk
    iend_crc = 0xae426082
    iend_chunk = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)

    # Combine all chunks
    png_data = png_signature + ihdr_chunk + text_chunk + idat_chunk + iend_chunk

    filepath = os.path.join(CHALLENGES_DIR, 'mysterious_image.png')
    with open(filepath, 'wb') as f:
        f.write(png_data)

    print(f"Created: {filepath}")
    print("Flag: FLAG{metadata_matters}")
    print("Hint: Use 'strings' or 'exiftool' to examine the image")
    return filepath


def create_strings_binary():
    """
    Challenge 2: Binary file with flag hidden among strings
    Tool needed: strings command
    Flag: FLAG{strings_reveal_secrets}
    """
    # Create a fake "binary" with lots of junk and a hidden flag
    junk_strings = [
        b"Loading configuration...",
        b"Initializing system...",
        b"ERROR: Cannot connect to server",
        b"WARNING: Low memory",
        b"Debug mode enabled",
        b"Version 1.0.0",
        b"Copyright 2024",
        b"All rights reserved",
        b"Checking license...",
        b"License valid",
    ]

    flag = b"FLAG{strings_reveal_secrets}"

    # Create binary content
    content = b'\x00' * 100  # Null bytes

    for s in junk_strings[:5]:
        content += s + b'\x00' * 50
        content += os.urandom(100)  # Random binary data

    # Hide the flag in the middle
    content += b'\x00' * 200
    content += b"SECRET_DATA_START:"
    content += flag
    content += b":SECRET_DATA_END"
    content += b'\x00' * 200

    for s in junk_strings[5:]:
        content += os.urandom(100)
        content += s + b'\x00' * 50

    content += b'\x00' * 100

    filepath = os.path.join(CHALLENGES_DIR, 'mystery_program.bin')
    with open(filepath, 'wb') as f:
        f.write(content)

    print(f"Created: {filepath}")
    print("Flag: FLAG{strings_reveal_secrets}")
    print("Hint: Use 'strings' command to find readable text")
    return filepath


def create_zip_in_image():
    """
    Challenge 3: Image with ZIP file appended (polyglot file)
    Tool needed: binwalk, foremost, or manual extraction
    Flag: FLAG{hidden_archive_found}
    """
    import zlib

    # Create a simple BMP image first
    width = 50
    height = 50

    # BMP Header
    bmp_header = b'BM'  # Signature
    pixel_data_size = width * height * 3
    file_size = 54 + pixel_data_size  # Header + pixels
    bmp_header += struct.pack('<I', file_size)  # File size
    bmp_header += b'\x00\x00\x00\x00'  # Reserved
    bmp_header += struct.pack('<I', 54)  # Pixel data offset

    # DIB Header (BITMAPINFOHEADER)
    dib_header = struct.pack('<I', 40)  # Header size
    dib_header += struct.pack('<i', width)  # Width
    dib_header += struct.pack('<i', height)  # Height
    dib_header += struct.pack('<H', 1)  # Color planes
    dib_header += struct.pack('<H', 24)  # Bits per pixel
    dib_header += struct.pack('<I', 0)  # Compression (none)
    dib_header += struct.pack('<I', pixel_data_size)  # Image size
    dib_header += struct.pack('<i', 2835)  # X pixels per meter
    dib_header += struct.pack('<i', 2835)  # Y pixels per meter
    dib_header += struct.pack('<I', 0)  # Colors in color table
    dib_header += struct.pack('<I', 0)  # Important colors

    # Create pixel data (blue gradient)
    pixels = b''
    for y in range(height):
        for x in range(width):
            b = (x * 255 // width) & 0xFF
            g = (y * 255 // height) & 0xFF
            r = 100
            pixels += bytes([b, g, r])

    bmp_data = bmp_header + dib_header + pixels

    # Create a ZIP file with the flag
    flag_content = b"Congratulations! You found the hidden archive!\n\nFLAG{hidden_archive_found}\n"

    # Create ZIP in memory
    import io
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('secret_flag.txt', flag_content)

    zip_data = zip_buffer.getvalue()

    # Combine BMP + ZIP (polyglot file)
    combined = bmp_data + zip_data

    filepath = os.path.join(CHALLENGES_DIR, 'innocent_picture.bmp')
    with open(filepath, 'wb') as f:
        f.write(combined)

    print(f"Created: {filepath}")
    print("Flag: FLAG{hidden_archive_found}")
    print("Hint: Use 'binwalk' or check if there's more than just an image")
    return filepath


def create_hex_encoded_file():
    """
    Challenge 4: Text file with flag encoded in hex dump
    Tool needed: xxd, hex editor, or manual decoding
    Flag: FLAG{hex_dump_decoded}
    """
    # Create a fake hex dump that contains the flag
    header = """MEMORY DUMP - CLASSIFIED
========================
Address  | 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F | ASCII
---------+-------------------------------------------------+------------------
"""

    # Some fake memory addresses with junk data
    lines = []

    # Add some random-looking hex lines
    for i in range(10):
        addr = f"0x{i*16:08X}"
        hex_part = ' '.join([f'{b:02X}' for b in os.urandom(16)])
        ascii_part = ''.join([chr(b) if 32 <= b < 127 else '.' for b in os.urandom(16)])
        lines.append(f"{addr} | {hex_part} | {ascii_part}")

    # Add the flag in hex
    flag = "FLAG{hex_dump_decoded}"
    flag_bytes = flag.encode()

    # Pad to 16 bytes per line
    while len(flag_bytes) % 16 != 0:
        flag_bytes += b'\x00'

    for i in range(0, len(flag_bytes), 16):
        chunk = flag_bytes[i:i+16]
        addr = f"0x{(10+i//16)*16:08X}"
        hex_part = ' '.join([f'{b:02X}' for b in chunk])
        ascii_part = ''.join([chr(b) if 32 <= b < 127 else '.' for b in chunk])
        lines.append(f"{addr} | {hex_part} | {ascii_part}")

    # Add more random lines after
    for i in range(15, 25):
        addr = f"0x{i*16:08X}"
        hex_part = ' '.join([f'{b:02X}' for b in os.urandom(16)])
        ascii_part = ''.join([chr(b) if 32 <= b < 127 else '.' for b in os.urandom(16)])
        lines.append(f"{addr} | {hex_part} | {ascii_part}")

    content = header + '\n'.join(lines) + "\n\nEND OF DUMP"

    filepath = os.path.join(CHALLENGES_DIR, 'memory_dump.txt')
    with open(filepath, 'w') as f:
        f.write(content)

    print(f"Created: {filepath}")
    print("Flag: FLAG{hex_dump_decoded}")
    print("Hint: Look at the hex values and decode them")
    return filepath


def create_audio_with_flag():
    """
    Challenge 5: WAV audio file with flag in metadata/data
    Tool needed: strings, exiftool, or audio analysis
    Flag: FLAG{audio_secrets_revealed}
    """
    # Create a simple WAV file with the flag hidden in it
    sample_rate = 44100
    duration = 1  # 1 second

    # Generate simple tone (440 Hz - A note)
    samples = []
    for i in range(sample_rate * duration):
        t = i / sample_rate
        # Simple sine wave approximation using integer math
        value = int(16000 * (((i * 440 * 4) // sample_rate) % 4 - 2) / 2)
        samples.append(max(-32768, min(32767, value)))

    # Create WAV file
    filepath = os.path.join(CHALLENGES_DIR, 'secret_audio.wav')

    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sample_rate)

        # Convert samples to bytes
        sample_bytes = array.array('h', samples).tobytes()
        wav_file.writeframes(sample_bytes)

    # Append flag as metadata (after the WAV data)
    with open(filepath, 'ab') as f:
        f.write(b'\x00' * 100)
        f.write(b'HIDDEN_FLAG: FLAG{audio_secrets_revealed}')
        f.write(b'\x00' * 100)

    print(f"Created: {filepath}")
    print("Flag: FLAG{audio_secrets_revealed}")
    print("Hint: Use 'strings' on the audio file or check beyond the audio data")
    return filepath


def create_base64_layers():
    """
    Challenge 6: File with multiple layers of base64 encoding
    Tool needed: base64 command, CyberChef, or Python
    Flag: FLAG{decode_all_layers}
    """
    flag = "FLAG{decode_all_layers}"

    # Encode multiple times
    encoded = flag.encode()
    layers = 5
    for i in range(layers):
        encoded = base64.b64encode(encoded)

    content = f"""TOP SECRET TRANSMISSION
=======================
Classification: ULTRA
Date: [REDACTED]
From: [REDACTED]
To: [REDACTED]

The following message has been encoded for security.
It has been processed through {layers} layers of encoding.

BEGIN ENCODED MESSAGE:
{encoded.decode()}
END ENCODED MESSAGE

Decode all layers to reveal the secret.
"""

    filepath = os.path.join(CHALLENGES_DIR, 'encoded_transmission.txt')
    with open(filepath, 'w') as f:
        f.write(content)

    print(f"Created: {filepath}")
    print(f"Flag: {flag}")
    print(f"Hint: Decode base64 {layers} times")
    return filepath


def create_file_header_challenge():
    """
    Challenge 7: File with wrong extension (JPEG disguised as TXT)
    Tool needed: file command, hex editor
    Flag: FLAG{file_signatures_matter}
    """
    # Create minimal JPEG with flag in comment
    # JPEG magic bytes
    jpeg_data = bytes([
        0xFF, 0xD8, 0xFF, 0xE0,  # SOI and APP0 marker
        0x00, 0x10,  # Length of APP0
        0x4A, 0x46, 0x49, 0x46, 0x00,  # JFIF identifier
        0x01, 0x01,  # Version
        0x00,  # Aspect ratio units
        0x00, 0x01, 0x00, 0x01,  # X and Y density
        0x00, 0x00,  # Thumbnail dimensions
    ])

    # Add comment segment with flag
    flag = b"FLAG{file_signatures_matter}"
    comment = b"This is not a text file! " + flag
    comment_marker = bytes([0xFF, 0xFE])  # COM marker
    comment_length = struct.pack('>H', len(comment) + 2)
    jpeg_data += comment_marker + comment_length + comment

    # Add minimal image data (1x1 pixel)
    # SOF0 (Start of Frame)
    jpeg_data += bytes([
        0xFF, 0xC0, 0x00, 0x0B,
        0x08, 0x00, 0x01, 0x00, 0x01,
        0x01, 0x01, 0x11, 0x00
    ])

    # DHT (Define Huffman Table) - minimal
    jpeg_data += bytes([
        0xFF, 0xC4, 0x00, 0x14,
        0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00
    ])

    # SOS (Start of Scan)
    jpeg_data += bytes([
        0xFF, 0xDA, 0x00, 0x08,
        0x01, 0x01, 0x00, 0x00,
        0x3F, 0x00, 0x7F
    ])

    # EOI (End of Image)
    jpeg_data += bytes([0xFF, 0xD9])

    # Save with wrong extension
    filepath = os.path.join(CHALLENGES_DIR, 'not_what_it_seems.txt')
    with open(filepath, 'wb') as f:
        f.write(jpeg_data)

    print(f"Created: {filepath}")
    print("Flag: FLAG{file_signatures_matter}")
    print("Hint: Use 'file' command or check the magic bytes")
    return filepath


def create_rot13_document():
    """
    Challenge 8: Document with ROT13 encoded content
    Tool needed: tr command, CyberChef, or manual decoding
    Flag: FLAG{rotation_cipher_solved}
    """
    import codecs

    flag = "FLAG{rotation_cipher_solved}"

    # ROT13 encode
    encoded_flag = codecs.encode(flag, 'rot_13')

    # Create fake classified document
    content = f"""CLASSIFIED DOCUMENT
===================
Document ID: CTF-2024-008
Classification: SECRET
Encoding: Standard Agency Protocol

Agent Report - Mission Debrief
------------------------------

The operation was successful. All objectives completed.
The extracted intelligence has been encoded using our
standard rotation protocol for transmission security.

ENCODED INTELLIGENCE:
{encoded_flag}

Remember: Our standard protocol uses alphabetic rotation.
The key is the same as the position in the alphabet of
the letter 'N' minus one... or just the number 13.

END OF DOCUMENT
"""

    filepath = os.path.join(CHALLENGES_DIR, 'classified_report.txt')
    with open(filepath, 'w') as f:
        f.write(content)

    print(f"Created: {filepath}")
    print(f"Flag: {flag}")
    print("Hint: ROT13 encoding - rotate each letter by 13 positions")
    return filepath


if __name__ == "__main__":
    print("="*50)
    print("Creating CTF Challenge Files")
    print("="*50)
    print()

    create_png_with_hidden_flag()
    print()

    create_strings_binary()
    print()

    create_zip_in_image()
    print()

    create_hex_encoded_file()
    print()

    create_audio_with_flag()
    print()

    create_base64_layers()
    print()

    create_file_header_challenge()
    print()

    create_rot13_document()
    print()

    print("="*50)
    print("All challenge files created successfully!")
    print(f"Location: {CHALLENGES_DIR}")
    print("="*50)
