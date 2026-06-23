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
    ('ESTADO DE RESULTADOS', True, None, True, None, 0, False, None, 0),
    ('PARTIDAS', True, None, True, None, 0, False, None, 0),
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
    ('Gastos de mantenimiento y reparación a la propiedad alq.', False, None, False, None, 3, True, 'Mantenimiento y reparaciones', 3),
    ('Gastos de mantenimiento y reparación de edificaciones', False, None, False, None, 3, True, 'Mantenimiento y reparaciones', 3),
    ('Gastos de mantenimiento y reparación de maquinaria y equipos', False, None, False, None, 3, True, 'Mantenimiento y reparaciones', 3),
    ('Gastos de mantenimiento y reparación de mobiliario y equipo', False, None, False, None, 3, True, 'Mantenimiento y reparaciones', 3),
    ('Gastos de mantenimiento y reparación de vehiculo', False, None, False, None, 3, True, 'Mantenimiento y reparaciones', 3),
    ('Viáticos administrativos', False, None, False, None, 3, False, None, 2),
    ('Gastos de comida por viáticos administrativos', False, None, False, None, 3, True, 'Viáticos administrativos', 3),
    ('Gastos de hospedaje por viáticos administrativos', False, None, False, None, 3, True, 'Viáticos administrativos', 3),
    ('Gastos de pasajes por viáticos administrativos', False, None, False, None, 3, True, 'Viáticos administrativos', 3),
    ('Gastos de transporte por viáticos administrativos', False, None, False, None, 3, True, 'Viáticos administrativos', 3),
    ('Otros gastos de viáticos administrativos', False, None, False, None, 3, True, 'Viáticos administrativos', 3),
    ('Gastos de seguro', False, None, False, None, 3, False, None, 2),
    ('Gastos de seguro de edificaciones', False, None, False, None, 3, True, 'Gastos de seguro', 3),
    ('Gastos de seguro de vehiculos', False, None, False, None, 3, True, 'Gastos de seguro', 3),
    ('Gastos de impuestos, tasas y contribuciones', False, None, False, None, 3, False, None, 2),
    ('Gasto por otras tasas', False, None, False, None, 3, True, 'Gastos de impuestos, tasas y contribuciones', 3),
    ('Gastos de impuesto por licencia de actividades economicas', False, None, False, None, 3, True, 'Gastos de impuestos, tasas y contribuciones', 3),
    ('Gastos de impuesto por publicidad', False, None, False, None, 3, True, 'Gastos de impuestos, tasas y contribuciones', 3),
    ('Gastos de patente vehicular', False, None, False, None, 3, True, 'Gastos de impuestos, tasas y contribuciones', 3),
    ('Gastos de tasa sencamer', False, None, False, None, 3, True, 'Gastos de impuestos, tasas y contribuciones', 3),
    ('Gastos de tasas de notaria y registro', False, None, False, None, 3, True, 'Gastos de impuestos, tasas y contribuciones', 3),
    ('Depreciaciones, deterioro y Amortización', False, None, False, None, 3, False, None, 2),
    ('Gastos de amortización de software', False, None, False, None, 3, True, 'Depreciaciones, deterioro y Amortización', 3),
    ('Gastos de depreciación de edificaciones', False, None, False, None, 3, True, 'Depreciaciones, deterioro y Amortización', 3),
    ('Gastos de depreciación de maquinarias y equipos', False, None, False, None, 3, True, 'Depreciaciones, deterioro y Amortización', 3),
    ('Gastos de depreciación de mobiliario y equipo', False, None, False, None, 3, True, 'Depreciaciones, deterioro y Amortización', 3),
    ('Gastos de depreciación de vehículos', False, None, False, None, 3, True, 'Depreciaciones, deterioro y Amortización', 3),
    ('Gastos de deterioro de edificaciones', False, None, False, None, 3, True, 'Depreciaciones, deterioro y Amortización', 3),
    ('Gastos de deterioro de maquinarias y equipos', False, None, False, None, 3, True, 'Depreciaciones, deterioro y Amortización', 3),
    ('Gastos de deterioro de mobiliario y equipo', False, None, False, None, 3, True, 'Depreciaciones, deterioro y Amortización', 3),
    ('Gastos de deterioro de vehículos', False, None, False, None, 3, True, 'Depreciaciones, deterioro y Amortización', 3),
    ('Gastos de deterioro por cuentas incobrables', False, None, False, None, 3, True, 'Depreciaciones, deterioro y Amortización', 3),
    ('Gasto por impuesto a las pensiones', False, None, False, None, 3, True, 'Gastos de impuestos, tasas y contribuciones', 3),
    ('Gastos Bancarios', False, None, False, None, 3, False, None, 2),
    ('Gastos de IGTF', False, None, False, None, 3, True, 'Gastos Bancarios', 3),
    ('Gastos de comisiones bancarias', False, None, False, None, 3, True, 'Gastos Bancarios', 3),
    ('Gastos de intereses de mora', False, None, False, None, 3, True, 'Gastos Bancarios', 3),
    ('Gastos de intereses sobre préstamos', False, None, False, None, 3, False, None, 2),
    ('Gastos de intereses sobre préstamos bancarios', False, None, False, None, 3, True, 'Gastos de intereses sobre préstamos', 3),
    ('Gastos de intereses sobre préstamos de terceros', False, None, False, None, 3, True, 'Gastos de intereses sobre préstamos', 3),
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
    ('Gastos de comida por viáticos comerciales', False, None, False, None, 3, True, 'Gastos de viáticos comerciales', 3),
    ('Gastos de hospedaje por viáticos comerciales', False, None, False, None, 3, True, 'Gastos de viáticos comerciales', 3),
    ('Gastos de pasajes por viáticos comerciales', False, None, False, None, 3, True, 'Gastos de viáticos comerciales', 3),
    ('Gastos de transporte por viáticos comerciales', False, None, False, None, 3, True, 'Gastos de viáticos comerciales', 3),
    ('Otros gastos de viáticos comerciales', False, None, False, None, 3, True, 'Gastos de viáticos comerciales', 3),
    ('Gastos de comisiones empleados del taller', False, None, False, None, 3, True, 'Subtotal Gastos de Comercialización y Logistica', 3),
    ('Gastos de fletes y envios no asociados al costo', False, None, False, None, 3, False, None, 2),
    ('Otros gastos no asociados al costo', False, None, False, None, 3, False, None, 2),
    ('Gastos de almacenaje sobre compras no incluídos en el costo', False, None, False, None, 3, True, 'Otros gastos no asociados al costo', 3),
    ('Gastos de armado de bicicletas no incluídos en el costo', False, None, False, None, 3, True, 'Otros gastos no asociados al costo', 3),
    ('Gastos de bolsas no incluídos en el costo', False, None, False, None, 3, True, 'Otros gastos no asociados al costo', 3),
    ('Gastos de embalaje no incluídos en el costo', False, None, False, None, 3, True, 'Otros gastos no asociados al costo', 3),
    ('Gastos de etiquetas no incluídos en el costo', False, None, False, None, 3, True, 'Otros gastos no asociados al costo', 3),
    ('Gastos de importación no incluídos en el costo', False, None, False, None, 3, True, 'Otros gastos no asociados al costo', 3),
    ('Gastos de seguro de mercancía no incluídos en el costo', False, None, False, None, 3, True, 'Otros gastos no asociados al costo', 3),
    ('Gastos de títulos de propiedad no incluídos en el costo', False, None, False, None, 3, True, 'Otros gastos no asociados al costo', 3),
    ('Gastos por combustible', False, None, False, None, 3, False, None, 2),
    ('Gastos por gasoil', False, None, False, None, 3, True, 'Gastos por combustible', 3),
    ('Gastos por gasolina', False, None, False, None, 3, True, 'Gastos por combustible', 3),
    ('Gastos de representación', False, None, False, None, 3, False, None, 2),
    ('Gastos por garantia', False, None, False, None, 3, False, None, 2),
    ('Gastos por suscripciones', False, None, False, None, 3, False, None, 2),
    ('Gastos de Stand y/o ferias comerciales', False, None, False, None, 3, False, None, 2),
    ('Gastos de alquiler Stand y/o ferias comerciales', False, None, False, None, 3, True, 'Gastos de Stand y/o ferias comerciales', 3),
    ('Gastos de otros viáticos Stand y/o ferias comerciales', False, None, False, None, 3, True, 'Gastos de Stand y/o ferias comerciales', 3),
    ('Gastos de pasajes Stand y/o ferias comerciales', False, None, False, None, 3, True, 'Gastos de Stand y/o ferias comerciales', 3),
    ('Gastos de premiaciones, donaciones Stand y/o ferias comerciales', False, None, False, None, 3, True, 'Gastos de Stand y/o ferias comerciales', 3),
    ('Gastos de publicidad Stand y/o ferias comerciales', False, None, False, None, 3, True, 'Gastos de Stand y/o ferias comerciales', 3),
    ('Gastos de viáticos comida Stand y/o ferias comerciales', False, None, False, None, 3, True, 'Gastos de Stand y/o ferias comerciales', 3),
    ('Gastos de viáticos hospedaje Stand y/o ferias comerciales', False, None, False, None, 3, True, 'Gastos de Stand y/o ferias comerciales', 3),
    ('Gastos de viáticos transporte Stand y/o ferias comerciales', False, None, False, None, 3, True, 'Gastos de Stand y/o ferias comerciales', 3),
    ('Subtotal Gastos de Mercadeo', True, None, True, None, 1, False, None, 1),
    ('Gastos de redes sociales', False, None, False, None, 3, False, None, 2),
    ('Gastos de medios publicitarios', False, None, False, None, 3, False, None, 2),
    ('Otros gastos de publicidad y promoción', False, None, False, None, 3, False, None, 2),
    ('Gastos de impresiones de material gráfico', False, None, False, None, 3, True, 'Otros gastos de publicidad y promoción', 3),
    ('Gastos de decoración', False, None, False, None, 3, True, 'Otros gastos de publicidad y promoción', 3),
    ('Gastos de muestras y material POP', False, None, False, None, 3, True, 'Otros gastos de publicidad y promoción', 3),
    ('Gastos de campañas y lanzamientos', False, None, False, None, 3, True, 'Otros gastos de publicidad y promoción', 3),
    ('Gastos de patrocinio y donación', False, None, False, None, 3, False, None, 2),
    ('Gastos de patrocinio, donación y/o obsequios en efectivo', False, None, False, None, 3, True, 'Gastos de patrocinio y donación', 3),
    ('Gastos de patrocinio, donación y/o obsequios en productos', False, None, False, None, 3, True, 'Gastos de patrocinio y donación', 3),
    ('Gastos de viáticos por eventos', False, None, False, None, 3, False, None, 2),
    ('Gastos de materiales y servicios por eventos', False, None, False, None, 3, False, None, 2),
    ('Gastos de alimentos y bebidas por eventos', False, None, False, None, 3, False, None, 2),
    ('Gastos de personal por eventos', False, None, False, None, 3, False, None, 2),
    ('Gastos de patrocinio, donación y/o obseq por eventos', False, None, False, None, 3, False, None, 2),
    ('Gastos de TI+I', True, None, True, None, 1, False, None, 1),
    ('Gastos de página web', False, None, False, None, 3, False, None, 2),
    ('Gastos de dominio de página web', False, None, False, None, 3, True, 'Gastos de página web', 3),
    ('Gastos de servidores', False, None, False, None, 3, True, 'Gastos de página web', 3),
    ('Gastos de desarrollo', False, None, False, None, 3, False, None, 2),
    ('Gastos de software tecnológico', False, None, False, None, 3, True, 'Gastos de desarrollo', 3),
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
    ('Deterioro de inventarios', False, None, False, None, 3, True, 'Faltante y deterioro de inventarios', 3),
    ('Faltante de inventarios', False, None, False, None, 3, True, 'Faltante y deterioro de inventarios', 3),
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
# (partida_name, is_header, section)
# section: 'activo_corriente' | 'activo_no_corriente' | 'pasivo_corriente' |
#          'pasivo_no_corriente' | 'patrimonio' | None (subtotal/total)
ESF_STRUCTURE = [
    # ACTIVOS
    ('TOTAL ACTIVOS', True, None),
    ('ACTIVOS CORRIENTES', True, None),
    ('Efectivo en caja', False, 'activo_corriente'),
    ('Efectivo en bancos nacional', False, 'activo_corriente'),
    ('Efectivo en bancos exterior', False, 'activo_corriente'),
    ('Efectivo en criptomonedas', False, 'activo_corriente'),
    ('Total Efectivo y Equivalentes', True, None),
    ('Cuentas por cobrar clientes', False, 'activo_corriente'),
    ('Cuentas por cobrar empleados', False, 'activo_corriente'),
    ('Cuentas por cobrar accionistas', False, 'activo_corriente'),
    ('Otras cuentas por cobrar', False, 'activo_corriente'),
    ('Provisión para cuentas incobrables', False, 'activo_corriente'),
    ('Total Cuentas por Cobrar (neto)', True, None),
    ('Inventario de mercancías', False, 'activo_corriente'),
    ('Inventario de materia prima', False, 'activo_corriente'),
    ('Inventario de suministros', False, 'activo_corriente'),
    ('Total Inventarios', True, None),
    ('Gastos pagados por anticipado', False, 'activo_corriente'),
    ('Seguros pagados por anticipado', False, 'activo_corriente'),
    ('IVA crédito fiscal', False, 'activo_corriente'),
    ('Retenciones de IVA por recuperar', False, 'activo_corriente'),
    ('Anticipos a proveedores', False, 'activo_corriente'),
    ('Total Otros Activos Corrientes', True, None),
    ('ACTIVOS NO CORRIENTES', True, None),
    ('Terrenos', False, 'activo_no_corriente'),
    ('Edificaciones y mejoras', False, 'activo_no_corriente'),
    ('Depreciación acumulada edificaciones', False, 'activo_no_corriente'),
    ('Maquinarias y equipos', False, 'activo_no_corriente'),
    ('Depreciación acumulada maquinarias', False, 'activo_no_corriente'),
    ('Mobiliario y equipo de oficina', False, 'activo_no_corriente'),
    ('Depreciación acumulada mobiliario', False, 'activo_no_corriente'),
    ('Vehículos', False, 'activo_no_corriente'),
    ('Depreciación acumulada vehículos', False, 'activo_no_corriente'),
    ('Software y licencias', False, 'activo_no_corriente'),
    ('Amortización acumulada software', False, 'activo_no_corriente'),
    ('Inversiones a largo plazo', False, 'activo_no_corriente'),
    ('Total Activos No Corrientes', True, None),
    # PASIVOS
    ('TOTAL PASIVOS Y PATRIMONIO', True, None),
    ('PASIVOS CORRIENTES', True, None),
    ('Cuentas por pagar proveedores', False, 'pasivo_corriente'),
    ('Cuentas por pagar accionistas', False, 'pasivo_corriente'),
    ('Otras cuentas por pagar', False, 'pasivo_corriente'),
    ('Total Cuentas por Pagar', True, None),
    ('Pasivos laborales corrientes', False, 'pasivo_corriente'),
    ('Prestaciones sociales por pagar', False, 'pasivo_corriente'),
    ('Total Pasivos Laborales Corrientes', True, None),
    ('IVA débito fiscal', False, 'pasivo_corriente'),
    ('Retenciones de IVA por enterar', False, 'pasivo_corriente'),
    ('ISLR por pagar', False, 'pasivo_corriente'),
    ('Aportes patronales por pagar', False, 'pasivo_corriente'),
    ('Préstamos bancarios corto plazo', False, 'pasivo_corriente'),
    ('Porción corriente préstamos LP', False, 'pasivo_corriente'),
    ('Anticipos de clientes', False, 'pasivo_corriente'),
    ('Ingresos diferidos', False, 'pasivo_corriente'),
    ('Total Otros Pasivos Corrientes', True, None),
    ('TOTAL PASIVOS CORRIENTES', True, None),
    ('PASIVOS NO CORRIENTES', True, None),
    ('Préstamos bancarios largo plazo', False, 'pasivo_no_corriente'),
    ('Préstamos de terceros largo plazo', False, 'pasivo_no_corriente'),
    ('Pasivos laborales largo plazo', False, 'pasivo_no_corriente'),
    ('Otras obligaciones largo plazo', False, 'pasivo_no_corriente'),
    ('TOTAL PASIVOS NO CORRIENTES', True, None),
    ('TOTAL PASIVOS', True, None),
    # PATRIMONIO
    ('PATRIMONIO', True, None),
    ('Capital social', False, 'patrimonio'),
    ('Reserva legal', False, 'patrimonio'),
    ('Otras reservas', False, 'patrimonio'),
    ('Utilidades retenidas años anteriores', False, 'patrimonio'),
    ('Pérdidas acumuladas', False, 'patrimonio'),
    ('Utilidad / pérdida del ejercicio', False, 'patrimonio'),
    ('Ajuste por inflación patrimonio', False, 'patrimonio'),
    ('TOTAL PATRIMONIO', True, None),
]

