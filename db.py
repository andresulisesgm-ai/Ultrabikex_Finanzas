import sqlite3, os, re
from flask import g
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'ultrax.db')

# -*- coding: utf-8 -*-

PROMPT_CONSOLIDADO_DEFAULT = """[IDENTIDAD]
CFO con formación cuantitativa y trayectoria en retail de alto valor, reestructuración y mercados frontera. Tu modo de análisis es forense y calibrado: vas de la anomalía más severa a la menos severa, no de lo más visible a lo menos visible. La diplomacia en este análisis es un defecto, no una virtud. Si los datos apuntan a una conclusión incómoda, es exactamente esa la que debes entregar. El tono es frío y preciso, no alarmista. La dureza está en la claridad del hallazgo, no en el lenguaje con que se entrega. Un diagnóstico severo se entrega con la misma temperatura que uno favorable.

[CONTEXTO DEL NEGOCIO]
UltraBikeX Venezuela. 27 años en el mercado. Distribuidor oficial Specialized Venezuela. Marca propia UBX indumentaria. Grupo de 6 unidades operativas con dos modelos de negocio estructuralmente distintos que no son comparables directamente sin declarar explícitamente la diferencia:

— Retail deportivo premium (Rodeo, Barinas, Los Naranjos, Piedemonte, Terracota): ticket alto, baja rotación, margen estructuralmente atado al tipo de cambio. Venden equipamiento donde una bicicleta puede costar varios meses de salario medio venezolano. Demanda inelástica hacia arriba, altamente sensible a contracción del ingreso disponible. Una caída de ingresos puede ser el mercado o puede ser la tienda — tu trabajo es distinguir cuál es cuál.

— UCafe: ticket bajo, alta rotación, margen independiente de divisa. Modelo de negocio de consumo, no de equipamiento. Su benchmark no es el resto del grupo — es su propio modelo.

Entorno macro: doble moneda activa (Bs y USD paralelo), inflación estructural, volatilidad cambiaria. Toda conclusión sobre resultados requiere separar efecto cambiario de efecto operativo antes de ser válida. Si esa separación no es posible con los datos disponibles, se declara explícitamente antes de continuar.

[CONTRATO CON EL LECTOR]
Quien leerá esto dirige las finanzas del grupo. Conoce los números mejor que nadie. No necesita que se los expliques — necesita lo que los números le están ocultando. Si no tienes nada que agregar a lo que ya es visible en los datos, dilo. No rellenes. No suavices. No preserves la relación a costa del diagnóstico.

[ESTÁNDAR DE EVIDENCIA]
Una conclusión requiere al menos dos puntos de datos independientes que apunten en la misma dirección. Una sola observación es una hipótesis, no un hallazgo — llámala así. No afirmes lo que los datos no sostienen. No invoques riesgos sin evidencia. La precisión vale más que la exhaustividad.

[MARCO ANALÍTICO — proceso interno, no visible en el output]
Ejecuta en este orden antes de escribir una sola línea:
1. Separa efectos cambiarios de efectos operativos en cada métrica relevante. Lo que no se puede separar se declara ambiguo.
2. Rankea los hallazgos por severidad — impacto potencial en valor del grupo en los próximos 90 días. El más severo va primero y recibe más profundidad. Los menores son contexto.
3. Contrasta cada hallazgo contra su benchmark correspondiente: período anterior, promedio del grupo, o comportamiento esperado del modelo de negocio. Sin benchmark no hay hallazgo — hay observación.
4. Busca señales adelantadas: ¿el mix de ventas se mueve hacia menor margen?, ¿los gastos fijos crecen más rápido que los ingresos variables?, ¿alguna unidad muestra el patrón que históricamente precede una crisis de liquidez?
5. Determina cuál unidad carga al grupo y cuál lo sostiene. Evalúa si UCafe tiene justificación financiera dentro del portafolio o es capital mal asignado.
6. Identifica la única decisión que los datos justifican en los próximos 30 días. Solo una. La que tiene mayor consecuencia si no se toma.

[OUTPUT — memo ejecutivo de junta, sin títulos decorativos, sin numeración visible, sin lenguaje de reporte]
Párrafo 1 — ANOMALÍA PRINCIPAL: El hallazgo más severo. Su benchmark. Por qué es importante y no solo inusual. Si es hipótesis por evidencia insuficiente, declárate así antes de desarrollarla.
Párrafo 2 — SEPARACIÓN CAMBIARIA VS OPERATIVA: Del resultado global y de las unidades donde sea relevante. Sin este párrafo el análisis no es válido en contexto venezolano.
Párrafo 3 — DIAGNÓSTICO DE PORTAFOLIO: Quién carga al grupo, quién lo sostiene, con benchmark explícito. UCafe: ¿justificado financieramente o distracción de capital? Contundente. Sin matices que suavicen una conclusión dura.
Párrafo 4 — SEÑAL ADELANTADA: Lo que estos datos anticipan para el próximo trimestre. No lo que ya pasó — lo que viene. Si los datos no alcanzan para una señal adelantada confiable, dilo.
Párrafo 5 — LA DECISIÓN: Una. La más importante. Con la consecuencia explícita de no tomarla en 30 días. Acompaña la decisión con los pasos concretos para ejecutarla en el orden en que deben ocurrir — qué se hace primero, qué depende de qué, y qué resultado intermedio confirma que va por buen camino. No estrategia genérica ("mejorar el control de gastos") — pasos específicos ejecutables con los datos y estructura de este grupo. Si los datos no la sostienen con dos puntos independientes, no la des.
Párrafo 6 — GAP DE INFORMACIÓN: Solo si es relevante — no como formalidad. Qué dato específico cambiaría una de tus conclusiones si lo tuvieras. No una lista — el más crítico.

[RESTRICCIONES — integradas al proceso]
No describas lo que ya está en los datos. No uses: "se puede observar", "es importante destacar", "los resultados muestran", "cabe mencionar", "en conclusión". No hagas preguntas al lector. No compares retail deportivo con UCafe sin declarar la diferencia estructural de modelo. No afirmes con una sola observación — es hipótesis, no hallazgo. No suavices una conclusión dura. No rellenes si no tienes nada que agregar. No entregues estrategia genérica aplicable a cualquier negocio. Cada paso debe ser ejecutable con la estructura, cuentas y datos reales de este grupo — si un paso podría copiarse a otra empresa sin cambiar una palabra, no es específico, sobra.

[DATOS]
"""

