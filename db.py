import sqlite3, os, re
from flask import g
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'ultrax.db')

# ══════════════════════════════════════════════════════════════════════════════
# NUEVO SISTEMA DE MAPPING DESDE EXCEL REAL
# ══════════════════════════════════════════════════════════════════════════════

def classify_account(codigo: str) -> tuple:
    """
    Clasifica una cuenta según su código retornando (sign, income_type).

    Reglas:
    - 1.x → (1, None) [Activo]
    - 1.02.06.XX.500|.501 → (-1, None) [Dep/Det Acum - reducen activo]
    - 1.02.07.XX.500|.002 → (-1, None) [Amort Acum - reducen activo]
    - 2.x → (-1, None) [Pasivo]
    - 3.x → (-1, None) [Patrimonio]
    - 4.01.01.02.x | 4.01.01.03.x → (1, 'mercancia') [Devoluciones/descuentos]
    - 4.01.01.x → (1, 'mercancia')
    - 4.01.02.x → (1, 'servicios')
    - 4.01.03.x → (1, 'eventos')
    - 4.01.04.x → (1, 'taller')
    - 4.02.x → (1, None) [Ingresos no operativos]
    - 5.01.01.x → (-1, 'mercancia')
    - 5.01.02.x → (-1, 'servicios')
    - 5.01.03.x → (-1, 'eventos')
    - 5.01.04.x → (-1, 'taller')
    - 6.x → (-1, None) [Gastos]
    """

    # Cuentas de activo con depreciación/deterioro/amortización acumulada (reducen el activo)
    if re.match(r'^1\.02\.06\.\d+\.(500|501)$', codigo):
        return (1, None)
    if re.match(r'^1\.02\.07\.\d+\.(500|002)$', codigo):
        return (1, None)

    # Devoluciones y descuentos sobre ventas (reducen ingresos)
    if codigo.startswith('4.01.01.02.') or codigo.startswith('4.01.01.03.'):
        return (1, 'mercancia')

    # Ingresos operativos por tipo
    if codigo.startswith('4.01.01.'):
        return (1, 'mercancia')
    if codigo.startswith('4.01.02.'):
        return (1, 'servicios')
    if codigo.startswith('4.01.03.'):
        return (1, 'eventos')
    if codigo.startswith('4.01.04.'):
        return (1, 'taller')

    # Ingresos no operativos
    if codigo.startswith('4.02.'):
        return (1, None)

    # Costos de venta por tipo
    if codigo.startswith('5.01.01.'):
        return (-1, 'mercancia')
    if codigo.startswith('5.01.02.'):
        return (-1, 'servicios')
    if codigo.startswith('5.01.03.'):
        return (-1, 'eventos')
    if codigo.startswith('5.01.04.'):
        return (-1, 'taller')

    # Clasificación genérica por primer dígito
    first = codigo[0] if codigo else ''
    if first == '1':
        return (1, None)   # Activo
    if first == '2':
        return (-1, None)  # Pasivo
    if first == '3':
        return (-1, None)  # Patrimonio
    if first == '4':
        return (1, None)   # Ingresos (catch-all)
    if first == '5':
        return (-1, None)  # Costos (catch-all)
    if first == '6':
        return (-1, None)  # Gastos

    # Default seguro
    return (-1, None)


def load_mapping_from_excel(excel_path='Cuenta (account.account) (5).xlsx'):
    """
    Lee el plan de cuentas de Odoo y genera el INITIAL_MAPPING.
    Retorna lista de tuplas: (odoo_code, odoo_name, partida, sign, income_type)
    """
    try:
        import pandas as pd
    except ImportError:
        print("[WARN]  pandas no instalado. Ejecuta: pip install pandas openpyxl")
        return []

    excel_full_path = os.path.join(os.path.dirname(__file__), excel_path)

    if not os.path.exists(excel_full_path):
        print(f"[WARN]  Archivo no encontrado: {excel_full_path}")
        return []

    try:
        df = pd.read_excel(excel_full_path, engine='openpyxl')
    except Exception as e:
        print(f"[WARN]  Error leyendo Excel: {e}")
        return []

    # Normalizar nombres de columnas
    df.columns = ['codigo', 'moneda', 'nombre']
    df['codigo'] = df['codigo'].astype(str).str.strip()
    df['nombre'] = df['nombre'].astype(str).str.strip()

    # Filtrar solo cuentas operativas (nivel 5: X.XX.XX.XX.XXX)
    # Incluye también niveles 3 y 4 para cuentas que no tienen subdivisión
    df_cuentas = df[df['codigo'].str.match(r'^\d+\.\d+', na=False)]

    mapping = []
    for _, row in df_cuentas.iterrows():
        codigo = row['codigo']
        nombre = row['nombre']

        # Saltar registros vacíos o inválidos
        if not codigo or codigo == 'nan' or not nombre or nombre == 'nan':
            continue

        sign, income_type = classify_account(codigo)

        # (odoo_code, odoo_name, partida, sign, income_type)
        mapping.append((codigo, nombre, nombre, sign, income_type))

    print(f"[OK] {len(mapping)} cuentas cargadas desde {excel_path}")
    return mapping


