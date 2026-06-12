# DIAGNÓSTICO ULTRAX - FASE 4
> **Nota:** Documento generado en modo de solo lectura sobre `ultrax_test.db` sin modificar el código ni la base de datos real.

## 1. SIGNO Y MONTO REAL DE CUENTAS DE VENTAS
Detalle del mapeo, valores del balance de comprobación original y los montos resultantes en la tabla `financials` para las cuentas de devoluciones y descuentos:

### Mapeo en la tabla `mapping`:
| Código Odoo | Nombre Cuenta Odoo | Partida EERR | Signo (sign) | Tipo Ingreso (income_type) |
| --- | --- | --- | --- | --- |
| 4.01.01.02.001 | Devoluciones sobre ventas | Devoluciones sobre ventas | -1 | mercancia |
| 4.01.01.03.001 | Descuentos sobre ventas | Descuentos sobre ventas | -1 | mercancia |
| 4.01.01.03.002 | Descuentos sobre ventas plan de fidelización | Descuentos sobre ventas plan de fidelización | -1 | mercancia |

### Comparativa de Balances en Origen vs financials:
| Código Odoo | Nombre Cuenta Odoo | Balance en XLSX Odoo | Signo Mapping | Partida financials | Monto en financials (Test DB) |
| --- | --- | --- | --- | --- | --- |
| 4.01.01.02.001 | Devoluciones sobre ventas | -500.00 | -1 | Devoluciones sobre ventas | 500.00 |
| 4.01.01.03.001 | Descuentos sobre ventas | -500.00 | -1 | Descuentos sobre ventas | 500.00 |
| 4.01.01.03.002 | Descuentos sobre ventas plan de fidelización | -500.00 | -1 | Descuentos sobre ventas plan de fidelización | 500.00 |

**Explicación del comportamiento:**
- En el balance de comprobación de Odoo, las devoluciones y descuentos se registran con signo negativo ($-500.00$ cada uno).
- En la tabla `mapping`, estas cuentas tienen un signo configurado de $-1$. Al aplicar la fórmula `amount = balance * sign` (es decir, $-500.00 \times -1$), el monto resultante se almacena en la tabla `financials` como un número positivo ($500.00$).
- Al momento de sumar los subtotales jerárquicos en el adaptador, el sistema simplemente **suma** las partidas (`total += valor`). Al estar almacenados como valores positivos, en lugar de restar y reducir los ingresos por ventas, los **incrementan**, ocasionando un descuadre acumulativo en la utilidad bruta.

---

