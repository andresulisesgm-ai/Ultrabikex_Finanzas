#!/usr/bin/env python
# -*- coding: utf-8 -*-
from db import INITIAL_GROUPS, seed_initial_groups
import sqlite3

print(f'INITIAL_GROUPS tiene {len(INITIAL_GROUPS)} entradas')
print('\nPrimeras 10 entradas:')
for i, g in enumerate(INITIAL_GROUPS[:10]):
    print(f'  {i+1}. {g}')

print('\n' + '='*80)
print('Ejecutando seed_initial_groups()...')
print('='*80)

try:
    seed_initial_groups()
    print('[OK] Función ejecutada')
except Exception as e:
    print(f'[ERROR] {e}')
    import traceback
    traceback.print_exc()

# Verificar resultado
conn = sqlite3.connect('data/ultrax.db')
count = conn.execute('SELECT COUNT(*) FROM mapping_groups').fetchone()[0]
print(f'\nRegistros en mapping_groups después de ejecutar: {count}')

if count > 0:
    rows = conn.execute('SELECT group_name, COUNT(*) as cnt FROM mapping_groups GROUP BY group_name').fetchall()
    print('\nGrupos insertados:')
    for row in rows:
        print(f'  - {row[0]}: {row[1]} cuentas')

conn.close()
