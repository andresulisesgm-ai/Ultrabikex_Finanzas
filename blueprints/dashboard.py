from flask import Blueprint, jsonify, request, session
import json
from datetime import datetime
from db import get_db
from auth import login_required
from constants import MONTHS, UNITS
from helpers import get_clasificacion

dashboard_bp = Blueprint('dashboard', __name__)

# Categorías de gasto: cada una agrupa partidas cuyo nombre contiene alguna palabra clave.
GASTO_CATS = {
    'Administración':   ['servicios públicos','telefonía','alquiler','condominio','outsorsing','oficina','limpieza','alimentos','honorarios','retenciones','mantenimiento','viáticos admin','seguro','impuesto','depreciación','deterioro','amortización','comisiones bancarias','IGTF','intereses'],
    'Rec. Humanos':     ['sueldos','salarios','horas extras','complemento de sueldos','bono de alimentación','vacaciones','utilidades','prestaciones','aporte patronal','guardería','HCM','salud','uniformes','fiestas','capacitación','transporte del personal'],
    'Comercialización': ['viáticos comerciales','fletes','almacenaje','importación','comisiones empleados','gasolina','garantías','suscripciones'],
    'Mercadeo':         ['redes sociales','medios publicitarios','impresiones','decoración','muestras','campañas'],
    'TI+I':             ['dominio','servidores','software tecnológico'],
    'No Operacionales': ['Faltante','Pérdida','Multas','deterioro de inventarios'],
}

# ── Dashboard Builder Config ──────────────────────────────────────────────────

DEFAULT_DASHBOARD_CONFIG = [
  {
    "id": "kc-ingr",
    "type": "kpi",
    "title": "Ingresos Totales",
    "subtitle": "Acumulado año",
    "tooltip": "Ingresos operativos acumulados en el año. No incluye ingresos no operativos (alquileres, intereses, ganancia cambiaria, etc.)",
    "icon": "💰",
    "colorClass": "cb",
    "visible": True,
    "order": 1,
    "widthSpan": 1,
    "dataset": "ingresos"
  },
  {
    "id": "kc-ub",
    "type": "kpi",
    "title": "Utilidad Bruta",
    "subtitle": "",
    "tooltip": "Ingresos Totales menos Costo de Ventas.",
    "icon": "📈",
    "colorClass": "cg",
    "visible": True,
    "order": 2,
    "widthSpan": 1,
    "dataset": "utilidad_bruta"
  },
  {
    "id": "kc-un",
    "type": "kpi",
    "title": "Utilidad Neta",
    "subtitle": "",
    "tooltip": "Resultado final después de todos los gastos operativos y no operativos.",
    "icon": "🏆",
    "colorClass": "ca",
    "visible": True,
    "order": 3,
    "widthSpan": 1,
    "dataset": "utilidad_neta"
  },
  {
    "id": "kc-mn",
    "type": "kpi",
    "title": "Margen Neto %",
    "subtitle": "Ref ≥5%",
    "tooltip": "Utilidad Neta como porcentaje de los Ingresos Totales.",
    "icon": "%",
    "colorClass": "ct",
    "visible": True,
    "order": 4,
    "widthSpan": 1,
    "dataset": "margen_neto"
  },
  {
    "id": "kc-ebt",
    "type": "kpi",
    "title": "EBITDA",
    "subtitle": "Acumulado año",
    "tooltip": "Utilidad antes de intereses, impuestos, depreciación y amortización.",
    "icon": "⭐",
    "colorClass": "ca",
    "visible": True,
    "order": 5,
    "widthSpan": 1,
    "dataset": "ebitda"
  },
  {
    "id": "kc-act",
    "type": "kpi",
    "title": "Total Activos",
    "subtitle": "Consolidado · último trimestre",
    "tooltip": "Todo lo que posee la empresa. Consolidado, al cierre del último trimestre cargado. No se suma entre trimestres -- es una foto a un momento dado.",
    "icon": "🏦",
    "colorClass": "cb",
    "visible": True,
    "order": 6,
    "widthSpan": 1,
    "dataset": "total_activos"
  },
  {
    "id": "kc-pas",
    "type": "kpi",
    "title": "Total Pasivos",
    "subtitle": "Consolidado · último trimestre",
    "tooltip": "Deudas y obligaciones totales de la empresa. Consolidado, al cierre del último trimestre cargado.",
    "icon": "📋",
    "colorClass": "cr",
    "visible": True,
    "order": 7,
    "widthSpan": 1,
    "dataset": "total_pasivos"
  },
  {
    "id": "kc-pat",
    "type": "kpi",
    "title": "Patrimonio",
    "subtitle": "Consolidado · último trimestre",
    "tooltip": "Lo que le pertenece a los socios: Activos menos Pasivos.",
    "icon": "💎",
    "colorClass": "cg",
    "visible": True,
    "order": 8,
    "widthSpan": 1,
    "dataset": "patrimonio"
  },
  {
    "id": "kc-rzc",
    "type": "kpi",
    "title": "Razón Corriente",
    "subtitle": "Ref 1.5 - 2",
    "tooltip": "Activo Corriente entre Pasivo Corriente. Mide la capacidad de pago a corto plazo.",
    "icon": "⚖️",
    "colorClass": "cp",
    "visible": True,
    "order": 9,
    "widthSpan": 1,
    "dataset": "razon_corriente"
  },
  {
    "id": "wc-estcap",
    "type": "chart",
    "title": "Estructura de Capital",
    "subtitle": "Activo vs Pasivo + Patrimonio, por trimestre",
    "visible": True,
    "order": 10,
    "size": "m",
    "widthSpan": 2,
    "chartType": "bar",
    "dataset": "estructura_capital"
  },
  {
    "id": "wc-estcapdet",
    "type": "chart",
    "title": "Estructura de Capital Detallada",
    "subtitle": "Activo y Pasivo por partida, por trimestre",
    "visible": True,
    "order": 11,
    "size": "l",
    "chartType": "bar",
    "dataset": "estructura_capital_detallada"
  }
]


