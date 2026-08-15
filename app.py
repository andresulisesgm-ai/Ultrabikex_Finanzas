from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
import sqlite3, os, shutil, tempfile, secrets
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from engine import OdooParser, MONTH_TO_QUARTER
from exporters.excel_eerr import ExcelExporter
from exporters.excel_esf import ESFExporter
from db import init_db, migrate_db, get_db, close_db, DB_PATH
from auth import login_required, admin_required, verify_password, get_current_user
from blueprints.backup import backup_bp
from blueprints.tasas import tasas_bp
from blueprints.metodo_pago import metodo_pago_bp
from blueprints.historial import historial_bp
from blueprints.eerr import eerr_bp
from blueprints.esf import esf_bp
from blueprints.indicadores import indicadores_bp
from blueprints.dashboard import dashboard_bp
from blueprints.core import core_bp
from blueprints.comparativas import comparativas_bp
from blueprints.presupuesto import presupuesto_bp
from blueprints.datos import datos_bp
from blueprints.divisa_real import divisa_real_bp
from constants import MONTHS, UNITS, ESF_PLUG_VARIACION_UMBRAL, PARTIDAS_DIVISOR_SEGMENTADO, SUBTOTAL_INGRESO_KEYS_POR_SEGMENTO, SEGMENTOS_INGRESO_PCT_VTAS
from helpers import divisor_ejec, divisor_ppto_mes, divisor_prev, calcular_muestra_pct_gastos, get_clasificacion, aplicar_factor_divisa, get_grouped_partidas_v2

