# 🎯 CAMBIOS IMPLEMENTADOS - SISTEMA DE MAPEO Y AGRUPACIÓN

## ✅ RESUMEN EJECUTIVO

Se han completado exitosamente los dos cambios estructurales solicitados:

1. **Reemplazo completo de INITIAL_MAPPING** con el plan de cuentas real de Odoo
2. **Sistema de agrupación de partidas** para presentación en estados financieros

---

## 📊 CAMBIO 1: NUEVO PLAN DE CUENTAS

### Archivos modificados:
- `db.py` (reescritura completa)

### Resultados:
- **717 cuentas** cargadas desde `Cuenta (account.account) (5).xlsx`
- **310 Activos** (1.x)
- **158 Pasivos** (2.x)
- **21 Patrimonio** (3.x)
- **33 Ingresos** (4.x)
- **10 Costos** (5.x)
- **185 Gastos** (6.x)

### Clasificación automática implementada:

| Tipo de cuenta | Sign | Income Type | Ejemplos |
|---------------|------|-------------|----------|
| Activos (1.x) | +1 | NULL | Caja, Bancos, Inventarios |
| Dep/Det Acum (1.02.06.XX.500/501) | -1 | NULL | Depreciaciones acumuladas |
| Amort Acum (1.02.07.XX.500/002) | -1 | NULL | Amortizaciones acumuladas |
| Pasivos (2.x) | -1 | NULL | Cuentas por pagar |
| Patrimonio (3.x) | -1 | NULL | Capital social |
| Ing. Mercancía (4.01.01.x) | +1 | 'mercancia' | Ventas de mercancías |
| Devoluciones (4.01.01.02/03.x) | -1 | 'mercancia' | Devoluciones y descuentos |
| Ing. Servicios (4.01.02.x) | +1 | 'servicios' | Servicios del café, FIT |
| Ing. Eventos (4.01.03.x) | +1 | 'eventos' | Ingresos por eventos |
| Ing. Taller (4.01.04.x) | +1 | 'taller' | Ingresos por taller |
| Ing. No Operativos (4.02.x) | +1 | NULL | Alquileres, intereses |
| Costos (5.x) | -1 | según 5.01.0X.x | Costos de venta |
| Gastos (6.x) | -1 | NULL | Gastos operativos |

### Funciones nuevas en `db.py`:

```python
def classify_account(codigo: str) -> tuple
    # Clasifica automáticamente por código
    # Retorna (sign, income_type)

def load_mapping_from_excel(excel_path='...') -> list
    # Lee el Excel y genera INITIAL_MAPPING
    # Retorna lista de tuplas

def reset_mapping() -> dict
    # Borra y recrea mapping con backup automático
    # USAR CON PRECAUCIÓN

def seed_initial_groups()
    # Inserta grupos iniciales en mapping_groups
```

---

## 🏗️ CAMBIO 2: SISTEMA DE AGRUPACIÓN

### Nueva tabla SQL:

```sql
CREATE TABLE mapping_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT NOT NULL,
    odoo_code TEXT NOT NULL,
    report_type TEXT NOT NULL CHECK(report_type IN ('eerr', 'esf')),
    display_order INTEGER DEFAULT 0,
    created_at TEXT,
    FOREIGN KEY (odoo_code) REFERENCES mapping(odoo_code) ON DELETE CASCADE
);
```

### Grupos iniciales creados (7 grupos, 36 asignaciones):

1. **Mantenimiento y reparaciones** (5 cuentas)
   - 6.01.01.02.001 a 6.01.01.02.005

2. **Viáticos administrativos** (5 cuentas)
   - 6.01.01.03.001 a 6.01.01.03.005

3. **Gastos de seguro** (4 cuentas)
   - 6.01.01.04.001 a 6.01.01.04.004

4. **Gastos de impuestos, tasas y contribuciones** (7 cuentas)
   - 6.01.01.05.001 a 6.01.01.05.007

5. **Depreciaciones, deterioro y Amortización** (10 cuentas)
   - 6.01.01.06.XXX + 6.01.01.07.XXX + 6.01.01.08.001

6. **Gastos Bancarios** (2 cuentas)
   - 6.01.01.09.001, 6.01.01.09.002

7. **Gastos de intereses sobre préstamos** (3 cuentas)
   - 6.01.01.10.001 a 6.01.01.10.003

### Nuevos endpoints en `app.py`:

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/mapping_groups` | GET | Lista todos los grupos con sus cuentas |
| `/api/mapping_groups` | POST | Crea/actualiza asignaciones de grupo |
| `/api/mapping_groups/<id>` | DELETE | Elimina una asignación individual |
| `/api/mapping_groups/group/<name>` | DELETE | Elimina un grupo completo |
| `/api/mapping/reset` | POST | Ejecuta reset_mapping() desde UI |

### Modificaciones en cálculos:

**Archivos modificados:**
- `app.py` - Funciones modificadas:
  - `eerr_completo()` - Línea ~861
  - `eerr_divisa_real()` - Línea ~1670

**Lógica de agrupación:**

```python
# Nueva función auxiliar
def get_grouped_partidas(db, report_type='eerr'):
    # Retorna:
    # - groups: dict {group_name: [partida1, partida2, ...]}
    # - grouped_partidas: set de partidas ya agrupadas

# En cálculos EERR:
groups, grouped_partidas = get_grouped_partidas(db, 'eerr')

