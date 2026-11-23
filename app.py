from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os, secrets
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

from db import init_db, migrate_db, close_db, get_db
from audit import registrar_auditoria
from auth import login_required, admin_required, superadmin_required, verify_password, authenticate_user, get_current_user, admin_reset_password, list_users
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
from blueprints.home import home_bp
from blueprints.exportables import exportables_bp
from blueprints.briefing import briefing_bp
from blueprints.mapeo import mapeo_bp
from blueprints.upload import upload_bp
from blueprints.sistema_empresas import sistema_empresas_bp
from blueprints.sistema_usuarios import sistema_usuarios_bp
from blueprints.sistema_auditoria import sistema_auditoria_bp
from constants import MONTHS

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
app.register_blueprint(home_bp)
app.register_blueprint(exportables_bp)
app.register_blueprint(briefing_bp)
app.register_blueprint(mapeo_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(sistema_empresas_bp)
app.register_blueprint(sistema_usuarios_bp)
app.register_blueprint(sistema_auditoria_bp)
app.config['UPLOAD_FOLDER'] = 'uploads'
FLASK_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
if not FLASK_SECRET_KEY:
    raise RuntimeError(
        "Falta la variable de entorno FLASK_SECRET_KEY. "
        "Verifica que el archivo .env existe en la raiz del proyecto."
    )
app.secret_key = FLASK_SECRET_KEY

init_db()
migrate_db()  # idempotente: asegura migraciones tambien bajo Gunicorn en produccion

from backup_scheduler import start_scheduler
start_scheduler()


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

    ok, res, status = authenticate_user(username, password)
    if ok:
        session['username'] = res['username']
        session['role'] = res['role']
        session['es_superadmin'] = res['es_superadmin']
        registrar_auditoria(get_db(), res['username'], 'auth', 'login_ok', f"role={res['role']}")
        return jsonify({'success': True, 'role': res['role'], 'es_superadmin': res['es_superadmin']})

    if status in (403, 423):
        registrar_auditoria(get_db(), username, 'auth', 'login_bloqueado' if status == 423 else 'login_inactivo', res)
    return jsonify({'error': res}), status

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/current-user')
@login_required
def current_user():
    return jsonify(get_current_user())

@app.route('/api/admin/list_users', methods=['GET'])
@admin_required
def admin_list_users_route():
    return jsonify(list_users())

@app.route('/api/admin/reset_password', methods=['POST'])
@admin_required
def admin_reset_password_route():
    data = request.get_json()
    username = data.get('username', '')
    new_password = data.get('new_password', '')
    db = get_db()
    target = db.execute('SELECT es_superadmin FROM users WHERE username = ?', (username,)).fetchone()
    if target and target['es_superadmin'] == 1 and session.get('es_superadmin') != 1:
        return jsonify({'error': 'No puedes restablecer la clave de un superadministrador'}), 403
    admin_username = session['username']
    success, message = admin_reset_password(username, new_password, admin_username)
    if success:
        registrar_auditoria(get_db(), admin_username, 'usuarios', 'resetear_clave', f'usuario={username}')
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'message': message}), 400






# ── Rutas base ────────────────────────────────────────────────────────────────

@app.route('/')
@login_required
def index():
    user = get_current_user()
    db = get_db()
    units_activas = [r[0] for r in db.execute(
        'SELECT nombre FROM unidades WHERE activo = 1 ORDER BY empresa_id, id'
    ).fetchall()]
    return render_template('index.html', units=units_activas, months=MONTHS, user=user)


if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
