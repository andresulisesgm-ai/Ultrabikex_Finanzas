================================================================================
VALIDADOR EERR - GUIA DE USO
================================================================================

PROPOSITO
---------
validador_eerr.py es un script de validacion automatica que compara los valores
calculados por el sistema contra valores esperados extraidos del Excel de
referencia "2 EEFF ULTRAX Rodeo.xlsx".

Funciona como test fixture: cada vez que modificas new_eerr_structure.py o la
logica de calculo, corres el validador y ves inmediatamente que mejoro y que
sigue roto.


USO
---
  python validador_eerr.py

  Output:
    - PASS: partidas que coinciden (tolerancia ±0.10)
    - FAIL: partidas que existen pero tienen valor incorrecto
    - MISSING: partidas que no existen en EERR_STRUCTURE
    - Resumen final con conteo y diagnostico


ESTADO ACTUAL (2026-06-06)
---------------------------
Resultados de la primera ejecucion:

  33 PASS    - Partidas individuales que cuadran
  12 FAIL    - Subtotales y totales con valores incorrectos
  11 MISSING - Partidas faltantes en EERR_STRUCTURE

PROBLEMAS DETECTADOS:

1. MISSING (11 partidas):
   - Costo de venta por mercancia         (20,670.85)
   - Ingresos por venta de mercancia      (47,933.03)
   - Gastos de asistencia outsorsing      (965.72)
   - Gastos de sueldos y salarios directivos
   - Gastos de horas extras, feriados y bono nocturno
   - Gastos de complemento de sueldos y salarios directivos
   - Gastos de Bono de alimentacion directivos
   - Gastos de bono de guarderia
   - Gastos de uniformes y dotacion al personal
   - Gastos de donaciones y obsequios al personal
   - Gastos de capacitacion al personal

2. FAIL - Totales principales (todos en 0.00):
   - Total Ingresos                       expected: 48,122.01
   - Total Costo de Ventas                expected: 20,670.85
   - Utilidad Bruta                       expected: 27,451.16
   - Total Gastos Operacionales           expected: 12,855.64
   - Utilidad Neta                        expected: -3,513.65

3. FAIL - Subtotales (valores incorrectos):
   - Subtotal Gastos de Administracion    sistema: 6,215.48  expected: 7,181.20  (falta 965.72)
   - Subtotal Gastos de RRHH              sistema: 0.00      expected: 2,123.88  (TODO faltante!)
   - Subtotal Gastos de Comercializacion  sistema: 0.00      expected: 3,337.60  (TODO faltante!)
   - Subtotal Gastos de Mercadeo          sistema: 129.32    expected: 212.96    (falta 83.64)


ANALISIS DE CAUSAS
------------------

Los totales estan en 0.00 porque la logica de calculo tiene bugs:

  Total Ingresos = suma de partidas con codigo 4.x
    -> "Ingresos por venta de mercancia" (47,933.03) esta MISSING
    -> Por eso el total da 0 en lugar de 48,122.01

  Total Costo de Ventas = suma de partidas con codigo 5.x
    -> "Costo de venta por mercancia" (20,670.85) esta MISSING
    -> Por eso el total da 0 en lugar de 20,670.85

  Subtotal Gastos de RRHH = 0.00
    -> La estructura actual solo tiene agrupadores RRHH con is_header=True
    -> No tiene las partidas hijas individuales
    -> La logica de calcular_subtotales_jerarquicos() suma desde el header
       hasta el siguiente header, y como NO hay partidas entre los headers
       RRHH, el subtotal da 0

  Subtotal Gastos de Comercializacion = 0.00
    -> Las partidas de comisiones (834.62 + 2,502.98 = 3,337.60) estan
       en la BD y el validador las encuentra individualmente (PASS)
    -> Pero NO estan en EERR_STRUCTURE dentro del bloque de Comercializacion
    -> Estan fuera, entre headers de utilidad
    -> Por eso el subtotal de Comercializacion da 0


PLAN DE CORRECCION
------------------

FASE 1 - Corregir EERR_STRUCTURE (new_eerr_structure.py)

  1.1. Cambiar nombres exactos de partidas principales:
       - "Ingresos por venta de mercancía" (actualmente mal escrito)
       - "Costo de venta por mercancía" (actualmente mal escrito)

  1.2. Agregar "Gastos de asistencia outsorsing" en bloque Administracion

  1.3. Expandir bloque RRHH con todas las partidas faltantes:
       - Sueldos y salarios directivos
       - Horas extras, feriados y bono nocturno
       - Complementos directivos
       - Bonos de alimentacion directivos
       - Bono de guarderia
       - Uniformes y dotacion
       - Donaciones y obsequios
       - Capacitacion

  1.4. Decidir sobre comisiones:
       Opcion A: Dejarlas fuera de Comercializacion (diseño actual)
                 -> Actualizar EXPECTED para reflejar esto

       Opcion B: Moverlas dentro de Comercializacion
                 -> Cambiar estructura y logica de calculo

FASE 2 - Validar cambios

  Despues de cada modificacion:
    python validador_eerr.py

  Objetivo:
    56 PASS / 0 FAIL / 0 MISSING


FASE 3 - Actualizar documentacion

  - Actualizar system_map.json con la estructura final
  - Documentar decisiones sobre comisiones
  - Marcar diagnostico_eerr.txt como RESUELTO


WORKFLOW RECOMENDADO
--------------------

1. Hacer un cambio atomico en new_eerr_structure.py
   Ejemplo: agregar "Ingresos por venta de mercancia"

2. Correr validador:
   python validador_eerr.py

3. Ver resultado:
   - Si mejoro (MISSING baja, PASS sube): commit
   - Si empeoro: revertir y probar otro enfoque

4. Repetir hasta llegar a 100% PASS

5. Regenerar EERR para Rodeo ENE-FEB 2026 y comparar visualmente con Excel


NOTAS TECNICAS
--------------

El validador NO levanta Flask. Lee directamente de la BD usando la misma
logica que app.py:

  - Importa EERR_STRUCTURE desde new_eerr_structure.py
  - Lee financials desde data/ultrax.db
  - Replica calcular_subtotales_jerarquicos() y calcular_totales_especiales()
  - Compara resultado contra EXPECTED hardcodeado

Esto hace que el validador sea:
  - Rapido (sin overhead de Flask)
  - Reproducible (mismo input = mismo output)
  - Independiente (puede correrse en CI/CD)


VALORES ESPERADOS
-----------------

Los valores en EXPECTED fueron extraidos manualmente del Excel
"2 EEFF ULTRAX Rodeo.xlsx", sheet "N EERR RODEO", columna ENE.

Si el Excel cambia, actualizar EXPECTED en validador_eerr.py lineas 21-73.


================================================================================
FIN DE LA GUIA
================================================================================
