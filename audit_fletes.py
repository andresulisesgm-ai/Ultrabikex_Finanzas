import sqlite3
conn = sqlite3.connect('data/ultrax.db')
conn.row_factory = sqlite3.Row
print('--- NODES Fletes/Envios ---')
rows = conn.execute("SELECT id, nombre, parent_id FROM eerr_nodes WHERE nombre LIKE '%envíos%' OR nombre LIKE '%fletes%'").fetchall()
for r in rows:
    print(dict(r))
conn.close()
