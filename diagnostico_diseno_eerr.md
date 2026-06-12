# DIAGNÓSTICO Y PROPUESTA DE DISEÑO: ESTRUCTURA JERÁRQUICA EERR

**Rol:** Auditor de Código  
**Proyecto:** ULTRAX (Flask + SQLite + JS Vanilla)  
**Fecha:** 10 de junio de 2026  

---

## TAREA 1: Análisis del Frontend (index.html / JS)

### 1. Consumo del Endpoint API
El frontend consume la respuesta del Estado de Resultados (EERR) en dos funciones asíncronas principales dentro de `<script>` en `templates/index.html`:

*   **EERR Normal:** Consumido en la función `loadEERR()` en la **línea 2680**:
    ```javascript
    const r=await fetch(`/api/eerr/completo?year=${year}&unit=${encodeURIComponent(unit)}`);
    ```
*   **EERR Divisa Real:** Consumido en la función `loadERRDivisa()` en la **línea 2452**:
    ```javascript
    const r=await fetch(`/api/eerr/divisa_real?year=${year}&unit=${encodeURIComponent(unit)}`);
    ```

### 2. Bucle de Renderizado de Filas (`rows`)
El array `d.rows` (o equivalente) devuelto por la API se recorre y renderiza en HTML en los siguientes bloques exactos de código:

