import sqlite3
conn = sqlite3.connect('data/ultrax.db')
conn.row_factory = sqlite3.Row
print('--- INGRESOS MAPPING ---')
rows = conn.execute("SELECT * FROM mapping WHERE odoo_code LIKE '4.%' LIMIT 20").fetchall()
for r in rows:
    print(dict(r))

print('\n--- GASTOS MAPPING ---')
rows = conn.execute("SELECT * FROM mapping WHERE odoo_code LIKE '6.%' LIMIT 20").fetchall()
for r in rows:
    print(dict(r))
conn.close()
