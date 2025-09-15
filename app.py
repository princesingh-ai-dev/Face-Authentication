from flask import Flask, render_template, redirect, url_for, session, flash, request
from authenticator import Authenticator
import threading
import time

app = Flask(__name__)
app.secret_key = 'face_auth_secret_key'  # In production, use env var or secure method

authenticator = Authenticator()

@app.route('/')
def home():
    """
    Home page with authentication trigger.
    """
    return render_template('home.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    """
    Trigger face authentication.
    On success, set session and redirect to dashboard.
    On failure, flash error.
    """
    success, message, user_id = authenticator.authenticate_user()
    if success:
        session['authenticated'] = True
        session['user_id'] = user_id
        flash(f'Welcome, {user_id}! Authentication successful.', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash(message, 'error')
        return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    """
    Protected dashboard, accessible only after authentication.
    """
    if not session.get('authenticated'):
        flash('Authentication required.', 'error')
        return redirect(url_for('home'))
    
    user_id = session.get('user_id', 'User')
    return render_template('dashboard.html', user_id=user_id)

@app.route('/logout')
def logout():
    """
    Clear session and redirect to home.
    """
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    # Create templates directory if needed, but assume manual or use static for demo
    app.run(debug=True, host='0.0.0.0', port=5000)