#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Analiza las partidas en financials y su mapping"""

import sqlite3

conn = sqlite3.connect('data/ultrax.db')
conn.row_factory = sqlite3.Row

# Obtener todas las partidas en financials
fin_partidas = [r[0] for r in conn.execute('SELECT DISTINCT partida FROM financials ORDER BY partida').fetchall()]

print('='*100)
print('ANÁLISIS DE PARTIDAS EN FINANCIALS vs MAPPING')
print('='*100)

sin_mapping = []
con_una_cuenta = []
con_multiples = []

for partida in fin_partidas:
    # Buscar TODAS las cuentas que mapean a esta partida
    cuentas = conn.execute('SELECT odoo_code, odoo_name FROM mapping WHERE partida = ? ORDER BY odoo_code', (partida,)).fetchall()

    if len(cuentas) == 0:
        sin_mapping.append(partida)
        print(f'\n[ERROR] PARTIDA SIN MAPPING: {partida}')
    elif len(cuentas) == 1:
        con_una_cuenta.append((partida, cuentas[0]))
        print(f'\n{partida}')
        print(f'  -> {cuentas[0][0]} | {cuentas[0][1]}')
    else:
        con_multiples.append((partida, cuentas))
        print(f'\n{partida} ({len(cuentas)} cuentas mapeadas)')
        for c in cuentas:
            print(f'  -> {c[0]} | {c[1]}')

print('\n' + '='*100)
print('RESUMEN')
print('='*100)
print(f'Total partidas en financials: {len(fin_partidas)}')
print(f'Partidas SIN MAPPING: {len(sin_mapping)}')
print(f'Partidas con 1 cuenta: {len(con_una_cuenta)}')
print(f'Partidas con múltiples cuentas: {len(con_multiples)}')

if sin_mapping:
    print('\n[ALERT] Las siguientes partidas NO tienen entrada en mapping:')
    for p in sin_mapping:
        print(f'  - {p}')

conn.close()
