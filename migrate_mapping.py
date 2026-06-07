#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de migración del plan de cuentas.

ADVERTENCIA: Este script ejecutará reset_mapping() que borrará y recreará
la tabla mapping completa. Se creará un backup automático antes de proceder.

Uso:
    python migrate_mapping.py --validate    # Solo validar sin cambios
    python migrate_mapping.py --execute     # Ejecutar migración completa
"""

import sys
import os

# Añadir el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import INITIAL_MAPPING, reset_mapping, migrate_db, seed_initial_groups, INITIAL_GROUPS
import sqlite3


def validate_mapping():
    """Valida el INITIAL_MAPPING antes de aplicar."""
    print("=" * 80)
    print("VALIDACIÓN DEL PLAN DE CUENTAS")
    print("=" * 80)

    if not INITIAL_MAPPING:
        print("[ERROR] ERROR: INITIAL_MAPPING está vacío")
        print("   Asegúrate de tener pandas y openpyxl instalados:")
        print("   pip install pandas openpyxl")
        return False

    print(f"[OK] Total de cuentas: {len(INITIAL_MAPPING)}")

    # Validar que no haya duplicados
    codes = [m[0] for m in INITIAL_MAPPING]
    if len(codes) != len(set(codes)):
        duplicates = [c for c in codes if codes.count(c) > 1]
        print(f"[ERROR] ERROR: Hay códigos duplicados: {set(duplicates)}")
        return False
    print("[OK] No hay códigos duplicados")

    # Validar que las cuentas especiales tengan sign correcto
    dep_acum = [m for m in INITIAL_MAPPING if '.500' in m[0] or '.501' in m[0]]
    if dep_acum and not all(m[3] == -1 for m in dep_acum):
        wrong = [m[0] for m in dep_acum if m[3] != -1]
        print(f"[ERROR] ERROR: Depreciaciones/Deterioros Acum deben tener sign=-1: {wrong}")
        return False
    if dep_acum:
        print(f"[OK] {len(dep_acum)} cuentas de Dep/Det Acum con sign=-1 correcto")

    # Validar income_types
    valid_types = {None, 'mercancia', 'servicios', 'eventos', 'taller'}
    invalid = [m for m in INITIAL_MAPPING if m[4] not in valid_types]
    if invalid:
        print(f"[ERROR] ERROR: income_type inválido en: {[m[0] for m in invalid[:5]]}")
        return False

    income_typed = [m for m in INITIAL_MAPPING if m[4] is not None]
    print(f"[OK] {len(income_typed)} cuentas con income_type asignado")

    # Distribución por tipo
    print("\n[STATS] DISTRIBUCIÓN DE CUENTAS:")
    activos = len([m for m in INITIAL_MAPPING if m[0].startswith('1.')])
    pasivos = len([m for m in INITIAL_MAPPING if m[0].startswith('2.')])
    patrimonio = len([m for m in INITIAL_MAPPING if m[0].startswith('3.')])
    ingresos = len([m for m in INITIAL_MAPPING if m[0].startswith('4.')])
    costos = len([m for m in INITIAL_MAPPING if m[0].startswith('5.')])
    gastos = len([m for m in INITIAL_MAPPING if m[0].startswith('6.')])

    print(f"   Activos (1.x):     {activos}")
    print(f"   Pasivos (2.x):     {pasivos}")
    print(f"   Patrimonio (3.x):  {patrimonio}")
    print(f"   Ingresos (4.x):    {ingresos}")
    print(f"   Costos (5.x):      {costos}")
    print(f"   Gastos (6.x):      {gastos}")

    # Distribución por income_type
    print("\n[STATS] DISTRIBUCIÓN POR TIPO DE INGRESO/COSTO:")
    mercancia = len([m for m in INITIAL_MAPPING if m[4] == 'mercancia'])
    servicios = len([m for m in INITIAL_MAPPING if m[4] == 'servicios'])
    eventos = len([m for m in INITIAL_MAPPING if m[4] == 'eventos'])
    taller = len([m for m in INITIAL_MAPPING if m[4] == 'taller'])

    print(f"   Mercancía:  {mercancia}")
    print(f"   Servicios:  {servicios}")
    print(f"   Eventos:    {eventos}")
    print(f"   Taller:     {taller}")

    # Validar grupos iniciales
    print(f"\n[OK] Grupos iniciales definidos: {len(INITIAL_GROUPS)}")
    group_names = set(g[0] for g in INITIAL_GROUPS)
    print(f"   Grupos únicos: {len(group_names)}")
    for gname in sorted(group_names):
        count = len([g for g in INITIAL_GROUPS if g[0] == gname])
        print(f"   - {gname}: {count} cuentas")

    print("\n" + "=" * 80)
    print("[OK] VALIDACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 80)

    return True


def execute_migration():
    """Ejecuta la migración completa."""
    print("\n" + "=" * 80)
    print("EJECUTANDO MIGRACIÓN")
    print("=" * 80)

    # Paso 1: Validar
    if not validate_mapping():
        print("[ERROR] Validación falló. Abortando migración.")
        return False

    # Paso 2: Confirmar con usuario
    print("\n[WARN]  ADVERTENCIA: Esta operación borrará y recreará la tabla mapping.")
    print("   Se creará un backup automático antes de proceder.")
    confirm = input("\n¿Deseas continuar? (escribe 'SI' en mayúsculas): ")

    if confirm != 'SI':
        print("[ERROR] Migración cancelada por el usuario.")
        return False

    # Paso 3: Ejecutar migrate_db (crear tabla mapping_groups si no existe)
    print("\n[STEP] Paso 1/3: Ejecutando migrate_db()...")
    try:
        migrate_db()
        print("[OK] migrate_db() completado")
    except Exception as e:
        print(f"[ERROR] Error en migrate_db(): {e}")
        return False

    # Paso 4: Ejecutar reset_mapping
    print("\n[STEP] Paso 2/3: Ejecutando reset_mapping()...")
    try:
        result = reset_mapping()
        if result.get('ok'):
            print(f"[OK] reset_mapping() completado")
            print(f"   - Cuentas insertadas: {result.get('inserted')}")
            print(f"   - Backup guardado en: {result.get('backup')}")
        else:
            print(f"[ERROR] Error en reset_mapping(): {result.get('error')}")
            return False
    except Exception as e:
        print(f"[ERROR] Error en reset_mapping(): {e}")
        return False

    # Paso 5: Insertar grupos iniciales
    print("\n[STEP] Paso 3/3: Insertando grupos iniciales...")
    try:
        seed_initial_groups()
        print("[OK] Grupos iniciales insertados")
    except Exception as e:
        print(f"[ERROR] Error en seed_initial_groups(): {e}")
        return False

    # Verificación final
    print("\n[STEP] Verificación final...")
    from db import DB_PATH
    conn = sqlite3.connect(DB_PATH)

    mapping_count = conn.execute('SELECT COUNT(*) FROM mapping').fetchone()[0]
    groups_count = conn.execute('SELECT COUNT(DISTINCT group_name) FROM mapping_groups').fetchone()[0]
    assignments_count = conn.execute('SELECT COUNT(*) FROM mapping_groups').fetchone()[0]

    print(f"   - Cuentas en mapping: {mapping_count}")
    print(f"   - Grupos definidos: {groups_count}")
    print(f"   - Asignaciones: {assignments_count}")

    conn.close()

    print("\n" + "=" * 80)
    print("[OK] MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 80)
    print("\n[SUCCESS] El sistema está listo para usar el nuevo plan de cuentas.")
    print("   Reinicia la aplicación con: python app.py")

    return True


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    mode = sys.argv[1]

    if mode == '--validate':
        success = validate_mapping()
        sys.exit(0 if success else 1)

    elif mode == '--execute':
        success = execute_migration()
        sys.exit(0 if success else 1)

    else:
        print(f"[ERROR] Modo desconocido: {mode}")
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()

