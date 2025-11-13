
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import jwt
import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Simple in-memory rate limiting (per IP)
from collections import defaultdict
import time
login_attempts = defaultdict(list)  # {ip: [timestamps]}
MAX_ATTEMPTS = 5
WINDOW_SECONDS = 60

# Create Flask app and enable CORS for cross-origin requests from frontend
app = Flask(__name__)
CORS(app, supports_credentials=True)

SECRET_KEY = os.environ.get('SECRET_KEY')  # Secret key for JWT encoding/decoding

# Function to get a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row  # Allows dict-like access to rows
    return conn

# Function to initialize the database and create the users table if it doesn't exist
def init_db():
    conn = get_db_connection()
    # Create users table with id, username, and password_hash columns
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )''')
    # Add a default user for testing (only if not already present)
    try:
        default_hash = generate_password_hash("rocket123")
        conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("admin", default_hash))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # User already exists, skip adding
    conn.close()

# Route for user login
# Accepts POST requests with JSON body containing username and password
# Returns success if credentials match a user in the database
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()  # Parse JSON body
    username = data.get('username')
    password = data.get('password')
    # Validate input
    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required."}), 400

    # Rate limiting by IP
    ip = request.remote_addr
    now = time.time()
    # Remove old attempts
    login_attempts[ip] = [t for t in login_attempts[ip] if now - t < WINDOW_SECONDS]
    if len(login_attempts[ip]) >= MAX_ATTEMPTS:
        return jsonify({"success": False, "message": "Too many login attempts. Please wait and try again."}), 429
    login_attempts[ip].append(now)

    conn = get_db_connection()
    # Query for user by username
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    print(f"Login attempt for user: {username}")
    if user:
        print("User found in DB.")
    else:
        print("User not found in DB.")
    if user and check_password_hash(user['password_hash'], password):
        print("Password correct. Generating JWT.")
        # User found and password matches
        payload = {
            'username': username,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)  # Token expires in 1 hour
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        print(f"JWT generated: {token}")
        resp = jsonify({"success": True})
        # Set JWT as HTTP-only cookie with cross-origin compatibility
        resp.set_cookie(
            'jwt',
            token,
            httponly=True,
            secure=False,  # Use True only with HTTPS in production
            samesite='Strict',
            max_age=3600,
            path='/'
        )
        print("JWT set as HTTP-only cookie.")
        return resp
    # User not found or password incorrect
    return jsonify({"success": False, "message": "Invalid credentials."}), 401

# Route for user signup (registration)
# Accepts POST requests with JSON body containing username and password
# Adds new user to the database if username is not taken
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()  # Parse JSON body
    username = data.get('username')
    password = data.get('password')
    # Validate input
    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required."}), 400

    conn = get_db_connection()
    try:
        # Hash the password before storing
        password_hash = generate_password_hash(password)
        conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        conn.close()
        # Signup successful
        return jsonify({"success": True, "message": "Signup successful!"})
    except sqlite3.IntegrityError:
        # Username already exists
        conn.close()
        return jsonify({"success": False, "message": "Username already exists."}), 409

# Route to serve game files securely to authenticated users
# Usage: /game/<filename> (e.g., /game/main.html)
# Requires a valid JWT token in the Authorization header
@app.route('/game/<path:filename>', methods=['GET'])
def serve_game_file(filename):
    token = request.cookies.get('jwt')
    print(f"Game file request for: {filename}")
    print(f"JWT from cookie: {token}")
    if not token:
        print("No JWT cookie found.")
        return jsonify({'success': False, 'message': 'Missing authentication cookie.'}), 401
    try:
        jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        print("JWT decoded successfully.")
    except jwt.ExpiredSignatureError:
        print("JWT expired.")
        return jsonify({'success': False, 'message': 'Token expired.'}), 401
    except jwt.InvalidTokenError:
        print("Invalid JWT.")
        return jsonify({'success': False, 'message': 'Invalid token.'}), 401
    # If valid, serve the requested game file from the game directory
    print(f"Serving file: {filename}")
    return send_from_directory('../game', filename)

# Main entry point: initialize database and start Flask app
if __name__ == '__main__':
    init_db()  # Ensure database and table exist
    app.run(debug=True)
