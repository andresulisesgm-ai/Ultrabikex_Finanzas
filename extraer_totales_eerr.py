#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Extraer totales y subtotales del JSON del EERR"""

import json

with open('eerr_rodeo_raw.json', 'r', encoding='latin-1') as f:
    data = json.load(f)

print('='*80)
print('ESTRUCTURA DE TOTALES/SUBTOTALES EN EERR - RODEO ENE 2026')
print('='*80)

rows = data.get('rows', [])
print(f'\nTotal de filas en EERR: {len(rows)}')

# Partidas clave a buscar
partidas_clave = [
    'Total Ingresos',
    'Utilidad Bruta',
    'Total Gastos Operacionales',
    'Subtotal Gastos de Administración',
    'Subtotal Gastos de Recursos Humanos',
    'Subtotal Gastos de Comercialización y Logistica',
    'Subtotal Gastos de Mercadeo',
    'Subtotal Gastos de Tecnología, Innovación e Investigación',
    'Utilidad antes de Comisiones por Ventas',
    'Utilidad después de Comisiones por Ventas',
    'Utilidad Neta'
]

print('\n[PARTIDAS CLAVE ENCONTRADAS]')
print('='*80)

for row in rows:
    partida = row.get('partida', '')
    if partida in partidas_clave:
        is_header = row.get('is_header', False)
        bold = row.get('bold', False)
        meses = row.get('meses', [])

        # Obtener valor de ENE
        ene_valor = 0
        if meses and len(meses) > 0:
            ene_data = meses[0]  # ENE
            if 'ejecutado' in ene_data:
                ene_valor = ene_data['ejecutado'].get('valor', 0)

        tipo = '[HEADER/TOTAL]' if (is_header or bold) else '[PARTIDA]    '

        print(f'\n{tipo} {partida}')
        print(f'  is_header: {is_header}')
        print(f'  bold: {bold}')
        print(f'  ENE valor: ${ene_valor:,.2f}')

print('\n' + '='*80)
print('[COMO SE CALCULAN LOS SUBTOTALES]')
print('='*80)
print('''
Los subtotales/totales en el EERR se calculan DINÁMICAMENTE en el backend:

1. El código recorre EERR_STRUCTURE secuencialmente
2. Cuando encuentra un header (is_header=True o is_total=True):
   - Marca el inicio de una sección
   - Suma todas las partidas NO-header que vienen después
   - Hasta encontrar el siguiente header
3. El valor calculado se asigna al header

Ejemplo: "Subtotal Gastos de Recursos Humanos"
- Es un header (is_header=True)
- Suma todas las partidas entre él y "Subtotal Gastos de Comercialización"
- Incluye solo partidas con is_header=False
- El total es la suma de esas partidas

Por lo tanto: LOS SUBTOTALES SE CALCULAN SUMANDO SUS HIJOS AUTOMÁTICAMENTE.
''')
