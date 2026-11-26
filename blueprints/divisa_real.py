from flask import Blueprint, jsonify, request, session
from datetime import datetime
from audit import registrar_auditoria
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

    # Desglose por unidad / por empresa (Divisa Real, mes puntual) -- mismo patron que
    # BCV (blueprints/dashboard.py, por_unidad/por_empresa) y que
    # /api/eerr/divisa_real/trimestres. Reutiliza calcular_estados_reales por unidad
    # o por empresa -- sin calculo paralelo.
    def _mes_valor_de(eerr, partida_name):
        row = next((r for r in eerr['rows'] if r['partida'] == partida_name), None)
        if not row:
            return 0.0
        mes_data = next((m for m in row['meses'] if m['month'] == month), None)
        return mes_data['ejecutado']['valor'] if mes_data else 0.0

    por_unidad = []
    if empresa_id is not None:
        unidades_empresa = [r['nombre'] for r in db.execute(
            'SELECT nombre FROM unidades WHERE empresa_id=?', (empresa_id,)
        ).fetchall()]
        for u in unidades_empresa:
            res_u = calcular_estados_reales(year, u, empresa_id=empresa_id, db=db)
            if 'error' in res_u:
                continue
            eerr_u = res_u['eerr_real']
            i_u = _mes_valor_de(eerr_u, 'Total Ingresos')
            c_u = _mes_valor_de(eerr_u, 'Total Costo de Ventas')
            g_u = _mes_valor_de(eerr_u, 'Total Gastos Operacionales y No Operacionales')
            ub_u = _mes_valor_de(eerr_u, 'Utilidad Bruta')
            un_u = _mes_valor_de(eerr_u, 'Utilidad Neta')
            if i_u or c_u or g_u:
                por_unidad.append({
                    'unit': u, 'ingresos': round(i_u, 2), 'costos': round(c_u, 2),
                    'gastos': round(g_u, 2), 'utilidad_bruta': round(ub_u, 2),
                    'utilidad_neta': round(un_u, 2)
                })

    por_empresa = []
    if empresa_id is None:
        empresas_reales = db.execute(
            "SELECT id, nombre_corto FROM empresas WHERE id != 1"
        ).fetchall()
        for emp in empresas_reales:
            res_e = calcular_estados_reales(year, '', empresa_id=emp['id'], db=db)
            if 'error' in res_e:
                continue
            eerr_e = res_e['eerr_real']
            un_e = _mes_valor_de(eerr_e, 'Utilidad Neta')
            ing_e = _mes_valor_de(eerr_e, 'Total Ingresos')
            if un_e or ing_e:
                por_empresa.append({'empresa': emp['nombre_corto'],
                                    'utilidad_neta': round(un_e, 2),
                                    'ingresos': round(ing_e, 2)})

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
        },
        'por_unidad': por_unidad,
        'por_empresa': por_empresa
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
    unidades = []
    distribucion = {}
    if empresa_id is not None:
        u_rows = db.execute(
            'SELECT nombre, recibe_plug_divisa FROM unidades WHERE empresa_id=? AND activo=1 ORDER BY id',
            (empresa_id,)
        ).fetchall()
        unidades = [{'nombre': r['nombre'], 'recibe_plug_divisa': bool(r['recibe_plug_divisa'])} for r in u_rows]
        d_rows = db.execute(
            'SELECT unit, porcentaje FROM ganancia_perdida_divisa_distribucion WHERE year=? AND quarter=? AND empresa_id=?',
            (year, quarter, empresa_id)
        ).fetchall()
        distribucion = {r['unit']: float(r['porcentaje'] or 0.0) for r in d_rows}
    return jsonify({
        'year': year, 'quarter': quarter, 'empresa_id': empresa_id,
        'sugerido_ganancia': sugerido if sugerido > 0 else 0.0,
        'sugerido_perdida': abs(sugerido) if sugerido < 0 else 0.0,
        'override_ganancia': row['ganancia'] if row else None,
        'override_perdida': row['perdida'] if row else None,
        'unidades': unidades,
        'distribucion': distribucion,
    })


