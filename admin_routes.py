from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)
ADMIN_PASSWORD = "admin123"

@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Incorrect password.')
    return render_template('admin_login.html')

@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin.admin_login'))

    conn = sqlite3.connect('Jain_Connect.db')
    conn.row_factory = sqlite3.Row
    users = conn.execute("SELECT id, username, name, email, xp, banned_until, password FROM users").fetchall()
    conn.close()
    return render_template('admin_dashboard.html', users=users)

@admin_bp.route('/admin/update_xp', methods=['POST'])
def update_xp():
    if not session.get('is_admin'):
        return redirect(url_for('admin.admin_login'))

    user_id = request.form.get('user_id')
    xp = request.form.get('xp')
    conn = sqlite3.connect('Jain_Connect.db')
    conn.execute("UPDATE users SET xp = ? WHERE id = ?", (xp, user_id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/ban_user', methods=['POST'])
def ban_user():
    if not session.get('is_admin'):
        return redirect(url_for('admin.admin_login'))

    user_id = request.form.get('user_id')
    days = int(request.form.get('ban_days'))
    banned_until = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    conn = sqlite3.connect('Jain_Connect.db')
    conn.execute("UPDATE users SET banned_until = ? WHERE id = ?", (banned_until, user_id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.admin_dashboard'))
