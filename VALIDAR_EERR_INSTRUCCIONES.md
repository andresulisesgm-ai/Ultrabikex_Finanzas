# INSTRUCCIONES: validar_eerr.py

Script para validar EERR comparando Excel vs Sistema para cualquier unidad y periodo.

---

## USO BÁSICO

```bash
python validar_eerr.py --excel "ruta/al/archivo.xlsx" --unit "Nombre_Unidad" --year 2026 --month ENE
```

---

## PARÁMETROS

### Obligatorios:

- `--excel` : Ruta completa al archivo Excel de EERR
- `--unit` : Nombre de la unidad (Rodeo, Terracota, Altamira, etc.)

### Opcionales:

- `--year` : Año a validar (default: 2026)
- `--month` : Mes a validar (default: ENE)
- `--server` : URL del servidor Flask (default: http://localhost:5000)
- `--verbose` o `-v` : Mostrar todas las partidas en detalle
- `--save` o `-s` : Guardar reporte en archivo JSON

---

## EJEMPLOS

### 1. Validación simple (solo resumen):
```bash
python validar_eerr.py --excel "C:\Desktop\EERR RODEO ENERO.xlsx" --unit Rodeo
```

### 2. Validación detallada (todas las partidas):
```bash
python validar_eerr.py --excel "C:\Desktop\EERR RODEO ENERO.xlsx" --unit Rodeo --verbose
```

### 3. Validación con mes/año específico:
```bash
python validar_eerr.py --excel "C:\Desktop\EERR TERRACOTA FEBRERO.xlsx" --unit Terracota --year 2026 --month FEB
```

### 4. Guardar reporte en archivo:
```bash
python validar_eerr.py --excel "EERR ALTAMIRA.xlsx" --unit Altamira --save reporte_altamira.json
```

### 5. Validación con servidor remoto:
```bash
python validar_eerr.py --excel "EERR.xlsx" --unit Rodeo --server http://192.168.1.100:5000
```

---

## OUTPUT

### Modo simple (sin --verbose):
```
====================================================================================================
                              VALIDACIÓN EERR: EXCEL vs SISTEMA
                         Rodeo - ENE 2026
====================================================================================================

RESUMEN:
Total partidas comparadas: 41
  [OK] Coinciden: 35 (85.4%)
  [X]  Difieren: 6 (14.6%)

Suma total Excel: $99,757.67
Suma total Sistema: $99,757.67
Diferencia total: $0.00

[DESGLOSE POR TIPO]
  Ingresos  - Excel: $48,122.01  Sistema: $48,122.01  Diff: $0.00
  Costos    - Excel: $20,670.85  Sistema: $20,670.85  Diff: $0.00
  Gastos    - Excel: $30,964.81  Sistema: $30,964.81  Diff: $0.00

[SUCCESS] TODOS LOS VALORES COINCIDEN!
```

### Modo detallado (con --verbose):
```
COMPARACIÓN PARTIDA POR PARTIDA:

#    Partida                                              Excel         Sistema         Diff Status
1    Gastos Bancarios                              $      0.00 $  1,415.25 $  1,415.25  [ERROR]
2    Costos de venta por mercancia                 $ 20,670.85 $ 20,670.85 $      0.00  [OK]
3    Gastos de sueldos y salarios empleados        $    205.50 $    205.50 $      0.00  [OK]
...
```

---

## CÓDIGOS DE SALIDA

- `0` : Validación exitosa (todos los valores coinciden)
- `1` : Hay diferencias o error en la ejecución

---

## REQUISITOS

1. **Servidor Flask corriendo:**
   ```bash
   python app.py
   ```

2. **Excel en formato Odoo:**
   - Columna A: Código + Nombre de cuenta (ej: "6.01.01.01.001 Gastos...")
   - Columna C: Balance (valor numérico)
   - Datos desde fila 8 aproximadamente

3. **Python 3.x con openpyxl:**
   ```bash
   pip install openpyxl
   ```

---

## SOLUCIÓN DE PROBLEMAS

### Error: "No se pudo conectar al servidor"
**Causa:** Flask no está corriendo o está en otro puerto

**Solución:**
```bash
# Verificar que Flask esté corriendo
python app.py

# O especificar otro puerto
python validar_eerr.py --excel "..." --unit "..." --server http://localhost:8000
```

### Error: "Archivo no encontrado"
**Causa:** Ruta incorrecta al Excel

**Solución:** Usar ruta absoluta o verificar que el archivo existe
```bash
# Windows
python validar_eerr.py --excel "C:\Users\andre\Desktop\EERR.xlsx" --unit Rodeo

# Linux/Mac
python validar_eerr.py --excel "/home/user/Desktop/EERR.xlsx" --unit Rodeo
```

### Advertencia: "6 PARTIDAS CON DIFERENCIAS"
**Causa:** Sistema de grupos (normal)

**Explicación:** El sistema agrupa partidas bajo nombres genéricos:
- Excel muestra: "Gastos de comisiones bancarias" + "Gastos de IGTF"
- Sistema muestra: "Gastos Bancarios" (suma de ambas)

**Verificación:** La suma total debe coincidir (Diferencia total: $0.00)

---

## WORKFLOW RECOMENDADO

### Para validar todas las sucursales:

1. **Crear directorio de reportes:**
   ```bash
   mkdir reportes_validacion
   ```

2. **Validar cada sucursal:**
   ```bash
   # Rodeo
   python validar_eerr.py --excel "EERR RODEO ENE.xlsx" --unit Rodeo --save reportes_validacion/rodeo.json

   # Terracota
   python validar_eerr.py --excel "EERR TERRACOTA ENE.xlsx" --unit Terracota --save reportes_validacion/terracota.json

   # Altamira
   python validar_eerr.py --excel "EERR ALTAMIRA ENE.xlsx" --unit Altamira --save reportes_validacion/altamira.json
   ```

3. **Revisar reportes:**
   - Verificar que todos muestren `[SUCCESS]`
   - Revisar diferencias si las hay
   - Los archivos JSON contienen el detalle completo

---

## NOTAS IMPORTANTES

1. **Los nombres de unidad deben coincidir exactamente** con los del sistema
   - Usar mayúsculas/minúsculas según como está en la BD
   - Ejemplos: "Rodeo", "Terracota", "Altamira"

2. **Meses válidos:** ENE, FEB, MAR, ABR, MAY, JUN, JUL, AGO, SEPT, OCT, NOV, DIC

3. **El script limpia automáticamente** los códigos de cuenta del Excel
   - "6.01.01.01.001 Gastos de..." → "Gastos de..."

4. **Valores en Excel:** Se toman en valor absoluto
   - Si Excel tiene -$100 (gasto), se compara como $100

---

## AYUDA

Para ver ayuda integrada:
```bash
python validar_eerr.py --help
```

---

**Creado:** 2026-06-05  
**Versión:** 1.0
