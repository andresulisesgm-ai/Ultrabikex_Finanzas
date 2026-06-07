# ANÁLISIS: Problema de Subtotales en /api/eerr/completo

**Fecha:** 2026-06-05  
**Endpoint:** `/api/eerr/completo`  
**Problema:** Todos los subtotales y totales retornan $0

---

## 🔴 CÓDIGO ACTUAL (app.py líneas 906-923)

```python
# Construir filas según EERR_STRUCTURE
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
```

### ❌ PROBLEMA:

1. **Headers/Totales no se calculan:** Si `partida_name` es un header como "Total Ingresos", NO está en `groups` y NO hay una partida con ese nombre exacto, entonces `matching` queda **vacío** → valores = $0

2. **No hay lógica de jerarquía:** El código no entiende que debe sumar las partidas hijas entre dos headers

3. **Solo funciona para:**
   - Partidas individuales con nombre exacto
   - Grupos definidos en `mapping_groups`

---

## 📊 LÓGICA REQUERIDA

### Cálculo de Subtotales Jerárquicos:

Para cada header (is_header=True), el subtotal debe ser:
**Suma de todas las partidas NO-header desde este header hasta el siguiente header**

### Ejemplo: "Subtotal Gastos de Recursos Humanos"

```python
EERR_STRUCTURE = [
    ...
    ('Subtotal Gastos de Recursos Humanos', True, None, True, None),  # Header
    ('Gastos de sueldos y salarios empleados', False, None, False, None),  # +205.50
    ('Gastos de complemento de sueldos...', False, None, False, None),     # +906.50
    ('Gastos de Bono de alimentación...', False, None, False, None),       # +240.00
    ...
    ('Gastos de transporte del personal', False, None, False, None),       # +241.50
    ('Subtotal Gastos de Comercialización...', True, None, True, None),   # STOP aquí
    ...
]
```

**Resultado esperado:** $2,123.88 (suma de las 12 partidas)

---

## 🎯 TOTALES ESPECIALES

Además de los subtotales jerárquicos, hay totales con lógica específica:

### 1. Total Ingresos
```python
Total Ingresos = suma de todas las partidas 4.xx (operativos + no operativos)
```

### 2. Total Costo de Ventas
```python
Total Costo de Ventas = suma de todas las partidas 5.xx
```

### 3. Utilidad Bruta
```python
Utilidad Bruta = Total Ingresos Operativos - Total Costo de Ventas
```

### 4. Total Gastos Operacionales
```python
Total Gastos Operacionales = suma de todos los subtotales de gastos 6.01.xx
```

### 5. Utilidad antes de Comisiones
```python
Utilidad antes de Comisiones = Utilidad Bruta - Total Gastos Operacionales
```

### 6. Utilidad después de Comisiones
```python
Utilidad después de Comisiones = Utilidad antes de Comisiones - Gastos de comisiones
```

### 7. Otros Gastos no Operacionales
```python
Otros Gastos no Operacionales = suma de partidas 6.02.xx
```

### 8. Otros Ingresos no Operacionales
```python
Otros Ingresos no Operacionales = suma de partidas 4.02.xx
```

### 9. Utilidad Neta
```python
Utilidad Neta = Utilidad después de Comisiones - Otros Gastos + Otros Ingresos
```

---

## 💡 SOLUCIÓN PROPUESTA

### Enfoque 1: Cálculo Jerárquico (para subtotales)

```python
def calcular_subtotal_jerarquico(eerr_structure, index, by_partida, month, ing_p, cos_p, gas_p, groups, grouped_partidas):
    """
    Calcula el subtotal de un header sumando todas las partidas
    desde este index hasta el siguiente header.
    """
    if not eerr_structure[index][1]:  # No es header
        return 0
    
    total = 0
    i = index + 1
    
    while i < len(eerr_structure):
        item = eerr_structure[i]
        partida_name = item[0]
        is_header = item[1]
        
        if is_header:  # Encontramos el siguiente header, parar
            break
        
        # Buscar partidas que coincidan con este nombre
        if partida_name in groups:
            matching = groups[partida_name]
        else:
            matching = [p for p in (ing_p | cos_p | gas_p)
                        if p.lower() == partida_name.lower()
                        and p not in grouped_partidas]
        
        # Sumar valores de este mes
        for p in matching:
            total += by_partida.get(p, {}).get(month, 0)
        
        i += 1
    
    return total
```

### Enfoque 2: Totales Especiales (para cálculos con lógica propia)

