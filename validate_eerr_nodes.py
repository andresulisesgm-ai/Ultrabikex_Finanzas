from eerr_engine import EERREngine
import pandas as pd

# Valores extraídos del Excel durante la auditoría
EXCEL_EXPECTED = {
    'ENE': {
        'Total Ingresos': 47933.03,
        'Total Costo de Ventas': 20670.85,
        'Utilidad Bruta': 27262.18,
        'Utilidad antes de Comisiones por Ventas': 17744.14,
        'Utilidad después de Comisiones por Ventas': 14406.54,
        'Utilidad Neta': -3513.65
    },
    'FEB': {
        'Total Ingresos': 51483.04,
        'Total Costo de Ventas': 24313.03,
        'Utilidad Bruta': 27170.01,
        'Utilidad antes de Comisiones por Ventas': 18423.49,
        'Utilidad después de Comisiones por Ventas': 17321.13,
        'Utilidad Neta': 8089.50
    },
    'MAR': {
        'Total Ingresos': 64106.18,
        'Total Costo de Ventas': 19883.02,
        'Utilidad Bruta': 44223.16,
        'Utilidad antes de Comisiones por Ventas': 34479.48,
        'Utilidad después de Comisiones por Ventas': 30275.20,
        'Utilidad Neta': 21401.30
    }
}

engine = EERREngine('data/ultrax.db')

def run_test():
    for month, expected in EXCEL_EXPECTED.items():
        print(f"\nVALIDANDO {month} 2026 (Unidad: Rodeo)...")
        node_values, nodes = engine.calculate('2026', month, 'Rodeo')
        
        # Mapear nombres de nodos a valores calculados
        results = {n['nombre']: node_values[n['id']] for n in nodes.values()}
        
        # DEBUG: Ver todos los nodos con valor != 0
        print("  --- DEBUG: NODOS CON VALOR ---")
        for nid in sorted(node_values.keys()):
            val = node_values[nid]
            if abs(val) > 0.01:
                print(f"    ID {nid:3d}: {nodes[nid]['nombre']:40s} = {val:12,.2f}")
        
        all_ok = True
        for key, expected_val in expected.items():
            actual_val = results.get(key, 0.0)
            diff = abs(actual_val - expected_val)
            ok = diff < 0.01
            status = "✅ OK" if ok else f"❌ FAIL (Diff: {diff:,.2f})"
            print(f"  {key:40s}: Actual={actual_val:12,.2f} | Expected={expected_val:12,.2f} | {status}")
            if not ok:
                all_ok = False
        
        if all_ok:
            print(f"RESULTADO: {month} VALIDADO AL CENTAVO.")
        else:
            print(f"RESULTADO: {month} TIENE DISCREPANCIAS.")

if __name__ == '__main__':
    run_test()
