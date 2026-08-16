from constants import PARTIDAS_DIVISOR_SEGMENTADO, SUBTOTAL_INGRESO_KEYS_POR_SEGMENTO, SEGMENTOS_INGRESO_PCT_VTAS


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


# ── %Gastos: rango de partidas donde aplica ──
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


def get_clasificacion(db):
    ing = set(r['partida'] for r in db.execute("SELECT DISTINCT partida FROM mapping WHERE odoo_code LIKE '4.%'").fetchall())
    cos = set(r['partida'] for r in db.execute("SELECT DISTINCT partida FROM mapping WHERE odoo_code LIKE '5.%'").fetchall())
    gas = set(r['partida'] for r in db.execute("SELECT DISTINCT partida FROM mapping WHERE odoo_code LIKE '6.%'").fetchall())
    return ing, cos, gas


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


# ── Funciones movidas desde app.py (Fase 3, reubicación directa) ───────────

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

