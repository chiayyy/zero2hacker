#!/usr/bin/env python3
"""
Basic XSS Challenge - Web Interface
Difficulty: Beginner | Points: 50 | Category: Web Security
"""
from flask import Flask, request, render_template_string

app = Flask(__name__)
FLAG = "FLAG{xss_1s_ev3rywh3re}"

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Search Portal</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 30px; }
        .container { max-width: 700px; margin: 0 auto; }
        h1 { color: #e94560; }
        .card { background: #16213e; border: 1px solid #0f3460; border-radius: 8px; padding: 20px; margin: 20px 0; }
        input[type=text] { width: 100%; padding: 10px; background: #0f3460; border: 1px solid #e94560; color: #eee; border-radius: 6px; font-size: 14px; }
        button { background: #e94560; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; margin-top: 8px; }
        button:hover { background: #c73652; }
        .result { margin-top: 15px; padding: 15px; background: #0f3460; border-radius: 6px; }
        .success { color: #4ecca3; background: #0d2b1f; border: 1px solid #4ecca3; padding: 15px; border-radius: 6px; font-size: 18px; text-align: center; }
        .error { color: #e94560; padding: 10px; border-radius: 6px; }
        code { background: #0f3460; padding: 2px 6px; border-radius: 4px; color: #4ecca3; }
        .hint { background: #0f3460; padding: 10px 15px; border-left: 3px solid #e94560; margin: 10px 0; font-size: 13px; color: #aaa; }
        .flag-var { display: none; }
    </style>
    <script>
        var secretFlag = "{{ flag }}";
    </script>
</head>
<body>
<div class="container">
    <h1>🔍 Search Portal</h1>

    <div class="card">
        <h3>Search</h3>
        <p>Search our knowledge base:</p>
        <form method="GET" action="/search">
            <input type="text" name="q" placeholder="Enter search term..." value="{{ query or '' }}">
            <button type="submit">Search</button>
        </form>
        {% if query %}
        <div class="result">
            <strong>Search results for:</strong> {{ query|safe }}
            <br><br>No results found. Try a different search term.
        </div>
        {% endif %}
        <div class="hint">💡 This search form reflects your input directly onto the page. What could go wrong?</div>
    </div>

    <div class="card">
        <h3>Submit Flag</h3>
        <p>Found the flag stored in a JavaScript variable? Submit it here:</p>
        <form method="POST" action="/submit">
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
    return render_template_string(TEMPLATE, flag=FLAG)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    return render_template_string(TEMPLATE, flag=FLAG, query=query)

@app.route('/submit', methods=['POST'])
def submit():
    submitted = request.form.get('flag', '').strip()
    if submitted.upper() == FLAG.upper():
        return render_template_string(TEMPLATE, flag=FLAG, submitted=submitted,
                                      result=f"Correct! Flag: {FLAG}", correct=True)
    return render_template_string(TEMPLATE, flag=FLAG, submitted=submitted,
                                  result="Wrong flag. Keep trying!", correct=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8085, debug=False)
