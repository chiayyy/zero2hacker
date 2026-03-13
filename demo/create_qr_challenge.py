#!/usr/bin/env python3
"""
Create QR code and update challenges
"""

import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

def create_qr_code():
    """Create QR code with hidden flag"""
    # Create QR code containing the flag
    flag_data = "flag{qr_code_decoded_successfully}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(flag_data)
    qr.make(fit=True)

    # Create QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white")

    # Create a larger canvas with title
    canvas = Image.new('RGB', (400, 450), 'white')
    draw = ImageDraw.Draw(canvas)

    # Try to load a font, fallback to default
    try:
        font_title = ImageFont.load_default().font_variant(size=24)
        font_subtitle = ImageFont.load_default().font_variant(size=16)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()

    # Add title
    draw.text((200, 30), 'CTF QR Challenge', fill='black', font=font_title, anchor='mm')
    draw.text((200, 60), 'Scan this QR code', fill='gray', font=font_subtitle, anchor='mm')

    # Paste QR code onto canvas
    qr_resized = qr_img.resize((300, 300))
    canvas.paste(qr_resized, (50, 100))

    # Add instructions
    draw.text((200, 420), 'Use any QR scanner app', fill='gray', font=font_subtitle, anchor='mm')

    # Save the image
    canvas.save('static/downloads/qr_challenge.png', 'PNG')
    print("Created QR challenge image: static/downloads/qr_challenge.png")
    print(f"QR contains: {flag_data}")

def create_network_challenge():
    """Create a network configuration file"""
    network_config = """# Network Configuration Challenge
# Find the hidden credentials in this config

[WiFi_Networks]
SSID: CTF_Guest
Password: guest123
Security: WPA2

SSID: Admin_Network
Password: flag{network_admin_access}
Security: WPA3-Enterprise
Hidden: true

SSID: Public_WiFi
Password: (none)
Security: Open

[Router_Config]
Admin_Panel: 192.168.1.1
Username: admin
Password: admin123
Backup_Key: aGVsbG93b3JsZA==

[VPN_Settings]
Server: vpn.company.com
Port: 1194
Protocol: OpenVPN
Auth_Key: ZmxhZ3tuZXR3b3JrX2NyZWRlbnRpYWxzfQ==

# The flag is hidden in one of the password fields above
# Look for the WiFi network that requires enterprise authentication
"""

    with open('static/downloads/network_config.txt', 'w') as f:
        f.write(network_config)

    print("Created network configuration file")

def create_binary_file():
    """Create a binary analysis file"""
    binary_content = """Binary Analysis Challenge
========================

Hexdump of suspicious file:
00000000: 7f45 4c46 0201 0100 0000 0000 0000 0000  .ELF............
00000010: 0200 3e00 0100 0000 4010 4000 0000 0000  ..>.....@.@.....
00000020: 4000 0000 0000 0000 4c11 0000 0000 0000  @.......L.......
00000030: 0000 0000 4000 3800 0900 4000 1b00 1a00  ....@.8...@.....

Assembly code section:
mov $0x666c6167, %eax     ; Load flag part 1
push %eax
mov $0x7b62696e, %eax     ; Load flag part 2
push %eax
mov $0x6172795f, %eax     ; Load flag part 3
push %eax
mov $0x616e616c, %eax     ; Load flag part 4
push %eax
mov $0x79736973, %eax     ; Load flag part 5
push %eax
mov $0x7d, %eax           ; Load flag part 6 (closing brace)
push %eax

; The flag is constructed on the stack
; Convert hex values to ASCII to get the flag
; Read from bottom to top: 0x666c6167 = "flag", etc.

Flag construction:
0x666c6167 = "galf" (reversed)
0x7b62696e = "nib{" (reversed)
0x6172795f = "_yra" (reversed)
0x616e616c = "lana" (reversed)
0x79736973 = "sysy" (reversed)
0x7d = "}"

Correct order: flag{binary_analysis}
"""

    with open('static/downloads/binary_analysis.txt', 'w') as f:
        f.write(binary_content)

    print("Created binary analysis file")

if __name__ == "__main__":
    print("Creating additional challenge files...")

    # Create downloads directory if it doesn't exist
    os.makedirs('static/downloads', exist_ok=True)

    # Create all files
    create_qr_code()
    create_network_challenge()
    create_binary_file()

    print("\nAll additional challenge files created!")