from flask import Blueprint, jsonify, request
from datetime import datetime
from db import get_db

core_bp = Blueprint('core', __name__)


@core_bp.route('/api/empresas', methods=['GET'])
def get_empresas():
    """
    Lista las empresas legales del Holding (tabla empresas). Usado para poblar
    dinámicamente el selector de empresa en el sidebar.
    """
    db = get_db()
    rows = db.execute('SELECT id, nombre_corto, nombre_legal, color FROM empresas ORDER BY id').fetchall()
    return jsonify([dict(r) for r in rows])


@core_bp.route('/api/unidades', methods=['GET'])
def get_unidades():
    """
    Lista todas las unidades de negocio con su empresa_id.
    Usado para poblar dinamicamente el selector de Alcance en Exportar Briefing IA.
    """
    db = get_db()
    rows = db.execute('SELECT nombre, empresa_id FROM unidades ORDER BY empresa_id, nombre').fetchall()
    return jsonify([dict(r) for r in rows])


@core_bp.route('/api/trazabilidad')
def trazabilidad():
    """
    Devuelve el desglose de cuentas Odoo que componen un KPI.
    Params: year, unit, kpi (ingresos|costos|gastos|utilidad_bruta|utilidad_neta|ebitda)
    """
    year  = request.args.get('year', str(datetime.now().year))
    unit  = request.args.get('unit', '')
    kpi   = request.args.get('kpi', 'ingresos')

    KPI_FILTERS = {
        'ingresos':       lambda c: c.startswith('4'),
        'costos':         lambda c: c.startswith('5'),
        'gastos':         lambda c: c.startswith('6'),
        'utilidad_bruta': lambda c: c.startswith('4') or c.startswith('5'),
        'utilidad_neta':  lambda c: c.startswith('4') or c.startswith('5') or c.startswith('6'),
        'ebitda':         lambda c: c.startswith('4') or c.startswith('5') or c.startswith('6'),
    }

    filtro = KPI_FILTERS.get(kpi)
    if not filtro:
        return jsonify({'error': 'KPI no reconocido'}), 400

    db  = get_db()
    uc  = "AND unit=?" if unit and unit != 'TODAS' else ''
    params = [year] + ([unit] if unit and unit != 'TODAS' else [])

    rows = db.execute(
        f"""SELECT odoo_code, odoo_name, partida,
                   SUM(amount_sign) as total
            FROM financials_detail
            WHERE year=? {uc}
            GROUP BY odoo_code, odoo_name, partida
            ORDER BY ABS(SUM(amount_sign)) DESC""",
        params
    ).fetchall()

    cuentas = [
        {
            'odoo_code': r['odoo_code'],
            'odoo_name': r['odoo_name'],
            'partida':   r['partida'],
            'total':     round(r['total'], 2)
        }
        for r in rows if filtro(r['odoo_code'])
    ]

    total_kpi = sum(c['total'] for c in cuentas)
    if kpi in ('costos', 'gastos'):
        total_kpi = abs(total_kpi)
    elif kpi == 'utilidad_bruta':
        total_kpi = sum(c['total'] for c in cuentas if c['odoo_code'].startswith('4')) - \
                    abs(sum(c['total'] for c in cuentas if c['odoo_code'].startswith('5')))
    elif kpi in ('utilidad_neta', 'ebitda'):
        total_kpi = sum(c['total'] for c in cuentas if c['odoo_code'].startswith('4')) - \
                    abs(sum(c['total'] for c in cuentas if c['odoo_code'].startswith('5'))) - \
                    abs(sum(c['total'] for c in cuentas if c['odoo_code'].startswith('6')))

    return jsonify({
        'kpi':    kpi,
        'year':   year,
        'unit':   unit,
        'total':  round(total_kpi, 2),
        'cuentas': cuentas
    })


@core_bp.route('/api/esf/trazabilidad', methods=['GET'])
def esf_trazabilidad():
    """
    Devuelve el desglose de cuentas Odoo que componen una partida de ESF
    (BCV, sin ajuste de divisa real), para un trimestre puntual. ESF es
    snapshot (mes de cierre del trimestre, no acumulado).

    La partida que llega puede ser un subtotal de nivel 2 (ej. "Otras
    cuentas por pagar L.P.") cuyas cuentas reales viven bajo sus hijas de
    nivel 3 (parent_name apuntando a esa partida en ESF_STRUCTURE_V2), o
    puede ser ya una hoja real -- se resuelve dinamicamente contra
    ESF_STRUCTURE_V2 en vez de asumir un nombre fijo.
    Params: year, quarter, partida, unit (opcional), empresa_id (opcional)
    """
    from engine import QUARTER_MONTH_CIERRE, ESF_STRUCTURE_V2
    year = request.args.get('year', str(datetime.now().year))
    quarter = request.args.get('quarter', type=int)
    partida = request.args.get('partida', '')
    unit = request.args.get('unit', '')
    empresa_id = request.args.get('empresa_id', type=int)
    if not quarter or not partida:
        return jsonify({'error': 'quarter y partida son requeridos'}), 400
    month = QUARTER_MONTH_CIERRE.get(quarter)
    if not month:
        return jsonify({'error': f'Quarter invalido: {quarter}'}), 400

    # Resolver nombres hoja reales: si la partida tiene hijas (nivel+1 con
    # parent_name == partida), usar esas; si no, la partida ya es hoja.
    hijas = [row[0] for row in ESF_STRUCTURE_V2 if row[7] == partida]
    nombres_hoja = hijas if hijas else [partida]

    db = get_db()
    placeholders = ','.join('?' * len(nombres_hoja))
    codigos_rows = db.execute(
        f"SELECT DISTINCT odoo_code FROM mapping_groups_v2 WHERE report_type='esf' AND group_name IN ({placeholders})",
        nombres_hoja
    ).fetchall()
    codigos = [r['odoo_code'] for r in codigos_rows]
    if not codigos:
        return jsonify({'partida': partida, 'year': year, 'quarter': quarter, 'unit': unit, 'total': 0.0, 'cuentas': []})

    uc = "AND unit=?" if unit and unit != 'TODAS' else ''
    empresa_clause = "AND empresa_id=?" if empresa_id is not None else ''
    cod_placeholders = ','.join('?' * len(codigos))
    params = [year, month] + codigos
    if unit and unit != 'TODAS':
        params.append(unit)
    if empresa_id is not None:
        params.append(empresa_id)

    rows = db.execute(f'''
        SELECT odoo_code, odoo_name, SUM(amount_sign) as total
        FROM financials_detail
        WHERE year=? AND report_type='esf' AND month=? AND odoo_code IN ({cod_placeholders}) {uc} {empresa_clause}
        GROUP BY odoo_code, odoo_name
        ORDER BY ABS(SUM(amount_sign)) DESC
    ''', params).fetchall()

    cuentas = [{'odoo_code': r['odoo_code'], 'odoo_name': r['odoo_name'], 'total': round(r['total'], 2)} for r in rows]
    total = round(sum(c['total'] for c in cuentas), 2)

    return jsonify({'partida': partida, 'year': year, 'quarter': quarter, 'unit': unit, 'total': total, 'cuentas': cuentas})


@core_bp.route('/api/years', methods=['GET'])
def get_years():
    db = get_db()
    rows = db.execute(
        '''SELECT year FROM financials
           UNION SELECT year FROM esf_data
           UNION SELECT year FROM budget'''
    ).fetchall()
    years = sorted({str(r['year']) for r in rows if r['year'] is not None}, reverse=True)
    if not years:
        years = [str(datetime.now().year)]
    return jsonify(years)

