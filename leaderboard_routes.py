# leaderboard_routes.py
from flask import Blueprint, render_template
import sqlite3

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('/leaderboard')
def leaderboard():
    conn = sqlite3.connect('Jain_Connect.db')
    users = conn.execute('SELECT username, xp FROM users ORDER BY xp DESC LIMIT 50').fetchall()
    conn.close()

    ranked_users = []
    for i, (username, xp) in enumerate(users, start=1):
        rank, color = get_rank_and_badge(xp)
        ranked_users.append({
            'position': i,
            'username': username,
            'xp': xp,
            'rank': rank,
            'color': color
        })

    return render_template('leaderboard.html', users=ranked_users)

def get_rank_and_badge(xp):
    if xp >= 1500:
        return "Mythic", "#FF4500"
    elif xp >= 1000:
        return "Legend", "#FFD700"
    elif xp >= 600:
        return "Elite", "#00FF7F"
    elif xp >= 300:
        return "Influencer", "#00BFFF"
    elif xp >= 150:
        return "Contributor", "#9370DB"
    elif xp >= 50:
        return "Explorer", "#6495ED"
    else:
        return "Rookie", "#A9A9A9"
