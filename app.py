from flask import Flask, redirect, url_for, session
from auth_routes import auth_bp
from social_routes import social_bp
from profile_routes import profile_bp
import sqlite3
from leaderboard_routes import leaderboard_bp
from admin_routes import admin_bp


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(social_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(leaderboard_bp)
app.register_blueprint(admin_bp)

# Initialize Database Tables if not exist
def init_db():
    conn = sqlite3.connect('Jain_Connect.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            content TEXT,
            image_path TEXT,
            likes INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            username TEXT,
            comment_text TEXT,
            FOREIGN KEY(post_id) REFERENCES posts(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            username TEXT,
            UNIQUE(post_id, username)
        )
    ''')

    conn.commit()
    conn.close()

init_db()

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return '<h1 style="color: white; background: black; height: 100vh; display: flex; align-items: center; justify-content: center;">Welcome to Jain Connect Dashboard</h1>'
    else:
        return redirect(url_for('auth.home'))

if __name__ == '__main__':
    app.run(debug=True)
