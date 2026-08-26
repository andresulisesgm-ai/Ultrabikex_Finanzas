import os
import hashlib
import secrets
import bcrypt
from dotenv import load_dotenv
from functools import wraps
from flask import session, redirect, url_for, jsonify

load_dotenv()

YOCE_PASSWORD = os.environ.get('YOCE_PASSWORD')
CAMILO_PASSWORD = os.environ.get('CAMILO_PASSWORD')

if not YOCE_PASSWORD or not CAMILO_PASSWORD:
    raise RuntimeError(
        "Faltan variables de entorno YOCE_PASSWORD y/o CAMILO_PASSWORD. "
        "Verifica que el archivo .env existe en la raiz del proyecto."
    )

# Usuarios hardcodeados con contraseñas hasheadas (bcrypt)
USERS = {
    'Yoce': {
        'password_hash': bcrypt.hashpw(YOCE_PASSWORD.encode(), bcrypt.gensalt()).decode(),
        'role': 'admin'
    },
    'Camilo': {
        'password_hash': bcrypt.hashpw(CAMILO_PASSWORD.encode(), bcrypt.gensalt()).decode(),
        'role': 'viewer'
    }
}


def verify_password(username, password):
    """Verifica credenciales y retorna el rol si son correctas."""
    user = USERS.get(username)
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
