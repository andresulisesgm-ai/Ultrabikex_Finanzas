from flask import Blueprint, jsonify, request
from datetime import datetime
from db import get_db
from auth import login_required

esf_bp = Blueprint('esf', __name__)


@esf_bp.route('/api/esf/totals', methods=['GET'])
@login_required
def esf_totals():
    """
    Retorna totales ESF del último quarter disponible para uso en dashboard widgets.
    Parámetros: year, unit (opcional).
    """
    from app import compute_esf
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')
    db   = get_db()

    result_quarters, quarters_available = compute_esf(db, year, unit)
    if not quarters_available:
        return jsonify({'error': 'Sin datos ESF'}), 404

    last_q = max(quarters_available)
    totales = result_quarters[last_q]['totales']

    return jsonify({
        'year': year,
        'unit': unit,
        'quarter': last_q,
        'totales': {
            'total_activos':        totales.get('TOTAL ACTIVOS', 0),
            'activos_corrientes':   totales.get('ACTIVOS CORRIENTES', 0),
            'activos_no_corrientes':totales.get('Total Activos No Corrientes', 0),
            'total_pasivos':        totales.get('TOTAL PASIVOS', 0),
            'pasivos_corrientes':   totales.get('TOTAL PASIVOS CORRIENTES', 0),
            'pasivos_no_corrientes':totales.get('TOTAL PASIVOS NO CORRIENTES', 0),
            'patrimonio':           totales.get('TOTAL PATRIMONIO', 0),
            'efectivo':             totales.get('Total Efectivo y Equivalentes', 0),
            'cuentas_por_cobrar':   totales.get('Total Cuentas por Cobrar (neto)', 0),
            'inventarios':          totales.get('Total Inventarios', 0),
            'cuentas_por_pagar':    totales.get('Total Cuentas por Pagar', 0),
        }
    })


@esf_bp.route('/api/esf', methods=['GET'])
def esf():
    """
    Estado de Situación Financiera por quarter.
    Parámetros: year, unit (opcional). Siempre retorna los 4 quarters;
    el filtro por quarter se aplica en el frontend.
    """
    from app import compute_esf
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')
    db   = get_db()

    result_quarters, quarters_available = compute_esf(db, year, unit)

    def var(q_a, q_b, key):
        a = result_quarters[q_a]['totales'].get(key, 0)
        b = result_quarters[q_b]['totales'].get(key, 0)
        if a == 0: return None
        return round((b - a) / abs(a) * 100, 1)

    variaciones = {}
    for key in ['TOTAL ACTIVOS', 'TOTAL PASIVOS', 'TOTAL PATRIMONIO', 'TOTAL PASIVOS Y PATRIMONIO']:
        variaciones[key] = {
            'Q1_Q2': var(1, 2, key),
            'Q2_Q3': var(2, 3, key),
            'Q3_Q4': var(3, 4, key),
        }

    return jsonify({
        'year': year, 'unit': unit,
        'quarters': result_quarters,
        'quarters_available': quarters_available,
        'variaciones': variaciones,
    })


@esf_bp.route('/api/esf/completo', methods=['GET'])
def esf_completo():
    """
    Estado de Situación Financiera completo con estructura jerárquica expandible de 3 niveles.
    Parámetros: year, unit (opcional).
    """
    from app import validate_esf_integrity
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')
    empresa_id = request.args.get('empresa_id', type=int) or None
    from engine import esf_engine
    result = esf_engine(year, unit, empresa_id=empresa_id)
    try:
        db = get_db()
        validate_esf_integrity(year, unit, result, db, empresa_id=empresa_id)
    except Exception as e:
        import logging
        logging.getLogger('esf_integrity_guard').error(f"Error al ejecutar validacion de integridad ESF: {str(e)}")

    year_prev = str(int(year) - 1)
    result_prev = esf_engine(year_prev, unit, empresa_id=empresa_id)
    prev_by_partida = {}
    for r in result_prev.get('rows', []):
        prev_by_partida[r['partida']] = r.get('quarters', {}).get(4, 0.0)
    for row in result.get('rows', []):
        row['year_prev'] = prev_by_partida.get(row['partida'], 0.0)
    result['year_prev'] = year_prev

    return jsonify(result)
