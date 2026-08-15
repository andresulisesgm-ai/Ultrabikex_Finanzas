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
    from app import compute_indicadores_v2
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')
    empresa_id = request.args.get('empresa_id', type=int) or None
    db   = get_db()

    indicadores = compute_indicadores_v2(db, year, empresa_id=empresa_id)
    if not indicadores:
        return jsonify({'error': 'Sin datos ESF para calcular indicadores'}), 404

    return jsonify({'year': year, 'unit': unit, 'empresa_id': empresa_id, 'indicadores': indicadores})
