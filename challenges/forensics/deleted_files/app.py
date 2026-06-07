#!/usr/bin/env python3
"""
Deleted Files Recovery Challenge - Web Interface
Difficulty: Medium | Points: 80 | Category: Digital Forensics
"""
from flask import Flask, render_template_string, send_file, request
import os, zipfile, io

app = Flask(__name__)

FLAG = "flag{forensics_recovery_expert}"
ZIP_PATH = os.path.join(os.path.dirname(__file__), "challenge_disk.zip")

def generate_challenge():
    if os.path.exists(ZIP_PATH):
        return True
    try:
        readme = b"Welcome to the forensics challenge!\nSome files have been deleted from this system.\nCan you recover them?\n"
        notes = b"Meeting notes:\n- Discuss project timeline\n- Review security protocols\n- Plan next sprint\n"
        config = b"[settings]\ndebug=false\nlog_level=info\nmax_connections=100\n"

        # The "deleted" file — its content is embedded in slack space (appended raw bytes after zip entries)
        secret_content = (
            "CONFIDENTIAL DOCUMENT\n"
            "=====================\n\n"
            "Project: SecureVault Development\n"
            "Date: 2024-01-15\n"
            "Classification: TOP SECRET\n\n"
            f"The secret flag for this challenge is: {FLAG}\n\n"
            "This information must not be disclosed to unauthorized personnel.\n"
        ).encode()

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("readme.txt", readme)
            zf.writestr("notes.txt", notes)
            zf.writestr("config.ini", config)
            # No secret file in directory listing — it's "deleted"

        # Append raw secret bytes after the ZIP (simulates file slack space / unallocated region)
        raw = buf.getvalue()
        raw += b"\x00" * 512  # padding like disk sectors
        raw += b"=== UNALLOCATED SPACE ===\n"
        raw += secret_content
        raw += b"\x00" * 256

        with open(ZIP_PATH, 'wb') as f:
            f.write(raw)
        return True
    except Exception as e:
        print(f"Error generating challenge: {e}")
        return False

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Deleted Files Recovery</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Courier New', monospace; background: #0d1117; color: #c9d1d9; margin: 0; padding: 30px; }
        .container { max-width: 750px; margin: 0 auto; }
        h1 { color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
        .badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 12px; margin-right: 6px; }
        .medium { background: #9e6a03; } .points { background: #388bfd22; border: 1px solid #388bfd; color: #58a6ff; }
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
        pre { background: #0d1117; padding: 15px; border-radius: 6px; border: 1px solid #30363d; overflow-x: auto; color: #3fb950; font-size: 12px; }
    </style>
</head>
<body>
<div class="container">
    <h1>🕵️ Deleted Files Recovery</h1>
    <span class="badge medium">Medium</span>
    <span class="badge points">80 pts</span>

    <div class="card">
        <h3>Challenge</h3>
        <p>An employee deleted a confidential document containing a secret flag. A disk image was captured before the drive was wiped.</p>
        <p>The file is no longer in the directory listing — but data is never truly gone. Recover the deleted content.</p>
        {% if disk_ready %}
        <a href="/download" class="btn">⬇ Download challenge_disk.zip</a>
        {% else %}
        <div class="error">⚠ Failed to generate challenge file. Check server logs.</div>
        {% endif %}
    </div>

    <div class="card">
        <h3>How to Recover</h3>
        <p>The zip file contains visible files plus hidden data in the unallocated space. Use <code>strings</code> or read the raw bytes:</p>
        <pre># Method 1: strings command (Linux/WSL)
strings challenge_disk.zip | grep -i flag

# Method 2: Python raw read
with open("challenge_disk.zip", "rb") as f:
    data = f.read()

# Look for readable text after the ZIP directory
text = data.decode("utf-8", errors="ignore")
for line in text.splitlines():
    if "flag{" in line:
        print(line)

# Method 3: hexdump
xxd challenge_disk.zip | grep -A2 "UNALLOC"</pre>
        <p>Tools: <code>strings</code>, <code>xxd</code>, <code>hexdump</code>, <code>foremost</code>, <code>binwalk</code></p>
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

disk_ready = generate_challenge()

@app.route('/')
def index():
    return render_template_string(TEMPLATE, disk_ready=disk_ready)

@app.route('/download')
def download():
    if not os.path.exists(ZIP_PATH):
        return "File not found", 404
    return send_file(ZIP_PATH, as_attachment=True, download_name='challenge_disk.zip')

@app.route('/submit', methods=['POST'])
def submit():
    submitted = request.form.get('flag', '').strip()
    if submitted.lower() == FLAG.lower():
        return render_template_string(TEMPLATE, disk_ready=disk_ready, submitted=submitted,
                                      result=f"Correct! Flag: {FLAG}", correct=True)
    return render_template_string(TEMPLATE, disk_ready=disk_ready, submitted=submitted,
                                  result="Wrong flag. Keep trying!", correct=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8084, debug=False)
