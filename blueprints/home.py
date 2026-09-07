from flask import Blueprint, jsonify, request
from datetime import datetime
import calendar

from db import get_db
from auth import login_required

home_bp = Blueprint('home_bp', __name__)

EERR_HOME_PARTIDAS = [
    ('ingresos', 'Total Ingresos'),
    ('costo_ventas', 'Total Costo de Ventas'),
    ('utilidad_bruta', 'Utilidad Bruta'),
    ('gastos_operacionales', 'Total Gastos Operacionales'),
    ('ebitda', 'Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA)'),
    ('utilidad_neta', 'Utilidad Neta'),
]

ESF_HOME_PARTIDAS = [
    ('activo_corriente', 'ACTIVOS CORRIENTES'),
    ('activo_no_corriente', 'Total Activos No Corrientes'),
    ('total_activo', 'TOTAL ACTIVOS'),
    ('pasivo_corriente', 'TOTAL PASIVOS CORRIENTES'),
    ('pasivo_no_corriente', 'TOTAL PASIVOS NO CORRIENTES'),
    ('total_pasivo', 'TOTAL PASIVOS'),
    ('patrimonio', 'TOTAL PATRIMONIO'),
]

IND_HOME_PREFIJOS = [
    ('roe', 'ROE'),
    ('roa', 'ROA'),
    ('razon_corriente', 'Ratio Corriente'),
    ('periodo_cobro', 'Período de cobro'),
    ('rotacion_inventarios', 'Rotación de Inventarios'),
    ('margen_neto', 'Margen Neto'),
]


def _saludo_dinamico():
    ahora = datetime.now()
    if ahora.hour < 12:
        saludo = 'Buenos días'
    elif ahora.hour < 19:
        saludo = 'Buenas tardes'
    else:
        saludo = 'Buenas noches'

    ultimo_dia_mes = calendar.monthrange(ahora.year, ahora.month)[1]
    extra = ''
    if ahora.day <= 3:
        extra = ' · Feliz inicio de mes'
    elif ahora.day >= ultimo_dia_mes - 2:
        extra = ' · Feliz fin de mes'

    return saludo, extra


@home_bp.route('/api/home/resumen', methods=['GET'])
@login_required
def home_resumen():
    from engine import eerr_divisa_real_trimestres, compute_indicadores_v2_divisa_real, calcular_estados_reales, _reshape_esf_rows_to_quarters

    year = request.args.get('year', str(datetime.now().year))
    empresa_id = request.args.get('empresa_id', type=int)
    db = get_db()

    if empresa_id:
        rows_q = db.execute('SELECT DISTINCT quarter FROM esf_data WHERE year=? AND empresa_id=?', (year, empresa_id)).fetchall()
    else:
        rows_q = db.execute('SELECT DISTINCT quarter FROM esf_data WHERE year=?', (year,)).fetchall()
    quarters_disponibles = sorted(r['quarter'] for r in rows_q)
    if not quarters_disponibles:
        return jsonify({'error': 'Sin datos ESF para el año solicitado'}), 404
    ultimo_q = max(quarters_disponibles)

    eerr_result = eerr_divisa_real_trimestres(db, year, '', empresa_id=empresa_id)
    if 'error' in eerr_result:
        return jsonify(eerr_result), 400
    eerr_q = eerr_result['quarters'].get(ultimo_q, {})
    eerr_home = {clave: round(eerr_q.get(partida, 0) or 0, 2) for clave, partida in EERR_HOME_PARTIDAS}

    estados = calcular_estados_reales(year, '', empresa_id=empresa_id, db=db)
    if 'error' in estados:
        return jsonify(estados), 400
    result_quarters = _reshape_esf_rows_to_quarters(estados.get('esf_real', {}))
    esf_tot_q = result_quarters.get(ultimo_q, {}).get('totales', {})
    esf_home = {clave: round(esf_tot_q.get(partida, 0) or 0, 2) for clave, partida in ESF_HOME_PARTIDAS}

    ind_result = compute_indicadores_v2_divisa_real(db, year, empresa_id=empresa_id)
    if isinstance(ind_result, dict) and 'error' in ind_result:
        return jsonify(ind_result), 400
    indicadores = ind_result.get('indicadores') or []
    ind_home = {}
    for clave, prefijo in IND_HOME_PREFIJOS:
        fila = next((i for i in indicadores if i.get('nombre', '').startswith(prefijo)), None)
        ind_home[clave] = fila.get('anio_actual') if fila else None

    saludo, extra = _saludo_dinamico()

    return jsonify({'year': year, 'quarter': ultimo_q, 'saludo': saludo, 'extra_saludo': extra, 'eerr': eerr_home, 'esf': esf_home, 'indicadores': ind_home})
