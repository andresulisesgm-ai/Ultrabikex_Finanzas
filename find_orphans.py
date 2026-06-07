import sqlite3

conn = sqlite3.connect('data/ultrax.db')
conn.row_factory = sqlite3.Row

# Partidas en financials
financial_partidas = set(r[0] for r in conn.execute('SELECT DISTINCT partida FROM financials').fetchall())

# Nombres en eerr_nodes
node_names = set(r[0] for r in conn.execute('SELECT nombre FROM eerr_nodes').fetchall())

unmapped = financial_partidas - node_names

print(f"Partidas en Financials: {len(financial_partidas)}")
print(f"Nombres en EERR Nodes: {len(node_names)}")
print(f"Sin mapear (Financials -> Nodes): {len(unmapped)}")
print("\nLISTA DE PARTIDAS HUÉRFANAS:")
for p in sorted(unmapped):
    print(f"  - {p}")

conn.close()
