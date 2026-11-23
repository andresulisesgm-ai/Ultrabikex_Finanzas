import os
import sqlite3
import hashlib
import secrets
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import session, redirect, url_for, jsonify, request

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'ultrax.db')

def get_user(username):
    """Obtiene un usuario desde la tabla users."""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        'SELECT username, password_hash, role, activo, es_superadmin, intentos_fallidos, bloqueado_hasta '
        'FROM users WHERE username = ?',
        (username,)
    ).fetchone()
    conn.close()
    if not row:
        return None
    return {
        'username': row[0],
        'password_hash': row[1],
        'role': row[2],
        'activo': row[3],
        'es_superadmin': row[4],
        'intentos_fallidos': row[5],
        'bloqueado_hasta': row[6],
    }

def verify_password(username, password):
    """Verifica credenciales y retorna el rol si son correctas."""
    user = get_user(username)
    if not user:
        return None
    if bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
        return user['role']
    return None


def authenticate_user(username, password):
    """Autentica usuario validando activo, bloqueo temporal y contador de intentos."""
    user = get_user(username)
    if not user:
        return False, 'Credenciales inválidas', 401
    if user['activo'] == 0:
        return False, 'Usuario desactivado', 403

    ahora = datetime.now()
    ahora_str = ahora.strftime('%Y-%m-%d %H:%M:%S')
    if user['bloqueado_hasta'] and user['bloqueado_hasta'] > ahora_str:
        return False, 'Usuario bloqueado temporalmente. Contacte al administrador.', 423

    if not bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
        intentos = (user['intentos_fallidos'] or 0) + 1
        conn = sqlite3.connect(DB_PATH)
        if intentos >= 5:
            bloqueado = (ahora + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')
            conn.execute(
                'UPDATE users SET intentos_fallidos = ?, bloqueado_hasta = ? WHERE username = ?',
                (intentos, bloqueado, username),
            )
            conn.commit()
            conn.close()
            return False, 'Usuario bloqueado temporalmente. Contacte al administrador.', 423
        conn.execute(
            'UPDATE users SET intentos_fallidos = ? WHERE username = ?',
            (intentos, username),
        )
        conn.commit()
        conn.close()
        return False, 'Credenciales inválidas', 401

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        'UPDATE users SET intentos_fallidos = 0, bloqueado_hasta = NULL WHERE username = ?',
        (username,),
    )
    conn.commit()
    conn.close()
    return True, {
        'username': user['username'],
        'role': user['role'],
        'es_superadmin': int(user['es_superadmin'] or 0),
    }, 200


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

def superadmin_required(f):
    """Decorador: requiere sesión activa y es_superadmin == 1."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'No autenticado. Inicia sesión.'}), 401
            return redirect(url_for('login_page'))
        if session.get('es_superadmin') != 1:
            return jsonify({'error': 'Acceso denegado. Se requiere rol de superadministrador.'}), 403
        return f(*args, **kwargs)
    return decorated

def get_current_user():
    """Retorna información del usuario actual."""
    if 'username' in session:
        return {
            'username': session['username'],
            'role': session['role'],
            'es_superadmin': int(session.get('es_superadmin', 0)),
        }
    return None

def is_admin():
    """Verifica si el usuario actual es admin."""
    return session.get('role') == 'admin'

def is_viewer():
    """Verifica si el usuario actual es viewer."""
    return session.get('role') == 'viewer'

def admin_reset_password(username, new_password, admin_username):

    """Resetea la clave de un usuario sin requerir la clave anterior. Solo para uso admin. Registra el evento en log."""
    if len(new_password) < 8:
        return False, "La clave nueva debe tener al menos 8 caracteres."
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute('SELECT username FROM users WHERE username = ?', (username,))
    if not cur.fetchone():
        conn.close()
        return False, "Usuario no encontrado."
    new_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    conn.execute('UPDATE users SET password_hash = ?, intentos_fallidos = 0, bloqueado_hasta = NULL WHERE username = ?', (new_hash, username))
    conn.commit()
    conn.close()

    import datetime
    log_path = os.path.join(os.path.dirname(__file__), 'password_reset_audit.log')
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.datetime.now().isoformat()} | admin={admin_username} | usuario_afectado={username}\n")

    return True, "Clave restablecida correctamente."


def list_users():
    """Retorna username y role de todos los usuarios, sin el hash."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute('SELECT username, role FROM users ORDER BY username').fetchall()
    conn.close()
    return [{'username': r[0], 'role': r[1]} for r in rows]


