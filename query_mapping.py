#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('data/ultrax.db')

print("="*80)
print("CONSULTA 1: odoo_code = '6.01.01.01.005'")
print("="*80)
result1 = conn.execute("SELECT odoo_code, odoo_name, partida FROM mapping WHERE odoo_code = '6.01.01.01.005'").fetchone()
print(result1)

print("\n" + "="*80)
print("CONSULTA 2: odoo_name LIKE '%outsor%'")
print("="*80)
result2 = conn.execute("SELECT odoo_code, odoo_name, partida FROM mapping WHERE odoo_name LIKE '%outsor%'").fetchall()
for row in result2:
    print(f"Code: {row[0]}")
    print(f"Name: {row[1]}")
    print(f"Partida: {row[2]}")
    print("-" * 80)

print(f"\nTotal resultados: {len(result2)}")

conn.close()