#### Para `loadEERR()` (Líneas 2826 - 2911):
```javascript
  for(const row of d.rows){
    const isHdr=row.is_header;
    const isTotal=totales.includes(row.partida);
    const useBold=row.bold || isHdr || isTotal;
    const bgColor=row.bg_color?`#${row.bg_color.substring(2)}`:null;
    const bgColorWithAlpha=bgColor?bgColor+'66':'';
    
    const isNote = row.es_nota || false;
    const parentName = isNote ? (NOTES_PARENT_MAP[row.partida] || '') : '';
    const isParent = parentNames.has(row.partida);

    const displayStyle = isNote ? 'display:none;' : '';
    const rStyle=displayStyle + (isHdr?hRowStyle:(bgColorWithAlpha?`background:${bgColorWithAlpha}`:''));
    const boldStyle=useBold?'font-weight:700':'';
    const cellBg=bgColorWithAlpha?`background:${bgColorWithAlpha}`:'background:#fff';

    let r='';
    if(isNote) {
      r=`<tr class="note-row" data-parent="${parentName}" style="${rStyle}"><td style="${lStyle};position:sticky;left:0;${cellBg};z-index:6;min-width:220px;width:220px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;border-right:2px solid var(--bd);padding-left:34px;${useBold?'font-weight:700':''}"><span style="color:var(--mu);margin-right:6px">•</span>${row.partida}</td>`;
    } else if(isParent) {
      r=`<tr class="parent-row" style="${rStyle}"><td style="${lStyle};position:sticky;left:0;${cellBg};z-index:6;min-width:220px;width:220px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;border-right:2px solid var(--bd);padding-left:${isTotal?'8px':'20px'};${useBold?'font-weight:700':''}"><span class="note-toggle" onclick="toggleNoteGroup(event, '${row.partida}')" style="cursor:pointer;margin-right:6px;display:inline-block;width:12px;font-family:monospace;color:var(--primary);font-weight:bold">▶</span>${row.partida}</td>`;
    } else {
      r=`<tr style="${rStyle}"><td style="${lStyle};position:sticky;left:0;${cellBg};z-index:6;min-width:220px;width:220px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;border-right:2px solid var(--bd);padding-left:${isTotal?'8px':'20px'};${useBold?'font-weight:700':''}">${row.partida}</td>`;
    }

    r+=`<td style="${cStyle};${boldStyle}">${fmtZ(row.year_prev.valor)}</td>`;
    r+=`<td style="${cStyle}">${pctZ(row.year_prev.pct_vtas)}</td>`;
    r+=`<td style="${cStyle};border-right:2px solid var(--bd)">${pctZ(row.year_prev.pct_gastos)}</td>`;

    // Renderizar celdas según tipo de mes
    for(let i=0;i<row.meses.length;i++){
      const m=row.meses[i];
      const type=m.type;
      const bg=i%2===0?'background-color:#f0f4f8':'background-color:#ffffff';
      const bLeft='border-left:2px solid var(--bd)';

      // TODOS: Monto, %V, %G
      r+=`<td style="${cStyle};${bg};${bLeft};${boldStyle}">${fmtZ(m.ejecutado.valor)}</td>`;
      r+=`<td style="${cStyle};${bg}">${pctZ(m.ejecutado.pct_vtas)}</td>`;
      r+=`<td style="${cStyle};${bg}">${pctZ(m.ejecutado.pct_gastos)}</td>`;

      // Tipo B+ (FEB, ABR, MAY, JUL, AGO, OCT, NOV, MAR, SEP, JUN, DIC)
      if(type!=='A'){
        r+=`<td style="${cStyle};${bg}">${varCol(m.vari_rel)}</td>`;

        if(type==='E'){  // DIC: AÑO
          r+=`<td style="${cStyle};${bg};${boldStyle}">${fmtZ(m.anio.valor)}</td>`;
          r+=`<td style="${cStyle};${bg}">${pctZ(m.anio.pct_vtas)}</td>`;
          r+=`<td style="${cStyle};${bg}">${pctZ(m.anio.pct_gastos)}</td>`;
        }else{  // Resto: ACUM EJEC
          r+=`<td style="${cStyle};${bg};${boldStyle}">${fmtZ(m.acum_ejecutado.valor)}</td>`;
          r+=`<td style="${cStyle};${bg}">${pctZ(m.acum_ejecutado.pct_vtas)}</td>`;
          r+=`<td style="${cStyle};${bg}">${pctZ(m.acum_ejecutado.pct_gastos)}</td>`;
        }

        // Tipo C+ (MAR, SEP, JUN, DIC)
        if(type==='C' || type==='D' || type==='E'){
          r+=`<td style="${cStyle};${bg}">${fmtZ(m.acum_ppto.valor)}</td>`;
          r+=`<td style="${cStyle};${bg}">${pctZ(m.acum_ppto.pct_vtas)}</td>`;
          r+=`<td style="${cStyle};${bg}">${varCol(m.var_ppto)}</td>`;

          // Tipo D (JUN)
          if(type==='D'){
            r+=`<td style="${cStyle};${bg}">${fmtZ(m.prom_6_ejec.valor)}</td>`;
            r+=`<td style="${cStyle};${bg}">${pctZ(m.prom_6_ejec.pct_vtas)}</td>`;
            r+=`<td style="${cStyle};${bg}">${pctZ(m.prom_6_ejec.pct_gastos)}</td>`;
            r+=`<td style="${cStyle};${bg}">${fmtZ(m.prom_6_ppto.valor)}</td>`;
            r+=`<td style="${cStyle};${bg}">${pctZ(m.prom_6_ppto.pct_vtas)}</td>`;
            r+=`<td style="${cStyle};${bg}">${varCol(m.var_ppto_prom)}</td>`;
          }
        }
      }
    }
    r+='</tr>';
    rows+=r;
  }
