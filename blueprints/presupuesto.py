import os
import tempfile
from flask import Blueprint, jsonify, request
from datetime import datetime
from db import get_db
from auth import admin_required
from constants import MONTHS

presupuesto_bp = Blueprint('presupuesto', __name__)


@presupuesto_bp.route('/api/budget', methods=['GET'])
def get_budget():
    """
    Retorna presupuesto vs real para year/unit dado.
    Parámetros: year, unit (opcional), month (opcional)
    """
    year  = request.args.get('year', str(datetime.now().year))
    unit  = request.args.get('unit', '')
    month = request.args.get('month', '')
    db    = get_db()

    uc = "AND unit=?" if unit else ''
    mc = "AND month=?" if month else ''
    params = [year] + ([unit] if unit else []) + ([month] if month else [])

    # Presupuesto
    brows = db.execute(
        f'SELECT partida, month, SUM(amount) amount FROM budget WHERE year=? {uc} {mc} GROUP BY partida, month',
        params
    ).fetchall()
    budget = {}
    for r in brows:
        budget.setdefault(r['partida'], {})[r['month']] = r['amount']

    # Real
    rrows = db.execute(
        f'SELECT partida, month, SUM(amount) amount FROM financials WHERE year=? {uc} {mc} GROUP BY partida, month',
        params
    ).fetchall()
    real = {}
    for r in rrows:
        real.setdefault(r['partida'], {})[r['month']] = r['amount']

    # Construir comparativo
    all_partidas = set(budget.keys()) | set(real.keys())
    result = []
    for p in sorted(all_partidas):
        row = {'partida': p, 'meses': {}}
        for m in MONTHS:
            b = budget.get(p, {}).get(m, 0)
            r = real.get(p, {}).get(m, 0)
            var = round((r - b) / abs(b) * 100, 1) if b != 0 else None
            row['meses'][m] = {'presupuesto': round(b, 2), 'real': round(r, 2), 'var_pct': var}
        row['acum_presupuesto'] = round(sum(budget.get(p, {}).get(m, 0) for m in MONTHS), 2)
        row['acum_real']        = round(sum(real.get(p, {}).get(m, 0) for m in MONTHS), 2)
        ap = row['acum_presupuesto']
        ar = row['acum_real']
        row['acum_var_pct']  = round((ar - ap) / abs(ap) * 100, 1) if ap != 0 else None
        result.append(row)

    return jsonify({'year': year, 'unit': unit, 'comparativo': result})


@presupuesto_bp.route('/api/budget', methods=['POST'])
@admin_required
def set_budget():
    """
    Carga/actualiza valores de presupuesto.
    Body JSON: {year, unit, month, partida, amount}
    O batch: {year, unit, rows: [{month, partida, amount}]}
    """
    d  = request.json
    db = get_db()
    try:
        if 'rows' in d:
            for row in d['rows']:
                db.execute(
                    '''INSERT INTO budget (year, month, unit, partida, amount) VALUES (?,?,?,?,?)
                       ON CONFLICT(year, month, unit, partida) DO UPDATE SET amount=excluded.amount''',
                    (d['year'], row['month'], d['unit'], row['partida'], row['amount'])
                )
        else:
            db.execute(
                '''INSERT INTO budget (year, month, unit, partida, amount) VALUES (?,?,?,?,?)
                   ON CONFLICT(year, month, unit, partida) DO UPDATE SET amount=excluded.amount''',
                (d['year'], d['month'], d['unit'], d['partida'], d['amount'])
            )
        db.commit()
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@presupuesto_bp.route('/api/budget/<year>/<unit>/<month>/<path:partida>', methods=['DELETE'])
@admin_required
def delete_budget(year, unit, month, partida):
    db = get_db()
    db.execute('DELETE FROM budget WHERE year=? AND unit=? AND month=? AND partida=?',
               (year, unit, month, partida))
    db.commit()
    return jsonify({'ok': True})


def _to_number(v):
    """Convierte una celda (número o texto con formato es-VE/en-US) a float, o None."""
    if v is None:
        return None
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace('$', '').replace('%', '').replace(' ', '')
    if not s or s == '-':
        return None
    neg = s.startswith('(') and s.endswith(')')
    if neg:
        s = s[1:-1]
    if ',' in s and '.' in s:          # 1.234,56 (es-VE)  ó  1,234.56 (en-US)
        if s.rfind(',') > s.rfind('.'):
            s = s.replace('.', '').replace(',', '.')
        else:
            s = s.replace(',', '')
    elif ',' in s:                      # 1234,56 -> 1234.56
        s = s.replace(',', '.')
    try:
        val = float(s)
        return -val if neg else val
    except ValueError:
        return None


