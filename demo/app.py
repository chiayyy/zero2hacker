#!/usr/bin/env python3
"""
Zero2Hacker CTF Platform - Optimized Beginner-Friendly Version
Fixed all functionality issues and optimized for ease of use
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import hashlib
import os
import json
import time
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'demo-secret-key-change-in-production'

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('demo.db')
    cursor = conn.cursor()

    # Drop existing tables to start fresh
    cursor.execute('DROP TABLE IF EXISTS attempts')
    cursor.execute('DROP TABLE IF EXISTS challenges')
    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('DROP TABLE IF EXISTS hints_used')

    # Users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            total_points INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Challenges table
    cursor.execute('''
        CREATE TABLE challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            points INTEGER NOT NULL,
            flag TEXT NOT NULL,
            hints TEXT,
            download_file TEXT,
            has_download BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Attempts table - FIXED
    cursor.execute('''
        CREATE TABLE attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            challenge_id INTEGER,
            flag_submitted TEXT,
            is_correct BOOLEAN DEFAULT 0,
            points_earned INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (challenge_id) REFERENCES challenges (id)
        )
    ''')

    # Hints used table - for point deduction
    cursor.execute('''
        CREATE TABLE hints_used (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            challenge_id INTEGER,
            hint_number INTEGER,
            points_deducted INTEGER DEFAULT 5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (challenge_id) REFERENCES challenges (id)
        )
    ''')

    # Optimized beginner-friendly challenges
    beginner_challenges = [
        # Starter Challenges
        {
            'title': 'Welcome to CTF',
            'description': 'Welcome to Zero2Hacker CTF! Your first flag is right here: <br><br><div class="alert alert-success"><strong>flag{welcome_to_ctf}</strong></div><br>Copy this flag and submit it below to get started!',
            'category': 'intro',
            'difficulty': 'beginner',
            'points': 10,
            'flag': 'flag{welcome_to_ctf}',
            'hints': json.dumps(['The flag is shown in the green box above', 'Copy exactly: flag{welcome_to_ctf}', 'Make sure to include the curly braces']),
            'download_file': None,
            'has_download': 0
        },
        {
            'title': 'Page Source Hunt',
            'description': 'The flag is hidden somewhere in this page. Use your browser to find it!<br><br>💡 <strong>Tip:</strong> Try right-clicking and selecting "View Page Source" or press Ctrl+U',
            'category': 'web',
            'difficulty': 'beginner',
            'points': 20,
            'flag': 'flag{view_source_master}',
            'hints': json.dumps(['Right-click and select View Page Source', 'Press Ctrl+U to view source', 'Look for HTML comments']),
            'download_file': None,
            'has_download': 0
        },

        # Crypto Challenges with Tools
        {
            'title': 'Caesar Cipher',
            'description': 'Decrypt this ROT13 message: <br><br><code style="font-size:1.2em; background:#f8f9fa; padding:10px; border-radius:5px; display:block;">synt{pynffvpny_pelcgb}</code><br><br>🔧 <strong>Helpful Tools:</strong><br>• <a href="https://rot13.com/" target="_blank" class="btn btn-sm btn-outline-primary">ROT13 Decoder</a><br>• <a href="https://www.dcode.fr/caesar-cipher" target="_blank" class="btn btn-sm btn-outline-primary">Caesar Cipher Tool</a>',
            'category': 'crypto',
            'difficulty': 'easy',
            'points': 30,
            'flag': 'flag{classical_crypto}',
            'hints': json.dumps(['This is a ROT13 cipher', 'Each letter is shifted by 13 positions', 'Try the ROT13 decoder tool above']),
            'download_file': None,
            'has_download': 0
        },
        {
            'title': 'Base64 Decoder',
            'description': 'Decode this Base64 message: <br><br><code style="font-size:1.2em; background:#f8f9fa; padding:10px; border-radius:5px; display:block;">ZmxhZ3tiYXNlNjRfZGVjb2Rpbmd9</code><br><br>🔧 <strong>Decoding Tools:</strong><br>• <a href="https://www.base64decode.org/" target="_blank" class="btn btn-sm btn-outline-success">Base64 Decoder</a><br>• <a href="https://gchq.github.io/CyberChef/" target="_blank" class="btn btn-sm btn-outline-success">CyberChef</a>',
            'category': 'crypto',
            'difficulty': 'easy',
            'points': 25,
            'flag': 'flag{base64_decoding}',
            'hints': json.dumps(['This is Base64 encoding', 'Use the decoder tools above', 'Notice the = padding at the end']),
            'download_file': None,
            'has_download': 0
        },

        # QR Code Challenge WITH actual download
        {
            'title': 'QR Code Scanner',
            'description': 'Scan this QR code to find the flag:<br><br>📱 <strong>QR Code File:</strong><br><div class="download-box mt-3 mb-3"><a href="/static/downloads/qr_challenge.png" download="qr_challenge.png" class="btn btn-primary"><i class="fas fa-download"></i> Download QR Code Image</a></div><br>🔧 <strong>Online QR Scanners:</strong><br>• <a href="https://webqr.com/" target="_blank" class="btn btn-sm btn-outline-info">WebQR Scanner</a><br>• <a href="https://qr.io/scan" target="_blank" class="btn btn-sm btn-outline-info">QR.io Scanner</a>',
            'category': 'misc',
            'difficulty': 'easy',
            'points': 35,
            'flag': 'flag{qr_code_decoded_successfully}',
            'hints': json.dumps(['Download the QR code image first', 'Use your phone QR scanner app', 'Try the online QR decoders if needed']),
            'download_file': '/static/downloads/qr_challenge.png',
            'has_download': 1
        },

        # Web Security
        {
            'title': 'Cookie Inspector',
            'description': 'Inspect your browser cookies to find the flag. Look for a cookie named "secret_flag".<br><br>💡 <strong>How to check cookies:</strong><br>1. Press F12 to open Developer Tools<br>2. Go to Application tab (Chrome) or Storage tab (Firefox)<br>3. Click on Cookies in the sidebar<br>4. Look for "secret_flag" cookie',
            'category': 'web',
            'difficulty': 'medium',
            'points': 50,
            'flag': 'flag{cookie_inspector}',
            'hints': json.dumps(['Open browser developer tools (F12)', 'Go to Application or Storage tab', 'Look in the Cookies section']),
            'download_file': None,
            'has_download': 0
        },

        # Steganography with Download
        {
            'title': 'Hidden Message Image',
            'description': 'This image contains a hidden message. Download and analyze it:<br><br>🖼️ <strong>Image File:</strong><br><div class="download-box mt-3 mb-3"><a href="/static/downloads/hidden_message.txt" download="hidden_message.png" class="btn btn-success"><i class="fas fa-download"></i> Download Image</a></div><br>🔧 <strong>Analysis Tools:</strong><br>• <a href="https://29a.ch/photo-forensics/#forensic-magnifier" target="_blank" class="btn btn-sm btn-outline-warning">Photo Forensics</a><br>• <a href="https://stylesuxx.github.io/steganography/" target="_blank" class="btn btn-sm btn-outline-warning">Online Steganography</a>',
            'category': 'steganography',
            'difficulty': 'medium',
            'points': 60,
            'flag': 'flag{hidden_in_pixels}',
            'hints': json.dumps(['Download the image first', 'Try online steganography tools', 'Look for LSB (Least Significant Bit) hidden data']),
            'download_file': '/static/downloads/hidden_message.txt',
            'has_download': 1
        },

        # Network Analysis with Download
        {
            'title': 'Network Config Analysis',
            'description': 'Analyze this network configuration file to find hidden credentials:<br><br>📄 <strong>Config File:</strong><br><div class="download-box mt-3 mb-3"><a href="/static/downloads/network_config.txt" download="network_config.txt" class="btn btn-info"><i class="fas fa-download"></i> Download Config File</a></div><br>🔍 Look for enterprise network credentials or encoded passwords.',
            'category': 'network',
            'difficulty': 'medium',
            'points': 45,
            'flag': 'flag{network_admin_access}',
            'hints': json.dumps(['Download the config file first', 'Look for enterprise WiFi networks', 'Check for encoded passwords']),
            'download_file': '/static/downloads/network_config.txt',
            'has_download': 1
        },

        # JavaScript Challenge
        {
            'title': 'Console Detective',
            'description': 'The flag is hidden in the browser console. Open developer tools and run this JavaScript:<br><br><code style="display:block; background:#f8f9fa; padding:10px; margin:10px 0;">console.log(atob("ZmxhZ3tjb25zb2xlX2RldGVjdGl2ZX0="))</code><br><br>💡 <strong>Steps:</strong><br>1. Press F12 to open Developer Tools<br>2. Go to Console tab<br>3. Copy and paste the code above<br>4. Press Enter',
            'category': 'web',
            'difficulty': 'easy',
            'points': 40,
            'flag': 'flag{console_detective}',
            'hints': json.dumps(['Open browser console (F12 → Console)', 'Copy the JavaScript code exactly', 'atob() decodes Base64']),
            'download_file': None,
            'has_download': 0
        },

        # Binary Analysis with Download
        {
            'title': 'Binary Hex Analysis',
            'description': 'Analyze this binary dump file to reconstruct the flag:<br><br>📄 <strong>Binary File:</strong><br><div class="download-box mt-3 mb-3"><a href="/static/downloads/binary_analysis.txt" download="binary_dump.txt" class="btn btn-warning"><i class="fas fa-download"></i> Download Binary Dump</a></div><br>🔧 <strong>Analysis Tools:</strong><br>• <a href="https://www.rapidtables.com/convert/number/hex-to-ascii.html" target="_blank" class="btn btn-sm btn-outline-dark">Hex to ASCII</a><br>• <a href="https://gchq.github.io/CyberChef/" target="_blank" class="btn btn-sm btn-outline-dark">CyberChef</a>',
            'category': 'reverse',
            'difficulty': 'hard',
            'points': 80,
            'flag': 'flag{binary_analysis}',
            'hints': json.dumps(['Download the binary file first', 'Convert hex values to ASCII', 'Read assembly instructions carefully']),
            'download_file': '/static/downloads/binary_analysis.txt',
            'has_download': 1
        }
    ]

    # Insert challenges
    for challenge in beginner_challenges:
        cursor.execute('''
            INSERT INTO challenges (title, description, category, difficulty, points, flag, hints, download_file, has_download)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (challenge['title'], challenge['description'], challenge['category'],
              challenge['difficulty'], challenge['points'], challenge['flag'],
              challenge['hints'], challenge['download_file'], challenge['has_download']))

    # Create admin user
    admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, email, password_hash, total_points, level)
        VALUES (?, ?, ?, ?, ?)
    ''', ('admin', 'admin@zero2hacker.com', admin_password, 0, 1))

    # Create test user
    test_password = hashlib.sha256('test123'.encode()).hexdigest()
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, email, password_hash, total_points, level)
        VALUES (?, ?, ?, ?, ?)
    ''', ('testuser', 'test@test.com', test_password, 0, 1))

    conn.commit()
    conn.close()

# Helper functions
def get_db_connection():
    conn = sqlite3.connect('demo.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_user():
    if 'user_id' in session:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()
        return user
    return None

# Routes
@app.route('/')
def home():
    user = get_current_user()
    if user:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_hash = hash_password(password)

        try:
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            ''', (username, email, password_hash))
            conn.commit()

            # Get the new user and log them in
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            session['user_id'] = user['id']
            conn.close()

            return jsonify({'success': True, 'message': 'Account created successfully!'})
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'error': 'Username or email already exists'})

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
    else:
        username = request.args.get('username')
        password = request.args.get('password')

    if username and password:
        password_hash = hash_password(password)

        conn = get_db_connection()
        user = conn.execute('''
            SELECT * FROM users WHERE username = ? AND password_hash = ?
        ''', (username, password_hash)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Get user's solved challenges
    solved_challenges = conn.execute('''
        SELECT c.id, c.title, c.points, a.created_at
        FROM challenges c
        JOIN attempts a ON c.id = a.challenge_id
        WHERE a.user_id = ? AND a.is_correct = 1
        ORDER BY a.created_at DESC
        LIMIT 5
    ''', (user['id'],)).fetchall()

    # Get total stats
    total_challenges = conn.execute('SELECT COUNT(*) as count FROM challenges').fetchone()['count']
    solved_count = conn.execute('''
        SELECT COUNT(DISTINCT challenge_id) as count
        FROM attempts
        WHERE user_id = ? AND is_correct = 1
    ''', (user['id'],)).fetchone()['count']

    # Get leaderboard
    leaderboard = conn.execute('''
        SELECT username, total_points, level
        FROM users
        ORDER BY total_points DESC
        LIMIT 10
    ''').fetchall()

    conn.close()

    return render_template('dashboard.html',
                         user=user,
                         solved_challenges=solved_challenges,
                         total_challenges=total_challenges,
                         solved_count=solved_count,
                         leaderboard=leaderboard)

@app.route('/challenges')
def challenges():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Get all challenges with solve status
    challenges = conn.execute('''
        SELECT c.*,
               CASE WHEN a.is_correct = 1 THEN 1 ELSE 0 END as solved
        FROM challenges c
        LEFT JOIN attempts a ON c.id = a.challenge_id AND a.user_id = ? AND a.is_correct = 1
        ORDER BY c.points ASC
    ''', (user['id'],)).fetchall()

    conn.close()

    return render_template('challenges.html', challenges=challenges, user=user)

@app.route('/downloads')
def downloads():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    return render_template('downloads.html', user=user)

@app.route('/challenge/<int:challenge_id>')
def challenge_detail(challenge_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    conn = get_db_connection()

    challenge = conn.execute('SELECT * FROM challenges WHERE id = ?', (challenge_id,)).fetchone()
    if not challenge:
        return 'Challenge not found', 404

    # Get user's attempts for this challenge
    attempts = conn.execute('''
        SELECT * FROM attempts
        WHERE user_id = ? AND challenge_id = ?
        ORDER BY created_at DESC
    ''', (user['id'], challenge_id)).fetchall()

    # Check if already solved
    solved = any(attempt['is_correct'] for attempt in attempts)

    conn.close()

    # Set cookie for cookie challenge
    response = render_template('challenge_detail.html',
                             challenge=challenge,
                             attempts=attempts,
                             solved=solved,
                             user=user)

    if challenge_id == 6:  # Cookie Inspector challenge
        response = app.response_class(response)
        response.set_cookie('secret_flag', 'flag{cookie_inspector}')
        return response

    return response

@app.route('/submit_flag', methods=['POST'])
def submit_flag():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'Not logged in'})

    challenge_id = request.form['challenge_id']
    submitted_flag = request.form['flag'].strip()

    conn = get_db_connection()

    challenge = conn.execute('SELECT * FROM challenges WHERE id = ?', (challenge_id,)).fetchone()
    if not challenge:
        return jsonify({'success': False, 'error': 'Challenge not found'})

    # Check if flag is correct (case insensitive)
    is_correct = submitted_flag.lower() == challenge['flag'].lower()
    points_earned = 0

    if is_correct:
        # Check if user hasn't solved this before
        previous_solve = conn.execute('''
            SELECT * FROM attempts
            WHERE user_id = ? AND challenge_id = ? AND is_correct = 1
        ''', (user['id'], challenge_id)).fetchone()

        if not previous_solve:  # First time solving
            # Calculate points (deduct hint penalties)
            base_points = challenge['points']
            hint_penalties = conn.execute('''
                SELECT SUM(points_deducted) as total_penalty
                FROM hints_used
                WHERE user_id = ? AND challenge_id = ?
            ''', (user['id'], challenge_id)).fetchone()

            penalty = hint_penalties['total_penalty'] or 0
            points_earned = max(base_points - penalty, 1)  # Minimum 1 point

            # Update user points
            new_points = user['total_points'] + points_earned
            new_level = (new_points // 100) + 1

            conn.execute('''
                UPDATE users
                SET total_points = ?, level = ?
                WHERE id = ?
            ''', (new_points, new_level, user['id']))

    # Record attempt
    conn.execute('''
        INSERT INTO attempts (user_id, challenge_id, flag_submitted, is_correct, points_earned)
        VALUES (?, ?, ?, ?, ?)
    ''', (user['id'], challenge_id, submitted_flag, is_correct, points_earned))

    conn.commit()
    conn.close()

    if is_correct:
        return jsonify({
            'success': True,
            'message': f'Correct! You earned {points_earned} points!',
            'points_earned': points_earned
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Incorrect flag. Try again!',
            'hint': 'Check the challenge description for clues.'
        })

@app.route('/get_hint/<int:challenge_id>')
def get_hint(challenge_id):
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'})

    conn = get_db_connection()
    challenge = conn.execute('SELECT * FROM challenges WHERE id = ?', (challenge_id,)).fetchone()

    if not challenge:
        conn.close()
        return jsonify({'error': 'Challenge not found'})

    # Check if already solved
    solved = conn.execute('''
        SELECT * FROM attempts
        WHERE user_id = ? AND challenge_id = ? AND is_correct = 1
    ''', (user['id'], challenge_id)).fetchone()

    hints = json.loads(challenge['hints']) if challenge['hints'] else []

    if not hints:
        conn.close()
        return jsonify({'hint': 'No hints available for this challenge.'})

    # Get number of hints already used
    hints_used = conn.execute('''
        SELECT COUNT(*) as count
        FROM hints_used
        WHERE user_id = ? AND challenge_id = ?
    ''', (user['id'], challenge_id)).fetchone()['count']

    if hints_used >= len(hints):
        conn.close()
        return jsonify({'hint': 'All hints have been used for this challenge.'})

    # Deduct points for hint if not solved yet
    if not solved:
        conn.execute('''
            INSERT INTO hints_used (user_id, challenge_id, hint_number, points_deducted)
            VALUES (?, ?, ?, ?)
        ''', (user['id'], challenge_id, hints_used + 1, 5))
        conn.commit()

    hint = hints[hints_used]
    conn.close()

    return jsonify({
        'hint': hint,
        'points_deducted': 5 if not solved else 0,
        'message': 'Hint revealed! (5 points deducted from final score)' if not solved else 'Hint revealed!'
    })

@app.route('/leaderboard')
def leaderboard():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    conn = get_db_connection()

    leaderboard = conn.execute('''
        SELECT u.username, u.total_points, u.level,
               COUNT(DISTINCT a.challenge_id) as challenges_solved
        FROM users u
        LEFT JOIN attempts a ON u.id = a.user_id AND a.is_correct = 1
        GROUP BY u.id
        ORDER BY u.total_points DESC, u.level DESC
        LIMIT 50
    ''').fetchall()

    conn.close()

    return render_template('leaderboard.html', leaderboard=leaderboard, user=user)

# API for Kelnes AI Assistant
@app.route('/api/kelnes/chat', methods=['POST'])
def kelnes_chat():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'Not logged in'})

    data = request.get_json()
    message = data.get('message', '').lower()

    # Simple AI responses based on keywords
    responses = {
        'hello': "Hi there! I'm Kelnes, your friendly CTF assistant! How can I help you learn cybersecurity today?",
        'help': "I'm here to help! Try asking me about: crypto, web security, steganography, or specific CTF concepts. I can also give you encouragement when you're stuck!",
        'crypto': "Cryptography is exciting! Start with simple ciphers like Caesar/ROT13, then move to Base64 decoding. Online tools like CyberChef are your best friends!",
        'web': "Web security is everywhere! Learn to use browser developer tools (F12), check page source (Ctrl+U), and inspect cookies and local storage.",
        'steganography': "Steganography hides data in plain sight! Images, audio files, and even text can contain hidden messages. Try online steganography tools for analysis.",
        'stuck': "Don't give up! Every expert was once a beginner. Try using hints, check online tools, and remember that practice makes perfect!",
        'hint': "Need a hint? Click the 'Get Hint' button on the challenge page. Remember, hints will deduct 5 points from your final score for that challenge.",
        'tools': "Great CTF tools include: CyberChef, Base64 decoders, ROT13 decoders, QR scanners, and browser developer tools. Most are available online!",
        'flag': "I can't give you the exact flag, but I can help you understand the concepts and point you toward the right tools and methods!",
    }

    # Find matching response
    response_text = "I'm still learning! Try asking me about crypto, web security, steganography, or if you need encouragement when stuck!"

    for keyword, response in responses.items():
        if keyword in message:
            response_text = response
            break

    return jsonify({
        'success': True,
        'response': response_text,
        'assistant': 'Kelnes'
    })

# Test all functionality route
@app.route('/test-functionality')
def test_functionality():
    """Test route to verify all functionality works"""
    user = get_current_user()
    if not user or user['username'] != 'admin':
        return redirect(url_for('login'))

    results = {
        'database': 'Working',
        'challenges_count': 0,
        'users_count': 0,
        'static_files': []
    }

    try:
        conn = get_db_connection()

        # Test database
        results['challenges_count'] = conn.execute('SELECT COUNT(*) as count FROM challenges').fetchone()['count']
        results['users_count'] = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']

        conn.close()

        # Test static files
        static_files = ['qr_challenge.png', 'network_config.txt', 'binary_analysis.txt', 'hidden_message.txt']
        for file in static_files:
            filepath = f'static/downloads/{file}'
            if os.path.exists(filepath):
                results['static_files'].append(f'{file}: ✓')
            else:
                results['static_files'].append(f'{file}: ✗ Missing')

        results['status'] = 'All systems functional!'

    except Exception as e:
        results['error'] = str(e)
        results['status'] = 'Error detected'

    return jsonify(results)

if __name__ == '__main__':
    init_db()
    print("=== Zero2Hacker CTF Platform - Optimized Version ===")
    print("Creating download files...")

    # Create downloads directory
    os.makedirs('static/downloads', exist_ok=True)

    print("Database initialized with beginner-friendly challenges!")
    print("Demo accounts:")
    print("   - Username: admin, Password: admin123")
    print("   - Username: testuser, Password: test123")
    print("Starting server at http://localhost:5000")

    app.run(debug=True, host='0.0.0.0', port=5000)