import os
import sys
import sqlite3

# Add current directory to path so we can import from app
sys.path.append('C:/Users/andre/Desktop/ultrax_app')

from app import app, eerr_completo_v2_ui_adapter, get_db

print("="*80)
print("PASO A - Identificar cómo se genera el EERR:")
print("="*80)
print("El EERR se genera en el endpoint /api/eerr/completo (que llama a /api/eerr_completo).")
print("Lógica principal: función 'eerr_completo_v2_ui_adapter(year, unit)' en app.py.")
print("Parámetros: recibe 'year' (año en formato string, ej. '2026') y 'unit' (sucursal/unidad, ej. 'Rodeo').")

print("\n" + "="*80)
print("PASO B y C - Ejecutar cálculo y extraer líneas de Recursos Humanos:")
print("="*80)

with app.app_context():
    db = get_db()
    year = '2026'
    unit = 'Rodeo'
    
    # Run adapter
    adapter_output = eerr_completo_v2_ui_adapter(year, unit)
    rows = adapter_output.get('rows', [])
    
    print(f"Calculando EERR para {unit} {year}...")
    
    # Find Recursos Humanos rows and their ENE 2026 values
    for r in rows:
        partida = r.get('partida', '')
        if 'recursos humanos' in partida.lower() or 'rrhh' in partida.lower():
            # ENE 2026 is month index 0
            ene_val = r['meses'][0]['ejecutado']['valor']
            print(f"  - Line: '{partida}' -> ENE 2026 Value = {ene_val}")

print("\n" + "="*80)
print("PASO D - Detalle de las cuentas RRHH (prefijo 6.01.02) mapeadas en mapping_groups_v2:")
print("="*80)

conn = sqlite3.connect('C:/Users/andre/Desktop/ultrax_app/data/ultrax.db')
c = conn.cursor()

# Get all accounts under 6.01.02 mapped in mapping_groups_v2
c.execute("""
    SELECT mgv.group_name, mgv.odoo_code, m.partida
    FROM mapping_groups_v2 mgv
    JOIN mapping m ON mgv.odoo_code = m.odoo_code
    WHERE mgv.odoo_code LIKE '6.01.02%' AND mgv.report_type='eerr'
    ORDER BY mgv.odoo_code
""")
mapped_accounts = c.fetchall()
print(f"Found {len(mapped_accounts)} mapped HR accounts in mapping_groups_v2:")

total_financials = 0.0
for group_name, odoo_code, partida_desc in mapped_accounts:
    # Query financials for this partida
    c.execute("""
        SELECT amount FROM financials
        WHERE year='2026' AND month='ENE' AND unit='Rodeo' AND partida=?
    """, (partida_desc,))
    f_row = c.fetchone()
    amount = f_row[0] if f_row else 0.0
    print(f"  Code: {odoo_code} | Group: {group_name:<50} | Description: {partida_desc:<50} | ENE Rodeo: {amount}")
    total_financials += amount

print("-"*80)
print(f"SUM OF INDIVIDUAL FINANCIAL VALUES: {total_financials:.2f}")

conn.close()
