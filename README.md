# ULTRAX — Sistema Financiero

App web local para consolidación financiera multi-unidad.

## Requisitos

- Python 3.10 o superior
- pip

## Instalación (solo la primera vez)

```bash
cd ultrax_app
pip install -r requirements.txt
```

## Arrancar la app

```bash
python app.py
```

Luego abre el navegador en: **http://localhost:5000**

La app corre localmente. Nadie fuera de tu red puede acceder.

## Uso mes a mes

1. **Cargar Reportes** → selecciona unidad, mes y año → sube el XLS de Odoo → clic en Procesar.
2. Repite para cada unidad del mes.
3. **Dashboard** se actualiza automáticamente.
4. **Exportar Excel** genera el Eff Ultrax completo descargable.

## Agregar cuentas nuevas de Odoo

1. Ve a **Mapeo de Cuentas**.
2. Clic en **+ Nueva cuenta**.
3. Ingresa el código Odoo (ej: `6.01.01.01.025`), el nombre en Odoo, la partida exacta del formato Eff Ultrax, y el signo (Ingreso o Gasto/Costo).
4. Guardar. Desde ese momento todos los reportes futuros incluirán esa cuenta.

## Unidades de negocio

- Rodeo
- PiedeMonte
- Terracota
- Ucafe
- Barinas
- Naranjos

## Datos

La base de datos vive en `data/ultrax.db` (SQLite). Haz backup de este archivo periódicamente.
