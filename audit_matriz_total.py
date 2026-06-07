import pandas as pd

xl = pd.ExcelFile('2 EEFF ULTRAX Rodeo.xlsx')
df_n = pd.read_excel(xl, 'N EERR RODEO', header=None)
df_e = pd.read_excel(xl, 'EERR RODEO', header=None)

# Mapeo de columnas: (Notas, EERR)
months = {
    'ENE': (2, 4),
    'FEB': (3, 8),
    'MAR': (4, 12),
}

# Mapeo de filas (índices 0-based)
rows_n = {
    'Ing_Op': 4,      # Total Ingresos Operativos
    'Costo': 28,      # Total Costo de Ventas
    'Gasto_Total': 35, # Total Gastos
    'Gasto_Op': 36,   # Total Gastos Operacionales
    'Ing_No_Op': 16,  # Total Ingresos No Operativos
    'Comer': 138,     # Subtotal Gastos de Comercialización
}

rows_e = {
    'Ing_Op': 3,      # Total Ingresos
    'Costo': 20,     # Total Costo de Ventas
    'UB': 34,        # Utilidad Bruta
    'U_b4_Com': 107, # Utilidad antes de Comisiones
    'U_aft_Com': 110,# Utilidad después de Comisiones
    'Net': 135,      # Utilidad Neta
}

def clean(val):
    try:
        return float(val) if pd.notna(val) else 0.0
    except:
        return 0.0

for m, cols in months.items():
    print(f"\n--- MATRIZ TRAZABILIDAD: {m} ---")
    
    n_col = cols[0]
    e_col = cols[1]
    
    # Valores Notas
    n_ing_op = clean(df_n.iloc[rows_n['Ing_Op'], n_col])
    n_costo = clean(df_n.iloc[rows_n['Costo'], n_col])
    n_gasto_tot = clean(df_n.iloc[rows_n['Gasto_Total'], n_col])
    n_gasto_op = clean(df_n.iloc[rows_n['Gasto_Op'], n_col])
    n_ing_no_op = clean(df_n.iloc[rows_n['Ing_No_Op'], n_col])
    n_comer = clean(df_n.iloc[rows_n['Comer'], n_col])
    
    # Valores EERR (Esperados)
    e_ing_op = clean(df_e.iloc[rows_e['Ing_Op'], e_col])
    e_costo = clean(df_e.iloc[rows_e['Costo'], e_col])
    e_ub = clean(df_e.iloc[rows_e['UB'], e_col])
    e_u_b4 = clean(df_e.iloc[rows_e['U_b4_Com'], e_col])
    e_u_aft = clean(df_e.iloc[rows_e['U_aft_Com'], e_col])
    e_net = clean(df_e.iloc[rows_e['Net'], e_col])
    
    # Fórmulas calculadas
    calc_ub = n_ing_op - n_costo
    calc_u_b4 = calc_ub - (n_gasto_op - n_comer)
    calc_u_aft = calc_u_b4 - n_comer
    calc_gasto_no_op = n_gasto_tot - n_gasto_op
    calc_net = calc_u_aft - calc_gasto_no_op + n_ing_no_op
    
    print(f"1. Ingresos Op: Notas={n_ing_op:,.2f} | EERR={e_ing_op:,.2f} | OK={abs(n_ing_op-e_ing_op)<1}")
    print(f"2. Costos:      Notas={n_costo:,.2f} | EERR={e_costo:,.2f} | OK={abs(n_costo-e_costo)<1}")
    print(f"3. Util. Bruta: Calc={calc_ub:,.2f} | EERR={e_ub:,.2f} | OK={abs(calc_ub-e_ub)<1}")
    print(f"4. U. b4 Comis: Calc={calc_u_b4:,.2f} | EERR={e_u_b4:,.2f} | OK={abs(calc_u_b4-e_u_b4)<1}")
    print(f"5. U. aft Comis: Calc={calc_u_aft:,.2f} | EERR={e_u_aft:,.2f} | OK={abs(calc_u_aft-e_u_aft)<1}")
    print(f"6. Util. Neta:  Calc={calc_net:,.2f} | EERR={e_net:,.2f} | OK={abs(calc_net-e_net)<1}")
