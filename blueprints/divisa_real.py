from flask import Blueprint, jsonify, request
from datetime import datetime
from db import get_db
from auth import login_required
from helpers import get_clasificacion

divisa_real_bp = Blueprint('divisa_real', __name__)


@divisa_real_bp.route('/api/esf-divisa-real', methods=['GET'])
def get_esf_divisa_real():
    year = request.args.get('year')
    quarter = request.args.get('quarter', type=int)
    empresa_id = request.args.get('empresa_id', type=int)
    if not year or not quarter:
        return jsonify({'error': 'year y quarter son requeridos'}), 400
    from engine import calcular_esf_divisa_real, calcular_estados_reales, esf_engine

    db = get_db()
    result = calcular_esf_divisa_real(year, quarter, empresa_id=empresa_id, db=db)
    if 'error' in result:
        return jsonify(result), 404

    # Metodología EERR Real / ESF Real (ago-2026): esf_completo ya no llama a esf_engine
    # directo con aplicar_divisa_real=True (eso mandaba la diferencia a Resultados
    # Acumulados, comportamiento incorrecto para el real) -- ahora usa el orquestador,
    # que mantiene Acumulados fijo (=BCV) y manda la diferencia como plug al EERR Real.
    estados = calcular_estados_reales(year, '', empresa_id=empresa_id, db=db)
    esf_completo = estados['esf_real']

    year_prev = str(int(year) - 1)
    result_prev = esf_engine(year_prev, '', empresa_id=empresa_id, db=db)
    prev_by_partida = {}
    for r in result_prev.get('rows', []):
        prev_by_partida[r['partida']] = r.get('quarters', {}).get(4, 0.0)
    for row in esf_completo.get('rows', []):
        row['year_prev'] = prev_by_partida.get(row['partida'], 0.0)
    esf_completo['year_prev'] = year_prev

    result['esf_completo'] = esf_completo
    return jsonify(result)


@divisa_real_bp.route('/api/esf-divisa-real/detalle-cuentas', methods=['GET'])
def get_esf_divisa_real_detalle_cuentas():
    year = request.args.get('year')
    quarter = request.args.get('quarter', type=int)
    empresa_id = request.args.get('empresa_id', type=int)
    if not year or not quarter:
        return jsonify({'error': 'year y quarter son requeridos'}), 400
    from engine import PARTIDAS_ESF_DIVISA_REAL, QUARTER_MONTH_CIERRE
    month = QUARTER_MONTH_CIERRE.get(quarter)
    if not month:
        return jsonify({'error': f'Quarter inválido: {quarter}'}), 400
    db = get_db()

    tasa_row = db.execute(
        'SELECT tasa_bcv_fin, tasa_paralela_fin FROM tasas_periodo WHERE year=? AND month=?',
        (year, month)
    ).fetchone()
    if not tasa_row or not tasa_row['tasa_bcv_fin'] or not tasa_row['tasa_paralela_fin']:
        return jsonify({'error': f'No hay tasa BCV/paralela fin de mes configurada para {month} {year}'}), 404
    ratio = tasa_row['tasa_bcv_fin'] / tasa_row['tasa_paralela_fin']

    placeholders = ','.join('?' * len(PARTIDAS_ESF_DIVISA_REAL))
    empresa_clause = ' AND fd.empresa_id = ?' if empresa_id is not None else ''
    empresa_params = (empresa_id,) if empresa_id is not None else ()
    rows = db.execute(f'''
        SELECT mg.group_name, fd.odoo_code, fd.odoo_name, fd.amount_sign as valor_real
        FROM financials_detail fd
        JOIN mapping_groups_v2 mg ON fd.odoo_code = mg.odoo_code AND mg.report_type='esf'
        WHERE fd.year=? AND fd.report_type='esf' AND fd.month=?
          AND mg.group_name IN ({placeholders}){empresa_clause}
    ''', (year, month, *PARTIDAS_ESF_DIVISA_REAL, *empresa_params)).fetchall()
    partidas = {p: [] for p in PARTIDAS_ESF_DIVISA_REAL}
    for r in rows:
        partidas[r['group_name']].append({
            'odoo_code': r['odoo_code'],
            'odoo_name': r['odoo_name'],
            'valor_real': round(r['valor_real'] * ratio, 2)
        })
    return jsonify({'year': year, 'quarter': quarter, 'partidas': partidas})


