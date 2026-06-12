# DIAGNÓSTICO ULTRAX - FASE 2
> **Nota:** Documento generado en modo de solo lectura. No se han alterado bases de datos, código ni archivos existentes.

## 1. EXPORT COMPLETO DE mapping_groups_v2
Resultados de la consulta: `SELECT * FROM mapping_groups_v2 ORDER BY display_order, group_name`

Total registros en `mapping_groups_v2`: **395**

| ID | Group Name (group_name) | Odoo Code (odoo_code) | Report Type (report_type) | Display Order (display_order) | Created At (created_at) |
| --- | --- | --- | --- | --- | --- |
| 1 | Total Ingresos | 4.01.01.01.001 | eerr | 40 | 2026-06-07 12:07:16 |
| 2 | Total Ingresos | 4.01.01.02.001 | eerr | 40 | 2026-06-07 12:07:16 |
| 3 | Total Ingresos | 4.01.01.03.001 | eerr | 40 | 2026-06-07 12:07:16 |
| 4 | Total Ingresos | 4.01.02.01.001 | eerr | 40 | 2026-06-07 12:07:16 |
| 5 | Total Ingresos | 4.01.03.01.001 | eerr | 40 | 2026-06-07 12:07:16 |
| 6 | Total Ingresos | 4.01.04.01.001 | eerr | 40 | 2026-06-07 12:07:16 |
| 7 | Subtotal Ingresos por Venta de Mercancia | 4.01.01.01.001 | eerr | 50 | 2026-06-07 12:07:16 |
| 8 | Subtotal Ingresos por Venta de Mercancia | 4.01.01.02.001 | eerr | 50 | 2026-06-07 12:07:16 |
| 9 | Subtotal Ingresos por Venta de Mercancia | 4.01.01.03.001 | eerr | 50 | 2026-06-07 12:07:16 |
| 10 | Ingresos por venta de mercancía | 4.01.01.01.001 | eerr | 60 | 2026-06-07 12:07:16 |
| 11 | Devoluciones sobre ventas | 4.01.01.02.001 | eerr | 70 | 2026-06-07 12:07:16 |
| 12 | Descuentos sobre ventas | 4.01.01.03.001 | eerr | 80 | 2026-06-07 12:07:16 |
| 13 | Subtotal Ingresos por Servicios | 4.01.02.01.001 | eerr | 100 | 2026-06-07 12:07:16 |
| 14 | Ingresos por servicios del café | 4.01.02.01.001 | eerr | 110 | 2026-06-07 12:07:16 |
| 15 | Ingresos por zona FIT | 4.01.02.01.002 | eerr | 120 | 2026-06-07 12:07:16 |
| 16 | Ingresos por fletes | 4.01.02.01.003 | eerr | 130 | 2026-06-07 12:07:16 |
| 17 | Subtotal Ingresos por Eventos | 4.01.03.01.001 | eerr | 150 | 2026-06-07 12:07:16 |
| 18 | Ingresos por eventos | 4.01.03.01.001 | eerr | 160 | 2026-06-07 12:07:16 |
| 19 | Subtotal Ingresos por Taller | 4.01.04.01.001 | eerr | 180 | 2026-06-07 12:07:16 |
| 20 | Ingresos por taller | 4.01.04.01.001 | eerr | 190 | 2026-06-07 12:07:16 |
| 21 | Total Costo de Ventas | 5.01.01.01.001 | eerr | 220 | 2026-06-07 12:07:16 |
| 22 | Total Costo de Ventas | 5.01.02.01.001 | eerr | 220 | 2026-06-07 12:07:16 |
| 23 | Total Costo de Ventas | 5.01.03.01.001 | eerr | 220 | 2026-06-07 12:07:16 |
| 24 | Subtotal Costo de Ventas por Mercancia | 5.01.01.01.001 | eerr | 230 | 2026-06-07 12:07:16 |
| 25 | Costo de venta por mercancía | 5.01.01.01.001 | eerr | 240 | 2026-06-07 12:07:16 |
| 26 | Subtotal Costo de Ventas por Servicios | 5.01.02.01.001 | eerr | 260 | 2026-06-07 12:07:16 |
| 27 | Costo de venta por servicio del café | 5.01.02.01.001 | eerr | 270 | 2026-06-07 12:07:16 |
| 28 | Subtotal Costo de Ventas por Eventos | 5.01.03.01.001 | eerr | 290 | 2026-06-07 12:07:16 |
| 29 | Costo de ventas por eventos | 5.01.03.01.001 | eerr | 300 | 2026-06-07 12:07:16 |
| 30 | Utilidad Bruta por Venta de Mercancia y Taller | 4.01.01.01.001 | eerr | 330 | 2026-06-07 12:07:16 |
| 31 | Utilidad Bruta por Venta de Mercancia y Taller | 4.01.01.02.001 | eerr | 330 | 2026-06-07 12:07:16 |
| 32 | Utilidad Bruta por Venta de Mercancia y Taller | 4.01.01.03.001 | eerr | 330 | 2026-06-07 12:07:16 |
| 33 | Utilidad Bruta por Venta de Mercancia y Taller | 4.01.04.01.001 | eerr | 330 | 2026-06-07 12:07:16 |
| 34 | Utilidad Bruta por Venta de Mercancia y Taller | 5.01.01.01.001 | eerr | 330 | 2026-06-07 12:07:16 |
| 35 | Utilidad Bruta por Servicios | 4.01.02.01.001 | eerr | 340 | 2026-06-07 12:07:16 |
| 36 | Utilidad Bruta por Servicios | 5.01.02.01.001 | eerr | 340 | 2026-06-07 12:07:16 |
| 37 | Utilidad Bruta por Eventos | 4.01.03.01.001 | eerr | 350 | 2026-06-07 12:07:16 |
| 38 | Utilidad Bruta por Eventos | 5.01.03.01.001 | eerr | 350 | 2026-06-07 12:07:16 |
| 39 | Utilidad Bruta | 4.01.01.01.001 | eerr | 360 | 2026-06-07 12:07:16 |
| 40 | Utilidad Bruta | 4.01.01.02.001 | eerr | 360 | 2026-06-07 12:07:16 |
| 41 | Utilidad Bruta | 4.01.01.03.001 | eerr | 360 | 2026-06-07 12:07:16 |
| 42 | Utilidad Bruta | 4.01.02.01.001 | eerr | 360 | 2026-06-07 12:07:16 |
| 43 | Utilidad Bruta | 4.01.03.01.001 | eerr | 360 | 2026-06-07 12:07:16 |
| 44 | Utilidad Bruta | 4.01.04.01.001 | eerr | 360 | 2026-06-07 12:07:16 |
| 45 | Utilidad Bruta | 5.01.01.01.001 | eerr | 360 | 2026-06-07 12:07:16 |
| 46 | Utilidad Bruta | 5.01.02.01.001 | eerr | 360 | 2026-06-07 12:07:16 |
| 47 | Utilidad Bruta | 5.01.03.01.001 | eerr | 360 | 2026-06-07 12:07:16 |
| 48 | Total Gastos Operacionales | 6.01.01.01.001 | eerr | 380 | 2026-06-07 12:07:16 |
| 49 | Total Gastos Operacionales | 6.01.02.01.001 | eerr | 380 | 2026-06-07 12:07:16 |
| 50 | Total Gastos Operacionales | 6.01.02.01.002 | eerr | 380 | 2026-06-07 12:07:16 |
| 51 | Total Gastos Operacionales | 6.01.02.01.003 | eerr | 380 | 2026-06-07 12:07:16 |
| 52 | Total Gastos Operacionales | 6.01.02.01.008 | eerr | 380 | 2026-06-07 12:07:16 |
| 53 | Total Gastos Operacionales | 6.01.02.01.009 | eerr | 380 | 2026-06-07 12:07:16 |
| 54 | Total Gastos Operacionales | 6.01.02.01.006 | eerr | 380 | 2026-06-07 12:07:16 |
| 55 | Total Gastos Operacionales | 6.01.02.01.007 | eerr | 380 | 2026-06-07 12:07:16 |
| 56 | Total Gastos Operacionales | 6.01.03.01 | eerr | 380 | 2026-06-07 12:07:16 |
| 57 | Total Gastos Operacionales | 6.01.03.03 | eerr | 380 | 2026-06-07 12:07:16 |
| 58 | Total Gastos Operacionales | 6.01.03.03.002 | eerr | 380 | 2026-06-07 12:07:16 |
| 59 | Total Gastos Operacionales | 6.01.04.01.001 | eerr | 380 | 2026-06-07 12:07:16 |
| 60 | Total Gastos Operacionales | 6.01.05 | eerr | 380 | 2026-06-07 12:07:16 |
| 61 | Subtotal Gastos de Administración | 6.01.01.01.001 | eerr | 390 | 2026-06-07 12:07:16 |
| 62 | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | 6.01.01.01.001 | eerr | 400 | 2026-06-07 12:07:16 |
| 63 | Gastos de servicios de telefonía e internet | 6.01.01.01.002 | eerr | 410 | 2026-06-07 12:07:16 |
| 64 | Gastos de alquiler del local | 6.01.01.01.003 | eerr | 420 | 2026-06-07 12:07:16 |
| 65 | Gastos de Condominio | 6.01.01.01.004 | eerr | 430 | 2026-06-07 12:07:16 |
| 66 | Gastos de asistencia outsorsing | 6.01.01.01.005 | eerr | 440 | 2026-06-07 12:07:16 |
| 67 | Gastos de alquiler de bienes muebles | 6.01.01.01.006 | eerr | 450 | 2026-06-07 12:07:16 |
| 68 | Gastos de artículos de oficina | 6.01.01.01.007 | eerr | 460 | 2026-06-07 12:07:16 |
| 69 | Gastos de artículos de limpieza e higiene | 6.01.01.01.008 | eerr | 470 | 2026-06-07 12:07:16 |
| 70 | Gastos de alimentos y bebidas | 6.01.01.01.009 | eerr | 480 | 2026-06-07 12:07:16 |
| 71 | Gastos de envíos y encomiendas administrativas | 6.01.01.01.010 | eerr | 490 | 2026-06-07 12:07:16 |
| 72 | Gastos de honorarios profesionales | 6.01.01.01.011 | eerr | 500 | 2026-06-07 12:07:16 |
| 73 | Gastos de estacionamiento | 6.01.01.01.012 | eerr | 510 | 2026-06-07 12:07:16 |
| 74 | Gastos de gestoría | 6.01.01.01.013 | eerr | 520 | 2026-06-07 12:07:16 |
| 75 | Gastos legales | 6.01.01.01.014 | eerr | 530 | 2026-06-07 12:07:16 |
| 76 | Gastos de taxi, transporte y/o delivery | 6.01.01.01.015 | eerr | 540 | 2026-06-07 12:07:16 |
| 77 | Gastos de suministros para taller | 6.01.01.01.016 | eerr | 550 | 2026-06-07 12:07:16 |
| 78 | Gastos de suministros del café | 6.01.01.01.017 | eerr | 560 | 2026-06-07 12:07:16 |
| 79 | Gastos por fiestas, festejos y/o reuniones | 6.01.01.01.018 | eerr | 570 | 2026-06-07 12:07:16 |
| 80 | Gastos de vigilancia | 6.01.01.01.019 | eerr | 580 | 2026-06-07 12:07:16 |
| 81 | Gastos de retenciones no descontadas | 6.01.01.01.999 | eerr | 590 | 2026-06-07 12:07:16 |
| 82 | Mantenimiento y reparaciones | 6.01.01.02.001 | eerr | 600 | 2026-06-07 12:07:16 |
| 83 | Mantenimiento y reparaciones | 6.01.01.02.002 | eerr | 600 | 2026-06-07 12:07:16 |
| 84 | Mantenimiento y reparaciones | 6.01.01.02.003 | eerr | 600 | 2026-06-07 12:07:16 |
| 85 | Mantenimiento y reparaciones | 6.01.01.02.004 | eerr | 600 | 2026-06-07 12:07:16 |
| 86 | Mantenimiento y reparaciones | 6.01.01.02.005 | eerr | 600 | 2026-06-07 12:07:16 |
| 87 | Viáticos administrativos | 6.01.01.03.001 | eerr | 610 | 2026-06-07 12:07:16 |
| 88 | Viáticos administrativos | 6.01.01.03.002 | eerr | 610 | 2026-06-07 12:07:16 |
| 89 | Viáticos administrativos | 6.01.01.03.003 | eerr | 610 | 2026-06-07 12:07:16 |
| 90 | Viáticos administrativos | 6.01.01.03.004 | eerr | 610 | 2026-06-07 12:07:16 |
| 91 | Viáticos administrativos | 6.01.01.03.005 | eerr | 610 | 2026-06-07 12:07:16 |
| 92 | Gastos de seguro | 6.01.01.04 | eerr | 620 | 2026-06-07 12:07:16 |
| 93 | Gastos de impuestos, tasas y contribuciones | 6.01.01.05 | eerr | 630 | 2026-06-07 12:07:16 |
| 94 | Depreciaciones, deterioro y Amortización | 6.01.01.06.001 | eerr | 640 | 2026-06-07 12:07:16 |
| 95 | Depreciaciones, deterioro y Amortización | 6.01.01.06.002 | eerr | 640 | 2026-06-07 12:07:16 |
| 96 | Depreciaciones, deterioro y Amortización | 6.01.01.06.003 | eerr | 640 | 2026-06-07 12:07:16 |
| 97 | Depreciaciones, deterioro y Amortización | 6.01.01.06.004 | eerr | 640 | 2026-06-07 12:07:16 |
| 98 | Depreciaciones, deterioro y Amortización | 6.01.01.07.001 | eerr | 640 | 2026-06-07 12:07:16 |
| 99 | Depreciaciones, deterioro y Amortización | 6.01.01.07.002 | eerr | 640 | 2026-06-07 12:07:16 |
| 100 | Depreciaciones, deterioro y Amortización | 6.01.01.07.003 | eerr | 640 | 2026-06-07 12:07:16 |
| 101 | Depreciaciones, deterioro y Amortización | 6.01.01.07.004 | eerr | 640 | 2026-06-07 12:07:16 |
| 102 | Depreciaciones, deterioro y Amortización | 6.01.01.07.999 | eerr | 640 | 2026-06-07 12:07:16 |
| 103 | Depreciaciones, deterioro y Amortización | 6.01.01.08.001 | eerr | 640 | 2026-06-07 12:07:16 |
| 104 | Gastos Bancarios | 6.01.01.09 | eerr | 650 | 2026-06-07 12:07:16 |
| 105 | Gastos de intereses sobre préstamos | 6.01.01.10 | eerr | 660 | 2026-06-07 12:07:16 |
| 106 | Subtotal Gastos de Recursos Humanos | 6.01.02.01.001 | eerr | 680 | 2026-06-07 12:07:16 |
| 107 | Subtotal Gastos de Recursos Humanos | 6.01.02.01.002 | eerr | 680 | 2026-06-07 12:07:16 |
| 108 | Subtotal Gastos de Recursos Humanos | 6.01.02.01.003 | eerr | 680 | 2026-06-07 12:07:16 |
| 109 | Subtotal Gastos de Recursos Humanos | 6.01.02.01.008 | eerr | 680 | 2026-06-07 12:07:16 |
| 110 | Subtotal Gastos de Recursos Humanos | 6.01.02.01.009 | eerr | 680 | 2026-06-07 12:07:16 |
| 111 | Subtotal Gastos de Recursos Humanos | 6.01.02.01.006 | eerr | 680 | 2026-06-07 12:07:16 |
| 112 | Subtotal Gastos de Recursos Humanos | 6.01.02.01.007 | eerr | 680 | 2026-06-07 12:07:16 |
| 113 | Gastos de sueldos y salarios empleados y directivos | 6.01.02.01.001 | eerr | 690 | 2026-06-07 12:07:16 |
| 114 | Gastos de sueldos y salarios empleados y directivos | 6.01.02.01.002 | eerr | 690 | 2026-06-07 12:07:16 |
| 115 | Gastos de sueldos y salarios empleados y directivos | 6.01.02.01.003 | eerr | 690 | 2026-06-07 12:07:16 |
| 116 | Gastos de sueldos y salarios empleados y directivos | 6.01.02.01.008 | eerr | 690 | 2026-06-07 12:07:16 |
| 117 | Gastos de sueldos y salarios empleados y directivos | 6.01.02.01.009 | eerr | 690 | 2026-06-07 12:07:16 |
| 118 | Gastos de sueldos y salarios empleados y directivos | 6.01.02.01.006 | eerr | 690 | 2026-06-07 12:07:16 |
| 119 | Gastos de sueldos y salarios empleados y directivos | 6.01.02.01.007 | eerr | 690 | 2026-06-07 12:07:16 |
| 120 | Gastos de complementos empleados y directivos | 6.01.02.01.004 | eerr | 700 | 2026-06-07 12:07:16 |
| 121 | Gastos de complementos empleados y directivos | 6.01.02.01.005 | eerr | 700 | 2026-06-07 12:07:16 |
| 122 | Gastos de complementos empleados y directivos | 6.01.02.01.010 | eerr | 700 | 2026-06-07 12:07:16 |
| 123 | Gastos de complementos empleados y directivos | 6.01.02.01.011 | eerr | 700 | 2026-06-07 12:07:16 |
| 124 | Gastos de complementos empleados y directivos | 6.01.02.01.012 | eerr | 700 | 2026-06-07 12:07:16 |
| 125 | Gastos de personal externo | 6.01.02.01.999 | eerr | 710 | 2026-06-07 12:07:16 |
| 126 | Gastos de pasivos laborales vacaciones | 6.01.02.02.001 | eerr | 720 | 2026-06-07 12:07:16 |
| 127 | Gastos de pasivos laborales vacaciones | 6.01.02.02.002 | eerr | 720 | 2026-06-07 12:07:16 |
| 128 | Gastos de pasivos laborales vacaciones | 6.01.02.02.003 | eerr | 720 | 2026-06-07 12:07:16 |
| 129 | Gastos de pasivos laborales vacaciones | 6.01.02.02.004 | eerr | 720 | 2026-06-07 12:07:16 |
| 130 | Gastos de pasivos laborales utilidades | 6.01.02.02.005 | eerr | 730 | 2026-06-07 12:07:16 |
| 131 | Gastos de pasivos laborales utilidades | 6.01.02.02.006 | eerr | 730 | 2026-06-07 12:07:16 |
| 132 | Gastos de pasivos laborales utilidades | 6.01.02.02.007 | eerr | 730 | 2026-06-07 12:07:16 |
| 133 | Gastos de pasivos laborales utilidades | 6.01.02.02.008 | eerr | 730 | 2026-06-07 12:07:16 |
| 134 | Gastos de pasivos laborales prestaciones e intereses | 6.01.02.02.009 | eerr | 740 | 2026-06-07 12:07:16 |
| 135 | Gastos de pasivos laborales prestaciones e intereses | 6.01.02.02.010 | eerr | 740 | 2026-06-07 12:07:16 |
| 136 | Gastos de pasivos laborales prestaciones e intereses | 6.01.02.02.011 | eerr | 740 | 2026-06-07 12:07:16 |
| 137 | Gastos de pasivos laborales prestaciones e intereses | 6.01.02.02.012 | eerr | 740 | 2026-06-07 12:07:16 |
| 138 | Gastos de pasivos laborales prestaciones e intereses | 6.01.02.02.013 | eerr | 740 | 2026-06-07 12:07:16 |
| 139 | Gastos de pasivos laborales prestaciones e intereses | 6.01.02.02.014 | eerr | 740 | 2026-06-07 12:07:16 |
| 140 | Gastos de pasivos laborales prestaciones e intereses | 6.01.02.02.015 | eerr | 740 | 2026-06-07 12:07:16 |
| 141 | Gastos de pasivos laborales prestaciones e intereses | 6.01.02.02.016 | eerr | 740 | 2026-06-07 12:07:16 |
| 142 | Gastos de pasivos laborales aportes | 6.01.02.02.017 | eerr | 750 | 2026-06-07 12:07:16 |
| 143 | Gastos de pasivos laborales aportes | 6.01.02.02.018 | eerr | 750 | 2026-06-07 12:07:16 |
| 144 | Gastos de pasivos laborales aportes | 6.01.02.02.019 | eerr | 750 | 2026-06-07 12:07:16 |
| 145 | Gastos de pasivos laborales aportes | 6.01.02.02.020 | eerr | 750 | 2026-06-07 12:07:16 |
| 146 | Gastos de pasivos laborales bono de guardería | 6.01.02.02.021 | eerr | 760 | 2026-06-07 12:07:16 |
| 147 | Gastos de pasivos laborales HCM | 6.01.02.02.022 | eerr | 770 | 2026-06-07 12:07:16 |
| 148 | Gastos de salud y seguridad laboral | 6.01.02.03.001 | eerr | 780 | 2026-06-07 12:07:16 |
| 149 | Gastos de salud y seguridad laboral dotación | 6.01.02.03.002 | eerr | 790 | 2026-06-07 12:07:16 |
| 150 | Gastos de salud y seguridad laboral fiestas y agasajos | 6.01.02.03.003 | eerr | 800 | 2026-06-07 12:07:16 |
| 151 | Otros gastos de personal | 6.01.02.04 | eerr | 810 | 2026-06-07 12:07:16 |
| 152 | Subtotal Gastos de Comercialización y Logistica | 6.01.03.01 | eerr | 830 | 2026-06-07 12:07:16 |
| 153 | Subtotal Gastos de Comercialización y Logistica | 6.01.03.03 | eerr | 830 | 2026-06-07 12:07:16 |
| 154 | Subtotal Gastos de Comercialización y Logistica | 6.01.03.03.002 | eerr | 830 | 2026-06-07 12:07:16 |
| 155 | Gastos de viáticos comerciales | 6.01.03.01 | eerr | 840 | 2026-06-07 12:07:16 |
| 156 | Gastos de fletes y envios no asociados al costo | 6.01.03.02.001 | eerr | 850 | 2026-06-07 12:07:16 |
| 157 | Otros gastos no asociados al costo | 6.01.03.02.002 | eerr | 860 | 2026-06-07 12:07:16 |
| 158 | Otros gastos no asociados al costo | 6.01.03.02.003 | eerr | 860 | 2026-06-07 12:07:16 |
| 159 | Otros gastos no asociados al costo | 6.01.03.02.004 | eerr | 860 | 2026-06-07 12:07:16 |
| 160 | Otros gastos no asociados al costo | 6.01.03.02.005 | eerr | 860 | 2026-06-07 12:07:16 |
| 161 | Otros gastos no asociados al costo | 6.01.03.02.006 | eerr | 860 | 2026-06-07 12:07:16 |
| 162 | Otros gastos no asociados al costo | 6.01.03.02.007 | eerr | 860 | 2026-06-07 12:07:16 |
| 163 | Otros gastos no asociados al costo | 6.01.03.02.008 | eerr | 860 | 2026-06-07 12:07:16 |
| 164 | Otros gastos no asociados al costo | 6.01.03.02.009 | eerr | 860 | 2026-06-07 12:07:16 |
| 165 | Gastos por combustible | 6.01.03.04 | eerr | 870 | 2026-06-07 12:07:16 |
| 166 | Gastos de representación | 6.01.03.05.001 | eerr | 880 | 2026-06-07 12:07:16 |
| 167 | Gastos por garantia | 6.01.03.06.001 | eerr | 890 | 2026-06-07 12:07:16 |
| 168 | Gastos por suscripciones | 6.01.03.07.001 | eerr | 900 | 2026-06-07 12:07:16 |
| 169 | Gastos de Stand y/o ferias comerciales | 6.01.03.08 | eerr | 910 | 2026-06-07 12:07:16 |
| 170 | Subtotal Gastos de Mercadeo | 6.01.04.01.001 | eerr | 930 | 2026-06-07 12:07:16 |
| 171 | Gastos de redes sociales | 6.01.04.01.001 | eerr | 940 | 2026-06-07 12:07:16 |
| 172 | Gastos de medios publicitarios | 6.01.04.01.002 | eerr | 950 | 2026-06-07 12:07:16 |
| 173 | Otros gastos de publicidad y promoción | 6.01.04.01.003 | eerr | 960 | 2026-06-07 12:07:16 |
| 174 | Otros gastos de publicidad y promoción | 6.01.04.01.004 | eerr | 960 | 2026-06-07 12:07:16 |
| 175 | Otros gastos de publicidad y promoción | 6.01.04.01.005 | eerr | 960 | 2026-06-07 12:07:16 |
| 176 | Otros gastos de publicidad y promoción | 6.01.04.01.006 | eerr | 960 | 2026-06-07 12:07:16 |
| 177 | Gastos de patrocinio y donación | 6.01.04.02 | eerr | 970 | 2026-06-07 12:07:16 |
| 178 | Gastos de viáticos por eventos | 6.01.04.03.001 | eerr | 980 | 2026-06-07 12:07:16 |
| 179 | Gastos de materiales y servicios por eventos | 6.01.04.03.002 | eerr | 990 | 2026-06-07 12:07:16 |
| 180 | Gastos de alimentos y bebidas por eventos | 6.01.04.03.003 | eerr | 1000 | 2026-06-07 12:07:16 |
| 181 | Gastos de personal por eventos | 6.01.04.03.004 | eerr | 1010 | 2026-06-07 12:07:16 |
| 182 | Gastos de patrocinio, donación y/o obseq por eventos | 6.01.04.03.005 | eerr | 1020 | 2026-06-07 12:07:16 |
| 183 | Gastos de TI+I | 6.01.05 | eerr | 1040 | 2026-06-07 12:07:16 |
| 184 | Gastos de página web | 6.01.05.01.001 | eerr | 1050 | 2026-06-07 12:07:16 |
| 185 | Gastos de página web | 6.01.05.01.002 | eerr | 1050 | 2026-06-07 12:07:16 |
| 186 | Gastos de desarrollo | 6.01.05.02 | eerr | 1060 | 2026-06-07 12:07:16 |
| 187 | Utilidad antes de Comisiones por Ventas | 4.01.01.01.001 | eerr | 1090 | 2026-06-07 12:07:16 |
| 188 | Utilidad antes de Comisiones por Ventas | 4.01.01.02.001 | eerr | 1090 | 2026-06-07 12:07:16 |
| 189 | Utilidad antes de Comisiones por Ventas | 4.01.01.03.001 | eerr | 1090 | 2026-06-07 12:07:16 |
| 190 | Utilidad antes de Comisiones por Ventas | 4.01.02.01.001 | eerr | 1090 | 2026-06-07 12:07:16 |
| 191 | Utilidad antes de Comisiones por Ventas | 4.01.03.01.001 | eerr | 1090 | 2026-06-07 12:07:16 |
| 192 | Utilidad antes de Comisiones por Ventas | 4.01.04.01.001 | eerr | 1090 | 2026-06-07 12:07:16 |
| 193 | Utilidad antes de Comisiones por Ventas | 5.01.01.01.001 | eerr | 1090 | 2026-06-07 12:07:16 |
| 194 | Utilidad antes de Comisiones por Ventas | 5.01.02.01.001 | eerr | 1090 | 2026-06-07 12:07:16 |
| 195 | Utilidad antes de Comisiones por Ventas | 5.01.03.01.001 | eerr | 1090 | 2026-06-07 12:07:16 |
| 196 | Utilidad antes de Comisiones por Ventas | 6.01.01.01.001 | eerr | 1090 | 2026-06-07 12:07:16 |
| 197 | Utilidad antes de Comisiones por Ventas | 6.01.02.01.001 | eerr | 1090 | 2026-06-07 12:07:16 |
| 198 | Utilidad antes de Comisiones por Ventas | 6.01.02.01.002 | eerr | 1090 | 2026-06-07 12:07:16 |
| 199 | Utilidad antes de Comisiones por Ventas | 6.01.02.01.003 | eerr | 1090 | 2026-06-07 12:07:16 |
| 200 | Utilidad antes de Comisiones por Ventas | 6.01.02.01.008 | eerr | 1090 | 2026-06-07 12:07:16 |
| 201 | Utilidad antes de Comisiones por Ventas | 6.01.02.01.009 | eerr | 1090 | 2026-06-07 12:07:16 |
| 202 | Utilidad antes de Comisiones por Ventas | 6.01.02.01.006 | eerr | 1090 | 2026-06-07 12:07:16 |
| 203 | Utilidad antes de Comisiones por Ventas | 6.01.02.01.007 | eerr | 1090 | 2026-06-07 12:07:16 |
| 204 | Utilidad antes de Comisiones por Ventas | 6.01.03.01 | eerr | 1090 | 2026-06-07 12:07:16 |
| 205 | Utilidad antes de Comisiones por Ventas | 6.01.03.03 | eerr | 1090 | 2026-06-07 12:07:16 |
| 206 | Utilidad antes de Comisiones por Ventas | 6.01.03.03.002 | eerr | 1090 | 2026-06-07 12:07:16 |
| 207 | Utilidad antes de Comisiones por Ventas | 6.01.04.01.001 | eerr | 1090 | 2026-06-07 12:07:16 |
| 208 | Utilidad antes de Comisiones por Ventas | 6.01.05 | eerr | 1090 | 2026-06-07 12:07:16 |
| 209 | Gastos de comisiones por ventas | 6.01.03.03 | eerr | 1100 | 2026-06-07 12:07:16 |
| 210 | Gastos de comisiones por ventas taller | 6.01.03.03.002 | eerr | 1110 | 2026-06-07 12:07:16 |
| 211 | Utilidad después de Comisiones por Ventas | 4.01.01.01.001 | eerr | 1120 | 2026-06-07 12:07:16 |
| 212 | Utilidad después de Comisiones por Ventas | 4.01.01.02.001 | eerr | 1120 | 2026-06-07 12:07:16 |
| 213 | Utilidad después de Comisiones por Ventas | 4.01.01.03.001 | eerr | 1120 | 2026-06-07 12:07:16 |
| 214 | Utilidad después de Comisiones por Ventas | 4.01.02.01.001 | eerr | 1120 | 2026-06-07 12:07:16 |
| 215 | Utilidad después de Comisiones por Ventas | 4.01.03.01.001 | eerr | 1120 | 2026-06-07 12:07:16 |
| 216 | Utilidad después de Comisiones por Ventas | 4.01.04.01.001 | eerr | 1120 | 2026-06-07 12:07:16 |
| 217 | Utilidad después de Comisiones por Ventas | 5.01.01.01.001 | eerr | 1120 | 2026-06-07 12:07:16 |
| 218 | Utilidad después de Comisiones por Ventas | 5.01.02.01.001 | eerr | 1120 | 2026-06-07 12:07:16 |
| 219 | Utilidad después de Comisiones por Ventas | 5.01.03.01.001 | eerr | 1120 | 2026-06-07 12:07:16 |
| 220 | Utilidad después de Comisiones por Ventas | 6.01.01.01.001 | eerr | 1120 | 2026-06-07 12:07:16 |
| 221 | Utilidad después de Comisiones por Ventas | 6.01.02.01.001 | eerr | 1120 | 2026-06-07 12:07:16 |
| 222 | Utilidad después de Comisiones por Ventas | 6.01.02.01.002 | eerr | 1120 | 2026-06-07 12:07:16 |
| 223 | Utilidad después de Comisiones por Ventas | 6.01.02.01.003 | eerr | 1120 | 2026-06-07 12:07:16 |
| 224 | Utilidad después de Comisiones por Ventas | 6.01.02.01.008 | eerr | 1120 | 2026-06-07 12:07:16 |
| 225 | Utilidad después de Comisiones por Ventas | 6.01.02.01.009 | eerr | 1120 | 2026-06-07 12:07:16 |
| 226 | Utilidad después de Comisiones por Ventas | 6.01.02.01.006 | eerr | 1120 | 2026-06-07 12:07:16 |
| 227 | Utilidad después de Comisiones por Ventas | 6.01.02.01.007 | eerr | 1120 | 2026-06-07 12:07:16 |
| 228 | Utilidad después de Comisiones por Ventas | 6.01.03.01 | eerr | 1120 | 2026-06-07 12:07:16 |
| 229 | Utilidad después de Comisiones por Ventas | 6.01.03.03 | eerr | 1120 | 2026-06-07 12:07:16 |
| 230 | Utilidad después de Comisiones por Ventas | 6.01.03.03.002 | eerr | 1120 | 2026-06-07 12:07:16 |
| 231 | Utilidad después de Comisiones por Ventas | 6.01.04.01.001 | eerr | 1120 | 2026-06-07 12:07:16 |
| 232 | Utilidad después de Comisiones por Ventas | 6.01.05 | eerr | 1120 | 2026-06-07 12:07:16 |
| 233 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 4.01.01.01.001 | eerr | 1130 | 2026-06-07 12:07:16 |
| 234 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 4.01.01.02.001 | eerr | 1130 | 2026-06-07 12:07:16 |
| 235 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 4.01.01.03.001 | eerr | 1130 | 2026-06-07 12:07:16 |
| 236 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 4.01.02.01.001 | eerr | 1130 | 2026-06-07 12:07:16 |
| 237 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 4.01.03.01.001 | eerr | 1130 | 2026-06-07 12:07:16 |
| 238 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 4.01.04.01.001 | eerr | 1130 | 2026-06-07 12:07:16 |
| 239 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 5.01.01.01.001 | eerr | 1130 | 2026-06-07 12:07:16 |
| 240 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 5.01.02.01.001 | eerr | 1130 | 2026-06-07 12:07:16 |
| 241 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 5.01.03.01.001 | eerr | 1130 | 2026-06-07 12:07:16 |
| 242 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.01.01.001 | eerr | 1130 | 2026-06-07 12:07:16 |
| 243 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.02.01.001 | eerr | 1130 | 2026-06-07 12:07:16 |
| 244 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.02.01.002 | eerr | 1130 | 2026-06-07 12:07:16 |
| 245 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.02.01.003 | eerr | 1130 | 2026-06-07 12:07:16 |
| 246 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.02.01.008 | eerr | 1130 | 2026-06-07 12:07:16 |
| 247 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.02.01.009 | eerr | 1130 | 2026-06-07 12:07:16 |
| 248 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.02.01.006 | eerr | 1130 | 2026-06-07 12:07:16 |
| 249 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.02.01.007 | eerr | 1130 | 2026-06-07 12:07:16 |
| 250 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.03.01 | eerr | 1130 | 2026-06-07 12:07:16 |
| 251 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.03.03 | eerr | 1130 | 2026-06-07 12:07:16 |
| 252 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.03.03.002 | eerr | 1130 | 2026-06-07 12:07:16 |
| 253 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.04.01.001 | eerr | 1130 | 2026-06-07 12:07:16 |
| 254 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.05 | eerr | 1130 | 2026-06-07 12:07:16 |
| 255 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.01.10 | eerr | 1130 | 2026-06-07 12:07:16 |
| 256 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.01.05 | eerr | 1130 | 2026-06-07 12:07:16 |
| 257 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.01.06.001 | eerr | 1130 | 2026-06-07 12:07:16 |
| 258 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.01.06.002 | eerr | 1130 | 2026-06-07 12:07:16 |
| 259 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.01.06.003 | eerr | 1130 | 2026-06-07 12:07:16 |
| 260 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.01.06.004 | eerr | 1130 | 2026-06-07 12:07:16 |
| 261 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.01.07.001 | eerr | 1130 | 2026-06-07 12:07:16 |
| 262 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.01.07.002 | eerr | 1130 | 2026-06-07 12:07:16 |
| 263 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.01.07.003 | eerr | 1130 | 2026-06-07 12:07:16 |
| 264 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.01.07.004 | eerr | 1130 | 2026-06-07 12:07:16 |
| 265 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.01.07.999 | eerr | 1130 | 2026-06-07 12:07:16 |
| 266 | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 6.01.01.08.001 | eerr | 1130 | 2026-06-07 12:07:16 |
| 267 | Utilidad antes de Intereses e Impuestos (EBIT) | 4.01.01.01.001 | eerr | 1140 | 2026-06-07 12:07:16 |
| 268 | Utilidad antes de Intereses e Impuestos (EBIT) | 4.01.01.02.001 | eerr | 1140 | 2026-06-07 12:07:16 |
| 269 | Utilidad antes de Intereses e Impuestos (EBIT) | 4.01.01.03.001 | eerr | 1140 | 2026-06-07 12:07:16 |
| 270 | Utilidad antes de Intereses e Impuestos (EBIT) | 4.01.02.01.001 | eerr | 1140 | 2026-06-07 12:07:16 |
| 271 | Utilidad antes de Intereses e Impuestos (EBIT) | 4.01.03.01.001 | eerr | 1140 | 2026-06-07 12:07:16 |
| 272 | Utilidad antes de Intereses e Impuestos (EBIT) | 4.01.04.01.001 | eerr | 1140 | 2026-06-07 12:07:16 |
| 273 | Utilidad antes de Intereses e Impuestos (EBIT) | 5.01.01.01.001 | eerr | 1140 | 2026-06-07 12:07:16 |
| 274 | Utilidad antes de Intereses e Impuestos (EBIT) | 5.01.02.01.001 | eerr | 1140 | 2026-06-07 12:07:16 |
| 275 | Utilidad antes de Intereses e Impuestos (EBIT) | 5.01.03.01.001 | eerr | 1140 | 2026-06-07 12:07:16 |
| 276 | Utilidad antes de Intereses e Impuestos (EBIT) | 6.01.01.01.001 | eerr | 1140 | 2026-06-07 12:07:16 |
| 277 | Utilidad antes de Intereses e Impuestos (EBIT) | 6.01.02.01.001 | eerr | 1140 | 2026-06-07 12:07:16 |
| 278 | Utilidad antes de Intereses e Impuestos (EBIT) | 6.01.02.01.002 | eerr | 1140 | 2026-06-07 12:07:16 |
| 279 | Utilidad antes de Intereses e Impuestos (EBIT) | 6.01.02.01.003 | eerr | 1140 | 2026-06-07 12:07:16 |
| 280 | Utilidad antes de Intereses e Impuestos (EBIT) | 6.01.02.01.008 | eerr | 1140 | 2026-06-07 12:07:16 |
| 281 | Utilidad antes de Intereses e Impuestos (EBIT) | 6.01.02.01.009 | eerr | 1140 | 2026-06-07 12:07:16 |
| 282 | Utilidad antes de Intereses e Impuestos (EBIT) | 6.01.02.01.006 | eerr | 1140 | 2026-06-07 12:07:16 |
| 283 | Utilidad antes de Intereses e Impuestos (EBIT) | 6.01.02.01.007 | eerr | 1140 | 2026-06-07 12:07:16 |
| 284 | Utilidad antes de Intereses e Impuestos (EBIT) | 6.01.03.01 | eerr | 1140 | 2026-06-07 12:07:16 |
| 285 | Utilidad antes de Intereses e Impuestos (EBIT) | 6.01.03.03 | eerr | 1140 | 2026-06-07 12:07:16 |
| 286 | Utilidad antes de Intereses e Impuestos (EBIT) | 6.01.03.03.002 | eerr | 1140 | 2026-06-07 12:07:16 |
| 287 | Utilidad antes de Intereses e Impuestos (EBIT) | 6.01.04.01.001 | eerr | 1140 | 2026-06-07 12:07:16 |
| 288 | Utilidad antes de Intereses e Impuestos (EBIT) | 6.01.05 | eerr | 1140 | 2026-06-07 12:07:16 |
| 289 | Utilidad antes de Intereses e Impuestos (EBIT) | 6.01.01.10 | eerr | 1140 | 2026-06-07 12:07:16 |
| 290 | Utilidad antes de Intereses e Impuestos (EBIT) | 6.01.01.05 | eerr | 1140 | 2026-06-07 12:07:16 |
| 291 | Otros Gastos no Operacionales | 6.02.01.01.001 | eerr | 1160 | 2026-06-07 12:07:16 |
| 292 | Otros Gastos no Operacionales | 6.02.01.01.007 | eerr | 1160 | 2026-06-07 12:07:16 |
| 293 | Otros Gastos no Operacionales | 6.02.01.01.008 | eerr | 1160 | 2026-06-07 12:07:16 |
| 294 | Faltante en Ventas | 6.02.01.01.001 | eerr | 1170 | 2026-06-07 12:07:16 |
| 295 | Pérdida en venta de activos | 6.02.01.01.002 | eerr | 1180 | 2026-06-07 12:07:16 |
| 296 | Pérdida en siniestro de activos | 6.02.01.01.003 | eerr | 1190 | 2026-06-07 12:07:16 |
| 297 | Pérdida en tasa cambiaria | 6.02.01.01.004 | eerr | 1200 | 2026-06-07 12:07:16 |
| 298 | Pérdida por diferencia en pagos | 6.02.01.01.005 | eerr | 1210 | 2026-06-07 12:07:16 |
| 299 | Multas | 6.02.01.01.006 | eerr | 1220 | 2026-06-07 12:07:16 |
| 300 | Faltante y deterioro de inventarios | 6.02.01.01.007 | eerr | 1230 | 2026-06-07 12:07:16 |
| 301 | Faltante y deterioro de inventarios | 6.02.01.01.008 | eerr | 1230 | 2026-06-07 12:07:16 |
| 302 | Total Gastos Operacionales y No Operacionales | 6.01.01.01.001 | eerr | 1240 | 2026-06-07 12:07:16 |
| 303 | Total Gastos Operacionales y No Operacionales | 6.01.02.01.001 | eerr | 1240 | 2026-06-07 12:07:16 |
| 304 | Total Gastos Operacionales y No Operacionales | 6.01.02.01.002 | eerr | 1240 | 2026-06-07 12:07:16 |
| 305 | Total Gastos Operacionales y No Operacionales | 6.01.02.01.003 | eerr | 1240 | 2026-06-07 12:07:16 |
| 306 | Total Gastos Operacionales y No Operacionales | 6.01.02.01.008 | eerr | 1240 | 2026-06-07 12:07:16 |
| 307 | Total Gastos Operacionales y No Operacionales | 6.01.02.01.009 | eerr | 1240 | 2026-06-07 12:07:16 |
| 308 | Total Gastos Operacionales y No Operacionales | 6.01.02.01.006 | eerr | 1240 | 2026-06-07 12:07:16 |
| 309 | Total Gastos Operacionales y No Operacionales | 6.01.02.01.007 | eerr | 1240 | 2026-06-07 12:07:16 |
| 310 | Total Gastos Operacionales y No Operacionales | 6.01.03.01 | eerr | 1240 | 2026-06-07 12:07:16 |
| 311 | Total Gastos Operacionales y No Operacionales | 6.01.03.03 | eerr | 1240 | 2026-06-07 12:07:16 |
| 312 | Total Gastos Operacionales y No Operacionales | 6.01.03.03.002 | eerr | 1240 | 2026-06-07 12:07:16 |
| 313 | Total Gastos Operacionales y No Operacionales | 6.01.04.01.001 | eerr | 1240 | 2026-06-07 12:07:16 |
| 314 | Total Gastos Operacionales y No Operacionales | 6.01.05 | eerr | 1240 | 2026-06-07 12:07:16 |
| 315 | Total Gastos Operacionales y No Operacionales | 6.02.01.01.001 | eerr | 1240 | 2026-06-07 12:07:16 |
| 316 | Total Gastos Operacionales y No Operacionales | 6.02.01.01.007 | eerr | 1240 | 2026-06-07 12:07:16 |
| 317 | Total Gastos Operacionales y No Operacionales | 6.02.01.01.008 | eerr | 1240 | 2026-06-07 12:07:16 |
| 318 | Otros Ingresos no Operacionales | 4.02.01.01.001 | eerr | 1250 | 2026-06-07 12:07:16 |
| 319 | Ingresos por alquileres | 4.02.01.01.001 | eerr | 1260 | 2026-06-07 12:07:16 |
| 320 | Ingresos por intereses | 4.02.01.01.002 | eerr | 1270 | 2026-06-07 12:07:16 |
| 321 | Ingresos por comisiones | 4.02.01.01.003 | eerr | 1280 | 2026-06-07 12:07:16 |
| 322 | Ingresos por servicios administrativos | 4.02.01.01.004 | eerr | 1290 | 2026-06-07 12:07:16 |
| 323 | Sobrante en ventas | 4.02.01.01.005 | eerr | 1300 | 2026-06-07 12:07:16 |
| 324 | Sobrante de inventarios | 4.02.01.01.006 | eerr | 1310 | 2026-06-07 12:07:16 |
| 325 | Ganancia en venta de activos | 4.02.01.01.007 | eerr | 1320 | 2026-06-07 12:07:16 |
| 326 | Ganancia por tasa cambiaria | 4.02.01.01.008 | eerr | 1330 | 2026-06-07 12:07:16 |
| 327 | Ganancia por diferencias en pagos | 4.02.01.01.009 | eerr | 1340 | 2026-06-07 12:07:16 |
| 328 | Utilidad Neta | 4.01.01.01.001 | eerr | 1370 | 2026-06-07 12:07:16 |
| 329 | Utilidad Neta | 4.01.01.02.001 | eerr | 1370 | 2026-06-07 12:07:16 |
| 330 | Utilidad Neta | 4.01.01.03.001 | eerr | 1370 | 2026-06-07 12:07:16 |
| 331 | Utilidad Neta | 4.01.02.01.001 | eerr | 1370 | 2026-06-07 12:07:16 |
| 332 | Utilidad Neta | 4.01.03.01.001 | eerr | 1370 | 2026-06-07 12:07:16 |
| 333 | Utilidad Neta | 4.01.04.01.001 | eerr | 1370 | 2026-06-07 12:07:16 |
| 334 | Utilidad Neta | 5.01.01.01.001 | eerr | 1370 | 2026-06-07 12:07:16 |
| 335 | Utilidad Neta | 5.01.02.01.001 | eerr | 1370 | 2026-06-07 12:07:16 |
| 336 | Utilidad Neta | 5.01.03.01.001 | eerr | 1370 | 2026-06-07 12:07:16 |
| 337 | Utilidad Neta | 6.01.01.01.001 | eerr | 1370 | 2026-06-07 12:07:16 |
| 338 | Utilidad Neta | 6.01.02.01.001 | eerr | 1370 | 2026-06-07 12:07:16 |
| 339 | Utilidad Neta | 6.01.02.01.002 | eerr | 1370 | 2026-06-07 12:07:16 |
| 340 | Utilidad Neta | 6.01.02.01.003 | eerr | 1370 | 2026-06-07 12:07:16 |
| 341 | Utilidad Neta | 6.01.02.01.008 | eerr | 1370 | 2026-06-07 12:07:16 |
| 342 | Utilidad Neta | 6.01.02.01.009 | eerr | 1370 | 2026-06-07 12:07:16 |
| 343 | Utilidad Neta | 6.01.02.01.006 | eerr | 1370 | 2026-06-07 12:07:16 |
| 344 | Utilidad Neta | 6.01.02.01.007 | eerr | 1370 | 2026-06-07 12:07:16 |
| 345 | Utilidad Neta | 6.01.03.01 | eerr | 1370 | 2026-06-07 12:07:16 |
| 346 | Utilidad Neta | 6.01.03.03 | eerr | 1370 | 2026-06-07 12:07:16 |
| 347 | Utilidad Neta | 6.01.03.03.002 | eerr | 1370 | 2026-06-07 12:07:16 |
| 348 | Utilidad Neta | 6.01.04.01.001 | eerr | 1370 | 2026-06-07 12:07:16 |
| 349 | Utilidad Neta | 6.01.05 | eerr | 1370 | 2026-06-07 12:07:16 |
| 350 | Utilidad Neta | 6.02.01.01.001 | eerr | 1370 | 2026-06-07 12:07:16 |
| 351 | Utilidad Neta | 6.02.01.01.007 | eerr | 1370 | 2026-06-07 12:07:16 |
| 352 | Utilidad Neta | 6.02.01.01.008 | eerr | 1370 | 2026-06-07 12:07:16 |
| 353 | Utilidad Neta | 4.02.01.01.001 | eerr | 1370 | 2026-06-07 12:07:16 |
| 354 | ISLR | 6.01.01.01.001 | eerr | 1380 | 2026-06-07 12:07:16 |
| 355 | ISLR | 6.01.02.01.001 | eerr | 1380 | 2026-06-07 12:07:16 |
| 356 | ISLR | 6.01.02.01.002 | eerr | 1380 | 2026-06-07 12:07:16 |
| 357 | ISLR | 6.01.02.01.003 | eerr | 1380 | 2026-06-07 12:07:16 |
| 358 | ISLR | 6.01.02.01.008 | eerr | 1380 | 2026-06-07 12:07:16 |
| 359 | ISLR | 6.01.02.01.009 | eerr | 1380 | 2026-06-07 12:07:16 |
| 360 | ISLR | 6.01.02.01.006 | eerr | 1380 | 2026-06-07 12:07:16 |
| 361 | ISLR | 6.01.02.01.007 | eerr | 1380 | 2026-06-07 12:07:16 |
| 362 | ISLR | 6.01.03.01 | eerr | 1380 | 2026-06-07 12:07:16 |
| 363 | ISLR | 6.01.03.03 | eerr | 1380 | 2026-06-07 12:07:16 |
| 364 | ISLR | 6.01.03.03.002 | eerr | 1380 | 2026-06-07 12:07:16 |
| 365 | ISLR | 6.01.04.01.001 | eerr | 1380 | 2026-06-07 12:07:16 |
| 366 | ISLR | 6.01.05 | eerr | 1380 | 2026-06-07 12:07:16 |
| 367 | ISLR | 6.02.01.01.001 | eerr | 1380 | 2026-06-07 12:07:16 |
| 368 | ISLR | 6.02.01.01.007 | eerr | 1380 | 2026-06-07 12:07:16 |
| 369 | ISLR | 6.02.01.01.008 | eerr | 1380 | 2026-06-07 12:07:16 |
| 370 | Utilidad Neta despues de ISLR | 4.01.01.01.001 | eerr | 1390 | 2026-06-07 12:07:16 |
| 371 | Utilidad Neta despues de ISLR | 4.01.01.02.001 | eerr | 1390 | 2026-06-07 12:07:16 |
| 372 | Utilidad Neta despues de ISLR | 4.01.01.03.001 | eerr | 1390 | 2026-06-07 12:07:16 |
| 373 | Utilidad Neta despues de ISLR | 4.01.02.01.001 | eerr | 1390 | 2026-06-07 12:07:16 |
| 374 | Utilidad Neta despues de ISLR | 4.01.03.01.001 | eerr | 1390 | 2026-06-07 12:07:16 |
| 375 | Utilidad Neta despues de ISLR | 4.01.04.01.001 | eerr | 1390 | 2026-06-07 12:07:16 |
| 376 | Utilidad Neta despues de ISLR | 5.01.01.01.001 | eerr | 1390 | 2026-06-07 12:07:16 |
| 377 | Utilidad Neta despues de ISLR | 5.01.02.01.001 | eerr | 1390 | 2026-06-07 12:07:16 |
| 378 | Utilidad Neta despues de ISLR | 5.01.03.01.001 | eerr | 1390 | 2026-06-07 12:07:16 |
| 379 | Utilidad Neta despues de ISLR | 6.01.01.01.001 | eerr | 1390 | 2026-06-07 12:07:16 |
| 380 | Utilidad Neta despues de ISLR | 6.01.02.01.001 | eerr | 1390 | 2026-06-07 12:07:16 |
| 381 | Utilidad Neta despues de ISLR | 6.01.02.01.002 | eerr | 1390 | 2026-06-07 12:07:16 |
| 382 | Utilidad Neta despues de ISLR | 6.01.02.01.003 | eerr | 1390 | 2026-06-07 12:07:16 |
| 383 | Utilidad Neta despues de ISLR | 6.01.02.01.008 | eerr | 1390 | 2026-06-07 12:07:16 |
| 384 | Utilidad Neta despues de ISLR | 6.01.02.01.009 | eerr | 1390 | 2026-06-07 12:07:16 |
| 385 | Utilidad Neta despues de ISLR | 6.01.02.01.006 | eerr | 1390 | 2026-06-07 12:07:16 |
| 386 | Utilidad Neta despues de ISLR | 6.01.02.01.007 | eerr | 1390 | 2026-06-07 12:07:16 |
| 387 | Utilidad Neta despues de ISLR | 6.01.03.01 | eerr | 1390 | 2026-06-07 12:07:16 |
| 388 | Utilidad Neta despues de ISLR | 6.01.03.03 | eerr | 1390 | 2026-06-07 12:07:16 |
| 389 | Utilidad Neta despues de ISLR | 6.01.03.03.002 | eerr | 1390 | 2026-06-07 12:07:16 |
| 390 | Utilidad Neta despues de ISLR | 6.01.04.01.001 | eerr | 1390 | 2026-06-07 12:07:16 |
| 391 | Utilidad Neta despues de ISLR | 6.01.05 | eerr | 1390 | 2026-06-07 12:07:16 |
| 392 | Utilidad Neta despues de ISLR | 6.02.01.01.001 | eerr | 1390 | 2026-06-07 12:07:16 |
| 393 | Utilidad Neta despues de ISLR | 6.02.01.01.007 | eerr | 1390 | 2026-06-07 12:07:16 |
| 394 | Utilidad Neta despues de ISLR | 6.02.01.01.008 | eerr | 1390 | 2026-06-07 12:07:16 |
| 395 | Utilidad Neta despues de ISLR | 4.02.01.01.001 | eerr | 1390 | 2026-06-07 12:07:16 |

