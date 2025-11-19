from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    login_message = session.pop('login_message', None)
    signup_message = session.pop('signup_message', None)
    return render_template('login.html', login_message=login_message, signup_message=signup_message)

@auth_bp.route('/signup', methods=['POST'])

def signup():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    username = request.form['username']
    password = request.form['password']

    try:
        conn = sqlite3.connect('Jain_Connect.db')
        conn.execute("INSERT INTO users (name, email, phone, username, password) VALUES (?, ?, ?, ?, ?)",
                     (name, email, phone, username, password))
        conn.commit()
        conn.close()
        
        # ✅ Auto-login here:
        session['username'] = username
        return redirect(url_for('social_feed.html'))

    except sqlite3.IntegrityError:
        session['signup_message'] = '❌ Username already exists.'
        return redirect(url_for('auth.home'))


@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('Jain_Connect.db')
    cursor = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['username'] = username
        return redirect(url_for('social.social_feed'))
    else:
        session['login_message'] = '❌ Invalid Username or Password.'
        return redirect(url_for('auth.home'))