@divisa_real_bp.route('/api/divisa_real/ganancia_perdida', methods=['POST'])
def save_ganancia_perdida_divisa():
    """Guarda el ajuste manual de Yocelin para Ganancia/Perdida en tasa cambiaria y su distribucion % por unidad."""
    data = request.get_json() or {}
    year = data.get('year')
    quarter = data.get('quarter')
    empresa_id = data.get('empresa_id')
    ganancia = float(data.get('ganancia', 0) or 0)
    perdida = float(data.get('perdida', 0) or 0)
    distribucion = data.get('distribucion')
    if not year or not quarter:
        return jsonify({'error': 'year y quarter son requeridos'}), 400

    dist_limpia = None
    if distribucion is not None and empresa_id is not None:
        if not isinstance(distribucion, dict):
            return jsonify({'error': 'distribucion debe ser un objeto {unidad: porcentaje}'}), 400
        dist_limpia = {}
        for u, pct in distribucion.items():
            try:
                v = float(pct or 0)
            except (TypeError, ValueError):
                return jsonify({'error': f'Porcentaje invalido para {u}'}), 400
            if v < 0 or v > 100:
                return jsonify({'error': f'Porcentaje fuera de rango (0-100) para {u}'}), 400
            dist_limpia[str(u)] = round(v, 4)
        total_pct = round(sum(dist_limpia.values()), 2)
        if (ganancia > 0 or perdida > 0) and abs(total_pct - 100.0) > 0.01:
            return jsonify({'error': f'La distribucion por unidad debe sumar 100% (actual: {total_pct:.2f}%)'}), 400

    db = get_db()
    db.execute('''
        INSERT INTO ganancia_perdida_divisa_override (year, quarter, empresa_id, ganancia, perdida, updated_at)
        VALUES (?, ?, ?, ?, ?, datetime('now','localtime'))
        ON CONFLICT(year, quarter, empresa_id) DO UPDATE SET
            ganancia=excluded.ganancia, perdida=excluded.perdida, updated_at=excluded.updated_at
    ''', (year, quarter, empresa_id, ganancia, perdida))

    if dist_limpia is not None and empresa_id is not None:
        db.execute(
            'DELETE FROM ganancia_perdida_divisa_distribucion WHERE year=? AND quarter=? AND empresa_id=?',
            (year, quarter, empresa_id)
        )
        for u, pct in dist_limpia.items():
            db.execute('''
                INSERT INTO ganancia_perdida_divisa_distribucion (year, quarter, empresa_id, unit, porcentaje, updated_at)
                VALUES (?, ?, ?, ?, ?, datetime('now','localtime'))
            ''', (year, quarter, empresa_id, u, pct))

    db.commit()
    registrar_auditoria(
        db,
        session.get('username', 'sistema'),
        'divisa_real',
        'guardar_override',
        f'year={year}, quarter={quarter}, empresa_id={empresa_id}, ganancia={ganancia}, perdida={perdida}, distribucion={dist_limpia}',
    )
    return jsonify({
        'ok': True, 'year': year, 'quarter': quarter, 'empresa_id': empresa_id,
        'ganancia': ganancia, 'perdida': perdida, 'distribucion': dist_limpia,
    })


@divisa_real_bp.route('/api/divisa_real/ganancia_perdida/undo', methods=['POST'])
def undo_ganancia_perdida_divisa():
    """Elimina el ajuste manual guardado y su distribucion por unidad."""
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
    if empresa_id is not None:
        db.execute(
            'DELETE FROM ganancia_perdida_divisa_distribucion WHERE year=? AND quarter=? AND empresa_id=?',
            (year, quarter, empresa_id)
        )
    db.commit()
    registrar_auditoria(
        db,
        session.get('username', 'sistema'),
        'divisa_real',
        'deshacer_override',
        f'year={year}, quarter={quarter}, empresa_id={empresa_id}',
    )
    return jsonify({'ok': True})