---

## 2. EXPORT COMPLETO DE mapping
Resultados de la consulta: `SELECT odoo_code, odoo_name, partida, sign, income_type FROM mapping ORDER BY odoo_code`

Total registros en `mapping`: **717**

| Código Odoo (odoo_code) | Nombre Odoo (odoo_name) | Partida EERR (partida) | Signo (sign) | Tipo Ingreso (income_type) |
| --- | --- | --- | --- | --- |
| 1.01 | Activo Corriente | Activo Corriente | 1 | NULL |
| 1.01.01 | Cajas | Cajas | 1 | NULL |
| 1.01.01.01 | Cajas en Bolivares | Cajas en Bolivares | 1 | NULL |
| 1.01.01.01.001 | Caja principal en Bs. | Caja principal en Bs. | 1 | NULL |
| 1.01.01.02 | Cajas en Divisas | Cajas en Divisas | 1 | NULL |
| 1.01.01.02.001 | Caja principal en $ | Caja principal en $ | 1 | NULL |
| 1.01.01.02.002 | Caja principal en euros cambio $ | Caja principal en euros cambio $ | 1 | NULL |
| 1.01.01.02.003 | Caja principal en pesos cambio $ | Caja principal en pesos cambio $ | 1 | NULL |
| 1.01.02 | Fondos | Fondos | 1 | NULL |
| 1.01.02.01 | Fondos en Bolivares | Fondos en Bolivares | 1 | NULL |
| 1.01.02.01.001 | Fondo de caja en tienda en Bs. Suc Rodeo | Fondo de caja en tienda en Bs. Suc Rodeo | 1 | NULL |
| 1.01.02.01.002 | Fondo de caja en tienda en Bs. Suc Piedemonte | Fondo de caja en tienda en Bs. Suc Piedemonte | 1 | NULL |
| 1.01.02.01.003 | Fondo de caja en tienda en Bs. Suc Terracota | Fondo de caja en tienda en Bs. Suc Terracota | 1 | NULL |
| 1.01.02.01.004 | Fondo de caja en tienda en Bs. Suc Barinas | Fondo de caja en tienda en Bs. Suc Barinas | 1 | NULL |
| 1.01.02.01.005 | Fondo de caja en tienda en Bs. Suc Los Naranjos | Fondo de caja en tienda en Bs. Suc Los Naranjos | 1 | NULL |
| 1.01.02.02 | Fondos en Divisas | Fondos en Divisas | 1 | NULL |
| 1.01.02.02.001 | Fondo de caja en tienda en $ Suc Rodeo | Fondo de caja en tienda en $ Suc Rodeo | 1 | NULL |
| 1.01.02.02.002 | Fondo de caja en tienda en $ Suc Piedemonte | Fondo de caja en tienda en $ Suc Piedemonte | 1 | NULL |
| 1.01.02.02.003 | Fondo de caja en tienda en $ Suc Terracota | Fondo de caja en tienda en $ Suc Terracota | 1 | NULL |
| 1.01.02.02.004 | Fondo de caja en tienda en $ Suc Barinas | Fondo de caja en tienda en $ Suc Barinas | 1 | NULL |
| 1.01.02.02.005 | Fondo de caja en tienda en $ Suc Los Naranjos | Fondo de caja en tienda en $ Suc Los Naranjos | 1 | NULL |
| 1.01.02.02.011 | Fondo de caja en tienda en euros cambio $ Suc Rodeo | Fondo de caja en tienda en euros cambio $ Suc Rodeo | 1 | NULL |
| 1.01.02.02.012 | Fondo de caja en tienda en euros cambio $ Suc Piedemonte | Fondo de caja en tienda en euros cambio $ Suc Piedemonte | 1 | NULL |
| 1.01.02.02.013 | Fondo de caja en tienda en euros cambio $ Suc Terracota | Fondo de caja en tienda en euros cambio $ Suc Terracota | 1 | NULL |
| 1.01.02.02.014 | Fondo de caja en tienda en euros cambio $ Suc Barinas | Fondo de caja en tienda en euros cambio $ Suc Barinas | 1 | NULL |
| 1.01.02.02.015 | Fondo de caja en tienda en euros cambio $ Suc Los Naranjos | Fondo de caja en tienda en euros cambio $ Suc Los Naranjos | 1 | NULL |
| 1.01.02.02.021 | Fondo de caja en tienda en pesos cambio $ Suc Rodeo | Fondo de caja en tienda en pesos cambio $ Suc Rodeo | 1 | NULL |
| 1.01.02.02.022 | Fondo de caja en tienda en pesos cambio $ Suc Piedemonte | Fondo de caja en tienda en pesos cambio $ Suc Piedemonte | 1 | NULL |
| 1.01.02.02.023 | Fondo de caja en tienda en pesos cambio $ Suc Terracota | Fondo de caja en tienda en pesos cambio $ Suc Terracota | 1 | NULL |
| 1.01.02.02.024 | Fondo de caja en tienda en pesos cambio $ Suc Barinas | Fondo de caja en tienda en pesos cambio $ Suc Barinas | 1 | NULL |
| 1.01.02.02.025 | Fondo de caja en tienda en pesos cambio $ Suc Los Naranjos | Fondo de caja en tienda en pesos cambio $ Suc Los Naranjos | 1 | NULL |
| 1.01.02.02.031 | Fondo de caja en mayor CCS en $ | Fondo de caja en mayor CCS en $ | 1 | NULL |
| 1.01.02.02.041 | Fondo de caja en mayor CCS en euros cambio $ | Fondo de caja en mayor CCS en euros cambio $ | 1 | NULL |
| 1.01.03 | Bancos | Bancos | 1 | NULL |
| 1.01.03.01 | Bancos en Bolivares | Bancos en Bolivares | 1 | NULL |
| 1.01.03.01.001 | Banco Mercantil | Banco Mercantil | 1 | NULL |
| 1.01.03.01.002 | Banco Banesco | Banco Banesco | 1 | NULL |
| 1.01.03.01.003 | Banco de Venezuela | Banco de Venezuela | 1 | NULL |
| 1.01.03.01.004 | Banco Venezolano de Credito | Banco Venezolano de Credito | 1 | NULL |
| 1.01.03.01.005 | Banco del Tesoro | Banco del Tesoro | 1 | NULL |
| 1.01.03.01.006 | Bancamiga Cuenta Corriente | Bancamiga Cuenta Corriente | 1 | NULL |
| 1.01.03.01.007 | Banco Provincial | Banco Provincial | 1 | NULL |
| 1.01.03.01.008 | Banco Nacional de Crédito BNC | Banco Nacional de Crédito BNC | 1 | NULL |
| 1.01.03.01.011 | Banco Bancamiga Sr Gilberto | Banco Bancamiga Sr Gilberto | 1 | NULL |
| 1.01.03.01.012 | Banco BNC Sr Gilberto | Banco BNC Sr Gilberto | 1 | NULL |
| 1.01.03.01.998 | Banco transitorio migración Terracota | Banco transitorio migración Terracota | 1 | NULL |
| 1.01.03.01.999 | Banco transitorio migración Barinas | Banco transitorio migración Barinas | 1 | NULL |
| 1.01.03.02 | Bancos en Divisas | Bancos en Divisas | 1 | NULL |
| 1.01.03.02.001 | Bank Of America | Bank Of America | 1 | NULL |
| 1.01.03.02.002 | Banesco Panamá UX | Banesco Panamá UX | 1 | NULL |
| 1.01.03.02.003 | Banco Mercantil Cuenta en $ | Banco Mercantil Cuenta en $ | 1 | NULL |
| 1.01.03.02.004 | Paypal | Paypal | 1 | NULL |
| 1.01.03.02.005 | Criptomonedas USDT | Criptomonedas USDT | 1 | NULL |
| 1.01.03.02.006 | Chase Bank, UX GROUP LLC | Chase Bank, UX GROUP LLC | 1 | NULL |
| 1.01.03.02.007 | Bancamiga Cash USD | Bancamiga Cash USD | 1 | NULL |
| 1.01.03.02.008 | Bancamiga Moneda Extranjera USD | Bancamiga Moneda Extranjera USD | 1 | NULL |
| 1.01.03.02.009 | Bancamiga Sr Gilberto Cash USD | Bancamiga Sr Gilberto Cash USD | 1 | NULL |
| 1.01.03.02.010 | BNC Cash USD | BNC Cash USD | 1 | NULL |
| 1.01.03.02.011 | Amerant Camilo | Amerant Camilo | 1 | NULL |
| 1.01.03.02.012 | Mercantil Panamá Ultrax | Mercantil Panamá Ultrax | 1 | NULL |
| 1.01.03.02.999 | Banco Custodia Mercantil Camilo USD | Banco Custodia Mercantil Camilo USD | 1 | NULL |
| 1.01.04 | Transito | Transito | 1 | NULL |
| 1.01.04.01 | Transito en Bolivares | Transito en Bolivares | 1 | NULL |
| 1.01.04.01.001 | Efectivo en transito en Bs. | Efectivo en transito en Bs. | 1 | NULL |
| 1.01.04.01.002 | Depositos en transito en Bs. | Depositos en transito en Bs. | 1 | NULL |
| 1.01.04.01.003 | Pagos del fondo en transito | Pagos del fondo en transito | 1 | NULL |
| 1.01.04.01.999 | Pagos de facturas cashea en tránsito | Pagos de facturas cashea en tránsito | 1 | NULL |
| 1.01.04.02 | Transito en Divisas | Transito en Divisas | 1 | NULL |
| 1.01.04.02.001 | Efectivo en transito en $ | Efectivo en transito en $ | 1 | NULL |
| 1.01.04.02.002 | Depositos en transito en $ | Depositos en transito en $ | 1 | NULL |
| 1.01.04.02.998 | Efectivo en transito por eventos | Efectivo en transito por eventos | 1 | NULL |
| 1.01.04.02.999 | Abonos o pagos en transito en $ | Abonos o pagos en transito en $ | 1 | NULL |
| 1.01.05 | Deudores Comerciales | Deudores Comerciales | 1 | NULL |
| 1.01.05.01 | Cuentas por cobrar clientes | Cuentas por cobrar clientes | 1 | NULL |
| 1.01.05.01.001 | Cuentas por cobrar clientes | Cuentas por cobrar clientes | 1 | NULL |
| 1.01.05.01.002 | Cuentas por cobrar AYM BIKE | Cuentas por cobrar AYM BIKE | 1 | NULL |
| 1.01.05.01.003 | Cuentas por cobrar BAD APPLE | Cuentas por cobrar BAD APPLE | 1 | NULL |
| 1.01.05.01.004 | Cuentas por cobrar ROYAL BIKE | Cuentas por cobrar ROYAL BIKE | 1 | NULL |
| 1.01.05.01.005 | Cuentas por cobrar SPRINT BIKE | Cuentas por cobrar SPRINT BIKE | 1 | NULL |
| 1.01.05.01.006 | Cuentas por cobrar TEAM BIKE | Cuentas por cobrar TEAM BIKE | 1 | NULL |
| 1.01.05.01.007 | Cuentas por cobrar TU BICI | Cuentas por cobrar TU BICI | 1 | NULL |
| 1.01.05.01.008 | Cuentas por cobrar XTREME BIKE | Cuentas por cobrar XTREME BIKE | 1 | NULL |
| 1.01.05.01.009 | Cuentas por cobrar SU BICICLETA | Cuentas por cobrar SU BICICLETA | 1 | NULL |
| 1.01.05.01.010 | Cuentas por cobrar TOPBIKE | Cuentas por cobrar TOPBIKE | 1 | NULL |
| 1.01.05.01.011 | Cuentas por cobrar UBIKE OSTDOOR SPORT C.A. | Cuentas por cobrar UBIKE OSTDOOR SPORT C.A. | 1 | NULL |
| 1.01.05.01.012 | Cuentas por cobrar DINO BIKE STORE C.A. | Cuentas por cobrar DINO BIKE STORE C.A. | 1 | NULL |
| 1.01.05.02 | Cuentas por cobrar empresas relacionadas | Cuentas por cobrar empresas relacionadas | 1 | NULL |
| 1.01.05.02.001 | Cuentas por cobrar ULTRABIKEX | Cuentas por cobrar ULTRABIKEX | 1 | NULL |
| 1.01.05.02.002 | Cuentas por cobrar DIUX | Cuentas por cobrar DIUX | 1 | NULL |
| 1.01.05.02.003 | Cuentas por cobrar PLUSUX | Cuentas por cobrar PLUSUX | 1 | NULL |
| 1.01.05.02.004 | Cuentas por cobrar UX BARINAS | Cuentas por cobrar UX BARINAS | 1 | NULL |
| 1.01.05.03 | Cuentas por cobrar empresas externas del grupo | Cuentas por cobrar empresas externas del grupo | 1 | NULL |
| 1.01.05.03.001 | Cuentas por cobrar UX CARACAS | Cuentas por cobrar UX CARACAS | 1 | NULL |
| 1.01.05.03.002 | Cuentas por cobrar UX PUERTO ORDAZ | Cuentas por cobrar UX PUERTO ORDAZ | 1 | NULL |
| 1.01.05.03.003 | Cuentas por cobrar UX VALENCIA | Cuentas por cobrar UX VALENCIA | 1 | NULL |
| 1.01.05.03.004 | Cuentas por cobrar UX LARA | Cuentas por cobrar UX LARA | 1 | NULL |
| 1.01.05.03.005 | Cuentas por cobrar DRYFIELD | Cuentas por cobrar DRYFIELD | 1 | NULL |
| 1.01.05.04 | Cuentas por cobrar socios | Cuentas por cobrar socios | 1 | NULL |
| 1.01.05.04.001 | Cuentas por cobrar Camilo Gonzalez | Cuentas por cobrar Camilo Gonzalez | 1 | NULL |
| 1.01.05.04.002 | Cuentas por cobrar Jenny Castro | Cuentas por cobrar Jenny Castro | 1 | NULL |
| 1.01.05.04.003 | Cuentas por cobrar Alfonso Marquez | Cuentas por cobrar Alfonso Marquez | 1 | NULL |
| 1.01.05.05 | Cuentas por cobrar empleados | Cuentas por cobrar empleados | 1 | NULL |
| 1.01.05.05.001 | Cuentas por cobrar empleados | Cuentas por cobrar empleados | 1 | NULL |
| 1.01.05.05.002 | Cuentas por cobrar empleados ULTRABIKEX | Cuentas por cobrar empleados ULTRABIKEX | 1 | NULL |
| 1.01.05.05.003 | Cuentas por cobrar empleados DIUX | Cuentas por cobrar empleados DIUX | 1 | NULL |
| 1.01.05.05.004 | Cuentas por cobrar empleados PLUSUX | Cuentas por cobrar empleados PLUSUX | 1 | NULL |
| 1.01.05.05.005 | Cuentas por cobrar empleados UX BARINAS | Cuentas por cobrar empleados UX BARINAS | 1 | NULL |
| 1.01.06 | Otras cuentas por cobrar | Otras cuentas por cobrar | 1 | NULL |
| 1.01.06.01 | Otras cuentas por cobrar | Otras cuentas por cobrar | 1 | NULL |
| 1.01.06.01.001 | Cuentas por cobrar terceros | Cuentas por cobrar terceros | 1 | NULL |
| 1.01.06.01.002 | Vuelto por cobrar terceros | Vuelto por cobrar terceros | 1 | NULL |
| 1.01.06.01.003 | Cuentas por Cobrar a proveedores por Garantias | Cuentas por Cobrar a proveedores por Garantias | 1 | NULL |
| 1.01.06.02 | Cuentas por cobrar por sociedades | Cuentas por cobrar por sociedades | 1 | NULL |
| 1.01.06.02.001 | Cuentas por cobrar sociedades Camilo | Cuentas por cobrar sociedades Camilo | 1 | NULL |
| 1.01.06.02.002 | Cuentas por cobrar sociedades Jenny | Cuentas por cobrar sociedades Jenny | 1 | NULL |
| 1.01.06.02.003 | Cuentas por cobrar sociedades Alfonso | Cuentas por cobrar sociedades Alfonso | 1 | NULL |
| 1.01.07 | Prestamos por cobrar | Prestamos por cobrar | 1 | NULL |
| 1.01.07.01 | Prestamos por cobrar empresas relacionadas | Prestamos por cobrar empresas relacionadas | 1 | NULL |
| 1.01.07.01.001 | Prestamos por cobrar ULTRABIKEX | Prestamos por cobrar ULTRABIKEX | 1 | NULL |
| 1.01.07.01.002 | Prestamos por cobrar DIUX | Prestamos por cobrar DIUX | 1 | NULL |
| 1.01.07.01.003 | Prestamos por cobrar PLUSUX | Prestamos por cobrar PLUSUX | 1 | NULL |
| 1.01.07.01.004 | Prestamos por cobrar UX BARINAS | Prestamos por cobrar UX BARINAS | 1 | NULL |
| 1.01.07.01.005 | Prestamos por cobrar UBX | Prestamos por cobrar UBX | 1 | NULL |
| 1.01.07.02 | Prestamos por cobrar empresas externas del grupo | Prestamos por cobrar empresas externas del grupo | 1 | NULL |
| 1.01.07.02.001 | Prestamos por cobrar UX CARACAS | Prestamos por cobrar UX CARACAS | 1 | NULL |
| 1.01.07.02.002 | Prestamos por cobrar Ux PUERTO ORDAZ | Prestamos por cobrar Ux PUERTO ORDAZ | 1 | NULL |
| 1.01.07.02.003 | Prestamos por cobrar UX VALENCIA | Prestamos por cobrar UX VALENCIA | 1 | NULL |
| 1.01.07.02.004 | Prestamos por cobrar UX LARA | Prestamos por cobrar UX LARA | 1 | NULL |
| 1.01.07.02.005 | Prestamos por cobrar DRYFIELD | Prestamos por cobrar DRYFIELD | 1 | NULL |
| 1.01.07.03 | Prestamos por cobrar socios | Prestamos por cobrar socios | 1 | NULL |
| 1.01.07.03.001 | Prestamos por cobrar Camilo Gonzalez | Prestamos por cobrar Camilo Gonzalez | 1 | NULL |
| 1.01.07.03.002 | Prestamos por cobrar Jenny Castro | Prestamos por cobrar Jenny Castro | 1 | NULL |
| 1.01.07.03.003 | Prestamos por cobrar Alfonso Marquez | Prestamos por cobrar Alfonso Marquez | 1 | NULL |
| 1.01.07.04 | Prestamos por cobrar empleados | Prestamos por cobrar empleados | 1 | NULL |
| 1.01.07.04.001 | Prestamos por cobrar empleados | Prestamos por cobrar empleados | 1 | NULL |
| 1.01.07.05 | Otros prestamos por cobrar | Otros prestamos por cobrar | 1 | NULL |
| 1.01.07.05.001 | Prestamos por cobrar terceros | Prestamos por cobrar terceros | 1 | NULL |
| 1.01.08 | Anticipos | Anticipos | 1 | NULL |
| 1.01.08.01 | Anticipos a proveedores | Anticipos a proveedores | 1 | NULL |
| 1.01.08.01.001 | Anticipos a proveedores | Anticipos a proveedores | 1 | NULL |
| 1.01.08.01.002 | Anticipos a proveedor Specialized | Anticipos a proveedor Specialized | 1 | NULL |
| 1.01.08.02 | Anticipos a socios | Anticipos a socios | 1 | NULL |
| 1.01.08.02.001 | Anticipos a Camilo Gonzalez | Anticipos a Camilo Gonzalez | 1 | NULL |
| 1.01.08.02.002 | Anticipos a Jenny Castro | Anticipos a Jenny Castro | 1 | NULL |
| 1.01.08.02.003 | Anticipos a Alfonso Marquez | Anticipos a Alfonso Marquez | 1 | NULL |
| 1.01.08.02.004 | Anticipos a Leonardo Roa | Anticipos a Leonardo Roa | 1 | NULL |
| 1.01.08.03 | Anticipos a empleados | Anticipos a empleados | 1 | NULL |
| 1.01.08.03.001 | Anticipos a empleados | Anticipos a empleados | 1 | NULL |
| 1.01.09 | Inventarios | Inventarios | 1 | NULL |
| 1.01.09.01 | Inventario de mercancias | Inventario de mercancias | 1 | NULL |
| 1.01.09.01.001 | Inventario de mercancias | Inventario de mercancias | 1 | NULL |
| 1.01.09.02 | Inventario de suministros | Inventario de suministros | 1 | NULL |
| 1.01.09.02.001 | Inventario de suministros del café | Inventario de suministros del café | 1 | NULL |
| 1.01.09.03 | Inventario en transito | Inventario en transito | 1 | NULL |
| 1.01.09.03.001 | Inventario de mercancias en transito | Inventario de mercancias en transito | 1 | NULL |
| 1.01.09.03.002 | Inventario de suministros del café en transito | Inventario de suministros del café en transito | 1 | NULL |
| 1.01.09.04 | Inventario en consignación | Inventario en consignación | 1 | NULL |
| 1.01.09.04.001 | Inventarios de mercancías propias a consignación | Inventarios de mercancías propias a consignación | 1 | NULL |
| 1.01.09.04.002 | Inventarios de mercancías de terceros a consignación | Inventarios de mercancías de terceros a consignación | 1 | NULL |
| 1.01.11 | Prepagados | Prepagados | 1 | NULL |
| 1.01.11.01 | Impuestos pagados por anticipado | Impuestos pagados por anticipado | 1 | NULL |
| 1.01.11.01.001 | IVA credito fiscal | IVA credito fiscal | 1 | NULL |
| 1.01.11.01.002 | Excedente de credito fiscal | Excedente de credito fiscal | 1 | NULL |
| 1.01.11.01.003 | Retencion IVA de clientes | Retencion IVA de clientes | 1 | NULL |
| 1.01.11.01.004 | Retenciones ISLR de clientes | Retenciones ISLR de clientes | 1 | NULL |
| 1.01.11.01.005 | Anticipo de ISLR | Anticipo de ISLR | 1 | NULL |
| 1.01.11.02 | Gastos pagados por anticipado | Gastos pagados por anticipado | 1 | NULL |
| 1.01.11.02.001 | Seguros pagados por anticipado | Seguros pagados por anticipado | 1 | NULL |
| 1.01.11.02.002 | Intereses pagados por anticipado | Intereses pagados por anticipado | 1 | NULL |
| 1.01.11.02.003 | Alquileres pagados por anticipado | Alquileres pagados por anticipado | 1 | NULL |
| 1.02 | Activo No Corriente | Activo No Corriente | 1 | NULL |
| 1.02.01 | Deudores Comerciales L.P. | Deudores Comerciales L.P. | 1 | NULL |
| 1.02.01.01 | Cuentas por cobrar clientes L.P. | Cuentas por cobrar clientes L.P. | 1 | NULL |
| 1.02.01.01.001 | Cuentas por cobrar clientes Mayor y Ciclismo L.P. | Cuentas por cobrar clientes Mayor y Ciclismo L.P. | 1 | NULL |
| 1.02.01.02 | Cuentas por cobrar empresas relacionadas L.P. | Cuentas por cobrar empresas relacionadas L.P. | 1 | NULL |
| 1.02.01.02.001 | Cuentas por cobrar ULTRABIKEX L.P. | Cuentas por cobrar ULTRABIKEX L.P. | 1 | NULL |
| 1.02.01.02.002 | Cuentas por cobrar DIUX L.P. | Cuentas por cobrar DIUX L.P. | 1 | NULL |
| 1.02.01.02.003 | Cuentas por cobrar PLUSUX L.P. | Cuentas por cobrar PLUSUX L.P. | 1 | NULL |
| 1.02.01.02.004 | Cuentas por cobrar UX BARINAS L.P. | Cuentas por cobrar UX BARINAS L.P. | 1 | NULL |
| 1.02.01.03 | Cuentas por cobrar empresas externas del grupo L.P. | Cuentas por cobrar empresas externas del grupo L.P. | 1 | NULL |
| 1.02.01.03.001 | Cuentas por cobrar UX CARACAS L.P. | Cuentas por cobrar UX CARACAS L.P. | 1 | NULL |
| 1.02.01.03.002 | Cuentas por cobrar UX PUERTO ORDAZ L.P. | Cuentas por cobrar UX PUERTO ORDAZ L.P. | 1 | NULL |
| 1.02.01.03.003 | Cuentas por cobrar UX VALENCIA L.P. | Cuentas por cobrar UX VALENCIA L.P. | 1 | NULL |
| 1.02.01.03.004 | Cuentas por cobrar UX LARA L.P. | Cuentas por cobrar UX LARA L.P. | 1 | NULL |
| 1.02.01.03.005 | Cuentas por cobrar DRYFIELD L.P. | Cuentas por cobrar DRYFIELD L.P. | 1 | NULL |
| 1.02.01.04 | Cuentas por cobrar socios L.P. | Cuentas por cobrar socios L.P. | 1 | NULL |
| 1.02.01.04.001 | Cuentas por cobrar Camilo Gonzalez L.P. | Cuentas por cobrar Camilo Gonzalez L.P. | 1 | NULL |
| 1.02.01.04.002 | Cuentas por cobrar Jenny Castro L.P. | Cuentas por cobrar Jenny Castro L.P. | 1 | NULL |
| 1.02.01.04.003 | Cuentas por cobrar Alfonso Marquez L.P. | Cuentas por cobrar Alfonso Marquez L.P. | 1 | NULL |
| 1.02.01.05 | Cuentas por cobrar empleados L.P. | Cuentas por cobrar empleados L.P. | 1 | NULL |
| 1.02.01.05.001 | Cuentas por cobrar empleados L.P. | Cuentas por cobrar empleados L.P. | 1 | NULL |
| 1.02.01.05.002 | Cuentas por cobrar empleados ULTRABIKEX L.P. | Cuentas por cobrar empleados ULTRABIKEX L.P. | 1 | NULL |
| 1.02.01.05.003 | Cuentas por cobrar empleados DIUX L.P. | Cuentas por cobrar empleados DIUX L.P. | 1 | NULL |
| 1.02.01.05.004 | Cuentas por cobrar empleados PLUSUX L.P. | Cuentas por cobrar empleados PLUSUX L.P. | 1 | NULL |
| 1.02.01.05.005 | Cuentas por cobrar empleados UX BARINAS L.P. | Cuentas por cobrar empleados UX BARINAS L.P. | 1 | NULL |
| 1.02.02 | Otras cuentas por cobrar L.P. | Otras cuentas por cobrar L.P. | 1 | NULL |
| 1.02.02.01 | Otras cuentas por cobrar L.P. | Otras cuentas por cobrar L.P. | 1 | NULL |
| 1.02.02.01.001 | Cuentas por cobrar terceros L.P. | Cuentas por cobrar terceros L.P. | 1 | NULL |
| 1.02.02.01.002 | Vuelto por cobrar terceros L.P. | Vuelto por cobrar terceros L.P. | 1 | NULL |
| 1.02.02.02 | Cuentas por cobrar por sociedades L.P. | Cuentas por cobrar por sociedades L.P. | 1 | NULL |
| 1.02.02.02.001 | Cuentas por cobrar sociedades Camilo L.P. | Cuentas por cobrar sociedades Camilo L.P. | 1 | NULL |
| 1.02.02.02.002 | Cuentas por cobrar sociedades Jenny L.P. | Cuentas por cobrar sociedades Jenny L.P. | 1 | NULL |
| 1.02.02.02.003 | Cuentas por cobrar sociedades Alfonso L.P. | Cuentas por cobrar sociedades Alfonso L.P. | 1 | NULL |
| 1.02.02.02.004 | Cuentas por cobrar sociedades Otros Socios | Cuentas por cobrar sociedades Otros Socios | 1 | NULL |
| 1.02.03 | Prestamos por cobrar L.P. | Prestamos por cobrar L.P. | 1 | NULL |
| 1.02.03.01 | Prestamos por cobrar empresas relacionadas L.P. | Prestamos por cobrar empresas relacionadas L.P. | 1 | NULL |
| 1.02.03.01.001 | Prestamos por cobrar ULTRABIKEX L.P. | Prestamos por cobrar ULTRABIKEX L.P. | 1 | NULL |
| 1.02.03.01.002 | Prestamos por cobrar DIUX L.P. | Prestamos por cobrar DIUX L.P. | 1 | NULL |
| 1.02.03.01.003 | Prestamos por cobrar PLUSUX L.P. | Prestamos por cobrar PLUSUX L.P. | 1 | NULL |
| 1.02.03.01.004 | Prestamos por cobrar UX BARINAS L.P. | Prestamos por cobrar UX BARINAS L.P. | 1 | NULL |
| 1.02.03.01.005 | Prestamos por cobrar UBX L.P. | Prestamos por cobrar UBX L.P. | 1 | NULL |
| 1.02.03.02 | Prestamos por cobrar empresas externas del grupo L.P. | Prestamos por cobrar empresas externas del grupo L.P. | 1 | NULL |
| 1.02.03.02.001 | Prestamos por cobrar UX CARACAS L.P. | Prestamos por cobrar UX CARACAS L.P. | 1 | NULL |
| 1.02.03.02.002 | Prestamos por cobrar Ux PUERTO ORDAZ L.P. | Prestamos por cobrar Ux PUERTO ORDAZ L.P. | 1 | NULL |
| 1.02.03.02.003 | Prestamos por cobrar UX VALENCIA L.P. | Prestamos por cobrar UX VALENCIA L.P. | 1 | NULL |
| 1.02.03.02.004 | Prestamos por cobrar UX LARA L.P. | Prestamos por cobrar UX LARA L.P. | 1 | NULL |
| 1.02.03.02.005 | Prestamos por cobrar DRYFIELD L.P. | Prestamos por cobrar DRYFIELD L.P. | 1 | NULL |
| 1.02.03.03 | Prestamos por cobrar socios L.P. | Prestamos por cobrar socios L.P. | 1 | NULL |
| 1.02.03.03.001 | Prestamos por cobrar Camilo Gonzalez L.P. | Prestamos por cobrar Camilo Gonzalez L.P. | 1 | NULL |
| 1.02.03.03.002 | Prestamos por cobrar Jenny Castro L.P. | Prestamos por cobrar Jenny Castro L.P. | 1 | NULL |
| 1.02.03.03.003 | Prestamos por cobrar Alfonso Marquez L.P. | Prestamos por cobrar Alfonso Marquez L.P. | 1 | NULL |
| 1.02.03.04 | Prestamos por cobrar empleados L.P. | Prestamos por cobrar empleados L.P. | 1 | NULL |
| 1.02.03.04.001 | Prestamos por cobrar empleados L.P. | Prestamos por cobrar empleados L.P. | 1 | NULL |
| 1.02.03.05 | Otros prestamos por cobrar L.P. | Otros prestamos por cobrar L.P. | 1 | NULL |
| 1.02.03.05.001 | Prestamos por cobrar tercercos L.P. | Prestamos por cobrar tercercos L.P. | 1 | NULL |
| 1.02.04 | Anticipos L.P. | Anticipos L.P. | 1 | NULL |
| 1.02.04.01 | Anticipos a proveedores L.P. | Anticipos a proveedores L.P. | 1 | NULL |
| 1.02.04.01.001 | Anticipos a proveedores L.P. | Anticipos a proveedores L.P. | 1 | NULL |
| 1.02.04.01.002 | Anticipos a proveedor Specialized L.P. | Anticipos a proveedor Specialized L.P. | 1 | NULL |
| 1.02.04.02 | Anticipos a socios L.P. | Anticipos a socios L.P. | 1 | NULL |
| 1.02.04.02.001 | Anticipos Camilo Gonzalez L.P. | Anticipos Camilo Gonzalez L.P. | 1 | NULL |
| 1.02.04.02.002 | Anticipos Jenny Castro L.P. | Anticipos Jenny Castro L.P. | 1 | NULL |
| 1.02.04.02.003 | Anticipos Alfonso Marquez L.P. | Anticipos Alfonso Marquez L.P. | 1 | NULL |
| 1.02.04.02.004 | Anticipos Leonardo Roa L.P. | Anticipos Leonardo Roa L.P. | 1 | NULL |
| 1.02.04.03 | Anticipos a empleados L.P. | Anticipos a empleados L.P. | 1 | NULL |
| 1.02.04.03.001 | Anticipos a empleados L.P. | Anticipos a empleados L.P. | 1 | NULL |
| 1.02.04.04 | Anticipos de prestaciones sociales L.P. | Anticipos de prestaciones sociales L.P. | 1 | NULL |
| 1.02.04.04.001 | Anticipos de prestaciones sociales L.P. | Anticipos de prestaciones sociales L.P. | 1 | NULL |
| 1.02.05 | Propiedades de Inversion | Propiedades de Inversion | 1 | NULL |
| 1.02.05.01 | Inversion en acciones | Inversion en acciones | 1 | NULL |
| 1.02.05.01.001 | Inversion en acciones | Inversion en acciones | 1 | NULL |
| 1.02.06 | Propiedad, planta y equipos | Propiedad, planta y equipos | 1 | NULL |
| 1.02.06.01 | Terrenos | Terrenos | 1 | NULL |
| 1.02.06.01.001 | Terreno | Terreno | 1 | NULL |
| 1.02.06.01.002 | Deterioro acum. Terreno | Deterioro acum. Terreno | 1 | NULL |
| 1.02.06.02 | Mobiliario y equipos | Mobiliario y equipos | 1 | NULL |
| 1.02.06.02.001 | Mobiliario y equipos | Mobiliario y equipos | 1 | NULL |
| 1.02.06.02.500 | Dep. Acum. Mob y Equipos | Dep. Acum. Mob y Equipos | -1 | NULL |
| 1.02.06.02.501 | Deterioro acum. Mob y Equipos | Deterioro acum. Mob y Equipos | -1 | NULL |
| 1.02.06.03 | Maquinaria y equipos | Maquinaria y equipos | 1 | NULL |
| 1.02.06.03.001 | Maquinarias y Equipos | Maquinarias y Equipos | 1 | NULL |
| 1.02.06.03.500 | Dep. Acum. Maquinarias y equipos | Dep. Acum. Maquinarias y equipos | -1 | NULL |
| 1.02.06.03.501 | Det. Acum. Maquinarias y equipos | Det. Acum. Maquinarias y equipos | -1 | NULL |
| 1.02.06.04 | Vehiculos | Vehiculos | 1 | NULL |
| 1.02.06.04.001 | Vehiculo Grand Cheroke año 2006 | Vehiculo Grand Cheroke año 2006 | 1 | NULL |
| 1.02.06.04.002 | Vehiculo Orlando año 2014 | Vehiculo Orlando año 2014 | 1 | NULL |
| 1.02.06.04.003 | Vehiculo Camion Cargo año 2006 | Vehiculo Camion Cargo año 2006 | 1 | NULL |
| 1.02.06.04.004 | Moto | Moto | 1 | NULL |
| 1.02.06.04.005 | Vehiculo Kangoo | Vehiculo Kangoo | 1 | NULL |
| 1.02.06.04.006 | Vehículo Hilux | Vehículo Hilux | 1 | NULL |
| 1.02.06.04.007 | Vehículo Toyota Vans | Vehículo Toyota Vans | 1 | NULL |
| 1.02.06.04.500 | Dep. Acum. Vehiculo Grand Cheroke año 2006 | Dep. Acum. Vehiculo Grand Cheroke año 2006 | -1 | NULL |
| 1.02.06.04.501 | Det. Acum. Vehiculo Grand Cheroke año 2006 | Det. Acum. Vehiculo Grand Cheroke año 2006 | -1 | NULL |
| 1.02.06.04.502 | Dep. Acum. Vehiculo Orlando año 2014 | Dep. Acum. Vehiculo Orlando año 2014 | 1 | NULL |
| 1.02.06.04.503 | Det. Acum. Vehiculo Orlando año 2014 | Det. Acum. Vehiculo Orlando año 2014 | 1 | NULL |
| 1.02.06.04.504 | Dep. Acum. Vehiculo Camion Cargo año 2006 | Dep. Acum. Vehiculo Camion Cargo año 2006 | 1 | NULL |
| 1.02.06.04.505 | Det. Acum. Vehiculo Camion Cargo año 2006 | Det. Acum. Vehiculo Camion Cargo año 2006 | 1 | NULL |
| 1.02.06.04.506 | Dep. Acum. Moto | Dep. Acum. Moto | 1 | NULL |
| 1.02.06.04.507 | Det. Acum. Moto | Det. Acum. Moto | 1 | NULL |
| 1.02.06.04.508 | Dep. Acum. Vehiculo Kangoo | Dep. Acum. Vehiculo Kangoo | 1 | NULL |
| 1.02.06.04.509 | Det. Acum. Vehiculo Kangoo | Det. Acum. Vehiculo Kangoo | 1 | NULL |
| 1.02.06.04.510 | Dep. Acum. Vehículo Hilux | Dep. Acum. Vehículo Hilux | 1 | NULL |
| 1.02.06.04.511 | Det. Acum. Vehículo Hilux | Det. Acum. Vehículo Hilux | 1 | NULL |
| 1.02.06.04.512 | Dep. Acum. Vehículo Toyota Vans | Dep. Acum. Vehículo Toyota Vans | 1 | NULL |
| 1.02.06.04.513 | Det. Acum. Vehículo Toyota Vans | Det. Acum. Vehículo Toyota Vans | 1 | NULL |
| 1.02.06.05 | Edificios y construcciones | Edificios y construcciones | 1 | NULL |
| 1.02.06.05.001 | Local C.C Plaza Mayor LP-4 | Local C.C Plaza Mayor LP-4 | 1 | NULL |
| 1.02.06.05.002 | Galpon Complejo Ind. y Com Gral. Avelino | Galpon Complejo Ind. y Com Gral. Avelino | 1 | NULL |
| 1.02.06.05.500 | Dep. Acum. Local C.C Plaza Mayor LP-4 | Dep. Acum. Local C.C Plaza Mayor LP-4 | -1 | NULL |
| 1.02.06.05.501 | Det. Acum. Local C.C Plaza Mayor LP-4 | Det. Acum. Local C.C Plaza Mayor LP-4 | -1 | NULL |
| 1.02.06.05.502 | Dep. Acum. Galpon Complejo Ind. y Com Gral. Avelino | Dep. Acum. Galpon Complejo Ind. y Com Gral. Avelino | 1 | NULL |
| 1.02.06.05.503 | Det. Acum. Galpon Complejo Ind. y Com Gral. Avelino | Det. Acum. Galpon Complejo Ind. y Com Gral. Avelino | 1 | NULL |
| 1.02.06.06 | Materiales de eventos | Materiales de eventos | 1 | NULL |
| 1.02.06.06.001 | Materiales para eventos | Materiales para eventos | 1 | NULL |
| 1.02.06.06.500 | Dep. Acum. Materiales para eventos | Dep. Acum. Materiales para eventos | -1 | NULL |
| 1.02.06.06.501 | Det. Acum. Materiales para eventos | Det. Acum. Materiales para eventos | -1 | NULL |
| 1.02.06.07 | Herramientas | Herramientas | 1 | NULL |
| 1.02.06.07.001 | Herramientas | Herramientas | 1 | NULL |
| 1.02.06.07.500 | Dep. Acum. Herramientas | Dep. Acum. Herramientas | -1 | NULL |
| 1.02.06.07.501 | Det. Acum. Herramientas | Det. Acum. Herramientas | -1 | NULL |
| 1.02.06.08 | Utensilios y equipos de cocina | Utensilios y equipos de cocina | 1 | NULL |
| 1.02.06.08.001 | Utensilios y equipos de cocina | Utensilios y equipos de cocina | 1 | NULL |
| 1.02.06.08.500 | Dep. Acum. Utensilios y equipos de cocina | Dep. Acum. Utensilios y equipos de cocina | -1 | NULL |
| 1.02.06.08.501 | Det. Acum. Utensilios y equipos de cocina | Det. Acum. Utensilios y equipos de cocina | -1 | NULL |
| 1.02.06.09 | Equipamiento deportivo | Equipamiento deportivo | 1 | NULL |
| 1.02.06.09.001 | Equipamiento deportivo | Equipamiento deportivo | 1 | NULL |
| 1.02.06.09.500 | Dep. Acum. Equipamiento deportivo | Dep. Acum. Equipamiento deportivo | -1 | NULL |
| 1.02.06.09.501 | Det. Acum. Equipamiento deportivo | Det. Acum. Equipamiento deportivo | -1 | NULL |
| 1.02.06.10 | Mejoras en bienes arrendados | Mejoras en bienes arrendados | 1 | NULL |
| 1.02.06.10.001 | Mejoras en bienes arrendados | Mejoras en bienes arrendados | 1 | NULL |
| 1.02.06.10.500 | Dep. Acum. Mejoras bienes arrendados | Dep. Acum. Mejoras bienes arrendados | -1 | NULL |
| 1.02.06.10.501 | Det. Acum. Mejoras bienes arrendados | Det. Acum. Mejoras bienes arrendados | -1 | NULL |
| 1.02.07 | Activos intangibles | Activos intangibles | 1 | NULL |
| 1.02.07.01 | Software Odoo | Software Odoo | 1 | NULL |
| 1.02.07.01.001 | Software Odoo | Software Odoo | 1 | NULL |
| 1.02.07.01.002 | Amortización Acum Odoo | Amortización Acum Odoo | -1 | NULL |
| 1.02.07.01.500 | Amortización Acum Odoo | Amortización Acum Odoo | -1 | NULL |
| 1.02.07.02 | CRM | CRM | 1 | NULL |
| 1.02.07.02.001 | Software CRM | Software CRM | 1 | NULL |
| 1.02.07.02.002 | Amortización CRM | Amortización CRM | -1 | NULL |
| 2.01 | Pasivo Corriente | Pasivo Corriente | -1 | NULL |
| 2.01.01 | Acreedores comerciales | Acreedores comerciales | -1 | NULL |
| 2.01.01.01 | Cuentas por pagar proveedores | Cuentas por pagar proveedores | -1 | NULL |
| 2.01.01.01.001 | Cuentas por pagar proveedores nacionales | Cuentas por pagar proveedores nacionales | -1 | NULL |
| 2.01.01.01.002 | Cuentas por pagar proveedores Internacionales | Cuentas por pagar proveedores Internacionales | -1 | NULL |
| 2.01.01.01.003 | Cuentas por pagar Specialized | Cuentas por pagar Specialized | -1 | NULL |
| 2.01.01.02 | Cuentas por pagar empresas relacionadas | Cuentas por pagar empresas relacionadas | -1 | NULL |
| 2.01.01.02.001 | Cuentas por pagar ULTRABIKEX | Cuentas por pagar ULTRABIKEX | -1 | NULL |
| 2.01.01.02.002 | Cuentas por pagar DIUX | Cuentas por pagar DIUX | -1 | NULL |
| 2.01.01.02.003 | Cuentas por pagar PLUSUX | Cuentas por pagar PLUSUX | -1 | NULL |
| 2.01.01.02.004 | Cuentas por pagar UX BARINAS | Cuentas por pagar UX BARINAS | -1 | NULL |
| 2.01.01.03 | Cuentas por pagar empresas externas del grupo | Cuentas por pagar empresas externas del grupo | -1 | NULL |
| 2.01.01.03.001 | Cuentas por pagar UX CARACAS | Cuentas por pagar UX CARACAS | -1 | NULL |
| 2.01.01.03.002 | Cuentas por pagar UX PUERTO ORDAZ | Cuentas por pagar UX PUERTO ORDAZ | -1 | NULL |
| 2.01.01.03.003 | Cuentas por pagar UX VALENCIA | Cuentas por pagar UX VALENCIA | -1 | NULL |
| 2.01.01.03.004 | Cuentas por pagar UX LARA | Cuentas por pagar UX LARA | -1 | NULL |
| 2.01.01.03.005 | Cuentas por pagar DRYFIELD | Cuentas por pagar DRYFIELD | -1 | NULL |
| 2.01.01.04 | Cuentas por pagar socios | Cuentas por pagar socios | -1 | NULL |
| 2.01.01.04.001 | Cuentas por pagar Camilo Gonzalez | Cuentas por pagar Camilo Gonzalez | -1 | NULL |
| 2.01.01.04.002 | Cuentas por pagar Jenny Castro | Cuentas por pagar Jenny Castro | -1 | NULL |
| 2.01.01.04.003 | Cuentas por pagar Alfonso Marquez | Cuentas por pagar Alfonso Marquez | -1 | NULL |
| 2.01.01.05 | Cuentas por pagar TDC y TDC | Cuentas por pagar TDC y TDC | -1 | NULL |
| 2.01.01.05.001 | Tarjeta de crédito Bofa Sra Zaida | Tarjeta de crédito Bofa Sra Zaida | -1 | NULL |
| 2.01.01.05.002 | Tarjeta de crédito Bancamiga Camilo | Tarjeta de crédito Bancamiga Camilo | -1 | NULL |
| 2.01.01.05.003 | Tarjeta de débito Banesco Panamá Camilo | Tarjeta de débito Banesco Panamá Camilo | -1 | NULL |
| 2.01.01.05.004 | Tarjeta de crédito BNC Camilo | Tarjeta de crédito BNC Camilo | -1 | NULL |
| 2.01.01.05.005 | Tarjeta de crédito Bancamiga Gilberto | Tarjeta de crédito Bancamiga Gilberto | -1 | NULL |
| 2.01.01.06 | Cuentas por pagar a proveedores en consignacion | Cuentas por pagar a proveedores en consignacion | -1 | NULL |
| 2.01.01.06.001 | Cuentas por pagar a proveedores en consignacion | Cuentas por pagar a proveedores en consignacion | -1 | NULL |
| 2.01.02 | Otras cuentas por pagar | Otras cuentas por pagar | -1 | NULL |
| 2.01.02.01 | Otras cuentas por pagar | Otras cuentas por pagar | -1 | NULL |
| 2.01.02.01.001 | Cuentas por pagar terceros | Cuentas por pagar terceros | -1 | NULL |
| 2.01.02.01.002 | Vuelto por pagar terceros | Vuelto por pagar terceros | -1 | NULL |
| 2.01.02.01.003 | Propinas por pagar | Propinas por pagar | -1 | NULL |
| 2.01.02.02 | Descuentos a empleados por pagar | Descuentos a empleados por pagar | -1 | NULL |
| 2.01.02.02.001 | Descuentos a empleados por pagar a ULTRABIKEX | Descuentos a empleados por pagar a ULTRABIKEX | -1 | NULL |
| 2.01.02.02.002 | Descuentos a empleados por pagar a DIUX | Descuentos a empleados por pagar a DIUX | -1 | NULL |
| 2.01.02.02.003 | Descuentos a empleados por pagar a PLUSUX | Descuentos a empleados por pagar a PLUSUX | -1 | NULL |
| 2.01.02.02.004 | Descuentos a empleados por Pagar a UX BARINAS | Descuentos a empleados por Pagar a UX BARINAS | -1 | NULL |
| 2.01.02.03 | Sueldos y salarios por pagar | Sueldos y salarios por pagar | -1 | NULL |
| 2.01.02.03.001 | Sueldos y salarios por pagar | Sueldos y salarios por pagar | -1 | NULL |
| 2.01.02.03.002 | Comisiones por pagar | Comisiones por pagar | -1 | NULL |
| 2.01.02.04 | Retenciones laborales a pagar | Retenciones laborales a pagar | -1 | NULL |
| 2.01.02.04.001 | Retencion IVSS por pagar | Retencion IVSS por pagar | -1 | NULL |
| 2.01.02.04.002 | Retención SPf por pagar | Retención SPf por pagar | -1 | NULL |
| 2.01.02.04.003 | Retención FAOV por pagar | Retención FAOV por pagar | -1 | NULL |
| 2.01.02.04.004 | Retención INCES por pagar | Retención INCES por pagar | -1 | NULL |
| 2.01.02.04.005 | Retención ARI por pagar | Retención ARI por pagar | -1 | NULL |
| 2.01.02.05 | Aportes patronales por pagar | Aportes patronales por pagar | -1 | NULL |
| 2.01.02.05.001 | Aporte IVSS por pagar | Aporte IVSS por pagar | -1 | NULL |
| 2.01.02.05.002 | Aporte SPF por pagar | Aporte SPF por pagar | -1 | NULL |
| 2.01.02.05.003 | Aporte FAOV por pagar | Aporte FAOV por pagar | -1 | NULL |
| 2.01.02.05.004 | Aporte INCES por pagar | Aporte INCES por pagar | -1 | NULL |
| 2.01.02.06 | Intereses por pagar | Intereses por pagar | -1 | NULL |
| 2.01.02.06.001 | Intereses bancarios por pagar | Intereses bancarios por pagar | -1 | NULL |
| 2.01.02.06.002 | Intereses sobre prestamos de terceros por pagar | Intereses sobre prestamos de terceros por pagar | -1 | NULL |
| 2.01.02.07 | Impuestos por pagar | Impuestos por pagar | -1 | NULL |
| 2.01.02.07.001 | IVA debito fiscal | IVA debito fiscal | -1 | NULL |
| 2.01.02.07.002 | IVA por pagar | IVA por pagar | -1 | NULL |
| 2.01.02.07.003 | Retenciones IVA a proveedores | Retenciones IVA a proveedores | -1 | NULL |
| 2.01.02.07.004 | Retenciones ISLR a proveedores | Retenciones ISLR a proveedores | -1 | NULL |
| 2.01.02.07.005 | Anticipo de ISLR por pagar | Anticipo de ISLR por pagar | -1 | NULL |
| 2.01.02.07.006 | ISLR Definitiva | ISLR Definitiva | -1 | NULL |
| 2.01.02.07.007 | Impuestos municipales por pagar | Impuestos municipales por pagar | -1 | NULL |
| 2.01.02.07.008 | IGTF por pagar | IGTF por pagar | -1 | NULL |
| 2.01.02.07.009 | IGTF percibido por pagar | IGTF percibido por pagar | -1 | NULL |
| 2.01.02.08 | Dividendos por pagar | Dividendos por pagar | -1 | NULL |
| 2.01.02.08.001 | Dividendos por pagar Camilo Gonzalez | Dividendos por pagar Camilo Gonzalez | -1 | NULL |
| 2.01.02.08.002 | Dividendos por pagar Jenny Castro | Dividendos por pagar Jenny Castro | -1 | NULL |
| 2.01.02.08.003 | Dividendos por pagar Alfonso Marquez | Dividendos por pagar Alfonso Marquez | -1 | NULL |
| 2.01.02.08.004 | Dividendos por pagar Leonardo Roa | Dividendos por pagar Leonardo Roa | -1 | NULL |
| 2.01.02.08.005 | Dividendos por pagar Gilberto Gonzalez Parra | Dividendos por pagar Gilberto Gonzalez Parra | -1 | NULL |
| 2.01.02.08.999 | Dividendos por pagar otros socios | Dividendos por pagar otros socios | -1 | NULL |
| 2.01.03 | Prestamos por pagar | Prestamos por pagar | -1 | NULL |
| 2.01.03.01 | Prestamos por pagar empresas relacionadas | Prestamos por pagar empresas relacionadas | -1 | NULL |
| 2.01.03.01.001 | Prestamos por pagar ULTRABIKEX | Prestamos por pagar ULTRABIKEX | -1 | NULL |
| 2.01.03.01.002 | Prestamos por pagar DIUX | Prestamos por pagar DIUX | -1 | NULL |
| 2.01.03.01.003 | Prestamos por pagar PLUSUX | Prestamos por pagar PLUSUX | -1 | NULL |
| 2.01.03.01.004 | Prestamos por pagar UX BARINAS | Prestamos por pagar UX BARINAS | -1 | NULL |
| 2.01.03.02 | Prestamos por pagar empresas externas del grupo | Prestamos por pagar empresas externas del grupo | -1 | NULL |
| 2.01.03.02.001 | Prestamos por pagar UX CARACAS | Prestamos por pagar UX CARACAS | -1 | NULL |
| 2.01.03.02.002 | Prestamos por pagar Ux PUERTO ORDAZ | Prestamos por pagar Ux PUERTO ORDAZ | -1 | NULL |
| 2.01.03.02.003 | Prestamos por pagar UX VALENCIA | Prestamos por pagar UX VALENCIA | -1 | NULL |
| 2.01.03.02.004 | Prestamos por pagar UX LARA | Prestamos por pagar UX LARA | -1 | NULL |
| 2.01.03.02.005 | Prestamos por pagar DRYFIELD | Prestamos por pagar DRYFIELD | -1 | NULL |
| 2.01.03.03 | Prestamos por pagar socios | Prestamos por pagar socios | -1 | NULL |
| 2.01.03.03.001 | Prestamos por pagar Camilo Gonzalez | Prestamos por pagar Camilo Gonzalez | -1 | NULL |
| 2.01.03.03.002 | Prestamos por pagar Jenny Castro | Prestamos por pagar Jenny Castro | -1 | NULL |
| 2.01.03.03.003 | Prestamos por pagar Alfonso Marquez | Prestamos por pagar Alfonso Marquez | -1 | NULL |
| 2.01.03.04 | Prestamos por pagar empleados | Prestamos por pagar empleados | -1 | NULL |
| 2.01.03.04.001 | Prestamos por pagar empleados | Prestamos por pagar empleados | -1 | NULL |
| 2.01.03.05 | Prestamos bancarios por pagar | Prestamos bancarios por pagar | -1 | NULL |
| 2.01.03.05.001 | Prestamo Banco Mercantil por pagar | Prestamo Banco Mercantil por pagar | -1 | NULL |
| 2.01.03.05.002 | Prestamo Banco Banesco por pagar | Prestamo Banco Banesco por pagar | -1 | NULL |
| 2.01.03.05.003 | Prestamo Banco de Venezuela por pagar | Prestamo Banco de Venezuela por pagar | -1 | NULL |
| 2.01.03.05.004 | Prestamo Banco Venezolano de Credito por pagar | Prestamo Banco Venezolano de Credito por pagar | -1 | NULL |
| 2.01.03.05.005 | Prestamo Banco del Tesoro por pagar | Prestamo Banco del Tesoro por pagar | -1 | NULL |
| 2.01.03.05.006 | Prestamo Bancamiga por pagar | Prestamo Bancamiga por pagar | -1 | NULL |
| 2.01.03.05.007 | Prestamo Bank Of America por pagar | Prestamo Bank Of America por pagar | -1 | NULL |
| 2.01.03.05.008 | Prestamo Banesco Panamá UX por pagar | Prestamo Banesco Panamá UX por pagar | -1 | NULL |
| 2.01.03.05.009 | Prestamo Chase Bank, UX GROUP LLC por pagar | Prestamo Chase Bank, UX GROUP LLC por pagar | -1 | NULL |
| 2.01.03.06 | Otros prestamos por pagar | Otros prestamos por pagar | -1 | NULL |
| 2.01.03.06.001 | Prestamos por pagar terceros | Prestamos por pagar terceros | -1 | NULL |
| 2.01.04 | Anticipos | Anticipos | -1 | NULL |
| 2.01.04.01 | Anticipos de clientes | Anticipos de clientes | -1 | NULL |
| 2.01.04.01.001 | Anticipos de clientes | Anticipos de clientes | -1 | NULL |
| 2.01.04.02 | Anticipos de socios | Anticipos de socios | -1 | NULL |
| 2.01.04.02.001 | Anticipos de Camilo Gonzalez | Anticipos de Camilo Gonzalez | -1 | NULL |
| 2.01.04.02.002 | Anticipos de Jenny Castro | Anticipos de Jenny Castro | -1 | NULL |
| 2.01.04.02.003 | Anticipos de Alfonso Marquez | Anticipos de Alfonso Marquez | -1 | NULL |
| 2.01.04.02.004 | Anticipos de Leonardo Roa | Anticipos de Leonardo Roa | -1 | NULL |
| 2.01.04.03 | Anticipos no reportados | Anticipos no reportados | -1 | NULL |
| 2.01.04.03.001 | Anticipos de clientes no reportados | Anticipos de clientes no reportados | -1 | NULL |
| 2.01.05 | Provisiones | Provisiones | -1 | NULL |
| 2.01.05.01 | Provisión para empleados | Provisión para empleados | -1 | NULL |
| 2.01.05.01.001 | Fondo de formación de empleados Plusux | Fondo de formación de empleados Plusux | -1 | NULL |
| 2.01.05.01.002 | Fondo para viajes de auditoria | Fondo para viajes de auditoria | -1 | NULL |
| 2.02 | Pasivo No Corriente | Pasivo No Corriente | -1 | NULL |
| 2.02.01 | Otras cuentas por pagar L.P. | Otras cuentas por pagar L.P. | -1 | NULL |
| 2.02.01.01 | Intereses por pagar L.P. | Intereses por pagar L.P. | -1 | NULL |
| 2.02.01.01.001 | Intereses bancarios por pagar L.P. | Intereses bancarios por pagar L.P. | -1 | NULL |
| 2.02.01.01.002 | Intereses sobre prestamos de terceros por pagar L.P. | Intereses sobre prestamos de terceros por pagar L.P. | -1 | NULL |
| 2.02.02 | Prestamos por pagar L.P. | Prestamos por pagar L.P. | -1 | NULL |
| 2.02.02.01 | Prestamos por pagar empresas relacionadas L.P. | Prestamos por pagar empresas relacionadas L.P. | -1 | NULL |
| 2.02.02.01.001 | Prestamos por pagar ULTRABIKEX L.P. | Prestamos por pagar ULTRABIKEX L.P. | -1 | NULL |
| 2.02.02.01.002 | Prestamos por pagar DIUX L.P. | Prestamos por pagar DIUX L.P. | -1 | NULL |
| 2.02.02.01.003 | Prestamos por pagar PLUSUX L.P. | Prestamos por pagar PLUSUX L.P. | -1 | NULL |
| 2.02.02.01.004 | Prestamos por pagar UX BARINAS L.P. | Prestamos por pagar UX BARINAS L.P. | -1 | NULL |
| 2.02.02.01.005 | Prestamos por pagar UBX L.P. | Prestamos por pagar UBX L.P. | -1 | NULL |
| 2.02.02.02 | Prestamos por pagar empresas externas del grupo L.P. | Prestamos por pagar empresas externas del grupo L.P. | -1 | NULL |
| 2.02.02.02.001 | Prestamos por pagar UX CARACAS L.P. | Prestamos por pagar UX CARACAS L.P. | -1 | NULL |
| 2.02.02.02.002 | Prestamos por pagar Ux PUERTO ORDAZ L.P. | Prestamos por pagar Ux PUERTO ORDAZ L.P. | -1 | NULL |
| 2.02.02.02.003 | Prestamos por pagar UX VALENCIA L.P. | Prestamos por pagar UX VALENCIA L.P. | -1 | NULL |
| 2.02.02.02.004 | Prestamos por pagar UX LARA L.P. | Prestamos por pagar UX LARA L.P. | -1 | NULL |
| 2.02.02.02.005 | Prestamos por pagar DRYFIELD L.P. | Prestamos por pagar DRYFIELD L.P. | -1 | NULL |
| 2.02.02.03 | Prestamos por pagar socios L.P. | Prestamos por pagar socios L.P. | -1 | NULL |
| 2.02.02.03.001 | Prestamos por pagar Camilo Gonzalez L.P. | Prestamos por pagar Camilo Gonzalez L.P. | -1 | NULL |
| 2.02.02.03.002 | Prestamos por pagar Jenny Castro L.P. | Prestamos por pagar Jenny Castro L.P. | -1 | NULL |
| 2.02.02.03.003 | Prestamos por pagar Alfonso Marquez L.P. | Prestamos por pagar Alfonso Marquez L.P. | -1 | NULL |
| 2.02.02.04 | Prestamos por pagar empleados L.P. | Prestamos por pagar empleados L.P. | -1 | NULL |
| 2.02.02.04.001 | Prestamos por pagar empleados L.P. | Prestamos por pagar empleados L.P. | -1 | NULL |
| 2.02.02.05 | Prestamos bancarios por pagar L.P. | Prestamos bancarios por pagar L.P. | -1 | NULL |
| 2.02.02.05.001 | Prestamo Banco Mercantil por pagar L.P | Prestamo Banco Mercantil por pagar L.P | -1 | NULL |
| 2.02.02.05.002 | Prestamo Banco Banesco por pagar L.P. | Prestamo Banco Banesco por pagar L.P. | -1 | NULL |
| 2.02.02.05.003 | Prestamo Banco de Venezuela por pagar L.P. | Prestamo Banco de Venezuela por pagar L.P. | -1 | NULL |
| 2.02.02.05.004 | Prestamo Banco Venezolano de Credito por pagar L.P. | Prestamo Banco Venezolano de Credito por pagar L.P. | -1 | NULL |
| 2.02.02.05.005 | Prestamo Banco del Tesoro por pagar L.P. | Prestamo Banco del Tesoro por pagar L.P. | -1 | NULL |
| 2.02.02.05.006 | Prestamo Bancamiga por pagar L.P. | Prestamo Bancamiga por pagar L.P. | -1 | NULL |
| 2.02.02.05.007 | Prestamo Bank Of America por pagar L.P. | Prestamo Bank Of America por pagar L.P. | -1 | NULL |
| 2.02.02.05.008 | Prestamo Banesco Panamá UX por pagar L.P. | Prestamo Banesco Panamá UX por pagar L.P. | -1 | NULL |
| 2.02.02.05.009 | Prestamo Chase Bank, UX GROUP LLC por pagar L.P. | Prestamo Chase Bank, UX GROUP LLC por pagar L.P. | -1 | NULL |
| 2.02.02.06 | Otros prestamos por pagar L.P. | Otros prestamos por pagar L.P. | -1 | NULL |
| 2.02.02.06.001 | Prestamos por pagar terceros L.P. | Prestamos por pagar terceros L.P. | -1 | NULL |
| 2.02.03 | Provisiones L.P. | Provisiones L.P. | -1 | NULL |
| 2.02.03.01 | Provisión para empleados L.P. | Provisión para empleados L.P. | -1 | NULL |
| 2.02.03.01.001 | Fondo de formación de empleados Plusux L.P. | Fondo de formación de empleados Plusux L.P. | -1 | NULL |
| 2.02.03.01.002 | Prestaciones Sociales L.P. | Prestaciones Sociales L.P. | -1 | NULL |
| 2.02.03.01.003 | Intereses sobres Prestaciones sociales L.P. | Intereses sobres Prestaciones sociales L.P. | -1 | NULL |
| 3.01 | Capital | Capital | -1 | NULL |
| 3.01.01 | Capital social | Capital social | -1 | NULL |
| 3.01.01.01 | Capital social suscrito | Capital social suscrito | -1 | NULL |
| 3.01.01.01.001 | Capital social suscrito y pagado | Capital social suscrito y pagado | -1 | NULL |
| 3.02 | Reservas | Reservas | -1 | NULL |
| 3.02.01 | Reservas legales y estatutarias | Reservas legales y estatutarias | -1 | NULL |
| 3.02.01.01 | Reserva legal | Reserva legal | -1 | NULL |
| 3.02.01.01.001 | Reserva legal | Reserva legal | -1 | NULL |
| 3.03 | Superavit | Superavit | -1 | NULL |
| 3.03.01 | Superavit por revaluacion | Superavit por revaluacion | -1 | NULL |
| 3.03.01.01 | Superavit por revaluacion de activos | Superavit por revaluacion de activos | -1 | NULL |
| 3.03.01.01.001 | Superavit por revaluacion de terrenos | Superavit por revaluacion de terrenos | -1 | NULL |
| 3.03.01.01.002 | Superavit por revaluacion de vehiculos | Superavit por revaluacion de vehiculos | -1 | NULL |
| 3.03.01.01.003 | Superavit por revaluacion de edificios | Superavit por revaluacion de edificios | -1 | NULL |
| 3.04 | Resultados | Resultados | -1 | NULL |
| 3.04.01 | Resultados acumulados | Resultados acumulados | -1 | NULL |
| 3.04.01.01 | Resultados acumulados | Resultados acumulados | -1 | NULL |
| 3.04.01.01.001 | Utilidad o perdida acumulada | Utilidad o perdida acumulada | -1 | NULL |
| 3.04.02 | Resultados del ejercicio | Resultados del ejercicio | -1 | NULL |
| 3.04.02.01 | Resultados del ejercicio | Resultados del ejercicio | -1 | NULL |
| 3.04.02.01.001 | Utilidad o perdida del ejercicio | Utilidad o perdida del ejercicio | -1 | NULL |
| 4.01 | Ingresos operativos | Ingresos operativos | 1 | NULL |
| 4.01.01 | Ingresos por venta de mercancias | Ingresos por venta de mercancias | 1 | NULL |
| 4.01.01.01 | Ingresos por venta de mercancias | Ingresos por venta de mercancias | 1 | mercancia |
| 4.01.01.01.001 | Ingresos por venta de mercancias | Ingresos por venta de mercancias | 1 | mercancia |
| 4.01.01.02 | Devoluciones sobre ventas | Devoluciones sobre ventas | 1 | mercancia |
| 4.01.01.02.001 | Devoluciones sobre ventas | Devoluciones sobre ventas | -1 | mercancia |
| 4.01.01.03 | Descuentos sobre ventas | Descuentos sobre ventas | 1 | mercancia |
| 4.01.01.03.001 | Descuentos sobre ventas | Descuentos sobre ventas | -1 | mercancia |
| 4.01.01.03.002 | Descuentos sobre ventas plan de fidelización | Descuentos sobre ventas plan de fidelización | -1 | mercancia |
| 4.01.02 | Ingresos por servicios | Ingresos por servicios | 1 | NULL |
| 4.01.02.01 | Ingresos por servicios | Ingresos por servicios | 1 | servicios |
| 4.01.02.01.001 | Ingresos por servicios del café | Ingresos por servicios del café | 1 | servicios |
| 4.01.02.01.002 | Ingresos por servicios zona FIT | Ingresos por servicios zona FIT | 1 | servicios |
| 4.01.02.01.003 | Ingresos por servicios de fletes | Ingresos por servicios de fletes | 1 | servicios |
| 4.01.02.01.004 | Ingresos por otros servicios | Ingresos por otros servicios | 1 | servicios |
| 4.01.03 | Ingresos por eventos | Ingresos por eventos | 1 | NULL |
| 4.01.03.01 | Ingresos por eventos | Ingresos por eventos | 1 | eventos |
| 4.01.03.01.001 | Ingresos por eventos | Ingresos por eventos | 1 | eventos |
| 4.01.04 | Ingresos por Taller | Ingresos por Taller | 1 | NULL |
| 4.01.04.01 | Ingresos por Taller | Ingresos por Taller | 1 | taller |
| 4.01.04.01.001 | Ingresos por Taller | Ingresos por Taller | 1 | taller |
| 4.02 | Ingresos no operativos | Ingresos no operativos | 1 | NULL |
| 4.02.01 | Otros Ingresos | Otros Ingresos | 1 | NULL |
| 4.02.01.01 | Otros Ingresos | Otros Ingresos | 1 | NULL |
| 4.02.01.01.001 | Ingresos por alquileres | Ingresos por alquileres | 1 | NULL |
| 4.02.01.01.002 | Ingresos por intereses | Ingresos por intereses | 1 | NULL |
| 4.02.01.01.003 | Ingresos por comisiones | Ingresos por comisiones | 1 | NULL |
| 4.02.01.01.004 | Ingresos por servicios administrativos | Ingresos por servicios administrativos | 1 | NULL |
| 4.02.01.01.005 | Sobrante en ventas | Sobrante en ventas | 1 | NULL |
| 4.02.01.01.006 | Sobrante de inventarios | Sobrante de inventarios | 1 | NULL |
| 4.02.01.01.007 | Ganancia en venta de activos | Ganancia en venta de activos | 1 | NULL |
| 4.02.01.01.008 | Ganancia por tasa cambiaria | Ganancia por tasa cambiaria | 1 | NULL |
| 4.02.01.01.009 | Ganancia por diferencias en pagos | Ganancia por diferencias en pagos | 1 | NULL |
| 5.01 | Costos de venta | Costos de venta | -1 | NULL |
| 5.01.01 | Costos de venta por mercancia | Costos de venta por mercancia | -1 | NULL |
| 5.01.01.01 | Costos de venta por mercancia | Costos de venta por mercancia | -1 | mercancia |
| 5.01.01.01.001 | Costos de venta por mercancia | Costos de venta por mercancia | -1 | mercancia |
| 5.01.02 | Costos de venta por servicios | Costos de venta por servicios | -1 | NULL |
| 5.01.02.01 | Costos de venta por servicios | Costos de venta por servicios | -1 | servicios |
| 5.01.02.01.001 | Costos de venta por servicios del café | Costos de venta por servicios del café | -1 | servicios |
| 5.01.03 | Costos de venta por eventos | Costos de venta por eventos | -1 | NULL |
| 5.01.03.01 | Costos de venta por eventos | Costos de venta por eventos | -1 | eventos |
| 5.01.03.01.001 | Costos de venta por eventos | Costos de venta por eventos | -1 | eventos |
| 6.01 | Gastos operativos | Gastos operativos | -1 | NULL |
| 6.01.01 | Gastos de administración | Gastos de administración | -1 | NULL |
| 6.01.01.01 | Gastos de administración | Gastos de administración | -1 | NULL |
| 6.01.01.01.001 | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | -1 | NULL |
| 6.01.01.01.002 | Gastos de servicios de telefonía e internet | Gastos de servicios de telefonía e internet | -1 | NULL |
| 6.01.01.01.003 | Gastos de alquiler del local | Gastos de alquiler del local | -1 | NULL |
| 6.01.01.01.004 | Gastos de Condominio | Gastos de Condominio | -1 | NULL |
| 6.01.01.01.005 | Gastos de asistencia outsorcing | Gastos de asistencia outsorcing | -1 | NULL |
| 6.01.01.01.006 | Gastos de alquiler de bienes muebles | Gastos de alquiler de bienes muebles | -1 | NULL |
| 6.01.01.01.007 | Gastos de artículos de oficina | Gastos de artículos de oficina | -1 | NULL |
| 6.01.01.01.008 | Gastos de artículos de limpieza e higiene | Gastos de artículos de limpieza e higiene | -1 | NULL |
| 6.01.01.01.009 | Gastos de alimentos y bebidas | Gastos de alimentos y bebidas | -1 | NULL |
| 6.01.01.01.010 | Gastos de envíos y encomiendas administrativas | Gastos de envíos y encomiendas administrativas | -1 | NULL |
| 6.01.01.01.011 | Gastos de honorarios profesionales | Gastos de honorarios profesionales | -1 | NULL |
| 6.01.01.01.012 | Gastos de estacionamiento | Gastos de estacionamiento | -1 | NULL |
| 6.01.01.01.013 | Gastos de gestoría | Gastos de gestoría | -1 | NULL |
| 6.01.01.01.014 | Gastos legales | Gastos legales | -1 | NULL |
| 6.01.01.01.015 | Gastos de taxi, transporte y/o delivery | Gastos de taxi, transporte y/o delivery | -1 | NULL |
| 6.01.01.01.016 | Gastos de suministros para taller | Gastos de suministros para taller | -1 | NULL |
| 6.01.01.01.017 | Gastos de suministros del café | Gastos de suministros del café | -1 | NULL |
| 6.01.01.01.018 | Gastos por fiestas, festejos y/o reuniones | Gastos por fiestas, festejos y/o reuniones | -1 | NULL |
| 6.01.01.01.019 | Gastos de vigilancia | Gastos de vigilancia | -1 | NULL |
| 6.01.01.01.999 | Gastos de retenciones no descontadas | Gastos de retenciones no descontadas | -1 | NULL |
| 6.01.01.02 | Gastos de mantenimiento y reparacion | Gastos de mantenimiento y reparacion | -1 | NULL |
| 6.01.01.02.001 | Gastos de mantenimiento y reparación de mobiliario y equipo | Gastos de mantenimiento y reparación de mobiliario y equipo | -1 | NULL |
| 6.01.01.02.002 | Gastos de mantenimiento y reparación de vehiculo | Gastos de mantenimiento y reparación de vehiculo | -1 | NULL |
| 6.01.01.02.003 | Gastos de mantenimiento y reparación de edificaciones | Gastos de mantenimiento y reparación de edificaciones | -1 | NULL |
| 6.01.01.02.004 | Gastos de mantenimiento y reparación a la propiedad alq. | Gastos de mantenimiento y reparación a la propiedad alq. | -1 | NULL |
| 6.01.01.02.005 | Gastos de mantenimiento y reparación de maquinaria y equipos | Gastos de mantenimiento y reparación de maquinaria y equipos | -1 | NULL |
| 6.01.01.03 | Gastos de viáticos administrativos | Gastos de viáticos administrativos | -1 | NULL |
| 6.01.01.03.001 | Gastos de pasajes por viáticos administrativos | Gastos de pasajes por viáticos administrativos | -1 | NULL |
| 6.01.01.03.002 | Gastos de comida por viáticos administrativos | Gastos de comida por viáticos administrativos | -1 | NULL |
| 6.01.01.03.003 | Gastos de hospedaje por viáticos administrativos | Gastos de hospedaje por viáticos administrativos | -1 | NULL |
| 6.01.01.03.004 | Gastos de transporte por viáticos administrativos | Gastos de transporte por viáticos administrativos | -1 | NULL |
| 6.01.01.03.005 | Otros gastos de viáticos administrativos | Otros gastos de viáticos administrativos | -1 | NULL |
| 6.01.01.04 | Gastos de seguro | Gastos de seguro | -1 | NULL |
| 6.01.01.04.001 | Gastos de seguro de edificaciones | Gastos de seguro de edificaciones | -1 | NULL |
| 6.01.01.04.002 | Gastos de seguro de vehiculos | Gastos de seguro de vehiculos | -1 | NULL |
| 6.01.01.05 | Gastos de impuestos, tasas y contribuciones | Gastos de impuestos, tasas y contribuciones | -1 | NULL |
| 6.01.01.05.001 | Gastos de patente vehicular | Gastos de patente vehicular | -1 | NULL |
| 6.01.01.05.002 | Gastos de tasas de notaria y registro | Gastos de tasas de notaria y registro | -1 | NULL |
| 6.01.01.05.003 | Gastos de impuesto por licencia de actividades economicas | Gastos de impuesto por licencia de actividades economicas | -1 | NULL |
| 6.01.01.05.004 | Gastos de impuesto por publicidad | Gastos de impuesto por publicidad | -1 | NULL |
| 6.01.01.05.005 | Gastos de tasa sencamer | Gastos de tasa sencamer | -1 | NULL |
| 6.01.01.05.007 | Gasto por impuesto a las pensiones | Gasto por impuesto a las pensiones | -1 | NULL |
| 6.01.01.05.999 | Gasto por otras tasas | Gasto por otras tasas | -1 | NULL |
| 6.01.01.06 | Gastos de depreciación | Gastos de depreciación | -1 | NULL |
| 6.01.01.06.001 | Gastos de depreciación de mobiliario y equipo | Gastos de depreciación de mobiliario y equipo | -1 | NULL |
| 6.01.01.06.002 | Gastos de depreciación de vehículos | Gastos de depreciación de vehículos | -1 | NULL |
| 6.01.01.06.003 | Gastos de depreciación de edificaciones | Gastos de depreciación de edificaciones | -1 | NULL |
| 6.01.01.06.004 | Gastos de depreciación de maquinarias y equipos | Gastos de depreciación de maquinarias y equipos | -1 | NULL |
| 6.01.01.07 | Gastos de deterioro | Gastos de deterioro | -1 | NULL |
| 6.01.01.07.001 | Gastos de deterioro de mobiliario y equipo | Gastos de deterioro de mobiliario y equipo | -1 | NULL |
| 6.01.01.07.002 | Gastos de deterioro de vehículos | Gastos de deterioro de vehículos | -1 | NULL |
| 6.01.01.07.003 | Gastos de deterioro de edificaciones | Gastos de deterioro de edificaciones | -1 | NULL |
| 6.01.01.07.004 | Gastos de deterioro de maquinarias y equipos | Gastos de deterioro de maquinarias y equipos | -1 | NULL |
| 6.01.01.07.999 | Gastos de deterioro por cuentas incobrables | Gastos de deterioro por cuentas incobrables | -1 | NULL |
| 6.01.01.08 | Gastos de amortización | Gastos de amortización | -1 | NULL |
| 6.01.01.08.001 | Gastos de amortización de software | Gastos de amortización de software | -1 | NULL |
| 6.01.01.09 | Gastos bancarios | Gastos bancarios | -1 | NULL |
| 6.01.01.09.001 | Gastos de comisiones bancarias | Gastos de comisiones bancarias | -1 | NULL |
| 6.01.01.09.002 | Gastos de IGTF | Gastos de IGTF | -1 | NULL |
| 6.01.01.09.003 | Gastos de intereses de mora | Gastos de intereses de mora | -1 | NULL |
| 6.01.01.10 | Gastos de intereses sobre préstamos | Gastos de intereses sobre préstamos | -1 | NULL |
| 6.01.01.10.001 | Gastos de intereses sobre préstamos de terceros | Gastos de intereses sobre préstamos de terceros | -1 | NULL |
| 6.01.01.10.002 | Gastos de intereses sobre préstamos bancarios | Gastos de intereses sobre préstamos bancarios | -1 | NULL |
| 6.01.02 | Gastos de recursos humanos | Gastos de recursos humanos | -1 | NULL |
| 6.01.02.01 | Gastos de sueldos y salarios | Gastos de sueldos y salarios | -1 | NULL |
| 6.01.02.01.001 | Gastos de sueldos y salarios empleados | Gastos de sueldos y salarios empleados | -1 | NULL |
| 6.01.02.01.002 | Gastos de sueldos y salarios directivos | Gastos de sueldos y salarios directivos | -1 | NULL |
| 6.01.02.01.003 | Gastos de horas extras, feriados y bono nocturno | Gastos de horas extras, feriados y bono nocturno | -1 | NULL |
| 6.01.02.01.004 | Gastos de complemento de sueldos y salarios empleados | Gastos de complemento de sueldos y salarios empleados | -1 | NULL |
| 6.01.02.01.005 | Gastos de complemento de sueldos y salarios directivos | Gastos de complemento de sueldos y salarios directivos | -1 | NULL |
| 6.01.02.01.006 | Gastos de Bono de alimentación empleados | Gastos de Bono de alimentación empleados | -1 | NULL |
| 6.01.02.01.007 | Gastos de Bono de alimentación directivos | Gastos de Bono de alimentación directivos | -1 | NULL |
| 6.01.02.01.008 | Gastos de vacaciones empleados | Gastos de vacaciones empleados | -1 | NULL |
| 6.01.02.01.009 | Gastos de vacaciones directivos | Gastos de vacaciones directivos | -1 | NULL |
| 6.01.02.01.010 | Gastos de complemento de vacaciones empleados | Gastos de complemento de vacaciones empleados | -1 | NULL |
| 6.01.02.01.011 | Gastos de complemento de vacaciones directivos | Gastos de complemento de vacaciones directivos | -1 | NULL |
| 6.01.02.01.012 | Gastos de otros bonos empleados | Gastos de otros bonos empleados | -1 | NULL |
| 6.01.02.01.999 | Gastos de servicios de personal externo | Gastos de servicios de personal externo | -1 | NULL |
| 6.01.02.02 | Gastos de pasivos laborales | Gastos de pasivos laborales | -1 | NULL |
| 6.01.02.02.001 | Gastos de bono vacacional empleados | Gastos de bono vacacional empleados | -1 | NULL |
| 6.01.02.02.002 | Gastos de bono vacacional directivos | Gastos de bono vacacional directivos | -1 | NULL |
| 6.01.02.02.003 | Gastos de complemento bono vacacional empleados | Gastos de complemento bono vacacional empleados | -1 | NULL |
| 6.01.02.02.004 | Gastos de complemento bono vacacional directivos | Gastos de complemento bono vacacional directivos | -1 | NULL |
| 6.01.02.02.005 | Gastos de utilidades empleados | Gastos de utilidades empleados | -1 | NULL |
| 6.01.02.02.006 | Gastos de utilidades directivos | Gastos de utilidades directivos | -1 | NULL |
| 6.01.02.02.007 | Gastos de complemento de utilidades empleados | Gastos de complemento de utilidades empleados | -1 | NULL |
| 6.01.02.02.008 | Gastos de complemento de utilidades directivos | Gastos de complemento de utilidades directivos | -1 | NULL |
| 6.01.02.02.009 | Gastos de prestaciones sociales empleados | Gastos de prestaciones sociales empleados | -1 | NULL |
| 6.01.02.02.010 | Gastos de prestaciones sociales directivos | Gastos de prestaciones sociales directivos | -1 | NULL |
| 6.01.02.02.011 | Gastos de complemento de prestaciones sociales empleados | Gastos de complemento de prestaciones sociales empleados | -1 | NULL |
| 6.01.02.02.012 | Gastos de complemento de prestaciones sociales directivos | Gastos de complemento de prestaciones sociales directivos | -1 | NULL |
| 6.01.02.02.013 | Gastos de intereses sobres prestaciones sociales empleados | Gastos de intereses sobres prestaciones sociales empleados | -1 | NULL |
| 6.01.02.02.014 | Gastos de intereses sobres prestaciones sociales directivos | Gastos de intereses sobres prestaciones sociales directivos | -1 | NULL |
| 6.01.02.02.015 | Gastos de complemento de intereses sobre prestaciones sociales empleados | Gastos de complemento de intereses sobre prestaciones sociales empleados | -1 | NULL |
| 6.01.02.02.016 | Gastos de complemento de intereses sobre prestaciones sociales directivos | Gastos de complemento de intereses sobre prestaciones sociales directivos | -1 | NULL |
| 6.01.02.02.017 | Gastos de aporte patronal IVSS | Gastos de aporte patronal IVSS | -1 | NULL |
| 6.01.02.02.018 | Gastos de aporte patronal SPF | Gastos de aporte patronal SPF | -1 | NULL |
| 6.01.02.02.019 | Gastos de aporte patronal FAOV | Gastos de aporte patronal FAOV | -1 | NULL |
| 6.01.02.02.020 | Gastos de aporte patronal INCES | Gastos de aporte patronal INCES | -1 | NULL |
| 6.01.02.02.021 | Gastos de bono de guardería | Gastos de bono de guardería | -1 | NULL |
| 6.01.02.02.022 | Gastos de póliza HCM | Gastos de póliza HCM | -1 | NULL |
| 6.01.02.03 | Gastos de seguridad y salud laboral | Gastos de seguridad y salud laboral | -1 | NULL |
| 6.01.02.03.001 | Gastos de salud y seguridad laboral | Gastos de salud y seguridad laboral | -1 | NULL |
| 6.01.02.03.002 | Gastos de uniformes y dotación al personal | Gastos de uniformes y dotación al personal | -1 | NULL |
| 6.01.02.03.003 | Gastos de fiestas y agasajos al personal | Gastos de fiestas y agasajos al personal | -1 | NULL |
| 6.01.02.04 | Otros gastos de personal | Otros gastos de personal | -1 | NULL |
| 6.01.02.04.001 | Gastos de donaciones y obsequios al personal | Gastos de donaciones y obsequios al personal | -1 | NULL |
| 6.01.02.04.002 | Gastos de capacitación al personal | Gastos de capacitación al personal | -1 | NULL |
| 6.01.02.04.003 | Gastos de transporte del personal | Gastos de transporte del personal | -1 | NULL |
| 6.01.03 | Gastos de comercialización y logística | Gastos de comercialización y logística | -1 | NULL |
| 6.01.03.01 | Gastos de viáticos comerciales | Gastos de viáticos comerciales | -1 | NULL |
| 6.01.03.01.001 | Gastos de pasajes por viáticos comerciales | Gastos de pasajes por viáticos comerciales | -1 | NULL |
| 6.01.03.01.002 | Gastos de comida por viáticos comerciales | Gastos de comida por viáticos comerciales | -1 | NULL |
| 6.01.03.01.003 | Gastos de hospedaje por viáticos comerciales | Gastos de hospedaje por viáticos comerciales | -1 | NULL |
| 6.01.03.01.004 | Gastos de transporte por viáticos comerciales | Gastos de transporte por viáticos comerciales | -1 | NULL |
| 6.01.03.01.005 | Otros gastos de viáticos comerciales | Otros gastos de viáticos comerciales | -1 | NULL |
| 6.01.03.02 | Gastos no asociados al costo | Gastos no asociados al costo | -1 | NULL |
| 6.01.03.02.001 | Gastos de envíos/fletes en ventas y compras no incluidas en el costo | Gastos de envíos/fletes en ventas y compras no incluidas en el costo | -1 | NULL |
| 6.01.03.02.002 | Gastos de almacenaje sobre compras no incluídos en el costo | Gastos de almacenaje sobre compras no incluídos en el costo | -1 | NULL |
| 6.01.03.02.003 | Gastos de importación no incluídos en el costo | Gastos de importación no incluídos en el costo | -1 | NULL |
| 6.01.03.02.004 | Gastos de seguro de mercancía no incluídos en el costo | Gastos de seguro de mercancía no incluídos en el costo | -1 | NULL |
| 6.01.03.02.005 | Gastos de bolsas no incluídos en el costo | Gastos de bolsas no incluídos en el costo | -1 | NULL |
| 6.01.03.02.006 | Gastos de embalaje no incluídos en el costo | Gastos de embalaje no incluídos en el costo | -1 | NULL |
| 6.01.03.02.007 | Gastos de etiquetas no incluídos en el costo | Gastos de etiquetas no incluídos en el costo | -1 | NULL |
| 6.01.03.02.008 | Gastos de armado de bicicletas no incluídos en el costo | Gastos de armado de bicicletas no incluídos en el costo | -1 | NULL |
| 6.01.03.02.009 | Gastos de títulos de propiedad no incluídos en el costo | Gastos de títulos de propiedad no incluídos en el costo | -1 | NULL |
| 6.01.03.03 | Gastos de comisiones por ventas | Gastos de comisiones por ventas | -1 | NULL |
| 6.01.03.03.001 | Gastos de comisiones empleados | Gastos de comisiones empleados | -1 | NULL |
| 6.01.03.03.002 | Gastos de comisiones empleados del taller | Gastos de comisiones empleados del taller | -1 | NULL |
| 6.01.03.03.003 | Gastos de comisiones por venta de personal externo | Gastos de comisiones por venta de personal externo | -1 | NULL |
| 6.01.03.04 | Gastos por combustible | Gastos por combustible | -1 | NULL |
| 6.01.03.04.001 | Gastos por gasolina | Gastos por gasolina | -1 | NULL |
| 6.01.03.04.002 | Gastos por gasoil | Gastos por gasoil | -1 | NULL |
| 6.01.03.05 | Gastos de representación | Gastos de representación | -1 | NULL |
| 6.01.03.05.001 | Gastos de representación | Gastos de representación | -1 | NULL |
| 6.01.03.06 | Gastos de garantías | Gastos de garantías | -1 | NULL |
| 6.01.03.06.001 | Gastos de garantías | Gastos de garantías | -1 | NULL |
| 6.01.03.07 | Gastos de Suscripciones | Gastos de Suscripciones | -1 | NULL |
| 6.01.03.07.001 | Gastos de suscripciones | Gastos de suscripciones | -1 | NULL |
| 6.01.03.08 | Gastos de Stand y/o ferias comerciales | Gastos de Stand y/o ferias comerciales | -1 | NULL |
| 6.01.03.08.001 | Gastos de alquiler Stand y/o ferias comerciales | Gastos de alquiler Stand y/o ferias comerciales | -1 | NULL |
| 6.01.03.08.002 | Gastos de pasajes Stand y/o ferias comerciales | Gastos de pasajes Stand y/o ferias comerciales | -1 | NULL |
| 6.01.03.08.003 | Gastos de viáticos comida Stand y/o ferias comerciales | Gastos de viáticos comida Stand y/o ferias comerciales | -1 | NULL |
| 6.01.03.08.004 | Gastos de viáticos hospedaje Stand y/o ferias comerciales | Gastos de viáticos hospedaje Stand y/o ferias comerciales | -1 | NULL |
| 6.01.03.08.005 | Gastos de viáticos transporte Stand y/o ferias comerciales | Gastos de viáticos transporte Stand y/o ferias comerciales | -1 | NULL |
| 6.01.03.08.006 | Gastos de otros viáticos Stand y/o ferias comerciales | Gastos de otros viáticos Stand y/o ferias comerciales | -1 | NULL |
| 6.01.03.08.007 | Gastos de publicidad Stand y/o ferias comerciales | Gastos de publicidad Stand y/o ferias comerciales | -1 | NULL |
| 6.01.03.08.008 | Gastos de premiaciones, donaciones Stand y/o ferias comerciales | Gastos de premiaciones, donaciones Stand y/o ferias comerciales | -1 | NULL |
| 6.01.04 | Gastos de mercadeo | Gastos de mercadeo | -1 | NULL |
| 6.01.04.01 | Gastos de publicidad y promoción | Gastos de publicidad y promoción | -1 | NULL |
| 6.01.04.01.001 | Gastos de redes sociales | Gastos de redes sociales | -1 | NULL |
| 6.01.04.01.002 | Gastos de medios publicitarios | Gastos de medios publicitarios | -1 | NULL |
| 6.01.04.01.003 | Gastos de impresiones de material gráfico | Gastos de impresiones de material gráfico | -1 | NULL |
| 6.01.04.01.004 | Gastos de decoración | Gastos de decoración | -1 | NULL |
| 6.01.04.01.005 | Gastos de muestras y material POP | Gastos de muestras y material POP | -1 | NULL |
| 6.01.04.01.006 | Gastos de campañas y lanzamientos | Gastos de campañas y lanzamientos | -1 | NULL |
| 6.01.04.02 | Gastos de patrocinio y donación | Gastos de patrocinio y donación | -1 | NULL |
| 6.01.04.02.001 | Gastos de patrocinio, donación y/o obsequios en efectivo | Gastos de patrocinio, donación y/o obsequios en efectivo | -1 | NULL |
| 6.01.04.02.002 | Gastos de patrocinio, donación y/o obsequios en productos | Gastos de patrocinio, donación y/o obsequios en productos | -1 | NULL |
| 6.01.04.03 | Gastos de eventos | Gastos de eventos | -1 | NULL |
| 6.01.04.03.001 | Gastos de viáticos por eventos | Gastos de viáticos por eventos | -1 | NULL |
| 6.01.04.03.002 | Gastos de materiales y servicios por eventos | Gastos de materiales y servicios por eventos | -1 | NULL |
| 6.01.04.03.003 | Gastos de alimentos y bebidas por eventos | Gastos de alimentos y bebidas por eventos | -1 | NULL |
| 6.01.04.03.004 | Gastos de personal por eventos | Gastos de personal por eventos | -1 | NULL |
| 6.01.04.03.005 | Gastos de patrocinio, donación y/o obsequios por eventos | Gastos de patrocinio, donación y/o obsequios por eventos | -1 | NULL |
| 6.01.05 | Gastos de TI+I | Gastos de TI+I | -1 | NULL |
| 6.01.05.01 | Gastos página web | Gastos página web | -1 | NULL |
| 6.01.05.01.001 | Gastos de dominio de página web | Gastos de dominio de página web | -1 | NULL |
| 6.01.05.01.002 | Gastos de servidores | Gastos de servidores | -1 | NULL |
| 6.01.05.02 | Gastos de desarrollo | Gastos de desarrollo | -1 | NULL |
| 6.01.05.02.001 | Gastos de software tecnológico | Gastos de software tecnológico | -1 | NULL |
| 6.02 | Gastos no operativos | Gastos no operativos | -1 | NULL |
| 6.02.01 | Otros Gastos | Otros Gastos | -1 | NULL |
| 6.02.01.01 | Otros Gastos | Otros Gastos | -1 | NULL |
| 6.02.01.01.001 | Faltante en Ventas | Faltante en Ventas | -1 | NULL |
| 6.02.01.01.002 | Pérdida en venta de activos | Pérdida en venta de activos | -1 | NULL |
| 6.02.01.01.003 | Pérdida en siniestro de activos | Pérdida en siniestro de activos | -1 | NULL |
| 6.02.01.01.004 | Pérdida en tasa cambiaria | Pérdida en tasa cambiaria | -1 | NULL |
| 6.02.01.01.005 | Pérdida por diferencia en pagos | Pérdida por diferencia en pagos | -1 | NULL |
| 6.02.01.01.006 | Multas | Multas | -1 | NULL |
| 6.02.01.01.007 | Faltante de inventarios | Faltante de inventarios | -1 | NULL |
| 6.02.01.01.008 | Deterioro de inventarios | Deterioro de inventarios | -1 | NULL |

