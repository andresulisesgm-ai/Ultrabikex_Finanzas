#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de diagnóstico del mapping actual.

Muestra:
1. Cuentas en mapping vs cuentas en financials/esf_data
2. Cuentas que se auto-mapearon
3. Cuentas potencialmente sin match
4. Estadísticas generales

Uso:
    python diagnostico_mapping.py
"""

import sqlite3
import os
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'ultrax.db')

def main():
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Base de datos no encontrada: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    print("="*80)
    print("DIAGNÓSTICO DEL MAPPING")
    print("="*80)

    # 1. Estadísticas de mapping
    total_mapping = conn.execute('SELECT COUNT(*) FROM mapping').fetchone()[0]
    print(f"\n[MAPPING TABLE]")
    print(f"  Total cuentas en mapping: {total_mapping}")

    # Distribución por tipo
    activos = conn.execute("SELECT COUNT(*) FROM mapping WHERE odoo_code LIKE '1.%'").fetchone()[0]
    pasivos = conn.execute("SELECT COUNT(*) FROM mapping WHERE odoo_code LIKE '2.%'").fetchone()[0]
    patrimonio = conn.execute("SELECT COUNT(*) FROM mapping WHERE odoo_code LIKE '3.%'").fetchone()[0]
    ingresos = conn.execute("SELECT COUNT(*) FROM mapping WHERE odoo_code LIKE '4.%'").fetchone()[0]
    costos = conn.execute("SELECT COUNT(*) FROM mapping WHERE odoo_code LIKE '5.%'").fetchone()[0]
    gastos = conn.execute("SELECT COUNT(*) FROM mapping WHERE odoo_code LIKE '6.%'").fetchone()[0]

    print(f"  - Activos (1.x):     {activos}")
    print(f"  - Pasivos (2.x):     {pasivos}")
    print(f"  - Patrimonio (3.x):  {patrimonio}")
    print(f"  - Ingresos (4.x):    {ingresos}")
    print(f"  - Costos (5.x):      {costos}")
    print(f"  - Gastos (6.x):      {gastos}")

    # 2. Partidas únicas en financials
    fin_partidas = set(r[0] for r in conn.execute('SELECT DISTINCT partida FROM financials').fetchall())
    print(f"\n[FINANCIALS TABLE]")
    print(f"  Partidas únicas: {len(fin_partidas)}")

    # 3. Partidas únicas en esf_data
    esf_partidas = set(r[0] for r in conn.execute('SELECT DISTINCT partida FROM esf_data').fetchall())
    print(f"\n[ESF_DATA TABLE]")
    print(f"  Partidas únicas: {len(esf_partidas)}")

    # 4. Partidas en mapping
    mapped_partidas = set(r[0] for r in conn.execute('SELECT DISTINCT partida FROM mapping').fetchall())
    print(f"\n[CROSS-CHECK]")
    print(f"  Partidas únicas en mapping: {len(mapped_partidas)}")

    # 5. Partidas en financials/esf que NO están en mapping (potencialmente sin match)
    unmapped_fin = fin_partidas - mapped_partidas
    unmapped_esf = esf_partidas - mapped_partidas

    if unmapped_fin:
        print(f"\n[ALERT] Partidas en FINANCIALS sin entrada en MAPPING: {len(unmapped_fin)}")
        for p in sorted(unmapped_fin)[:10]:
            print(f"    - {p}")
        if len(unmapped_fin) > 10:
            print(f"    ... y {len(unmapped_fin) - 10} más")
    else:
        print(f"\n[OK] Todas las partidas de FINANCIALS están en MAPPING")

    if unmapped_esf:
        print(f"\n[ALERT] Partidas en ESF_DATA sin entrada en MAPPING: {len(unmapped_esf)}")
        for p in sorted(unmapped_esf)[:10]:
            print(f"    - {p}")
        if len(unmapped_esf) > 10:
            print(f"    ... y {len(unmapped_esf) - 10} más")
    else:
        print(f"\n[OK] Todas las partidas de ESF_DATA están en MAPPING")

    # 6. Códigos de cuenta en mapping que NO tienen datos en financials/esf
    # (están mapeadas pero nunca se han usado)
    used_codes_fin = set()
    used_codes_esf = set()

    # Obtener códigos usados mediante JOIN inverso
    rows_fin = conn.execute('''
        SELECT DISTINCT m.odoo_code
        FROM mapping m
        JOIN financials f ON m.partida = f.partida
    ''').fetchall()
    used_codes_fin = set(r[0] for r in rows_fin)

    rows_esf = conn.execute('''
        SELECT DISTINCT m.odoo_code
        FROM mapping m
        JOIN esf_data e ON m.partida = e.partida
    ''').fetchall()
    used_codes_esf = set(r[0] for r in rows_esf)

    all_mapped_codes = set(r[0] for r in conn.execute('SELECT odoo_code FROM mapping').fetchall())
    unused_codes = all_mapped_codes - used_codes_fin - used_codes_esf

    print(f"\n[USAGE STATS]")
    print(f"  Códigos en mapping: {len(all_mapped_codes)}")
    print(f"  Códigos usados en financials: {len(used_codes_fin)}")
    print(f"  Códigos usados en esf_data: {len(used_codes_esf)}")
    print(f"  Códigos SIN USAR (nunca cargados): {len(unused_codes)}")

    # 7. Grupos
    total_groups = conn.execute('SELECT COUNT(DISTINCT group_name) FROM mapping_groups').fetchone()[0]
    total_assignments = conn.execute('SELECT COUNT(*) FROM mapping_groups').fetchone()[0]

    print(f"\n[GRUPOS]")
    print(f"  Grupos definidos: {total_groups}")
    print(f"  Asignaciones totales: {total_assignments}")

    if total_groups > 0:
        group_rows = conn.execute('''
            SELECT group_name, COUNT(*) as cnt
            FROM mapping_groups
            GROUP BY group_name
            ORDER BY cnt DESC
        ''').fetchall()

        for row in group_rows:
            print(f"    - {row[0]}: {row[1]} cuentas")

    # 8. Income types
    print(f"\n[INCOME TYPES]")
    income_types = conn.execute('''
        SELECT income_type, COUNT(*) as cnt
        FROM mapping
        GROUP BY income_type
        ORDER BY cnt DESC
    ''').fetchall()

    for row in income_types:
        itype = row[0] if row[0] else 'NULL'
        print(f"    - {itype}: {row[1]} cuentas")

    print("\n" + "="*80)

    conn.close()


if __name__ == '__main__':
    main()
