import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import os, tempfile
from datetime import datetime

MONTHS = ['ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEPT','OCT','NOV','DIC']

MONTH_TO_QUARTER = {
    'ENE': 1, 'FEB': 1, 'MAR': 1,
    'ABR': 2, 'MAY': 2, 'JUN': 2,
    'JUL': 3, 'AGO': 3, 'SEPT': 3,
    'OCT': 4, 'NOV': 4, 'DIC': 4,
}

# ── EERR Structure ──────────────────────────────────────────────────────
# Nueva EERR_STRUCTURE extraída de EJEMPLO EERR.xlsx (hoja EERR LOS NA)
# Formato: (partida_name, is_header, parent, bold, bg_color, level, es_nota)
# Colores: FF6AD9E8 (azul claro), FF66FF66 (verde), FFFFFF00 (amarillo)

EERR_STRUCTURE = [
    ('Total Ingresos', True, None, True, 'FF6AD9E8', 0, False, None, 0),
    ('Subtotal Ingresos por Venta de Mercancia', True, None, True, None, 1, False, None, 1),
    ('Ingresos por venta de mercancias', False, None, False, None, 3, True, 'Subtotal Ingresos por Venta de Mercancia', 3),
    ('Devoluciones sobre ventas', False, None, False, None, 3, False, None, 2),
    ('Descuentos sobre ventas', False, None, False, None, 3, False, None, 2),
    ('Subtotal Ingresos por Servicios', True, None, True, None, 1, False, None, 1),
    ('Ingresos por servicios del café', False, None, False, None, 3, False, None, 2),
    ('Ingresos por zona FIT', False, None, False, None, 3, False, None, 2),
    ('Ingresos por fletes', False, None, False, None, 3, False, None, 2),
    ('Ingresos por otros servicios', False, None, False, None, 3, False, None, 2),
    ('Subtotal Ingresos por Eventos', True, None, True, None, 1, False, None, 1),
    ('Ingresos por eventos', False, None, False, None, 3, False, None, 2),
    ('Subtotal Ingresos por Taller', True, None, True, None, 1, False, None, 1),
    ('Ingresos por taller', False, None, False, None, 3, False, None, 2),
    ('Total Costo de Ventas', True, None, True, None, 0, False, None, 0),
    ('Subtotal Costo de Ventas por Mercancia', True, None, True, None, 1, False, None, 1),
    ('Costos de venta por mercancia', False, None, False, None, 3, True, 'Subtotal Costo de Ventas por Mercancia', 3),
    ('Subtotal Costo de Ventas por Servicios', True, None, True, None, 1, False, None, 1),
    ('Costo de venta por servicio del café', False, None, False, None, 3, False, None, 2),
    ('Subtotal Costo de Ventas por Eventos', True, None, True, None, 1, False, None, 1),
    ('Costo de ventas por eventos', False, None, False, None, 3, False, None, 2),
    ('Utilidad Bruta por Venta de Mercancia y Taller', True, None, True, 'FF66FF66', 0, False, None, 0),
    ('Utilidad Bruta por Servicios', True, None, True, 'FF66FF66', 0, False, None, 0),
    ('Utilidad Bruta por Eventos', True, None, True, 'FF66FF66', 0, False, None, 0),
    ('Utilidad Bruta', True, None, True, 'FF66FF66', 0, False, None, 0),
    ('Total Gastos Operacionales', True, None, True, None, 0, False, None, 0),
    ('Subtotal Gastos de Administración', True, None, True, None, 1, False, None, 1),
    ('Gastos de servicios públicos (Agua, luz, Aseo Urbano)', False, None, False, None, 3, False, None, 2),
    ('Gastos de servicios de telefonía e internet', False, None, False, None, 3, False, None, 2),
    ('Gastos de alquiler del local', False, None, False, None, 3, False, None, 2),
    ('Gastos de Condominio', False, None, False, None, 3, False, None, 2),
    ('Gastos de asistencia outsorcing', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de alquiler de bienes muebles', False, None, False, None, 3, False, None, 2),
    ('Gastos de artículos de oficina', False, None, False, None, 3, False, None, 2),
    ('Gastos de artículos de limpieza e higiene', False, None, False, None, 3, False, None, 2),
    ('Gastos de alimentos y bebidas', False, None, False, None, 3, False, None, 2),
    ('Gastos de envíos y encomiendas administrativas', False, None, False, None, 3, False, None, 2),
    ('Gastos de honorarios profesionales', False, None, False, None, 3, False, None, 2),
    ('Gastos de estacionamiento', False, None, False, None, 3, False, None, 2),
    ('Gastos de gestoría', False, None, False, None, 3, False, None, 2),
    ('Gastos legales', False, None, False, None, 3, False, None, 2),
    ('Gastos de taxi, transporte y/o delivery', False, None, False, None, 3, False, None, 2),
    ('Gastos de suministros para taller', False, None, False, None, 3, False, None, 2),
    ('Gastos de suministros del café', False, None, False, None, 3, False, None, 2),
    ('Gastos por fiestas, festejos y/o reuniones', False, None, False, None, 3, False, None, 2),
    ('Gastos de vigilancia', False, None, False, None, 3, False, None, 2),
    ('Gastos de retenciones no descontadas', False, None, False, None, 3, False, None, 2),
    ('Mantenimiento y reparaciones', False, None, False, None, 3, False, None, 2),
    ('Gastos de mantenimiento y reparación a la propiedad alq.', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de mantenimiento y reparación de edificaciones', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de mantenimiento y reparación de maquinaria y equipos', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de mantenimiento y reparación de mobiliario y equipo', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de mantenimiento y reparación de vehiculo', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Viáticos administrativos', False, None, False, None, 3, False, None, 2),
    ('Gastos de comida por viáticos administrativos', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de hospedaje por viáticos administrativos', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de pasajes por viáticos administrativos', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de transporte por viáticos administrativos', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Otros gastos de viáticos administrativos', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de seguro', False, None, False, None, 3, False, None, 2),
    ('Gastos de seguro de edificaciones', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de seguro de vehiculos', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de impuestos, tasas y contribuciones', False, None, False, None, 3, False, None, 2),
    ('Gasto por otras tasas', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de impuesto por licencia de actividades economicas', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de impuesto por publicidad', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de patente vehicular', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de tasa sencamer', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de tasas de notaria y registro', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Depreciaciones, deterioro y Amortización', False, None, False, None, 3, False, None, 2),
    ('Gastos de amortización de software', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de depreciación de edificaciones', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de depreciación de maquinarias y equipos', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de depreciación de mobiliario y equipo', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de depreciación de vehículos', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de deterioro de edificaciones', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de deterioro de maquinarias y equipos', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de deterioro de mobiliario y equipo', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de deterioro de vehículos', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de deterioro por cuentas incobrables', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gasto por impuesto a las pensiones', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos Bancarios', False, None, False, None, 3, False, None, 2),
    ('Gastos de IGTF', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de comisiones bancarias', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de intereses de mora', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de intereses sobre préstamos', False, None, False, None, 3, False, None, 2),
    ('Gastos de intereses sobre préstamos bancarios', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Gastos de intereses sobre préstamos de terceros', False, None, False, None, 3, True, 'Subtotal Gastos de Administración', 3),
    ('Subtotal Gastos de Recursos Humanos', True, None, True, None, 1, False, None, 1),
    ('Gastos de sueldos y salarios empleados y directivos', True, None, False, None, 2, False, 'Subtotal Gastos de Recursos Humanos', 2),
    ('Gastos de sueldos y salarios empleados', False, None, False, None, 3, True, 'Gastos de sueldos y salarios empleados y directivos', 3),
    ('Gastos de sueldos y salarios directivos', False, None, False, None, 3, True, 'Gastos de sueldos y salarios empleados y directivos', 3),
    ('Gastos de horas extras, feriados y bono nocturno', False, None, False, None, 3, True, 'Gastos de sueldos y salarios empleados y directivos', 3),
    ('Gastos de Bono de alimentación empleados', False, None, False, None, 3, True, 'Gastos de sueldos y salarios empleados y directivos', 3),
    ('Gastos de Bono de alimentación directivos', False, None, False, None, 3, True, 'Gastos de sueldos y salarios empleados y directivos', 3),
    ('Gastos de vacaciones empleados', False, None, False, None, 3, True, 'Gastos de sueldos y salarios empleados y directivos', 3),
    ('Gastos de vacaciones directivos', False, None, False, None, 3, True, 'Gastos de sueldos y salarios empleados y directivos', 3),
    ('Gastos de complementos empleados y directivos', True, None, False, None, 2, False, 'Subtotal Gastos de Recursos Humanos', 2),
    ('Gastos de complemento de sueldos y salarios empleados', False, None, False, None, 3, True, 'Gastos de complementos empleados y directivos', 3),
    ('Gastos de complemento de sueldos y salarios directivos', False, None, False, None, 3, True, 'Gastos de complementos empleados y directivos', 3),
    ('Gastos de complemento de vacaciones empleados', False, None, False, None, 3, True, 'Gastos de complementos empleados y directivos', 3),
    ('Gastos de complemento de vacaciones directivos', False, None, False, None, 3, True, 'Gastos de complementos empleados y directivos', 3),
    ('Gastos de otros bonos empleados', False, None, False, None, 3, True, 'Gastos de complementos empleados y directivos', 3),
    ('Gastos de personal externo', True, None, False, None, 2, False, 'Subtotal Gastos de Recursos Humanos', 2),
    ('Gastos de servicios de personal externo', False, None, False, None, 3, True, 'Gastos de personal externo', 3),
    ('Gastos de pasivos laborales vacaciones', True, None, False, None, 2, False, 'Subtotal Gastos de Recursos Humanos', 2),
    ('Gastos de bono vacacional empleados', False, None, False, None, 3, True, 'Gastos de pasivos laborales vacaciones', 3),
    ('Gastos de bono vacacional directivos', False, None, False, None, 3, True, 'Gastos de pasivos laborales vacaciones', 3),
    ('Gastos de complemento bono vacacional empleados', False, None, False, None, 3, True, 'Gastos de pasivos laborales vacaciones', 3),
    ('Gastos de complemento bono vacacional directivos', False, None, False, None, 3, True, 'Gastos de pasivos laborales vacaciones', 3),
    ('Gastos de pasivos laborales utilidades', True, None, False, None, 2, False, 'Subtotal Gastos de Recursos Humanos', 2),
    ('Gastos de utilidades empleados', False, None, False, None, 3, True, 'Gastos de pasivos laborales utilidades', 3),
    ('Gastos de utilidades directivos', False, None, False, None, 3, True, 'Gastos de pasivos laborales utilidades', 3),
    ('Gastos de complemento de utilidades empleados', False, None, False, None, 3, True, 'Gastos de pasivos laborales utilidades', 3),
    ('Gastos de complemento de utilidades directivos', False, None, False, None, 3, True, 'Gastos de pasivos laborales utilidades', 3),
    ('Gastos de pasivos laborales prestaciones e intereses', True, None, False, None, 2, False, 'Subtotal Gastos de Recursos Humanos', 2),
    ('Gastos de prestaciones sociales empleados', False, None, False, None, 3, True, 'Gastos de pasivos laborales prestaciones e intereses', 3),
    ('Gastos de prestaciones sociales directivos', False, None, False, None, 3, True, 'Gastos de pasivos laborales prestaciones e intereses', 3),
    ('Gastos de complemento de prestaciones sociales empleados', False, None, False, None, 3, True, 'Gastos de pasivos laborales prestaciones e intereses', 3),
    ('Gastos de complemento de prestaciones sociales directivos', False, None, False, None, 3, True, 'Gastos de pasivos laborales prestaciones e intereses', 3),
    ('Gastos de intereses sobres prestaciones sociales empleados', False, None, False, None, 3, True, 'Gastos de pasivos laborales prestaciones e intereses', 3),
    ('Gastos de intereses sobres prestaciones sociales directivos', False, None, False, None, 3, True, 'Gastos de pasivos laborales prestaciones e intereses', 3),
    ('Gastos de complemento de intereses sobre prestaciones sociales empleados', False, None, False, None, 3, True, 'Gastos de pasivos laborales prestaciones e intereses', 3),
    ('Gastos de complemento de intereses sobre prestaciones sociales directivos', False, None, False, None, 3, True, 'Gastos de pasivos laborales prestaciones e intereses', 3),
    ('Gastos de pasivos laborales aportes', True, None, False, None, 2, False, 'Subtotal Gastos de Recursos Humanos', 2),
    ('Gastos de aporte patronal IVSS', False, None, False, None, 3, True, 'Gastos de pasivos laborales aportes', 3),
    ('Gastos de aporte patronal SPF', False, None, False, None, 3, True, 'Gastos de pasivos laborales aportes', 3),
    ('Gastos de aporte patronal FAOV', False, None, False, None, 3, True, 'Gastos de pasivos laborales aportes', 3),
    ('Gastos de aporte patronal INCES', False, None, False, None, 3, True, 'Gastos de pasivos laborales aportes', 3),
    ('Gastos de pasivos laborales bono de guardería', True, None, False, None, 2, False, 'Subtotal Gastos de Recursos Humanos', 2),
    ('Gastos de bono de guardería', False, None, False, None, 3, True, 'Gastos de pasivos laborales bono de guardería', 3),
    ('Gastos de pasivos laborales HCM', True, None, False, None, 2, False, 'Subtotal Gastos de Recursos Humanos', 2),
    ('Gastos de póliza HCM', False, None, False, None, 3, True, 'Gastos de pasivos laborales HCM', 3),
    ('Gastos de salud y seguridad laboral', False, None, False, None, 2, False, 'Subtotal Gastos de Recursos Humanos', 2),
    ('Gastos de salud y seguridad laboral dotación', False, None, False, None, 2, False, 'Subtotal Gastos de Recursos Humanos', 2),
    ('Gastos de uniformes y dotación al personal', False, None, False, None, 3, True, 'Gastos de salud y seguridad laboral dotación', 3),
    ('Gastos de salud y seguridad laboral fiestas y agasajos', True, None, False, None, 2, False, 'Subtotal Gastos de Recursos Humanos', 2),
    ('Gastos de fiestas y agasajos al personal', False, None, False, None, 3, True, 'Gastos de salud y seguridad laboral fiestas y agasajos', 3),
    ('Otros gastos de personal', True, None, False, None, 2, False, 'Subtotal Gastos de Recursos Humanos', 2),
    ('Gastos de transporte del personal', False, None, False, None, 3, True, 'Otros gastos de personal', 3),
    ('Gastos de donaciones y obsequios al personal', False, None, False, None, 3, True, 'Otros gastos de personal', 3),
    ('Gastos de capacitación al personal', False, None, False, None, 3, True, 'Otros gastos de personal', 3),
    ('Subtotal Gastos de Comercialización y Logistica', True, None, True, None, 1, False, None, 1),
    ('Gastos de viáticos comerciales', False, None, False, None, 3, False, None, 2),
    ('Gastos de comida por viáticos comerciales', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Gastos de hospedaje por viáticos comerciales', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Gastos de pasajes por viáticos comerciales', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Gastos de transporte por viáticos comerciales', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Otros gastos de viáticos comerciales', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Gastos de comisiones empleados del taller', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Gastos de fletes y envios no asociados al costo', False, None, False, None, 3, False, None, 2),
    ('Otros gastos no asociados al costo', False, None, False, None, 3, False, None, 2),
    ('Gastos de almacenaje sobre compras no incluídos en el costo', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Gastos de armado de bicicletas no incluídos en el costo', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Gastos de bolsas no incluídos en el costo', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Gastos de embalaje no incluídos en el costo', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Gastos de etiquetas no incluídos en el costo', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Gastos de importación no incluídos en el costo', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Gastos de seguro de mercancía no incluídos en el costo', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Gastos de títulos de propiedad no incluídos en el costo', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Gastos por combustible', False, None, False, None, 3, False, None, 2),
    ('Gastos por gasoil', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Gastos por gasolina', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Gastos de representación', False, None, False, None, 3, False, None, 2),
    ('Gastos por garantia', False, None, False, None, 3, False, None, 2),
    ('Gastos por suscripciones', False, None, False, None, 3, False, None, 2),
    ('Gastos de Stand y/o ferias comerciales', False, None, False, None, 3, False, None, 2),
    ('Gastos de alquiler Stand y/o ferias comerciales', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Gastos de otros viáticos Stand y/o ferias comerciales', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Gastos de pasajes Stand y/o ferias comerciales', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Gastos de premiaciones, donaciones Stand y/o ferias comerciales', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Gastos de publicidad Stand y/o ferias comerciales', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Gastos de viáticos comida Stand y/o ferias comerciales', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Gastos de viáticos hospedaje Stand y/o ferias comerciales', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Gastos de viáticos transporte Stand y/o ferias comerciales', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Subtotal Gastos de Mercadeo', True, None, True, None, 1, False, None, 1),
    ('Gastos de redes sociales', False, None, False, None, 3, False, None, 2),
    ('Gastos de medios publicitarios', False, None, False, None, 3, False, None, 2),
    ('Otros gastos de publicidad y promoción', False, None, False, None, 3, False, None, 2),
    ('Gastos de impresiones de material gráfico', False, None, False, None, 3, True, 'Subtotal Gastos de Mercadeo', 3),
    ('Gastos de decoración', False, None, False, None, 3, True, 'Subtotal Gastos de Mercadeo', 3),
    ('Gastos de muestras y material POP', False, None, False, None, 3, True, 'Subtotal Gastos de Mercadeo', 3),
    ('Gastos de campañas y lanzamientos', False, None, False, None, 3, True, 'Subtotal Gastos de Mercadeo', 3),
    ('Gastos de patrocinio y donación', False, None, False, None, 3, False, None, 2),
    ('Gastos de patrocinio, donación y/o obsequios en efectivo', False, None, False, None, 3, True, 'Subtotal Gastos de Mercadeo', 3),
    ('Gastos de patrocinio, donación y/o obsequios en productos', False, None, False, None, 3, True, 'Subtotal Gastos de Mercadeo', 3),
    ('Gastos de viáticos por eventos', False, None, False, None, 3, False, None, 2),
    ('Gastos de materiales y servicios por eventos', False, None, False, None, 3, False, None, 2),
    ('Gastos de alimentos y bebidas por eventos', False, None, False, None, 3, False, None, 2),
    ('Gastos de personal por eventos', False, None, False, None, 3, False, None, 2),
    ('Gastos de patrocinio, donación y/o obseq por eventos', False, None, False, None, 3, False, None, 2),
    ('Gastos de TI+I', True, None, True, None, 1, False, None, 1),
    ('Gastos de página web', False, None, False, None, 3, False, None, 2),
    ('Gastos de dominio de página web', False, None, False, None, 3, True, 'Gastos de TI+I', 3),
    ('Gastos de servidores', False, None, False, None, 3, True, 'Gastos de TI+I', 3),
    ('Gastos de desarrollo', False, None, False, None, 3, False, None, 2),
    ('Gastos de software tecnológico', False, None, False, None, 3, True, 'Gastos de TI+I', 3),
    ('Utilidad antes de Comisiones por Ventas', True, None, True, 'FF66FF66', 0, False, None, 0),
    ('Gastos de comisiones por ventas', False, None, False, None, 3, False, None, 2),
    ('Gastos de comisiones empleados', False, None, False, None, 3, True, 'Gastos de comisiones por ventas', 3),
    ('Gastos de comisiones por venta de personal externo', False, None, False, None, 3, True, 'Gastos de comisiones por ventas', 3),
    ('Gastos de comisiones por ventas taller', False, None, False, None, 3, False, None, 2),
    ('Utilidad después de Comisiones por Ventas', True, None, True, 'FF66FF66', 0, False, None, 0),
    ('Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA)', True, None, True, 'FF66FF66', 0, False, None, 0),
    ('Utilidad antes de Intereses e Impuestos (EBIT)', True, None, True, 'FF66FF66', 0, False, None, 0),
    ('Otros Gastos no Operacionales', True, None, True, None, 0, False, None, 0),
    ('Faltante en Ventas', False, None, False, None, 3, False, None, 2),
    ('Pérdida en venta de activos', False, None, False, None, 3, False, None, 2),
    ('Pérdida en siniestro de activos', False, None, False, None, 3, False, None, 2),
    ('Pérdida en tasa cambiaria', False, None, False, None, 3, False, None, 2),
    ('Pérdida por diferencia en pagos', False, None, False, None, 3, False, None, 2),
    ('Multas', False, None, False, None, 3, False, None, 2),
    ('Faltante y deterioro de inventarios', False, None, False, None, 3, False, None, 2),
    ('Deterioro de inventarios', False, None, False, None, 3, True, 'Otros Gastos no Operacionales', 3),
    ('Faltante de inventarios', False, None, False, None, 3, True, 'Otros Gastos no Operacionales', 3),
    ('Total Gastos Operacionales y No Operacionales', True, None, True, 'FFFFFF00', 0, False, None, 0),
    ('Otros Ingresos no Operacionales', True, None, True, None, 0, False, None, 1),
    ('Ingresos por alquileres', False, None, False, None, 3, False, None, 2),
    ('Ingresos por intereses', False, None, False, None, 3, False, None, 2),
    ('Ingresos por comisiones', False, None, False, None, 3, False, None, 2),
    ('Ingresos por servicios administrativos', False, None, False, None, 3, False, None, 2),
    ('Sobrante en ventas', False, None, False, None, 3, False, None, 2),
    ('Sobrante de inventarios', False, None, False, None, 3, False, None, 2),
    ('Ganancia en venta de activos', False, None, False, None, 3, False, None, 2),
    ('Ganancia por tasa cambiaria', False, None, False, None, 3, False, None, 2),
    ('Ganancia por diferencias en pagos', False, None, False, None, 3, False, None, 2),
    ('Utilidad Neta', True, None, True, 'FF66FF66', 0, False, None, 0),
    ('ISLR', True, None, True, None, 0, False, None, 0),
    ('Utilidad Neta despues de ISLR', True, None, True, 'FF66FF66', 0, False, None, 0),
]

# ── ESF Structure ─────────────────────────────────────────────────────────────

class OdooParser:
    """
    Parsea el reporte de balance de comprobación de Odoo.
    Detecta automáticamente si la cuenta es de resultado (4/5/6)
    o de balance (1/2/3) para rutear el insert correctamente.
    """
    def __init__(self, path):
        self.path = path
        self.names = {}

    def parse(self):
        """
        Retorna dict: {code: amount}
        Para cuentas 4/5/6: amount es el saldo del período.
        Para cuentas 1/2/3: amount es el saldo acumulado (snapshot).
        El ruteo al destino (financials vs esf_data) lo hace el caller.
        """
        accounts = {}
        try:
            df = pd.read_excel(self.path, header=None, engine='openpyxl')
        except Exception:
            df = pd.read_excel(self.path, header=None)

        for _, row in df.iterrows():
            cell = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ''
            cell = cell.strip()
            if cell and cell[0].isdigit() and '.' in cell[:5]:
                parts = cell.split(' ', 1)
                if len(parts) == 2:
                    code = parts[0].strip()
                    name = parts[1].strip()
                    try:
                        balance = float(row.iloc[2]) if pd.notna(row.iloc[2]) else 0.0
                    except (ValueError, IndexError):
                        balance = 0.0
                    accounts[code] = balance
                    self.names[code] = name
        return accounts

    @staticmethod
    def is_balance_account(code):
        """True si la cuenta es de balance (activo/pasivo/patrimonio)."""
        return code.startswith('1.') or code.startswith('2.') or code.startswith('3.')

    @staticmethod
    def month_to_quarter(month):
        return MONTH_TO_QUARTER.get(month, 1)


def build_effective_structure(static_structure=None, db_overrides=None):
    """
    Combina la estructura estática por defecto (EERR_STRUCTURE) con los overrides
    de la base de datos (eerr_nodes). En Fase 1 db_overrides es vacío.
    """
    if static_structure is None:
        static_structure = EERR_STRUCTURE
    if db_overrides is None:
        db_overrides = []

    effective = []
    # Límites operacionales en la lista estática
    start_idx = -1
    end_idx = -1
    for idx, entry in enumerate(static_structure):
        if entry[0] == 'Subtotal Gastos de Administración':
            start_idx = idx
        if entry[0] == 'Gastos de desarrollo':
            end_idx = idx

    for idx, item in enumerate(static_structure):
        name = item[0]
        is_hdr = item[1]
        parent = item[2]
        bold = item[3]
        bg_color = item[4]
        level = item[5] if len(item) > 5 else (0 if is_hdr else 3)
        es_nota = item[6] if len(item) > 6 else False
        parent_name = item[7] if len(item) > 7 else None
        indent = item[8] if len(item) > 8 else (3 if es_nota else (1 if is_hdr else 2))

        # Determinar movible
        # 4.1 Bloqueados por exclusión hardcodeada:
        blocked_leaves = {
            'Gasto por impuesto a las pensiones',
            'Gastos de IGTF',
            'Gastos de comisiones bancarias',
            'Gastos de impresiones de material gráfico',
            'Gastos de patrocinio y donación'
        }
        
        # 4.2 Subtotales con membresía fija (bloqueados para el HEADER):
        blocked_headers = {
            'Subtotal Gastos de Administración',
            'Subtotal Gastos de Recursos Humanos',
            'Subtotal Gastos de Comercialización y Logistica',
            'Subtotal Gastos de Mercadeo',
            'Gastos de TI+I'
        }

        movible = 'bloqueado'
        if start_idx != -1 and end_idx != -1 and start_idx <= idx <= end_idx:
            # Está en la zona operativa de gastos
            if is_hdr:
                if name in blocked_headers:
                    movible = 'bloqueado'
                else:
                    movible = 'libre' # Otros headers intermedios
            else:
                if name in blocked_leaves:
                    movible = 'bloqueado'
                else:
                    movible = 'libre'

        node_dict = {
            'partida_name': name,
            'is_header': is_hdr,
            'level': level,
            'bold': bold,
            'bg_color': bg_color,
            'es_nota': es_nota,
            'parent_name': parent_name,
            'indent': indent,
            'movible': movible
        }
        effective.append(node_dict)

    # Aplicar reubicación por overrides
    if db_overrides:
        import logging
        logger = logging.getLogger('eerr_v2_overrides')
        
        all_leaves = [n for n in effective if not n['is_header']]
        leaf_names = [n['partida_name'] for n in all_leaves]
        
        blocked_leaves = {
            'Gasto por impuesto a las pensiones',
            'Gastos de IGTF',
            'Gastos de comisiones bancarias',
            'Gastos de impresiones de material gráfico',
            'Gastos de patrocinio y donación'
        }
        
        target_subtotals = {
            'Subtotal Gastos de Administración',
            'Subtotal Gastos de Recursos Humanos',
            'Subtotal Gastos de Comercialización y Logistica',
            'Subtotal Gastos de Mercadeo',
            'Gastos de TI+I'
        }
        
        for override in db_overrides:
            if isinstance(override, dict):
                p_name = override.get('partida_name')
                target = override.get('target_subtotal')
            elif hasattr(override, 'keys'):
                p_name = override['partida_name']
                target = override['target_subtotal']
            else:
                p_name = override[0]
                target = override[1]
                
            if not p_name or not target:
                continue
                
            # Validaciones obligatorias
            if target not in target_subtotals:
                logger.warning(f"Rechazado override: Subtotal destino '{target}' inválido.")
                continue
                
            if p_name not in leaf_names:
                logger.warning(f"Rechazado override: Partida '{p_name}' no existe como hoja en EERR.")
                continue
                
            if leaf_names.count(p_name) > 1:
                logger.warning(f"Rechazado override: Partida '{p_name}' está duplicada y no se puede mover.")
                continue
                
            if p_name in blocked_leaves:
                logger.warning(f"Rechazado override: Partida '{p_name}' está bloqueada (no movible).")
                continue
                
            # Localizar el nodo hoja
            node_idx = -1
            for idx, n in enumerate(effective):
                if n['partida_name'] == p_name and not n['is_header']:
                    node_idx = idx
                    break
                    
            if node_idx == -1:
                continue
                
            node_to_move = effective.pop(node_idx)
            
            # Localizar el subtotal destino
            target_idx = -1
            for idx, n in enumerate(effective):
                if n['partida_name'] == target and n['is_header']:
                    target_idx = idx
                    break
                    
            if target_idx == -1:
                logger.warning(f"Rechazado override: Subtotal '{target}' no se encontró en la estructura.")
                effective.insert(node_idx, node_to_move) # Restaurar
                continue
                
            # Encontrar el final de los hijos actuales del subtotal destino
            insert_idx = target_idx + 1
            target_level = effective[target_idx]['level']
            
            while insert_idx < len(effective):
                n = effective[insert_idx]
                if n['level'] <= target_level:
                    break
                insert_idx += 1
                
            # Actualizar parent, level e indentación
            node_to_move['parent_name'] = target
            node_to_move['level'] = 3
            node_to_move['indent'] = 2
            node_to_move['es_nota'] = False
            
            # Insertar en la nueva posición
            effective.insert(insert_idx, node_to_move)

    return effective

# ── ESF Structure V2 ─────────────────────────────────────────────────────────
# Formato: (nombre, is_header, parent, bold, bg_color, level, es_nota, parent_name, indent)
ESF_STRUCTURE_V2 = [
    # ACTIVOS
    ('TOTAL ACTIVOS', True, None, True, None, 0, False, None, 0),
    ('ACTIVOS CORRIENTES', True, None, True, None, 1, False, None, 1),
    ('Efectivo y Equivalentes', True, None, True, None, 2, False, 'ACTIVOS CORRIENTES', 2),
    ('Caja en Bs', False, None, False, None, 3, False, 'Efectivo y Equivalentes', 3),
    ('Caja en $', False, None, False, None, 3, False, 'Efectivo y Equivalentes', 3),
    ('Fondo en Bs', False, None, False, None, 3, False, 'Efectivo y Equivalentes', 3),
    ('Fondo en $', False, None, False, None, 3, False, 'Efectivo y Equivalentes', 3),
    ('Bancos en Bs', False, None, False, None, 3, False, 'Efectivo y Equivalentes', 3),
    ('Bancos en $', False, None, False, None, 3, False, 'Efectivo y Equivalentes', 3),
    ('Bancos en transito en Bs', False, None, False, None, 3, False, 'Efectivo y Equivalentes', 3),
    ('Bancos en transito en $', False, None, False, None, 3, False, 'Efectivo y Equivalentes', 3),
    
    ('Cuentas por Cobrar', True, None, True, None, 2, False, 'ACTIVOS CORRIENTES', 2),
    ('Cuentas por cobrar clientes', False, None, False, None, 3, False, 'Cuentas por Cobrar', 3),
    ('A empresas relacionadas del grupo (CxC)', False, None, False, None, 3, False, 'Cuentas por Cobrar', 3),
    ('A empresas externas del grupo (CxC)', False, None, False, None, 3, False, 'Cuentas por Cobrar', 3),
    ('A socios (CxC)', False, None, False, None, 3, False, 'Cuentas por Cobrar', 3),
    ('Cuentas por cobrar empleados', False, None, False, None, 3, False, 'Cuentas por Cobrar', 3),
    
    ('Otras Cuentas por Cobrar', True, None, True, None, 2, False, 'ACTIVOS CORRIENTES', 2),
    ('Otras cuentas por cobrar', False, None, False, None, 3, False, 'Otras Cuentas por Cobrar', 3),
    ('Cuentas por cobrar por sociedades', False, None, False, None, 3, False, 'Otras Cuentas por Cobrar', 3),
    
    ('Préstamos por Cobrar', True, None, True, None, 2, False, 'ACTIVOS CORRIENTES', 2),
    ('A empresas relacionadas del grupo (PxC)', False, None, False, None, 3, False, 'Préstamos por Cobrar', 3),
    ('A empresas externas del grupo (PxC)', False, None, False, None, 3, False, 'Préstamos por Cobrar', 3),
    ('A socios (PxC)', False, None, False, None, 3, False, 'Préstamos por Cobrar', 3),
    ('A empleados (PxC)', False, None, False, None, 3, False, 'Préstamos por Cobrar', 3),
    ('Otros prestamos por cobrar', False, None, False, None, 3, False, 'Préstamos por Cobrar', 3),
    
    ('Anticipos', True, None, True, None, 2, False, 'ACTIVOS CORRIENTES', 2),
    ('Anticipos a proveedores', False, None, False, None, 3, False, 'Anticipos', 3),
    ('Anticipos a socios', False, None, False, None, 3, False, 'Anticipos', 3),
    ('Anticipos a empleados', False, None, False, None, 3, False, 'Anticipos', 3),
    
    ('Inventarios', True, None, True, None, 2, False, 'ACTIVOS CORRIENTES', 2),
    ('Inventario de mercancias', False, None, False, None, 3, False, 'Inventarios', 3),
    ('Inventario de suministros', False, None, False, None, 3, False, 'Inventarios', 3),
    ('Inventario en transito', False, None, False, None, 3, False, 'Inventarios', 3),
    ('Inventarios de Consignacion', False, None, False, None, 3, False, 'Inventarios', 3),
    
    ('Prepagados', True, None, True, None, 2, False, 'ACTIVOS CORRIENTES', 2),
    ('Impuestos pagados por anticipado', False, None, False, None, 3, False, 'Prepagados', 3),
    ('Gastos pagados por anticipado', False, None, False, None, 3, False, 'Prepagados', 3),
    
    ('Total Activos Corrientes', True, None, True, None, 1, False, 'ACTIVOS CORRIENTES', 1),
    
    ('ACTIVOS NO CORRIENTES', True, None, True, None, 1, False, None, 1),
    ('Otros activos no corrientes', True, None, True, None, 2, False, 'ACTIVOS NO CORRIENTES', 2),
    ('Cuentas por cobrar clientes L.P.', False, None, False, None, 3, False, 'Otros activos no corrientes', 3),
    ('Otras cuentas por cobrar L.P.', False, None, False, None, 3, False, 'Otros activos no corrientes', 3),
    ('Prestamos por cobrar L.P.', False, None, False, None, 3, False, 'Otros activos no corrientes', 3),
    ('Anticipos LP', False, None, False, None, 3, False, 'Otros activos no corrientes', 3),
    ('Propiedades de inversión', True, None, True, None, 3, False, 'Otros activos no corrientes', 3),
    ('Propiedades de Inversión', False, None, False, None, 4, False, 'Propiedades de inversión', 4),
    ('Propiedades, Plantas y Equipos', True, None, True, None, 2, False, 'ACTIVOS NO CORRIENTES', 2),
    ('Terrenos', False, None, False, None, 3, False, 'Propiedades, Plantas y Equipos', 3),
    ('Mobiliario y equipos', False, None, False, None, 3, False, 'Propiedades, Plantas y Equipos', 3),
    ('Maquinaria y equipos', False, None, False, None, 3, False, 'Propiedades, Plantas y Equipos', 3),
    ('Vehiculos', False, None, False, None, 3, False, 'Propiedades, Plantas y Equipos', 3),
    ('Edificios y construcciones', False, None, False, None, 3, False, 'Propiedades, Plantas y Equipos', 3),
    ('Materiales de eventos', False, None, False, None, 3, False, 'Propiedades, Plantas y Equipos', 3),
    ('Herramientas', False, None, False, None, 3, False, 'Propiedades, Plantas y Equipos', 3),
    ('Utensilios y equipos de cocina', False, None, False, None, 3, False, 'Propiedades, Plantas y Equipos', 3),
    ('Equipamiento deportivo', False, None, False, None, 3, False, 'Propiedades, Plantas y Equipos', 3),
    ('Mejoras a bienes arrendados', False, None, False, None, 3, False, 'Propiedades, Plantas y Equipos', 3),
    ('Software Odoo y Crm', False, None, False, None, 3, False, 'Propiedades, Plantas y Equipos', 3),
    ('Total Activos No Corrientes', True, None, True, None, 1, False, 'ACTIVOS NO CORRIENTES', 1),
    
    # PASIVOS
    ('PASIVOS CORRIENTES', True, None, True, None, 1, False, None, 1),
    ('Cuentas por Pagar', True, None, True, None, 2, False, 'PASIVOS CORRIENTES', 2),
    ('A proveedores', False, None, False, None, 3, False, 'Cuentas por Pagar', 3),
    ('A empresas relacionadas del grupo (CxP)', False, None, False, None, 3, False, 'Cuentas por Pagar', 3),
    ('A empresas externas del grupo (CxP)', False, None, False, None, 3, False, 'Cuentas por Pagar', 3),
    ('A socios (CxP)', False, None, False, None, 3, False, 'Cuentas por Pagar', 3),
    ('Cuentas por pagar TDD y TDC', False, None, False, None, 3, False, 'Cuentas por Pagar', 3),
    ('A proveedores en consignación', False, None, False, None, 3, False, 'Cuentas por Pagar', 3),
    
    ('Otras cuentas por pagar', True, None, True, None, 2, False, 'PASIVOS CORRIENTES', 2),
    ('Otras Cuentas por pagar', False, None, False, None, 3, False, 'Otras cuentas por pagar', 3),
    ('Descuentos a empleados por pagar', False, None, False, None, 3, False, 'Otras cuentas por pagar', 3),
    ('Sueldos y Salarios por pagar', False, None, False, None, 3, False, 'Otras cuentas por pagar', 3),
    ('Retenciones Laborales por pagar', False, None, False, None, 3, False, 'Otras cuentas por pagar', 3),
    ('Aportes patronales por pagar', False, None, False, None, 3, False, 'Otras cuentas por pagar', 3),
    ('Intereses por pagar', False, None, False, None, 3, False, 'Otras cuentas por pagar', 3),
    ('Impuestos por pagar', False, None, False, None, 3, False, 'Otras cuentas por pagar', 3),
    ('Dividendos por pagar', False, None, False, None, 3, False, 'Otras cuentas por pagar', 3),
    
    ('Préstamos por Pagar', True, None, True, None, 2, False, 'PASIVOS CORRIENTES', 2),
    ('A empresas relacionadas del grupo (PxP)', False, None, False, None, 3, False, 'Préstamos por Pagar', 3),
    ('A empresas externas del grupo (PxP)', False, None, False, None, 3, False, 'Préstamos por Pagar', 3),
    ('A socios (PxP)', False, None, False, None, 3, False, 'Préstamos por Pagar', 3),
    ('A empleados (PxP)', False, None, False, None, 3, False, 'Préstamos por Pagar', 3),
    ('Prestamos bancarios por pagar', False, None, False, None, 3, False, 'Préstamos por Pagar', 3),
    ('Otros prestamos por pagar', False, None, False, None, 3, False, 'Préstamos por Pagar', 3),
    
    ('Anticipos de Pasivo', True, None, True, None, 2, False, 'PASIVOS CORRIENTES', 2),
    ('De clientes', False, None, False, None, 3, False, 'Anticipos de Pasivo', 3),
    ('De socios', False, None, False, None, 3, False, 'Anticipos de Pasivo', 3),
    ('No reportados', False, None, False, None, 3, False, 'Anticipos de Pasivo', 3),
    
    ('Provisiones', True, None, True, None, 2, False, 'PASIVOS CORRIENTES', 2),
    ('Provisiones para empleados', False, None, False, None, 3, False, 'Provisiones', 3),
    
    ('Total Pasivos Corrientes', True, None, True, None, 1, False, 'PASIVOS CORRIENTES', 1),
    
    ('PASIVOS NO CORRIENTES', True, None, True, None, 1, False, None, 1),
    ('Otras cuentas por pagar L.P.', True, None, True, None, 2, False, 'PASIVOS NO CORRIENTES', 2),
    ('Intereses por pagar LP', False, None, False, None, 3, False, 'Otras cuentas por pagar L.P.', 3),
    ('Prestamos por pagar LP', False, None, False, None, 3, False, 'Otras cuentas por pagar L.P.', 3),
    ('Provisiones LP', False, None, False, None, 3, False, 'Otras cuentas por pagar L.P.', 3),
    ('Total Pasivos No Corrientes', True, None, True, None, 1, False, 'PASIVOS NO CORRIENTES', 1),
    ('TOTAL PASIVOS', True, None, True, None, 0, False, None, 0),
    
    # PATRIMONIO
    ('PATRIMONIO', True, None, True, None, 1, False, None, 1),
    ('Capital social', False, None, False, None, 2, False, 'PATRIMONIO', 2),
    ('Reservas legales y estatutarias', False, None, False, None, 2, False, 'PATRIMONIO', 2),
    ('Superavit por revaluacion', False, None, False, None, 2, False, 'PATRIMONIO', 2),
    ('Resultados acumulados', False, None, False, None, 2, False, 'PATRIMONIO', 2),
    ('Resultados del ejercicio', False, None, False, None, 2, False, 'PATRIMONIO', 2),
    ('Total Patrimonio', True, None, True, None, 1, False, 'PATRIMONIO', 1),
    ('TOTAL PASIVOS Y PATRIMONIO', True, None, True, None, 0, False, None, 0),
]


def esf_engine(year, unit='', aplicar_divisa_real=False, empresa_id=None,
               utilidad_externa_q=None, acumulados_fijos_q=None):
    import sqlite3
    import os
    
    DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'ultrax.db')
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Obtener grupos de presentación de mapping_groups_v2 para ESF
    rows_groups = cursor.execute(
        '''SELECT mg.group_name, m.partida
           FROM mapping_groups_v2 mg
           JOIN mapping m ON mg.odoo_code = m.odoo_code
           WHERE mg.report_type = 'esf'
           ORDER BY mg.display_order'''
    ).fetchall()
    
    groups_v2 = {}
    for r in rows_groups:
        groups_v2.setdefault(r['group_name'], []).append(r['partida'])
        
    # 2. Leer datos de esf_data
    if unit:
        rows_esf = cursor.execute(
            '''SELECT quarter, partida, SUM(amount) amount
               FROM esf_data
               WHERE year = ? AND unit = ?
               GROUP BY quarter, partida''',
            (year, unit)
        ).fetchall()
    elif empresa_id:
        rows_esf = cursor.execute(
            '''SELECT quarter, partida, SUM(amount) amount
               FROM esf_data
               WHERE year = ? AND empresa_id = ?
               GROUP BY quarter, partida''',
            (year, empresa_id)
        ).fetchall()
    else:
        rows_esf = cursor.execute(
            '''SELECT quarter, partida, SUM(amount) amount
               FROM esf_data
               WHERE year = ?
               GROUP BY quarter, partida''',
            (year,)
        ).fetchall()
        
    db_data = {}
    for r in rows_esf:
        db_data[(r['quarter'], r['partida'])] = r['amount']
        
    # 2b. Detalle por cuenta individual Odoo (nivel 4 trazabilidad)
    detail_args = [year]
    detail_unit_clause = ''
    if unit:
        detail_unit_clause = 'AND fd.unit = ?'
        detail_args.append(unit)
    else:
        # Bug confirmado ago-2026 (10-ago): ESF es exclusivamente consolidado --
        # financials_detail.unit SIEMPRE es 'CONSOLIDADO' para report_type='esf',
        # nunca el nombre de una unidad de negocio individual. El filtro anterior
        # (lista de nombres de unidad vía empresa_id) nunca coincidía, dejando
        # detail_by_group vacío y borrando (poniendo en 0.0) las 7 partidas
        # revalorizables de Divisa Real en cualquier llamada consolidada por empresa.
        # empresa_id sigue filtrando (Holding=None trae todas las empresas; una
        # empresa_id especifica trae solo esa).
        if empresa_id is not None:
            detail_unit_clause = "AND fd.unit = 'CONSOLIDADO' AND fd.empresa_id = ?"
            detail_args.append(empresa_id)
        else:
            detail_unit_clause = "AND fd.unit = 'CONSOLIDADO'"
        
    detail_rows_raw = cursor.execute(f'''
        SELECT fd.quarter, mg.group_name, fd.odoo_code, fd.odoo_name,
               fd.amount_sign as total
        FROM financials_detail fd
        JOIN mapping_groups_v2 mg ON fd.odoo_code = mg.odoo_code
        WHERE fd.year = ? AND fd.report_type = "esf"
          AND mg.report_type = "esf"
          AND fd.month IN (
              CASE fd.quarter WHEN 1 THEN 'MAR' WHEN 2 THEN 'JUN'
                              WHEN 3 THEN 'SEPT' WHEN 4 THEN 'DIC' END
          )
          AND fd.amount_sign != 0
          {detail_unit_clause}
    ''', detail_args).fetchall()
    
    detail_by_group = {}
    for r in detail_rows_raw:
        gn = r['group_name']
        key = (r['odoo_code'], r['odoo_name'])
        if gn not in detail_by_group:
            detail_by_group[gn] = {}
        if key not in detail_by_group[gn]:
            detail_by_group[gn][key] = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
        detail_by_group[gn][key][r['quarter']] = round(r['total'], 2)

    conn.close()
    
    # 3. Utilidad Neta: externa (metodología EERR Real/ESF Real) o vía EERR V2 normal
    utilidad_q = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
    if utilidad_externa_q is not None:
        utilidad_q = utilidad_externa_q
    else:
        try:
            from app import eerr_completo_v2_ui_adapter
            eerr_data = eerr_completo_v2_ui_adapter(year, unit, empresa_id=empresa_id)
            net_income_row = None
            for r in eerr_data.get('rows', []):
                if r.get('partida') == 'Utilidad Neta despues de ISLR':
                    net_income_row = r
                    break
            if net_income_row:
                q_months = {
                    1: ['ENE', 'FEB', 'MAR'],
                    2: ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN'],
                    3: ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEPT'],
                    4: ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEPT', 'OCT', 'NOV', 'DIC']
                }
                for q, months in q_months.items():
                    q_sum = 0.0
                    for m_data in net_income_row.get('meses', []):
                        if m_data.get('month') in months:
                            q_sum += m_data.get('ejecutado', {}).get('valor', 0.0)
                    utilidad_q[q] = q_sum
        except Exception as e:
            try:
                from app import app as flask_app
                flask_app.logger.error(
                    f"Error al calcular Utilidad Neta para ESF (year={year}, unit={unit}): {str(e)}"
                )
            except Exception:
                pass

    tasas_por_quarter = {}
    if aplicar_divisa_real:
        conn_tasas = sqlite3.connect(DB_PATH)
        conn_tasas.row_factory = sqlite3.Row
        cursor_tasas = conn_tasas.cursor()
        for q_num, month_cierre in QUARTER_MONTH_CIERRE.items():
            row_tasa = cursor_tasas.execute(
                'SELECT tasa_bcv_fin, tasa_paralela_fin FROM tasas_periodo WHERE year=? AND month=?',
                (year, month_cierre)
            ).fetchone()
            if row_tasa and row_tasa['tasa_bcv_fin'] and row_tasa['tasa_paralela_fin']:
                tasas_por_quarter[q_num] = (row_tasa['tasa_bcv_fin'], row_tasa['tasa_paralela_fin'])
        conn_tasas.close()
        
    # 4. Calcular los saldos trimestrales para cada partida
    quarters_data = {q: {} for q in [1, 2, 3, 4]}
    plug_divisa_q = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
    
    for q in [1, 2, 3, 4]:
        # Inicializar todos los nodos en 0
        for item in ESF_STRUCTURE_V2:
            quarters_data[q][item[0]] = 0.0
            
        # Asignar Resultados del ejercicio
        quarters_data[q]['Resultados del ejercicio'] = utilidad_q[q]
        
        # Asignar valores a hojas (is_header == False) excluyendo calculados
        for item in ESF_STRUCTURE_V2:
            name, is_header = item[0], item[1]
            if not is_header and name not in ('Resultados acumulados', 'Resultados del ejercicio'):
                partidas = groups_v2.get(name, [])
                quarters_data[q][name] = sum(db_data.get((q, p), 0.0) for p in partidas)
                
        # ESF Divisa Real: sustituir el total de partidas revalorizables aplicando
        # automáticamente el ratio BCV_fin/Paralela_fin del trimestre (no afecta ESF Normal).
        # Sin tasa cargada para el trimestre, la cuenta queda en su valor real sin ajuste.
        if aplicar_divisa_real:
            for name in PARTIDAS_ESF_DIVISA_REAL:
                cuentas = detail_by_group.get(name, {})
                total_ajustado = 0.0
                ratio = tasas_por_quarter.get(q)
                for (odoo_code, odoo_name), q_vals in cuentas.items():
                    valor_real = q_vals.get(q, 0.0)
                    if ratio:
                        valor = valor_real * (ratio[0] / ratio[1])
                    else:
                        valor = valor_real
                    total_ajustado += valor
                quarters_data[q][name] = total_ajustado
                
        # Calcular headers de nivel 3 (suman sus hijos de nivel 4)
        for item in ESF_STRUCTURE_V2:
            name, is_header, level = item[0], item[1], item[5]
            if is_header and level == 3:
                # Suman todos los nivel 4 que tienen a este node como parent_name
                level_4_children = [x[0] for x in ESF_STRUCTURE_V2 if x[5] == 4 and x[7] == name]
                quarters_data[q][name] = sum(quarters_data[q].get(c, 0.0) for c in level_4_children)
                
        # Calcular headers de nivel 2 (suman sus hijos de nivel 3)
        for item in ESF_STRUCTURE_V2:
            name, is_header, level = item[0], item[1], item[5]
            if is_header and level == 2:
                # Suman todos los nivel 3 que tienen a este node como parent_name
                level_3_children = [x[0] for x in ESF_STRUCTURE_V2 if x[5] == 3 and x[7] == name]
                quarters_data[q][name] = sum(quarters_data[q].get(c, 0.0) for c in level_3_children)
                
        # Calcular subtotales de nivel 1
        # Total Activos Corrientes
        level_2_activos_corr = [x[0] for x in ESF_STRUCTURE_V2 if x[5] == 2 and x[7] == 'ACTIVOS CORRIENTES']
        quarters_data[q]['Total Activos Corrientes'] = sum(quarters_data[q].get(c, 0.0) for c in level_2_activos_corr)
        quarters_data[q]['ACTIVOS CORRIENTES'] = quarters_data[q]['Total Activos Corrientes']
        
        # Total Activos No Corrientes
        level_2_activos_nocorr = [x[0] for x in ESF_STRUCTURE_V2 if x[5] == 2 and x[7] == 'ACTIVOS NO CORRIENTES']
        quarters_data[q]['Total Activos No Corrientes'] = sum(quarters_data[q].get(c, 0.0) for c in level_2_activos_nocorr)
        quarters_data[q]['ACTIVOS NO CORRIENTES'] = quarters_data[q]['Total Activos No Corrientes']
        
        # Total Pasivos Corrientes
        level_2_pasivos_corr = [x[0] for x in ESF_STRUCTURE_V2 if x[5] == 2 and x[7] == 'PASIVOS CORRIENTES']
        quarters_data[q]['Total Pasivos Corrientes'] = sum(quarters_data[q].get(c, 0.0) for c in level_2_pasivos_corr)
        quarters_data[q]['PASIVOS CORRIENTES'] = quarters_data[q]['Total Pasivos Corrientes']
        
        # Total Pasivos No Corrientes
        level_2_pasivos_nocorr = [x[0] for x in ESF_STRUCTURE_V2 if x[5] == 2 and x[7] == 'PASIVOS NO CORRIENTES']
        quarters_data[q]['Total Pasivos No Corrientes'] = sum(quarters_data[q].get(c, 0.0) for c in level_2_pasivos_nocorr)
        quarters_data[q]['PASIVOS NO CORRIENTES'] = quarters_data[q]['Total Pasivos No Corrientes']
        
        # Calcular level 0 Totales
        quarters_data[q]['TOTAL ACTIVOS'] = quarters_data[q]['Total Activos Corrientes'] + quarters_data[q]['Total Activos No Corrientes']
        quarters_data[q]['TOTAL PASIVOS'] = quarters_data[q]['Total Pasivos Corrientes'] + quarters_data[q]['Total Pasivos No Corrientes']
        
        # Regla Especial 2: Resultados acumulados = TOTAL ACTIVOS - TOTAL PASIVOS - (Capital social + Reservas legales y estatutarias + Superavit por revaluacion + Resultados del ejercicio)
        cap_social = quarters_data[q].get('Capital social', 0.0)
        reservas = quarters_data[q].get('Reservas legales y estatutarias', 0.0)
        superavit = quarters_data[q].get('Superavit por revaluacion', 0.0)
        res_ejer = quarters_data[q].get('Resultados del ejercicio', 0.0)

        res_acum_calculado = quarters_data[q]['TOTAL ACTIVOS'] - quarters_data[q]['TOTAL PASIVOS'] - cap_social - reservas - superavit - res_ejer

        if acumulados_fijos_q is not None:
            # Metodología ESF Real (ago-2026): Resultados Acumulados queda fijo, idéntico
            # al de BCV -- no absorbe la diferencia de cuadre. La diferencia se expone
            # aparte como plug_divisa_q para que la use calcular_estados_reales.
            quarters_data[q]['Resultados acumulados'] = acumulados_fijos_q[q]
            plug_divisa_q[q] = res_acum_calculado - acumulados_fijos_q[q]
        else:
            quarters_data[q]['Resultados acumulados'] = res_acum_calculado
        
        # Total Patrimonio = Capital social + Reservas + Superavit + Resultados acumulados + Resultados del ejercicio
        level_2_patrimonio = [x[0] for x in ESF_STRUCTURE_V2 if x[5] == 2 and x[7] == 'PATRIMONIO']
        quarters_data[q]['Total Patrimonio'] = sum(quarters_data[q].get(c, 0.0) for c in level_2_patrimonio)
        quarters_data[q]['PATRIMONIO'] = quarters_data[q]['Total Patrimonio']
        
        # TOTAL PASIVOS Y PATRIMONIO = TOTAL PASIVOS + Total Patrimonio
        quarters_data[q]['TOTAL PASIVOS Y PATRIMONIO'] = quarters_data[q]['TOTAL PASIVOS'] + quarters_data[q]['Total Patrimonio']
        
    # 5. Formatear salida estructurada
    rows = []
    for item in ESF_STRUCTURE_V2:
        name = item[0]
        is_header = item[1]
        bold = item[3]
        bg_color = item[4]
        level = item[5]
        parent_name = item[7]
        indent = item[8]
        
        quarters_val = {q: round(quarters_data[q].get(name, 0.0), 2) for q in [1, 2, 3, 4]}
        
        rows.append({
            'partida': name,
            'is_header': is_header,
            'bold': bold,
            'bg_color': bg_color,
            'level': level,
            'parent_name': parent_name,
            'indent': indent,
            'quarters': quarters_val
        })
        
        # Nivel 4: cuentas individuales que componen este nodo hoja
        if not is_header and name not in ('Resultados acumulados', 'Resultados del ejercicio'):
            for (odoo_code, odoo_name), q_vals in detail_by_group.get(name, {}).items():
                rows.append({
                    'partida':    odoo_name,
                    'odoo_code':  odoo_code,
                    'is_header':  False,
                    'bold':       False,
                    'bg_color':   None,
                    'level':      4,
                    'parent_name': name,
                    'indent':     indent + 1,
                    'quarters':   q_vals
                })
        
    result = {
        'year': year,
        'unit': unit,
        'rows': rows
    }
    if acumulados_fijos_q is not None:
        result['plug_divisa_q'] = plug_divisa_q
    return result


# ── ESF Divisa Real ──────────────────────────────────────────────────────────
PARTIDAS_ESF_DIVISA_REAL = [
    'Caja en Bs', 'Fondo en Bs', 'Bancos en Bs', 'Bancos en transito en Bs',
    'Impuestos pagados por anticipado', 'Retenciones Laborales por pagar', 'Impuestos por pagar'
]
QUARTER_MONTH_CIERRE = {1: 'MAR', 2: 'JUN', 3: 'SEPT', 4: 'DIC'}


def calcular_esf_divisa_real(year, quarter, empresa_id=None):
    import sqlite3
    import os

    DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'ultrax.db')
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    month = QUARTER_MONTH_CIERRE.get(quarter)
    if not month:
        conn.close()
        return {'error': f'Quarter inválido: {quarter}'}

    tasa_row = cursor.execute(
        'SELECT tasa_bcv_fin, tasa_paralela_fin FROM tasas_periodo WHERE year=? AND month=?',
        (year, month)
    ).fetchone()

    if not tasa_row or not tasa_row['tasa_bcv_fin'] or not tasa_row['tasa_paralela_fin']:
        conn.close()
        return {'error': f'No hay tasa BCV/paralela fin de mes configurada para {month} {year}'}

    tasa_bcv_fin = tasa_row['tasa_bcv_fin']
    tasa_paralela_fin = tasa_row['tasa_paralela_fin']
    ratio = tasa_bcv_fin / tasa_paralela_fin

    placeholders = ','.join('?' * len(PARTIDAS_ESF_DIVISA_REAL))
    empresa_clause = ' AND fd.empresa_id = ?' if empresa_id is not None else ''
    empresa_params = (empresa_id,) if empresa_id is not None else ()
    rows = cursor.execute(f'''
        SELECT mg.group_name, fd.odoo_code, fd.amount_sign as total
        FROM financials_detail fd
        JOIN mapping_groups_v2 mg ON fd.odoo_code = mg.odoo_code AND mg.report_type = 'esf'
        WHERE fd.year = ? AND fd.report_type = 'esf' AND fd.month = ?
          AND mg.group_name IN ({placeholders}){empresa_clause}
    ''', (year, month, *PARTIDAS_ESF_DIVISA_REAL, *empresa_params)).fetchall()

    saldo_por_partida = {p: 0.0 for p in PARTIDAS_ESF_DIVISA_REAL}
    for r in rows:
        valor_ajustado = r['total'] * ratio
        saldo_por_partida[r['group_name']] += valor_ajustado

    saldo_total_bs = sum(saldo_por_partida.values())

    conn.close()

    saldo_total_usd = round(saldo_total_bs / tasa_paralela_fin, 2) if tasa_paralela_fin else None

    return {
        'year': year,
        'quarter': quarter,
        'month_cierre': month,
        'tasa_bcv_fin': tasa_bcv_fin,
        'tasa_paralela_fin': tasa_paralela_fin,
        'partidas': {k: round(v, 2) for k, v in saldo_por_partida.items()},
        'saldo_total_bs': round(saldo_total_bs, 2),
        'saldo_total_usd': saldo_total_usd
    }


SUBTOTAL_EXCLUSIONS = {
    'Subtotal Gastos de Administración': [
        'Gasto por impuesto a las pensiones', 'Gastos de IGTF', 'Gastos de comisiones bancarias',
        'Gastos de intereses de mora', 'Gastos de mantenimiento y reparación a la propiedad alq.',
        'Gastos de mantenimiento y reparación de edificaciones',
        'Gastos de mantenimiento y reparación de maquinaria y equipos',
        'Gastos de mantenimiento y reparación de mobiliario y equipo',
        'Gastos de mantenimiento y reparación de vehiculo',
        'Gastos de comida por viáticos administrativos', 'Gastos de hospedaje por viáticos administrativos',
        'Gastos de pasajes por viáticos administrativos', 'Gastos de transporte por viáticos administrativos',
        'Otros gastos de viáticos administrativos', 'Gastos de seguro de edificaciones',
        'Gastos de seguro de vehiculos', 'Gasto por otras tasas',
        'Gastos de impuesto por licencia de actividades economicas', 'Gastos de impuesto por publicidad',
        'Gastos de patente vehicular', 'Gastos de tasa sencamer', 'Gastos de tasas de notaria y registro',
        'Gastos de amortización de software', 'Gastos de depreciación de edificaciones',
        'Gastos de depreciación de maquinarias y equipos', 'Gastos de depreciación de mobiliario y equipo',
        'Gastos de depreciación de vehículos', 'Gastos de deterioro de edificaciones',
        'Gastos de deterioro de maquinarias y equipos', 'Gastos de deterioro de mobiliario y equipo',
        'Gastos de deterioro de vehículos', 'Gastos de deterioro por cuentas incobrables',
        'Gastos de intereses sobre préstamos bancarios', 'Gastos de intereses sobre préstamos de terceros'
    ],
    'Subtotal Gastos de Recursos Humanos': ['Gastos de uniformes y dotación al personal'],
    'Subtotal Gastos de Mercadeo': ['Gastos de impresiones de material gráfico', 'Gastos de patrocinio y donación', 'Gastos de decoración'],
    'Subtotal Gastos de Comercialización y Logistica': [
        'Gastos de comida por viáticos comerciales', 'Gastos de hospedaje por viáticos comerciales',
        'Gastos de pasajes por viáticos comerciales', 'Gastos de transporte por viáticos comerciales',
        'Otros gastos de viáticos comerciales', 'Gastos de almacenaje sobre compras no incluídos en el costo',
        'Gastos de armado de bicicletas no incluídos en el costo', 'Gastos de bolsas no incluídos en el costo',
        'Gastos de embalaje no incluídos en el costo', 'Gastos de etiquetas no incluídos en el costo',
        'Gastos de importación no incluídos en el costo', 'Gastos de seguro de mercancía no incluídos en el costo',
        'Gastos de títulos de propiedad no incluídos en el costo', 'Gastos por gasoil', 'Gastos por gasolina',
        'Gastos de alquiler Stand y/o ferias comerciales', 'Gastos de otros viáticos Stand y/o ferias comerciales',
        'Gastos de pasajes Stand y/o ferias comerciales',
        'Gastos de premiaciones, donaciones Stand y/o ferias comerciales',
        'Gastos de publicidad Stand y/o ferias comerciales', 'Gastos de viáticos comida Stand y/o ferias comerciales',
        'Gastos de viáticos hospedaje Stand y/o ferias comerciales',
        'Gastos de viáticos transporte Stand y/o ferias comerciales'
    ],
    'Gastos de TI+I': ['Gastos de dominio de página web', 'Gastos de servidores', 'Gastos de software tecnológico'],
    'Otros Gastos no Operacionales': ['Deterioro de inventarios', 'Faltante de inventarios'],
}


def calcular_estados_reales(year, unit='', empresa_id=None):
    """
    Orquestador de la metodología EERR Real / ESF Real (Yocelin, ago-2026, 9-ago).
    Orden de cálculo (sin dependencia circular, confirmado por Yocelin):
    1. EERR Real preliminar (sin la línea de Ganancia/Pérdida en tasa cambiaria).
    2. ESF BCV normal, para tener Resultados Acumulados de referencia (fijo en el real).
    3. ESF Real (aplicar_divisa_real=True), con Utilidad Neta externa del paso 1 y
       Acumulados fijos del paso 2 -- devuelve el plug de diferencia por trimestre.
    4. EERR Real final: se reinyecta el plug del paso 3 en el mes de cierre de cada
       trimestre, recalculando toda la cascada de subtotales.
    Retorna: {'eerr_real': <dict de _calcular_eerr_divisa_real>, 'esf_real': <dict de esf_engine>}
    """
    from app import _calcular_eerr_divisa_real

    # 1. EERR Real preliminar CONSOLIDADO (unit='' siempre, ESF es exclusivamente
    # consolidado -- el plug debe calcularse sobre la utilidad de TODA la empresa,
    # sin importar qué unidad pidió el llamante; ver Paso 4 para el EERR de la unidad).
    eerr_preliminar = _calcular_eerr_divisa_real(year, '', empresa_id=empresa_id)
    if 'error' in eerr_preliminar:
        return eerr_preliminar

    # Extraer Utilidad Neta despues de ISLR por trimestre (mismo agrupamiento que esf_engine)
    q_months = {
        1: ['ENE', 'FEB', 'MAR'],
        2: ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN'],
        3: ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEPT'],
        4: ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEPT', 'OCT', 'NOV', 'DIC']
    }
    utilidad_externa_q = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
    net_income_row = None
    for r in eerr_preliminar.get('rows', []):
        if r.get('partida') == 'Utilidad Neta despues de ISLR':
            net_income_row = r
            break
    if net_income_row:
        for q, months in q_months.items():
            q_sum = 0.0
            for m_data in net_income_row.get('meses', []):
                if m_data.get('month') in months:
                    q_sum += m_data.get('ejecutado', {}).get('valor', 0.0)
            utilidad_externa_q[q] = q_sum

    # 2. ESF BCV normal -> Acumulados de referencia (fijo en el real)
    esf_bcv = esf_engine(year, '', aplicar_divisa_real=False, empresa_id=empresa_id)
    acumulados_fijos_q = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
    for r in esf_bcv.get('rows', []):
        if r.get('partida') == 'Resultados acumulados':
            for q in [1, 2, 3, 4]:
                acumulados_fijos_q[q] = r['quarters'].get(q, 0.0)
            break

    # 3. ESF Real: Utilidad externa + Acumulados fijos -> plug de diferencia
    esf_real = esf_engine(
        year, '', aplicar_divisa_real=True, empresa_id=empresa_id,
        utilidad_externa_q=utilidad_externa_q, acumulados_fijos_q=acumulados_fijos_q
    )
    plug_divisa_q = esf_real.get('plug_divisa_q', {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0})

    # Corrección ago-2026 (10-ago), confirmada contra el Excel de Yocelin: "Resultados del
    # ejercicio" en su hoja 'N ESF ULTRAX' YA INCLUYE la ganancia/perdida en tasa cambiaria
    # (Fila 26 esta ANTES de Utilidad Neta en su hoja, dentro de Total Ingresos No
    # Operativos) -- no es una utilidad "limpia" sin esa linea como se asumio al principio.
    # utilidad_final_q = preliminar + plug reproduce exactamente ese comportamiento
    # (verificado: 30389.95 + 15395.36 = 45785.31, exacto contra el Excel). Se parchea
    # solo 'Resultados del ejercicio' en esf_real -- TOTAL ACTIVOS/PASIVOS/Acumulados no
    # cambian, ya son correctos y no dependen de la utilidad.
    utilidad_final_q = {q: utilidad_externa_q[q] + plug_divisa_q[q] for q in [1, 2, 3, 4]}
    for row in esf_real.get('rows', []):
        if row.get('partida') == 'Resultados del ejercicio':
            for q in [1, 2, 3, 4]:
                row['quarters'][q] = round(utilidad_final_q[q], 2)
            break

    # 4. EERR Real final: reinyectar el plug en el mes de cierre correspondiente.
    # Regla confirmada contra el Excel de Yocelin (10-ago-2026): el ajuste consolidado de
    # Ganancia/Perdida en tasa cambiaria SOLO aparece en la unidad Rodeo y en el consolidado
    # -- las demas unidades (PiedeMonte, Terracota, Ucafe, Barinas, Naranjos) no lo llevan.
    # Confirmado con datos literales de "N EERR RODEO" vs "N EERR ULTRAX" (valores identicos)
    # vs "N EERR PIEDEM"/"N EERR TERRA"/"N EERR UCAFE"/"N EERR BARINAS"/"N EERR LOS NA" (vacios).
    unit_recibe_plug = unit in ('', 'Rodeo')
    plug_a_inyectar = plug_divisa_q if unit_recibe_plug else None
    eerr_real = _calcular_eerr_divisa_real(year, unit, empresa_id=empresa_id, plug_divisa_q=plug_a_inyectar)
    if 'error' in eerr_real:
        return eerr_real

    return {
        'eerr_real': eerr_real,
        'esf_real': esf_real,
    }
