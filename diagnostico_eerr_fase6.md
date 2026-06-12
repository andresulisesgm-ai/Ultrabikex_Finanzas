# DIAGNÓSTICO ULTRAX - FASE 6
> **Nota:** Documento generado en modo de solo lectura. No se han modificado bases de datos, código ni archivos de producción.

## 1. TRANSCRIPCIÓN DE FILAS - HOJA 'EERR ULTRAX'

A continuación se detallan las filas del archivo Excel `EEFF_ULTRAX_2026.xlsx` en la hoja `'EERR ULTRAX'` para la sección comprendida entre `'Subtotal Gastos de Recursos Humanos'` y `'Subtotal Gastos de Comercialización y Logistica'` inclusive:

| Fila | Sangría (Indent) | Negrita | Nombre Exacto en Celda | ENE |
| --- | --- | --- | --- | --- |
| 68 | 1.0 | Sí | `Subtotal Gastos de Recursos Humanos` | 410.00 |
| 69 | 2.0 | No | `Gastos de sueldos y salarios empleados y directivos` | 70.00 |
| 70 | 2.0 | No | `Gastos de complementos empleados y directivos` | 50.00 |
| 71 | 2.0 | No | `Gastos de personal externo` | 10.00 |
| 72 | 2.0 | No | `Gastos de pasivos laborales vacaciones` | 40.00 |
| 73 | 2.0 | No | `Gastos de pasivos laborales utilidades` | 40.00 |
| 74 | 2.0 | No | `Gastos de pasivos laborales prestaciones e intereses` | 80.00 |
| 75 | 2.0 | No | `Gastos de pasivos laborales aportes` | 40.00 |
| 76 | 2.0 | No | `Gastos de pasivos laborales bono de guardería` | 10.00 |
| 77 | 2.0 | No | `Gastos de pasivos laborales HCM` | 10.00 |
| 78 | 2.0 | No | `Gastos de salud y seguridad laboral` | 10.00 |
| 79 | 2.0 | No | `Gastos de salud y seguridad laboral dotación` | 10.00 |
| 80 | 2.0 | No | `Gastos de salud y seguridad laboral fiestas y agasajos` | 10.00 |
| 81 | 2.0 | No | `Otros gastos de personal` | 30.00 |
| 82 | 2.0 | No | *Fila Vacía* | - |
| 83 | 1.0 | Sí | `Subtotal Gastos de Comercialización y Logistica` | 300.00 |

**Total de filas transcritas:** 16

## 2. AUDITORÍA DE PARTIDA: 'Gastos de salud y seguridad laboral dotación'

Búsqueda en base de datos para `'Gastos de salud y seguridad laboral dotación'`:

### En `mapping_groups_v2`:
| ID | group_name | odoo_code | report_type | display_order |
| --- | --- | --- | --- | --- |
| 149 | `Gastos de salud y seguridad laboral dotación` | `6.01.02.03.002` | `eerr` | 790 |

### En `mapping`:
*No se encontró ningún registro.*

NO EXISTE NINGUNA FUENTE DE DATOS para esta partida en la tabla `mapping`.

## 3. AUDITORÍA DE PARTIDA: 'Gastos de salud y seguridad laboral'

Búsqueda en base de datos para `'Gastos de salud y seguridad laboral'`:

### En `mapping_groups_v2`:
| ID | group_name | odoo_code | report_type | display_order |
| --- | --- | --- | --- | --- |
| 148 | `Gastos de salud y seguridad laboral` | `6.01.02.03.001` | `eerr` | 780 |

### En `mapping`:
| odoo_code | odoo_name | partida | sign |
| --- | --- | --- | --- |
| `6.01.02.03.001` | `Gastos de salud y seguridad laboral` | `Gastos de salud y seguridad laboral` | -1 |

## 4. ANÁLISIS DE DUPLICACIÓN EN ultrax_test.db (ADAPTADOR REAL)

Resultados de ejecución del adaptador real `eerr_completo_v2_ui_adapter(year='2026', unit='Rodeo')` para Enero 2026:

- **`Gastos de salud y seguridad laboral`** (calculado): **`10.00`** (proveniente del Odoo code `6.01.02.03.001` con partida homónima)
- **`Gastos de salud y seguridad laboral dotación`** (calculado): **`10.00`** (proveniente del Odoo code `6.01.02.03.002` que en la tabla `mapping` tiene como partida `'Gastos de uniformes y dotación al personal'`)

### Conclusión de Duplicación:
- Las partidas `'Gastos de salud y seguridad laboral'` y `'Gastos de salud y seguridad laboral dotación'` no se duplican entre sí, ya que calculan sus valores a partir de códigos Odoo distintos (`6.01.02.03.001` y `6.01.02.03.002` respectivamente).
- Sin embargo, debido a que el código `6.01.02.03.002` está mapeado en la tabla `mapping` a la partida `'Gastos de uniformes y dotación al personal'` y en `mapping_groups_v2` al grupo `'Gastos de salud y seguridad laboral dotación'`, y ambas aparecen en la salida jerárquica del adaptador, el monto de `10.00` correspondiente a este código Odoo se calcula e inserta dos veces en el reporte (una vez bajo cada nombre), duplicando el valor de ese código en el total general.
