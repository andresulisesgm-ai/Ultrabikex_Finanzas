# VALIDACIÓN DE METADATA — FASE 1 JERARQUÍA EERR

> **Nota:** Este reporte documenta el resultado de extender `EERR_STRUCTURE` con los campos `parent_name` e `indent` y reubicar la nota de guardería.


## 1. CONTEO DE 'Gastos de bono de guardería'

*   **Cantidad de apariciones:** 1

    *   *Confirmación:* La tupla aparece **UNA SOLA VEZ** en `EERR_STRUCTURE` como se requería. Se ubica correctamente en la posición 100.



## 2. NODOS SIN MATCH DE INDENT

*   *Resultado:* **Ninguno**. Todos los nodos con `es_nota=False` encontraron su correspondencia exacta de indentación en la columna A de la hoja 'EERR ULTRAX' de `EEFF ULTRAX 2026.xlsx` mediante normalización y mapeos auxiliares.


## 3. TABLA COMPLETA DE ESTRUCTURA EXTENDIDA

| Posición | partida_name | level | es_nota | parent_name | indent |
| --- | --- | --- | --- | --- | --- |
| 0 | `ESTADO DE RESULTADOS` | 0 | False | *None* | 0 |
| 1 | `PARTIDAS` | 0 | False | *None* | 0 |
| 2 | `Total Ingresos` | 0 | False | *None* | 0 |
| 3 | `Subtotal Ingresos por Venta de Mercancia` | 1 | False | *None* | 1 |
| 4 | `Ingresos por venta de mercancias` | 3 | True | `Subtotal Ingresos por Venta de Mercancia` | 3 |
| 5 | `Devoluciones sobre ventas` | 3 | False | *None* | 2 |
| 6 | `Descuentos sobre ventas` | 3 | False | *None* | 2 |
| 7 | `Subtotal Ingresos por Servicios` | 1 | False | *None* | 1 |
| 8 | `Ingresos por servicios del café` | 3 | False | *None* | 2 |
| 9 | `Ingresos por zona FIT` | 3 | False | *None* | 2 |
| 10 | `Ingresos por fletes` | 3 | False | *None* | 2 |
| 11 | `Ingresos por otros servicios` | 3 | False | *None* | 2 |
| 12 | `Subtotal Ingresos por Eventos` | 1 | False | *None* | 1 |
| 13 | `Ingresos por eventos` | 3 | False | *None* | 2 |
| 14 | `Subtotal Ingresos por Taller` | 1 | False | *None* | 1 |
| 15 | `Ingresos por taller` | 3 | False | *None* | 2 |
| 16 | `Total Costo de Ventas` | 0 | False | *None* | 0 |
| 17 | `Subtotal Costo de Ventas por Mercancia` | 1 | False | *None* | 1 |
| 18 | `Costos de venta por mercancia` | 3 | True | `Subtotal Costo de Ventas por Mercancia` | 3 |
| 19 | `Subtotal Costo de Ventas por Servicios` | 1 | False | *None* | 1 |
| 20 | `Costo de venta por servicio del café` | 3 | False | *None* | 2 |
| 21 | `Subtotal Costo de Ventas por Eventos` | 1 | False | *None* | 1 |
| 22 | `Costo de ventas por eventos` | 3 | False | *None* | 2 |
| 23 | `Utilidad Bruta por Venta de Mercancia y Taller` | 0 | False | *None* | 0 |
| 24 | `Utilidad Bruta por Servicios` | 0 | False | *None* | 0 |
| 25 | `Utilidad Bruta por Eventos` | 0 | False | *None* | 0 |
| 26 | `Utilidad Bruta` | 0 | False | *None* | 0 |
| 27 | `Total Gastos Operacionales` | 0 | False | *None* | 0 |
| 28 | `Subtotal Gastos de Administración` | 1 | False | *None* | 1 |
| 29 | `Gastos de servicios públicos (Agua, luz, Aseo Urbano)` | 3 | False | *None* | 2 |
| 30 | `Gastos de servicios de telefonía e internet` | 3 | False | *None* | 2 |
| 31 | `Gastos de alquiler del local` | 3 | False | *None* | 2 |
| 32 | `Gastos de Condominio` | 3 | False | *None* | 2 |
| 33 | `Gastos de asistencia outsorcing` | 3 | True | `Subtotal Gastos de Administración` | 3 |
| 34 | `Gastos de alquiler de bienes muebles` | 3 | False | *None* | 2 |
| 35 | `Gastos de artículos de oficina` | 3 | False | *None* | 2 |
| 36 | `Gastos de artículos de limpieza e higiene` | 3 | False | *None* | 2 |
| 37 | `Gastos de alimentos y bebidas` | 3 | False | *None* | 2 |
| 38 | `Gastos de envíos y encomiendas administrativas` | 3 | False | *None* | 2 |
| 39 | `Gastos de honorarios profesionales` | 3 | False | *None* | 2 |
| 40 | `Gastos de estacionamiento` | 3 | False | *None* | 2 |
| 41 | `Gastos de gestoría` | 3 | False | *None* | 2 |
| 42 | `Gastos legales` | 3 | False | *None* | 2 |
| 43 | `Gastos de taxi, transporte y/o delivery` | 3 | False | *None* | 2 |
| 44 | `Gastos de suministros para taller` | 3 | False | *None* | 2 |
| 45 | `Gastos de suministros del café` | 3 | False | *None* | 2 |
| 46 | `Gastos por fiestas, festejos y/o reuniones` | 3 | False | *None* | 2 |
| 47 | `Gastos de vigilancia` | 3 | False | *None* | 2 |
| 48 | `Gastos de retenciones no descontadas` | 3 | False | *None* | 2 |
| 49 | `Mantenimiento y reparaciones` | 3 | False | *None* | 2 |
| 50 | `Viáticos administrativos` | 3 | False | *None* | 2 |
| 51 | `Gastos de seguro` | 3 | False | *None* | 2 |
| 52 | `Gastos de impuestos, tasas y contribuciones` | 3 | False | *None* | 2 |
| 53 | `Depreciaciones, deterioro y Amortización` | 3 | False | *None* | 2 |
| 54 | `Gasto por impuesto a las pensiones` | 3 | True | `Gastos de impuestos, tasas y contribuciones` | 3 |
| 55 | `Gastos de IGTF` | 3 | True | `Gastos Bancarios` | 3 |
| 56 | `Gastos de comisiones bancarias` | 3 | True | `Gastos Bancarios` | 3 |
| 57 | `Gastos Bancarios` | 3 | False | *None* | 2 |
| 58 | `Gastos de intereses sobre préstamos` | 3 | False | *None* | 2 |
| 59 | `Subtotal Gastos de Recursos Humanos` | 1 | False | *None* | 1 |
| 60 | `Gastos de sueldos y salarios empleados y directivos` | 2 | False | *None* | 2 |
| 61 | `Gastos de sueldos y salarios empleados` | 3 | True | `Gastos de sueldos y salarios empleados y directivos` | 3 |
| 62 | `Gastos de sueldos y salarios directivos` | 3 | True | `Gastos de sueldos y salarios empleados y directivos` | 3 |
| 63 | `Gastos de horas extras, feriados y bono nocturno` | 3 | True | `Gastos de sueldos y salarios empleados y directivos` | 3 |
| 64 | `Gastos de Bono de alimentación empleados` | 3 | True | `Gastos de sueldos y salarios empleados y directivos` | 3 |
| 65 | `Gastos de Bono de alimentación directivos` | 3 | True | `Gastos de sueldos y salarios empleados y directivos` | 3 |
| 66 | `Gastos de complementos empleados y directivos` | 2 | False | *None* | 2 |
| 67 | `Gastos de complemento de sueldos y salarios empleados` | 3 | True | `Gastos de complementos empleados and directivos` | 3 |
| 68 | `Gastos de complemento de sueldos y salarios directivos` | 3 | True | `Gastos de complementos empleados y directivos` | 3 |
| 69 | `Gastos de personal externo` | 2 | False | *None* | 2 |
| 70 | `Gastos de servicios de personal externo` | 3 | True | `Gastos de personal externo` | 3 |
| 71 | `Gastos de pasivos laborales vacaciones` | 2 | False | *None* | 2 |
| 72 | `Gastos de vacaciones empleados` | 3 | True | `Gastos de pasivos laborales vacaciones` | 3 |
| 73 | `Gastos de vacaciones directivos` | 3 | True | `Gastos de pasivos laborales vacaciones` | 3 |
| 74 | `Gastos de complemento de vacaciones empleados` | 3 | True | `Gastos de pasivos laborales vacaciones` | 3 |
| 75 | `Gastos de complemento de vacaciones directivos` | 3 | True | `Gastos de pasivos laborales vacaciones` | 3 |
| 76 | `Gastos de pasivos laborales utilidades` | 2 | False | *None* | 2 |
| 77 | `Gastos de bono vacacional empleados` | 3 | True | `Gastos de pasivos laborales utilidades` | 3 |
| 78 | `Gastos de bono vacacional directivos` | 3 | True | `Gastos de pasivos laborales utilidades` | 3 |
| 79 | `Gastos de complemento bono vacacional empleados` | 3 | True | `Gastos de pasivos laborales utilidades` | 3 |
| 80 | `Gastos de complemento bono vacacional directivos` | 3 | True | `Gastos de pasivos laborales utilidades` | 3 |
| 81 | `Gastos de utilidades empleados` | 3 | True | `Gastos de pasivos laborales utilidades` | 3 |
| 82 | `Gastos de utilidades directivos` | 3 | True | `Gastos de pasivos laborales utilidades` | 3 |
| 83 | `Gastos de complemento de utilidades empleados` | 3 | True | `Gastos de pasivos laborales utilidades` | 3 |
| 84 | `Gastos de complemento de utilidades directivos` | 3 | True | `Gastos de pasivos laborales utilidades` | 3 |
| 85 | `Gastos de pasivos laborales prestaciones e intereses` | 2 | False | *None* | 2 |
| 86 | `Gastos de prestaciones sociales empleados` | 3 | True | `Gastos de pasivos laborales prestaciones e intereses` | 3 |
| 87 | `Gastos de prestaciones sociales directivos` | 3 | True | `Gastos de pasivos laborales prestaciones e intereses` | 3 |
| 88 | `Gastos de complemento de prestaciones sociales empleados` | 3 | True | `Gastos de pasivos laborales prestaciones e intereses` | 3 |
| 89 | `Gastos de complemento de prestaciones sociales directivos` | 3 | True | `Gastos de pasivos laborales prestaciones e intereses` | 3 |
| 90 | `Gastos de intereses sobres prestaciones sociales empleados` | 3 | True | `Gastos de pasivos laborales prestaciones e intereses` | 3 |
| 91 | `Gastos de intereses sobres prestaciones sociales directivos` | 3 | True | `Gastos de pasivos laborales prestaciones e intereses` | 3 |
| 92 | `Gastos de complemento de intereses sobre prestaciones sociales empleados` | 3 | True | `Gastos de pasivos laborales prestaciones e intereses` | 3 |
| 93 | `Gastos de complemento de intereses sobre prestaciones sociales directivos` | 3 | True | `Gastos de pasivos laborales prestaciones e intereses` | 3 |
| 94 | `Gastos de pasivos laborales aportes` | 2 | False | *None* | 2 |
| 95 | `Gastos de aporte patronal IVSS` | 3 | True | `Gastos de pasivos laborales aportes` | 3 |
| 96 | `Gastos de aporte patronal SPF` | 3 | True | `Gastos de pasivos laborales aportes` | 3 |
| 97 | `Gastos de aporte patronal FAOV` | 3 | True | `Gastos de pasivos laborales aportes` | 3 |
| 98 | `Gastos de aporte patronal INCES` | 3 | True | `Gastos de pasivos laborales aportes` | 3 |
| 99 | `Gastos de pasivos laborales bono de guardería` | 2 | False | *None* | 2 |
| 100 | `Gastos de bono de guardería` | 3 | True | `Gastos de pasivos laborales bono de guardería` | 3 |
| 101 | `Gastos de pasivos laborales HCM` | 2 | False | *None* | 2 |
| 102 | `Gastos de póliza HCM` | 3 | True | `Gastos de pasivos laborales HCM` | 3 |
| 103 | `Gastos de salud y seguridad laboral` | 3 | False | *None* | 2 |
| 104 | `Gastos de salud y seguridad laboral dotación` | 3 | False | *None* | 2 |
| 105 | `Gastos de uniformes y dotación al personal` | 3 | True | `Gastos de salud y seguridad laboral dotación` | 3 |
| 106 | `Gastos de salud y seguridad laboral fiestas y agasajos` | 2 | False | *None* | 2 |
| 107 | `Gastos de fiestas y agasajos al personal` | 3 | True | `Gastos de salud y seguridad laboral fiestas y agasajos` | 3 |
| 108 | `Otros gastos de personal` | 2 | False | *None* | 2 |
| 109 | `Gastos de otros bonos empleados` | 3 | True | `Otros gastos de personal` | 3 |
| 110 | `Gastos de transporte del personal` | 3 | True | `Otros gastos de personal` | 3 |
| 111 | `Gastos de donaciones y obsequios al personal` | 3 | True | `Otros gastos de personal` | 3 |
| 112 | `Gastos de capacitación al personal` | 3 | True | `Otros gastos de personal` | 3 |
| 113 | `Subtotal Gastos de Comercialización y Logistica` | 1 | False | *None* | 1 |
| 114 | `Gastos de viáticos comerciales` | 3 | False | *None* | 2 |
| 115 | `Gastos de comisiones empleados` | 3 | True | `Subtotal Gastos de Comercialización y Logistica` | 3 |
| 116 | `Gastos de comisiones empleados del taller` | 3 | True | `Subtotal Gastos de Comercialización y Logistica` | 3 |
| 117 | `Gastos de comisiones por venta de personal externo` | 3 | True | `Subtotal Gastos de Comercialización y Logistica` | 3 |
| 118 | `Gastos de fletes y envios no asociados al costo` | 3 | False | *None* | 2 |
| 119 | `Otros gastos no asociados al costo` | 3 | False | *None* | 2 |
| 120 | `Gastos por combustible` | 3 | False | *None* | 2 |
| 121 | `Gastos de representación` | 3 | False | *None* | 2 |
| 122 | `Gastos por garantia` | 3 | False | *None* | 2 |
| 123 | `Gastos por suscripciones` | 3 | False | *None* | 2 |
| 124 | `Gastos de Stand y/o ferias comerciales` | 3 | False | *None* | 2 |
| 125 | `Subtotal Gastos de Mercadeo` | 1 | False | *None* | 1 |
| 126 | `Gastos de redes sociales` | 3 | False | *None* | 2 |
| 127 | `Gastos de medios publicitarios` | 3 | False | *None* | 2 |
| 128 | `Gastos de impresiones de material gráfico` | 3 | True | `Otros gastos de publicidad y promoción` | 3 |
| 129 | `Otros gastos de publicidad y promoción` | 3 | False | *None* | 2 |
| 130 | `Gastos de patrocinio y donación` | 3 | False | *None* | 2 |
| 131 | `Gastos de patrocinio, donación y/o obsequios en efectivo` | 3 | True | `Gastos de patrocinio y donación` | 3 |
| 132 | `Gastos de patrocinio, donación y/o obsequios en productos` | 3 | True | `Gastos de patrocinio y donación` | 3 |
| 133 | `Gastos de viáticos por eventos` | 3 | False | *None* | 2 |
| 134 | `Gastos de materiales y servicios por eventos` | 3 | False | *None* | 2 |
| 135 | `Gastos de alimentos y bebidas por eventos` | 3 | False | *None* | 2 |
| 136 | `Gastos de personal por eventos` | 3 | False | *None* | 2 |
| 137 | `Gastos de patrocinio, donación y/o obseq por eventos` | 3 | False | *None* | 2 |
| 138 | `Subtotal Gastos de TI+I` | 1 | False | *None* | 1 |
| 139 | `Gastos de página web` | 3 | False | *None* | 2 |
| 140 | `Gastos de desarrollo` | 3 | False | *None* | 2 |
| 141 | `Utilidad antes de Comisiones por Ventas` | 0 | False | *None* | 0 |
| 142 | `Gastos de comisiones por ventas` | 3 | False | *None* | 2 |
| 143 | `Gastos de comisiones por ventas taller` | 3 | False | *None* | 2 |
| 144 | `Utilidad después de Comisiones por Ventas` | 0 | False | *None* | 0 |
| 145 | `Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA)` | 0 | False | *None* | 0 |
| 146 | `Utilidad antes de Intereses e Impuestos (EBIT)` | 0 | False | *None* | 0 |
| 147 | `Otros Gastos no Operacionales` | 0 | False | *None* | 0 |
| 148 | `Faltante en Ventas` | 3 | False | *None* | 2 |
| 149 | `Pérdida en venta de activos` | 3 | False | *None* | 2 |
| 150 | `Pérdida en siniestro de activos` | 3 | False | *None* | 2 |
| 151 | `Pérdida en tasa cambiaria` | 3 | False | *None* | 2 |
| 152 | `Pérdida por diferencia en pagos` | 3 | False | *None* | 2 |
| 153 | `Multas` | 3 | False | *None* | 2 |
| 154 | `Faltante y deterioro de inventarios` | 3 | False | *None* | 2 |
| 155 | `Total Gastos Operacionales y No Operacionales` | 0 | False | *None* | 0 |
| 156 | `Otros Ingresos no Operacionales` | 0 | False | *None* | 1 |
| 157 | `Ingresos por alquileres` | 3 | False | *None* | 2 |
| 158 | `Ingresos por intereses` | 3 | False | *None* | 2 |
| 159 | `Ingresos por comisiones` | 3 | False | *None* | 2 |
| 160 | `Ingresos por servicios administrativos` | 3 | False | *None* | 2 |
| 161 | `Sobrante en ventas` | 3 | False | *None* | 2 |
| 162 | `Sobrante de inventarios` | 3 | False | *None* | 2 |
| 163 | `Ganancia en venta de activos` | 3 | False | *None* | 2 |
| 164 | `Ganancia por tasa cambiaria` | 3 | False | *None* | 2 |
| 165 | `Ganancia por diferencias en pagos` | 3 | False | *None* | 2 |
| 166 | `Utilidad Neta` | 0 | False | *None* | 0 |
| 167 | `ISLR` | 0 | False | *None* | 0 |
| 168 | `Utilidad Neta despues de ISLR` | 0 | False | *None* | 0 |