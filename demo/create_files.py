#!/usr/bin/env python3
"""
Generate actual files for CTF challenges
"""

from PIL import Image, ImageDraw, ImageFont
import wave
import numpy as np
import struct
import os

def create_secret_image():
    """Create image with hidden metadata"""
    # Create a colorful CTF challenge image
    img = Image.new('RGB', (800, 600), color='#1e293b')
    draw = ImageDraw.Draw(img)

    # Try to use default font
    try:
        font_large = ImageFont.load_default().font_variant(size=48)
        font_medium = ImageFont.load_default().font_variant(size=24)
        font_small = ImageFont.load_default().font_variant(size=16)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Draw background pattern
    for x in range(0, 800, 50):
        for y in range(0, 600, 50):
            if (x + y) % 100 == 0:
                draw.rectangle([x, y, x+25, y+25], fill='#334155')

    # Main title
    draw.text((400, 150), 'CTF FORENSICS CHALLENGE', fill='#22d3ee', font=font_large, anchor='mm')
    draw.text((400, 220), 'Hidden Data Analysis', fill='#94a3b8', font=font_medium, anchor='mm')

    # Challenge info
    draw.text((400, 300), 'This image contains hidden metadata', fill='#f8fafc', font=font_medium, anchor='mm')
    draw.text((400, 340), 'Use EXIF analysis tools to find the flag', fill='#cbd5e1', font=font_small, anchor='mm')

    # Decorative elements
    draw.rectangle([100, 400, 700, 500], outline='#22d3ee', width=3)
    draw.text((400, 450), 'GPS: 40.7589, -73.9851 (Times Square, NYC)', fill='#fbbf24', font=font_small, anchor='mm')

    # Add some binary-looking data
    binary_text = "01100110 01101100 01100001 01100111"
    draw.text((400, 520), f'Binary: {binary_text}', fill='#10b981', font=font_small, anchor='mm')

    # Save the image
    img.save('static/downloads/secret_image.jpg', 'JPEG', quality=95,
             exif=b'\xff\xe1\x00\x16Exif\x00\x00II*\x00\x08\x00\x00\x00')
    print("✅ Created secret_image.jpg")

def create_steganography_image():
    """Create PNG image with LSB steganography simulation"""
    # Create base image
    img = Image.new('RGB', (600, 400), color='#0f172a')
    draw = ImageDraw.Draw(img)

    try:
        font_large = ImageFont.load_default().font_variant(size=36)
        font_medium = ImageFont.load_default().font_variant(size=18)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()

    # Create a nature scene simulation
    # Sky gradient
    for y in range(150):
        color = int(15 + (y * 0.3))  # Gradual blue increase
        draw.rectangle([0, y, 600, y+1], fill=(color, color*2, color*4))

    # Ground
    draw.rectangle([0, 150, 600, 400], fill='#064e3b')

    # "Trees" (simple triangles)
    for i, x in enumerate([100, 200, 350, 480]):
        height = 80 + (i * 10)
        draw.polygon([(x, 150), (x-30, 150+height), (x+30, 150+height)], fill='#166534')

    # Title overlay
    draw.text((300, 50), 'STEGANOGRAPHY CHALLENGE', fill='#fbbf24', font=font_large, anchor='mm')
    draw.text((300, 320), 'Hidden message: flag{hidden_in_pixels}', fill='#f8fafc', font=font_medium, anchor='mm')
    draw.text((300, 350), 'LSB Analysis Required', fill='#cbd5e1', font=font_medium, anchor='mm')

    # Save as PNG
    img.save('static/downloads/steganography_image.png', 'PNG')
    print("✅ Created steganography_image.png")

def create_audio_file():
    """Create WAV audio file with hidden data simulation"""
    # Audio parameters
    sample_rate = 44100  # Hz
    duration = 3  # seconds
    frequency = 440  # A4 note

    # Generate sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Create a simple melody
    wave_data = []

    # First tone (A4)
    tone1 = np.sin(2 * np.pi * 440 * t[:sample_rate])
    # Second tone (C5)
    tone2 = np.sin(2 * np.pi * 523.25 * t[:sample_rate])
    # Third tone (E5)
    tone3 = np.sin(2 * np.pi * 659.25 * t[:sample_rate])

    # Combine tones
    wave_data = np.concatenate([tone1, tone2, tone3])

    # Normalize to 16-bit range
    wave_data = (wave_data * 32767).astype(np.int16)

    # Save as WAV file
    with wave.open('static/downloads/hidden_audio.wav', 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(wave_data.tobytes())

    print("✅ Created hidden_audio.wav")

def create_pcap_simulation():
    """Create a mock PCAP file (actually a text file with PCAP-like content)"""
    pcap_content = """# Mock PCAP File - Network Capture Analysis
# This simulates a packet capture file for educational purposes

Frame 1: Ethernet II, Src: 00:0c:29:8d:1e:4f, Dst: 00:50:56:c0:00:08
Internet Protocol Version 4, Src: 192.168.1.100, Dst: 192.168.1.1
Transmission Control Protocol, Src Port: 45232, Dst Port: 80

Frame 2: HTTP Request
GET /login.php HTTP/1.1
Host: vulnerable-site.local
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
Accept: text/html,application/xhtml+xml
Cookie: sessionid=guest123

Frame 3: HTTP Response
HTTP/1.1 200 OK
Content-Type: text/html
Set-Cookie: sessionid=flag{packet_capture_analysis}; Path=/
Server: Apache/2.4.41

Frame 4: TCP Data
POST /submit.php HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 45

username=admin&password=secretpass123&token=abc

Frame 5: DNS Query
Standard query 0x1234 A vulnerable-site.local
Answer: 192.168.1.50

# Analysis Notes:
# - Session cookie contains the flag
# - Look for Set-Cookie header in Frame 3
# - Flag format: flag{packet_capture_analysis}
"""

    with open('static/downloads/network_capture.pcap', 'w') as f:
        f.write(pcap_content)

    print("✅ Created network_capture.pcap")

if __name__ == "__main__":
    print("🎯 Generating CTF challenge files...")

    # Create downloads directory if it doesn't exist
    os.makedirs('static/downloads', exist_ok=True)

    # Generate all files
    create_secret_image()
    create_steganography_image()
    create_audio_file()
    create_pcap_simulation()

    print("\n✅ All challenge files created successfully!")
    print("📁 Files are located in static/downloads/")