@dashboard_bp.route('/api/dashboard', methods=['GET'])
def dashboard():
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', 'TODAS')
    empresa_id = request.args.get('empresa_id', type=int) or None
    db   = get_db()
    ing_p, cos_p, gas_p = get_clasificacion(db)

    # 1. Obtener los datos del EERR
    eerr_unit_param = '' if unit == 'TODAS' else unit
    from engine import eerr_completo_v2_ui_adapter
    eerr_data = eerr_completo_v2_ui_adapter(db, year, eerr_unit_param, empresa_id=empresa_id)

    # Función auxiliar para extraer datos del EERR
    def get_eerr_values(partida_name):
        row = next((r for r in eerr_data['rows'] if r['partida'] == partida_name), None)
        if not row:
            return {m: 0.0 for m in MONTHS}, 0.0
        
        monthly_vals = {}
        total_anual = 0.0
        for m_data in row['meses']:
            m_name = m_data['month']
            val = m_data['ejecutado']['valor']
            monthly_vals[m_name] = val
            total_anual += val
            
        return monthly_vals, round(total_anual, 2)

    # Extracción directa de los nodos del EERR
    ingresos_mes, tI = get_eerr_values('Total Ingresos')
    costos_mes, tC   = get_eerr_values('Total Costo de Ventas')
    ub_mes, ub       = get_eerr_values('Utilidad Bruta')
    gastos_mes, tG   = get_eerr_values('Total Gastos Operacionales y No Operacionales')
    ebt_mes, ebt     = get_eerr_values('Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA)')
    un_mes, un       = get_eerr_values('Utilidad Neta')

    # 2. Desglose por unidad (por_unidad) — solo si la empresa activa tiene unidades propias.
    # Holding (empresa_id=None) no tiene desglose por unidad: es agregado de 4 empresas, no de unidades.
    por_unidad = []
    unidades_empresa = []
    if empresa_id is not None:
        unidades_empresa = [r['nombre'] for r in db.execute(
            'SELECT nombre FROM unidades WHERE empresa_id=?', (empresa_id,)
        ).fetchall()]
    for u in unidades_empresa:
        eerr_u = eerr_completo_v2_ui_adapter(db, year, u, empresa_id=empresa_id)
        
        def get_u_total(p_name):
            r = next((row for row in eerr_u['rows'] if row['partida'] == p_name), None)
            return sum(m['ejecutado']['valor'] for m in r['meses']) if r else 0.0

        i_u = get_u_total('Total Ingresos')
        c_u = get_u_total('Total Costo de Ventas')
        g_u = get_u_total('Total Gastos Operacionales y No Operacionales')
        ub_u = get_u_total('Utilidad Bruta')
        un_u = get_u_total('Utilidad Neta')

        mb_u = round(ub_u / i_u * 100, 1) if i_u else 0
        mn_u = round(un_u / i_u * 100, 1) if i_u else 0
        rc_u = round(c_u / i_u * 100, 1) if i_u else 0
        rg_u = round(g_u / i_u * 100, 1) if i_u else 0

        if i_u or c_u or g_u:
            por_unidad.append({
                'unit': u, 'ingresos': round(i_u, 2), 'costos': round(c_u, 2), 'gastos': round(g_u, 2),
                'utilidad_bruta': round(ub_u, 2), 'utilidad_neta': round(un_u, 2),
                'margen_bruto': mb_u, 'margen_neto': mn_u, 'ratio_costo': rc_u, 'ratio_gasto': rg_u
            })

    # 3. Top 10 Gastos desglosados
    gas_rows = []
    for r in eerr_data['rows']:
        if not r['is_header'] and r['partida'] in gas_p:
            val_anual = sum(m['ejecutado']['valor'] for m in r['meses'])
            if val_anual > 0:
                gas_rows.append({
                    'partida': r['partida'],
                    'total': round(val_anual, 2),
                    't': round(val_anual, 2)
                })
    top_gastos = sorted(gas_rows, key=lambda x: x['total'], reverse=True)[:10]

    # Compatibilidad de EBITDA: asegurar que depreciación esté en top_gastos para que la fórmula simplificada de JS (un + depr) cuadre exactamente
    depr_row = next((r for r in eerr_data['rows'] if r['partida'] == 'Depreciaciones, deterioro y Amortización'), None)
    depr_val = sum(m['ejecutado']['valor'] for m in depr_row['meses']) if depr_row else 0.0
    
    depr_in_top = any(g['partida'] == 'Depreciaciones, deterioro y Amortización' for g in top_gastos)
    if not depr_in_top and depr_val > 0:
        top_gastos.append({
            'partida': 'Depreciaciones, deterioro y Amortización',
            'total': round(depr_val, 2),
            't': round(depr_val, 2)
        })

    # 4. Distribución por categorías (cat_gastos)
    subtotal_mapping = {
        'Subtotal Gastos de Administración': 'Administración',
        'Subtotal Gastos de Recursos Humanos': 'Rec. Humanos',
        'Subtotal Gastos de Comercialización y Logistica': 'Comercialización',
        'Subtotal Gastos de Mercadeo': 'Mercadeo',
        'Gastos de TI+I': 'TI+I',
        'Otros Gastos no Operacionales': 'No Operacionales'
    }
    
    cat_gastos = []
    for subtotal_name, cat_name in subtotal_mapping.items():
        _, val_anual = get_eerr_values(subtotal_name)
        if val_anual > 0:
            cat_gastos.append({
                'categoria': cat_name,
                'total': val_anual
            })

    # 5. Datos Mensuales (months_data)
    months_data = []
    for m in MONTHS:
        i = ingresos_mes.get(m, 0.0)
        c = costos_mes.get(m, 0.0)
        g = gastos_mes.get(m, 0.0)
        u_b = ub_mes.get(m, 0.0)
        u_n = un_mes.get(m, 0.0)
        
        months_data.append({
            'month': m, 'ingresos': round(i, 2), 'costos': round(c, 2), 'gastos': round(g, 2),
            'utilidad_bruta': round(u_b, 2), 'utilidad_neta': round(u_n, 2),
            'margen_bruto': round(u_b / i * 100, 1) if i else 0,
            'margen_neto': round(u_n / i * 100, 1) if i else 0,
            'ratio_costo': round(c / i * 100, 1) if i else 0,
            'ratio_gasto': round(g / i * 100, 1) if i else 0
        })

    # 6. Punto de Equilibrio (pe) usando los totales consolidados
    pe = None
    if unit != 'TODAS' and tI > 0:
        mc = 1 - tC / tI
        if mc > 0:
            pev = tG / mc
            pe = {
                'pe_ingresos': round(pev, 2),
                'ingresos_actuales': round(tI, 2),
                'cobertura_pct': round(tI / pev * 100, 1) if pev else 0,
                'margen_contribucion_pct': round(mc * 100, 1)
            }

    # 7. Meses cargados
    loaded = []
    if empresa_id is not None:
        unidades_rows = db.execute('SELECT nombre FROM unidades WHERE empresa_id=?', [empresa_id]).fetchall()
        unidades_list = [r['nombre'] for r in unidades_rows]
        if unidades_list:
            placeholders = ','.join(['?'] * len(unidades_list))
            loaded = db.execute(
                f'SELECT DISTINCT unit, month FROM financials WHERE year=? AND unit IN ({placeholders}) ORDER BY unit, month',
                [year] + unidades_list
            ).fetchall()

    # 8. Indicadores Avanzados: usar compute_indicadores_v2 (formulas corregidas de
    # ROE/ROA/Periodo de Cobro, ver ultrax_logs.md), nunca compute_indicadores (v1),
    # que queda obsoleta. ESF y sus indicadores van SIEMPRE consolidados, nunca
    # filtrados por unit -- regla de negocio: el ESF no existe por unidad de negocio.
    from engine import compute_indicadores_v2, compute_esf
    indicadores_avanzados = compute_indicadores_v2(db, year, empresa_id=empresa_id)

    razon_corriente = None
    ind_rc = next((i for i in indicadores_avanzados if i['nombre'].startswith('Ratio Corriente')), None)
    if ind_rc:
        razon_corriente = ind_rc['anio_actual']

    esf_quarters, esf_q_avail = compute_esf(db, year, '', empresa_id=empresa_id)
    total_activos = total_pasivos = patrimonio = None
    if esf_q_avail:
        esf_last_q = max(esf_q_avail)
        esf_tot = esf_quarters[esf_last_q]['totales']
        total_activos = round(esf_tot.get('TOTAL ACTIVOS', 0), 2)
        total_pasivos = round(esf_tot.get('TOTAL PASIVOS', 0), 2)
        patrimonio    = round(esf_tot.get('TOTAL PATRIMONIO', 0), 2)

    totals = {
        'ingresos': round(tI, 2),
        'costos': round(tC, 2),
        'utilidad_bruta': round(ub, 2),
        'gastos': round(tG, 2),
        'ebitda': round(ebt, 2),
        'utilidad_neta': round(un, 2),
        'total_activos': total_activos,
        'total_pasivos': total_pasivos,
        'patrimonio': patrimonio,
        'razon_corriente': razon_corriente
    }

    return jsonify({
        'months': months_data, 'por_unidad': por_unidad, 'top_gastos': top_gastos,
        'cat_gastos': cat_gastos, 'loaded': [{'unit': r['unit'], 'month': r['month']} for r in loaded],
        'totals': totals,
        'indicadores_avanzados': indicadores_avanzados,
        'punto_equilibrio': pe
    })


