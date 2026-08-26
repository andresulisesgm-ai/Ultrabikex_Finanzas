from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os, secrets
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from db import init_db, migrate_db, close_db
from auth import login_required, admin_required, verify_password, get_current_user, change_password
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
from blueprints.upload import upload_bp
from constants import MONTHS, UNITS

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
app.register_blueprint(upload_bp)
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

@app.route('/api/change_password', methods=['POST'])
@login_required
def change_password_route():
    data = request.get_json()
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    username = session['username']
    success, message = change_password(username, current_password, new_password)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'message': message}), 400



# ── Rutas base ────────────────────────────────────────────────────────────────

@app.route('/')
@login_required
def index():
    user = get_current_user()
    return render_template('index.html', units=UNITS, months=MONTHS, user=user)


# ── Shutdown ──────────────────────────────────────────────────────────────────

@app.route('/api/shutdown', methods=['POST'])
@admin_required
def shutdown():
    import threading, time, subprocess
    def _stop():
        time.sleep(0.3)
        # Antes de auto-matarse, cerrar cualquier OTRO proceso python.exe que
        # tambien este escuchando en el puerto 5000 (zombie de un cierre
        # incompleto anterior) -- identificado por puerto especifico via
        # netstat, nunca por nombre generico de proceso.
        try:
            propio_pid = os.getpid()
            out = subprocess.run(
                ['netstat', '-ano'], capture_output=True, text=True, timeout=3
            ).stdout
            for linea in out.splitlines():
                if ':5000' in linea and 'LISTENING' in linea:
                    pid = linea.strip().split()[-1]
                    if pid.isdigit() and int(pid) != propio_pid:
                        subprocess.run(
                            ['taskkill', '/F', '/PID', pid],
                            capture_output=True, timeout=3
                        )
        except Exception:
            pass  # limpieza best-effort, nunca debe bloquear el apagado normal
        os._exit(0)
    threading.Thread(target=_stop, daemon=True).start()
    return jsonify({'ok': True})


if __name__ == '__main__':
    init_db()
    migrate_db()  # seguro de llamar siempre: es idempotente
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
