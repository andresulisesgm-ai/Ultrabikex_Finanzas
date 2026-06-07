import sqlite3
conn = sqlite3.connect('data/ultrax.db')
conn.row_factory = sqlite3.Row
print('--- FINANCIALS Personal Rodeo ENE ---')
rows = conn.execute("SELECT partida, amount FROM financials WHERE year=2026 AND month='ENE' AND unit='Rodeo' AND partida LIKE '%personal%'").fetchall()
for r in rows:
    print(dict(r))
conn.close()
