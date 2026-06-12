import os
import sys
import shutil
import sqlite3
import pandas as pd
import openpyxl
import unicodedata
import re

# Configurar rutas
PROJECT_DIR = r"C:\Users\andre\Desktop\ultrax_app"
sys.path.append(PROJECT_DIR)

db_real = os.path.join(PROJECT_DIR, "data", "ultrax_backup_pre_atomic.db")
db_test = os.path.join(PROJECT_DIR, "data", "ultrax_test.db")
trial_balance_path = os.path.join(PROJECT_DIR, "ESTADO DE RESULTADOS ODOO COMPROBACION1.xlsx")
reference_path = os.path.join(PROJECT_DIR, "EEFF ULTRAX 2026.xlsx")
output_path = os.path.join(PROJECT_DIR, "diagnostico_eerr_paqueteB_resultado.md")

def normalize_name(s):
    if not s:
        return ""
    # Remover acentos y caracteres especiales
    s = "".join(c for c in unicodedata.normalize('NFD', str(s)) if unicodedata.category(c) != 'Mn')
    # Convertir a minúsculas y quitar todos los espacios
    s = s.lower().strip()
    s = re.sub(r'\s+', '', s)
    return s

def main():
    print("=== INICIANDO FASE 3 DE DIAGNÓSTICO ===")
    
    # 1. Crear copia de la base de datos
    if os.path.exists(db_test):
        os.remove(db_test)
    shutil.copy2(db_real, db_test)
    print(f"Base de datos de prueba creada en: {db_test}")
    
    # 2. Leer trial balance
    print(f"Leyendo trial balance: {trial_balance_path}")
    df_trial = pd.read_excel(trial_balance_path, header=None)
    accounts = []
    names_map = {}
    for idx, row in df_trial.iterrows():
        cell = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ''
        cell = cell.strip()
        if cell and cell[0].isdigit() and '.' in cell[:5]:
            parts = cell.split(' ', 1)
            if len(parts) == 2:
                code = parts[0].strip()
                name = parts[1].strip()
                try:
                    balance = float(row.iloc[2]) if pd.notna(row.iloc[2]) else 0.0
                except (ValueError, IndexError):
                    balance = 0.0
                accounts.append((code, name, balance))
                names_map[code] = name
                
    print(f"Cuentas encontradas en balance de comprobación: {len(accounts)}")
    
    # 3. Conectar a ultrax_test.db para buscar mappings e insertar en financials
    conn = sqlite3.connect(db_test)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Borrar registros previos para Rodeo 2026 ENE
    cursor.execute("DELETE FROM financials WHERE year='2026' AND month='ENE' AND unit='Rodeo'")
    conn.commit()
    print("Registros anteriores de Rodeo 2026 ENE eliminados de ultrax_test.db")
    
    # Mapear e insertar
    partida_amounts = {}
    unmapped_trial = []
    
    for code, name, balance in accounts:
        # Buscar en mapping
        m = cursor.execute("SELECT partida, sign FROM mapping WHERE odoo_code=?", (code,)).fetchone()
        if m:
            partida = m['partida']
            sign = m['sign']
            amount = balance * sign
            partida_amounts[partida] = partida_amounts.get(partida, 0.0) + amount
        else:
            unmapped_trial.append((code, name, balance))
            
    print(f"Cuentas mapeadas: {len(partida_amounts)} partidas únicas.")
    print(f"Cuentas sin mapear encontradas en el archivo de prueba: {len(unmapped_trial)}")
    
    # Insertar partidas acumuladas en financials
    for partida, amount in partida_amounts.items():
        cursor.execute(
            '''INSERT INTO financials (year, month, unit, partida, amount) VALUES (?,?,?,?,?)
               ON CONFLICT(year, month, unit, partida) DO UPDATE SET amount=excluded.amount''',
            ('2026', 'ENE', 'Rodeo', partida, amount)
        )
    conn.commit()
    print("Partidas insertadas en tabla financials de ultrax_test.db")
    
    # 4. Patch y carga de app.py apuntando a ultrax_test.db
    # Modificamos la variable DB_PATH de db.py antes de importar app
    import db
    db.DB_PATH = db_test
    
    from app import app, eerr_completo_v2_ui_adapter
    
    # Ejecutar adaptador en contexto de Flask
    print("Ejecutando eerr_completo_v2_ui_adapter para Rodeo 2026...")
    with app.app_context():
        adapter_res = eerr_completo_v2_ui_adapter('2026', 'Rodeo')
        
    calculated_vals = {}
    for row in adapter_res['rows']:
        partida = row['partida']
        val = row['meses'][0]['ejecutado']['valor'] # ENE es index 0
        calculated_vals[partida] = val
        
    print(f"Adaptador retornó {len(calculated_vals)} partidas.")
    
    # 5. Leer hoja 'EERR ULTRAX' de EEFF ULTRAX 2026.xlsx
    print(f"Leyendo Excel de referencia: {reference_path}")
    wb = openpyxl.load_workbook(reference_path, data_only=True)
    ws = wb["EERR ULTRAX"]
    
    expected_vals = {}
    expected_original_names = {}
    
    # Columnas: columna 1 (A) es PARTIDAS, columna 5 (E) es ENE
    for row_idx in range(4, ws.max_row + 1):
        partida_name = ws.cell(row=row_idx, column=1).value
        if partida_name:
            partida_name_str = str(partida_name).strip()
            val = ws.cell(row=row_idx, column=5).value
            val_float = float(val) if val is not None else 0.0
            expected_vals[partida_name_str] = val_float
            expected_original_names[normalize_name(partida_name_str)] = partida_name_str
            
    wb.close()
    print(f"Cargadas {len(expected_vals)} partidas del Excel de referencia.")
    
    # 6. Comparación
    comparison = []
    matched_expected_normalized = set()
    
    for part_calc, val_calc in calculated_vals.items():
        norm_calc = normalize_name(part_calc)
        
        # Buscar en expected_vals por normalización
        found_expected_name = None
        for exp_name in expected_vals.keys():
            if normalize_name(exp_name) == norm_calc:
                found_expected_name = exp_name
                break
                
        if found_expected_name:
            val_expected = expected_vals[found_expected_name]
            matched_expected_normalized.add(normalize_name(found_expected_name))
        else:
            val_expected = 0.0
            
        diff = val_calc - val_expected
        comparison.append({
            'partida': part_calc,
            'valor_calculado': val_calc,
            'valor_esperado': val_expected,
            'diferencia': diff,
            'coincide_nombre': found_expected_name if found_expected_name else "No encontrado en Excel"
        })
        
    # Identificar partidas en Excel sin contraparte en el sistema
    excel_only = []
    for exp_name, val_expected in expected_vals.items():
        norm_exp = normalize_name(exp_name)
        if norm_exp not in matched_expected_normalized:
            excel_only.append((exp_name, val_expected))
            
    # Ordenar comparación: diferencias significativas primero
    comparison_sorted = sorted(comparison, key=lambda x: abs(x['diferencia']), reverse=True)
    
    # 7. Escribir diagnostico_eerr_fase3.md
    print(f"Escribiendo reporte en: {output_path}")
    md = []
    md.append("# DIAGNÓSTICO ULTRAX - PAQUETE B RESULTADO\n")
    md.append("> **Nota:** Documento generado en modo de solo lectura sobre la base de datos de prueba `ultrax_test.db`.\n\n")
    
    md.append("## 1. COMPARATIVA DE SALDOS REALES (Calculado vs Esperado - ENE 2026)\n")
    md.append("Comparación de los montos calculados por `eerr_completo_v2_ui_adapter()` usando `ESTADO DE RESULTADOS ODOO COMPROBACION1.xlsx` contra los montos esperados en la hoja 'EERR ULTRAX' de `EEFF ULTRAX 2026.xlsx` para el mes de Enero 2026 (Rodeo).\n\n")
    
    md.append("| Partida en Sistema | Partida en Excel | Valor Calculado | Valor Esperado (Excel) | Diferencia |\n")
    md.append("| --- | --- | --- | --- | --- |\n")
    
    for c in comparison_sorted:
        diff_style = f"**{c['diferencia']:.2f}**" if abs(c['diferencia']) > 0.01 else f"{c['diferencia']:.2f}"
        md.append(f"| {c['partida']} | {c['coincide_nombre']} | {c['valor_calculado']:.2f} | {c['valor_esperado']:.2f} | {diff_style} |\n")
        
    md.append("\n---\n\n")
    
    md.append("## 2. LÍNEAS DEL EXCEL SIN CONTRAPARTE EN EL SISTEMA\n")
    md.append("Las siguientes líneas del archivo `EEFF ULTRAX 2026.xlsx` (hoja EERR ULTRAX) no se encontraron en la salida del adaptador jerárquico. Estas representan partidas del Excel que no tienen correspondencia de nombres en la estructura de la aplicación:\n\n")
    
    md.append("| Partida en Excel | Valor Esperado (ENE) |\n")
    md.append("| --- | --- |\n")
    if not excel_only:
        md.append("| *Ninguna* | *Ninguno* |\n")
    else:
        for name, val in sorted(excel_only, key=lambda x: x[0]):
            md.append(f"| {name} | {val:.2f} |\n")
            
    md.append("\n")
    
    # Escribir el archivo final
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("".join(md))
        
    print(f"=== FASE 3 COMPLETADA. REPORTE GENERADO EN {output_path} ===")
    conn.close()

if __name__ == '__main__':
    main()
