# PLAN DE INSERCIÓN: 28 PARTIDAS FALTANTES EN EERR_STRUCTURE

## RESUMEN
- **28 partidas** con datos reales no aparecen en EERR
- **Impacto:** $149,983.62 no se muestra en Estado de Resultados
- **Acción:** Insertar en posiciones jerárquicas correctas

---

## BLOQUE 1: INGRESOS POR VENTA DE MERCANCÍA
**Posición:** Después de línea 26 (`Subtotal Ingresos por Venta de Mercancia`)

### Partidas a insertar:
```python
# LÍNEA 27 (ya existe): ('Ingresos por venta de mercancía', False, None, False, None),
```

**PROBLEMA DETECTADO:** Ya existe una partida `'Ingresos por venta de mercancía'` (con tilde) en línea 27, pero en la BD está como `'Ingresos por venta de mercancias'` (sin tilde, plural).

**INSERCIÓN:**
```python
# Después de línea 27:
('Ingresos por venta de mercancias', False, None, False, None),  # NUEVA (sin tilde, plural) - $91,964.11
```

---

## BLOQUE 2: INGRESOS POR TALLER
**Posición:** Después de línea 36 (`Subtotal Ingresos por Taller`)

### Partidas a insertar:
```python
# LÍNEA 37 (ya existe): ('Ingresos por taller', False, None, False, None),
```

**PROBLEMA DETECTADO:** Ya existe `'Ingresos por taller'` (minúscula), pero en la BD está como `'Ingresos por Taller'` (mayúscula).

**INSERCIÓN:**
```python
# Después de línea 37:
('Ingresos por Taller', False, None, False, None),  # NUEVA (mayúscula) - $692.10
```

---

## BLOQUE 3: COSTOS DE VENTA
**Posición:** Después de línea 39 (`Subtotal Costo de Ventas por Mercancia`)

### Partidas a insertar:
```python
# LÍNEA 40 (ya existe): ('Costo de venta por mercancía', False, None, False, None),
```

**PROBLEMA DETECTADO:** Ya existe `'Costo de venta por mercancía'` (con tilde, singular), pero en la BD está como:
- `'Costos de venta por mercancia'` (sin tilde, plural)
- `'Costos de venta por servicios del café'`

**INSERCIÓN:**
```python
# Después de línea 40:
('Costos de venta por mercancia', False, None, False, None),  # NUEVA (plural, sin tilde) - $42,006.98
```

**Posición:** Después de línea 42 (`Costo de venta por servicio del café`)

**INSERCIÓN:**
```python
# Después de línea 42:
('Costos de venta por servicios del café', False, None, False, None),  # NUEVA (plural "Costos") - $621.71
```

---

## BLOQUE 4: GASTOS DE RECURSOS HUMANOS
**Posición:** Después de línea 78 (`Subtotal Gastos de Recursos Humanos`)

### Partidas a insertar (en orden jerárquico):

**4.1. Sueldos y salarios (después de línea 79)**
```python
# LÍNEA 79 (ya existe - AGRUPADOR): ('Gastos de sueldos y salarios empleados y directivos', False, None, False, None),
```

**INSERCIÓN:**
```python
# Después de línea 79:
('Gastos de sueldos y salarios empleados', False, None, False, None),  # NUEVA - $541.66
```

**4.2. Complementos (después de línea 80)**
```python
# LÍNEA 80 (ya existe - AGRUPADOR): ('Gastos de complementos empleados y directivos', False, None, False, None),
```

**INSERCIÓN:**
```python
# Después de línea 80:
('Gastos de complemento de sueldos y salarios empleados', False, None, False, None),  # NUEVA - $3,947.35
('Gastos de Bono de alimentación empleados', False, None, False, None),  # NUEVA - $850.54
```

**4.3. Personal externo (después de línea 81)**
```python
# LÍNEA 81 (ya existe - AGRUPADOR): ('Gastos de personal externo', False, None, False, None),
```

**INSERCIÓN:**
```python
# Después de línea 81:
('Gastos de servicios de personal externo', False, None, False, None),  # NUEVA - $409.70
```

**4.4. Vacaciones (después de línea 82)**
```python
# LÍNEA 82 (ya existe - AGRUPADOR): ('Gastos de pasivos laborales vacaciones', False, None, False, None),
```

**INSERCIÓN:**
```python
# Después de línea 82:
('Gastos de vacaciones empleados', False, None, False, None),  # NUEVA - $34.53
('Gastos de complemento de vacaciones empleados', False, None, False, None),  # NUEVA - $91.73
('Gastos de bono vacacional empleados', False, None, False, None),  # NUEVA - $23.45
('Gastos de complemento bono vacacional empleados', False, None, False, None),  # NUEVA - $56.76
```

**4.5. Prestaciones e intereses (después de línea 84)**
```python
# LÍNEA 84 (ya existe - AGRUPADOR): ('Gastos de pasivos laborales prestaciones e intereses', False, None, False, None),
```

**INSERCIÓN:**
```python
# Después de línea 84:
('Gastos de prestaciones sociales empleados', False, None, False, None),  # NUEVA - $15.56
('Gastos de intereses sobres prestaciones sociales empleados', False, None, False, None),  # NUEVA - $0.76
```

**4.6. Aportes patronales (después de línea 85)**
```python
# LÍNEA 85 (ya existe - AGRUPADOR): ('Gastos de pasivos laborales aportes', False, None, False, None),
```

