import sqlite3
import re

class EERREngine:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def calculate(self, year, month, unit):
        conn = self.get_connection()
        
        # 1. Cargar Nodos
        nodes = {r['id']: dict(r) for r in conn.execute('SELECT * FROM eerr_nodes ORDER BY nivel DESC, display_order').fetchall()}
        node_values = {node_id: 0.0 for node_id in nodes}

        # 2. Cargar Mapeos
        mappings = conn.execute('SELECT * FROM eerr_mapping').fetchall()
        
        # 3. Cargar Datos Financials
        financials = conn.execute(
            'SELECT partida, amount FROM financials WHERE year=? AND month=? AND unit=?',
            (year, month, unit)
        ).fetchall()
        fin_dict = {r['partida']: r['amount'] for r in financials}

        # 4. Fase A: Asignar valores a hojas (Leaf nodes)
        mapped_count = 0
        for m in mappings:
            partida = m['partida_nota']
            if partida in fin_dict:
                node_values[m['nodo_id']] += fin_dict[partida] * m['sign']
                mapped_count += 1
        
        print(f"DEBUG: {len(financials)} registros en financials, {len(mappings)} mappings, {mapped_count} mapeados con éxito.")

        # 5. Fase B: Agregación Bottom-Up (Hijo -> Padre)
        # Ordenados por nivel desc (más profundos primero)
        sorted_nodes = sorted(nodes.values(), key=lambda x: x['nivel'], reverse=True)
        for node in sorted_nodes:
            if node['parent_id'] is not None and node['parent_id'] in node_values:
                node_values[node['parent_id']] += node_values[node['id']]

        # 6. Fase C: Cálculos de Fórmulas
        formulas = conn.execute('SELECT nodo_id, formula FROM eerr_formulas').fetchall()
        
        # Función para evaluar fórmula: "NODE(1000) - NODE(2000)"
        def evaluate_formula(formula, values):
            def replace_node(match):
                node_id = int(match.group(1))
                return str(values.get(node_id, 0.0))
            
            expr = re.sub(r'NODE\((\d+)\)', replace_node, formula)
            try:
                # Seguridad: Solo permitimos números, operadores básicos y paréntesis
                if not re.match(r'^[0-9\.\+\-\*\/\(\)\s]+$', expr):
                    return 0.0
                return eval(expr)
            except:
                return 0.0

        # Para simplificar, iteramos varias veces para resolver dependencias (o podríamos usar un DAG)
        # En este caso, 3 iteraciones bastan para la profundidad de ULTRAX
        for _ in range(3):
            for f in formulas:
                node_values[f['nodo_id']] = evaluate_formula(f['formula'], node_values)

        conn.close()
        return node_values, nodes

    def get_report_structure(self, node_values, nodes):
        """Convierte los resultados en una lista plana para el frontend."""
        # Ordenar por display_order si existe, o por ID para mantener estructura de seed
        report = []
        # Re-obtener nodos en orden jerárquico (top-down)
        conn = self.get_connection()
        ordered_nodes = conn.execute('SELECT * FROM eerr_nodes ORDER BY id').fetchall()
        conn.close()

        for n in ordered_nodes:
            report.append({
                'id': n['id'],
                'nombre': n['nombre'],
                'nivel': n['nivel'],
                'tipo': n['tipo'],
                'bold': bool(n['bold']),
                'bg_color': n['bg_color'],
                'valor': node_values[n['id']]
            })
        return report
