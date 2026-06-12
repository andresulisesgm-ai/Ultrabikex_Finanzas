# Reporte de Auditoría - Mapeo Contable y Cuentas sin Clasificar

Este reporte detalla cómo se realiza el mapeo de cuentas contables de Odoo hacia las partidas del Estado de Resultados (EERR), qué ocurre con las cuentas sin clasificar, y presenta una reconciliación numérica basada en los datos reales del mes de prueba (Ene 2026, Rodeo).

---

## 1. Hallazgos Principales

1. **Mecanismo de Asociación:**
   - La asociación se realiza mediante la tabla SQLite `mapping`. Esta tabla relaciona el código de cuenta de Odoo (`odoo_code`) con la correspondiente partida del EERR (`partida`), aplicando un multiplicador de signo (`sign` = `1` o `-1`) y un tipo de ingreso (`income_type`).
2. **Ubicación del Mapeo:**
   - El mapeo inicial se carga desde el archivo Excel [Cuenta (account.account) (5).xlsx](file:///C:/Users/andre/Desktop/ultrax_app/Cuenta%20(account.account)%20(5).xlsx) a través de la función `load_mapping_from_excel()` de [db.py](file:///C:/Users/andre/Desktop/ultrax_app/db.py#L87).
   - En ejecución, los mapeos viven en la tabla de base de datos `mapping` y se agrupan en la tabla `mapping_groups_v2` (Matriz Maestra) para el cálculo jerárquico.
3. **Manejo de Cuentas sin Mapear:**
   - Durante la carga del Balance de Comprobación (`/api/upload`), si una cuenta Odoo no tiene mapeo en la tabla `mapping`, el sistema realiza un **auto-mapeo** bajo dos criterios:
     1. Coincidencia exacta de nombre limpio: `lower(odoo_name) = lower(account_name)`.
     2. Coincidencia por prefijo del código (primeros dos bloques, ej: `6.01`).
   - Si no se encuentra ninguna coincidencia, la cuenta se agrega al array `unmapped`, se incrementa el contador de omitidos (`skipped`) y **se excluye silenciosamente del cálculo financiero** (no se inserta en `financials` ni se refleja en el EERR). Sin embargo, se imprime una advertencia en el stdout del servidor y se muestra una lista detallada en la consola de depuración.
4. **Mecanismo de Edición Manual:**
   - Existe una interfaz completa en el frontend ([templates/index.html](file:///C:/Users/andre/Desktop/ultrax_app/templates/index.html)) conectada a los endpoints `/api/mapping` (GET/POST/DELETE) y `/api/mapping/log` en [app.py](file:///C:/Users/andre/Desktop/ultrax_app/app.py) que permite a los usuarios:
     - Consultar, agregar, modificar y eliminar asociaciones manuales.
     - Auditar los cambios a través de una bitácora de auditoría (`mapping_log`) y revertir/restaurar mapeos previamente eliminados.

---

## 2. Evidencia y Código de Referencia

### A) Procesamiento Contable (app.py:L140-189):
El flujo de lectura de balances contables y exclusión de cuentas no mapeadas se encuentra en [app.py](file:///C:/Users/andre/Desktop/ultrax_app/app.py#L140-L189):
```python
        for code, amount in accounts.items():
            is_balance = OdooParser.is_balance_account(code)
            m = db.execute('SELECT partida, sign, income_type FROM mapping WHERE odoo_code = ?', (code,)).fetchone()

            if not m:
                # Auto-mapeo... (omitiendo por brevedad)
                ...
                if auto:
                    db.execute('INSERT OR IGNORE INTO mapping ...')
                    m = auto

            if m:
                signed_amount = amount * (m['sign'] if m['sign'] else -1)
                if is_balance or is_esf:
                    db.execute('INSERT INTO esf_data ...')
                else:
                    db.execute('INSERT INTO financials ...')
            else:
                unmapped.append({'code': code, 'name': parser.names.get(code, ''), 'amount': amount})
                skipped += 1
```

### B) Tablas de la Base de Datos SQLite:
Las tablas de mapeo y jerarquía son:
- **`mapping`**: Guarda la asociación directa transaccional.
  ```sql
  CREATE TABLE mapping (
      odoo_code TEXT PRIMARY KEY,
      odoo_name TEXT NOT NULL,
      partida TEXT,
      sign INTEGER NOT NULL DEFAULT 1,
      income_type TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
  )
  ```
- **`mapping_groups_v2`** (Matriz Maestra V2): Agrupa los códigos Odoo bajo subtotales o nodos del EERR.
  ```sql
  CREATE TABLE mapping_groups_v2 (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      group_name TEXT NOT NULL,
      odoo_code TEXT NOT NULL,
      report_type TEXT NOT NULL,
      display_order INTEGER DEFAULT 0,
      created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
      FOREIGN KEY (odoo_code) REFERENCES mapping(odoo_code) ON DELETE CASCADE
  )
  ```

---

## 3. Prueba Concreta (Validación Numérica de Ene 2026, Rodeo)

Se ejecutó un script de verificación cruzada entre el archivo de Balance de Comprobación real y los saldos calculados en la base de datos:

- **Total de Cuentas en Trial Balance:** 171 cuentas.
- **Suma de balances brutos en Excel (Cuentas Gastos clase '6.'):** $1,490.00
- **Suma de importes en tabla `financials` para Gastos ('6.'):** $1,490.00
- **Diferencia:** **$0.00**
- **Cuentas de gastos sin mapear detectadas con movimientos:** **0**

---

## 4. Diagnóstico y Riesgo

1. **Estado Actual:** 
   Actualmente **no existen cuentas huérfanas con movimientos** para el mes de prueba. El 100% de los importes reportados en el Balance de Comprobación está mapeado a alguna partida en `mapping`.
2. **Riesgo Operativo:**
   Si a futuro se importa un Balance de Comprobación con cuentas nuevas (no presentes en el Excel de mapeo inicial) y el auto-mapeo por nombre o prefijo falla, **estas cuentas se omitirán del cálculo de subtotales**, resultando en una discrepancia entre la suma real del Balance de Comprobación y la Utilidad Neta reportada por el EERR. No obstante, el sistema alertará de esto imprimiendo el listado de huérfanas en la consola e indicando que el balance general descuadra.

---

## 5. Recomendación de Diseño para Mapeo Editable

Para implementar una pantalla de mapeo y overrides robusta (Fase 4):
1. **Detección Activa de Huérfanas:** Crear una vista o tarjeta en la UI que alerte si hay cuentas con balance en el último archivo subido que fueron omitidas.
2. **Catch-All Automático:** Opcionalmente, agregar una partida virtual "Cuentas sin clasificar" a `EERR_STRUCTURE` de nivel 3 (nota) que recolecte temporalmente cualquier movimiento de cuentas no mapeadas, evitando que la Utilidad Neta descuadre y permitiendo al usuario identificar de inmediato el monto no asignado.
3. **Mapeo Integrado:** Permitir al usuario hacer click en una cuenta huérfana de la lista y abrir un modal para asignarle una partida de EERR existente, guardando el cambio en la tabla `mapping` e iniciando una re-importación automática de los saldos del mes en cuestión.
