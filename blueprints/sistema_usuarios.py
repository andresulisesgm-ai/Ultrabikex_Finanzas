from datetime import datetime
import re
import bcrypt
from flask import Blueprint, jsonify, request, session
from audit import registrar_auditoria
from auth import login_required, admin_required
from db import get_db

sistema_usuarios_bp = Blueprint('sistema_usuarios', __name__)


@sistema_usuarios_bp.route('/api/admin/users', methods=['GET'])
@admin_required
def listar_usuarios():
    """Lista todos los usuarios sin password_hash e indica si están bloqueados."""
    db = get_db()
    rows = db.execute(
        'SELECT username, role, activo, es_superadmin, intentos_fallidos, bloqueado_hasta '
        'FROM users ORDER BY username'
    ).fetchall()
    ahora_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return jsonify([
        {
            'username': r['username'],
            'role': r['role'],
            'activo': r['activo'],
            'es_superadmin': r['es_superadmin'],
            'intentos_fallidos': r['intentos_fallidos'],
            'bloqueado_hasta': r['bloqueado_hasta'],
            'bloqueado': bool(r['bloqueado_hasta'] and r['bloqueado_hasta'] > ahora_str),
        }
        for r in rows
    ])


@sistema_usuarios_bp.route('/api/admin/users', methods=['POST'])
@admin_required
def crear_usuario():
    """Crea un nuevo usuario con rol admin o viewer y clave bcrypt."""
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    role = (data.get('role') or '').strip()

    if not re.fullmatch(r'[A-Za-z0-9_.-]{3,30}', username):
        return jsonify({'error': 'Usuario inválido (3-30 caracteres sin espacios)'}), 400
    if role not in ('admin', 'viewer'):
        return jsonify({'error': 'Rol inválido (admin o viewer)'}), 400
    if len(password) < 8:
        return jsonify({'error': 'La clave debe tener al menos 8 caracteres'}), 400

    db = get_db()
    dup = db.execute(
        'SELECT username FROM users WHERE LOWER(username) = LOWER(?)',
        (username,),
    ).fetchone()
    if dup:
        return jsonify({'error': 'Ya existe un usuario con ese nombre'}), 409

    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    db.execute(
        'INSERT INTO users (username, password_hash, role, activo, es_superadmin, intentos_fallidos, bloqueado_hasta) '
        'VALUES (?, ?, ?, 1, 0, 0, NULL)',
        (username, pw_hash, role),
    )
    db.commit()
    registrar_auditoria(
        db,
        session.get('username', 'sistema'),
        'usuarios',
        'crear_usuario',
        f'username={username}, role={role}',
    )
    return jsonify({
        'username': username,
        'role': role,
        'activo': 1,
        'es_superadmin': 0,
    }), 201


@sistema_usuarios_bp.route('/api/admin/users/<username>', methods=['PUT'])
@admin_required
def actualizar_usuario(username):
    """Actualiza el rol y estado activo de un usuario."""
    db = get_db()
    usr = db.execute(
        'SELECT username, es_superadmin FROM users WHERE username = ?',
        (username,),
    ).fetchone()
    if not usr:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    if usr['es_superadmin'] == 1 and session.get('es_superadmin') != 1:
        return jsonify({'error': 'No puedes modificar una cuenta superadministrador'}), 403

    data = request.get_json(silent=True) or {}
    role = (data.get('role') or '').strip()
    activo = int(bool(data.get('activo')))

    if role not in ('admin', 'viewer'):
        return jsonify({'error': 'Rol inválido (admin o viewer)'}), 400
    if username == session.get('username') and not activo:
        return jsonify({'error': 'No puedes desactivar tu propio usuario'}), 400

    db.execute(
        'UPDATE users SET role = ?, activo = ? WHERE username = ?',
        (role, activo, username),
    )
    db.commit()
    registrar_auditoria(
        db,
        session.get('username', 'sistema'),
        'usuarios',
        'editar_usuario',
        f'username={username}, role={role}, activo={activo}',
    )
    return jsonify({'username': username, 'role': role, 'activo': activo}), 200


@sistema_usuarios_bp.route('/api/admin/users/<username>/unlock', methods=['POST'])
@admin_required
def desbloquear_usuario(username):
    """Desbloquea un usuario y reinicia su contador de intentos fallidos."""
    db = get_db()
    usr = db.execute(
        'SELECT username, es_superadmin FROM users WHERE username = ?',
        (username,),
    ).fetchone()
    if not usr:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    if usr['es_superadmin'] == 1 and session.get('es_superadmin') != 1:
        return jsonify({'error': 'No puedes modificar una cuenta superadministrador'}), 403

    db.execute(
        'UPDATE users SET intentos_fallidos = 0, bloqueado_hasta = NULL WHERE username = ?',
        (username,),
    )
    db.commit()
    registrar_auditoria(
        db,
        session.get('username', 'sistema'),
        'usuarios',
        'desbloquear_usuario',
        f'username={username}',
    )
    return jsonify({'ok': True, 'username': username}), 200


@sistema_usuarios_bp.route('/api/perfil/cambiar_clave', methods=['POST'])
@login_required
def cambiar_clave_propia():
    """Permite al usuario autenticado cambiar su propia clave."""
    data = request.get_json(silent=True) or {}
    clave_actual = data.get('clave_actual') or ''
    clave_nueva = data.get('clave_nueva') or ''
    clave_confirmacion = data.get('clave_confirmacion') or ''

    if not clave_actual or not clave_nueva or not clave_confirmacion:
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400
    if clave_nueva != clave_confirmacion:
        return jsonify({'error': 'La confirmación no coincide con la clave nueva'}), 400
    if len(clave_nueva) < 8:
        return jsonify({'error': 'La clave nueva debe tener al menos 8 caracteres'}), 400

    username = session['username']
    db = get_db()
    row = db.execute(
        'SELECT password_hash FROM users WHERE username = ?',
        (username,),
    ).fetchone()
    if not row or not bcrypt.checkpw(clave_actual.encode(), row['password_hash'].encode()):
        return jsonify({'error': 'La clave actual es incorrecta'}), 400

    new_hash = bcrypt.hashpw(clave_nueva.encode(), bcrypt.gensalt()).decode()
    db.execute(
        'UPDATE users SET password_hash = ? WHERE username = ?',
        (new_hash, username),
    )
    db.commit()
    registrar_auditoria(
        db,
        username,
        'usuarios',
        'cambiar_clave_propia',
        f'username={username}',
    )
    return jsonify({'ok': True, 'message': 'Clave actualizada correctamente'}), 200
