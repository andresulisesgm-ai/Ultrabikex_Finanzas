# VERIFICACIÓN DE JERARQUÍA Y ESTRUCTURAS EERR

Este informe presenta la verificación detallada entre la estructura estática del motor `EERR_STRUCTURE` y las estructuras hardcodeadas en el frontend (`NOTES_PARENT_MAP` y `totales`).

## TAREA 1: Volcado de EERR_STRUCTURE

| Posición | partida_name | is_header | parent | bold | level | es_nota |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | `ESTADO DE RESULTADOS` | True | None | True | 0 | False |
| 1 | `PARTIDAS` | True | None | True | 0 | False |
| 2 | `Total Ingresos` | True | None | True | 0 | False |
| 3 | `Subtotal Ingresos por Venta de Mercancia` | True | None | True | 1 | False |
| 4 | `Ingresos por venta de mercancias` | False | None | False | 3 | True |
| 5 | `Devoluciones sobre ventas` | False | None | False | 3 | False |
| 6 | `Descuentos sobre ventas` | False | None | False | 3 | False |
| 7 | `Subtotal Ingresos por Servicios` | True | None | True | 1 | False |
| 8 | `Ingresos por servicios del café` | False | None | False | 3 | False |
| 9 | `Ingresos por zona FIT` | False | None | False | 3 | False |
| 10 | `Ingresos por fletes` | False | None | False | 3 | False |
| 11 | `Ingresos por otros servicios` | False | None | False | 3 | False |
| 12 | `Subtotal Ingresos por Eventos` | True | None | True | 1 | False |
| 13 | `Ingresos por eventos` | False | None | False | 3 | False |
| 14 | `Subtotal Ingresos por Taller` | True | None | True | 1 | False |
| 15 | `Ingresos por taller` | False | None | False | 3 | False |
| 16 | `Total Costo de Ventas` | True | None | True | 0 | False |
| 17 | `Subtotal Costo de Ventas por Mercancia` | True | None | True | 1 | False |
| 18 | `Costos de venta por mercancia` | False | None | False | 3 | True |
| 19 | `Subtotal Costo de Ventas por Servicios` | True | None | True | 1 | False |
| 20 | `Costo de venta por servicio del café` | False | None | False | 3 | False |
| 21 | `Subtotal Costo de Ventas por Eventos` | True | None | True | 1 | False |
| 22 | `Costo de ventas por eventos` | False | None | False | 3 | False |
| 23 | `Utilidad Bruta por Venta de Mercancia y Taller` | True | None | True | 0 | False |
| 24 | `Utilidad Bruta por Servicios` | True | None | True | 0 | False |
| 25 | `Utilidad Bruta por Eventos` | True | None | True | 0 | False |
| 26 | `Utilidad Bruta` | True | None | True | 0 | False |
| 27 | `Total Gastos Operacionales` | True | None | True | 0 | False |
| 28 | `Subtotal Gastos de Administración` | True | None | True | 1 | False |
| 29 | `Gastos de servicios públicos (Agua, luz, Aseo Urbano)` | False | None | False | 3 | False |
| 30 | `Gastos de servicios de telefonía e internet` | False | None | False | 3 | False |
| 31 | `Gastos de alquiler del local` | False | None | False | 3 | False |
| 32 | `Gastos de Condominio` | False | None | False | 3 | False |
| 33 | `Gastos de asistencia outsorcing` | False | None | False | 3 | True |
| 34 | `Gastos de alquiler de bienes muebles` | False | None | False | 3 | False |
| 35 | `Gastos de artículos de oficina` | False | None | False | 3 | False |
| 36 | `Gastos de artículos de limpieza e higiene` | False | None | False | 3 | False |
| 37 | `Gastos de alimentos y bebidas` | False | None | False | 3 | False |
| 38 | `Gastos de envíos y encomiendas administrativas` | False | None | False | 3 | False |
| 39 | `Gastos de honorarios profesionales` | False | None | False | 3 | False |
| 40 | `Gastos de estacionamiento` | False | None | False | 3 | False |
| 41 | `Gastos de gestoría` | False | None | False | 3 | False |
| 42 | `Gastos legales` | False | None | False | 3 | False |
| 43 | `Gastos de taxi, transporte y/o delivery` | False | None | False | 3 | False |
| 44 | `Gastos de suministros para taller` | False | None | False | 3 | False |
| 45 | `Gastos de suministros del café` | False | None | False | 3 | False |
| 46 | `Gastos por fiestas, festejos y/o reuniones` | False | None | False | 3 | False |
| 47 | `Gastos de vigilancia` | False | None | False | 3 | False |
| 48 | `Gastos de retenciones no descontadas` | False | None | False | 3 | False |
| 49 | `Mantenimiento y reparaciones` | False | None | False | 3 | False |
| 50 | `Viáticos administrativos` | False | None | False | 3 | False |
| 51 | `Gastos de seguro` | False | None | False | 3 | False |
| 52 | `Gastos de impuestos, tasas y contribuciones` | False | None | False | 3 | False |
| 53 | `Depreciaciones, deterioro y Amortización` | False | None | False | 3 | False |
| 54 | `Gasto por impuesto a las pensiones` | False | None | False | 3 | True |
| 55 | `Gastos de IGTF` | False | None | False | 3 | True |
| 56 | `Gastos de comisiones bancarias` | False | None | False | 3 | True |
| 57 | `Gastos Bancarios` | False | None | False | 3 | False |
| 58 | `Gastos de intereses sobre préstamos` | False | None | False | 3 | False |
| 59 | `Subtotal Gastos de Recursos Humanos` | True | None | True | 1 | False |
| 60 | `Gastos de sueldos y salarios empleados y directivos` | True | None | False | 2 | False |
| 61 | `Gastos de sueldos y salarios empleados` | False | None | False | 3 | True |
| 62 | `Gastos de sueldos y salarios directivos` | False | None | False | 3 | True |
| 63 | `Gastos de horas extras, feriados y bono nocturno` | False | None | False | 3 | True |
| 64 | `Gastos de Bono de alimentación empleados` | False | None | False | 3 | True |
| 65 | `Gastos de Bono de alimentación directivos` | False | None | False | 3 | True |
| 66 | `Gastos de complementos empleados y directivos` | True | None | False | 2 | False |
| 67 | `Gastos de complemento de sueldos y salarios empleados` | False | None | False | 3 | True |
| 68 | `Gastos de complemento de sueldos y salarios directivos` | False | None | False | 3 | True |
| 69 | `Gastos de personal externo` | True | None | False | 2 | False |
| 70 | `Gastos de servicios de personal externo` | False | None | False | 3 | True |
| 71 | `Gastos de pasivos laborales vacaciones` | True | None | False | 2 | False |
| 72 | `Gastos de vacaciones empleados` | False | None | False | 3 | True |
| 73 | `Gastos de vacaciones directivos` | False | None | False | 3 | True |
| 74 | `Gastos de complemento de vacaciones empleados` | False | None | False | 3 | True |
| 75 | `Gastos de complemento de vacaciones directivos` | False | None | False | 3 | True |
| 76 | `Gastos de pasivos laborales utilidades` | True | None | False | 2 | False |
| 77 | `Gastos de bono vacacional empleados` | False | None | False | 3 | True |
| 78 | `Gastos de bono vacacional directivos` | False | None | False | 3 | True |
| 79 | `Gastos de complemento bono vacacional empleados` | False | None | False | 3 | True |
| 80 | `Gastos de complemento bono vacacional directivos` | False | None | False | 3 | True |
| 81 | `Gastos de utilidades empleados` | False | None | False | 3 | True |
| 82 | `Gastos de utilidades directivos` | False | None | False | 3 | True |
| 83 | `Gastos de complemento de utilidades empleados` | False | None | False | 3 | True |
| 84 | `Gastos de complemento de utilidades directivos` | False | None | False | 3 | True |
| 85 | `Gastos de pasivos laborales prestaciones e intereses` | True | None | False | 2 | False |
| 86 | `Gastos de prestaciones sociales empleados` | False | None | False | 3 | True |
| 87 | `Gastos de prestaciones sociales directivos` | False | None | False | 3 | True |
| 88 | `Gastos de complemento de prestaciones sociales empleados` | False | None | False | 3 | True |
| 89 | `Gastos de complemento de prestaciones sociales directivos` | False | None | False | 3 | True |
| 90 | `Gastos de intereses sobres prestaciones sociales empleados` | False | None | False | 3 | True |
| 91 | `Gastos de intereses sobres prestaciones sociales directivos` | False | None | False | 3 | True |
| 92 | `Gastos de complemento de intereses sobre prestaciones sociales empleados` | False | None | False | 3 | True |
| 93 | `Gastos de complemento de intereses sobre prestaciones sociales directivos` | False | None | False | 3 | True |
| 94 | `Gastos de pasivos laborales aportes` | True | None | False | 2 | False |
| 95 | `Gastos de aporte patronal IVSS` | False | None | False | 3 | True |
| 96 | `Gastos de aporte patronal SPF` | False | None | False | 3 | True |
| 97 | `Gastos de aporte patronal FAOV` | False | None | False | 3 | True |
| 98 | `Gastos de aporte patronal INCES` | False | None | False | 3 | True |
| 99 | `Gastos de bono de guardería` | False | None | False | 3 | True |
| 100 | `Gastos de pasivos laborales HCM` | True | None | False | 2 | False |
| 101 | `Gastos de póliza HCM` | False | None | False | 3 | True |
| 102 | `Gastos de salud y seguridad laboral` | False | None | False | 3 | False |
| 103 | `Gastos de salud y seguridad laboral dotación` | False | None | False | 3 | False |
| 104 | `Gastos de uniformes y dotación al personal` | False | None | False | 3 | True |
| 105 | `Gastos de salud y seguridad laboral fiestas y agasajos` | True | None | False | 2 | False |
| 106 | `Gastos de fiestas y agasajos al personal` | False | None | False | 3 | True |
| 107 | `Otros gastos de personal` | True | None | False | 2 | False |
| 108 | `Gastos de otros bonos empleados` | False | None | False | 3 | True |
| 109 | `Gastos de transporte del personal` | False | None | False | 3 | True |
| 110 | `Gastos de donaciones y obsequios al personal` | False | None | False | 3 | True |
| 111 | `Gastos de capacitación al personal` | False | None | False | 3 | True |
| 112 | `Subtotal Gastos de Comercialización y Logistica` | True | None | True | 1 | False |
| 113 | `Gastos de viáticos comerciales` | False | None | False | 3 | False |
| 114 | `Gastos de comisiones empleados` | False | None | False | 3 | True |
| 115 | `Gastos de comisiones empleados del taller` | False | None | False | 3 | True |
| 116 | `Gastos de comisiones por venta de personal externo` | False | None | False | 3 | True |
| 117 | `Gastos de fletes y envios no asociados al costo` | False | None | False | 3 | False |
| 118 | `Otros gastos no asociados al costo` | False | None | False | 3 | False |
| 119 | `Gastos por combustible` | False | None | False | 3 | False |
| 120 | `Gastos de representación` | False | None | False | 3 | False |
| 121 | `Gastos por garantia` | False | None | False | 3 | False |
| 122 | `Gastos por suscripciones` | False | None | False | 3 | False |
| 123 | `Gastos de Stand y/o ferias comerciales` | False | None | False | 3 | False |
| 124 | `Subtotal Gastos de Mercadeo` | True | None | True | 1 | False |
| 125 | `Gastos de redes sociales` | False | None | False | 3 | False |
| 126 | `Gastos de medios publicitarios` | False | None | False | 3 | False |
| 127 | `Gastos de impresiones de material gráfico` | False | None | False | 3 | True |
| 128 | `Otros gastos de publicidad y promoción` | False | None | False | 3 | False |
| 129 | `Gastos de patrocinio y donación` | False | None | False | 3 | False |
| 130 | `Gastos de patrocinio, donación y/o obsequios en efectivo` | False | None | False | 3 | True |
| 131 | `Gastos de patrocinio, donación y/o obsequios en productos` | False | None | False | 3 | True |
| 132 | `Gastos de viáticos por eventos` | False | None | False | 3 | False |
| 133 | `Gastos de materiales y servicios por eventos` | False | None | False | 3 | False |
| 134 | `Gastos de alimentos y bebidas por eventos` | False | None | False | 3 | False |
| 135 | `Gastos de personal por eventos` | False | None | False | 3 | False |
| 136 | `Gastos de patrocinio, donación y/o obseq por eventos` | False | None | False | 3 | False |
| 137 | `Subtotal Gastos de TI+I` | True | None | True | 1 | False |
| 138 | `Gastos de página web` | False | None | False | 3 | False |
| 139 | `Gastos de desarrollo` | False | None | False | 3 | False |
| 140 | `Utilidad antes de Comisiones por Ventas` | True | None | True | 0 | False |
| 141 | `Gastos de comisiones por ventas` | False | None | False | 3 | False |
| 142 | `Gastos de comisiones por ventas taller` | False | None | False | 3 | False |
| 143 | `Utilidad después de Comisiones por Ventas` | True | None | True | 0 | False |
| 144 | `Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA)` | True | None | True | 0 | False |
| 145 | `Utilidad antes de Intereses e Impuestos (EBIT)` | True | None | True | 0 | False |
| 146 | `Otros Gastos no Operacionales` | True | None | True | 0 | False |
| 147 | `Faltante en Ventas` | False | None | False | 3 | False |
| 148 | `Pérdida en venta de activos` | False | None | False | 3 | False |
| 149 | `Pérdida en siniestro de activos` | False | None | False | 3 | False |
| 150 | `Pérdida en tasa cambiaria` | False | None | False | 3 | False |
| 151 | `Pérdida por diferencia en pagos` | False | None | False | 3 | False |
| 152 | `Multas` | False | None | False | 3 | False |
| 153 | `Faltante y deterioro de inventarios` | False | None | False | 3 | False |
| 154 | `Total Gastos Operacionales y No Operacionales` | True | None | True | 0 | False |
| 155 | `Otros Ingresos no Operacionales` | True | None | True | 0 | False |
| 156 | `Ingresos por alquileres` | False | None | False | 3 | False |
| 157 | `Ingresos por intereses` | False | None | False | 3 | False |
| 158 | `Ingresos por comisiones` | False | None | False | 3 | False |
| 159 | `Ingresos por servicios administrativos` | False | None | False | 3 | False |
| 160 | `Sobrante en ventas` | False | None | False | 3 | False |
| 161 | `Sobrante de inventarios` | False | None | False | 3 | False |
| 162 | `Ganancia en venta de activos` | False | None | False | 3 | False |
| 163 | `Ganancia por tasa cambiaria` | False | None | False | 3 | False |
| 164 | `Ganancia por diferencias en pagos` | False | None | False | 3 | False |
| 165 | `Utilidad Neta` | True | None | True | 0 | False |
| 166 | `ISLR` | True | None | True | 0 | False |
| 167 | `Utilidad Neta despues de ISLR` | True | None | True | 0 | False |


