#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para cambiar las contraseñas de usuarios ULTRAX
"""
import hashlib
import sys

def generar_hash(password):
    """Genera el hash SHA-256 de una contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def actualizar_auth_py(admin_hash, viewer_hash):
    """Actualiza el archivo auth.py con los nuevos hashes"""
    contenido = f'''import hashlib
import secrets
from functools import wraps
from flask import session, redirect, url_for, jsonify

# Usuarios hardcodeados con contraseñas hasheadas (SHA-256)
USERS = {{
    'admin': {{
        'password_hash': '{admin_hash}',
        'role': 'admin'
    }},
    'viewer': {{
        'password_hash': '{viewer_hash}',
        'role': 'viewer'
    }}
}}

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
            return jsonify({{'error': 'Acceso denegado. Se requiere rol de administrador.'}}), 403
        return f(*args, **kwargs)
    return decorated

def get_current_user():
    """Retorna información del usuario actual."""
    if 'username' in session:
        return {{
            'username': session['username'],
            'role': session['role']
        }}
    return None

def is_admin():
    """Verifica si el usuario actual es admin."""
    return session.get('role') == 'admin'

def is_viewer():
    """Verifica si el usuario actual es viewer."""
    return session.get('role') == 'viewer'
'''

    with open('auth.py', 'w', encoding='utf-8') as f:
        f.write(contenido)

def main():
    print("=" * 60)
    print("  CAMBIO DE CONTRASEÑAS - ULTRAX")
    print("=" * 60)
    print()

    # Cambiar contraseña de admin
    print("📋 USUARIO ADMINISTRADOR (admin)")
    print("-" * 60)
    admin_pass = input("Nueva contraseña para admin: ").strip()

    if len(admin_pass) < 4:
        print("❌ Error: La contraseña debe tener al menos 4 caracteres")
        sys.exit(1)

    admin_confirm = input("Confirma la contraseña para admin: ").strip()

    if admin_pass != admin_confirm:
        print("❌ Error: Las contraseñas no coinciden")
        sys.exit(1)

    admin_hash = generar_hash(admin_pass)
    print("✅ Contraseña de admin configurada")
    print()

    # Cambiar contraseña de viewer
    print("📋 USUARIO VISOR (viewer)")
    print("-" * 60)
    viewer_pass = input("Nueva contraseña para viewer: ").strip()

    if len(viewer_pass) < 4:
        print("❌ Error: La contraseña debe tener al menos 4 caracteres")
        sys.exit(1)

    viewer_confirm = input("Confirma la contraseña para viewer: ").strip()

    if viewer_pass != viewer_confirm:
        print("❌ Error: Las contraseñas no coinciden")
        sys.exit(1)

    viewer_hash = generar_hash(viewer_pass)
    print("✅ Contraseña de viewer configurada")
    print()

    # Confirmar cambios
    print("=" * 60)
    print("⚠️  ¿Deseas aplicar estos cambios?")
    confirmar = input("Escribe 'SI' para confirmar: ").strip().upper()

    if confirmar != 'SI':
        print("❌ Operación cancelada")
        sys.exit(0)

    # Actualizar archivo
    try:
        actualizar_auth_py(admin_hash, viewer_hash)
        print()
        print("=" * 60)
        print("✅ ¡CONTRASEÑAS ACTUALIZADAS EXITOSAMENTE!")
        print("=" * 60)
        print()
        print("📝 Nuevas credenciales:")
        print(f"   Admin:  admin / {admin_pass}")
        print(f"   Viewer: viewer / {viewer_pass}")
        print()
        print("⚠️  IMPORTANTE: Reinicia la aplicación para que los cambios surtan efecto")
        print()
    except Exception as e:
        print(f"❌ Error al actualizar auth.py: {e}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operación cancelada por el usuario")
        sys.exit(0)
