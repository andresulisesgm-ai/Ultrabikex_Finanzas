#!/usr/bin/env python3
"""
Script de validación automática del EERR.
Compara los valores calculados por el sistema contra valores esperados del Excel.

Uso:
    python validador_eerr.py

Output:
    PASS/FAIL/MISSING por cada partida con detalles de diferencias
"""

import sqlite3
import sys
from pathlib import Path

# Valores esperados extraídos del Excel "2 EEFF ULTRAX Rodeo.xlsx"
# Sheet: N EERR RODEO, Columna: ENE, Unidad: Rodeo, Año: 2026
EXPECTED = {
    "Total Ingresos": 48122.01,
    "Ingresos por venta de mercancias": 47933.03,
    "Total Costo de Ventas": 20670.85,
    "Costos de venta por mercancia": 20670.85,
    "Utilidad Bruta": 27451.16,
    "Total Gastos Operacionales": 12855.64,
    "Subtotal Gastos de Administración": 7181.20,
    "Gastos de servicios públicos (Agua, luz, Aseo Urbano)": 91.41,
    "Gastos de servicios de telefonía e internet": 21.60,
    "Gastos de alquiler del local": 1460.74,
    "Gastos de Condominio": 1879.61,
    "Gastos de asistencia outsorcing": 965.72,
    "Gastos de alquiler de bienes muebles": 122.00,
    "Gastos de artículos de oficina": 34.95,
    "Gastos de artículos de limpieza e higiene": 98.84,
    "Gastos de alimentos y bebidas": 114.90,
    "Gastos de retenciones no descontadas": 0.06,
    "Gastos de impuesto por licencia de actividades economicas": 864.63,
    "Gasto por impuesto a las pensiones": 111.49,
    "Gastos de comisiones bancarias": 774.08,
    "Gastos de IGTF": 641.17,
    "Subtotal Gastos de Recursos Humanos": 2123.88,
    "Gastos de sueldos y salarios empleados": 205.50,
    "Gastos de sueldos y salarios directivos": 0.0,
    "Gastos de horas extras, feriados y bono nocturno": 0.0,
    "Gastos de complemento de sueldos y salarios empleados": 906.50,
    "Gastos de complemento de sueldos y salarios directivos": 0.0,
    "Gastos de Bono de alimentación empleados": 240.00,
    "Gastos de Bono de alimentación directivos": 0.0,
    "Gastos de servicios de personal externo": 5.00,
    "Gastos de aporte patronal IVSS": 1.48,
    "Gastos de aporte patronal SPF": 0.59,
    "Gastos de aporte patronal FAOV": 5.39,
    "Gastos de aporte patronal INCES": 11.57,
    "Gastos de bono de guardería": 0.0,
    "Gastos de póliza HCM": 98.70,
    "Gastos de salud y seguridad laboral": 12.82,
    "Gastos de uniformes y dotación al personal": 0.0,
    "Gastos de fiestas y agasajos al personal": 394.83,
    "Gastos de donaciones y obsequios al personal": 0.0,
    "Gastos de capacitación al personal": 0.0,
    "Gastos de transporte del personal": 241.50,
    "Subtotal Gastos de Comercialización y Logistica": 3337.60,
    "Gastos de comisiones empleados": 834.62,
    "Gastos de comisiones por venta de personal externo": 2502.98,
    "Subtotal Gastos de Mercadeo": 212.96,
    "Gastos de medios publicitarios": 129.32,
    "Gastos de impresiones de material gráfico": 83.64,
    "Otros Gastos no Operacionales": 18109.17,
    "Faltante en Ventas": 21.64,
    "Pérdida en tasa cambiaria": 18087.53,
    "Otros Ingresos no Operacionales": 188.98,
    "Utilidad Neta": -3324.67,
    "Utilidad Neta despues de ISLR": -3324.67,
}

TOLERANCE = 0.10  # Tolerancia de redondeo

# Parámetros de consulta
YEAR = '2026'
MONTH = 'ENE'
UNIT = 'Rodeo'