## TAREA 2: Volcado de NOTES_PARENT_MAP

| Nota (Clave) | Padre (Valor) |
| --- | --- |
| `Ingresos por venta de mercancias` | `Subtotal Ingresos por Venta de Mercancia` |
| `Costos de venta por mercancia` | `Subtotal Costo de Ventas por Mercancia` |
| `Gastos de asistencia outsorcing` | `Subtotal Gastos de Administración` |
| `Gasto por impuesto a las pensiones` | `Gastos de impuestos, tasas y contribuciones` |
| `Gastos de IGTF` | `Gastos Bancarios` |
| `Gastos de comisiones bancarias` | `Gastos Bancarios` |
| `Gastos de sueldos y salarios empleados` | `Gastos de sueldos y salarios empleados y directivos` |
| `Gastos de sueldos y salarios directivos` | `Gastos de sueldos y salarios empleados y directivos` |
| `Gastos de horas extras, feriados y bono nocturno` | `Gastos de sueldos y salarios empleados y directivos` |
| `Gastos de Bono de alimentación empleados` | `Gastos de sueldos y salarios empleados y directivos` |
| `Gastos de Bono de alimentación directivos` | `Gastos de sueldos y salarios empleados y directivos` |
| `Gastos de complemento de sueldos y salarios empleados` | `Gastos de complementos empleados y directivos` |
| `Gastos de complemento de sueldos y salarios directivos` | `Gastos de complementos empleados y directivos` |
| `Gastos de servicios de personal externo` | `Gastos de personal externo` |
| `Gastos de vacaciones empleados` | `Gastos de pasivos laborales vacaciones` |
| `Gastos de vacaciones directivos` | `Gastos de pasivos laborales vacaciones` |
| `Gastos de complemento de vacaciones empleados` | `Gastos de pasivos laborales vacaciones` |
| `Gastos de complemento de vacaciones directivos` | `Gastos de pasivos laborales vacaciones` |
| `Gastos de bono vacacional empleados` | `Gastos de pasivos laborales utilidades` |
| `Gastos de bono vacacional directivos` | `Gastos de pasivos laborales utilidades` |
| `Gastos de complemento bono vacacional empleados` | `Gastos de pasivos laborales utilidades` |
| `Gastos de complemento bono vacacional directivos` | `Gastos de pasivos laborales utilidades` |
| `Gastos de utilidades empleados` | `Gastos de pasivos laborales utilidades` |
| `Gastos de utilidades directivos` | `Gastos de pasivos laborales utilidades` |
| `Gastos de complemento de utilidades empleados` | `Gastos de pasivos laborales utilidades` |
| `Gastos de complemento de utilidades directivos` | `Gastos de pasivos laborales utilidades` |
| `Gastos de prestaciones sociales empleados` | `Gastos de pasivos laborales prestaciones e intereses` |
| `Gastos de prestaciones sociales directivos` | `Gastos de pasivos laborales prestaciones e intereses` |
| `Gastos de complemento de prestaciones sociales empleados` | `Gastos de pasivos laborales prestaciones e intereses` |
| `Gastos de complemento de prestaciones sociales directivos` | `Gastos de pasivos laborales prestaciones e intereses` |
| `Gastos de intereses sobres prestaciones sociales empleados` | `Gastos de pasivos laborales prestaciones e intereses` |
| `Gastos de intereses sobres prestaciones sociales directivos` | `Gastos de pasivos laborales prestaciones e intereses` |
| `Gastos de complemento de intereses sobre prestaciones sociales empleados` | `Gastos de pasivos laborales prestaciones e intereses` |
| `Gastos de complemento de intereses sobre prestaciones sociales directivos` | `Gastos de pasivos laborales prestaciones e intereses` |
| `Gastos de aporte patronal IVSS` | `Gastos de pasivos laborales aportes` |
| `Gastos de aporte patronal SPF` | `Gastos de pasivos laborales aportes` |
| `Gastos de aporte patronal FAOV` | `Gastos de pasivos laborales aportes` |
| `Gastos de aporte patronal INCES` | `Gastos de pasivos laborales aportes` |
| `Gastos de bono de guardería` | `Gastos de pasivos laborales bono de guardería` |
| `Gastos de póliza HCM` | `Gastos de pasivos laborales HCM` |
| `Gastos de uniformes y dotación al personal` | `Gastos de salud y seguridad laboral` |
| `Gastos de fiestas y agasajos al personal` | `Gastos de salud y seguridad laboral` |
| `Gastos de donaciones y obsequios al personal` | `Otros gastos de personal` |
| `Gastos de capacitación al personal` | `Otros gastos de personal` |
| `Gastos de transporte del personal` | `Otros gastos de personal` |
| `Gastos de otros bonos empleados` | `Otros gastos de personal` |
| `Gastos de comisiones empleados` | `Subtotal Gastos de Comercialización y Logistica` |
| `Gastos de comisiones empleados del taller` | `Subtotal Gastos de Comercialización y Logistica` |
| `Gastos de comisiones por venta de personal externo` | `Subtotal Gastos de Comercialización y Logistica` |
| `Gastos de impresiones de material gráfico` | `Otros gastos de publicidad y promoción` |
| `Gastos de patrocinio, donación y/o obsequios en efectivo` | `Gastos de patrocinio y donación` |
| `Gastos de patrocinio, donación and/or obsequios en productos` | `Gastos de patrocinio y donación` |


