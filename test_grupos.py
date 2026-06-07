#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test del sistema de grupos en EERR"""

import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

DB_PATH = 'data/ultrax.db'

def test_grupos():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Simular get_grouped_partidas
    rows = conn.execute('''
        SELECT mg.group_name, m.partida, mg.odoo_code
        FROM mapping_groups mg
        JOIN mapping m ON mg.odoo_code = m.odoo_code
        WHERE mg.report_type = 'eerr'
        ORDER BY mg.display_order, mg.group_name
    ''').fetchall()

    groups = {}
    grouped_partidas = set()

    for r in rows:
        group_name = r['group_name']
        partida = r['partida']

        if group_name not in groups:
            groups[group_name] = []
        groups[group_name].append(partida)
        grouped_partidas.add(partida)

    print('='*80)
    print('TEST: SISTEMA DE GRUPOS EN EERR')
    print('='*80)

    print(f'\nTotal de grupos definidos: {len(groups)}')
    print(f'Total de partidas agrupadas: {len(grouped_partidas)}')

    print('\n' + '-'*80)
    print('DETALLE DE GRUPOS:')
    print('-'*80)

    for gname, partidas in sorted(groups.items()):
        print(f'\n[{gname}] - {len(partidas)} partidas')
        for p in partidas:
            print(f'  • {p}')

    # Verificar si alguna de las partidas agrupadas tiene datos en financials
    print('\n' + '-'*80)
    print('VERIFICACIÓN CON DATOS REALES:')
    print('-'*80)

    for gname, partidas in sorted(groups.items()):
        # Buscar si alguna de estas partidas tiene datos
        placeholders = ','.join(['?'] * len(partidas))
        rows_data = conn.execute(
            f'SELECT partida, SUM(amount) as total FROM financials WHERE partida IN ({placeholders}) GROUP BY partida',
            partidas
        ).fetchall()

        if rows_data:
            total_grupo = sum(r['total'] for r in rows_data)
            print(f'\n[{gname}]')
            print(f'  Total en financials: {total_grupo:,.2f}')
            for r in rows_data:
                print(f'    - {r["partida"]}: {r["total"]:,.2f}')
        else:
            print(f'\n[{gname}] - Sin datos en financials')

    conn.close()

    print('\n' + '='*80)
    print('[OK] TEST COMPLETADO')
    print('='*80)

if __name__ == '__main__':
    test_grupos()
