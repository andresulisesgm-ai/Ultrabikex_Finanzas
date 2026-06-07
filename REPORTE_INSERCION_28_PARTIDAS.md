# REPORTE: INSERCIÓN DE 28 PARTIDAS EN EERR_STRUCTURE

**Fecha:** 2026-06-05  
**Archivo modificado:** `engine.py`  
**Estado:** ✅ COMPLETADO

---

## RESUMEN EJECUTIVO

Se insertaron **28 partidas faltantes** en `EERR_STRUCTURE` para garantizar que todos los datos financieros aparezcan en el Estado de Resultados.

### Impacto:
- **Antes:** $149,983.62 en transacciones no se mostraban en EERR
- **Después:** 100% de cobertura - $191,857.23 total cubierto
- **Partidas totales en EERR_STRUCTURE:** 116 (no-headers)
- **Cobertura directa:** 56 partidas ($187,023.38)
- **Cobertura vía grupos:** 10 partidas ($4,833.85)

---

## INSERCIONES REALIZADAS

### 1. INGRESOS (2 partidas - $92,656.21)

**Ingresos por Venta de Mercancía:**
- Línea insertada: `('Ingresos por venta de mercancias', False, None, False, None)`
- Monto: $91,964.11
- Posición: Después de línea 27

**Ingresos por Taller:**
- Línea insertada: `('Ingresos por Taller', False, None, False, None)`
- Monto: $692.10
- Posición: Después de línea 38

---

### 2. COSTOS (2 partidas - $42,628.69)

**Costos de Venta por Mercancía:**
- Línea insertada: `('Costos de venta por mercancia', False, None, False, None)`
- Monto: $42,006.98
- Posición: Después de línea 42

**Costos de Venta por Servicios:**
- Línea insertada: `('Costos de venta por servicios del café', False, None, False, None)`
- Monto: $621.71
- Posición: Después de línea 44

---

### 3. GASTOS DE RECURSOS HUMANOS (17 partidas - $7,019.18)

#### 3.1. Sueldos y Salarios
- `('Gastos de sueldos y salarios empleados', False, None, False, None)` - $541.66

#### 3.2. Complementos
- `('Gastos de complemento de sueldos y salarios empleados', False, None, False, None)` - $3,947.35
- `('Gastos de Bono de alimentación empleados', False, None, False, None)` - $850.54

#### 3.3. Personal Externo
- `('Gastos de servicios de personal externo', False, None, False, None)` - $409.70

#### 3.4. Vacaciones (4 partidas)
- `('Gastos de vacaciones empleados', False, None, False, None)` - $34.53
- `('Gastos de complemento de vacaciones empleados', False, None, False, None)` - $91.73
- `('Gastos de bono vacacional empleados', False, None, False, None)` - $23.45
- `('Gastos de complemento bono vacacional empleados', False, None, False, None)` - $56.76

#### 3.5. Prestaciones e Intereses
- `('Gastos de prestaciones sociales empleados', False, None, False, None)` - $15.56
- `('Gastos de intereses sobres prestaciones sociales empleados', False, None, False, None)` - $0.76

#### 3.6. Aportes Patronales (4 partidas)
- `('Gastos de aporte patronal IVSS', False, None, False, None)` - $5.47
- `('Gastos de aporte patronal SPF', False, None, False, None)` - $2.20
- `('Gastos de aporte patronal FAOV', False, None, False, None)` - $15.19
- `('Gastos de aporte patronal INCES', False, None, False, None)` - $30.12

#### 3.7. Póliza HCM
- `('Gastos de póliza HCM', False, None, False, None)` - $296.10

#### 3.8. Fiestas y Agasajos
- `('Gastos de fiestas y agasajos al personal', False, None, False, None)` - $592.24

#### 3.9. Otros
- `('Gastos de donaciones y obsequios al personal', False, None, False, None)` - $92.37
- `('Gastos de transporte del personal', False, None, False, None)` - $657.77

---

### 4. GASTOS DE COMERCIALIZACIÓN (1 partida - $119.50)

- `('Gastos de envíos/fletes en ventas y compras no incluidas en el costo', False, None, False, None)`

---

### 5. GASTOS DE MERCADEO (1 partida - $204.00)

- `('Gastos de impresiones de material gráfico', False, None, False, None)`

---

### 6. COMISIONES POR VENTAS (3 partidas - $6,200.28)

- `('Gastos de comisiones empleados', False, None, False, None)` - $1,744.27
- `('Gastos de comisiones empleados del taller', False, None, False, None)` - $305.47
- `('Gastos de comisiones por venta de personal externo', False, None, False, None)` - $4,150.54

---

### 7. OTROS GASTOS NO OPERACIONALES (1 partida - $511.44)

- `('Deterioro de inventarios', False, None, False, None)`

---

## VERIFICACIÓN FINAL

```
[ESTADISTICAS]
  Partidas en financials: 66
  Partidas en EERR_STRUCTURE (no-headers): 116
  Grupos definidos: 7
  Partidas agrupadas: 31

[COBERTURA]
  [OK] Con cobertura directa: 56
  [OK] Con cobertura via grupos: 10
  [X]  SIN COBERTURA: 0

[IMPACTO FINANCIERO]
  Cubierto directo: $187,023.38
  Cubierto via grupos: $4,833.85
  Sin cobertura: $0.00
  Total general: $191,857.23
  % Cobertura: 100.0%

[SUCCESS] 100% DE COBERTURA
```

---

## NOTAS TÉCNICAS

### Problema de variaciones de nombres
Muchas partidas ya existían en EERR_STRUCTURE pero con pequeñas diferencias ortográficas:
- **Tildes:** `mercancía` vs `mercancia`
- **Mayúsculas:** `taller` vs `Taller`
- **Singular/Plural:** `Costo` vs `Costos`

**Solución aplicada:** Se insertaron las partidas con el nombre **EXACTO** que aparece en la base de datos para garantizar el match correcto.

### Alternativa futura
En lugar de duplicar nombres similares, se podría usar el sistema de `mapping_groups` para mapear variantes ortográficas al nombre canónico, evitando duplicación.

---

## ARCHIVOS MODIFICADOS

1. **engine.py**
   - EERR_STRUCTURE: De 119 líneas a 147 líneas
   - 28 nuevas partidas insertadas en posiciones jerárquicas correctas

2. **Archivos de verificación creados:**
   - `plan_insercion_eerr.md` - Plan detallado de inserción
   - `verificar_cobertura_final.py` - Script de verificación
   - `REPORTE_INSERCION_28_PARTIDAS.md` - Este reporte

---

## RESULTADO FINAL

✅ **100% DE COBERTURA ALCANZADA**

Todas las 66 partidas presentes en la tabla `financials` ahora tienen representación en `EERR_STRUCTURE`, ya sea:
- Directamente (56 partidas)
- Vía grupos (10 partidas agrupadas en 7 grupos)

Los $149,983.62 que no aparecían en el Estado de Resultados ahora se muestran correctamente.

---

**Fin del reporte**
