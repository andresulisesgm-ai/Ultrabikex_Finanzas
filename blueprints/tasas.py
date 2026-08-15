from flask import Blueprint, jsonify, request
from db import get_db
from auth import admin_required

tasas_bp = Blueprint('tasas', __name__)


@tasas_bp.route('/api/tasas', methods=['GET'])
def get_tasas():
    """Retorna todas las tasas por período o una específica si se pasa year/month."""
    year  = request.args.get('year')
    month = request.args.get('month')
    db    = get_db()

    if year and month:
        row = db.execute(
            'SELECT * FROM tasas_periodo WHERE year=? AND month=?',
            (year, month)
        ).fetchone()
        if not row:
            return jsonify({'error': 'No hay tasas configuradas para este período'}), 404
        return jsonify(dict(row))
    else:
        rows = db.execute('''
            SELECT * FROM tasas_periodo
            ORDER BY year DESC,
            CASE month
                WHEN 'ENE' THEN 1 WHEN 'FEB' THEN 2 WHEN 'MAR' THEN 3 WHEN 'ABR' THEN 4
                WHEN 'MAY' THEN 5 WHEN 'JUN' THEN 6 WHEN 'JUL' THEN 7 WHEN 'AGO' THEN 8
                WHEN 'SEPT' THEN 9 WHEN 'OCT' THEN 10 WHEN 'NOV' THEN 11 WHEN 'DIC' THEN 12
            END DESC
        ''').fetchall()
        return jsonify([dict(r) for r in rows])


@tasas_bp.route('/api/tasas', methods=['POST'])
@admin_required
def save_tasas():
    """
    Guarda o actualiza tasas para un período.
    Body: {year, month, tasa_bcv_inicio, tasa_bcv_fin, tasa_paralela_inicio, tasa_paralela_fin}
    Calcula promedios y factor_diferencial automáticamente.
    """
    data = request.get_json()
    year   = data.get('year')
    month  = data.get('month')
    bcv_ini    = data.get('tasa_bcv_inicio')
    bcv_fin    = data.get('tasa_bcv_fin')
    par_ini    = data.get('tasa_paralela_inicio')
    par_fin    = data.get('tasa_paralela_fin')

    if not all([year, month, bcv_ini is not None, bcv_fin is not None, par_ini is not None, par_fin is not None]):
        return jsonify({'error': 'Faltan parámetros requeridos'}), 400

    if bcv_ini <= 0 or bcv_fin <= 0:
        return jsonify({'error': 'Tasas BCV deben ser mayores a cero'}), 400

    # Calcular promedios
    bcv_prom = (bcv_ini + bcv_fin) / 2
    par_prom = (par_ini + par_fin) / 2
    diferencial = par_prom / bcv_prom

    db = get_db()
    db.execute('''
        INSERT INTO tasas_periodo (year, month, tasa_bcv_inicio, tasa_bcv_fin, tasa_bcv_promedio,
                                   tasa_paralela_inicio, tasa_paralela_fin, tasa_paralela_promedio,
                                   factor_diferencial)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(year, month) DO UPDATE SET
            tasa_bcv_inicio = excluded.tasa_bcv_inicio,
            tasa_bcv_fin = excluded.tasa_bcv_fin,
            tasa_bcv_promedio = excluded.tasa_bcv_promedio,
            tasa_paralela_inicio = excluded.tasa_paralela_inicio,
            tasa_paralela_fin = excluded.tasa_paralela_fin,
            tasa_paralela_promedio = excluded.tasa_paralela_promedio,
            factor_diferencial = excluded.factor_diferencial
    ''', (year, month, bcv_ini, bcv_fin, bcv_prom, par_ini, par_fin, par_prom, diferencial))
    db.commit()

    return jsonify({
        'ok': True,
        'year': year,
        'month': month,
        'tasa_bcv_promedio': round(bcv_prom, 4),
        'tasa_paralela_promedio': round(par_prom, 4),
        'factor_diferencial': round(diferencial, 4)
    })


@tasas_bp.route('/api/tasas/<int:tasa_id>', methods=['DELETE'])
@admin_required
def delete_tasa(tasa_id):
    db = get_db()
    db.execute('DELETE FROM tasas_periodo WHERE id = ?', (tasa_id,))
    db.commit()
    return jsonify({'ok': True})
