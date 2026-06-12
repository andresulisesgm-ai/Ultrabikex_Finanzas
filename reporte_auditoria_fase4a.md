# Reporte de Auditoría - Fase 4a (Solo Lectura)

Este reporte detalla el estado actual de la lógica de nodos movibles, overrides de jerarquía y la tabla `eerr_nodes` en la base de datos de **ULTRAX**.

---

## 1. Flag y Lógica `movible` en `engine.py`

En [engine.py](file:///C:/Users/andre/Desktop/ultrax_app/engine.py), la función [build_effective_structure](file:///C:/Users/andre/Desktop/ultrax_app/engine.py#L647) implementa la determinación de si una partida es movible o no.

### Código Exacto (Líneas 678–721):
```python
        # Determinar movible
        # 4.1 Bloqueados por exclusión hardcodeada:
        blocked_leaves = {
            'Gasto por impuesto a las pensiones',
            'Gastos de IGTF',
            'Gastos de comisiones bancarias',
            'Gastos de impresiones de material gráfico',
            'Gastos de patrocinio y donación'
        }
        
        # 4.2 Subtotales con membresía fija (bloqueados para el HEADER):
        blocked_headers = {
            'Subtotal Gastos de Administración',
            'Subtotal Gastos de Recursos Humanos',
            'Subtotal Gastos de Comercialización y Logistica',
            'Subtotal Gastos de Mercadeo',
            'Subtotal Gastos de TI+I'
        }

        movible = 'bloqueado'
        if start_idx != -1 and end_idx != -1 and start_idx <= idx <= end_idx:
            # Está en la zona operativa de gastos
            if is_hdr:
                if name in blocked_headers:
                    movible = 'bloqueado'
                else:
                    movible = 'libre' # Otros headers intermedios
            else:
                if name in blocked_leaves:
                    movible = 'bloqueado'
                else:
                    movible = 'libre'
```

### Análisis del Cálculo:
- **Origen de la decisión:** No es estático simple. Es dinámico y se calcula en base al índice (`idx`) del elemento, su nombre (`name`), y si es un header (`is_hdr`).
- **Límites Operacionales:** Solo se consideran como candidatos a ser libres aquellos que se encuentran en el rango del bloque de Gastos Operativos (desde el índice de `'Subtotal Gastos de Administración'` hasta el de `'Gastos de desarrollo'`). Cualquier nodo fuera de esta zona operativa se marca como `'bloqueado'`.
- **Reglas de exclusión:** 
  - Las hojas bloqueadas siempre (`blocked_leaves`) coinciden con las indicadas: *"Gasto por impuesto a las pensiones"*, *"Gastos de IGTF"*, *"Gastos de comisiones bancarias"*, *"Gastos de impresiones de material gráfico"*, and *"Gastos de patrocinio y donación"*.
  - Los 5 subtotales fijos (`blocked_headers`) quedan excluidos/bloqueados para movimiento, pero otros headers intermedios opcionales o cuentas hoja operativas no excluidas se evalúan como `'libre'`.

---

## 2. Estado de la Tabla `eerr_nodes` en la Base de Datos

### Schema de la tabla:
```sql
CREATE TABLE eerr_nodes (
    id            INTEGER PRIMARY KEY,
    parent_id     INTEGER,
    nombre        TEXT NOT NULL,
    nivel         INTEGER NOT NULL,
    tipo          TEXT CHECK(tipo IN ('total', 'subtotal', 'grupo', 'hoja')),
    bold          INTEGER DEFAULT 0,
    bg_color      TEXT,
    display_order INTEGER
)
```

### Contenido actual:
- **Total de filas registradas:** 167 filas.
- **Muestra representativa (primeras 5 filas):**
  ```python
  {'id': 1, 'parent_id': None, 'nombre': 'ESTADO DE RESULTADOS', 'nivel': 0, 'tipo': 'total', 'bold': 1, 'bg_color': None, 'display_order': 0}
  {'id': 2, 'parent_id': None, 'nombre': 'PARTIDAS', 'nivel': 0, 'tipo': 'total', 'bold': 1, 'bg_color': None, 'display_order': 10}
  {'id': 3, 'parent_id': None, 'nombre': 'Total Ingresos', 'nivel': 0, 'tipo': 'total', 'bold': 1, 'bg_color': 'FF6AD9E8', 'display_order': 20}
  {'id': 4, 'parent_id': 3, 'nombre': 'Subtotal Ingresos por Venta de Mercancia', 'nivel': 1, 'tipo': 'subtotal', 'bold': 1, 'bg_color': None, 'display_order': 30}
  {'id': 5, 'parent_id': 4, 'nombre': 'Ingresos por venta de mercancias', 'nivel': 3, 'tipo': 'hoja', 'bold': 0, 'bg_color': None, 'display_order': 40}
  ```

---

## 3. Endpoints en `app.py` y Uso del Flag

Tras realizar una búsqueda en todo el código de [app.py](file:///C:/Users/andre/Desktop/ultrax_app/app.py):
- **Lectura/Escritura de `eerr_nodes`:** **No existen** endpoints ni funciones en `app.py` que realicen operaciones SQL de lectura o escritura sobre la tabla `eerr_nodes`.
- **Uso del flag `movible`:** El backend de Flask no hace referencia ni envía la propiedad `movible` en ninguno de sus endpoints, a pesar de que está presente en el diccionario interno retornado por `build_effective_structure()`.

---

## 4. Referencias en `templates/index.html`

Se revisó la plantilla principal del frontend:
- ** overrides en EERR:** **No hay** referencias a `movible`, `eerr_nodes` o tablas de overrides para la estructura de EERR.
- **kpi / dashboard overrides:** Las únicas referencias de la palabra `overrides` en el JS están limitadas a la persistencia en `localStorage` de la configuración de visibilidad y orden de los widgets del panel/dashboard (Líneas 1253–1260):
  ```javascript
  // Aplicar localStorage overrides para modo normal (retrocompatibilidad)
  const localHidden = LS.get('hidden', null);
  const localKPI = LS.get('kpi', null);
  const localOrder = LS.get('worder', null);
  ```