# Partidas ESF que son cuentas de balance (tienen datos en esf_data)
ESF_LEAF_PARTIDAS = {row[0] for row in ESF_STRUCTURE if not row[1]}


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


class ExcelExporter:
    """Genera Excel del EERR usando eerr_completo_v2_ui_adapter() — subtotales como valores del engine."""

    def __init__(self, year, units, months):
        self.year   = year
        self.units  = units
        self.months = months

    def generate(self):
        import openpyxl
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
        from app import eerr_completo_v2_ui_adapter
        import os, tempfile

        wb = openpyxl.Workbook()
        wb.remove(wb.active)

        HDR_FILL  = PatternFill('solid', start_color='1F3864')  # Azul oscuro - título
        SUB_FILL  = PatternFill('solid', start_color='D6DCE4')  # Gris claro - header columnas
        SEC_FILL  = PatternFill('solid', start_color='F2F2F2')  # Gris suave - subtotales
        WHITE_FILL= PatternFill('solid', start_color='FFFFFF')  # Blanco - partidas
        ACUM_FILL = PatternFill('solid', start_color='FFFFFF')  # Blanco - acumulados
        VAR_FILL  = PatternFill('solid', start_color='FFFFFF')  # Blanco - variaciones
        WHITE_FONT= Font(name='Arial', bold=True, color='FFFFFF', size=10)  # Blanco sobre azul
        DARK_FONT = Font(name='Arial', bold=True, color='000000', size=10)  # Negro sobre gris
        NORM_FONT = Font(name='Arial', size=9)
        TEAL_FILL = PatternFill('solid', start_color='D6DCE4')  # Gris claro - totales principales
        NUM_FMT   = '#,##0.00;(#,##0.00);"-"'
        PCT_FMT   = '0.0%;(0.0%);"-"'
        thin      = Side(style='thin', color='D9D9D9')  # Borde gris suave
        border    = Border(left=thin, right=thin, top=thin, bottom=thin)

        TOTALES_HDR = {
            'Total Ingresos', 'Total Costo de Ventas', 'Utilidad Bruta',
            'Total Gastos Operacionales', 'Total Gastos Operacionales y No Operacionales',
            'Utilidad Neta', 'Utilidad Neta despues de ISLR',
            'Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA)',
            'Utilidad antes de Intereses e Impuestos (EBIT)',
            'Utilidad Bruta por Venta de Mercancia y Taller',
            'Utilidad Bruta por Servicios', 'Utilidad Bruta por Eventos',
            'Utilidad antes de Comisiones por Ventas',
            'Utilidad después de Comisiones por Ventas'
        }

        N_MONTHS     = len(self.months)
        COL_ANUAL    = 2
        COL_M_START  = 3
        COL_M_END    = COL_M_START + N_MONTHS - 1
        COL_ACUM     = COL_M_END + 1
        COL_VAR      = COL_M_END + 2
        COL_PVTAS    = COL_M_END + 3
        COL_PGASTOS  = COL_M_END + 4

        sheets_to_build = list(self.units) + ['CONSOLIDADO']

        for unit in sheets_to_build:
            engine_unit = unit if unit != 'CONSOLIDADO' else ''
            data = eerr_completo_v2_ui_adapter(self.year, engine_unit)
            rows = data.get('rows', [])

            ws = wb.create_sheet(unit)
            ws.sheet_view.showGridLines = False

            last_col = get_column_letter(COL_PGASTOS)
            ws.merge_cells(f'A1:{last_col}1')
            title = ws['A1']
            title.value     = f'ESTADO DE RESULTADOS — {unit.upper()} — {self.year}'
            title.font      = Font(name='Arial', bold=True, color='FFFFFF', size=12)
            title.fill      = HDR_FILL
            title.alignment = Alignment(horizontal='center', vertical='center')
            ws.row_dimensions[1].height = 24

            ws.row_dimensions[2].height = 20
            headers = ['PARTIDAS', 'ANUAL'] + list(self.months) + ['ACUM EJEC', '%VAR', '%VTAS', '%GASTOS']
            for col_idx, h in enumerate(headers, 1):
                cell = ws.cell(row=2, column=col_idx, value=h)
                cell.font      = WHITE_FONT
                cell.fill      = SUB_FILL
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.border    = border

            ws.column_dimensions['A'].width = 52
            ws.column_dimensions['B'].width = 14
            for ci in range(COL_M_START, COL_M_END + 1):
                ws.column_dimensions[get_column_letter(ci)].width = 11
            ws.column_dimensions[get_column_letter(COL_ACUM)].width    = 14
            ws.column_dimensions[get_column_letter(COL_VAR)].width     = 9
            ws.column_dimensions[get_column_letter(COL_PVTAS)].width   = 9
            ws.column_dimensions[get_column_letter(COL_PGASTOS)].width = 9

            row_num      = 3
            partida_rows = {}

            for item in rows:
                partida   = item['partida']
                is_header = item['is_header']
                indent    = item.get('indent', 0)
                meses     = item.get('meses', [])

                ws.row_dimensions[row_num].height = 16

                if partida in TOTALES_HDR:
                    fill, fnt = TEAL_FILL, DARK_FONT
                elif is_header:
                    fill, fnt = SEC_FILL, DARK_FONT
                else:
                    fill, fnt = WHITE_FILL, NORM_FONT

                # Columna A
                a_cell = ws.cell(row=row_num, column=1, value=partida)
                a_cell.font      = fnt
                a_cell.fill      = fill
                a_cell.alignment = Alignment(vertical='center', indent=indent)
                a_cell.border    = border

                # Columnas de meses
                for m_idx, month in enumerate(self.months):
                    col = COL_M_START + m_idx
                    # Buscar el mes correspondiente en la lista meses del engine
                    mes_data = next((m for m in meses if m.get('month') == month), None)
                    val = mes_data['ejecutado']['valor'] if mes_data else None
                    val = val if val else None

                    c = ws.cell(row=row_num, column=col, value=val)
                    c.number_format = NUM_FMT
                    c.font          = fnt
                    c.fill          = fill
                    c.alignment     = Alignment(horizontal='right', vertical='center')
                    c.border        = border

                # Columna B: ANUAL = SUM(meses)
                month_range = f'{get_column_letter(COL_M_START)}{row_num}:{get_column_letter(COL_M_END)}{row_num}'
                b_cell = ws.cell(row=row_num, column=COL_ANUAL)
                b_cell.value         = f'=SUM({month_range})'
                b_cell.number_format = NUM_FMT
                b_cell.font          = fnt
                b_cell.fill          = fill
                b_cell.alignment     = Alignment(horizontal='right', vertical='center')
                b_cell.border        = border

                # Columna ACUM EJEC
                acum_cell = ws.cell(row=row_num, column=COL_ACUM)
                acum_cell.value         = f'=B{row_num}'
                acum_cell.number_format = NUM_FMT
                acum_cell.font          = Font(name='Arial', size=9, italic=True, bold=is_header)
                acum_cell.fill          = ACUM_FILL if not is_header else fill
                acum_cell.alignment     = Alignment(horizontal='right', vertical='center')
                acum_cell.border        = border

                # Columna %VAR
                if N_MONTHS >= 2:
                    last_m_col  = get_column_letter(COL_M_END)
                    prev_m_col  = get_column_letter(COL_M_END - 1)
                    var_formula = (
                        f'=IF(AND({prev_m_col}{row_num}<>0,{prev_m_col}{row_num}<>""),'
                        f'({last_m_col}{row_num}-{prev_m_col}{row_num})/ABS({prev_m_col}{row_num}),"")'
                    )
                else:
                    var_formula = '=""'
                var_cell = ws.cell(row=row_num, column=COL_VAR)
                var_cell.value         = var_formula
                var_cell.number_format = PCT_FMT
                var_cell.font          = Font(name='Arial', size=9)
                var_cell.fill          = VAR_FILL if not is_header else fill
                var_cell.alignment     = Alignment(horizontal='right', vertical='center')
                var_cell.border        = border

                partida_rows[partida] = row_num
                row_num += 1

            # %VTAS y %GASTOS
            total_ing_row = partida_rows.get('Total Ingresos')
            total_gas_row = partida_rows.get('Total Gastos Operacionales')
            for p, r in partida_rows.items():
                pv = ws.cell(row=r, column=COL_PVTAS)
                pg = ws.cell(row=r, column=COL_PGASTOS)
                if total_ing_row:
                    pv.value         = f'=IF(B{total_ing_row}<>0,B{r}/B{total_ing_row},"")'
                    pv.number_format = PCT_FMT
                if total_gas_row:
                    pg.value         = f'=IF(B{total_gas_row}<>0,B{r}/B{total_gas_row},"")'
                    pg.number_format = PCT_FMT
                for c in [pv, pg]:
                    c.font      = NORM_FONT
                    c.border    = border
                    c.alignment = Alignment(horizontal='right', vertical='center')

            ws.freeze_panes = 'B3'

            # Construir Notas y obtener mapa de filas
            notes_name, partida_month_rows = self._build_notes_sheet(wb, unit, engine_unit)

            # Si hay datos en Notas, reescribir celdas de meses en EERR con fórmulas a Notas
            if partida_month_rows:
                for partida, r in partida_rows.items():
                    if partida in partida_month_rows:
                        for m_idx, month in enumerate(self.months):
                            col = COL_M_START + m_idx
                            filas = partida_month_rows[partida].get(month, [])
                            if filas:
                                refs = '+'.join(
                                    f"'{notes_name}'!{get_column_letter(4+m_idx)}{f}"
                                    for f in filas
                                )
                                c = ws.cell(row=r, column=col)
                                c.value = f'={refs}'
                                c.number_format = NUM_FMT

        path = os.path.join(tempfile.gettempdir(), f'EEFF_ULTRAX_{self.year}.xlsx')
        wb.save(path)
        return path

    def _build_notes_sheet(self, wb, unit, engine_unit):
        import sqlite3, os
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
        from collections import defaultdict

        DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'ultrax.db')
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row

        HDR_FILL  = PatternFill('solid', start_color='1F3864')
        SEC_FILL  = PatternFill('solid', start_color='F2F2F2')
        WHITE_FILL= PatternFill('solid', start_color='FFFFFF')
        WHITE_FONT= Font(name='Arial', bold=True, color='FFFFFF', size=10)
        DARK_FONT = Font(name='Arial', bold=True, color='000000', size=10)
        NORM_FONT = Font(name='Arial', size=9)
        NUM_FMT   = '#,##0.00;(#,##0.00);"-"'
        thin      = Side(style='thin', color='D9D9D9')
        border    = Border(left=thin, right=thin, top=thin, bottom=thin)

        notes_sheet_name = f'N EERR {unit}'
        ws = wb.create_sheet(notes_sheet_name)
        ws.sheet_view.showGridLines = False

        N = len(self.months)
        total_cols = 4 + N + 1  # codigo, nombre, partida, (vacio), meses..., total

        ws.merge_cells(f'A1:{get_column_letter(total_cols)}1')
        t = ws['A1']
        t.value     = f'NOTAS — ESTADO DE RESULTADOS — {unit.upper()} — {self.year}'
        t.font      = Font(name='Arial', bold=True, color='FFFFFF', size=12)
        t.fill      = HDR_FILL
        t.alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 24

        headers = ['CÓDIGO ODOO', 'NOMBRE CUENTA', 'PARTIDA'] + list(self.months) + ['TOTAL']
        for ci, h in enumerate(headers, 1):
            cell = ws.cell(row=2, column=ci, value=h)
            cell.font      = WHITE_FONT
            cell.fill      = HDR_FILL
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border    = border

        ws.column_dimensions['A'].width = 18
        ws.column_dimensions['B'].width = 45
        ws.column_dimensions['C'].width = 40
        for ci in range(4, 4 + N + 2):
            ws.column_dimensions[get_column_letter(ci)].width = 12

        partidas_order = [item[0] for item in EERR_STRUCTURE if not item[1]]

        if engine_unit:
            rows = conn.execute(
                '''SELECT fd.odoo_code, fd.odoo_name,
                          COALESCE(mg.group_name, fd.partida) as group_name,
                          fd.month, fd.amount_sign
                   FROM financials_detail fd
                   LEFT JOIN mapping_groups_v2 mg
                          ON fd.odoo_code = mg.odoo_code AND mg.report_type='eerr'
                   WHERE fd.year=? AND fd.unit=? AND fd.report_type='eerr'
                   ORDER BY group_name, fd.odoo_code, fd.month''',
                (self.year, engine_unit)
            ).fetchall()
        else:
            rows = conn.execute(
                '''SELECT fd.odoo_code, fd.odoo_name,
                          COALESCE(mg.group_name, fd.partida) as group_name,
                          fd.month, SUM(fd.amount_sign) as amount_sign
                   FROM financials_detail fd
                   LEFT JOIN mapping_groups_v2 mg
                          ON fd.odoo_code = mg.odoo_code AND mg.report_type='eerr'
                   WHERE fd.year=? AND fd.report_type='eerr'
                   GROUP BY fd.odoo_code, fd.odoo_name, group_name, fd.month
                   ORDER BY group_name, fd.odoo_code, fd.month''',
                (self.year,)
            ).fetchall()

        data = defaultdict(lambda: defaultdict(lambda: {'name': '', 'meses': {}}))
        for r in rows:
            data[r['group_name']][r['odoo_code']]['name'] = r['odoo_name']
            data[r['group_name']][r['odoo_code']]['meses'][r['month']] = r['amount_sign']

        # mapa retornado: {partida: {month: [row_nums en hoja Notas]}}
        partida_month_rows = defaultdict(lambda: defaultdict(list))

        row_num = 3
        for partida in partidas_order:
            if partida not in data:
                continue

            # Fila cabecera de partida
            ws.row_dimensions[row_num].height = 16
            ws.merge_cells(f'A{row_num}:C{row_num}')
            a = ws.cell(row=row_num, column=1, value=partida)
            a.font = DARK_FONT; a.fill = SEC_FILL; a.border = border
            for ci in range(2, 4 + N + 2):
                c = ws.cell(row=row_num, column=ci)
                c.fill = SEC_FILL; c.border = border
            row_num += 1

            for code, info in sorted(data[partida].items()):
                ws.row_dimensions[row_num].height = 15
                ws.cell(row=row_num, column=1, value=code).border = border
                ws.cell(row=row_num, column=1).font = NORM_FONT
                ws.cell(row=row_num, column=2, value=info['name']).border = border
                ws.cell(row=row_num, column=2).font = NORM_FONT
                ws.cell(row=row_num, column=3, value=partida).border = border
                ws.cell(row=row_num, column=3).font = NORM_FONT

                for m_idx, month in enumerate(self.months):
                    col = 4 + m_idx
                    val = info['meses'].get(month, None)
                    c = ws.cell(row=row_num, column=col, value=val)
                    c.number_format = NUM_FMT
                    c.font = NORM_FONT
                    c.border = border
                    c.alignment = Alignment(horizontal='right')
                    # Registrar esta fila para el mes en el mapa
                    partida_month_rows[partida][month].append(row_num)

                # Total fila
                m_start = get_column_letter(4)
                m_end   = get_column_letter(3 + N)
                tot = ws.cell(row=row_num, column=4+N,
                              value=f'=SUM({m_start}{row_num}:{m_end}{row_num})')
                tot.number_format = NUM_FMT
                tot.font = NORM_FONT
                tot.border = border
                tot.alignment = Alignment(horizontal='right')

                row_num += 1

        ws.freeze_panes = 'A3'
        conn.close()
        return notes_sheet_name, partida_month_rows


