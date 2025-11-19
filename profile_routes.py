from flask import Blueprint, render_template, redirect, url_for, session
import sqlite3

profile_bp = Blueprint('profile', __name__)

# Self profile
@profile_bp.route('/profile')
def own_profile():
    if 'username' not in session:
        return redirect(url_for('auth.home'))

    username = session['username']

    conn = sqlite3.connect('Jain_Connect.db')
    user_data = conn.execute("SELECT name, email, phone, xp FROM users WHERE username=?", (username,)).fetchone()
    posts = conn.execute("SELECT * FROM posts WHERE username=?", (username,)).fetchall()
    conn.close()

    name, email, phone, xp = user_data
    rank, ring_color = get_rank_and_badge(xp)

    return render_template('profile.html',
        name=name, username=username, email=email, phone=phone, xp=xp,
        rank=rank, ring_color=ring_color, total_posts=len(posts), total_likes=sum(p[4] for p in posts)
    )

# View other users
@profile_bp.route('/profile/<username>')
def view_profile(username):
    conn = sqlite3.connect('Jain_Connect.db')
    user_data = conn.execute("SELECT name, email, phone, xp FROM users WHERE username=?", (username,)).fetchone()
    posts = conn.execute("SELECT * FROM posts WHERE username=?", (username,)).fetchall()
    conn.close()

    if not user_data:
        return f"<h2 style='color:white; text-align:center;'>User '{username}' not found</h2>"

    name, email, phone, xp = user_data
    rank, ring_color = get_rank_and_badge(xp)

    return render_template('profile.html',
        name=name, username=username, email=email, phone=phone, xp=xp,
        rank=rank, ring_color=ring_color, total_posts=len(posts), total_likes=sum(p[4] for p in posts)
    )

def get_rank_and_badge(xp):
    if xp < 100:
        return "Beginner", "#777"
    elif xp < 300:
        return "Rookie", "#4caf50"
    elif xp < 600:
        return "Explorer", "#2196f3"
    elif xp < 1000:
        return "Achiever", "#9c27b0"
    elif xp > 1000:
        return "Legend", "#ff9800"