@divisa_real_bp.route('/api/dashboard_divisa_real', methods=['GET'])
def dashboard_divisa_real():
    """
    Dashboard con montos ajustados por factores de divisa real.
    Reutiliza el motor central _calcular_eerr_divisa_real (mismo usado por
    /api/eerr/divisa_real) para evitar calculo paralelo y garantizar
    consistencia de cifras entre el Dashboard y la pagina EERR Divisa Real.
    Parametros: year, month, unit (opcional)
    """
    year  = request.args.get('year', str(datetime.now().year))
    month = request.args.get('month')
    unit  = request.args.get('unit', 'TODAS')
    empresa_id = request.args.get('empresa_id', type=int)
    db    = get_db()

    if not month:
        return jsonify({'error': 'Se requiere mes especifico para divisa real'}), 400

    tasas_row = db.execute(
        'SELECT tasa_bcv_promedio, tasa_paralela_promedio FROM tasas_periodo WHERE year=? AND month=?',
        (year, month)
    ).fetchone()

    if not tasas_row:
        return jsonify({'error': f'No hay tasas configuradas para {month} {year}'}), 404

    bcv = tasas_row['tasa_bcv_promedio']
    paralela = tasas_row['tasa_paralela_promedio']

    if bcv is None or bcv <= 0:
        return jsonify({'error': f"Tasa BCV promedio invalida o cero para el mes {month} {year}"}), 400
    if paralela is None or paralela <= 0:
        return jsonify({'error': f"Tasa paralela promedio invalida o cero para el mes {month} {year}"}), 400

    diferencial = paralela / bcv

    from engine import calcular_estados_reales
    eerr_unit_param = '' if unit == 'TODAS' else unit
    estados_real = calcular_estados_reales(year, eerr_unit_param, empresa_id=empresa_id, db=db)
    if 'error' in estados_real:
        return jsonify(estados_real), 400
    eerr_data = estados_real['eerr_real']

    def get_mes_valor(partida_name):
        row = next((r for r in eerr_data['rows'] if r['partida'] == partida_name), None)
        if not row:
            return 0.0
        mes_data = next((m for m in row['meses'] if m['month'] == month), None)
        return mes_data['ejecutado']['valor'] if mes_data else 0.0

    ing_real = get_mes_valor('Total Ingresos')
    cos_real = get_mes_valor('Total Costo de Ventas')
    gas_real = get_mes_valor('Total Gastos Operacionales y No Operacionales')
    ub_real  = get_mes_valor('Utilidad Bruta')
    un_real  = get_mes_valor('Utilidad Neta')
    ebitda_real = get_mes_valor('Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA)')
    otros_ing_real = get_mes_valor('Otros Ingresos no Operacionales')
    otros_gas_real = get_mes_valor('Otros Gastos no Operacionales')
    seg_mercancia_real = get_mes_valor('Subtotal Ingresos por Venta de Mercancia')
    seg_servicios_real = get_mes_valor('Subtotal Ingresos por Servicios')
    seg_eventos_real = get_mes_valor('Subtotal Ingresos por Eventos')
    seg_taller_real = get_mes_valor('Subtotal Ingresos por Taller')

    return jsonify({
        'year': year,
        'month': month,
        'unit': unit,
        'tasas': {
            'bcv': bcv,
            'paralela': paralela,
            'diferencial': diferencial
        },
        'divisa_real': {
            'ingresos': round(ing_real, 2),
            'costos': round(cos_real, 2),
            'gastos': round(gas_real, 2),
            'utilidad_bruta': round(ub_real, 2),
            'utilidad_neta': round(un_real, 2),
            'ebitda': round(ebitda_real, 2),
            'otros_ingresos_no_operacionales': round(otros_ing_real, 2),
            'otros_gastos_no_operacionales': round(otros_gas_real, 2),
            'ingresos_segmentos': {
                'Venta de Mercancía': round(seg_mercancia_real, 2),
                'Servicios': round(seg_servicios_real, 2),
                'Eventos': round(seg_eventos_real, 2),
                'Taller': round(seg_taller_real, 2)
            }
        }
    })


@divisa_real_bp.route('/api/eerr/divisa_real', methods=['GET'])
@login_required
def eerr_divisa_real():
    from engine import calcular_estados_reales
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')
    empresa_id = request.args.get('empresa_id', type=int)
    db = get_db()
    estados = calcular_estados_reales(year, unit, empresa_id=empresa_id, db=db)
    if 'error' in estados:
        return jsonify(estados), 400
    return jsonify(estados['eerr_real'])


