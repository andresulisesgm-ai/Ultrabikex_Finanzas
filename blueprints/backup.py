from flask import Blueprint, jsonify, request, send_file, send_from_directory, session
from datetime import datetime, timezone, timedelta
import sqlite3, os, re, shutil, tempfile
from audit import registrar_auditoria
from db import DB_PATH
from auth import admin_required
from backup_scheduler import BACKUP_DIR

backup_bp = Blueprint('backup', __name__)
AUTO_BACKUP_RE = re.compile(r'^ultrax_auto_[\w\-]+\.db$')
TZ_VE = timezone(timedelta(hours=-4))


def _validar_auto_backup(filename):
    return bool(filename) and filename == os.path.basename(filename) and bool(AUTO_BACKUP_RE.match(filename))


@backup_bp.route('/api/backup', methods=['GET'])
def backup():
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    return send_file(DB_PATH, as_attachment=True, download_name=f'ultrax_backup_{ts}.db',
                     mimetype='application/octet-stream')


@backup_bp.route('/api/restore', methods=['POST'])
@admin_required
def restore():
    file = request.files.get('file')
    if not file: return jsonify({'error': 'No se envió archivo'}), 400
    if not file.filename.endswith('.db'): return jsonify({'error': 'El archivo debe ser .db'}), 400
    tmp_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    tmp = tmp_file.name
    tmp_file.close()
    try:
        file.save(tmp)
        conn   = sqlite3.connect(tmp)
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        conn.close()
        if not {'financials', 'mapping', 'history'}.issubset(tables):
            os.remove(tmp)
            return jsonify({'error': f'DB inválida. Tablas: {tables}'}), 400
        shutil.copy2(DB_PATH, DB_PATH + '.bk')
        shutil.move(tmp, DB_PATH)
        conn_aud = sqlite3.connect(DB_PATH)
        registrar_auditoria(conn_aud, session.get('username', 'sistema'), 'backup', 'restaurar_manual', f'archivo={file.filename}')
        conn_aud.close()
        return jsonify({'ok': True, 'message': 'Base de datos restaurada correctamente'})
    except Exception as e:
        if os.path.exists(tmp): os.remove(tmp)
        return jsonify({'error': str(e)}), 500


@backup_bp.route('/api/backup/auto/list', methods=['GET'])
@admin_required
def list_auto_backups():
    """Lista los respaldos automáticos disponibles en data/backups/."""
    if not os.path.isdir(BACKUP_DIR):
        return jsonify([])
    items = []
    for fname in os.listdir(BACKUP_DIR):
        if not _validar_auto_backup(fname):
            continue
        full_path = os.path.join(BACKUP_DIR, fname)
        if not os.path.isfile(full_path):
            continue
        mtime = os.path.getmtime(full_path)
        items.append({
            'filename': fname,
            'fecha_ve': datetime.fromtimestamp(mtime, tz=TZ_VE).strftime('%Y-%m-%d %H:%M:%S'),
            'size_mb': round(os.path.getsize(full_path) / (1024 * 1024), 2),
            '_mtime': mtime,
        })
    items.sort(key=lambda x: x['_mtime'], reverse=True)
    for it in items:
        it.pop('_mtime', None)
    return jsonify(items)


@backup_bp.route('/api/backup/auto/download/<filename>', methods=['GET'])
@admin_required
def download_auto_backup(filename):
    """Descarga un respaldo automático validado desde data/backups/."""
    if not _validar_auto_backup(filename):
        return jsonify({'error': 'Nombre de archivo inválido'}), 400
    full_path = os.path.join(BACKUP_DIR, filename)
    if not os.path.isfile(full_path):
        return jsonify({'error': 'Respaldo no encontrado'}), 404
    return send_from_directory(
        BACKUP_DIR,
        filename,
        as_attachment=True,
        mimetype='application/octet-stream',
    )


@backup_bp.route('/api/backup/auto/restore/<filename>', methods=['POST'])
@admin_required
def restore_auto_backup(filename):
    """Restaura la base de datos desde un respaldo automático validado."""
    if not _validar_auto_backup(filename):
        return jsonify({'error': 'Nombre de archivo inválido'}), 400
    full_path = os.path.join(BACKUP_DIR, filename)
    if not os.path.isfile(full_path):
        return jsonify({'error': 'Respaldo no encontrado'}), 404
    try:
        conn = sqlite3.connect(full_path)
        integrity = conn.execute('PRAGMA integrity_check').fetchone()
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        conn.close()
        if not integrity or integrity[0] != 'ok':
            return jsonify({'error': 'El respaldo falló PRAGMA integrity_check'}), 400
        if not {'financials', 'mapping', 'history'}.issubset(tables):
            return jsonify({'error': f'DB inválida. Tablas: {tables}'}), 400
        shutil.copy2(DB_PATH, DB_PATH + '.bk')
        shutil.copy2(full_path, DB_PATH)
        conn_aud = sqlite3.connect(DB_PATH)
        registrar_auditoria(conn_aud, session.get('username', 'sistema'), 'backup', 'restaurar_auto', f'archivo={filename}')
        conn_aud.close()
        return jsonify({'ok': True, 'message': f'Base de datos restaurada desde {filename}'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