---

## 3. CUENTAS 4.x/5.x/6.x SIN MAPEAR EN V2
Resultados de la consulta:
```sql
SELECT m.odoo_code, m.odoo_name, m.partida, m.sign
FROM mapping m
WHERE (m.odoo_code LIKE '4.%' OR m.odoo_code LIKE '5.%' OR m.odoo_code LIKE '6.%')
AND m.odoo_code NOT IN (SELECT odoo_code FROM mapping_groups_v2 WHERE report_type='eerr')
ORDER BY m.odoo_code;
```

Total cuentas operativas (4.x/5.x/6.x) sin mapear en `mapping_groups_v2` (V2): **84**

| Código Odoo | Nombre Cuenta Odoo | Partida EERR | Signo |
| --- | --- | --- | --- |
| 4.01 | Ingresos operativos | Ingresos operativos | 1 |
| 4.01.01 | Ingresos por venta de mercancias | Ingresos por venta de mercancias | 1 |
| 4.01.01.01 | Ingresos por venta de mercancias | Ingresos por venta de mercancias | 1 |
| 4.01.01.02 | Devoluciones sobre ventas | Devoluciones sobre ventas | 1 |
| 4.01.01.03 | Descuentos sobre ventas | Descuentos sobre ventas | 1 |
| 4.01.01.03.002 | Descuentos sobre ventas plan de fidelización | Descuentos sobre ventas plan de fidelización | -1 |
| 4.01.02 | Ingresos por servicios | Ingresos por servicios | 1 |
| 4.01.02.01 | Ingresos por servicios | Ingresos por servicios | 1 |
| 4.01.02.01.004 | Ingresos por otros servicios | Ingresos por otros servicios | 1 |
| 4.01.03 | Ingresos por eventos | Ingresos por eventos | 1 |
| 4.01.03.01 | Ingresos por eventos | Ingresos por eventos | 1 |
| 4.01.04 | Ingresos por Taller | Ingresos por Taller | 1 |
| 4.01.04.01 | Ingresos por Taller | Ingresos por Taller | 1 |
| 4.02 | Ingresos no operativos | Ingresos no operativos | 1 |
| 4.02.01 | Otros Ingresos | Otros Ingresos | 1 |
| 4.02.01.01 | Otros Ingresos | Otros Ingresos | 1 |
| 5.01 | Costos de venta | Costos de venta | -1 |
| 5.01.01 | Costos de venta por mercancia | Costos de venta por mercancia | -1 |
| 5.01.01.01 | Costos de venta por mercancia | Costos de venta por mercancia | -1 |
| 5.01.02 | Costos de venta por servicios | Costos de venta por servicios | -1 |
| 5.01.02.01 | Costos de venta por servicios | Costos de venta por servicios | -1 |
| 5.01.03 | Costos de venta por eventos | Costos de venta por eventos | -1 |
| 5.01.03.01 | Costos de venta por eventos | Costos de venta por eventos | -1 |
| 6.01 | Gastos operativos | Gastos operativos | -1 |
| 6.01.01 | Gastos de administración | Gastos de administración | -1 |
| 6.01.01.01 | Gastos de administración | Gastos de administración | -1 |
| 6.01.01.02 | Gastos de mantenimiento y reparacion | Gastos de mantenimiento y reparacion | -1 |
| 6.01.01.03 | Gastos de viáticos administrativos | Gastos de viáticos administrativos | -1 |
| 6.01.01.04.001 | Gastos de seguro de edificaciones | Gastos de seguro de edificaciones | -1 |
| 6.01.01.04.002 | Gastos de seguro de vehiculos | Gastos de seguro de vehiculos | -1 |
| 6.01.01.05.001 | Gastos de patente vehicular | Gastos de patente vehicular | -1 |
| 6.01.01.05.002 | Gastos de tasas de notaria y registro | Gastos de tasas de notaria y registro | -1 |
| 6.01.01.05.003 | Gastos de impuesto por licencia de actividades economicas | Gastos de impuesto por licencia de actividades economicas | -1 |
| 6.01.01.05.004 | Gastos de impuesto por publicidad | Gastos de impuesto por publicidad | -1 |
| 6.01.01.05.005 | Gastos de tasa sencamer | Gastos de tasa sencamer | -1 |
| 6.01.01.05.007 | Gasto por impuesto a las pensiones | Gasto por impuesto a las pensiones | -1 |
| 6.01.01.05.999 | Gasto por otras tasas | Gasto por otras tasas | -1 |
| 6.01.01.06 | Gastos de depreciación | Gastos de depreciación | -1 |
| 6.01.01.07 | Gastos de deterioro | Gastos de deterioro | -1 |
| 6.01.01.08 | Gastos de amortización | Gastos de amortización | -1 |
| 6.01.01.09.001 | Gastos de comisiones bancarias | Gastos de comisiones bancarias | -1 |
| 6.01.01.09.002 | Gastos de IGTF | Gastos de IGTF | -1 |
| 6.01.01.09.003 | Gastos de intereses de mora | Gastos de intereses de mora | -1 |
| 6.01.01.10.001 | Gastos de intereses sobre préstamos de terceros | Gastos de intereses sobre préstamos de terceros | -1 |
| 6.01.01.10.002 | Gastos de intereses sobre préstamos bancarios | Gastos de intereses sobre préstamos bancarios | -1 |
| 6.01.02 | Gastos de recursos humanos | Gastos de recursos humanos | -1 |
| 6.01.02.01 | Gastos de sueldos y salarios | Gastos de sueldos y salarios | -1 |
| 6.01.02.02 | Gastos de pasivos laborales | Gastos de pasivos laborales | -1 |
| 6.01.02.03 | Gastos de seguridad y salud laboral | Gastos de seguridad y salud laboral | -1 |
| 6.01.02.04.001 | Gastos de donaciones y obsequios al personal | Gastos de donaciones y obsequios al personal | -1 |
| 6.01.02.04.002 | Gastos de capacitación al personal | Gastos de capacitación al personal | -1 |
| 6.01.02.04.003 | Gastos de transporte del personal | Gastos de transporte del personal | -1 |
| 6.01.03 | Gastos de comercialización y logística | Gastos de comercialización y logística | -1 |
| 6.01.03.01.001 | Gastos de pasajes por viáticos comerciales | Gastos de pasajes por viáticos comerciales | -1 |
| 6.01.03.01.002 | Gastos de comida por viáticos comerciales | Gastos de comida por viáticos comerciales | -1 |
| 6.01.03.01.003 | Gastos de hospedaje por viáticos comerciales | Gastos de hospedaje por viáticos comerciales | -1 |
| 6.01.03.01.004 | Gastos de transporte por viáticos comerciales | Gastos de transporte por viáticos comerciales | -1 |
| 6.01.03.01.005 | Otros gastos de viáticos comerciales | Otros gastos de viáticos comerciales | -1 |
| 6.01.03.02 | Gastos no asociados al costo | Gastos no asociados al costo | -1 |
| 6.01.03.03.001 | Gastos de comisiones empleados | Gastos de comisiones empleados | -1 |
| 6.01.03.03.003 | Gastos de comisiones por venta de personal externo | Gastos de comisiones por venta de personal externo | -1 |
| 6.01.03.04.001 | Gastos por gasolina | Gastos por gasolina | -1 |
| 6.01.03.04.002 | Gastos por gasoil | Gastos por gasoil | -1 |
| 6.01.03.05 | Gastos de representación | Gastos de representación | -1 |
| 6.01.03.06 | Gastos de garantías | Gastos de garantías | -1 |
| 6.01.03.07 | Gastos de Suscripciones | Gastos de Suscripciones | -1 |
| 6.01.03.08.001 | Gastos de alquiler Stand y/o ferias comerciales | Gastos de alquiler Stand y/o ferias comerciales | -1 |
| 6.01.03.08.002 | Gastos de pasajes Stand y/o ferias comerciales | Gastos de pasajes Stand y/o ferias comerciales | -1 |
| 6.01.03.08.003 | Gastos de viáticos comida Stand y/o ferias comerciales | Gastos de viáticos comida Stand y/o ferias comerciales | -1 |
| 6.01.03.08.004 | Gastos de viáticos hospedaje Stand y/o ferias comerciales | Gastos de viáticos hospedaje Stand y/o ferias comerciales | -1 |
| 6.01.03.08.005 | Gastos de viáticos transporte Stand y/o ferias comerciales | Gastos de viáticos transporte Stand y/o ferias comerciales | -1 |
| 6.01.03.08.006 | Gastos de otros viáticos Stand y/o ferias comerciales | Gastos de otros viáticos Stand y/o ferias comerciales | -1 |
| 6.01.03.08.007 | Gastos de publicidad Stand y/o ferias comerciales | Gastos de publicidad Stand y/o ferias comerciales | -1 |
| 6.01.03.08.008 | Gastos de premiaciones, donaciones Stand y/o ferias comerciales | Gastos de premiaciones, donaciones Stand y/o ferias comerciales | -1 |
| 6.01.04 | Gastos de mercadeo | Gastos de mercadeo | -1 |
| 6.01.04.01 | Gastos de publicidad y promoción | Gastos de publicidad y promoción | -1 |
| 6.01.04.02.001 | Gastos de patrocinio, donación y/o obsequios en efectivo | Gastos de patrocinio, donación y/o obsequios en efectivo | -1 |
| 6.01.04.02.002 | Gastos de patrocinio, donación y/o obsequios en productos | Gastos de patrocinio, donación y/o obsequios en productos | -1 |
| 6.01.04.03 | Gastos de eventos | Gastos de eventos | -1 |
| 6.01.05.01 | Gastos página web | Gastos página web | -1 |
| 6.01.05.02.001 | Gastos de software tecnológico | Gastos de software tecnológico | -1 |
| 6.02 | Gastos no operativos | Gastos no operativos | -1 |
| 6.02.01 | Otros Gastos | Otros Gastos | -1 |
| 6.02.01.01 | Otros Gastos | Otros Gastos | -1 |

