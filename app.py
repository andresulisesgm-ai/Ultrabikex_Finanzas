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

app = Flask(__name__)
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
ESF_PLUG_VARIACION_UMBRAL = 0.25

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

UNITS  = ['Rodeo', 'PiedeMonte', 'Terracota', 'Ucafe', 'Barinas', 'Naranjos']
MONTHS = ['ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEPT','OCT','NOV','DIC']

# ── %Vtas segmentado para Costo de Ventas / Utilidad Bruta por segmento ──
# Estas partidas dividen %Vtas contra el ingreso de su propio segmento
# (Mercancia+Taller, Servicios o Eventos) en vez del Total Ingresos general.
# Spec confirmado contra formulas de ESF_EJEMPLO.xlsx, hoja "EERR RODEO".
PARTIDAS_DIVISOR_SEGMENTADO = {
    'Subtotal Costo de Ventas por Mercancia': 'mercancia_taller',
    'Costos de venta por mercancia': 'mercancia_taller',
    'Utilidad Bruta por Venta de Mercancia y Taller': 'mercancia_taller',
    'Subtotal Costo de Ventas por Servicios': 'servicios',
    'Costo de venta por servicio del café': 'servicios',
    'Utilidad Bruta por Servicios': 'servicios',
    'Subtotal Costo de Ventas por Eventos': 'eventos',
    'Costo de ventas por eventos': 'eventos',
    'Utilidad Bruta por Eventos': 'eventos',
}

# Claves de subtotales_por_mes[m] (ya calculadas via EERR_STRUCTURE) por segmento.
SUBTOTAL_INGRESO_KEYS_POR_SEGMENTO = {
    'mercancia_taller': ['Subtotal Ingresos por Venta de Mercancia', 'Subtotal Ingresos por Taller'],
    'servicios': ['Subtotal Ingresos por Servicios'],
    'eventos': ['Subtotal Ingresos por Eventos'],
}

# Partidas hoja por segmento (mismo universo que arma EERR_STRUCTURE para
# los subtotales de arriba), usadas contra datos crudos: by_budget y by_prev_raw.
SEGMENTOS_INGRESO_PCT_VTAS = {
    'mercancia_taller': [
        'Ingresos por venta de mercancias',
        'Devoluciones sobre ventas',
        'Descuentos sobre ventas',
        'Ingresos por taller',
    ],
    'servicios': [
        'Ingresos por servicios del café',
        'Ingresos por zona FIT',
        'Ingresos por fletes',
        'Ingresos por otros servicios',
    ],
    'eventos': [
        'Ingresos por eventos',
    ],
}


def divisor_ejec(partida_name, subtotales_mes, default, by_partida=None, m=None, ing_p=None):
    """Divisor de %Vtas ejecutado (y base de acumulado/promedio) para un mes."""
    if partida_name == 'Total Ingresos' and by_partida is not None and ing_p is not None:
        return sum(by_partida.get(p, {}).get(m, 0) for p in ing_p)
    segmento = PARTIDAS_DIVISOR_SEGMENTADO.get(partida_name)
    if segmento is None:
        return default
    return sum(subtotales_mes.get(k, 0) for k in SUBTOTAL_INGRESO_KEYS_POR_SEGMENTO[segmento])


def divisor_ppto_mes(partida_name, by_budget, m, default, ing_p=None):
    """Divisor de %Vtas de presupuesto para un mes."""
    if partida_name == 'Total Ingresos' and ing_p is not None:
        return sum(by_budget.get(p, {}).get(m, 0) for p in ing_p)
    segmento = PARTIDAS_DIVISOR_SEGMENTADO.get(partida_name)
    if segmento is None:
        return default
    return sum(by_budget.get(p, {}).get(m, 0) for p in SEGMENTOS_INGRESO_PCT_VTAS[segmento])


def divisor_prev(partida_name, by_prev_raw, default, ing_p=None):
    """Divisor de %Vtas para la columna de año anterior."""
    if partida_name == 'Total Ingresos' and ing_p is not None:
        return sum(by_prev_raw.get(p, 0) for p in ing_p)
    segmento = PARTIDAS_DIVISOR_SEGMENTADO.get(partida_name)
    if segmento is None:
        return default
    return sum(by_prev_raw.get(p, 0) for p in SEGMENTOS_INGRESO_PCT_VTAS[segmento])


# ── %Gastos: rango de partidas donde aplica ──────────────────────────────
# Desde 'Total Gastos Operacionales' hasta 'Total Gastos Operacionales y No
# Operacionales' (ambos inclusive), excluyendo cualquier línea de Utilidad
# (Utilidad antes/después de Comisiones, EBIT, EBITDA quedan intercaladas
# en ese rango). ISLR se agrega aparte: confirmado por la cliente, aunque
# está fuera del rango contiguo.
PARTIDAS_PCT_GASTOS_EXTRA = {'ISLR'}


def calcular_muestra_pct_gastos(effective):
    """Devuelve {partida_name: bool} indicando si esa fila debe mostrar %Gastos."""
    resultado = {}
    en_rango = False
    for node in effective:
        nombre = node['partida_name']
        if nombre == 'Total Gastos Operacionales':
            en_rango = True
        muestra = (en_rango and not nombre.startswith('Utilidad')) or nombre in PARTIDAS_PCT_GASTOS_EXTRA
        resultado[nombre] = muestra
        if nombre == 'Total Gastos Operacionales y No Operacionales':
            en_rango = False
    return resultado


# Categorías de gasto: cada una agrupa partidas cuyo nombre contiene alguna palabra clave.
GASTO_CATS = {
    'Administración':   ['servicios públicos','telefonía','alquiler','condominio','outsorsing','oficina','limpieza','alimentos','honorarios','retenciones','mantenimiento','viáticos admin','seguro','impuesto','depreciación','deterioro','amortización','comisiones bancarias','IGTF','intereses'],
    'Rec. Humanos':     ['sueldos','salarios','horas extras','complemento de sueldos','bono de alimentación','vacaciones','utilidades','prestaciones','aporte patronal','guardería','HCM','salud','uniformes','fiestas','capacitación','transporte del personal'],
    'Comercialización': ['viáticos comerciales','fletes','almacenaje','importación','comisiones empleados','gasolina','garantías','suscripciones'],
    'Mercadeo':         ['redes sociales','medios publicitarios','impresiones','decoración','muestras','campañas'],
    'TI+I':             ['dominio','servidores','software tecnológico'],
    'No Operacionales': ['Faltante','Pérdida','Multas','deterioro de inventarios'],
}


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

def get_clasificacion(db):
    ing = set(r['partida'] for r in db.execute("SELECT DISTINCT partida FROM mapping WHERE odoo_code LIKE '4.%'").fetchall())
    cos = set(r['partida'] for r in db.execute("SELECT DISTINCT partida FROM mapping WHERE odoo_code LIKE '5.%'").fetchall())
    gas = set(r['partida'] for r in db.execute("SELECT DISTINCT partida FROM mapping WHERE odoo_code LIKE '6.%'").fetchall())
    return ing, cos, gas

