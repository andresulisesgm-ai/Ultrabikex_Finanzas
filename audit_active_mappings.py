import sqlite3
conn = sqlite3.connect('data/ultrax.db')
conn.row_factory = sqlite3.Row
print('--- MAPPINGS FOR ENE Rodeo ---')
rows = conn.execute("""
    SELECT m.partida_nota, n.nombre, n.id, f.amount 
    FROM eerr_mapping m 
    JOIN eerr_nodes n ON m.nodo_id = n.id 
    JOIN financials f ON m.partida_nota = f.partida 
    WHERE f.year=2026 AND f.month='ENE' AND f.unit='Rodeo'
""").fetchall()
for r in rows:
    print(dict(r))
conn.close()
