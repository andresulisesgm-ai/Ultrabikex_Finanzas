import os
import sqlite3
import hashlib
import secrets
import bcrypt
from functools import wraps
from flask import session, redirect, url_for, jsonify

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'ultrax.db')

def get_user(username):
    """Obtiene un usuario desde la tabla users."""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        'SELECT username, password_hash, role FROM users WHERE username = ?',
        (username,)
    ).fetchone()
    conn.close()
    if not row:
        return None
    return {'username': row[0], 'password_hash': row[1], 'role': row[2]}

def verify_password(username, password):
    """Verifica credenciales y retorna el rol si son correctas."""
    user = get_user(username)
    if not user:
        return None
    if bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
        return user['role']
    return None


def login_required(f):
    """Decorador: requiere que el usuario esté autenticado."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Decorador: requiere rol admin."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login_page'))
        if session.get('role') != 'admin':
            return jsonify({'error': 'Acceso denegado. Se requiere rol de administrador.'}), 403
        return f(*args, **kwargs)
    return decorated

def get_current_user():
    """Retorna información del usuario actual."""
    if 'username' in session:
        return {
            'username': session['username'],
            'role': session['role']
        }
    return None

def is_admin():
    """Verifica si el usuario actual es admin."""
    return session.get('role') == 'admin'

def is_viewer():
    """Verifica si el usuario actual es viewer."""
    return session.get('role') == 'viewer'

def change_password(username, current_password, new_password):
    """Cambia la clave de un usuario, validando la clave actual primero."""
    if not verify_password(username, current_password):
        return False, "Clave actual incorrecta."
    if len(new_password) < 8:
        return False, "La clave nueva debe tener al menos 8 caracteres."
    new_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    conn = sqlite3.connect(DB_PATH)
    conn.execute('UPDATE users SET password_hash = ? WHERE username = ?', (new_hash, username))
    conn.commit()
    conn.close()
    return True, "Clave actualizada correctamente."

