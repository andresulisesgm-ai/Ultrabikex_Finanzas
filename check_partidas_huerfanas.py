import sqlite3
import engine

conn = sqlite3.connect('data/ultrax.db')
conn.row_factory = sqlite3.Row

# 1. Nombres de partida HOJA (is_header=False) que espera EERR_STRUCTURE
partidas_estructura = set()
for tupla in engine.EERR_STRUCTURE:
    nombre, is_header = tupla[0], tupla[1]
    if not is_header:
        partidas_estructura.add(nombre)

# 2. Nombres de partida reales en financials (con algún monto distinto de 0, todas las unidades/meses/años)
rows = conn.execute("SELECT DISTINCT partida FROM financials WHERE amount != 0").fetchall()
partidas_financials = set(r['partida'] for r in rows)

# 3. Huérfanas: existen en financials pero NO en EERR_STRUCTURE (dato real que el EERR nunca va a sumar)
huerfanas = partidas_financials - partidas_estructura

print(f"Total partidas distintas en financials (con monto != 0): {len(partidas_financials)}")
print(f"Total partidas hoja en EERR_STRUCTURE: {len(partidas_estructura)}")
print(f"\n=== PARTIDAS HUÉRFANAS (en financials, sin equivalente en EERR_STRUCTURE): {len(huerfanas)} ===")
for p in sorted(huerfanas):
    # Sumar monto total afectado y unidades/meses para dimensionar el impacto
    detalle = conn.execute(
        "SELECT unit, month, year, amount FROM financials WHERE partida=? ORDER BY year, month",
        [p]
    ).fetchall()
    total = sum(d['amount'] for d in detalle)
    unidades = sorted(set(d['unit'] for d in detalle))
    print(f"\n'{p}'")
    print(f"  Monto total acumulado: {total:.2f}")
    print(f"  Unidades afectadas: {unidades}")
    print(f"  Filas: {len(detalle)}")

conn.close()
