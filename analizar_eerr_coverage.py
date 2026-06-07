#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Analiza cobertura de EERR_STRUCTURE vs datos reales"""

import sqlite3
from engine import EERR_STRUCTURE

conn = sqlite3.connect('data/ultrax.db')
conn.row_factory = sqlite3.Row

# Obtener todas las partidas en financials con sus totales
fin_data = conn.execute('''
    SELECT partida, SUM(amount) as total
    FROM financials
    GROUP BY partida
    ORDER BY partida
''').fetchall()

fin_partidas = {r['partida']: r['total'] for r in fin_data}

# Obtener todas las partidas NO-header en EERR_STRUCTURE
eerr_partidas = set(item[0] for item in EERR_STRUCTURE if not item[1])

# Obtener grupos
groups_rows = conn.execute('''
    SELECT mg.group_name, m.partida
    FROM mapping_groups mg
    JOIN mapping m ON mg.odoo_code = m.odoo_code
    WHERE mg.report_type = 'eerr'
''').fetchall()

groups = {}
for r in groups_rows:
    if r['group_name'] not in groups:
        groups[r['group_name']] = []
    groups[r['group_name']].append(r['partida'])

print('='*80)
print('ANÁLISIS DE COBERTURA: EERR_STRUCTURE vs FINANCIALS')
print('='*80)

print(f'\nPartidas en financials: {len(fin_partidas)}')
print(f'Partidas en EERR_STRUCTURE (no-headers): {len(eerr_partidas)}')
print(f'Grupos definidos: {len(groups)}')

# Clasificar partidas
sin_cobertura = []
en_grupo = []
en_eerr = []

for partida, total in fin_partidas.items():
    # Verificar si está en un grupo
    en_algun_grupo = False
    grupo_nombre = None
    for gname, gpartidas in groups.items():
        if partida in gpartidas:
            en_algun_grupo = True
            grupo_nombre = gname
            break

    if en_algun_grupo:
        # Verificar si el grupo está en EERR_STRUCTURE
        if grupo_nombre in eerr_partidas:
            en_grupo.append((partida, total, grupo_nombre))
        else:
            sin_cobertura.append((partida, total, f'Grupo "{grupo_nombre}" no está en EERR_STRUCTURE'))
    elif partida in eerr_partidas:
        en_eerr.append((partida, total))
    else:
        sin_cobertura.append((partida, total, 'No está en EERR_STRUCTURE ni en grupos'))

print('\n' + '-'*80)
print(f'[OK] Con cobertura directa en EERR_STRUCTURE: {len(en_eerr)}')
print(f'[OK] Con cobertura vía grupos: {len(en_grupo)}')
print(f'[X] SIN COBERTURA: {len(sin_cobertura)}')

if sin_cobertura:
    print('\n' + '='*80)
    print('PARTIDAS SIN COBERTURA (no aparecen en EERR):')
    print('='*80)
    total_sin_cobertura = 0
    for partida, total, razon in sorted(sin_cobertura, key=lambda x: abs(x[1]), reverse=True):
        total_sin_cobertura += total
        print(f'\n{partida}')
        print(f'  Total: ${total:,.2f}')
        print(f'  Razón: {razon}')

    print('\n' + '-'*80)
    print(f'IMPACTO FINANCIERO: ${total_sin_cobertura:,.2f} NO aparece en EERR')
    print('-'*80)

if en_grupo:
    print('\n' + '='*80)
    print('PARTIDAS CON COBERTURA VÍA GRUPOS:')
    print('='*80)
    for partida, total, grupo in sorted(en_grupo, key=lambda x: x[2]):
        print(f'  [{grupo}] {partida} → ${total:,.2f}')

conn.close()
