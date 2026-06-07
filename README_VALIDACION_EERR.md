# Sistema de Validación EERR

Script automatizado para validar Estados de Resultados comparando archivos Excel (Odoo) contra el sistema web.

---

## 🚀 INICIO RÁPIDO

### Validación simple:
```bash
python validar_eerr.py --excel "EERR RODEO ENERO.xlsx" --unit Rodeo
```

### Validación detallada:
```bash
python validar_eerr.py --excel "EERR RODEO ENERO.xlsx" --unit Rodeo --verbose
```

### Guardar reporte:
```bash
python validar_eerr.py --excel "EERR RODEO ENERO.xlsx" --unit Rodeo --save reporte.json
```

---

## 📋 REQUISITOS PREVIOS

1. **Python 3.x instalado**
2. **Servidor Flask corriendo:**
   ```bash
   python app.py
   ```
3. **Librería openpyxl:**
   ```bash
   pip install openpyxl
   ```

---

## 🔧 USO DEL SCRIPT

### Sintaxis completa:
```bash
python validar_eerr.py \
    --excel "ruta/al/archivo.xlsx" \
    --unit "NombreUnidad" \
    [--year 2026] \
    [--month ENE] \
    [--server http://localhost:5000] \
    [--verbose] \
    [--save archivo.json]
```

### Parámetros:

| Parámetro | Requerido | Default | Descripción |
|-----------|-----------|---------|-------------|
| `--excel` | ✅ Sí | - | Ruta al archivo Excel |
| `--unit` | ✅ Sí | - | Nombre de la unidad |
| `--year` | ❌ No | 2026 | Año a validar |
| `--month` | ❌ No | ENE | Mes a validar |
| `--server` | ❌ No | http://localhost:5000 | URL del servidor |
| `--verbose` o `-v` | ❌ No | false | Mostrar todas las partidas |
| `--save` o `-s` | ❌ No | - | Guardar reporte JSON |

---

## 📝 EJEMPLOS DE USO

### 1. Validación básica (solo resumen)
```bash
python validar_eerr.py --excel "C:\Desktop\EERR RODEO.xlsx" --unit Rodeo
```

**Output:**
```
Total partidas comparadas: 41
  [OK] Coinciden: 35 (85.4%)
  [X]  Difieren: 6 (14.6%)

Suma total Excel: $99,757.67
Suma total Sistema: $99,757.67
Diferencia total: $0.00

[SUCCESS] TODOS LOS VALORES COINCIDEN!
```

### 2. Validación detallada (todas las partidas)
```bash
python validar_eerr.py --excel "EERR RODEO.xlsx" --unit Rodeo --verbose
```

**Output adicional:**
```
#    Partida                                              Excel         Sistema         Diff Status
1    Costos de venta por mercancia                 $ 20,670.85 $ 20,670.85 $      0.00  [OK]
2    Gastos de sueldos y salarios empleados        $    205.50 $    205.50 $      0.00  [OK]
...
```

### 3. Validar mes específico
```bash
python validar_eerr.py --excel "EERR FEB.xlsx" --unit Terracota --year 2026 --month FEB
```

### 4. Guardar reporte para auditoría
```bash
python validar_eerr.py --excel "EERR.xlsx" --unit Altamira --save auditoria_altamira.json
```

El archivo JSON contendrá:
```json
{
  "metadata": {
    "fecha": "2026-06-05T22:15:30",
    "excel": "EERR.xlsx",
    "unit": "Altamira",
    "year": 2026,
    "month": "ENE"
  },
  "resumen": {
    "total": 41,
    "coinciden": 35,
    "difieren": 6,
    "suma_excel": 99757.67,
    "suma_sistema": 99757.67
  },
  "comparaciones": [...]
}
```

---

## 🎯 VALIDACIÓN MASIVA

### Usando el script bash (Linux/Mac/Git Bash):

1. **Editar** `validar_todas_sucursales.sh`:
   ```bash
   # Agregar tus sucursales
   validar_sucursal "ruta/EERR RODEO.xlsx" "Rodeo"
   validar_sucursal "ruta/EERR TERRACOTA.xlsx" "Terracota"
   validar_sucursal "ruta/EERR ALTAMIRA.xlsx" "Altamira"
   ```

2. **Ejecutar:**
   ```bash
   chmod +x validar_todas_sucursales.sh
   ./validar_todas_sucursales.sh
   ```

3. **Ver reportes:**
   ```bash
   ls reportes_validacion/
   ```

### Usando el batch (Windows):

```batch
validar_sucursal.bat "C:\Desktop\EERR RODEO.xlsx" Rodeo
validar_sucursal.bat "C:\Desktop\EERR TERRACOTA.xlsx" Terracota
```

---

## ⚠️ INTERPRETACIÓN DE RESULTADOS

### ✅ Resultado exitoso:
```
[SUCCESS] TODOS LOS VALORES COINCIDEN!
Diferencia total: $0.00
```
**Significado:** Excel y Sistema tienen los mismos valores

### ⚠️ Diferencias por grupos:
```
[ALERT] 6 PARTIDAS CON DIFERENCIAS
Diferencia total: $0.00
```

**Explicación:** Las diferencias son de **presentación** debido al sistema de grupos:

| Excel (desagregado) | Sistema (agrupado) |
|---------------------|---------------------|
| Gastos de comisiones bancarias: $774.08 | Gastos Bancarios: $1,415.25 |
| Gastos de IGTF: $641.17 | (agrupa ambas) |

