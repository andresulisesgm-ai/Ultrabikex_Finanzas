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
from blueprints.exportables import exportables_bp
from blueprints.briefing import briefing_bp
from blueprints.mapeo import mapeo_bp
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
app.register_blueprint(exportables_bp)
app.register_blueprint(briefing_bp)
app.register_blueprint(mapeo_bp)
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
