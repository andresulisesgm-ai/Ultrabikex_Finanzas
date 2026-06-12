# Reporte de Validación e Integridad - Fase 2

Este reporte confirma el cumplimiento de todas las condiciones y pruebas de regresión de la **Fase 2 (Personalización de Jerarquía EERR)** del sistema **ULTRAX**.

---

## 1. Resultado de Validación A — Identidad Estructural

Se verificó la estructura generada dinámicamente mediante `build_effective_structure(EERR_STRUCTURE, db_overrides=[])` frente al bucle estático de lectura directa que existía originalmente en el sistema.

### Detalles de la comparación:
- **Elementos en estructura original (lectura directa):** 169 elementos.
- **Elementos en estructura nueva (con overrides vacíos):** 169 elementos.
- **Diferencias encontradas:** **0** diferencias.

El orden, los nombres de las partidas (`partida_name`), la bandera de encabezado (`is_header`), y los niveles de jerarquía (`level`) coinciden al **100% elemento por elemento**.

### Salida del Script de Validación (`scratch_validate.py`):
```text
=== VALIDACIÓN A: IDENTIDAD ESTRUCTURAL ===
Longitud A (Original): 169
Longitud B (Nueva): 169
Total diferencias: 0

[SUCCESS] Ambas listas son completamente IDÉNTICAS (169 elementos).
```

---

## 2. Resultado de Validación B — Regresión Financiera (Ene 2026)

Se re-corrió la suite de conciliación financiera (`test_fase3.py`) utilizando el balance de comprobación de prueba y comparándolo contra la hoja baseline **EERR ULTRAX** de `EEFF ULTRAX 2026.xlsx` (Unidad: Rodeo, Enero 2026).

Todos los subtotales y totales clave calculados bajo la nueva estructura dinámica presentan una **diferencia exacta de 0.00** contra el Excel de referencia.

### Tabla de Reconciliación (Totales y Subtotales Clave):

| Partida en Sistema | Partida en Excel | Valor Calculado | Valor Esperado (Excel) | Diferencia |
| :--- | :--- | :---: | :---: | :---: |
| **Total Ingresos** | Total Ingresos | 13,800.00 | 13,800.00 | **0.00** |
| **Subtotal Ingresos por Venta de Mercancia** | Subtotal Ingresos por Venta de Mercancia | 13,500.00 | 13,500.00 | **0.00** |
| **Subtotal Ingresos por Servicios** | Subtotal Ingresos por Servicios | 200.00 | 200.00 | **0.00** |
| **Subtotal Ingresos por Eventos** | Subtotal Ingresos por Eventos | 50.00 | 50.00 | **0.00** |
| **Subtotal Ingresos por Taller** | Subtotal Ingresos por Taller | 50.00 | 50.00 | **0.00** |
| **Total Costo de Ventas** | Total Costo de Ventas | 9,050.00 | 9,050.00 | **0.00** |
| **Subtotal Costo de Ventas por Mercancia** | Subtotal Costo de Ventas por Mercancia | 9,000.00 | 9,000.00 | **0.00** |
| **Subtotal Costo de Ventas por Servicios** | Subtotal Costo de Ventas por Servicios | 20.00 | 20.00 | **0.00** |
| **Subtotal Costo de Ventas por Eventos** | Subtotal Costo de Ventas por Eventos | 30.00 | 30.00 | **0.00** |
| **Utilidad Bruta por Venta de Mercancia y Taller** | Utilidad Bruta por Venta de Mercancia y Taller | 4,550.00 | 4,550.00 | **0.00** |
| **Utilidad Bruta por Servicios** | Utilidad Bruta por Servicios | 180.00 | 180.00 | **0.00** |
| **Utilidad Bruta por Eventos** | Utilidad Bruta por Eventos | 20.00 | 20.00 | **0.00** |
| **Utilidad Bruta** | Utilidad Bruta | 4,750.00 | 4,750.00 | **0.00** |
| **Total Gastos Operacionales** | Total Gastos Operacionales | 1,410.00 | 1,410.00 | **0.00** |
| **Subtotal Gastos de Administración** | Subtotal Gastos de Administración | 540.00 | 540.00 | **0.00** |
| **Subtotal Gastos de Recursos Humanos** | Subtotal Gastos de Recursos Humanos | 410.00 | 410.00 | **0.00** |
| **Subtotal Gastos de Comercialización y Logistica** | Subtotal Gastos de Comercialización y Logistica | 300.00 | 300.00 | **0.00** |
| **Subtotal Gastos de Mercadeo** | Subtotal Gastos de Mercadeo | 130.00 | 130.00 | **0.00** |
| **Subtotal Gastos de TI+I** | Subtotal Gastos de TI+I | 30.00 | 30.00 | **0.00** |
| **Utilidad antes de Comisiones por Ventas** | Utilidad antes de Comisiones por Ventas | 3,370.00 | 3,370.00 | **0.00** |
| **Utilidad después de Comisiones por Ventas** | Utilidad después de Comisiones por Ventas | 3,340.00 | 3,340.00 | **0.00** |
| **Utilidad antes de intereses, impuestos, ebitda** | EBITDA | 3,530.00 | 3,530.00 | **0.00** |
| **Utilidad antes de Intereses e Impuestos (EBIT)** | Utilidad antes de Intereses e Impuestos (EBIT) | 3,430.00 | 3,430.00 | **0.00** |
| **Otros Gastos no Operacionales** | Otros Gastos no Operacionales | 80.00 | 80.00 | **0.00** |
| **Total Gastos Operacionales y No Operacionales** | Total Gastos Operacionales y No Operacionales | 1,490.00 | 1,490.00 | **0.00** |
| **Otros Ingresos no Operacionales** | Otros Ingresos no Operacionales | 450.00 | 450.00 | **0.00** |
| **Utilidad Neta** | Utilidad Neta | 3,710.00 | 3,710.00 | **0.00** |
| **Utilidad Neta despues de ISLR** | Utilidad Neta despues de ISLR | 3,710.00 | 3,710.00 | **0.00** |

---

## 3. Confirmación de Archivos Modificados

- Se confirma que **únicamente** [app.py](file:///C:/Users/andre/Desktop/ultrax_app/app.py) (para el desacoplamiento de la estructura) y [engine.py](file:///C:/Users/andre/Desktop/ultrax_app/engine.py) (para la corrección ortográfica de la Fase 1 y la definición de `build_effective_structure`) fueron modificados con propósitos de esta implementación de la Fase 2.
- No se realizaron cambios en el frontend (`templates/index.html`) ni en la lógica matemática de consolidación para esta entrega.
