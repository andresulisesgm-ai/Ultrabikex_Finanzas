# DIAGNÓSTICO DEL SISTEMA FINANCIERO ULTRAX — ESTADO DE RESULTADOS (EERR)
> **Nota:** Este diagnóstico es de solo lectura y documenta el estado actual del sistema sin realizar modificaciones.

## 1. ESQUEMA DE BASE DE DATOS
A continuación se detallan todas las tablas SQLite relacionadas con el Estado de Resultados (EERR), cuentas, partidas, notas y agrupaciones. Se incluye la definición de columnas, tipos, claves foráneas y un extracto de los primeros 5 registros.

#### Tabla: `mapping`

**Columnas:**
| Columna | Tipo | No Nulo | Valor Defecto | Clave Primaria |
| --- | --- | --- | --- | --- |
| odoo_code | TEXT | No | Ninguno | Sí |
| odoo_name | TEXT | Sí | Ninguno | No |
| partida | TEXT | Sí | Ninguno | No |
| sign | INTEGER | Sí | -1 | No |
| income_type | TEXT | No | NULL | No |

*Sin claves foráneas.*

**Datos Reales (SELECT * LIMIT 5):**

| odoo_code | odoo_name | partida | sign | income_type |
| --- | --- | --- | --- | --- |
| 1.01 | Activo Corriente | Activo Corriente | 1 | NULL |
| 1.01.01 | Cajas | Cajas | 1 | NULL |
| 1.01.01.01 | Cajas en Bolivares | Cajas en Bolivares | 1 | NULL |
| 1.01.01.01.001 | Caja principal en Bs. | Caja principal en Bs. | 1 | NULL |
| 1.01.01.02 | Cajas en Divisas | Cajas en Divisas | 1 | NULL |


---

#### Tabla: `mapping_groups`

**Columnas:**
| Columna | Tipo | No Nulo | Valor Defecto | Clave Primaria |
| --- | --- | --- | --- | --- |
| id | INTEGER | No | Ninguno | Sí |
| group_name | TEXT | Sí | Ninguno | No |
| odoo_code | TEXT | Sí | Ninguno | No |
| report_type | TEXT | Sí | Ninguno | No |
| display_order | INTEGER | No | 0 | No |
| created_at | TEXT | Sí | datetime('now','localtime') | No |

**Claves Foráneas:**
| Columna Origen | Tabla Destino | Columna Destino | ON UPDATE | ON DELETE |
| --- | --- | --- | --- | --- |
| odoo_code | mapping | odoo_code | NO ACTION | CASCADE |

**Datos Reales (SELECT * LIMIT 5):**

| id | group_name | odoo_code | report_type | display_order | created_at |
| --- | --- | --- | --- | --- | --- |
| 1 | Mantenimiento y reparaciones | 6.01.01.02.001 | eerr | 10 | 2026-06-05 21:19:29 |
| 2 | Mantenimiento y reparaciones | 6.01.01.02.002 | eerr | 10 | 2026-06-05 21:19:29 |
| 3 | Mantenimiento y reparaciones | 6.01.01.02.003 | eerr | 10 | 2026-06-05 21:19:29 |
| 4 | Mantenimiento y reparaciones | 6.01.01.02.004 | eerr | 10 | 2026-06-05 21:19:29 |
| 5 | Mantenimiento y reparaciones | 6.01.01.02.005 | eerr | 10 | 2026-06-05 21:19:29 |


---

#### Tabla: `mapping_groups_v2`

**Columnas:**
| Columna | Tipo | No Nulo | Valor Defecto | Clave Primaria |
| --- | --- | --- | --- | --- |
| id | INTEGER | No | Ninguno | Sí |
| group_name | TEXT | Sí | Ninguno | No |
| odoo_code | TEXT | Sí | Ninguno | No |
| report_type | TEXT | Sí | Ninguno | No |
| display_order | INTEGER | No | 0 | No |
| created_at | TEXT | Sí | datetime('now','localtime') | No |

**Claves Foráneas:**
| Columna Origen | Tabla Destino | Columna Destino | ON UPDATE | ON DELETE |
| --- | --- | --- | --- | --- |
| odoo_code | mapping | odoo_code | NO ACTION | CASCADE |

**Datos Reales (SELECT * LIMIT 5):**

| id | group_name | odoo_code | report_type | display_order | created_at |
| --- | --- | --- | --- | --- | --- |
| 1 | Total Ingresos | 4.01.01.01.001 | eerr | 40 | 2026-06-07 12:07:16 |
| 2 | Total Ingresos | 4.01.01.02.001 | eerr | 40 | 2026-06-07 12:07:16 |
| 3 | Total Ingresos | 4.01.01.03.001 | eerr | 40 | 2026-06-07 12:07:16 |
| 4 | Total Ingresos | 4.01.02.01.001 | eerr | 40 | 2026-06-07 12:07:16 |
| 5 | Total Ingresos | 4.01.03.01.001 | eerr | 40 | 2026-06-07 12:07:16 |


---

#### Tabla: `financials`

**Columnas:**
| Columna | Tipo | No Nulo | Valor Defecto | Clave Primaria |
| --- | --- | --- | --- | --- |
| id | INTEGER | No | Ninguno | Sí |
| year | TEXT | Sí | Ninguno | No |
| month | TEXT | Sí | Ninguno | No |
| unit | TEXT | Sí | Ninguno | No |
| partida | TEXT | Sí | Ninguno | No |
| amount | REAL | Sí | 0 | No |

*Sin claves foráneas.*

**Datos Reales (SELECT * LIMIT 5):**

| id | year | month | unit | partida | amount |
| --- | --- | --- | --- | --- | --- |
| 1 | 2026 | ENE | Rodeo | Ingresos por venta de mercancias | 47933.03 |
| 2 | 2026 | ENE | Rodeo | Ingresos por intereses | 0.05 |
| 3 | 2026 | ENE | Rodeo | Ingresos por comisiones | 4.49 |
| 4 | 2026 | ENE | Rodeo | Sobrante en ventas | 4.78 |
| 5 | 2026 | ENE | Rodeo | Ganancia por tasa cambiaria | 179.05 |


---

#### Tabla: `eerr_nodes`

**Columnas:**
| Columna | Tipo | No Nulo | Valor Defecto | Clave Primaria |
| --- | --- | --- | --- | --- |
| id | INTEGER | No | Ninguno | Sí |
| parent_id | INTEGER | No | Ninguno | No |
| nombre | TEXT | Sí | Ninguno | No |
| nivel | INTEGER | Sí | Ninguno | No |
| tipo | TEXT | No | Ninguno | No |
| bold | INTEGER | No | 0 | No |
| bg_color | TEXT | No | Ninguno | No |
| display_order | INTEGER | No | Ninguno | No |

*Sin claves foráneas.*

**Datos Reales (SELECT * LIMIT 5):**

| id | parent_id | nombre | nivel | tipo | bold | bg_color | display_order |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | NULL | ESTADO DE RESULTADOS | 0 | total | 1 | NULL | 0 |
| 2 | NULL | PARTIDAS | 0 | total | 1 | NULL | 10 |
| 3 | NULL | Total Ingresos | 0 | total | 1 | FF6AD9E8 | 20 |
| 4 | 3 | Subtotal Ingresos por Venta de Mercancia | 1 | subtotal | 1 | NULL | 30 |
| 5 | 4 | Ingresos por venta de mercancias | 3 | hoja | 0 | NULL | 40 |


---

#### Tabla: `eerr_mapping`

**Columnas:**
| Columna | Tipo | No Nulo | Valor Defecto | Clave Primaria |
| --- | --- | --- | --- | --- |
| id | INTEGER | No | Ninguno | Sí |
| partida_nota | TEXT | Sí | Ninguno | No |
| nodo_id | INTEGER | Sí | Ninguno | No |
| sign | INTEGER | No | 1 | No |

**Claves Foráneas:**
| Columna Origen | Tabla Destino | Columna Destino | ON UPDATE | ON DELETE |
| --- | --- | --- | --- | --- |
| nodo_id | eerr_nodes | id | NO ACTION | NO ACTION |

**Datos Reales (SELECT * LIMIT 5):**

| id | partida_nota | nodo_id | sign |
| --- | --- | --- | --- |
| 927 | Ingresos por venta de mercancias | 5 | 1 |
| 928 | Devoluciones sobre ventas | 6 | 1 |
| 929 | Descuentos sobre ventas | 7 | 1 |
| 930 | Ingresos por servicios del café | 9 | 1 |
| 931 | Ingresos por zona FIT | 10 | 1 |


---

#### Tabla: `eerr_formulas`

**Columnas:**
| Columna | Tipo | No Nulo | Valor Defecto | Clave Primaria |
| --- | --- | --- | --- | --- |
| id | INTEGER | No | Ninguno | Sí |
| nodo_id | INTEGER | Sí | Ninguno | No |
| formula | TEXT | Sí | Ninguno | No |

**Claves Foráneas:**
| Columna Origen | Tabla Destino | Columna Destino | ON UPDATE | ON DELETE |
| --- | --- | --- | --- | --- |
| nodo_id | eerr_nodes | id | NO ACTION | NO ACTION |

**Datos Reales (SELECT * LIMIT 5):**

| id | nodo_id | formula |
| --- | --- | --- |
| 62 | 28 | NODE(28) - NODE(53) |
| 63 | 27 | NODE(28) + NODE(59) + NODE(112) + NODE(124) + NODE(137) |
| 64 | 26 | NODE(3) - NODE(16) |
| 65 | 140 | NODE(26) - (NODE(27) - NODE(112)) |
| 66 | 143 | NODE(140) - NODE(112) |


---