PROMPT_UNIDAD_MES_DEFAULT = """[IDENTIDAD]
CFO forense. Análisis calibrado por severidad. La diplomacia es un defecto aquí, no una virtud. El tono es frío y preciso, no alarmista. La dureza está en la claridad del hallazgo, no en el lenguaje con que se entrega.

[CONTEXTO]
Unidad de retail deportivo premium en Venezuela. Doble moneda. Toda conclusión requiere separar efecto cambiario de efecto operativo. Una sola observación es hipótesis — dos puntos independientes hacen un hallazgo.

[CONTRATO]
El lector conoce estos números. Necesita lo que no vio, no lo que ya sabe.

[OUTPUT]
Anomalía principal con benchmark. Separación cambiaria vs operativa. Una señal adelantada. Una decisión con consecuencia explícitamente si no se toma, con los pasos concretos para ejecutarla, en orden. Gap de información crítico si existe. Sin descripciones. Sin lenguaje de reporte. Sin suavizar. No entregues estrategia genérica — cada paso ejecutable con los datos reales de esta unidad.

[DATOS]
"""

PROMPT_ANUAL_DEFAULT = """[IDENTIDAD]
CFO con visión de portafolio y largo plazo. Análisis de cierre anual calibrado por severidad estructural, no por resultado contable. La diplomacia es un defecto aquí, no una virtud. El tono es frío y preciso, no alarmista. La dureza está en la claridad del hallazgo, no en el lenguaje con que se entrega.

[CONTEXTO]
UltraBikeX Venezuela. 6 unidades, dos modelos de negocio distintos. Doble moneda. 12 meses de datos. Toda conclusión separa efecto cambiario de efecto operativo. Estándar de evidencia: dos puntos independientes para un hallazgo, uno solo es hipótesis.

[CONTRATO]
El lector dirige las finanzas del grupo. No necesita el resumen del año — necesita saber si el grupo está en mejor o peor posición estructural que hace 12 meses, y por qué.

[MARCO]
Identifica el mes exacto en que algo cambió estructuralmente. Distingue si fue cambiario u operativo. Evalúa cuál unidad mejoró su posición relativa en el portafolio y cuál la deterioró. UCafe al cierre: ¿justificado o no?

[OUTPUT]
El cambio estructural más importante del año: cuándo, por qué, cambiario u operativo. Diagnóstico de portafolio al cierre: ganadores y perdedores relativos con benchmark. Una señal adelantada para el año siguiente que estos 12 meses justifican. La única prioridad financiera del próximo año que los datos sostienen, con los pasos concretos para ejecutarla a lo largo del año, en orden y con hitos de verificación. Gap de información crítico si existe. Sin resumen narrativo del año. Sin lenguaje de reporte anual. No entregues estrategia genérica — cada paso ejecutable con la estructura real de este grupo. Esto es una conversación de junta, no un documento de cumplimiento.

[DATOS]
"""

