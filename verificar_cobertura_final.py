#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verificación final de cobertura EERR_STRUCTURE"""

import sqlite3
from engine import EERR_STRUCTURE

conn = sqlite3.connect('data/ultrax.db')
conn.row_factory = sqlite3.Row

# Obtener partidas en financials con totales
fin_data = conn.execute('''
    SELECT partida, SUM(amount) as total
    FROM financials
    GROUP BY partida
    ORDER BY ABS(SUM(amount)) DESC
''').fetchall()

fin_partidas = {r['partida']: r['total'] for r in fin_data}

# Partidas en EERR_STRUCTURE (no headers)
eerr_partidas = set(item[0] for item in EERR_STRUCTURE if not item[1])

# Grupos
groups_rows = conn.execute('''
    SELECT mg.group_name, m.partida
    FROM mapping_groups mg
    JOIN mapping m ON mg.odoo_code = m.odoo_code
    WHERE mg.report_type = 'eerr'
''').fetchall()

groups = {}
grouped_partidas = set()
for r in groups_rows:
    if r['group_name'] not in groups:
        groups[r['group_name']] = []
    groups[r['group_name']].append(r['partida'])
    grouped_partidas.add(r['partida'])

print('='*80)
print('VERIFICACION FINAL: COBERTURA DE EERR_STRUCTURE')
print('='*80)

print(f'\n[ESTADISTICAS]')
print(f'  Partidas en financials: {len(fin_partidas)}')
print(f'  Partidas en EERR_STRUCTURE (no-headers): {len(eerr_partidas)}')
print(f'  Grupos definidos: {len(groups)}')
print(f'  Partidas agrupadas: {len(grouped_partidas)}')

# Clasificar
con_cobertura_directa = []
con_cobertura_grupo = []
sin_cobertura = []

for partida, total in fin_partidas.items():
    # Verificar si está en grupo
    en_grupo = False
    grupo_nombre = None
    for gname, gpartidas in groups.items():
        if partida in gpartidas:
            en_grupo = True
            grupo_nombre = gname
            break

    if en_grupo:
        if grupo_nombre in eerr_partidas:
            con_cobertura_grupo.append((partida, total, grupo_nombre))
        else:
            sin_cobertura.append((partida, total))
    elif partida in eerr_partidas:
        con_cobertura_directa.append((partida, total))
    else:
        sin_cobertura.append((partida, total))

print(f'\n[COBERTURA]')
print(f'  [OK] Con cobertura directa: {len(con_cobertura_directa)}')
print(f'  [OK] Con cobertura via grupos: {len(con_cobertura_grupo)}')
print(f'  [X]  SIN COBERTURA: {len(sin_cobertura)}')

total_cubierto_directo = sum(abs(t) for _, t in con_cobertura_directa)
total_cubierto_grupo = sum(abs(t) for _, t, _ in con_cobertura_grupo)
total_sin_cobertura = sum(abs(t) for _, t in sin_cobertura)
total_general = sum(abs(t) for _, t in fin_partidas.items())

print(f'\n[IMPACTO FINANCIERO]')
print(f'  Cubierto directo: ${total_cubierto_directo:,.2f}')
print(f'  Cubierto via grupos: ${total_cubierto_grupo:,.2f}')
print(f'  Sin cobertura: ${total_sin_cobertura:,.2f}')
print(f'  Total general: ${total_general:,.2f}')
print(f'  % Cobertura: {((total_cubierto_directo + total_cubierto_grupo) / total_general * 100):.1f}%')

if sin_cobertura:
    print('\n[ALERT] PARTIDAS AUN SIN COBERTURA:')
    for partida, total in sin_cobertura:
        print(f'  - {partida}: ${total:,.2f}')
else:
    print('\n[SUCCESS] 100% DE COBERTURA - Todas las partidas de financials estan en EERR')

print('\n[PARTIDAS CON COBERTURA VIA GRUPOS]')
for partida, total, grupo in sorted(con_cobertura_grupo, key=lambda x: x[2]):
    print(f'  [{grupo}] {partida} - ${total:,.2f}')

print('\n' + '='*80)
print('[OK] VERIFICACION COMPLETADA')
print('='*80)

conn.close()
