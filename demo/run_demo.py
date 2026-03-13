#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set UTF-8 encoding
import locale
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except:
    pass

# Import and run the app
if __name__ == '__main__':
    from app import app, init_db

    # Initialize database
    init_db()

    print("=" * 50)
    print("Zero2Hacker CTF Platform - Demo Version")
    print("=" * 50)
    print("Server starting at: http://localhost:5000")
    print("")
    print("Demo Account:")
    print("  Username: admin")
    print("  Password: admin123")
    print("")
    print("Features Available:")
    print("  - 4 Sample CTF Challenges")
    print("  - User Registration & Login")
    print("  - Points & Leaderboard System")
    print("  - Interactive Challenge Solving")
    print("")
    print("Challenge Categories:")
    print("  1. Introduction Challenge")
    print("  2. Caesar Cipher (Crypto)")
    print("  3. SQL Injection (Web Security)")
    print("  4. Hidden Message (Steganography)")
    print("")
    print("Ready to hack! Visit http://localhost:5000")
    print("=" * 50)

    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)