## 2. TOTALES "UTILIDAD BRUTA POR X"
Se buscó textualmente en los archivos [app.py](file:///C:/Users/andre/Desktop/ultrax_app/app.py) y [engine.py](file:///C:/Users/andre/Desktop/ultrax_app/engine.py) cualquier fórmula o lógica asociada a las partidas de utilidad bruta por categoría:

### Partida: `Utilidad Bruta por Venta de Mercancia y Taller`
**Referencias en `app.py`:** Ninguna.
**Referencias en `engine.py`:**
- Línea 45: `('Utilidad Bruta por Venta de Mercancia y Taller', True, None, True, 'FF66FF66', 0, False),`

### Partida: `Utilidad Bruta por Servicios`
**Referencias en `app.py`:** Ninguna.
**Referencias en `engine.py`:**
- Línea 46: `('Utilidad Bruta por Servicios', True, None, True, 'FF66FF66', 0, False),`

### Partida: `Utilidad Bruta por Eventos`
**Referencias en `app.py`:** Ninguna.
**Referencias en `engine.py`:**
- Línea 47: `('Utilidad Bruta por Eventos', True, None, True, 'FF66FF66', 0, False),`

**Confirmación**: No existe **ninguna** fórmula de cálculo en el código para `Utilidad Bruta por Venta de Mercancia y Taller`, `Utilidad Bruta por Servicios` ni `Utilidad Bruta por Eventos`. Estás partidas quedan estáticas y siempre muestran un valor de **$0.00** en el reporte calculado, ya que no son partidas hoja (no acumulan transacciones de `financials` directamente) y al ser definidas con nivel `level=0`, el algoritmo de subtotales detiene la suma de forma inmediata al encontrar el siguiente encabezado de nivel 0.

---

## 3. UBICACIÓN DE HOJAS RRHH EN N EERR vs EERR_STRUCTURE
Comparativa de la estructura de Recursos Humanos y sus niveles jerárquicos entre la hoja de cálculo de referencia `'N EERR'` en `EEFF ULTRAX 2026.xlsx` y la declaración de `EERR_STRUCTURE` en [engine.py](file:///C:/Users/andre/Desktop/ultrax_app/engine.py):

### Tabla Comparativa de Jerarquía de Recursos Humanos:
| Partida en Excel ('N EERR') | Anidación / Grupo Padre en Código (`engine.py`) | Nivel en Código |
| --- | --- | --- |
| Gastos de sueldos y salarios empleados | Gastos de sueldos y salarios empleados y directivos | Level 3 |
| Gastos de sueldos y salarios directivos | Gastos de sueldos y salarios empleados y directivos | Level 3 |
| Gastos de horas extras, feriados y bono nocturno | Gastos de sueldos y salarios empleados y directivos | Level 3 |
| Gastos de complemento de sueldos y salarios empleados | Gastos de complementos empleados y directivos | Level 3 |
| Gastos de complemento de sueldos y salarios directivos | Gastos de complementos empleados y directivos | Level 3 |
| Gastos de Bono de alimentación empleados | Gastos de sueldos y salarios empleados y directivos | Level 3 |
| Gastos de Bono de alimentación directivos | Gastos de sueldos y salarios empleados y directivos | Level 3 |
| Gastos de vacaciones empleados | Gastos de pasivos laborales vacaciones | Level 3 |
| Gastos de vacaciones directivos | Gastos de pasivos laborales vacaciones | Level 3 |
| Gastos de complemento de vacaciones empleados | Gastos de pasivos laborales vacaciones | Level 3 |
| Gastos de complemento de vacaciones directivos | Gastos de pasivos laborales vacaciones | Level 3 |
| Gastos de otros bonos empleados | Otros gastos de personal | Level 3 |
| Gastos de servicios de personal externo | Gastos de personal externo | Level 3 |
| Gastos de bono vacacional empleados | Gastos de pasivos laborales utilidades | Level 3 |
| Gastos de bono vacacional directivos | Gastos de pasivos laborales utilidades | Level 3 |
| Gastos de complemento bono vacacional empleados | Gastos de pasivos laborales utilidades | Level 3 |
| Gastos de complemento bono vacacional directivos | Gastos de pasivos laborales utilidades | Level 3 |
| Gastos de utilidades empleados | Gastos de pasivos laborales utilidades | Level 3 |
| Gastos de utilidades directivos | Gastos de pasivos laborales utilidades | Level 3 |
| Gastos de complemento de utilidades empleados | Gastos de pasivos laborales utilidades | Level 3 |
| Gastos de complemento de utilidades directivos | Gastos de pasivos laborales utilidades | Level 3 |
| Gastos de prestaciones sociales empleados | Gastos de pasivos laborales prestaciones e intereses | Level 3 |
| Gastos de prestaciones sociales directivos | Gastos de pasivos laborales prestaciones e intereses | Level 3 |
| Gastos de complemento de prestaciones sociales empleados | Gastos de pasivos laborales prestaciones e intereses | Level 3 |
| Gastos de complemento de prestaciones sociales directivos | Gastos de pasivos laborales prestaciones e intereses | Level 3 |
| Gastos de intereses sobres prestaciones sociales empleados | Gastos de pasivos laborales prestaciones e intereses | Level 3 |
| Gastos de intereses sobres prestaciones sociales directivos | Gastos de pasivos laborales prestaciones e intereses | Level 3 |
| Gastos de complemento de intereses sobre prestaciones sociales empleados | Gastos de pasivos laborales prestaciones e intereses | Level 3 |
| Gastos de complemento de intereses sobre prestaciones sociales directivos | Gastos de pasivos laborales prestaciones e intereses | Level 3 |
| Gastos de aporte patronal IVSS | Gastos de pasivos laborales aportes | Level 3 |
| Gastos de aporte patronal SPF | Gastos de pasivos laborales aportes | Level 3 |
| Gastos de aporte patronal FAOV | Gastos de pasivos laborales aportes | Level 3 |
| Gastos de aporte patronal INCES | Gastos de pasivos laborales aportes | Level 3 |
| Gastos de bono de guardería | Gastos de pasivos laborales aportes | Level 3 |
| Gastos de póliza HCM | Gastos de pasivos laborales HCM | Level 3 |
| Gastos de salud y seguridad laboral | Gastos de pasivos laborales HCM | Level 3 |
| Gastos de uniformes y dotación al personal | Gastos de pasivos laborales HCM | Level 3 |
| Gastos de fiestas y agasajos al personal | Gastos de salud y seguridad laboral fiestas y agasajos | Level 3 |
| Gastos de donaciones y obsequios al personal | Otros gastos de personal | Level 3 |
| Gastos de capacitación al personal | Otros gastos de personal | Level 3 |
| Gastos de transporte del personal | Otros gastos de personal | Level 3 |

### Observación Jerárquica del Excel vs Código:
1. **Estructura Plana en Excel**: En la hoja `'N EERR'`, todas las partidas de Recursos Humanos están listadas al mismo nivel (dentro del nivel de sangría `Indent 3.0`), situándose como hijas directas de la sección principal `Subtotal Gastos de Recursos Humanos`.
2. **Anidamiento en Código**: En la definición de `EERR_STRUCTURE`, se introdujeron múltiples agrupadores intermedios ficticios con nivel `level=2` (ej. `Gastos de complementos empleados y directivos`, `Gastos de pasivos laborales aportes`, `Gastos de pasivos laborales HCM`, etc.). Las cuentas transaccionales reales se anidan dentro de estos agrupadores de nivel 2 con nivel `level=3`.
