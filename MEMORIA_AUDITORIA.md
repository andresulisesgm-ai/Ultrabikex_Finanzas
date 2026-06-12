# Memoria de Auditoría - Conciliación Financiera (Rodeo 2026)
*Creado el 7 de junio de 2026 para la persistencia de contexto entre sesiones.*

---

## 📌 Estado Actual del Trabajo
Se realizó una auditoría de conciliación financiera exhaustiva entre la base de datos del sistema (`data/ultrax.db`) y el libro de Excel de referencia `2 EEFF ULTRAX Rodeo febrero.xlsx` para la empresa **Rodeo** en los meses de **enero, febrero y marzo de 2026**.

* **Veredicto:** **NO VERIFICADO (FALLIDO)** debido a un bug de cálculo jerárquico crítico en el backend y una brecha de importación en el mes de marzo.

---

## 🔍 Hallazgos Críticos Localizados

### 1. El Bug del Nivel 0 (Subtotales en $0.00)
* **Archivo:** `app.py`
* **Función:** `eerr_completo_v2_ui_adapter` (Bucle jerárquico de subtotales, líneas 1386-1410).
* **Problema:** En el cálculo de agregación bottom-up de subtotales, el código contiene la condición de interrupción:
  ```python
  if c_level <= level:
      break
  ```
  Al procesar un nodo con `level = 0` (como `Utilidad Bruta por Venta de Mercancia y Taller`), la búsqueda de descendientes se interrumpe de inmediato en la primera iteración porque el nodo siguiente (`Utilidad Bruta por Servicios`) también es de nivel `0`. Esto hace que el acumulador se quede en `0.00`.

### 2. Brecha de Datos en Marzo 2026
* **Problema:** La base de datos tiene **0 registros** de transacciones y de presupuesto para marzo de 2026.
* **Causa:** No se ha importado el balance de comprobación de marzo de 2026 de Odoo. El archivo `ODOO MARZO.xlsx` en la carpeta `Desktop/YOCELI` pertenece a **marzo de 2025**, por lo que es inválido para este análisis.

### 3. Diferencia Estructural de Recursos Humanos
* **Problema:** El sistema en `engine.EERR_STRUCTURE` introduce jerarquías anidadas (ej. anidar póliza de HCM y seguridad laboral bajo el subtotal `Gastos de pasivos laborales HCM`), mientras que el Excel de referencia los presenta planos y separados. Esto causa diferencias al comparar líneas individuales directas, aunque los totales generales del grupo Recursos Humanos coinciden.

---

## 📂 Archivos y Rutas Clave
* **ID de la Conversación Origen:** `95b48c1c-4c4a-446d-852f-257d6def51a0`
* **Reporte Comparativo Completo (ENE/FEB):** `C:\Users\andre\.gemini\antigravity-cli\brain\95b48c1c-4c4a-446d-852f-257d6def51a0\reporte_comparativo_rodeo_ene_feb.md`
* **Reporte General de Auditoría:** `C:\Users\andre\.gemini\antigravity-cli\brain\95b48c1c-4c4a-446d-852f-257d6def51a0\auditoria_conciliacion_financiera.md`
* **Script de Comparación Automatizada:** `C:\Users\andre\.gemini\antigravity-cli\brain\95b48c1c-4c4a-446d-852f-257d6def51a0\scratch\write_final_markdown_report.py`

---

## 🚀 Próximos Pasos Recomendados
1. **Corregir el bucle de `app.py`:** Ajustar la lógica del subtotal jerárquico para que no se detenga prematuramente en los encabezados nivel 0.
2. **Cargar balance de Marzo 2026:** Obtener de Odoo el archivo real de marzo 2026 e importarlo al sistema.
3. **Aplanar Recursos Humanos:** Opcionalmente, modificar la estructura en `engine.EERR_STRUCTURE` para remover las subjerarquías de nivel 2 y dejarlo plano, igualando la visualización del Excel.