```python
def calcular_total_especial(partida_name, by_partida, month, ing_p, cos_p, gas_p, subtotales):
    """
    Calcula totales especiales con lógica específica.
    """
    if partida_name == 'Total Ingresos':
        # Suma de todas las partidas 4.xx
        return sum(by_partida.get(p, {}).get(month, 0) for p in ing_p)
    
    elif partida_name == 'Total Costo de Ventas':
        # Suma de todas las partidas 5.xx
        return sum(by_partida.get(p, {}).get(month, 0) for p in cos_p)
    
    elif partida_name == 'Utilidad Bruta':
        # Total Ingresos - Total Costos
        return subtotales.get('Total Ingresos', 0) - subtotales.get('Total Costo de Ventas', 0)
    
    elif partida_name == 'Total Gastos Operacionales':
        # Suma de subtotales de gastos operativos
        return (subtotales.get('Subtotal Gastos de Administración', 0) +
                subtotales.get('Subtotal Gastos de Recursos Humanos', 0) +
                subtotales.get('Subtotal Gastos de Comercialización y Logistica', 0) +
                subtotales.get('Subtotal Gastos de Mercadeo', 0) +
                subtotales.get('Subtotal Gastos de Tecnología, Innovación e Investigación', 0))
    
    elif partida_name == 'Utilidad antes de Comisiones por Ventas':
        return subtotales.get('Utilidad Bruta', 0) - subtotales.get('Total Gastos Operacionales', 0)
    
    elif partida_name == 'Utilidad después de Comisiones por Ventas':
        # Requiere calcular suma de comisiones
        comisiones = (subtotales.get('Gastos de comisiones por ventas', 0) +
                     subtotales.get('Gastos de comisiones por ventas taller', 0))
        return subtotales.get('Utilidad antes de Comisiones por Ventas', 0) - comisiones
    
    elif partida_name == 'Utilidad Neta':
        # Utilidad después de Comisiones - Otros Gastos + Otros Ingresos
        otros_gastos = subtotales.get('Otros Gastos no Operacionales', 0)
        otros_ingresos = subtotales.get('Otros Ingresos no Operacionales', 0)
        return subtotales.get('Utilidad después de Comisiones por Ventas', 0) - otros_gastos + otros_ingresos
    
    return None  # No es un total especial
```

---

## 🔧 IMPLEMENTACIÓN

### Algoritmo de dos pasadas:

**Pasada 1:** Calcular subtotales jerárquicos
- Recorrer EERR_STRUCTURE
- Para cada header, sumar partidas hijas
- Guardar en diccionario `subtotales`

**Pasada 2:** Calcular totales especiales
- Usar `subtotales` de pasada 1
- Aplicar lógicas específicas (Utilidad Bruta, etc.)
- Actualizar `subtotales`

**Pasada 3:** Generar output final
- Usar valores calculados para headers
- Usar valores directos para partidas individuales

---

## ✅ CAMBIOS NECESARIOS EN app.py

### Ubicación: Función `eerr_completo()` líneas 906-1030

**Cambio principal:**
1. Antes del loop principal, hacer pre-cálculo de subtotales
2. En el loop, usar subtotales pre-calculados si es header
3. Si no es header, usar lógica actual (buscar partidas)

### Código propuesto:

```python
# ANTES DEL LOOP (después de línea 905)
# Pre-calcular subtotales para todos los meses
subtotales_por_mes = {}
for m in MONTHS:
    subtotales_por_mes[m] = calcular_todos_subtotales(
        EERR_STRUCTURE, by_partida, m, ing_p, cos_p, gas_p, 
        groups, grouped_partidas
    )

# EN EL LOOP (reemplazar líneas 915-922)
if is_header:
    # Es un header: usar subtotal pre-calculado
    matching_values = {m: subtotales_por_mes[m].get(partida_name, 0) for m in MONTHS}
else:
    # Es una partida individual: usar lógica actual
    if partida_name in groups:
        matching = groups[partida_name]
    else:
        matching = [p for p in (ing_p | cos_p | gas_p)
                    if p.lower() == partida_name.lower()
                    and p not in grouped_partidas]
```

---

## 📝 NOTAS IMPORTANTES

1. **Orden de cálculo importa:** 
   - Primero subtotales básicos
   - Luego totales que usan subtotales
   - Finalmente utilidades que usan totales

2. **Dependencias:**
   - "Utilidad Bruta" depende de "Total Ingresos" y "Total Costo de Ventas"
   - "Utilidad Neta" depende de múltiples subtotales previos

3. **Grupos vs Headers:**
   - Grupos (`mapping_groups`): Suma de partidas específicas
   - Headers jerárquicos: Suma de partidas hasta siguiente header
   - Totales especiales: Lógica custom (suma de subtotales, restas, etc.)

---

## 🎯 RESULTADO ESPERADO

Después de implementar, para Rodeo ENE 2026:

```
Total Ingresos:                              $48,122.01
Total Costo de Ventas:                       $20,670.85
Utilidad Bruta:                              $27,451.16
Subtotal Gastos de Administración:           $ 7,663.81
Subtotal Gastos de Recursos Humanos:         $ 2,123.88
Subtotal Gastos de Comercialización:         $   119.50
Subtotal Gastos de Mercadeo:                 $   212.96
Total Gastos Operacionales:                  $10,120.15
Utilidad antes de Comisiones:                $17,330.01
Gastos de comisiones:                        $ 3,337.60
Utilidad después de Comisiones:              $13,992.41
Otros Gastos no Operacionales:               $18,109.17
Otros Ingresos no Operacionales:             $   184.16
Utilidad Neta:                               -$ 3,932.60
```

---

**Siguiente paso:** Implementar las funciones de cálculo en `app.py`

---

**Fin del análisis**
