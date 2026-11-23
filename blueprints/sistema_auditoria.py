from flask import Blueprint, jsonify, request
from auth import admin_required
from db import get_db

sistema_auditoria_bp = Blueprint('sistema_auditoria', __name__)


@sistema_auditoria_bp.route('/api/admin/audit_log', methods=['GET'])
@admin_required
def get_audit_log():
    """Consulta paginada y filtrada del registro de auditoría."""
    modulo = (request.args.get('modulo') or '').strip()
    usuario = (request.args.get('usuario') or '').strip()
    desde = (request.args.get('desde') or '').strip()
    hasta = (request.args.get('hasta') or '').strip()
    limit = request.args.get('limit', default=100, type=int) or 100
    offset = request.args.get('offset', default=0, type=int) or 0
    limit = max(1, min(limit, 500))
    offset = max(0, offset)

    where_clauses = []
    params = []
    if modulo:
        where_clauses.append('modulo = ?')
        params.append(modulo)
    if usuario:
        where_clauses.append('LOWER(usuario) LIKE LOWER(?)')
        params.append(f'%{usuario}%')
    if desde:
        where_clauses.append('fecha_hora >= ?')
        params.append(f'{desde} 00:00:00')
    if hasta:
        where_clauses.append('fecha_hora <= ?')
        params.append(f'{hasta} 23:59:59')

    where_sql = ('WHERE ' + ' AND '.join(where_clauses)) if where_clauses else ''

    db = get_db()
    total = db.execute(
        f'SELECT COUNT(*) FROM audit_log {where_sql}',
        params,
    ).fetchone()[0]

    rows = db.execute(
        f'SELECT id, fecha_hora, usuario, modulo, accion, detalle '
        f'FROM audit_log {where_sql} ORDER BY fecha_hora DESC, id DESC LIMIT ? OFFSET ?',
        params + [limit, offset],
    ).fetchall()

    modulos = [
        r[0] for r in db.execute(
            'SELECT DISTINCT modulo FROM audit_log ORDER BY modulo'
        ).fetchall()
    ]

    return jsonify({
        'items': [dict(r) for r in rows],
        'total': total,
        'modulos': modulos,
    })
