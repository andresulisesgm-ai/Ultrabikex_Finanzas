#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Funciones para calcular subtotales dinámicos en EERR
Estas funciones se integran en app.py para /api/eerr/completo
"""

def calcular_subtotales_jerarquicos(eerr_structure, by_partida, month, ing_p, cos_p, gas_p, groups, grouped_partidas):
    """
    Calcula todos los subtotales jerárquicos para un mes dado.

    Para cada header (is_header=True):
    - Suma todas las partidas NO-header desde este header hasta el siguiente header

    Returns:
        dict: {nombre_header: valor_calculado}
    """
    subtotales = {}
    all_partidas = ing_p | cos_p | gas_p

    for i, item in enumerate(eerr_structure):
        partida_name = item[0]
        is_header = item[1]

        if not is_header:
            continue  # Solo procesamos headers

        # Acumular partidas hijas hasta el siguiente header
        total = 0
        j = i + 1

        while j < len(eerr_structure):
            child_item = eerr_structure[j]
            child_name = child_item[0]
            child_is_header = child_item[1]

            # Parar cuando encontramos otro header
            if child_is_header:
                break

            # Buscar partidas que coincidan con este nombre
            if child_name in groups:
                # Es un grupo: tomar todas las partidas del grupo
                matching = groups[child_name]
            else:
                # Buscar partida individual
                matching = [p for p in all_partidas
                           if p.lower() == child_name.lower()
                           and p not in grouped_partidas]

            # Sumar valores de las partidas encontradas
            for p in matching:
                total += by_partida.get(p, {}).get(month, 0)

            j += 1

        subtotales[partida_name] = total

    return subtotales


def calcular_totales_especiales(subtotales, by_partida, month, ing_p, cos_p, gas_p):
    """
    Calcula totales especiales con lógicas específicas.

    Args:
        subtotales: dict con subtotales ya calculados
        by_partida: datos de partidas por mes
        month: mes a calcular
        ing_p, cos_p, gas_p: sets de partidas clasificadas

    Returns:
        dict: {nombre_total: valor_calculado}
    """
    totales = {}

    # 1. Total Ingresos = suma de TODAS las partidas de ingresos (4.xx)
    totales['Total Ingresos'] = sum(by_partida.get(p, {}).get(month, 0) for p in ing_p)

    # 2. Total Costo de Ventas = suma de TODAS las partidas de costos (5.xx)
    totales['Total Costo de Ventas'] = sum(by_partida.get(p, {}).get(month, 0) for p in cos_p)

    # 3. Utilidad Bruta = Total Ingresos - Total Costo de Ventas
    # (Nota: en este punto "Total Ingresos" incluye operativos + no operativos)
    # Si necesitas separar, deberías filtrar por código 4.01.xx vs 4.02.xx
    totales['Utilidad Bruta'] = totales['Total Ingresos'] - totales['Total Costo de Ventas']

    # 4. Total Gastos Operacionales = suma de subtotales de gastos operativos
    gastos_operacionales = 0
    for nombre_subtotal in ['Subtotal Gastos de Administración',
                            'Subtotal Gastos de Recursos Humanos',
                            'Subtotal Gastos de Comercialización y Logistica',
                            'Subtotal Gastos de Mercadeo',
                            'Subtotal Gastos de Tecnología, Innovación e Investigación']:
        gastos_operacionales += subtotales.get(nombre_subtotal, 0)

    totales['Total Gastos Operacionales'] = gastos_operacionales

    # 5. Utilidad antes de Comisiones = Utilidad Bruta - Total Gastos Operacionales
    totales['Utilidad antes de Comisiones por Ventas'] = (
        totales['Utilidad Bruta'] - totales['Total Gastos Operacionales']
    )

    # 6. Suma de comisiones (están bajo su propio header)
    comisiones_total = 0
    for nombre_comision in ['Gastos de comisiones por ventas',
                            'Gastos de comisiones por ventas taller']:
        comisiones_total += subtotales.get(nombre_comision, 0)

    # 7. Utilidad después de Comisiones = antes - comisiones
    totales['Utilidad después de Comisiones por Ventas'] = (
        totales['Utilidad antes de Comisiones por Ventas'] - comisiones_total
    )

    # 8. Otros Gastos no Operacionales (subtotal ya calculado)
    totales['Otros Gastos no Operacionales'] = subtotales.get('Otros Gastos no Operacionales', 0)

    # 9. Otros Ingresos no Operacionales (subtotal ya calculado)
    totales['Otros Ingresos no Operacionales'] = subtotales.get('Otros Ingresos no Operacionales', 0)

    # 10. Utilidad Neta = Utilidad después de Comisiones - Otros Gastos + Otros Ingresos
    totales['Utilidad Neta'] = (
        totales['Utilidad después de Comisiones por Ventas'] -
        totales['Otros Gastos no Operacionales'] +
        totales['Otros Ingresos no Operacionales']
    )

    return totales


def obtener_valor_partida_o_subtotal(partida_name, is_header, subtotales_combinados,
                                     by_partida, month, ing_p, cos_p, gas_p,
                                     groups, grouped_partidas):
    """
    Obtiene el valor de una partida, ya sea:
    - Un subtotal pre-calculado (si es header)
    - Una partida individual (si no es header)

    Args:
        partida_name: nombre de la partida/header
        is_header: si es header o no
        subtotales_combinados: dict con todos los subtotales y totales calculados
        by_partida: datos de partidas
        month: mes
        ing_p, cos_p, gas_p: clasificación de partidas
        groups: grupos de mapping_groups
        grouped_partidas: partidas ya agrupadas

    Returns:
        float: valor calculado
    """
    if is_header:
        # Es un header: usar valor pre-calculado
        return subtotales_combinados.get(partida_name, 0)
    else:
        # Es una partida individual: buscar valor directo
        all_partidas = ing_p | cos_p | gas_p

        if partida_name in groups:
            # Es un grupo: tomar todas las partidas del grupo
            matching = groups[partida_name]
        else:
            # Buscar partida individual
            matching = [p for p in all_partidas
                       if p.lower() == partida_name.lower()
                       and p not in grouped_partidas]

        # Sumar valores
        return sum(by_partida.get(p, {}).get(month, 0) for p in matching)
