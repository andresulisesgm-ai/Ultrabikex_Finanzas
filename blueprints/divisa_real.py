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

    result = calcular_esf_divisa_real(year, quarter, empresa_id=empresa_id)
    if 'error' in result:
        return jsonify(result), 404

    # Metodología EERR Real / ESF Real (ago-2026): esf_completo ya no llama a esf_engine
    # directo con aplicar_divisa_real=True (eso mandaba la diferencia a Resultados
    # Acumulados, comportamiento incorrecto para el real) -- ahora usa el orquestador,
    # que mantiene Acumulados fijo (=BCV) y manda la diferencia como plug al EERR Real.
    estados = calcular_estados_reales(year, '', empresa_id=empresa_id)
    esf_completo = estados['esf_real']

    year_prev = str(int(year) - 1)
    result_prev = esf_engine(year_prev, '', empresa_id=empresa_id)
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
    estados_real = calcular_estados_reales(year, eerr_unit_param, empresa_id=empresa_id)
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
        }
    })


@divisa_real_bp.route('/api/divisa_real/resumen', methods=['GET'])
@login_required
def divisa_real_resumen():
    """
    Resumen de montos en Divisa Real para widgets del dashboard.
    Si se pasa month: calcula solo ese mes.
    Si no se pasa month: acumula todos los meses con tasas disponibles en el año.
    """
    year  = request.args.get('year', str(datetime.now().year))
    month = request.args.get('month')
    unit  = request.args.get('unit', 'TODAS')
    db    = get_db()

    uc = '' if unit in ('TODAS', '') else "AND unit=?"
    uc_params = [] if unit in ('TODAS', '') else [unit]

    # Obtener tasas disponibles
    if month:
        tasas_rows = db.execute(
            'SELECT month, tasa_bcv_promedio, tasa_paralela_promedio FROM tasas_periodo WHERE year=? AND month=?',
            (year, month)
        ).fetchall()
    else:
        tasas_rows = db.execute(
            'SELECT month, tasa_bcv_promedio, tasa_paralela_promedio FROM tasas_periodo WHERE year=? ORDER BY month',
            (year,)
        ).fetchall()

    if not tasas_rows:
        return jsonify({'error': 'Sin tasas disponibles para el período'}), 404

    tasas_by_month = {r['month']: {'bcv': r['tasa_bcv_promedio'], 'paralela': r['tasa_paralela_promedio']} for r in tasas_rows}
    meses_con_tasas = list(tasas_by_month.keys())

    # Mapping partida → (odoo_code, sign) (tomando el código más específico)
    mapping_rows = db.execute('SELECT partida, odoo_code, sign FROM mapping').fetchall()
    partida_to_mapping = {}
    for r in mapping_rows:
        p = r['partida']
        code = r['odoo_code']
        sign = r['sign']
        if p not in partida_to_mapping or len(code.split('.')) > len(partida_to_mapping[p][0].split('.')):
            partida_to_mapping[p] = (code, sign)

    ing_p, cos_p, gas_p = get_clasificacion(db)

    ing_total = cos_total = gas_total = 0.0
    ing_lit_total = cos_lit_total = gas_lit_total = 0.0
    paralela_sum = 0.0
    bcv_sum = 0.0

    for mes in meses_con_tasas:
        tasas = tasas_by_month[mes]
        bcv = tasas['bcv']
        paralela = tasas['paralela']
        if not bcv or bcv <= 0 or not paralela or paralela <= 0:
            continue
        diferencial = paralela / bcv
        paralela_sum += paralela
        bcv_sum += bcv

        metodos_rows = db.execute(
            'SELECT unit, odoo_code, pct_cash FROM metodo_pago_cuenta WHERE year=? AND month=?',
            (year, mes)
        ).fetchall()
        metodos_map = {(r['unit'], r['odoo_code']): r['pct_cash'] for r in metodos_rows}

        rows = db.execute(
            f'SELECT unit, partida, amount FROM financials WHERE year=? AND month=? {uc}',
            (year, mes) + tuple(uc_params)
        ).fetchall()

        data_ajustado = {}
        data_literal = {}
        for r in rows:
            partida = r['partida']
            amount = r['amount']
            mapping_info = partida_to_mapping.get(partida)
            odoo_code = mapping_info[0] if mapping_info else None
            pct_cash = metodos_map.get((r['unit'], odoo_code), 100.0) if odoo_code else 100.0
            pct_bcv = 100 - pct_cash
            ajustado = amount * (pct_cash / 100) + amount * (pct_bcv / 100) / diferencial
            data_ajustado[partida] = data_ajustado.get(partida, 0) + ajustado
            data_literal[partida] = data_literal.get(partida, 0) + amount

        def total(codes, d): return sum(d.get(p, 0) for p in codes)
        ing_total  += total(ing_p, data_ajustado)
        cos_total  += total(cos_p, data_ajustado)
        gas_total  += total(gas_p, data_ajustado)
        ing_lit_total += total(ing_p, data_literal)
        cos_lit_total += total(cos_p, data_literal)
        gas_lit_total += total(gas_p, data_literal)

    n = len(meses_con_tasas)
    tasa_paralela_prom = round(paralela_sum / n, 4) if n else None
    tasa_bcv_prom = round(bcv_sum / n, 4) if n else None

    return jsonify({
        'year': year,
        'unit': unit,
        'meses': meses_con_tasas,
        'tasa_paralela_promedio': tasa_paralela_prom,
        'tasa_bcv_promedio': tasa_bcv_prom,
        'divisa_real': {
            'ingresos':      round(ing_total, 2),
            'costos':        round(cos_total, 2),
            'gastos':        round(gas_total, 2),
            'utilidad_bruta': round(ing_total - cos_total, 2),
            'utilidad_neta': round(ing_total - cos_total - gas_total, 2),
        },
        'literal_bcv': {
            'ingresos':      round(ing_lit_total, 2),
            'costos':        round(cos_lit_total, 2),
            'gastos':        round(gas_lit_total, 2),
            'utilidad_bruta': round(ing_lit_total - cos_lit_total, 2),
            'utilidad_neta': round(ing_lit_total - cos_lit_total - gas_lit_total, 2),
        }
    })


@divisa_real_bp.route('/api/eerr/divisa_real', methods=['GET'])
@login_required
def eerr_divisa_real():
    from engine import calcular_estados_reales
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')
    empresa_id = request.args.get('empresa_id', type=int)
    estados = calcular_estados_reales(year, unit, empresa_id=empresa_id)
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
    return jsonify(resultado)
