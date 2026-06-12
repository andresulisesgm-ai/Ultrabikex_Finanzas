# DISEÑO: CAPA DE PERSONALIZACIÓN DE JERARQUÍA EERR

**Rol:** Auditor de Código  
**Proyecto:** ULTRAX (Flask + SQLite + JS Vanilla)  
**Fecha:** 10 de junio de 2026  

---

## FASE 0: Confirmación de Garantía y Decisión del Nodo "Gastos de pasivos laborales bono de guardería" (Sección 3.2)

### 1. Detección de Duplicación de Saldos (is_header)
Al auditar los saldos y el comportamiento de la base de datos para la cuenta `6.01.02.02.021` (`Gastos de bono de guardería`):
*   Si se inserta el nuevo nodo tal como se especificó en la sección 3.2 original:  
    `('Gastos de pasivos laborales bono de guardería', False, None, False, None, 2, False)` (con `is_header = False`)  
    Ocurrirá un **descuadre por doble contabilidad** (monto sumado dos veces):
    1. En `mapping_groups_v2`, el código `6.01.02.02.021` (`Gastos de bono de guardería`) está mapeado al grupo `Gastos de pasivos laborales bono de guardería`. Si este nuevo nodo tiene `is_header=False`, resolverá su saldo (`10.00` en ENE 2026) y se sumará al subtotal de RRHH.
    2. Al mismo tiempo, la nota `'Gastos de bono de guardería'` (que sigue en la estructura con `is_header=False`) también resolverá su saldo de la base de datos (`10.00`) y se sumará al subtotal de RRHH.
    
    Al ser ambos nodos hojas (`is_header=False`), el subtotal de RRHH acumulará `20.00` en lugar de `10.00`.
*   **Decisión y Corrección:** El nuevo nodo intermedio debe definirse obligatoriamente con `is_header = True` para comportarse como un agrupador de nivel 2 y evitar la duplicación de hojas en la suma bottom-up:
    ```python
    ('Gastos de pasivos laborales bono de guardería', True, None, False, None, 2, False)
    ```

### 2. Decision de Reubicación Posicional de la Nota "Gastos de bono de guardería"
*   **Problema con la posición actual:** Actualmente en `EERR_STRUCTURE`, la nota `'Gastos de bono de guardería'` se encuentra posicionada inmediatamente después de las aportaciones patronales (bajo `'Gastos de pasivos laborales aportes'`). Si se inserta el nuevo header `'Gastos de pasivos laborales bono de guardería'` entre aportes y HCM, pero la nota se queda en su posición actual:
    *   La nota se considerará hija de `'Gastos de pasivos laborales aportes'`.
    *   El nuevo agrupador `'Gastos de pasivos laborales bono de guardería'` (con `is_header=True`) no tendrá ningún nodo hoja posicionado bajo él antes de que se detenga el escaneo (ya que el siguiente nodo sería `'Gastos de pasivos laborales HCM'`, con `level=2`), por lo que su cálculo propio dará **0.00**. Esto crearía una inconsistencia visual seria.
*   **Decisión y Corrección Recomendada:** Para una consistencia visual y de cálculo completa, se debe **reubicar posicionalmente** la nota `Gastos de bono de guardería` para que quede inmediatamente debajo del nuevo agrupador.

#### Comparación de Secuencias (EERR_STRUCTURE):

**Secuencia Actual:**
```python
Index 94: ('Gastos de pasivos laborales aportes', True, None, False, None, 2, False)
Index 95: ('Gastos de aporte patronal IVSS', False, None, False, None, 3, True)
Index 96: ('Gastos de aporte patronal SPF', False, None, False, None, 3, True)
Index 97: ('Gastos de aporte patronal FAOV', False, None, False, None, 3, True)
Index 98: ('Gastos de aporte patronal INCES', False, None, False, None, 3, True)
Index 99: ('Gastos de bono de guardería', False, None, False, None, 3, True)
Index 100: ('Gastos de pasivos laborales HCM', True, None, False, None, 2, False)
```

**Secuencia Corregida:**
```python
Index 94: ('Gastos de pasivos laborales aportes', True, None, False, None, 2, False)
Index 95: ('Gastos de aporte patronal IVSS', False, None, False, None, 3, True)
Index 96: ('Gastos de aporte patronal SPF', False, None, False, None, 3, True)
Index 97: ('Gastos de aporte patronal FAOV', False, None, False, None, 3, True)
Index 98: ('Gastos de aporte patronal INCES', False, None, False, None, 3, True)
# 1. Nuevo Agrupador de Nivel 2 (is_header=True)
Index 99: ('Gastos de pasivos laborales bono de guardería', True, None, False, None, 2, False)
# 2. Nota Reubicada como Hija (level=3, es_nota=True)
Index 100: ('Gastos de bono de guardería', False, None, False, None, 3, True)
Index 101: ('Gastos de pasivos laborales HCM', True, None, False, None, 2, False)
```

---

## 1. Tabla Resumen de Mecanismos de Cálculo