def get_clasificacion_by_type(db):
    """Retorna partidas agrupadas por income_type para el EERR detallado."""
    rows = db.execute(
        "SELECT partida, income_type, odoo_code FROM mapping WHERE income_type IS NOT NULL"
    ).fetchall()
    by_type = {'mercancia_taller': {'ing': set(), 'cos': set()},
               'servicios':        {'ing': set(), 'cos': set()},
               'eventos':          {'ing': set(), 'cos': set()}}
    for r in rows:
        t = r['income_type']
        if t not in by_type:
            continue
        code = r['odoo_code']
        if code.startswith('4.'):
            by_type[t]['ing'].add(r['partida'])
        elif code.startswith('5.'):
            by_type[t]['cos'].add(r['partida'])
    return by_type


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
    if is_esf:
        unit = 'CONSOLIDADO'

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
                    'SELECT COUNT(*) FROM esf_data WHERE year=? AND quarter=? AND unit=?',
                    (year, quarter_check, 'CONSOLIDADO')
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
                'DELETE FROM esf_data WHERE year=? AND quarter=? AND unit=?',
                (year, quarter, unit)
            )
            db.execute(
                'DELETE FROM financials_detail WHERE year=? AND quarter=? AND unit=? AND report_type=\'esf\'',
                (year, quarter, unit)
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
                       (year, month, unit, odoo_code, odoo_name, partida, amount_orig, amount_sign, report_type, quarter)
                       VALUES (?,?,?,?,?,?,?,?,?,?)
                       ON CONFLICT(year, month, unit, odoo_code) 
                       DO UPDATE SET amount_orig=excluded.amount_orig, 
                                    amount_sign=excluded.amount_sign,
                                    partida=excluded.partida''',
                    (year, month, unit, code, parser.names.get(code, ''),
                     m['partida'], amount, signed_amount, report_type, quarter)
                )

                if is_balance or is_esf:
                    # Cuentas 1.x / 2.x / 3.x → esf_data (snapshot trimestral)
                    db.execute(
                        '''INSERT INTO esf_data (year, quarter, unit, partida, amount) VALUES (?,?,?,?,?)
                           ON CONFLICT(year, quarter, unit, partida) DO UPDATE SET amount=excluded.amount''',
                        (year, quarter, unit, m['partida'], signed_amount)
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
                    'INSERT INTO history (year, month, unit, inserted, is_esf) VALUES (?,?,?,?,?)',
                    (year, month, unit, inserted_fin + inserted_esf, 1 if is_esf else 0)
                )
                new_id = new_entry.lastrowid
                db.execute(
                    'UPDATE history SET superseded_by=?, superseded_at=datetime(\'now\',\'localtime\') WHERE id=?',
                    (new_id, prev['id'])
                )
                db.commit()
            else:
                db.execute(
                    'INSERT INTO history (year, month, unit, inserted, is_esf) VALUES (?,?,?,?,?)',
                    (year, month, unit, inserted_fin + inserted_esf, 1 if is_esf else 0)
                )
                db.commit()
        else:
            db.execute(
                'INSERT INTO history (year, month, unit, inserted, is_esf) VALUES (?,?,?,?,?)',
                (year, month, unit, inserted_fin + inserted_esf, 1 if is_esf else 0)
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

@app.route('/api/history', methods=['GET'])
def get_history():
    db = get_db()
    return jsonify([dict(r) for r in db.execute('SELECT * FROM history ORDER BY id DESC').fetchall()])


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

@app.route('/api/history/<int:hid>/revert', methods=['POST'])
@admin_required
def revert_history(hid):
    db = get_db()
    h  = db.execute('SELECT * FROM history WHERE id=?', (hid,)).fetchone()
    if not h:         return jsonify({'error': 'No encontrado'}), 404
    if h['reverted']: return jsonify({'error': 'Ya revertida'}), 400
    if h['is_esf']:
        quarter = MONTH_TO_QUARTER.get(h['month'], 1)
        db.execute('DELETE FROM esf_data WHERE year=? AND quarter=? AND unit=?', (h['year'], quarter, h['unit']))
        db.execute('DELETE FROM financials_detail WHERE year=? AND quarter=? AND unit=? AND report_type=\'esf\'', (h['year'], quarter, h['unit']))
    else:
        db.execute('DELETE FROM financials WHERE year=? AND month=? AND unit=?', (h['year'], h['month'], h['unit']))
    db.execute('UPDATE history SET reverted=1 WHERE id=?', (hid,))
    db.commit()
    return jsonify({'ok': True})


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

@app.route('/api/eerr/grupos', methods=['GET'])
def get_eerr_grupos():
    from engine import EERR_STRUCTURE
    grupos = []
    for item in EERR_STRUCTURE:
        name = item[0]
        level = item[5] if len(item) > 5 else (0 if item[1] else 3)
        if level in (1, 2, 3):
            clean = name
            if level == 1:
                if clean.startswith("Subtotal "):
                    clean = clean[len("Subtotal "):]
                label = clean
            elif level == 2:
                if clean.startswith("Gastos de "):
                    clean = clean[len("Gastos de "):]
                elif clean.startswith("Ingresos por "):
                    clean = clean[len("Ingresos por "):]
                elif clean.startswith("Costos de "):
                    clean = clean[len("Costos de "):]
                clean = clean[0].upper() + clean[1:] if clean else clean
                label = "  → " + clean
            elif level == 3:
                if clean.startswith("Gastos de "):
                    clean = clean[len("Gastos de "):]
                elif clean.startswith("Ingresos por "):
                    clean = clean[len("Ingresos por "):]
                elif clean.startswith("Costos de "):
                    clean = clean[len("Costos de "):]
                clean = clean[0].upper() + clean[1:] if clean else clean
                label = "    → " + clean
            else:
                label = clean
            grupos.append({
                "nombre": name,
                "nivel": level,
                "label": label
            })
    return jsonify(grupos)

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

@app.route('/api/eerr_nodes/overrides', methods=['GET'])
def get_eerr_nodes_overrides():
    from engine import EERR_STRUCTURE, build_effective_structure
    db = get_db()
    rows = db.execute('SELECT partida_name, target_subtotal FROM eerr_nodes').fetchall()
    overrides_list = [dict(r) for r in rows]
    
    effective = build_effective_structure(EERR_STRUCTURE, db_overrides=[])
    movable_partidas = []
    for node in effective:
        if node['movible'] == 'libre' and not node['is_header']:
            movable_partidas.append({
                'partida_name': node['partida_name'],
                'original_subtotal': node['parent_name']
            })
            
    return jsonify({
        'movable_partidas': movable_partidas,
        'overrides': overrides_list
    })

@app.route('/api/eerr_nodes/overrides', methods=['POST'])
@admin_required
def save_eerr_nodes_overrides():
    d = request.json
    partida_name = d.get('partida_name')
    target_subtotal = d.get('target_subtotal')
    if not partida_name or not target_subtotal:
        return jsonify({'error': 'Faltan parámetros'}), 400
    db = get_db()
    if target_subtotal == 'original':
        db.execute('DELETE FROM eerr_nodes WHERE partida_name = ?', (partida_name,))
    else:
        exist = db.execute('SELECT 1 FROM eerr_nodes WHERE partida_name = ?', (partida_name,)).fetchone()
        if exist:
            db.execute(
                'UPDATE eerr_nodes SET target_subtotal = ? WHERE partida_name = ?',
                (target_subtotal, partida_name)
            )
        else:
            db.execute(
                'INSERT INTO eerr_nodes (partida_name, target_subtotal, nombre, nivel, tipo) VALUES (?, ?, ?, 0, "hoja")',
                (partida_name, target_subtotal, partida_name)
            )
    db.commit()
    return jsonify({'ok': True})

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

@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', 'TODAS')
    empresa_id = request.args.get('empresa_id', type=int) or None
    db   = get_db()
    ing_p, cos_p, gas_p = get_clasificacion(db)

    # 1. Obtener los datos del EERR
    eerr_unit_param = '' if unit == 'TODAS' else unit
    eerr_data = eerr_completo_v2_ui_adapter(year, eerr_unit_param, empresa_id=empresa_id)

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

    # 2. Desglose por unidad (por_unidad)
    por_unidad = []
    for u in (UNITS if (empresa_id is None or empresa_id == 2) else []):
        eerr_u = eerr_completo_v2_ui_adapter(year, u)
        
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
    loaded = db.execute(
        'SELECT DISTINCT unit, month FROM financials WHERE year=? ORDER BY unit, month', (year,)
    ).fetchall()

    # 8. Indicadores Avanzados pasando ingresos y utilidad neta calculados
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


@app.route('/api/empresas', methods=['GET'])
def get_empresas():
    """
    Lista las empresas legales del Holding (tabla empresas). Usado para poblar
    dinámicamente el selector de empresa en el sidebar.
    """
    db = get_db()
    rows = db.execute('SELECT id, nombre_corto, nombre_legal, color FROM empresas ORDER BY id').fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/trazabilidad')
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

@app.route('/api/dashboard/config', methods=['GET'])
@login_required
def get_dashboard_config():
    import json
    username = session.get('username')
    db = get_db()
    row = db.execute('SELECT config_json FROM dashboard_config WHERE username = ?', [username]).fetchone()
    if row:
        return jsonify(json.loads(row['config_json']))
    return jsonify(DEFAULT_DASHBOARD_CONFIG)

@app.route('/api/dashboard/config', methods=['POST'])
@login_required
def save_dashboard_config():
    import json
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



# ── Detalle de gasto (drill-down de gráficos interactivos) ──────────────────────

@app.route('/api/gasto/detalle', methods=['GET'])
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


# ── Detalle genérico de gráficos (drill-down universal) ──────────────────────

@app.route('/api/grafico/detalle', methods=['GET'])
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

    uc = '' if (not unit or unit == 'TODAS') else "AND unit=?"
    uc_params = [] if (not unit or unit == 'TODAS') else [unit]
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
            for u in UNITS:
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


# ── EERR ──────────────────────────────────────────────────────────────────────

@app.route('/api/eerr', methods=['GET'])
def eerr():
    year  = request.args.get('year', str(datetime.now().year))
    unit  = request.args.get('unit', '')
    month = request.args.get('month', '')
    db    = get_db()
    uc    = "AND unit=?" if unit else ''
    mc    = "AND month=?" if month else ''
    params = [year] + ([unit] if unit else []) + ([month] if month else [])

    rows = db.execute(
        f'SELECT partida, SUM(amount) total FROM financials WHERE year=? {uc} {mc} GROUP BY partida',
        params
    ).fetchall()
    data = {r['partida']: r['total'] for r in rows}

    ing_codes = set(r['partida'] for r in db.execute("SELECT DISTINCT partida FROM mapping WHERE odoo_code LIKE '4.%'").fetchall())
    cos_codes = set(r['partida'] for r in db.execute("SELECT DISTINCT partida FROM mapping WHERE odoo_code LIKE '5.%'").fetchall())
    gas_codes = set(r['partida'] for r in db.execute("SELECT DISTINCT partida FROM mapping WHERE odoo_code LIKE '6.%'").fetchall())

    def total(codes): return sum(data.get(p, 0) for p in codes)
    tI = total(ing_codes); tC = total(cos_codes); tG = total(gas_codes)
    ub = tI - tC; un = tI - tC - tG

    detail_ing = {p: data.get(p, 0) for p in ing_codes if data.get(p, 0)}
    detail_cos = {p: data.get(p, 0) for p in cos_codes if data.get(p, 0)}
    detail_gas = {p: data.get(p, 0) for p in gas_codes if data.get(p, 0)}

    return jsonify({
        'ingresos': tI, 'costos': tC, 'gastos': tG,
        'utilidad_bruta': ub, 'utilidad_neta': un,
        'margen_bruto': round(ub / tI * 100, 1) if tI else 0,
        'margen_neto':  round(un / tI * 100, 1) if tI else 0,
        'detail_ing': detail_ing, 'detail_cos': detail_cos, 'detail_gas': detail_gas
    })


@app.route('/api/eerr/detalle', methods=['GET'])
def eerr_detalle():
    """
    EERR con desglose por tipo de ingreso (mercancia_taller, servicios, eventos),
    columna ACUM EJEC y %VAR mes a mes.
    Parámetros: year, unit (opcional), month_from, month_to (opcionales para filtrar rango)
    """
    year       = request.args.get('year', str(datetime.now().year))
    unit       = request.args.get('unit', '')
    month_from = request.args.get('month_from', '')
    month_to   = request.args.get('month_to', '')
    db         = get_db()

    # Determinar meses activos
    if month_from and month_to and month_from in MONTHS and month_to in MONTHS:
        fi = MONTHS.index(month_from); ti = MONTHS.index(month_to)
        active_months = MONTHS[fi:ti+1] if fi <= ti else MONTHS[fi:] + MONTHS[:ti+1]
    else:
        active_months = MONTHS

    uc = "AND unit=?" if unit else ''
    ph_m = ','.join('?' * len(active_months))
    params = [year] + ([unit] if unit else []) + active_months

    # Totales por partida y mes
    rows = db.execute(
        f'''SELECT partida, month, SUM(amount) amount
            FROM financials
            WHERE year=? {uc} AND month IN ({ph_m})
            GROUP BY partida, month''',
        params
    ).fetchall()

    # Estructura: {partida: {month: amount}}
    by_partida = {}
    for r in rows:
        by_partida.setdefault(r['partida'], {})[r['month']] = r['amount']

    by_type = get_clasificacion_by_type(db)
    ing_p, cos_p, gas_p = get_clasificacion(db)

    def sum_type(type_key, flow):
        """Suma por tipo de ingreso/costo para un tipo y flujo ('ing'|'cos')."""
        partidas = by_type.get(type_key, {}).get(flow, set())
        result   = {}
        for m in active_months:
            result[m] = sum(by_partida.get(p, {}).get(m, 0) for p in partidas)
        return result

    def sum_partidas(partidas):
        result = {}
        for m in active_months:
            result[m] = sum(by_partida.get(p, {}).get(m, 0) for p in partidas)
        return result

    def acum(monthly_dict):
        return sum(monthly_dict.values())

    def var_pct(monthly_dict):
        """Lista de variaciones mes a mes."""
        vals = [monthly_dict.get(m, 0) for m in active_months]
        result = []
        for i, v in enumerate(vals):
            if i == 0 or vals[i-1] == 0:
                result.append(None)
            else:
                result.append(round((v - vals[i-1]) / abs(vals[i-1]) * 100, 1))
        return result

    # Ingresos por tipo
    ing_mt  = sum_type('mercancia_taller', 'ing')
    ing_svc = sum_type('servicios', 'ing')
    ing_evt = sum_type('eventos', 'ing')
    ing_tot = sum_partidas(ing_p)

    # Costos por tipo
    cos_mt  = sum_type('mercancia_taller', 'cos')
    cos_svc = sum_type('servicios', 'cos')
    cos_evt = sum_type('eventos', 'cos')
    cos_tot = sum_partidas(cos_p)

    # Utilidad bruta por tipo
    def diff_monthly(a, b):
        return {m: a.get(m, 0) - b.get(m, 0) for m in active_months}

    ub_mt  = diff_monthly(ing_mt,  cos_mt)
    ub_svc = diff_monthly(ing_svc, cos_svc)
    ub_evt = diff_monthly(ing_evt, cos_evt)
    ub_tot = diff_monthly(ing_tot, cos_tot)

    gas_tot = sum_partidas(gas_p)
    un_tot  = {m: ing_tot.get(m, 0) - cos_tot.get(m, 0) - gas_tot.get(m, 0) for m in active_months}

    def build_row(label, monthly):
        return {
            'partida': label,
            'meses':   {m: round(monthly.get(m, 0), 2) for m in active_months},
            'acum':    round(acum(monthly), 2),
            'var_pct': var_pct(monthly)
        }

    # Detalle de gastos por partida con ACUM y %VAR
    gas_detail = []
    for p in sorted(gas_p):
        monthly = {m: by_partida.get(p, {}).get(m, 0) for m in active_months}
        if acum(monthly) != 0:
            gas_detail.append(build_row(p, monthly))

    return jsonify({
        'year': year, 'unit': unit, 'months': active_months,
        'ingresos': {
            'total':           build_row('Total Ingresos', ing_tot),
            'mercancia_taller':build_row('Mercancía y Taller', ing_mt),
            'servicios':       build_row('Servicios', ing_svc),
            'eventos':         build_row('Eventos', ing_evt),
        },
        'costos': {
            'total':           build_row('Total Costos', cos_tot),
            'mercancia_taller':build_row('Costo Mercancía y Taller', cos_mt),
            'servicios':       build_row('Costo Servicios', cos_svc),
            'eventos':         build_row('Costo Eventos', cos_evt),
        },
        'utilidad_bruta': {
            'total':           build_row('Utilidad Bruta', ub_tot),
            'mercancia_taller':build_row('UB Mercancía y Taller', ub_mt),
            'servicios':       build_row('UB Servicios', ub_svc),
            'eventos':         build_row('UB Eventos', ub_evt),
        },
        'gastos': {
            'total':  build_row('Total Gastos', gas_tot),
            'detalle':gas_detail,
        },
        'utilidad_neta': build_row('Utilidad Neta', un_tot),
    })


def eerr_completo_v2_ui_adapter(year, unit, empresa_id=None):
    from engine import EERR_STRUCTURE, SUBTOTAL_EXCLUSIONS
    db   = get_db()

    year_prev = str(int(year) - 1)
    if unit:
        uc = "AND unit=?"
        uc_params = [unit]
    elif empresa_id:
        unidades_rows = db.execute('SELECT nombre FROM unidades WHERE empresa_id=?', [empresa_id]).fetchall()
        unidades_list = [r['nombre'] for r in unidades_rows]
        if unidades_list:
            placeholders = ','.join(['?'] * len(unidades_list))
            uc = f"AND unit IN ({placeholders})"
            uc_params = unidades_list
        else:
            uc = "AND unit=?"
            uc_params = ['__EMPRESA_SIN_UNIDADES__']
    else:
        uc = ''
        uc_params = []

    MONTH_TYPES = {
        'ENE': 'A',
        'FEB': 'B',
        'MAR': 'C',
        'ABR': 'B',
        'MAY': 'B',
        'JUN': 'D',
        'JUL': 'B',
        'AGO': 'B',
        'SEPT': 'C',
        'OCT': 'B',
        'NOV': 'B',
        'DIC': 'E',
    }

    # 1. Clasificación
    ing_p, cos_p, gas_p = get_clasificacion(db)

    # 2. Obtener grupos de presentación de mapping_groups_v2
    groups_v2, _ = get_grouped_partidas_v2(db, 'eerr')

    # 3. Leer datos año actual por partida y mes
    rows_curr = db.execute(
        f'''SELECT partida, month, SUM(amount) amount FROM financials
            WHERE year=? {uc} GROUP BY partida, month''',
        [year] + uc_params
    ).fetchall()

    by_partida = {}
    for r in rows_curr:
        by_partida.setdefault(r['partida'], {})[r['month']] = r['amount']

    # Leer datos año anterior (total anual por partida)
    rows_prev = db.execute(
        f'''SELECT partida, SUM(amount) amount FROM financials
            WHERE year=? {uc} GROUP BY partida''',
        [year_prev] + uc_params
    ).fetchall()
    by_prev_raw = {r['partida']: r['amount'] for r in rows_prev}

    # Leer presupuesto por partida y mes
    rows_budget = db.execute(
        f'''SELECT partida, month, SUM(amount) amount FROM budget
            WHERE year=? {uc} GROUP BY partida, month''',
        [year] + uc_params
    ).fetchall()
    by_budget = {}
    for r in rows_budget:
        by_budget.setdefault(r['partida'], {})[r['month']] = r['amount']

    import unicodedata
    def norm(s):
        if not s: return ''
        s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
        return s.lower().strip()

    def resolve_leaf_value(partida_name, month, data_dict):
        if partida_name in groups_v2:
            return sum(data_dict.get(p, {}).get(month, 0) for p in groups_v2[partida_name])
        val = data_dict.get(partida_name, {}).get(month, 0)
        if val == 0:
            pn_norm = norm(partida_name)
            for k, v in data_dict.items():
                if norm(k) == pn_norm:
                    return v.get(month, 0)
        return val

    def resolve_leaf_value_prev(partida_name, data_dict):
        if partida_name in groups_v2:
            return sum(data_dict.get(p, 0) for p in groups_v2[partida_name])
        val = data_dict.get(partida_name, 0)
        if val == 0:
            pn_norm = norm(partida_name)
            for k, v in data_dict.items():
                if norm(k) == pn_norm:
                    return v
        return val

    from engine import build_effective_structure
    db_overrides = db.execute('SELECT partida_name, target_subtotal FROM eerr_nodes').fetchall()
    effective = build_effective_structure(EERR_STRUCTURE, db_overrides=db_overrides)
    muestra_pct_gastos_map = calcular_muestra_pct_gastos(effective)
    structure_with_levels = [(node['partida_name'], node['is_header'], node['level']) for node in effective]

    # Pre-calcular subtotales para todos los meses
    subtotales_por_mes = {}
    for m in MONTHS:
        subtotales_por_mes[m] = {}
        # Primero popular nodos hoja
        for name, is_header, level in structure_with_levels:
            if not is_header:
                subtotales_por_mes[m][name] = resolve_leaf_value(name, m, by_partida)

        # Luego calcular subtotales jerárquicos de forma recursiva/bottom-up
        for i, (name, is_header, level) in enumerate(structure_with_levels):
            if is_header:
                total = 0
                j = i + 1
                while j < len(structure_with_levels):
                    c_name, c_is_header, c_level = structure_with_levels[j]
                    if c_level <= level:
                        break
                    if not c_is_header:
                        # Excluir cuentas que se duplicarían
                        if c_name in SUBTOTAL_EXCLUSIONS.get(name, []):
                            pass
                        else:
                            total += subtotales_por_mes[m].get(c_name, 0)
                    j += 1
                subtotales_por_mes[m][name] = total
                if name == 'Subtotal Gastos de Comercialización y Logistica':
                    subtotales_por_mes[m][name] += (
                        subtotales_por_mes[m].get('Gastos de comisiones empleados', 0)
                        + subtotales_por_mes[m].get('Gastos de comisiones por venta de personal externo', 0)
                    )

    # Definición de partidas operativas para Total Ingresos
    op_ing_partidas = ing_p - {
        'Ingresos por alquileres',
        'Ingresos por intereses',
        'Ingresos por comisiones',
        'Ingresos por servicios administrativos',
        'Sobrante en ventas',
        'Sobrante de inventarios',
        'Ganancia en venta de activos',
        'Ganancia por tasa cambiaria',
        'Ganancia por diferencias en pagos'
    }

    valores_calculados_por_mes = {}
    ingresos_ejec_mes = {}
    gastos_ejec_mes = {}
    ingresos_ppto_mes = {}
    gastos_ppto_mes = {}

    for m in MONTHS:
        ingresos_operativos = sum(by_partida.get(p, {}).get(m, 0) for p in op_ing_partidas)
        otros_ing = subtotales_por_mes[m].get('Otros Ingresos no Operacionales', 0)
        costo_ventas = sum(by_partida.get(p, {}).get(m, 0) for p in cos_p)
        utilidad_bruta = ingresos_operativos - costo_ventas

        gastos_operacionales = 0
        for nombre in ['Subtotal Gastos de Administración',
                       'Subtotal Gastos de Recursos Humanos',
                       'Subtotal Gastos de Comercialización y Logistica',
                       'Subtotal Gastos de Mercadeo',
                       'Gastos de TI+I']:
            gastos_operacionales += subtotales_por_mes[m].get(nombre, 0)

        comisiones = 0
        for nombre in ['Gastos de comisiones empleados',
                       'Gastos de comisiones empleados del taller',
                       'Gastos de comisiones por venta de personal externo']:
            comisiones += subtotales_por_mes[m].get(nombre, 0)

        utilidad_despues_comisiones = utilidad_bruta - gastos_operacionales
        utilidad_antes_comisiones = utilidad_despues_comisiones + comisiones

        otros_gastos = subtotales_por_mes[m].get('Otros Gastos no Operacionales', 0)
        gastos_impuestos = subtotales_por_mes[m].get('Gastos de impuestos, tasas y contribuciones', 0)
        gastos_intereses = subtotales_por_mes[m].get('Gastos de intereses sobre préstamos', 0)
        depreciaciones = subtotales_por_mes[m].get('Depreciaciones, deterioro y Amortización', 0)

        ebit = utilidad_bruta - gastos_operacionales + gastos_intereses + gastos_impuestos
        ebitda = ebit + depreciaciones

        utilidad_neta = utilidad_despues_comisiones + otros_ing - otros_gastos
        islr = subtotales_por_mes[m].get('ISLR', 0)
        utilidad_neta_despues_islr = utilidad_neta - islr

        totales_mes = {
            'Total Ingresos Operativos': ingresos_operativos,
            'Otros Ingresos no Operacionales': otros_ing,
            'Total Ingresos': ingresos_operativos,
            'Total Costo de Ventas': costo_ventas,
            'Utilidad Bruta': utilidad_bruta,
            'Total Gastos Operacionales': gastos_operacionales,
            'Utilidad antes de Comisiones por Ventas': utilidad_antes_comisiones,
            'Utilidad después de Comisiones por Ventas': utilidad_despues_comisiones,
            'Otros Gastos no Operacionales': otros_gastos,
            'Total Gastos Operacionales y No Operacionales': gastos_operacionales + otros_gastos,
            'Utilidad antes de Intereses e Impuestos (EBIT)': ebit,
            'Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA)': ebitda,
            'Utilidad Neta': utilidad_neta,
            'ISLR': islr,
            'Utilidad Neta despues de ISLR': utilidad_neta_despues_islr,
            'Utilidad Bruta por Venta de Mercancia y Taller': (
                subtotales_por_mes[m].get('Subtotal Ingresos por Venta de Mercancia', 0)
                + subtotales_por_mes[m].get('Subtotal Ingresos por Taller', 0)
                - subtotales_por_mes[m].get('Subtotal Costo de Ventas por Mercancia', 0)
            ),
            'Utilidad Bruta por Servicios': (
                subtotales_por_mes[m].get('Subtotal Ingresos por Servicios', 0)
                - subtotales_por_mes[m].get('Subtotal Costo de Ventas por Servicios', 0)
            ),
            'Utilidad Bruta por Eventos': (
                subtotales_por_mes[m].get('Subtotal Ingresos por Eventos', 0)
                - subtotales_por_mes[m].get('Subtotal Costo de Ventas por Eventos', 0)
            )
        }

        valores_calculados_por_mes[m] = {**subtotales_por_mes[m], **totales_mes}

        ingresos_ejec_mes[m] = ingresos_operativos
        gastos_ejec_mes[m] = gastos_operacionales + otros_gastos
        ingresos_ppto_mes[m] = sum(by_budget.get(p, {}).get(m, 0) for p in op_ing_partidas)
        gastos_ppto_mes[m] = sum(by_budget.get(p, {}).get(m, 0) for p in gas_p)

    ingresos_prev = sum(by_prev_raw.get(p, 0) for p in op_ing_partidas)
    gastos_prev = sum(by_prev_raw.get(p, 0) for p in gas_p)

    def safe_pct(num, den):
        return round(num / den * 100, 1) if den != 0 else 0

    def safe_var(val, base):
        if base == 0: return None
        return round((val - base) / abs(base) * 100, 1)

    rows = []
    for node in effective:
        partida_name = node['partida_name']
        is_header = node['is_header']
        parent = None
        bold = node['bold']
        bg_color = node['bg_color']
        es_nota = node['es_nota']
        parent_name = node['parent_name']
        indent = node['indent']

        if is_header:
            prev_val = valores_calculados_por_mes.get('DIC', {}).get(partida_name, 0)
        else:
            prev_val = resolve_leaf_value_prev(partida_name, by_prev_raw)

        prev_pct_vtas = safe_pct(prev_val, divisor_prev(partida_name, by_prev_raw, ingresos_prev, ing_p))
        prev_pct_gastos = safe_pct(prev_val, gastos_prev)

        meses_data = []
        acum_ejec = 0
        acum_ppto = 0
        acum_ing_ejec = 0
        acum_ing_ppto = 0
        acum_gas_ejec = 0
        acum_gas_ppto = 0
        val_ejec_mes_anterior = None

        for m in MONTHS:
            month_type = MONTH_TYPES[m]

            if is_header:
                val_ejec = valores_calculados_por_mes[m].get(partida_name, 0)
                val_ppto = 0
            else:
                val_ejec = resolve_leaf_value(partida_name, m, by_partida)
                val_ppto = resolve_leaf_value(partida_name, m, by_budget)

            divisor_vtas_mes = divisor_ejec(partida_name, subtotales_por_mes[m], ingresos_ejec_mes[m], by_partida, m, ing_p)
            divisor_vtas_ppto = divisor_ppto_mes(partida_name, by_budget, m, ingresos_ppto_mes[m], ing_p)

            acum_ejec += val_ejec
            acum_ppto += val_ppto
            acum_ing_ejec += divisor_vtas_mes
            acum_ing_ppto += divisor_vtas_ppto
            acum_gas_ejec += gastos_ejec_mes[m]
            acum_gas_ppto += gastos_ppto_mes[m]

            pct_vtas_ejec = safe_pct(val_ejec, divisor_vtas_mes)
            pct_gastos_ejec = safe_pct(val_ejec, gastos_ejec_mes[m])

            mes_data = {
                'type': month_type,
                'month': m,
                'ejecutado': {
                    'valor': round(val_ejec, 2),
                    'pct_vtas': pct_vtas_ejec,
                    'pct_gastos': pct_gastos_ejec,
                }
            }

            if month_type != 'A':
                mes_data['vari_rel'] = safe_var(val_ejec, val_ejec_mes_anterior) if val_ejec_mes_anterior is not None else None

                if month_type == 'E':  # DIC
                    mes_data['anio'] = {
                        'valor': round(acum_ejec, 2),
                        'pct_vtas': safe_pct(acum_ejec, acum_ing_ejec),
                        'pct_gastos': safe_pct(acum_ejec, acum_gas_ejec),
                    }
                else:
                    mes_data['acum_ejecutado'] = {
                        'valor': round(acum_ejec, 2),
                        'pct_vtas': safe_pct(acum_ejec, acum_ing_ejec),
                        'pct_gastos': safe_pct(acum_ejec, acum_gas_ejec),
                    }

                if month_type in ('C', 'D', 'E'):
                    mes_data['acum_ppto'] = {
                        'valor': round(acum_ppto, 2),
                        'pct_vtas': safe_pct(acum_ppto, acum_ing_ppto),
                    }
                    mes_data['var_ppto'] = safe_var(acum_ejec, acum_ppto)

                    if month_type == 'D':  # JUN
                        prom_ejec = acum_ejec / 6
                        prom_ppto = acum_ppto / 6
                        prom_ing_ejec = acum_ing_ejec / 6
                        prom_ing_ppto = acum_ing_ppto / 6
                        prom_gas_ejec = acum_gas_ejec / 6
                        prom_gas_ppto = acum_gas_ppto / 6

                        mes_data['prom_6_ejec'] = {
                            'valor': round(prom_ejec, 2),
                            'pct_vtas': safe_pct(prom_ejec, prom_ing_ejec),
                            'pct_gastos': safe_pct(prom_ejec, prom_gas_ejec),
                        }
                        mes_data['prom_6_ppto'] = {
                            'valor': round(prom_ppto, 2),
                            'pct_vtas': safe_pct(prom_ppto, prom_ing_ppto),
                        }
                        mes_data['var_ppto_prom'] = safe_var(prom_ejec, prom_ppto)

            meses_data.append(mes_data)
            val_ejec_mes_anterior = val_ejec

        rows.append({
            'partida': partida_name,
            'is_header': is_header,
            'parent': parent,
            'bold': bold,
            'bg_color': bg_color,
            'es_nota': es_nota,
            'parent_name': parent_name,
            'indent': indent,
            'muestra_pct_gastos': muestra_pct_gastos_map.get(partida_name, False),
            'year_prev': {
                'valor': round(prev_val, 2),
                'pct_vtas': prev_pct_vtas,
                'pct_gastos': prev_pct_gastos,
            },
            'meses': meses_data,
        })

    return {
        'year': year,
        'year_prev': year_prev,
        'unit': unit,
        'rows': rows,
    }


def validate_eerr_v2_integrity(year, unit, adapter_output, db):
    """
    Guarda de integridad para EERR V2 y el adaptador V1.
    Realiza validaciones de coherencia financiera y de contrato de interfaz,
    registrando cualquier desviación de forma no bloqueante.
    """
    import logging
    logger = logging.getLogger('eerr_v2_integrity_guard')
    
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO)
        try:
            fh = logging.FileHandler('integrity_guard.log', encoding='utf-8')
            fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logger.addHandler(fh)
        except Exception:
            pass

    discrepancies = []
    
    # 1. Validación de subtotales vs suma de hojas
    from engine import EERR_STRUCTURE, build_effective_structure
    db_overrides = db.execute('SELECT partida_name, target_subtotal FROM eerr_nodes').fetchall()
    effective = build_effective_structure(EERR_STRUCTURE, db_overrides=db_overrides)
    structure_with_levels = [(node['partida_name'], node['is_header'], node['level']) for node in effective]

    rows_map = {r['partida']: r for r in adapter_output['rows']}
    
    for i, (name, is_header, level) in enumerate(structure_with_levels):
        if is_header:
            j = i + 1
            child_leaves = []
            while j < len(structure_with_levels):
                c_name, c_is_header, c_level = structure_with_levels[j]
                if c_level <= level:
                    break
                if not c_is_header:
                    if name == 'Subtotal Gastos de Administración' and c_name in [
                        'Gasto por impuesto a las pensiones',
                        'Gastos de IGTF',
                        'Gastos de comisiones bancarias',
                        'Gastos de intereses de mora',
                        'Gastos de mantenimiento y reparación a la propiedad alq.',
                        'Gastos de mantenimiento y reparación de edificaciones',
                        'Gastos de mantenimiento y reparación de maquinaria y equipos',
                        'Gastos de mantenimiento y reparación de mobiliario y equipo',
                        'Gastos de mantenimiento y reparación de vehiculo',
                        'Gastos de comida por viáticos administrativos',
                        'Gastos de hospedaje por viáticos administrativos',
                        'Gastos de pasajes por viáticos administrativos',
                        'Gastos de transporte por viáticos administrativos',
                        'Otros gastos de viáticos administrativos',
                        'Gastos de seguro de edificaciones',
                        'Gastos de seguro de vehiculos',
                        'Gasto por otras tasas',
                        'Gastos de impuesto por licencia de actividades economicas',
                        'Gastos de impuesto por publicidad',
                        'Gastos de patente vehicular',
                        'Gastos de tasa sencamer',
                        'Gastos de tasas de notaria y registro',
                        'Gastos de amortización de software',
                        'Gastos de depreciación de edificaciones',
                        'Gastos de depreciación de maquinarias y equipos',
                        'Gastos de depreciación de mobiliario y equipo',
                        'Gastos de depreciación de vehículos',
                        'Gastos de deterioro de edificaciones',
                        'Gastos de deterioro de maquinarias y equipos',
                        'Gastos de deterioro de mobiliario y equipo',
                        'Gastos de deterioro de vehículos',
                        'Gastos de deterioro por cuentas incobrables',
                        'Gastos de intereses sobre préstamos bancarios',
                        'Gastos de intereses sobre préstamos de terceros'
                    ]:
                        pass
                    elif name == 'Subtotal Gastos de Recursos Humanos' and c_name in [
                        'Gastos de uniformes y dotación al personal'
                    ]:
                        pass
                    elif name == 'Subtotal Gastos de Mercadeo' and c_name in [
                        'Gastos de impresiones de material gráfico',
                        'Gastos de patrocinio y donación'
                    ]:
                        pass
                    elif name == 'Subtotal Gastos de Comercialización y Logistica' and c_name in [
                        'Gastos de comida por viáticos comerciales',
                        'Gastos de hospedaje por viáticos comerciales',
                        'Gastos de pasajes por viáticos comerciales',
                        'Gastos de transporte por viáticos comerciales',
                        'Otros gastos de viáticos comerciales',
                        'Gastos de almacenaje sobre compras no incluídos en el costo',
                        'Gastos de armado de bicicletas no incluídos en el costo',
                        'Gastos de bolsas no incluídos en el costo',
                        'Gastos de embalaje no incluídos en el costo',
                        'Gastos de etiquetas no incluídos en el costo',
                        'Gastos de importación no incluídos en el costo',
                        'Gastos de seguro de mercancía no incluídos en el costo',
                        'Gastos de títulos de propiedad no incluídos en el costo',
                        'Gastos por gasoil',
                        'Gastos por gasolina',
                        'Gastos de alquiler Stand y/o ferias comerciales',
                        'Gastos de otros viáticos Stand y/o ferias comerciales',
                        'Gastos de pasajes Stand y/o ferias comerciales',
                        'Gastos de premiaciones, donaciones Stand y/o ferias comerciales',
                        'Gastos de publicidad Stand y/o ferias comerciales',
                        'Gastos de viáticos comida Stand y/o ferias comerciales',
                        'Gastos de viáticos hospedaje Stand y/o ferias comerciales',
                        'Gastos de viáticos transporte Stand y/o ferias comerciales'
                    ]:
                        pass
                    elif name == 'Gastos de TI+I' and c_name in [
                        'Gastos de dominio de página web',
                        'Gastos de servidores',
                        'Gastos de software tecnológico'
                    ]:
                        pass
                    elif name == 'Otros Gastos no Operacionales' and c_name in [
                        'Deterioro de inventarios',
                        'Faltante de inventarios'
                    ]:
                        pass
                    else:
                        child_leaves.append(c_name)
                j += 1
            if name == 'Subtotal Gastos de Comercialización y Logistica':
                child_leaves.append('Gastos de comisiones empleados')
                child_leaves.append('Gastos de comisiones por venta de personal externo')

            for m_idx, m in enumerate(MONTHS):
                sum_leaves = 0.0
                for leaf_name in child_leaves:
                    if leaf_name in rows_map:
                        sum_leaves += rows_map[leaf_name]['meses'][m_idx]['ejecutado']['valor']
                
                header_val = 0.0
                if name in rows_map:
                    header_val = rows_map[name]['meses'][m_idx]['ejecutado']['valor']
                
                if name in [
                    'Subtotal Gastos de Administración',
                    'Subtotal Gastos de Recursos Humanos',
                    'Subtotal Gastos de Comercialización y Logistica',
                    'Subtotal Gastos de Mercadeo',
                    'Gastos de TI+I',
                    'Gastos de sueldos y salarios empleados y directivos',
                    'Gastos de complementos empleados y directivos',
                    'Gastos de personal externo',
                    'Gastos de pasivos laborales vacaciones',
                    'Gastos de pasivos laborales utilidades',
                    'Gastos de pasivos laborales prestaciones e intereses',
                    'Gastos de pasivos laborales aportes',
                    'Gastos de pasivos laborales HCM',
                    'Gastos de salud y seguridad laboral fiestas y agasajos',
                    'Otros gastos de personal'
                ]:
                    diff = abs(header_val - sum_leaves)
                    if diff > 0.05:
                        msg = f"Discrepancia de subtotal en [{name}] para el mes {m}: Valor Header={header_val:.2f}, Suma Hojas={sum_leaves:.2f} (Diff={diff:.2f})"
                        discrepancies.append(msg)

    # 2. Validación contra baseline dinámico (validation_baselines)
    baseline_rows = db.execute(
        'SELECT month, partida, valor_esperado FROM validation_baselines WHERE year = ? AND unit = ?',
        [year, unit]
    ).fetchall()
    if baseline_rows:
        months_in_adapter = adapter_output['rows'][0]['meses'] if adapter_output['rows'] else []
        month_index = {m['month']: idx for idx, m in enumerate(months_in_adapter)}
        for row in baseline_rows:
            b_month = row['month']
            row_name = row['partida']
            expected_val = row['valor_esperado']
            if row_name in rows_map and b_month in month_index:
                idx = month_index[b_month]
                actual_val = rows_map[row_name]['meses'][idx]['ejecutado']['valor']
                diff = abs(actual_val - expected_val)
                if diff > 0.05:
                    msg = f"Descuadre contra baseline validado en [{row_name}] mes {b_month}: Esperado={expected_val:.2f}, Obtenido={actual_val:.2f} (Diff={diff:.2f})"
                    discrepancies.append(msg)
            elif row_name not in rows_map:
                discrepancies.append(f"Fila obligatoria de baseline [{row_name}] no encontrada en la respuesta")

    # 3. Validación de cuentas activas en financials sin mapear en mapping_groups_v2
    try:
        missing_mappings = db.execute('''
            SELECT DISTINCT m.partida, m.odoo_code
            FROM financials f
            JOIN (
                SELECT odoo_code, partida FROM mapping m
                WHERE NOT EXISTS (
                    SELECT 1 FROM mapping sub 
                    WHERE sub.odoo_code LIKE m.odoo_code || '.%' AND sub.odoo_code != m.odoo_code
                )
            ) m ON f.partida = m.partida
            LEFT JOIN mapping_groups_v2 mg ON m.odoo_code = mg.odoo_code
            WHERE mg.odoo_code IS NULL AND f.year = ?
        ''', [year]).fetchall()
        for r in missing_mappings:
            msg = f"Cuenta transaccional activa sin mapear en mapping_groups_v2: Partida='{r['partida']}', OdooCode='{r['odoo_code']}'"
            discrepancies.append(msg)
    except Exception as e:
        discrepancies.append(f"Error al validar cuentas sin mapear: {str(e)}")

    # 4. Validación del contrato de la API del Frontend
    required_keys_always = {'type', 'month', 'ejecutado'}
    required_keys_ejecutado = {'valor', 'pct_vtas', 'pct_gastos'}
    
    for r in adapter_output['rows']:
        partida = r['partida']
        for m_idx, m_data in enumerate(r['meses']):
            missing_keys = required_keys_always - set(m_data.keys())
            if missing_keys:
                discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Faltan claves básicas del contrato: {missing_keys}")
                continue
                
            ejec = m_data['ejecutado']
            if not isinstance(ejec, dict):
                discrepancies.append(f"Fila [{partida}] mes index {m_idx}: 'ejecutado' debe ser un diccionario")
                continue
            missing_ejec = required_keys_ejecutado - set(ejec.keys())
            if missing_ejec:
                discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Faltan claves en 'ejecutado': {missing_ejec}")
            
            m_type = m_data['type']
            
            if m_type != 'A':
                if 'vari_rel' not in m_data:
                    discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Falta 'vari_rel' en mes tipo {m_type}")
                
                if m_type == 'E':
                    if 'anio' not in m_data:
                        discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Falta 'anio' en mes tipo E")
                    else:
                        missing_anio = required_keys_ejecutado - set(m_data['anio'].keys())
                        if missing_anio:
                            discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Faltan claves en 'anio': {missing_anio}")
                else:
                    if 'acum_ejecutado' not in m_data:
                        discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Falta 'acum_ejecutado' en mes tipo {m_type}")
                    else:
                        missing_acum = required_keys_ejecutado - set(m_data['acum_ejecutado'].keys())
                        if missing_acum:
                            discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Faltan claves en 'acum_ejecutado': {missing_acum}")
                
                if m_type in ('C', 'D', 'E'):
                    if 'acum_ppto' not in m_data:
                        discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Falta 'acum_ppto' en mes tipo {m_type}")
                    else:
                        missing_ppto = {'valor', 'pct_vtas'} - set(m_data['acum_ppto'].keys())
                        if missing_ppto:
                            discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Faltan claves en 'acum_ppto': {missing_ppto}")
                    if 'var_ppto' not in m_data:
                        discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Falta 'var_ppto' en mes tipo {m_type}")
                        
                    if m_type == 'D':
                        if 'prom_6_ejec' not in m_data:
                            discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Falta 'prom_6_ejec' en mes tipo D")
                        else:
                            missing_prom_ejec = required_keys_ejecutado - set(m_data['prom_6_ejec'].keys())
                            if missing_prom_ejec:
                                discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Faltan claves en 'prom_6_ejec': {missing_prom_ejec}")
                        if 'prom_6_ppto' not in m_data:
                            discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Falta 'prom_6_ppto' en mes tipo D")
                        else:
                            missing_prom_ppto = {'valor', 'pct_vtas'} - set(m_data['prom_6_ppto'].keys())
                            if missing_prom_ppto:
                                discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Faltan claves en 'prom_6_ppto': {missing_prom_ppto}")
                        if 'var_ppto_prom' not in m_data:
                            discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Falta 'var_ppto_prom' en mes tipo D")

    if discrepancies:
        logger.warning(f"--- DETECTADAS DISCREPANCIAS DE INTEGRIDAD (EERR V2) - Unidad={unit}, Año={year} ---")
        for d in discrepancies:
            logger.warning(d)
        return False, discrepancies
    else:
        logger.info(f"Integridad validada exitosamente para Unidad={unit}, Año={year}. Sin descuadres.")
        return True, []


def validate_esf_integrity(year, unit, esf_output, db):
    """
    Guarda de integridad para ESF.
    No replica el patrón de EERR 1:1 porque la identidad Activo=Pasivo+Patrimonio
    y el subtotal-vs-hojas se cumplen siempre por construcción algebraica en esf_engine
    (Resultados acumulados es un plug, headers se calculan sumando hijos directos).
    Valida lo que sí puede fallar: mapeo de cuentas y razonabilidad del plug.
    """
    import logging
    logger = logging.getLogger('esf_integrity_guard')

    if not logger.handlers:
        logging.basicConfig(level=logging.INFO)
        try:
            fh = logging.FileHandler('integrity_guard_esf.log', encoding='utf-8')
            fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logger.addHandler(fh)
        except Exception:
            pass

    discrepancies = []

    # 1. Cuentas activas en financials_detail (report_type='esf') sin mapear en mapping_groups_v2
    try:
        missing_mappings = db.execute('''
            SELECT DISTINCT fd.odoo_code, fd.odoo_name
            FROM financials_detail fd
            LEFT JOIN mapping_groups_v2 mg
                ON fd.odoo_code = mg.odoo_code AND mg.report_type = 'esf'
            WHERE fd.report_type = 'esf' AND fd.year = ? AND mg.odoo_code IS NULL
              AND fd.amount_sign != 0
        ''', [year]).fetchall()
        for r in missing_mappings:
            msg = f"Cuenta ESF activa sin mapear en mapping_groups_v2: OdooCode='{r['odoo_code']}', Nombre='{r['odoo_name']}'"
            discrepancies.append(msg)
    except Exception as e:
        discrepancies.append(f"Error al validar cuentas ESF sin mapear: {str(e)}")

    # 2. Razonabilidad del plug "Resultados acumulados" (variación trimestre a trimestre)
    rows_map = {r['partida']: r for r in esf_output.get('rows', [])}
    res_acum = rows_map.get('Resultados acumulados')
    total_activos = rows_map.get('TOTAL ACTIVOS')

    if res_acum and total_activos:
        quarters_present = sorted(res_acum['quarters'].keys())
        for i in range(1, len(quarters_present)):
            q_prev = quarters_present[i - 1]
            q_curr = quarters_present[i]
            val_prev = res_acum['quarters'][q_prev]
            val_curr = res_acum['quarters'][q_curr]
            activos_curr = total_activos['quarters'].get(q_curr, 0.0)

            variacion = abs(val_curr - val_prev)
            if activos_curr:
                variacion_pct = variacion / abs(activos_curr)
                if variacion_pct > ESF_PLUG_VARIACION_UMBRAL:
                    msg = (f"Salto brusco en Resultados acumulados (plug) entre Q{q_prev} y Q{q_curr}: "
                           f"Q{q_prev}={val_prev:.2f}, Q{q_curr}={val_curr:.2f}, "
                           f"Variación={variacion:.2f} ({variacion_pct*100:.1f}% de Total Activos, "
                           f"umbral={ESF_PLUG_VARIACION_UMBRAL*100:.0f}%)")
                    discrepancies.append(msg)

            # Alerta separada: cambio de signo en el plug (independiente del %,
            # puede indicar patrimonio insuficiente frente a pérdidas acumuladas reales)
            if (val_prev > 0 and val_curr < 0) or (val_prev < 0 and val_curr > 0):
                msg_signo = (f"Cambio de signo en Resultados acumulados (plug) entre Q{q_prev} y Q{q_curr}: "
                             f"Q{q_prev}={val_prev:.2f} -> Q{q_curr}={val_curr:.2f}")
                discrepancies.append(msg_signo)

    if discrepancies:
        logger.warning(f"--- DETECTADAS DISCREPANCIAS DE INTEGRIDAD (ESF) - Unidad={unit}, Año={year} ---")
        for d in discrepancies:
            logger.warning(d)
    else:
        logger.info(f"Integridad ESF validada exitosamente para Unidad={unit}, Año={year}. Sin descuadres.")

    return discrepancies


@app.route('/api/eerr/completo', methods=['GET'])
def eerr_completo():
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')
    empresa_id = request.args.get('empresa_id', type=int) or None

    data = eerr_completo_v2_ui_adapter(year, unit, empresa_id=empresa_id)
    
    try:
        db = get_db()
        validate_eerr_v2_integrity(year, unit, data, db)
    except Exception as e:
        app.logger.error(f"Error al ejecutar validacion de integridad: {str(e)}")

    return jsonify(data)


# ── ESF ───────────────────────────────────────────────────────────────────────


def compute_esf(db, year, unit='', empresa_id=None):
    """
    Calcula el Estado de Situación Financiera por quarter (consolidando unidades
    cuando unit está vacío). Devuelve (result_quarters, quarters_available).
    """
    from engine import esf_engine

    if unit:
        uc = 'AND unit=?'
        params_q = [year, unit]
    elif empresa_id:
        uc = 'AND empresa_id=?'
        params_q = [year, empresa_id]
    else:
        uc = ''
        params_q = [year]
    rows_q = db.execute(f'SELECT DISTINCT quarter FROM esf_data WHERE year=? {uc}', params_q).fetchall()
    quarters_available = sorted([r['quarter'] for r in rows_q])

    res = esf_engine(year, unit, empresa_id=empresa_id)
    try:
        validate_esf_integrity(year, unit, res, db)
    except Exception as e:
        app.logger.error(f"Error al ejecutar validacion de integridad ESF: {str(e)}")
    
    result_quarters = {
        1: {'totales': {}, 'partidas': {}},
        2: {'totales': {}, 'partidas': {}},
        3: {'totales': {}, 'partidas': {}},
        4: {'totales': {}, 'partidas': {}}
    }
    for row in res.get('rows', []):
        partida = row.get('partida')
        quarters_val = row.get('quarters', {})
        for q in [1, 2, 3, 4]:
            val = quarters_val.get(q, 0.0)
            result_quarters[q]['totales'][partida] = val
            result_quarters[q]['partidas'][partida] = val
            
    # Mapeo de compatibilidad de nomenclaturas de Totales del Balance (Fase 4 - ESF)
    for q in [1, 2, 3, 4]:
        tot = result_quarters[q]['totales']
        tot['Total Efectivo y Equivalentes']   = tot.get('Efectivo y Equivalentes', 0.0)
        tot['Total Cuentas por Cobrar (neto)'] = tot.get('Cuentas por Cobrar', 0.0)
        tot['Total Inventarios']               = tot.get('Inventarios', 0.0)
        tot['ACTIVOS CORRIENTES']              = tot.get('ACTIVOS CORRIENTES', 0.0)
        tot['Total Activos No Corrientes']     = tot.get('Total Activos No Corrientes', 0.0) or tot.get('ACTIVOS NO CORRIENTES', 0.0)
        tot['TOTAL ACTIVOS']                   = tot.get('TOTAL ACTIVOS', 0.0)
        
        tot['Total Cuentas por Pagar']         = tot.get('Cuentas por Pagar', 0.0)
        tot['TOTAL PASIVOS CORRIENTES']        = tot.get('TOTAL PASIVOS CORRIENTES', 0.0) or tot.get('Total Pasivos Corrientes', 0.0) or tot.get('PASIVOS CORRIENTES', 0.0)
        tot['TOTAL PASIVOS NO CORRIENTES']     = tot.get('TOTAL PASIVOS NO CORRIENTES', 0.0) or tot.get('Total Pasivos No Corrientes', 0.0) or tot.get('PASIVOS NO CORRIENTES', 0.0)
        tot['TOTAL PASIVOS']                   = tot.get('TOTAL PASIVOS', 0.0)
        tot['TOTAL PATRIMONIO']                = tot.get('TOTAL PATRIMONIO', 0.0) or tot.get('Total Patrimonio', 0.0) or tot.get('PATRIMONIO', 0.0)
        tot['TOTAL PASIVOS Y PATRIMONIO']      = tot.get('TOTAL PASIVOS Y PATRIMONIO', 0.0)
        
    return result_quarters, quarters_available


def compute_indicadores_v2(db, year, empresa_id=None):
    """
    Calcula los 20 indicadores financieros por trimestre + año actual + año anterior.
    Estructura de salida compatible con el módulo Indicadores Financieros del frontend.
    """
    from engine import EERR_STRUCTURE, build_effective_structure
    import unicodedata

    def safe_div(a, b):
        if b is None or b == 0:
            return None
        return round(a / b, 4) if a is not None else None

    def vari_rel(prev, curr):
        if prev is None or curr is None:
            return None
        if prev == 0:
            return 1.0 if curr > 0 else None
        return round((curr - prev) / abs(prev), 4)

    QUARTER_MONTHS = {
        1: ['ENE','FEB','MAR'],
        2: ['ABR','MAY','JUN'],
        3: ['JUL','AGO','SEPT'],
        4: ['OCT','NOV','DIC']
    }

    # ── EERR: cargar financials por trimestre ──────────────────────────────────
    groups_v2, _ = get_grouped_partidas_v2(db, 'eerr')
    db_overrides = db.execute('SELECT partida_name, target_subtotal FROM eerr_nodes').fetchall()
    effective = build_effective_structure(EERR_STRUCTURE, db_overrides=db_overrides)

    def norm(s):
        if not s: return ''
        s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
        return s.lower().strip()

    NODOS = {
        'Total Ingresos': 'ingresos',
        'Total Costo de Ventas': 'costos',
        'Utilidad Bruta': 'ut_bruta',
        'Total Gastos Operacionales': 'gas_op',
        'Utilidad Neta Operacional': 'ut_op',
        'Otros Ingresos no Operacionales': 'ot_ing',
        'Otros Gastos no Operacionales': 'ot_gas',
        'ISLR': 'islr',
        'Utilidad Neta despues de ISLR': 'ut_neta',
    }

    def _extract_eerr(rows, months):
        """Extrae subtotales EERR de rows ya cargados, filtrando por meses."""
        result = {v: 0.0 for v in NODOS.values()}
        for row in rows:
            partida = row.get('partida', '')
            if partida not in NODOS:
                continue
            key = NODOS[partida]
            for idx, mes_data in enumerate(row.get('meses', [])):
                if idx < len(MONTHS) and MONTHS[idx] in months:
                    result[key] += mes_data.get('ejecutado', {}).get('valor', 0) or 0
        # Fix indicadores: 'Ingresos Brutos' en la hoja de Yocelin (' EERR ULTRAX')
        # excluye las 9 partidas de Ingresos No Operativos (suma solo Mercancia+Taller,
        # Servicios y Eventos) - distinto de 'Total Ingresos' del EERR normal, que sí las incluye.
        result['ingresos'] = result['ingresos'] - result['ot_ing']
        result['ut_bruta'] = result['ingresos'] - result['costos']
        result['ut_op']    = result['ut_bruta'] - result['gas_op']
        result['otros_nop'] = result['ot_ing'] - result['ot_gas']
        result['ut_ai']    = result['ut_op'] + result['otros_nop']
        result['ut_neta']  = result['ut_ai'] - result['islr']
        result['margen_bruto'] = safe_div(result['ut_bruta'], result['ingresos'])
        result['margen_neto']  = safe_div(result['ut_neta'], result['ingresos'])
        return result

    # ── Cache único EERR y ESF ─────────────────────────────────────────────────
    from engine import esf_engine
    all_months = ['ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEPT','OCT','NOV','DIC']
    year_prev = str(int(year) - 1)

    # EERR: una sola llamada por año
    _rows_curr = eerr_completo_v2_ui_adapter(year, '', empresa_id=empresa_id).get('rows', [])
    _rows_prev = eerr_completo_v2_ui_adapter(year_prev, '', empresa_id=empresa_id).get('rows', [])

    # ESF: una sola llamada para el año actual
    _esf_res = esf_engine(year, '', empresa_id=empresa_id)
    _esf_rows = {n['partida']: n.get('quarters', {}) for n in _esf_res.get('rows', [])}
    _result_quarters, _ = compute_esf(db, year, '', empresa_id=empresa_id)

    def get_esf_quarter(q):
        rows_esf = {p: qs.get(q, 0) or 0 for p, qs in _esf_rows.items()}
        tot = _result_quarters.get(q, {}).get('totales', {})
        return {
            'tot_activos':   tot.get('TOTAL ACTIVOS', 0),
            'act_corr':      tot.get('ACTIVOS CORRIENTES', 0),
            'pas_corr':      tot.get('TOTAL PASIVOS CORRIENTES', 0) or tot.get('PASIVOS CORRIENTES', 0),
            'tot_pas':       tot.get('TOTAL PASIVOS', 0),
            'patrimonio':    tot.get('TOTAL PATRIMONIO', 0) or tot.get('PATRIMONIO', 0),
            'efectivo':      tot.get('Total Efectivo y Equivalentes', 0),
            'inventarios':   tot.get('Total Inventarios', 0),
            'cxc':           tot.get('Total Cuentas por Cobrar (neto)', 0),
            'res_ejercicio': rows_esf.get('Resultados del ejercicio', 0),
        }

    # ── Año anterior (acumulado anual) ─────────────────────────────────────────
    prev_eerr = _extract_eerr(_rows_prev, all_months)
    prev_esf  = {
        'tot_activos':0,'act_corr':0,'pas_corr':0,'tot_pas':0,
        'patrimonio':0,'efectivo':0,'inventarios':0,'cxc':0,'res_ejercicio':0
    }

    # ── Calcular por trimestre ─────────────────────────────────────────────────
    quarters_data = {}
    acum_eerr = {k: 0 for k in ['ingresos','costos','ut_bruta','gas_op','ut_op','otros_nop','ut_ai','islr','ut_neta']}
    for q in [1, 2, 3, 4]:
        months = QUARTER_MONTHS[q]
        eerr_q = _extract_eerr(_rows_curr, months)
        esf_q  = get_esf_quarter(q)
        for k in acum_eerr:
            acum_eerr[k] += eerr_q.get(k, 0) or 0
        quarters_data[q] = {'eerr': eerr_q, 'esf': esf_q}

    # Año actual acumulado
    ing_aa  = acum_eerr['ingresos']
    cos_aa  = acum_eerr['costos']
    esf_last = quarters_data[max(q for q in [1,2,3,4] if quarters_data[q]['esf']['tot_activos'] != 0) if any(quarters_data[q]['esf']['tot_activos'] for q in [1,2,3,4]) else 4]['esf']

    def build_ind(nombre, referencia, val_prev, vals_q, val_aa, es_pct=False, es_ratio=False):
        resultado = {'nombre': nombre, 'referencia': referencia, 'es_pct': es_pct, 'es_ratio': es_ratio}
        resultado['year_prev'] = val_prev
        resultado['anio_actual'] = val_aa
        trimestres = []
        vp = val_prev
        for q in [1,2,3,4]:
            v = vals_q[q]
            trimestres.append({'q': q, 'valor': v, 'vari_rel': vari_rel(vp, v)})
            if v is not None:
                vp = v
        resultado['trimestres'] = trimestres
        resultado['vari_rel_aa'] = vari_rel(val_prev, val_aa)
        return resultado

    def qv(q, key):
        return quarters_data[q]['eerr'].get(key)

    def qe(q, key):
        return quarters_data[q]['esf'].get(key, 0) or 0

    indicadores = [
        build_ind('Ingresos Brutos', None,
            prev_eerr['ingresos'],
            {q: qv(q,'ingresos') for q in [1,2,3,4]},
            ing_aa),
        build_ind('Costo de ventas', None,
            prev_eerr['costos'],
            {q: qv(q,'costos') for q in [1,2,3,4]},
            cos_aa),
        build_ind('Utilidad Bruta', None,
            prev_eerr['ut_bruta'],
            {q: qv(q,'ut_bruta') for q in [1,2,3,4]},
            acum_eerr['ut_bruta']),
        build_ind('Margen Bruto (30% a 50%)', '30%-50%',
            prev_eerr['margen_bruto'],
            {q: qv(q,'margen_bruto') for q in [1,2,3,4]},
            safe_div(acum_eerr['ut_bruta'], ing_aa), es_pct=True),
        build_ind('Gastos Operacionales', None,
            prev_eerr['gas_op'],
            {q: qv(q,'gas_op') for q in [1,2,3,4]},
            acum_eerr['gas_op']),
        build_ind('Utilidad Neta operacional', None,
            prev_eerr['ut_op'],
            {q: qv(q,'ut_op') for q in [1,2,3,4]},
            acum_eerr['ut_op']),
        build_ind('Otros Ingresos y gastos no operacionales', None,
            prev_eerr['otros_nop'],
            {q: qv(q,'otros_nop') for q in [1,2,3,4]},
            acum_eerr['otros_nop']),
        build_ind('Utilidad Neta antes de ISLR', None,
            prev_eerr['ut_ai'],
            {q: qv(q,'ut_ai') for q in [1,2,3,4]},
            acum_eerr['ut_ai']),
        build_ind('ISLR', None,
            prev_eerr['islr'],
            {q: qv(q,'islr') for q in [1,2,3,4]},
            acum_eerr['islr']),
        build_ind('Utilidad Neta despues de ISLR', None,
            prev_eerr['ut_neta'],
            {q: qv(q,'ut_neta') for q in [1,2,3,4]},
            acum_eerr['ut_neta']),
        build_ind('Margen Neto (5% y 15%)', '5%-15%',
            prev_eerr['margen_neto'],
            {q: qv(q,'margen_neto') for q in [1,2,3,4]},
            safe_div(acum_eerr['ut_neta'], ing_aa), es_pct=True),
        build_ind('ROE (10% y 20%)', '10%-20%',
            None,
            {q: safe_div(qe(q,'res_ejercicio'), qe(q,'patrimonio')) for q in [1,2,3,4]},
            safe_div(esf_last['res_ejercicio'], esf_last['patrimonio']), es_pct=True),
        build_ind('Rotación de Inventarios (2 y 3 meses)', '2-3 meses',
            None,
            {q: safe_div(qe(q,'inventarios')*3, qv(q,'costos')) for q in [1,2,3,4]},
            safe_div(esf_last['inventarios']*12, cos_aa), es_ratio=True),
        build_ind('Rotación de Activos (entre 1,5 a 2 veces al año)', '1.5-2x',
            None,
            {q: safe_div(qv(q,'ingresos'), qe(q,'tot_activos')) for q in [1,2,3,4]},
            safe_div(ing_aa, esf_last['tot_activos']), es_ratio=True),
        build_ind('Rentabilidad de Activos (ROA) (5% a 15%)', '5%-15%',
            None,
            {q: safe_div(qe(q,'res_ejercicio'), qe(q,'tot_activos')) for q in [1,2,3,4]},
            safe_div(esf_last['res_ejercicio'], esf_last['tot_activos']), es_pct=True),
        build_ind('Período de cobro (30 a 60 días max)', '30-60 días',
            None,
            {q: safe_div(qe(q,'cxc')*90, qv(q,'ingresos')) for q in [1,2,3,4]},
            safe_div(esf_last['cxc']*365, ing_aa), es_ratio=True),
        build_ind('Ratio Corriente (entre 1,5 y 2)', '1.5-2',
            None,
            {q: safe_div(qe(q,'act_corr'), qe(q,'pas_corr')) for q in [1,2,3,4]},
            safe_div(esf_last['act_corr'], esf_last['pas_corr']), es_ratio=True),
        build_ind('Ratio Endeudamiento (entre 0,4 y 0,6)', '0.4-0.6',
            None,
            {q: safe_div(qe(q,'tot_pas'), qe(q,'patrimonio')) for q in [1,2,3,4]},
            safe_div(esf_last['tot_pas'], esf_last['patrimonio']), es_ratio=True),
        build_ind('Prueba Ácida (entre 0,8 y 1)', '0.8-1',
            None,
            {q: safe_div(qe(q,'act_corr')-qe(q,'inventarios'), qe(q,'pas_corr')) for q in [1,2,3,4]},
            safe_div(esf_last['act_corr']-esf_last['inventarios'], esf_last['pas_corr']), es_ratio=True),
        build_ind('Prueba Defensiva (entre 0,5 Y 0,7)', '0.5-0.7',
            None,
            {q: safe_div(qe(q,'efectivo'), qe(q,'pas_corr')) for q in [1,2,3,4]},
            safe_div(esf_last['efectivo'], esf_last['pas_corr']), es_ratio=True),
    ]
    return indicadores


def compute_indicadores(db, year, unit='', ingresos=0.0, util_neta=0.0, empresa_id=None):
    """
    Calcula indicadores financieros combinando datos de ESF + EERR (original para Dashboard).
    """
    result_quarters, quarters_available = compute_esf(db, year, unit, empresa_id=empresa_id)
    if not quarters_available:
        return None

    last_q = max(quarters_available)
    esf = result_quarters[last_q]['totales']

    tot_activos = esf.get('TOTAL ACTIVOS', 0)
    tot_ac      = esf.get('ACTIVOS CORRIENTES', 0)
    tot_pc      = esf.get('TOTAL PASIVOS CORRIENTES', 0)
    tot_pas     = esf.get('TOTAL PASIVOS', 0)
    tot_pat     = esf.get('TOTAL PATRIMONIO', 0)
    tot_ef      = esf.get('Total Efectivo y Equivalentes', 0)
    tot_inv     = esf.get('Total Inventarios', 0)
    tot_cxc     = esf.get('Total Cuentas por Cobrar (neto)', 0)

    # Ingresos y costos trimestrales (para rotación inventarios)
    if unit:
        uc = "AND unit=?"
        uc_params = [unit]
    elif empresa_id:
        unidades_rows = db.execute('SELECT nombre FROM unidades WHERE empresa_id=?', [empresa_id]).fetchall()
        nombres_unidades = [r['nombre'] for r in unidades_rows]
        if nombres_unidades:
            uc = f"AND unit IN ({','.join('?'*len(nombres_unidades))})"
            uc_params = nombres_unidades
        else:
            uc = "AND 1=0"
            uc_params = []
    else:
        uc = ''
        uc_params = []
    meses_q = {1:[1,2,3], 2:[4,5,6], 3:[7,8,9], 4:[10,11,12]}[last_q]
    meses_nombres = [MONTHS[m-1] for m in meses_q]
    rows_q = db.execute(
        f'''SELECT SUM(amount_sign) total, odoo_code AS account_number FROM financials_detail
            WHERE year=? AND month IN ({','.join('?'*len(meses_nombres))}) {uc}
            GROUP BY odoo_code''',
        [year] + meses_nombres + uc_params
    ).fetchall()
    ing_q = sum(r['total'] for r in rows_q if r['account_number'].startswith('4'))
    cos_q = sum(r['total'] for r in rows_q if r['account_number'].startswith('5'))

    def safe_div(a, b):
        return round(a / b, 2) if b != 0 else None

    return {
        'roe':              safe_div(util_neta, tot_pat),
        'roa':              safe_div(util_neta, tot_activos),
        'ratio_corriente':  safe_div(tot_ac, tot_pc),
        'prueba_acida':     safe_div(tot_ac - tot_inv, tot_pc),
        'prueba_defensiva': safe_div(tot_ef, tot_pc),
        'ratio_endeud':     safe_div(tot_pas, tot_pat),
        'rotacion_inv':     safe_div(tot_inv * 3, cos_q) if cos_q else None,
        'rotacion_activos': safe_div(ing_q, tot_activos),
        'periodo_cobro':    safe_div(tot_cxc * 90, ing_q) if ing_q else None,
    }


@app.route('/api/esf/totals', methods=['GET'])
@login_required
def esf_totals():
    """
    Retorna totales ESF del último quarter disponible para uso en dashboard widgets.
    Parámetros: year, unit (opcional).
    """
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')
    db   = get_db()

    result_quarters, quarters_available = compute_esf(db, year, unit)
    if not quarters_available:
        return jsonify({'error': 'Sin datos ESF'}), 404

    last_q = max(quarters_available)
    totales = result_quarters[last_q]['totales']

    return jsonify({
        'year': year,
        'unit': unit,
        'quarter': last_q,
        'totales': {
            'total_activos':        totales.get('TOTAL ACTIVOS', 0),
            'activos_corrientes':   totales.get('ACTIVOS CORRIENTES', 0),
            'activos_no_corrientes':totales.get('Total Activos No Corrientes', 0),
            'total_pasivos':        totales.get('TOTAL PASIVOS', 0),
            'pasivos_corrientes':   totales.get('TOTAL PASIVOS CORRIENTES', 0),
            'pasivos_no_corrientes':totales.get('TOTAL PASIVOS NO CORRIENTES', 0),
            'patrimonio':           totales.get('TOTAL PATRIMONIO', 0),
            'efectivo':             totales.get('Total Efectivo y Equivalentes', 0),
            'cuentas_por_cobrar':   totales.get('Total Cuentas por Cobrar (neto)', 0),
            'inventarios':          totales.get('Total Inventarios', 0),
            'cuentas_por_pagar':    totales.get('Total Cuentas por Pagar', 0),
        }
    })


@app.route('/api/esf', methods=['GET'])
def esf():
    """
    Estado de Situación Financiera por quarter.
    Parámetros: year, unit (opcional). Siempre retorna los 4 quarters;
    el filtro por quarter se aplica en el frontend.
    """
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')
    db   = get_db()

    result_quarters, quarters_available = compute_esf(db, year, unit)

    def var(q_a, q_b, key):
        a = result_quarters[q_a]['totales'].get(key, 0)
        b = result_quarters[q_b]['totales'].get(key, 0)
        if a == 0: return None
        return round((b - a) / abs(a) * 100, 1)

    variaciones = {}
    for key in ['TOTAL ACTIVOS', 'TOTAL PASIVOS', 'TOTAL PATRIMONIO', 'TOTAL PASIVOS Y PATRIMONIO']:
        variaciones[key] = {
            'Q1_Q2': var(1, 2, key),
            'Q2_Q3': var(2, 3, key),
            'Q3_Q4': var(3, 4, key),
        }

    return jsonify({
        'year': year, 'unit': unit,
        'quarters': result_quarters,
        'quarters_available': quarters_available,
        'variaciones': variaciones,
    })


@app.route('/api/esf/completo', methods=['GET'])
def esf_completo():
    """
    Estado de Situación Financiera completo con estructura jerárquica expandible de 3 niveles.
    Parámetros: year, unit (opcional).
    """
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')
    empresa_id = request.args.get('empresa_id', type=int) or None
    from engine import esf_engine
    result = esf_engine(year, unit, empresa_id=empresa_id)
    try:
        db = get_db()
        validate_esf_integrity(year, unit, result, db)
    except Exception as e:
        app.logger.error(f"Error al ejecutar validacion de integridad ESF: {str(e)}")

    year_prev = str(int(year) - 1)
    result_prev = esf_engine(year_prev, unit, empresa_id=empresa_id)
    prev_by_partida = {}
    for r in result_prev.get('rows', []):
        prev_by_partida[r['partida']] = r.get('quarters', {}).get(4, 0.0)
    for row in result.get('rows', []):
        row['year_prev'] = prev_by_partida.get(row['partida'], 0.0)
    result['year_prev'] = year_prev

    return jsonify(result)


@app.route('/api/indicadores', methods=['GET'])
def get_indicadores():
    """
    Retorna indicadores financieros avanzados (ROE, ROA, liquidez, rotación).
    Parámetros: year, unit (opcional), empresa_id (opcional).
    """
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')
    empresa_id = request.args.get('empresa_id', type=int) or None
    db   = get_db()

    indicadores = compute_indicadores_v2(db, year, empresa_id=empresa_id)
    if not indicadores:
        return jsonify({'error': 'Sin datos ESF para calcular indicadores'}), 404

    return jsonify({'year': year, 'unit': unit, 'empresa_id': empresa_id, 'indicadores': indicadores})


# ── Divisa Real (Tasas y Métodos de Pago) ────────────────────────────────────

@app.route('/api/tasas', methods=['GET'])
def get_tasas():
    """Retorna todas las tasas por período o una específica si se pasa year/month."""
    year  = request.args.get('year')
    month = request.args.get('month')
    db    = get_db()

    if year and month:
        row = db.execute(
            'SELECT * FROM tasas_periodo WHERE year=? AND month=?',
            (year, month)
        ).fetchone()
        if not row:
            return jsonify({'error': 'No hay tasas configuradas para este período'}), 404
        return jsonify(dict(row))
    else:
        rows = db.execute('''
            SELECT * FROM tasas_periodo
            ORDER BY year DESC,
            CASE month
                WHEN 'ENE' THEN 1 WHEN 'FEB' THEN 2 WHEN 'MAR' THEN 3 WHEN 'ABR' THEN 4
                WHEN 'MAY' THEN 5 WHEN 'JUN' THEN 6 WHEN 'JUL' THEN 7 WHEN 'AGO' THEN 8
                WHEN 'SEPT' THEN 9 WHEN 'OCT' THEN 10 WHEN 'NOV' THEN 11 WHEN 'DIC' THEN 12
            END DESC
        ''').fetchall()
        return jsonify([dict(r) for r in rows])


@app.route('/api/tasas', methods=['POST'])
@admin_required
def save_tasas():
    """
    Guarda o actualiza tasas para un período.
    Body: {year, month, tasa_bcv_inicio, tasa_bcv_fin, tasa_paralela_inicio, tasa_paralela_fin}
    Calcula promedios y factor_diferencial automáticamente.
    """
    data = request.get_json()
    year   = data.get('year')
    month  = data.get('month')
    bcv_ini    = data.get('tasa_bcv_inicio')
    bcv_fin    = data.get('tasa_bcv_fin')
    par_ini    = data.get('tasa_paralela_inicio')
    par_fin    = data.get('tasa_paralela_fin')

    if not all([year, month, bcv_ini is not None, bcv_fin is not None, par_ini is not None, par_fin is not None]):
        return jsonify({'error': 'Faltan parámetros requeridos'}), 400

    if bcv_ini <= 0 or bcv_fin <= 0:
        return jsonify({'error': 'Tasas BCV deben ser mayores a cero'}), 400

    # Calcular promedios
    bcv_prom = (bcv_ini + bcv_fin) / 2
    par_prom = (par_ini + par_fin) / 2
    diferencial = par_prom / bcv_prom

    db = get_db()
    db.execute('''
        INSERT INTO tasas_periodo (year, month, tasa_bcv_inicio, tasa_bcv_fin, tasa_bcv_promedio,
                                   tasa_paralela_inicio, tasa_paralela_fin, tasa_paralela_promedio,
                                   factor_diferencial)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(year, month) DO UPDATE SET
            tasa_bcv_inicio = excluded.tasa_bcv_inicio,
            tasa_bcv_fin = excluded.tasa_bcv_fin,
            tasa_bcv_promedio = excluded.tasa_bcv_promedio,
            tasa_paralela_inicio = excluded.tasa_paralela_inicio,
            tasa_paralela_fin = excluded.tasa_paralela_fin,
            tasa_paralela_promedio = excluded.tasa_paralela_promedio,
            factor_diferencial = excluded.factor_diferencial
    ''', (year, month, bcv_ini, bcv_fin, bcv_prom, par_ini, par_fin, par_prom, diferencial))
    db.commit()

    return jsonify({
        'ok': True,
        'year': year,
        'month': month,
        'tasa_bcv_promedio': round(bcv_prom, 4),
        'tasa_paralela_promedio': round(par_prom, 4),
        'factor_diferencial': round(diferencial, 4)
    })


@app.route('/api/tasas/<int:tasa_id>', methods=['DELETE'])
@admin_required
def delete_tasa(tasa_id):
    db = get_db()
    db.execute('DELETE FROM tasas_periodo WHERE id = ?', (tasa_id,))
    db.commit()
    return jsonify({'ok': True})


@app.route('/api/esf-divisa-real', methods=['GET'])
def get_esf_divisa_real():
    year = request.args.get('year')
    quarter = request.args.get('quarter', type=int)
    if not year or not quarter:
        return jsonify({'error': 'year y quarter son requeridos'}), 400
    from engine import calcular_esf_divisa_real, esf_engine

    db = get_db()
    overrides_rows = db.execute(
        'SELECT odoo_code, valor_override FROM esf_divisa_real_overrides WHERE year=? AND quarter=?',
        (year, quarter)
    ).fetchall()
    overrides_flat = {r['odoo_code']: r['valor_override'] for r in overrides_rows}
    overrides_keyed = {(quarter, r['odoo_code']): r['valor_override'] for r in overrides_rows}

    result = calcular_esf_divisa_real(year, quarter, overrides=overrides_flat)
    if 'error' in result:
        return jsonify(result), 404

    esf_completo = esf_engine(year, '', overrides_divisa_real=overrides_keyed)

    year_prev = str(int(year) - 1)
    result_prev = esf_engine(year_prev, '')
    prev_by_partida = {}
    for r in result_prev.get('rows', []):
        prev_by_partida[r['partida']] = r.get('quarters', {}).get(4, 0.0)
    for row in esf_completo.get('rows', []):
        row['year_prev'] = prev_by_partida.get(row['partida'], 0.0)
    esf_completo['year_prev'] = year_prev

    result['esf_completo'] = esf_completo
    return jsonify(result)


@app.route('/api/esf-divisa-real/detalle-cuentas', methods=['GET'])
def get_esf_divisa_real_detalle_cuentas():
    year = request.args.get('year')
    quarter = request.args.get('quarter', type=int)
    if not year or not quarter:
        return jsonify({'error': 'year y quarter son requeridos'}), 400
    from engine import PARTIDAS_ESF_DIVISA_REAL, QUARTER_MONTH_CIERRE
    month = QUARTER_MONTH_CIERRE.get(quarter)
    if not month:
        return jsonify({'error': f'Quarter inválido: {quarter}'}), 400
    db = get_db()
    placeholders = ','.join('?' * len(PARTIDAS_ESF_DIVISA_REAL))
    rows = db.execute(f'''
        SELECT mg.group_name, fd.odoo_code, fd.odoo_name, fd.amount_sign as valor_real
        FROM financials_detail fd
        JOIN mapping_groups_v2 mg ON fd.odoo_code = mg.odoo_code AND mg.report_type='esf'
        WHERE fd.year=? AND fd.report_type='esf' AND fd.month=?
          AND mg.group_name IN ({placeholders})
    ''', (year, month, *PARTIDAS_ESF_DIVISA_REAL)).fetchall()

    overrides_rows = db.execute(
        'SELECT odoo_code, valor_override FROM esf_divisa_real_overrides WHERE year=? AND quarter=?',
        (year, quarter)
    ).fetchall()
    overrides_map = {r['odoo_code']: r['valor_override'] for r in overrides_rows}

    partidas = {p: [] for p in PARTIDAS_ESF_DIVISA_REAL}
    for r in rows:
        partidas[r['group_name']].append({
            'odoo_code': r['odoo_code'],
            'odoo_name': r['odoo_name'],
            'valor_real': round(r['valor_real'], 2),
            'valor_override': overrides_map.get(r['odoo_code'])
        })
    return jsonify({'year': year, 'quarter': quarter, 'partidas': partidas})


@app.route('/api/esf-divisa-real/override', methods=['POST'])
@admin_required
def save_esf_divisa_real_override():
    body = request.get_json()
    year = body.get('year')
    quarter = body.get('quarter')
    odoo_code = body.get('odoo_code')
    valor_nuevo = body.get('valor_nuevo')
    if None in (year, quarter, odoo_code, valor_nuevo):
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    db = get_db()
    row_prev = db.execute(
        'SELECT valor_override FROM esf_divisa_real_overrides WHERE year=? AND quarter=? AND odoo_code=?',
        (year, quarter, odoo_code)
    ).fetchone()
    valor_anterior = row_prev['valor_override'] if row_prev else None

    db.execute('''
        INSERT INTO esf_divisa_real_overrides (year, quarter, odoo_code, valor_override, updated_at)
        VALUES (?, ?, ?, ?, datetime('now','localtime'))
        ON CONFLICT(year, quarter, odoo_code) DO UPDATE SET
            valor_override = excluded.valor_override,
            updated_at = excluded.updated_at
    ''', (year, quarter, odoo_code, valor_nuevo))

    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.execute('''
        INSERT INTO esf_divisa_real_override_log
        (year, quarter, odoo_code, valor_anterior, valor_nuevo, timestamp)
        VALUES (?,?,?,?,?,?)
    ''', (year, quarter, odoo_code, valor_anterior, valor_nuevo, ts))
    db.commit()

    from engine import calcular_esf_divisa_real, esf_engine
    overrides_rows = db.execute(
        'SELECT odoo_code, valor_override FROM esf_divisa_real_overrides WHERE year=? AND quarter=?',
        (year, quarter)
    ).fetchall()
    overrides_flat = {r['odoo_code']: r['valor_override'] for r in overrides_rows}
    panel_divisa_real = calcular_esf_divisa_real(year, quarter, overrides=overrides_flat)

    overrides_keyed = {(quarter, r['odoo_code']): r['valor_override'] for r in overrides_rows}
    esf_completo = esf_engine(year, '', overrides_divisa_real=overrides_keyed)

    return jsonify({'ok': True, 'panel_divisa_real': panel_divisa_real, 'esf_completo': esf_completo})



@app.route('/api/metodo_pago', methods=['GET'])
def get_metodo_pago():
    """Retorna métodos de pago para year/month dados, agrupados por odoo_code."""
    year  = request.args.get('year')
    month = request.args.get('month')

    if not year or not month:
        return jsonify({'error': 'Se requiere year y month'}), 400

    db   = get_db()
    rows = db.execute(
        'SELECT * FROM metodo_pago_cuenta WHERE year=? AND month=? ORDER BY odoo_code, unit',
        (year, month)
    ).fetchall()

    return jsonify([dict(r) for r in rows])


@app.route('/api/metodo_pago', methods=['POST'])
@admin_required
def save_metodo_pago():
    """
    Guarda % Cash/BCV para un período.
    Body: {year, month, metodos: [{unit, odoo_code, pct_cash}, ...]}
    """
    data = request.get_json()
    year    = data.get('year')
    month   = data.get('month')
    metodos = data.get('metodos', [])

    if not all([year, month]):
        return jsonify({'error': 'Faltan year/month'}), 400

    if not metodos:
        return jsonify({'error': 'No hay métodos de pago para guardar'}), 400

    db = get_db()

    # Borrar configuración anterior del período
    db.execute('DELETE FROM metodo_pago_cuenta WHERE year=? AND month=?', (year, month))

    # Insertar nueva configuración
    for m in metodos:
        unit     = m.get('unit')
        code     = m.get('odoo_code')
        pct_cash = m.get('pct_cash', 0)

        if not all([unit, code]) or pct_cash < 0 or pct_cash > 100:
            continue

        db.execute('''
            INSERT OR IGNORE INTO metodo_pago_cuenta (year, month, unit, odoo_code, pct_cash)
            VALUES (?, ?, ?, ?, ?)
        ''', (year, month, unit, code, pct_cash))

    db.commit()
    return jsonify({'ok': True, 'inserted': len(metodos)})


@app.route('/api/metodo_pago/copiar', methods=['POST'])
@admin_required
def copiar_metodo_pago():
    """
    Copia configuración de % Cash/BCV de un período anterior.
    Body: {from_year, from_month, to_year, to_month}
    """
    data = request.get_json()
    from_y = data.get('from_year')
    from_m = data.get('from_month')
    to_y   = data.get('to_year')
    to_m   = data.get('to_month')
    units  = data.get('units')  # lista de unidades; None = todas

    if not all([from_y, from_m, to_y, to_m]):
        return jsonify({'error': 'Faltan parámetros'}), 400

    db = get_db()

    # Leer configuración origen (filtrado por unidades si se especifica)
    if units:
        placeholders = ','.join('?' * len(units))
        rows = db.execute(
            'SELECT unit, odoo_code, pct_cash FROM metodo_pago_cuenta WHERE year=? AND month=? AND unit IN (' + placeholders + ')',
            [from_y, from_m] + list(units)
        ).fetchall()
    else:
        rows = db.execute(
            'SELECT unit, odoo_code, pct_cash FROM metodo_pago_cuenta WHERE year=? AND month=?',
            (from_y, from_m)
        ).fetchall()

    if not rows:
        return jsonify({'error': 'No hay configuración en el período origen'}), 404

    # Borrar destino solo para las unidades afectadas
    if units:
        placeholders = ','.join('?' * len(units))
        db.execute(
            'DELETE FROM metodo_pago_cuenta WHERE year=? AND month=? AND unit IN (' + placeholders + ')',
            [to_y, to_m] + list(units)
        )
    else:
        db.execute('DELETE FROM metodo_pago_cuenta WHERE year=? AND month=?', (to_y, to_m))

    # Insertar en destino
    for r in rows:
        db.execute('''
            INSERT INTO metodo_pago_cuenta (year, month, unit, odoo_code, pct_cash)
            VALUES (?, ?, ?, ?, ?)
        ''', (to_y, to_m, r['unit'], r['odoo_code'], r['pct_cash']))

    db.commit()
    return jsonify({'ok': True, 'copied': len(rows)})


# ── Función auxiliar para ajuste de divisa real ──────────────────────────────

def aplicar_factor_divisa(amount, pct_cash, diferencial):
    """
    Aplica ajuste de divisa real a un monto según % Cash / % BCV.

    Args:
        amount: Monto a ajustar
        pct_cash: Porcentaje pagado en cash/dólares (0-100)
        diferencial: Factor diferencial (tasa_paralela / tasa_bcv)

    Returns:
        Monto ajustado
    """
    if pct_cash is None:
        # Sin configuración, asumir 100% Cash (sin ajuste)
        return amount

    # % BCV = 100 - % Cash
    pct_bcv = 100 - pct_cash

    # Componente Cash: sin ajuste (factor 1)
    cash_component = amount * (pct_cash / 100)

    # Componente BCV: ajustar por diferencial
    bcv_component = amount * (pct_bcv / 100) / diferencial

    return cash_component + bcv_component


@app.route('/api/dashboard_divisa_real', methods=['GET'])
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

    eerr_unit_param = '' if unit == 'TODAS' else unit
    eerr_data = _calcular_eerr_divisa_real(year, eerr_unit_param)

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
@app.route('/api/divisa_real/resumen', methods=['GET'])
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


def _calcular_eerr_divisa_real(year, unit):
    """
    Calcula el Estado de Resultados COMPLETO con ajuste de divisa real.
    Misma estructura que /api/eerr/completo (119 partidas, tipos A/B/C/D/E)
    pero con montos ajustados por factor diferencial según % Cash/BCV.
    Función interna reutilizable - no es vista Flask. Usada por
    /api/eerr/divisa_real y /api/dashboard_divisa_real.
    Parámetros: year, unit
    Retorna: dict con year, year_prev, unit, rows
    """
    from engine import EERR_STRUCTURE, build_effective_structure

    db = get_db()

    year_prev = str(int(year) - 1)
    uc = "AND unit=?" if unit else ''
    uc_params = [unit] if unit else []

    MONTH_TYPES = {
        'ENE': 'A', 'FEB': 'B', 'MAR': 'C', 'ABR': 'B', 'MAY': 'B', 'JUN': 'D',
        'JUL': 'B', 'AGO': 'B', 'SEPT': 'C', 'OCT': 'B', 'NOV': 'B', 'DIC': 'E',
    }

    # ── PASO 4: CARGAR TASAS DESDE tasas_periodo ──
    tasas_rows = db.execute(
        'SELECT month, tasa_bcv_promedio, tasa_paralela_promedio, factor_diferencial FROM tasas_periodo WHERE year=?',
        [year]
    ).fetchall()
    
    tasas_by_month = {}
    for r in tasas_rows:
        m = r['month']
        bcv = r['tasa_bcv_promedio']
        paralela = r['tasa_paralela_promedio']
        
        # Validación de tasas
        if bcv is None or bcv <= 0:
            return jsonify({'error': f"Tasa BCV promedio inválida o cero para el mes {m} {year}"}), 400
        if paralela is None or paralela <= 0:
            return jsonify({'error': f"Tasa paralela promedio inválida o cero para el mes {m} {year}"}), 400
            
        diferencial = paralela / bcv
        tasas_by_month[m] = {
            'diferencial': diferencial
        }

    # ── PASO 1: LEER DATOS REALES DE financials ──
    rows_curr = db.execute(
        f'''SELECT partida, month, unit, amount FROM financials
            WHERE year=? {uc}''',
        [year] + uc_params
    ).fetchall()

    # Validar que existan tasas para todos los meses que contienen transacciones (Paso 4)
    months_in_data = set(r['month'] for r in rows_curr)
    for m in months_in_data:
        if m not in tasas_by_month:
            return jsonify({'error': f"Faltan tasas de cambio (tasas_periodo) para el periodo {year}/{m}"}), 400

    # ── PASO 2: OBTENER UN SOLO odoo_code REPRESENTATIVO POR PARTIDA ──
    mapping_rows = db.execute(
        'SELECT partida, odoo_code FROM mapping'
    ).fetchall()
    partida_to_code = {}
    for r in mapping_rows:
        p = r['partida']
        code = r['odoo_code']
        if p not in partida_to_code or len(code.split('.')) > len(partida_to_code[p].split('.')):
            partida_to_code[p] = code

    # ── PASO 3: CARGAR CONFIGURACIÓN DE % Cash/BCV ──
    metodos_rows = db.execute(
        'SELECT month, unit, odoo_code, pct_cash FROM metodo_pago_cuenta WHERE year=?',
        [year]
    ).fetchall()
    metodos_map = {(r['month'], r['unit'], r['odoo_code']): r['pct_cash'] for r in metodos_rows}

    # ── PASO 5 & 6: APLICAR AJUSTE DE DIVISA REAL Y AGRUPAR POR PARTIDA/MES ──
    by_partida = {}
    for r in rows_curr:
        partida = r['partida']
        month = r['month']
        row_unit = r['unit']
        amount_literal = r['amount']
        
        # Obtener odoo_code representativo
        odoo_code = partida_to_code.get(partida)
        pct_cash = 100.0
        
        if odoo_code:
            pct_cash = metodos_map.get((month, row_unit, odoo_code))
            if pct_cash is None:
                # FALLBACK EXPLÍCITO: Si no hay configuración para la cuenta/unidad, asumir 100% Cash (factor = 1)
                pct_cash = 100.0
                
        diferencial = tasas_by_month[month]['diferencial']
        amount_ajustado = aplicar_factor_divisa(amount_literal, pct_cash, diferencial)
        
        # Agrupación segura (Paso 6)
        by_partida.setdefault(partida, {})[month] = by_partida.get(partida, {}).get(month, 0) + amount_ajustado

    # Año anterior (sin ajuste - usar literal)
    rows_prev = db.execute(
        f'''SELECT partida, SUM(amount) amount FROM financials
            WHERE year=? {uc} GROUP BY partida''',
        [year_prev] + uc_params
    ).fetchall()
    by_prev_raw = {r['partida']: r['amount'] for r in rows_prev}

    # Presupuesto (sin ajuste)
    rows_budget = db.execute(
        f'''SELECT partida, month, SUM(amount) amount FROM budget
            WHERE year=? {uc} GROUP BY partida, month''',
        [year] + uc_params
    ).fetchall()
    by_budget = {}
    for r in rows_budget:
        by_budget.setdefault(r['partida'], {})[r['month']] = r['amount']

    # Clasificación
    ing_p, cos_p, gas_p = get_clasificacion(db)

    # Obtener grupos de presentación de mapping_groups_v2
    groups_v2, _ = get_grouped_partidas_v2(db, 'eerr')

    import unicodedata
    def norm(s):
        if not s: return ''
        s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
        return s.lower().strip()

    def resolve_leaf_value(partida_name, month, data_dict):
        if partida_name in groups_v2:
            return sum(data_dict.get(p, {}).get(month, 0) for p in groups_v2[partida_name])
        val = data_dict.get(partida_name, {}).get(month, 0)
        if val == 0:
            pn_norm = norm(partida_name)
            for k, v in data_dict.items():
                if norm(k) == pn_norm:
                    return v.get(month, 0)
        return val

    def resolve_leaf_value_prev(partida_name, data_dict):
        if partida_name in groups_v2:
            return sum(data_dict.get(p, 0) for p in groups_v2[partida_name])
        val = data_dict.get(partida_name, 0)
        if val == 0:
            pn_norm = norm(partida_name)
            for k, v in data_dict.items():
                if norm(k) == pn_norm:
                    return v
        return val

    # ── PASO 7: AGREGACIÓN JERÁRQUICA V2 DE SUBTOTALES ──
    db_overrides = db.execute('SELECT partida_name, target_subtotal FROM eerr_nodes').fetchall()
    effective = build_effective_structure(EERR_STRUCTURE, db_overrides=db_overrides)
    muestra_pct_gastos_map = calcular_muestra_pct_gastos(effective)
    structure_with_levels = [(node['partida_name'], node['is_header'], node['level']) for node in effective]

    subtotales_por_mes = {}
    for m in MONTHS:
        subtotales_por_mes[m] = {}
        for name, is_header, level in structure_with_levels:
            if not is_header:
                subtotales_por_mes[m][name] = resolve_leaf_value(name, m, by_partida)

        for i, (name, is_header, level) in enumerate(structure_with_levels):
            if is_header:
                total = 0
                j = i + 1
                while j < len(structure_with_levels):
                    c_name, c_is_header, c_level = structure_with_levels[j]
                    if c_level <= level:
                        break
                    if not c_is_header:
                        # Excluir cuentas que se duplicarían
                        if name == 'Subtotal Gastos de Administración' and c_name in [
                            'Gasto por impuesto a las pensiones',
                            'Gastos de IGTF',
                            'Gastos de comisiones bancarias',
                            'Gastos de intereses de mora',
                            'Gastos de mantenimiento y reparación a la propiedad alq.',
                            'Gastos de mantenimiento y reparación de edificaciones',
                            'Gastos de mantenimiento y reparación de maquinaria y equipos',
                            'Gastos de mantenimiento y reparación de mobiliario y equipo',
                            'Gastos de mantenimiento y reparación de vehiculo',
                            'Gastos de comida por viáticos administrativos',
                            'Gastos de hospedaje por viáticos administrativos',
                            'Gastos de pasajes por viáticos administrativos',
                            'Gastos de transporte por viáticos administrativos',
                            'Otros gastos de viáticos administrativos',
                            'Gastos de seguro de edificaciones',
                            'Gastos de seguro de vehiculos',
                            'Gasto por otras tasas',
                            'Gastos de impuesto por licencia de actividades economicas',
                            'Gastos de impuesto por publicidad',
                            'Gastos de patente vehicular',
                            'Gastos de tasa sencamer',
                            'Gastos de tasas de notaria y registro',
                            'Gastos de amortización de software',
                            'Gastos de depreciación de edificaciones',
                            'Gastos de depreciación de maquinarias y equipos',
                            'Gastos de depreciación de mobiliario y equipo',
                            'Gastos de depreciación de vehículos',
                            'Gastos de deterioro de edificaciones',
                            'Gastos de deterioro de maquinarias y equipos',
                            'Gastos de deterioro de mobiliario y equipo',
                            'Gastos de deterioro de vehículos',
                            'Gastos de deterioro por cuentas incobrables',
                            'Gastos de intereses sobre préstamos bancarios',
                            'Gastos de intereses sobre préstamos de terceros'
                        ]:
                            pass
                        elif name == 'Subtotal Gastos de Recursos Humanos' and c_name in [
                            'Gastos de uniformes y dotación al personal'
                        ]:
                            pass
                        elif name == 'Subtotal Gastos de Mercadeo' and c_name in [
                            'Gastos de impresiones de material gráfico',
                            'Gastos de patrocinio y donación'
                        ]:
                            pass
                        elif name == 'Subtotal Gastos de Comercialización y Logistica' and c_name in [
                            'Gastos de comida por viáticos comerciales',
                            'Gastos de hospedaje por viáticos comerciales',
                            'Gastos de pasajes por viáticos comerciales',
                            'Gastos de transporte por viáticos comerciales',
                            'Otros gastos de viáticos comerciales',
                            'Gastos de almacenaje sobre compras no incluídos en el costo',
                            'Gastos de armado de bicicletas no incluídos en el costo',
                            'Gastos de bolsas no incluídos en el costo',
                            'Gastos de embalaje no incluídos en el costo',
                            'Gastos de etiquetas no incluídos en el costo',
                            'Gastos de importación no incluídos en el costo',
                            'Gastos de seguro de mercancía no incluídos en el costo',
                            'Gastos de títulos de propiedad no incluídos en el costo',
                            'Gastos por gasoil',
                            'Gastos por gasolina',
                            'Gastos de alquiler Stand y/o ferias comerciales',
                            'Gastos de otros viáticos Stand y/o ferias comerciales',
                            'Gastos de pasajes Stand y/o ferias comerciales',
                            'Gastos de premiaciones, donaciones Stand y/o ferias comerciales',
                            'Gastos de publicidad Stand y/o ferias comerciales',
                            'Gastos de viáticos comida Stand y/o ferias comerciales',
                            'Gastos de viáticos hospedaje Stand y/o ferias comerciales',
                            'Gastos de viáticos transporte Stand y/o ferias comerciales'
                        ]:
                            pass
                        elif name == 'Gastos de TI+I' and c_name in [
                            'Gastos de dominio de página web',
                            'Gastos de servidores',
                            'Gastos de software tecnológico'
                        ]:
                            pass
                        elif name == 'Otros Gastos no Operacionales' and c_name in [
                            'Deterioro de inventarios',
                            'Faltante de inventarios'
                        ]:
                            pass
                        else:
                            total += subtotales_por_mes[m].get(c_name, 0)
                    j += 1
                subtotales_por_mes[m][name] = total
                if name == 'Subtotal Gastos de Comercialización y Logistica':
                    subtotales_por_mes[m][name] += (
                        subtotales_por_mes[m].get('Gastos de comisiones empleados', 0)
                        + subtotales_por_mes[m].get('Gastos de comisiones por venta de personal externo', 0)
                    )

    # Definición de partidas operativas para Total Ingresos
    op_ing_partidas = ing_p - {
        'Ingresos por alquileres',
        'Ingresos por intereses',
        'Ingresos por comisiones',
        'Ingresos por servicios administrativos',
        'Sobrante en ventas',
        'Sobrante de inventarios',
        'Ganancia en venta de activos',
        'Ganancia por tasa cambiaria',
        'Ganancia por diferencias en pagos'
    }

    valores_calculados_por_mes = {}
    ingresos_ejec_mes = {}
    gastos_ejec_mes = {}
    ingresos_ppto_mes = {}
    gastos_ppto_mes = {}

    for m in MONTHS:
        ingresos_operativos = sum(by_partida.get(p, {}).get(m, 0) for p in op_ing_partidas)
        otros_ing = subtotales_por_mes[m].get('Otros Ingresos no Operacionales', 0)
        costo_ventas = sum(by_partida.get(p, {}).get(m, 0) for p in cos_p)
        utilidad_bruta = ingresos_operativos - costo_ventas

        gastos_operacionales = 0
        for nombre in ['Subtotal Gastos de Administración',
                       'Subtotal Gastos de Recursos Humanos',
                       'Subtotal Gastos de Comercialización y Logistica',
                       'Subtotal Gastos de Mercadeo',
                       'Gastos de TI+I']:
            gastos_operacionales += subtotales_por_mes[m].get(nombre, 0)

        comisiones = 0
        for nombre in ['Gastos de comisiones empleados',
                       'Gastos de comisiones empleados del taller',
                       'Gastos de comisiones por venta de personal externo']:
            comisiones += subtotales_por_mes[m].get(nombre, 0)

        utilidad_despues_comisiones = utilidad_bruta - gastos_operacionales
        utilidad_antes_comisiones = utilidad_despues_comisiones + comisiones

        otros_gastos = subtotales_por_mes[m].get('Otros Gastos no Operacionales', 0)
        gastos_impuestos = subtotales_por_mes[m].get('Gastos de impuestos, tasas y contribuciones', 0)
        gastos_intereses = subtotales_por_mes[m].get('Gastos de intereses sobre préstamos', 0)
        depreciaciones = subtotales_por_mes[m].get('Depreciaciones, deterioro y Amortización', 0)

        ebit = utilidad_bruta - gastos_operacionales + gastos_intereses + gastos_impuestos
        ebitda = ebit + depreciaciones

        utilidad_neta = utilidad_despues_comisiones + otros_ing - otros_gastos
        islr = subtotales_por_mes[m].get('ISLR', 0)
        utilidad_neta_despues_islr = utilidad_neta - islr

        totales_mes = {
            'Total Ingresos Operativos': ingresos_operativos,
            'Otros Ingresos no Operacionales': otros_ing,
            'Total Ingresos': ingresos_operativos,
            'Total Costo de Ventas': costo_ventas,
            'Utilidad Bruta': utilidad_bruta,
            'Total Gastos Operacionales': gastos_operacionales,
            'Utilidad antes de Comisiones por Ventas': utilidad_antes_comisiones,
            'Utilidad después de Comisiones por Ventas': utilidad_despues_comisiones,
            'Otros Gastos no Operacionales': otros_gastos,
            'Total Gastos Operacionales y No Operacionales': gastos_operacionales + otros_gastos,
            'Utilidad antes de Intereses e Impuestos (EBIT)': ebit,
            'Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA)': ebitda,
            'Utilidad Neta': utilidad_neta,
            'ISLR': islr,
            'Utilidad Neta despues de ISLR': utilidad_neta_despues_islr,
            'Utilidad Bruta por Venta de Mercancia y Taller': (
                subtotales_por_mes[m].get('Subtotal Ingresos por Venta de Mercancia', 0)
                + subtotales_por_mes[m].get('Subtotal Ingresos por Taller', 0)
                - subtotales_por_mes[m].get('Subtotal Costo de Ventas por Mercancia', 0)
            ),
            'Utilidad Bruta por Servicios': (
                subtotales_por_mes[m].get('Subtotal Ingresos por Servicios', 0)
                - subtotales_por_mes[m].get('Subtotal Costo de Ventas por Servicios', 0)
            ),
            'Utilidad Bruta por Eventos': (
                subtotales_por_mes[m].get('Subtotal Ingresos por Eventos', 0)
                - subtotales_por_mes[m].get('Subtotal Costo de Ventas por Eventos', 0)
            )
        }

        valores_calculados_por_mes[m] = {**subtotales_por_mes[m], **totales_mes}

        ingresos_ejec_mes[m] = ingresos_operativos
        gastos_ejec_mes[m] = gastos_operacionales + otros_gastos
        ingresos_ppto_mes[m] = sum(by_budget.get(p, {}).get(m, 0) for p in op_ing_partidas)
        gastos_ppto_mes[m] = sum(by_budget.get(p, {}).get(m, 0) for p in gas_p)

    ingresos_prev = sum(by_prev_raw.get(p, 0) for p in op_ing_partidas)
    gastos_prev = sum(by_prev_raw.get(p, 0) for p in gas_p)

    def safe_pct(num, den):
        return round(num / den * 100, 1) if den != 0 else 0

    def safe_var(val, base):
        if base == 0: return None
        return round((val - base) / abs(base) * 100, 1)

    rows = []
    for node in effective:
        partida_name = node['partida_name']
        is_header = node['is_header']
        parent = None
        bold = node['bold']
        bg_color = node['bg_color']
        es_nota = node['es_nota']
        parent_name = node['parent_name']
        indent = node['indent']

        if is_header:
            prev_val = valores_calculados_por_mes.get('DIC', {}).get(partida_name, 0)
        else:
            prev_val = resolve_leaf_value_prev(partida_name, by_prev_raw)

        prev_pct_vtas = safe_pct(prev_val, divisor_prev(partida_name, by_prev_raw, ingresos_prev, ing_p))
        prev_pct_gastos = safe_pct(prev_val, gastos_prev)

        meses_data = []
        acum_ejec = 0
        acum_ppto = 0
        acum_ing_ejec = 0
        acum_ing_ppto = 0
        acum_gas_ejec = 0
        acum_gas_ppto = 0
        val_ejec_mes_anterior = None

        for m in MONTHS:
            month_type = MONTH_TYPES[m]

            if is_header:
                val_ejec = valores_calculados_por_mes[m].get(partida_name, 0)
                val_ppto = 0
            else:
                val_ejec = resolve_leaf_value(partida_name, m, by_partida)
                val_ppto = resolve_leaf_value(partida_name, m, by_budget)

            divisor_vtas_mes = divisor_ejec(partida_name, subtotales_por_mes[m], ingresos_ejec_mes[m], by_partida, m, ing_p)
            divisor_vtas_ppto = divisor_ppto_mes(partida_name, by_budget, m, ingresos_ppto_mes[m], ing_p)

            acum_ejec += val_ejec
            acum_ppto += val_ppto
            acum_ing_ejec += divisor_vtas_mes
            acum_ing_ppto += divisor_vtas_ppto
            acum_gas_ejec += gastos_ejec_mes[m]
            acum_gas_ppto += gastos_ppto_mes[m]

            pct_vtas_ejec = safe_pct(val_ejec, divisor_vtas_mes)
            pct_gastos_ejec = safe_pct(val_ejec, gastos_ejec_mes[m])

            mes_data = {
                'type': month_type,
                'month': m,
                'ejecutado': {
                    'valor': round(val_ejec, 2),
                    'pct_vtas': pct_vtas_ejec,
                    'pct_gastos': pct_gastos_ejec,
                }
            }

            if month_type != 'A':
                mes_data['vari_rel'] = safe_var(val_ejec, val_ejec_mes_anterior) if val_ejec_mes_anterior is not None else None

                if month_type == 'E':  # DIC: AÑO
                    mes_data['anio'] = {
                        'valor': round(acum_ejec, 2),
                        'pct_vtas': safe_pct(acum_ejec, acum_ing_ejec),
                        'pct_gastos': safe_pct(acum_ejec, acum_gas_ejec),
                    }
                else:
                    mes_data['acum_ejecutado'] = {
                        'valor': round(acum_ejec, 2),
                        'pct_vtas': safe_pct(acum_ejec, acum_ing_ejec),
                        'pct_gastos': safe_pct(acum_ejec, acum_gas_ejec),
                    }

                if month_type in ('C', 'D', 'E'):
                    mes_data['acum_ppto'] = {
                        'valor': round(acum_ppto, 2),
                        'pct_vtas': safe_pct(acum_ppto, acum_ing_ppto),
                    }
                    mes_data['var_ppto'] = safe_var(acum_ejec, acum_ppto)

                    if month_type == 'D':  # JUN
                        prom_ejec = acum_ejec / 6
                        prom_ppto = acum_ppto / 6
                        prom_ing_ejec = acum_ing_ejec / 6
                        prom_ing_ppto = acum_ing_ppto / 6
                        prom_gas_ejec = acum_gas_ejec / 6

                        mes_data['prom_6_ejec'] = {
                            'valor': round(prom_ejec, 2),
                            'pct_vtas': safe_pct(prom_ejec, prom_ing_ejec),
                            'pct_gastos': safe_pct(prom_ejec, prom_gas_ejec),
                        }
                        mes_data['prom_6_ppto'] = {
                            'valor': round(prom_ppto, 2),
                            'pct_vtas': safe_pct(prom_ppto, prom_ing_ppto),
                        }
                        mes_data['var_ppto_prom'] = safe_var(prom_ejec, prom_ppto)

            meses_data.append(mes_data)
            val_ejec_mes_anterior = val_ejec

        rows.append({
            'partida': partida_name,
            'is_header': is_header,
            'parent': parent,
            'bold': bold,
            'bg_color': bg_color,
            'es_nota': es_nota,
            'parent_name': parent_name,
            'indent': indent,
            'muestra_pct_gastos': muestra_pct_gastos_map.get(partida_name, False),
            'year_prev': {
                'valor': round(prev_val, 2),
                'pct_vtas': prev_pct_vtas,
                'pct_gastos': prev_pct_gastos,
            },
            'meses': meses_data,
        })

    return {
        'year': year,
        'year_prev': year_prev,
        'unit': unit,
        'rows': rows,
    }


@app.route('/api/eerr/divisa_real', methods=['GET'])
@login_required
def eerr_divisa_real():
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')
    return jsonify(_calcular_eerr_divisa_real(year, unit))


# ── Presupuesto ───────────────────────────────────────────────────────────────

@app.route('/api/budget', methods=['GET'])
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


@app.route('/api/budget', methods=['POST'])
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


@app.route('/api/budget/<year>/<unit>/<month>/<path:partida>', methods=['DELETE'])
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


@app.route('/api/budget/import', methods=['POST'])
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


# ── Comparativa ───────────────────────────────────────────────────────────────

@app.route('/api/comparativa', methods=['GET'])
def comparativa():
    year = int(request.args.get('year', datetime.now().year))
    unit = request.args.get('unit', '')
    prev = year - 1
    db   = get_db()
    ing_p, cos_p, gas_p = get_clasificacion(db)
    uc = "AND unit=?" if unit else ''
    uc_params = [unit] if unit else []

    def totals(yr):
        def s(partidas):
            if not partidas: return 0
            ph = ','.join('?' * len(partidas))
            r  = db.execute(
                f'SELECT SUM(amount) FROM financials WHERE year=? AND partida IN ({ph}) {uc}',
                [str(yr)] + list(partidas) + uc_params
            ).fetchone()
            return r[0] or 0
        i = s(ing_p); c = s(cos_p); g = s(gas_p)
        ub = i - c; un = i - c - g
        return {
            'ingresos': round(i, 2), 'costos': round(c, 2), 'gastos': round(g, 2),
            'utilidad_bruta': round(ub, 2), 'utilidad_neta': round(un, 2),
            'margen_bruto': round(ub / i * 100, 1) if i else 0,
            'margen_neto':  round(un / i * 100, 1) if i else 0
        }

    def by_month(yr):
        rows = []
        for m in MONTHS:
            def sm(partidas):
                if not partidas: return 0
                ph = ','.join('?' * len(partidas))
                r  = db.execute(
                    f'SELECT SUM(amount) FROM financials WHERE year=? AND month=? AND partida IN ({ph}) {uc}',
                    [str(yr), m] + list(partidas) + uc_params
                ).fetchone()
                return r[0] or 0
            i = sm(ing_p); c = sm(cos_p); g = sm(gas_p)
            rows.append({'month': m, 'ingresos': round(i, 2), 'costos': round(c, 2),
                         'gastos': round(g, 2), 'utilidad_neta': round(i - c - g, 2)})
        return rows

    return jsonify({
        'year': year, 'prev': prev,
        'actual': totals(year), 'anterior': totals(prev),
        'meses_actual': by_month(year), 'meses_anterior': by_month(prev)
    })


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

    if mf and mt and mf in MONTHS and mt in MONTHS:
        fi, ti = MONTHS.index(mf), MONTHS.index(mt)
        sel = MONTHS[fi:ti+1] if fi <= ti else MONTHS[fi:] + MONTHS[:ti+1]
    elif mf and mf in MONTHS:
        sel = MONTHS[MONTHS.index(mf):]
    else:
        sel = MONTHS

    divisa = request.args.get('divisa', '') == '1'
    units  = [unit] if unit else UNITS
    exp    = ExcelExporter(year, units, sel, divisa_real=divisa)
    try:
        path = exp.generate()
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    suf   = (f'_{unit}' if unit else '_CONSOLIDADO') + ('_DIVISA_REAL' if divisa else '') + (f'_{mf}-{mt}' if mf and mt else '')
    return send_file(path, as_attachment=True, download_name=f'EERR_ULTRAX_{year}{suf}.xlsx')


@app.route('/api/export/esf', methods=['GET'])
def export_esf():
    from exporters.excel_esf import ESFExporter
    year = request.args.get('year', str(datetime.now().year))
    quarter = request.args.get('quarter', '')
    QUARTER_MESES = {
        '1': ['ENE', 'FEB', 'MAR'],
        '2': ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN'],
        '3': ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEPT'],
        '4': MONTHS,
    }
    meses = QUARTER_MESES.get(quarter, MONTHS)
    exp  = ESFExporter(year, meses)
    path = exp.generate()
    suf  = f'_Q{quarter}' if quarter else ''
    return send_file(path, as_attachment=True, download_name=f'ESF_ULTRAX_{year}{suf}_CONSOLIDADO.xlsx')


@app.route('/api/export/esf/pdf', methods=['GET'])
def export_esf_pdf():
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
    except ImportError:
        return jsonify({'error': 'reportlab no instalado. Ejecuta: pip install reportlab'}), 500

    from engine import ESF_STRUCTURE
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')
    db   = get_db()
    result_quarters, _ = compute_esf(db, year, unit)

    # Headers de sección que NO tienen un total propio en result_quarters['totales']
    section_only = {'ACTIVOS NO CORRIENTES', 'PASIVOS CORRIENTES', 'PASIVOS NO CORRIENTES', 'PATRIMONIO'}
    # Headers "grandes" (resaltado fuerte)
    grand = {'TOTAL ACTIVOS', 'TOTAL PASIVOS Y PATRIMONIO', 'TOTAL PASIVOS', 'TOTAL PATRIMONIO'}

    def cell_val(partida, is_header, q):
        tot = result_quarters[q]['totales']
        if is_header:
            return tot.get(partida)            # None si es header de sección sin total
        return result_quarters[q]['partidas'].get(partida, 0)

    def fmt_n(v):
        if v is None:        return '—'
        if abs(v) >= 1e6:    return f'${v/1e6:.1f}M'
        if abs(v) >= 1e3:    return f'${v/1e3:.1f}K'
        return f'${v:,.0f}'

    HDR = colors.HexColor('#1e3a5f'); BG = colors.HexColor('#f8fafc')
    GRY = colors.HexColor('#e2e8f0'); SEC = colors.HexColor('#dbe4ef')

    tmp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    tmp = tmp_file.name
    tmp_file.close()
    doc = SimpleDocTemplate(tmp, pagesize=landscape(A4), leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    title_style = ParagraphStyle('T', fontSize=14, fontName='Helvetica-Bold', spaceAfter=4, alignment=TA_CENTER)
    sub_style   = ParagraphStyle('S', fontSize=9, fontName='Helvetica', textColor=colors.HexColor('#64748b'), spaceAfter=12, alignment=TA_CENTER)

    label = unit if unit else 'Consolidado — Todas las Unidades'
    story = [
        Paragraph(f'ULTRAX — Estado de Situación Financiera {year}', title_style),
        Paragraph(label + f'  |  Generado {datetime.now().strftime("%d/%m/%Y %H:%M")}', sub_style),
    ]

    data = [['Partida', 'Q1 (Ene–Mar)', 'Q2 (Abr–Jun)', 'Q3 (Jul–Sep)', 'Q4 (Oct–Dic)']]
    style = [
        ('BACKGROUND',(0,0),(-1,0),HDR), ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'), ('FONTSIZE',(0,0),(-1,-1),8),
        ('ALIGN',(1,0),(-1,-1),'RIGHT'), ('ALIGN',(0,0),(0,-1),'LEFT'),
        ('GRID',(0,0),(-1,-1),0.4,GRY), ('TOPPADDING',(0,0),(-1,-1),3.5), ('BOTTOMPADDING',(0,0),(-1,-1),3.5),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ]

    ri = 0
    for partida, is_header, section in ESF_STRUCTURE:
        ri += 1
        vals = [fmt_n(cell_val(partida, is_header, q)) for q in [1, 2, 3, 4]]
        data.append([partida] + vals)
        if is_header and partida in grand:
            style += [('BACKGROUND',(0,ri),(-1,ri),HDR), ('TEXTCOLOR',(0,ri),(-1,ri),colors.white),
                      ('FONTNAME',(0,ri),(-1,ri),'Helvetica-Bold')]
        elif is_header and (partida in section_only or partida.startswith('TOTAL ')):
            style += [('BACKGROUND',(0,ri),(-1,ri),SEC), ('FONTNAME',(0,ri),(-1,ri),'Helvetica-Bold')]
        elif is_header:   # subtotales 'Total ...'
            style += [('FONTNAME',(0,ri),(-1,ri),'Helvetica-Bold'), ('BACKGROUND',(0,ri),(-1,ri),BG)]

    t = Table(data, colWidths=[10*cm] + [4*cm]*4, repeatRows=1)
    t.setStyle(TableStyle(style))
    story.append(t)

    doc.build(story)
    suf = f'_{unit}' if unit else '_CONSOLIDADO'
    return send_file(tmp, as_attachment=True, download_name=f'ESF_ULTRAX_{year}{suf}.pdf',
                     mimetype='application/pdf')


@app.route('/api/export/pdf', methods=['GET'])
def export_pdf():
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    except ImportError:
        return jsonify({'error': 'reportlab no instalado. Ejecuta: pip install reportlab'}), 500

    year  = request.args.get('year', str(datetime.now().year))
    unit  = request.args.get('unit', '')
    db    = get_db()
    ing_p, cos_p, gas_p = get_clasificacion(db)
    uc    = "AND unit=?" if unit else ''
    uc_params = [unit] if unit else []

    def sm(partidas, month=''):
        if not partidas: return 0
        ph    = ','.join('?' * len(partidas))
        extra = f"AND month='{month}'" if month else ''
        r     = db.execute(
            f'SELECT SUM(amount) FROM financials WHERE year=? AND partida IN ({ph}) {uc} {extra}',
            [year] + list(partidas) + uc_params
        ).fetchone()
        return r[0] or 0

    tmp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    tmp = tmp_file.name
    tmp_file.close()
    doc = SimpleDocTemplate(tmp, pagesize=landscape(A4), leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles    = getSampleStyleSheet()
    title_style = ParagraphStyle('T', fontSize=14, fontName='Helvetica-Bold', spaceAfter=4, alignment=TA_CENTER)
    sub_style   = ParagraphStyle('S', fontSize=9,  fontName='Helvetica', textColor=colors.HexColor('#64748b'), spaceAfter=12, alignment=TA_CENTER)

    BLU = colors.HexColor('#2563eb'); GRN = colors.HexColor('#059669')
    RED = colors.HexColor('#dc2626'); BG  = colors.HexColor('#f8fafc')
    HDR = colors.HexColor('#1e3a5f'); GRY = colors.HexColor('#e2e8f0')

    def fmt_n(v):
        if v is None: return '—'
        if abs(v) >= 1e6: return f'${v/1e6:.1f}M'
        if abs(v) >= 1e3: return f'${v/1e3:.1f}K'
        return f'${v:,.0f}'

    story = []
    label = unit if unit else 'Consolidado — Todas las Unidades'
    story.append(Paragraph(f'ULTRAX — Estado de Resultados {year}', title_style))
    story.append(Paragraph(label + f'  |  Generado {datetime.now().strftime("%d/%m/%Y %H:%M")}', sub_style))

    headers = ['Mes','Ingresos','Costos','Util.Bruta','Gastos','Util.Neta','Mg.Bruto%','Mg.Neto%']
    rows = [headers]
    for m in MONTHS:
        i = sm(ing_p, m); c = sm(cos_p, m); g = sm(gas_p, m); ub = i - c; un = i - c - g
        mb = ub/i*100 if i else 0; mn = un/i*100 if i else 0
        rows.append([m, fmt_n(i), fmt_n(c), fmt_n(ub), fmt_n(g), fmt_n(un), f'{mb:.1f}%', f'{mn:.1f}%'])
    ti = sm(ing_p); tc = sm(cos_p); tg = sm(gas_p); tub = ti-tc; tun = ti-tc-tg
    tmb = tub/ti*100 if ti else 0; tmn = tun/ti*100 if ti else 0
    rows.append(['TOTAL', fmt_n(ti), fmt_n(tc), fmt_n(tub), fmt_n(tg), fmt_n(tun), f'{tmb:.1f}%', f'{tmn:.1f}%'])

    col_w = [1.5*cm] + [2.8*cm]*7
    t  = Table(rows, colWidths=col_w, repeatRows=1)
    ts = TableStyle([
        ('BACKGROUND',(0,0),(-1,0),HDR), ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'), ('FONTSIZE',(0,0),(-1,0),8),
        ('ALIGN',(0,0),(-1,-1),'RIGHT'), ('ALIGN',(0,0),(0,-1),'CENTER'),
        ('FONTNAME',(0,1),(-1,-2),'Helvetica'), ('FONTSIZE',(0,1),(-1,-2),8),
        ('BACKGROUND',(0,-1),(-1,-1),colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR',(0,-1),(-1,-1),colors.white), ('FONTNAME',(0,-1),(-1,-1),'Helvetica-Bold'),
        ('ROWBACKGROUNDS',(0,1),(-1,-2),[colors.white, BG]),
        ('GRID',(0,0),(-1,-1),0.4,GRY), ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5),
    ])
    for ri, row in enumerate(rows[1:-1], 1):
        un_val = sm(ing_p, MONTHS[ri-1]) - sm(cos_p, MONTHS[ri-1]) - sm(gas_p, MONTHS[ri-1])
        ts.add('TEXTCOLOR', (5, ri), (5, ri), GRN if un_val >= 0 else RED)
    t.setStyle(ts)
    story.append(t)

    if not unit:
        story.append(Spacer(1, 0.6*cm))
        u_rows = [['Unidad','Ingresos','Costos','Gastos','Util.Neta','Mg.Bruto%','Mg.Neto%']]
        for u in UNITS:
            def us(ps):
                if not ps: return 0
                ph = ','.join('?'*len(ps))
                r  = db.execute(f'SELECT SUM(amount) FROM financials WHERE year=? AND unit=? AND partida IN ({ph})',
                                [year, u] + list(ps)).fetchone()
                return r[0] or 0
            i = us(ing_p); c = us(cos_p); g = us(gas_p); ub = i-c; un2 = i-c-g
            if i or c or g:
                u_rows.append([u, fmt_n(i), fmt_n(c), fmt_n(g), fmt_n(un2),
                               f'{ub/i*100:.1f}%' if i else '—', f'{un2/i*100:.1f}%' if i else '—'])
        ut = Table(u_rows, colWidths=[3*cm]+[3.2*cm]*6, repeatRows=1)
        ut.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),HDR), ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'), ('FONTSIZE',(0,0),(-1,-1),8),
            ('ALIGN',(0,0),(-1,-1),'RIGHT'), ('ALIGN',(0,0),(0,-1),'LEFT'),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white, BG]),
            ('GRID',(0,0),(-1,-1),0.4,GRY), ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5),
        ]))
        story.append(Paragraph('Resumen por Unidad de Negocio',
                                ParagraphStyle('H2', fontSize=11, fontName='Helvetica-Bold', spaceAfter=6, spaceBefore=4)))
        story.append(ut)

    doc.build(story)
    suf = f'_{unit}' if unit else '_CONSOLIDADO'
    return send_file(tmp, as_attachment=True, download_name=f'ULTRAX_{year}{suf}.pdf', mimetype='application/pdf')


# ── Data helpers ──────────────────────────────────────────────────────────────

@app.route('/api/data', methods=['GET'])
def get_data():
    year        = request.args.get('year', str(datetime.now().year))
    unit        = request.args.get('unit', '')
    report_type = request.args.get('report_type', '')
    db          = get_db()
    q      = 'SELECT * FROM financials_detail WHERE year=?'
    params = [year]
    if unit:        q += ' AND unit=?';        params.append(unit)
    if report_type: q += ' AND report_type=?'; params.append(report_type)
    rows = db.execute(q + ' ORDER BY unit, month, odoo_code', params).fetchall()
    # Marcar filas que tienen historial de override
    result = []
    for r in rows:
        row = dict(r)
        log = db.execute(
            '''SELECT valor_anterior, valor_nuevo, timestamp
               FROM financials_override_log
               WHERE year=? AND month=? AND unit=? AND odoo_code=?
               ORDER BY id DESC LIMIT 1''',
            (row['year'], row['month'], row['unit'], row['odoo_code'])
        ).fetchone()
        row['has_override'] = log is not None
        row['override_last'] = dict(log) if log else None
        result.append(row)
    return jsonify(result)


@app.route('/api/data/override', methods=['POST'])
@admin_required
def data_override():
    body        = request.get_json()
    year        = body.get('year')
    month       = body.get('month')
    unit        = body.get('unit')
    odoo_code   = body.get('odoo_code')
    valor_nuevo = body.get('valor_nuevo')
    if None in (year, month, unit, odoo_code, valor_nuevo):
        return jsonify({'error': 'Faltan campos obligatorios'}), 400
    db = get_db()
    # Leer valor actual
    row = db.execute(
        'SELECT amount_sign, report_type, partida FROM financials_detail WHERE year=? AND month=? AND unit=? AND odoo_code=?',
        (year, month, unit, odoo_code)
    ).fetchone()
    if not row:
        return jsonify({'error': 'Registro no encontrado'}), 404
    valor_anterior = row['amount_sign']
    report_type    = row['report_type']
    partida        = row['partida']
    # Actualizar financials_detail
    db.execute(
        'UPDATE financials_detail SET amount_sign=? WHERE year=? AND month=? AND unit=? AND odoo_code=?',
        (valor_nuevo, year, month, unit, odoo_code)
    )
    # Actualizar en cascada financials o esf_data
    if report_type == 'eerr':
        db.execute(
            '''UPDATE financials SET amount=(
                SELECT SUM(amount_sign) FROM financials_detail
                WHERE year=? AND month=? AND unit=? AND partida=? AND report_type='eerr'
               ) WHERE year=? AND month=? AND unit=? AND partida=?''',
            (year, month, unit, partida, year, month, unit, partida)
        )
    else:
        row_esf = db.execute(
            'SELECT quarter FROM financials_detail WHERE year=? AND month=? AND unit=? AND odoo_code=?',
            (year, month, unit, odoo_code)
        ).fetchone()
        if row_esf:
            quarter = row_esf['quarter']
            db.execute(
                '''UPDATE esf_data SET amount=(
                    SELECT SUM(amount_sign) FROM financials_detail
                    WHERE year=? AND unit=? AND partida=? AND report_type='esf' AND quarter=?
                   ) WHERE year=? AND quarter=? AND unit=? AND partida=?''',
                (year, unit, partida, quarter, year, quarter, unit, partida)
            )
    # Guardar en log
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.execute(
        '''INSERT INTO financials_override_log (year, month, unit, odoo_code, report_type, valor_anterior, valor_nuevo, timestamp)
           VALUES (?,?,?,?,?,?,?,?)''',
        (year, month, unit, odoo_code, report_type, valor_anterior, valor_nuevo, ts)
    )
    db.commit()
    return jsonify({'ok': True, 'valor_anterior': valor_anterior, 'valor_nuevo': valor_nuevo})


@app.route('/api/data/override/undo', methods=['POST'])
@admin_required
def data_override_undo():
    body      = request.get_json()
    year      = body.get('year')
    month     = body.get('month')
    unit      = body.get('unit')
    odoo_code = body.get('odoo_code')
    if None in (year, month, unit, odoo_code):
        return jsonify({'error': 'Faltan campos obligatorios'}), 400
    db = get_db()
    # Último registro del log
    log = db.execute(
        '''SELECT id, valor_anterior, report_type FROM financials_override_log
           WHERE year=? AND month=? AND unit=? AND odoo_code=?
           ORDER BY id DESC LIMIT 1''',
        (year, month, unit, odoo_code)
    ).fetchone()
    if not log:
        return jsonify({'error': 'No hay override que deshacer'}), 404
    valor_revertido = log['valor_anterior']
    report_type     = log['report_type']
    # Leer partida
    row = db.execute(
        'SELECT partida, quarter FROM financials_detail WHERE year=? AND month=? AND unit=? AND odoo_code=?',
        (year, month, unit, odoo_code)
    ).fetchone()
    partida = row['partida']
    quarter = row['quarter']
    # Revertir financials_detail
    db.execute(
        'UPDATE financials_detail SET amount_sign=? WHERE year=? AND month=? AND unit=? AND odoo_code=?',
        (valor_revertido, year, month, unit, odoo_code)
    )
    # Revertir en cascada
    if report_type == 'eerr':
        db.execute(
            '''UPDATE financials SET amount=(
                SELECT SUM(amount_sign) FROM financials_detail
                WHERE year=? AND month=? AND unit=? AND partida=? AND report_type='eerr'
               ) WHERE year=? AND month=? AND unit=? AND partida=?''',
            (year, month, unit, partida, year, month, unit, partida)
        )
    else:
        db.execute(
            '''UPDATE esf_data SET amount=(
                SELECT SUM(amount_sign) FROM financials_detail
                WHERE year=? AND unit=? AND partida=? AND report_type='esf' AND quarter=?
               ) WHERE year=? AND quarter=? AND unit=? AND partida=?''',
            (year, unit, partida, quarter, year, quarter, unit, partida)
        )
    # Eliminar el log revertido
    db.execute('DELETE FROM financials_override_log WHERE id=?', (log['id'],))
    db.commit()
    return jsonify({'ok': True, 'valor_revertido': valor_revertido})

@app.route('/api/years', methods=['GET'])
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


# ── Backup / Restore ──────────────────────────────────────────────────────────

@app.route('/api/backup', methods=['GET'])
def backup():
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    return send_file(DB_PATH, as_attachment=True, download_name=f'ultrax_backup_{ts}.db',
                     mimetype='application/octet-stream')

@app.route('/api/restore', methods=['POST'])
@admin_required
def restore():
    file = request.files.get('file')
    if not file: return jsonify({'error': 'No se envió archivo'}), 400
    if not file.filename.endswith('.db'): return jsonify({'error': 'El archivo debe ser .db'}), 400
    tmp_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    tmp = tmp_file.name
    tmp_file.close()
    try:
        file.save(tmp)
        conn   = sqlite3.connect(tmp)
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        conn.close()
        if not {'financials', 'mapping', 'history'}.issubset(tables):
            os.remove(tmp)
            return jsonify({'error': f'DB inválida. Tablas: {tables}'}), 400
        shutil.copy2(DB_PATH, DB_PATH + '.bk')
        shutil.move(tmp, DB_PATH)
        return jsonify({'ok': True, 'message': 'Base de datos restaurada correctamente'})
    except Exception as e:
        if os.path.exists(tmp): os.remove(tmp)
        return jsonify({'error': str(e)}), 500



def get_grouped_partidas_v2(db, report_type='eerr'):
    """
    Retorna grupos basados en mapping_groups_v2 (Matriz Maestra).
    """
    rows = db.execute(
        '''SELECT mg.group_name, m.partida
           FROM mapping_groups_v2 mg
           JOIN mapping m ON mg.odoo_code = m.odoo_code
           WHERE mg.report_type = ?
           ORDER BY mg.display_order''',
        [report_type]
    ).fetchall()

    groups = {}
    grouped_partidas = set()
    for r in rows:
        gname = r['group_name']
        partida = r['partida']
        groups.setdefault(gname, []).append(partida)
        grouped_partidas.add(partida)
    return groups, grouped_partidas

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
    else:
        year = request.args.get('year', str(datetime.now().year))
        month = request.args.get('month', '')
        unit = request.args.get('unit', '')
        tipo = request.args.get('tipo', 'eerr')
        prompt_text = request.args.get('prompt_text')

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
    alcance = unit if unit else "Consolidado grupo"
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
    if tipo in ['eerr', 'eerr_divisa', 'completo']:
        lines.append('## ESTADO DE RESULTADOS')
        lines.append('')
        data = eerr_completo_v2_ui_adapter(year, unit)
        rows = data.get('rows', [])

        meses_disponibles = []
        if rows:
            meses_disponibles = [m['month'] for m in rows[0].get('meses', [])]
            if month:
                meses_disponibles = [m for m in meses_disponibles if m == month.upper()]

        # Encabezado tabla
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
                valores = ' | '.join(
                    f"{meses_data.get(m, 0):,.0f}" for m in meses_disponibles
                )
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
        result_quarters, quarters_available = compute_esf(db, year, unit)

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

    # ── COMPARATIVA POR UNIDAD ────────────────────────────────────────────────
    if tipo == 'comparativa':
        UNIDADES_COMPARABLES = {'Rodeo', 'Barinas', 'Naranjos', 'PiedeMonte', 'Terracota'}

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
            data_u = eerr_completo_v2_ui_adapter(year, u)
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