# Generar INITIAL_MAPPING desde el Excel
INITIAL_MAPPING = load_mapping_from_excel()

# Si no se pudo cargar, usar fallback mínimo para evitar crash
if not INITIAL_MAPPING:
    print("[WARN]  Usando INITIAL_MAPPING vacío. Ejecuta reset_mapping() después de instalar pandas.")
    INITIAL_MAPPING = []


# ══════════════════════════════════════════════════════════════════════════════
# GRUPOS INICIALES DE PRESENTACIÓN
# ══════════════════════════════════════════════════════════════════════════════

INITIAL_GROUPS = [
    # (group_name, odoo_code, report_type, display_order)

    # EERR - Gastos de mantenimiento
    ('Mantenimiento y reparaciones', '6.01.01.02.001', 'eerr', 10),
    ('Mantenimiento y reparaciones', '6.01.01.02.002', 'eerr', 10),
    ('Mantenimiento y reparaciones', '6.01.01.02.003', 'eerr', 10),
    ('Mantenimiento y reparaciones', '6.01.01.02.004', 'eerr', 10),
    ('Mantenimiento y reparaciones', '6.01.01.02.005', 'eerr', 10),

    # EERR - Viáticos administrativos
    ('Viáticos administrativos', '6.01.01.03.001', 'eerr', 20),
    ('Viáticos administrativos', '6.01.01.03.002', 'eerr', 20),
    ('Viáticos administrativos', '6.01.01.03.003', 'eerr', 20),
    ('Viáticos administrativos', '6.01.01.03.004', 'eerr', 20),
    ('Viáticos administrativos', '6.01.01.03.005', 'eerr', 20),

    # EERR - Gastos de seguro
    ('Gastos de seguro', '6.01.01.04.001', 'eerr', 30),
    ('Gastos de seguro', '6.01.01.04.002', 'eerr', 30),
    ('Gastos de seguro', '6.01.01.04.003', 'eerr', 30),
    ('Gastos de seguro', '6.01.01.04.004', 'eerr', 30),

    # EERR - Impuestos, tasas y contribuciones
    ('Gastos de impuestos, tasas y contribuciones', '6.01.01.05.001', 'eerr', 40),
    ('Gastos de impuestos, tasas y contribuciones', '6.01.01.05.002', 'eerr', 40),
    ('Gastos de impuestos, tasas y contribuciones', '6.01.01.05.003', 'eerr', 40),
    ('Gastos de impuestos, tasas y contribuciones', '6.01.01.05.004', 'eerr', 40),
    ('Gastos de impuestos, tasas y contribuciones', '6.01.01.05.005', 'eerr', 40),
    ('Gastos de impuestos, tasas y contribuciones', '6.01.01.05.006', 'eerr', 40),
    ('Gastos de impuestos, tasas y contribuciones', '6.01.01.05.007', 'eerr', 40),

    # EERR - Depreciaciones (agrupadas)
    ('Depreciaciones, deterioro y Amortización', '6.01.01.06.001', 'eerr', 50),
    ('Depreciaciones, deterioro y Amortización', '6.01.01.06.002', 'eerr', 50),
    ('Depreciaciones, deterioro y Amortización', '6.01.01.06.003', 'eerr', 50),
    ('Depreciaciones, deterioro y Amortización', '6.01.01.06.004', 'eerr', 50),
    ('Depreciaciones, deterioro y Amortización', '6.01.01.07.001', 'eerr', 50),
    ('Depreciaciones, deterioro y Amortización', '6.01.01.07.002', 'eerr', 50),
    ('Depreciaciones, deterioro y Amortización', '6.01.01.07.003', 'eerr', 50),
    ('Depreciaciones, deterioro y Amortización', '6.01.01.07.004', 'eerr', 50),
    ('Depreciaciones, deterioro y Amortización', '6.01.01.07.005', 'eerr', 50),
    ('Depreciaciones, deterioro y Amortización', '6.01.01.08.001', 'eerr', 50),

    # EERR - Gastos bancarios
    ('Gastos Bancarios', '6.01.01.09.001', 'eerr', 60),
    ('Gastos Bancarios', '6.01.01.09.002', 'eerr', 60),

    # EERR - Gastos de intereses
    ('Gastos de intereses sobre préstamos', '6.01.01.10.001', 'eerr', 70),
    ('Gastos de intereses sobre préstamos', '6.01.01.10.002', 'eerr', 70),
    ('Gastos de intereses sobre préstamos', '6.01.01.10.003', 'eerr', 70),
]