```

> [!NOTE]
> Existe una estructura de renderizado análoga para `loadERRDivisa()` en las **líneas 2536 - 2621** que repite exactamente este flujo de iteración pero sin el mapeo/toggle de notas (ya que la vista en divisas solo renderiza las partidas principales agregadas).

### 3. Dependencias Estáticas y Hardcoding en JS
Se identificaron los siguientes elementos fijos en el código JS del frontend:

1.  **Lista de Totales/Subtotales (`totales`):**
    *   **Línea 2527** (dentro de `loadERRDivisa()`) y **Línea 2760** (dentro de `loadEERR()`):
        ```javascript
        const totales=[
          'Total Ingresos','Total Ingresos Operativos','Total Ingresos No Operativos',
          'Total Costo de Ventas',
          'Utilidad Bruta','Utilidad Bruta Mercancía y Taller','Utilidad Bruta Servicios','Utilidad Bruta Eventos',
          'Total Gastos','Subtotal Gastos Operacionales','Subtotal Gastos de Administración','Subtotal Gastos de Recursos Humanos','Subtotal Gastos de Comercialización y Logística','Subtotal Gastos de Mercadeo',
          'Subtotal Gastos TI+I','Otros Gastos no Operacionales',
          'Utilidad Neta','ISLR','Utilidad Neta después de ISLR'
        ];
        ```
    *   **Lógica dependiente:** La pertenencia a esta lista (`const isTotal = totales.includes(row.partida)`) determina si la celda se dibuja en negrita y su nivel de sangrado a la izquierda: `padding-left: ${isTotal ? '8px' : '20px'}`.
2.  **Mapeo de Relación Nota → Padre (`NOTES_PARENT_MAP`):**
    *   **Líneas 2769 - 2822:** Un objeto que mapea 52 cuentas de detalle (tipo nota) a su respectiva partida de agrupación de nivel superior (ej. `'Gastos de póliza HCM': 'Gastos de pasivos laborales HCM'`).
    *   **Lógica dependiente:**
        *   **Línea 2834:** `const parentName = isNote ? (NOTES_PARENT_MAP[row.partida] || '') : '';`
        *   **Línea 2835:** `const isParent = parentNames.has(row.partida);`
        *   Determina qué filas se configuran como padres colapsables (`class="parent-row"`, agregando un toggle `▶`) y cuáles se configuran como notas hijas ocultables (`class="note-row" data-parent="..." style="display:none;"`).
3.  **Lógica de Indentación/Nivel:**
    *   El frontend **no utiliza el campo `nivel` u `order`** proveniente del payload de la API para calcular la indentación CSS.
    *   En su lugar, aplica márgenes fijos basados puramente en su naturaleza hardcodeada:
        *   Notas (`isNote`): `padding-left: 34px` (Línea 2844).
        *   Totales (`isTotal`): `padding-left: 8px` (Líneas 2846, 2848).
        *   Partidas regulares: `padding-left: 20px` (Líneas 2846, 2848).

### 4. Conclusión sobre el Renderizado del Frontend
> [!IMPORTANT]
> **El renderizado NO es 100% dinámico.**
> Si bien itera sobre las filas y columnas enviadas por la API, la jerarquía visual de colapso (qué fila es hija de cuál otra), el control de visibilidad interactivo (toggle) y la diferenciación estética de los totales e indentaciones dependen críticamente de cadenas de texto y relaciones hardcodeadas en el código JavaScript (`totales` y `NOTES_PARENT_MAP`).

---

## TAREA 2: Análisis de la Estructura de Datos (Backend y BD)

### 1. Estructura `EERR_STRUCTURE` (`engine.py`)
En `engine.py` (líneas 22 - 192), la tupla se define de la siguiente manera:
*   **Campos de cada nodo:** `(partida_name, is_header, parent, bold, bg_color, level, es_nota)`
    *   `partida_name` (str): Nombre identificador único de la partida.
    *   `is_header` (bool): True si es un nodo agrupador/subtotal; False si es hoja.
    *   `parent` (None/str): Define el parentesco (siempre viene como `None` en la lista estática).
    *   `bold` (bool): Flag de formato en negrita.
    *   `bg_color` (str/None): Color de fondo en hexadecimal (ej. `'FF6AD9E8'`).
    *   `level` (int): Nivel de profundidad en el árbol jerárquico (0, 1, 2, 3).
    *   `es_nota` (bool): Indica si la fila representa un detalle desagregado colapsable en la interfaz.

*   **Tipos de Nodo y Niveles:**
    1.  **Total/Fórmula General (Nivel 0):** Ej. `Total Ingresos`, `Utilidad Bruta` (`is_header=True`, `level=0`).
    2.  **Subtotal Seccional (Nivel 1):** Ej. `Subtotal Gastos de Administración` (`is_header=True`, `level=1`).
    3.  **Grupo de Cuentas (Nivel 2):** Ej. `Gastos de seguro` (`is_header=True`, `level=2`).
    4.  **Detalle/Nota Hoja (Nivel 3):** Ej. `Ingresos por venta de mercancias` (`is_header=False`, `level=3`, `es_nota=True`).

### 2. Esquema y Estado de la Tabla `eerr_nodes`
*   **PRAGMA table_info:**
    ```sql
    CREATE TABLE eerr_nodes (
        id INTEGER PRIMARY KEY,
        parent_id INTEGER,
        nombre TEXT NOT NULL,
        nivel INTEGER NOT NULL,
        tipo TEXT,
        bold INTEGER DEFAULT 0,
        bg_color TEXT,
        display_order INTEGER
    );
    ```
*   **Confirmación de Contenido:**
    La tabla **NO está vacía**. En la base de datos activa (`ultrax_backup_pre_atomic.db`) y de pruebas (`ultrax_test.db`), esta tabla contiene **167 filas** que reproducen de forma relacional (`parent_id` apuntando a `id`) la estructura de `EERR_STRUCTURE`.
*   **Uso Actual:**
    **Completamente huérfana.** No existe ninguna referencia de consulta (queries `SELECT`), inserción o actualización sobre `eerr_nodes` en `app.py`, `db.py` o `engine.py`. El sistema calcula y renderiza basándose exclusivamente en el objeto estático en memoria `EERR_STRUCTURE` y fórmulas manuales.

### 3. Relación de `mapping_groups_v2` con "group_name"
La tabla `mapping_groups_v2` define agrupaciones uniendo códigos de Odoo con un nombre de grupo de presentación:
```sql
SELECT mg.group_name, m.partida
FROM mapping_groups_v2 mg
JOIN mapping m ON mg.odoo_code = m.odoo_code
```
En el backend (`app.py`, línea 1348), los nombres de las partidas estáticas de `EERR_STRUCTURE` se cotejan directamente mediante coincidencia de texto contra las claves generadas por `group_name`:
```python
def resolve_leaf_value(partida_name, month, data_dict):
    if partida_name in groups_v2: # groups_v2 contiene los group_name como llaves
        return sum(data_dict.get(p, {}).get(month, 0) for p in groups_v2[partida_name])