class ESFExporter:
    """Genera Excel del ESF usando esf_engine() — subtotales como fórmulas SUM."""

    def __init__(self, year, units):
        self.year  = year
        self.units = units

    def generate(self):
        import openpyxl
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
        import os, tempfile

        wb = openpyxl.Workbook()
        wb.remove(wb.active)

        HDR_FILL  = PatternFill('solid', start_color='1F3864')
        SUB_FILL  = PatternFill('solid', start_color='D6DCE4')
        SEC_FILL  = PatternFill('solid', start_color='F2F2F2')
        WHITE_FILL= PatternFill('solid', start_color='FFFFFF')
        VAR_FILL  = PatternFill('solid', start_color='FFFFFF')
        WHITE_FONT= Font(name='Arial', bold=True, color='FFFFFF', size=10)
        DARK_FONT = Font(name='Arial', bold=True, color='000000', size=10)
        NORM_FONT = Font(name='Arial', size=9)
        NUM_FMT   = '#,##0.00;(#,##0.00);"-"'
        PCT_FMT   = '0.0%;(0.0%);"-"'
        thin      = Side(style='thin', color='D6DCE4')
        border    = Border(left=thin, right=thin, top=thin, bottom=thin)

        TOTALES = {
            'TOTAL ACTIVOS', 'TOTAL PASIVOS Y PATRIMONIO',
            'TOTAL PASIVOS', 'TOTAL PATRIMONIO',
            'TOTAL PASIVOS CORRIENTES', 'TOTAL PASIVOS NO CORRIENTES'
        }

        # Columnas: A=Partida, B=Q1, C=Q2, D=Q3, E=Q4, F=%VarQ1Q2, G=%VarQ2Q3, H=%VarQ3Q4
        COL_Q     = {1: 2, 2: 3, 3: 4, 4: 5}
        COL_VAR12 = 6
        COL_VAR23 = 7
        COL_VAR34 = 8
        QUARTERS  = [1, 2, 3, 4]

        sheets_to_build = list(self.units) + ['CONSOLIDADO']

        for unit in sheets_to_build:
            # Obtener datos del engine
            engine_unit = unit if unit != 'CONSOLIDADO' else ''
            data = esf_engine(self.year, engine_unit)
            rows = data.get('rows', [])

            ws = wb.create_sheet(unit)
            ws.sheet_view.showGridLines = False

            ws.merge_cells('A1:H1')
            t = ws['A1']
            t.value     = f'ESTADO DE SITUACIÓN FINANCIERA — {unit.upper()} — {self.year}'
            t.font      = Font(name='Arial', bold=True, color='FFFFFF', size=12)
            t.fill      = HDR_FILL
            t.alignment = Alignment(horizontal='center', vertical='center')
            ws.row_dimensions[1].height = 24

            headers = ['PARTIDAS', 'Q1 (Mar)', 'Q2 (Jun)', 'Q3 (Sep)', 'Q4 (Dic)',
                       '% Var Q1→Q2', '% Var Q2→Q3', '% Var Q3→Q4']
            ws.row_dimensions[2].height = 20
            for ci, h in enumerate(headers, 1):
                cell = ws.cell(row=2, column=ci, value=h)
                cell.font      = WHITE_FONT
                cell.fill      = SUB_FILL
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.border    = border

            ws.column_dimensions['A'].width = 45
            for ci in range(2, 9):
                ws.column_dimensions[get_column_letter(ci)].width = 15

            row_num = 3
            # Mapa: partida -> lista de row_nums hijos (para construir SUM)
            # Usamos stack para trackear cabeceras abiertas
            # Estructura: stack de (partida, row_num, [child_rows])
            header_stack = []   # stack de dicts {partida, row, col_children: {q: [rows]}}
            partida_row  = {}   # partida -> row_num

            for item in rows:
                partida    = item['partida']
                is_header  = item['is_header']
                level      = item.get('level', 0)
                indent     = item.get('indent', 0)
                quarters_v = item.get('quarters', {})

                ws.row_dimensions[row_num].height = 16

                if partida in TOTALES:
                    fill, fnt = HDR_FILL, WHITE_FONT
                elif is_header:
                    fill, fnt = SEC_FILL, DARK_FONT
                else:
                    fill, fnt = WHITE_FILL, NORM_FONT

                # Columna A
                a_cell = ws.cell(row=row_num, column=1, value=partida)
                a_cell.font      = fnt
                a_cell.fill      = fill
                a_cell.alignment = Alignment(vertical='center', indent=indent)
                a_cell.border    = border

                # Columnas Q1-Q4
                for q in QUARTERS:
                    col = COL_Q[q]
                    c   = ws.cell(row=row_num, column=col)
                    c.font      = fnt
                    c.fill      = fill
                    c.alignment = Alignment(horizontal='right', vertical='center')
                    c.border    = border
                    c.number_format = NUM_FMT

                    if is_header:
                        # Buscar hijos directos en el stack
                        # El valor ya viene calculado del engine — usarlo como valor
                        val = quarters_v.get(q, None) or quarters_v.get(str(q), None)
                        c.value = val if val else None
                    else:
                        val = quarters_v.get(q, None) or quarters_v.get(str(q), None)
                        c.value = val if val else None

                # Columnas %Var
                for var_col, qa, qb in [
                    (COL_VAR12, 'B', 'C'),
                    (COL_VAR23, 'C', 'D'),
                    (COL_VAR34, 'D', 'E')
                ]:
                    vc = ws.cell(row=row_num, column=var_col)
                    vc.value = (
                        f'=IF(AND({qa}{row_num}<>0,{qa}{row_num}<>""),'
                        f'({qb}{row_num}-{qa}{row_num})/ABS({qa}{row_num}),"")'
                    )
                    vc.number_format = PCT_FMT
                    vc.font      = Font(name='Arial', size=9)
                    vc.fill      = VAR_FILL if not is_header else fill
                    vc.alignment = Alignment(horizontal='right', vertical='center')
                    vc.border    = border

                partida_row[partida] = row_num
                row_num += 1

            ws.freeze_panes = 'B3'

            # Hoja de Notas ESF
            engine_unit = unit if unit != 'CONSOLIDADO' else ''
            self._build_notes_sheet(wb, unit, engine_unit)

        path = os.path.join(tempfile.gettempdir(), f'ESF_ULTRAX_{self.year}.xlsx')
        wb.save(path)
        return path

    def _build_notes_sheet(self, wb, unit, engine_unit):
        import sqlite3, os
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
        from openpyxl.utils import get_column_letter

        DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'ultrax.db')
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row

        HDR_FILL  = PatternFill('solid', start_color='1F3864')
        SEC_FILL  = PatternFill('solid', start_color='F2F2F2')
        WHITE_FILL= PatternFill('solid', start_color='FFFFFF')
        WHITE_FONT= Font(name='Arial', bold=True, color='FFFFFF', size=10)
        DARK_FONT = Font(name='Arial', bold=True, color='000000', size=10)
        NORM_FONT = Font(name='Arial', size=9)
        NUM_FMT   = '#,##0.00;(#,##0.00);"-"'
        thin      = Side(style='thin', color='D6DCE4')
        border    = Border(left=thin, right=thin, top=thin, bottom=thin)

        ws = wb.create_sheet(f'N ESF {unit}')
        ws.sheet_view.showGridLines = False

        # Título
        ws.merge_cells('A1:G1')
        t = ws['A1']
        t.value     = f'NOTAS — ESTADO DE SITUACIÓN FINANCIERA — {unit.upper()} — {self.year}'
        t.font      = Font(name='Arial', bold=True, color='FFFFFF', size=12)
        t.fill      = HDR_FILL
        t.alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 24

        # Encabezados
        headers = ['CÓDIGO ODOO', 'NOMBRE CUENTA', 'PARTIDA', 'Q1', 'Q2', 'Q3', 'Q4']
        for ci, h in enumerate(headers, 1):
            cell = ws.cell(row=2, column=ci, value=h)
            cell.font      = WHITE_FONT
            cell.fill      = HDR_FILL
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border    = border

        ws.column_dimensions['A'].width = 18
        ws.column_dimensions['B'].width = 45
        ws.column_dimensions['C'].width = 40
        for ci in range(4, 8):
            ws.column_dimensions[get_column_letter(ci)].width = 14

        # Orden de partidas desde ESF_STRUCTURE
        partidas_order = [item[0] for item in ESF_STRUCTURE if not item[1]]

        # Query detalle con JOIN para resolver group_name
        if engine_unit:
            rows = conn.execute(
                '''SELECT fd.odoo_code, fd.odoo_name,
                          COALESCE(mg.group_name, fd.partida) as group_name,
                          fd.quarter, fd.amount_sign
                   FROM financials_detail fd
                   LEFT JOIN mapping_groups_v2 mg
                          ON fd.odoo_code = mg.odoo_code AND mg.report_type='esf'
                   WHERE fd.year=? AND fd.unit=? AND fd.report_type='esf'
                   ORDER BY group_name, fd.odoo_code, fd.quarter''',
                (self.year, engine_unit)
            ).fetchall()
        else:
            rows = conn.execute(
                '''SELECT fd.odoo_code, fd.odoo_name,
                          COALESCE(mg.group_name, fd.partida) as group_name,
                          fd.quarter, SUM(fd.amount_sign) as amount_sign
                   FROM financials_detail fd
                   LEFT JOIN mapping_groups_v2 mg
                          ON fd.odoo_code = mg.odoo_code AND mg.report_type='esf'
                   WHERE fd.year=? AND fd.report_type='esf'
                   GROUP BY fd.odoo_code, fd.odoo_name, group_name, fd.quarter
                   ORDER BY group_name, fd.odoo_code, fd.quarter''',
                (self.year,)
            ).fetchall()

        # Agrupar por group_name → cuenta → trimestre
        from collections import defaultdict
        data = defaultdict(lambda: defaultdict(lambda: {'name': '', 'quarters': {}}))
        for r in rows:
            data[r['group_name']][r['odoo_code']]['name'] = r['odoo_name']
            data[r['group_name']][r['odoo_code']]['quarters'][r['quarter']] = r['amount_sign']

        row_num = 3
        for partida in partidas_order:
            if partida not in data:
                continue

            # Fila cabecera de partida
            ws.row_dimensions[row_num].height = 16
            a = ws.cell(row=row_num, column=1, value=partida)
            a.font = DARK_FONT; a.fill = SEC_FILL; a.border = border
            ws.merge_cells(f'A{row_num}:C{row_num}')
            for ci in range(4, 8):
                c = ws.cell(row=row_num, column=ci)
                c.fill = SEC_FILL; c.border = border
            row_num += 1

            for code, info in sorted(data[partida].items()):
                ws.row_dimensions[row_num].height = 15
                ws.cell(row=row_num, column=1, value=code).border = border
                ws.cell(row=row_num, column=1).font = NORM_FONT
                ws.cell(row=row_num, column=2, value=info['name']).border = border
                ws.cell(row=row_num, column=2).font = NORM_FONT
                ws.cell(row=row_num, column=3, value=partida).border = border
                ws.cell(row=row_num, column=3).font = NORM_FONT

                for q in [1, 2, 3, 4]:
                    col = 3 + q
                    val = info['quarters'].get(q, None)
                    c = ws.cell(row=row_num, column=col, value=val)
                    c.number_format = NUM_FMT
                    c.font = NORM_FONT
                    c.border = border
                    c.alignment = Alignment(horizontal='right')

                row_num += 1

        ws.freeze_panes = 'A3'
        conn.close()

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


def esf_engine(year, unit):
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
    
    # 3. Importación perezosa de la Utilidad Neta desde EERR V2
    utilidad_q = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
    try:
        from app import eerr_completo_v2_ui_adapter
        eerr_data = eerr_completo_v2_ui_adapter(year, unit)
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
        # Fallback silencioso en caso de error
        pass
        
    # 4. Calcular los saldos trimestrales para cada partida
    quarters_data = {q: {} for q in [1, 2, 3, 4]}
    
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
        
        res_acum = quarters_data[q]['TOTAL ACTIVOS'] - quarters_data[q]['TOTAL PASIVOS'] - cap_social - reservas - superavit - res_ejer
        quarters_data[q]['Resultados acumulados'] = res_acum
        
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
        
    return {
        'year': year,
        'unit': unit,
        'rows': rows
    }


