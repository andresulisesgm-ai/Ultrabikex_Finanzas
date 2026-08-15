from flask import Blueprint, jsonify, request
from datetime import datetime
from db import get_db
from auth import admin_required

datos_bp = Blueprint('datos', __name__)


@datos_bp.route('/api/data', methods=['GET'])
def get_data():
    year        = request.args.get('year', str(datetime.now().year))
    unit        = request.args.get('unit', '')
    report_type = request.args.get('report_type', '')
    empresa_id  = request.args.get('empresa_id', type=int) or None
    db          = get_db()
    q      = 'SELECT * FROM financials_detail WHERE year=?'
    params = [year]
    if unit:        q += ' AND unit=?';        params.append(unit)
    if report_type: q += ' AND report_type=?'; params.append(report_type)
    if empresa_id:  q += ' AND empresa_id=?';  params.append(empresa_id)
    rows = db.execute(q + ' ORDER BY unit, month, odoo_code', params).fetchall()
    # Marcar filas que tienen historial de override
    result = []
    for r in rows:
        row = dict(r)
        log = db.execute(
            '''SELECT valor_anterior, valor_nuevo, timestamp
               FROM financials_override_log
               WHERE year=? AND month=? AND unit=? AND odoo_code=?
               ORDER BY id DESC LIMIT 1''',
            (row['year'], row['month'], row['unit'], row['odoo_code'])
        ).fetchone()
        row['has_override'] = log is not None
        row['override_last'] = dict(log) if log else None
        result.append(row)
    return jsonify(result)


@datos_bp.route('/api/data/override', methods=['POST'])
@admin_required
def data_override():
    body        = request.get_json()
    year        = body.get('year')
    month       = body.get('month')
    unit        = body.get('unit')
    odoo_code   = body.get('odoo_code')
    valor_nuevo = body.get('valor_nuevo')
    empresa_id  = body.get('empresa_id')
    if None in (year, month, unit, odoo_code, valor_nuevo):
        return jsonify({'error': 'Faltan campos obligatorios'}), 400
    db = get_db()
    # Leer valor actual
    row = db.execute(
        'SELECT amount_sign, report_type, partida FROM financials_detail WHERE year=? AND month=? AND unit=? AND odoo_code=? AND empresa_id IS ?',
        (year, month, unit, odoo_code, empresa_id)
    ).fetchone()
    if not row:
        return jsonify({'error': 'Registro no encontrado'}), 404
    valor_anterior = row['amount_sign']
    report_type    = row['report_type']
    partida        = row['partida']
    # Actualizar financials_detail
    db.execute(
        'UPDATE financials_detail SET amount_sign=? WHERE year=? AND month=? AND unit=? AND odoo_code=? AND empresa_id IS ?',
        (valor_nuevo, year, month, unit, odoo_code, empresa_id)
    )
    # Actualizar en cascada financials o esf_data
    if report_type == 'eerr':
        db.execute(
            '''UPDATE financials SET amount=(
                SELECT SUM(amount_sign) FROM financials_detail
                WHERE year=? AND month=? AND unit=? AND partida=? AND report_type='eerr'
               ) WHERE year=? AND month=? AND unit=? AND partida=?''',
            (year, month, unit, partida, year, month, unit, partida)
        )
    else:
        row_esf = db.execute(
            'SELECT quarter FROM financials_detail WHERE year=? AND month=? AND unit=? AND odoo_code=? AND empresa_id IS ?',
            (year, month, unit, odoo_code, empresa_id)
        ).fetchone()
        if row_esf:
            quarter = row_esf['quarter']
            db.execute(
                '''UPDATE esf_data SET amount=(
                    SELECT SUM(amount_sign) FROM financials_detail
                    WHERE year=? AND unit=? AND partida=? AND report_type='esf' AND quarter=? AND empresa_id IS ?
                   ) WHERE year=? AND quarter=? AND unit=? AND partida=? AND empresa_id IS ?''',
                (year, unit, partida, quarter, empresa_id, year, quarter, unit, partida, empresa_id)
            )
    # Guardar en log
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.execute(
        '''INSERT INTO financials_override_log (year, month, unit, odoo_code, report_type, valor_anterior, valor_nuevo, timestamp, empresa_id)
           VALUES (?,?,?,?,?,?,?,?,?)''',
        (year, month, unit, odoo_code, report_type, valor_anterior, valor_nuevo, ts, empresa_id)
    )
    db.commit()
    return jsonify({'ok': True, 'valor_anterior': valor_anterior, 'valor_nuevo': valor_nuevo})


@datos_bp.route('/api/data/override/undo', methods=['POST'])
@admin_required
def data_override_undo():
    body      = request.get_json()
    year      = body.get('year')
    month     = body.get('month')
    unit      = body.get('unit')
    odoo_code = body.get('odoo_code')
    empresa_id = body.get('empresa_id')
    if None in (year, month, unit, odoo_code):
        return jsonify({'error': 'Faltan campos obligatorios'}), 400
    db = get_db()
    # Último registro del log
    log = db.execute(
        '''SELECT id, valor_anterior, report_type, empresa_id FROM financials_override_log
           WHERE year=? AND month=? AND unit=? AND odoo_code=? AND empresa_id IS ?
           ORDER BY id DESC LIMIT 1''',
        (year, month, unit, odoo_code, empresa_id)
    ).fetchone()
    if not log:
        return jsonify({'error': 'No hay override que deshacer'}), 404
    valor_revertido = log['valor_anterior']
    report_type     = log['report_type']
    log_empresa_id  = log['empresa_id']
    # Leer partida
    row = db.execute(
        'SELECT partida, quarter FROM financials_detail WHERE year=? AND month=? AND unit=? AND odoo_code=? AND empresa_id IS ?',
        (year, month, unit, odoo_code, log_empresa_id)
    ).fetchone()
    partida = row['partida']
    quarter = row['quarter']
    # Revertir financials_detail
    db.execute(
        'UPDATE financials_detail SET amount_sign=? WHERE year=? AND month=? AND unit=? AND odoo_code=? AND empresa_id IS ?',
        (valor_revertido, year, month, unit, odoo_code, log_empresa_id)
    )
    # Revertir en cascada
    if report_type == 'eerr':
        db.execute(
            '''UPDATE financials SET amount=(
                SELECT SUM(amount_sign) FROM financials_detail
                WHERE year=? AND month=? AND unit=? AND partida=? AND report_type='eerr'
               ) WHERE year=? AND month=? AND unit=? AND partida=?''',
            (year, month, unit, partida, year, month, unit, partida)
        )
    else:
        db.execute(
            '''UPDATE esf_data SET amount=(
                SELECT SUM(amount_sign) FROM financials_detail
                WHERE year=? AND unit=? AND partida=? AND report_type='esf' AND quarter=? AND empresa_id IS ?
               ) WHERE year=? AND quarter=? AND unit=? AND partida=? AND empresa_id IS ?''',
            (year, unit, partida, quarter, log_empresa_id, year, quarter, unit, partida, log_empresa_id)
        )
    # Eliminar el log revertido
    db.execute('DELETE FROM financials_override_log WHERE id=?', (log['id'],))
    db.commit()
    return jsonify({'ok': True, 'valor_revertido': valor_revertido})
