#!/usr/bin/env python3
"""
Basic SQL Injection Challenge
Difficulty: Easy
Points: 50
Category: Web Security

Description:
This web application has a login form that is vulnerable to SQL injection.
Find a way to bypass the authentication and retrieve the flag.

The application uses a simple SQLite database with users table.
Goal: Login as admin user to get the flag.
"""

from flask import Flask, request, render_template_string, g
import sqlite3
import os

app = Flask(__name__)

# Database setup
DATABASE = 'challenge.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.executescript('''
            DROP TABLE IF EXISTS users;
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                flag TEXT
            );

            INSERT INTO users (username, password, role, flag) VALUES
            ('admin', 'super_secret_password_123', 'admin', 'flag{sql_injection_basics}'),
            ('user', 'password123', 'user', NULL),
            ('guest', 'guest', 'guest', NULL);
        ''')
        db.commit()

# HTML template
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Secure Login Portal</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 50px; background: #f0f0f0; }
        .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], input[type="password"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%; }
        .btn:hover { background: #0056b3; }
        .error { color: red; margin-top: 10px; }
        .success { color: green; margin-top: 10px; }
        .hint { background: #e7f3ff; padding: 10px; border-left: 4px solid #007bff; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🔐 Secure Login Portal</h2>
        <p>Welcome to our highly secure login system!</p>

        <form method="POST">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn">Login</button>
        </form>

        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}

        {% if success %}
            <div class="success">{{ success }}</div>
        {% endif %}

        <div class="hint">
            <strong>Hint:</strong> This application might have some security vulnerabilities.
            Try exploring different input combinations. The admin user has special privileges!
        </div>

        <div class="hint">
            <strong>Challenge:</strong> Find a way to login as admin without knowing the password.
            Common SQL injection payloads might help: <code>' OR '1'='1</code>
        </div>
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Vulnerable SQL query - DO NOT use in production!
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

        try:
            db = get_db()
            cursor = db.execute(query)
            user = cursor.fetchone()

            if user:
                if user['role'] == 'admin':
                    return render_template_string(LOGIN_TEMPLATE,
                        success=f"Welcome Admin! Here's your flag: {user['flag']}")
                else:
                    return render_template_string(LOGIN_TEMPLATE,
                        success=f"Welcome {user['username']}! You are logged in as {user['role']}.")
            else:
                return render_template_string(LOGIN_TEMPLATE,
                    error="Invalid username or password!")

        except sqlite3.Error as e:
            return render_template_string(LOGIN_TEMPLATE,
                error=f"Database error: {str(e)}")

    return render_template_string(LOGIN_TEMPLATE)

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True, host='0.0.0.0', port=8080)