```
> [!IMPORTANT]
> Por lo tanto, el campo `group_name` actúa como puente dinámico mediante **coincidencia estricta de strings** con el primer elemento de la tupla en `EERR_STRUCTURE`.

---

## TAREA 3: Análisis de Riesgos (Nodos Nuevos vía Override)

Si un usuario agrega un nuevo nodo a través de un override en base de datos (por ejemplo, insertando un nuevo grupo en `mapping_groups_v2` o una fila en `eerr_nodes`) que **no existe en la constante estática `EERR_STRUCTURE`**, ocurrirá lo siguiente:

1.  **Omisión Total en la API (Backend):** El bucle que genera el reporte final en el backend (`eerr_completo_v2_ui_adapter`) itera estrictamente sobre `EERR_STRUCTURE`. El nuevo nodo **no aparecerá** en el JSON devuelto al cliente.
2.  **Descuadre / Pérdida de Saldos:** Al no estar en `EERR_STRUCTURE`, el nodo tampoco se sumará a los subtotales automáticos (que se calculan sumando elementos subsecuentes en la lista estática). La suma del subtotal principal no cuadrará con la suma visual de sus hojas.
3.  **Fallas de Colapso e Interacción en el Frontend:** Si por alguna vía alternativa el nodo llegara al frontend como una fila de tipo nota:
    *   No existirá en la constante JavaScript `NOTES_PARENT_MAP`.
    *   La fila se mostrará siempre visible o huérfana de lógica interactiva.
    *   Hacer clic en el toggle del nodo padre no colapsará ni expandirá este nuevo nodo.
4.  **Pérdida de Estilo Visual:** Al no figurar en el array `totales` del JS, si el nuevo nodo es un totalizador o subtotal, se renderizará con la tipografía normal (sin negrita) y con un sangrado desalineado (`padding-left: 20px` en lugar de `8px`), dañando la estética.

---

## TAREA 4: Propuesta de Diseño (Estructura Efectiva Dinámica)

Para solventar el acoplamiento estático y permitir overrides dinámicos, se propone introducir una etapa de unificación (merge) en el backend que ensamble la jerarquía final.

### 1. Firma de la Función
```python
def build_effective_structure(static_structure: list, db_nodes: list) -> list:
    """
    Combina la estructura estática por defecto con los overrides y nuevos nodos
    definidos en la base de datos para generar la jerarquía final ordenada.
    
    :param static_structure: Lista de tuplas (EERR_STRUCTURE original)
    :param db_nodes: Lista de diccionarios que representan filas de eerr_nodes en BD
    :return: Lista de diccionarios con la estructura efectiva resuelta.
    """