app = Flask(__name__)
app.register_blueprint(backup_bp)
app.register_blueprint(tasas_bp)
app.register_blueprint(metodo_pago_bp)
app.register_blueprint(historial_bp)
app.register_blueprint(eerr_bp)
app.register_blueprint(esf_bp)
app.register_blueprint(indicadores_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(core_bp)
app.register_blueprint(comparativas_bp)
app.register_blueprint(presupuesto_bp)
app.register_blueprint(datos_bp)
app.register_blueprint(divisa_real_bp)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = secrets.token_hex(32)
limiter = Limiter(get_remote_address, app=app, default_limits=[])
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.errorhandler(429)
def rate_limit_exceeded(e):
    return jsonify({'error': 'Demasiados intentos. Espera 30 segundos e inténtalo de nuevo.'}), 429



# ── Protección global por defecto (fix seguridad ultrax jul-2026) ──
# Todas las rutas requieren sesión activa, salvo las explícitamente exentas abajo.
RUTAS_PUBLICAS = {'login_page', 'login', 'static'}

# Umbral de variación trimestral del plug "Resultados acumulados" en
# el guardián de integridad ESF (validate_esf_integrity). Calibrado
# empíricamente en jul-2026 con datos simulados (rango observado:
# 9.6%-21.7% de Total Activos en fluctuación normal). Recalibrar cuando
# se acumulen varios trimestres de datos reales de producción.

@app.before_request
def _requerir_sesion_global():
    if request.endpoint in RUTAS_PUBLICAS or request.endpoint is None:
        return
    if 'username' not in session:
        if request.path.startswith('/api/'):
            return jsonify({'error': 'No autenticado. Inicia sesión.'}), 401
        return redirect(url_for('login_page'))

# Registrar función de cierre de base de datos
app.teardown_appcontext(close_db)








# ── Anti-caché ──────────────────────────────────────────────────────────────────
# Evita que el navegador sirva versiones viejas de index.html / respuestas API
# durante el desarrollo (causa típica de SyntaxError fantasma por HTML cacheado).

@app.after_request
def no_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


# ── Helpers ───────────────────────────────────────────────────────────────────




# ── Rutas de autenticación ────────────────────────────────────────────────────

@app.route('/login')
def login_page():
    if 'username' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per 30 seconds")
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Usuario y contraseña son requeridos'}), 400

    role = verify_password(username, password)
    if role:
        session['username'] = username
        session['role'] = role
        return jsonify({'success': True, 'role': role})

    return jsonify({'error': 'Credenciales inválidas'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/current-user')
@login_required
def current_user():
    return jsonify(get_current_user())


# ── Rutas base ────────────────────────────────────────────────────────────────

@app.route('/')
@login_required
def index():
    user = get_current_user()
    return render_template('index.html', units=UNITS, months=MONTHS, user=user)


# ── Upload ────────────────────────────────────────────────────────────────────

@app.route('/api/upload', methods=['POST'])
@admin_required
def upload():
    file    = request.files.get('file')
    if file and not file.filename.lower().endswith(('.xlsx', '.xls')):
        return jsonify({'error': 'El archivo debe ser .xlsx o .xls'}), 400
    unit    = request.form.get('unit')
    month   = request.form.get('month')
    year    = request.form.get('year', str(datetime.now().year))
    is_esf  = request.form.get('is_esf', 'false').lower() == 'true'
    empresa_id = request.form.get('empresa_id', type=int) or None
    if is_esf:
        unit = 'CONSOLIDADO'
        if not empresa_id:
            return jsonify({'error': 'empresa_id es requerido para cargas de ESF'}), 400

    if not all([file, unit, month]):
        return jsonify({'error': 'Faltan parámetros'}), 400

    force = request.form.get('force', 'false').lower() == 'true'

    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    if file_size > 10 * 1024 * 1024:
        return jsonify({'error': 'El archivo excede el tamaño máximo permitido (10MB)'}), 400

    safe_filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
    file.save(path)

    try:
        parser   = OdooParser(path)
        accounts = parser.parse()
        if not accounts:
            return jsonify({'error': 'No se reconoció ninguna cuenta en el archivo. Verifica el formato.'}), 400

        balance_count = sum(1 for code in accounts if OdooParser.is_balance_account(code))
        result_count = len(accounts) - balance_count

        if is_esf and result_count > balance_count:
            return jsonify({'error': f'El archivo parece ser un EERR (mayoría de cuentas de resultado: {result_count} vs {balance_count} de balance), pero se marcó como ESF. Verifica el archivo o la selección.'}), 400

        if not is_esf and balance_count > result_count:
            return jsonify({'error': f'El archivo parece ser un ESF (mayoría de cuentas de balance: {balance_count} vs {result_count} de resultado), pero se marcó como EERR. Verifica el archivo o la selección.'}), 400

        db = get_db()

        if not force:
            if is_esf:
                quarter_check = MONTH_TO_QUARTER.get(month, 1)
                existing = db.execute(
                    'SELECT COUNT(*) FROM esf_data WHERE year=? AND quarter=? AND unit=? AND empresa_id=?',
                    (year, quarter_check, 'CONSOLIDADO', empresa_id)
                ).fetchone()[0]
            else:
                existing = db.execute(
                    'SELECT COUNT(*) FROM financials WHERE year=? AND month=? AND unit=?',
                    (year, month, unit)
                ).fetchone()[0]
            if existing > 0:
                return jsonify({'exists': True}), 200

        inserted_fin, inserted_esf, skipped, unmapped = 0, 0, 0, []
        quarter = MONTH_TO_QUARTER.get(month, 1)

        # Limpiar datos previos del mismo período antes de insertar (evita acumulación de cargas)
        if is_esf:
            db.execute(
                'DELETE FROM esf_data WHERE year=? AND quarter=? AND unit=? AND empresa_id=?',
                (year, quarter, unit, empresa_id)
            )
            db.execute(
                'DELETE FROM financials_detail WHERE year=? AND quarter=? AND unit=? AND report_type=\'esf\' AND empresa_id=?',
                (year, quarter, unit, empresa_id)
            )
            db.commit()
        else:
            db.execute(
                'DELETE FROM financials WHERE year=? AND month=? AND unit=?',
                (year, month, unit)
            )
            db.execute(
                'DELETE FROM financials_detail WHERE year=? AND month=? AND unit=? AND report_type=\'eerr\'',
                (year, month, unit)
            )
            db.commit()

        for code, amount in accounts.items():
            is_balance = OdooParser.is_balance_account(code)

            m = db.execute('SELECT partida, sign, income_type FROM mapping WHERE odoo_code = ?', (code,)).fetchone()

            if not m:
                # Auto-mapeo por nombre exacto, luego por prefijo de código
                name_clean = parser.names.get(code, '').strip().lower()
                auto = None
                if name_clean:
                    auto = db.execute(
                        'SELECT partida, sign, income_type FROM mapping WHERE lower(odoo_name)=?',
                        (name_clean,)
                    ).fetchone()
                if not auto:
                    prefix = '.'.join(code.split('.')[:2])
                    auto = db.execute(
                        "SELECT partida, sign, income_type FROM mapping WHERE odoo_code LIKE ? LIMIT 1",
                        (prefix + '%',)
                    ).fetchone()
                if auto:
                    db.execute(
                        'INSERT OR IGNORE INTO mapping (odoo_code, odoo_name, partida, sign, income_type) VALUES (?,?,?,?,?)',
                        (code, parser.names.get(code, ''), auto['partida'], auto['sign'], auto['income_type'])
                    )
                    db.commit()
                    m = auto

            if m:
                signed_amount = amount * (m['sign'] if m['sign'] else -1)

                # Guardar detalle cuenta por cuenta para Notas
                report_type = 'esf' if (is_balance or is_esf) else 'eerr'
                db.execute(
                    '''INSERT INTO financials_detail 
                       (year, month, unit, odoo_code, odoo_name, partida, amount_orig, amount_sign, report_type, quarter, empresa_id)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?)
                       ON CONFLICT(year, month, unit, odoo_code, empresa_id) 
                       DO UPDATE SET amount_orig=excluded.amount_orig, 
                                    amount_sign=excluded.amount_sign,
                                    partida=excluded.partida''',
                    (year, month, unit, code, parser.names.get(code, ''),
                     m['partida'], amount, signed_amount, report_type, quarter,
                     empresa_id if is_esf else None)
                )

                if is_balance or is_esf:
                    # Cuentas 1.x / 2.x / 3.x → esf_data (snapshot trimestral)
                    db.execute(
                        '''INSERT INTO esf_data (year, quarter, unit, partida, amount, empresa_id) VALUES (?,?,?,?,?,?)
                           ON CONFLICT(year, quarter, unit, partida, empresa_id) DO UPDATE SET amount=excluded.amount''',
                        (year, quarter, unit, m['partida'], signed_amount, empresa_id if is_esf else None)
                    )
                    inserted_esf += 1
                else:
                    # Cuentas 4.x / 5.x / 6.x → financials (flujo mensual)
                    db.execute(
                        '''INSERT INTO financials (year, month, unit, partida, amount) VALUES (?,?,?,?,?)
                           ON CONFLICT(year, month, unit, partida) DO UPDATE SET amount=excluded.amount''',
                        (year, month, unit, m['partida'], signed_amount)
                    )
                    inserted_fin += 1
            else:
                unmapped.append({'code': code, 'name': parser.names.get(code, ''), 'amount': amount})
                skipped += 1

        db.commit()
        # Marcar entrada anterior como sustituida si es un reemplazo
        if force:
            prev = db.execute(
                '''SELECT id FROM history WHERE year=? AND month=? AND unit=? AND is_esf=?
                   AND superseded_by IS NULL ORDER BY created_at DESC LIMIT 1''',
                (year, month, unit, 1 if is_esf else 0)
            ).fetchone()
            if prev:
                new_entry = db.execute(
                    'INSERT INTO history (year, month, unit, inserted, is_esf, empresa_id) VALUES (?,?,?,?,?,?)',
                    (year, month, unit, inserted_fin + inserted_esf, 1 if is_esf else 0, empresa_id if is_esf else None)
                )
                new_id = new_entry.lastrowid
                db.execute(
                    'UPDATE history SET superseded_by=?, superseded_at=datetime(\'now\',\'localtime\') WHERE id=?',
                    (new_id, prev['id'])
                )
                db.commit()
            else:
                db.execute(
                    'INSERT INTO history (year, month, unit, inserted, is_esf, empresa_id) VALUES (?,?,?,?,?,?)',
                    (year, month, unit, inserted_fin + inserted_esf, 1 if is_esf else 0, empresa_id if is_esf else None)
                )
                db.commit()
        else:
            db.execute(
                'INSERT INTO history (year, month, unit, inserted, is_esf, empresa_id) VALUES (?,?,?,?,?,?)',
                (year, month, unit, inserted_fin + inserted_esf, 1 if is_esf else 0, empresa_id if is_esf else None)
            )
            db.commit()

        # Conciliación (solo cuentas de resultado)
        total_odoo = sum(abs(v) for c, v in accounts.items() if not OdooParser.is_balance_account(c))
        total_db_row = db.execute(
            'SELECT SUM(ABS(amount)) FROM financials WHERE year=? AND month=? AND unit=?',
            (year, month, unit)
        ).fetchone()
        total_db = total_db_row[0] or 0
        concilia = {
            'total_odoo': round(total_odoo, 2),
            'total_db': round(total_db, 2),
            'diferencia': round(abs(total_odoo - total_db), 2),
            'ok': abs(total_odoo - total_db) < 0.01
        }

        # LOG TEMPORAL: Mostrar cuentas sin mapear
        if unmapped:
            print("\n" + "="*80)
            print(f"CUENTAS SIN MAPEAR - {year}/{month}/{unit}")
            print("="*80)
            for u in unmapped:
                print(f"  Code: {u['code']:20s} | Name: {u['name']:50s} | Amount: {u['amount']:>15,.2f}")
            print("="*80 + "\n")

        return jsonify({
            'inserted_financials': inserted_fin,
            'inserted_esf': inserted_esf,
            'skipped': skipped,
            'unmapped': unmapped,
            'conciliacion': concilia
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── History ───────────────────────────────────────────────────────────────────


@app.route('/api/mapping/unmapped', methods=['GET'])
def get_unmapped_accounts():
    """
    Retorna cuentas que existen en financials/esf_data pero NO en mapping.
    Útil para detectar cuentas que se auto-mapearon o que faltan.
    """
    db = get_db()

    # Cuentas únicas en financials
    fin_partidas = set(r['partida'] for r in db.execute('SELECT DISTINCT partida FROM financials').fetchall())

    # Cuentas únicas en esf_data
    esf_partidas = set(r['partida'] for r in db.execute('SELECT DISTINCT partida FROM esf_data').fetchall())

    # Cuentas únicas en mapping
    mapped_partidas = set(r['partida'] for r in db.execute('SELECT DISTINCT partida FROM mapping').fetchall())

    # Diferencias
    unmapped_fin = fin_partidas - mapped_partidas
    unmapped_esf = esf_partidas - mapped_partidas

    # Obtener detalles de las partidas sin mapear
    result = {
        'financials_unmapped': sorted(list(unmapped_fin)),
        'esf_unmapped': sorted(list(unmapped_esf)),
        'total_unmapped': len(unmapped_fin) + len(unmapped_esf),
        'total_in_financials': len(fin_partidas),
        'total_in_esf': len(esf_partidas),
        'total_in_mapping': len(mapped_partidas)
    }

    return jsonify(result)



# ── Mapping ───────────────────────────────────────────────────────────────────

@app.route('/api/mapping', methods=['GET'])
def get_mapping():
    db = get_db()
    return jsonify([dict(r) for r in db.execute('SELECT * FROM mapping ORDER BY odoo_code').fetchall()])

@app.route('/api/mapping', methods=['POST'])
@admin_required
def add_mapping():
    d  = request.json
    db = get_db()
    try:
        db.execute(
            'INSERT OR REPLACE INTO mapping (odoo_code, odoo_name, partida, sign, income_type) VALUES (?,?,?,?,?)',
            (d['odoo_code'], d['odoo_name'], d['partida'], d.get('sign', 1), d.get('income_type'))
        )
        db.execute(
            'INSERT INTO mapping_log (action, odoo_code, odoo_name, partida, sign, income_type) VALUES (?,?,?,?,?,?)',
            ('INSERT', d['odoo_code'], d['odoo_name'], d['partida'], d.get('sign', 1), d.get('income_type'))
        )
        # Update or Insert mapping_groups_v2 if group_name is provided
        group_name = d.get('group_name')
        if group_name:
            exist = db.execute('SELECT 1 FROM mapping_groups_v2 WHERE odoo_code = ?', (d['odoo_code'],)).fetchone()
            if exist:
                db.execute(
                    'UPDATE mapping_groups_v2 SET group_name = ? WHERE odoo_code = ?',
                    (group_name, d['odoo_code'])
                )
            else:
                db.execute(
                    'INSERT INTO mapping_groups_v2 (group_name, odoo_code, report_type, display_order) VALUES (?, ?, ?, ?)',
                    (group_name, d['odoo_code'], 'eerr', 100)
                )
        db.commit()
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mapping/grupo', methods=['GET'])
def get_mapping_grupo():
    code = request.args.get('code', '')
    if not code:
        return jsonify({'group_name': None})
    db = get_db()
    row = db.execute('SELECT group_name FROM mapping_groups_v2 WHERE odoo_code = ?', (code,)).fetchone()
    return jsonify({'group_name': row['group_name'] if row else None})

@app.route('/api/mapping/sin-clasificar', methods=['GET'])
def get_mapping_sin_clasificar():
    from engine import EERR_STRUCTURE
    eerr_leaves = set(item[0].lower().strip() for item in EERR_STRUCTURE if not item[1])
    db = get_db()
    rows = db.execute('''
        SELECT m.odoo_code, m.odoo_name, m.partida, m.sign, m.income_type
        FROM mapping m
        LEFT JOIN mapping_groups_v2 mg ON m.odoo_code = mg.odoo_code
        WHERE (m.odoo_code LIKE '4%' OR m.odoo_code LIKE '5%' OR m.odoo_code LIKE '6%')
          AND mg.odoo_code IS NULL
          AND (length(m.odoo_code) - length(replace(m.odoo_code, '.', ''))) = 4
    ''').fetchall()
    
    unclassified = []
    for r in rows:
        partida = r['partida'].lower().strip()
        if partida in eerr_leaves:
            unclassified.append(dict(r))
            
    return jsonify({
        'count': len(unclassified),
        'accounts': unclassified
    })

@app.route('/api/mapping/sin-clasificar-esf', methods=['GET'])
def get_mapping_sin_clasificar_esf():
    from engine import ESF_STRUCTURE_V2
    esf_leaves = set(item[0].lower().strip() for item in ESF_STRUCTURE_V2 if not item[1])
    db = get_db()
    rows = db.execute('''
        SELECT m.odoo_code, m.odoo_name, m.partida, m.sign, m.income_type
        FROM mapping m
        LEFT JOIN mapping_groups_v2 mg ON m.odoo_code = mg.odoo_code
            AND mg.report_type = 'esf'
        WHERE (m.odoo_code LIKE '1%' OR m.odoo_code LIKE '2%' OR m.odoo_code LIKE '3%')
          AND mg.odoo_code IS NULL
          AND (length(m.odoo_code) - length(replace(m.odoo_code, '.', ''))) = 4
    ''').fetchall()
    unclassified = []
    for r in rows:
        partida = r['partida'].lower().strip()
        if partida in esf_leaves:
            unclassified.append(dict(r))
    return jsonify({
        'count': len(unclassified),
        'accounts': unclassified
    })


@app.route('/api/mapping/<code>', methods=['DELETE'])
@admin_required
def delete_mapping(code):
    db  = get_db()
    row = db.execute('SELECT * FROM mapping WHERE odoo_code=?', (code,)).fetchone()
    if row:
        db.execute(
            'INSERT INTO mapping_log (action, odoo_code, odoo_name, partida, sign, income_type) VALUES (?,?,?,?,?,?)',
            ('DELETE', row['odoo_code'], row['odoo_name'], row['partida'], row['sign'], row['income_type'])
        )
    db.execute('DELETE FROM mapping WHERE odoo_code=?', (code,))
    db.commit()
    return jsonify({'ok': True})

@app.route('/api/mapping/log', methods=['GET'])
def mapping_log():
    db = get_db()
    return jsonify([dict(r) for r in db.execute('SELECT * FROM mapping_log ORDER BY id DESC LIMIT 200').fetchall()])

@app.route('/api/mapping/log/<int:lid>/restore', methods=['POST'])
@admin_required
def restore_mapping_log(lid):
    db    = get_db()
    entry = db.execute('SELECT * FROM mapping_log WHERE id=?', (lid,)).fetchone()
    if not entry:                        return jsonify({'error': 'No encontrado'}), 404
    if entry['action'] != 'DELETE':      return jsonify({'error': 'Solo se pueden restaurar eliminaciones'}), 400
    db.execute(
        'INSERT OR IGNORE INTO mapping (odoo_code, odoo_name, partida, sign, income_type) VALUES (?,?,?,?,?)',
        (entry['odoo_code'], entry['odoo_name'], entry['partida'], entry['sign'], entry['income_type'])
    )
    db.commit()
    return jsonify({'ok': True})


# ── Dashboard ─────────────────────────────────────────────────────────────────














# ── EERR ──────────────────────────────────────────────────────────────────────







































# ── Exports ───────────────────────────────────────────────────────────────────

@app.route('/api/export/excel', methods=['GET'])
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
    nombre_emp_dl = _nombre_empresa_display(db_conn, empresa_id) if unit == '' else unit
    suf   = (f'_{unit}' if unit else '_CONSOLIDADO') + ('_DIVISA_REAL' if divisa else '') + (f'_{mf}-{mt}' if mf and mt else '')
    return send_file(path, as_attachment=True, download_name=f'EERR_{nombre_emp_dl}_{year}{suf}.xlsx')


@app.route('/api/export/esf', methods=['GET'])
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
    nombre_emp_esf = _nombre_empresa_display(db_conn_esf, empresa_id)
    suf  = f'_Q{quarter}' if quarter else ''
    return send_file(path, as_attachment=True, download_name=f'ESF_{nombre_emp_esf}_{year}{suf}.xlsx')


@app.route('/api/export/esf-divisa-real', methods=['GET'])
def export_esf_divisa_real():
    from exporters.excel_esf_divisa import ESFDivisaRealExporter
    year = request.args.get('year', str(datetime.now().year))
    empresa_id = request.args.get('empresa_id', type=int)
    exp = ESFDivisaRealExporter(year, empresa_id=empresa_id)
    path = exp.generate()
    db_conn_dr = get_db()
    nombre_emp_dr = _nombre_empresa_display(db_conn_dr, empresa_id)
    return send_file(path, as_attachment=True, download_name=f'ESF_DIVISA_REAL_{nombre_emp_dr}_{year}.xlsx')






@app.route('/api/mapping/reset', methods=['POST'])
@admin_required
def reset_mapping_endpoint():
    """
    Endpoint para ejecutar reset_mapping() desde la UI.
    ⚠️  ADVERTENCIA: Borra y recrea toda la tabla mapping.
    """
    from db import reset_mapping
    result = reset_mapping()
    return jsonify(result)


@app.route('/api/briefing-prompt', methods=['GET'])
@admin_required
def get_briefing_prompt():
    tipo = request.args.get('tipo', '')
    default_flag = request.args.get('default', '0') == '1'
    tipos_validos = {'consolidado', 'unidad_mes', 'anual', 'comparativo_mes', 'comparativo_anual'}
    if tipo not in tipos_validos:
        return jsonify({'error': 'tipo_reporte inválido'}), 400

    if default_flag:
        from db import (
            PROMPT_CONSOLIDADO_DEFAULT, PROMPT_UNIDAD_MES_DEFAULT, PROMPT_ANUAL_DEFAULT,
            PROMPT_COMPARATIVO_MES_DEFAULT, PROMPT_COMPARATIVO_ANUAL_DEFAULT
        )
        fallbacks = {
            'consolidado': PROMPT_CONSOLIDADO_DEFAULT,
            'unidad_mes': PROMPT_UNIDAD_MES_DEFAULT,
            'anual': PROMPT_ANUAL_DEFAULT,
            'comparativo_mes': PROMPT_COMPARATIVO_MES_DEFAULT,
            'comparativo_anual': PROMPT_COMPARATIVO_ANUAL_DEFAULT
        }
        return jsonify({'tipo_reporte': tipo, 'prompt_text': fallbacks.get(tipo, '')})

    db = get_db()
    row = db.execute(
        "SELECT prompt_text FROM briefing_prompts WHERE tipo_reporte = ?", (tipo,)
    ).fetchone()

    if row is None:
        return jsonify({'error': 'prompt no encontrado'}), 404

    return jsonify({'tipo_reporte': tipo, 'prompt_text': row['prompt_text']})


@app.route('/api/briefing-prompt', methods=['POST'])
@admin_required
def save_briefing_prompt():
    data = request.get_json()
    tipo = data.get('tipo_reporte', '')
    texto = data.get('prompt_text', '')

    tipos_validos = {'consolidado', 'unidad_mes', 'anual', 'comparativo_mes', 'comparativo_anual'}
    if tipo not in tipos_validos:
        return jsonify({'error': 'tipo_reporte inválido'}), 400
    if not texto.strip():
        return jsonify({'error': 'prompt_text vacío'}), 400

    db = get_db()
    db.execute("""
        INSERT INTO briefing_prompts (tipo_reporte, prompt_text, updated_at)
        VALUES (?, ?, datetime('now','localtime'))
        ON CONFLICT(tipo_reporte) DO UPDATE SET
            prompt_text = excluded.prompt_text,
            updated_at = excluded.updated_at
    """, (tipo, texto))
    db.commit()

    return jsonify({'status': 'ok', 'tipo_reporte': tipo})


# ── Exportar para IA ──────────────────────────────────────────────────────────

def _nombre_empresa(db, empresa_id):
    row = db.execute('SELECT nombre_corto FROM empresas WHERE id=?', (empresa_id,)).fetchone()
    return row['nombre_corto'] if row else f"Empresa {empresa_id}"


def _nombre_empresa_display(db, empresa_id):
    """Nombre corto para uso en exportables (títulos de hoja, nombres de archivo).
    'Holding' para empresa_id=None (agregado de las 4 empresas); nombre comercial
    sin sufijo legal (' C.A.') para empresas individuales."""
    if empresa_id is None:
        return 'Holding'
    row = db.execute('SELECT nombre_corto FROM empresas WHERE id=?', (empresa_id,)).fetchone()
    nombre = row['nombre_corto'] if row else f"Empresa {empresa_id}"
    if nombre.endswith(' C.A.'):
        nombre = nombre[:-5]
    return nombre.strip()


@app.route('/api/export/ai', methods=['GET', 'POST'])
@admin_required
def export_ai():
    from datetime import datetime as dt
    import io
    from db import (
        PROMPT_CONSOLIDADO_DEFAULT, PROMPT_UNIDAD_MES_DEFAULT, PROMPT_ANUAL_DEFAULT,
        PROMPT_COMPARATIVO_MES_DEFAULT, PROMPT_COMPARATIVO_ANUAL_DEFAULT
    )

    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        year = data.get('year') or request.args.get('year', str(datetime.now().year))
        month = data.get('month') or request.args.get('month', '')
        unit = data.get('unit') or request.args.get('unit', '')
        tipo = data.get('tipo') or request.args.get('tipo', 'eerr')
        prompt_text = data.get('prompt_text')
        empresa_id = data.get('empresa_id') or request.args.get('empresa_id', type=int)
        quarter = data.get('quarter') or request.args.get('quarter', type=int)
    else:
        year = request.args.get('year', str(datetime.now().year))
        month = request.args.get('month', '')
        unit = request.args.get('unit', '')
        tipo = request.args.get('tipo', 'eerr')
        prompt_text = request.args.get('prompt_text')
        empresa_id = request.args.get('empresa_id', type=int)
        quarter = request.args.get('quarter', type=int)

    db = get_db()

    # ── Selección de prompt ────────────────────────────────────────────────────
    if not prompt_text:
        if tipo == 'comparativa':
            tipo_prompt = 'comparativo_anual' if month == '' else 'comparativo_mes'
        else:
            if unit == '':
                tipo_prompt = 'consolidado'
            elif month == '':
                tipo_prompt = 'anual'
            else:
                tipo_prompt = 'unidad_mes'

        row_p = db.execute("SELECT prompt_text FROM briefing_prompts WHERE tipo_reporte = ?", (tipo_prompt,)).fetchone()
        if row_p:
            prompt = row_p['prompt_text']
        else:
            # Fallback a constantes importadas de db.py
            fallbacks = {
                'consolidado': PROMPT_CONSOLIDADO_DEFAULT,
                'unidad_mes': PROMPT_UNIDAD_MES_DEFAULT,
                'anual': PROMPT_ANUAL_DEFAULT,
                'comparativo_mes': PROMPT_COMPARATIVO_MES_DEFAULT,
                'comparativo_anual': PROMPT_COMPARATIVO_ANUAL_DEFAULT
            }
            prompt = fallbacks.get(tipo_prompt, PROMPT_CONSOLIDADO_DEFAULT)
    else:
        prompt = prompt_text

    # ── Construcción del archivo .md ───────────────────────────────────────────
    lines = []
    lines.append(prompt)
    lines.append('')

    # Encabezado
    periodo = f"{month} {year}" if month else f"Año completo {year}"
    alcance = unit if unit else ('Consolidado grupo' if empresa_id is None else _nombre_empresa(db, empresa_id))
    moneda = "USD Paralelo" if 'divisa' in tipo else "USD / Bs"

    lines.append(f"# BRIEFING FINANCIERO — ULTRABIKEX")
    lines.append(f"**Período:** {periodo}")
    lines.append(f"**Alcance:** {alcance}")
    lines.append(f"**Moneda:** {moneda}")
    lines.append(f"**Generado:** {dt.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append('')
    lines.append('---')
    lines.append('')

    # ── EERR ──────────────────────────────────────────────────────────────────
    if tipo in ['eerr', 'completo']:
        lines.append('## ESTADO DE RESULTADOS')
        lines.append('')
        from engine import eerr_completo_v2_ui_adapter
        data = eerr_completo_v2_ui_adapter(db, year, unit, empresa_id=empresa_id)
        rows = data.get('rows', [])

        meses_disponibles = []
        if rows:
            meses_disponibles = [m['month'] for m in rows[0].get('meses', [])]
            if month:
                meses_disponibles = [m for m in meses_disponibles if m == month.upper()]

        header = '| Partida | ' + ' | '.join(meses_disponibles) + ' | ACUM |' if meses_disponibles else '| Partida | ACUM |'
        separator = '|---' * (len(meses_disponibles) + 2) + '|'
        lines.append(header)
        lines.append(separator)

        for row in rows:
            partida = row.get('partida', '')
            prefix = '**' if row.get('bold') else ''
            suffix = '**' if row.get('bold') else ''
            meses_data = {m['month']: m.get('ejecutado', {}).get('valor', 0) for m in row.get('meses', [])}

            if meses_disponibles:
                valores = ' | '.join(f"{meses_data.get(m, 0):,.0f}" for m in meses_disponibles)
                acum = sum(m.get('ejecutado', {}).get('valor', 0) for m in row.get('meses', []))
                lines.append(f"| {prefix}{partida}{suffix} | {valores} | {acum:,.0f} |")
            else:
                acum = sum(m.get('ejecutado', {}).get('valor', 0) for m in row.get('meses', []))
                lines.append(f"| {prefix}{partida}{suffix} | {acum:,.0f} |")

        lines.append('')
        lines.append('---')
        lines.append('')

    # ── EERR DIVISA REAL ─────────────────────────────────────────────────────
    if tipo in ['eerr_divisa', 'completo']:
        lines.append('## ESTADO DE RESULTADOS — DIVISA REAL')
        lines.append('')
        from engine import _calcular_eerr_divisa_real
        data_dr = _calcular_eerr_divisa_real(db, year, unit, empresa_id=empresa_id)
        rows_dr = data_dr.get('rows', [])

        meses_disponibles_dr = []
        if rows_dr:
            meses_disponibles_dr = [m['month'] for m in rows_dr[0].get('meses', [])]
            if month:
                meses_disponibles_dr = [m for m in meses_disponibles_dr if m == month.upper()]

        header_dr = '| Partida | ' + ' | '.join(meses_disponibles_dr) + ' | ACUM |' if meses_disponibles_dr else '| Partida | ACUM |'
        separator_dr = '|---' * (len(meses_disponibles_dr) + 2) + '|'
        lines.append(header_dr)
        lines.append(separator_dr)

        for row in rows_dr:
            partida = row.get('partida', '')
            prefix = '**' if row.get('bold') else ''
            suffix = '**' if row.get('bold') else ''
            meses_data = {m['month']: m.get('ejecutado', {}).get('valor', 0) for m in row.get('meses', [])}

            if meses_disponibles_dr:
                valores = ' | '.join(f"{meses_data.get(m, 0):,.0f}" for m in meses_disponibles_dr)
                acum = sum(m.get('ejecutado', {}).get('valor', 0) for m in row.get('meses', []))
                lines.append(f"| {prefix}{partida}{suffix} | {valores} | {acum:,.0f} |")
            else:
                acum = sum(m.get('ejecutado', {}).get('valor', 0) for m in row.get('meses', []))
                lines.append(f"| {prefix}{partida}{suffix} | {acum:,.0f} |")

        lines.append('')
        lines.append('---')
        lines.append('')

    # ── ESF ───────────────────────────────────────────────────────────────────
    if tipo in ['esf', 'completo']:
        lines.append('## ESTADO DE SITUACIÓN FINANCIERA')
        lines.append('')
        from engine import compute_esf
        result_quarters, quarters_available = compute_esf(db, year, unit, empresa_id=empresa_id)

        for q in quarters_available:
            lines.append(f"### Q{q}")
            totales = result_quarters[q]['totales']
            claves = [
                'ACTIVOS CORRIENTES', 'Total Activos No Corrientes', 'TOTAL ACTIVOS',
                'TOTAL PASIVOS CORRIENTES', 'TOTAL PASIVOS NO CORRIENTES', 'TOTAL PASIVOS',
                'TOTAL PATRIMONIO', 'TOTAL PASIVOS Y PATRIMONIO'
            ]
            lines.append('| Partida | Valor |')
            lines.append('|---|---|')
            for clave in claves:
                val = totales.get(clave, 0)
                lines.append(f"| {clave} | {val:,.0f} |")
            lines.append('')

    # ── ESF DIVISA REAL ─────────────────────────────────────────────────────
    if tipo in ['esf_divisa', 'completo']:
        lines.append('## ESTADO DE SITUACIÓN FINANCIERA — DIVISA REAL')
        lines.append('')
        if not quarter:
            lines.append('_No se especificó trimestre; sección omitida._')
            lines.append('')
        else:
            from engine import calcular_esf_divisa_real
            overrides_rows = db.execute(
                'SELECT odoo_code, valor_override FROM esf_divisa_real_overrides WHERE year=? AND quarter=? AND empresa_id IS ?',
                (year, quarter, empresa_id)
            ).fetchall()
            overrides_flat = {r['odoo_code']: r['valor_override'] for r in overrides_rows}
            result_dr = calcular_esf_divisa_real(year, quarter, overrides=overrides_flat, empresa_id=empresa_id)
            if 'error' in result_dr:
                lines.append(f"_{result_dr['error']}_")
                lines.append('')
            else:
                lines.append(f"**Trimestre:** Q{quarter} | **Tasa paralela fin de mes:** {result_dr['tasa_paralela_fin']}")
                lines.append('')
                lines.append('| Partida | Bs |')
                lines.append('|---|---|')
                for k, v in result_dr['partidas'].items():
                    lines.append(f"| {k} | {v:,.2f} |")
                lines.append(f"| **Saldo Total** | **{result_dr['saldo_total_bs']:,.2f}** |")
                lines.append('')
                usd_txt = f"{result_dr['saldo_total_usd']:,.2f}" if result_dr['saldo_total_usd'] is not None else "N/D"
                lines.append(f"**Saldo Total USD (paralelo):** {usd_txt}")
                lines.append('')
        lines.append('---')
        lines.append('')

    # ── COMPARATIVA POR UNIDAD ────────────────────────────────────────────────
    if tipo == 'comparativa':
        empresa_id_comp = request.args.get('empresa_id', type=int) if request.method == 'GET' else data.get('empresa_id')
        # Ucafe excluida: es venta de café, negocio distinto al resto (retail) — no es comparable, decisión de negocio.
        if empresa_id_comp is not None:
            rows_unidades = db.execute('SELECT nombre FROM unidades WHERE empresa_id=? AND nombre != ?', [empresa_id_comp, 'Ucafe']).fetchall()
            UNIDADES_COMPARABLES = {r[0] for r in rows_unidades}
        else:
            UNIDADES_COMPARABLES = {r[0] for r in db.execute('SELECT nombre FROM unidades WHERE nombre != ?', ['Ucafe']).fetchall()}

        if request.method == 'POST':
            units = data.get('units') or []
        else:
            units = request.args.getlist('units')

        units = [u for u in units if u in UNIDADES_COMPARABLES]
        units = list(dict.fromkeys(units))

        if len(units) < 2:
            return jsonify({'error': 'Selecciona al menos 2 unidades válidas para comparar'}), 400

        lines.append('## COMPARATIVA DE UNIDADES OPERATIVAS')
        lines.append('')
        lines.append('| Unidad | Ingresos | Costos | Gastos Operacionales | Otros | Utilidad Neta | Margen Bruto | Margen Neto |')
        lines.append('|---|---|---|---|---|---|---|---|')

        for u in units:
            data_u = eerr_completo_v2_ui_adapter(db, year, u)
            rows_u = data_u.get('rows', [])

            def valor_partida(nombre_partida):
                for row in rows_u:
                    if row.get('partida', '').strip() == nombre_partida:
                        if month:
                            for m in row.get('meses', []):
                                if m['month'] == month.upper():
                                    return m.get('ejecutado', {}).get('valor', 0)
                            return 0
                        else:
                            return sum(m.get('ejecutado', {}).get('valor', 0) for m in row.get('meses', []))
                return 0

            i = valor_partida('Total Ingresos')
            c = valor_partida('Total Costo de Ventas')
            ub = valor_partida('Utilidad Bruta')
            g = valor_partida('Total Gastos Operacionales')
            un = valor_partida('Utilidad Neta')
            otros = ub - g - un

            mb = (ub / i * 100) if i else 0
            mn = (un / i * 100) if i else 0

            lines.append(f"| {u} | {i:,.2f} | {c:,.2f} | {g:,.2f} | {otros:,.2f} | {un:,.2f} | {mb:.1f}% | {mn:.1f}% |")

        lines.append('')
        lines.append('---')
        lines.append('')

    # ── Entrega ────────────────────────────────────────────────────────────────
    contenido = '\n'.join(lines)
    nombre = f"ultrax_briefing_{alcance.replace(' ','_')}_{periodo.replace(' ','_')}.md"

    from flask import Response
    return Response(
        contenido,
        mimetype='text/markdown',
        headers={'Content-Disposition': f'attachment; filename="{nombre}"'}
    )


# ── Shutdown ──────────────────────────────────────────────────────────────────

@app.route('/api/shutdown', methods=['POST'])
@admin_required
def shutdown():
    import threading, time
    def _stop():
        time.sleep(0.3)
        os._exit(0)
    threading.Thread(target=_stop, daemon=True).start()
    return jsonify({'ok': True})


if __name__ == '__main__':
    init_db()
    migrate_db()  # seguro de llamar siempre: es idempotente
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
