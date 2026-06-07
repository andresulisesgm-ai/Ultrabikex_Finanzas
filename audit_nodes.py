import sqlite3
conn = sqlite3.connect('data/ultrax.db')
conn.row_factory = sqlite3.Row
print('--- EERR NODES (Top 20) ---')
rows = conn.execute("SELECT id, parent_id, nombre, nivel FROM eerr_nodes LIMIT 20").fetchall()
for r in rows:
    print(dict(r))

print('\n--- MAPPING (Top 5) ---')
rows = conn.execute("SELECT partida_nota, nodo_id FROM eerr_mapping LIMIT 5").fetchall()
for r in rows:
    print(dict(r))
conn.close()
