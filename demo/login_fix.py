#!/usr/bin/env python3
"""
Fix for the login route to handle both AJAX and regular form submissions
"""

def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        password_hash = hash_password(password)

        conn = get_db_connection()
        user = conn.execute('''
            SELECT * FROM users WHERE username = ? AND password_hash = ?
        ''', (username, password_hash)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']

            # Check if it's an AJAX request
            if request.headers.get('Content-Type') == 'application/json' or \
               request.headers.get('Accept', '').find('application/json') != -1:
                return jsonify({'success': True, 'message': 'Login successful!'})
            else:
                # Regular form submission - redirect to dashboard
                return redirect(url_for('dashboard'))
        else:
            # Check if it's an AJAX request
            if request.headers.get('Content-Type') == 'application/json' or \
               request.headers.get('Accept', '').find('application/json') != -1:
                return jsonify({'success': False, 'error': 'Invalid username or password'})
            else:
                # Regular form submission - show error on login page
                return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')