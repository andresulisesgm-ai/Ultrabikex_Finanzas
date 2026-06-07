#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de validación: Excel vs Sistema
Compara partida por partida los montos de EERR para cualquier unidad/periodo

Uso:
    python validar_eerr.py --excel "ruta/al/archivo.xlsx" --unit "Rodeo" --year 2026 --month ENE
"""

import json
import openpyxl
import re
import argparse
import sys
import os
from datetime import datetime

def limpiar_nombre(texto):
    """Quita el código de cuenta al inicio (ej: '6.01.01.01.001 Gastos...' -> 'Gastos...')"""
    if not texto:
        return ''
    # Patrón: uno o más dígitos.dígitos... seguido de espacio
    texto = re.sub(r'^\d+(\.\d+)*\s+', '', texto.strip())
    # Quitar espacios extras al inicio (como "  Ganancia y Perdida")
    texto = texto.strip()
    return texto

def cargar_sistema(unit, year, server='http://localhost:5000'):
    """Carga datos del sistema vía API"""
    import urllib.request
    import urllib.error

    url = f"{server}/api/eerr/completo?year={year}&unit={unit}"

    print(f'\n[SISTEMA] Consultando: {url}')

    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode('latin-1'))

        print(f'  [OK] Respuesta recibida: {len(data.get("rows", []))} filas')
        return data

    except urllib.error.URLError as e:
        print(f'  [ERROR] No se pudo conectar al servidor: {e}')
        print(f'  [HINT] Asegúrate de que Flask esté corriendo: python app.py')
        return None
    except Exception as e:
        print(f'  [ERROR] Error al cargar datos: {e}')
        return None

def cargar_excel(excel_path):
    """Carga datos del Excel"""
    print(f'\n[EXCEL] Cargando: {excel_path}')

    if not os.path.exists(excel_path):
        print(f'  [ERROR] Archivo no encontrado: {excel_path}')
        return None

    try:
        wb = openpyxl.load_workbook(excel_path, data_only=True)
        sheet = wb.active
        print(f'  [OK] Excel cargado: {sheet.title}')
        return sheet
    except Exception as e:
        print(f'  [ERROR] No se pudo cargar Excel: {e}')
        return None

def parsear_excel(sheet):
    """Parsea el Excel y retorna diccionario {partida: valor}"""
    excel_dict = {}

    # Buscar fila de inicio (después de "Name" o directamente desde fila 8)
    data_start_row = 8

    # Intentar detectar automáticamente
    for i in range(1, 20):
        row = sheet[i]
        if row[0].value and isinstance(row[0].value, str):
            if 'Name' in row[0].value or 'PARTIDA' in row[0].value.upper():
                data_start_row = i + 1
                break

    print(f'  [INFO] Leyendo datos desde fila {data_start_row}')

    for row in sheet.iter_rows(min_row=data_start_row, values_only=True):
        if row[0] and isinstance(row[0], str):
            nombre_completo = row[0].strip()
            nombre_limpio = limpiar_nombre(nombre_completo)

            # Buscar valor en columna C (Balance) o siguientes
            valor = None
            for cell in row[1:6]:  # Revisar columnas B-F
                if isinstance(cell, (int, float)) and cell != 0:
                    valor = abs(float(cell))
                    break

            if valor is not None and valor != 0:
                excel_dict[nombre_limpio] = valor

    print(f'  [INFO] Partidas procesadas: {len(excel_dict)}')
    return excel_dict

def comparar(excel_dict, sistema_dict, verbose=True):
    """Compara ambos diccionarios y retorna lista de comparaciones"""
    todas = sorted(set(list(excel_dict.keys()) + list(sistema_dict.keys())))

    comparaciones = []
    for partida in todas:
        excel_val = excel_dict.get(partida, 0)
        sistema_info = sistema_dict.get(partida, {'valor': 0, 'is_header': False})
        sistema_val = sistema_info['valor'] if isinstance(sistema_info, dict) else sistema_info
        is_header = sistema_info.get('is_header', False) if isinstance(sistema_info, dict) else False

        diff = sistema_val - excel_val
        match = abs(diff) < 0.01

        # Filtrar totales generales del Excel
        skip_keywords = ['Ganancia y Perdida', 'Ingreso', 'Gasto']
        if any(kw == partida for kw in skip_keywords):
            continue

        comparaciones.append({
            'partida': partida,
            'excel': excel_val,
            'sistema': sistema_val,
            'diff': diff,
            'match': match,
            'is_header': is_header,
            'en_excel': partida in excel_dict,
            'en_sistema': partida in sistema_dict
        })

    return comparaciones

def imprimir_reporte(comparaciones, verbose=True):
    """Imprime reporte de comparación"""
    print('\n' + '='*100)
    print(' '*35 + 'COMPARACIÓN PARTIDA POR PARTIDA')
    print('='*100)

    if verbose:
        print(f'\n{"#":<4} {"Partida":<60} {"Excel":>15} {"Sistema":>15} {"Diff":>12} {"Status":<8}')
        print('-'*100)

        # Ordenar por diferencia absoluta
        comparaciones_ordenadas = sorted(comparaciones, key=lambda x: abs(x['diff']), reverse=True)

        for i, c in enumerate(comparaciones_ordenadas, 1):
            status = ' [OK]  ' if c['match'] else ' [ERROR]'
            tipo = '[H]' if c['is_header'] else '   '
            print(f'{i:<4} {tipo} {c["partida"]:<57} ${c["excel"]:>13,.2f} ${c["sistema"]:>13,.2f} ${c["diff"]:>10,.2f} {status}')

    # Resumen
    total = len(comparaciones)
    ok = sum(1 for c in comparaciones if c['match'])
    error = total - ok

    solo_en_excel = sum(1 for c in comparaciones if c['en_excel'] and not c['en_sistema'] and c['excel'] != 0)
    solo_en_sistema = sum(1 for c in comparaciones if c['en_sistema'] and not c['en_excel'] and c['sistema'] != 0)

    print('\n' + '='*100)
    print(' '*40 + 'RESUMEN')
    print('='*100)

    print(f'\nTotal partidas comparadas: {total}')
    if total > 0:
        print(f'  [OK] Coinciden: {ok} ({ok/total*100:.1f}%)')
        print(f'  [X]  Difieren: {error} ({error/total*100:.1f}%)')
    else:
        print('  [WARN] No hay partidas para comparar')

    if solo_en_excel > 0 or solo_en_sistema > 0:
        print(f'\nPartidas solo en Excel: {solo_en_excel}')
        print(f'Partidas solo en Sistema: {solo_en_sistema}')

    # Totales
    suma_excel = sum(c['excel'] for c in comparaciones)
    suma_sistema = sum(c['sistema'] for c in comparaciones)

    print(f'\nSuma total Excel: ${suma_excel:,.2f}')
    print(f'Suma total Sistema: ${suma_sistema:,.2f}')
    print(f'Diferencia total: ${suma_sistema - suma_excel:,.2f}')

    # Desglose por tipo
    ingresos_excel = sum(c['excel'] for c in comparaciones
                        if 'ingreso' in c['partida'].lower() or 'ganancia' in c['partida'].lower()
                        or 'sobrante' in c['partida'].lower())
    ingresos_sistema = sum(c['sistema'] for c in comparaciones
                          if 'ingreso' in c['partida'].lower() or 'ganancia' in c['partida'].lower()
                          or 'sobrante' in c['partida'].lower())

    costos_excel = sum(c['excel'] for c in comparaciones if 'costo' in c['partida'].lower())
    costos_sistema = sum(c['sistema'] for c in comparaciones if 'costo' in c['partida'].lower())

    gastos_excel = sum(c['excel'] for c in comparaciones
                      if 'gasto' in c['partida'].lower() or 'faltante' in c['partida'].lower()
                      or 'pérdida' in c['partida'].lower() or 'perdida' in c['partida'].lower())
    gastos_sistema = sum(c['sistema'] for c in comparaciones
                        if 'gasto' in c['partida'].lower() or 'faltante' in c['partida'].lower()
                        or 'pérdida' in c['partida'].lower() or 'perdida' in c['partida'].lower())

    if ingresos_excel > 0 or costos_excel > 0 or gastos_excel > 0:
        print('\n[DESGLOSE POR TIPO]')
        if ingresos_excel > 0 or ingresos_sistema > 0:
            print(f'  Ingresos  - Excel: ${ingresos_excel:>12,.2f}  Sistema: ${ingresos_sistema:>12,.2f}  Diff: ${ingresos_sistema-ingresos_excel:>10,.2f}')
        if costos_excel > 0 or costos_sistema > 0:
            print(f'  Costos    - Excel: ${costos_excel:>12,.2f}  Sistema: ${costos_sistema:>12,.2f}  Diff: ${costos_sistema-costos_excel:>10,.2f}')
        if gastos_excel > 0 or gastos_sistema > 0:
            print(f'  Gastos    - Excel: ${gastos_excel:>12,.2f}  Sistema: ${gastos_sistema:>12,.2f}  Diff: ${gastos_sistema-gastos_excel:>10,.2f}')

    # Mayores diferencias
    if error > 0 and verbose:
        print(f'\n[MAYORES DIFERENCIAS - TOP 10]')
        print('-'*100)
        difs_ordenadas = sorted([c for c in comparaciones if not c['match']],
                               key=lambda x: abs(x['diff']), reverse=True)

        for c in difs_ordenadas[:10]:
            print(f'{c["partida"]:<65} Excel: ${c["excel"]:>12,.2f}  Sistema: ${c["sistema"]:>12,.2f}  Diff: ${c["diff"]:>12,.2f}')

    print('\n' + '='*100)
    if error == 0 and total > 0:
        print(' '*35 + '[SUCCESS] TODOS LOS VALORES COINCIDEN!')
    elif total == 0:
        print(' '*30 + '[ERROR] NO SE ENCONTRARON PARTIDAS PARA COMPARAR')
    else:
        print(' '*30 + f'[ALERT] {error} PARTIDAS CON DIFERENCIAS')
    print('='*100)

    return error == 0

def main():
    parser = argparse.ArgumentParser(
        description='Validación EERR: Excel vs Sistema',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Ejemplos:
  python validar_eerr.py --excel "C:/Desktop/EERR RODEO ENERO.xlsx" --unit Rodeo --year 2026 --month ENE
  python validar_eerr.py --excel "EERR TERRACOTA.xlsx" --unit Terracota
  python validar_eerr.py --excel "EERR ALTAMIRA.xlsx" --unit Altamira --verbose
        '''
    )

    parser.add_argument('--excel', required=True,
                       help='Ruta al archivo Excel de EERR')
    parser.add_argument('--unit', required=True,
                       help='Nombre de la unidad (Rodeo, Terracota, Altamira, etc.)')
    parser.add_argument('--year', type=int, default=2026,
                       help='Año a validar (default: 2026)')
    parser.add_argument('--month', default='ENE',
                       help='Mes a validar (default: ENE)')
    parser.add_argument('--server', default='http://localhost:5000',
                       help='URL del servidor Flask (default: http://localhost:5000)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Mostrar todas las partidas (default: solo resumen)')
    parser.add_argument('--save', '-s', metavar='ARCHIVO',
                       help='Guardar reporte en archivo JSON')

    args = parser.parse_args()

    # Header
    print('='*100)
    print(' '*30 + 'VALIDACIÓN EERR: EXCEL vs SISTEMA')
    print(f' '*25 + f'{args.unit} - {args.month} {args.year}')
    print('='*100)
    print(f'\nFecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'Excel: {args.excel}')
    print(f'Unidad: {args.unit}')
    print(f'Periodo: {args.month} {args.year}')
    print(f'Servidor: {args.server}')

    # 1. Cargar Sistema
    sistema_data = cargar_sistema(args.unit, args.year, args.server)
    if sistema_data is None:
        print('\n[ERROR] No se pudieron cargar datos del sistema')
        sys.exit(1)

    # Procesar datos del sistema
    sistema_dict = {}
    for row in sistema_data.get('rows', []):
        partida = row.get('partida', '')
        is_header = row.get('is_header', False)
        meses = row.get('meses', [])

        if meses and len(meses) > 0:
            # Buscar el mes correcto
            mes_data = None
            for mes in meses:
                if mes.get('month') == args.month:
                    mes_data = mes
                    break

            if mes_data and 'ejecutado' in mes_data:
                valor = mes_data['ejecutado'].get('valor', 0)
                sistema_dict[partida] = {
                    'valor': valor,
                    'is_header': is_header
                }

    print(f'  [INFO] Partidas del sistema: {len(sistema_dict)}')

    # 2. Cargar Excel
    sheet = cargar_excel(args.excel)
    if sheet is None:
        print('\n[ERROR] No se pudo cargar el Excel')
        sys.exit(1)

    excel_dict = parsear_excel(sheet)

    if len(excel_dict) == 0:
        print('\n[ERROR] No se encontraron partidas en el Excel')
        sys.exit(1)

    # 3. Comparar
    comparaciones = comparar(excel_dict, sistema_dict, verbose=args.verbose)

    # 4. Imprimir reporte
    success = imprimir_reporte(comparaciones, verbose=args.verbose)

    # 5. Guardar a archivo si se solicitó
    if args.save:
        try:
            with open(args.save, 'w', encoding='utf-8') as f:
                json.dump({
                    'metadata': {
                        'fecha': datetime.now().isoformat(),
                        'excel': args.excel,
                        'unit': args.unit,
                        'year': args.year,
                        'month': args.month,
                        'server': args.server
                    },
                    'resumen': {
                        'total': len(comparaciones),
                        'coinciden': sum(1 for c in comparaciones if c['match']),
                        'difieren': sum(1 for c in comparaciones if not c['match']),
                        'suma_excel': sum(c['excel'] for c in comparaciones),
                        'suma_sistema': sum(c['sistema'] for c in comparaciones)
                    },
                    'comparaciones': comparaciones
                }, f, indent=2, ensure_ascii=False)
            print(f'\n[INFO] Reporte guardado en: {args.save}')
        except Exception as e:
            print(f'\n[ERROR] No se pudo guardar el reporte: {e}')

    # Exit code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
