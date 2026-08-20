from flask import Blueprint, jsonify, request
from datetime import datetime
from db import get_db

indicadores_bp = Blueprint('indicadores', __name__)


@indicadores_bp.route('/api/indicadores', methods=['GET'])
def get_indicadores():
    """
    Retorna indicadores financieros avanzados (ROE, ROA, liquidez, rotación).
    Parámetros: year, unit (opcional), empresa_id (opcional).
    """
    from engine import compute_indicadores_v2
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')
    empresa_id = request.args.get('empresa_id', type=int) or None
    db   = get_db()

    indicadores = compute_indicadores_v2(db, year, empresa_id=empresa_id)
    if not indicadores:
        return jsonify({'error': 'Sin datos ESF para calcular indicadores'}), 404

    return jsonify({'year': year, 'unit': unit, 'empresa_id': empresa_id, 'indicadores': indicadores})


@indicadores_bp.route('/api/indicadores/divisa_real', methods=['GET'])
def get_indicadores_divisa_real():
    """
    Retorna indicadores financieros (ROE, ROA, liquidez, rotación) en modo Divisa
    Real. Mismo contrato de respuesta que /api/indicadores, distinta fuente de
    datos (calcular_estados_reales en vez de BCV) -- ver
    compute_indicadores_v2_divisa_real en engine.py.
    Parámetros: year, unit (opcional), empresa_id (opcional).
    """
    from engine import compute_indicadores_v2_divisa_real
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')
    empresa_id = request.args.get('empresa_id', type=int) or None
    db   = get_db()
    indicadores = compute_indicadores_v2_divisa_real(db, year, empresa_id=empresa_id)
    if isinstance(indicadores, dict) and 'error' in indicadores:
        return jsonify({'error': indicadores['error']}), 404
    if not indicadores:
        return jsonify({'error': 'Sin datos ESF para calcular indicadores en Divisa Real'}), 404
    return jsonify({'year': year, 'unit': unit, 'empresa_id': empresa_id, 'indicadores': indicadores})
