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
from engine import esf_engine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('esf_integrity')

TOLERANCE = 0.01


def get_value(rows, partida, quarter):
    for r in rows:
        if r['partida'] == partida:
            return r['quarters'].get(quarter, 0.0)
    return 0.0


def validate_esf_integrity(year, unit, esf_data):
    discrepancies = []
    rows = esf_data.get('rows', [])

    if not rows:
        discrepancies.append("No hay datos en el output de esf_engine.")
        return False, discrepancies

    quarters_con_datos = []
    for q in [1, 2, 3, 4]:
        total_activos = get_value(rows, 'TOTAL ACTIVOS', q)
        if total_activos != 0.0:
            quarters_con_datos.append(q)

    if not quarters_con_datos:
        discrepancies.append("Todos los quarters tienen TOTAL ACTIVOS = 0. Sin datos cargados.")
        return False, discrepancies

    for q in quarters_con_datos:
        label = f"Q{q}"

        total_activos    = get_value(rows, 'TOTAL ACTIVOS', q)
        activos_corr     = get_value(rows, 'ACTIVOS CORRIENTES', q)
        activos_nocorr   = get_value(rows, 'ACTIVOS NO CORRIENTES', q)
        total_pasivos    = get_value(rows, 'TOTAL PASIVOS', q)
        pasivos_corr     = get_value(rows, 'PASIVOS CORRIENTES', q)
        pasivos_nocorr   = get_value(rows, 'PASIVOS NO CORRIENTES', q)
        patrimonio       = get_value(rows, 'PATRIMONIO', q)
        total_pas_pat    = get_value(rows, 'TOTAL PASIVOS Y PATRIMONIO', q)

        # Activos Corrientes + No Corrientes = Total Activos
        activos_calc = round(activos_corr + activos_nocorr, 2)
        if abs(activos_calc - total_activos) > TOLERANCE:
            discrepancies.append(
                f"{label} | Total Activos: AC({activos_corr}) + ANC({activos_nocorr}) = {activos_calc} "
                f"vs TOTAL ACTIVOS={total_activos}"
            )

        # Pasivos Corrientes + No Corrientes = Total Pasivos
        pasivos_calc = round(pasivos_corr + pasivos_nocorr, 2)
        if abs(pasivos_calc - total_pasivos) > TOLERANCE:
            discrepancies.append(
                f"{label} | Total Pasivos: PC({pasivos_corr}) + PNC({pasivos_nocorr}) = {pasivos_calc} "
                f"vs TOTAL PASIVOS={total_pasivos}"
            )

        # Total Pasivos + Patrimonio = Total Pasivos y Patrimonio
        pas_pat_calc = round(total_pasivos + patrimonio, 2)
        if abs(pas_pat_calc - total_pas_pat) > TOLERANCE:
            discrepancies.append(
                f"{label} | Pasivos+Patrimonio: {total_pasivos} + {patrimonio} = {pas_pat_calc} "
                f"vs TOTAL PASIVOS Y PATRIMONIO={total_pas_pat}"
            )

        # Cuadre fundamental: TOTAL ACTIVOS = TOTAL PASIVOS Y PATRIMONIO
        cuadre = round(total_activos - total_pas_pat, 2)
        if abs(cuadre) > TOLERANCE:
            discrepancies.append(
                f"{label} | CUADRE ROTO: TOTAL ACTIVOS={total_activos} vs "
                f"TOTAL PASIVOS Y PATRIMONIO={total_pas_pat} | diferencia={cuadre}"
            )

    return len(discrepancies) == 0, discrepancies


def run_suite():
    logger.info("=== INICIANDO VALIDACIÓN DE INTEGRIDAD PARA ESF ===")

    year = '2026'
    unit = 'Rodeo'

    logger.info(f"Paso 1: Ejecutando esf_engine para {unit} {year}...")
    try:
        from app import app
        with app.app_context():
            esf_data = esf_engine(year, unit)
        logger.info("esf_engine ejecutado exitosamente.")
    except Exception as e:
        logger.error(f"Error crítico al ejecutar esf_engine: {str(e)}")
        sys.exit(1)

    logger.info("Paso 2: Validando integridad del ESF...")
    success, discrepancies = validate_esf_integrity(year, unit, esf_data)

    print("\n" + "="*80)
    print(f"REPORTE DE INTEGRIDAD ESF - {unit} {year}")
    print("="*80)

    if success:
        rows = esf_data.get('rows', [])
        quarters_con_datos = [q for q in [1, 2, 3, 4] if get_value(rows, 'TOTAL ACTIVOS', q) != 0.0]
        print("\n[PASS] Integridad del ESF garantizada.")
        print(f" - Quarters validados: {quarters_con_datos}")
        print(" - Activos Corrientes + No Corrientes = Total Activos: Verificado.")
        print(" - Pasivos Corrientes + No Corrientes = Total Pasivos: Verificado.")
        print(" - Cuadre TOTAL ACTIVOS = TOTAL PASIVOS Y PATRIMONIO: Verificado.")
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
