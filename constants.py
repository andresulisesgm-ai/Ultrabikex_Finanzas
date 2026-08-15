MONTHS = ['ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEPT','OCT','NOV','DIC']
UNITS  = ['Rodeo', 'PiedeMonte', 'Terracota', 'Ucafe', 'Barinas', 'Naranjos']

ESF_PLUG_VARIACION_UMBRAL = 0.25

# ── %Vtas segmentado para Costo de Ventas / Utilidad Bruta por segmento ──
# Estas partidas dividen %Vtas contra el ingreso de su propio segmento
# (Mercancia+Taller, Servicios o Eventos) en vez del Total Ingresos general.
# Spec confirmado contra formulas de ESF_EJEMPLO.xlsx, hoja "EERR RODEO".
PARTIDAS_DIVISOR_SEGMENTADO = {
    'Subtotal Costo de Ventas por Mercancia': 'mercancia_taller',
    'Costos de venta por mercancia': 'mercancia_taller',
    'Utilidad Bruta por Venta de Mercancia y Taller': 'mercancia_taller',
    'Subtotal Costo de Ventas por Servicios': 'servicios',
    'Costo de venta por servicio del café': 'servicios',
    'Utilidad Bruta por Servicios': 'servicios',
    'Subtotal Costo de Ventas por Eventos': 'eventos',
    'Costo de ventas por eventos': 'eventos',
    'Utilidad Bruta por Eventos': 'eventos',
}

# Claves de subtotales_por_mes[m] (ya calculadas via EERR_STRUCTURE) por segmento.
SUBTOTAL_INGRESO_KEYS_POR_SEGMENTO = {
    'mercancia_taller': ['Subtotal Ingresos por Venta de Mercancia', 'Subtotal Ingresos por Taller'],
    'servicios': ['Subtotal Ingresos por Servicios'],
    'eventos': ['Subtotal Ingresos por Eventos'],
}

# Partidas hoja por segmento (mismo universo que arma EERR_STRUCTURE para
# los subtotales de arriba), usadas contra datos crudos: by_budget y by_prev_raw.
SEGMENTOS_INGRESO_PCT_VTAS = {
    'mercancia_taller': [
        'Ingresos por venta de mercancias',
        'Devoluciones sobre ventas',
        'Descuentos sobre ventas',
        'Ingresos por taller',
    ],
    'servicios': [
        'Ingresos por servicios del café',
        'Ingresos por zona FIT',
        'Ingresos por fletes',
        'Ingresos por otros servicios',
    ],
    'eventos': [
        'Ingresos por eventos',
    ],
}
