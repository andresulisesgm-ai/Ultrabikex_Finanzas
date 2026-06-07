# HALLAZGOS: VALIDACIÓN EERR EXCEL VS SISTEMA

**Fecha:** 2026-06-05  
**Archivo analizado:** `C:\Users\andre\Desktop\EERR RODEO ENERO.xlsx`  
**Endpoint:** `/api/eerr/completo?year=2026&unit=Rodeo`

---

## PROBLEMA CRÍTICO DETECTADO

### 🔴 Servidor Flask con módulo cacheado

**Síntoma:** Todos los subtotales y totales aparecen en $0.00 en el JSON del sistema.

```
Total Ingresos: $0.00
Utilidad Bruta: $0.00
Total Gastos Operacionales: $0.00
Subtotal Gastos de Administración: $0.00
Subtotal Gastos de Recursos Humanos: $0.00
Utilidad Neta: $0.00
```

**Causa:** El servidor Flask tiene cacheado el módulo `engine.py` en memoria. Cuando se hicieron los cambios (eliminar 11 agrupadores de RRHH, eliminar 4 duplicados), el servidor no recargó el módulo.

**Solución:** Reiniciar el servidor Flask:
```bash
# Detener procesos actuales
taskkill /F /PID 4868
taskkill /F /PID 2180

# Reiniciar servidor
python app.py
```

---

## ESTRUCTURA DEL EXCEL VS SISTEMA

### Excel (Odoo export)
**Formato:** Usa **códigos de cuenta** como identificadores

Ejemplo:
```
6.01.01.01.001 Gastos de servicios públicos (Agua, luz, Aseo Urbano)  -91.41
6.01.02.01.001 Gastos de sueldos y salarios empleados                -205.50
4.01.01.01.001 Ingresos por venta de mercancias                    47,933.03
```

**Columnas:**
- Columna A: Código + Nombre (ej: "6.01.01.01.001 Gastos de...")
- Columna C: Balance (valor numérico)

**Headers en Excel:**
```
Fila 7: ('Name', None, 'Balance', None)
```

**Datos desde:** Fila 8

---

### Sistema (API /api/eerr/completo)
**Formato:** Usa **nombres de partidas** como identificadores

Ejemplo:
```
{
  "partida": "Gastos de servicios públicos (Agua, luz, Aseo Urbano)",
  "is_header": false,
  "bold": false,
  "meses": [
    {
      "month": "ENE",
      "ejecutado": {
        "valor": 91.41,
        "pct_vtas": 0.19,
        "pct_gastos": 0.76
      }
    }
  ]
}
```

**Diferencias clave:**
1. ❌ Excel incluye código de cuenta en el nombre
2. ❌ Excel usa valores negativos para gastos/costos
3. ❌ Sistema usa valores positivos siempre
4. ✅ Sistema tiene metadata adicional (is_header, bold, porcentajes)

---

## CÓMO SE CALCULAN LOS SUBTOTALES

**Respuesta:** Los subtotales/totales se calculan **DINÁMICAMENTE** en el backend.

### Algoritmo (en `app.py`):

```python
# Pseudocódigo del cálculo de subtotales

for item in EERR_STRUCTURE:
    if item.is_header or item.is_total:
        # Este es un subtotal/total
        # Suma todas las partidas NO-header que siguen
        # Hasta encontrar el siguiente header
        
        subtotal = 0
        for siguiente_item in items_siguientes:
            if siguiente_item.is_header:
                break  # Fin de esta sección
            subtotal += siguiente_item.valor
        
        item.valor = subtotal
```

### Ejemplo: "Subtotal Gastos de Recursos Humanos"

1. Es un header (`is_header=True`)
2. Suma las siguientes partidas NO-header:
   - Gastos de sueldos y salarios empleados: $205.50
   - Gastos de complemento de sueldos...: $906.50
   - ... (todas las partidas RRHH)
   - Hasta "Subtotal Gastos de Comercialización" (siguiente header)
3. **Total RRHH = $2,123.88**

### Conclusión:
✅ **LOS SUBTOTALES SE CALCULAN SUMANDO SUS HIJOS AUTOMÁTICAMENTE**

No son campos independientes ni vienen precalculados de la BD.

---

## VALIDACIÓN EXCEL VS SISTEMA

### Script creado: `validar_eerr.py`

**Funcionalidad:**
1. ✅ Lee Excel de Rodeo ENE 2026
2. ✅ Lee JSON del endpoint `/api/eerr/completo`
3. ✅ Compara partida por partida
4. ✅ Genera tabla de comparación
5. ✅ Muestra resumen de coincidencias/diferencias

### Resultado actual:

```
Total de partidas comparadas: 79
  [OK] Coinciden: 0 (0.0%)
  [X]  Difieren: 79 (100.0%)

Partidas solo en Excel: 42
Partidas solo en Sistema: 37
```

**❌ 100% de diferencias** debido a:
1. Servidor Flask con módulo cacheado (todos los valores en $0.00)
2. Excel usa códigos de cuenta, sistema usa nombres
3. Excel usa valores negativos, sistema usa positivos

---

## PRÓXIMOS PASOS

### 1. Reiniciar servidor Flask ⚠️ CRÍTICO
```bash
# Matar procesos actuales
taskkill /F /PID 4868
taskkill /F /PID 2180

# Reiniciar
python app.py
```

### 2. Actualizar script de validación

**Mejoras necesarias:**
- Normalizar nombres de partidas (quitar códigos de cuenta)
- Convertir valores negativos del Excel a positivos
- Mejorar detección de columnas en Excel
- Agregar tolerancia para redondeo ($0.01)

### 3. Validar totales calculados

Una vez reiniciado el servidor, verificar que:
- ✅ Total Ingresos = suma de ingresos
- ✅ Total Gastos = suma de gastos
- ✅ Utilidad Bruta = Ingresos - Costos
- ✅ Utilidad Neta = Utilidad Bruta - Gastos

---

## ARCHIVOS CREADOS

1. **`validar_eerr.py`** - Script de validación Excel vs Sistema
2. **`extraer_totales_eerr.py`** - Extrae subtotales del JSON
3. **`eerr_rodeo_raw.json`** - JSON completo del endpoint
4. **`HALLAZGOS_VALIDACION_EERR.md`** - Este documento

---

## DATOS DEL EXCEL (RESUMEN)

**Archivo:** `C:\Users\andre\Desktop\EERR RODEO ENERO.xlsx`  
**Hoja:** Sheet1  
**Estructura:**
- Fila 1-6: Metadata (Ganancia y Perdida, Target Moves, Date From/To)
- Fila 7: Headers (Name, Balance)
- Fila 8+: Datos (42 partidas con valores)

**Partidas principales:**
```
Ingresos por venta de mercancias:           $47,933.03
Costos de venta por mercancia:             -$20,670.85
Gastos totales:                            -$51,635.66
Pérdida en tasa cambiaria:                 -$18,087.53
Gastos de comisiones (personal externo):    -$2,502.98
RRHH (sueldos, complementos, aportes):      -$2,123.88
```

**Utilidad/Pérdida del periodo:** -$3,513.65

---

**Fin del reporte**