@dashboard_bp.route('/api/dashboard/config', methods=['GET'])
@login_required
def get_dashboard_config():
    username = session.get('username')
    db = get_db()
    row = db.execute('SELECT config_json FROM dashboard_config WHERE username = ?', [username]).fetchone()
    if row:
        return jsonify(json.loads(row['config_json']))
    return jsonify(DEFAULT_DASHBOARD_CONFIG)


@dashboard_bp.route('/api/dashboard/config', methods=['POST'])
@login_required
def save_dashboard_config():
    username = session.get('username')
    config_data = request.get_json()
    if not isinstance(config_data, list):
        return jsonify({'error': 'La configuración debe ser una lista de widgets'}), 400
    
    config_json = json.dumps(config_data)
    db = get_db()
    db.execute('''
        INSERT INTO dashboard_config (username, config_json, updated_at)
        VALUES (?, ?, datetime('now', 'localtime'))
        ON CONFLICT(username) DO UPDATE SET
            config_json = excluded.config_json,
            updated_at = excluded.updated_at
    ''', [username, config_json])
    db.commit()
    return jsonify({'ok': True})


@dashboard_bp.route('/api/gasto/detalle', methods=['GET'])
def gasto_detalle():
    """
    Drill-down de un gráfico de gastos: dada una partida o una categoría,
    devuelve su evolución mensual, total, % sobre gastos y las partidas que la componen.
    Parámetros: year, unit ('' o 'TODAS' = consolidado), y partida=... o categoria=...
    """
    year      = request.args.get('year', str(datetime.now().year))
    unit      = request.args.get('unit', '')
    partida   = request.args.get('partida', '')
    categoria = request.args.get('categoria', '')
    db        = get_db()

    uc = '' if (not unit or unit == 'TODAS') else "AND unit=?"
    uc_params = [] if (not unit or unit == 'TODAS') else [unit]
    _, _, gas_p = get_clasificacion(db)

    if partida:
        targets, titulo = [partida], partida
    elif categoria:
        kws = GASTO_CATS.get(categoria, [])
        targets = sorted(p for p in gas_p if any(k.lower() in p.lower() for k in kws))
        titulo  = categoria
    else:
        return jsonify({'error': 'Especifica partida o categoria'}), 400

    if not targets:
        return jsonify({'titulo': titulo, 'unit': unit or 'TODAS', 'year': year,
                        'meses': [{'month': m, 'amount': 0} for m in MONTHS],
                        'total': 0, 'partidas': [], 'pct_gastos': 0, 'es_categoria': bool(categoria)})

    ph = ','.join('?' * len(targets))

    mrows = db.execute(
        f'SELECT month, SUM(amount) t FROM financials WHERE year=? AND partida IN ({ph}) {uc} GROUP BY month',
        [year] + targets + uc_params
    ).fetchall()
    by_month = {r['month']: r['t'] or 0 for r in mrows}
    meses    = [{'month': m, 'amount': round(by_month.get(m, 0), 2)} for m in MONTHS]
    total    = round(sum(by_month.values()), 2)

    prows = db.execute(
        f'SELECT partida, SUM(amount) t FROM financials WHERE year=? AND partida IN ({ph}) {uc} GROUP BY partida ORDER BY t DESC',
        [year] + targets + uc_params
    ).fetchall()
    partidas = [{'partida': r['partida'], 'total': round(r['t'] or 0, 2)} for r in prows if (r['t'] or 0)]

    tot_gastos = 0
    if gas_p:
        phg = ','.join('?' * len(gas_p))
        tot_gastos = db.execute(
            f'SELECT SUM(amount) FROM financials WHERE year=? AND partida IN ({phg}) {uc}',
            [year] + list(gas_p) + uc_params
        ).fetchone()[0] or 0
    pct = round(total / tot_gastos * 100, 1) if tot_gastos else 0

    return jsonify({'titulo': titulo, 'unit': unit or 'TODAS', 'year': year,
                    'meses': meses, 'total': total, 'partidas': partidas,
                    'pct_gastos': pct, 'es_categoria': bool(categoria)})