**Verificación:** Si la "Diferencia total" es $0.00, los valores son correctos.

### ❌ Error real:
```
[ALERT] 15 PARTIDAS CON DIFERENCIAS
Diferencia total: $5,234.50
```

**Acción requerida:** Revisar partidas específicas en modo `--verbose`

---

## 🔍 SOLUCIÓN DE PROBLEMAS

### Error: "No se pudo conectar al servidor"

**Causa:** Flask no está corriendo

**Solución:**
```bash
# Terminal 1: Iniciar Flask
python app.py

# Terminal 2: Ejecutar validación
python validar_eerr.py --excel "..." --unit "..."
```

### Error: "Archivo no encontrado"

**Causa:** Ruta incorrecta

**Solución:** Usar ruta absoluta
```bash
# Bien
python validar_eerr.py --excel "C:\Users\andre\Desktop\EERR.xlsx" --unit Rodeo

# Mal
python validar_eerr.py --excel "EERR.xlsx" --unit Rodeo
```

### Error: "No se encontraron partidas en el Excel"

**Causa:** Formato de Excel incorrecto

**Requisitos del Excel:**
- Columna A: Código + Nombre (ej: "6.01.01.01.001 Gastos...")
- Columna C: Balance (numérico)
- Datos desde fila 8 aproximadamente

### Valores no coinciden pero deberían

**Verificación:**
1. ¿El mes y año son correctos? `--year 2026 --month ENE`
2. ¿El nombre de la unidad está bien escrito? (case-sensitive)
3. ¿El Excel es de la unidad correcta?
4. ¿Flask se reinició después de cambios en `engine.py`?

---

## 📊 FORMATO DEL EXCEL (ODOO)

El script espera archivos Excel exportados de Odoo con esta estructura:

```
Fila 1:  Ganancia y Perdida
Fila 2:  
Fila 3:  Target Moves | All Posted Entries
Fila 4:  Date From    | 2026-01-01
Fila 5:  Date To      | 2026-01-31
Fila 6:
Fila 7:  Name         | Balance
Fila 8:  6.01.01.01.001 Gastos de servicios públicos | -91.41
Fila 9:  4.01.01.01.001 Ingresos por venta...        | 47933.03
...
```

**Notas:**
- El script **limpia automáticamente** los códigos de cuenta
- Los valores negativos se convierten a **positivos** (absoluto)
- Se ignoran filas con valor 0

---

## 🎓 CASOS DE USO

### 1. Validación mensual de cierre
```bash
# Al cierre de cada mes, validar todas las sucursales
./validar_todas_sucursales.sh
```

### 2. Auditoría de una sucursal específica
```bash
python validar_eerr.py \
    --excel "EERR RODEO ENE.xlsx" \
    --unit Rodeo \
    --verbose \
    --save auditoria_rodeo_ene2026.json
```

### 3. Comparación rápida después de correcciones
```bash
# Sin verbose para ver solo si hay diferencias
python validar_eerr.py --excel "EERR CORREGIDO.xlsx" --unit Rodeo
```

### 4. Validación de periodo anterior
```bash
python validar_eerr.py \
    --excel "EERR RODEO DIC 2025.xlsx" \
    --unit Rodeo \
    --year 2025 \
    --month DIC
```

---

## 📁 ARCHIVOS DEL SISTEMA

| Archivo | Descripción |
|---------|-------------|
| `validar_eerr.py` | Script principal de validación |
| `VALIDAR_EERR_INSTRUCCIONES.md` | Documentación detallada |
| `README_VALIDACION_EERR.md` | Este archivo |
| `validar_sucursal.bat` | Helper para Windows |
| `validar_todas_sucursales.sh` | Validación masiva (bash) |

---

## 🔄 WORKFLOW RECOMENDADO

1. **Exportar Excel de Odoo** para la sucursal y mes específico

2. **Validar con el script:**
   ```bash
   python validar_eerr.py --excel "EERR.xlsx" --unit NombreSucursal --verbose
   ```

3. **Revisar resultado:**
   - ✅ Si coincide → Continuar con siguiente sucursal
   - ❌ Si difiere → Revisar partidas con diferencia

4. **Si hay diferencias reales:**
   - Verificar mapping en la BD
   - Verificar clasificación de cuentas
   - Corregir en sistema
   - Re-validar

5. **Guardar evidencia:**
   ```bash
   python validar_eerr.py --excel "EERR.xlsx" --unit X --save evidencia_X.json
   ```

---

## 💡 TIPS

1. **Nombres de unidades:** Deben coincidir exactamente con los de la BD
   - ✅ "Rodeo" 
   - ❌ "rodeo", "RODEO", "Rodeo "

2. **Meses válidos:** ENE, FEB, MAR, ABR, MAY, JUN, JUL, AGO, SEPT, OCT, NOV, DIC

3. **Rendimiento:** El script es rápido (~2-5 segundos por sucursal)

4. **Automatización:** Puedes agregar el script a tareas programadas (cron/Task Scheduler)

5. **Backup:** Los reportes JSON sirven como backup de valores en un momento específico

---

## 📞 SOPORTE

Para ver la ayuda integrada:
```bash
python validar_eerr.py --help
```

Para reportar problemas, incluir:
- Comando ejecutado
- Output completo del error
- Archivo Excel (si es posible)
- Versión de Python: `python --version`

---

## 📄 LICENCIA

Uso interno - UltraX

---

**Última actualización:** 2026-06-05  
**Versión:** 1.0.0
