# INVENTARIO COMPLETO Y PROPUESTA DE LIMPIEZA/REORGANIZACIÓN
> **Nota:** De acuerdo con las instrucciones de solo diagnóstico, en esta fase **NO** se ha realizado ningún borrado, reubicación ni renombrado de archivos. Esta es una propuesta teórica.

## 1. Resumen Ejecutivo de Espacio y Archivos

* **Total de archivos analizados:** 95
* **Tamaño total actual:** 8.14 MB (8,531,632 bytes)

| Categoría | Cantidad | Tamaño (KB) | % del Total (Espacio) | Estado Propuesto |
| --- | --- | --- | --- | --- |
| A) ESENCIAL (Código vivo / BD en uso) | 12 | 1032.64 KB | 12.4% | Mantener en raíz / intactos |
| B) BACKUP/HISTÓRICO (Copias de seguridad / logs / temporales) | 16 | 6108.62 KB | 73.3% | Mover a `_archive/` o `_backups_no_restaurar/` |
| C) CÓDIGO MUERTO/BORRADOR (Diseños y borradores obsoletos) | 1 | 12.33 KB | 0.1% | Mover a `_archive/` o `_backups_no_restaurar/` |
| D) SCRIPTS DE VALIDACIÓN/TEST (Pruebas, auditorías, migraciones) | 12 | 41.19 KB | 0.5% | Mantener en raíz / intactos |
| E) DOCUMENTACIÓN/CONTEXTO (Archivos .md / Excel de referencia) | 54 | 1136.89 KB | 13.6% | Mantener en raíz / intactos |

## 2. Propuesta de Reorganización de Archivos
Para mantener la raíz del repositorio limpia, se propone mover todos los archivos de las categorías **B (Backup/Histórico)** y **C (Código muerto/Borrador)** a carpetas específicas.

### Carpetas Propuestas:
1. `_backups_no_restaurar/` (ya existe en parte o se formalizará): Para todos los archivos en categoría **B** (copias de seguridad de código, históricos JSON grandes, logs).
2. `_archive/` o `_borradores/`: Para los archivos de la categoría **C** (intentos antiguos de diseño que no se importan pero sirven de referencia histórica).

## 3. Tabla General de Inventario