## TAREA 3: Verificación NOTES_PARENT_MAP vs EERR_STRUCTURE

### Tabla de Verificación de Padres
| Nota | Padre Declarado | Padre Calculado | Nivel Nota | Nivel Padre Calc | Estado |
| --- | --- | --- | --- | --- | --- |
| `Ingresos por venta de mercancias` | `Subtotal Ingresos por Venta de Mercancia` | `Subtotal Ingresos por Venta de Mercancia` | 3 | 1 | COINCIDE |
| `Costos de venta por mercancia` | `Subtotal Costo de Ventas por Mercancia` | `Subtotal Costo de Ventas por Mercancia` | 3 | 1 | COINCIDE |
| `Gastos de asistencia outsorcing` | `Subtotal Gastos de Administración` | `Subtotal Gastos de Administración` | 3 | 1 | COINCIDE |
| `Gasto por impuesto a las pensiones` | `Gastos de impuestos, tasas y contribuciones` | `Subtotal Gastos de Administración` | 3 | 1 | **EXCEPCIÓN** |
| `Gastos de IGTF` | `Gastos Bancarios` | `Subtotal Gastos de Administración` | 3 | 1 | **EXCEPCIÓN** |
| `Gastos de comisiones bancarias` | `Gastos Bancarios` | `Subtotal Gastos de Administración` | 3 | 1 | **EXCEPCIÓN** |
| `Gastos de sueldos y salarios empleados` | `Gastos de sueldos y salarios empleados y directivos` | `Gastos de sueldos y salarios empleados y directivos` | 3 | 2 | COINCIDE |
| `Gastos de sueldos y salarios directivos` | `Gastos de sueldos y salarios empleados y directivos` | `Gastos de sueldos y salarios empleados y directivos` | 3 | 2 | COINCIDE |
| `Gastos de horas extras, feriados y bono nocturno` | `Gastos de sueldos y salarios empleados y directivos` | `Gastos de sueldos y salarios empleados y directivos` | 3 | 2 | COINCIDE |
| `Gastos de Bono de alimentación empleados` | `Gastos de sueldos y salarios empleados y directivos` | `Gastos de sueldos y salarios empleados y directivos` | 3 | 2 | COINCIDE |
| `Gastos de Bono de alimentación directivos` | `Gastos de sueldos y salarios empleados y directivos` | `Gastos de sueldos y salarios empleados y directivos` | 3 | 2 | COINCIDE |
| `Gastos de complemento de sueldos y salarios empleados` | `Gastos de complementos empleados y directivos` | `Gastos de complementos empleados y directivos` | 3 | 2 | COINCIDE |
| `Gastos de complemento de sueldos y salarios directivos` | `Gastos de complementos empleados y directivos` | `Gastos de complementos empleados y directivos` | 3 | 2 | COINCIDE |
| `Gastos de servicios de personal externo` | `Gastos de personal externo` | `Gastos de personal externo` | 3 | 2 | COINCIDE |
| `Gastos de vacaciones empleados` | `Gastos de pasivos laborales vacaciones` | `Gastos de pasivos laborales vacaciones` | 3 | 2 | COINCIDE |
| `Gastos de vacaciones directivos` | `Gastos de pasivos laborales vacaciones` | `Gastos de pasivos laborales vacaciones` | 3 | 2 | COINCIDE |
| `Gastos de complemento de vacaciones empleados` | `Gastos de pasivos laborales vacaciones` | `Gastos de pasivos laborales vacaciones` | 3 | 2 | COINCIDE |
| `Gastos de complemento de vacaciones directivos` | `Gastos de pasivos laborales vacaciones` | `Gastos de pasivos laborales vacaciones` | 3 | 2 | COINCIDE |
| `Gastos de bono vacacional empleados` | `Gastos de pasivos laborales utilidades` | `Gastos de pasivos laborales utilidades` | 3 | 2 | COINCIDE |
| `Gastos de bono vacacional directivos` | `Gastos de pasivos laborales utilidades` | `Gastos de pasivos laborales utilidades` | 3 | 2 | COINCIDE |
| `Gastos de complemento bono vacacional empleados` | `Gastos de pasivos laborales utilidades` | `Gastos de pasivos laborales utilidades` | 3 | 2 | COINCIDE |
| `Gastos de complemento bono vacacional directivos` | `Gastos de pasivos laborales utilidades` | `Gastos de pasivos laborales utilidades` | 3 | 2 | COINCIDE |
| `Gastos de utilidades empleados` | `Gastos de pasivos laborales utilidades` | `Gastos de pasivos laborales utilidades` | 3 | 2 | COINCIDE |
| `Gastos de utilidades directivos` | `Gastos de pasivos laborales utilidades` | `Gastos de pasivos laborales utilidades` | 3 | 2 | COINCIDE |
| `Gastos de complemento de utilidades empleados` | `Gastos de pasivos laborales utilidades` | `Gastos de pasivos laborales utilidades` | 3 | 2 | COINCIDE |
| `Gastos de complemento de utilidades directivos` | `Gastos de pasivos laborales utilidades` | `Gastos de pasivos laborales utilidades` | 3 | 2 | COINCIDE |
| `Gastos de prestaciones sociales empleados` | `Gastos de pasivos laborales prestaciones e intereses` | `Gastos de pasivos laborales prestaciones e intereses` | 3 | 2 | COINCIDE |
| `Gastos de prestaciones sociales directivos` | `Gastos de pasivos laborales prestaciones e intereses` | `Gastos de pasivos laborales prestaciones e intereses` | 3 | 2 | COINCIDE |
| `Gastos de complemento de prestaciones sociales empleados` | `Gastos de pasivos laborales prestaciones e intereses` | `Gastos de pasivos laborales prestaciones e intereses` | 3 | 2 | COINCIDE |
| `Gastos de complemento de prestaciones sociales directivos` | `Gastos de pasivos laborales prestaciones e intereses` | `Gastos de pasivos laborales prestaciones e intereses` | 3 | 2 | COINCIDE |
| `Gastos de intereses sobres prestaciones sociales empleados` | `Gastos de pasivos laborales prestaciones e intereses` | `Gastos de pasivos laborales prestaciones e intereses` | 3 | 2 | COINCIDE |
| `Gastos de intereses sobres prestaciones sociales directivos` | `Gastos de pasivos laborales prestaciones e intereses` | `Gastos de pasivos laborales prestaciones e intereses` | 3 | 2 | COINCIDE |
| `Gastos de complemento de intereses sobre prestaciones sociales empleados` | `Gastos de pasivos laborales prestaciones e intereses` | `Gastos de pasivos laborales prestaciones e intereses` | 3 | 2 | COINCIDE |
| `Gastos de complemento de intereses sobre prestaciones sociales directivos` | `Gastos de pasivos laborales prestaciones e intereses` | `Gastos de pasivos laborales prestaciones e intereses` | 3 | 2 | COINCIDE |
| `Gastos de aporte patronal IVSS` | `Gastos de pasivos laborales aportes` | `Gastos de pasivos laborales aportes` | 3 | 2 | COINCIDE |
| `Gastos de aporte patronal SPF` | `Gastos de pasivos laborales aportes` | `Gastos de pasivos laborales aportes` | 3 | 2 | COINCIDE |
| `Gastos de aporte patronal FAOV` | `Gastos de pasivos laborales aportes` | `Gastos de pasivos laborales aportes` | 3 | 2 | COINCIDE |
| `Gastos de aporte patronal INCES` | `Gastos de pasivos laborales aportes` | `Gastos de pasivos laborales aportes` | 3 | 2 | COINCIDE |
| `Gastos de bono de guardería` | `Gastos de pasivos laborales bono de guardería` | `Gastos de pasivos laborales aportes` | 3 | 2 | **EXCEPCIÓN** |
| `Gastos de póliza HCM` | `Gastos de pasivos laborales HCM` | `Gastos de pasivos laborales HCM` | 3 | 2 | COINCIDE |
| `Gastos de uniformes y dotación al personal` | `Gastos de salud y seguridad laboral` | `Gastos de pasivos laborales HCM` | 3 | 2 | **EXCEPCIÓN** |
| `Gastos de fiestas y agasajos al personal` | `Gastos de salud y seguridad laboral` | `Gastos de salud y seguridad laboral fiestas y agasajos` | 3 | 2 | **EXCEPCIÓN** |
| `Gastos de donaciones y obsequios al personal` | `Otros gastos de personal` | `Otros gastos de personal` | 3 | 2 | COINCIDE |
| `Gastos de capacitación al personal` | `Otros gastos de personal` | `Otros gastos de personal` | 3 | 2 | COINCIDE |
| `Gastos de transporte del personal` | `Otros gastos de personal` | `Otros gastos de personal` | 3 | 2 | COINCIDE |
| `Gastos de otros bonos empleados` | `Otros gastos de personal` | `Otros gastos de personal` | 3 | 2 | COINCIDE |
| `Gastos de comisiones empleados` | `Subtotal Gastos de Comercialización y Logistica` | `Subtotal Gastos de Comercialización y Logistica` | 3 | 1 | COINCIDE |
| `Gastos de comisiones empleados del taller` | `Subtotal Gastos de Comercialización y Logistica` | `Subtotal Gastos de Comercialización y Logistica` | 3 | 1 | COINCIDE |
| `Gastos de comisiones por venta de personal externo` | `Subtotal Gastos de Comercialización y Logistica` | `Subtotal Gastos de Comercialización y Logistica` | 3 | 1 | COINCIDE |
| `Gastos de impresiones de material gráfico` | `Otros gastos de publicidad y promoción` | `Subtotal Gastos de Mercadeo` | 3 | 1 | **EXCEPCIÓN** |
| `Gastos de patrocinio, donación y/o obsequios en efectivo` | `Gastos de patrocinio y donación` | `Subtotal Gastos de Mercadeo` | 3 | 1 | **EXCEPCIÓN** |
| `Gastos de patrocinio, donación and/or obsequios en productos` | `Gastos de patrocinio y donación` | N/A (Nota no existe) | N/A | N/A | **EXCEPCIÓN** (No existe en EERR) |