@divisa_real_bp.route('/api/eerr/divisa_real/trimestres', methods=['GET'])
@login_required
def eerr_divisa_real_trimestres_route():
    from engine import eerr_divisa_real_trimestres
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')
    empresa_id = request.args.get('empresa_id', type=int)
    db = get_db()
    resultado = eerr_divisa_real_trimestres(db, year, unit, empresa_id=empresa_id)
    if 'error' in resultado:
        return jsonify(resultado), 400

    # Desglose por unidad (Divisa Real) -- mismo patron que BCV (blueprints/dashboard.py),
    # solo si la empresa activa tiene unidades propias. Reutiliza eerr_divisa_real_trimestres
    # por unidad, mismo motor que el consolidado -- sin calculo paralelo.
    por_unidad = []
    if empresa_id is not None:
        unidades_empresa = [r['nombre'] for r in db.execute(
            'SELECT nombre FROM unidades WHERE empresa_id=?', (empresa_id,)
        ).fetchall()]
        for u in unidades_empresa:
            res_u = eerr_divisa_real_trimestres(db, year, u, empresa_id=empresa_id)
            if 'error' not in res_u:
                por_unidad.append({'unit': u, 'quarters': res_u['quarters']})
    resultado['por_unidad'] = por_unidad

    return jsonify(resultado)


@divisa_real_bp.route('/api/divisa_real/ganancia_perdida', methods=['GET'])
def get_ganancia_perdida_divisa():
    """
    Retorna el valor sugerido (calculado por el motor, plug_divisa_q incremental del
    trimestre) y el valor override manual si existe, para que Yocelin confirme o
    corrija cuanto de la diferencia de tasa cambiaria va a Ganancia vs Perdida.
    Parametros: year, quarter, empresa_id (opcional).
    """
    year = request.args.get('year')
    quarter = request.args.get('quarter', type=int)
    empresa_id = request.args.get('empresa_id', type=int)
    if not year or not quarter:
        return jsonify({'error': 'year y quarter son requeridos'}), 400
    from engine import calcular_estados_reales
    db = get_db()
    estados = calcular_estados_reales(year, '', empresa_id=empresa_id)
    if 'error' in estados:
        return jsonify(estados), 400
    plug_q = estados.get('esf_real', {}).get('plug_divisa_q', {})
    valor_acum = plug_q.get(quarter, 0.0)
    valor_prev = plug_q.get(quarter - 1, 0.0) if quarter > 1 else 0.0
    sugerido = round(valor_acum - valor_prev, 2)
    row = db.execute(
        'SELECT ganancia, perdida FROM ganancia_perdida_divisa_override WHERE year=? AND quarter=? AND empresa_id IS ?',
        (year, quarter, empresa_id)
    ).fetchone()
    return jsonify({
        'year': year, 'quarter': quarter, 'empresa_id': empresa_id,
        'sugerido_ganancia': sugerido if sugerido > 0 else 0.0,
        'sugerido_perdida': abs(sugerido) if sugerido < 0 else 0.0,
        'override_ganancia': row['ganancia'] if row else None,
        'override_perdida': row['perdida'] if row else None,
    })


@divisa_real_bp.route('/api/divisa_real/ganancia_perdida', methods=['POST'])
def save_ganancia_perdida_divisa():
    """Guarda el ajuste manual de Yocelin para Ganancia/Perdida en tasa cambiaria."""
    data = request.get_json() or {}
    year = data.get('year')
    quarter = data.get('quarter')
    empresa_id = data.get('empresa_id')
    ganancia = data.get('ganancia', 0) or 0
    perdida = data.get('perdida', 0) or 0
    if not year or not quarter:
        return jsonify({'error': 'year y quarter son requeridos'}), 400
    db = get_db()
    db.execute('''
        INSERT INTO ganancia_perdida_divisa_override (year, quarter, empresa_id, ganancia, perdida, updated_at)
        VALUES (?, ?, ?, ?, ?, datetime('now','localtime'))
        ON CONFLICT(year, quarter, empresa_id) DO UPDATE SET
            ganancia=excluded.ganancia, perdida=excluded.perdida, updated_at=excluded.updated_at
    ''', (year, quarter, empresa_id, ganancia, perdida))
    db.commit()
    return jsonify({'ok': True, 'year': year, 'quarter': quarter, 'empresa_id': empresa_id, 'ganancia': ganancia, 'perdida': perdida})


@divisa_real_bp.route('/api/divisa_real/ganancia_perdida/undo', methods=['POST'])
def undo_ganancia_perdida_divisa():
    """Elimina el ajuste manual guardado, volviendo al valor sugerido por el sistema."""
    data = request.get_json() or {}
    year = data.get('year')
    quarter = data.get('quarter')
    empresa_id = data.get('empresa_id')
    if not year or not quarter:
        return jsonify({'error': 'year y quarter son requeridos'}), 400
    db = get_db()
    db.execute(
        'DELETE FROM ganancia_perdida_divisa_override WHERE year=? AND quarter=? AND empresa_id IS ?',
        (year, quarter, empresa_id)
    )
    db.commit()
    return jsonify({'ok': True})