---

## 4. VERIFICACIÓN DE GROUPS_V2 CONTRA EERR_STRUCTURE
A continuación se verifica si cada `group_name` distinto presente en `mapping_groups_v2` con `report_type='eerr'` existe textualmente como primer elemento (`item[0]`) de `EERR_STRUCTURE` en `engine.py`.

Total de nombres de grupos distintos en `mapping_groups_v2` (report_type='eerr'): **117**
Total de elementos en `EERR_STRUCTURE`: **167**

### Tabla de Verificación de Coincidencias:
| Group Name en DB | ¿Existe en EERR_STRUCTURE? |
| --- | --- |
| Costo de venta por mercancía | ❌ NO |
| Costo de venta por servicio del café | ✅ Sí |
| Costo de ventas por eventos | ✅ Sí |
| Depreciaciones, deterioro y Amortización | ✅ Sí |
| Descuentos sobre ventas | ✅ Sí |
| Devoluciones sobre ventas | ✅ Sí |
| Faltante en Ventas | ✅ Sí |
| Faltante y deterioro de inventarios | ✅ Sí |
| Ganancia en venta de activos | ✅ Sí |
| Ganancia por diferencias en pagos | ✅ Sí |
| Ganancia por tasa cambiaria | ✅ Sí |
| Gastos Bancarios | ✅ Sí |
| Gastos de Condominio | ✅ Sí |
| Gastos de Stand y/o ferias comerciales | ✅ Sí |
| Gastos de TI+I | ❌ NO |
| Gastos de alimentos y bebidas | ✅ Sí |
| Gastos de alimentos y bebidas por eventos | ✅ Sí |
| Gastos de alquiler de bienes muebles | ✅ Sí |
| Gastos de alquiler del local | ✅ Sí |
| Gastos de artículos de limpieza e higiene | ✅ Sí |
| Gastos de artículos de oficina | ✅ Sí |
| Gastos de asistencia outsorsing | ❌ NO |
| Gastos de comisiones por ventas | ✅ Sí |
| Gastos de comisiones por ventas taller | ✅ Sí |
| Gastos de complementos empleados y directivos | ✅ Sí |
| Gastos de desarrollo | ✅ Sí |
| Gastos de envíos y encomiendas administrativas | ✅ Sí |
| Gastos de estacionamiento | ✅ Sí |
| Gastos de fletes y envios no asociados al costo | ✅ Sí |
| Gastos de gestoría | ✅ Sí |
| Gastos de honorarios profesionales | ✅ Sí |
| Gastos de impuestos, tasas y contribuciones | ✅ Sí |
| Gastos de intereses sobre préstamos | ✅ Sí |
| Gastos de materiales y servicios por eventos | ✅ Sí |
| Gastos de medios publicitarios | ✅ Sí |
| Gastos de pasivos laborales HCM | ✅ Sí |
| Gastos de pasivos laborales aportes | ✅ Sí |
| Gastos de pasivos laborales bono de guardería | ❌ NO |
| Gastos de pasivos laborales prestaciones e intereses | ✅ Sí |
| Gastos de pasivos laborales utilidades | ✅ Sí |
| Gastos de pasivos laborales vacaciones | ✅ Sí |
| Gastos de patrocinio y donación | ✅ Sí |
| Gastos de patrocinio, donación y/o obseq por eventos | ✅ Sí |
| Gastos de personal externo | ✅ Sí |
| Gastos de personal por eventos | ✅ Sí |
| Gastos de página web | ✅ Sí |
| Gastos de redes sociales | ✅ Sí |
| Gastos de representación | ✅ Sí |
| Gastos de retenciones no descontadas | ✅ Sí |
| Gastos de salud y seguridad laboral | ✅ Sí |
| Gastos de salud y seguridad laboral dotación | ✅ Sí |
| Gastos de salud y seguridad laboral fiestas y agasajos | ✅ Sí |
| Gastos de seguro | ✅ Sí |
| Gastos de servicios de telefonía e internet | ✅ Sí |
| Gastos de servicios públicos (Agua, luz, Aseo Urbano) | ✅ Sí |
| Gastos de sueldos y salarios empleados y directivos | ✅ Sí |
| Gastos de suministros del café | ✅ Sí |
| Gastos de suministros para taller | ✅ Sí |
| Gastos de taxi, transporte y/o delivery | ✅ Sí |
| Gastos de vigilancia | ✅ Sí |
| Gastos de viáticos comerciales | ✅ Sí |
| Gastos de viáticos por eventos | ✅ Sí |
| Gastos legales | ✅ Sí |
| Gastos por combustible | ✅ Sí |
| Gastos por fiestas, festejos y/o reuniones | ✅ Sí |
| Gastos por garantia | ✅ Sí |
| Gastos por suscripciones | ✅ Sí |
| ISLR | ✅ Sí |
| Ingresos por alquileres | ✅ Sí |
| Ingresos por comisiones | ✅ Sí |
| Ingresos por eventos | ✅ Sí |
| Ingresos por fletes | ✅ Sí |
| Ingresos por intereses | ✅ Sí |
| Ingresos por servicios administrativos | ✅ Sí |
| Ingresos por servicios del café | ✅ Sí |
| Ingresos por taller | ✅ Sí |
| Ingresos por venta de mercancía | ❌ NO |
| Ingresos por zona FIT | ✅ Sí |
| Mantenimiento y reparaciones | ✅ Sí |
| Multas | ✅ Sí |
| Otros Gastos no Operacionales | ✅ Sí |
| Otros Ingresos no Operacionales | ✅ Sí |
| Otros gastos de personal | ✅ Sí |
| Otros gastos de publicidad y promoción | ✅ Sí |
| Otros gastos no asociados al costo | ✅ Sí |
| Pérdida en siniestro de activos | ✅ Sí |
| Pérdida en tasa cambiaria | ✅ Sí |
| Pérdida en venta de activos | ✅ Sí |
| Pérdida por diferencia en pagos | ✅ Sí |
| Sobrante de inventarios | ✅ Sí |
| Sobrante en ventas | ✅ Sí |
| Subtotal Costo de Ventas por Eventos | ✅ Sí |
| Subtotal Costo de Ventas por Mercancia | ✅ Sí |
| Subtotal Costo de Ventas por Servicios | ✅ Sí |
| Subtotal Gastos de Administración | ✅ Sí |
| Subtotal Gastos de Comercialización y Logistica | ✅ Sí |
| Subtotal Gastos de Mercadeo | ✅ Sí |
| Subtotal Gastos de Recursos Humanos | ✅ Sí |
| Subtotal Ingresos por Eventos | ✅ Sí |
| Subtotal Ingresos por Servicios | ✅ Sí |
| Subtotal Ingresos por Taller | ✅ Sí |
| Subtotal Ingresos por Venta de Mercancia | ✅ Sí |
| Total Costo de Ventas | ✅ Sí |
| Total Gastos Operacionales | ✅ Sí |
| Total Gastos Operacionales y No Operacionales | ✅ Sí |
| Total Ingresos | ✅ Sí |
| Utilidad Bruta | ✅ Sí |
| Utilidad Bruta por Eventos | ✅ Sí |
| Utilidad Bruta por Servicios | ✅ Sí |
| Utilidad Bruta por Venta de Mercancia y Taller | ✅ Sí |
| Utilidad Neta | ✅ Sí |
| Utilidad Neta despues de ISLR | ✅ Sí |
| Utilidad antes de Comisiones por Ventas | ✅ Sí |
| Utilidad antes de Intereses e Impuestos (EBIT) | ✅ Sí |
| Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | ✅ Sí |
| Utilidad después de Comisiones por Ventas | ✅ Sí |
| Viáticos administrativos | ✅ Sí |

### Nombres de grupos sin coincidencia exacta en `EERR_STRUCTURE`:
Se encontraron **5** nombres de grupos sin coincidencia exacta:
- `Costo de venta por mercancía`
- `Gastos de TI+I`
- `Gastos de asistencia outsorsing`
- `Gastos de pasivos laborales bono de guardería`
- `Ingresos por venta de mercancía`

