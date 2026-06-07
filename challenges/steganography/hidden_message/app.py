#!/usr/bin/env python3
"""
Hidden Message Steganography Challenge - Web Interface
Difficulty: Easy | Points: 40 | Category: Steganography
"""
from flask import Flask, render_template_string, send_file
import os, io

app = Flask(__name__)

FLAG = "FLAG{steganography_rocks}"
IMAGE_PATH = os.path.join(os.path.dirname(__file__), "challenge_image.png")

def generate_image():
    try:
        from PIL import Image
    except ImportError:
        return False
    if os.path.exists(IMAGE_PATH):
        return True
    width, height = 400, 300
    img = Image.new('RGB', (width, height))
    pixels = [(int(255*(x/width)), int(255*(y/height)), int(255*((x+y)/(width+height)))) for y in range(height) for x in range(width)]
    img.putdata(pixels)

    def text_to_bits(text):
        return ''.join(format(ord(c), '08b') for c in text + "###END###")

    bits = text_to_bits(FLAG)
    new_pixels = []
    idx = 0
    for r, g, b in pixels:
        if idx < len(bits): r = (r & 0xFE) | int(bits[idx]); idx += 1
        if idx < len(bits): g = (g & 0xFE) | int(bits[idx]); idx += 1
        if idx < len(bits): b = (b & 0xFE) | int(bits[idx]); idx += 1
        new_pixels.append((r, g, b))
    out = Image.new('RGB', (width, height))
    out.putdata(new_pixels)
    out.save(IMAGE_PATH)
    return True

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Hidden Message - Steganography</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Courier New', monospace; background: #0d1117; color: #c9d1d9; margin: 0; padding: 30px; }
        .container { max-width: 700px; margin: 0 auto; }
        h1 { color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
        .badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 12px; margin-right: 6px; }
        .easy { background: #238636; } .points { background: #388bfd22; border: 1px solid #388bfd; color: #58a6ff; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; margin: 20px 0; }
        a.btn { display: inline-block; background: #1f6feb; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; margin-top: 10px; }
        a.btn:hover { background: #388bfd; }
        button { background: #238636; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; margin-top: 8px; }
        button:hover { background: #2ea043; }
        input[type=text] { width: 100%; padding: 10px; background: #0d1117; border: 1px solid #30363d; color: #c9d1d9; border-radius: 6px; font-family: monospace; font-size: 14px; }
        label { display: block; margin-bottom: 6px; color: #8b949e; }
        .success { color: #3fb950; background: #0d2b11; border: 1px solid #238636; padding: 15px; border-radius: 6px; font-size: 18px; text-align: center; }
        .error { color: #f85149; background: #2d0f0f; border: 1px solid #f85149; padding: 10px; border-radius: 6px; }
        code { background: #0d1117; padding: 2px 6px; border-radius: 4px; color: #f0883e; }
        pre { background: #0d1117; padding: 15px; border-radius: 6px; border: 1px solid #30363d; overflow-x: auto; color: #3fb950; font-size: 13px; }
        img.preview { max-width: 100%; border: 1px solid #30363d; border-radius: 6px; margin-top: 10px; }
    </style>
</head>
<body>
<div class="container">
    <h1>🖼️ Hidden Message</h1>
    <span class="badge easy">Easy</span>
    <span class="badge points">40 pts</span>

    <div class="card">
        <h3>Challenge</h3>
        <p>A secret flag has been hidden inside this image using <strong>LSB (Least Significant Bit) steganography</strong>.</p>
        <p>The image looks completely normal to the human eye — but it contains a hidden message in the pixel data.</p>
        {% if image_ready %}
        <img src="/image" class="preview" alt="Challenge Image">
        <br>
        <a href="/download" class="btn">⬇ Download challenge_image.png</a>
        {% else %}
        <div class="error">⚠ Could not generate image. Install Pillow: <code>pip install Pillow</code> then restart.</div>
        {% endif %}
    </div>

    <div class="card">
        <h3>How to Extract the Flag</h3>
        <p>Use Python to extract the LSB from each pixel's RGB channels:</p>
        <pre>from PIL import Image

img = Image.open("challenge_image.png").convert("RGB")
pixels = list(img.getdata())
bits = ""
for r, g, b in pixels:
    bits += str(r & 1)
    bits += str(g & 1)
    bits += str(b & 1)

msg = ""
for i in range(0, len(bits), 8):
    byte = bits[i:i+8]
    if len(byte) == 8:
        char = chr(int(byte, 2))
        msg += char
        if msg.endswith("###END###"):
            print(msg[:-9])
            break</pre>
        <p>Or use tools like <code>steghide</code>, <code>stegsolve</code>, or <code>zsteg</code>.</p>
    </div>

    <div class="card">
        <h3>Submit Flag</h3>
        <form method="POST" action="/submit">
            <label>Enter the flag (format: flag{...}):</label>
            <input type="text" name="flag" placeholder="flag{...}" value="{{ submitted or '' }}">
            <button type="submit">Submit</button>
        </form>
        {% if result %}
        <div class="{{ 'success' if correct else 'error' }}" style="margin-top:12px">{{ result }}</div>
        {% endif %}
    </div>
</div>
</body>
</html>
"""

image_ready = generate_image()

@app.route('/')
def index():
    return render_template_string(TEMPLATE, image_ready=image_ready)

@app.route('/image')
def serve_image():
    if not os.path.exists(IMAGE_PATH):
        return "Image not found", 404
    return send_file(IMAGE_PATH, mimetype='image/png')

@app.route('/download')
def download():
    if not os.path.exists(IMAGE_PATH):
        return "Image not found", 404
    return send_file(IMAGE_PATH, as_attachment=True, download_name='challenge_image.png')

@app.route('/submit', methods=['POST'])
def submit():
    submitted = request.form.get('flag', '').strip()
    if submitted.lower() == FLAG.lower():
        return render_template_string(TEMPLATE, image_ready=image_ready, submitted=submitted,
                                      result=f"Correct! Flag: {FLAG}", correct=True)
    return render_template_string(TEMPLATE, image_ready=image_ready, submitted=submitted,
                                  result="Wrong flag. Keep trying!", correct=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082, debug=False)
