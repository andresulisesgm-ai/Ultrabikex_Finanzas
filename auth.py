import hashlib
import secrets
from functools import wraps
from flask import session, redirect, url_for, jsonify

# Usuarios hardcodeados con contraseñas hasheadas (SHA-256)
# Contraseñas por defecto:
#   admin: admin2026
#   viewer: viewer2026
USERS = {
    'admin': {
        'password_hash': hashlib.sha256('admin2026'.encode()).hexdigest(),
        'role': 'admin'
    },
    'viewer': {
        'password_hash': hashlib.sha256('viewer2026'.encode()).hexdigest(),
        'role': 'viewer'
    }
}

def verify_password(username, password):
    """Verifica credenciales y retorna el rol si son correctas."""
    user = USERS.get(username)
    if not user:
        return None

    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if password_hash == user['password_hash']:
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
