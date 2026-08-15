from flask import Blueprint, jsonify, request, send_file
from datetime import datetime
import sqlite3, os, shutil, tempfile
from db import DB_PATH
from auth import admin_required

backup_bp = Blueprint('backup', __name__)


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
        return jsonify({'ok': True, 'message': 'Base de datos restaurada correctamente'})
    except Exception as e:
        if os.path.exists(tmp): os.remove(tmp)
        return jsonify({'error': str(e)}), 500