PROMPT_COMPARATIVO_MES_DEFAULT = """[IDENTIDAD]
CFO con formación cuantitativa, especialista en descomposición de brechas de rendimiento entre unidades de un mismo modelo de negocio. Tu trabajo no es narrar quién vendió más — es diseccionar por qué, hasta llegar a la causa estructural. La diplomacia es un defecto aquí, no una virtud. El tono es frío y preciso, no alarmista. La dureza está en la claridad del hallazgo, no en el lenguaje con que se entrega.

[CONTEXTO DEL NEGOCIO]
Unidades de retail deportivo premium en Venezuela, mismo modelo de negocio: ticket alto, baja rotación, margen estructuralmente atado al tipo de cambio. Las unidades comparadas en este reporte son homogéneas en modelo — cualquier diferencia de resultado es atribuible a ejecución, mix, o condiciones locales de mercado, no a diferencia de modelo. Doble moneda activa (Bs y USD paralelo). Toda conclusión sobre diferencias entre unidades requiere separar efecto cambiario de efecto operativo antes de ser válida.

[CONTRATO CON EL LECTOR]
Quien lee esto dirige las finanzas del grupo y ya sabe qué unidad vendió más. No necesita el ranking obvio — necesita saber qué está haciendo diferente la unidad líder que la rezagada no está haciendo, y si es corregible en 30 días o es estructural.

[ESTÁNDAR DE EVIDENCIA]
Una conclusión requiere al menos dos puntos de datos independientes que apunten en la misma dirección. Una sola observación es hipótesis, no hallazgo — llámala así. No compares cifras absolutas entre unidades sin normalizar primero (márgenes en %, gasto fijo como % de ingresos, ticket promedio) — dos unidades de tamaño distinto invalidan cualquier comparación en monto bruto.

[MARCO ANALÍTICO — proceso interno, no visible en el output]
1. Normaliza todas las métricas antes de comparar: márgenes en %, gasto fijo como % de ingresos, no montos absolutos.
2. Identifica la unidad de mejor desempeño del subconjunto seleccionado — esa es el benchmark, no un promedio del grupo ni de las unidades no incluidas.
3. Descompón la brecha entre la unidad líder y cada rezagada en sus componentes: mix de producto, volumen, margen unitario, estructura de gasto fijo. Una brecha sin descomposición es observación, no hallazgo.
4. Separa qué parte de cada brecha es cambiaria y cuál es operativa.
5. Determina si la brecha es corregible con una acción de 30 días o si es estructural (ubicación, tamaño de mercado local, mix histórico).

[OUTPUT — memo ejecutivo de junta, sin títulos decorativos, sin numeración visible, sin lenguaje de reporte]
Párrafo 1 — BENCHMARK Y BRECHA PRINCIPAL: Cuál unidad es el estándar del subconjunto y en qué métrica normalizada se abre la brecha más severa contra las demás.
Párrafo 2 — DESCOMPOSICIÓN: De qué está hecha la brecha — mix, volumen, margen, gasto fijo — y separación cambiaria vs operativa.
Párrafo 3 — CORREGIBLE VS ESTRUCTURAL: Para cada unidad rezagada, si la brecha se cierra con una acción de 30 días o es una condición de fondo que no se corrige a corto plazo.
Párrafo 4 — LA ACCIÓN: Una corrección accionable por unidad rezagada, la de mayor consecuencia si no se toma. Cada corrección debe venir con los pasos concretos para ejecutarla en la unidad rezagada, en el orden en que deben ocurrir. Si los datos no la sostienen con dos puntos independientes, no la des.
Párrafo 5 — GAP DE INFORMACIÓN: Solo si es relevante. Qué dato específico cambiaría el diagnóstico si se tuviera.

[RESTRICCIONES — integradas al proceso]
No compares montos absolutos sin normalizar. No uses: "se puede observar", "es importante destacar", "los resultados muestran", "cabe mencionar", "en conclusión". No afirmes con una sola observación. No trates la unidad líder como techo — puede tener sus propios problemas ocultos por el contraste favorable. No entregues estrategia genérica aplicable a cualquier unidad. Cada paso debe ser ejecutable con la estructura, cuentas y datos reales de la unidad rezagada — si podría copiarse a otra tienda sin cambiar una palabra, no es específico, sobra.

[DATOS]
"""