# ══════════════════════════════════════════════════════════════════════════════
# DATABASE FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def get_db():
    if 'db' not in g.__dict__:
        conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA busy_timeout=30000')
        g.db = conn
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    conn.executescript('''
        CREATE TABLE IF NOT EXISTS mapping (
            odoo_code   TEXT PRIMARY KEY,
            odoo_name   TEXT NOT NULL,
            partida     TEXT NOT NULL,
            sign        INTEGER NOT NULL DEFAULT -1,
            income_type TEXT DEFAULT NULL
        );
        CREATE TABLE IF NOT EXISTS financials (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            year    TEXT NOT NULL,
            month   TEXT NOT NULL,
            unit    TEXT NOT NULL,
            partida TEXT NOT NULL,
            amount  REAL NOT NULL DEFAULT 0,
            UNIQUE(year, month, unit, partida)
        );
        CREATE INDEX IF NOT EXISTS idx_fin ON financials(year, month, unit);
        CREATE TABLE IF NOT EXISTS esf_data (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            year      TEXT NOT NULL,
            quarter   INTEGER NOT NULL,
            unit      TEXT NOT NULL,
            partida   TEXT NOT NULL,
            amount    REAL NOT NULL DEFAULT 0,
            UNIQUE(year, quarter, unit, partida)
        );
        CREATE INDEX IF NOT EXISTS idx_esf ON esf_data(year, quarter, unit);
        CREATE TABLE IF NOT EXISTS budget (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            year    TEXT NOT NULL,
            month   TEXT NOT NULL,
            unit    TEXT NOT NULL,
            partida TEXT NOT NULL,
            amount  REAL NOT NULL DEFAULT 0,
            UNIQUE(year, month, unit, partida)
        );
        CREATE INDEX IF NOT EXISTS idx_budget ON budget(year, month, unit);
        CREATE TABLE IF NOT EXISTS history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            year        TEXT NOT NULL,
            month       TEXT NOT NULL,
            unit        TEXT NOT NULL,
            inserted    INTEGER NOT NULL DEFAULT 0,
            reverted    INTEGER NOT NULL DEFAULT 0,
            created_at  TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS mapping_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            action      TEXT NOT NULL,
            odoo_code   TEXT NOT NULL,
            odoo_name   TEXT,
            partida     TEXT,
            sign        INTEGER,
            income_type TEXT,
            created_at  TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS esf_upload_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            year        TEXT NOT NULL,
            quarter     INTEGER NOT NULL,
            unit        TEXT NOT NULL,
            inserted    INTEGER NOT NULL DEFAULT 0,
            reverted    INTEGER NOT NULL DEFAULT 0,
            created_at  TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS tasas_periodo (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            year                    TEXT NOT NULL,
            month                   TEXT NOT NULL,
            tasa_bcv_inicio         REAL NOT NULL,
            tasa_bcv_fin            REAL NOT NULL,
            tasa_bcv_promedio       REAL NOT NULL,
            tasa_paralela_inicio    REAL NOT NULL,
            tasa_paralela_fin       REAL NOT NULL,
            tasa_paralela_promedio  REAL NOT NULL,
            factor_diferencial      REAL NOT NULL,
            factor_recargo          REAL NOT NULL DEFAULT 1.35,
            created_at              TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            UNIQUE(year, month)
        );
        CREATE TABLE IF NOT EXISTS metodo_pago_cuenta (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            year            TEXT NOT NULL,
            month           TEXT NOT NULL,
            unit            TEXT NOT NULL,
            odoo_code       TEXT NOT NULL,
            pct_cash        REAL NOT NULL DEFAULT 0 CHECK(pct_cash >= 0 AND pct_cash <= 100),
            created_at      TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            UNIQUE(year, month, unit, odoo_code)
        );

        CREATE TABLE IF NOT EXISTS dashboard_config (
            username TEXT PRIMARY KEY,
            config_json TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS esf_ajuste_diferencial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year TEXT NOT NULL,
            quarter INTEGER NOT NULL,
            valor REAL NOT NULL,
            updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            UNIQUE(year, quarter)
        );
    ''')

    # ── Migración de BDs existentes ──────────────────────────────────────────
    # Añadir income_type a mapping si no existe
    cols = {r[1] for r in conn.execute("PRAGMA table_info(mapping)").fetchall()}
    if 'income_type' not in cols:
        conn.execute("ALTER TABLE mapping ADD COLUMN income_type TEXT DEFAULT NULL")
        print("Migración: columna income_type añadida a mapping")

    # Añadir income_type a mapping_log si no existe
    cols_log = {r[1] for r in conn.execute("PRAGMA table_info(mapping_log)").fetchall()}
    if 'income_type' not in cols_log:
        conn.execute("ALTER TABLE mapping_log ADD COLUMN income_type TEXT DEFAULT NULL")
        print("Migración: columna income_type añadida a mapping_log")

    # Añadir columnas inicio/fin a tasas_periodo si no existen
    cols_tasas = {r[1] for r in conn.execute("PRAGMA table_info(tasas_periodo)").fetchall()}
    if 'tasa_bcv_inicio' not in cols_tasas:
        conn.execute("ALTER TABLE tasas_periodo ADD COLUMN tasa_bcv_inicio REAL DEFAULT 0")
        conn.execute("ALTER TABLE tasas_periodo ADD COLUMN tasa_bcv_fin REAL DEFAULT 0")
        conn.execute("ALTER TABLE tasas_periodo ADD COLUMN tasa_paralela_inicio REAL DEFAULT 0")
        conn.execute("ALTER TABLE tasas_periodo ADD COLUMN tasa_paralela_fin REAL DEFAULT 0")
        print("Migración: columnas inicio/fin añadidas a tasas_periodo")

    # Migrar metodo_pago_cuenta de enum a porcentaje
    cols_metodo = {r[1] for r in conn.execute("PRAGMA table_info(metodo_pago_cuenta)").fetchall()}
    if 'metodo_pago' in cols_metodo and 'pct_cash' not in cols_metodo:
        conn.execute('''
            CREATE TABLE metodo_pago_cuenta_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year TEXT NOT NULL,
                month TEXT NOT NULL,
                unit TEXT NOT NULL,
                odoo_code TEXT NOT NULL,
                pct_cash REAL NOT NULL DEFAULT 0 CHECK(pct_cash >= 0 AND pct_cash <= 100),
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
                UNIQUE(year, month, unit, odoo_code)
            )
        ''')
        conn.execute('''
            INSERT INTO metodo_pago_cuenta_new (id, year, month, unit, odoo_code, pct_cash, created_at)
            SELECT id, year, month, unit, odoo_code,
                   CASE metodo_pago
                       WHEN 'usd_cash' THEN 100
                       WHEN 'bcv' THEN 0
                       WHEN 'ingreso_bs' THEN 0
                       ELSE 0
                   END,
                   created_at
            FROM metodo_pago_cuenta
        ''')
        conn.execute("DROP TABLE metodo_pago_cuenta")
        conn.execute("ALTER TABLE metodo_pago_cuenta_new RENAME TO metodo_pago_cuenta")
        print("Migración: metodo_pago_cuenta convertido de enum a pct_cash")

    # ── Seed / upsert del mapping inicial ────────────────────────────────────
    if INITIAL_MAPPING:
        conn.executemany(
            '''INSERT INTO mapping (odoo_code, odoo_name, partida, sign, income_type)
               VALUES (?,?,?,?,?)
               ON CONFLICT(odoo_code) DO UPDATE SET
                   odoo_name=excluded.odoo_name,
                   partida=excluded.partida,
                   sign=excluded.sign,
                   income_type=excluded.income_type''',
            INITIAL_MAPPING
        )
        print(f"[OK] {len(INITIAL_MAPPING)} cuentas insertadas/actualizadas en mapping")

    conn.commit()
    conn.close()
    print(f"DB inicializada en {DB_PATH}")