**INSERCIÓN:**
```python
# Después de línea 85:
('Gastos de aporte patronal IVSS', False, None, False, None),  # NUEVA - $5.47
('Gastos de aporte patronal SPF', False, None, False, None),  # NUEVA - $2.20
('Gastos de aporte patronal FAOV', False, None, False, None),  # NUEVA - $15.19
('Gastos de aporte patronal INCES', False, None, False, None),  # NUEVA - $30.12
```

**4.7. Póliza HCM (después de línea 87)**
```python
# LÍNEA 87 (ya existe - AGRUPADOR): ('Gastos de pasivos laborales HCM', False, None, False, None),
```

**INSERCIÓN:**
```python
# Después de línea 87:
('Gastos de póliza HCM', False, None, False, None),  # NUEVA - $296.10
```

**4.8. Fiestas y agasajos (después de línea 90)**
```python
# LÍNEA 90 (ya existe - AGRUPADOR): ('Gastos de salud y seguridad laboral fiestas y agasajos', False, None, False, None),
```

**INSERCIÓN:**
```python
# Después de línea 90:
('Gastos de fiestas y agasajos al personal', False, None, False, None),  # NUEVA - $592.24
```

**4.9. Otros gastos de personal (después de línea 91)**
```python
# LÍNEA 91 (ya existe - AGRUPADOR): ('Otros gastos de personal', False, None, False, None),
```

**INSERCIÓN:**
```python
# Después de línea 91:
('Gastos de donaciones y obsequios al personal', False, None, False, None),  # NUEVA - $92.37
('Gastos de transporte del personal', False, None, False, None),  # NUEVA - $657.77
```

---

## BLOQUE 5: GASTOS DE COMERCIALIZACIÓN Y LOGÍSTICA
**Posición:** Después de línea 92 (`Subtotal Gastos de Comercialización y Logistica`)

**5.1. Fletes y envíos (después de línea 94)**
```python
# LÍNEA 94 (ya existe - AGRUPADOR): ('Gastos de fletes y envios no asociados al costo', False, None, False, None),
```

**INSERCIÓN:**
```python
# Después de línea 94:
('Gastos de envíos/fletes en ventas y compras no incluidas en el costo', False, None, False, None),  # NUEVA - $119.50
```

---

## BLOQUE 6: GASTOS DE MERCADEO
**Posición:** Después de línea 103 (`Gastos de medios publicitarios`)

**INSERCIÓN:**
```python
# Después de línea 103:
('Gastos de impresiones de material gráfico', False, None, False, None),  # NUEVA - $204.00
```

---

## BLOQUE 7: COMISIONES POR VENTAS
**Posición:** Después de línea 114 (`Utilidad antes de Comisiones por Ventas`)

**7.1. Comisiones empleados (después de línea 115)**
```python
# LÍNEA 115 (ya existe - AGRUPADOR): ('Gastos de comisiones por ventas', False, None, False, None),
```

**INSERCIÓN:**
```python
# Después de línea 115:
('Gastos de comisiones empleados', False, None, False, None),  # NUEVA - $1,744.27
```

**7.2. Comisiones taller (después de línea 116)**
```python
# LÍNEA 116 (ya existe - AGRUPADOR): ('Gastos de comisiones por ventas taller', False, None, False, None),
```

**INSERCIÓN:**
```python
# Después de línea 116:
('Gastos de comisiones empleados del taller', False, None, False, None),  # NUEVA - $305.47
```

**7.3. Comisiones personal externo (después de línea 116)**
```python
# Después de línea 116 (nueva, no tiene agrupador):
('Gastos de comisiones por venta de personal externo', False, None, False, None),  # NUEVA - $4,150.54
```

---

## BLOQUE 8: OTROS GASTOS NO OPERACIONALES
**Posición:** Después de línea 127 (`Faltante y deterioro de inventarios`)

**INSERCIÓN:**
```python
# Después de línea 127:
('Deterioro de inventarios', False, None, False, None),  # NUEVA - $511.44
```

---

## RESUMEN DE INSERCIONES

| Bloque | Línea base | Partidas a insertar | Monto total |
|--------|-----------|---------------------|-------------|
| Ingresos Mercancía | 27 | 1 | $91,964.11 |
| Ingresos Taller | 37 | 1 | $692.10 |
| Costos | 40-42 | 2 | $42,628.69 |
| RRHH | 79-91 | 17 | $7,019.18 |
| Comercialización | 94 | 1 | $119.50 |
| Mercadeo | 103 | 1 | $204.00 |
| Comisiones Ventas | 115-116 | 3 | $6,200.28 |
| No Operacionales | 127 | 1 | $511.44 |
| **TOTAL** | | **28** | **$149,983.62** |

---

## NOTAS IMPORTANTES

1. **Problema de tildes/mayúsculas:** Muchas partidas ya existen en EERR_STRUCTURE pero con diferencias mínimas de escritura (tildes, mayúsculas/minúsculas, singular/plural). Las nuevas inserciones usan el nombre EXACTO de la base de datos.

2. **Partidas agrupadas:** Varias de estas partidas deberían estar agrupadas bajo los nombres genéricos existentes, pero actualmente el sistema busca match EXACTO de nombre.

3. **Alternativa:** En lugar de duplicar nombres similares, podríamos usar el sistema de grupos para mapear variantes al nombre canónico.

---

## APROBACIÓN REQUERIDA

¿Procedo con estas 28 inserciones en las posiciones indicadas?
