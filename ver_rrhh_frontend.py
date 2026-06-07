#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Ver exactamente cómo se renderiza RRHH en el frontend para Rodeo ENE 2026"""

import requests
import json

# Ejecutar el endpoint
url = "http://localhost:5000/api/eerr/completo?year=2026&unit=Rodeo"

print('='*80)
print('CONSULTANDO EERR FRONTEND - RODEO ENE 2026')
print('='*80)
print(f'\nURL: {url}')

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    print(f'[OK] Respuesta recibida')

    # El EERR completo viene en data['eerr'] o data['months'][0]
    # Primero verificar estructura
    if 'months' in data and len(data['months']) > 0:
        eerr_data = data['months'][0]
        print(f"[INFO] Mes: {eerr_data.get('month', 'N/A')}")
    else:
        print('[ERROR] No se encontró data de meses en la respuesta')
        print(json.dumps(data, indent=2))
        exit(1)

    # Buscar la sección de RRHH
    lines = eerr_data.get('lines', [])

    print(f'\n[INFO] Total de líneas en EERR: {len(lines)}')

    # Encontrar el índice de "Subtotal Gastos de Recursos Humanos"
    rrhh_start = -1
    rrhh_end = -1

    for i, line in enumerate(lines):
        if line['name'] == 'Subtotal Gastos de Recursos Humanos':
            rrhh_start = i
        elif rrhh_start >= 0 and line['name'] == 'Subtotal Gastos de Comercialización y Logistica':
            rrhh_end = i
            break

    if rrhh_start < 0:
        print('[ERROR] No se encontró la sección de RRHH')
        exit(1)

    print(f'\n[INFO] Sección RRHH encontrada: líneas {rrhh_start} a {rrhh_end}')

    # Extraer líneas de RRHH
    rrhh_lines = lines[rrhh_start:rrhh_end] if rrhh_end > 0 else lines[rrhh_start:]

    print('\n' + '='*80)
    print('SECCIÓN DE RECURSOS HUMANOS - RODEO ENE 2026')
    print('='*80)

    total_rrhh = 0
    partidas_con_datos = []
    partidas_sin_datos = []

    for i, line in enumerate(rrhh_lines):
        name = line['name']
        value = line.get('value', 0)
        is_header = line.get('is_header', False)
        is_total = line.get('is_total', False)

        # Formatear el tipo de línea
        if is_header or is_total:
            tipo = '[HEADER/TOTAL]'
        else:
            tipo = '[PARTIDA]    '

        # Formatear valor
        if value == 0:
            valor_str = '$0.00'
            if not (is_header or is_total):
                partidas_sin_datos.append(name)
        else:
            valor_str = f'${value:,.2f}'
            if not (is_header or is_total):
                partidas_con_datos.append((name, value))
                if value > 0:  # Solo sumar gastos positivos (no ingresos negativos)
                    total_rrhh += value

        print(f'{i:2d}. {tipo} {name:60s} {valor_str:>15s}')

    print('\n' + '='*80)
    print('RESUMEN')
    print('='*80)
    print(f'Total de líneas en sección RRHH: {len(rrhh_lines)}')
    print(f'Partidas con datos: {len(partidas_con_datos)}')
    print(f'Partidas sin datos ($0.00): {len(partidas_sin_datos)}')
    print(f'\nTotal RRHH calculado: ${total_rrhh:,.2f}')

    if partidas_sin_datos:
        print('\n[ALERT] PARTIDAS CON $0.00 (candidatas para limpieza):')
        for p in partidas_sin_datos:
            print(f'  - {p}')

    # Verificar duplicados
    partida_names = [p[0] for p in partidas_con_datos]
    duplicados = [name for name in partida_names if partida_names.count(name) > 1]
    if duplicados:
        print('\n[ALERT] PARTIDAS DUPLICADAS:')
        for dup in set(duplicados):
            print(f'  - {dup}')

    print('\n[PARTIDAS CON DATOS]:')
    for name, value in partidas_con_datos:
        print(f'  {name:60s} ${value:,.2f}')

except requests.exceptions.ConnectionError:
    print('\n[ERROR] No se pudo conectar al servidor Flask')
    print('Asegúrate de que el servidor esté corriendo con: python app.py')
except Exception as e:
    print(f'\n[ERROR] {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
