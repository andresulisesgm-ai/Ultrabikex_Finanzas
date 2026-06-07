import sqlite3
from engine import EERR_STRUCTURE

DB_PATH = 'data/ultrax.db'

def setup_full_eerr():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM eerr_mapping')
    cursor.execute('DELETE FROM eerr_formulas')
    cursor.execute('DELETE FROM eerr_nodes')

    nodes_to_insert = []
    mappings_to_insert = []
    
    current_parents = {}
    node_id_map = {} 

    for i, item in enumerate(EERR_STRUCTURE):
        name, is_header, _, bold, bg_color, level = item
        node_id = i + 1
        
        # AJUSTE MANUAL DE NIVELES PARA AGRUPACIÓN
        if name in ('Gastos de impuestos, tasas y contribuciones', 
                    'Depreciaciones, deterioro y Amortización',
                    'Gastos Bancarios'):
            is_header = True
            level = 2

        node_id_map[(name, level)] = node_id
        
        parent_id = None
        if level > 0:
            for l in range(level - 1, -1, -1):
                if l in current_parents:
                    parent_id = current_parents[l]
                    break
        
        # REGLA DE EXCLUSIÓN: Nodos que NO deben sumarse a su padre (según Excel)
        if name == 'Depreciaciones, deterioro y Amortización':
            parent_id = None # Excluir de Subtotal Admin

        if is_header:
            current_parents[level] = node_id
            for l in range(level + 1, 4):
                if l in current_parents: del current_parents[l]
        
        tipo = 'hoja'
        if is_header:
            if level == 0: tipo = 'total'
            elif level == 1: tipo = 'subtotal'
            else: tipo = 'grupo'

        nodes_to_insert.append((node_id, parent_id, name, level, tipo, 1 if bold else 0, bg_color, i * 10))
        if not is_header: mappings_to_insert.append((name, node_id, 1))

    # MAPEO DE PARTIDAS HUÉRFANAS Y ESPECÍFICAS
    orphans = [
        ('Costos de venta por servicios del café', 'Costo de venta por servicio del café', 3),
        ('Deterioro de inventarios', 'Faltante y deterioro de inventarios', 3),
        ('Gastos de comida por viáticos administrativos', 'Viáticos administrativos', 3),
        ('Gastos de deterioration por cuentas incobrables', 'Depreciaciones, deterioro y Amortización', 3),
        ('Gastos de envíos/fletes en ventas y compras no incluidas en el costo', 'Gastos de fletes y envios no asociados al costo', 3),
        ('Gastos de hospedaje por viáticos administrativos', 'Viáticos administrativos', 3),
        ('Gastos de impuesto por licencia de actividades economicas', 'Gastos de impuestos, tasas y contribuciones', 3),
        ('Gastos de impuesto por publicidad', 'Gastos de impuestos, tasas y contribuciones', 3),
        ('Gastos de intereses sobre préstamos de terceros', 'Gastos de intereses sobre préstamos', 3),
        ('Gastos de mantenimiento y reparación de maquinaria y equipos', 'Mantenimiento y reparaciones', 3),
        ('Gastos de mantenimiento y reparación de mobiliario y equipo', 'Mantenimiento y reparaciones', 3),
        ('Gastos de transporte por viáticos administrativos', 'Viáticos administrativos', 3),
        ('Ingresos por Taller', 'Ingresos por taller', 3),
        ('Gasto por impuesto a las pensiones', 'Gastos de impuestos, tasas y contribuciones', 3),
        ('Gastos de IGTF', 'Gastos Bancarios', 3),
        ('Gastos de comisiones bancarias', 'Gastos Bancarios', 3),
        ('Gastos de deterioro por cuentas incobrables', 'Depreciaciones, deterioro y Amortización', 3)
    ]
    for odoo_p, eerr_n, level in orphans:
        target_id = node_id_map.get((eerr_n, level))
        if not target_id: target_id = node_id_map.get((eerr_n, 2))
        if target_id: mappings_to_insert.append((odoo_p, target_id, 1))

    cursor.executemany('INSERT INTO eerr_nodes (id, parent_id, nombre, nivel, tipo, bold, bg_color, display_order) VALUES (?,?,?,?,?,?,?,?)', nodes_to_insert)
    cursor.executemany('INSERT OR REPLACE INTO eerr_mapping (partida_nota, nodo_id, sign) VALUES (?,?,?)', mappings_to_insert)

    def get_id(name, level=0): return node_id_map.get((name, level))

    ID_ING_TOT = get_id('Total Ingresos', 0)
    ID_COST_TOT = get_id('Total Costo de Ventas', 0)
    ID_UB = get_id('Utilidad Bruta', 0)
    ID_GAS_OP = get_id('Total Gastos Operacionales', 0)
    ID_COMER = get_id('Subtotal Gastos de Comercialización y Logistica', 1)
    ID_DEPR = get_id('Depreciaciones, deterioro y Amortización', 2)
    ID_IMP = get_id('Gastos de impuestos, tasas y contribuciones', 2)
    ID_U_B4_COM = get_id('Utilidad antes de Comisiones por Ventas', 0)
    ID_U_AFT_COM = get_id('Utilidad después de Comisiones por Ventas', 0)
    ID_EBITDA = get_id('Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA)', 0)
    ID_G_NO_OP = get_id('Otros Gastos no Operacionales', 0)
    ID_I_NO_OP = get_id('Otros Ingresos no Operacionales', 0)
    ID_NET = get_id('Utilidad Neta', 0)

    formulas = [
        # UB
        (ID_UB, f"NODE({ID_ING_TOT}) - NODE({ID_COST_TOT})"),
        # U. antes Comisiones = UB - (Gas_Op - Comer)
        (ID_U_B4_COM, f"NODE({ID_UB}) - (NODE({ID_GAS_OP}) - NODE({ID_COMER}))"),
        # U. después Comisiones
        (ID_U_AFT_COM, f"NODE({ID_U_B4_COM}) - NODE({ID_COMER})"),
        # EBITDA = Utilidad + Impuestos + Depreciaciones
        (ID_EBITDA, f"NODE({ID_U_AFT_COM}) + NODE({ID_IMP}) + NODE({ID_DEPR})"),
        # EBIT = EBITDA - Depreciaciones
        (get_id('Utilidad antes de Intereses e Impuestos (EBIT)', 0), f"NODE({ID_EBITDA}) - NODE({ID_DEPR})"),
        # Total Gastos Op y No Op
        (get_id('Total Gastos Operacionales y No Operacionales', 0), f"NODE({ID_GAS_OP}) + NODE({ID_G_NO_OP}) + NODE({ID_DEPR})"),
        # Utilidad Neta
        (ID_NET, f"NODE({ID_U_AFT_COM}) - NODE({ID_G_NO_OP}) + NODE({ID_I_NO_OP})"),
        # Neta despues ISLR
        (get_id('Utilidad Neta despues de ISLR', 0), f"NODE({ID_NET}) - NODE({get_id('ISLR', 0)})")
    ]
    
    cursor.executemany('INSERT INTO eerr_formulas (nodo_id, formula) VALUES (?,?)', [f for f in formulas if f[0]])
    conn.commit()
    conn.close()
    print("EERR Migración Final v2 Completa.")

if __name__ == '__main__':
    setup_full_eerr()
