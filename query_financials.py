#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('data/ultrax.db')

rows = conn.execute("""
    SELECT year, month, unit, partida, amount
    FROM financials
    WHERE partida = 'Gastos de asistencia outsorcing'
""").fetchall()

print("="*80)
print("BÚSQUEDA EN FINANCIALS: 'Gastos de asistencia outsorcing'")
print("="*80)
print(f"\nRegistros encontrados: {len(rows)}")

if rows:
    print("\nDETALLE:")
    print("-"*80)
    for r in rows:
        print(f"Year: {r[0]} | Month: {r[1]} | Unit: {r[2]} | Partida: {r[3]} | Amount: {r[4]:,.2f}")
else:
    print("\n[INFO] No hay datos en financials para esta partida")

conn.close()