@presupuesto_bp.route('/api/budget/import', methods=['POST'])
@admin_required
def import_budget():
    """
    Importa presupuesto desde CSV o Excel.
    Form-data: file, year, unit (obligatoria — no se permite consolidado).
    Formato esperado: una columna 'Partida' (o la primera) y columnas con encabezado
    de mes (ENE, FEB, ... DIC). Cada celda numérica se inserta/actualiza en budget.
    """
    file = request.files.get('file')
    year = request.form.get('year', str(datetime.now().year))
    unit = request.form.get('unit', '').strip()

    if not file:
        return jsonify({'error': 'No se envió archivo'}), 400
    if not unit:
        return jsonify({'error': 'Debe seleccionar una unidad específica (no Consolidado) para importar'}), 400

    fn = (file.filename or '').lower()
    rows_matrix = []
    try:
        if fn.endswith('.csv'):
            import csv, io
            text = file.read().decode('utf-8-sig', errors='replace')
            sample = text[:4096]
            delim = ';' if sample.count(';') > sample.count(',') else ','
            rows_matrix = [r for r in csv.reader(io.StringIO(text), delimiter=delim)]
        elif fn.endswith('.xlsx'):
            import openpyxl
            tmp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
            tmp = tmp_file.name
            tmp_file.close()
            file.save(tmp)
            wb = openpyxl.load_workbook(tmp, data_only=True)
            ws = wb.active
            rows_matrix = [list(r) for r in ws.iter_rows(values_only=True)]
            wb.close()
            os.remove(tmp)
        elif fn.endswith('.xls'):
            try:
                import xlrd
            except ImportError:
                return jsonify({'error': '.xls requiere xlrd. Convierte el archivo a .xlsx o .csv'}), 400
            tmp_file = tempfile.NamedTemporaryFile(suffix='.xls', delete=False)
            tmp = tmp_file.name
            tmp_file.close()
            file.save(tmp)
            book = xlrd.open_workbook(tmp)
            sh   = book.sheet_by_index(0)
            rows_matrix = [sh.row_values(i) for i in range(sh.nrows)]
            os.remove(tmp)
        else:
            return jsonify({'error': 'Formato no soportado. Usa .csv, .xlsx o .xls'}), 400
    except Exception as e:
        return jsonify({'error': f'Error leyendo archivo: {e}'}), 500

    if not rows_matrix:
        return jsonify({'error': 'El archivo está vacío'}), 400

    # Localizar fila de encabezado (la primera que contenga al menos un mes reconocible)
    header_idx = None
    for i, r in enumerate(rows_matrix):
        cells = [str(c).strip().upper() if c is not None else '' for c in r]
        if any(c in MONTHS for c in cells):
            header_idx = i
            break
    if header_idx is None:
        return jsonify({'error': f'No se encontró fila de encabezado con meses ({", ".join(MONTHS)})'}), 400

    header_up = [str(c).strip().upper() if c is not None else '' for c in rows_matrix[header_idx]]

    partida_col = 0
    for j, c in enumerate(header_up):
        if any(k in c for k in ('PARTIDA', 'CUENTA', 'CONCEPTO')):
            partida_col = j
            break
    month_cols = {j: header_up[j] for j in range(len(header_up)) if header_up[j] in MONTHS}
    if not month_cols:
        return jsonify({'error': 'No se reconoció ninguna columna de mes'}), 400

    db = get_db()
    inserted = 0
    partidas = set()
    for r in rows_matrix[header_idx + 1:]:
        if partida_col >= len(r):
            continue
        partida = str(r[partida_col]).strip() if r[partida_col] is not None else ''
        if not partida:
            continue
        for j, mname in month_cols.items():
            if j >= len(r):
                continue
            amount = _to_number(r[j])
            if amount is None:
                continue
            db.execute(
                '''INSERT INTO budget (year, month, unit, partida, amount) VALUES (?,?,?,?,?)
                   ON CONFLICT(year, month, unit, partida) DO UPDATE SET amount=excluded.amount''',
                (year, mname, unit, partida, amount)
            )
            inserted += 1
            partidas.add(partida)
    db.commit()

    return jsonify({'ok': True, 'inserted': inserted, 'partidas': len(partidas),
                    'meses': sorted(month_cols.values(), key=lambda m: MONTHS.index(m)),
                    'unit': unit, 'year': year})
