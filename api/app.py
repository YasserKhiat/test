from flask import Flask, request
import sqlite3
import subprocess
import os
import bcrypt  # Secure hashing

app = Flask(__name__)

# SECURITY FIX: Use environment variable for secret key
SECRET_KEY = os.environ.get("SECRET_KEY", "default-safe-key")

def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # SECURITY FIX: Parameterized queries prevent SQL Injection
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    conn.close()

    # SECURITY FIX: Check hash instead of plain password
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return {"status": "success", "user": username}
    
    return {"status": "error", "message": "Invalid credentials"}

@app.route("/ping", methods=["POST"])
def ping():
    host = request.json.get("host", "")
    
    # SECURITY FIX: Input validation
    if ";" in host or "&" in host or "|" in host:
        return {"error": "Invalid characters"}, 400
        
    try:
        # SECURITY FIX: shell=False prevents command chaining
        output = subprocess.check_output(["ping", "-c", "1", host]) 
        return {"output": output.decode()}
    except subprocess.CalledProcessError:
        return {"error": "Ping failed"}

@app.route("/hash", methods=["POST"])
def hash_password():
    pwd = request.json.get("password", "admin")
    # SECURITY FIX: Use bcrypt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd.encode('utf-8'), salt)
    return {"hash": hashed.decode('utf-8')}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)