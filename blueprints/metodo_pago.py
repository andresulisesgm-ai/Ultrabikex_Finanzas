from flask import Blueprint, jsonify, request
from db import get_db
from auth import admin_required

metodo_pago_bp = Blueprint('metodo_pago', __name__)


@metodo_pago_bp.route('/api/metodo_pago', methods=['GET'])
def get_metodo_pago():
    """Retorna métodos de pago para year/month dados, agrupados por odoo_code."""
    year  = request.args.get('year')
    month = request.args.get('month')

    if not year or not month:
        return jsonify({'error': 'Se requiere year y month'}), 400

    db   = get_db()
    rows = db.execute(
        'SELECT * FROM metodo_pago_cuenta WHERE year=? AND month=? ORDER BY odoo_code, unit',
        (year, month)
    ).fetchall()

    return jsonify([dict(r) for r in rows])


@metodo_pago_bp.route('/api/metodo_pago', methods=['POST'])
@admin_required
def save_metodo_pago():
    """
    Guarda % Cash/BCV para un período.
    Body: {year, month, metodos: [{unit, odoo_code, pct_cash}, ...]}
    """
    data = request.get_json()
    year    = data.get('year')
    month   = data.get('month')
    metodos = data.get('metodos', [])

    if not all([year, month]):
        return jsonify({'error': 'Faltan year/month'}), 400

    if not metodos:
        return jsonify({'error': 'No hay métodos de pago para guardar'}), 400

    db = get_db()

    # Borrar configuración anterior del período
    db.execute('DELETE FROM metodo_pago_cuenta WHERE year=? AND month=?', (year, month))

    # Insertar nueva configuración
    for m in metodos:
        unit     = m.get('unit')
        code     = m.get('odoo_code')
        pct_cash = m.get('pct_cash', 0)

        if not all([unit, code]) or pct_cash < 0 or pct_cash > 100:
            continue

        db.execute('''
            INSERT OR IGNORE INTO metodo_pago_cuenta (year, month, unit, odoo_code, pct_cash)
            VALUES (?, ?, ?, ?, ?)
        ''', (year, month, unit, code, pct_cash))

    db.commit()
    return jsonify({'ok': True, 'inserted': len(metodos)})


@metodo_pago_bp.route('/api/metodo_pago/copiar', methods=['POST'])
@admin_required
def copiar_metodo_pago():
    """
    Copia configuración de % Cash/BCV de un período anterior.
    Body: {from_year, from_month, to_year, to_month}
    """
    data = request.get_json()
    from_y = data.get('from_year')
    from_m = data.get('from_month')
    to_y   = data.get('to_year')
    to_m   = data.get('to_month')
    units  = data.get('units')  # lista de unidades; None = todas

    if not all([from_y, from_m, to_y, to_m]):
        return jsonify({'error': 'Faltan parámetros'}), 400

    db = get_db()

    # Leer configuración origen (filtrado por unidades si se especifica)
    if units:
        placeholders = ','.join('?' * len(units))
        rows = db.execute(
            'SELECT unit, odoo_code, pct_cash FROM metodo_pago_cuenta WHERE year=? AND month=? AND unit IN (' + placeholders + ')',
            [from_y, from_m] + list(units)
        ).fetchall()
    else:
        rows = db.execute(
            'SELECT unit, odoo_code, pct_cash FROM metodo_pago_cuenta WHERE year=? AND month=?',
            (from_y, from_m)
        ).fetchall()

    if not rows:
        return jsonify({'error': 'No hay configuración en el período origen'}), 404

    # Borrar destino solo para las unidades afectadas
    if units:
        placeholders = ','.join('?' * len(units))
        db.execute(
            'DELETE FROM metodo_pago_cuenta WHERE year=? AND month=? AND unit IN (' + placeholders + ')',
            [to_y, to_m] + list(units)
        )
    else:
        db.execute('DELETE FROM metodo_pago_cuenta WHERE year=? AND month=?', (to_y, to_m))

    # Insertar en destino
    for r in rows:
        db.execute('''
            INSERT INTO metodo_pago_cuenta (year, month, unit, odoo_code, pct_cash)
            VALUES (?, ?, ?, ?, ?)
        ''', (to_y, to_m, r['unit'], r['odoo_code'], r['pct_cash']))

    db.commit()
    return jsonify({'ok': True, 'copied': len(rows)})
