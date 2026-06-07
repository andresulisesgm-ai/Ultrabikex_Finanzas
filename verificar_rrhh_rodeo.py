#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verificar gastos de RRHH para Rodeo ENE 2026"""

import sqlite3
from engine import EERR_STRUCTURE

# Identificar partidas de RRHH en EERR_STRUCTURE
# La sección de RRHH está entre "Subtotal Gastos de Recursos Humanos" y "Subtotal Gastos de Comercialización"
rrhh_partidas = []
in_rrhh_section = False

for i, item in enumerate(EERR_STRUCTURE):
    name, is_header, _, _, _ = item

    if name == 'Subtotal Gastos de Recursos Humanos':
        in_rrhh_section = True
        continue

    if name == 'Subtotal Gastos de Comercialización y Logistica':
        break

    if in_rrhh_section and not is_header:
        rrhh_partidas.append(name)

print('='*80)
print('VERIFICACION: GASTOS DE RRHH - RODEO ENE 2026')
print('='*80)

print(f'\n[1] PARTIDAS DE RRHH EN EERR_STRUCTURE: {len(rrhh_partidas)}')
print('-'*80)
for p in rrhh_partidas:
    print(f'  - {p}')

# Conectar a BD
conn = sqlite3.connect('data/ultrax.db')
conn.row_factory = sqlite3.Row

# Obtener datos de financials para Rodeo ENE 2026
fin_rows = conn.execute("""
    SELECT partida, amount
    FROM financials
    WHERE year='2026' AND month='ENE' AND unit='Rodeo'
""").fetchall()

fin_data = {r['partida']: r['amount'] for r in fin_rows}

# Obtener grupos de RRHH
groups_rows = conn.execute("""
    SELECT mg.group_name, m.partida
    FROM mapping_groups mg
    JOIN mapping m ON mg.odoo_code = m.odoo_code
    WHERE mg.report_type = 'eerr'
""").fetchall()

groups = {}
for r in groups_rows:
    if r['group_name'] not in groups:
        groups[r['group_name']] = []
    groups[r['group_name']].append(r['partida'])

print(f'\n[2] PARTIDAS DE RRHH QUE EXISTEN EN FINANCIALS RODEO ENE 2026:')
print('-'*80)

total_rrhh = 0
found_partidas = []

for partida in rrhh_partidas:
    # Verificar si la partida está en financials directamente
    if partida in fin_data:
        amount = fin_data[partida]
        total_rrhh += amount
        found_partidas.append(partida)
        print(f'  [OK] {partida}: ${amount:,.2f}')
    # Verificar si es un grupo
    elif partida in groups:
        group_total = 0
        print(f'  [GRUPO] {partida}:')
        for sub_partida in groups[partida]:
            if sub_partida in fin_data:
                amount = fin_data[sub_partida]
                group_total += amount
                total_rrhh += amount
                found_partidas.append(sub_partida)
                print(f'      + {sub_partida}: ${amount:,.2f}')
        print(f'      Subtotal grupo: ${group_total:,.2f}')

print(f'\n[SUBTOTAL CALCULADO]: ${total_rrhh:,.2f}')

# Identificar partidas de RRHH en financials que no están cubiertas
print(f'\n[3] PARTIDAS DE RRHH EN FINANCIALS NO CUBIERTAS:')
print('-'*80)

# Partidas que parecen ser de RRHH (empiezan con "Gastos de" y contienen palabras clave)
rrhh_keywords = [
    'sueldo', 'salario', 'complemento', 'bono', 'vacacion', 'utilidad',
    'prestacion', 'interes', 'aporte', 'ivss', 'spf', 'faov', 'inces',
    'guarderia', 'hcm', 'poliza', 'personal', 'externo', 'comision',
    'dotacion', 'fiesta', 'agasajo', 'donacion', 'obsequio', 'transporte'
]

uncovered = []
for partida, amount in fin_data.items():
    # Si ya está en found_partidas, skip
    if partida in found_partidas:
        continue

    # Verificar si parece ser de RRHH
    partida_lower = partida.lower()
    is_rrhh = any(keyword in partida_lower for keyword in rrhh_keywords)

    if is_rrhh:
        uncovered.append((partida, amount))

if uncovered:
    uncovered_total = 0
    for partida, amount in uncovered:
        print(f'  [!] {partida}: ${amount:,.2f}')
        uncovered_total += amount
    print(f'\n  Total no cubierto: ${uncovered_total:,.2f}')
    print(f'  Total incluyendo no cubierto: ${total_rrhh + uncovered_total:,.2f}')
else:
    print('  [OK] No hay partidas de RRHH sin cobertura')

print('\n' + '='*80)
print('COMPARACION CON EXCEL:')
print('='*80)
print(f'  Excel Rodeo ENE 2026: $2,123.88')
print(f'  Sistema (calculado):  ${total_rrhh:,.2f}')
diferencia = 2123.88 - total_rrhh
print(f'  Diferencia:           ${diferencia:,.2f}')

if abs(diferencia) < 0.01:
    print('\n  [SUCCESS] Los totales coinciden!')
elif abs(diferencia) < 1.00:
    print(f'\n  [OK] Diferencia menor a $1.00 (probablemente redondeo)')
else:
    print(f'\n  [ALERT] Diferencia de ${abs(diferencia):,.2f}')
    if uncovered:
        print(f'  Posible causa: ${uncovered_total:,.2f} en partidas no cubiertas')

conn.close()