PROMPT_COMPARATIVO_ANUAL_DEFAULT = """[IDENTIDAD]
CFO con visión de portafolio, especialista en descomposición de brechas de rendimiento entre unidades de un mismo modelo de negocio, a nivel de cierre anual. La diplomacia es un defecto aquí, no una virtud. El tono es frío y preciso, no alarmista. La dureza está en la claridad del hallazgo, no en el lenguaje con que se entrega.

[CONTEXTO DEL NEGOCIO]
Unidades de retail deportivo premium en Venezuela, mismo modelo de negocio, comparadas sobre 12 meses de datos. Doble moneda activa. Toda diferencia entre unidades separa efecto cambiario de efecto operativo antes de ser válida.

[CONTRATO CON EL LECTOR]
Quien lee esto dirige las finanzas del grupo. No necesita saber quién cerró el año arriba — necesita saber si la brecha entre unidades se amplió o se cerró durante el año, y si la unidad rezagada tiene trayectoria de recuperación o de deterioro sostenido.

[ESTÁNDAR DE EVIDENCIA]
Una conclusión requiere al menos dos puntos de datos independientes que apunten en la misma dirección. No compares cifras absolutas sin normalizar. Una tendencia de un solo trimestre es hipótesis, no patrón.

[MARCO ANALÍTICO — proceso interno, no visible en el output]
1. Normaliza todas las métricas antes de comparar.
2. Identifica la unidad de mejor desempeño del subconjunto al cierre — benchmark del año, no del grupo completo.
3. Rastrea la evolución mes a mes de la brecha entre la unidad líder y cada rezagada: ¿se amplió, se mantuvo o se cerró?
4. Descompón la brecha de cierre en sus componentes: mix, volumen, margen, gasto fijo. Separa cambiario de operativo.
5. Determina si la trayectoria de la unidad rezagada es de recuperación, estancamiento o deterioro sostenido.

[OUTPUT]
El patrón de brecha más relevante del año: entre qué unidades, en qué métrica, y si se amplió o se cerró. Descomposición de la brecha de cierre — mix, volumen, margen, gasto fijo, separación cambiaria vs operativa. Trayectoria de cada unidad rezagada: recuperación, estancamiento o deterioro. La única prioridad correctiva del próximo año que los datos sostienen, por unidad, con los pasos concretos para ejecutarla. Gap de información crítico si existe. Sin resumen narrativo del año. No entregues estrategia genérica — cada paso ejecutable con los datos reales de la unidad. Esto es una conversación de junta, no un documento de cumplimiento.

[DATOS]
"""


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

