#!/usr/bin/env python3
"""
Caesar Cipher Challenge - Web Interface
Difficulty: Beginner | Points: 25 | Category: Cryptography
"""
from flask import Flask, request, render_template_string

app = Flask(__name__)

FLAG = "FLAG{caesar_was_here}"
# FLAG{caesar_was_here} encrypted with ROT13
ENCRYPTED = "SYNT{pnrfne_jnf_urer}"

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Caesar Cipher Challenge</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Courier New', monospace; background: #0d1117; color: #c9d1d9; margin: 0; padding: 30px; }
        .container { max-width: 700px; margin: 0 auto; }
        h1 { color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
        .badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 12px; margin-right: 6px; }
        .beginner { background: #1f6feb; } .points { background: #388bfd22; border: 1px solid #388bfd; color: #58a6ff; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; margin: 20px 0; }
        .encrypted { font-size: 22px; color: #f0883e; letter-spacing: 2px; text-align: center; padding: 15px; background: #0d1117; border-radius: 6px; border: 1px dashed #30363d; }
        label { display: block; margin-bottom: 6px; color: #8b949e; }
        input[type=number], input[type=text] { width: 100%; padding: 10px; background: #0d1117; border: 1px solid #30363d; color: #c9d1d9; border-radius: 6px; font-family: monospace; font-size: 14px; }
        button { background: #238636; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; margin-top: 8px; }
        button:hover { background: #2ea043; }
        .result { margin-top: 12px; padding: 10px; background: #0d1117; border-radius: 6px; font-size: 16px; color: #3fb950; border: 1px solid #238636; }
        .error { color: #f85149; border-color: #f85149; }
        .success { color: #3fb950; background: #0d2b11; border-color: #238636; padding: 15px; border-radius: 6px; font-size: 18px; text-align: center; }
        .hint { color: #8b949e; font-size: 13px; margin-top: 8px; }
        hr { border-color: #30363d; }
    </style>
</head>
<body>
<div class="container">
    <h1>🔐 Caesar Cipher</h1>
    <span class="badge beginner">Beginner</span>
    <span class="badge points">25 pts</span>

    <div class="card">
        <h3>Challenge</h3>
        <p>This message has been encrypted with a Caesar cipher. Decrypt it to find the flag.</p>
        <div class="encrypted">{{ encrypted }}</div>
    </div>

    <div class="card">
        <h3>Try a Shift</h3>
        <form method="POST" action="/decrypt">
            <label>Shift value (1-25):</label>
            <input type="number" name="shift" min="1" max="25" value="{{ shift or '' }}" required>
            <button type="submit">Decrypt</button>
        </form>
        {% if decrypted %}
        <div class="result">Shift {{ shift }}: {{ decrypted }}</div>
        {% endif %}
        <p class="hint">Tip: Try all shifts from 1 to 25 until the output looks readable.</p>
    </div>

    <div class="card">
        <h3>Submit Flag</h3>
        <form method="POST" action="/submit">
            <label>Enter the flag (format: flag{...}):</label>
            <input type="text" name="flag" placeholder="flag{...}" value="{{ submitted or '' }}">
            <button type="submit">Submit</button>
        </form>
        {% if result %}
        <div class="{{ 'success' if correct else 'result error' }}">{{ result }}</div>
        {% endif %}
    </div>
</div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(TEMPLATE, encrypted=ENCRYPTED)

@app.route('/decrypt', methods=['POST'])
def decrypt():
    shift = int(request.form.get('shift', 0))
    result = ""
    for c in ENCRYPTED:
        if c.isalpha():
            base = 65 if c.isupper() else 97
            result += chr((ord(c) - base - shift) % 26 + base)
        else:
            result += c
    return render_template_string(TEMPLATE, encrypted=ENCRYPTED, shift=shift, decrypted=result)

@app.route('/submit', methods=['POST'])
def submit():
    submitted = request.form.get('flag', '').strip()
    if submitted.lower() == FLAG.lower():
        return render_template_string(TEMPLATE, encrypted=ENCRYPTED, submitted=submitted,
                                      result=f"Correct! Flag: {FLAG}", correct=True)
    return render_template_string(TEMPLATE, encrypted=ENCRYPTED, submitted=submitted,
                                  result="Wrong flag. Keep trying!", correct=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=False)
