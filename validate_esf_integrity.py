#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suite de validación de integridad para el ESF.
Verifica coherencia interna de subtotales y el cuadre fundamental
TOTAL ACTIVOS = TOTAL PASIVOS + TOTAL PATRIMONIO.
Uso:
    python validate_esf_integrity.py
"""
import sys
import logging
from app import app, compute_esf, get_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('esf_integrity')

TOLERANCE = 0.01

def validate_esf_integrity(year, unit, result_quarters, quarters_available):
    discrepancies = []

    if not quarters_available:
        discrepancies.append("No hay datos cargados en esf_data para el período solicitado.")
        return False, discrepancies

    for q in quarters_available:
        data = result_quarters.get(q, {})
        totales = data.get('totales', {})
        partidas = data.get('partidas', {})

        label = f"Q{q}"

        # --- Subtotal: Efectivo y Equivalentes ---
        ef_parts = ['Efectivo en caja', 'Efectivo en bancos nacional',
                    'Efectivo en bancos exterior', 'Efectivo en criptomonedas']
        ef_sum = sum(partidas.get(p, 0) for p in ef_parts)
        ef_total = totales.get('Total Efectivo y Equivalentes', 0)
        if abs(ef_sum - ef_total) > TOLERANCE:
            discrepancies.append(f"{label} | Efectivo: suma partidas={ef_sum:.2f} vs total={ef_total:.2f}")

        # --- Subtotal: Cuentas por Cobrar ---
        cxc_parts = ['Cuentas por cobrar clientes', 'Cuentas por cobrar empleados',
                     'Cuentas por cobrar accionistas', 'Otras cuentas por cobrar',
                     'Provisión para cuentas incobrables']
        cxc_sum = sum(partidas.get(p, 0) for p in cxc_parts)
        cxc_total = totales.get('Total Cuentas por Cobrar (neto)', 0)
        if abs(cxc_sum - cxc_total) > TOLERANCE:
            discrepancies.append(f"{label} | CxC: suma partidas={cxc_sum:.2f} vs total={cxc_total:.2f}")

        # --- Subtotal: Inventarios ---
        inv_parts = ['Inventario de mercancías', 'Inventario de materia prima',
                     'Inventario de suministros']
        inv_sum = sum(partidas.get(p, 0) for p in inv_parts)
        inv_total = totales.get('Total Inventarios', 0)
        if abs(inv_sum - inv_total) > TOLERANCE:
            discrepancies.append(f"{label} | Inventarios: suma partidas={inv_sum:.2f} vs total={inv_total:.2f}")

        # --- Subtotal: Otros Activos Corrientes ---
        oac_parts = ['Gastos pagados por anticipado', 'Seguros pagados por anticipado',
                     'IVA crédito fiscal', 'Retenciones de IVA por recuperar',
                     'Anticipos a proveedores']
        oac_sum = sum(partidas.get(p, 0) for p in oac_parts)
        oac_total = totales.get('Total Otros Activos Corrientes', 0)
        if abs(oac_sum - oac_total) > TOLERANCE:
            discrepancies.append(f"{label} | Otros AC: suma partidas={oac_sum:.2f} vs total={oac_total:.2f}")

        # --- Activos Corrientes ---
        ac_calc = ef_total + cxc_total + inv_total + oac_total
        ac_total = totales.get('ACTIVOS CORRIENTES', 0)
        if abs(ac_calc - ac_total) > TOLERANCE:
            discrepancies.append(f"{label} | Activos Corrientes: calculado={ac_calc:.2f} vs total={ac_total:.2f}")

        # --- Total Activos ---
        anc_total = totales.get('Total Activos No Corrientes', 0)
        activos_calc = ac_total + anc_total
        activos_total = totales.get('TOTAL ACTIVOS', 0)
        if abs(activos_calc - activos_total) > TOLERANCE:
            discrepancies.append(f"{label} | Total Activos: calculado={activos_calc:.2f} vs total={activos_total:.2f}")

        # --- Subtotal: Cuentas por Pagar ---
        cxp_parts = ['Cuentas por pagar proveedores', 'Cuentas por pagar accionistas',
                     'Otras cuentas por pagar']
        cxp_sum = sum(partidas.get(p, 0) for p in cxp_parts)
        cxp_total = totales.get('Total Cuentas por Pagar', 0)
        if abs(cxp_sum - cxp_total) > TOLERANCE:
            discrepancies.append(f"{label} | CxP: suma partidas={cxp_sum:.2f} vs total={cxp_total:.2f}")

        # --- Subtotal: Pasivos Laborales ---
        lab_parts = ['Pasivos laborales corrientes', 'Prestaciones sociales por pagar']
        lab_sum = sum(partidas.get(p, 0) for p in lab_parts)
        lab_total = totales.get('Total Pasivos Laborales Corrientes', 0)
        if abs(lab_sum - lab_total) > TOLERANCE:
            discrepancies.append(f"{label} | Pasivos Laborales: suma partidas={lab_sum:.2f} vs total={lab_total:.2f}")

        # --- Subtotal: Otros Pasivos Corrientes ---
        opc_parts = ['IVA débito fiscal', 'Retenciones de IVA por enterar', 'ISLR por pagar',
                     'Aportes patronales por pagar', 'Préstamos bancarios corto plazo',
                     'Porción corriente préstamos LP', 'Anticipos de clientes', 'Ingresos diferidos']
        opc_sum = sum(partidas.get(p, 0) for p in opc_parts)
        opc_total = totales.get('Total Otros Pasivos Corrientes', 0)
        if abs(opc_sum - opc_total) > TOLERANCE:
            discrepancies.append(f"{label} | Otros PC: suma partidas={opc_sum:.2f} vs total={opc_total:.2f}")

        # --- Pasivos Corrientes ---
        pc_calc = cxp_total + lab_total + opc_total
        pc_total = totales.get('TOTAL PASIVOS CORRIENTES', 0)
        if abs(pc_calc - pc_total) > TOLERANCE:
            discrepancies.append(f"{label} | Pasivos Corrientes: calculado={pc_calc:.2f} vs total={pc_total:.2f}")

        # --- Total Pasivos ---
        pnc_total = totales.get('TOTAL PASIVOS NO CORRIENTES', 0)
        pasivos_calc = pc_total + pnc_total
        pasivos_total = totales.get('TOTAL PASIVOS', 0)
        if abs(pasivos_calc - pasivos_total) > TOLERANCE:
            discrepancies.append(f"{label} | Total Pasivos: calculado={pasivos_calc:.2f} vs total={pasivos_total:.2f}")

        # --- Cuadre fundamental: ACTIVOS = PASIVOS + PATRIMONIO ---
        pat_total = totales.get('TOTAL PATRIMONIO', 0)
        pas_pat = totales.get('TOTAL PASIVOS Y PATRIMONIO', 0)
        cuadre = activos_total - pas_pat
        if abs(cuadre) > TOLERANCE:
            discrepancies.append(f"{label} | CUADRE ROTO: Activos={activos_total:.2f} vs Pasivos+Patrimonio={pas_pat:.2f} | diferencia={cuadre:.2f}")

        pasivos_pat_calc = pasivos_total + pat_total
        if abs(pasivos_pat_calc - pas_pat) > TOLERANCE:
            discrepancies.append(f"{label} | Total Pasivos+Patrimonio: calculado={pasivos_pat_calc:.2f} vs total={pas_pat:.2f}")

    return len(discrepancies) == 0, discrepancies


def run_suite():
    logger.info("=== INICIANDO VALIDACIÓN DE INTEGRIDAD PARA ESF ===")
    with app.app_context():
        db = get_db()
        year = '2026'
        unit = 'Rodeo'

        logger.info(f"Paso 1: Ejecutando compute_esf para {unit} {year}...")
        try:
            result_quarters, quarters_available = compute_esf(db, year, unit)
            logger.info(f"compute_esf ejecutado. Quarters disponibles: {quarters_available}")
        except Exception as e:
            logger.error(f"Error crítico al ejecutar compute_esf: {str(e)}")
            sys.exit(1)

        logger.info("Paso 2: Validando integridad del ESF...")
        success, discrepancies = validate_esf_integrity(year, unit, result_quarters, quarters_available)

        print("\n" + "="*80)
        print(f"REPORTE DE INTEGRIDAD ESF - {unit} {year}")
        print("="*80)

        if success:
            print("\n[PASS] Integridad del ESF garantizada.")
            print(f" - Quarters validados: {quarters_available}")
            print(" - Subtotales internos: Verificados.")
            print(" - Cuadre ACTIVOS = PASIVOS + PATRIMONIO: Verificado.")
            print("="*80)
            return True
        else:
            print(f"\n[FAIL] Se detectaron {len(discrepancies)} discrepancias:")
            for idx, d in enumerate(discrepancies, 1):
                print(f"  {idx}. {d}")
            print("\n[WARNING] Resolver las diferencias antes de continuar.")
            print("="*80)
            return False


if __name__ == '__main__':
    success = run_suite()
    sys.exit(0 if success else 1)
