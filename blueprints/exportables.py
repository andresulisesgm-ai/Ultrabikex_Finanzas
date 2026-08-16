from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
from constants import MONTHS
from db import get_db

exportables_bp = Blueprint('exportables', __name__)


@exportables_bp.route('/api/export/excel', methods=['GET'])
def export_excel():
    tipo = request.args.get('tipo', '')
    year = request.args.get('year', str(datetime.now().year))

    if tipo == 'indicadores':
        from exporters.excel_indicadores import IndicadoresExporter
        exp = IndicadoresExporter(year)
        path = exp.generate()
        return send_file(path, as_attachment=True, download_name=f'INDICADORES_ULTRAX_{year}.xlsx')

    from exporters.excel_eerr import ExcelExporter
    unit = request.args.get('unit', '')
    mf   = request.args.get('month_from', '')
    mt   = request.args.get('month_to', '')
    empresa_id = request.args.get('empresa_id', type=int)

    if mf and mt and mf in MONTHS and mt in MONTHS:
        fi, ti = MONTHS.index(mf), MONTHS.index(mt)
        sel = MONTHS[fi:ti+1] if fi <= ti else MONTHS[fi:] + MONTHS[:ti+1]
    elif mf and mf in MONTHS:
        sel = MONTHS[MONTHS.index(mf):]
    else:
        sel = MONTHS

    divisa = request.args.get('divisa', '') == '1'
    db_conn = get_db()
    if unit:
        units = [unit]
    elif empresa_id is not None:
        units = [r[0] for r in db_conn.execute('SELECT nombre FROM unidades WHERE empresa_id=?', [empresa_id]).fetchall()]
    else:
        # Holding (sin empresa_id explícito desde este flujo): agregado de todas las unidades reales de las 4 empresas.
        units = [r[0] for r in db_conn.execute('SELECT nombre FROM unidades').fetchall()]
    exp    = ExcelExporter(year, units, sel, divisa_real=divisa, empresa_id=empresa_id)
    try:
        path = exp.generate()
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    from helpers import _nombre_empresa_display
    nombre_emp_dl = _nombre_empresa_display(db_conn, empresa_id) if unit == '' else unit
    suf   = (f'_{unit}' if unit else '_CONSOLIDADO') + ('_DIVISA_REAL' if divisa else '') + (f'_{mf}-{mt}' if mf and mt else '')
    return send_file(path, as_attachment=True, download_name=f'EERR_{nombre_emp_dl}_{year}{suf}.xlsx')


@exportables_bp.route('/api/export/esf', methods=['GET'])
def export_esf():
    from exporters.excel_esf import ESFExporter
    year = request.args.get('year', str(datetime.now().year))
    quarter = request.args.get('quarter', '')
    empresa_id = request.args.get('empresa_id', type=int)
    QUARTER_MESES = {
        '1': ['ENE', 'FEB', 'MAR'],
        '2': ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN'],
        '3': ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEPT'],
        '4': MONTHS,
    }
    meses = QUARTER_MESES.get(quarter, MONTHS)
    exp  = ESFExporter(year, meses, empresa_id=empresa_id)
    path = exp.generate()
    db_conn_esf = get_db()
    from helpers import _nombre_empresa_display
    nombre_emp_esf = _nombre_empresa_display(db_conn_esf, empresa_id)
    suf  = f'_Q{quarter}' if quarter else ''
    return send_file(path, as_attachment=True, download_name=f'ESF_{nombre_emp_esf}_{year}{suf}.xlsx')


@exportables_bp.route('/api/export/esf-divisa-real', methods=['GET'])
def export_esf_divisa_real():
    from exporters.excel_esf_divisa import ESFDivisaRealExporter
    year = request.args.get('year', str(datetime.now().year))
    empresa_id = request.args.get('empresa_id', type=int)
    exp = ESFDivisaRealExporter(year, empresa_id=empresa_id)
    path = exp.generate()
    db_conn_dr = get_db()
    from helpers import _nombre_empresa_display
    nombre_emp_dr = _nombre_empresa_display(db_conn_dr, empresa_id)
    return send_file(path, as_attachment=True, download_name=f'ESF_DIVISA_REAL_{nombre_emp_dr}_{year}.xlsx')