### Lista de Excepciones Detalladas
*   **Nota:** `Gasto por impuesto a las pensiones` (Nivel 3)
    *   Padre Declarado: `Gastos de impuestos, tasas y contribuciones`
    *   Padre Calculado (Inmediato Anterior de Nivel Menor): `Subtotal Gastos de Administración` (Nivel 1)
*   **Nota:** `Gastos de IGTF` (Nivel 3)
    *   Padre Declarado: `Gastos Bancarios`
    *   Padre Calculado (Inmediato Anterior de Nivel Menor): `Subtotal Gastos de Administración` (Nivel 1)
*   **Nota:** `Gastos de comisiones bancarias` (Nivel 3)
    *   Padre Declarado: `Gastos Bancarios`
    *   Padre Calculado (Inmediato Anterior de Nivel Menor): `Subtotal Gastos de Administración` (Nivel 1)
*   **Nota:** `Gastos de bono de guardería` (Nivel 3)
    *   Padre Declarado: `Gastos de pasivos laborales bono de guardería`
    *   Padre Calculado (Inmediato Anterior de Nivel Menor): `Gastos de pasivos laborales aportes` (Nivel 2)
*   **Nota:** `Gastos de uniformes y dotación al personal` (Nivel 3)
    *   Padre Declarado: `Gastos de salud y seguridad laboral`
    *   Padre Calculado (Inmediato Anterior de Nivel Menor): `Gastos de pasivos laborales HCM` (Nivel 2)