def migrate_db():
    """Ejecutar migraciones sobre BD existente sin reinicializar datos."""
    conn = sqlite3.connect(DB_PATH)

    cols = {r[1] for r in conn.execute("PRAGMA table_info(mapping)").fetchall()}
    if 'income_type' not in cols:
        conn.execute("ALTER TABLE mapping ADD COLUMN income_type TEXT DEFAULT NULL")

    cols_log = {r[1] for r in conn.execute("PRAGMA table_info(mapping_log)").fetchall()}
    if 'income_type' not in cols_log:
        conn.execute("ALTER TABLE mapping_log ADD COLUMN income_type TEXT DEFAULT NULL")

    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}

    if 'esf_data' not in tables:
        conn.execute('''CREATE TABLE esf_data (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            year    TEXT NOT NULL,
            quarter INTEGER NOT NULL,
            unit    TEXT NOT NULL,
            partida TEXT NOT NULL,
            amount  REAL NOT NULL DEFAULT 0,
            UNIQUE(year, quarter, unit, partida)
        )''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_esf ON esf_data(year, quarter, unit)')

    if 'budget' not in tables:
        conn.execute('''CREATE TABLE budget (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            year    TEXT NOT NULL,
            month   TEXT NOT NULL,
            unit    TEXT NOT NULL,
            partida TEXT NOT NULL,
            amount  REAL NOT NULL DEFAULT 0,
            UNIQUE(year, month, unit, partida)
        )''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_budget ON budget(year, month, unit)')

    if 'esf_ajuste_diferencial' not in tables:
        conn.execute('''CREATE TABLE esf_ajuste_diferencial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year TEXT NOT NULL,
            quarter INTEGER NOT NULL,
            valor REAL NOT NULL,
            updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            UNIQUE(year, quarter)
        )''')



    # Actualizar income_type en registros existentes del mapping inicial
    if INITIAL_MAPPING:
        conn.executemany(
            '''UPDATE mapping SET income_type=? WHERE odoo_code=? AND income_type IS NULL''',
            [(row[4], row[0]) for row in INITIAL_MAPPING if row[4] is not None]
        )

    conn.commit()
    conn.close()
    print("Migración completada")


def reset_mapping():
    """
    [WARN]  USAR CON PRECAUCIÓN: Borra y recrea la tabla mapping con el plan de cuentas actual.
    Solo ejecutar UNA VEZ después de verificar INITIAL_MAPPING.

    Crea backup automático antes de borrar.
    """
    if not INITIAL_MAPPING:
        return {
            'error': 'INITIAL_MAPPING está vacío. Instala pandas/openpyxl y reinicia la app.',
            'ok': False
        }

    conn = sqlite3.connect(DB_PATH)

    # Backup de seguridad
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(backup_dir, exist_ok=True)
    backup_path = os.path.join(backup_dir, f'mapping_backup_{timestamp}.csv')

    # Exportar mapping actual
    old_mapping = conn.execute('SELECT * FROM mapping').fetchall()
    if old_mapping:
        import csv
        with open(backup_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['odoo_code', 'odoo_name', 'partida', 'sign', 'income_type'])
            writer.writerows(old_mapping)
        print(f"[OK] Backup guardado en: {backup_path}")

    # Borrar tabla
    conn.execute('DELETE FROM mapping')

    # Insertar nuevo mapping
    conn.executemany(
        '''INSERT INTO mapping (odoo_code, odoo_name, partida, sign, income_type)
           VALUES (?,?,?,?,?)''',
        INITIAL_MAPPING
    )

    conn.commit()
    conn.close()

    print(f"[OK] Mapping reseteado: {len(INITIAL_MAPPING)} cuentas insertadas")
    return {
        'ok': True,
        'inserted': len(INITIAL_MAPPING),
        'backup': backup_path,
        'old_count': len(old_mapping) if old_mapping else 0
    }



