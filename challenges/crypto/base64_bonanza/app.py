#!/usr/bin/env python3
"""
Base64 Bonanza Challenge - Web Interface
Difficulty: Beginner | Points: 50 | Category: Cryptography
"""
from flask import Flask, request, render_template_string
import base64

app = Flask(__name__)

FLAG = "FLAG{base64_decoding_rocks}"
# Multi-layer encoded flag: base64 of base64 of base64
ENCODED = base64.b64encode(base64.b64encode(base64.b64encode(FLAG.encode()).decode().encode()).decode().encode()).decode()

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Base64 Bonanza</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Courier New', monospace; background: #0d1117; color: #c9d1d9; margin: 0; padding: 30px; }
        .container { max-width: 700px; margin: 0 auto; }
        h1 { color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
        .badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 12px; margin-right: 6px; }
        .beginner { background: #1f6feb; } .points { background: #388bfd22; border: 1px solid #388bfd; color: #58a6ff; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; margin: 20px 0; }
        .encoded { font-size: 14px; color: #f0883e; word-break: break-all; padding: 15px; background: #0d1117; border-radius: 6px; border: 1px dashed #30363d; }
        label { display: block; margin-bottom: 6px; color: #8b949e; }
        input[type=text] { width: 100%; padding: 10px; background: #0d1117; border: 1px solid #30363d; color: #c9d1d9; border-radius: 6px; font-family: monospace; font-size: 14px; }
        button { background: #238636; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; margin-top: 8px; }
        button:hover { background: #2ea043; }
        .result { margin-top: 12px; padding: 10px; background: #0d1117; border-radius: 6px; font-size: 15px; color: #3fb950; border: 1px solid #238636; word-break: break-all; }
        .success { color: #3fb950; background: #0d2b11; border: 1px solid #238636; padding: 15px; border-radius: 6px; font-size: 18px; text-align: center; }
        .error { color: #f85149; background: #2d0f0f; border: 1px solid #f85149; padding: 10px; border-radius: 6px; }
        code { background: #0d1117; padding: 2px 6px; border-radius: 4px; color: #f0883e; }
        pre { background: #0d1117; padding: 15px; border-radius: 6px; border: 1px solid #30363d; color: #3fb950; font-size: 12px; }
    </style>
</head>
<body>
<div class="container">
    <h1>🔐 Base64 Bonanza</h1>
    <span class="badge beginner">Beginner</span>
    <span class="badge points">50 pts</span>

    <div class="card">
        <h3>Challenge</h3>
        <p>The flag has been encoded multiple times using Base64. Can you decode it?</p>
        <div class="encoded">{{ encoded }}</div>
    </div>

    <div class="card">
        <h3>Decode It</h3>
        <form method="POST" action="/decode">
            <label>Paste a Base64 string to decode:</label>
            <input type="text" name="b64" placeholder="Paste base64 here..." value="{{ b64input or '' }}">
            <button type="submit">Decode</button>
        </form>
        {% if decoded %}
        <div class="result">→ {{ decoded }}</div>
        {% endif %}
        <p style="color:#8b949e;font-size:13px;margin-top:10px">Tip: You may need to decode multiple times.</p>
    </div>

    <div class="card">
        <h3>Python Cheatsheet</h3>
        <pre>import base64

# Decode once
base64.b64decode("your_string").decode()

# Decode multiple layers
data = "{{ encoded }}"
for i in range(3):
    data = base64.b64decode(data).decode()
    print(f"Layer {i+1}: {data}")</pre>
    </div>

    <div class="card">
        <h3>Submit Flag</h3>
        <form method="POST" action="/submit">
            <label>Enter the flag (format: FLAG{...}):</label>
            <input type="text" name="flag" placeholder="FLAG{...}" value="{{ submitted or '' }}">
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

@app.route('/')
def index():
    return render_template_string(TEMPLATE, encoded=ENCODED)

@app.route('/decode', methods=['POST'])
def decode():
    b64input = request.form.get('b64', '').strip()
    try:
        decoded = base64.b64decode(b64input).decode('utf-8', errors='replace')
    except Exception as e:
        decoded = f"Error: {e}"
    return render_template_string(TEMPLATE, encoded=ENCODED, b64input=b64input, decoded=decoded)

@app.route('/submit', methods=['POST'])
def submit():
    submitted = request.form.get('flag', '').strip()
    if submitted.upper() == FLAG.upper():
        return render_template_string(TEMPLATE, encoded=ENCODED, submitted=submitted,
                                      result=f"Correct! Flag: {FLAG}", correct=True)
    return render_template_string(TEMPLATE, encoded=ENCODED, submitted=submitted,
                                  result="Wrong flag. Keep trying!", correct=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8086, debug=False)