for partida_name in EERR_STRUCTURE:
    if partida_name in groups:
        # Es un grupo: sumar todas las partidas del grupo
        matching = groups[partida_name]
    else:
        # Partida individual (excluir las que están en grupos)
        matching = [p for p in (ing_p | cos_p | gas_p)
                    if p.lower() == partida_name.lower()
                    and p not in grouped_partidas]
```

---

## 📝 INSTRUCCIONES DE EJECUCIÓN

### PASO 1: Validar (sin cambios)

```bash
python migrate_mapping.py --validate
```

**Salida esperada:**
```
[OK] 717 cuentas cargadas desde Cuenta (account.account) (5).xlsx
[OK] Total de cuentas: 717
[OK] No hay códigos duplicados
[OK] 19 cuentas de Dep/Det Acum con sign=-1 correcto
[OK] 22 cuentas con income_type asignado
[OK] VALIDACIÓN COMPLETADA EXITOSAMENTE
```

### PASO 2: Ejecutar migración

⚠️ **ADVERTENCIA:** Esto borrará y recreará la tabla `mapping`. Se crea backup automático.

```bash
python migrate_mapping.py --execute
```

El script pedirá confirmación:
```
¿Deseas continuar? (escribe 'SI' en mayúsculas):
```

**Salida esperada:**
```
[STEP] Paso 1/3: Ejecutando migrate_db()...
[OK] migrate_db() completado
[OK] Tabla mapping_groups creada

[STEP] Paso 2/3: Ejecutando reset_mapping()...
[OK] Backup guardado en: data/mapping_backup_YYYYMMDD_HHMMSS.csv
[OK] reset_mapping() completado
   - Cuentas insertadas: 717

[STEP] Paso 3/3: Insertando grupos iniciales...
[OK] 36 grupos iniciales insertados

[STEP] Verificación final...
   - Cuentas en mapping: 717
   - Grupos definidos: 7
   - Asignaciones: 36

[OK] MIGRACIÓN COMPLETADA EXITOSAMENTE

[SUCCESS] El sistema está listo para usar el nuevo plan de cuentas.
   Reinicia la aplicación con: python app.py
```

### PASO 3: Reiniciar la aplicación

```bash
python app.py
```

O en Windows:
```bash
ultrax.bat
```

---

## 🔍 VALIDACIONES IMPLEMENTADAS

### En el script de migración:

- ✅ No hay códigos duplicados
- ✅ Depreciaciones/deterioros con sign=-1 correcto
- ✅ Income_types válidos (mercancia, servicios, eventos, taller, NULL)
- ✅ Distribución de cuentas por tipo
- ✅ Grupos iniciales válidos

### En el código:

- ✅ `FOREIGN KEY` en `mapping_groups` → `mapping.odoo_code`
- ✅ `ON DELETE CASCADE` para mantener integridad
- ✅ `CHECK(report_type IN ('eerr', 'esf'))` en tabla
- ✅ Índices en `odoo_code` y `(report_type, group_name)`

---

## 📂 ARCHIVOS MODIFICADOS

| Archivo | Cambios | Líneas |
|---------|---------|--------|
| `db.py` | Reescritura completa | 442 |
| `app.py` | Nuevos endpoints + modificaciones | ~150 |
| `migrate_mapping.py` | Script nuevo | 207 |

---

## 🎯 PRÓXIMOS PASOS (OPCIONAL)

### Frontend (UI):

1. **Página de gestión de mapeo:**
   - Mostrar tabla de cuentas con filtros
   - Botón "Asignar a grupo" por cuenta
   - Modal para crear nuevo grupo

2. **Validación visual:**
   - Mostrar cuentas sin mapear al subir archivo
   - Highlight de cuentas agrupadas en EERR/ESF

3. **Endpoint de test:**
   ```javascript
   // Probar endpoint de grupos
   GET /api/mapping_groups?report_type=eerr
   
   // Crear nuevo grupo
   POST /api/mapping_groups
   {
     "group_name": "Nuevo Grupo",
     "odoo_codes": ["6.01.XX.XX.001", "6.01.XX.XX.002"],
     "report_type": "eerr",
     "display_order": 100
   }
   ```

---

## ⚠️ NOTAS IMPORTANTES

1. **Backup automático:** Cada vez que se ejecuta `reset_mapping()`, se crea un backup CSV en `data/mapping_backup_YYYYMMDD_HHMMSS.csv`

2. **Encoding:** El Excel se lee con `openpyxl` que maneja UTF-8 correctamente

3. **Performance:** Los índices en `mapping_groups` aseguran queries rápidas

4. **Extensibilidad:** Se pueden agregar más grupos desde la UI usando el endpoint POST `/api/mapping_groups`

5. **Retrocompatibilidad:** Los cálculos antiguos siguen funcionando; los grupos solo afectan si existen en `mapping_groups`

---

## 📞 SOPORTE

Si hay problemas:

1. Revisar logs de la validación
2. Verificar que `pandas` y `openpyxl` están instalados
3. Comprobar que el archivo Excel esté en la carpeta raíz
4. Revisar el backup CSV generado antes de la migración

**Comandos de diagnóstico:**

```bash
# Ver backup más reciente
ls -la data/mapping_backup_*.csv | tail -1

# Contar cuentas en DB
sqlite3 data/ultrax.db "SELECT COUNT(*) FROM mapping;"

# Ver grupos
sqlite3 data/ultrax.db "SELECT group_name, COUNT(*) FROM mapping_groups GROUP BY group_name;"
```

---

✅ **IMPLEMENTACIÓN COMPLETADA EXITOSAMENTE**

Fecha: 2026-06-05
Versión: 2.0 - Plan de Cuentas Real + Agrupación