| Nodo | Mecanismo | Archivo y Líneas |
| :--- | :---: | :--- |
| **"Subtotal Gastos de Administración"** | (a) Suma posicional (con exclusión híbrida) | [app.py:1387-1411](file:///C:/Users/andre/Desktop/ultrax_app/app.py#L1387-L1411) |
| **"Total Gastos Operacionales"** | (b) Fórmula con nombres fijos | [app.py:1438-1444](file:///C:/Users/andre/Desktop/ultrax_app/app.py#L1438-L1444) y [1473](file:///C:/Users/andre/Desktop/ultrax_app/app.py#L1473) |
| **"Utilidad Bruta"** | (d) Otro mecanismo (Agregación por clasificación BD con exclusiones manuales) | [app.py:1433-1436](file:///C:/Users/andre/Desktop/ultrax_app/app.py#L1433-L1436) y [1414-1424](file:///C:/Users/andre/Desktop/ultrax_app/app.py#L1414-L1424) |

---

## 2. Fragmentos de Código Citados Textualmente

### A) "Subtotal Gastos de Administración" (Líneas 1387-1411 de `app.py`)
```python
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
                            'Gastos de impresiones de material gráfico',
                            'Gastos de patrocinio y donación'
                        ]:
                            pass
                        else:
                            total += subtotales_por_mes[m].get(c_name, 0)
                    j += 1
                subtotales_por_mes[m][name] = total
```

### B) "Total Gastos Operacionales" (Líneas 1438-1444 y 1473 de `app.py`)
```python
        gastos_operacionales = 0
        for nombre in ['Subtotal Gastos de Administración',
                       'Subtotal Gastos de Recursos Humanos',
                       'Subtotal Gastos de Comercialización y Logistica',
                       'Subtotal Gastos de Mercadeo',
                       'Subtotal Gastos de TI+I']:
            gastos_operacionales += subtotales_por_mes[m].get(nombre, 0)
```
Y su mapeo final en el diccionario de respuesta:
```python
            'Total Gastos Operacionales': gastos_operacionales,
```

### C) "Utilidad Bruta" (Líneas 1414-1424 y 1433-1436 de `app.py`)
Clasificación con exclusión de no operacionales:
```python
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
```
Cálculo de Utilidad Bruta:
```python
        ingresos_operativos = sum(by_partida.get(p, {}).get(m, 0) for p in op_ing_partidas)
        otros_ing = subtotales_por_mes[m].get('Otros Ingresos no Operacionales', 0)
        costo_ventas = sum(by_partida.get(p, {}).get(m, 0) for p in cos_p)
        utilidad_bruta = ingresos_operativos - costo_ventas
```
Y su mapeo final:
```python
            'Utilidad Bruta': utilidad_bruta,
```

---

## 3. Listado de Nombres Hardcodeados Involucrados

### Para "Subtotal Gastos de Administración" (Exclusiones específicas):
*   `'Gasto por impuesto a las pensiones'`
*   `'Gastos de IGTF'`
*   `'Gastos de comisiones bancarias'`

### Para "Total Gastos Operacionales" (Subtotales sumados):
*   `'Subtotal Gastos de Administración'`
*   `'Subtotal Gastos de Recursos Humanos'`
*   `'Subtotal Gastos de Comercialización y Logistica'`
*   `'Subtotal Gastos de Mercadeo'`
*   `'Subtotal Gastos de TI+I'`

### Para "Utilidad Bruta" (Ingresos no operativos excluidos):
*   `'Ingresos por alquileres'`
*   `'Ingresos por intereses'`
*   `'Ingresos por comisiones'`
*   `'Ingresos por servicios administrativos'`
*   `'Sobrante en ventas'`
*   `'Sobrante de inventarios'`
*   `'Ganancia en venta de activos'`
*   `'Ganancia por tasa cambiaria'`
*   `'Ganancia por diferencias en pagos'`

---

## 4. Conclusión

Si un usuario moviera una partida hoja (ej. `"Gastos de seguro"`) de `"Subtotal Gastos de Administración"` a `"Subtotal Gastos de Comercialización y Logistica"` cambiando únicamente su posición/parent en una estructura efectiva, **el monto se movería automáticamente y de manera correcta entre ambos subtotales sin generar descuadres**. Esto ocurre porque los subtotales se calculan dinámicamente utilizando el mecanismo (a) de recorrido por nivel y posición física en la estructura. A su vez, dado que tanto el subtotal de origen como el de destino forman parte de la lista fija de nombres que se consolidan en `"Total Gastos Operacionales"` (mecanismo b), la suma global se mantendrá consistente y balanceada. 

Sin embargo, si se mueve una partida que pertenece a las exclusiones hardcodeadas (como `"Gastos de IGTF"`), o si se intentase desplazar una partida hacia un subtotal nuevo que no esté explícitamente listado en el cálculo de `"Total Gastos Operacionales"`, se produciría un descuadre debido a los filtros y fórmulas de nombres fijos que persisten en la lógica del backend.