```

### 2. Formato de Entrada / Salida
*   **Entrada `static_structure`:**
    `[('Total Ingresos', True, None, True, 'FF6AD9E8', 0, False), ...]`
*   **Entrada `db_nodes` (ejemplo de fila de BD):**
    `[{'nombre': 'Gastos Extraordinarios', 'parent_id': 50, 'nivel': 2, 'tipo': 'subtotal', 'bold': 1, 'bg_color': 'FFFF0000', 'display_order': 250}, ...]`
*   **Salida (Estructura Efectiva Ordenada):**
    ```python
    [
      {
        "nombre": "Total Ingresos",
        "is_header": True,
        "parent_name": None,
        "bold": True,
        "bg_color": "FF6AD9E8",
        "level": 0,
        "es_nota": False
      },
      ...
    ]
    ```

### 3. Reglas de Merge e Integración
```
                                        +------------------+
                                        |  EERR_STRUCTURE  |
                                        | (Static Default) |
                                        +--------+---------+
                                                 |
                                                 v
  +------------------+  SELECT           +-------+---------+
  |  eerr_nodes BD   +------------------>|  Merge & Resolve|
  | (User Overrides) |                   |  Hierarchies    |
  +------------------+                   +-------+---------+
                                                 |
                                                 v
                                        +--------+---------+
                                        |     OUTPUT       |
                                        |Effective Structure|
                                        +------------------+
```

1.  **Resolución de Identidad (Matching):** 
    Se utiliza el campo `nombre` (normalizado sin acentos ni mayúsculas) como clave única de emparejamiento entre la definición estática y los registros de la base de datos.
2.  **Sobreescritura de Propiedades (Updates):**
    Si un nodo existe en ambas fuentes, los valores no nulos provenientes de la base de datos (`bold`, `bg_color`, `nivel`) sobreescriben a los valores por defecto definidos en la constante estática.
3.  **Inserción de Nuevos Nodos (Additions):**
    Si un nodo en `db_nodes` no existe en `static_structure`, se inserta dinámicamente:
    *   Su posición relativa dentro de la lista final se determina mediante el campo `display_order`.
    *   Su nivel (`level`) y pertenencia se validan contra el nombre de su nodo padre resuelto mediante la relación `parent_id`.
4.  **Movimiento de Nodos (Reorganization):**
    Si en la base de datos se modifica el `parent_id` de un nodo agrupador, la función de merge reubicará al nodo junto con todo su subárbol de dependencias directas e indirectas bajo el nuevo nodo destino, recalculando de manera automática el nivel de indentación (`level`) de los descendientes sumando la diferencia de niveles.
5.  **Exclusión de Nodos (Deletions):**
    Si un nodo está marcado en la base de datos como inactivo o con tipo `'deleted'`, se elimina de la estructura de salida junto con toda su descendencia jerárquica para evitar discrepancias e inconsistencias de saldos.
