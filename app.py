from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
import sqlite3, os, shutil, tempfile, secrets
from datetime import datetime
from engine import OdooParser, ExcelExporter, ESFExporter, MONTH_TO_QUARTER
from db import init_db, migrate_db, get_db, close_db, DB_PATH
from auth import login_required, admin_required, verify_password, get_current_user

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = secrets.token_hex(32)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Registrar función de cierre de base de datos
app.teardown_appcontext(close_db)

UNITS  = ['Rodeo', 'PiedeMonte', 'Terracota', 'Ucafe', 'Barinas', 'Naranjos']
MONTHS = ['ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEPT','OCT','NOV','DIC']

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
    unit    = request.form.get('unit')
    month   = request.form.get('month')
    year    = request.form.get('year', str(datetime.now().year))
    is_esf  = request.form.get('is_esf', 'false').lower() == 'true'

    if not all([file, unit, month]):
        return jsonify({'error': 'Faltan parámetros'}), 400

    path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(path)

    try:
        parser   = OdooParser(path)
        accounts = parser.parse()
        db       = get_db()

        inserted_fin, inserted_esf, skipped, unmapped = 0, 0, 0, []
        quarter = MONTH_TO_QUARTER.get(month, 1)

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
        db.execute(
            'INSERT INTO history (year, month, unit, inserted) VALUES (?,?,?,?)',
            (year, month, unit, inserted_fin + inserted_esf)
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
        db.commit()
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    db   = get_db()
    ing_p, cos_p, gas_p = get_clasificacion(db)
    uc = '' if unit == 'TODAS' else f"AND unit='{unit}'"

    def by_month(partidas):
        if not partidas: return {}
        ph   = ','.join('?' * len(partidas))
        rows = db.execute(
            f'SELECT month, SUM(amount) t FROM financials WHERE year=? AND partida IN ({ph}) {uc} GROUP BY month',
            [year] + list(partidas)
        ).fetchall()
        return {r['month']: r['t'] or 0 for r in rows}

    def u_sum(partidas, uname):
        if not partidas: return 0
        ph  = ','.join('?' * len(partidas))
        row = db.execute(
            f'SELECT SUM(amount) FROM financials WHERE year=? AND unit=? AND partida IN ({ph})',
            [year, uname] + list(partidas)
        ).fetchone()
        return row[0] or 0

    im, cm, gm = by_month(ing_p), by_month(cos_p), by_month(gas_p)

    por_unidad = []
    for u in UNITS:
        i = u_sum(ing_p, u); c = u_sum(cos_p, u); g = u_sum(gas_p, u)
        if i or c or g:
            ub = i - c; un = i - c - g
            por_unidad.append({
                'unit': u, 'ingresos': round(i, 2), 'costos': round(c, 2), 'gastos': round(g, 2),
                'utilidad_bruta': round(ub, 2), 'utilidad_neta': round(un, 2),
                'margen_bruto': round(ub / i * 100, 1) if i else 0,
                'margen_neto': round(un / i * 100, 1) if i else 0,
                'ratio_costo': round(c / i * 100, 1) if i else 0,
                'ratio_gasto': round(g / i * 100, 1) if i else 0
            })

    top_gastos = []
    if gas_p:
        rows = db.execute(
            f'SELECT partida, SUM(amount) t FROM financials WHERE year=? AND partida IN ({",".join("?"*len(gas_p))}) {uc} GROUP BY partida ORDER BY t DESC LIMIT 10',
            [year] + list(gas_p)
        ).fetchall()
        top_gastos = [dict(r) for r in rows]

    cat_gastos = []
    if gas_p:
        for cat, kws in GASTO_CATS.items():
            matching = [p for p in gas_p if any(k.lower() in p.lower() for k in kws)]
            if matching:
                ph = ','.join('?' * len(matching))
                t  = db.execute(
                    f'SELECT SUM(amount) FROM financials WHERE year=? AND partida IN ({ph}) {uc}',
                    [year] + matching
                ).fetchone()[0] or 0
                if t: cat_gastos.append({'categoria': cat, 'total': round(t, 2)})

    months_data = []
    for m in MONTHS:
        i = im.get(m, 0); c = cm.get(m, 0); g = gm.get(m, 0); ub = i - c; un = i - c - g
        months_data.append({
            'month': m, 'ingresos': round(i, 2), 'costos': round(c, 2), 'gastos': round(g, 2),
            'utilidad_bruta': round(ub, 2), 'utilidad_neta': round(un, 2),
            'margen_bruto': round(ub / i * 100, 1) if i else 0,
            'margen_neto': round(un / i * 100, 1) if i else 0,
            'ratio_costo': round(c / i * 100, 1) if i else 0,
            'ratio_gasto': round(g / i * 100, 1) if i else 0
        })

    pe = None
    if unit != 'TODAS':
        ti = sum(m['ingresos'] for m in months_data)
        tc = sum(m['costos']   for m in months_data)
        tg = sum(m['gastos']   for m in months_data)
        if ti > 0:
            mc = 1 - tc / ti
            if mc > 0:
                pev = tg / mc
                pe  = {
                    'pe_ingresos': round(pev, 2), 'ingresos_actuales': round(ti, 2),
                    'cobertura_pct': round(ti / pev * 100, 1) if pev else 0,
                    'margen_contribucion_pct': round(mc * 100, 1)
                }

    loaded = db.execute(
        'SELECT DISTINCT unit, month FROM financials WHERE year=? ORDER BY unit, month', (year,)
    ).fetchall()

    # Incluir indicadores avanzados si hay datos ESF
    indicadores_avanzados = compute_indicadores(db, year, unit if unit != 'TODAS' else '')

    return jsonify({
        'months': months_data, 'por_unidad': por_unidad, 'top_gastos': top_gastos,
        'cat_gastos': cat_gastos, 'loaded': [{'unit': r['unit'], 'month': r['month']} for r in loaded],
        'punto_equilibrio': pe, 'indicadores_avanzados': indicadores_avanzados
    })


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

    uc = '' if (not unit or unit == 'TODAS') else f"AND unit='{unit}'"
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
        [year] + targets
    ).fetchall()
    by_month = {r['month']: r['t'] or 0 for r in mrows}
    meses    = [{'month': m, 'amount': round(by_month.get(m, 0), 2)} for m in MONTHS]
    total    = round(sum(by_month.values()), 2)

    prows = db.execute(
        f'SELECT partida, SUM(amount) t FROM financials WHERE year=? AND partida IN ({ph}) {uc} GROUP BY partida ORDER BY t DESC',
        [year] + targets
    ).fetchall()
    partidas = [{'partida': r['partida'], 'total': round(r['t'] or 0, 2)} for r in prows if (r['t'] or 0)]

    tot_gastos = 0
    if gas_p:
        phg = ','.join('?' * len(gas_p))
        tot_gastos = db.execute(
            f'SELECT SUM(amount) FROM financials WHERE year=? AND partida IN ({phg}) {uc}',
            [year] + list(gas_p)
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

    uc = '' if (not unit or unit == 'TODAS') else f"AND unit='{unit}'"
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
                    [year] + list(ps)
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
                    [year] + list(ps)
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
                    [year] + list(ps)
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
                        [year] + list(ps)
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
    uc    = f"AND unit='{unit}'" if unit else ''
    mc    = f"AND month='{month}'" if month else ''

    rows = db.execute(
        f'SELECT partida, SUM(amount) total FROM financials WHERE year=? {uc} {mc} GROUP BY partida',
        [year]
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

    uc = f"AND unit='{unit}'" if unit else ''
    ph_m = ','.join('?' * len(active_months))

    # Totales por partida y mes
    rows = db.execute(
        f'''SELECT partida, month, SUM(amount) amount
            FROM financials
            WHERE year=? {uc} AND month IN ({ph_m})
            GROUP BY partida, month''',
        [year] + active_months
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


# ── Funciones auxiliares para cálculo de subtotales EERR ──────────────────────

def calcular_subtotales_jerarquicos(eerr_structure, by_partida, month, ing_p, cos_p, gas_p, groups, grouped_partidas):
    """
    Calcula todos los subtotales jerárquicos para un mes dado.
    Usa el campo level (índice 5) para determinar el scope de cada header:
    solo hace break cuando encuentra un header del mismo nivel o superior.
    level: 0=totales principales, 1=subtotales, 2=agrupadores internos, 3=partidas hoja
    """
    subtotales = {}
    all_partidas = ing_p | cos_p | gas_p

    for i, item in enumerate(eerr_structure):
        partida_name = item[0]
        is_header = item[1]
        current_level = item[5] if len(item) > 5 else 0

        if not is_header:
            continue

        total = 0
        j = i + 1

        while j < len(eerr_structure):
            child_item = eerr_structure[j]
            child_name = child_item[0]
            child_is_header = child_item[1]
            child_level = child_item[5] if len(child_item) > 5 else 0

            # Solo cortar cuando encontramos header del mismo nivel o superior
            if child_is_header and child_level <= current_level:
                break

            # Sumar solo partidas hoja (no header)
            if not child_is_header:
                if child_name in groups:
                    matching = groups[child_name]
                else:
                    matching = [p for p in all_partidas
                               if p.lower() == child_name.lower()
                               and p not in grouped_partidas]

                for p in matching:
                    total += by_partida.get(p, {}).get(month, 0)

            j += 1

        subtotales[partida_name] = total

    return subtotales


def calcular_totales_especiales(subtotales, by_partida, month, ing_p, cos_p, gas_p):
    """
    Calcula totales especiales con lógicas específicas.
    IMPORTANTE: los valores calculados aquí deben aplicarse DESPUÉS de
    resultados.update(subtotales) para evitar que sean sobrescritos.
    """
    totales = {}

    # 1. Total Ingresos Operativos (solo cuentas 4.x)
    totales['Total Ingresos Operativos'] = sum(by_partida.get(p, {}).get(month, 0) for p in ing_p)

    # 2. Otros Ingresos no Operacionales (ya calculado por subtotales)
    otros_ing = subtotales.get('Otros Ingresos no Operacionales', 0)
    totales['Otros Ingresos no Operacionales'] = otros_ing

    # 3. Total Ingresos = Operativos + No Operativos
    totales['Total Ingresos'] = totales['Total Ingresos Operativos'] + otros_ing

    # 4. Total Costo de Ventas
    totales['Total Costo de Ventas'] = sum(by_partida.get(p, {}).get(month, 0) for p in cos_p)

    # 5. Utilidad Bruta = Ingresos Operativos - Costos
    totales['Utilidad Bruta'] = totales['Total Ingresos Operativos'] - totales['Total Costo de Ventas']

    # 6. Total Gastos Operacionales = suma de subtotales operacionales
    gastos_operacionales = 0
    for nombre in ['Subtotal Gastos de Administración',
                   'Subtotal Gastos de Recursos Humanos',
                   'Subtotal Gastos de Comercialización y Logistica',
                   'Subtotal Gastos de Mercadeo',
                   'Subtotal Gastos de TI+I']:
        gastos_operacionales += subtotales.get(nombre, 0)
    totales['Total Gastos Operacionales'] = gastos_operacionales

    # 7. Utilidad antes de Comisiones
    totales['Utilidad antes de Comisiones por Ventas'] = (
        totales['Utilidad Bruta'] - totales['Total Gastos Operacionales']
    )

    # 8. Comisiones (nombres reales en la BD según new_eerr_structure.py)
    comisiones = 0
    for nombre in ['Gastos de comisiones empleados',
                   'Gastos de comisiones empleados del taller',
                   'Gastos de comisiones por venta de personal externo']:
        comisiones += subtotales.get(nombre, 0)

    # 9. Utilidad después de Comisiones
    totales['Utilidad después de Comisiones por Ventas'] = (
        totales['Utilidad antes de Comisiones por Ventas'] - comisiones
    )

    # 10. Otros Gastos no Operacionales (ya calculado por subtotales)
    totales['Otros Gastos no Operacionales'] = subtotales.get('Otros Gastos no Operacionales', 0)

    # 11. Utilidad Neta
    totales['Utilidad Neta'] = (
        totales['Utilidad después de Comisiones por Ventas'] -
        totales['Otros Gastos no Operacionales'] +
        otros_ing
    )

    # 12. ISLR
    totales['ISLR'] = subtotales.get('ISLR', 0)

    # 13. Utilidad Neta después de ISLR
    totales['Utilidad Neta despues de ISLR'] = totales['Utilidad Neta'] - totales['ISLR']

    return totales


@app.route('/api/eerr/completo', methods=['GET'])
def eerr_completo():
    """
    Estado de Resultados COMPLETO con estructura exacta del Excel.
    Tipos de mes:
    - ENE: Monto, %V, %G (3 cols)
    - FEB, ABR, MAY, JUL, AGO, OCT, NOV: + Vari Rel, ACUM EJEC, %V, %G (7 cols)
    - MAR, SEP: + ACUM PPTO, %V, Var PPTO (10 cols)
    - JUN: + PROM 6 EJEC, %V, %G, PROM 6 PPTO, %V, Var PPTO (16 cols)
    - DIC: Monto, %V, %G, Vari Rel, AÑO, %V, %G, ACUM PPTO, %V, Var PPTO (10 cols)
    """
    from engine import EERR_STRUCTURE

    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')
    db   = get_db()

    year_prev = str(int(year) - 1)
    uc = f"AND unit='{unit}'" if unit else ''

    # Mapeo de estructura por mes
    MONTH_TYPES = {
        'ENE': 'A',  # 3 cols
        'FEB': 'B',  # 7 cols
        'MAR': 'C',  # 10 cols
        'ABR': 'B',
        'MAY': 'B',
        'JUN': 'D',  # 16 cols
        'JUL': 'B',
        'AGO': 'B',
        'SEPT': 'C',  # 10 cols
        'OCT': 'B',
        'NOV': 'B',
        'DIC': 'E',  # 10 cols
    }

    # Leer datos año actual por partida y mes
    rows_curr = db.execute(
        f'''SELECT partida, month, SUM(amount) amount FROM financials
            WHERE year=? {uc} GROUP BY partida, month''',
        [year]
    ).fetchall()

    by_partida = {}
    for r in rows_curr:
        by_partida.setdefault(r['partida'], {})[r['month']] = r['amount']

    # Leer datos año anterior (total anual por partida)
    rows_prev = db.execute(
        f'''SELECT partida, SUM(amount) amount FROM financials
            WHERE year=? {uc} GROUP BY partida''',
        [year_prev]
    ).fetchall()
    by_prev = {r['partida']: r['amount'] for r in rows_prev}

    # Leer presupuesto por partida y mes
    rows_budget = db.execute(
        f'''SELECT partida, month, SUM(amount) amount FROM budget
            WHERE year=? {uc} GROUP BY partida, month''',
        [year]
    ).fetchall()
    by_budget = {}
    for r in rows_budget:
        by_budget.setdefault(r['partida'], {})[r['month']] = r['amount']

    # Clasificación
    ing_p, cos_p, gas_p = get_clasificacion(db)

    # Obtener grupos de presentación
    groups, grouped_partidas = get_grouped_partidas(db, 'eerr')

    # Totales de ingresos y gastos por mes
    ingresos_ejec_mes = {}
    gastos_ejec_mes = {}
    ingresos_ppto_mes = {}
    gastos_ppto_mes = {}

    # Totales año anterior
    ingresos_prev = sum(by_prev.get(p, 0) for p in ing_p)
    gastos_prev = sum(by_prev.get(p, 0) for p in gas_p)

    for m in MONTHS:
        ingresos_ejec_mes[m] = sum(by_partida.get(p, {}).get(m, 0) for p in ing_p)
        gastos_ejec_mes[m] = sum(by_partida.get(p, {}).get(m, 0) for p in gas_p)
        ingresos_ppto_mes[m] = sum(by_budget.get(p, {}).get(m, 0) for p in ing_p)
        gastos_ppto_mes[m] = sum(by_budget.get(p, {}).get(m, 0) for p in gas_p)

    def safe_pct(num, den):
        return round(num / den * 100, 1) if den != 0 else 0

    def safe_var(val, base):
        """Calcula variación relativa porcentual."""
        if base == 0:
            return None
        return round((val - base) / abs(base) * 100, 1)

    # PRE-CALCULAR SUBTOTALES PARA TODOS LOS MESES
    subtotales_por_mes = {}
    totales_por_mes = {}
    for m in MONTHS:
        # Paso 1: Calcular subtotales jerárquicos
        subtotales_por_mes[m] = calcular_subtotales_jerarquicos(
            EERR_STRUCTURE, by_partida, m, ing_p, cos_p, gas_p, groups, grouped_partidas
        )
        # Paso 2: Calcular totales especiales
        totales_por_mes[m] = calcular_totales_especiales(
            subtotales_por_mes[m], by_partida, m, ing_p, cos_p, gas_p
        )

    # Combinar subtotales y totales
    valores_calculados_por_mes = {}
    for m in MONTHS:
        valores_calculados_por_mes[m] = {**subtotales_por_mes[m], **totales_por_mes[m]}

    # Construir filas según EERR_STRUCTURE
    rows = []
    for item in EERR_STRUCTURE:
        partida_name = item[0]
        is_header = item[1]
        parent = item[2] if len(item) > 2 else None
        bold = item[3] if len(item) > 3 else False
        bg_color = item[4] if len(item) > 4 else None

        # CAMBIO: Para headers, usar valores pre-calculados
        if is_header:
            # Es un header/total: usar valor calculado
            matching = None  # No buscar partidas individuales
        else:
            # Es una partida individual: buscar como antes
            if partida_name in groups:
                matching = groups[partida_name]
            else:
                matching = [p for p in (ing_p | cos_p | gas_p)
                            if p.lower() == partida_name.lower()
                            and p not in grouped_partidas]

        # Año anterior (mismo cálculo)
        if is_header:
            # Para headers: calcular suma del año anterior también
            prev_val = valores_calculados_por_mes.get('DIC', {}).get(partida_name, 0) if 'DIC' in valores_calculados_por_mes else 0
        else:
            prev_val = sum(by_prev.get(p, 0) for p in matching) if matching else 0

        prev_pct_vtas = safe_pct(prev_val, ingresos_prev)
        prev_pct_gastos = safe_pct(prev_val, gastos_prev)

        # Por cada mes
        meses_data = []
        acum_ejec = 0
        acum_ppto = 0
        acum_ing_ejec = 0
        acum_ing_ppto = 0
        acum_gas_ejec = 0
        acum_gas_ppto = 0
        val_ejec_mes_anterior = None

        for i, m in enumerate(MONTHS):
            month_type = MONTH_TYPES[m]

            # CAMBIO: Obtener valor según si es header o partida
            if is_header:
                val_ejec = valores_calculados_por_mes[m].get(partida_name, 0)
                val_ppto = 0  # Los headers no tienen presupuesto directo
            else:
                val_ejec = sum(by_partida.get(p, {}).get(m, 0) for p in matching) if matching else 0
                val_ppto = sum(by_budget.get(p, {}).get(m, 0) for p in matching) if matching else 0

            acum_ejec += val_ejec
            acum_ppto += val_ppto

            # Acumular ingresos y gastos
            acum_ing_ejec += ingresos_ejec_mes[m]
            acum_ing_ppto += ingresos_ppto_mes[m]
            acum_gas_ejec += gastos_ejec_mes[m]
            acum_gas_ppto += gastos_ppto_mes[m]

            # Porcentajes del mes ejecutado
            pct_vtas_ejec = safe_pct(val_ejec, ingresos_ejec_mes[m])
            pct_gastos_ejec = safe_pct(val_ejec, gastos_ejec_mes[m])

            # Base de datos del mes
            mes_data = {
                'type': month_type,
                'month': m,
                'ejecutado': {
                    'valor': round(val_ejec, 2),
                    'pct_vtas': pct_vtas_ejec,
                    'pct_gastos': pct_gastos_ejec,
                }
            }

            # Tipo B+ (FEB, ABR, MAY, JUL, AGO, OCT, NOV, MAR, SEP, JUN, DIC)
            if month_type != 'A':
                # Variación relativa vs mes anterior
                mes_data['vari_rel'] = safe_var(val_ejec, val_ejec_mes_anterior) if val_ejec_mes_anterior is not None else None

                # Acumulado ejecutado
                if month_type == 'E':  # DIC: columna AÑO en lugar de ACUM EJEC
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

                # Tipo C+ (MAR, SEP, JUN, DIC)
                if month_type in ('C', 'D', 'E'):
                    mes_data['acum_ppto'] = {
                        'valor': round(acum_ppto, 2),
                        'pct_vtas': safe_pct(acum_ppto, acum_ing_ppto),
                    }
                    mes_data['var_ppto'] = safe_var(acum_ejec, acum_ppto)

                    # Tipo D (JUN): promedios 6 meses
                    if month_type == 'D':
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
            'year_prev': {
                'valor': round(prev_val, 2),
                'pct_vtas': prev_pct_vtas,
                'pct_gastos': prev_pct_gastos,
            },
            'meses': meses_data,
        })

    return jsonify({
        'year': year,
        'year_prev': year_prev,
        'unit': unit,
        'rows': rows,
    })


# ── ESF ───────────────────────────────────────────────────────────────────────

def _esf_sections():
    """Partidas agrupadas por sección a partir de ESF_STRUCTURE."""
    from engine import ESF_STRUCTURE
    sections = {
        'activo_corriente':    set(),
        'activo_no_corriente': set(),
        'pasivo_corriente':    set(),
        'pasivo_no_corriente': set(),
        'patrimonio':          set(),
    }
    for partida, is_header, section in ESF_STRUCTURE:
        if not is_header and section:
            sections[section].add(partida)
    return sections


def compute_esf(db, year, unit=''):
    """
    Calcula el Estado de Situación Financiera por quarter (consolidando unidades
    cuando unit está vacío). Devuelve (result_quarters, quarters_available).
    """
    uc = f"AND unit='{unit}'" if unit else ''
    rows = db.execute(
        f'SELECT quarter, unit, partida, SUM(amount) amount FROM esf_data WHERE year=? {uc} GROUP BY quarter, unit, partida',
        [year]
    ).fetchall()

    by_quarter = {}
    for r in rows:
        q = r['quarter']
        by_quarter.setdefault(q, {})
        p = r['partida']
        by_quarter[q][p] = by_quarter[q].get(p, 0) + r['amount']

    quarters_available = sorted(by_quarter.keys())
    sections = _esf_sections()

    result_quarters = {}
    for q in [1, 2, 3, 4]:
        data_q = by_quarter.get(q, {})

        tot_ef    = sum(data_q.get(p, 0) for p in ['Efectivo en caja','Efectivo en bancos nacional','Efectivo en bancos exterior','Efectivo en criptomonedas'])
        tot_cxc   = sum(data_q.get(p, 0) for p in ['Cuentas por cobrar clientes','Cuentas por cobrar empleados','Cuentas por cobrar accionistas','Otras cuentas por cobrar','Provisión para cuentas incobrables'])
        tot_inv   = sum(data_q.get(p, 0) for p in ['Inventario de mercancías','Inventario de materia prima','Inventario de suministros'])
        tot_oac   = sum(data_q.get(p, 0) for p in ['Gastos pagados por anticipado','Seguros pagados por anticipado','IVA crédito fiscal','Retenciones de IVA por recuperar','Anticipos a proveedores'])
        tot_ac    = tot_ef + tot_cxc + tot_inv + tot_oac
        tot_anc   = sum(data_q.get(p, 0) for p in sections['activo_no_corriente'])
        tot_activos = tot_ac + tot_anc

        tot_cxp   = sum(data_q.get(p, 0) for p in ['Cuentas por pagar proveedores','Cuentas por pagar accionistas','Otras cuentas por pagar'])
        tot_lab_c = sum(data_q.get(p, 0) for p in ['Pasivos laborales corrientes','Prestaciones sociales por pagar'])
        tot_opc   = sum(data_q.get(p, 0) for p in ['IVA débito fiscal','Retenciones de IVA por enterar','ISLR por pagar','Aportes patronales por pagar','Préstamos bancarios corto plazo','Porción corriente préstamos LP','Anticipos de clientes','Ingresos diferidos'])
        tot_pc    = tot_cxp + tot_lab_c + tot_opc
        tot_pnc   = sum(data_q.get(p, 0) for p in sections['pasivo_no_corriente'])
        tot_pas   = tot_pc + tot_pnc
        tot_pat   = sum(data_q.get(p, 0) for p in sections['patrimonio'])
        tot_pas_pat = tot_pas + tot_pat

        result_quarters[q] = {
            'partidas': {p: round(v, 2) for p, v in data_q.items()},
            'totales': {
                'Total Efectivo y Equivalentes':    round(tot_ef, 2),
                'Total Cuentas por Cobrar (neto)':  round(tot_cxc, 2),
                'Total Inventarios':                round(tot_inv, 2),
                'Total Otros Activos Corrientes':   round(tot_oac, 2),
                'ACTIVOS CORRIENTES':               round(tot_ac, 2),
                'Total Activos No Corrientes':      round(tot_anc, 2),
                'TOTAL ACTIVOS':                    round(tot_activos, 2),
                'Total Cuentas por Pagar':          round(tot_cxp, 2),
                'Total Pasivos Laborales Corrientes':round(tot_lab_c, 2),
                'Total Otros Pasivos Corrientes':   round(tot_opc, 2),
                'TOTAL PASIVOS CORRIENTES':         round(tot_pc, 2),
                'TOTAL PASIVOS NO CORRIENTES':      round(tot_pnc, 2),
                'TOTAL PASIVOS':                    round(tot_pas, 2),
                'TOTAL PATRIMONIO':                 round(tot_pat, 2),
                'TOTAL PASIVOS Y PATRIMONIO':       round(tot_pas_pat, 2),
            }
        }
    return result_quarters, quarters_available


def compute_indicadores(db, year, unit=''):
    """
    Calcula indicadores financieros combinando datos de ESF + EERR.
    Retorna dict con indicadores: ROE, ROA, Ratio Corriente, Prueba Ácida,
    Prueba Defensiva, Ratio Endeudamiento, Rotación Inventarios,
    Rotación Activos, Período Cobro.
    """
    # Obtener datos ESF del último quarter disponible
    result_quarters, quarters_available = compute_esf(db, year, unit)
    if not quarters_available:
        return None

    last_q = max(quarters_available)
    esf = result_quarters[last_q]['totales']

    # Obtener datos EERR del año completo
    uc = f"AND unit='{unit}'" if unit else ''
    rows = db.execute(
        f'''SELECT SUM(amount) total, account_number FROM financials
            WHERE year=? {uc} GROUP BY account_number''',
        [year]
    ).fetchall()

    ingresos = sum(r['total'] for r in rows if r['account_number'].startswith('4'))
    costos   = sum(r['total'] for r in rows if r['account_number'].startswith('5'))
    gastos   = sum(r['total'] for r in rows if r['account_number'].startswith('6'))
    util_bruta = ingresos - costos
    util_neta  = util_bruta - gastos

    tot_activos = esf.get('TOTAL ACTIVOS', 0)
    tot_ac      = esf.get('ACTIVOS CORRIENTES', 0)
    tot_pc      = esf.get('TOTAL PASIVOS CORRIENTES', 0)
    tot_pas     = esf.get('TOTAL PASIVOS', 0)
    tot_pat     = esf.get('TOTAL PATRIMONIO', 0)
    tot_ef      = esf.get('Total Efectivo y Equivalentes', 0)
    tot_inv     = esf.get('Total Inventarios', 0)
    tot_cxc     = esf.get('Total Cuentas por Cobrar (neto)', 0)

    # Ingresos y costos trimestrales (para rotación inventarios)
    meses_q = {1:[1,2,3], 2:[4,5,6], 3:[7,8,9], 4:[10,11,12]}[last_q]
    rows_q = db.execute(
        f'''SELECT SUM(amount) total, account_number FROM financials
            WHERE year=? AND month IN ({','.join('?'*len(meses_q))}) {uc}
            GROUP BY account_number''',
        [year] + meses_q
    ).fetchall()
    ing_q = sum(r['total'] for r in rows_q if r['account_number'].startswith('4'))
    cos_q = sum(r['total'] for r in rows_q if r['account_number'].startswith('5'))

    def safe_div(a, b):
        return round(a / b, 2) if b != 0 else None

    return {
        'roe':              safe_div(util_neta, tot_pat),      # % (multiplicar x100 en frontend)
        'roa':              safe_div(util_neta, tot_activos),  # %
        'ratio_corriente':  safe_div(tot_ac, tot_pc),
        'prueba_acida':     safe_div(tot_ac - tot_inv, tot_pc),
        'prueba_defensiva': safe_div(tot_ef, tot_pc),
        'ratio_endeud':     safe_div(tot_pas, tot_pat),
        'rotacion_inv':     safe_div(tot_inv * 3, cos_q) if cos_q else None,  # meses
        'rotacion_activos': safe_div(ing_q, tot_activos),      # veces/trimestre → x4 para anual
        'periodo_cobro':    safe_div(tot_cxc * 90, ing_q) if ing_q else None,  # días
    }


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


@app.route('/api/indicadores', methods=['GET'])
def get_indicadores():
    """
    Retorna indicadores financieros avanzados (ROE, ROA, liquidez, rotación).
    Parámetros: year, unit (opcional).
    """
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')
    db   = get_db()

    indicadores = compute_indicadores(db, year, unit)
    if not indicadores:
        return jsonify({'error': 'Sin datos ESF para calcular indicadores'}), 404

    return jsonify({'year': year, 'unit': unit, 'indicadores': indicadores})


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
        rows = db.execute('SELECT * FROM tasas_periodo ORDER BY year DESC, month DESC').fetchall()
        return jsonify([dict(r) for r in rows])


@app.route('/api/tasas', methods=['POST'])
@admin_required
def save_tasas():
    """
    Guarda o actualiza tasas para un período.
    Body: {year, month, tasa_bcv_inicio, tasa_bcv_fin, tasa_paralela_inicio, tasa_paralela_fin, factor_recargo?}
    Calcula promedios y factor_diferencial automáticamente.
    """
    data = request.get_json()
    year   = data.get('year')
    month  = data.get('month')
    bcv_ini    = data.get('tasa_bcv_inicio')
    bcv_fin    = data.get('tasa_bcv_fin')
    par_ini    = data.get('tasa_paralela_inicio')
    par_fin    = data.get('tasa_paralela_fin')
    recargo    = data.get('factor_recargo', 1.35)

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
                                   factor_diferencial, factor_recargo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(year, month) DO UPDATE SET
            tasa_bcv_inicio = excluded.tasa_bcv_inicio,
            tasa_bcv_fin = excluded.tasa_bcv_fin,
            tasa_bcv_promedio = excluded.tasa_bcv_promedio,
            tasa_paralela_inicio = excluded.tasa_paralela_inicio,
            tasa_paralela_fin = excluded.tasa_paralela_fin,
            tasa_paralela_promedio = excluded.tasa_paralela_promedio,
            factor_diferencial = excluded.factor_diferencial,
            factor_recargo = excluded.factor_recargo
    ''', (year, month, bcv_ini, bcv_fin, bcv_prom, par_ini, par_fin, par_prom, diferencial, recargo))
    db.commit()

    return jsonify({
        'ok': True,
        'year': year,
        'month': month,
        'tasa_bcv_promedio': round(bcv_prom, 4),
        'tasa_paralela_promedio': round(par_prom, 4),
        'factor_diferencial': round(diferencial, 4),
        'factor_recargo': recargo
    })


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

    if not all([from_y, from_m, to_y, to_m]):
        return jsonify({'error': 'Faltan parámetros'}), 400

    db = get_db()

    # Leer configuración origen
    rows = db.execute(
        'SELECT unit, odoo_code, pct_cash FROM metodo_pago_cuenta WHERE year=? AND month=?',
        (from_y, from_m)
    ).fetchall()

    if not rows:
        return jsonify({'error': 'No hay configuración en el período origen'}), 404

    # Borrar destino si existe
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
    Parámetros: year, month, unit (opcional)
    """
    year  = request.args.get('year', str(datetime.now().year))
    month = request.args.get('month')
    unit  = request.args.get('unit', 'TODAS')
    db    = get_db()

    if not month:
        return jsonify({'error': 'Se requiere mes específico para divisa real'}), 400

    # Obtener tasas del período
    tasas_row = db.execute(
        'SELECT * FROM tasas_periodo WHERE year=? AND month=?',
        (year, month)
    ).fetchone()

    if not tasas_row:
        return jsonify({'error': f'No hay tasas configuradas para {month} {year}'}), 404

    diferencial = tasas_row['factor_diferencial']
    recargo     = tasas_row['factor_recargo']

    # Obtener métodos de pago del período
    metodos_rows = db.execute(
        'SELECT unit, odoo_code, pct_cash FROM metodo_pago_cuenta WHERE year=? AND month=?',
        (year, month)
    ).fetchall()

    # Dict: (unit, odoo_code) -> pct_cash
    metodos_map = {(r['unit'], r['odoo_code']): r['pct_cash'] for r in metodos_rows}

    # Obtener datos financials del mes con JOIN a mapping para obtener odoo_code
    uc = '' if unit == 'TODAS' else f"AND f.unit='{unit}'"
    rows = db.execute(
        f'''SELECT f.unit, f.partida, m.odoo_code, f.amount, m.sign
            FROM financials f
            LEFT JOIN mapping m ON f.partida = m.partida
            WHERE f.year=? AND f.month=? {uc}''',
        (year, month)
    ).fetchall()

    # Aplicar factores según % Cash/BCV
    def aplicar_factor(amount, unit, odoo_code, sign):
        """Aplica factor según % Cash / % BCV."""
        if not odoo_code:
            return amount

        pct_cash = metodos_map.get((unit, odoo_code))

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

    # Calcular montos ajustados
    data_ajustado = {}
    data_literal = {}

    for r in rows:
        partida = r['partida']
        amount_literal = r['amount']
        amount_ajustado = aplicar_factor(amount_literal, r['unit'], r['odoo_code'], r['sign'])

        data_literal[partida] = data_literal.get(partida, 0) + amount_literal
        data_ajustado[partida] = data_ajustado.get(partida, 0) + amount_ajustado

    # Clasificar partidas
    ing_p, cos_p, gas_p = get_clasificacion(db)

    def total(codes, data_dict):
        return sum(data_dict.get(p, 0) for p in codes)

    # Literal (BCV)
    ing_lit = total(ing_p, data_literal)
    cos_lit = total(cos_p, data_literal)
    gas_lit = total(gas_p, data_literal)
    ub_lit  = ing_lit - cos_lit
    un_lit  = ub_lit - gas_lit

    # Ajustado (Divisa Real)
    ing_real = total(ing_p, data_ajustado)
    cos_real = total(cos_p, data_ajustado)
    gas_real = total(gas_p, data_ajustado)
    ub_real  = ing_real - cos_real
    un_real  = ub_real - gas_real

    return jsonify({
        'year': year,
        'month': month,
        'unit': unit,
        'tasas': {
            'bcv': tasas_row['tasa_bcv_promedio'],
            'paralela': tasas_row['tasa_paralela_promedio'],
            'diferencial': diferencial,
            'recargo': recargo
        },
        'literal_bcv': {
            'ingresos': round(ing_lit, 2),
            'costos': round(cos_lit, 2),
            'gastos': round(gas_lit, 2),
            'utilidad_bruta': round(ub_lit, 2),
            'utilidad_neta': round(un_lit, 2),
        },
        'divisa_real': {
            'ingresos': round(ing_real, 2),
            'costos': round(cos_real, 2),
            'gastos': round(gas_real, 2),
            'utilidad_bruta': round(ub_real, 2),
            'utilidad_neta': round(un_real, 2),
        },
        'diferencias': {
            'ingresos': round(ing_real - ing_lit, 2),
            'costos': round(cos_real - cos_lit, 2),
            'gastos': round(gas_real - gas_lit, 2),
            'utilidad_bruta': round(ub_real - ub_lit, 2),
            'utilidad_neta': round(un_real - un_lit, 2),
            'utilidad_distribuible': round(un_real, 2),
        }
    })


@app.route('/api/eerr/divisa_real', methods=['GET'])
@login_required
def eerr_divisa_real():
    """
    Estado de Resultados COMPLETO con ajuste de divisa real.
    Misma estructura que /api/eerr/completo (119 partidas, tipos A/B/C/D/E)
    pero con montos ajustados por factor diferencial según % Cash/BCV.
    Parámetros: year, unit
    """
    from engine import EERR_STRUCTURE

    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')
    db = get_db()

    year_prev = str(int(year) - 1)
    uc = f"AND unit='{unit}'" if unit else ''

    # Mapeo de estructura por mes
    MONTH_TYPES = {
        'ENE': 'A', 'FEB': 'B', 'MAR': 'C', 'ABR': 'B', 'MAY': 'B', 'JUN': 'D',
        'JUL': 'B', 'AGO': 'B', 'SEPT': 'C', 'OCT': 'B', 'NOV': 'B', 'DIC': 'E',
    }

    # ── CARGAR TASAS Y MÉTODOS DE PAGO POR MES ──
    tasas_by_month = {}
    metodos_by_month = {}

    for m in MONTHS:
        # Tasas del período
        tasas_row = db.execute(
            'SELECT * FROM tasas_periodo WHERE year=? AND month=?',
            (year, m)
        ).fetchone()

        if tasas_row:
            tasas_by_month[m] = {
                'diferencial': tasas_row['factor_diferencial'],
                'recargo': tasas_row['factor_recargo']
            }

        # Métodos de pago del período
        metodos_rows = db.execute(
            'SELECT unit, odoo_code, pct_cash FROM metodo_pago_cuenta WHERE year=? AND month=?',
            (year, m)
        ).fetchall()

        metodos_by_month[m] = {(r['unit'], r['odoo_code']): r['pct_cash'] for r in metodos_rows}

    # ── LEER DATOS Y APLICAR FACTORES ──
    # Obtener datos con odoo_code para aplicar factores
    rows_curr = db.execute(
        f'''SELECT f.partida, f.month, f.unit, f.amount, m.odoo_code
            FROM financials f
            LEFT JOIN mapping m ON f.partida = m.partida
            WHERE f.year=? {uc}''',
        [year]
    ).fetchall()

    # Aplicar factores y agregar por partida/mes
    by_partida = {}
    for r in rows_curr:
        partida = r['partida']
        month = r['month']
        amount_literal = r['amount']

        # Obtener configuración del mes
        tasas = tasas_by_month.get(month)
        metodos_map = metodos_by_month.get(month, {})

        if tasas and r['odoo_code']:
            pct_cash = metodos_map.get((r['unit'], r['odoo_code']))
            diferencial = tasas['diferencial']
            amount_ajustado = aplicar_factor_divisa(amount_literal, pct_cash, diferencial)
        else:
            # Sin tasas o sin odoo_code, usar literal
            amount_ajustado = amount_literal

        by_partida.setdefault(partida, {})[month] = by_partida.get(partida, {}).get(month, 0) + amount_ajustado

    # Año anterior (sin ajuste - usar literal)
    rows_prev = db.execute(
        f'''SELECT partida, SUM(amount) amount FROM financials
            WHERE year=? {uc} GROUP BY partida''',
        [year_prev]
    ).fetchall()
    by_prev = {r['partida']: r['amount'] for r in rows_prev}

    # Presupuesto (sin ajuste)
    rows_budget = db.execute(
        f'''SELECT partida, month, SUM(amount) amount FROM budget
            WHERE year=? {uc} GROUP BY partida, month''',
        [year]
    ).fetchall()
    by_budget = {}
    for r in rows_budget:
        by_budget.setdefault(r['partida'], {})[r['month']] = r['amount']

    # Clasificación
    ing_p, cos_p, gas_p = get_clasificacion(db)

    # Obtener grupos de presentación
    groups, grouped_partidas = get_grouped_partidas(db, 'eerr')

    # Totales de ingresos y gastos por mes
    ingresos_ejec_mes = {}
    gastos_ejec_mes = {}
    ingresos_ppto_mes = {}
    gastos_ppto_mes = {}

    ingresos_prev = sum(by_prev.get(p, 0) for p in ing_p)
    gastos_prev = sum(by_prev.get(p, 0) for p in gas_p)

    for m in MONTHS:
        ingresos_ejec_mes[m] = sum(by_partida.get(p, {}).get(m, 0) for p in ing_p)
        gastos_ejec_mes[m] = sum(by_partida.get(p, {}).get(m, 0) for p in gas_p)
        ingresos_ppto_mes[m] = sum(by_budget.get(p, {}).get(m, 0) for p in ing_p)
        gastos_ppto_mes[m] = sum(by_budget.get(p, {}).get(m, 0) for p in gas_p)

    def safe_pct(num, den):
        return round(num / den * 100, 1) if den != 0 else 0

    def safe_var(val, base):
        if base == 0:
            return None
        return round((val - base) / abs(base) * 100, 1)

    # ── CONSTRUIR FILAS SEGÚN EERR_STRUCTURE ──
    rows = []
    for item in EERR_STRUCTURE:
        partida_name = item[0]
        is_header = item[1]
        parent = item[2] if len(item) > 2 else None
        bold = item[3] if len(item) > 3 else False
        bg_color = item[4] if len(item) > 4 else None

        # Verificar si esta partida es un grupo
        if partida_name in groups:
            # Es un grupo: sumar todas las partidas del grupo
            matching = groups[partida_name]
        else:
            # Buscar partida individual (excluir las que están en grupos)
            matching = [p for p in (ing_p | cos_p | gas_p)
                        if p.lower() == partida_name.lower()
                        and p not in grouped_partidas]

        # Año anterior
        prev_val = sum(by_prev.get(p, 0) for p in matching)
        prev_pct_vtas = safe_pct(prev_val, ingresos_prev)
        prev_pct_gastos = safe_pct(prev_val, gastos_prev)

        # Por cada mes
        meses_data = []
        acum_ejec = 0
        acum_ppto = 0
        acum_ing_ejec = 0
        acum_ing_ppto = 0
        acum_gas_ejec = 0
        acum_gas_ppto = 0
        val_ejec_mes_anterior = None

        for i, m in enumerate(MONTHS):
            month_type = MONTH_TYPES[m]
            val_ejec = sum(by_partida.get(p, {}).get(m, 0) for p in matching)
            val_ppto = sum(by_budget.get(p, {}).get(m, 0) for p in matching)

            acum_ejec += val_ejec
            acum_ppto += val_ppto
            acum_ing_ejec += ingresos_ejec_mes[m]
            acum_ing_ppto += ingresos_ppto_mes[m]
            acum_gas_ejec += gastos_ejec_mes[m]
            acum_gas_ppto += gastos_ppto_mes[m]

            pct_vtas_ejec = safe_pct(val_ejec, ingresos_ejec_mes[m])
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
            'year_prev': {
                'valor': round(prev_val, 2),
                'pct_vtas': prev_pct_vtas,
                'pct_gastos': prev_pct_gastos,
            },
            'meses': meses_data,
        })

    return jsonify({
        'year': year,
        'year_prev': year_prev,
        'unit': unit,
        'rows': rows,
    })


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

    uc = f"AND unit='{unit}'" if unit else ''
    mc = f"AND month='{month}'" if month else ''

    # Presupuesto
    brows = db.execute(
        f'SELECT partida, month, SUM(amount) amount FROM budget WHERE year=? {uc} {mc} GROUP BY partida, month',
        [year]
    ).fetchall()
    budget = {}
    for r in brows:
        budget.setdefault(r['partida'], {})[r['month']] = r['amount']

    # Real
    rrows = db.execute(
        f'SELECT partida, month, SUM(amount) amount FROM financials WHERE year=? {uc} {mc} GROUP BY partida, month',
        [year]
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
            tmp = tempfile.mktemp(suffix='.xlsx')
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
            tmp = tempfile.mktemp(suffix='.xls')
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
    uc = f"AND unit='{unit}'" if unit else ''

    def totals(yr):
        def s(partidas):
            if not partidas: return 0
            ph = ','.join('?' * len(partidas))
            r  = db.execute(
                f'SELECT SUM(amount) FROM financials WHERE year=? AND partida IN ({ph}) {uc}',
                [str(yr)] + list(partidas)
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
                    [str(yr), m] + list(partidas)
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
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')
    mf   = request.args.get('month_from', '')
    mt   = request.args.get('month_to', '')
    db   = get_db()

    q = 'SELECT * FROM financials WHERE year=?'; params = [year]
    if unit: q += ' AND unit=?'; params.append(unit)
    if mf and mt and mf in MONTHS and mt in MONTHS:
        fi, ti = MONTHS.index(mf), MONTHS.index(mt)
        sel = MONTHS[fi:ti+1] if fi <= ti else MONTHS[fi:] + MONTHS[:ti+1]
        q += f' AND month IN ({",".join("?"*len(sel))})'; params.extend(sel)
    elif mf and mf in MONTHS:
        sel = MONTHS[MONTHS.index(mf):]
        q += f' AND month IN ({",".join("?"*len(sel))})'; params.extend(sel)

    rows = db.execute(q + ' ORDER BY unit, month, partida', params).fetchall()
    exp  = ExcelExporter([dict(r) for r in rows], year, [unit] if unit else UNITS, MONTHS)
    path = exp.generate()
    suf  = (f'_{unit}' if unit else '_CONSOLIDADO') + (f'_{mf}-{mt}' if mf and mt else '')
    return send_file(path, as_attachment=True, download_name=f'EERR_ULTRAX_{year}{suf}.xlsx')


@app.route('/api/export/esf', methods=['GET'])
def export_esf():
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')
    db   = get_db()

    uc   = f"AND unit='{unit}'" if unit else ''
    rows = db.execute(
        f'SELECT * FROM esf_data WHERE year=? {uc} ORDER BY unit, quarter, partida', [year]
    ).fetchall()
    exp  = ESFExporter([dict(r) for r in rows], year, [unit] if unit else UNITS)
    path = exp.generate()
    suf  = f'_{unit}' if unit else '_CONSOLIDADO'
    return send_file(path, as_attachment=True, download_name=f'ESF_ULTRAX_{year}{suf}.xlsx')


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

    tmp = tempfile.mktemp(suffix='.pdf')
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
    uc    = f"AND unit='{unit}'" if unit else ''

    def sm(partidas, month=''):
        if not partidas: return 0
        ph    = ','.join('?' * len(partidas))
        extra = f"AND month='{month}'" if month else ''
        r     = db.execute(
            f'SELECT SUM(amount) FROM financials WHERE year=? AND partida IN ({ph}) {uc} {extra}',
            [year] + list(partidas)
        ).fetchone()
        return r[0] or 0

    tmp = tempfile.mktemp(suffix='.pdf')
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
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')
    db   = get_db()
    q    = 'SELECT * FROM financials WHERE year=?'; params = [year]
    if unit: q += ' AND unit=?'; params.append(unit)
    return jsonify([dict(r) for r in db.execute(q + ' ORDER BY unit, month, partida', params).fetchall()])

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
    tmp = tempfile.mktemp(suffix='.db')
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


# ── Mapping Groups (Agrupación de partidas) ──────────────────────────────────

def get_grouped_partidas(db, report_type='eerr'):
    """
    Retorna:
    - groups: dict {group_name: [partida1, partida2, ...]}
    - grouped_partidas: set de partidas que YA están en un grupo

    Usado en EERR/ESF para agrupar partidas bajo un nombre común.
    """
    rows = db.execute(
        '''SELECT mg.group_name, m.partida, mg.odoo_code
           FROM mapping_groups mg
           JOIN mapping m ON mg.odoo_code = m.odoo_code
           WHERE mg.report_type = ?
           ORDER BY mg.display_order, mg.group_name''',
        [report_type]
    ).fetchall()

    groups = {}
    grouped_partidas = set()

    for r in rows:
        group_name = r['group_name']
        partida = r['partida']

        if group_name not in groups:
            groups[group_name] = []
        groups[group_name].append(partida)
        grouped_partidas.add(partida)

    return groups, grouped_partidas


@app.route('/api/mapping_groups', methods=['GET'])
def get_mapping_groups():
    """
    Retorna todos los grupos con sus cuentas.
    Query params:
    - report_type: 'eerr' | 'esf' (opcional)
    """
    report_type = request.args.get('report_type', '')
    db = get_db()

    query = '''
        SELECT
            mg.id,
            mg.group_name,
            mg.odoo_code,
            mg.report_type,
            mg.display_order,
            m.odoo_name,
            m.partida
        FROM mapping_groups mg
        LEFT JOIN mapping m ON mg.odoo_code = m.odoo_code
    '''

    if report_type:
        query += ' WHERE mg.report_type = ?'
        rows = db.execute(query + ' ORDER BY mg.group_name, mg.display_order', [report_type]).fetchall()
    else:
        rows = db.execute(query + ' ORDER BY mg.report_type, mg.group_name, mg.display_order').fetchall()

    # Agrupar por group_name
    groups = {}
    for r in rows:
        gname = r['group_name']
        if gname not in groups:
            groups[gname] = {
                'group_name': gname,
                'report_type': r['report_type'],
                'display_order': r['display_order'],
                'accounts': []
            }
        groups[gname]['accounts'].append({
            'id': r['id'],
            'odoo_code': r['odoo_code'],
            'odoo_name': r['odoo_name'],
            'partida': r['partida']
        })

    return jsonify(list(groups.values()))


@app.route('/api/mapping_groups', methods=['POST'])
@admin_required
def save_mapping_groups():
    """
    Crea o actualiza asignaciones de grupos.
    Body: {
        group_name: "Mantenimiento y reparaciones",
        odoo_codes: ["6.01.01.02.001", "6.01.01.02.002", ...],
        report_type: "eerr",
        display_order: 10  (opcional)
    }
    """
    data = request.get_json()
    group_name = data.get('group_name', '').strip()
    odoo_codes = data.get('odoo_codes', [])
    report_type = data.get('report_type', 'eerr')
    display_order = data.get('display_order', 0)

    if not group_name or not odoo_codes:
        return jsonify({'error': 'group_name y odoo_codes son requeridos'}), 400

    if report_type not in ['eerr', 'esf']:
        return jsonify({'error': 'report_type debe ser eerr o esf'}), 400

    db = get_db()

    # Borrar asignaciones anteriores de estas cuentas al mismo grupo
    db.execute(
        'DELETE FROM mapping_groups WHERE group_name=? AND report_type=?',
        (group_name, report_type)
    )

    # Insertar nuevas asignaciones
    for code in odoo_codes:
        db.execute(
            '''INSERT INTO mapping_groups (group_name, odoo_code, report_type, display_order)
               VALUES (?,?,?,?)''',
            (group_name, code, report_type, display_order)
        )

    db.commit()
    return jsonify({'ok': True, 'inserted': len(odoo_codes)})


@app.route('/api/mapping_groups/<int:group_id>', methods=['DELETE'])
@admin_required
def delete_mapping_group(group_id):
    """Elimina una asignación de grupo individual."""
    db = get_db()
    db.execute('DELETE FROM mapping_groups WHERE id=?', (group_id,))
    db.commit()
    return jsonify({'ok': True})


@app.route('/api/mapping_groups/group/<path:group_name>', methods=['DELETE'])
@admin_required
def delete_mapping_group_by_name(group_name):
    """Elimina un grupo completo con todas sus asignaciones."""
    db = get_db()
    deleted = db.execute('DELETE FROM mapping_groups WHERE group_name=?', (group_name,)).rowcount
    db.commit()
    return jsonify({'ok': True, 'deleted': deleted})


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
    app.run(debug=True, host='0.0.0.0', port=5000)