| Archivo | Categoría | Tamaño (KB) | Modificación (Git) | ¿En Uso Activo? | Acción Propuesta |
| --- | --- | --- | --- | --- | --- |
| [`.aider.chat.history.md`](file:///C:/Users/andre/Desktop/ultrax_app/.aider.chat.history.md) | E | 23.93 KB | No commit history (untracked) | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`.aider.input.history`](file:///C:/Users/andre/Desktop/ultrax_app/.aider.input.history) | B | 1.58 KB | No commit history (untracked) | NO | Mover a `_backups_no_restaurar/` |
| [`.claude/FORMULAS_CLIENTE.md`](file:///C:/Users/andre/Desktop/ultrax_app/.claude/FORMULAS_CLIENTE.md) | E | 9.41 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`.claude/settings.local.json`](file:///C:/Users/andre/Desktop/ultrax_app/.claude/settings.local.json) | E | 0.80 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`.gitignore`](file:///C:/Users/andre/Desktop/ultrax_app/.gitignore) | A | 0.01 KB | 2026-06-06 | SÍ | Mantener intacto |
| [`ANALISIS_SUBTOTALES_EERR.md`](file:///C:/Users/andre/Desktop/ultrax_app/ANALISIS_SUBTOTALES_EERR.md) | E | 9.84 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`CAMBIAR_CONTRASEÑAS.md`](file:///C:/Users/andre/Desktop/ultrax_app/CAMBIAR_CONTRASEÑAS.md) | E | 2.01 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`CAMBIOS_IMPLEMENTADOS.md`](file:///C:/Users/andre/Desktop/ultrax_app/CAMBIOS_IMPLEMENTADOS.md) | E | 8.62 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`CLAUDE.md`](file:///C:/Users/andre/Desktop/ultrax_app/CLAUDE.md) | E | 0.14 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`Cuenta (account.account) (5).xlsx`](file:///C:/Users/andre/Desktop/ultrax_app/Cuenta (account.account) (5).xlsx) | E | 29.34 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`EEFF ULTRAX 2026.xlsx`](file:///C:/Users/andre/Desktop/ultrax_app/EEFF ULTRAX 2026.xlsx) | E | 310.75 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`EERR RODEO ENERO.xlsx`](file:///C:/Users/andre/Desktop/ultrax_app/EERR RODEO ENERO.xlsx) | E | 10.70 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`ESTADO DE RESULTADOS ODOO COMPROBACION1.xlsx`](file:///C:/Users/andre/Desktop/ultrax_app/ESTADO DE RESULTADOS ODOO COMPROBACION1.xlsx) | E | 16.47 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`HALLAZGOS_VALIDACION_EERR.md`](file:///C:/Users/andre/Desktop/ultrax_app/HALLAZGOS_VALIDACION_EERR.md) | E | 5.60 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`MEMORIA_AUDITORIA.md`](file:///C:/Users/andre/Desktop/ultrax_app/MEMORIA_AUDITORIA.md) | E | 3.15 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`PLAN_ELIMINACION_AGRUPADORES_RRHH.md`](file:///C:/Users/andre/Desktop/ultrax_app/PLAN_ELIMINACION_AGRUPADORES_RRHH.md) | E | 6.83 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`README.md`](file:///C:/Users/andre/Desktop/ultrax_app/README.md) | E | 1.16 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`README_VALIDACION_EERR.md`](file:///C:/Users/andre/Desktop/ultrax_app/README_VALIDACION_EERR.md) | E | 8.55 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`REPORTE_IMPLEMENTACION_SUBTOTALES.md`](file:///C:/Users/andre/Desktop/ultrax_app/REPORTE_IMPLEMENTACION_SUBTOTALES.md) | E | 7.59 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`REPORTE_INSERCION_28_PARTIDAS.md`](file:///C:/Users/andre/Desktop/ultrax_app/REPORTE_INSERCION_28_PARTIDAS.md) | E | 5.71 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`REPORTE_LIMPIEZA_AGRUPADORES_RRHH.md`](file:///C:/Users/andre/Desktop/ultrax_app/REPORTE_LIMPIEZA_AGRUPADORES_RRHH.md) | E | 6.89 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`REPORTE_LIMPIEZA_DUPLICADOS.md`](file:///C:/Users/andre/Desktop/ultrax_app/REPORTE_LIMPIEZA_DUPLICADOS.md) | E | 3.46 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`REPORTE_VALIDACION_FINAL.md`](file:///C:/Users/andre/Desktop/ultrax_app/REPORTE_VALIDACION_FINAL.md) | E | 7.71 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`VALIDAR_EERR_INSTRUCCIONES.md`](file:///C:/Users/andre/Desktop/ultrax_app/VALIDAR_EERR_INSTRUCCIONES.md) | E | 5.53 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`_backups_no_restaurar/ultrax_backup_antes_de_borrar_20260612_142903.db`](file:///C:/Users/andre/Desktop/ultrax_app/_backups_no_restaurar/ultrax_backup_antes_de_borrar_20260612_142903.db) | B | 760.00 KB | 2026-06-12 | NO | Mover a `_backups_no_restaurar/` |
| [`_backups_no_restaurar/ultrax_backup_current.db`](file:///C:/Users/andre/Desktop/ultrax_app/_backups_no_restaurar/ultrax_backup_current.db) | B | 608.00 KB | 2026-06-12 | NO | Mover a `_backups_no_restaurar/` |
| [`_backups_no_restaurar/ultrax_backup_post_paso2.db`](file:///C:/Users/andre/Desktop/ultrax_app/_backups_no_restaurar/ultrax_backup_post_paso2.db) | B | 608.00 KB | 2026-06-12 | NO | Mover a `_backups_no_restaurar/` |
| [`_backups_no_restaurar/ultrax_backup_pre_atomic.db`](file:///C:/Users/andre/Desktop/ultrax_app/_backups_no_restaurar/ultrax_backup_pre_atomic.db) | B | 608.00 KB | 2026-06-12 | NO | Mover a `_backups_no_restaurar/` |
| [`_backups_no_restaurar/ultrax_pre_fase1.db`](file:///C:/Users/andre/Desktop/ultrax_app/_backups_no_restaurar/ultrax_pre_fase1.db) | B | 608.00 KB | 2026-06-12 | NO | Mover a `_backups_no_restaurar/` |
| [`_backups_no_restaurar/ultrax_pre_paqueteA1.db`](file:///C:/Users/andre/Desktop/ultrax_app/_backups_no_restaurar/ultrax_pre_paqueteA1.db) | B | 608.00 KB | 2026-06-12 | NO | Mover a `_backups_no_restaurar/` |
| [`_backups_no_restaurar/ultrax_pre_paqueteA2.db`](file:///C:/Users/andre/Desktop/ultrax_app/_backups_no_restaurar/ultrax_pre_paqueteA2.db) | B | 608.00 KB | 2026-06-12 | NO | Mover a `_backups_no_restaurar/` |
| [`_backups_no_restaurar/ultrax_pre_paqueteB.db`](file:///C:/Users/andre/Desktop/ultrax_app/_backups_no_restaurar/ultrax_pre_paqueteB.db) | B | 608.00 KB | 2026-06-12 | NO | Mover a `_backups_no_restaurar/` |
| [`_backups_no_restaurar/ultrax_test.db`](file:///C:/Users/andre/Desktop/ultrax_app/_backups_no_restaurar/ultrax_test.db) | B | 608.00 KB | 2026-06-12 | NO | Mover a `_backups_no_restaurar/` |
| [`app.py`](file:///C:/Users/andre/Desktop/ultrax_app/app.py) | A | 143.12 KB | 2026-06-12 | SÍ | Mantener intacto |
| [`app_backup_antes_de_cambio_20260612_142903.py`](file:///C:/Users/andre/Desktop/ultrax_app/app_backup_antes_de_cambio_20260612_142903.py) | B | 143.78 KB | 2026-06-12 | NO | Mover a `_backups_no_restaurar/` |
| [`app_backup_fase5.py`](file:///C:/Users/andre/Desktop/ultrax_app/app_backup_fase5.py) | B | 135.07 KB | 2026-06-12 | NO | Mover a `_backups_no_restaurar/` |
| [`auth.py`](file:///C:/Users/andre/Desktop/ultrax_app/auth.py) | A | 1.92 KB | 2026-06-06 | SÍ | Mantener intacto |
| [`cambiar_clave.bat`](file:///C:/Users/andre/Desktop/ultrax_app/cambiar_clave.bat) | A | 0.08 KB | 2026-06-06 | SÍ | Mantener intacto |
| [`cambiar_clave.py`](file:///C:/Users/andre/Desktop/ultrax_app/cambiar_clave.py) | A | 4.55 KB | 2026-06-06 | SÍ | Mantener intacto |
| [`data/mapping_backup_20260605_210251.csv`](file:///C:/Users/andre/Desktop/ultrax_app/data/mapping_backup_20260605_210251.csv) | B | 61.90 KB | 2026-06-06 | NO | Mover a `_backups_no_restaurar/` |
| [`data/mapping_backup_20260605_210308.csv`](file:///C:/Users/andre/Desktop/ultrax_app/data/mapping_backup_20260605_210308.csv) | B | 61.90 KB | 2026-06-06 | NO | Mover a `_backups_no_restaurar/` |
| [`data/ultrax.db`](file:///C:/Users/andre/Desktop/ultrax_app/data/ultrax.db) | A | 608.00 KB | 2026-06-12 | SÍ | Mantener intacto |
| [`db.py`](file:///C:/Users/andre/Desktop/ultrax_app/db.py) | A | 20.96 KB | 2026-06-12 | SÍ | Mantener intacto |
| [`diagnostico_diseno_eerr.md`](file:///C:/Users/andre/Desktop/ultrax_app/diagnostico_diseno_eerr.md) | E | 17.01 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`diagnostico_eerr.md`](file:///C:/Users/andre/Desktop/ultrax_app/diagnostico_eerr.md) | E | 209.87 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`diagnostico_eerr_fase2.md`](file:///C:/Users/andre/Desktop/ultrax_app/diagnostico_eerr_fase2.md) | E | 122.88 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`diagnostico_eerr_fase3.md`](file:///C:/Users/andre/Desktop/ultrax_app/diagnostico_eerr_fase3.md) | E | 17.12 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`diagnostico_eerr_fase4.md`](file:///C:/Users/andre/Desktop/ultrax_app/diagnostico_eerr_fase4.md) | E | 8.81 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`diagnostico_eerr_fase5.md`](file:///C:/Users/andre/Desktop/ultrax_app/diagnostico_eerr_fase5.md) | E | 16.97 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`diagnostico_eerr_fase6.md`](file:///C:/Users/andre/Desktop/ultrax_app/diagnostico_eerr_fase6.md) | E | 4.04 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`diagnostico_eerr_paqueteA1_resultado.md`](file:///C:/Users/andre/Desktop/ultrax_app/diagnostico_eerr_paqueteA1_resultado.md) | E | 17.11 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`diagnostico_eerr_paqueteA2_resultado.md`](file:///C:/Users/andre/Desktop/ultrax_app/diagnostico_eerr_paqueteA2_resultado.md) | E | 17.06 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`diagnostico_eerr_paqueteB_resultado.md`](file:///C:/Users/andre/Desktop/ultrax_app/diagnostico_eerr_paqueteB_resultado.md) | E | 17.07 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`diseno_capa_personalizacion_eerr.md`](file:///C:/Users/andre/Desktop/ultrax_app/diseno_capa_personalizacion_eerr.md) | E | 9.98 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`engine.py`](file:///C:/Users/andre/Desktop/ultrax_app/engine.py) | A | 45.86 KB | 2026-06-12 | SÍ | Mantener intacto |
| [`inspect_step2_trazabilidad.py`](file:///C:/Users/andre/Desktop/ultrax_app/inspect_step2_trazabilidad.py) | D | 2.35 KB | No commit history (untracked) | SÍ (Test/Utility) | Mantener intacto en raíz (o agrupar en `tests/` en un refactor futuro) |
| [`inspect_step2b_grupo_rrhh.py`](file:///C:/Users/andre/Desktop/ultrax_app/inspect_step2b_grupo_rrhh.py) | D | 2.75 KB | No commit history (untracked) | SÍ (Test/Utility) | Mantener intacto en raíz (o agrupar en `tests/` en un refactor futuro) |
| [`inspect_step3_logica_subtotal.py`](file:///C:/Users/andre/Desktop/ultrax_app/inspect_step3_logica_subtotal.py) | D | 3.89 KB | No commit history (untracked) | SÍ (Test/Utility) | Mantener intacto en raíz (o agrupar en `tests/` en un refactor futuro) |
| [`integrity_guard.log`](file:///C:/Users/andre/Desktop/ultrax_app/integrity_guard.log) | B | 44.32 KB | 2026-06-12 | NO | Mover a `_backups_no_restaurar/` |
| [`migrate_eerr_structure.py`](file:///C:/Users/andre/Desktop/ultrax_app/migrate_eerr_structure.py) | D | 6.21 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener intacto en raíz (o agrupar en `tests/` en un refactor futuro) |
| [`migrate_mapping.py`](file:///C:/Users/andre/Desktop/ultrax_app/migrate_mapping.py) | D | 7.06 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (o agrupar en `tests/` en un refactor futuro) |
| [`new_eerr_structure.py`](file:///C:/Users/andre/Desktop/ultrax_app/new_eerr_structure.py) | C | 12.33 KB | 2026-06-12 | NO | Mover a `_archive/` |
| [`plan_insercion_eerr.md`](file:///C:/Users/andre/Desktop/ultrax_app/plan_insercion_eerr.md) | E | 9.08 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`reconciliation_results.json`](file:///C:/Users/andre/Desktop/ultrax_app/reconciliation_results.json) | B | 36.08 KB | 2026-06-12 | NO | Mover a `_backups_no_restaurar/` |
| [`reporte_auditoria_fase4a.md`](file:///C:/Users/andre/Desktop/ultrax_app/reporte_auditoria_fase4a.md) | E | 5.23 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`reporte_auditoria_mapeo.md`](file:///C:/Users/andre/Desktop/ultrax_app/reporte_auditoria_mapeo.md) | E | 6.55 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`reporte_validacion_fase1.md`](file:///C:/Users/andre/Desktop/ultrax_app/reporte_validacion_fase1.md) | E | 5.86 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`reporte_validacion_fase2.md`](file:///C:/Users/andre/Desktop/ultrax_app/reporte_validacion_fase2.md) | E | 5.22 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`reporte_validacion_fase3.md`](file:///C:/Users/andre/Desktop/ultrax_app/reporte_validacion_fase3.md) | E | 3.93 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`requirements.txt`](file:///C:/Users/andre/Desktop/ultrax_app/requirements.txt) | A | 0.07 KB | 2026-06-06 | SÍ | Mantener intacto |
| [`scratch_check.py`](file:///C:/Users/andre/Desktop/ultrax_app/scratch_check.py) | D | 0.23 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (o agrupar en `tests/` en un refactor futuro) |
| [`scratch_validate.py`](file:///C:/Users/andre/Desktop/ultrax_app/scratch_validate.py) | D | 1.41 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (o agrupar en `tests/` en un refactor futuro) |
| [`system_map.json`](file:///C:/Users/andre/Desktop/ultrax_app/system_map.json) | E | 14.33 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`templates/index.html`](file:///C:/Users/andre/Desktop/ultrax_app/templates/index.html) | A | 202.61 KB | 2026-06-12 | SÍ | Mantener intacto |
| [`templates/login.html`](file:///C:/Users/andre/Desktop/ultrax_app/templates/login.html) | A | 4.62 KB | 2026-06-06 | SÍ | Mantener intacto |
| [`test_colors.html`](file:///C:/Users/andre/Desktop/ultrax_app/test_colors.html) | D | 1.54 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener intacto en raíz (o agrupar en `tests/` en un refactor futuro) |
| [`test_fase3.py`](file:///C:/Users/andre/Desktop/ultrax_app/test_fase3.py) | D | 8.76 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (o agrupar en `tests/` en un refactor futuro) |
| [`ultrax.bat`](file:///C:/Users/andre/Desktop/ultrax_app/ultrax.bat) | A | 0.83 KB | 2026-06-06 | SÍ | Mantener intacto |
| [`uploads/EERR BARINAS ENERO.xlsx`](file:///C:/Users/andre/Desktop/ultrax_app/uploads/EERR BARINAS ENERO.xlsx) | E | 10.83 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener en `uploads/` |
| [`uploads/EERR LOS NARANJOS ENERO.xlsx`](file:///C:/Users/andre/Desktop/ultrax_app/uploads/EERR LOS NARANJOS ENERO.xlsx) | E | 10.51 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener en `uploads/` |
| [`uploads/EERR PIEDEMONTE ENERO.xlsx`](file:///C:/Users/andre/Desktop/ultrax_app/uploads/EERR PIEDEMONTE ENERO.xlsx) | E | 10.52 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener en `uploads/` |
| [`uploads/EERR RODEO ENERO.xlsx`](file:///C:/Users/andre/Desktop/ultrax_app/uploads/EERR RODEO ENERO.xlsx) | E | 10.70 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener en `uploads/` |
| [`uploads/EERR TERRACOTA ENERO.xlsx`](file:///C:/Users/andre/Desktop/ultrax_app/uploads/EERR TERRACOTA ENERO.xlsx) | E | 11.21 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener en `uploads/` |
| [`uploads/EERR UCAFE ENERO.xlsx`](file:///C:/Users/andre/Desktop/ultrax_app/uploads/EERR UCAFE ENERO.xlsx) | E | 10.29 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener en `uploads/` |
| [`uploads/ESTADO DE RESULTADOS ODOO COMPROBACION1.xlsx`](file:///C:/Users/andre/Desktop/ultrax_app/uploads/ESTADO DE RESULTADOS ODOO COMPROBACION1.xlsx) | E | 16.47 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener en `uploads/` |
| [`uploads/Financial report - 2026-06-05T224211.230.xlsx`](file:///C:/Users/andre/Desktop/ultrax_app/uploads/Financial report - 2026-06-05T224211.230.xlsx) | E | 7.48 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener en `uploads/` |
| [`validacion_correcion_parent_name.md`](file:///C:/Users/andre/Desktop/ultrax_app/validacion_correcion_parent_name.md) | E | 1.89 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`validacion_metadata_fase1.md`](file:///C:/Users/andre/Desktop/ultrax_app/validacion_metadata_fase1.md) | E | 14.62 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`validar_subtotal_rrhh.py`](file:///C:/Users/andre/Desktop/ultrax_app/validar_subtotal_rrhh.py) | D | 2.51 KB | No commit history (untracked) | SÍ (Test/Utility) | Mantener intacto en raíz (o agrupar en `tests/` en un refactor futuro) |
| [`validate_parents.py`](file:///C:/Users/andre/Desktop/ultrax_app/validate_parents.py) | D | 1.85 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (o agrupar en `tests/` en un refactor futuro) |
| [`validate_v2_integrity_suite.py`](file:///C:/Users/andre/Desktop/ultrax_app/validate_v2_integrity_suite.py) | D | 2.64 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (o agrupar en `tests/` en un refactor futuro) |
| [`verificacion_jerarquia_eerr.md`](file:///C:/Users/andre/Desktop/ultrax_app/verificacion_jerarquia_eerr.md) | E | 33.92 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`verificacion_mecanismos_calculo.md`](file:///C:/Users/andre/Desktop/ultrax_app/verificacion_mecanismos_calculo.md) | E | 5.85 KB | 2026-06-12 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`~$2 EEFF ULTRAX Rodeo.xlsx`](file:///C:/Users/andre/Desktop/ultrax_app/~$2 EEFF ULTRAX Rodeo.xlsx) | E | 0.16 KB | 2026-06-06 | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |
| [`~$EEFF ULTRAX 2026.xlsx`](file:///C:/Users/andre/Desktop/ultrax_app/~$EEFF ULTRAX 2026.xlsx) | E | 0.16 KB | No commit history (untracked) | SÍ (Test/Utility) | Mantener intacto en raíz (Documentación) |