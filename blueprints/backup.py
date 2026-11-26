from flask import Blueprint, jsonify, request, send_file, send_from_directory, session, after_this_request
from datetime import datetime, timezone, timedelta
import sqlite3, os, re, tempfile
from audit import registrar_auditoria
from db import DB_PATH, close_db
from auth import admin_required
from backup_scheduler import BACKUP_DIR

backup_bp = Blueprint('backup', __name__)
AUTO_BACKUP_RE = re.compile(r'^ultrax_auto_[\w\-]+\.db$')
TZ_VE = timezone(timedelta(hours=-4))


def _validar_auto_backup(filename):
    return bool(filename) and filename == os.path.basename(filename) and bool(AUTO_BACKUP_RE.match(filename))


def _open_db_direct(path):
    conn = sqlite3.connect(path, timeout=30.0)
    conn.execute('PRAGMA busy_timeout=30000')
    return conn


def _sqlite_backup_file(src_path, dst_path):
    """Copia atómica y consistente de una BD SQLite usando la API oficial .backup() (segura con WAL)."""
    src = _open_db_direct(src_path)
    dst = _open_db_direct(dst_path)
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()


@backup_bp.route('/api/backup', methods=['GET'])
def backup():
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    tmp_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    tmp_path = tmp_file.name
    tmp_file.close()
    try:
        _sqlite_backup_file(DB_PATH, tmp_path)
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        return jsonify({'error': str(e)}), 500

    @after_this_request
    def _cleanup_tmp(response):
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except OSError:
            pass
        return response

    return send_file(tmp_path, as_attachment=True, download_name=f'ultrax_backup_{ts}.db',
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
        conn = _open_db_direct(tmp)
        try:
            integrity = conn.execute('PRAGMA integrity_check').fetchone()
            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        finally:
            conn.close()
        if not integrity or integrity[0] != 'ok':
            os.remove(tmp)
            return jsonify({'error': 'El archivo falló PRAGMA integrity_check'}), 400
        if not {'financials', 'mapping', 'history'}.issubset(tables):
            os.remove(tmp)
            return jsonify({'error': f'DB inválida. Tablas: {tables}'}), 400
        close_db()
        _sqlite_backup_file(DB_PATH, DB_PATH + '.bk')
        _sqlite_backup_file(tmp, DB_PATH)
        os.remove(tmp)
        conn_aud = _open_db_direct(DB_PATH)
        try:
            registrar_auditoria(conn_aud, session.get('username', 'sistema'), 'backup', 'restaurar_manual', f'archivo={file.filename}')
        finally:
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
        conn = _open_db_direct(full_path)
        try:
            integrity = conn.execute('PRAGMA integrity_check').fetchone()
            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        finally:
            conn.close()
        if not integrity or integrity[0] != 'ok':
            return jsonify({'error': 'El respaldo falló PRAGMA integrity_check'}), 400
        if not {'financials', 'mapping', 'history'}.issubset(tables):
            return jsonify({'error': f'DB inválida. Tablas: {tables}'}), 400
        close_db()
        _sqlite_backup_file(DB_PATH, DB_PATH + '.bk')
        _sqlite_backup_file(full_path, DB_PATH)
        conn_aud = _open_db_direct(DB_PATH)
        try:
            registrar_auditoria(conn_aud, session.get('username', 'sistema'), 'backup', 'restaurar_auto', f'archivo={filename}')
        finally:
            conn_aud.close()
        return jsonify({'ok': True, 'message': f'Base de datos restaurada desde {filename}'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
