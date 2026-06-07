#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verificar cuántas líneas tiene la sección RRHH en EERR_STRUCTURE"""

from engine import EERR_STRUCTURE

# Contar total de partidas
total_partidas = len([x for x in EERR_STRUCTURE if not x[1]])
print(f'Total partidas (no-headers) en EERR_STRUCTURE: {total_partidas}')

# Contar partidas en sección RRHH
rrhh_section = False
rrhh_count = 0
rrhh_partidas = []

for item in EERR_STRUCTURE:
    name = item[0]
    is_header = item[1]

    if name == 'Subtotal Gastos de Recursos Humanos':
        rrhh_section = True
        continue

    if name == 'Subtotal Gastos de Comercialización y Logistica':
        break

    if rrhh_section and not is_header:
        rrhh_count += 1
        rrhh_partidas.append(name)

print(f'\nPartidas en seccion RRHH: {rrhh_count}')
print('\nLista de partidas RRHH:')
for i, p in enumerate(rrhh_partidas, 1):
    print(f'{i:2d}. {p}')
