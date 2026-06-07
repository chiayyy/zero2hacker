#!/usr/bin/env python3
"""
Cookie Monster Challenge - Web Interface
Difficulty: Easy | Points: 50 | Category: Web Security
"""
from flask import Flask, request, render_template_string, make_response, redirect

app = Flask(__name__)
FLAG = "FLAG{cookies_are_not_secure}"

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Cookie Monster - Admin Portal</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 30px; }
        .container { max-width: 700px; margin: 0 auto; }
        h1 { color: #4ecca3; }
        .card { background: #16213e; border: 1px solid #0f3460; border-radius: 8px; padding: 20px; margin: 20px 0; }
        .cookie-box { background: #0f3460; padding: 15px; border-radius: 6px; font-family: monospace; color: #f0883e; word-break: break-all; }
        input[type=text] { width: 100%; padding: 10px; background: #0f3460; border: 1px solid #4ecca3; color: #eee; border-radius: 6px; font-size: 14px; font-family: monospace; }
        button { background: #4ecca3; color: #1a1a2e; font-weight: bold; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; margin-top: 8px; }
        button:hover { background: #3ab895; }
        .admin-panel { background: #0d2b1f; border: 2px solid #4ecca3; padding: 20px; border-radius: 8px; text-align: center; }
        .flag { font-size: 24px; color: #4ecca3; font-family: monospace; font-weight: bold; }
        .error { color: #e94560; padding: 10px; border-radius: 6px; }
        .success { color: #4ecca3; background: #0d2b1f; border: 1px solid #4ecca3; padding: 15px; border-radius: 6px; font-size: 18px; text-align: center; }
        .user-badge { display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 13px; }
        .user { background: #0f3460; } .admin { background: #238636; }
        code { background: #0f3460; padding: 2px 6px; border-radius: 4px; color: #4ecca3; }
    </style>
</head>
<body>
<div class="container">
    <h1>🍪 Admin Portal</h1>

    <div class="card">
        <h3>Your Session</h3>
        <p>Current role: <span class="user-badge {{ 'admin' if role == 'admin' else 'user' }}">{{ role }}</span></p>
        <p>Current cookies:</p>
        <div class="cookie-box">role={{ role }}</div>
    </div>

    {% if role == 'admin' %}
    <div class="admin-panel">
        <h2>🎉 Welcome, Admin!</h2>
        <p>You have successfully accessed the admin panel.</p>
        <div class="flag">{{ flag }}</div>
    </div>
    {% else %}
    <div class="card">
        <h3>🔒 Access Denied</h3>
        <p>This section is for admins only. Your current role is <code>{{ role }}</code>.</p>
        <p>Can you find a way to become an admin?</p>
        <p style="color:#8b949e;font-size:13px">Hint: Authentication is based on a cookie. Try modifying it using DevTools (F12 → Application → Cookies) or with curl.</p>
    </div>
    {% endif %}

    <div class="card">
        <h3>Set Cookie Manually</h3>
        <p>Enter a role value to set the <code>role</code> cookie:</p>
        <form method="POST" action="/set-cookie">
            <input type="text" name="role" placeholder="Enter role..." value="{{ role }}">
            <button type="submit">Set Cookie & Reload</button>
        </form>
    </div>

    <div class="card">
        <h3>Submit Flag</h3>
        <form method="POST" action="/submit">
            <input type="text" name="flag" placeholder="FLAG{...}" value="{{ submitted or '' }}" style="margin-bottom:8px">
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
    role = request.cookies.get('role', 'guest')
    return render_template_string(TEMPLATE, role=role, flag=FLAG if role == 'admin' else '')

@app.route('/set-cookie', methods=['POST'])
def set_cookie():
    role = request.form.get('role', 'guest')
    resp = make_response(redirect('/'))
    resp.set_cookie('role', role)
    return resp

@app.route('/submit', methods=['POST'])
def submit():
    role = request.cookies.get('role', 'guest')
    submitted = request.form.get('flag', '').strip()
    if submitted.upper() == FLAG.upper():
        resp = make_response(render_template_string(TEMPLATE, role=role, flag=FLAG,
                                                     submitted=submitted, result=f"Correct! Flag: {FLAG}", correct=True))
        return resp
    resp = make_response(render_template_string(TEMPLATE, role=role, flag=FLAG if role == 'admin' else '',
                                                 submitted=submitted, result="Wrong flag. Keep trying!", correct=False))
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8087, debug=False)
