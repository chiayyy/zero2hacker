#!/usr/bin/env python3
"""
Hidden Message Steganography Challenge
Difficulty: Easy
Points: 40
Category: Steganography

Description:
There's a secret message hidden in this image using LSB steganography.
Can you extract the hidden flag?

This script creates the challenge image with the hidden message.
"""

from PIL import Image
import os

def text_to_binary(text):
    """Convert text to binary representation"""
    return ''.join(format(ord(char), '08b') for char in text)

def hide_message_in_image(image_path, message, output_path):
    """Hide message in image using LSB steganography"""
    # Open the image
    img = Image.open(image_path)
    img = img.convert('RGB')

    # Convert message to binary and add delimiter
    binary_message = text_to_binary(message + "###END###")

    # Get image data
    pixels = list(img.getdata())

    # Check if image can hold the message
    if len(binary_message) > len(pixels) * 3:
        raise ValueError("Image too small to hold the message")

    # Hide message in LSB of RGB values
    data_index = 0
    new_pixels = []

    for pixel in pixels:
        r, g, b = pixel

        # Modify LSB of each color channel if we still have message data
        if data_index < len(binary_message):
            r = (r & 0xFE) | int(binary_message[data_index])
            data_index += 1

        if data_index < len(binary_message):
            g = (g & 0xFE) | int(binary_message[data_index])
            data_index += 1

        if data_index < len(binary_message):
            b = (b & 0xFE) | int(binary_message[data_index])
            data_index += 1

        new_pixels.append((r, g, b))

    # Create new image with hidden message
    new_img = Image.new('RGB', img.size)
    new_img.putdata(new_pixels)
    new_img.save(output_path)
    print(f"Message hidden in {output_path}")

def extract_message_from_image(image_path):
    """Extract hidden message from image"""
    img = Image.open(image_path)
    img = img.convert('RGB')

    pixels = list(img.getdata())
    binary_message = ""

    # Extract LSB from each pixel
    for pixel in pixels:
        r, g, b = pixel
        binary_message += str(r & 1)
        binary_message += str(g & 1)
        binary_message += str(b & 1)

    # Convert binary to text
    message = ""
    for i in range(0, len(binary_message), 8):
        byte = binary_message[i:i+8]
        if len(byte) == 8:
            char = chr(int(byte, 2))
            if char.isprintable():
                message += char
                # Check for end delimiter
                if message.endswith("###END###"):
                    return message[:-9]  # Remove delimiter

    return message

def create_base_image():
    """Create a simple base image for the challenge"""
    # Create a colorful gradient image
    width, height = 400, 300
    img = Image.new('RGB', (width, height))

    pixels = []
    for y in range(height):
        for x in range(width):
            r = int(255 * (x / width))
            g = int(255 * (y / height))
            b = int(255 * ((x + y) / (width + height)))
            pixels.append((r, g, b))

    img.putdata(pixels)
    img.save('original.png')
    return 'original.png'

if __name__ == "__main__":
    # Hidden message (the flag)
    secret_message = "flag{hidden_in_plain_sight}"

    # Create base image
    base_image = create_base_image()

    # Hide message in image
    output_image = "challenge_image.png"
    hide_message_in_image(base_image, secret_message, output_image)

    # Verify extraction works
    extracted = extract_message_from_image(output_image)
    print(f"Original message: {secret_message}")
    print(f"Extracted message: {extracted}")
    print(f"Extraction successful: {secret_message == extracted}")

    # Clean up
    os.remove(base_image)

    print(f"\nChallenge image created: {output_image}")
    print(f"Hidden message: {secret_message}")
    print("\nSolution: Use LSB steganography extraction tools or write a script to extract the hidden message.")