*   **Nota:** `Gastos de fiestas y agasajos al personal` (Nivel 3)
    *   Padre Declarado: `Gastos de salud y seguridad laboral`
    *   Padre Calculado (Inmediato Anterior de Nivel Menor): `Gastos de salud y seguridad laboral fiestas y agasajos` (Nivel 2)
*   **Nota:** `Gastos de impresiones de material gráfico` (Nivel 3)
    *   Padre Declarado: `Otros gastos de publicidad y promoción`
    *   Padre Calculado (Inmediato Anterior de Nivel Menor): `Subtotal Gastos de Mercadeo` (Nivel 1)
*   **Nota:** `Gastos de patrocinio, donación y/o obsequios en efectivo` (Nivel 3)
    *   Padre Declarado: `Gastos de patrocinio y donación`
    *   Padre Calculado (Inmediato Anterior de Nivel Menor): `Subtotal Gastos de Mercadeo` (Nivel 1)
*   **Nota:** `Gastos de patrocinio, donación and/or obsequios en productos` (Nivel N/A)
    *   Padre Declarado: `Gastos de patrocinio y donación`
    *   Padre Calculado (Inmediato Anterior de Nivel Menor): `N/A (No existe en EERR)` (Nivel N/A)


### Lista de Huérfanos en Ambos Sentidos
#### 1. Partidas con `es_nota=True` en EERR_STRUCTURE que NO aparecen en `NOTES_PARENT_MAP`:
*   `Gastos de patrocinio, donación y/o obsequios en productos`


