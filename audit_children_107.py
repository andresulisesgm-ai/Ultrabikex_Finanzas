import sqlite3
conn = sqlite3.connect('data/ultrax.db')
conn.row_factory = sqlite3.Row
print('--- CHILDREN OF ID 107 ---')
rows = conn.execute("SELECT id, nombre, nivel, parent_id FROM eerr_nodes WHERE parent_id=107").fetchall()
for r in rows:
    print(dict(r))
conn.close()
