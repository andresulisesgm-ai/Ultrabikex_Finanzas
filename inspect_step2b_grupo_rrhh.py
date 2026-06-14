import sqlite3
import openpyxl
import os

db_path = 'data/ultrax.db'
excel_path = 'EEFF ULTRAX 2026.xlsx'

print("="*80)
print("SECCIÓN 1 - Encontrar el group_name de las '9 líneas RRHH' ya mapeadas:")
print("="*80)
try:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        SELECT mgv.id, mgv.group_name, mgv.odoo_code, mgv.report_type, mgv.display_order, m.partida
        FROM mapping_groups_v2 mgv
        JOIN mapping m ON mgv.odoo_code = m.odoo_code
        WHERE m.partida LIKE '%bono vacacional%'
           OR m.partida LIKE '%prestaciones sociales%'
           OR m.partida LIKE '%aporte patronal%'
           OR m.partida LIKE '%póliza HCM%'
           OR m.partida LIKE '%salud y seguridad%'
           OR m.partida LIKE '%utilidades empleados%'
           OR m.partida LIKE '%utilidades directivos%'
           OR m.partida LIKE '%bono de guardería%'
           OR m.partida LIKE '%fiestas y agasajos%'
           OR m.partida LIKE '%donaciones y obsequios%'
           OR m.partida LIKE '%capacitación al personal%'
           OR m.partida LIKE '%transporte del personal%'
        ORDER BY mgv.display_order;
    """)
    rows = c.fetchall()
    for r in rows:
        print(r)
except Exception as e:
    print("Error in Sección 1:", e)

print("\n" + "="*80)
print("SECCIÓN 2 - Buscar en N EERR el encabezado/subtotal que agrupa el bloque de filas 110-136:")
print("="*80)
try:
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    ws = wb['N EERR']
    for r_idx in range(95, 113):
        cell_a = ws.cell(row=r_idx, column=1)
        cell_b = ws.cell(row=r_idx, column=2)
        val_a = cell_a.value
        val_b = cell_b.value
        if val_a is not None or val_b is not None:
            print(f"Row {r_idx}: A={repr(val_a)}, B={repr(val_b)}")
except Exception as e:
    print("Error in Sección 2:", e)

print("\n" + "="*80)
print("SECCIÓN 3 - Buscar en EERR ULTRAX (hoja de presentación) cualquier línea con 'Personal', 'RRHH', o 'Recursos Humanos':")
print("="*80)
try:
    ws_pres = wb['EERR ULTRAX']
    for r_idx in range(1, ws_pres.max_row + 1):
        for c_idx in range(1, ws_pres.max_column + 1):
            cell = ws_pres.cell(row=r_idx, column=c_idx)
            val = cell.value
            if val and any(word in str(val).lower() for word in ['personal', 'rrhh', 'recursos humanos']):
                # Print current cell and the next few cells in the row to find values
                row_vals = [ws_pres.cell(row=r_idx, column=i).value for i in range(1, ws_pres.max_column + 1)]
                print(f"Cell {cell.coordinate}: {repr(val)}")
                print(f"  Entire Row {r_idx}: {[v for v in row_vals if v is not None][:10]}")
except Exception as e:
    print("Error in Sección 3:", e)

if conn:
    conn.close()
