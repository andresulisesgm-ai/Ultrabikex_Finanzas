from flask import Blueprint, jsonify, request
from db import get_db
from auth import admin_required
from engine import MONTH_TO_QUARTER

historial_bp = Blueprint('historial', __name__)


@historial_bp.route('/api/history', methods=['GET'])
def get_history():
    db = get_db()
    return jsonify([dict(r) for r in db.execute('SELECT * FROM history ORDER BY id DESC').fetchall()])


@historial_bp.route('/api/history/<int:hid>/revert', methods=['POST'])
@admin_required
def revert_history(hid):
    db = get_db()
    h  = db.execute('SELECT * FROM history WHERE id=?', (hid,)).fetchone()
    if not h:         return jsonify({'error': 'No encontrado'}), 404
    if h['reverted']: return jsonify({'error': 'Ya revertida'}), 400
    if h['is_esf']:
        quarter = MONTH_TO_QUARTER.get(h['month'], 1)
        db.execute('DELETE FROM esf_data WHERE year=? AND quarter=? AND unit=? AND empresa_id=?', (h['year'], quarter, h['unit'], h['empresa_id']))
        db.execute('DELETE FROM financials_detail WHERE year=? AND quarter=? AND unit=? AND report_type=\'esf\' AND empresa_id=?', (h['year'], quarter, h['unit'], h['empresa_id']))
    else:
        db.execute('DELETE FROM financials WHERE year=? AND month=? AND unit=?', (h['year'], h['month'], h['unit']))
    db.execute('UPDATE history SET reverted=1 WHERE id=?', (hid,))
    db.commit()
    return jsonify({'ok': True})
