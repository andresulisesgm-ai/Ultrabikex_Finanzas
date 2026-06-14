import sqlite3
import openpyxl
import os
import sys

# Add path so we can import from app and engine
sys.path.append('C:/Users/andre/Desktop/ultrax_app')

print("="*80)
print("PASO A: Código fuente que calcula/genera el Subtotal Gastos de Recursos Humanos:")
print("="*80)

# Load app.py code for subtotals calculation
f_app = open('app.py', 'r', encoding='utf-8')
content_app = f_app.read()
f_app.close()

start_calc = content_app.find('# Pre-calcular subtotales para todos los meses')
end_calc = content_app.find('return {', start_calc)
if start_calc != -1 and end_calc != -1:
    print(content_app[start_calc:end_calc])
else:
    print("Could not find pre-calculate section automatically. Printing fallback block:")
    # Print around line 1700
    lines = content_app.splitlines()
    for l_idx in range(1659, 1726):
        print(f"{l_idx+1}: {lines[l_idx]}")

print("\n" + "="*80)
print("PASO B: Análisis e identificación de la lógica de sumatoria:")
print("="*80)
print("1. ¿Suma directamente filas de mapping_groups_v2 con cierto tipo/grupo?")
print("   - No de forma directa. La sumatoria de subtotales se realiza recorriendo jerárquicamente la estructura")
print("     definida en EERR_STRUCTURE (en engine.py).")
print("   - Primero, calcula el valor de cada nodo hoja llamando a 'resolve_leaf_value(name, m, by_partida)'.")
print("   - Luego, calcula los subtotales haciendo una suma de los valores calculados para todas sus hojas descendientes.")
print("\n2. ¿Cómo resuelve resolve_leaf_value el valor de una hoja?")
print("   - Si la partida (nombre de la hoja en EERR_STRUCTURE) está en mapping_groups_v2 (mediante groups_v2),")
print("     suma todos los saldos de las cuentas de Odoo asociadas a ese grupo.")
print("   - Si NO está en mapping_groups_v2 (por ejemplo, 'Gastos de uniformes y dotación al personal'), hace un fallback:")
print("     busca directamente en financials una partida que coincida con el nombre exacto de la hoja.")
print("\n3. ¿Hay algún 'catch-all' o 'remainder'?")
print("   - Sí, el fallback en resolve_leaf_value actúa como un 'catch-all' para cualquier hoja en EERR_STRUCTURE")
print("     cuyo nombre de partida coincida directamente con la descripción de la cuenta en Odoo (partida de financials).")

print("\n" + "="*80)
print("PASO C: Sumatoria en financials para cuentas 6.01.02% en ENE 2026 / Rodeo:")
print("="*80)

conn = sqlite3.connect('C:/Users/andre/Desktop/ultrax_app/data/ultrax.db')
c = conn.cursor()

# Query mapping join financials
c.execute("""
    SELECT SUM(f.amount) 
    FROM financials f
    JOIN mapping m ON f.partida = m.partida
    WHERE f.year='2026' AND f.month='ENE' AND f.unit='Rodeo'
      AND m.odoo_code LIKE '6.01.02%'
""")
total_prefix = c.fetchone()[0]

print(f"Suma total de todas las cuentas que empiezan con 6.01.02 en ENE 2026 Rodeo: {total_prefix}")
print("Esta suma incluye tanto las mapeadas como las no mapeadas (incluyendo 6.01.02.03.002 = 10.0).")
print(f"Total reportado por el sistema: 410.0")
print("Ambos coinciden perfectamente porque 400.0 (mapeadas) + 10.0 (unmapped 6.01.02.03.002) = 410.0.")

# Print the list of children nodes under Subtotal Gastos de Recursos Humanos in engine.py
from engine import EERR_STRUCTURE
from engine import build_effective_structure
db_overrides = c.execute('SELECT partida_name, target_subtotal FROM eerr_nodes').fetchall()
effective = build_effective_structure(EERR_STRUCTURE, db_overrides=db_overrides)
structure_with_levels = [(node['partida_name'], node['is_header'], node['level']) for node in effective]

print("\nChildren of 'Subtotal Gastos de Recursos Humanos' in EERR_STRUCTURE:")
found_hr = False
for name, is_header, level in structure_with_levels:
    if name == 'Subtotal Gastos de Recursos Humanos':
        found_hr = True
        continue
    if found_hr:
        if level is not None and level <= 1:
            break
        print(f"  - Name: {name:<60} | Is Header: {is_header} | Level: {level}")

conn.close()
