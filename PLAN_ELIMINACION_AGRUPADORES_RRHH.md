# PLAN DE ELIMINACIÓN: AGRUPADORES OBSOLETOS DE RRHH

**Archivo:** `engine.py`  
**Sección:** Subtotal Gastos de Recursos Humanos (líneas 78-109)  
**Acción:** Eliminar 11 líneas de agrupadores genéricos obsoletos

---

## LÍNEAS A ELIMINAR

### 1. Línea 79 ❌
```python
('Gastos de sueldos y salarios empleados y directivos', False, None, False, None),
```
**Razón:** Agrupador genérico inventado. Reemplazado por:
- Línea 80: `Gastos de sueldos y salarios empleados` (partida real con datos)

---

### 2. Línea 81 ❌
```python
('Gastos de complementos empleados y directivos', False, None, False, None),
```
**Razón:** Agrupador genérico inventado. Reemplazado por:
- Línea 82: `Gastos de complemento de sueldos y salarios empleados` (partida real)
- Línea 83: `Gastos de Bono de alimentación empleados` (partida real)

---

### 3. Línea 84 ❌
```python
('Gastos de personal externo', False, None, False, None),
```
**Razón:** Agrupador genérico inventado. Reemplazado por:
- Línea 85: `Gastos de servicios de personal externo` (partida real con datos)

---

### 4. Línea 86 ❌
```python
('Gastos de pasivos laborales vacaciones', False, None, False, None),
```
**Razón:** Agrupador genérico inventado. Reemplazado por partidas específicas:
- Línea 87: `Gastos de vacaciones empleados`
- Línea 88: `Gastos de complemento de vacaciones empleados`
- Línea 89: `Gastos de bono vacacional empleados`
- Línea 90: `Gastos de complemento bono vacacional empleados`

---

### 5. Línea 91 ❌
```python
('Gastos de pasivos laborales utilidades', False, None, False, None),
```
**Razón:** Agrupador genérico sin partidas reales asociadas. Sin datos en el sistema.

---

### 6. Línea 92 ❌
```python
('Gastos de pasivos laborales prestaciones e intereses', False, None, False, None),
```
**Razón:** Agrupador genérico inventado. Reemplazado por partidas específicas:
- Línea 93: `Gastos de prestaciones sociales empleados`
- Línea 94: `Gastos de intereses sobres prestaciones sociales empleados`

---

### 7. Línea 95 ❌
```python
('Gastos de pasivos laborales aportes', False, None, False, None),
```
**Razón:** Agrupador genérico inventado. Reemplazado por partidas específicas:
- Línea 96: `Gastos de aporte patronal IVSS`
- Línea 97: `Gastos de aporte patronal SPF`
- Línea 98: `Gastos de aporte patronal FAOV`
- Línea 99: `Gastos de aporte patronal INCES`

---

### 8. Línea 100 ❌
```python
('Gastos de pasivos laborales bono de guardería', False, None, False, None),
```
**Razón:** Agrupador genérico sin partidas reales asociadas. Sin datos en el sistema.

---

### 9. Línea 101 ❌
```python
('Gastos de pasivos laborales HCM', False, None, False, None),
```
**Razón:** Agrupador genérico inventado. Reemplazado por:
- Línea 102: `Gastos de póliza HCM` (partida real con datos)

---

### 10. Línea 105 ❌
```python
('Gastos de salud y seguridad laboral fiestas y agasajos', False, None, False, None),
```
**Razón:** Agrupador genérico inventado. Reemplazado por:
- Línea 106: `Gastos de fiestas y agasajos al personal` (partida real con datos)

---

### 11. Línea 107 ❌
```python
('Otros gastos de personal', False, None, False, None),
```
**Razón:** Agrupador genérico inventado. Reemplazado por partidas específicas:
- Línea 108: `Gastos de donaciones y obsequios al personal`
- Línea 109: `Gastos de transporte del personal` (con datos)

---

## RESUMEN DE ELIMINACIONES