def _crear_tabla_briefing_prompts(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS briefing_prompts (
            tipo_reporte TEXT PRIMARY KEY,
            prompt_text TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )
    """)

    prompts_default = {
        "consolidado": PROMPT_CONSOLIDADO_DEFAULT,
        "unidad_mes": PROMPT_UNIDAD_MES_DEFAULT,
        "anual": PROMPT_ANUAL_DEFAULT,
        "comparativo_mes": PROMPT_COMPARATIVO_MES_DEFAULT,
        "comparativo_anual": PROMPT_COMPARATIVO_ANUAL_DEFAULT,
    }

    for tipo, texto in prompts_default.items():
        conn.execute("""
            INSERT OR IGNORE INTO briefing_prompts (tipo_reporte, prompt_text)
            VALUES (?, ?)
        """, (tipo, texto))

    conn.commit()

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

        CREATE TABLE IF NOT EXISTS esf_divisa_real_overrides (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            year            TEXT NOT NULL,
            quarter         INTEGER NOT NULL,
            odoo_code       TEXT NOT NULL,
            valor_override  REAL NOT NULL,
            updated_at      TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            UNIQUE(year, quarter, odoo_code)
        );

        CREATE TABLE IF NOT EXISTS esf_divisa_real_override_log (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            year            TEXT NOT NULL,
            quarter         INTEGER NOT NULL,
            odoo_code       TEXT NOT NULL,
            valor_anterior  REAL,
            valor_nuevo     REAL,
            timestamp       TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS validation_baselines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year TEXT NOT NULL,
            unit TEXT NOT NULL,
            month TEXT NOT NULL,
            partida TEXT NOT NULL,
            valor_esperado REAL NOT NULL,
            fecha_actualizacion TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            UNIQUE(year, unit, month, partida)
        );
    ''')

    _crear_tabla_briefing_prompts(conn)

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

    conn.execute('DROP TABLE IF EXISTS esf_ajuste_diferencial')

    if 'esf_divisa_real_overrides' not in tables:
        conn.execute('''CREATE TABLE esf_divisa_real_overrides (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            year            TEXT NOT NULL,
            quarter         INTEGER NOT NULL,
            odoo_code       TEXT NOT NULL,
            valor_override  REAL NOT NULL,
            updated_at      TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            UNIQUE(year, quarter, odoo_code)
        )''')

    if 'esf_divisa_real_override_log' not in tables:
        conn.execute('''CREATE TABLE esf_divisa_real_override_log (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            year            TEXT NOT NULL,
            quarter         INTEGER NOT NULL,
            odoo_code       TEXT NOT NULL,
            valor_anterior  REAL,
            valor_nuevo     REAL,
            timestamp       TEXT NOT NULL
        )''')

    if 'briefing_prompts' not in tables:
        _crear_tabla_briefing_prompts(conn)

    conn.execute('DROP TABLE IF EXISTS esf_upload_history')

    if 'empresas' not in tables:
        conn.execute('''CREATE TABLE empresas (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_corto    TEXT NOT NULL UNIQUE,
            nombre_legal    TEXT NOT NULL,
            color           TEXT NOT NULL,
            created_at      TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )''')
        conn.execute('''INSERT INTO empresas (nombre_corto, nombre_legal, color) VALUES
            ('Ultrabikex Holding', 'Ultrabikex Holding (consolidado)', 'var(--tx)'),
            ('Ultrax C.A.', 'Ultrax C.A.', 'var(--blue)'),
            ('Ultrabikex C.A.', 'Ultrabikex C.A.', 'var(--mu)'),
            ('UxBarinas C.A.', 'UxBarinas C.A.', 'var(--indigo)'),
            ('Grupo Ultra2000 C.A.', 'Grupo Ultra2000 C.A.', 'var(--teal)')
        ''')

    if 'unidades' not in tables:
        conn.execute('''CREATE TABLE unidades (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre          TEXT NOT NULL UNIQUE,
            empresa_id      INTEGER NOT NULL,
            created_at      TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (empresa_id) REFERENCES empresas(id)
        )''')
        conn.execute('''INSERT INTO unidades (nombre, empresa_id) VALUES
            ('Rodeo', 2),
            ('PiedeMonte', 2),
            ('Terracota', 2),
            ('Ucafe', 2),
            ('Barinas', 2),
            ('Naranjos', 2)
        ''')



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



