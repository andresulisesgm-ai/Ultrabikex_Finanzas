from flask import Blueprint, jsonify, request, session
from datetime import datetime
from db import get_db
from constants import MONTHS
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
    "icon": "💰",
    "colorClass": "cb",
    "visible": True,
    "order": 1,
    "dataset": "ingresos"
  },
  {
    "id": "kc-ub",
    "type": "kpi",
    "title": "Utilidad Bruta",
    "subtitle": "",
    "icon": "📈",
    "colorClass": "cg",
    "visible": True,
    "order": 2,
    "dataset": "utilidad_bruta"
  },
  {
    "id": "kc-gas",
    "type": "kpi",
    "title": "Total Gastos",
    "subtitle": "Operac.+No operac.",
    "icon": "📉",
    "colorClass": "cr",
    "visible": True,
    "order": 3,
    "dataset": "gastos"
  },
  {
    "id": "kc-un",
    "type": "kpi",
    "title": "Utilidad Neta",
    "subtitle": "",
    "icon": "🏆",
    "colorClass": "ca",
    "visible": True,
    "order": 4,
    "dataset": "utilidad_neta"
  },
  {
    "id": "kc-mb",
    "type": "kpi",
    "title": "Margen Bruto %",
    "subtitle": "Ref ≥30%",
    "icon": "%",
    "colorClass": "cp",
    "visible": False,
    "order": 5,
    "dataset": "margen_bruto"
  },
  {
    "id": "kc-mn",
    "type": "kpi",
    "title": "Margen Neto %",
    "subtitle": "Ref ≥5%",
    "icon": "%",
    "colorClass": "ct",
    "visible": False,
    "order": 6,
    "dataset": "margen_neto"
  },
  {
    "id": "kc-cos",
    "type": "kpi",
    "title": "Costo de Ventas",
    "subtitle": "Acumulado año",
    "icon": "🏭",
    "colorClass": "cb",
    "visible": False,
    "order": 7,
    "dataset": "costos"
  },
  {
    "id": "kc-rc",
    "type": "kpi",
    "title": "%Costo/Venta",
    "subtitle": "Eficiencia costos",
    "icon": "⚙️",
    "colorClass": "cr",
    "visible": False,
    "order": 8,
    "dataset": "ratio_costo"
  },
  {
    "id": "kc-ebt",
    "type": "kpi",
    "title": "EBITDA",
    "subtitle": "Acumulado año",
    "icon": "⭐",
    "colorClass": "ca",
    "visible": False,
    "order": 9,
    "dataset": "ebitda"
  },
  {
    "id": "kc-rg",
    "type": "kpi",
    "title": "%Gasto/Venta",
    "subtitle": "Eficiencia operativa",
    "icon": "🔧",
    "colorClass": "cg",
    "visible": False,
    "order": 10,
    "dataset": "ratio_gasto"
  },
  {
    "id": "wc-pe",
    "type": "special",
    "title": "Punto de Equilibrio",
    "subtitle": "Solo disponible por unidad",
    "visible": False,
    "order": 11,
    "doubleWidth": True,
    "dataset": "punto_equilibrio"
  },
  {
    "id": "wc-sem",
    "type": "special",
    "title": "Semáforo Financiero",
    "subtitle": "Estado de salud por indicador",
    "visible": True,
    "order": 12,
    "doubleWidth": False,
    "dataset": "semaforo",
    "sem_activos": ["mb","mn","rc","rg","un","pe","roe","roa","ratio_c","pa","pd","end","rotinv","rotact","cobro"]
  },
  {
    "id": "wc-gau",
    "type": "special",
    "title": "Indicadores Gauge",
    "subtitle": "Margen Neto · Cobertura PE · Eficiencia Operativa",
    "visible": True,
    "order": 13,
    "doubleWidth": False,
    "dataset": "gauges"
  },
  {
    "id": "wc-rank",
    "type": "special",
    "title": "Ranking de Rentabilidad",
    "subtitle": "Ordenado por margen neto",
    "visible": True,
    "order": 14,
    "doubleWidth": False,
    "dataset": "ranking"
  },
  {
    "id": "wc-main",
    "type": "chart",
    "title": "Ingresos · Costos · Gastos",
    "subtitle": "Evolución mensual · clic para ver detalle",
    "visible": True,
    "order": 15,
    "doubleWidth": True,
    "chartType": "bar",
    "dataset": "ingresos_costos_gastos"
  },
  {
    "id": "wc-tm",
    "type": "special",
    "title": "Participación por Unidad",
    "subtitle": "Ingresos proporcionales",
    "visible": True,
    "order": 16,
    "doubleWidth": False,
    "dataset": "participacion_unidad"
  },
  {
    "id": "wc-rad",
    "type": "chart",
    "title": "Comparativo Multidimensional",
    "subtitle": "Por unidad de negocio",
    "visible": True,
    "order": 17,
    "doubleWidth": False,
    "chartType": "radar",
    "dataset": "comparativo_multidimensional"
  },
  {
    "id": "wc-mg",
    "type": "chart",
    "title": "Márgenes %",
    "subtitle": "Bruto y neto mensual · clic para ver detalle",
    "visible": True,
    "order": 18,
    "doubleWidth": False,
    "chartType": "line",
    "dataset": "margenes"
  },
  {
    "id": "wc-un",
    "type": "chart",
    "title": "Utilidad Neta Mensual",
    "subtitle": "+/− por mes · clic para ver detalle",
    "visible": True,
    "order": 19,
    "doubleWidth": False,
    "chartType": "bar",
    "dataset": "utilidad_neta_mensual"
  },
  {
    "id": "wc-est",
    "type": "chart",
    "title": "Estructura de Gastos",
    "subtitle": "Por categoría · clic para ver detalle",
    "visible": True,
    "order": 20,
    "doubleWidth": False,
    "chartType": "doughnut",
    "dataset": "estructura_gastos"
  },
  {
    "id": "wc-tg",
    "type": "chart",
    "title": "Top 10 Gastos",
    "subtitle": "Mayor impacto · clic para ver detalle",
    "visible": True,
    "order": 21,
    "doubleWidth": True,
    "chartType": "bar",
    "dataset": "top_gastos"
  },
  {
    "id": "wc-wf",
    "type": "special",
    "title": "Cascada P&L",
    "subtitle": "De ingresos a utilidad neta",
    "visible": True,
    "order": 22,
    "doubleWidth": True,
    "dataset": "cascada_pl"
  },
  {
    "id": "wc-tbl",
    "type": "table",
    "title": "Resumen Mensual",
    "subtitle": "Detalle por período",
    "visible": True,
    "order": 23,
    "doubleWidth": True,
    "dataset": "tabla_resumen"
  },
  {
    "id": "wc-esf-kpi-activos",
    "type": "esf",
    "title": "Total Activos",
    "subtitle": "Último quarter disponible",
    "icon": "🏦",
    "colorClass": "cb",
    "visible": False,
    "order": 24,
    "dataset": "esf_totals"
  },
  {
    "id": "wc-esf-kpi-pasivos",
    "type": "esf",
    "title": "Total Pasivos",
    "subtitle": "Último quarter disponible",
    "icon": "📋",
    "colorClass": "cr",
    "visible": False,
    "order": 25,
    "dataset": "esf_totals"
  },
  {
    "id": "wc-esf-kpi-patrimonio",
    "type": "esf",
    "title": "Patrimonio",
    "subtitle": "Último quarter disponible",
    "icon": "💎",
    "colorClass": "cg",
    "visible": False,
    "order": 26,
    "dataset": "esf_totals"
  },
  {
    "id": "wc-esf-kpi-efectivo",
    "type": "esf",
    "title": "Efectivo y Equivalentes",
    "subtitle": "Último quarter disponible",
    "icon": "💵",
    "colorClass": "ca",
    "visible": False,
    "order": 27,
    "dataset": "esf_totals"
  },
  {
    "id": "wc-esf-kpi-cxc",
    "type": "esf",
    "title": "Cuentas por Cobrar",
    "subtitle": "Último quarter disponible",
    "icon": "📥",
    "colorClass": "cp",
    "visible": False,
    "order": 28,
    "dataset": "esf_totals"
  },
  {
    "id": "wc-esf-kpi-inv",
    "type": "esf",
    "title": "Inventarios",
    "subtitle": "Último quarter disponible",
    "icon": "📦",
    "colorClass": "ct",
    "visible": False,
    "order": 29,
    "dataset": "esf_totals"
  },
  {
    "id": "wc-esf-estructura",
    "type": "esf",
    "title": "Estructura Financiera",
    "subtitle": "Activos · Pasivos · Patrimonio",
    "visible": True,
    "order": 30,
    "doubleWidth": True,
    "chartType": "doughnut",
    "dataset": "esf_totals"
  },
  {
    "id": "wc-ind-roe",
    "type": "indicador",
    "title": "ROE",
    "subtitle": "Retorno sobre Patrimonio",
    "icon": "📊",
    "colorClass": "cg",
    "visible": False,
    "order": 31,
    "dataset": "indicadores_avanzados"
  },
  {
    "id": "wc-ind-roa",
    "type": "indicador",
    "title": "ROA",
    "subtitle": "Retorno sobre Activos",
    "icon": "📊",
    "colorClass": "cb",
    "visible": False,
    "order": 32,
    "dataset": "indicadores_avanzados"
  },
  {
    "id": "wc-ind-rc",
    "type": "indicador",
    "title": "Razón Corriente",
    "subtitle": "Activo Cte / Pasivo Cte",
    "icon": "⚖️",
    "colorClass": "ca",
    "visible": False,
    "order": 33,
    "dataset": "indicadores_avanzados"
  },
  {
    "id": "wc-ind-pa",
    "type": "indicador",
    "title": "Prueba Ácida",
    "subtitle": "Liquidez sin inventarios",
    "icon": "🧪",
    "colorClass": "cp",
    "visible": False,
    "order": 34,
    "dataset": "indicadores_avanzados"
  },
  {
    "id": "wc-ind-pd",
    "type": "indicador",
    "title": "Prueba Defensiva",
    "subtitle": "Solo efectivo / Pasivo Cte",
    "icon": "🛡️",
    "colorClass": "ct",
    "visible": False,
    "order": 35,
    "dataset": "indicadores_avanzados"
  },
  {
    "id": "wc-ind-end",
    "type": "indicador",
    "title": "Ratio Endeudamiento",
    "subtitle": "Pasivos / Patrimonio",
    "icon": "📉",
    "colorClass": "cr",
    "visible": False,
    "order": 36,
    "dataset": "indicadores_avanzados"
  },
  {
    "id": "wc-ind-rotinv",
    "type": "indicador",
    "title": "Rotación Inventarios",
    "subtitle": "Meses de cobertura",
    "icon": "🔄",
    "colorClass": "cb",
    "visible": False,
    "order": 37,
    "dataset": "indicadores_avanzados"
  },
  {
    "id": "wc-ind-rotact",
    "type": "indicador",
    "title": "Rotación de Activos",
    "subtitle": "Veces por trimestre",
    "icon": "⚙️",
    "colorClass": "cg",
    "visible": False,
    "order": 38,
    "dataset": "indicadores_avanzados"
  },
  {
    "id": "wc-ind-cobro",
    "type": "indicador",
    "title": "Período de Cobro",
    "subtitle": "Días promedio de cobro",
    "icon": "📅",
    "colorClass": "ca",
    "visible": False,
    "order": 39,
    "dataset": "indicadores_avanzados"
  },
  {
    "id": "wc-panel-indicadores",
    "type": "panel",
    "title": "Panel de Indicadores",
    "subtitle": "ROE · ROA · Liquidez · Rotación",
    "visible": False,
    "order": 40,
    "doubleWidth": True,
    "chartType": "bar",
    "dataset": "indicadores_avanzados"
  },
  {
    "id": "wc-panel-esf",
    "type": "panel",
    "title": "Panel Balance ESF",
    "subtitle": "Activos · Pasivos · Patrimonio",
    "visible": False,
    "order": 41,
    "doubleWidth": True,
    "chartType": "bar",
    "dataset": "esf_totals"
  },
  {
    "id": "wc-divisa-ingr",
    "type": "divisa",
    "title": "Ingresos en USD Real",
    "subtitle": "Ajustado por tasa paralela",
    "icon": "💵",
    "colorClass": "cb",
    "visible": True,
    "order": 42,
    "dataset": "divisa_real"
  },
  {
    "id": "wc-divisa-un",
    "type": "divisa",
    "title": "Utilidad Neta en USD Real",
    "subtitle": "Ajustado por tasa paralela",
    "icon": "💰",
    "colorClass": "cg",
    "visible": True,
    "order": 43,
    "dataset": "divisa_real"
  },
  {
    "id": "wc-divisa-comp",
    "type": "divisa",
    "title": "Comparativa Bs vs USD Real",
    "subtitle": "Ingresos · Costos · Utilidad",
    "visible": True,
    "order": 44,
    "doubleWidth": True,
    "chartType": "bar",
    "dataset": "divisa_real"
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

    # 8. Indicadores Avanzados pasando ingresos y utilidad neta calculados
    from app import compute_indicadores
    indicadores_avanzados = compute_indicadores(db, year, '' if unit == 'TODAS' else unit, tI, un, empresa_id=empresa_id)

    totals = {
        'ingresos': round(tI, 2),
        'costos': round(tC, 2),
        'utilidad_bruta': round(ub, 2),
        'gastos': round(tG, 2),
        'ebitda': round(ebt, 2),
        'utilidad_neta': round(un, 2)
    }

    return jsonify({
        'months': months_data, 'por_unidad': por_unidad, 'top_gastos': top_gastos,
        'cat_gastos': cat_gastos, 'loaded': [{'unit': r['unit'], 'month': r['month']} for r in loaded],
        'totals': totals,
        'indicadores_avanzados': indicadores_avanzados,
        'punto_equilibrio': pe
    })