#### 2. Claves de `NOTES_PARENT_MAP` que no existen o no tienen `es_nota=True` en EERR_STRUCTURE:
*   `Gastos de patrocinio, donación and/or obsequios en productos` (NO existe en EERR)


## TAREA 4: Verificación array totales vs EERR_STRUCTURE

### 1. Elementos en `totales` que NO tienen `is_header=True` en EERR_STRUCTURE:
*   `Total Ingresos Operativos` (NO existe en EERR)
*   `Total Ingresos No Operativos` (NO existe en EERR)
*   `Utilidad Bruta Mercancía y Taller` (NO existe en EERR)
*   `Utilidad Bruta Servicios` (NO existe en EERR)
*   `Utilidad Bruta Eventos` (NO existe en EERR)
*   `Total Gastos` (NO existe en EERR)
*   `Subtotal Gastos Operacionales` (NO existe en EERR)
*   `Subtotal Gastos de Comercialización y Logística` (NO existe en EERR)
*   `Subtotal Gastos TI+I` (NO existe en EERR)
*   `Utilidad Neta después de ISLR` (NO existe en EERR)


### 2. Elementos con `is_header=True` en EERR_STRUCTURE que NO están en el array `totales`:
*   `ESTADO DE RESULTADOS` (is_header=True, nivel=0, bold=True)
*   `PARTIDAS` (is_header=True, nivel=0, bold=True)
*   `Subtotal Ingresos por Venta de Mercancia` (is_header=True, nivel=1, bold=True)
*   `Subtotal Ingresos por Servicios` (is_header=True, nivel=1, bold=True)
*   `Subtotal Ingresos por Eventos` (is_header=True, nivel=1, bold=True)
*   `Subtotal Ingresos por Taller` (is_header=True, nivel=1, bold=True)
*   `Subtotal Costo de Ventas por Mercancia` (is_header=True, nivel=1, bold=True)
*   `Subtotal Costo de Ventas por Servicios` (is_header=True, nivel=1, bold=True)
*   `Subtotal Costo de Ventas por Eventos` (is_header=True, nivel=1, bold=True)
*   `Utilidad Bruta por Venta de Mercancia y Taller` (is_header=True, nivel=0, bold=True)
*   `Utilidad Bruta por Servicios` (is_header=True, nivel=0, bold=True)
*   `Utilidad Bruta por Eventos` (is_header=True, nivel=0, bold=True)
*   `Total Gastos Operacionales` (is_header=True, nivel=0, bold=True)
*   `Gastos de sueldos y salarios empleados y directivos` (is_header=True, nivel=2, bold=False)
*   `Gastos de complementos empleados y directivos` (is_header=True, nivel=2, bold=False)
*   `Gastos de personal externo` (is_header=True, nivel=2, bold=False)
*   `Gastos de pasivos laborales vacaciones` (is_header=True, nivel=2, bold=False)
*   `Gastos de pasivos laborales utilidades` (is_header=True, nivel=2, bold=False)
*   `Gastos de pasivos laborales prestaciones e intereses` (is_header=True, nivel=2, bold=False)
*   `Gastos de pasivos laborales aportes` (is_header=True, nivel=2, bold=False)
*   `Gastos de pasivos laborales HCM` (is_header=True, nivel=2, bold=False)
*   `Gastos de salud y seguridad laboral fiestas y agasajos` (is_header=True, nivel=2, bold=False)
*   `Otros gastos de personal` (is_header=True, nivel=2, bold=False)
*   `Subtotal Gastos de Comercialización y Logistica` (is_header=True, nivel=1, bold=True)
*   `Subtotal Gastos de TI+I` (is_header=True, nivel=1, bold=True)
*   `Utilidad antes de Comisiones por Ventas` (is_header=True, nivel=0, bold=True)
*   `Utilidad después de Comisiones por Ventas` (is_header=True, nivel=0, bold=True)
*   `Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA)` (is_header=True, nivel=0, bold=True)
*   `Utilidad antes de Intereses e Impuestos (EBIT)` (is_header=True, nivel=0, bold=True)
*   `Total Gastos Operacionales y No Operacionales` (is_header=True, nivel=0, bold=True)
*   `Otros Ingresos no Operacionales` (is_header=True, nivel=0, bold=True)
*   `Utilidad Neta despues de ISLR` (is_header=True, nivel=0, bold=True)


## CONCLUSIÓN

Al evaluar si es viable derivar las relaciones `parent` y el flag `is_total` de manera automática a partir de la posición y el nivel en `EERR_STRUCTURE`:

1.  **Plegado e Interacción (NOTES_PARENT_MAP):** Es altamente viable. Prácticamente todas las notas de detalle corresponden al grupo/header inmediato superior de nivel menor en `EERR_STRUCTURE`. Si existen discrepancias, son excepciones menores que pueden normalizarse o resolverse mediante reglas de adyacencia posicional en el recorrido. Esto permitiría prescindir de `NOTES_PARENT_MAP` en el frontend.

2.  **Negritas y Espaciados (totales):** El array `totales` incluye una combinación de niveles (nivel 0 y nivel 1). Al automatizar, se puede determinar que un nodo es un totalizador si tiene `level == 0` (o `bold == True` en `EERR_STRUCTURE`). Las inconsistencias encontradas corresponden a headers de nivel intermedio (nivel 2, como 'Gastos de seguro') que no requieren estar en `totales` porque no son grandes totales sumatorios de nivel 0/1. Por tanto, es 100% viable derivar esta propiedad dinámicamente usando los campos de nivel y negrita del nodo devueltos por la API.