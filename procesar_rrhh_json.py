#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Procesar JSON del EERR y extraer sección RRHH"""

import json

with open('temp_eerr.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

rows = data.get('rows', [])

print('='*80)
print(f'EERR FRONTEND - 2026 - Rodeo')
print('='*80)
print(f'\n[INFO] Total de lineas en EERR: {len(rows)}')

# Encontrar sección RRHH
rrhh_start = -1
rrhh_end = -1

for i, row in enumerate(rows):
    partida = row.get('partida', '')
    if partida == 'Subtotal Gastos de Recursos Humanos':
        rrhh_start = i
    elif rrhh_start >= 0 and partida == 'Subtotal Gastos de Comercialización y Logistica':
        rrhh_end = i
        break

if rrhh_start < 0:
    print('[ERROR] No se encontró la sección de RRHH')
    exit(1)

rrhh_rows = rows[rrhh_start:rrhh_end] if rrhh_end > 0 else rows[rrhh_start:]

print(f'[INFO] Sección RRHH: filas {rrhh_start} a {rrhh_end-1} ({len(rrhh_rows)} filas)')

print('\n' + '='*80)
print('SECCION DE RECURSOS HUMANOS - ENERO 2026')
print('='*80)

total_rrhh = 0
partidas_con_datos = []
partidas_sin_datos = []

for i, row in enumerate(rrhh_rows):
    partida = row.get('partida', '')
    is_header = row.get('is_header', False)
    bold = row.get('bold', False)

    # Obtener valor de enero (primera posición en meses)
    meses = row.get('meses', [])
    value = 0
    if meses and len(meses) > 0:
        ene_data = meses[0]  # ENE
        if 'ejecutado' in ene_data:
            value = ene_data['ejecutado'].get('valor', 0)

    if is_header or bold:
        tipo = '[HEADER/TOTAL]'
    else:
        tipo = '[PARTIDA]    '

    if value == 0:
        valor_str = '$0.00'
        if not (is_header or bold):
            partidas_sin_datos.append(partida)
    else:
        valor_str = f'${value:,.2f}'
        if not (is_header or bold):
            partidas_con_datos.append((partida, value))
            if value > 0:
                total_rrhh += value

    print(f'{i:2d}. {tipo} {partida:65s} {valor_str:>15s}')

print('\n' + '='*80)
print('RESUMEN')
print('='*80)
print(f'Total lineas en seccion RRHH: {len(rrhh_rows)}')
print(f'Partidas con datos: {len(partidas_con_datos)}')
print(f'Partidas sin datos ($0.00): {len(partidas_sin_datos)}')
print(f'\nTotal RRHH calculado: ${total_rrhh:,.2f}')

if partidas_sin_datos:
    print(f'\n[ALERT] {len(partidas_sin_datos)} PARTIDAS CON $0.00 (candidatas para limpieza):')
    for p in partidas_sin_datos:
        print(f'  - {p}')

# Verificar duplicados
partida_names = [p[0] for p in partidas_con_datos]
duplicados = [name for name in partida_names if partida_names.count(name) > 1]
if duplicados:
    print('\n[ALERT] PARTIDAS DUPLICADAS CON DATOS:')
    for dup in set(duplicados):
        valores = [v for n, v in partidas_con_datos if n == dup]
        print(f'  - {dup}')
        for val in valores:
            print(f'      ${val:,.2f}')
else:
    print('\n[OK] No hay partidas duplicadas con datos')

print('\n' + '='*80)
print('[PARTIDAS CON DATOS EN ENERO 2026]:')
print('='*80)
for name, value in partidas_con_datos:
    print(f'  {name:65s} ${value:,.2f}')

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