| # | Línea | Partida a eliminar | Motivo |
|---|-------|-------------------|--------|
| 1 | 79 | Gastos de sueldos y salarios empleados y directivos | Agrupador genérico |
| 2 | 81 | Gastos de complementos empleados y directivos | Agrupador genérico |
| 3 | 84 | Gastos de personal externo | Agrupador genérico |
| 4 | 86 | Gastos de pasivos laborales vacaciones | Agrupador genérico |
| 5 | 91 | Gastos de pasivos laborales utilidades | Sin datos |
| 6 | 92 | Gastos de pasivos laborales prestaciones e intereses | Agrupador genérico |
| 7 | 95 | Gastos de pasivos laborales aportes | Agrupador genérico |
| 8 | 100 | Gastos de pasivos laborales bono de guardería | Sin datos |
| 9 | 101 | Gastos de pasivos laborales HCM | Agrupador genérico |
| 10 | 105 | Gastos de salud y seguridad laboral fiestas y agasajos | Agrupador genérico |
| 11 | 107 | Otros gastos de personal | Agrupador genérico |

**Total:** 11 líneas a eliminar

---

## ESTRUCTURA RRHH DESPUÉS DE LA ELIMINACIÓN

```python
    ('Subtotal Gastos de Recursos Humanos', True, None, True, None),          # LÍNEA 78 - HEADER
    ('Gastos de sueldos y salarios empleados', False, None, False, None),     # LÍNEA 79 (nueva)
    ('Gastos de complemento de sueldos y salarios empleados', False, None, False, None),
    ('Gastos de Bono de alimentación empleados', False, None, False, None),
    ('Gastos de servicios de personal externo', False, None, False, None),
    ('Gastos de vacaciones empleados', False, None, False, None),
    ('Gastos de complemento de vacaciones empleados', False, None, False, None),
    ('Gastos de bono vacacional empleados', False, None, False, None),
    ('Gastos de complemento bono vacacional empleados', False, None, False, None),
    ('Gastos de prestaciones sociales empleados', False, None, False, None),
    ('Gastos de intereses sobres prestaciones sociales empleados', False, None, False, None),
    ('Gastos de aporte patronal IVSS', False, None, False, None),
    ('Gastos de aporte patronal SPF', False, None, False, None),
    ('Gastos de aporte patronal FAOV', False, None, False, None),
    ('Gastos de aporte patronal INCES', False, None, False, None),
    ('Gastos de póliza HCM', False, None, False, None),
    ('Gastos de salud y seguridad laboral', False, None, False, None),
    ('Gastos de salud y seguridad laboral dotación', False, None, False, None),
    ('Gastos de fiestas y agasajos al personal', False, None, False, None),
    ('Gastos de donaciones y obsequios al personal', False, None, False, None),
    ('Gastos de transporte del personal', False, None, False, None),
    ('Subtotal Gastos de Comercialización y Logistica', True, None, True, None),  # SIGUIENTE SECCIÓN
```

**Antes:** 32 líneas en sección RRHH (1 header + 31 partidas)  
**Después:** 21 líneas en sección RRHH (1 header + 20 partidas)  
**Reducción:** 11 líneas vacías eliminadas

---

## IMPACTO EN EERR_STRUCTURE

- **Antes:** 112 partidas (no-headers)
- **Después:** 101 partidas (no-headers)
- **Cobertura:** Se mantiene en 100% (las partidas con datos reales permanecen)
- **Total RRHH:** Se mantiene en $2,123.88 (sin cambios en cálculos)

---

## VERIFICACIÓN POST-ELIMINACIÓN

Después de la eliminación se debe verificar:
1. ✅ Cobertura sigue en 100%
2. ✅ Total RRHH Rodeo ENE 2026 sigue siendo $2,123.88
3. ✅ No hay líneas con $0.00 excepto partidas reales sin datos en ese mes
4. ✅ Frontend muestra solo 21 líneas en RRHH (vs 32 actuales)

---

**¿Apruebas la eliminación de estas 11 líneas?**