def get_db():
    """Conectar a la base de datos"""
    db_path = Path(__file__).parent / 'data' / 'ultrax.db'
    if not db_path.exists():
        print(f"ERROR: Base de datos no encontrada en {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def get_clasificacion(db):
    """Obtener clasificación de partidas por tipo"""
    ing = set(r['partida'] for r in db.execute(
        "SELECT DISTINCT partida FROM mapping WHERE odoo_code LIKE '4.%'"
    ).fetchall())

    cos = set(r['partida'] for r in db.execute(
        "SELECT DISTINCT partida FROM mapping WHERE odoo_code LIKE '5.%'"
    ).fetchall())

    gas = set(r['partida'] for r in db.execute(
        "SELECT DISTINCT partida FROM mapping WHERE odoo_code LIKE '6.%'"
    ).fetchall())

    return ing, cos, gas


def get_groups(db):
    """Obtener grupos de presentación"""
    rows = db.execute(
        "SELECT group_name, odoo_code FROM mapping_groups WHERE report_type='eerr'"
    ).fetchall()

    groups = {}
    for r in rows:
        group_name = r['group_name']
        odoo_code = r['odoo_code']

        # Obtener la partida del código
        m = db.execute(
            "SELECT partida FROM mapping WHERE odoo_code=?", (odoo_code,)
        ).fetchone()

        if m:
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(m['partida'])

    return groups


def calcular_eerr(db):
    """Calcular el EERR usando la misma lógica que el sistema"""
    from new_eerr_structure import EERR_STRUCTURE

    # Leer datos del mes
    rows = db.execute(
        '''SELECT partida, SUM(amount) as amount FROM financials
           WHERE year=? AND month=? AND unit=?
           GROUP BY partida''',
        (YEAR, MONTH, UNIT)
    ).fetchall()

    by_partida = {r['partida']: r['amount'] for r in rows}

    # Clasificar partidas
    ing_p, cos_p, gas_p = get_clasificacion(db)
    all_partidas = ing_p | cos_p | gas_p

    # Obtener grupos
    groups = get_groups(db)
    grouped_partidas = set()
    for partidas in groups.values():
        grouped_partidas.update(partidas)

    # Calcular subtotales jerárquicos
    subtotales = {}

    for i, item in enumerate(EERR_STRUCTURE):
        partida_name = item[0]
        is_header = item[1]
        level = item[5] if len(item) > 5 else 3

        if not is_header:
            continue

        total = 0
        j = i + 1

        while j < len(EERR_STRUCTURE):
            child_item = EERR_STRUCTURE[j]
            child_name = child_item[0]
            child_is_header = child_item[1]
            child_level = child_item[5] if len(child_item) > 5 else 3

            # Solo break si encontramos un header del mismo nivel o superior
            if child_is_header and child_level <= level:
                break

            # Buscar partidas que coincidan
            if child_name in groups:
                matching = groups[child_name]
            else:
                matching = [p for p in all_partidas
                           if p.lower() == child_name.lower()
                           and p not in grouped_partidas]

            for p in matching:
                total += by_partida.get(p, 0)

            j += 1

        subtotales[partida_name] = total

    # Calcular totales especiales
    resultados = {}

    # Total Costo de Ventas
    resultados['Total Costo de Ventas'] = sum(by_partida.get(p, 0) for p in cos_p)

    # Total Gastos Operacionales
    gastos_operacionales = 0
    for nombre in ['Subtotal Gastos de Administración',
                   'Subtotal Gastos de Recursos Humanos',
                   'Subtotal Gastos de Comercialización y Logistica',
                   'Subtotal Gastos de Mercadeo',
                   'Subtotal Gastos de TI+I']:
        gastos_operacionales += subtotales.get(nombre, 0)
    resultados['Total Gastos Operacionales'] = gastos_operacionales

    # Agregar subtotales PRIMERO
    resultados.update(subtotales)

    # Agregar partidas individuales
    for partida, monto in by_partida.items():
        if partida not in resultados:
            resultados[partida] = monto

    # AHORA calcular partidas derivadas (después del update para no ser sobrescritas)

    # Total Ingresos = Ingresos Operativos + Otros Ingresos no Operacionales
    ingresos_operativos = sum(by_partida.get(p, 0) for p in ing_p if not p.startswith('Ganancia')
                              and not p.startswith('Sobrante') and not p.startswith('Ingresos por comisiones')
                              and not p.startswith('Ingresos por intereses') and not p.startswith('Ingresos por alquileres')
                              and not p.startswith('Ingresos por servicios administrativos'))
    otros_ingresos_no_op = resultados.get('Otros Ingresos no Operacionales', 0)
    resultados['Total Ingresos'] = ingresos_operativos + otros_ingresos_no_op

    # Utilidad Bruta
    resultados['Utilidad Bruta'] = resultados['Total Ingresos'] - resultados['Total Costo de Ventas']

    # Utilidad antes de Comisiones
    resultados['Utilidad antes de Comisiones por Ventas'] = (
        resultados['Utilidad Bruta'] - resultados['Total Gastos Operacionales']
    )

    # Comisiones
    comisiones = 0
    for nombre in ['Gastos de comisiones por ventas', 'Gastos de comisiones por ventas taller']:
        comisiones += subtotales.get(nombre, 0)

    # Utilidad después de Comisiones
    resultados['Utilidad después de Comisiones por Ventas'] = (
        resultados['Utilidad antes de Comisiones por Ventas'] - comisiones
    )

    # Utilidad Neta
    resultados['Utilidad Neta'] = (
        resultados['Utilidad después de Comisiones por Ventas'] -
        resultados.get('Otros Gastos no Operacionales', 0) +
        resultados.get('Otros Ingresos no Operacionales', 0)
    )

    # Utilidad Neta después de ISLR
    islr = resultados.get('ISLR', 0)
    resultados['Utilidad Neta despues de ISLR'] = resultados['Utilidad Neta'] - islr

    return resultados


def normalizar_nombre(nombre):
    """Normalizar nombre para comparación"""
    return nombre.lower().strip()


def buscar_en_resultados(nombre_esperado, resultados):
    """Buscar una partida en los resultados con coincidencia flexible"""
    # Intentar coincidencia exacta primero
    if nombre_esperado in resultados:
        return resultados[nombre_esperado]

    # Intentar coincidencia case-insensitive
    norm_esperado = normalizar_nombre(nombre_esperado)
    for nombre, valor in resultados.items():
        if normalizar_nombre(nombre) == norm_esperado:
            return valor

    # Intentar coincidencia parcial
    for nombre, valor in resultados.items():
        if norm_esperado in normalizar_nombre(nombre) or normalizar_nombre(nombre) in norm_esperado:
            return valor

    return None


def validar():
    """Ejecutar validación completa"""
    print("="*80)
    print(f"VALIDADOR EERR - {UNIT} {MONTH} {YEAR}")
    print("="*80)
    print()

    db = get_db()
    resultados = calcular_eerr(db)
    db.close()

    passed = 0
    failed = 0
    missing = 0

    resultados_validacion = []

    for partida_esperada, valor_esperado in sorted(EXPECTED.items()):
        valor_sistema = buscar_en_resultados(partida_esperada, resultados)

        if valor_sistema is None:
            status = "MISSING"
            missing += 1
            delta = None
            resultado = f"{status:8s} {partida_esperada:50s} expected={valor_esperado:>12,.2f}"
        else:
            delta = abs(valor_sistema - valor_esperado)

            if delta <= TOLERANCE:
                status = "PASS"
                passed += 1
                resultado = f"{status:8s} {partida_esperada:50s} sistema={valor_sistema:>12,.2f}  expected={valor_esperado:>12,.2f}"
            else:
                status = "FAIL"
                failed += 1
                diferencia = valor_sistema - valor_esperado
                resultado = f"{status:8s} {partida_esperada:50s} sistema={valor_sistema:>12,.2f}  expected={valor_esperado:>12,.2f}  delta={diferencia:>+12,.2f}"

        resultados_validacion.append((status, resultado))

    # Imprimir resultados agrupados por estado
    for estado in ["PASS", "FAIL", "MISSING"]:
        items = [r for s, r in resultados_validacion if s == estado]
        if items:
            print(f"\n{estado}:")
            print("-" * 80)
            for item in items:
                print(item)

    # Resumen
    print()
    print("="*80)
    print(f"RESUMEN: {passed} PASS / {failed} FAIL / {missing} MISSING")
    print("="*80)

    # Detalle de problemas críticos
    if failed > 0 or missing > 0:
        print()
        print("PROBLEMAS DETECTADOS:")
        print("-" * 80)

        if missing > 0:
            print(f"\n{missing} partidas FALTANTES en EERR_STRUCTURE:")
            print("  -> Estas partidas tienen montos en la BD pero no aparecen en el EERR")
            print("  -> Revisa diagnostico_eerr.txt para ver que cuentas estan mapeadas a ellas")

        if failed > 0:
            print(f"\n{failed} partidas con VALORES INCORRECTOS:")
            print("  -> Los subtotales probablemente estan mal calculados")
            print("  -> Verifica la logica de agrupacion en calcular_subtotales_jerarquicos()")

    return passed, failed, missing


if __name__ == '__main__':
    try:
        passed, failed, missing = validar()

        # Exit code: 0 si todo OK, 1 si hay problemas
        sys.exit(0 if (failed == 0 and missing == 0) else 1)

    except Exception as e:
        print(f"\nERROR FATAL: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(2)
