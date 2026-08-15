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
