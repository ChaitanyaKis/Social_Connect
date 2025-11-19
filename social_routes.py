from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.utils import secure_filename

social_bp = Blueprint('social', __name__)
UPLOAD_FOLDER = 'static/uploads'

@social_bp.route('/feed')
def social_feed():
    conn = sqlite3.connect('Jain_Connect.db')
    posts = conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    comments = conn.execute("SELECT * FROM comments").fetchall()
    conn.close()

    # Group comments by post_id
    comment_dict = {}
    for c in comments:
        comment_dict.setdefault(c[1], []).append({'username': c[2], 'text': c[3]})

    return render_template('social_feed.html', posts=posts, comments=comment_dict)

@social_bp.route('/post', methods=['POST'])
def create_post():
    content = request.form['content']
    image = request.files.get('image')
    username = session.get('username')

    image_filename = None
    if image and image.filename:
        image_filename = secure_filename(image.filename)
        image.save(os.path.join(UPLOAD_FOLDER, image_filename))

    conn = sqlite3.connect('Jain_Connect.db')
    conn.execute("INSERT INTO posts (username, content, image_path, likes) VALUES (?, ?, ?, ?)",
                 (username, content, image_filename, 0))
    conn.execute("UPDATE users SET xp = xp + 10 WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    return redirect(url_for('social.social_feed'))

@social_bp.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    username = session.get('username')
    if not username:
        return redirect(url_for('auth.home'))

    conn = sqlite3.connect('Jain_Connect.db')
    cursor = conn.cursor()

    # Check if user already liked this post
    cursor.execute("SELECT * FROM likes WHERE post_id = ? AND username = ?", (post_id, username))
    existing_like = cursor.fetchone()

    if not existing_like:
        # Add like record
        cursor.execute("INSERT INTO likes (post_id, username) VALUES (?, ?)", (post_id, username))
        # Increase post like count
        cursor.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (post_id,))

        # XP to liker
        cursor.execute("UPDATE users SET xp = xp + 2 WHERE username = ?", (username,))

        # XP to post owner
        cursor.execute("SELECT username FROM posts WHERE id = ?", (post_id,))
        post_owner = cursor.fetchone()
        if post_owner:
            cursor.execute("UPDATE users SET xp = xp + 5 WHERE username = ?", (post_owner[0],))

        conn.commit()

    conn.close()
    return redirect(url_for('social.social_feed'))


@social_bp.route('/comment/<int:post_id>', methods=['POST'])
def comment_post(post_id):
    username = session.get('username')
    comment_text = request.form['comment']

    if username and comment_text:
        conn = sqlite3.connect('Jain_Connect.db')
        conn.execute("INSERT INTO comments (post_id, username, comment_text) VALUES (?, ?, ?)",
                     (post_id, username, comment_text))
        
        # XP for commenter
        conn.execute("UPDATE users SET xp = xp + 3 WHERE username = ?", (username,))

        conn.commit()
        conn.close()
    return redirect(url_for('social.social_feed'))


@social_bp.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('auth.home'))

    username = session['username']
    conn = sqlite3.connect('Jain_Connect.db')
    user = conn.execute("SELECT name, email, phone, xp FROM users WHERE username=?", (username,)).fetchone()
    posts = conn.execute("SELECT * FROM posts WHERE username=?", (username,)).fetchall()
    conn.close()

    if user:
        name, email, phone, xp = user
    else:
        name = email = phone = ''
        xp = 0

    rank, ring_color = get_rank_and_badge(xp)

    return render_template('profile.html',
        username=username, name=name, email=email, phone=phone,
        xp=xp, rank=rank, ring_color=ring_color,
        total_posts=len(posts), total_likes=sum(p[4] for p in posts)
    )

@social_bp.route('/profile/<username>')
def view_user_profile(username):
    conn = sqlite3.connect('Jain_Connect.db')
    user = conn.execute("SELECT name, email, phone, xp FROM users WHERE username = ?", (username,)).fetchone()
    posts = conn.execute("SELECT * FROM posts WHERE username=?", (username,)).fetchall()
    conn.close()

    if not user:
        return f"<h2 style='color:white; text-align:center;'>User '{username}' not found</h2>"

    name, email, phone, xp = user
    rank, ring_color = get_rank_and_badge(xp)

    return render_template('profile.html',
        username=username, name=name, email=email, phone=phone,
        xp=xp, rank=rank, ring_color=ring_color,
        total_posts=len(posts), total_likes=sum(p[4] for p in posts)
    )

# Rank and Badge Calculation Function
def get_rank_and_badge(xp):
    if xp >= 1500:
        return "Mythic", "#FFD700"  # Gold
    elif xp >= 1000:
        return "Legend", "#FF8C00"  # Orange
    elif xp >= 600:
        return "Elite", "#00FF00"  # Green
    elif xp >= 300:
        return "Influencer", "#00C6FF"  # Blue
    elif xp >= 150:
        return "Contributor", "#AAAAFF"  # Purple
    elif xp >= 50:
        return "Explorer", "#8888FF"  # Light Blue
    else:
        return "Rookie", "#888888"  # Grey
