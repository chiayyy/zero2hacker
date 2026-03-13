#!/usr/bin/env python3
"""
Caesar Cipher Challenge
Difficulty: Beginner
Points: 25
Category: Cryptography

Description:
Decrypt this message that has been encoded with a Caesar cipher.
The flag is in the format flag{...}

Encrypted message: synt{pynffvpny_pelcgb}

Hints:
1. This is a simple substitution cipher where each letter is shifted by a fixed number
2. Try different shift values (1-25)
3. The message should be readable English when decrypted correctly
"""

def caesar_encrypt(text, shift):
    """Encrypt text using Caesar cipher"""
    result = ""
    for char in text:
        if char.isalpha():
            ascii_offset = 65 if char.isupper() else 97
            result += chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
        else:
            result += char
    return result

def caesar_decrypt(text, shift):
    """Decrypt text using Caesar cipher"""
    return caesar_encrypt(text, -shift)

# Original message
original = "flag{classical_crypto}"

# Encrypt with shift of 13 (ROT13)
encrypted = caesar_encrypt(original, 13)
print(f"Encrypted message: {encrypted}")

# Solution
print(f"\nSolution:")
for shift in range(1, 26):
    decrypted = caesar_decrypt(encrypted, shift)
    print(f"Shift {shift:2d}: {decrypted}")
    if decrypted == original:
        print(f"*** CORRECT: Shift {shift} gives the flag!")

print(f"\nFlag: {original}")