@dashboard_bp.route('/api/grafico/detalle', methods=['GET'])
def grafico_detalle():
    """
    Drill-down universal: dado el id del gráfico, devuelve su desglose.
    Parámetros: chart_id, year, unit (opcional), month (opcional para filtros específicos).
    """
    chart_id = request.args.get('chart_id', '')
    year     = request.args.get('year', str(datetime.now().year))
    unit     = request.args.get('unit', '')
    month    = request.args.get('month', '')
    db       = get_db()

    empresa_id = request.args.get('empresa_id', type=int) or None
    unidades_empresa = []
    if empresa_id is not None:
        unidades_empresa = [r['nombre'] for r in db.execute(
            'SELECT nombre FROM unidades WHERE empresa_id=?', (empresa_id,)
        ).fetchall()]

    if unit and unit != 'TODAS':
        uc = "AND unit=?"
        uc_params = [unit]
    elif empresa_id is not None and unidades_empresa:
        ph_u = ','.join('?' * len(unidades_empresa))
        uc = f"AND unit IN ({ph_u})"
        uc_params = list(unidades_empresa)
    else:
        uc = ''
        uc_params = []
    ing_p, cos_p, gas_p = get_clasificacion(db)

    if chart_id == 'ch-main':
        # Evolución principal (Ing/Cos/Gas) → detalle mes por mes
        meses = []
        for m in MONTHS:
            mc = f"AND month='{m}'"
            def msum(ps):
                if not ps: return 0
                ph = ','.join('?' * len(ps))
                return db.execute(
                    f'SELECT SUM(amount) FROM financials WHERE year=? AND partida IN ({ph}) {uc} {mc}',
                    [year] + list(ps) + uc_params
                ).fetchone()[0] or 0
            i = msum(ing_p); c = msum(cos_p); g = msum(gas_p)
            ub = i - c; un = i - c - g
            meses.append({'month': m, 'ingresos': round(i, 2), 'costos': round(c, 2),
                          'gastos': round(g, 2), 'utilidad_bruta': round(ub, 2),
                          'utilidad_neta': round(un, 2)})
        return jsonify({'titulo': 'Evolución Mensual', 'chart_id': chart_id,
                        'unit': unit or 'TODAS', 'year': year, 'meses': meses})

    elif chart_id == 'ch-mg':
        # Márgenes % → tabla mes por mes con cálculo
        meses = []
        for m in MONTHS:
            mc = f"AND month='{m}'"
            def msum(ps):
                if not ps: return 0
                ph = ','.join('?' * len(ps))
                return db.execute(
                    f'SELECT SUM(amount) FROM financials WHERE year=? AND partida IN ({ph}) {uc} {mc}',
                    [year] + list(ps) + uc_params
                ).fetchone()[0] or 0
            i = msum(ing_p); c = msum(cos_p); g = msum(gas_p)
            ub = i - c; un = i - c - g
            mb = (ub / i * 100) if i else 0
            mn = (un / i * 100) if i else 0
            meses.append({'month': m, 'ingresos': round(i, 2), 'costos': round(c, 2),
                          'gastos': round(g, 2), 'utilidad_bruta': round(ub, 2),
                          'utilidad_neta': round(un, 2), 'margen_bruto': round(mb, 1),
                          'margen_neto': round(mn, 1)})
        return jsonify({'titulo': 'Márgenes % — Detalle Mensual', 'chart_id': chart_id,
                        'unit': unit or 'TODAS', 'year': year, 'meses': meses})

    elif chart_id == 'ch-un':
        # Utilidad Neta → tabla mes por mes con componentes
        meses = []
        for m in MONTHS:
            mc = f"AND month='{m}'"
            def msum(ps):
                if not ps: return 0
                ph = ','.join('?' * len(ps))
                return db.execute(
                    f'SELECT SUM(amount) FROM financials WHERE year=? AND partida IN ({ph}) {uc} {mc}',
                    [year] + list(ps) + uc_params
                ).fetchone()[0] or 0
            i = msum(ing_p); c = msum(cos_p); g = msum(gas_p); un = i - c - g
            meses.append({'month': m, 'ingresos': round(i, 2), 'costos': round(c, 2),
                          'gastos': round(g, 2), 'utilidad_neta': round(un, 2)})
        return jsonify({'titulo': 'Utilidad Neta — Detalle Mensual', 'chart_id': chart_id,
                        'unit': unit or 'TODAS', 'year': year, 'meses': meses})

    elif chart_id == 'ch-rad':
        # Radar/Line comparativo → si consolidado, detalle por unidad; si unidad, detalle mensual Ing vs UN
        if not unit or unit == 'TODAS':
            # Vista consolidada: desglose por unidad (igual que top gastos pero para ingresos)
            unidades = []
            for u in (unidades_empresa if empresa_id is not None else UNITS):
                uc_u = f"AND unit='{u}'"
                def usum(ps):
                    if not ps: return 0
                    ph = ','.join('?' * len(ps))
                    return db.execute(
                        f'SELECT SUM(amount) FROM financials WHERE year=? AND partida IN ({ph}) {uc_u}',
                        [year] + list(ps)
                    ).fetchone()[0] or 0
                i = usum(ing_p); c = usum(cos_p); g = usum(gas_p)
                if i or c or g:
                    ub = i - c; un = i - c - g
                    unidades.append({'unit': u, 'ingresos': round(i, 2), 'costos': round(c, 2),
                                     'gastos': round(g, 2), 'utilidad_neta': round(un, 2),
                                     'margen_bruto': round(ub / i * 100, 1) if i else 0,
                                     'margen_neto': round(un / i * 100, 1) if i else 0})
            return jsonify({'titulo': 'Comparativo por Unidad', 'chart_id': chart_id,
                            'unit': 'TODAS', 'year': year, 'unidades': unidades})
        else:
            # Vista unidad individual: Ingresos vs Util.Neta mensual
            meses = []
            for m in MONTHS:
                mc = f"AND month='{m}'"
                def msum(ps):
                    if not ps: return 0
                    ph = ','.join('?' * len(ps))
                    return db.execute(
                        f'SELECT SUM(amount) FROM financials WHERE year=? AND partida IN ({ph}) {uc} {mc}',
                        [year] + list(ps) + uc_params
                    ).fetchone()[0] or 0
                i = msum(ing_p); c = msum(cos_p); g = msum(gas_p); un = i - c - g
                meses.append({'month': m, 'ingresos': round(i, 2), 'utilidad_neta': round(un, 2)})
            return jsonify({'titulo': f'Ingresos vs Util. Neta — {unit}', 'chart_id': chart_id,
                            'unit': unit, 'year': year, 'meses': meses})

    else:
        return jsonify({'error': 'chart_id no reconocido'}), 400

