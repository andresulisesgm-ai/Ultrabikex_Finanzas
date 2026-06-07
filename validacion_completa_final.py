#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Validación completa EERR: Excel vs Sistema - Rodeo ENE 2026"""

import json
import openpyxl
import re

print('='*100)
print(' '*30 + 'VALIDACIÓN COMPLETA EERR')
print(' '*30 + 'Excel vs Sistema - Rodeo ENE 2026')
print('='*100)

# 1. Cargar Sistema
with open('eerr_rodeo_final.json', 'r', encoding='latin-1') as f:
    sistema_data = json.load(f)

sistema_dict = {}
for row in sistema_data.get('rows', []):
    partida = row.get('partida', '')
    is_header = row.get('is_header', False)
    meses = row.get('meses', [])
    if meses:
        valor = meses[0].get('ejecutado', {}).get('valor', 0)
        if valor != 0 and not is_header:
            sistema_dict[partida] = valor

# 2. Cargar Excel
wb = openpyxl.load_workbook(r'C:\Users\andre\Desktop\EERR RODEO ENERO.xlsx', data_only=True)
sheet = wb.active

def limpiar_nombre(texto):
    if not texto:
        return ''
    texto = re.sub(r'^\d+(\.\d+)*\s+', '', texto.strip())
    return texto.strip()

excel_dict = {}
for row in sheet.iter_rows(min_row=8, values_only=True):
    if row[0] and isinstance(row[0], str):
        nombre_limpio = limpiar_nombre(row[0])
        if len(row) > 2 and isinstance(row[2], (int, float)):
            valor = abs(float(row[2]))
            if valor != 0:
                excel_dict[nombre_limpio] = valor

# 3. Comparar
print('\n' + '='*100)
print(f'{"#":<4} {"Partida":<60} {"Excel":>15} {"Sistema":>15} {"Diff":>12} {"Status":<8}')
print('='*100)

todas = sorted(set(list(excel_dict.keys()) + list(sistema_dict.keys())))

comparaciones = []
for partida in todas:
    excel_val = excel_dict.get(partida, 0)
    sistema_val = sistema_dict.get(partida, 0)
    diff = sistema_val - excel_val
    match = abs(diff) < 0.01

    # Filtrar partidas agregadas del Excel
    if partida not in ['Ganancia y Perdida', 'Ingreso', 'Gasto']:
        comparaciones.append({
            'partida': partida,
            'excel': excel_val,
            'sistema': sistema_val,
            'diff': diff,
            'match': match
        })

# Ordenar por diferencia absoluta
comparaciones.sort(key=lambda x: abs(x['diff']), reverse=True)

for i, c in enumerate(comparaciones, 1):
    status = ' [OK]  ' if c['match'] else ' [ERROR]'
    print(f'{i:<4} {c["partida"]:<60} ${c["excel"]:>13,.2f} ${c["sistema"]:>13,.2f} ${c["diff"]:>10,.2f} {status}')

# 4. Resumen
print('\n' + '='*100)
print(' '*40 + 'RESUMEN')
print('='*100)

total = len(comparaciones)
ok = sum(1 for c in comparaciones if c['match'])
error = total - ok

print(f'\nTotal partidas: {total}')
print(f'  [OK] Coinciden: {ok} ({ok/total*100:.1f}%)')
print(f'  [X]  Difieren: {error} ({error/total*100:.1f}%)')

# Totales
suma_excel = sum(c['excel'] for c in comparaciones)
suma_sistema = sum(c['sistema'] for c in comparaciones)
print(f'\nSuma total Excel: ${suma_excel:,.2f}')
print(f'Suma total Sistema: ${suma_sistema:,.2f}')
print(f'Diferencia: ${suma_sistema - suma_excel:,.2f}')

# Desglose por tipo
ingresos_excel = sum(c['excel'] for c in comparaciones if 'ingreso' in c['partida'].lower() or 'ganancia' in c['partida'].lower() or 'sobrante' in c['partida'].lower())
ingresos_sistema = sum(c['sistema'] for c in comparaciones if 'ingreso' in c['partida'].lower() or 'ganancia' in c['partida'].lower() or 'sobrante' in c['partida'].lower())

gastos_excel = sum(c['excel'] for c in comparaciones if 'gasto' in c['partida'].lower() or 'faltante' in c['partida'].lower() or 'pérdida' in c['partida'].lower() or 'perdida' in c['partida'].lower())
gastos_sistema = sum(c['sistema'] for c in comparaciones if 'gasto' in c['partida'].lower() or 'faltante' in c['partida'].lower() or 'pérdida' in c['partida'].lower() or 'perdida' in c['partida'].lower())

costos_excel = sum(c['excel'] for c in comparaciones if 'costo' in c['partida'].lower())
costos_sistema = sum(c['sistema'] for c in comparaciones if 'costo' in c['partida'].lower())

print('\n[DESGLOSE POR TIPO]')
print(f'  Ingresos  - Excel: ${ingresos_excel:>12,.2f}  Sistema: ${ingresos_sistema:>12,.2f}  Diff: ${ingresos_sistema-ingresos_excel:>10,.2f}')
print(f'  Costos    - Excel: ${costos_excel:>12,.2f}  Sistema: ${costos_sistema:>12,.2f}  Diff: ${costos_sistema-costos_excel:>10,.2f}')
print(f'  Gastos    - Excel: ${gastos_excel:>12,.2f}  Sistema: ${gastos_sistema:>12,.2f}  Diff: ${gastos_sistema-gastos_excel:>10,.2f}')

print('\n' + '='*100)
if error == 0:
    print(' '*35 + '[SUCCESS] TODOS LOS VALORES COINCIDEN!')
else:
    print(f' '*30 + f'[ALERT] {error} PARTIDAS CON DIFERENCIAS')
print('='*100)