## 2. MAPEOS Y JERARQUÍA EXISTENTE
### Estructura Jerárquica Hardcodeada en Código (`engine.py`)
La jerarquía de presentación, niveles, nombres de partidas y estilos de celdas se define estáticamente en [engine.py](file:///C:/Users/andre/Desktop/ultrax_app/engine.py) mediante la constante `EERR_STRUCTURE`:

```python
EERR_STRUCTURE = [
    ('ESTADO DE RESULTADOS', True, None, True, None, 0, False),
    ('PARTIDAS', True, None, True, None, 0, False),
    ('Total Ingresos', True, None, True, 'FF6AD9E8', 0, False),
    ('Subtotal Ingresos por Venta de Mercancia', True, None, True, None, 1, False),
    ('Ingresos por venta de mercancias', False, None, False, None, 3, True),
    ('Devoluciones sobre ventas', False, None, False, None, 3, False),
    ('Descuentos sobre ventas', False, None, False, None, 3, False),
    ('Subtotal Ingresos por Servicios', True, None, True, None, 1, False),
    ('Ingresos por servicios del café', False, None, False, None, 3, False),
    ('Ingresos por zona FIT', False, None, False, None, 3, False),
    ('Ingresos por fletes', False, None, False, None, 3, False),
    ('Subtotal Ingresos por Eventos', True, None, True, None, 1, False),
    ('Ingresos por eventos', False, None, False, None, 3, False),
    ('Subtotal Ingresos por Taller', True, None, True, None, 1, False),
    ('Ingresos por taller', False, None, False, None, 3, False),
    ('Total Costo de Ventas', True, None, True, None, 0, False),
    ('Subtotal Costo de Ventas por Mercancia', True, None, True, None, 1, False),
    ('Costos de venta por mercancia', False, None, False, None, 3, True),
    ('Subtotal Costo de Ventas por Servicios', True, None, True, None, 1, False),
    ('Costo de venta por servicio del café', False, None, False, None, 3, False),
    ('Subtotal Costo de Ventas por Eventos', True, None, True, None, 1, False),
    ('Costo de ventas por eventos', False, None, False, None, 3, False),
    ('Utilidad Bruta por Venta de Mercancia y Taller', True, None, True, 'FF66FF66', 0, False),
    ('Utilidad Bruta por Servicios', True, None, True, 'FF66FF66', 0, False),
    ('Utilidad Bruta por Eventos', True, None, True, 'FF66FF66', 0, False),
    ('Utilidad Bruta', True, None, True, 'FF66FF66', 0, False),
    ('Total Gastos Operacionales', True, None, True, None, 0, False),
    ('Subtotal Gastos de Administración', True, None, True, None, 1, False),
    ('Gastos de servicios públicos (Agua, luz, Aseo Urbano)', False, None, False, None, 3, False),
    ('Gastos de servicios de telefonía e internet', False, None, False, None, 3, False),
    ('Gastos de alquiler del local', False, None, False, None, 3, False),
    ('Gastos de Condominio', False, None, False, None, 3, False),
    ('Gastos de asistencia outsorcing', False, None, False, None, 3, True),
    ('Gastos de alquiler de bienes muebles', False, None, False, None, 3, False),
    ('Gastos de artículos de oficina', False, None, False, None, 3, False),
    ('Gastos de artículos de limpieza e higiene', False, None, False, None, 3, False),
    ('Gastos de alimentos y bebidas', False, None, False, None, 3, False),
    ('Gastos de envíos y encomiendas administrativas', False, None, False, None, 3, False),
    ('Gastos de honorarios profesionales', False, None, False, None, 3, False),
    ('Gastos de estacionamiento', False, None, False, None, 3, False),
    ('Gastos de gestoría', False, None, False, None, 3, False),
    ('Gastos legales', False, None, False, None, 3, False),
    ('Gastos de taxi, transporte y/o delivery', False, None, False, None, 3, False),
    ('Gastos de suministros para taller', False, None, False, None, 3, False),
    ('Gastos de suministros del café', False, None, False, None, 3, False),
    ('Gastos por fiestas, festejos y/o reuniones', False, None, False, None, 3, False),
    ('Gastos de vigilancia', False, None, False, None, 3, False),
    ('Gastos de retenciones no descontadas', False, None, False, None, 3, False),
    ('Mantenimiento y reparaciones', False, None, False, None, 3, False),
    ('Viáticos administrativos', False, None, False, None, 3, False),
    ('Gastos de seguro', False, None, False, None, 3, False),
    ('Gastos de impuestos, tasas y contribuciones', False, None, False, None, 3, False),
    ('Depreciaciones, deterioro y Amortización', False, None, False, None, 3, False),
    ('Gasto por impuesto a las pensiones', False, None, False, None, 3, True),
    ('Gastos de IGTF', False, None, False, None, 3, True),
    ('Gastos de comisiones bancarias', False, None, False, None, 3, True),
    ('Gastos Bancarios', False, None, False, None, 3, False),
    ('Gastos de intereses sobre préstamos', False, None, False, None, 3, False),
    ('Subtotal Gastos de Recursos Humanos', True, None, True, None, 1, False),
    ('Gastos de sueldos y salarios empleados y directivos', True, None, False, None, 2, False),
    ('Gastos de sueldos y salarios empleados', False, None, False, None, 3, True),
    ('Gastos de sueldos y salarios directivos', False, None, False, None, 3, True),
    ('Gastos de horas extras, feriados y bono nocturno', False, None, False, None, 3, True),
    ('Gastos de Bono de alimentación empleados', False, None, False, None, 3, True),
    ('Gastos de Bono de alimentación directivos', False, None, False, None, 3, True),
    ('Gastos de complementos empleados y directivos', True, None, False, None, 2, False),
    ('Gastos de complemento de sueldos y salarios empleados', False, None, False, None, 3, True),
    ('Gastos de complemento de sueldos y salarios directivos', False, None, False, None, 3, True),
    ('Gastos de personal externo', True, None, False, None, 2, False),
    ('Gastos de servicios de personal externo', False, None, False, None, 3, True),
    ('Gastos de pasivos laborales vacaciones', True, None, False, None, 2, False),
    ('Gastos de vacaciones empleados', False, None, False, None, 3, True),
    ('Gastos de vacaciones directivos', False, None, False, None, 3, True),
    ('Gastos de complemento de vacaciones empleados', False, None, False, None, 3, True),
    ('Gastos de complemento de vacaciones directivos', False, None, False, None, 3, True),
    ('Gastos de pasivos laborales utilidades', True, None, False, None, 2, False),
    ('Gastos de bono vacacional empleados', False, None, False, None, 3, True),
    ('Gastos de bono vacacional directivos', False, None, False, None, 3, True),
    ('Gastos de complemento bono vacacional empleados', False, None, False, None, 3, True),
    ('Gastos de complemento bono vacacional directivos', False, None, False, None, 3, True),
    ('Gastos de utilidades empleados', False, None, False, None, 3, True),
    ('Gastos de utilidades directivos', False, None, False, None, 3, True),
    ('Gastos de complemento de utilidades empleados', False, None, False, None, 3, True),
    ('Gastos de complemento de utilidades directivos', False, None, False, None, 3, True),
    ('Gastos de pasivos laborales prestaciones e intereses', True, None, False, None, 2, False),
    ('Gastos de prestaciones sociales empleados', False, None, False, None, 3, True),
    ('Gastos de prestaciones sociales directivos', False, None, False, None, 3, True),
    ('Gastos de complemento de prestaciones sociales empleados', False, None, False, None, 3, True),
    ('Gastos de complemento de prestaciones sociales directivos', False, None, False, None, 3, True),
    ('Gastos de intereses sobres prestaciones sociales empleados', False, None, False, None, 3, True),
    ('Gastos de intereses sobres prestaciones sociales directivos', False, None, False, None, 3, True),
    ('Gastos de complemento de intereses sobre prestaciones sociales empleados', False, None, False, None, 3, True),
    ('Gastos de complemento de intereses sobre prestaciones sociales directivos', False, None, False, None, 3, True),
    ('Gastos de pasivos laborales aportes', True, None, False, None, 2, False),
    ('Gastos de aporte patronal IVSS', False, None, False, None, 3, True),
    ('Gastos de aporte patronal SPF', False, None, False, None, 3, True),
    ('Gastos de aporte patronal FAOV', False, None, False, None, 3, True),
    ('Gastos de aporte patronal INCES', False, None, False, None, 3, True),
    ('Gastos de bono de guardería', False, None, False, None, 3, True),
    ('Gastos de pasivos laborales HCM', True, None, False, None, 2, False),
    ('Gastos de póliza HCM', False, None, False, None, 3, True),
    ('Gastos de salud y seguridad laboral', False, None, False, None, 3, False),
    ('Gastos de salud y seguridad laboral dotación', False, None, False, None, 3, False),
    ('Gastos de uniformes y dotación al personal', False, None, False, None, 3, True),
    ('Gastos de salud y seguridad laboral fiestas y agasajos', True, None, False, None, 2, False),
    ('Gastos de fiestas y agasajos al personal', False, None, False, None, 3, True),
    ('Otros gastos de personal', True, None, False, None, 2, False),
    ('Gastos de otros bonos empleados', False, None, False, None, 3, True),
    ('Gastos de transporte del personal', False, None, False, None, 3, True),
    ('Gastos de donaciones y obsequios al personal', False, None, False, None, 3, True),
    ('Gastos de capacitación al personal', False, None, False, None, 3, True),
    ('Subtotal Gastos de Comercialización y Logistica', True, None, True, None, 1, False),
    ('Gastos de viáticos comerciales', False, None, False, None, 3, False),
    ('Gastos de comisiones empleados', False, None, False, None, 3, True),
    ('Gastos de comisiones empleados del taller', False, None, False, None, 3, True),
    ('Gastos de comisiones por venta de personal externo', False, None, False, None, 3, True),
    ('Gastos de fletes y envios no asociados al costo', False, None, False, None, 3, False),
    ('Otros gastos no asociados al costo', False, None, False, None, 3, False),
    ('Gastos por combustible', False, None, False, None, 3, False),
    ('Gastos de representación', False, None, False, None, 3, False),
    ('Gastos por garantia', False, None, False, None, 3, False),
    ('Gastos por suscripciones', False, None, False, None, 3, False),
    ('Gastos de Stand y/o ferias comerciales', False, None, False, None, 3, False),
    ('Subtotal Gastos de Mercadeo', True, None, True, None, 1, False),
    ('Gastos de redes sociales', False, None, False, None, 3, False),
    ('Gastos de medios publicitarios', False, None, False, None, 3, False),
    ('Gastos de impresiones de material gráfico', False, None, False, None, 3, True),
    ('Otros gastos de publicidad y promoción', False, None, False, None, 3, False),
    ('Gastos de patrocinio y donación', False, None, False, None, 3, False),
    ('Gastos de patrocinio, donación y/o obsequios en efectivo', False, None, False, None, 3, True),
    ('Gastos de patrocinio, donación y/o obsequios en productos', False, None, False, None, 3, True),
    ('Gastos de viáticos por eventos', False, None, False, None, 3, False),
    ('Gastos de materiales y servicios por eventos', False, None, False, None, 3, False),
    ('Gastos de alimentos y bebidas por eventos', False, None, False, None, 3, False),
    ('Gastos de personal por eventos', False, None, False, None, 3, False),
    ('Gastos de patrocinio, donación y/o obseq por eventos', False, None, False, None, 3, False),
    ('Subtotal Gastos de TI+I', True, None, True, None, 1, False),
    ('Gastos de página web', False, None, False, None, 3, False),
    ('Gastos de desarrollo', False, None, False, None, 3, False),
    ('Utilidad antes de Comisiones por Ventas', True, None, True, 'FF66FF66', 0, False),
    ('Gastos de comisiones por ventas', False, None, False, None, 3, False),
    ('Gastos de comisiones por ventas taller', False, None, False, None, 3, False),
    ('Utilidad después de Comisiones por Ventas', True, None, True, 'FF66FF66', 0, False),
    ('Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA)', True, None, True, 'FF66FF66', 0, False),
    ('Utilidad antes de Intereses e Impuestos (EBIT)', True, None, True, 'FF66FF66', 0, False),
    ('Otros Gastos no Operacionales', True, None, True, None, 0, False),
    ('Faltante en Ventas', False, None, False, None, 3, False),
    ('Pérdida en venta de activos', False, None, False, None, 3, False),
    ('Pérdida en siniestro de activos', False, None, False, None, 3, False),
    ('Pérdida en tasa cambiaria', False, None, False, None, 3, False),
    ('Pérdida por diferencia en pagos', False, None, False, None, 3, False),
    ('Multas', False, None, False, None, 3, False),
    ('Faltante y deterioro de inventarios', False, None, False, None, 3, False),
    ('Total Gastos Operacionales y No Operacionales', True, None, True, 'FFFFFF00', 0, False),
    ('Otros Ingresos no Operacionales', True, None, True, None, 0, False),
    ('Ingresos por alquileres', False, None, False, None, 3, False),
    ('Ingresos por intereses', False, None, False, None, 3, False),
    ('Ingresos por comisiones', False, None, False, None, 3, False),
    ('Ingresos por servicios administrativos', False, None, False, None, 3, False),
    ('Sobrante en ventas', False, None, False, None, 3, False),
    ('Sobrante de inventarios', False, None, False, None, 3, False),
    ('Ganancia en venta de activos', False, None, False, None, 3, False),
    ('Ganancia por tasa cambiaria', False, None, False, None, 3, False),
    ('Ganancia por diferencias en pagos', False, None, False, None, 3, False),
    ('Utilidad Neta', True, None, True, 'FF66FF66', 0, False),
    ('ISLR', True, None, True, None, 0, False),
    ('Utilidad Neta despues de ISLR', True, None, True, 'FF66FF66', 0, False),
]
```

### Estructura Jerárquica en Base de Datos (`eerr_nodes`)
Adicionalmente, existe una jerarquía equivalente de nodos en la tabla `eerr_nodes` del archivo SQLite. A continuación se muestra la estructura jerárquica reconstruida a partir de la base de datos:

| ID | Padre ID | Nombre Nodo | Nivel | Tipo | Negrita | Color Fondo |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | NULL | ESTADO DE RESULTADOS | 0 | total | Sí | Ninguno |
| 2 | NULL | PARTIDAS | 0 | total | Sí | Ninguno |
| 3 | NULL | Total Ingresos | 0 | total | Sí | FF6AD9E8 |
| 4 | 3 |   Subtotal Ingresos por Venta de Mercancia | 1 | subtotal | Sí | Ninguno |
| 5 | 4 |       Ingresos por venta de mercancias | 3 | hoja | No | Ninguno |
| 6 | 4 |       Devoluciones sobre ventas | 3 | hoja | No | Ninguno |
| 7 | 4 |       Descuentos sobre ventas | 3 | hoja | No | Ninguno |
| 8 | 3 |   Subtotal Ingresos por Servicios | 1 | subtotal | Sí | Ninguno |
| 9 | 8 |       Ingresos por servicios del café | 3 | hoja | No | Ninguno |
| 10 | 8 |       Ingresos por zona FIT | 3 | hoja | No | Ninguno |
| 11 | 8 |       Ingresos por fletes | 3 | hoja | No | Ninguno |
| 12 | 3 |   Subtotal Ingresos por Eventos | 1 | subtotal | Sí | Ninguno |
| 13 | 12 |       Ingresos por eventos | 3 | hoja | No | Ninguno |
| 14 | 3 |   Subtotal Ingresos por Taller | 1 | subtotal | Sí | Ninguno |
| 15 | 14 |       Ingresos por taller | 3 | hoja | No | Ninguno |
| 16 | NULL | Total Costo de Ventas | 0 | total | Sí | Ninguno |
| 17 | 16 |   Subtotal Costo de Ventas por Mercancia | 1 | subtotal | Sí | Ninguno |
| 18 | 17 |       Costos de venta por mercancia | 3 | hoja | No | Ninguno |
| 19 | 16 |   Subtotal Costo de Ventas por Servicios | 1 | subtotal | Sí | Ninguno |
| 20 | 19 |       Costo de venta por servicio del café | 3 | hoja | No | Ninguno |
| 21 | 16 |   Subtotal Costo de Ventas por Eventos | 1 | subtotal | Sí | Ninguno |
| 22 | 21 |       Costo de ventas por eventos | 3 | hoja | No | Ninguno |
| 23 | NULL | Utilidad Bruta por Venta de Mercancia y Taller | 0 | total | Sí | FF66FF66 |
| 24 | NULL | Utilidad Bruta por Servicios | 0 | total | Sí | FF66FF66 |
| 25 | NULL | Utilidad Bruta por Eventos | 0 | total | Sí | FF66FF66 |
| 26 | NULL | Utilidad Bruta | 0 | total | Sí | FF66FF66 |
| 27 | NULL | Total Gastos Operacionales | 0 | total | Sí | Ninguno |
| 28 | 27 |   Subtotal Gastos de Administración | 1 | subtotal | Sí | Ninguno |
| 29 | 28 |       Gastos de servicios públicos (Agua, luz, Aseo Urbano) | 3 | hoja | No | Ninguno |
| 30 | 28 |       Gastos de servicios de telefonía e internet | 3 | hoja | No | Ninguno |
| 31 | 28 |       Gastos de alquiler del local | 3 | hoja | No | Ninguno |
| 32 | 28 |       Gastos de Condominio | 3 | hoja | No | Ninguno |
| 33 | 28 |       Gastos de asistencia outsorcing | 3 | hoja | No | Ninguno |
| 34 | 28 |       Gastos de alquiler de bienes muebles | 3 | hoja | No | Ninguno |
| 35 | 28 |       Gastos de artículos de oficina | 3 | hoja | No | Ninguno |
| 36 | 28 |       Gastos de artículos de limpieza e higiene | 3 | hoja | No | Ninguno |
| 37 | 28 |       Gastos de alimentos y bebidas | 3 | hoja | No | Ninguno |
| 38 | 28 |       Gastos de envíos y encomiendas administrativas | 3 | hoja | No | Ninguno |
| 39 | 28 |       Gastos de honorarios profesionales | 3 | hoja | No | Ninguno |
| 40 | 28 |       Gastos de estacionamiento | 3 | hoja | No | Ninguno |
| 41 | 28 |       Gastos de gestoría | 3 | hoja | No | Ninguno |
| 42 | 28 |       Gastos legales | 3 | hoja | No | Ninguno |
| 43 | 28 |       Gastos de taxi, transporte y/o delivery | 3 | hoja | No | Ninguno |
| 44 | 28 |       Gastos de suministros para taller | 3 | hoja | No | Ninguno |
| 45 | 28 |       Gastos de suministros del café | 3 | hoja | No | Ninguno |
| 46 | 28 |       Gastos por fiestas, festejos y/o reuniones | 3 | hoja | No | Ninguno |
| 47 | 28 |       Gastos de vigilancia | 3 | hoja | No | Ninguno |
| 48 | 28 |       Gastos de retenciones no descontadas | 3 | hoja | No | Ninguno |
| 49 | 28 |       Mantenimiento y reparaciones | 3 | hoja | No | Ninguno |
| 50 | 28 |       Viáticos administrativos | 3 | hoja | No | Ninguno |
| 51 | 28 |       Gastos de seguro | 3 | hoja | No | Ninguno |
| 52 | 28 |     Gastos de impuestos, tasas y contribuciones | 2 | grupo | No | Ninguno |
| 53 | 28 |     Depreciaciones, deterioro y Amortización | 2 | grupo | No | Ninguno |
| 54 | 53 |       Gasto por impuesto a las pensiones | 3 | hoja | No | Ninguno |
| 55 | 53 |       Gastos de IGTF | 3 | hoja | No | Ninguno |
| 56 | 53 |       Gastos de comisiones bancarias | 3 | hoja | No | Ninguno |
| 57 | 28 |     Gastos Bancarios | 2 | grupo | No | Ninguno |
| 58 | 57 |       Gastos de intereses sobre préstamos | 3 | hoja | No | Ninguno |
| 59 | 27 |   Subtotal Gastos de Recursos Humanos | 1 | subtotal | Sí | Ninguno |
| 60 | 59 |     Gastos de sueldos y salarios empleados y directivos | 2 | grupo | No | Ninguno |
| 61 | 60 |       Gastos de sueldos y salarios empleados | 3 | hoja | No | Ninguno |
| 62 | 60 |       Gastos de sueldos y salarios directivos | 3 | hoja | No | Ninguno |
| 63 | 60 |       Gastos de horas extras, feriados y bono nocturno | 3 | hoja | No | Ninguno |
| 64 | 60 |       Gastos de Bono de alimentación empleados | 3 | hoja | No | Ninguno |
| 65 | 60 |       Gastos de Bono de alimentación directivos | 3 | hoja | No | Ninguno |
| 66 | 59 |     Gastos de complementos empleados y directivos | 2 | grupo | No | Ninguno |
| 67 | 66 |       Gastos de complemento de sueldos y salarios empleados | 3 | hoja | No | Ninguno |
| 68 | 66 |       Gastos de complemento de sueldos y salarios directivos | 3 | hoja | No | Ninguno |
| 69 | 59 |     Gastos de personal externo | 2 | grupo | No | Ninguno |
| 70 | 69 |       Gastos de servicios de personal externo | 3 | hoja | No | Ninguno |
| 71 | 59 |     Gastos de pasivos laborales vacaciones | 2 | grupo | No | Ninguno |
| 72 | 71 |       Gastos de vacaciones empleados | 3 | hoja | No | Ninguno |
| 73 | 71 |       Gastos de vacaciones directivos | 3 | hoja | No | Ninguno |
| 74 | 71 |       Gastos de complemento de vacaciones empleados | 3 | hoja | No | Ninguno |
| 75 | 71 |       Gastos de complemento de vacaciones directivos | 3 | hoja | No | Ninguno |
| 76 | 59 |     Gastos de pasivos laborales utilidades | 2 | grupo | No | Ninguno |
| 77 | 76 |       Gastos de bono vacacional empleados | 3 | hoja | No | Ninguno |
| 78 | 76 |       Gastos de bono vacacional directivos | 3 | hoja | No | Ninguno |
| 79 | 76 |       Gastos de complemento bono vacacional empleados | 3 | hoja | No | Ninguno |
| 80 | 76 |       Gastos de complemento bono vacacional directivos | 3 | hoja | No | Ninguno |
| 81 | 76 |       Gastos de utilidades empleados | 3 | hoja | No | Ninguno |
| 82 | 76 |       Gastos de utilidades directivos | 3 | hoja | No | Ninguno |
| 83 | 76 |       Gastos de complemento de utilidades empleados | 3 | hoja | No | Ninguno |
| 84 | 76 |       Gastos de complemento de utilidades directivos | 3 | hoja | No | Ninguno |
| 85 | 59 |     Gastos de pasivos laborales prestaciones e intereses | 2 | grupo | No | Ninguno |
| 86 | 85 |       Gastos de prestaciones sociales empleados | 3 | hoja | No | Ninguno |
| 87 | 85 |       Gastos de prestaciones sociales directivos | 3 | hoja | No | Ninguno |
| 88 | 85 |       Gastos de complemento de prestaciones sociales empleados | 3 | hoja | No | Ninguno |
| 89 | 85 |       Gastos de complemento de prestaciones sociales directivos | 3 | hoja | No | Ninguno |
| 90 | 85 |       Gastos de intereses sobres prestaciones sociales empleados | 3 | hoja | No | Ninguno |
| 91 | 85 |       Gastos de intereses sobres prestaciones sociales directivos | 3 | hoja | No | Ninguno |
| 92 | 85 |       Gastos de complemento de intereses sobre prestaciones sociales empleados | 3 | hoja | No | Ninguno |
| 93 | 85 |       Gastos de complemento de intereses sobre prestaciones sociales directivos | 3 | hoja | No | Ninguno |
| 94 | 59 |     Gastos de pasivos laborales aportes | 2 | grupo | No | Ninguno |
| 95 | 94 |       Gastos de aporte patronal IVSS | 3 | hoja | No | Ninguno |
| 96 | 94 |       Gastos de aporte patronal SPF | 3 | hoja | No | Ninguno |
| 97 | 94 |       Gastos de aporte patronal FAOV | 3 | hoja | No | Ninguno |
| 98 | 94 |       Gastos de aporte patronal INCES | 3 | hoja | No | Ninguno |
| 99 | 94 |       Gastos de bono de guardería | 3 | hoja | No | Ninguno |
| 100 | 59 |     Gastos de pasivos laborales HCM | 2 | grupo | No | Ninguno |
| 101 | 100 |       Gastos de póliza HCM | 3 | hoja | No | Ninguno |
| 102 | 100 |       Gastos de salud y seguridad laboral | 3 | hoja | No | Ninguno |
| 103 | 100 |       Gastos de salud y seguridad laboral dotación | 3 | hoja | No | Ninguno |
| 104 | 100 |       Gastos de uniformes y dotación al personal | 3 | hoja | No | Ninguno |
| 105 | 59 |     Gastos de salud y seguridad laboral fiestas y agasajos | 2 | grupo | No | Ninguno |
| 106 | 105 |       Gastos de fiestas y agasajos al personal | 3 | hoja | No | Ninguno |
| 107 | 59 |     Otros gastos de personal | 2 | grupo | No | Ninguno |
| 108 | 107 |       Gastos de otros bonos empleados | 3 | hoja | No | Ninguno |
| 109 | 107 |       Gastos de transporte del personal | 3 | hoja | No | Ninguno |
| 110 | 107 |       Gastos de donaciones y obsequios al personal | 3 | hoja | No | Ninguno |
| 111 | 107 |       Gastos de capacitación al personal | 3 | hoja | No | Ninguno |
| 112 | 27 |   Subtotal Gastos de Comercialización y Logistica | 1 | subtotal | Sí | Ninguno |
| 113 | 112 |       Gastos de viáticos comerciales | 3 | hoja | No | Ninguno |
| 114 | 112 |       Gastos de comisiones empleados | 3 | hoja | No | Ninguno |
| 115 | 112 |       Gastos de comisiones empleados del taller | 3 | hoja | No | Ninguno |
| 116 | 112 |       Gastos de comisiones por venta de personal externo | 3 | hoja | No | Ninguno |
| 117 | 112 |       Gastos de fletes y envios no asociados al costo | 3 | hoja | No | Ninguno |
| 118 | 112 |       Otros gastos no asociados al costo | 3 | hoja | No | Ninguno |
| 119 | 112 |       Gastos por combustible | 3 | hoja | No | Ninguno |
| 120 | 112 |       Gastos de representación | 3 | hoja | No | Ninguno |
| 121 | 112 |       Gastos por garantia | 3 | hoja | No | Ninguno |
| 122 | 112 |       Gastos por suscripciones | 3 | hoja | No | Ninguno |
| 123 | 112 |       Gastos de Stand y/o ferias comerciales | 3 | hoja | No | Ninguno |
| 124 | 27 |   Subtotal Gastos de Mercadeo | 1 | subtotal | Sí | Ninguno |
| 125 | 124 |       Gastos de redes sociales | 3 | hoja | No | Ninguno |
| 126 | 124 |       Gastos de medios publicitarios | 3 | hoja | No | Ninguno |
| 127 | 124 |       Gastos de impresiones de material gráfico | 3 | hoja | No | Ninguno |
| 128 | 124 |       Otros gastos de publicidad y promoción | 3 | hoja | No | Ninguno |
| 129 | 124 |       Gastos de patrocinio y donación | 3 | hoja | No | Ninguno |
| 130 | 124 |       Gastos de patrocinio, donación y/o obsequios en efectivo | 3 | hoja | No | Ninguno |
| 131 | 124 |       Gastos de patrocinio, donación y/o obsequios en productos | 3 | hoja | No | Ninguno |
| 132 | 124 |       Gastos de viáticos por eventos | 3 | hoja | No | Ninguno |
| 133 | 124 |       Gastos de materiales y servicios por eventos | 3 | hoja | No | Ninguno |
| 134 | 124 |       Gastos de alimentos y bebidas por eventos | 3 | hoja | No | Ninguno |
| 135 | 124 |       Gastos de personal por eventos | 3 | hoja | No | Ninguno |
| 136 | 124 |       Gastos de patrocinio, donación y/o obseq por eventos | 3 | hoja | No | Ninguno |
| 137 | 27 |   Subtotal Gastos de TI+I | 1 | subtotal | Sí | Ninguno |
| 138 | 137 |       Gastos de página web | 3 | hoja | No | Ninguno |
| 139 | 137 |       Gastos de desarrollo | 3 | hoja | No | Ninguno |
| 140 | NULL | Utilidad antes de Comisiones por Ventas | 0 | total | Sí | FF66FF66 |
| 141 | 140 |       Gastos de comisiones por ventas | 3 | hoja | No | Ninguno |
| 142 | 140 |       Gastos de comisiones por ventas taller | 3 | hoja | No | Ninguno |
| 143 | NULL | Utilidad después de Comisiones por Ventas | 0 | total | Sí | FF66FF66 |
| 144 | NULL | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | 0 | total | Sí | FF66FF66 |
| 145 | NULL | Utilidad antes de Intereses e Impuestos (EBIT) | 0 | total | Sí | FF66FF66 |
| 146 | NULL | Otros Gastos no Operacionales | 0 | total | Sí | Ninguno |
| 147 | 146 |       Faltante en Ventas | 3 | hoja | No | Ninguno |
| 148 | 146 |       Pérdida en venta de activos | 3 | hoja | No | Ninguno |
| 149 | 146 |       Pérdida en siniestro de activos | 3 | hoja | No | Ninguno |
| 150 | 146 |       Pérdida en tasa cambiaria | 3 | hoja | No | Ninguno |
| 151 | 146 |       Pérdida por diferencia en pagos | 3 | hoja | No | Ninguno |
| 152 | 146 |       Multas | 3 | hoja | No | Ninguno |
| 153 | 146 |       Faltante y deterioro de inventarios | 3 | hoja | No | Ninguno |
| 154 | NULL | Total Gastos Operacionales y No Operacionales | 0 | total | Sí | FFFFFF00 |
| 155 | NULL | Otros Ingresos no Operacionales | 0 | total | Sí | Ninguno |
| 156 | 155 |       Ingresos por alquileres | 3 | hoja | No | Ninguno |
| 157 | 155 |       Ingresos por intereses | 3 | hoja | No | Ninguno |
| 158 | 155 |       Ingresos por comisiones | 3 | hoja | No | Ninguno |
| 159 | 155 |       Ingresos por servicios administrativos | 3 | hoja | No | Ninguno |
| 160 | 155 |       Sobrante en ventas | 3 | hoja | No | Ninguno |
| 161 | 155 |       Sobrante de inventarios | 3 | hoja | No | Ninguno |
| 162 | 155 |       Ganancia en venta de activos | 3 | hoja | No | Ninguno |
| 163 | 155 |       Ganancia por tasa cambiaria | 3 | hoja | No | Ninguno |
| 164 | 155 |       Ganancia por diferencias en pagos | 3 | hoja | No | Ninguno |
| 165 | NULL | Utilidad Neta | 0 | total | Sí | FF66FF66 |
| 166 | NULL | ISLR | 0 | total | Sí | Ninguno |
| 167 | NULL | Utilidad Neta despues de ISLR | 0 | total | Sí | FF66FF66 |

### Mapeo Partida → Nota y Nota → Línea EERR en Base de Datos
La tabla `eerr_mapping` define la relación entre las partidas/notas reales recibidas de financials y los nodos jerárquicos del Estado de Resultados en `eerr_nodes`:

| ID | Partida / Nota | Nodo ID | Nombre Nodo EERR | Signo (Afectación) |
| --- | --- | --- | --- | --- |
| 927 | Ingresos por venta de mercancias | 5 | Ingresos por venta de mercancias | 1 |
| 928 | Devoluciones sobre ventas | 6 | Devoluciones sobre ventas | 1 |
| 929 | Descuentos sobre ventas | 7 | Descuentos sobre ventas | 1 |
| 930 | Ingresos por servicios del café | 9 | Ingresos por servicios del café | 1 |
| 931 | Ingresos por zona FIT | 10 | Ingresos por zona FIT | 1 |
| 932 | Ingresos por fletes | 11 | Ingresos por fletes | 1 |
| 933 | Ingresos por eventos | 13 | Ingresos por eventos | 1 |
| 934 | Ingresos por taller | 15 | Ingresos por taller | 1 |
| 935 | Costos de venta por mercancia | 18 | Costos de venta por mercancia | 1 |
| 936 | Costo de venta por servicio del café | 20 | Costo de venta por servicio del café | 1 |
| 937 | Costo de ventas por eventos | 22 | Costo de ventas por eventos | 1 |
| 938 | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | 29 | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | 1 |
| 939 | Gastos de servicios de telefonía e internet | 30 | Gastos de servicios de telefonía e internet | 1 |
| 940 | Gastos de alquiler del local | 31 | Gastos de alquiler del local | 1 |
| 941 | Gastos de Condominio | 32 | Gastos de Condominio | 1 |
| 942 | Gastos de asistencia outsorcing | 33 | Gastos de asistencia outsorcing | 1 |
| 943 | Gastos de alquiler de bienes muebles | 34 | Gastos de alquiler de bienes muebles | 1 |
| 944 | Gastos de artículos de oficina | 35 | Gastos de artículos de oficina | 1 |
| 945 | Gastos de artículos de limpieza e higiene | 36 | Gastos de artículos de limpieza e higiene | 1 |
| 946 | Gastos de alimentos y bebidas | 37 | Gastos de alimentos y bebidas | 1 |
| 947 | Gastos de envíos y encomiendas administrativas | 38 | Gastos de envíos y encomiendas administrativas | 1 |
| 948 | Gastos de honorarios profesionales | 39 | Gastos de honorarios profesionales | 1 |
| 949 | Gastos de estacionamiento | 40 | Gastos de estacionamiento | 1 |
| 950 | Gastos de gestoría | 41 | Gastos de gestoría | 1 |
| 951 | Gastos legales | 42 | Gastos legales | 1 |
| 952 | Gastos de taxi, transporte y/o delivery | 43 | Gastos de taxi, transporte y/o delivery | 1 |
| 953 | Gastos de suministros para taller | 44 | Gastos de suministros para taller | 1 |
| 954 | Gastos de suministros del café | 45 | Gastos de suministros del café | 1 |
| 955 | Gastos por fiestas, festejos y/o reuniones | 46 | Gastos por fiestas, festejos y/o reuniones | 1 |
| 956 | Gastos de vigilancia | 47 | Gastos de vigilancia | 1 |
| 957 | Gastos de retenciones no descontadas | 48 | Gastos de retenciones no descontadas | 1 |
| 958 | Mantenimiento y reparaciones | 49 | Mantenimiento y reparaciones | 1 |
| 959 | Viáticos administrativos | 50 | Viáticos administrativos | 1 |
| 960 | Gastos de seguro | 51 | Gastos de seguro | 1 |
| 961 | Gasto por impuesto a las pensiones | 54 | Gasto por impuesto a las pensiones | 1 |
| 962 | Gastos de IGTF | 55 | Gastos de IGTF | 1 |
| 963 | Gastos de comisiones bancarias | 56 | Gastos de comisiones bancarias | 1 |
| 964 | Gastos de intereses sobre préstamos | 58 | Gastos de intereses sobre préstamos | 1 |
| 965 | Gastos de sueldos y salarios empleados | 61 | Gastos de sueldos y salarios empleados | 1 |
| 966 | Gastos de sueldos y salarios directivos | 62 | Gastos de sueldos y salarios directivos | 1 |
| 967 | Gastos de horas extras, feriados y bono nocturno | 63 | Gastos de horas extras, feriados y bono nocturno | 1 |
| 968 | Gastos de Bono de alimentación empleados | 64 | Gastos de Bono de alimentación empleados | 1 |
| 969 | Gastos de Bono de alimentación directivos | 65 | Gastos de Bono de alimentación directivos | 1 |
| 970 | Gastos de complemento de sueldos y salarios empleados | 67 | Gastos de complemento de sueldos y salarios empleados | 1 |
| 971 | Gastos de complemento de sueldos y salarios directivos | 68 | Gastos de complemento de sueldos y salarios directivos | 1 |
| 972 | Gastos de servicios de personal externo | 70 | Gastos de servicios de personal externo | 1 |
| 973 | Gastos de vacaciones empleados | 72 | Gastos de vacaciones empleados | 1 |
| 974 | Gastos de vacaciones directivos | 73 | Gastos de vacaciones directivos | 1 |
| 975 | Gastos de complemento de vacaciones empleados | 74 | Gastos de complemento de vacaciones empleados | 1 |
| 976 | Gastos de complemento de vacaciones directivos | 75 | Gastos de complemento de vacaciones directivos | 1 |

*(Mostrando los primeros 50 registros del mapeo en base de datos)*


---

## 3. LÓGICA DE CÁLCULO
A continuación se transcriben las funciones críticas de cálculo y estructuración del Estado de Resultados ubicadas en [app.py](file:///C:/Users/andre/Desktop/ultrax_app/app.py):

### Función: `calcular_subtotales_jerarquicos`
**Origen de partidas a sumar:** Dinámico desde base de datos y parámetros. Recibe `groups` (obtenido de `get_grouped_partidas`, que consulta la tabla `mapping_groups`) y `all_partidas` (compuesto de `ing_p | cos_p | gas_p` obtenidas de la tabla `mapping` mediante la función `get_clasificacion(db)`).

```python
def calcular_subtotales_jerarquicos(eerr_structure, by_partida, month, ing_p, cos_p, gas_p, groups, grouped_partidas):
    """
    Calcula todos los subtotales jerárquicos para un mes dado.
    Usa el campo level (índice 5) para determinar el scope de cada header:
    solo hace break cuando encuentra un header del mismo nivel o superior.
    level: 0=totales principales, 1=subtotales, 2=agrupadores internos, 3=partidas hoja
    """
    subtotales = {}
    all_partidas = ing_p | cos_p | gas_p

    for i, item in enumerate(eerr_structure):
        partida_name = item[0]
        is_header = item[1]
        current_level = item[5] if len(item) > 5 else 0

        if not is_header:
            continue

        total = 0
        j = i + 1

        while j < len(eerr_structure):
            child_item = eerr_structure[j]
            child_name = child_item[0]
            child_is_header = child_item[1]
            child_level = child_item[5] if len(child_item) > 5 else 0

            # Solo cortar cuando encontramos header del mismo nivel o superior
            if child_is_header and child_level <= current_level:
                break

            # Sumar solo partidas hoja (no header)
            if not child_is_header:
                if child_name in groups:
                    matching = groups[child_name]
                else:
                    matching = [p for p in all_partidas
                               if p.lower() == child_name.lower()
                               and p not in grouped_partidas]

                for p in matching:
                    total += by_partida.get(p, {}).get(month, 0)

            j += 1

        subtotales[partida_name] = total

    return subtotales



```

### Función: `calcular_totales_especiales`
**Origen de partidas a sumar:** Mixto. Usa una combinación de consultas dinámicas (las listas de partidas `ing_p`, `cos_p`, `gas_p` se obtienen dinámicamente de la base de datos) y partidas/subtotales específicos cuyos nombres están hardcodeados en el código para realizar operaciones (como `'Gastos de comisiones empleados'`, `'Gastos de impuestos, tasas y contribuciones'`, `'Utilidad Bruta'`, etc.).

```python
def calcular_totales_especiales(subtotales, by_partida, month, ing_p, cos_p, gas_p):
    """
    Calcula totales especiales con lógicas específicas.
    IMPORTANTE: los valores calculados aquí deben aplicarse DESPUÉS de
    resultados.update(subtotales) para evitar que sean sobrescritos.
    """
    totales = {}

    # 1. Total Ingresos Operativos (solo cuentas 4.x)
    totales['Total Ingresos Operativos'] = sum(by_partida.get(p, {}).get(month, 0) for p in ing_p)

    # 2. Otros Ingresos no Operacionales (ya calculado por subtotales)
    otros_ing = subtotales.get('Otros Ingresos no Operacionales', 0)
    totales['Otros Ingresos no Operacionales'] = otros_ing

    # 3. Total Ingresos = Solo Ingresos Operativos (según Excel)
    totales['Total Ingresos'] = totales['Total Ingresos Operativos']

    # 4. Total Costo de Ventas
    totales['Total Costo de Ventas'] = sum(by_partida.get(p, {}).get(month, 0) for p in cos_p)

    # 5. Utilidad Bruta = Ingresos Operativos - Costos
    totales['Utilidad Bruta'] = totales['Total Ingresos Operativos'] - totales['Total Costo de Ventas']

    # 6. Total Gastos Operacionales = suma de subtotales operacionales
    gastos_operacionales = 0
    for nombre in ['Subtotal Gastos de Administración',
                   'Subtotal Gastos de Recursos Humanos',
                   'Subtotal Gastos de Comercialización y Logistica',
                   'Subtotal Gastos de Mercadeo',
                   'Subtotal Gastos de TI+I']:
        gastos_operacionales += subtotales.get(nombre, 0)
    totales['Total Gastos Operacionales'] = gastos_operacionales

    # 7. Utilidad antes de Comisiones
    totales['Utilidad antes de Comisiones por Ventas'] = (
        totales['Utilidad Bruta'] - totales['Total Gastos Operacionales']
    )

    # 8. Comisiones (nombres reales en la BD según new_eerr_structure.py)
    comisiones = 0
    for nombre in ['Gastos de comisiones empleados',
                   'Gastos de comisiones empleados del taller',
                   'Gastos de comisiones por venta de personal externo']:
        comisiones += subtotales.get(nombre, 0)

    # 9. Utilidad después de Comisiones
    totales['Utilidad después de Comisiones por Ventas'] = (
        totales['Utilidad antes de Comisiones por Ventas'] - comisiones
    )

    # 10. Otros Gastos no Operacionales (ya calculado por subtotales)
    totales['Otros Gastos no Operacionales'] = subtotales.get('Otros Gastos no Operacionales', 0)

    # 10.5. EBIT y EBITDA (alineados a las fórmulas de Excel)
    gastos_impuestos = subtotales.get('Gastos de impuestos, tasas y contribuciones', 0)
    gastos_intereses = subtotales.get('Gastos de intereses sobre préstamos', 0)
    depreciaciones = subtotales.get('Depreciaciones, deterioro y Amortización', 0)

    totales['Utilidad antes de Intereses e Impuestos (EBIT)'] = (
        totales['Utilidad después de Comisiones por Ventas'] + gastos_intereses + gastos_impuestos
    )
    totales['Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA)'] = (
        totales['Utilidad antes de Intereses e Impuestos (EBIT)'] + depreciaciones
    )

    # 11. Utilidad Neta
    totales['Utilidad Neta'] = (
        totales['Utilidad después de Comisiones por Ventas'] -
        totales['Otros Gastos no Operacionales'] +
        otros_ing
    )

    # 12. ISLR
    totales['ISLR'] = subtotales.get('ISLR', 0)

    # 13. Utilidad Neta después de ISLR
    totales['Utilidad Neta despues de ISLR'] = totales['Utilidad Neta'] - totales['ISLR']

    return totales



```

### Función: `eerr_completo_v2_ui_adapter`
**Origen de partidas a sumar:** Mixto. Importa la estructura jerárquica estática `EERR_STRUCTURE` de `engine.py`. Luego realiza consultas dinámicas a las tablas `financials` (datos reales de transacciones), `budget` (presupuesto) y `mapping` (mediante `get_clasificacion`). Además, obtiene las agrupaciones dinámicas de la tabla `mapping_groups_v2` usando `get_grouped_partidas_v2(db, 'eerr')`.

```python
def eerr_completo_v2_ui_adapter(year, unit):
    from engine import EERR_STRUCTURE
    db   = get_db()

    year_prev = str(int(year) - 1)
    uc = f"AND unit='{unit}'" if unit else ''

    MONTH_TYPES = {
        'ENE': 'A',
        'FEB': 'B',
        'MAR': 'C',
        'ABR': 'B',
        'MAY': 'B',
        'JUN': 'D',
        'JUL': 'B',
        'AGO': 'B',
        'SEPT': 'C',
        'OCT': 'B',
        'NOV': 'B',
        'DIC': 'E',
    }

    # 1. Clasificación
    ing_p, cos_p, gas_p = get_clasificacion(db)

    # 2. Obtener grupos de presentación de mapping_groups_v2
    groups_v2, _ = get_grouped_partidas_v2(db, 'eerr')

    # 3. Leer datos año actual por partida y mes
    rows_curr = db.execute(
        f'''SELECT partida, month, SUM(amount) amount FROM financials
            WHERE year=? {uc} GROUP BY partida, month''',
        [year]
    ).fetchall()

    by_partida = {}
    for r in rows_curr:
        by_partida.setdefault(r['partida'], {})[r['month']] = r['amount']

    # Leer datos año anterior (total anual por partida)
    rows_prev = db.execute(
        f'''SELECT partida, SUM(amount) amount FROM financials
            WHERE year=? {uc} GROUP BY partida''',
        [year_prev]
    ).fetchall()
    by_prev_raw = {r['partida']: r['amount'] for r in rows_prev}

    # Leer presupuesto por partida y mes
    rows_budget = db.execute(
        f'''SELECT partida, month, SUM(amount) amount FROM budget
            WHERE year=? {uc} GROUP BY partida, month''',
        [year]
    ).fetchall()
    by_budget = {}
    for r in rows_budget:
        by_budget.setdefault(r['partida'], {})[r['month']] = r['amount']

    import unicodedata
    def norm(s):
        if not s: return ''
        s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
        return s.lower().strip()

    def resolve_leaf_value(partida_name, month, data_dict):
        if partida_name in groups_v2:
            return sum(data_dict.get(p, {}).get(month, 0) for p in groups_v2[partida_name])
        val = data_dict.get(partida_name, {}).get(month, 0)
        if val == 0:
            pn_norm = norm(partida_name)
            for k, v in data_dict.items():
                if norm(k) == pn_norm:
                    return v.get(month, 0)
        return val

    def resolve_leaf_value_prev(partida_name, data_dict):
        if partida_name in groups_v2:
            return sum(data_dict.get(p, 0) for p in groups_v2[partida_name])
        val = data_dict.get(partida_name, 0)
        if val == 0:
            pn_norm = norm(partida_name)
            for k, v in data_dict.items():
                if norm(k) == pn_norm:
                    return v
        return val

    structure_with_levels = []
    for item in EERR_STRUCTURE:
        name = item[0]
        is_header = item[1]
        level = item[5] if len(item) > 5 else (0 if is_header else 3)
        structure_with_levels.append((name, is_header, level))

    # Pre-calcular subtotales para todos los meses
    subtotales_por_mes = {}
    for m in MONTHS:
        subtotales_por_mes[m] = {}
        # Primero popular nodos hoja
        for name, is_header, level in structure_with_levels:
            if not is_header:
                subtotales_por_mes[m][name] = resolve_leaf_value(name, m, by_partida)

        # Luego calcular subtotales jerárquicos de forma recursiva/bottom-up
        for i, (name, is_header, level) in enumerate(structure_with_levels):
            if is_header:
                total = 0
                j = i + 1
                while j < len(structure_with_levels):
                    c_name, c_is_header, c_level = structure_with_levels[j]
                    if c_level <= level:
                        break
                    if not c_is_header:
                        # Excluir cuentas que se duplicarían
                        if name == 'Subtotal Gastos de Administración' and c_name in [
                            'Gasto por impuesto a las pensiones',
                            'Gastos de IGTF',
                            'Gastos de comisiones bancarias'
                        ]:
                            pass
                        elif name == 'Subtotal Gastos de Mercadeo' and c_name in [
                            'Gastos de impresiones de material gráfico'
                        ]:
                            pass
                        else:
                            total += subtotales_por_mes[m].get(c_name, 0)
                    j += 1
                subtotales_por_mes[m][name] = total

    # Definición de partidas operativas para Total Ingresos
    op_ing_partidas = ing_p - {
        'Ingresos por alquileres',
        'Ingresos por intereses',
        'Ingresos por comisiones',
        'Ingresos por servicios administrativos',
        'Sobrante en ventas',
        'Sobrante de inventarios',
        'Ganancia en venta de activos',
        'Ganancia por tasa cambiaria',
        'Ganancia por diferencias en pagos'
    }

    valores_calculados_por_mes = {}
    ingresos_ejec_mes = {}
    gastos_ejec_mes = {}
    ingresos_ppto_mes = {}
    gastos_ppto_mes = {}

    for m in MONTHS:
        ingresos_operativos = sum(by_partida.get(p, {}).get(m, 0) for p in op_ing_partidas)
        otros_ing = subtotales_por_mes[m].get('Otros Ingresos no Operacionales', 0)
        costo_ventas = sum(by_partida.get(p, {}).get(m, 0) for p in cos_p)
        utilidad_bruta = ingresos_operativos - costo_ventas

        gastos_operacionales = 0
        for nombre in ['Subtotal Gastos de Administración',
                       'Subtotal Gastos de Recursos Humanos',
                       'Subtotal Gastos de Comercialización y Logistica',
                       'Subtotal Gastos de Mercadeo',
                       'Subtotal Gastos de TI+I']:
            gastos_operacionales += subtotales_por_mes[m].get(nombre, 0)

        comisiones = 0
        for nombre in ['Gastos de comisiones empleados',
                       'Gastos de comisiones empleados del taller',
                       'Gastos de comisiones por venta de personal externo']:
            comisiones += subtotales_por_mes[m].get(nombre, 0)

        utilidad_despues_comisiones = utilidad_bruta - gastos_operacionales
        utilidad_antes_comisiones = utilidad_despues_comisiones + comisiones

        otros_gastos = subtotales_por_mes[m].get('Otros Gastos no Operacionales', 0)
        gastos_impuestos = subtotales_por_mes[m].get('Gastos de impuestos, tasas y contribuciones', 0)
        gastos_intereses = subtotales_por_mes[m].get('Gastos de intereses sobre préstamos', 0)
        depreciaciones = subtotales_por_mes[m].get('Depreciaciones, deterioro y Amortización', 0)

        ebit = utilidad_bruta - gastos_operacionales + gastos_intereses + gastos_impuestos
        ebitda = ebit + depreciaciones

        utilidad_neta = utilidad_despues_comisiones - otros_gastos + otros_ing
        islr = subtotales_por_mes[m].get('ISLR', 0)
        utilidad_neta_despues_islr = utilidad_neta - islr

        totales_mes = {
            'Total Ingresos Operativos': ingresos_operativos,
            'Otros Ingresos no Operacionales': otros_ing,
            'Total Ingresos': ingresos_operativos,
            'Total Costo de Ventas': costo_ventas,
            'Utilidad Bruta': utilidad_bruta,
            'Total Gastos Operacionales': gastos_operacionales,
            'Utilidad antes de Comisiones por Ventas': utilidad_antes_comisiones,
            'Utilidad después de Comisiones por Ventas': utilidad_despues_comisiones,
            'Otros Gastos no Operacionales': otros_gastos,
            'Total Gastos Operacionales y No Operacionales': gastos_operacionales + otros_gastos,
            'Utilidad antes de Intereses e Impuestos (EBIT)': ebit,
            'Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA)': ebitda,
            'Utilidad Neta': utilidad_neta,
            'ISLR': islr,
            'Utilidad Neta despues de ISLR': utilidad_neta_despues_islr
        }

        valores_calculados_por_mes[m] = {**subtotales_por_mes[m], **totales_mes}

        ingresos_ejec_mes[m] = ingresos_operativos
        gastos_ejec_mes[m] = gastos_operacionales
        ingresos_ppto_mes[m] = sum(by_budget.get(p, {}).get(m, 0) for p in op_ing_partidas)
        gastos_ppto_mes[m] = sum(by_budget.get(p, {}).get(m, 0) for p in gas_p)

    ingresos_prev = sum(by_prev_raw.get(p, 0) for p in op_ing_partidas)
    gastos_prev = sum(by_prev_raw.get(p, 0) for p in gas_p)

    def safe_pct(num, den):
        return round(num / den * 100, 1) if den != 0 else 0

    def safe_var(val, base):
        if base == 0: return None
        return round((val - base) / abs(base) * 100, 1)

    rows = []
    for item in EERR_STRUCTURE:
        partida_name = item[0]
        is_header = item[1]
        parent = item[2] if len(item) > 2 else None
        bold = item[3] if len(item) > 3 else False
        bg_color = item[4] if len(item) > 4 else None
        es_nota = item[6] if len(item) > 6 else False

        if is_header:
            prev_val = valores_calculados_por_mes.get('DIC', {}).get(partida_name, 0)
        else:
            prev_val = resolve_leaf_value_prev(partida_name, by_prev_raw)

        prev_pct_vtas = safe_pct(prev_val, ingresos_prev)
        prev_pct_gastos = safe_pct(prev_val, gastos_prev)

        meses_data = []
        acum_ejec = 0
        acum_ppto = 0
        acum_ing_ejec = 0
        acum_ing_ppto = 0
        acum_gas_ejec = 0
        acum_gas_ppto = 0
        val_ejec_mes_anterior = None

        for m in MONTHS:
            month_type = MONTH_TYPES[m]

            if is_header:
                val_ejec = valores_calculados_por_mes[m].get(partida_name, 0)
                val_ppto = 0
            else:
                val_ejec = resolve_leaf_value(partida_name, m, by_partida)
                val_ppto = resolve_leaf_value(partida_name, m, by_budget)

            acum_ejec += val_ejec
            acum_ppto += val_ppto
            acum_ing_ejec += ingresos_ejec_mes[m]
            acum_ing_ppto += ingresos_ppto_mes[m]
            acum_gas_ejec += gastos_ejec_mes[m]
            acum_gas_ppto += gastos_ppto_mes[m]

            pct_vtas_ejec = safe_pct(val_ejec, ingresos_ejec_mes[m])
            pct_gastos_ejec = safe_pct(val_ejec, gastos_ejec_mes[m])

            mes_data = {
                'type': month_type,
                'month': m,
                'ejecutado': {
                    'valor': round(val_ejec, 2),
                    'pct_vtas': pct_vtas_ejec,
                    'pct_gastos': pct_gastos_ejec,
                }
            }

            if month_type != 'A':
                mes_data['vari_rel'] = safe_var(val_ejec, val_ejec_mes_anterior) if val_ejec_mes_anterior is not None else None

                if month_type == 'E':  # DIC
                    mes_data['anio'] = {
                        'valor': round(acum_ejec, 2),
                        'pct_vtas': safe_pct(acum_ejec, acum_ing_ejec),
                        'pct_gastos': safe_pct(acum_ejec, acum_gas_ejec),
                    }
                else:
                    mes_data['acum_ejecutado'] = {
                        'valor': round(acum_ejec, 2),
                        'pct_vtas': safe_pct(acum_ejec, acum_ing_ejec),
                        'pct_gastos': safe_pct(acum_ejec, acum_gas_ejec),
                    }

                if month_type in ('C', 'D', 'E'):
                    mes_data['acum_ppto'] = {
                        'valor': round(acum_ppto, 2),
                        'pct_vtas': safe_pct(acum_ppto, acum_ing_ppto),
                    }
                    mes_data['var_ppto'] = safe_var(acum_ejec, acum_ppto)

                    if month_type == 'D':  # JUN
                        prom_ejec = acum_ejec / 6
                        prom_ppto = acum_ppto / 6
                        prom_ing_ejec = acum_ing_ejec / 6
                        prom_ing_ppto = acum_ing_ppto / 6
                        prom_gas_ejec = acum_gas_ejec / 6
                        prom_gas_ppto = acum_gas_ppto / 6

                        mes_data['prom_6_ejec'] = {
                            'valor': round(prom_ejec, 2),
                            'pct_vtas': safe_pct(prom_ejec, prom_ing_ejec),
                            'pct_gastos': safe_pct(prom_ejec, prom_gas_ejec),
                        }
                        mes_data['prom_6_ppto'] = {
                            'valor': round(prom_ppto, 2),
                            'pct_vtas': safe_pct(prom_ppto, prom_ing_ppto),
                        }
                        mes_data['var_ppto_prom'] = safe_var(prom_ejec, prom_ppto)

            meses_data.append(mes_data)
            val_ejec_mes_anterior = val_ejec

        rows.append({
            'partida': partida_name,
            'is_header': is_header,
            'parent': parent,
            'bold': bold,
            'bg_color': bg_color,
            'es_nota': es_nota,
            'year_prev': {
                'valor': round(prev_val, 2),
                'pct_vtas': prev_pct_vtas,
                'pct_gastos': prev_pct_gastos,
            },
            'meses': meses_data,
        })

    return {
        'year': year,
        'year_prev': year_prev,
        'unit': unit,
        'rows': rows,
    }



```

### Función: `get_grouped_partidas`
**Origen de partidas a sumar:** Dinámico. Realiza una query SQL directa a la base de datos para obtener el listado de asociaciones entre grupos y códigos Odoo (tablas `mapping_groups` o `mapping_groups_v2` según corresponda, unidas con la tabla `mapping`).

```python
def get_grouped_partidas(db, report_type='eerr'):
    """
    Retorna:
    - groups: dict {group_name: [partida1, partida2, ...]}
    - grouped_partidas: set de partidas que YA están en un grupo

    Usado en EERR/ESF para agrupar partidas bajo un nombre común.
    """
    rows = db.execute(
        '''SELECT mg.group_name, m.partida, mg.odoo_code
           FROM mapping_groups mg
           JOIN mapping m ON mg.odoo_code = m.odoo_code
           WHERE mg.report_type = ?
           ORDER BY mg.display_order, mg.group_name''',
        [report_type]
    ).fetchall()

    groups = {}
    grouped_partidas = set()

    for r in rows:
        group_name = r['group_name']
        partida = r['partida']

        if group_name not in groups:
            groups[group_name] = []
        groups[group_name].append(partida)
        grouped_partidas.add(partida)

    return groups, grouped_partidas


```

### Función: `get_grouped_partidas_v2`
**Origen de partidas a sumar:** Dinámico. Realiza una query SQL directa a la base de datos para obtener el listado de asociaciones entre grupos y códigos Odoo (tablas `mapping_groups` o `mapping_groups_v2` según corresponda, unidas con la tabla `mapping`).

```python
def get_grouped_partidas_v2(db, report_type='eerr'):
    """
    Retorna grupos basados en mapping_groups_v2 (Matriz Maestra).
    """
    rows = db.execute(
        '''SELECT mg.group_name, m.partida
           FROM mapping_groups_v2 mg
           JOIN mapping m ON mg.odoo_code = m.odoo_code
           WHERE mg.report_type = ?
           ORDER BY mg.display_order''',
        [report_type]
    ).fetchall()

    groups = {}
    grouped_partidas = set()
    for r in rows:
        gname = r['group_name']
        partida = r['partida']
        groups.setdefault(gname, []).append(partida)
        grouped_partidas.add(partida)
    return groups, grouped_partidas


```

### Función: `calcular_subtotales_jerarquicos_v2`
**Origen de partidas a sumar:** Dinámico. Suma las partidas reales asociadas a cada grupo según el diccionario `groups` que es recuperado dinámicamente de `mapping_groups_v2` en base de datos.

```python
def calcular_subtotales_jerarquicos_v2(eerr_structure, by_partida, month, ing_p, cos_p, gas_p, groups):
    """
    Calcula subtotales basándose EXCLUSIVAMENTE en mapping_groups_v2.
    """
    subtotales = {}
    for i, item in enumerate(eerr_structure):
        partida_name = item[0]
        is_header = item[1]
        if not is_header: continue

        total = 0
        # Buscar en la matriz maestra
        matching_partidas = groups.get(partida_name, [])
        for p in matching_partidas:
            total += by_partida.get(p, {}).get(month, 0)
        
        subtotales[partida_name] = total
    return subtotales


```


---

## 4. FLUJO DESDE app.py
Los endpoints expuestos en [app.py](file:///C:/Users/andre/Desktop/ultrax_app/app.py) que se encargan de generar o procesar el Estado de Resultados (EERR) son los siguientes:

### Endpoint: `@app.route('/api/eerr')` (`def eerr()`)
**Flujo de llamadas y orden de ejecución:**
1. Extrae los parámetros `year`, `unit` y `month` de la petición.
2. Conecta a la base de datos mediante `get_db()`.
3. Ejecuta una query para sumar el `amount` de cada partida en la tabla `financials` filtrada por año, mes y unidad.
4. Obtiene el listado de partidas clasificadas como ingresos, costos y gastos de la tabla `mapping` usando `get_clasificacion(db)`.
5. Calcula de forma directa sumas simples de ingresos operativos, costos de venta y gastos operacionales.
6. Calcula márgenes de utilidad bruta, neta, margen bruto % y margen neto %.
7. Devuelve el JSON con los totales y los desgloses de ingresos, costos y gastos.

```python
def eerr():
    year  = request.args.get('year', str(datetime.now().year))
    unit  = request.args.get('unit', '')
    month = request.args.get('month', '')
    db    = get_db()
    uc    = f"AND unit='{unit}'" if unit else ''
    mc    = f"AND month='{month}'" if month else ''

    rows = db.execute(
        f'SELECT partida, SUM(amount) total FROM financials WHERE year=? {uc} {mc} GROUP BY partida',
        [year]
    ).fetchall()
    data = {r['partida']: r['total'] for r in rows}

    ing_codes = set(r['partida'] for r in db.execute("SELECT DISTINCT partida FROM mapping WHERE odoo_code LIKE '4.%'").fetchall())
    cos_codes = set(r['partida'] for r in db.execute("SELECT DISTINCT partida FROM mapping WHERE odoo_code LIKE '5.%'").fetchall())
    gas_codes = set(r['partida'] for r in db.execute("SELECT DISTINCT partida FROM mapping WHERE odoo_code LIKE '6.%'").fetchall())

    def total(codes): return sum(data.get(p, 0) for p in codes)
    tI = total(ing_codes); tC = total(cos_codes); tG = total(gas_codes)
    ub = tI - tC; un = tI - tC - tG

    detail_ing = {p: data.get(p, 0) for p in ing_codes if data.get(p, 0)}
    detail_cos = {p: data.get(p, 0) for p in cos_codes if data.get(p, 0)}
    detail_gas = {p: data.get(p, 0) for p in gas_codes if data.get(p, 0)}

    return jsonify({
        'ingresos': tI, 'costos': tC, 'gastos': tG,
        'utilidad_bruta': ub, 'utilidad_neta': un,
        'margen_bruto': round(ub / tI * 100, 1) if tI else 0,
        'margen_neto':  round(un / tI * 100, 1) if tI else 0,
        'detail_ing': detail_ing, 'detail_cos': detail_cos, 'detail_gas': detail_gas
    })



```

### Endpoint: `@app.route('/api/eerr_detalle')` (`def eerr_detalle()`)
**Flujo de llamadas y orden de ejecución:**
1. Extrae los parámetros `year`, `unit`, `month_from` y `month_to` de la petición.
2. Identifica el rango de meses activos a partir del arreglo global `MONTHS`.
3. Conecta a la base de datos mediante `get_db()`.
4. Consulta la tabla `financials` para traer los montos acumulados por mes y partida.
5. Agrupa cuentas por tipo de ingreso (mercancía/servicios/eventos) llamando a `get_clasificacion_by_type(db)` (que consulta la tabla `mapping`).
6. Llama a `get_clasificacion(db)`.
7. Reconcilia los montos mensuales calculando variaciones relativas e ingresos/costos por línea de negocio.
8. Devuelve el JSON formateado.

```python
def eerr_detalle():
    """
    EERR con desglose por tipo de ingreso (mercancia_taller, servicios, eventos),
    columna ACUM EJEC y %VAR mes a mes.
    Parámetros: year, unit (opcional), month_from, month_to (opcionales para filtrar rango)
    """
    year       = request.args.get('year', str(datetime.now().year))
    unit       = request.args.get('unit', '')
    month_from = request.args.get('month_from', '')
    month_to   = request.args.get('month_to', '')
    db         = get_db()

    # Determinar meses activos
    if month_from and month_to and month_from in MONTHS and month_to in MONTHS:
        fi = MONTHS.index(month_from); ti = MONTHS.index(month_to)
        active_months = MONTHS[fi:ti+1] if fi <= ti else MONTHS[fi:] + MONTHS[:ti+1]
    else:
        active_months = MONTHS

    uc = f"AND unit='{unit}'" if unit else ''
    ph_m = ','.join('?' * len(active_months))

    # Totales por partida y mes
    rows = db.execute(
        f'''SELECT partida, month, SUM(amount) amount
            FROM financials
            WHERE year=? {uc} AND month IN ({ph_m})
            GROUP BY partida, month''',
        [year] + active_months
    ).fetchall()

    # Estructura: {partida: {month: amount}}
    by_partida = {}
    for r in rows:
        by_partida.setdefault(r['partida'], {})[r['month']] = r['amount']

    by_type = get_clasificacion_by_type(db)
    ing_p, cos_p, gas_p = get_clasificacion(db)

    def sum_type(type_key, flow):
        """Suma por tipo de ingreso/costo para un tipo y flujo ('ing'|'cos')."""
        partidas = by_type.get(type_key, {}).get(flow, set())
        result   = {}
        for m in active_months:
            result[m] = sum(by_partida.get(p, {}).get(m, 0) for p in partidas)
        return result

    def sum_partidas(partidas):
        result = {}
        for m in active_months:
            result[m] = sum(by_partida.get(p, {}).get(m, 0) for p in partidas)
        return result

    def acum(monthly_dict):
        return sum(monthly_dict.values())

    def var_pct(monthly_dict):
        """Lista de variaciones mes a mes."""
        vals = [monthly_dict.get(m, 0) for m in active_months]
        result = []
        for i, v in enumerate(vals):
            if i == 0 or vals[i-1] == 0:
                result.append(None)
            else:
                result.append(round((v - vals[i-1]) / abs(vals[i-1]) * 100, 1))
        return result

    # Ingresos por tipo
    ing_mt  = sum_type('mercancia_taller', 'ing')
    ing_svc = sum_type('servicios', 'ing')
    ing_evt = sum_type('eventos', 'ing')
    ing_tot = sum_partidas(ing_p)

    # Costos por tipo
    cos_mt  = sum_type('mercancia_taller', 'cos')
    cos_svc = sum_type('servicios', 'cos')
    cos_evt = sum_type('eventos', 'cos')
    cos_tot = sum_partidas(cos_p)

    # Utilidad bruta por tipo
    def diff_monthly(a, b):
        return {m: a.get(m, 0) - b.get(m, 0) for m in active_months}

    ub_mt  = diff_monthly(ing_mt,  cos_mt)
    ub_svc = diff_monthly(ing_svc, cos_svc)
    ub_evt = diff_monthly(ing_evt, cos_evt)
    ub_tot = diff_monthly(ing_tot, cos_tot)

    gas_tot = sum_partidas(gas_p)
    un_tot  = {m: ing_tot.get(m, 0) - cos_tot.get(m, 0) - gas_tot.get(m, 0) for m in active_months}

    def build_row(label, monthly):
        return {
            'partida': label,
            'meses':   {m: round(monthly.get(m, 0), 2) for m in active_months},
            'acum':    round(acum(monthly), 2),
            'var_pct': var_pct(monthly)
        }

    # Detalle de gastos por partida con ACUM y %VAR
    gas_detail = []
    for p in sorted(gas_p):
        monthly = {m: by_partida.get(p, {}).get(m, 0) for m in active_months}
        if acum(monthly) != 0:
            gas_detail.append(build_row(p, monthly))

    return jsonify({
        'year': year, 'unit': unit, 'months': active_months,
        'ingresos': {
            'total':           build_row('Total Ingresos', ing_tot),
            'mercancia_taller':build_row('Mercancía y Taller', ing_mt),
            'servicios':       build_row('Servicios', ing_svc),
            'eventos':         build_row('Eventos', ing_evt),
        },
        'costos': {
            'total':           build_row('Total Costos', cos_tot),
            'mercancia_taller':build_row('Costo Mercancía y Taller', cos_mt),
            'servicios':       build_row('Costo Servicios', cos_svc),
            'eventos':         build_row('Costo Eventos', cos_evt),
        },
        'utilidad_bruta': {
            'total':           build_row('Utilidad Bruta', ub_tot),
            'mercancia_taller':build_row('UB Mercancía y Taller', ub_mt),
            'servicios':       build_row('UB Servicios', ub_svc),
            'eventos':         build_row('UB Eventos', ub_evt),
        },
        'gastos': {
            'total':  build_row('Total Gastos', gas_tot),
            'detalle':gas_detail,
        },
        'utilidad_neta': build_row('Utilidad Neta', un_tot),
    })



```

### Endpoint: `@app.route('/api/eerr_completo')` (`def eerr_completo()`)
**Flujo de llamadas y orden de ejecución:**
1. Extrae los parámetros `year` y `unit` de la petición.
2. Invoca la función adaptadora común `eerr_completo_v2_ui_adapter(year, unit)`.
   - *Dentro de `eerr_completo_v2_ui_adapter`:*
     - Carga la estructura `EERR_STRUCTURE` de `engine.py`.
     - Obtiene la clasificación general de cuentas con `get_clasificacion(db)`.
     - Carga las asociaciones dinámicas de grupos de la Matriz Maestra con `get_grouped_partidas_v2(db, 'eerr')`.
     - Realiza consultas dinámicas a `financials` (año actual y año anterior) y `budget`.
     - Calcula los subtotales de forma jerárquica bottom-up usando la lógica de niveles (`level`).
     - Calcula los totales financieros especiales (EBITDA, EBIT, Utilidad Bruta, Utilidad Neta, ISLR).
     - Construye y retorna el diccionario estructurado por filas y meses.
3. Valida la coherencia de los datos ejecutando `validate_eerr_v2_integrity(year, unit, data, db)`.
   - Registra cualquier descuadre de forma no bloqueante en el log `integrity_guard.log`.
4. Retorna el resultado completo formateado en JSON.

```python
def eerr_completo():
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')

    data = eerr_completo_v2_ui_adapter(year, unit)
    
    try:
        db = get_db()
        validate_eerr_v2_integrity(year, unit, data, db)
    except Exception as e:
        app.logger.error(f"Error al ejecutar validacion de integridad: {str(e)}")

    return jsonify(data)



```

### Endpoint: `@app.route('/api/eerr_completo_v2')` (`def eerr_completo_v2()`)
**Flujo de llamadas y orden de ejecución:**
1. Extrae los parámetros `year` y `unit` de la petición.
2. Llama a la función adaptadora común `eerr_completo_v2_ui_adapter(year, unit)`.
3. Reformatea la salida del adaptador a un formato simplificado requerido por la versión 2 de la UI (sin columnas acumuladas complejas, solo montos por mes).
4. Retorna el JSON simplificado.

```python
def eerr_completo_v2():
    """
    Versión 2 del EERR: Basada íntegramente en la Matriz Maestra (mapping_groups_v2).
    """
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')

    # Obtenemos los datos desde el adaptador común para asegurar que no haya descuadres
    data = eerr_completo_v2_ui_adapter(year, unit)

    # Reformateamos los datos al contrato simplificado esperado por V2
    rows = []
    for r in data['rows']:
        meses_data = []
        acum_ejec = 0
        for m_data in r['meses']:
            val_ejec = m_data['ejecutado']['valor']
            acum_ejec += val_ejec
            meses_data.append({
                'month': m_data['month'],
                'ejecutado': {'valor': val_ejec}
            })
        rows.append({
            'partida': r['partida'],
            'is_header': r['is_header'],
            'bold': r['bold'],
            'bg_color': r['bg_color'],
            'es_nota': r.get('es_nota', False),
            'meses': meses_data,
            'acum_ejec': round(acum_ejec, 2)
        })

    return jsonify({
        'year': year,
        'unit': unit,
        'rows': rows
    })




```

### Endpoint: `@app.route('/api/eerr_divisa_real')` (`def eerr_divisa_real()`)
**Flujo de llamadas y orden de ejecución:**
1. Extrae los parámetros `year` y `unit` de la petición.
2. Conecta a la base de datos y carga las tasas de cambio de cada mes (`tasas_periodo`).
3. Carga los porcentajes de cash configurados para cada cuenta Odoo de cada mes (`metodo_pago_cuenta`).
4. Realiza una query a la tabla `financials` unida con `mapping` para obtener el `odoo_code` de cada registro.
5. Itera aplicando la función `aplicar_factor_divisa` a cada registro transaccional basándose en su % Cash y las tasas de BCV/Paralela.
6. Carga las asociaciones de grupos llamando a `get_grouped_partidas(db, 'eerr')` (utiliza la tabla `mapping_groups`, no `mapping_groups_v2`).
7. Construye la estructura del reporte iterando sobre `EERR_STRUCTURE` de `engine.py`.
8. Calcula totales y variaciones acumuladas con los montos convertidos a divisa real.
9. Devuelve el JSON con la estructura adaptada a la UI.

```python
def eerr_divisa_real():
    """
    Estado de Resultados COMPLETO con ajuste de divisa real.
    Misma estructura que /api/eerr/completo (119 partidas, tipos A/B/C/D/E)
    pero con montos ajustados por factor diferencial según % Cash/BCV.
    Parámetros: year, unit
    """
    from engine import EERR_STRUCTURE

    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')
    db = get_db()

    year_prev = str(int(year) - 1)
    uc = f"AND unit='{unit}'" if unit else ''

    # Mapeo de estructura por mes
    MONTH_TYPES = {
        'ENE': 'A', 'FEB': 'B', 'MAR': 'C', 'ABR': 'B', 'MAY': 'B', 'JUN': 'D',
        'JUL': 'B', 'AGO': 'B', 'SEPT': 'C', 'OCT': 'B', 'NOV': 'B', 'DIC': 'E',
    }

    # ── CARGAR TASAS Y MÉTODOS DE PAGO POR MES ──
    tasas_by_month = {}
    metodos_by_month = {}

    for m in MONTHS:
        # Tasas del período
        tasas_row = db.execute(
            'SELECT * FROM tasas_periodo WHERE year=? AND month=?',
            (year, m)
        ).fetchone()

        if tasas_row:
            tasas_by_month[m] = {
                'diferencial': tasas_row['factor_diferencial'],
                'recargo': tasas_row['factor_recargo']
            }

        # Métodos de pago del período
        metodos_rows = db.execute(
            'SELECT unit, odoo_code, pct_cash FROM metodo_pago_cuenta WHERE year=? AND month=?',
            (year, m)
        ).fetchall()

        metodos_by_month[m] = {(r['unit'], r['odoo_code']): r['pct_cash'] for r in metodos_rows}

    # ── LEER DATOS Y APLICAR FACTORES ──
    # Obtener datos con odoo_code para aplicar factores
    rows_curr = db.execute(
        f'''SELECT f.partida, f.month, f.unit, f.amount, m.odoo_code
            FROM financials f
            LEFT JOIN mapping m ON f.partida = m.partida
            WHERE f.year=? {uc}''',
        [year]
    ).fetchall()

    # Aplicar factores y agregar por partida/mes
    by_partida = {}
    for r in rows_curr:
        partida = r['partida']
        month = r['month']
        amount_literal = r['amount']

        # Obtener configuración del mes
        tasas = tasas_by_month.get(month)
        metodos_map = metodos_by_month.get(month, {})

        if tasas and r['odoo_code']:
            pct_cash = metodos_map.get((r['unit'], r['odoo_code']))
            diferencial = tasas['diferencial']
            amount_ajustado = aplicar_factor_divisa(amount_literal, pct_cash, diferencial)
        else:
            # Sin tasas o sin odoo_code, usar literal
            amount_ajustado = amount_literal

        by_partida.setdefault(partida, {})[month] = by_partida.get(partida, {}).get(month, 0) + amount_ajustado

    # Año anterior (sin ajuste - usar literal)
    rows_prev = db.execute(
        f'''SELECT partida, SUM(amount) amount FROM financials
            WHERE year=? {uc} GROUP BY partida''',
        [year_prev]
    ).fetchall()
    by_prev = {r['partida']: r['amount'] for r in rows_prev}

    # Presupuesto (sin ajuste)
    rows_budget = db.execute(
        f'''SELECT partida, month, SUM(amount) amount FROM budget
            WHERE year=? {uc} GROUP BY partida, month''',
        [year]
    ).fetchall()
    by_budget = {}
    for r in rows_budget:
        by_budget.setdefault(r['partida'], {})[r['month']] = r['amount']

    # Clasificación
    ing_p, cos_p, gas_p = get_clasificacion(db)

    # Obtener grupos de presentación
    groups, grouped_partidas = get_grouped_partidas(db, 'eerr')

    # Totales de ingresos y gastos por mes
    ingresos_ejec_mes = {}
    gastos_ejec_mes = {}
    ingresos_ppto_mes = {}
    gastos_ppto_mes = {}

    ingresos_prev = sum(by_prev.get(p, 0) for p in ing_p)
    gastos_prev = sum(by_prev.get(p, 0) for p in gas_p)

    for m in MONTHS:
        ingresos_ejec_mes[m] = sum(by_partida.get(p, {}).get(m, 0) for p in ing_p)
        gastos_ejec_mes[m] = sum(by_partida.get(p, {}).get(m, 0) for p in gas_p)
        ingresos_ppto_mes[m] = sum(by_budget.get(p, {}).get(m, 0) for p in ing_p)
        gastos_ppto_mes[m] = sum(by_budget.get(p, {}).get(m, 0) for p in gas_p)

    def safe_pct(num, den):
        return round(num / den * 100, 1) if den != 0 else 0

    def safe_var(val, base):
        if base == 0:
            return None
        return round((val - base) / abs(base) * 100, 1)

    # ── CONSTRUIR FILAS SEGÚN EERR_STRUCTURE ──
    rows = []
    for item in EERR_STRUCTURE:
        partida_name = item[0]
        is_header = item[1]
        parent = item[2] if len(item) > 2 else None
        bold = item[3] if len(item) > 3 else False
        bg_color = item[4] if len(item) > 4 else None

        # Verificar si esta partida es un grupo
        if partida_name in groups:
            # Es un grupo: sumar todas las partidas del grupo
            matching = groups[partida_name]
        else:
            # Buscar partida individual (excluir las que están en grupos)
            matching = [p for p in (ing_p | cos_p | gas_p)
                        if p.lower() == partida_name.lower()
                        and p not in grouped_partidas]

        # Año anterior
        prev_val = sum(by_prev.get(p, 0) for p in matching)
        prev_pct_vtas = safe_pct(prev_val, ingresos_prev)
        prev_pct_gastos = safe_pct(prev_val, gastos_prev)

        # Por cada mes
        meses_data = []
        acum_ejec = 0
        acum_ppto = 0
        acum_ing_ejec = 0
        acum_ing_ppto = 0
        acum_gas_ejec = 0
        acum_gas_ppto = 0
        val_ejec_mes_anterior = None

        for i, m in enumerate(MONTHS):
            month_type = MONTH_TYPES[m]
            val_ejec = sum(by_partida.get(p, {}).get(m, 0) for p in matching)
            val_ppto = sum(by_budget.get(p, {}).get(m, 0) for p in matching)

            acum_ejec += val_ejec
            acum_ppto += val_ppto
            acum_ing_ejec += ingresos_ejec_mes[m]
            acum_ing_ppto += ingresos_ppto_mes[m]
            acum_gas_ejec += gastos_ejec_mes[m]
            acum_gas_ppto += gastos_ppto_mes[m]

            pct_vtas_ejec = safe_pct(val_ejec, ingresos_ejec_mes[m])
            pct_gastos_ejec = safe_pct(val_ejec, gastos_ejec_mes[m])

            mes_data = {
                'type': month_type,
                'month': m,
                'ejecutado': {
                    'valor': round(val_ejec, 2),
                    'pct_vtas': pct_vtas_ejec,
                    'pct_gastos': pct_gastos_ejec,
                }
            }

            if month_type != 'A':
                mes_data['vari_rel'] = safe_var(val_ejec, val_ejec_mes_anterior) if val_ejec_mes_anterior is not None else None

                if month_type == 'E':  # DIC: AÑO
                    mes_data['anio'] = {
                        'valor': round(acum_ejec, 2),
                        'pct_vtas': safe_pct(acum_ejec, acum_ing_ejec),
                        'pct_gastos': safe_pct(acum_ejec, acum_gas_ejec),
                    }
                else:
                    mes_data['acum_ejecutado'] = {
                        'valor': round(acum_ejec, 2),
                        'pct_vtas': safe_pct(acum_ejec, acum_ing_ejec),
                        'pct_gastos': safe_pct(acum_ejec, acum_gas_ejec),
                    }

                if month_type in ('C', 'D', 'E'):
                    mes_data['acum_ppto'] = {
                        'valor': round(acum_ppto, 2),
                        'pct_vtas': safe_pct(acum_ppto, acum_ing_ppto),
                    }
                    mes_data['var_ppto'] = safe_var(acum_ejec, acum_ppto)

                    if month_type == 'D':  # JUN
                        prom_ejec = acum_ejec / 6
                        prom_ppto = acum_ppto / 6
                        prom_ing_ejec = acum_ing_ejec / 6
                        prom_ing_ppto = acum_ing_ppto / 6
                        prom_gas_ejec = acum_gas_ejec / 6

                        mes_data['prom_6_ejec'] = {
                            'valor': round(prom_ejec, 2),
                            'pct_vtas': safe_pct(prom_ejec, prom_ing_ejec),
                            'pct_gastos': safe_pct(prom_ejec, prom_gas_ejec),
                        }
                        mes_data['prom_6_ppto'] = {
                            'valor': round(prom_ppto, 2),
                            'pct_vtas': safe_pct(prom_ppto, prom_ing_ppto),
                        }
                        mes_data['var_ppto_prom'] = safe_var(prom_ejec, prom_ppto)

            meses_data.append(mes_data)
            val_ejec_mes_anterior = val_ejec

        rows.append({
            'partida': partida_name,
            'is_header': is_header,
            'parent': parent,
            'bold': bold,
            'bg_color': bg_color,
            'year_prev': {
                'valor': round(prev_val, 2),
                'pct_vtas': prev_pct_vtas,
                'pct_gastos': prev_pct_gastos,
            },
            'meses': meses_data,
        })

    return jsonify({
        'year': year,
        'year_prev': year_prev,
        'unit': unit,
        'rows': rows,
    })



```


---

## 5. INVENTARIO DE PARTIDAS ACTUALES
Este inventario contiene la totalidad de las cuentas transaccionales cargadas en la tabla `mapping` de la base de datos (un total de 717 cuentas). Para cada una se muestra su código Odoo, nombre de cuenta Odoo, la partida EERR asociada en la base de datos, el grupo de presentación de la Matriz Maestra (`mapping_groups_v2`) y la línea asociada en la jerarquía vieja (`mapping_groups`):

| Código Odoo | Nombre Cuenta Odoo | Partida Asociada (mapping.partida) | Grupo Matriz Maestra (V2) | Grupo Presentación (V1) |
| --- | --- | --- | --- | --- |
| 1.01 | Activo Corriente | Activo Corriente | Sin mapear | Sin mapear |
| 1.01.01 | Cajas | Cajas | Sin mapear | Sin mapear |
| 1.01.01.01 | Cajas en Bolivares | Cajas en Bolivares | Sin mapear | Sin mapear |
| 1.01.01.01.001 | Caja principal en Bs. | Caja principal en Bs. | Sin mapear | Sin mapear |
| 1.01.01.02 | Cajas en Divisas | Cajas en Divisas | Sin mapear | Sin mapear |
| 1.01.01.02.001 | Caja principal en $ | Caja principal en $ | Sin mapear | Sin mapear |
| 1.01.01.02.002 | Caja principal en euros cambio $ | Caja principal en euros cambio $ | Sin mapear | Sin mapear |
| 1.01.01.02.003 | Caja principal en pesos cambio $ | Caja principal en pesos cambio $ | Sin mapear | Sin mapear |
| 1.01.02 | Fondos | Fondos | Sin mapear | Sin mapear |
| 1.01.02.01 | Fondos en Bolivares | Fondos en Bolivares | Sin mapear | Sin mapear |
| 1.01.02.01.001 | Fondo de caja en tienda en Bs. Suc Rodeo | Fondo de caja en tienda en Bs. Suc Rodeo | Sin mapear | Sin mapear |
| 1.01.02.01.002 | Fondo de caja en tienda en Bs. Suc Piedemonte | Fondo de caja en tienda en Bs. Suc Piedemonte | Sin mapear | Sin mapear |
| 1.01.02.01.003 | Fondo de caja en tienda en Bs. Suc Terracota | Fondo de caja en tienda en Bs. Suc Terracota | Sin mapear | Sin mapear |
| 1.01.02.01.004 | Fondo de caja en tienda en Bs. Suc Barinas | Fondo de caja en tienda en Bs. Suc Barinas | Sin mapear | Sin mapear |
| 1.01.02.01.005 | Fondo de caja en tienda en Bs. Suc Los Naranjos | Fondo de caja en tienda en Bs. Suc Los Naranjos | Sin mapear | Sin mapear |
| 1.01.02.02 | Fondos en Divisas | Fondos en Divisas | Sin mapear | Sin mapear |
| 1.01.02.02.001 | Fondo de caja en tienda en $ Suc Rodeo | Fondo de caja en tienda en $ Suc Rodeo | Sin mapear | Sin mapear |
| 1.01.02.02.002 | Fondo de caja en tienda en $ Suc Piedemonte | Fondo de caja en tienda en $ Suc Piedemonte | Sin mapear | Sin mapear |
| 1.01.02.02.003 | Fondo de caja en tienda en $ Suc Terracota | Fondo de caja en tienda en $ Suc Terracota | Sin mapear | Sin mapear |
| 1.01.02.02.004 | Fondo de caja en tienda en $ Suc Barinas | Fondo de caja en tienda en $ Suc Barinas | Sin mapear | Sin mapear |
| 1.01.02.02.005 | Fondo de caja en tienda en $ Suc Los Naranjos | Fondo de caja en tienda en $ Suc Los Naranjos | Sin mapear | Sin mapear |
| 1.01.02.02.011 | Fondo de caja en tienda en euros cambio $ Suc Rodeo | Fondo de caja en tienda en euros cambio $ Suc Rodeo | Sin mapear | Sin mapear |
| 1.01.02.02.012 | Fondo de caja en tienda en euros cambio $ Suc Piedemonte | Fondo de caja en tienda en euros cambio $ Suc Piedemonte | Sin mapear | Sin mapear |
| 1.01.02.02.013 | Fondo de caja en tienda en euros cambio $ Suc Terracota | Fondo de caja en tienda en euros cambio $ Suc Terracota | Sin mapear | Sin mapear |
| 1.01.02.02.014 | Fondo de caja en tienda en euros cambio $ Suc Barinas | Fondo de caja en tienda en euros cambio $ Suc Barinas | Sin mapear | Sin mapear |
| 1.01.02.02.015 | Fondo de caja en tienda en euros cambio $ Suc Los Naranjos | Fondo de caja en tienda en euros cambio $ Suc Los Naranjos | Sin mapear | Sin mapear |
| 1.01.02.02.021 | Fondo de caja en tienda en pesos cambio $ Suc Rodeo | Fondo de caja en tienda en pesos cambio $ Suc Rodeo | Sin mapear | Sin mapear |
| 1.01.02.02.022 | Fondo de caja en tienda en pesos cambio $ Suc Piedemonte | Fondo de caja en tienda en pesos cambio $ Suc Piedemonte | Sin mapear | Sin mapear |
| 1.01.02.02.023 | Fondo de caja en tienda en pesos cambio $ Suc Terracota | Fondo de caja en tienda en pesos cambio $ Suc Terracota | Sin mapear | Sin mapear |
| 1.01.02.02.024 | Fondo de caja en tienda en pesos cambio $ Suc Barinas | Fondo de caja en tienda en pesos cambio $ Suc Barinas | Sin mapear | Sin mapear |
| 1.01.02.02.025 | Fondo de caja en tienda en pesos cambio $ Suc Los Naranjos | Fondo de caja en tienda en pesos cambio $ Suc Los Naranjos | Sin mapear | Sin mapear |
| 1.01.02.02.031 | Fondo de caja en mayor CCS en $ | Fondo de caja en mayor CCS en $ | Sin mapear | Sin mapear |
| 1.01.02.02.041 | Fondo de caja en mayor CCS en euros cambio $ | Fondo de caja en mayor CCS en euros cambio $ | Sin mapear | Sin mapear |
| 1.01.03 | Bancos | Bancos | Sin mapear | Sin mapear |
| 1.01.03.01 | Bancos en Bolivares | Bancos en Bolivares | Sin mapear | Sin mapear |
| 1.01.03.01.001 | Banco Mercantil | Banco Mercantil | Sin mapear | Sin mapear |
| 1.01.03.01.002 | Banco Banesco | Banco Banesco | Sin mapear | Sin mapear |
| 1.01.03.01.003 | Banco de Venezuela | Banco de Venezuela | Sin mapear | Sin mapear |
| 1.01.03.01.004 | Banco Venezolano de Credito | Banco Venezolano de Credito | Sin mapear | Sin mapear |
| 1.01.03.01.005 | Banco del Tesoro | Banco del Tesoro | Sin mapear | Sin mapear |
| 1.01.03.01.006 | Bancamiga Cuenta Corriente | Bancamiga Cuenta Corriente | Sin mapear | Sin mapear |
| 1.01.03.01.007 | Banco Provincial | Banco Provincial | Sin mapear | Sin mapear |
| 1.01.03.01.008 | Banco Nacional de Crédito BNC | Banco Nacional de Crédito BNC | Sin mapear | Sin mapear |
| 1.01.03.01.011 | Banco Bancamiga Sr Gilberto | Banco Bancamiga Sr Gilberto | Sin mapear | Sin mapear |
| 1.01.03.01.012 | Banco BNC Sr Gilberto | Banco BNC Sr Gilberto | Sin mapear | Sin mapear |
| 1.01.03.01.998 | Banco transitorio migración Terracota | Banco transitorio migración Terracota | Sin mapear | Sin mapear |
| 1.01.03.01.999 | Banco transitorio migración Barinas | Banco transitorio migración Barinas | Sin mapear | Sin mapear |
| 1.01.03.02 | Bancos en Divisas | Bancos en Divisas | Sin mapear | Sin mapear |
| 1.01.03.02.001 | Bank Of America | Bank Of America | Sin mapear | Sin mapear |
| 1.01.03.02.002 | Banesco Panamá UX | Banesco Panamá UX | Sin mapear | Sin mapear |
| 1.01.03.02.003 | Banco Mercantil Cuenta en $ | Banco Mercantil Cuenta en $ | Sin mapear | Sin mapear |
| 1.01.03.02.004 | Paypal | Paypal | Sin mapear | Sin mapear |
| 1.01.03.02.005 | Criptomonedas USDT | Criptomonedas USDT | Sin mapear | Sin mapear |
| 1.01.03.02.006 | Chase Bank, UX GROUP LLC | Chase Bank, UX GROUP LLC | Sin mapear | Sin mapear |
| 1.01.03.02.007 | Bancamiga Cash USD | Bancamiga Cash USD | Sin mapear | Sin mapear |
| 1.01.03.02.008 | Bancamiga Moneda Extranjera USD | Bancamiga Moneda Extranjera USD | Sin mapear | Sin mapear |
| 1.01.03.02.009 | Bancamiga Sr Gilberto Cash USD | Bancamiga Sr Gilberto Cash USD | Sin mapear | Sin mapear |
| 1.01.03.02.010 | BNC Cash USD | BNC Cash USD | Sin mapear | Sin mapear |
| 1.01.03.02.011 | Amerant Camilo | Amerant Camilo | Sin mapear | Sin mapear |
| 1.01.03.02.012 | Mercantil Panamá Ultrax | Mercantil Panamá Ultrax | Sin mapear | Sin mapear |
| 1.01.03.02.999 | Banco Custodia Mercantil Camilo USD | Banco Custodia Mercantil Camilo USD | Sin mapear | Sin mapear |
| 1.01.04 | Transito | Transito | Sin mapear | Sin mapear |
| 1.01.04.01 | Transito en Bolivares | Transito en Bolivares | Sin mapear | Sin mapear |
| 1.01.04.01.001 | Efectivo en transito en Bs. | Efectivo en transito en Bs. | Sin mapear | Sin mapear |
| 1.01.04.01.002 | Depositos en transito en Bs. | Depositos en transito en Bs. | Sin mapear | Sin mapear |
| 1.01.04.01.003 | Pagos del fondo en transito | Pagos del fondo en transito | Sin mapear | Sin mapear |
| 1.01.04.01.999 | Pagos de facturas cashea en tránsito | Pagos de facturas cashea en tránsito | Sin mapear | Sin mapear |
| 1.01.04.02 | Transito en Divisas | Transito en Divisas | Sin mapear | Sin mapear |
| 1.01.04.02.001 | Efectivo en transito en $ | Efectivo en transito en $ | Sin mapear | Sin mapear |
| 1.01.04.02.002 | Depositos en transito en $ | Depositos en transito en $ | Sin mapear | Sin mapear |
| 1.01.04.02.998 | Efectivo en transito por eventos | Efectivo en transito por eventos | Sin mapear | Sin mapear |
| 1.01.04.02.999 | Abonos o pagos en transito en $ | Abonos o pagos en transito en $ | Sin mapear | Sin mapear |
| 1.01.05 | Deudores Comerciales | Deudores Comerciales | Sin mapear | Sin mapear |
| 1.01.05.01 | Cuentas por cobrar clientes | Cuentas por cobrar clientes | Sin mapear | Sin mapear |
| 1.01.05.01.001 | Cuentas por cobrar clientes | Cuentas por cobrar clientes | Sin mapear | Sin mapear |
| 1.01.05.01.002 | Cuentas por cobrar AYM BIKE | Cuentas por cobrar AYM BIKE | Sin mapear | Sin mapear |
| 1.01.05.01.003 | Cuentas por cobrar BAD APPLE | Cuentas por cobrar BAD APPLE | Sin mapear | Sin mapear |
| 1.01.05.01.004 | Cuentas por cobrar ROYAL BIKE | Cuentas por cobrar ROYAL BIKE | Sin mapear | Sin mapear |
| 1.01.05.01.005 | Cuentas por cobrar SPRINT BIKE | Cuentas por cobrar SPRINT BIKE | Sin mapear | Sin mapear |
| 1.01.05.01.006 | Cuentas por cobrar TEAM BIKE | Cuentas por cobrar TEAM BIKE | Sin mapear | Sin mapear |
| 1.01.05.01.007 | Cuentas por cobrar TU BICI | Cuentas por cobrar TU BICI | Sin mapear | Sin mapear |
| 1.01.05.01.008 | Cuentas por cobrar XTREME BIKE | Cuentas por cobrar XTREME BIKE | Sin mapear | Sin mapear |
| 1.01.05.01.009 | Cuentas por cobrar SU BICICLETA | Cuentas por cobrar SU BICICLETA | Sin mapear | Sin mapear |
| 1.01.05.01.010 | Cuentas por cobrar TOPBIKE | Cuentas por cobrar TOPBIKE | Sin mapear | Sin mapear |
| 1.01.05.01.011 | Cuentas por cobrar UBIKE OSTDOOR SPORT C.A. | Cuentas por cobrar UBIKE OSTDOOR SPORT C.A. | Sin mapear | Sin mapear |
| 1.01.05.01.012 | Cuentas por cobrar DINO BIKE STORE C.A. | Cuentas por cobrar DINO BIKE STORE C.A. | Sin mapear | Sin mapear |
| 1.01.05.02 | Cuentas por cobrar empresas relacionadas | Cuentas por cobrar empresas relacionadas | Sin mapear | Sin mapear |
| 1.01.05.02.001 | Cuentas por cobrar ULTRABIKEX | Cuentas por cobrar ULTRABIKEX | Sin mapear | Sin mapear |
| 1.01.05.02.002 | Cuentas por cobrar DIUX | Cuentas por cobrar DIUX | Sin mapear | Sin mapear |
| 1.01.05.02.003 | Cuentas por cobrar PLUSUX | Cuentas por cobrar PLUSUX | Sin mapear | Sin mapear |
| 1.01.05.02.004 | Cuentas por cobrar UX BARINAS | Cuentas por cobrar UX BARINAS | Sin mapear | Sin mapear |
| 1.01.05.03 | Cuentas por cobrar empresas externas del grupo | Cuentas por cobrar empresas externas del grupo | Sin mapear | Sin mapear |
| 1.01.05.03.001 | Cuentas por cobrar UX CARACAS | Cuentas por cobrar UX CARACAS | Sin mapear | Sin mapear |
| 1.01.05.03.002 | Cuentas por cobrar UX PUERTO ORDAZ | Cuentas por cobrar UX PUERTO ORDAZ | Sin mapear | Sin mapear |
| 1.01.05.03.003 | Cuentas por cobrar UX VALENCIA | Cuentas por cobrar UX VALENCIA | Sin mapear | Sin mapear |
| 1.01.05.03.004 | Cuentas por cobrar UX LARA | Cuentas por cobrar UX LARA | Sin mapear | Sin mapear |
| 1.01.05.03.005 | Cuentas por cobrar DRYFIELD | Cuentas por cobrar DRYFIELD | Sin mapear | Sin mapear |
| 1.01.05.04 | Cuentas por cobrar socios | Cuentas por cobrar socios | Sin mapear | Sin mapear |
| 1.01.05.04.001 | Cuentas por cobrar Camilo Gonzalez | Cuentas por cobrar Camilo Gonzalez | Sin mapear | Sin mapear |
| 1.01.05.04.002 | Cuentas por cobrar Jenny Castro | Cuentas por cobrar Jenny Castro | Sin mapear | Sin mapear |
| 1.01.05.04.003 | Cuentas por cobrar Alfonso Marquez | Cuentas por cobrar Alfonso Marquez | Sin mapear | Sin mapear |
| 1.01.05.05 | Cuentas por cobrar empleados | Cuentas por cobrar empleados | Sin mapear | Sin mapear |
| 1.01.05.05.001 | Cuentas por cobrar empleados | Cuentas por cobrar empleados | Sin mapear | Sin mapear |
| 1.01.05.05.002 | Cuentas por cobrar empleados ULTRABIKEX | Cuentas por cobrar empleados ULTRABIKEX | Sin mapear | Sin mapear |
| 1.01.05.05.003 | Cuentas por cobrar empleados DIUX | Cuentas por cobrar empleados DIUX | Sin mapear | Sin mapear |
| 1.01.05.05.004 | Cuentas por cobrar empleados PLUSUX | Cuentas por cobrar empleados PLUSUX | Sin mapear | Sin mapear |
| 1.01.05.05.005 | Cuentas por cobrar empleados UX BARINAS | Cuentas por cobrar empleados UX BARINAS | Sin mapear | Sin mapear |
| 1.01.06 | Otras cuentas por cobrar | Otras cuentas por cobrar | Sin mapear | Sin mapear |
| 1.01.06.01 | Otras cuentas por cobrar | Otras cuentas por cobrar | Sin mapear | Sin mapear |
| 1.01.06.01.001 | Cuentas por cobrar terceros | Cuentas por cobrar terceros | Sin mapear | Sin mapear |
| 1.01.06.01.002 | Vuelto por cobrar terceros | Vuelto por cobrar terceros | Sin mapear | Sin mapear |
| 1.01.06.01.003 | Cuentas por Cobrar a proveedores por Garantias | Cuentas por Cobrar a proveedores por Garantias | Sin mapear | Sin mapear |
| 1.01.06.02 | Cuentas por cobrar por sociedades | Cuentas por cobrar por sociedades | Sin mapear | Sin mapear |
| 1.01.06.02.001 | Cuentas por cobrar sociedades Camilo | Cuentas por cobrar sociedades Camilo | Sin mapear | Sin mapear |
| 1.01.06.02.002 | Cuentas por cobrar sociedades Jenny | Cuentas por cobrar sociedades Jenny | Sin mapear | Sin mapear |
| 1.01.06.02.003 | Cuentas por cobrar sociedades Alfonso | Cuentas por cobrar sociedades Alfonso | Sin mapear | Sin mapear |
| 1.01.07 | Prestamos por cobrar | Prestamos por cobrar | Sin mapear | Sin mapear |
| 1.01.07.01 | Prestamos por cobrar empresas relacionadas | Prestamos por cobrar empresas relacionadas | Sin mapear | Sin mapear |
| 1.01.07.01.001 | Prestamos por cobrar ULTRABIKEX | Prestamos por cobrar ULTRABIKEX | Sin mapear | Sin mapear |
| 1.01.07.01.002 | Prestamos por cobrar DIUX | Prestamos por cobrar DIUX | Sin mapear | Sin mapear |
| 1.01.07.01.003 | Prestamos por cobrar PLUSUX | Prestamos por cobrar PLUSUX | Sin mapear | Sin mapear |
| 1.01.07.01.004 | Prestamos por cobrar UX BARINAS | Prestamos por cobrar UX BARINAS | Sin mapear | Sin mapear |
| 1.01.07.01.005 | Prestamos por cobrar UBX | Prestamos por cobrar UBX | Sin mapear | Sin mapear |
| 1.01.07.02 | Prestamos por cobrar empresas externas del grupo | Prestamos por cobrar empresas externas del grupo | Sin mapear | Sin mapear |
| 1.01.07.02.001 | Prestamos por cobrar UX CARACAS | Prestamos por cobrar UX CARACAS | Sin mapear | Sin mapear |
| 1.01.07.02.002 | Prestamos por cobrar Ux PUERTO ORDAZ | Prestamos por cobrar Ux PUERTO ORDAZ | Sin mapear | Sin mapear |
| 1.01.07.02.003 | Prestamos por cobrar UX VALENCIA | Prestamos por cobrar UX VALENCIA | Sin mapear | Sin mapear |
| 1.01.07.02.004 | Prestamos por cobrar UX LARA | Prestamos por cobrar UX LARA | Sin mapear | Sin mapear |
| 1.01.07.02.005 | Prestamos por cobrar DRYFIELD | Prestamos por cobrar DRYFIELD | Sin mapear | Sin mapear |
| 1.01.07.03 | Prestamos por cobrar socios | Prestamos por cobrar socios | Sin mapear | Sin mapear |
| 1.01.07.03.001 | Prestamos por cobrar Camilo Gonzalez | Prestamos por cobrar Camilo Gonzalez | Sin mapear | Sin mapear |
| 1.01.07.03.002 | Prestamos por cobrar Jenny Castro | Prestamos por cobrar Jenny Castro | Sin mapear | Sin mapear |
| 1.01.07.03.003 | Prestamos por cobrar Alfonso Marquez | Prestamos por cobrar Alfonso Marquez | Sin mapear | Sin mapear |
| 1.01.07.04 | Prestamos por cobrar empleados | Prestamos por cobrar empleados | Sin mapear | Sin mapear |
| 1.01.07.04.001 | Prestamos por cobrar empleados | Prestamos por cobrar empleados | Sin mapear | Sin mapear |
| 1.01.07.05 | Otros prestamos por cobrar | Otros prestamos por cobrar | Sin mapear | Sin mapear |
| 1.01.07.05.001 | Prestamos por cobrar terceros | Prestamos por cobrar terceros | Sin mapear | Sin mapear |
| 1.01.08 | Anticipos | Anticipos | Sin mapear | Sin mapear |
| 1.01.08.01 | Anticipos a proveedores | Anticipos a proveedores | Sin mapear | Sin mapear |
| 1.01.08.01.001 | Anticipos a proveedores | Anticipos a proveedores | Sin mapear | Sin mapear |
| 1.01.08.01.002 | Anticipos a proveedor Specialized | Anticipos a proveedor Specialized | Sin mapear | Sin mapear |
| 1.01.08.02 | Anticipos a socios | Anticipos a socios | Sin mapear | Sin mapear |
| 1.01.08.02.001 | Anticipos a Camilo Gonzalez | Anticipos a Camilo Gonzalez | Sin mapear | Sin mapear |
| 1.01.08.02.002 | Anticipos a Jenny Castro | Anticipos a Jenny Castro | Sin mapear | Sin mapear |
| 1.01.08.02.003 | Anticipos a Alfonso Marquez | Anticipos a Alfonso Marquez | Sin mapear | Sin mapear |
| 1.01.08.02.004 | Anticipos a Leonardo Roa | Anticipos a Leonardo Roa | Sin mapear | Sin mapear |
| 1.01.08.03 | Anticipos a empleados | Anticipos a empleados | Sin mapear | Sin mapear |
| 1.01.08.03.001 | Anticipos a empleados | Anticipos a empleados | Sin mapear | Sin mapear |
| 1.01.09 | Inventarios | Inventarios | Sin mapear | Sin mapear |
| 1.01.09.01 | Inventario de mercancias | Inventario de mercancias | Sin mapear | Sin mapear |
| 1.01.09.01.001 | Inventario de mercancias | Inventario de mercancias | Sin mapear | Sin mapear |
| 1.01.09.02 | Inventario de suministros | Inventario de suministros | Sin mapear | Sin mapear |
| 1.01.09.02.001 | Inventario de suministros del café | Inventario de suministros del café | Sin mapear | Sin mapear |
| 1.01.09.03 | Inventario en transito | Inventario en transito | Sin mapear | Sin mapear |
| 1.01.09.03.001 | Inventario de mercancias en transito | Inventario de mercancias en transito | Sin mapear | Sin mapear |
| 1.01.09.03.002 | Inventario de suministros del café en transito | Inventario de suministros del café en transito | Sin mapear | Sin mapear |
| 1.01.09.04 | Inventario en consignación | Inventario en consignación | Sin mapear | Sin mapear |
| 1.01.09.04.001 | Inventarios de mercancías propias a consignación | Inventarios de mercancías propias a consignación | Sin mapear | Sin mapear |
| 1.01.09.04.002 | Inventarios de mercancías de terceros a consignación | Inventarios de mercancías de terceros a consignación | Sin mapear | Sin mapear |
| 1.01.11 | Prepagados | Prepagados | Sin mapear | Sin mapear |
| 1.01.11.01 | Impuestos pagados por anticipado | Impuestos pagados por anticipado | Sin mapear | Sin mapear |
| 1.01.11.01.001 | IVA credito fiscal | IVA credito fiscal | Sin mapear | Sin mapear |
| 1.01.11.01.002 | Excedente de credito fiscal | Excedente de credito fiscal | Sin mapear | Sin mapear |
| 1.01.11.01.003 | Retencion IVA de clientes | Retencion IVA de clientes | Sin mapear | Sin mapear |
| 1.01.11.01.004 | Retenciones ISLR de clientes | Retenciones ISLR de clientes | Sin mapear | Sin mapear |
| 1.01.11.01.005 | Anticipo de ISLR | Anticipo de ISLR | Sin mapear | Sin mapear |
| 1.01.11.02 | Gastos pagados por anticipado | Gastos pagados por anticipado | Sin mapear | Sin mapear |
| 1.01.11.02.001 | Seguros pagados por anticipado | Seguros pagados por anticipado | Sin mapear | Sin mapear |
| 1.01.11.02.002 | Intereses pagados por anticipado | Intereses pagados por anticipado | Sin mapear | Sin mapear |
| 1.01.11.02.003 | Alquileres pagados por anticipado | Alquileres pagados por anticipado | Sin mapear | Sin mapear |
| 1.02 | Activo No Corriente | Activo No Corriente | Sin mapear | Sin mapear |
| 1.02.01 | Deudores Comerciales L.P. | Deudores Comerciales L.P. | Sin mapear | Sin mapear |
| 1.02.01.01 | Cuentas por cobrar clientes L.P. | Cuentas por cobrar clientes L.P. | Sin mapear | Sin mapear |
| 1.02.01.01.001 | Cuentas por cobrar clientes Mayor y Ciclismo L.P. | Cuentas por cobrar clientes Mayor y Ciclismo L.P. | Sin mapear | Sin mapear |
| 1.02.01.02 | Cuentas por cobrar empresas relacionadas L.P. | Cuentas por cobrar empresas relacionadas L.P. | Sin mapear | Sin mapear |
| 1.02.01.02.001 | Cuentas por cobrar ULTRABIKEX L.P. | Cuentas por cobrar ULTRABIKEX L.P. | Sin mapear | Sin mapear |
| 1.02.01.02.002 | Cuentas por cobrar DIUX L.P. | Cuentas por cobrar DIUX L.P. | Sin mapear | Sin mapear |
| 1.02.01.02.003 | Cuentas por cobrar PLUSUX L.P. | Cuentas por cobrar PLUSUX L.P. | Sin mapear | Sin mapear |
| 1.02.01.02.004 | Cuentas por cobrar UX BARINAS L.P. | Cuentas por cobrar UX BARINAS L.P. | Sin mapear | Sin mapear |
| 1.02.01.03 | Cuentas por cobrar empresas externas del grupo L.P. | Cuentas por cobrar empresas externas del grupo L.P. | Sin mapear | Sin mapear |
| 1.02.01.03.001 | Cuentas por cobrar UX CARACAS L.P. | Cuentas por cobrar UX CARACAS L.P. | Sin mapear | Sin mapear |
| 1.02.01.03.002 | Cuentas por cobrar UX PUERTO ORDAZ L.P. | Cuentas por cobrar UX PUERTO ORDAZ L.P. | Sin mapear | Sin mapear |
| 1.02.01.03.003 | Cuentas por cobrar UX VALENCIA L.P. | Cuentas por cobrar UX VALENCIA L.P. | Sin mapear | Sin mapear |
| 1.02.01.03.004 | Cuentas por cobrar UX LARA L.P. | Cuentas por cobrar UX LARA L.P. | Sin mapear | Sin mapear |
| 1.02.01.03.005 | Cuentas por cobrar DRYFIELD L.P. | Cuentas por cobrar DRYFIELD L.P. | Sin mapear | Sin mapear |
| 1.02.01.04 | Cuentas por cobrar socios L.P. | Cuentas por cobrar socios L.P. | Sin mapear | Sin mapear |
| 1.02.01.04.001 | Cuentas por cobrar Camilo Gonzalez L.P. | Cuentas por cobrar Camilo Gonzalez L.P. | Sin mapear | Sin mapear |
| 1.02.01.04.002 | Cuentas por cobrar Jenny Castro L.P. | Cuentas por cobrar Jenny Castro L.P. | Sin mapear | Sin mapear |
| 1.02.01.04.003 | Cuentas por cobrar Alfonso Marquez L.P. | Cuentas por cobrar Alfonso Marquez L.P. | Sin mapear | Sin mapear |
| 1.02.01.05 | Cuentas por cobrar empleados L.P. | Cuentas por cobrar empleados L.P. | Sin mapear | Sin mapear |
| 1.02.01.05.001 | Cuentas por cobrar empleados L.P. | Cuentas por cobrar empleados L.P. | Sin mapear | Sin mapear |
| 1.02.01.05.002 | Cuentas por cobrar empleados ULTRABIKEX L.P. | Cuentas por cobrar empleados ULTRABIKEX L.P. | Sin mapear | Sin mapear |
| 1.02.01.05.003 | Cuentas por cobrar empleados DIUX L.P. | Cuentas por cobrar empleados DIUX L.P. | Sin mapear | Sin mapear |
| 1.02.01.05.004 | Cuentas por cobrar empleados PLUSUX L.P. | Cuentas por cobrar empleados PLUSUX L.P. | Sin mapear | Sin mapear |
| 1.02.01.05.005 | Cuentas por cobrar empleados UX BARINAS L.P. | Cuentas por cobrar empleados UX BARINAS L.P. | Sin mapear | Sin mapear |
| 1.02.02 | Otras cuentas por cobrar L.P. | Otras cuentas por cobrar L.P. | Sin mapear | Sin mapear |
| 1.02.02.01 | Otras cuentas por cobrar L.P. | Otras cuentas por cobrar L.P. | Sin mapear | Sin mapear |
| 1.02.02.01.001 | Cuentas por cobrar terceros L.P. | Cuentas por cobrar terceros L.P. | Sin mapear | Sin mapear |
| 1.02.02.01.002 | Vuelto por cobrar terceros L.P. | Vuelto por cobrar terceros L.P. | Sin mapear | Sin mapear |
| 1.02.02.02 | Cuentas por cobrar por sociedades L.P. | Cuentas por cobrar por sociedades L.P. | Sin mapear | Sin mapear |
| 1.02.02.02.001 | Cuentas por cobrar sociedades Camilo L.P. | Cuentas por cobrar sociedades Camilo L.P. | Sin mapear | Sin mapear |
| 1.02.02.02.002 | Cuentas por cobrar sociedades Jenny L.P. | Cuentas por cobrar sociedades Jenny L.P. | Sin mapear | Sin mapear |
| 1.02.02.02.003 | Cuentas por cobrar sociedades Alfonso L.P. | Cuentas por cobrar sociedades Alfonso L.P. | Sin mapear | Sin mapear |
| 1.02.02.02.004 | Cuentas por cobrar sociedades Otros Socios | Cuentas por cobrar sociedades Otros Socios | Sin mapear | Sin mapear |
| 1.02.03 | Prestamos por cobrar L.P. | Prestamos por cobrar L.P. | Sin mapear | Sin mapear |
| 1.02.03.01 | Prestamos por cobrar empresas relacionadas L.P. | Prestamos por cobrar empresas relacionadas L.P. | Sin mapear | Sin mapear |
| 1.02.03.01.001 | Prestamos por cobrar ULTRABIKEX L.P. | Prestamos por cobrar ULTRABIKEX L.P. | Sin mapear | Sin mapear |
| 1.02.03.01.002 | Prestamos por cobrar DIUX L.P. | Prestamos por cobrar DIUX L.P. | Sin mapear | Sin mapear |
| 1.02.03.01.003 | Prestamos por cobrar PLUSUX L.P. | Prestamos por cobrar PLUSUX L.P. | Sin mapear | Sin mapear |
| 1.02.03.01.004 | Prestamos por cobrar UX BARINAS L.P. | Prestamos por cobrar UX BARINAS L.P. | Sin mapear | Sin mapear |
| 1.02.03.01.005 | Prestamos por cobrar UBX L.P. | Prestamos por cobrar UBX L.P. | Sin mapear | Sin mapear |
| 1.02.03.02 | Prestamos por cobrar empresas externas del grupo L.P. | Prestamos por cobrar empresas externas del grupo L.P. | Sin mapear | Sin mapear |
| 1.02.03.02.001 | Prestamos por cobrar UX CARACAS L.P. | Prestamos por cobrar UX CARACAS L.P. | Sin mapear | Sin mapear |
| 1.02.03.02.002 | Prestamos por cobrar Ux PUERTO ORDAZ L.P. | Prestamos por cobrar Ux PUERTO ORDAZ L.P. | Sin mapear | Sin mapear |
| 1.02.03.02.003 | Prestamos por cobrar UX VALENCIA L.P. | Prestamos por cobrar UX VALENCIA L.P. | Sin mapear | Sin mapear |
| 1.02.03.02.004 | Prestamos por cobrar UX LARA L.P. | Prestamos por cobrar UX LARA L.P. | Sin mapear | Sin mapear |
| 1.02.03.02.005 | Prestamos por cobrar DRYFIELD L.P. | Prestamos por cobrar DRYFIELD L.P. | Sin mapear | Sin mapear |
| 1.02.03.03 | Prestamos por cobrar socios L.P. | Prestamos por cobrar socios L.P. | Sin mapear | Sin mapear |
| 1.02.03.03.001 | Prestamos por cobrar Camilo Gonzalez L.P. | Prestamos por cobrar Camilo Gonzalez L.P. | Sin mapear | Sin mapear |
| 1.02.03.03.002 | Prestamos por cobrar Jenny Castro L.P. | Prestamos por cobrar Jenny Castro L.P. | Sin mapear | Sin mapear |
| 1.02.03.03.003 | Prestamos por cobrar Alfonso Marquez L.P. | Prestamos por cobrar Alfonso Marquez L.P. | Sin mapear | Sin mapear |
| 1.02.03.04 | Prestamos por cobrar empleados L.P. | Prestamos por cobrar empleados L.P. | Sin mapear | Sin mapear |
| 1.02.03.04.001 | Prestamos por cobrar empleados L.P. | Prestamos por cobrar empleados L.P. | Sin mapear | Sin mapear |
| 1.02.03.05 | Otros prestamos por cobrar L.P. | Otros prestamos por cobrar L.P. | Sin mapear | Sin mapear |
| 1.02.03.05.001 | Prestamos por cobrar tercercos L.P. | Prestamos por cobrar tercercos L.P. | Sin mapear | Sin mapear |
| 1.02.04 | Anticipos L.P. | Anticipos L.P. | Sin mapear | Sin mapear |
| 1.02.04.01 | Anticipos a proveedores L.P. | Anticipos a proveedores L.P. | Sin mapear | Sin mapear |
| 1.02.04.01.001 | Anticipos a proveedores L.P. | Anticipos a proveedores L.P. | Sin mapear | Sin mapear |
| 1.02.04.01.002 | Anticipos a proveedor Specialized L.P. | Anticipos a proveedor Specialized L.P. | Sin mapear | Sin mapear |
| 1.02.04.02 | Anticipos a socios L.P. | Anticipos a socios L.P. | Sin mapear | Sin mapear |
| 1.02.04.02.001 | Anticipos Camilo Gonzalez L.P. | Anticipos Camilo Gonzalez L.P. | Sin mapear | Sin mapear |
| 1.02.04.02.002 | Anticipos Jenny Castro L.P. | Anticipos Jenny Castro L.P. | Sin mapear | Sin mapear |
| 1.02.04.02.003 | Anticipos Alfonso Marquez L.P. | Anticipos Alfonso Marquez L.P. | Sin mapear | Sin mapear |
| 1.02.04.02.004 | Anticipos Leonardo Roa L.P. | Anticipos Leonardo Roa L.P. | Sin mapear | Sin mapear |
| 1.02.04.03 | Anticipos a empleados L.P. | Anticipos a empleados L.P. | Sin mapear | Sin mapear |
| 1.02.04.03.001 | Anticipos a empleados L.P. | Anticipos a empleados L.P. | Sin mapear | Sin mapear |
| 1.02.04.04 | Anticipos de prestaciones sociales L.P. | Anticipos de prestaciones sociales L.P. | Sin mapear | Sin mapear |
| 1.02.04.04.001 | Anticipos de prestaciones sociales L.P. | Anticipos de prestaciones sociales L.P. | Sin mapear | Sin mapear |
| 1.02.05 | Propiedades de Inversion | Propiedades de Inversion | Sin mapear | Sin mapear |
| 1.02.05.01 | Inversion en acciones | Inversion en acciones | Sin mapear | Sin mapear |
| 1.02.05.01.001 | Inversion en acciones | Inversion en acciones | Sin mapear | Sin mapear |
| 1.02.06 | Propiedad, planta y equipos | Propiedad, planta y equipos | Sin mapear | Sin mapear |
| 1.02.06.01 | Terrenos | Terrenos | Sin mapear | Sin mapear |
| 1.02.06.01.001 | Terreno | Terreno | Sin mapear | Sin mapear |
| 1.02.06.01.002 | Deterioro acum. Terreno | Deterioro acum. Terreno | Sin mapear | Sin mapear |
| 1.02.06.02 | Mobiliario y equipos | Mobiliario y equipos | Sin mapear | Sin mapear |
| 1.02.06.02.001 | Mobiliario y equipos | Mobiliario y equipos | Sin mapear | Sin mapear |
| 1.02.06.02.500 | Dep. Acum. Mob y Equipos | Dep. Acum. Mob y Equipos | Sin mapear | Sin mapear |
| 1.02.06.02.501 | Deterioro acum. Mob y Equipos | Deterioro acum. Mob y Equipos | Sin mapear | Sin mapear |
| 1.02.06.03 | Maquinaria y equipos | Maquinaria y equipos | Sin mapear | Sin mapear |
| 1.02.06.03.001 | Maquinarias y Equipos | Maquinarias y Equipos | Sin mapear | Sin mapear |
| 1.02.06.03.500 | Dep. Acum. Maquinarias y equipos | Dep. Acum. Maquinarias y equipos | Sin mapear | Sin mapear |
| 1.02.06.03.501 | Det. Acum. Maquinarias y equipos | Det. Acum. Maquinarias y equipos | Sin mapear | Sin mapear |
| 1.02.06.04 | Vehiculos | Vehiculos | Sin mapear | Sin mapear |
| 1.02.06.04.001 | Vehiculo Grand Cheroke año 2006 | Vehiculo Grand Cheroke año 2006 | Sin mapear | Sin mapear |
| 1.02.06.04.002 | Vehiculo Orlando año 2014 | Vehiculo Orlando año 2014 | Sin mapear | Sin mapear |
| 1.02.06.04.003 | Vehiculo Camion Cargo año 2006 | Vehiculo Camion Cargo año 2006 | Sin mapear | Sin mapear |
| 1.02.06.04.004 | Moto | Moto | Sin mapear | Sin mapear |
| 1.02.06.04.005 | Vehiculo Kangoo | Vehiculo Kangoo | Sin mapear | Sin mapear |
| 1.02.06.04.006 | Vehículo Hilux | Vehículo Hilux | Sin mapear | Sin mapear |
| 1.02.06.04.007 | Vehículo Toyota Vans | Vehículo Toyota Vans | Sin mapear | Sin mapear |
| 1.02.06.04.500 | Dep. Acum. Vehiculo Grand Cheroke año 2006 | Dep. Acum. Vehiculo Grand Cheroke año 2006 | Sin mapear | Sin mapear |
| 1.02.06.04.501 | Det. Acum. Vehiculo Grand Cheroke año 2006 | Det. Acum. Vehiculo Grand Cheroke año 2006 | Sin mapear | Sin mapear |
| 1.02.06.04.502 | Dep. Acum. Vehiculo Orlando año 2014 | Dep. Acum. Vehiculo Orlando año 2014 | Sin mapear | Sin mapear |
| 1.02.06.04.503 | Det. Acum. Vehiculo Orlando año 2014 | Det. Acum. Vehiculo Orlando año 2014 | Sin mapear | Sin mapear |
| 1.02.06.04.504 | Dep. Acum. Vehiculo Camion Cargo año 2006 | Dep. Acum. Vehiculo Camion Cargo año 2006 | Sin mapear | Sin mapear |
| 1.02.06.04.505 | Det. Acum. Vehiculo Camion Cargo año 2006 | Det. Acum. Vehiculo Camion Cargo año 2006 | Sin mapear | Sin mapear |
| 1.02.06.04.506 | Dep. Acum. Moto | Dep. Acum. Moto | Sin mapear | Sin mapear |
| 1.02.06.04.507 | Det. Acum. Moto | Det. Acum. Moto | Sin mapear | Sin mapear |
| 1.02.06.04.508 | Dep. Acum. Vehiculo Kangoo | Dep. Acum. Vehiculo Kangoo | Sin mapear | Sin mapear |
| 1.02.06.04.509 | Det. Acum. Vehiculo Kangoo | Det. Acum. Vehiculo Kangoo | Sin mapear | Sin mapear |
| 1.02.06.04.510 | Dep. Acum. Vehículo Hilux | Dep. Acum. Vehículo Hilux | Sin mapear | Sin mapear |
| 1.02.06.04.511 | Det. Acum. Vehículo Hilux | Det. Acum. Vehículo Hilux | Sin mapear | Sin mapear |
| 1.02.06.04.512 | Dep. Acum. Vehículo Toyota Vans | Dep. Acum. Vehículo Toyota Vans | Sin mapear | Sin mapear |
| 1.02.06.04.513 | Det. Acum. Vehículo Toyota Vans | Det. Acum. Vehículo Toyota Vans | Sin mapear | Sin mapear |
| 1.02.06.05 | Edificios y construcciones | Edificios y construcciones | Sin mapear | Sin mapear |
| 1.02.06.05.001 | Local C.C Plaza Mayor LP-4 | Local C.C Plaza Mayor LP-4 | Sin mapear | Sin mapear |
| 1.02.06.05.002 | Galpon Complejo Ind. y Com Gral. Avelino | Galpon Complejo Ind. y Com Gral. Avelino | Sin mapear | Sin mapear |
| 1.02.06.05.500 | Dep. Acum. Local C.C Plaza Mayor LP-4 | Dep. Acum. Local C.C Plaza Mayor LP-4 | Sin mapear | Sin mapear |
| 1.02.06.05.501 | Det. Acum. Local C.C Plaza Mayor LP-4 | Det. Acum. Local C.C Plaza Mayor LP-4 | Sin mapear | Sin mapear |
| 1.02.06.05.502 | Dep. Acum. Galpon Complejo Ind. y Com Gral. Avelino | Dep. Acum. Galpon Complejo Ind. y Com Gral. Avelino | Sin mapear | Sin mapear |
| 1.02.06.05.503 | Det. Acum. Galpon Complejo Ind. y Com Gral. Avelino | Det. Acum. Galpon Complejo Ind. y Com Gral. Avelino | Sin mapear | Sin mapear |
| 1.02.06.06 | Materiales de eventos | Materiales de eventos | Sin mapear | Sin mapear |
| 1.02.06.06.001 | Materiales para eventos | Materiales para eventos | Sin mapear | Sin mapear |
| 1.02.06.06.500 | Dep. Acum. Materiales para eventos | Dep. Acum. Materiales para eventos | Sin mapear | Sin mapear |
| 1.02.06.06.501 | Det. Acum. Materiales para eventos | Det. Acum. Materiales para eventos | Sin mapear | Sin mapear |
| 1.02.06.07 | Herramientas | Herramientas | Sin mapear | Sin mapear |
| 1.02.06.07.001 | Herramientas | Herramientas | Sin mapear | Sin mapear |
| 1.02.06.07.500 | Dep. Acum. Herramientas | Dep. Acum. Herramientas | Sin mapear | Sin mapear |
| 1.02.06.07.501 | Det. Acum. Herramientas | Det. Acum. Herramientas | Sin mapear | Sin mapear |
| 1.02.06.08 | Utensilios y equipos de cocina | Utensilios y equipos de cocina | Sin mapear | Sin mapear |
| 1.02.06.08.001 | Utensilios y equipos de cocina | Utensilios y equipos de cocina | Sin mapear | Sin mapear |
| 1.02.06.08.500 | Dep. Acum. Utensilios y equipos de cocina | Dep. Acum. Utensilios y equipos de cocina | Sin mapear | Sin mapear |
| 1.02.06.08.501 | Det. Acum. Utensilios y equipos de cocina | Det. Acum. Utensilios y equipos de cocina | Sin mapear | Sin mapear |
| 1.02.06.09 | Equipamiento deportivo | Equipamiento deportivo | Sin mapear | Sin mapear |
| 1.02.06.09.001 | Equipamiento deportivo | Equipamiento deportivo | Sin mapear | Sin mapear |
| 1.02.06.09.500 | Dep. Acum. Equipamiento deportivo | Dep. Acum. Equipamiento deportivo | Sin mapear | Sin mapear |
| 1.02.06.09.501 | Det. Acum. Equipamiento deportivo | Det. Acum. Equipamiento deportivo | Sin mapear | Sin mapear |
| 1.02.06.10 | Mejoras en bienes arrendados | Mejoras en bienes arrendados | Sin mapear | Sin mapear |
| 1.02.06.10.001 | Mejoras en bienes arrendados | Mejoras en bienes arrendados | Sin mapear | Sin mapear |
| 1.02.06.10.500 | Dep. Acum. Mejoras bienes arrendados | Dep. Acum. Mejoras bienes arrendados | Sin mapear | Sin mapear |
| 1.02.06.10.501 | Det. Acum. Mejoras bienes arrendados | Det. Acum. Mejoras bienes arrendados | Sin mapear | Sin mapear |
| 1.02.07 | Activos intangibles | Activos intangibles | Sin mapear | Sin mapear |
| 1.02.07.01 | Software Odoo | Software Odoo | Sin mapear | Sin mapear |
| 1.02.07.01.001 | Software Odoo | Software Odoo | Sin mapear | Sin mapear |
| 1.02.07.01.002 | Amortización Acum Odoo | Amortización Acum Odoo | Sin mapear | Sin mapear |
| 1.02.07.01.500 | Amortización Acum Odoo | Amortización Acum Odoo | Sin mapear | Sin mapear |
| 1.02.07.02 | CRM | CRM | Sin mapear | Sin mapear |
| 1.02.07.02.001 | Software CRM | Software CRM | Sin mapear | Sin mapear |
| 1.02.07.02.002 | Amortización CRM | Amortización CRM | Sin mapear | Sin mapear |
| 2.01 | Pasivo Corriente | Pasivo Corriente | Sin mapear | Sin mapear |
| 2.01.01 | Acreedores comerciales | Acreedores comerciales | Sin mapear | Sin mapear |
| 2.01.01.01 | Cuentas por pagar proveedores | Cuentas por pagar proveedores | Sin mapear | Sin mapear |
| 2.01.01.01.001 | Cuentas por pagar proveedores nacionales | Cuentas por pagar proveedores nacionales | Sin mapear | Sin mapear |
| 2.01.01.01.002 | Cuentas por pagar proveedores Internacionales | Cuentas por pagar proveedores Internacionales | Sin mapear | Sin mapear |
| 2.01.01.01.003 | Cuentas por pagar Specialized | Cuentas por pagar Specialized | Sin mapear | Sin mapear |
| 2.01.01.02 | Cuentas por pagar empresas relacionadas | Cuentas por pagar empresas relacionadas | Sin mapear | Sin mapear |
| 2.01.01.02.001 | Cuentas por pagar ULTRABIKEX | Cuentas por pagar ULTRABIKEX | Sin mapear | Sin mapear |
| 2.01.01.02.002 | Cuentas por pagar DIUX | Cuentas por pagar DIUX | Sin mapear | Sin mapear |
| 2.01.01.02.003 | Cuentas por pagar PLUSUX | Cuentas por pagar PLUSUX | Sin mapear | Sin mapear |
| 2.01.01.02.004 | Cuentas por pagar UX BARINAS | Cuentas por pagar UX BARINAS | Sin mapear | Sin mapear |
| 2.01.01.03 | Cuentas por pagar empresas externas del grupo | Cuentas por pagar empresas externas del grupo | Sin mapear | Sin mapear |
| 2.01.01.03.001 | Cuentas por pagar UX CARACAS | Cuentas por pagar UX CARACAS | Sin mapear | Sin mapear |
| 2.01.01.03.002 | Cuentas por pagar UX PUERTO ORDAZ | Cuentas por pagar UX PUERTO ORDAZ | Sin mapear | Sin mapear |
| 2.01.01.03.003 | Cuentas por pagar UX VALENCIA | Cuentas por pagar UX VALENCIA | Sin mapear | Sin mapear |
| 2.01.01.03.004 | Cuentas por pagar UX LARA | Cuentas por pagar UX LARA | Sin mapear | Sin mapear |
| 2.01.01.03.005 | Cuentas por pagar DRYFIELD | Cuentas por pagar DRYFIELD | Sin mapear | Sin mapear |
| 2.01.01.04 | Cuentas por pagar socios | Cuentas por pagar socios | Sin mapear | Sin mapear |
| 2.01.01.04.001 | Cuentas por pagar Camilo Gonzalez | Cuentas por pagar Camilo Gonzalez | Sin mapear | Sin mapear |
| 2.01.01.04.002 | Cuentas por pagar Jenny Castro | Cuentas por pagar Jenny Castro | Sin mapear | Sin mapear |
| 2.01.01.04.003 | Cuentas por pagar Alfonso Marquez | Cuentas por pagar Alfonso Marquez | Sin mapear | Sin mapear |
| 2.01.01.05 | Cuentas por pagar TDC y TDC | Cuentas por pagar TDC y TDC | Sin mapear | Sin mapear |
| 2.01.01.05.001 | Tarjeta de crédito Bofa Sra Zaida | Tarjeta de crédito Bofa Sra Zaida | Sin mapear | Sin mapear |
| 2.01.01.05.002 | Tarjeta de crédito Bancamiga Camilo | Tarjeta de crédito Bancamiga Camilo | Sin mapear | Sin mapear |
| 2.01.01.05.003 | Tarjeta de débito Banesco Panamá Camilo | Tarjeta de débito Banesco Panamá Camilo | Sin mapear | Sin mapear |
| 2.01.01.05.004 | Tarjeta de crédito BNC Camilo | Tarjeta de crédito BNC Camilo | Sin mapear | Sin mapear |
| 2.01.01.05.005 | Tarjeta de crédito Bancamiga Gilberto | Tarjeta de crédito Bancamiga Gilberto | Sin mapear | Sin mapear |
| 2.01.01.06 | Cuentas por pagar a proveedores en consignacion | Cuentas por pagar a proveedores en consignacion | Sin mapear | Sin mapear |
| 2.01.01.06.001 | Cuentas por pagar a proveedores en consignacion | Cuentas por pagar a proveedores en consignacion | Sin mapear | Sin mapear |
| 2.01.02 | Otras cuentas por pagar | Otras cuentas por pagar | Sin mapear | Sin mapear |
| 2.01.02.01 | Otras cuentas por pagar | Otras cuentas por pagar | Sin mapear | Sin mapear |
| 2.01.02.01.001 | Cuentas por pagar terceros | Cuentas por pagar terceros | Sin mapear | Sin mapear |
| 2.01.02.01.002 | Vuelto por pagar terceros | Vuelto por pagar terceros | Sin mapear | Sin mapear |
| 2.01.02.01.003 | Propinas por pagar | Propinas por pagar | Sin mapear | Sin mapear |
| 2.01.02.02 | Descuentos a empleados por pagar | Descuentos a empleados por pagar | Sin mapear | Sin mapear |
| 2.01.02.02.001 | Descuentos a empleados por pagar a ULTRABIKEX | Descuentos a empleados por pagar a ULTRABIKEX | Sin mapear | Sin mapear |
| 2.01.02.02.002 | Descuentos a empleados por pagar a DIUX | Descuentos a empleados por pagar a DIUX | Sin mapear | Sin mapear |
| 2.01.02.02.003 | Descuentos a empleados por pagar a PLUSUX | Descuentos a empleados por pagar a PLUSUX | Sin mapear | Sin mapear |
| 2.01.02.02.004 | Descuentos a empleados por Pagar a UX BARINAS | Descuentos a empleados por Pagar a UX BARINAS | Sin mapear | Sin mapear |
| 2.01.02.03 | Sueldos y salarios por pagar | Sueldos y salarios por pagar | Sin mapear | Sin mapear |
| 2.01.02.03.001 | Sueldos y salarios por pagar | Sueldos y salarios por pagar | Sin mapear | Sin mapear |
| 2.01.02.03.002 | Comisiones por pagar | Comisiones por pagar | Sin mapear | Sin mapear |
| 2.01.02.04 | Retenciones laborales a pagar | Retenciones laborales a pagar | Sin mapear | Sin mapear |
| 2.01.02.04.001 | Retencion IVSS por pagar | Retencion IVSS por pagar | Sin mapear | Sin mapear |
| 2.01.02.04.002 | Retención SPf por pagar | Retención SPf por pagar | Sin mapear | Sin mapear |
| 2.01.02.04.003 | Retención FAOV por pagar | Retención FAOV por pagar | Sin mapear | Sin mapear |
| 2.01.02.04.004 | Retención INCES por pagar | Retención INCES por pagar | Sin mapear | Sin mapear |
| 2.01.02.04.005 | Retención ARI por pagar | Retención ARI por pagar | Sin mapear | Sin mapear |
| 2.01.02.05 | Aportes patronales por pagar | Aportes patronales por pagar | Sin mapear | Sin mapear |
| 2.01.02.05.001 | Aporte IVSS por pagar | Aporte IVSS por pagar | Sin mapear | Sin mapear |
| 2.01.02.05.002 | Aporte SPF por pagar | Aporte SPF por pagar | Sin mapear | Sin mapear |
| 2.01.02.05.003 | Aporte FAOV por pagar | Aporte FAOV por pagar | Sin mapear | Sin mapear |
| 2.01.02.05.004 | Aporte INCES por pagar | Aporte INCES por pagar | Sin mapear | Sin mapear |
| 2.01.02.06 | Intereses por pagar | Intereses por pagar | Sin mapear | Sin mapear |
| 2.01.02.06.001 | Intereses bancarios por pagar | Intereses bancarios por pagar | Sin mapear | Sin mapear |
| 2.01.02.06.002 | Intereses sobre prestamos de terceros por pagar | Intereses sobre prestamos de terceros por pagar | Sin mapear | Sin mapear |
| 2.01.02.07 | Impuestos por pagar | Impuestos por pagar | Sin mapear | Sin mapear |
| 2.01.02.07.001 | IVA debito fiscal | IVA debito fiscal | Sin mapear | Sin mapear |
| 2.01.02.07.002 | IVA por pagar | IVA por pagar | Sin mapear | Sin mapear |
| 2.01.02.07.003 | Retenciones IVA a proveedores | Retenciones IVA a proveedores | Sin mapear | Sin mapear |
| 2.01.02.07.004 | Retenciones ISLR a proveedores | Retenciones ISLR a proveedores | Sin mapear | Sin mapear |
| 2.01.02.07.005 | Anticipo de ISLR por pagar | Anticipo de ISLR por pagar | Sin mapear | Sin mapear |
| 2.01.02.07.006 | ISLR Definitiva | ISLR Definitiva | Sin mapear | Sin mapear |
| 2.01.02.07.007 | Impuestos municipales por pagar | Impuestos municipales por pagar | Sin mapear | Sin mapear |
| 2.01.02.07.008 | IGTF por pagar | IGTF por pagar | Sin mapear | Sin mapear |
| 2.01.02.07.009 | IGTF percibido por pagar | IGTF percibido por pagar | Sin mapear | Sin mapear |
| 2.01.02.08 | Dividendos por pagar | Dividendos por pagar | Sin mapear | Sin mapear |
| 2.01.02.08.001 | Dividendos por pagar Camilo Gonzalez | Dividendos por pagar Camilo Gonzalez | Sin mapear | Sin mapear |
| 2.01.02.08.002 | Dividendos por pagar Jenny Castro | Dividendos por pagar Jenny Castro | Sin mapear | Sin mapear |
| 2.01.02.08.003 | Dividendos por pagar Alfonso Marquez | Dividendos por pagar Alfonso Marquez | Sin mapear | Sin mapear |
| 2.01.02.08.004 | Dividendos por pagar Leonardo Roa | Dividendos por pagar Leonardo Roa | Sin mapear | Sin mapear |
| 2.01.02.08.005 | Dividendos por pagar Gilberto Gonzalez Parra | Dividendos por pagar Gilberto Gonzalez Parra | Sin mapear | Sin mapear |
| 2.01.02.08.999 | Dividendos por pagar otros socios | Dividendos por pagar otros socios | Sin mapear | Sin mapear |
| 2.01.03 | Prestamos por pagar | Prestamos por pagar | Sin mapear | Sin mapear |
| 2.01.03.01 | Prestamos por pagar empresas relacionadas | Prestamos por pagar empresas relacionadas | Sin mapear | Sin mapear |
| 2.01.03.01.001 | Prestamos por pagar ULTRABIKEX | Prestamos por pagar ULTRABIKEX | Sin mapear | Sin mapear |
| 2.01.03.01.002 | Prestamos por pagar DIUX | Prestamos por pagar DIUX | Sin mapear | Sin mapear |
| 2.01.03.01.003 | Prestamos por pagar PLUSUX | Prestamos por pagar PLUSUX | Sin mapear | Sin mapear |
| 2.01.03.01.004 | Prestamos por pagar UX BARINAS | Prestamos por pagar UX BARINAS | Sin mapear | Sin mapear |
| 2.01.03.02 | Prestamos por pagar empresas externas del grupo | Prestamos por pagar empresas externas del grupo | Sin mapear | Sin mapear |
| 2.01.03.02.001 | Prestamos por pagar UX CARACAS | Prestamos por pagar UX CARACAS | Sin mapear | Sin mapear |
| 2.01.03.02.002 | Prestamos por pagar Ux PUERTO ORDAZ | Prestamos por pagar Ux PUERTO ORDAZ | Sin mapear | Sin mapear |
| 2.01.03.02.003 | Prestamos por pagar UX VALENCIA | Prestamos por pagar UX VALENCIA | Sin mapear | Sin mapear |
| 2.01.03.02.004 | Prestamos por pagar UX LARA | Prestamos por pagar UX LARA | Sin mapear | Sin mapear |
| 2.01.03.02.005 | Prestamos por pagar DRYFIELD | Prestamos por pagar DRYFIELD | Sin mapear | Sin mapear |
| 2.01.03.03 | Prestamos por pagar socios | Prestamos por pagar socios | Sin mapear | Sin mapear |
| 2.01.03.03.001 | Prestamos por pagar Camilo Gonzalez | Prestamos por pagar Camilo Gonzalez | Sin mapear | Sin mapear |
| 2.01.03.03.002 | Prestamos por pagar Jenny Castro | Prestamos por pagar Jenny Castro | Sin mapear | Sin mapear |
| 2.01.03.03.003 | Prestamos por pagar Alfonso Marquez | Prestamos por pagar Alfonso Marquez | Sin mapear | Sin mapear |
| 2.01.03.04 | Prestamos por pagar empleados | Prestamos por pagar empleados | Sin mapear | Sin mapear |
| 2.01.03.04.001 | Prestamos por pagar empleados | Prestamos por pagar empleados | Sin mapear | Sin mapear |
| 2.01.03.05 | Prestamos bancarios por pagar | Prestamos bancarios por pagar | Sin mapear | Sin mapear |
| 2.01.03.05.001 | Prestamo Banco Mercantil por pagar | Prestamo Banco Mercantil por pagar | Sin mapear | Sin mapear |
| 2.01.03.05.002 | Prestamo Banco Banesco por pagar | Prestamo Banco Banesco por pagar | Sin mapear | Sin mapear |
| 2.01.03.05.003 | Prestamo Banco de Venezuela por pagar | Prestamo Banco de Venezuela por pagar | Sin mapear | Sin mapear |
| 2.01.03.05.004 | Prestamo Banco Venezolano de Credito por pagar | Prestamo Banco Venezolano de Credito por pagar | Sin mapear | Sin mapear |
| 2.01.03.05.005 | Prestamo Banco del Tesoro por pagar | Prestamo Banco del Tesoro por pagar | Sin mapear | Sin mapear |
| 2.01.03.05.006 | Prestamo Bancamiga por pagar | Prestamo Bancamiga por pagar | Sin mapear | Sin mapear |
| 2.01.03.05.007 | Prestamo Bank Of America por pagar | Prestamo Bank Of America por pagar | Sin mapear | Sin mapear |
| 2.01.03.05.008 | Prestamo Banesco Panamá UX por pagar | Prestamo Banesco Panamá UX por pagar | Sin mapear | Sin mapear |
| 2.01.03.05.009 | Prestamo Chase Bank, UX GROUP LLC por pagar | Prestamo Chase Bank, UX GROUP LLC por pagar | Sin mapear | Sin mapear |
| 2.01.03.06 | Otros prestamos por pagar | Otros prestamos por pagar | Sin mapear | Sin mapear |
| 2.01.03.06.001 | Prestamos por pagar terceros | Prestamos por pagar terceros | Sin mapear | Sin mapear |
| 2.01.04 | Anticipos | Anticipos | Sin mapear | Sin mapear |
| 2.01.04.01 | Anticipos de clientes | Anticipos de clientes | Sin mapear | Sin mapear |
| 2.01.04.01.001 | Anticipos de clientes | Anticipos de clientes | Sin mapear | Sin mapear |
| 2.01.04.02 | Anticipos de socios | Anticipos de socios | Sin mapear | Sin mapear |
| 2.01.04.02.001 | Anticipos de Camilo Gonzalez | Anticipos de Camilo Gonzalez | Sin mapear | Sin mapear |
| 2.01.04.02.002 | Anticipos de Jenny Castro | Anticipos de Jenny Castro | Sin mapear | Sin mapear |
| 2.01.04.02.003 | Anticipos de Alfonso Marquez | Anticipos de Alfonso Marquez | Sin mapear | Sin mapear |
| 2.01.04.02.004 | Anticipos de Leonardo Roa | Anticipos de Leonardo Roa | Sin mapear | Sin mapear |
| 2.01.04.03 | Anticipos no reportados | Anticipos no reportados | Sin mapear | Sin mapear |
| 2.01.04.03.001 | Anticipos de clientes no reportados | Anticipos de clientes no reportados | Sin mapear | Sin mapear |
| 2.01.05 | Provisiones | Provisiones | Sin mapear | Sin mapear |
| 2.01.05.01 | Provisión para empleados | Provisión para empleados | Sin mapear | Sin mapear |
| 2.01.05.01.001 | Fondo de formación de empleados Plusux | Fondo de formación de empleados Plusux | Sin mapear | Sin mapear |
| 2.01.05.01.002 | Fondo para viajes de auditoria | Fondo para viajes de auditoria | Sin mapear | Sin mapear |
| 2.02 | Pasivo No Corriente | Pasivo No Corriente | Sin mapear | Sin mapear |
| 2.02.01 | Otras cuentas por pagar L.P. | Otras cuentas por pagar L.P. | Sin mapear | Sin mapear |
| 2.02.01.01 | Intereses por pagar L.P. | Intereses por pagar L.P. | Sin mapear | Sin mapear |
| 2.02.01.01.001 | Intereses bancarios por pagar L.P. | Intereses bancarios por pagar L.P. | Sin mapear | Sin mapear |
| 2.02.01.01.002 | Intereses sobre prestamos de terceros por pagar L.P. | Intereses sobre prestamos de terceros por pagar L.P. | Sin mapear | Sin mapear |
| 2.02.02 | Prestamos por pagar L.P. | Prestamos por pagar L.P. | Sin mapear | Sin mapear |
| 2.02.02.01 | Prestamos por pagar empresas relacionadas L.P. | Prestamos por pagar empresas relacionadas L.P. | Sin mapear | Sin mapear |
| 2.02.02.01.001 | Prestamos por pagar ULTRABIKEX L.P. | Prestamos por pagar ULTRABIKEX L.P. | Sin mapear | Sin mapear |
| 2.02.02.01.002 | Prestamos por pagar DIUX L.P. | Prestamos por pagar DIUX L.P. | Sin mapear | Sin mapear |
| 2.02.02.01.003 | Prestamos por pagar PLUSUX L.P. | Prestamos por pagar PLUSUX L.P. | Sin mapear | Sin mapear |
| 2.02.02.01.004 | Prestamos por pagar UX BARINAS L.P. | Prestamos por pagar UX BARINAS L.P. | Sin mapear | Sin mapear |
| 2.02.02.01.005 | Prestamos por pagar UBX L.P. | Prestamos por pagar UBX L.P. | Sin mapear | Sin mapear |
| 2.02.02.02 | Prestamos por pagar empresas externas del grupo L.P. | Prestamos por pagar empresas externas del grupo L.P. | Sin mapear | Sin mapear |
| 2.02.02.02.001 | Prestamos por pagar UX CARACAS L.P. | Prestamos por pagar UX CARACAS L.P. | Sin mapear | Sin mapear |
| 2.02.02.02.002 | Prestamos por pagar Ux PUERTO ORDAZ L.P. | Prestamos por pagar Ux PUERTO ORDAZ L.P. | Sin mapear | Sin mapear |
| 2.02.02.02.003 | Prestamos por pagar UX VALENCIA L.P. | Prestamos por pagar UX VALENCIA L.P. | Sin mapear | Sin mapear |
| 2.02.02.02.004 | Prestamos por pagar UX LARA L.P. | Prestamos por pagar UX LARA L.P. | Sin mapear | Sin mapear |
| 2.02.02.02.005 | Prestamos por pagar DRYFIELD L.P. | Prestamos por pagar DRYFIELD L.P. | Sin mapear | Sin mapear |
| 2.02.02.03 | Prestamos por pagar socios L.P. | Prestamos por pagar socios L.P. | Sin mapear | Sin mapear |
| 2.02.02.03.001 | Prestamos por pagar Camilo Gonzalez L.P. | Prestamos por pagar Camilo Gonzalez L.P. | Sin mapear | Sin mapear |
| 2.02.02.03.002 | Prestamos por pagar Jenny Castro L.P. | Prestamos por pagar Jenny Castro L.P. | Sin mapear | Sin mapear |
| 2.02.02.03.003 | Prestamos por pagar Alfonso Marquez L.P. | Prestamos por pagar Alfonso Marquez L.P. | Sin mapear | Sin mapear |
| 2.02.02.04 | Prestamos por pagar empleados L.P. | Prestamos por pagar empleados L.P. | Sin mapear | Sin mapear |
| 2.02.02.04.001 | Prestamos por pagar empleados L.P. | Prestamos por pagar empleados L.P. | Sin mapear | Sin mapear |
| 2.02.02.05 | Prestamos bancarios por pagar L.P. | Prestamos bancarios por pagar L.P. | Sin mapear | Sin mapear |
| 2.02.02.05.001 | Prestamo Banco Mercantil por pagar L.P | Prestamo Banco Mercantil por pagar L.P | Sin mapear | Sin mapear |
| 2.02.02.05.002 | Prestamo Banco Banesco por pagar L.P. | Prestamo Banco Banesco por pagar L.P. | Sin mapear | Sin mapear |
| 2.02.02.05.003 | Prestamo Banco de Venezuela por pagar L.P. | Prestamo Banco de Venezuela por pagar L.P. | Sin mapear | Sin mapear |
| 2.02.02.05.004 | Prestamo Banco Venezolano de Credito por pagar L.P. | Prestamo Banco Venezolano de Credito por pagar L.P. | Sin mapear | Sin mapear |
| 2.02.02.05.005 | Prestamo Banco del Tesoro por pagar L.P. | Prestamo Banco del Tesoro por pagar L.P. | Sin mapear | Sin mapear |
| 2.02.02.05.006 | Prestamo Bancamiga por pagar L.P. | Prestamo Bancamiga por pagar L.P. | Sin mapear | Sin mapear |
| 2.02.02.05.007 | Prestamo Bank Of America por pagar L.P. | Prestamo Bank Of America por pagar L.P. | Sin mapear | Sin mapear |
| 2.02.02.05.008 | Prestamo Banesco Panamá UX por pagar L.P. | Prestamo Banesco Panamá UX por pagar L.P. | Sin mapear | Sin mapear |
| 2.02.02.05.009 | Prestamo Chase Bank, UX GROUP LLC por pagar L.P. | Prestamo Chase Bank, UX GROUP LLC por pagar L.P. | Sin mapear | Sin mapear |
| 2.02.02.06 | Otros prestamos por pagar L.P. | Otros prestamos por pagar L.P. | Sin mapear | Sin mapear |
| 2.02.02.06.001 | Prestamos por pagar terceros L.P. | Prestamos por pagar terceros L.P. | Sin mapear | Sin mapear |
| 2.02.03 | Provisiones L.P. | Provisiones L.P. | Sin mapear | Sin mapear |
| 2.02.03.01 | Provisión para empleados L.P. | Provisión para empleados L.P. | Sin mapear | Sin mapear |
| 2.02.03.01.001 | Fondo de formación de empleados Plusux L.P. | Fondo de formación de empleados Plusux L.P. | Sin mapear | Sin mapear |
| 2.02.03.01.002 | Prestaciones Sociales L.P. | Prestaciones Sociales L.P. | Sin mapear | Sin mapear |
| 2.02.03.01.003 | Intereses sobres Prestaciones sociales L.P. | Intereses sobres Prestaciones sociales L.P. | Sin mapear | Sin mapear |
| 3.01 | Capital | Capital | Sin mapear | Sin mapear |
| 3.01.01 | Capital social | Capital social | Sin mapear | Sin mapear |
| 3.01.01.01 | Capital social suscrito | Capital social suscrito | Sin mapear | Sin mapear |
| 3.01.01.01.001 | Capital social suscrito y pagado | Capital social suscrito y pagado | Sin mapear | Sin mapear |
| 3.02 | Reservas | Reservas | Sin mapear | Sin mapear |
| 3.02.01 | Reservas legales y estatutarias | Reservas legales y estatutarias | Sin mapear | Sin mapear |
| 3.02.01.01 | Reserva legal | Reserva legal | Sin mapear | Sin mapear |
| 3.02.01.01.001 | Reserva legal | Reserva legal | Sin mapear | Sin mapear |
| 3.03 | Superavit | Superavit | Sin mapear | Sin mapear |
| 3.03.01 | Superavit por revaluacion | Superavit por revaluacion | Sin mapear | Sin mapear |
| 3.03.01.01 | Superavit por revaluacion de activos | Superavit por revaluacion de activos | Sin mapear | Sin mapear |
| 3.03.01.01.001 | Superavit por revaluacion de terrenos | Superavit por revaluacion de terrenos | Sin mapear | Sin mapear |
| 3.03.01.01.002 | Superavit por revaluacion de vehiculos | Superavit por revaluacion de vehiculos | Sin mapear | Sin mapear |
| 3.03.01.01.003 | Superavit por revaluacion de edificios | Superavit por revaluacion de edificios | Sin mapear | Sin mapear |
| 3.04 | Resultados | Resultados | Sin mapear | Sin mapear |
| 3.04.01 | Resultados acumulados | Resultados acumulados | Sin mapear | Sin mapear |
| 3.04.01.01 | Resultados acumulados | Resultados acumulados | Sin mapear | Sin mapear |
| 3.04.01.01.001 | Utilidad o perdida acumulada | Utilidad o perdida acumulada | Sin mapear | Sin mapear |
| 3.04.02 | Resultados del ejercicio | Resultados del ejercicio | Sin mapear | Sin mapear |
| 3.04.02.01 | Resultados del ejercicio | Resultados del ejercicio | Sin mapear | Sin mapear |
| 3.04.02.01.001 | Utilidad o perdida del ejercicio | Utilidad o perdida del ejercicio | Sin mapear | Sin mapear |
| 4.01 | Ingresos operativos | Ingresos operativos | Sin mapear | Sin mapear |
| 4.01.01 | Ingresos por venta de mercancias | Ingresos por venta de mercancias | Sin mapear | Sin mapear |
| 4.01.01.01 | Ingresos por venta de mercancias | Ingresos por venta de mercancias | Sin mapear | Sin mapear |
| 4.01.01.01.001 | Ingresos por venta de mercancias | Ingresos por venta de mercancias | Total Ingresos | Sin mapear |
| 4.01.01.01.001 | Ingresos por venta de mercancias | Ingresos por venta de mercancias | Subtotal Ingresos por Venta de Mercancia | Sin mapear |
| 4.01.01.01.001 | Ingresos por venta de mercancias | Ingresos por venta de mercancias | Ingresos por venta de mercancía | Sin mapear |
| 4.01.01.01.001 | Ingresos por venta de mercancias | Ingresos por venta de mercancias | Utilidad Bruta por Venta de Mercancia y Taller | Sin mapear |
| 4.01.01.01.001 | Ingresos por venta de mercancias | Ingresos por venta de mercancias | Utilidad Bruta | Sin mapear |
| 4.01.01.01.001 | Ingresos por venta de mercancias | Ingresos por venta de mercancias | Utilidad antes de Comisiones por Ventas | Sin mapear |
| 4.01.01.01.001 | Ingresos por venta de mercancias | Ingresos por venta de mercancias | Utilidad después de Comisiones por Ventas | Sin mapear |
| 4.01.01.01.001 | Ingresos por venta de mercancias | Ingresos por venta de mercancias | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 4.01.01.01.001 | Ingresos por venta de mercancias | Ingresos por venta de mercancias | Utilidad antes de Intereses e Impuestos (EBIT) | Sin mapear |
| 4.01.01.01.001 | Ingresos por venta de mercancias | Ingresos por venta de mercancias | Utilidad Neta | Sin mapear |
| 4.01.01.01.001 | Ingresos por venta de mercancias | Ingresos por venta de mercancias | Utilidad Neta despues de ISLR | Sin mapear |
| 4.01.01.02 | Devoluciones sobre ventas | Devoluciones sobre ventas | Sin mapear | Sin mapear |
| 4.01.01.02.001 | Devoluciones sobre ventas | Devoluciones sobre ventas | Total Ingresos | Sin mapear |
| 4.01.01.02.001 | Devoluciones sobre ventas | Devoluciones sobre ventas | Subtotal Ingresos por Venta de Mercancia | Sin mapear |
| 4.01.01.02.001 | Devoluciones sobre ventas | Devoluciones sobre ventas | Devoluciones sobre ventas | Sin mapear |
| 4.01.01.02.001 | Devoluciones sobre ventas | Devoluciones sobre ventas | Utilidad Bruta por Venta de Mercancia y Taller | Sin mapear |
| 4.01.01.02.001 | Devoluciones sobre ventas | Devoluciones sobre ventas | Utilidad Bruta | Sin mapear |
| 4.01.01.02.001 | Devoluciones sobre ventas | Devoluciones sobre ventas | Utilidad antes de Comisiones por Ventas | Sin mapear |
| 4.01.01.02.001 | Devoluciones sobre ventas | Devoluciones sobre ventas | Utilidad después de Comisiones por Ventas | Sin mapear |
| 4.01.01.02.001 | Devoluciones sobre ventas | Devoluciones sobre ventas | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 4.01.01.02.001 | Devoluciones sobre ventas | Devoluciones sobre ventas | Utilidad antes de Intereses e Impuestos (EBIT) | Sin mapear |
| 4.01.01.02.001 | Devoluciones sobre ventas | Devoluciones sobre ventas | Utilidad Neta | Sin mapear |
| 4.01.01.02.001 | Devoluciones sobre ventas | Devoluciones sobre ventas | Utilidad Neta despues de ISLR | Sin mapear |
| 4.01.01.03 | Descuentos sobre ventas | Descuentos sobre ventas | Sin mapear | Sin mapear |
| 4.01.01.03.001 | Descuentos sobre ventas | Descuentos sobre ventas | Total Ingresos | Sin mapear |
| 4.01.01.03.001 | Descuentos sobre ventas | Descuentos sobre ventas | Subtotal Ingresos por Venta de Mercancia | Sin mapear |
| 4.01.01.03.001 | Descuentos sobre ventas | Descuentos sobre ventas | Descuentos sobre ventas | Sin mapear |
| 4.01.01.03.001 | Descuentos sobre ventas | Descuentos sobre ventas | Utilidad Bruta por Venta de Mercancia y Taller | Sin mapear |
| 4.01.01.03.001 | Descuentos sobre ventas | Descuentos sobre ventas | Utilidad Bruta | Sin mapear |
| 4.01.01.03.001 | Descuentos sobre ventas | Descuentos sobre ventas | Utilidad antes de Comisiones por Ventas | Sin mapear |
| 4.01.01.03.001 | Descuentos sobre ventas | Descuentos sobre ventas | Utilidad después de Comisiones por Ventas | Sin mapear |
| 4.01.01.03.001 | Descuentos sobre ventas | Descuentos sobre ventas | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 4.01.01.03.001 | Descuentos sobre ventas | Descuentos sobre ventas | Utilidad antes de Intereses e Impuestos (EBIT) | Sin mapear |
| 4.01.01.03.001 | Descuentos sobre ventas | Descuentos sobre ventas | Utilidad Neta | Sin mapear |
| 4.01.01.03.001 | Descuentos sobre ventas | Descuentos sobre ventas | Utilidad Neta despues de ISLR | Sin mapear |
| 4.01.01.03.002 | Descuentos sobre ventas plan de fidelización | Descuentos sobre ventas plan de fidelización | Sin mapear | Sin mapear |
| 4.01.02 | Ingresos por servicios | Ingresos por servicios | Sin mapear | Sin mapear |
| 4.01.02.01 | Ingresos por servicios | Ingresos por servicios | Sin mapear | Sin mapear |
| 4.01.02.01.001 | Ingresos por servicios del café | Ingresos por servicios del café | Total Ingresos | Sin mapear |
| 4.01.02.01.001 | Ingresos por servicios del café | Ingresos por servicios del café | Subtotal Ingresos por Servicios | Sin mapear |
| 4.01.02.01.001 | Ingresos por servicios del café | Ingresos por servicios del café | Ingresos por servicios del café | Sin mapear |
| 4.01.02.01.001 | Ingresos por servicios del café | Ingresos por servicios del café | Utilidad Bruta por Servicios | Sin mapear |
| 4.01.02.01.001 | Ingresos por servicios del café | Ingresos por servicios del café | Utilidad Bruta | Sin mapear |
| 4.01.02.01.001 | Ingresos por servicios del café | Ingresos por servicios del café | Utilidad antes de Comisiones por Ventas | Sin mapear |
| 4.01.02.01.001 | Ingresos por servicios del café | Ingresos por servicios del café | Utilidad después de Comisiones por Ventas | Sin mapear |
| 4.01.02.01.001 | Ingresos por servicios del café | Ingresos por servicios del café | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 4.01.02.01.001 | Ingresos por servicios del café | Ingresos por servicios del café | Utilidad antes de Intereses e Impuestos (EBIT) | Sin mapear |
| 4.01.02.01.001 | Ingresos por servicios del café | Ingresos por servicios del café | Utilidad Neta | Sin mapear |
| 4.01.02.01.001 | Ingresos por servicios del café | Ingresos por servicios del café | Utilidad Neta despues de ISLR | Sin mapear |
| 4.01.02.01.002 | Ingresos por servicios zona FIT | Ingresos por servicios zona FIT | Ingresos por zona FIT | Sin mapear |
| 4.01.02.01.003 | Ingresos por servicios de fletes | Ingresos por servicios de fletes | Ingresos por fletes | Sin mapear |
| 4.01.02.01.004 | Ingresos por otros servicios | Ingresos por otros servicios | Sin mapear | Sin mapear |
| 4.01.03 | Ingresos por eventos | Ingresos por eventos | Sin mapear | Sin mapear |
| 4.01.03.01 | Ingresos por eventos | Ingresos por eventos | Sin mapear | Sin mapear |
| 4.01.03.01.001 | Ingresos por eventos | Ingresos por eventos | Total Ingresos | Sin mapear |
| 4.01.03.01.001 | Ingresos por eventos | Ingresos por eventos | Subtotal Ingresos por Eventos | Sin mapear |
| 4.01.03.01.001 | Ingresos por eventos | Ingresos por eventos | Ingresos por eventos | Sin mapear |
| 4.01.03.01.001 | Ingresos por eventos | Ingresos por eventos | Utilidad Bruta por Eventos | Sin mapear |
| 4.01.03.01.001 | Ingresos por eventos | Ingresos por eventos | Utilidad Bruta | Sin mapear |
| 4.01.03.01.001 | Ingresos por eventos | Ingresos por eventos | Utilidad antes de Comisiones por Ventas | Sin mapear |
| 4.01.03.01.001 | Ingresos por eventos | Ingresos por eventos | Utilidad después de Comisiones por Ventas | Sin mapear |
| 4.01.03.01.001 | Ingresos por eventos | Ingresos por eventos | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 4.01.03.01.001 | Ingresos por eventos | Ingresos por eventos | Utilidad antes de Intereses e Impuestos (EBIT) | Sin mapear |
| 4.01.03.01.001 | Ingresos por eventos | Ingresos por eventos | Utilidad Neta | Sin mapear |
| 4.01.03.01.001 | Ingresos por eventos | Ingresos por eventos | Utilidad Neta despues de ISLR | Sin mapear |
| 4.01.04 | Ingresos por Taller | Ingresos por Taller | Sin mapear | Sin mapear |
| 4.01.04.01 | Ingresos por Taller | Ingresos por Taller | Sin mapear | Sin mapear |
| 4.01.04.01.001 | Ingresos por Taller | Ingresos por Taller | Total Ingresos | Sin mapear |
| 4.01.04.01.001 | Ingresos por Taller | Ingresos por Taller | Subtotal Ingresos por Taller | Sin mapear |
| 4.01.04.01.001 | Ingresos por Taller | Ingresos por Taller | Ingresos por taller | Sin mapear |
| 4.01.04.01.001 | Ingresos por Taller | Ingresos por Taller | Utilidad Bruta por Venta de Mercancia y Taller | Sin mapear |
| 4.01.04.01.001 | Ingresos por Taller | Ingresos por Taller | Utilidad Bruta | Sin mapear |
| 4.01.04.01.001 | Ingresos por Taller | Ingresos por Taller | Utilidad antes de Comisiones por Ventas | Sin mapear |
| 4.01.04.01.001 | Ingresos por Taller | Ingresos por Taller | Utilidad después de Comisiones por Ventas | Sin mapear |
| 4.01.04.01.001 | Ingresos por Taller | Ingresos por Taller | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 4.01.04.01.001 | Ingresos por Taller | Ingresos por Taller | Utilidad antes de Intereses e Impuestos (EBIT) | Sin mapear |
| 4.01.04.01.001 | Ingresos por Taller | Ingresos por Taller | Utilidad Neta | Sin mapear |
| 4.01.04.01.001 | Ingresos por Taller | Ingresos por Taller | Utilidad Neta despues de ISLR | Sin mapear |
| 4.02 | Ingresos no operativos | Ingresos no operativos | Sin mapear | Sin mapear |
| 4.02.01 | Otros Ingresos | Otros Ingresos | Sin mapear | Sin mapear |
| 4.02.01.01 | Otros Ingresos | Otros Ingresos | Sin mapear | Sin mapear |
| 4.02.01.01.001 | Ingresos por alquileres | Ingresos por alquileres | Otros Ingresos no Operacionales | Sin mapear |
| 4.02.01.01.001 | Ingresos por alquileres | Ingresos por alquileres | Ingresos por alquileres | Sin mapear |
| 4.02.01.01.001 | Ingresos por alquileres | Ingresos por alquileres | Utilidad Neta | Sin mapear |
| 4.02.01.01.001 | Ingresos por alquileres | Ingresos por alquileres | Utilidad Neta despues de ISLR | Sin mapear |
| 4.02.01.01.002 | Ingresos por intereses | Ingresos por intereses | Ingresos por intereses | Sin mapear |
| 4.02.01.01.003 | Ingresos por comisiones | Ingresos por comisiones | Ingresos por comisiones | Sin mapear |
| 4.02.01.01.004 | Ingresos por servicios administrativos | Ingresos por servicios administrativos | Ingresos por servicios administrativos | Sin mapear |
| 4.02.01.01.005 | Sobrante en ventas | Sobrante en ventas | Sobrante en ventas | Sin mapear |
| 4.02.01.01.006 | Sobrante de inventarios | Sobrante de inventarios | Sobrante de inventarios | Sin mapear |
| 4.02.01.01.007 | Ganancia en venta de activos | Ganancia en venta de activos | Ganancia en venta de activos | Sin mapear |
| 4.02.01.01.008 | Ganancia por tasa cambiaria | Ganancia por tasa cambiaria | Ganancia por tasa cambiaria | Sin mapear |
| 4.02.01.01.009 | Ganancia por diferencias en pagos | Ganancia por diferencias en pagos | Ganancia por diferencias en pagos | Sin mapear |
| 5.01 | Costos de venta | Costos de venta | Sin mapear | Sin mapear |
| 5.01.01 | Costos de venta por mercancia | Costos de venta por mercancia | Sin mapear | Sin mapear |
| 5.01.01.01 | Costos de venta por mercancia | Costos de venta por mercancia | Sin mapear | Sin mapear |
| 5.01.01.01.001 | Costos de venta por mercancia | Costos de venta por mercancia | Total Costo de Ventas | Sin mapear |
| 5.01.01.01.001 | Costos de venta por mercancia | Costos de venta por mercancia | Subtotal Costo de Ventas por Mercancia | Sin mapear |
| 5.01.01.01.001 | Costos de venta por mercancia | Costos de venta por mercancia | Costo de venta por mercancía | Sin mapear |
| 5.01.01.01.001 | Costos de venta por mercancia | Costos de venta por mercancia | Utilidad Bruta por Venta de Mercancia y Taller | Sin mapear |
| 5.01.01.01.001 | Costos de venta por mercancia | Costos de venta por mercancia | Utilidad Bruta | Sin mapear |
| 5.01.01.01.001 | Costos de venta por mercancia | Costos de venta por mercancia | Utilidad antes de Comisiones por Ventas | Sin mapear |
| 5.01.01.01.001 | Costos de venta por mercancia | Costos de venta por mercancia | Utilidad después de Comisiones por Ventas | Sin mapear |
| 5.01.01.01.001 | Costos de venta por mercancia | Costos de venta por mercancia | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 5.01.01.01.001 | Costos de venta por mercancia | Costos de venta por mercancia | Utilidad antes de Intereses e Impuestos (EBIT) | Sin mapear |
| 5.01.01.01.001 | Costos de venta por mercancia | Costos de venta por mercancia | Utilidad Neta | Sin mapear |
| 5.01.01.01.001 | Costos de venta por mercancia | Costos de venta por mercancia | Utilidad Neta despues de ISLR | Sin mapear |
| 5.01.02 | Costos de venta por servicios | Costos de venta por servicios | Sin mapear | Sin mapear |
| 5.01.02.01 | Costos de venta por servicios | Costos de venta por servicios | Sin mapear | Sin mapear |
| 5.01.02.01.001 | Costos de venta por servicios del café | Costos de venta por servicios del café | Total Costo de Ventas | Sin mapear |
| 5.01.02.01.001 | Costos de venta por servicios del café | Costos de venta por servicios del café | Subtotal Costo de Ventas por Servicios | Sin mapear |
| 5.01.02.01.001 | Costos de venta por servicios del café | Costos de venta por servicios del café | Costo de venta por servicio del café | Sin mapear |
| 5.01.02.01.001 | Costos de venta por servicios del café | Costos de venta por servicios del café | Utilidad Bruta por Servicios | Sin mapear |
| 5.01.02.01.001 | Costos de venta por servicios del café | Costos de venta por servicios del café | Utilidad Bruta | Sin mapear |
| 5.01.02.01.001 | Costos de venta por servicios del café | Costos de venta por servicios del café | Utilidad antes de Comisiones por Ventas | Sin mapear |
| 5.01.02.01.001 | Costos de venta por servicios del café | Costos de venta por servicios del café | Utilidad después de Comisiones por Ventas | Sin mapear |
| 5.01.02.01.001 | Costos de venta por servicios del café | Costos de venta por servicios del café | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 5.01.02.01.001 | Costos de venta por servicios del café | Costos de venta por servicios del café | Utilidad antes de Intereses e Impuestos (EBIT) | Sin mapear |
| 5.01.02.01.001 | Costos de venta por servicios del café | Costos de venta por servicios del café | Utilidad Neta | Sin mapear |
| 5.01.02.01.001 | Costos de venta por servicios del café | Costos de venta por servicios del café | Utilidad Neta despues de ISLR | Sin mapear |
| 5.01.03 | Costos de venta por eventos | Costos de venta por eventos | Sin mapear | Sin mapear |
| 5.01.03.01 | Costos de venta por eventos | Costos de venta por eventos | Sin mapear | Sin mapear |
| 5.01.03.01.001 | Costos de venta por eventos | Costos de venta por eventos | Total Costo de Ventas | Sin mapear |
| 5.01.03.01.001 | Costos de venta por eventos | Costos de venta por eventos | Subtotal Costo de Ventas por Eventos | Sin mapear |
| 5.01.03.01.001 | Costos de venta por eventos | Costos de venta por eventos | Costo de ventas por eventos | Sin mapear |
| 5.01.03.01.001 | Costos de venta por eventos | Costos de venta por eventos | Utilidad Bruta por Eventos | Sin mapear |
| 5.01.03.01.001 | Costos de venta por eventos | Costos de venta por eventos | Utilidad Bruta | Sin mapear |
| 5.01.03.01.001 | Costos de venta por eventos | Costos de venta por eventos | Utilidad antes de Comisiones por Ventas | Sin mapear |
| 5.01.03.01.001 | Costos de venta por eventos | Costos de venta por eventos | Utilidad después de Comisiones por Ventas | Sin mapear |
| 5.01.03.01.001 | Costos de venta por eventos | Costos de venta por eventos | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 5.01.03.01.001 | Costos de venta por eventos | Costos de venta por eventos | Utilidad antes de Intereses e Impuestos (EBIT) | Sin mapear |
| 5.01.03.01.001 | Costos de venta por eventos | Costos de venta por eventos | Utilidad Neta | Sin mapear |
| 5.01.03.01.001 | Costos de venta por eventos | Costos de venta por eventos | Utilidad Neta despues de ISLR | Sin mapear |
| 6.01 | Gastos operativos | Gastos operativos | Sin mapear | Sin mapear |
| 6.01.01 | Gastos de administración | Gastos de administración | Sin mapear | Sin mapear |
| 6.01.01.01 | Gastos de administración | Gastos de administración | Sin mapear | Sin mapear |
| 6.01.01.01.001 | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | Total Gastos Operacionales | Sin mapear |
| 6.01.01.01.001 | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | Subtotal Gastos de Administración | Sin mapear |
| 6.01.01.01.001 | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | Sin mapear |
| 6.01.01.01.001 | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | Utilidad antes de Comisiones por Ventas | Sin mapear |
| 6.01.01.01.001 | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | Utilidad después de Comisiones por Ventas | Sin mapear |
| 6.01.01.01.001 | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 6.01.01.01.001 | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | Utilidad antes de Intereses e Impuestos (EBIT) | Sin mapear |
| 6.01.01.01.001 | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | Total Gastos Operacionales y No Operacionales | Sin mapear |
| 6.01.01.01.001 | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | Utilidad Neta | Sin mapear |
| 6.01.01.01.001 | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | ISLR | Sin mapear |
| 6.01.01.01.001 | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | Gastos de servicios públicos (Agua, luz, Aseo Urbano) | Utilidad Neta despues de ISLR | Sin mapear |
| 6.01.01.01.002 | Gastos de servicios de telefonía e internet | Gastos de servicios de telefonía e internet | Gastos de servicios de telefonía e internet | Sin mapear |
| 6.01.01.01.003 | Gastos de alquiler del local | Gastos de alquiler del local | Gastos de alquiler del local | Sin mapear |
| 6.01.01.01.004 | Gastos de Condominio | Gastos de Condominio | Gastos de Condominio | Sin mapear |
| 6.01.01.01.005 | Gastos de asistencia outsorcing | Gastos de asistencia outsorcing | Gastos de asistencia outsorsing | Sin mapear |
| 6.01.01.01.006 | Gastos de alquiler de bienes muebles | Gastos de alquiler de bienes muebles | Gastos de alquiler de bienes muebles | Sin mapear |
| 6.01.01.01.007 | Gastos de artículos de oficina | Gastos de artículos de oficina | Gastos de artículos de oficina | Sin mapear |
| 6.01.01.01.008 | Gastos de artículos de limpieza e higiene | Gastos de artículos de limpieza e higiene | Gastos de artículos de limpieza e higiene | Sin mapear |
| 6.01.01.01.009 | Gastos de alimentos y bebidas | Gastos de alimentos y bebidas | Gastos de alimentos y bebidas | Sin mapear |
| 6.01.01.01.010 | Gastos de envíos y encomiendas administrativas | Gastos de envíos y encomiendas administrativas | Gastos de envíos y encomiendas administrativas | Sin mapear |
| 6.01.01.01.011 | Gastos de honorarios profesionales | Gastos de honorarios profesionales | Gastos de honorarios profesionales | Sin mapear |
| 6.01.01.01.012 | Gastos de estacionamiento | Gastos de estacionamiento | Gastos de estacionamiento | Sin mapear |
| 6.01.01.01.013 | Gastos de gestoría | Gastos de gestoría | Gastos de gestoría | Sin mapear |
| 6.01.01.01.014 | Gastos legales | Gastos legales | Gastos legales | Sin mapear |
| 6.01.01.01.015 | Gastos de taxi, transporte y/o delivery | Gastos de taxi, transporte y/o delivery | Gastos de taxi, transporte y/o delivery | Sin mapear |
| 6.01.01.01.016 | Gastos de suministros para taller | Gastos de suministros para taller | Gastos de suministros para taller | Sin mapear |
| 6.01.01.01.017 | Gastos de suministros del café | Gastos de suministros del café | Gastos de suministros del café | Sin mapear |
| 6.01.01.01.018 | Gastos por fiestas, festejos y/o reuniones | Gastos por fiestas, festejos y/o reuniones | Gastos por fiestas, festejos y/o reuniones | Sin mapear |
| 6.01.01.01.019 | Gastos de vigilancia | Gastos de vigilancia | Gastos de vigilancia | Sin mapear |
| 6.01.01.01.999 | Gastos de retenciones no descontadas | Gastos de retenciones no descontadas | Gastos de retenciones no descontadas | Sin mapear |
| 6.01.01.02 | Gastos de mantenimiento y reparacion | Gastos de mantenimiento y reparacion | Sin mapear | Sin mapear |
| 6.01.01.02.001 | Gastos de mantenimiento y reparación de mobiliario y equipo | Gastos de mantenimiento y reparación de mobiliario y equipo | Mantenimiento y reparaciones | Mantenimiento y reparaciones |
| 6.01.01.02.002 | Gastos de mantenimiento y reparación de vehiculo | Gastos de mantenimiento y reparación de vehiculo | Mantenimiento y reparaciones | Mantenimiento y reparaciones |
| 6.01.01.02.003 | Gastos de mantenimiento y reparación de edificaciones | Gastos de mantenimiento y reparación de edificaciones | Mantenimiento y reparaciones | Mantenimiento y reparaciones |
| 6.01.01.02.004 | Gastos de mantenimiento y reparación a la propiedad alq. | Gastos de mantenimiento y reparación a la propiedad alq. | Mantenimiento y reparaciones | Mantenimiento y reparaciones |
| 6.01.01.02.005 | Gastos de mantenimiento y reparación de maquinaria y equipos | Gastos de mantenimiento y reparación de maquinaria y equipos | Mantenimiento y reparaciones | Mantenimiento y reparaciones |
| 6.01.01.03 | Gastos de viáticos administrativos | Gastos de viáticos administrativos | Sin mapear | Sin mapear |
| 6.01.01.03.001 | Gastos de pasajes por viáticos administrativos | Gastos de pasajes por viáticos administrativos | Viáticos administrativos | Viáticos administrativos |
| 6.01.01.03.002 | Gastos de comida por viáticos administrativos | Gastos de comida por viáticos administrativos | Viáticos administrativos | Viáticos administrativos |
| 6.01.01.03.003 | Gastos de hospedaje por viáticos administrativos | Gastos de hospedaje por viáticos administrativos | Viáticos administrativos | Viáticos administrativos |
| 6.01.01.03.004 | Gastos de transporte por viáticos administrativos | Gastos de transporte por viáticos administrativos | Viáticos administrativos | Viáticos administrativos |
| 6.01.01.03.005 | Otros gastos de viáticos administrativos | Otros gastos de viáticos administrativos | Viáticos administrativos | Viáticos administrativos |
| 6.01.01.04 | Gastos de seguro | Gastos de seguro | Gastos de seguro | Sin mapear |
| 6.01.01.04.001 | Gastos de seguro de edificaciones | Gastos de seguro de edificaciones | Sin mapear | Gastos de seguro |
| 6.01.01.04.002 | Gastos de seguro de vehiculos | Gastos de seguro de vehiculos | Sin mapear | Gastos de seguro |
| 6.01.01.05 | Gastos de impuestos, tasas y contribuciones | Gastos de impuestos, tasas y contribuciones | Gastos de impuestos, tasas y contribuciones | Sin mapear |
| 6.01.01.05 | Gastos de impuestos, tasas y contribuciones | Gastos de impuestos, tasas y contribuciones | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 6.01.01.05 | Gastos de impuestos, tasas y contribuciones | Gastos de impuestos, tasas y contribuciones | Utilidad antes de Intereses e Impuestos (EBIT) | Sin mapear |
| 6.01.01.05.001 | Gastos de patente vehicular | Gastos de patente vehicular | Sin mapear | Gastos de impuestos, tasas y contribuciones |
| 6.01.01.05.002 | Gastos de tasas de notaria y registro | Gastos de tasas de notaria y registro | Sin mapear | Gastos de impuestos, tasas y contribuciones |
| 6.01.01.05.003 | Gastos de impuesto por licencia de actividades economicas | Gastos de impuesto por licencia de actividades economicas | Sin mapear | Gastos de impuestos, tasas y contribuciones |
| 6.01.01.05.004 | Gastos de impuesto por publicidad | Gastos de impuesto por publicidad | Sin mapear | Gastos de impuestos, tasas y contribuciones |
| 6.01.01.05.005 | Gastos de tasa sencamer | Gastos de tasa sencamer | Sin mapear | Gastos de impuestos, tasas y contribuciones |
| 6.01.01.05.007 | Gasto por impuesto a las pensiones | Gasto por impuesto a las pensiones | Sin mapear | Gastos de impuestos, tasas y contribuciones |
| 6.01.01.05.999 | Gasto por otras tasas | Gasto por otras tasas | Sin mapear | Sin mapear |
| 6.01.01.06 | Gastos de depreciación | Gastos de depreciación | Sin mapear | Sin mapear |
| 6.01.01.06.001 | Gastos de depreciación de mobiliario y equipo | Gastos de depreciación de mobiliario y equipo | Depreciaciones, deterioro y Amortización | Depreciaciones, deterioro y Amortización |
| 6.01.01.06.001 | Gastos de depreciación de mobiliario y equipo | Gastos de depreciación de mobiliario y equipo | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Depreciaciones, deterioro y Amortización |
| 6.01.01.06.002 | Gastos de depreciación de vehículos | Gastos de depreciación de vehículos | Depreciaciones, deterioro y Amortización | Depreciaciones, deterioro y Amortización |
| 6.01.01.06.002 | Gastos de depreciación de vehículos | Gastos de depreciación de vehículos | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Depreciaciones, deterioro y Amortización |
| 6.01.01.06.003 | Gastos de depreciación de edificaciones | Gastos de depreciación de edificaciones | Depreciaciones, deterioro y Amortización | Depreciaciones, deterioro y Amortización |
| 6.01.01.06.003 | Gastos de depreciación de edificaciones | Gastos de depreciación de edificaciones | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Depreciaciones, deterioro y Amortización |
| 6.01.01.06.004 | Gastos de depreciación de maquinarias y equipos | Gastos de depreciación de maquinarias y equipos | Depreciaciones, deterioro y Amortización | Depreciaciones, deterioro y Amortización |
| 6.01.01.06.004 | Gastos de depreciación de maquinarias y equipos | Gastos de depreciación de maquinarias y equipos | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Depreciaciones, deterioro y Amortización |
| 6.01.01.07 | Gastos de deterioro | Gastos de deterioro | Sin mapear | Sin mapear |
| 6.01.01.07.001 | Gastos de deterioro de mobiliario y equipo | Gastos de deterioro de mobiliario y equipo | Depreciaciones, deterioro y Amortización | Depreciaciones, deterioro y Amortización |
| 6.01.01.07.001 | Gastos de deterioro de mobiliario y equipo | Gastos de deterioro de mobiliario y equipo | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Depreciaciones, deterioro y Amortización |
| 6.01.01.07.002 | Gastos de deterioro de vehículos | Gastos de deterioro de vehículos | Depreciaciones, deterioro y Amortización | Depreciaciones, deterioro y Amortización |
| 6.01.01.07.002 | Gastos de deterioro de vehículos | Gastos de deterioro de vehículos | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Depreciaciones, deterioro y Amortización |
| 6.01.01.07.003 | Gastos de deterioro de edificaciones | Gastos de deterioro de edificaciones | Depreciaciones, deterioro y Amortización | Depreciaciones, deterioro y Amortización |
| 6.01.01.07.003 | Gastos de deterioro de edificaciones | Gastos de deterioro de edificaciones | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Depreciaciones, deterioro y Amortización |
| 6.01.01.07.004 | Gastos de deterioro de maquinarias y equipos | Gastos de deterioro de maquinarias y equipos | Depreciaciones, deterioro y Amortización | Depreciaciones, deterioro y Amortización |
| 6.01.01.07.004 | Gastos de deterioro de maquinarias y equipos | Gastos de deterioro de maquinarias y equipos | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Depreciaciones, deterioro y Amortización |
| 6.01.01.07.999 | Gastos de deterioro por cuentas incobrables | Gastos de deterioro por cuentas incobrables | Depreciaciones, deterioro y Amortización | Sin mapear |
| 6.01.01.07.999 | Gastos de deterioro por cuentas incobrables | Gastos de deterioro por cuentas incobrables | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 6.01.01.08 | Gastos de amortización | Gastos de amortización | Sin mapear | Sin mapear |
| 6.01.01.08.001 | Gastos de amortización de software | Gastos de amortización de software | Depreciaciones, deterioro y Amortización | Depreciaciones, deterioro y Amortización |
| 6.01.01.08.001 | Gastos de amortización de software | Gastos de amortización de software | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Depreciaciones, deterioro y Amortización |
| 6.01.01.09 | Gastos bancarios | Gastos bancarios | Gastos Bancarios | Sin mapear |
| 6.01.01.09.001 | Gastos de comisiones bancarias | Gastos de comisiones bancarias | Sin mapear | Gastos Bancarios |
| 6.01.01.09.002 | Gastos de IGTF | Gastos de IGTF | Sin mapear | Gastos Bancarios |
| 6.01.01.09.003 | Gastos de intereses de mora | Gastos de intereses de mora | Sin mapear | Sin mapear |
| 6.01.01.10 | Gastos de intereses sobre préstamos | Gastos de intereses sobre préstamos | Gastos de intereses sobre préstamos | Sin mapear |
| 6.01.01.10 | Gastos de intereses sobre préstamos | Gastos de intereses sobre préstamos | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 6.01.01.10 | Gastos de intereses sobre préstamos | Gastos de intereses sobre préstamos | Utilidad antes de Intereses e Impuestos (EBIT) | Sin mapear |
| 6.01.01.10.001 | Gastos de intereses sobre préstamos de terceros | Gastos de intereses sobre préstamos de terceros | Sin mapear | Gastos de intereses sobre préstamos |
| 6.01.01.10.002 | Gastos de intereses sobre préstamos bancarios | Gastos de intereses sobre préstamos bancarios | Sin mapear | Gastos de intereses sobre préstamos |
| 6.01.02 | Gastos de recursos humanos | Gastos de recursos humanos | Sin mapear | Sin mapear |
| 6.01.02.01 | Gastos de sueldos y salarios | Gastos de sueldos y salarios | Sin mapear | Sin mapear |
| 6.01.02.01.001 | Gastos de sueldos y salarios empleados | Gastos de sueldos y salarios empleados | Total Gastos Operacionales | Sin mapear |
| 6.01.02.01.001 | Gastos de sueldos y salarios empleados | Gastos de sueldos y salarios empleados | Subtotal Gastos de Recursos Humanos | Sin mapear |
| 6.01.02.01.001 | Gastos de sueldos y salarios empleados | Gastos de sueldos y salarios empleados | Gastos de sueldos y salarios empleados y directivos | Sin mapear |
| 6.01.02.01.001 | Gastos de sueldos y salarios empleados | Gastos de sueldos y salarios empleados | Utilidad antes de Comisiones por Ventas | Sin mapear |
| 6.01.02.01.001 | Gastos de sueldos y salarios empleados | Gastos de sueldos y salarios empleados | Utilidad después de Comisiones por Ventas | Sin mapear |
| 6.01.02.01.001 | Gastos de sueldos y salarios empleados | Gastos de sueldos y salarios empleados | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 6.01.02.01.001 | Gastos de sueldos y salarios empleados | Gastos de sueldos y salarios empleados | Utilidad antes de Intereses e Impuestos (EBIT) | Sin mapear |
| 6.01.02.01.001 | Gastos de sueldos y salarios empleados | Gastos de sueldos y salarios empleados | Total Gastos Operacionales y No Operacionales | Sin mapear |
| 6.01.02.01.001 | Gastos de sueldos y salarios empleados | Gastos de sueldos y salarios empleados | Utilidad Neta | Sin mapear |
| 6.01.02.01.001 | Gastos de sueldos y salarios empleados | Gastos de sueldos y salarios empleados | ISLR | Sin mapear |
| 6.01.02.01.001 | Gastos de sueldos y salarios empleados | Gastos de sueldos y salarios empleados | Utilidad Neta despues de ISLR | Sin mapear |
| 6.01.02.01.002 | Gastos de sueldos y salarios directivos | Gastos de sueldos y salarios directivos | Total Gastos Operacionales | Sin mapear |
| 6.01.02.01.002 | Gastos de sueldos y salarios directivos | Gastos de sueldos y salarios directivos | Subtotal Gastos de Recursos Humanos | Sin mapear |
| 6.01.02.01.002 | Gastos de sueldos y salarios directivos | Gastos de sueldos y salarios directivos | Gastos de sueldos y salarios empleados y directivos | Sin mapear |
| 6.01.02.01.002 | Gastos de sueldos y salarios directivos | Gastos de sueldos y salarios directivos | Utilidad antes de Comisiones por Ventas | Sin mapear |
| 6.01.02.01.002 | Gastos de sueldos y salarios directivos | Gastos de sueldos y salarios directivos | Utilidad después de Comisiones por Ventas | Sin mapear |
| 6.01.02.01.002 | Gastos de sueldos y salarios directivos | Gastos de sueldos y salarios directivos | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 6.01.02.01.002 | Gastos de sueldos y salarios directivos | Gastos de sueldos y salarios directivos | Utilidad antes de Intereses e Impuestos (EBIT) | Sin mapear |
| 6.01.02.01.002 | Gastos de sueldos y salarios directivos | Gastos de sueldos y salarios directivos | Total Gastos Operacionales y No Operacionales | Sin mapear |
| 6.01.02.01.002 | Gastos de sueldos y salarios directivos | Gastos de sueldos y salarios directivos | Utilidad Neta | Sin mapear |
| 6.01.02.01.002 | Gastos de sueldos y salarios directivos | Gastos de sueldos y salarios directivos | ISLR | Sin mapear |
| 6.01.02.01.002 | Gastos de sueldos y salarios directivos | Gastos de sueldos y salarios directivos | Utilidad Neta despues de ISLR | Sin mapear |
| 6.01.02.01.003 | Gastos de horas extras, feriados y bono nocturno | Gastos de horas extras, feriados y bono nocturno | Total Gastos Operacionales | Sin mapear |
| 6.01.02.01.003 | Gastos de horas extras, feriados y bono nocturno | Gastos de horas extras, feriados y bono nocturno | Subtotal Gastos de Recursos Humanos | Sin mapear |
| 6.01.02.01.003 | Gastos de horas extras, feriados y bono nocturno | Gastos de horas extras, feriados y bono nocturno | Gastos de sueldos y salarios empleados y directivos | Sin mapear |
| 6.01.02.01.003 | Gastos de horas extras, feriados y bono nocturno | Gastos de horas extras, feriados y bono nocturno | Utilidad antes de Comisiones por Ventas | Sin mapear |
| 6.01.02.01.003 | Gastos de horas extras, feriados y bono nocturno | Gastos de horas extras, feriados y bono nocturno | Utilidad después de Comisiones por Ventas | Sin mapear |
| 6.01.02.01.003 | Gastos de horas extras, feriados y bono nocturno | Gastos de horas extras, feriados y bono nocturno | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 6.01.02.01.003 | Gastos de horas extras, feriados y bono nocturno | Gastos de horas extras, feriados y bono nocturno | Utilidad antes de Intereses e Impuestos (EBIT) | Sin mapear |
| 6.01.02.01.003 | Gastos de horas extras, feriados y bono nocturno | Gastos de horas extras, feriados y bono nocturno | Total Gastos Operacionales y No Operacionales | Sin mapear |
| 6.01.02.01.003 | Gastos de horas extras, feriados y bono nocturno | Gastos de horas extras, feriados y bono nocturno | Utilidad Neta | Sin mapear |
| 6.01.02.01.003 | Gastos de horas extras, feriados y bono nocturno | Gastos de horas extras, feriados y bono nocturno | ISLR | Sin mapear |
| 6.01.02.01.003 | Gastos de horas extras, feriados y bono nocturno | Gastos de horas extras, feriados y bono nocturno | Utilidad Neta despues de ISLR | Sin mapear |
| 6.01.02.01.004 | Gastos de complemento de sueldos y salarios empleados | Gastos de complemento de sueldos y salarios empleados | Gastos de complementos empleados y directivos | Sin mapear |
| 6.01.02.01.005 | Gastos de complemento de sueldos y salarios directivos | Gastos de complemento de sueldos y salarios directivos | Gastos de complementos empleados y directivos | Sin mapear |
| 6.01.02.01.006 | Gastos de Bono de alimentación empleados | Gastos de Bono de alimentación empleados | Total Gastos Operacionales | Sin mapear |
| 6.01.02.01.006 | Gastos de Bono de alimentación empleados | Gastos de Bono de alimentación empleados | Subtotal Gastos de Recursos Humanos | Sin mapear |
| 6.01.02.01.006 | Gastos de Bono de alimentación empleados | Gastos de Bono de alimentación empleados | Gastos de sueldos y salarios empleados y directivos | Sin mapear |
| 6.01.02.01.006 | Gastos de Bono de alimentación empleados | Gastos de Bono de alimentación empleados | Utilidad antes de Comisiones por Ventas | Sin mapear |
| 6.01.02.01.006 | Gastos de Bono de alimentación empleados | Gastos de Bono de alimentación empleados | Utilidad después de Comisiones por Ventas | Sin mapear |
| 6.01.02.01.006 | Gastos de Bono de alimentación empleados | Gastos de Bono de alimentación empleados | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 6.01.02.01.006 | Gastos de Bono de alimentación empleados | Gastos de Bono de alimentación empleados | Utilidad antes de Intereses e Impuestos (EBIT) | Sin mapear |
| 6.01.02.01.006 | Gastos de Bono de alimentación empleados | Gastos de Bono de alimentación empleados | Total Gastos Operacionales y No Operacionales | Sin mapear |
| 6.01.02.01.006 | Gastos de Bono de alimentación empleados | Gastos de Bono de alimentación empleados | Utilidad Neta | Sin mapear |
| 6.01.02.01.006 | Gastos de Bono de alimentación empleados | Gastos de Bono de alimentación empleados | ISLR | Sin mapear |
| 6.01.02.01.006 | Gastos de Bono de alimentación empleados | Gastos de Bono de alimentación empleados | Utilidad Neta despues de ISLR | Sin mapear |
| 6.01.02.01.007 | Gastos de Bono de alimentación directivos | Gastos de Bono de alimentación directivos | Total Gastos Operacionales | Sin mapear |
| 6.01.02.01.007 | Gastos de Bono de alimentación directivos | Gastos de Bono de alimentación directivos | Subtotal Gastos de Recursos Humanos | Sin mapear |
| 6.01.02.01.007 | Gastos de Bono de alimentación directivos | Gastos de Bono de alimentación directivos | Gastos de sueldos y salarios empleados y directivos | Sin mapear |
| 6.01.02.01.007 | Gastos de Bono de alimentación directivos | Gastos de Bono de alimentación directivos | Utilidad antes de Comisiones por Ventas | Sin mapear |
| 6.01.02.01.007 | Gastos de Bono de alimentación directivos | Gastos de Bono de alimentación directivos | Utilidad después de Comisiones por Ventas | Sin mapear |
| 6.01.02.01.007 | Gastos de Bono de alimentación directivos | Gastos de Bono de alimentación directivos | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 6.01.02.01.007 | Gastos de Bono de alimentación directivos | Gastos de Bono de alimentación directivos | Utilidad antes de Intereses e Impuestos (EBIT) | Sin mapear |
| 6.01.02.01.007 | Gastos de Bono de alimentación directivos | Gastos de Bono de alimentación directivos | Total Gastos Operacionales y No Operacionales | Sin mapear |
| 6.01.02.01.007 | Gastos de Bono de alimentación directivos | Gastos de Bono de alimentación directivos | Utilidad Neta | Sin mapear |
| 6.01.02.01.007 | Gastos de Bono de alimentación directivos | Gastos de Bono de alimentación directivos | ISLR | Sin mapear |
| 6.01.02.01.007 | Gastos de Bono de alimentación directivos | Gastos de Bono de alimentación directivos | Utilidad Neta despues de ISLR | Sin mapear |
| 6.01.02.01.008 | Gastos de vacaciones empleados | Gastos de vacaciones empleados | Total Gastos Operacionales | Sin mapear |
| 6.01.02.01.008 | Gastos de vacaciones empleados | Gastos de vacaciones empleados | Subtotal Gastos de Recursos Humanos | Sin mapear |
| 6.01.02.01.008 | Gastos de vacaciones empleados | Gastos de vacaciones empleados | Gastos de sueldos y salarios empleados y directivos | Sin mapear |
| 6.01.02.01.008 | Gastos de vacaciones empleados | Gastos de vacaciones empleados | Utilidad antes de Comisiones por Ventas | Sin mapear |
| 6.01.02.01.008 | Gastos de vacaciones empleados | Gastos de vacaciones empleados | Utilidad después de Comisiones por Ventas | Sin mapear |
| 6.01.02.01.008 | Gastos de vacaciones empleados | Gastos de vacaciones empleados | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 6.01.02.01.008 | Gastos de vacaciones empleados | Gastos de vacaciones empleados | Utilidad antes de Intereses e Impuestos (EBIT) | Sin mapear |
| 6.01.02.01.008 | Gastos de vacaciones empleados | Gastos de vacaciones empleados | Total Gastos Operacionales y No Operacionales | Sin mapear |
| 6.01.02.01.008 | Gastos de vacaciones empleados | Gastos de vacaciones empleados | Utilidad Neta | Sin mapear |
| 6.01.02.01.008 | Gastos de vacaciones empleados | Gastos de vacaciones empleados | ISLR | Sin mapear |
| 6.01.02.01.008 | Gastos de vacaciones empleados | Gastos de vacaciones empleados | Utilidad Neta despues de ISLR | Sin mapear |
| 6.01.02.01.009 | Gastos de vacaciones directivos | Gastos de vacaciones directivos | Total Gastos Operacionales | Sin mapear |
| 6.01.02.01.009 | Gastos de vacaciones directivos | Gastos de vacaciones directivos | Subtotal Gastos de Recursos Humanos | Sin mapear |
| 6.01.02.01.009 | Gastos de vacaciones directivos | Gastos de vacaciones directivos | Gastos de sueldos y salarios empleados y directivos | Sin mapear |
| 6.01.02.01.009 | Gastos de vacaciones directivos | Gastos de vacaciones directivos | Utilidad antes de Comisiones por Ventas | Sin mapear |
| 6.01.02.01.009 | Gastos de vacaciones directivos | Gastos de vacaciones directivos | Utilidad después de Comisiones por Ventas | Sin mapear |
| 6.01.02.01.009 | Gastos de vacaciones directivos | Gastos de vacaciones directivos | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 6.01.02.01.009 | Gastos de vacaciones directivos | Gastos de vacaciones directivos | Utilidad antes de Intereses e Impuestos (EBIT) | Sin mapear |
| 6.01.02.01.009 | Gastos de vacaciones directivos | Gastos de vacaciones directivos | Total Gastos Operacionales y No Operacionales | Sin mapear |
| 6.01.02.01.009 | Gastos de vacaciones directivos | Gastos de vacaciones directivos | Utilidad Neta | Sin mapear |
| 6.01.02.01.009 | Gastos de vacaciones directivos | Gastos de vacaciones directivos | ISLR | Sin mapear |
| 6.01.02.01.009 | Gastos de vacaciones directivos | Gastos de vacaciones directivos | Utilidad Neta despues de ISLR | Sin mapear |
| 6.01.02.01.010 | Gastos de complemento de vacaciones empleados | Gastos de complemento de vacaciones empleados | Gastos de complementos empleados y directivos | Sin mapear |
| 6.01.02.01.011 | Gastos de complemento de vacaciones directivos | Gastos de complemento de vacaciones directivos | Gastos de complementos empleados y directivos | Sin mapear |
| 6.01.02.01.012 | Gastos de otros bonos empleados | Gastos de otros bonos empleados | Gastos de complementos empleados y directivos | Sin mapear |
| 6.01.02.01.999 | Gastos de servicios de personal externo | Gastos de servicios de personal externo | Gastos de personal externo | Sin mapear |
| 6.01.02.02 | Gastos de pasivos laborales | Gastos de pasivos laborales | Sin mapear | Sin mapear |
| 6.01.02.02.001 | Gastos de bono vacacional empleados | Gastos de bono vacacional empleados | Gastos de pasivos laborales vacaciones | Sin mapear |
| 6.01.02.02.002 | Gastos de bono vacacional directivos | Gastos de bono vacacional directivos | Gastos de pasivos laborales vacaciones | Sin mapear |
| 6.01.02.02.003 | Gastos de complemento bono vacacional empleados | Gastos de complemento bono vacacional empleados | Gastos de pasivos laborales vacaciones | Sin mapear |
| 6.01.02.02.004 | Gastos de complemento bono vacacional directivos | Gastos de complemento bono vacacional directivos | Gastos de pasivos laborales vacaciones | Sin mapear |
| 6.01.02.02.005 | Gastos de utilidades empleados | Gastos de utilidades empleados | Gastos de pasivos laborales utilidades | Sin mapear |
| 6.01.02.02.006 | Gastos de utilidades directivos | Gastos de utilidades directivos | Gastos de pasivos laborales utilidades | Sin mapear |
| 6.01.02.02.007 | Gastos de complemento de utilidades empleados | Gastos de complemento de utilidades empleados | Gastos de pasivos laborales utilidades | Sin mapear |
| 6.01.02.02.008 | Gastos de complemento de utilidades directivos | Gastos de complemento de utilidades directivos | Gastos de pasivos laborales utilidades | Sin mapear |
| 6.01.02.02.009 | Gastos de prestaciones sociales empleados | Gastos de prestaciones sociales empleados | Gastos de pasivos laborales prestaciones e intereses | Sin mapear |
| 6.01.02.02.010 | Gastos de prestaciones sociales directivos | Gastos de prestaciones sociales directivos | Gastos de pasivos laborales prestaciones e intereses | Sin mapear |
| 6.01.02.02.011 | Gastos de complemento de prestaciones sociales empleados | Gastos de complemento de prestaciones sociales empleados | Gastos de pasivos laborales prestaciones e intereses | Sin mapear |
| 6.01.02.02.012 | Gastos de complemento de prestaciones sociales directivos | Gastos de complemento de prestaciones sociales directivos | Gastos de pasivos laborales prestaciones e intereses | Sin mapear |
| 6.01.02.02.013 | Gastos de intereses sobres prestaciones sociales empleados | Gastos de intereses sobres prestaciones sociales empleados | Gastos de pasivos laborales prestaciones e intereses | Sin mapear |
| 6.01.02.02.014 | Gastos de intereses sobres prestaciones sociales directivos | Gastos de intereses sobres prestaciones sociales directivos | Gastos de pasivos laborales prestaciones e intereses | Sin mapear |
| 6.01.02.02.015 | Gastos de complemento de intereses sobre prestaciones sociales empleados | Gastos de complemento de intereses sobre prestaciones sociales empleados | Gastos de pasivos laborales prestaciones e intereses | Sin mapear |
| 6.01.02.02.016 | Gastos de complemento de intereses sobre prestaciones sociales directivos | Gastos de complemento de intereses sobre prestaciones sociales directivos | Gastos de pasivos laborales prestaciones e intereses | Sin mapear |
| 6.01.02.02.017 | Gastos de aporte patronal IVSS | Gastos de aporte patronal IVSS | Gastos de pasivos laborales aportes | Sin mapear |
| 6.01.02.02.018 | Gastos de aporte patronal SPF | Gastos de aporte patronal SPF | Gastos de pasivos laborales aportes | Sin mapear |
| 6.01.02.02.019 | Gastos de aporte patronal FAOV | Gastos de aporte patronal FAOV | Gastos de pasivos laborales aportes | Sin mapear |
| 6.01.02.02.020 | Gastos de aporte patronal INCES | Gastos de aporte patronal INCES | Gastos de pasivos laborales aportes | Sin mapear |
| 6.01.02.02.021 | Gastos de bono de guardería | Gastos de bono de guardería | Gastos de pasivos laborales bono de guardería | Sin mapear |
| 6.01.02.02.022 | Gastos de póliza HCM | Gastos de póliza HCM | Gastos de pasivos laborales HCM | Sin mapear |
| 6.01.02.03 | Gastos de seguridad y salud laboral | Gastos de seguridad y salud laboral | Sin mapear | Sin mapear |
| 6.01.02.03.001 | Gastos de salud y seguridad laboral | Gastos de salud y seguridad laboral | Gastos de salud y seguridad laboral | Sin mapear |
| 6.01.02.03.002 | Gastos de uniformes y dotación al personal | Gastos de uniformes y dotación al personal | Gastos de salud y seguridad laboral dotación | Sin mapear |
| 6.01.02.03.003 | Gastos de fiestas y agasajos al personal | Gastos de fiestas y agasajos al personal | Gastos de salud y seguridad laboral fiestas y agasajos | Sin mapear |
| 6.01.02.04 | Otros gastos de personal | Otros gastos de personal | Otros gastos de personal | Sin mapear |
| 6.01.02.04.001 | Gastos de donaciones y obsequios al personal | Gastos de donaciones y obsequios al personal | Sin mapear | Sin mapear |
| 6.01.02.04.002 | Gastos de capacitación al personal | Gastos de capacitación al personal | Sin mapear | Sin mapear |
| 6.01.02.04.003 | Gastos de transporte del personal | Gastos de transporte del personal | Sin mapear | Sin mapear |
| 6.01.03 | Gastos de comercialización y logística | Gastos de comercialización y logística | Sin mapear | Sin mapear |
| 6.01.03.01 | Gastos de viáticos comerciales | Gastos de viáticos comerciales | Total Gastos Operacionales | Sin mapear |
| 6.01.03.01 | Gastos de viáticos comerciales | Gastos de viáticos comerciales | Subtotal Gastos de Comercialización y Logistica | Sin mapear |
| 6.01.03.01 | Gastos de viáticos comerciales | Gastos de viáticos comerciales | Gastos de viáticos comerciales | Sin mapear |
| 6.01.03.01 | Gastos de viáticos comerciales | Gastos de viáticos comerciales | Utilidad antes de Comisiones por Ventas | Sin mapear |
| 6.01.03.01 | Gastos de viáticos comerciales | Gastos de viáticos comerciales | Utilidad después de Comisiones por Ventas | Sin mapear |
| 6.01.03.01 | Gastos de viáticos comerciales | Gastos de viáticos comerciales | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 6.01.03.01 | Gastos de viáticos comerciales | Gastos de viáticos comerciales | Utilidad antes de Intereses e Impuestos (EBIT) | Sin mapear |
| 6.01.03.01 | Gastos de viáticos comerciales | Gastos de viáticos comerciales | Total Gastos Operacionales y No Operacionales | Sin mapear |
| 6.01.03.01 | Gastos de viáticos comerciales | Gastos de viáticos comerciales | Utilidad Neta | Sin mapear |
| 6.01.03.01 | Gastos de viáticos comerciales | Gastos de viáticos comerciales | ISLR | Sin mapear |
| 6.01.03.01 | Gastos de viáticos comerciales | Gastos de viáticos comerciales | Utilidad Neta despues de ISLR | Sin mapear |
| 6.01.03.01.001 | Gastos de pasajes por viáticos comerciales | Gastos de pasajes por viáticos comerciales | Sin mapear | Sin mapear |
| 6.01.03.01.002 | Gastos de comida por viáticos comerciales | Gastos de comida por viáticos comerciales | Sin mapear | Sin mapear |
| 6.01.03.01.003 | Gastos de hospedaje por viáticos comerciales | Gastos de hospedaje por viáticos comerciales | Sin mapear | Sin mapear |
| 6.01.03.01.004 | Gastos de transporte por viáticos comerciales | Gastos de transporte por viáticos comerciales | Sin mapear | Sin mapear |
| 6.01.03.01.005 | Otros gastos de viáticos comerciales | Otros gastos de viáticos comerciales | Sin mapear | Sin mapear |
| 6.01.03.02 | Gastos no asociados al costo | Gastos no asociados al costo | Sin mapear | Sin mapear |
| 6.01.03.02.001 | Gastos de envíos/fletes en ventas y compras no incluidas en el costo | Gastos de envíos/fletes en ventas y compras no incluidas en el costo | Gastos de fletes y envios no asociados al costo | Sin mapear |
| 6.01.03.02.002 | Gastos de almacenaje sobre compras no incluídos en el costo | Gastos de almacenaje sobre compras no incluídos en el costo | Otros gastos no asociados al costo | Sin mapear |
| 6.01.03.02.003 | Gastos de importación no incluídos en el costo | Gastos de importación no incluídos en el costo | Otros gastos no asociados al costo | Sin mapear |
| 6.01.03.02.004 | Gastos de seguro de mercancía no incluídos en el costo | Gastos de seguro de mercancía no incluídos en el costo | Otros gastos no asociados al costo | Sin mapear |
| 6.01.03.02.005 | Gastos de bolsas no incluídos en el costo | Gastos de bolsas no incluídos en el costo | Otros gastos no asociados al costo | Sin mapear |
| 6.01.03.02.006 | Gastos de embalaje no incluídos en el costo | Gastos de embalaje no incluídos en el costo | Otros gastos no asociados al costo | Sin mapear |
| 6.01.03.02.007 | Gastos de etiquetas no incluídos en el costo | Gastos de etiquetas no incluídos en el costo | Otros gastos no asociados al costo | Sin mapear |
| 6.01.03.02.008 | Gastos de armado de bicicletas no incluídos en el costo | Gastos de armado de bicicletas no incluídos en el costo | Otros gastos no asociados al costo | Sin mapear |
| 6.01.03.02.009 | Gastos de títulos de propiedad no incluídos en el costo | Gastos de títulos de propiedad no incluídos en el costo | Otros gastos no asociados al costo | Sin mapear |
| 6.01.03.03 | Gastos de comisiones por ventas | Gastos de comisiones por ventas | Total Gastos Operacionales | Sin mapear |
| 6.01.03.03 | Gastos de comisiones por ventas | Gastos de comisiones por ventas | Subtotal Gastos de Comercialización y Logistica | Sin mapear |
| 6.01.03.03 | Gastos de comisiones por ventas | Gastos de comisiones por ventas | Utilidad antes de Comisiones por Ventas | Sin mapear |
| 6.01.03.03 | Gastos de comisiones por ventas | Gastos de comisiones por ventas | Gastos de comisiones por ventas | Sin mapear |
| 6.01.03.03 | Gastos de comisiones por ventas | Gastos de comisiones por ventas | Utilidad después de Comisiones por Ventas | Sin mapear |
| 6.01.03.03 | Gastos de comisiones por ventas | Gastos de comisiones por ventas | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 6.01.03.03 | Gastos de comisiones por ventas | Gastos de comisiones por ventas | Utilidad antes de Intereses e Impuestos (EBIT) | Sin mapear |
| 6.01.03.03 | Gastos de comisiones por ventas | Gastos de comisiones por ventas | Total Gastos Operacionales y No Operacionales | Sin mapear |
| 6.01.03.03 | Gastos de comisiones por ventas | Gastos de comisiones por ventas | Utilidad Neta | Sin mapear |
| 6.01.03.03 | Gastos de comisiones por ventas | Gastos de comisiones por ventas | ISLR | Sin mapear |
| 6.01.03.03 | Gastos de comisiones por ventas | Gastos de comisiones por ventas | Utilidad Neta despues de ISLR | Sin mapear |
| 6.01.03.03.001 | Gastos de comisiones empleados | Gastos de comisiones empleados | Sin mapear | Sin mapear |
| 6.01.03.03.002 | Gastos de comisiones empleados del taller | Gastos de comisiones empleados del taller | Total Gastos Operacionales | Sin mapear |
| 6.01.03.03.002 | Gastos de comisiones empleados del taller | Gastos de comisiones empleados del taller | Subtotal Gastos de Comercialización y Logistica | Sin mapear |
| 6.01.03.03.002 | Gastos de comisiones empleados del taller | Gastos de comisiones empleados del taller | Utilidad antes de Comisiones por Ventas | Sin mapear |
| 6.01.03.03.002 | Gastos de comisiones empleados del taller | Gastos de comisiones empleados del taller | Gastos de comisiones por ventas taller | Sin mapear |
| 6.01.03.03.002 | Gastos de comisiones empleados del taller | Gastos de comisiones empleados del taller | Utilidad después de Comisiones por Ventas | Sin mapear |
| 6.01.03.03.002 | Gastos de comisiones empleados del taller | Gastos de comisiones empleados del taller | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 6.01.03.03.002 | Gastos de comisiones empleados del taller | Gastos de comisiones empleados del taller | Utilidad antes de Intereses e Impuestos (EBIT) | Sin mapear |
| 6.01.03.03.002 | Gastos de comisiones empleados del taller | Gastos de comisiones empleados del taller | Total Gastos Operacionales y No Operacionales | Sin mapear |
| 6.01.03.03.002 | Gastos de comisiones empleados del taller | Gastos de comisiones empleados del taller | Utilidad Neta | Sin mapear |
| 6.01.03.03.002 | Gastos de comisiones empleados del taller | Gastos de comisiones empleados del taller | ISLR | Sin mapear |
| 6.01.03.03.002 | Gastos de comisiones empleados del taller | Gastos de comisiones empleados del taller | Utilidad Neta despues de ISLR | Sin mapear |
| 6.01.03.03.003 | Gastos de comisiones por venta de personal externo | Gastos de comisiones por venta de personal externo | Sin mapear | Sin mapear |
| 6.01.03.04 | Gastos por combustible | Gastos por combustible | Gastos por combustible | Sin mapear |
| 6.01.03.04.001 | Gastos por gasolina | Gastos por gasolina | Sin mapear | Sin mapear |
| 6.01.03.04.002 | Gastos por gasoil | Gastos por gasoil | Sin mapear | Sin mapear |
| 6.01.03.05 | Gastos de representación | Gastos de representación | Sin mapear | Sin mapear |
| 6.01.03.05.001 | Gastos de representación | Gastos de representación | Gastos de representación | Sin mapear |
| 6.01.03.06 | Gastos de garantías | Gastos de garantías | Sin mapear | Sin mapear |
| 6.01.03.06.001 | Gastos de garantías | Gastos de garantías | Gastos por garantia | Sin mapear |
| 6.01.03.07 | Gastos de Suscripciones | Gastos de Suscripciones | Sin mapear | Sin mapear |
| 6.01.03.07.001 | Gastos de suscripciones | Gastos de suscripciones | Gastos por suscripciones | Sin mapear |
| 6.01.03.08 | Gastos de Stand y/o ferias comerciales | Gastos de Stand y/o ferias comerciales | Gastos de Stand y/o ferias comerciales | Sin mapear |
| 6.01.03.08.001 | Gastos de alquiler Stand y/o ferias comerciales | Gastos de alquiler Stand y/o ferias comerciales | Sin mapear | Sin mapear |
| 6.01.03.08.002 | Gastos de pasajes Stand y/o ferias comerciales | Gastos de pasajes Stand y/o ferias comerciales | Sin mapear | Sin mapear |
| 6.01.03.08.003 | Gastos de viáticos comida Stand y/o ferias comerciales | Gastos de viáticos comida Stand y/o ferias comerciales | Sin mapear | Sin mapear |
| 6.01.03.08.004 | Gastos de viáticos hospedaje Stand y/o ferias comerciales | Gastos de viáticos hospedaje Stand y/o ferias comerciales | Sin mapear | Sin mapear |
| 6.01.03.08.005 | Gastos de viáticos transporte Stand y/o ferias comerciales | Gastos de viáticos transporte Stand y/o ferias comerciales | Sin mapear | Sin mapear |
| 6.01.03.08.006 | Gastos de otros viáticos Stand y/o ferias comerciales | Gastos de otros viáticos Stand y/o ferias comerciales | Sin mapear | Sin mapear |
| 6.01.03.08.007 | Gastos de publicidad Stand y/o ferias comerciales | Gastos de publicidad Stand y/o ferias comerciales | Sin mapear | Sin mapear |
| 6.01.03.08.008 | Gastos de premiaciones, donaciones Stand y/o ferias comerciales | Gastos de premiaciones, donaciones Stand y/o ferias comerciales | Sin mapear | Sin mapear |
| 6.01.04 | Gastos de mercadeo | Gastos de mercadeo | Sin mapear | Sin mapear |
| 6.01.04.01 | Gastos de publicidad y promoción | Gastos de publicidad y promoción | Sin mapear | Sin mapear |
| 6.01.04.01.001 | Gastos de redes sociales | Gastos de redes sociales | Total Gastos Operacionales | Sin mapear |
| 6.01.04.01.001 | Gastos de redes sociales | Gastos de redes sociales | Subtotal Gastos de Mercadeo | Sin mapear |
| 6.01.04.01.001 | Gastos de redes sociales | Gastos de redes sociales | Gastos de redes sociales | Sin mapear |
| 6.01.04.01.001 | Gastos de redes sociales | Gastos de redes sociales | Utilidad antes de Comisiones por Ventas | Sin mapear |
| 6.01.04.01.001 | Gastos de redes sociales | Gastos de redes sociales | Utilidad después de Comisiones por Ventas | Sin mapear |
| 6.01.04.01.001 | Gastos de redes sociales | Gastos de redes sociales | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 6.01.04.01.001 | Gastos de redes sociales | Gastos de redes sociales | Utilidad antes de Intereses e Impuestos (EBIT) | Sin mapear |
| 6.01.04.01.001 | Gastos de redes sociales | Gastos de redes sociales | Total Gastos Operacionales y No Operacionales | Sin mapear |
| 6.01.04.01.001 | Gastos de redes sociales | Gastos de redes sociales | Utilidad Neta | Sin mapear |
| 6.01.04.01.001 | Gastos de redes sociales | Gastos de redes sociales | ISLR | Sin mapear |
| 6.01.04.01.001 | Gastos de redes sociales | Gastos de redes sociales | Utilidad Neta despues de ISLR | Sin mapear |
| 6.01.04.01.002 | Gastos de medios publicitarios | Gastos de medios publicitarios | Gastos de medios publicitarios | Sin mapear |
| 6.01.04.01.003 | Gastos de impresiones de material gráfico | Gastos de impresiones de material gráfico | Otros gastos de publicidad y promoción | Sin mapear |
| 6.01.04.01.004 | Gastos de decoración | Gastos de decoración | Otros gastos de publicidad y promoción | Sin mapear |
| 6.01.04.01.005 | Gastos de muestras y material POP | Gastos de muestras y material POP | Otros gastos de publicidad y promoción | Sin mapear |
| 6.01.04.01.006 | Gastos de campañas y lanzamientos | Gastos de campañas y lanzamientos | Otros gastos de publicidad y promoción | Sin mapear |
| 6.01.04.02 | Gastos de patrocinio y donación | Gastos de patrocinio y donación | Gastos de patrocinio y donación | Sin mapear |
| 6.01.04.02.001 | Gastos de patrocinio, donación y/o obsequios en efectivo | Gastos de patrocinio, donación y/o obsequios en efectivo | Sin mapear | Sin mapear |
| 6.01.04.02.002 | Gastos de patrocinio, donación y/o obsequios en productos | Gastos de patrocinio, donación y/o obsequios en productos | Sin mapear | Sin mapear |
| 6.01.04.03 | Gastos de eventos | Gastos de eventos | Sin mapear | Sin mapear |
| 6.01.04.03.001 | Gastos de viáticos por eventos | Gastos de viáticos por eventos | Gastos de viáticos por eventos | Sin mapear |
| 6.01.04.03.002 | Gastos de materiales y servicios por eventos | Gastos de materiales y servicios por eventos | Gastos de materiales y servicios por eventos | Sin mapear |
| 6.01.04.03.003 | Gastos de alimentos y bebidas por eventos | Gastos de alimentos y bebidas por eventos | Gastos de alimentos y bebidas por eventos | Sin mapear |
| 6.01.04.03.004 | Gastos de personal por eventos | Gastos de personal por eventos | Gastos de personal por eventos | Sin mapear |
| 6.01.04.03.005 | Gastos de patrocinio, donación y/o obsequios por eventos | Gastos de patrocinio, donación y/o obsequios por eventos | Gastos de patrocinio, donación y/o obseq por eventos | Sin mapear |
| 6.01.05 | Gastos de TI+I | Gastos de TI+I | Total Gastos Operacionales | Sin mapear |
| 6.01.05 | Gastos de TI+I | Gastos de TI+I | Gastos de TI+I | Sin mapear |
| 6.01.05 | Gastos de TI+I | Gastos de TI+I | Utilidad antes de Comisiones por Ventas | Sin mapear |
| 6.01.05 | Gastos de TI+I | Gastos de TI+I | Utilidad después de Comisiones por Ventas | Sin mapear |
| 6.01.05 | Gastos de TI+I | Gastos de TI+I | Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA) | Sin mapear |
| 6.01.05 | Gastos de TI+I | Gastos de TI+I | Utilidad antes de Intereses e Impuestos (EBIT) | Sin mapear |
| 6.01.05 | Gastos de TI+I | Gastos de TI+I | Total Gastos Operacionales y No Operacionales | Sin mapear |
| 6.01.05 | Gastos de TI+I | Gastos de TI+I | Utilidad Neta | Sin mapear |
| 6.01.05 | Gastos de TI+I | Gastos de TI+I | ISLR | Sin mapear |
| 6.01.05 | Gastos de TI+I | Gastos de TI+I | Utilidad Neta despues de ISLR | Sin mapear |
| 6.01.05.01 | Gastos página web | Gastos página web | Sin mapear | Sin mapear |
| 6.01.05.01.001 | Gastos de dominio de página web | Gastos de dominio de página web | Gastos de página web | Sin mapear |
| 6.01.05.01.002 | Gastos de servidores | Gastos de servidores | Gastos de página web | Sin mapear |
| 6.01.05.02 | Gastos de desarrollo | Gastos de desarrollo | Gastos de desarrollo | Sin mapear |
| 6.01.05.02.001 | Gastos de software tecnológico | Gastos de software tecnológico | Sin mapear | Sin mapear |
| 6.02 | Gastos no operativos | Gastos no operativos | Sin mapear | Sin mapear |
| 6.02.01 | Otros Gastos | Otros Gastos | Sin mapear | Sin mapear |
| 6.02.01.01 | Otros Gastos | Otros Gastos | Sin mapear | Sin mapear |
| 6.02.01.01.001 | Faltante en Ventas | Faltante en Ventas | Otros Gastos no Operacionales | Sin mapear |
| 6.02.01.01.001 | Faltante en Ventas | Faltante en Ventas | Faltante en Ventas | Sin mapear |
| 6.02.01.01.001 | Faltante en Ventas | Faltante en Ventas | Total Gastos Operacionales y No Operacionales | Sin mapear |
| 6.02.01.01.001 | Faltante en Ventas | Faltante en Ventas | Utilidad Neta | Sin mapear |
| 6.02.01.01.001 | Faltante en Ventas | Faltante en Ventas | ISLR | Sin mapear |
| 6.02.01.01.001 | Faltante en Ventas | Faltante en Ventas | Utilidad Neta despues de ISLR | Sin mapear |
| 6.02.01.01.002 | Pérdida en venta de activos | Pérdida en venta de activos | Pérdida en venta de activos | Sin mapear |
| 6.02.01.01.003 | Pérdida en siniestro de activos | Pérdida en siniestro de activos | Pérdida en siniestro de activos | Sin mapear |
| 6.02.01.01.004 | Pérdida en tasa cambiaria | Pérdida en tasa cambiaria | Pérdida en tasa cambiaria | Sin mapear |
| 6.02.01.01.005 | Pérdida por diferencia en pagos | Pérdida por diferencia en pagos | Pérdida por diferencia en pagos | Sin mapear |
| 6.02.01.01.006 | Multas | Multas | Multas | Sin mapear |
| 6.02.01.01.007 | Faltante de inventarios | Faltante de inventarios | Otros Gastos no Operacionales | Sin mapear |
| 6.02.01.01.007 | Faltante de inventarios | Faltante de inventarios | Faltante y deterioro de inventarios | Sin mapear |
| 6.02.01.01.007 | Faltante de inventarios | Faltante de inventarios | Total Gastos Operacionales y No Operacionales | Sin mapear |
| 6.02.01.01.007 | Faltante de inventarios | Faltante de inventarios | Utilidad Neta | Sin mapear |
| 6.02.01.01.007 | Faltante de inventarios | Faltante de inventarios | ISLR | Sin mapear |
| 6.02.01.01.007 | Faltante de inventarios | Faltante de inventarios | Utilidad Neta despues de ISLR | Sin mapear |
| 6.02.01.01.008 | Deterioro de inventarios | Deterioro de inventarios | Otros Gastos no Operacionales | Sin mapear |
| 6.02.01.01.008 | Deterioro de inventarios | Deterioro de inventarios | Faltante y deterioro de inventarios | Sin mapear |
| 6.02.01.01.008 | Deterioro de inventarios | Deterioro de inventarios | Total Gastos Operacionales y No Operacionales | Sin mapear |
| 6.02.01.01.008 | Deterioro de inventarios | Deterioro de inventarios | Utilidad Neta | Sin mapear |
| 6.02.01.01.008 | Deterioro de inventarios | Deterioro de inventarios | ISLR | Sin mapear |
| 6.02.01.01.008 | Deterioro de inventarios | Deterioro de inventarios | Utilidad Neta despues de ISLR | Sin mapear |


---

## 6. MANEJO DE PARTIDAS AUSENTES
El sistema maneja las cuentas o partidas que no registraron movimientos en un mes dado mediante las siguientes estrategias:

1. **Resolución de Valor con Fallback (`resolve_leaf_value`):** Si una partida hoja no tiene monto en la clave del diccionario (`dict.get(partida_name, {}).get(month, 0) == 0`), se realiza una búsqueda insensible a acentos/mayúsculas en los datos de la base de datos para evitar pérdidas de montos por variaciones tipográficas en Odoo.
2. **Funciones de División Segura (`safe_pct` y `safe_var`):** Se evita el error de división por cero (`ZeroDivisionError`) comprobando si el denominador es cero y retornando `0` o `None` en su defecto.
3. **Oclusión de Filas de Gasto en Detalle:** Al listar el desglose de gastos en la API (`/api/eerr/detalle`), se filtran aquellas partidas cuya sumatoria en el año sea igual a cero (`acum(monthly) != 0`).

### Transcripción de Funciones de Control de Valores Nulos/Cero:

#### Código de `resolve_leaf_value`:
```python
    def resolve_leaf_value(partida_name, month, data_dict):
        if partida_name in groups_v2:
            return sum(data_dict.get(p, {}).get(month, 0) for p in groups_v2[partida_name])
        val = data_dict.get(partida_name, {}).get(month, 0)
        if val == 0:
            pn_norm = norm(partida_name)
            for k, v in data_dict.items():
                if norm(k) == pn_norm:
                    return v.get(month, 0)
        return val


```

#### Código de `safe_pct`:
```python
    def safe_pct(num, den):
        return round(num / den * 100, 1) if den != 0 else 0


```

#### Código de `safe_var`:
```python
    def safe_var(val, base):
        if base == 0: return None
        return round((val - base) / abs(base) * 100, 1)

    rows = []
    for item in EERR_STRUCTURE:
        partida_name = item[0]
        is_header = item[1]
        parent = item[2] if len(item) > 2 else None
        bold = item[3] if len(item) > 3 else False
        bg_color = item[4] if len(item) > 4 else None
        es_nota = item[6] if len(item) > 6 else False

        if is_header:
            prev_val = valores_calculados_por_mes.get('DIC', {}).get(partida_name, 0)
        else:
            prev_val = resolve_leaf_value_prev(partida_name, by_prev_raw)

        prev_pct_vtas = safe_pct(prev_val, ingresos_prev)
        prev_pct_gastos = safe_pct(prev_val, gastos_prev)

        meses_data = []
        acum_ejec = 0
        acum_ppto = 0
        acum_ing_ejec = 0
        acum_ing_ppto = 0
        acum_gas_ejec = 0
        acum_gas_ppto = 0
        val_ejec_mes_anterior = None

        for m in MONTHS:
            month_type = MONTH_TYPES[m]

            if is_header:
                val_ejec = valores_calculados_por_mes[m].get(partida_name, 0)
                val_ppto = 0
            else:
                val_ejec = resolve_leaf_value(partida_name, m, by_partida)
                val_ppto = resolve_leaf_value(partida_name, m, by_budget)

            acum_ejec += val_ejec
            acum_ppto += val_ppto
            acum_ing_ejec += ingresos_ejec_mes[m]
            acum_ing_ppto += ingresos_ppto_mes[m]
            acum_gas_ejec += gastos_ejec_mes[m]
            acum_gas_ppto += gastos_ppto_mes[m]

            pct_vtas_ejec = safe_pct(val_ejec, ingresos_ejec_mes[m])
            pct_gastos_ejec = safe_pct(val_ejec, gastos_ejec_mes[m])

            mes_data = {
                'type': month_type,
                'month': m,
                'ejecutado': {
                    'valor': round(val_ejec, 2),
                    'pct_vtas': pct_vtas_ejec,
                    'pct_gastos': pct_gastos_ejec,
                }
            }

            if month_type != 'A':
                mes_data['vari_rel'] = safe_var(val_ejec, val_ejec_mes_anterior) if val_ejec_mes_anterior is not None else None

                if month_type == 'E':  # DIC
                    mes_data['anio'] = {
                        'valor': round(acum_ejec, 2),
                        'pct_vtas': safe_pct(acum_ejec, acum_ing_ejec),
                        'pct_gastos': safe_pct(acum_ejec, acum_gas_ejec),
                    }
                else:
                    mes_data['acum_ejecutado'] = {
                        'valor': round(acum_ejec, 2),
                        'pct_vtas': safe_pct(acum_ejec, acum_ing_ejec),
                        'pct_gastos': safe_pct(acum_ejec, acum_gas_ejec),
                    }

                if month_type in ('C', 'D', 'E'):
                    mes_data['acum_ppto'] = {
                        'valor': round(acum_ppto, 2),
                        'pct_vtas': safe_pct(acum_ppto, acum_ing_ppto),
                    }
                    mes_data['var_ppto'] = safe_var(acum_ejec, acum_ppto)

                    if month_type == 'D':  # JUN
                        prom_ejec = acum_ejec / 6
                        prom_ppto = acum_ppto / 6
                        prom_ing_ejec = acum_ing_ejec / 6
                        prom_ing_ppto = acum_ing_ppto / 6
                        prom_gas_ejec = acum_gas_ejec / 6
                        prom_gas_ppto = acum_gas_ppto / 6

                        mes_data['prom_6_ejec'] = {
                            'valor': round(prom_ejec, 2),
                            'pct_vtas': safe_pct(prom_ejec, prom_ing_ejec),
                            'pct_gastos': safe_pct(prom_ejec, prom_gas_ejec),
                        }
                        mes_data['prom_6_ppto'] = {
                            'valor': round(prom_ppto, 2),
                            'pct_vtas': safe_pct(prom_ppto, prom_ing_ppto),
                        }
                        mes_data['var_ppto_prom'] = safe_var(prom_ejec, prom_ppto)

            meses_data.append(mes_data)
            val_ejec_mes_anterior = val_ejec

        rows.append({
            'partida': partida_name,
            'is_header': is_header,
            'parent': parent,
            'bold': bold,
            'bg_color': bg_color,
            'es_nota': es_nota,
            'year_prev': {
                'valor': round(prev_val, 2),
                'pct_vtas': prev_pct_vtas,
                'pct_gastos': prev_pct_gastos,
            },
            'meses': meses_data,
        })

    return {
        'year': year,
        'year_prev': year_prev,
        'unit': unit,
        'rows': rows,
    }



```

