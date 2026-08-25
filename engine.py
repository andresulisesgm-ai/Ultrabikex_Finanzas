import pandas as pd
import os
from datetime import datetime

import logging
from constants import MONTHS, ESF_PLUG_VARIACION_UMBRAL
from helpers import get_grouped_partidas_v2

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
               utilidad_externa_q=None, acumulados_fijos_q=None, db=None):
    import sqlite3
    import os

    DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'ultrax.db')

    _conn_propia = db is None
    if db is not None:
        conn = db
    else:
        conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA busy_timeout=30000')
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
        lista = groups_v2.setdefault(r['group_name'], [])
        if r['partida'] not in lista:
            lista.append(r['partida'])
        
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

    # 3. Utilidad Neta: externa (metodología EERR Real/ESF Real) o vía EERR V2 normal
    utilidad_q = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
    if utilidad_externa_q is not None:
        utilidad_q = utilidad_externa_q
    else:
        try:
            eerr_data = eerr_completo_v2_ui_adapter(conn, year, unit, empresa_id=empresa_id)
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
            import logging
            logging.getLogger(__name__).error(
                f"Error al calcular Utilidad Neta para ESF (year={year}, unit={unit}): {str(e)}"
            )
    tasas_por_quarter = {}
    if aplicar_divisa_real:
        cursor_tasas = conn.cursor()
        for q_num, month_cierre in QUARTER_MONTH_CIERRE.items():
            row_tasa = cursor_tasas.execute(
                'SELECT tasa_bcv_fin, tasa_paralela_fin FROM tasas_periodo WHERE year=? AND month=?',
                (year, month_cierre)
            ).fetchone()
            if row_tasa and row_tasa['tasa_bcv_fin'] and row_tasa['tasa_paralela_fin']:
                tasas_por_quarter[q_num] = (row_tasa['tasa_bcv_fin'], row_tasa['tasa_paralela_fin'])
        
    # 4. Calcular los saldos trimestrales para cada partida
    quarters_data = {q: {} for q in [1, 2, 3, 4]}
    plug_divisa_q = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
    # Fix ago-2026: trimestres sin filas reales en esf_data no deben producir un plug
    # de Ganancia/Perdida en tasa cambiaria espurio (ver ultrax_deuda_tecnica_refactor.md,
    # "Plug fantasma"). Derivado directo de db_data, sin query nueva.
    esf_quarters_available = set(q_db for (q_db, _p) in db_data.keys())
    
    for q in [1, 2, 3, 4]:
        # Inicializar todos los nodos en 0
        for item in ESF_STRUCTURE_V2:
            quarters_data[q][item[0]] = 0.0
            
        # Asignar Resultados del ejercicio -- solo si el trimestre tiene esf_data
        # real. Sin esta guarda, utilidad_q[q] sigue trayendo la Utilidad Neta
        # acumulada de EERR (que puede tener meses cargados aunque ESF no tenga
        # balance para ese trimestre), inflando TOTAL PASIVOS Y PATRIMONIO en
        # trimestres sin datos reales de balance (ver ultrax_errores_evitar.md).
        quarters_data[q]['Resultados del ejercicio'] = utilidad_q[q] if q in esf_quarters_available else 0.0
        
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

        if q not in esf_quarters_available:
            # Trimestre sin esf_data real -- no calcular plug fantasma. TOTAL ACTIVOS/
            # TOTAL PASIVOS ya quedaron en 0 por falta de datos; sin esta guarda,
            # res_acum_calculado tomaría ese 0 como saldo real y generaría un plug de
            # Ganancia/Perdida en tasa cambiaria espurio.
            quarters_data[q]['Resultados acumulados'] = acumulados_fijos_q[q] if acumulados_fijos_q is not None else 0.0
            plug_divisa_q[q] = 0.0
        else:
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
    if _conn_propia:
        conn.close()
    return result


# ── ESF Divisa Real ──────────────────────────────────────────────────────────
PARTIDAS_ESF_DIVISA_REAL = [
    'Caja en Bs', 'Fondo en Bs', 'Bancos en Bs', 'Bancos en transito en Bs',
    'Impuestos pagados por anticipado', 'Retenciones Laborales por pagar', 'Impuestos por pagar'
]
QUARTER_MONTH_CIERRE = {1: 'MAR', 2: 'JUN', 3: 'SEPT', 4: 'DIC'}


def calcular_esf_divisa_real(year, quarter, empresa_id=None, db=None):
    import sqlite3
    import os

    DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'ultrax.db')
    _conn_propia = db is None
    if db is not None:
        conn = db
    else:
        conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA busy_timeout=30000')
    cursor = conn.cursor()

    month = QUARTER_MONTH_CIERRE.get(quarter)
    if not month:
        if _conn_propia:
            conn.close()
        return {'error': f'Quarter inválido: {quarter}'}

    tasa_row = cursor.execute(
        'SELECT tasa_bcv_fin, tasa_paralela_fin FROM tasas_periodo WHERE year=? AND month=?',
        (year, month)
    ).fetchone()

    if not tasa_row or not tasa_row['tasa_bcv_fin'] or not tasa_row['tasa_paralela_fin']:
        if _conn_propia:
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

    if _conn_propia:
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


def calcular_estados_reales(year, unit='', empresa_id=None, db=None):
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
    import sqlite3, os
    DB_PATH_LOCAL = os.path.join(os.path.dirname(__file__), 'data', 'ultrax.db')
    _conn_propia = db is None
    if db is not None:
        conn_estados = db
    else:
        conn_estados = sqlite3.connect(DB_PATH_LOCAL, timeout=30.0, check_same_thread=False)
        conn_estados.row_factory = sqlite3.Row
        conn_estados.execute('PRAGMA journal_mode=WAL')
        conn_estados.execute('PRAGMA busy_timeout=30000')
    try:
        # 1. EERR Real preliminar CONSOLIDADO (unit='' siempre, ESF es exclusivamente
        # consolidado -- el plug debe calcularse sobre la utilidad de TODA la empresa,
        # sin importar qué unidad pidió el llamante; ver Paso 4 para el EERR de la unidad).
        eerr_preliminar = _calcular_eerr_divisa_real(conn_estados, year, '', empresa_id=empresa_id)
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
        esf_bcv = esf_engine(year, '', aplicar_divisa_real=False, empresa_id=empresa_id, db=conn_estados)
        acumulados_fijos_q = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
        for r in esf_bcv.get('rows', []):
            if r.get('partida') == 'Resultados acumulados':
                for q in [1, 2, 3, 4]:
                    acumulados_fijos_q[q] = r['quarters'].get(q, 0.0)
                break

        # 3. ESF Real: Utilidad externa + Acumulados fijos -> plug de diferencia
        esf_real = esf_engine(
            year, '', aplicar_divisa_real=True, empresa_id=empresa_id,
            utilidad_externa_q=utilidad_externa_q, acumulados_fijos_q=acumulados_fijos_q,
            db=conn_estados
        )
        plug_divisa_q = esf_real.get('plug_divisa_q', {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0})

        # Construir plug_efectivo_q considerando overrides manuales
        plug_efectivo_q = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
        for q in [1, 2, 3, 4]:
            if empresa_id:
                row_ov = conn_estados.execute(
                    'SELECT ganancia, perdida FROM ganancia_perdida_divisa_override WHERE year=? AND quarter=? AND empresa_id=?',
                    (year, q, empresa_id)
                ).fetchone()
                inc_q = (float(row_ov['ganancia'] or 0.0) - float(row_ov['perdida'] or 0.0)) if row_ov is not None else 0.0
            else:
                # Bug real corregido (ago-2026): el Holding (empresa_id=None) buscaba una fila de
                # override con empresa_id IS NULL, que estructuralmente nunca se llega a cargar --
                # Yocelin confirma que el ajuste manual siempre lo carga por empresa, nunca a nivel
                # Holding (decisión de negocio). El Holding es agregado, no fuente de datos propia
                # (mismo criterio ya aplicado en el resto del sistema) -- ahora suma los overrides
                # de las empresas reales que ya tengan uno guardado para ese trimestre, en vez de
                # buscar uno propio que nunca existe.
                rows_ov = conn_estados.execute(
                    'SELECT ganancia, perdida FROM ganancia_perdida_divisa_override WHERE year=? AND quarter=? AND empresa_id IS NOT NULL',
                    (year, q)
                ).fetchall()
                inc_q = sum(float(r['ganancia'] or 0.0) - float(r['perdida'] or 0.0) for r in rows_ov)
            # ago-2026: sin override, Divisa Real NO cuadra automatico (esa
            # regla es exclusiva de BCV) -- Yocelin confirma que solo su ajuste
            # manual es valido aca; el plug automatico (BCV) queda descartado
            # como fallback.
            plug_efectivo_q[q] = plug_efectivo_q.get(q - 1, 0.0) + inc_q

        if empresa_id:
            rows_q_avail = conn_estados.execute(
                'SELECT DISTINCT quarter FROM esf_data WHERE year=? AND empresa_id=?',
                [year, empresa_id]
            ).fetchall()
        else:
            rows_q_avail = conn_estados.execute(
                'SELECT DISTINCT quarter FROM esf_data WHERE year=?', [year]
            ).fetchall()
        esf_quarters_available = set(r['quarter'] for r in rows_q_avail)

        # Corrección ago-2026 (10-ago), confirmada contra el Excel de Yocelin: "Resultados del
        # ejercicio" en su hoja 'N ESF ULTRAX' YA INCLUYE la ganancia/perdida en tasa cambiaria
        # (Fila 26 esta ANTES de Utilidad Neta en su hoja, dentro de Total Ingresos No
        # Operativos) -- no es una utilidad "limpia" sin esa linea como se asumio al principio.
        # utilidad_final_q = preliminar + plug reproduce exactamente ese comportamiento
        # (verificado: 30389.95 + 15395.36 = 45785.31, exacto contra el Excel). Se parchea
        # solo 'Resultados del ejercicio' en esf_real -- TOTAL ACTIVOS/PASIVOS/Acumulados no
        # cambian, ya son correctos y no dependen de la utilidad.
        utilidad_final_q = {q: utilidad_externa_q[q] + plug_efectivo_q[q] for q in [1, 2, 3, 4]}
        for row in esf_real.get('rows', []):
            if row.get('partida') == 'Resultados del ejercicio':
                for q in [1, 2, 3, 4]:
                    if q in esf_quarters_available:
                        row['quarters'][q] = round(utilidad_final_q[q], 2)
                break

        for row in esf_real.get('rows', []):
            if row.get('partida') in ('Total Patrimonio', 'TOTAL PASIVOS Y PATRIMONIO'):
                for q in [1, 2, 3, 4]:
                    if q in esf_quarters_available:
                        row['quarters'][q] = round(row['quarters'].get(q, 0.0) + plug_efectivo_q[q], 2)

        # 4. EERR Real final: reinyectar el plug en el mes de cierre correspondiente.
        # Regla confirmada contra el Excel de Yocelin (10-ago-2026): el ajuste consolidado de
        # Ganancia/Perdida en tasa cambiaria SOLO aparece en la unidad Rodeo y en el consolidado
        # -- las demas unidades (PiedeMonte, Terracota, Ucafe, Barinas, Naranjos) no lo llevan.
        # Confirmado con datos literales de "N EERR RODEO" vs "N EERR ULTRAX" (valores identicos)
        # vs "N EERR PIEDEM"/"N EERR TERRA"/"N EERR UCAFE"/"N EERR BARINAS"/"N EERR LOS NA" (vacios).
        unit_recibe_plug = unit in ('', 'Rodeo')
        plug_a_inyectar = plug_efectivo_q if unit_recibe_plug else None
        eerr_real = _calcular_eerr_divisa_real(conn_estados, year, unit, empresa_id=empresa_id, plug_divisa_q=plug_a_inyectar)
        if 'error' in eerr_real:
            return eerr_real

        return {
            'eerr_real': eerr_real,
            'esf_real': esf_real,
        }
    finally:
        if _conn_propia:
            conn_estados.close()

def eerr_completo_v2_ui_adapter(db, year, unit, empresa_id=None):
    from helpers import (
        get_clasificacion, get_grouped_partidas_v2, calcular_muestra_pct_gastos,
        divisor_ejec, divisor_ppto_mes, divisor_prev
    )

    year_prev = str(int(year) - 1)
    if unit:
        uc = "AND unit=?"
        uc_params = [unit]
    elif empresa_id:
        unidades_rows = db.execute('SELECT nombre FROM unidades WHERE empresa_id=?', [empresa_id]).fetchall()
        unidades_list = [r['nombre'] for r in unidades_rows]
        if unidades_list:
            placeholders = ','.join(['?'] * len(unidades_list))
            uc = f"AND unit IN ({placeholders})"
            uc_params = unidades_list
        else:
            uc = "AND unit=?"
            uc_params = ['__EMPRESA_SIN_UNIDADES__']
    else:
        uc = ''
        uc_params = []

    MONTH_TYPES = {
        'ENE': 'A',
        'FEB': 'B',
        'MAR': 'C',
        'ABR': 'B',
        'MAY': 'B',
        'JUN': 'D',
        'JUL': 'B',
        'AGO': 'B',
        'SEPT': 'C',
        'OCT': 'B',
        'NOV': 'B',
        'DIC': 'E',
    }

    # 1. Clasificación
    ing_p, cos_p, gas_p = get_clasificacion(db)

    # 2. Obtener grupos de presentación de mapping_groups_v2
    groups_v2, _ = get_grouped_partidas_v2(db, 'eerr')

    # 3. Leer datos año actual por partida y mes
    rows_curr = db.execute(
        f'''SELECT partida, month, SUM(amount) amount FROM financials
            WHERE year=? {uc} GROUP BY partida, month''',
        [year] + uc_params
    ).fetchall()

    by_partida = {}
    for r in rows_curr:
        by_partida.setdefault(r['partida'], {})[r['month']] = r['amount']

    # Leer datos año anterior (total anual por partida)
    rows_prev = db.execute(
        f'''SELECT partida, SUM(amount) amount FROM financials
            WHERE year=? {uc} GROUP BY partida''',
        [year_prev] + uc_params
    ).fetchall()
    by_prev_raw = {r['partida']: r['amount'] for r in rows_prev}

    # Leer presupuesto por partida y mes
    rows_budget = db.execute(
        f'''SELECT partida, month, SUM(amount) amount FROM budget
            WHERE year=? {uc} GROUP BY partida, month''',
        [year] + uc_params
    ).fetchall()
    by_budget = {}
    for r in rows_budget:
        by_budget.setdefault(r['partida'], {})[r['month']] = r['amount']

    import unicodedata, functools
    @functools.lru_cache(maxsize=None)
    def norm(s):
        # Perf fix (ago-2026): memoizado -- se llamaba miles de veces sobre las
        # mismas keys de data_dict dentro del loop de fallback, sin cachear el
        # resultado (1+ segundo por llamada al motor). Funcion pura, cachear es
        # seguro. Ver ultrax_deuda_tecnica_refactor.md.
        if not s: return ''
        s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
        return s.lower().strip()

    def resolve_leaf_value(partida_name, month, data_dict):
        if partida_name in groups_v2:
            return sum(data_dict.get(p, {}).get(month, 0) for p in groups_v2[partida_name])
        val = data_dict.get(partida_name, {}).get(month, 0)
        if val == 0:
            pn_norm = norm(partida_name)
            for k, v in data_dict.items():
                if norm(k) == pn_norm:
                    return v.get(month, 0)
        return val

    def resolve_leaf_value_prev(partida_name, data_dict):
        if partida_name in groups_v2:
            return sum(data_dict.get(p, 0) for p in groups_v2[partida_name])
        val = data_dict.get(partida_name, 0)
        if val == 0:
            pn_norm = norm(partida_name)
            for k, v in data_dict.items():
                if norm(k) == pn_norm:
                    return v
        return val

    db_overrides = db.execute('SELECT partida_name, target_subtotal FROM eerr_nodes').fetchall()
    effective = build_effective_structure(EERR_STRUCTURE, db_overrides=db_overrides)
    muestra_pct_gastos_map = calcular_muestra_pct_gastos(effective)
    structure_with_levels = [(node['partida_name'], node['is_header'], node['level']) for node in effective]

    # Pre-calcular subtotales para todos los meses
    subtotales_por_mes = {}
    for m in MONTHS:
        subtotales_por_mes[m] = {}
        # Primero popular nodos hoja
        for name, is_header, level in structure_with_levels:
            if not is_header:
                subtotales_por_mes[m][name] = resolve_leaf_value(name, m, by_partida)

        # Luego calcular subtotales jerárquicos de forma recursiva/bottom-up
        for i, (name, is_header, level) in enumerate(structure_with_levels):
            if is_header:
                total = 0
                j = i + 1
                while j < len(structure_with_levels):
                    c_name, c_is_header, c_level = structure_with_levels[j]
                    if c_level <= level:
                        break
                    if not c_is_header:
                        # Excluir cuentas que se duplicarían
                        if c_name in SUBTOTAL_EXCLUSIONS.get(name, []):
                            pass
                        else:
                            total += subtotales_por_mes[m].get(c_name, 0)
                    j += 1
                subtotales_por_mes[m][name] = total
                if name == 'Subtotal Gastos de Comercialización y Logistica':
                    subtotales_por_mes[m][name] += (
                        subtotales_por_mes[m].get('Gastos de comisiones empleados', 0)
                        + subtotales_por_mes[m].get('Gastos de comisiones por venta de personal externo', 0)
                    )

    # Definición de partidas operativas para Total Ingresos
    op_ing_partidas = ing_p - {
        'Ingresos por alquileres',
        'Ingresos por intereses',
        'Ingresos por comisiones',
        'Ingresos por servicios administrativos',
        'Sobrante en ventas',
        'Sobrante de inventarios',
        'Ganancia en venta de activos',
        'Ganancia por tasa cambiaria',
        'Ganancia por diferencias en pagos'
    }

    valores_calculados_por_mes = {}
    ingresos_ejec_mes = {}
    gastos_ejec_mes = {}
    ingresos_ppto_mes = {}
    gastos_ppto_mes = {}

    for m in MONTHS:
        ingresos_operativos = sum(by_partida.get(p, {}).get(m, 0) for p in op_ing_partidas)
        otros_ing = subtotales_por_mes[m].get('Otros Ingresos no Operacionales', 0)
        costo_ventas = sum(by_partida.get(p, {}).get(m, 0) for p in cos_p)
        utilidad_bruta = ingresos_operativos - costo_ventas

        gastos_operacionales = 0
        for nombre in ['Subtotal Gastos de Administración',
                       'Subtotal Gastos de Recursos Humanos',
                       'Subtotal Gastos de Comercialización y Logistica',
                       'Subtotal Gastos de Mercadeo',
                       'Gastos de TI+I']:
            gastos_operacionales += subtotales_por_mes[m].get(nombre, 0)

        comisiones = 0
        for nombre in ['Gastos de comisiones empleados',
                       'Gastos de comisiones empleados del taller',
                       'Gastos de comisiones por venta de personal externo']:
            comisiones += subtotales_por_mes[m].get(nombre, 0)

        utilidad_despues_comisiones = utilidad_bruta - gastos_operacionales
        utilidad_antes_comisiones = utilidad_despues_comisiones + comisiones

        otros_gastos = subtotales_por_mes[m].get('Otros Gastos no Operacionales', 0)
        gastos_impuestos = subtotales_por_mes[m].get('Gastos de impuestos, tasas y contribuciones', 0)
        gastos_intereses = subtotales_por_mes[m].get('Gastos de intereses sobre préstamos', 0)
        depreciaciones = subtotales_por_mes[m].get('Depreciaciones, deterioro y Amortización', 0)

        ebit = utilidad_bruta - gastos_operacionales + gastos_intereses + gastos_impuestos
        ebitda = ebit + depreciaciones

        utilidad_neta = utilidad_despues_comisiones - otros_gastos + otros_ing
        islr = subtotales_por_mes[m].get('ISLR', 0)
        utilidad_neta_despues_islr = utilidad_neta - islr

        totales_mes = {
            'Total Ingresos Operativos': ingresos_operativos,
            'Otros Ingresos no Operacionales': otros_ing,
            'Total Ingresos': ingresos_operativos,
            'Total Costo de Ventas': costo_ventas,
            'Utilidad Bruta': utilidad_bruta,
            'Total Gastos Operacionales': gastos_operacionales,
            'Utilidad antes de Comisiones por Ventas': utilidad_antes_comisiones,
            'Utilidad después de Comisiones por Ventas': utilidad_despues_comisiones,
            'Otros Gastos no Operacionales': otros_gastos,
            'Total Gastos Operacionales y No Operacionales': gastos_operacionales + otros_gastos,
            'Utilidad antes de Intereses e Impuestos (EBIT)': ebit,
            'Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA)': ebitda,
            'Utilidad Neta': utilidad_neta,
            'ISLR': islr,
            'Utilidad Neta despues de ISLR': utilidad_neta_despues_islr,
            'Utilidad Bruta por Venta de Mercancia y Taller': (
                subtotales_por_mes[m].get('Subtotal Ingresos por Venta de Mercancia', 0)
                + subtotales_por_mes[m].get('Subtotal Ingresos por Taller', 0)
                - subtotales_por_mes[m].get('Subtotal Costo de Ventas por Mercancia', 0)
            ),
            'Utilidad Bruta por Servicios': (
                subtotales_por_mes[m].get('Subtotal Ingresos por Servicios', 0)
                - subtotales_por_mes[m].get('Subtotal Costo de Ventas por Servicios', 0)
            ),
            'Utilidad Bruta por Eventos': (
                subtotales_por_mes[m].get('Subtotal Ingresos por Eventos', 0)
                - subtotales_por_mes[m].get('Subtotal Costo de Ventas por Eventos', 0)
            )
        }

        valores_calculados_por_mes[m] = {**subtotales_por_mes[m], **totales_mes}

        ingresos_ejec_mes[m] = ingresos_operativos
        gastos_ejec_mes[m] = gastos_operacionales + otros_gastos
        ingresos_ppto_mes[m] = sum(by_budget.get(p, {}).get(m, 0) for p in op_ing_partidas)
        gastos_ppto_mes[m] = sum(by_budget.get(p, {}).get(m, 0) for p in gas_p)

    # ── Subtotales jerárquicos y totales para AÑO ANTERIOR (fix ago-2026, 10-ago) ──
    # Mismo bug que en _calcular_eerr_divisa_real: prev_val para partidas header
    # usaba valores_calculados_por_mes.get('DIC', {}) -- diciembre del AÑO ACTUAL,
    # no datos reales de by_prev_raw (año anterior).
    subtotales_prev = {}
    for name, is_header, level in structure_with_levels:
        if not is_header:
            subtotales_prev[name] = resolve_leaf_value_prev(name, by_prev_raw)

    for i, (name, is_header, level) in enumerate(structure_with_levels):
        if is_header:
            total = 0
            j = i + 1
            while j < len(structure_with_levels):
                c_name, c_is_header, c_level = structure_with_levels[j]
                if c_level <= level:
                    break
                if not c_is_header:
                    if c_name in SUBTOTAL_EXCLUSIONS.get(name, []):
                        pass
                    else:
                        total += subtotales_prev.get(c_name, 0)
                j += 1
            subtotales_prev[name] = total
            if name == 'Subtotal Gastos de Comercialización y Logistica':
                subtotales_prev[name] += (
                    subtotales_prev.get('Gastos de comisiones empleados', 0)
                    + subtotales_prev.get('Gastos de comisiones por venta de personal externo', 0)
                )

    ingresos_operativos_prev = sum(by_prev_raw.get(p, 0) for p in op_ing_partidas)
    otros_ing_prev = subtotales_prev.get('Otros Ingresos no Operacionales', 0)
    costo_ventas_prev = sum(by_prev_raw.get(p, 0) for p in cos_p)
    utilidad_bruta_prev = ingresos_operativos_prev + otros_ing_prev - costo_ventas_prev

    gastos_operacionales_prev = 0
    for nombre in ['Subtotal Gastos de Administración',
                   'Subtotal Gastos de Recursos Humanos',
                   'Subtotal Gastos de Comercialización y Logistica',
                   'Subtotal Gastos de Mercadeo',
                   'Gastos de TI+I']:
        gastos_operacionales_prev += subtotales_prev.get(nombre, 0)

    comisiones_prev = 0
    for nombre in ['Gastos de comisiones empleados',
                   'Gastos de comisiones empleados del taller',
                   'Gastos de comisiones por venta de personal externo']:
        comisiones_prev += subtotales_prev.get(nombre, 0)

    utilidad_despues_comisiones_prev = utilidad_bruta_prev - gastos_operacionales_prev
    utilidad_antes_comisiones_prev = utilidad_despues_comisiones_prev + comisiones_prev

    otros_gastos_prev = subtotales_prev.get('Otros Gastos no Operacionales', 0)
    gastos_impuestos_prev = subtotales_prev.get('Gastos de impuestos, tasas y contribuciones', 0)
    gastos_intereses_prev = subtotales_prev.get('Gastos de intereses sobre préstamos', 0)
    depreciaciones_prev = subtotales_prev.get('Depreciaciones, deterioro y Amortización', 0)

    ebit_prev = utilidad_bruta_prev - gastos_operacionales_prev + gastos_intereses_prev + gastos_impuestos_prev
    ebitda_prev = ebit_prev + depreciaciones_prev

    utilidad_neta_prev = utilidad_despues_comisiones_prev - otros_gastos_prev
    islr_prev = subtotales_prev.get('ISLR', 0)
    utilidad_neta_despues_islr_prev = utilidad_neta_prev - islr_prev

    totales_prev_dict = {
        'Total Ingresos Operativos': ingresos_operativos_prev,
        'Otros Ingresos no Operacionales': otros_ing_prev,
        'Total Ingresos': ingresos_operativos_prev + otros_ing_prev,
        'Total Costo de Ventas': costo_ventas_prev,
        'Utilidad Bruta': utilidad_bruta_prev,
        'Total Gastos Operacionales': gastos_operacionales_prev,
        'Utilidad antes de Comisiones por Ventas': utilidad_antes_comisiones_prev,
        'Utilidad después de Comisiones por Ventas': utilidad_despues_comisiones_prev,
        'Otros Gastos no Operacionales': otros_gastos_prev,
        'Total Gastos Operacionales y No Operacionales': gastos_operacionales_prev + otros_gastos_prev,
        'Utilidad antes de Intereses e Impuestos (EBIT)': ebit_prev,
        'Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA)': ebitda_prev,
        'Utilidad Neta': utilidad_neta_prev,
        'ISLR': islr_prev,
        'Utilidad Neta despues de ISLR': utilidad_neta_despues_islr_prev,
        'Utilidad Bruta por Venta de Mercancia y Taller': (
            subtotales_prev.get('Subtotal Ingresos por Venta de Mercancia', 0)
            + subtotales_prev.get('Subtotal Ingresos por Taller', 0)
            - subtotales_prev.get('Subtotal Costo de Ventas por Mercancia', 0)
        ),
        'Utilidad Bruta por Servicios': (
            subtotales_prev.get('Subtotal Ingresos por Servicios', 0)
            - subtotales_prev.get('Subtotal Costo de Ventas por Servicios', 0)
        ),
        'Utilidad Bruta por Eventos': (
            subtotales_prev.get('Subtotal Ingresos por Eventos', 0)
            - subtotales_prev.get('Subtotal Costo de Ventas por Eventos', 0)
        )
    }
    valores_calculados_prev = {**subtotales_prev, **totales_prev_dict}

    ingresos_prev = sum(by_prev_raw.get(p, 0) for p in op_ing_partidas)
    gastos_prev = sum(by_prev_raw.get(p, 0) for p in gas_p)

    def safe_pct(num, den):
        return round(num / den * 100, 1) if den != 0 else 0

    def safe_var(val, base):
        if base == 0: return None
        return round((val - base) / abs(base) * 100, 1)

    rows = []
    for node in effective:
        partida_name = node['partida_name']
        is_header = node['is_header']
        parent = None
        bold = node['bold']
        bg_color = node['bg_color']
        es_nota = node['es_nota']
        parent_name = node['parent_name']
        indent = node['indent']

        if is_header:
            prev_val = valores_calculados_prev.get(partida_name, 0)
        else:
            prev_val = resolve_leaf_value_prev(partida_name, by_prev_raw)

        prev_pct_vtas = safe_pct(prev_val, divisor_prev(partida_name, by_prev_raw, ingresos_prev, ing_p))
        prev_pct_gastos = safe_pct(prev_val, gastos_prev)

        meses_data = []
        acum_ejec = 0
        acum_ppto = 0
        acum_ing_ejec = 0
        acum_ing_ppto = 0
        acum_gas_ejec = 0
        acum_gas_ppto = 0
        val_ejec_mes_anterior = None

        for m in MONTHS:
            month_type = MONTH_TYPES[m]

            if is_header:
                val_ejec = valores_calculados_por_mes[m].get(partida_name, 0)
                val_ppto = 0
            else:
                val_ejec = resolve_leaf_value(partida_name, m, by_partida)
                val_ppto = resolve_leaf_value(partida_name, m, by_budget)

            divisor_vtas_mes = divisor_ejec(partida_name, subtotales_por_mes[m], ingresos_ejec_mes[m], by_partida, m, ing_p)
            divisor_vtas_ppto = divisor_ppto_mes(partida_name, by_budget, m, ingresos_ppto_mes[m], ing_p)

            acum_ejec += val_ejec
            acum_ppto += val_ppto
            acum_ing_ejec += divisor_vtas_mes
            acum_ing_ppto += divisor_vtas_ppto
            acum_gas_ejec += gastos_ejec_mes[m]
            acum_gas_ppto += gastos_ppto_mes[m]

            pct_vtas_ejec = safe_pct(val_ejec, divisor_vtas_mes)
            pct_gastos_ejec = safe_pct(val_ejec, gastos_ejec_mes[m])

            mes_data = {
                'type': month_type,
                'month': m,
                'ejecutado': {
                    'valor': round(val_ejec, 2),
                    'pct_vtas': pct_vtas_ejec,
                    'pct_gastos': pct_gastos_ejec,
                }
            }

            if month_type != 'A':
                mes_data['vari_rel'] = safe_var(val_ejec, val_ejec_mes_anterior) if val_ejec_mes_anterior is not None else None

                if month_type == 'E':  # DIC
                    mes_data['anio'] = {
                        'valor': round(acum_ejec, 2),
                        'pct_vtas': safe_pct(acum_ejec, acum_ing_ejec),
                        'pct_gastos': safe_pct(acum_ejec, acum_gas_ejec),
                    }
                else:
                    mes_data['acum_ejecutado'] = {
                        'valor': round(acum_ejec, 2),
                        'pct_vtas': safe_pct(acum_ejec, acum_ing_ejec),
                        'pct_gastos': safe_pct(acum_ejec, acum_gas_ejec),
                    }

                if month_type in ('C', 'D', 'E'):
                    mes_data['acum_ppto'] = {
                        'valor': round(acum_ppto, 2),
                        'pct_vtas': safe_pct(acum_ppto, acum_ing_ppto),
                    }
                    mes_data['var_ppto'] = safe_var(acum_ejec, acum_ppto)

                    if month_type == 'D':  # JUN
                        prom_ejec = acum_ejec / 6
                        prom_ppto = acum_ppto / 6
                        prom_ing_ejec = acum_ing_ejec / 6
                        prom_ing_ppto = acum_ing_ppto / 6
                        prom_gas_ejec = acum_gas_ejec / 6
                        prom_gas_ppto = acum_gas_ppto / 6

                        mes_data['prom_6_ejec'] = {
                            'valor': round(prom_ejec, 2),
                            'pct_vtas': safe_pct(prom_ejec, prom_ing_ejec),
                            'pct_gastos': safe_pct(prom_ejec, prom_gas_ejec),
                        }
                        mes_data['prom_6_ppto'] = {
                            'valor': round(prom_ppto, 2),
                            'pct_vtas': safe_pct(prom_ppto, prom_ing_ppto),
                        }
                        mes_data['var_ppto_prom'] = safe_var(prom_ejec, prom_ppto)

            meses_data.append(mes_data)
            val_ejec_mes_anterior = val_ejec

        rows.append({
            'partida': partida_name,
            'is_header': is_header,
            'parent': parent,
            'bold': bold,
            'bg_color': bg_color,
            'es_nota': es_nota,
            'parent_name': parent_name,
            'indent': indent,
            'muestra_pct_gastos': muestra_pct_gastos_map.get(partida_name, False),
            'year_prev': {
                'valor': round(prev_val, 2),
                'pct_vtas': prev_pct_vtas,
                'pct_gastos': prev_pct_gastos,
            },
            'meses': meses_data,
        })

    return {
        'year': year,
        'year_prev': year_prev,
        'unit': unit,
        'rows': rows,
    }



def _calcular_eerr_divisa_real(db, year, unit, empresa_id=None, plug_divisa_q=None):
    """
    Calcula el Estado de Resultados COMPLETO con ajuste de divisa real.
    Misma estructura que /api/eerr/completo (119 partidas, tipos A/B/C/D/E)
    pero con montos ajustados por factor diferencial según % Cash/BCV.
    Función interna reutilizable - no es vista Flask. Usada por
    /api/eerr/divisa_real y /api/dashboard_divisa_real.
    Parámetros: year, unit
    Retorna: dict con year, year_prev, unit, rows
    """
    from helpers import (
        get_clasificacion, get_grouped_partidas_v2, calcular_muestra_pct_gastos,
        divisor_ejec, divisor_ppto_mes, divisor_prev, aplicar_factor_divisa
    )

    year_prev = str(int(year) - 1)
    if unit:
        uc = "AND unit=?"
        uc_params = [unit]
    elif empresa_id is not None:
        unidades_empresa = [r['nombre'] for r in db.execute(
            'SELECT nombre FROM unidades WHERE empresa_id=?', (empresa_id,)
        ).fetchall()]
        if unidades_empresa:
            placeholders = ','.join('?' * len(unidades_empresa))
            uc = f"AND unit IN ({placeholders})"
            uc_params = unidades_empresa
        else:
            uc = "AND 1=0"
            uc_params = []
    else:
        uc = ''
        uc_params = []

    MONTH_TYPES = {
        'ENE': 'A', 'FEB': 'B', 'MAR': 'C', 'ABR': 'B', 'MAY': 'B', 'JUN': 'D',
        'JUL': 'B', 'AGO': 'B', 'SEPT': 'C', 'OCT': 'B', 'NOV': 'B', 'DIC': 'E',
    }

    # ── PASO 4: CARGAR TASAS DESDE tasas_periodo ──
    tasas_rows = db.execute(
        'SELECT month, tasa_bcv_promedio, tasa_paralela_promedio, factor_diferencial FROM tasas_periodo WHERE year=?',
        [year]
    ).fetchall()
    
    tasas_by_month = {}
    for r in tasas_rows:
        m = r['month']
        bcv = r['tasa_bcv_promedio']
        paralela = r['tasa_paralela_promedio']
        
        # Validación de tasas
        if bcv is None or bcv <= 0:
            return {'error': f"Tasa BCV promedio inválida o cero para el mes {m} {year}"}
        if paralela is None or paralela <= 0:
            return {'error': f"Tasa paralela promedio inválida o cero para el mes {m} {year}"}
            
        diferencial = paralela / bcv
        tasas_by_month[m] = {
            'diferencial': diferencial
        }

    # ── PASO 1+2+3 (REESCRITO): LEER DETALLE POR CUENTA DESDE financials_detail ──
    rows_curr = db.execute(
        f'''SELECT partida, month, unit, odoo_code, amount_sign as amount FROM financials_detail
            WHERE year=? AND report_type='eerr' {uc}''',
        [year] + uc_params
    ).fetchall()

    months_in_data = set(r['month'] for r in rows_curr)
    for m in months_in_data:
        if m not in tasas_by_month:
            return {'error': f"Faltan tasas de cambio (tasas_periodo) para el periodo {year}/{m}"}

    metodos_rows = db.execute(
        'SELECT month, unit, odoo_code, pct_cash FROM metodo_pago_cuenta WHERE year=?',
        [year]
    ).fetchall()
    metodos_map = {(r['month'], r['unit'], r['odoo_code']): r['pct_cash'] for r in metodos_rows}

    cuentas_sin_ajuste = {r['odoo_code'] for r in db.execute(
        'SELECT odoo_code FROM mapping WHERE excluir_divisa_real=1'
    ).fetchall()}

    by_partida = {}
    for r in rows_curr:
        partida = r['partida']
        month = r['month']
        row_unit = r['unit']
        odoo_code = r['odoo_code']
        amount_literal = r['amount']

        if odoo_code in cuentas_sin_ajuste:
            # Metodología EERR Real / ESF Real (ago-2026): estas cuentas se excluyen
            # por completo del EERR Real. El valor de Ganancia/Pérdida en tasa cambiaria
            # ya no viene de Odoo -- se recalcula como plug desde ESF Real y se inyecta
            # aparte en el mes de cierre de cada trimestre (ver calcular_estados_reales).
            continue

        pct_cash = metodos_map.get((month, row_unit, odoo_code))
        diferencial = tasas_by_month[month]['diferencial']
        amount_ajustado = aplicar_factor_divisa(amount_literal, pct_cash, diferencial)

        by_partida.setdefault(partida, {})[month] = by_partida.get(partida, {}).get(month, 0) + amount_ajustado

    # Metodología EERR Real / ESF Real (ago-2026): inyectar el plug de Ganancia/Pérdida
    # en tasa cambiaria (calculado por calcular_estados_reales desde el ESF Real) en el
    # mes de cierre del trimestre correspondiente, ANTES de calcular subtotales/totales,
    # para que la cascada completa (Otros Gastos no Operacionales, Utilidad Neta, EBIT,
    # etc.) quede consistente con el ajuste.
    if plug_divisa_q is not None:
        quarter_close_month = {1: 'MAR', 2: 'JUN', 3: 'SEPT', 4: 'DIC'}
        for q in sorted(plug_divisa_q.keys()):
            valor_acum_q = plug_divisa_q[q]
            valor_acum_prev = plug_divisa_q.get(q - 1, 0.0)
            valor_incremental = valor_acum_q - valor_acum_prev
            month = quarter_close_month.get(q)
            if not month or valor_incremental == 0:
                continue
            if valor_incremental > 0:
                partida_destino = 'Ganancia por tasa cambiaria'
            else:
                partida_destino = 'Pérdida en tasa cambiaria'
            by_partida.setdefault(partida_destino, {})
            by_partida[partida_destino][month] = by_partida[partida_destino].get(month, 0) + abs(valor_incremental)

    # Año anterior (sin ajuste - usar literal)
    rows_prev = db.execute(
        f'''SELECT partida, SUM(amount) amount FROM financials
            WHERE year=? {uc} GROUP BY partida''',
        [year_prev] + uc_params
    ).fetchall()
    by_prev_raw = {r['partida']: r['amount'] for r in rows_prev}

    # Presupuesto (sin ajuste)
    rows_budget = db.execute(
        f'''SELECT partida, month, SUM(amount) amount FROM budget
            WHERE year=? {uc} GROUP BY partida, month''',
        [year] + uc_params
    ).fetchall()
    by_budget = {}
    for r in rows_budget:
        by_budget.setdefault(r['partida'], {})[r['month']] = r['amount']

    # Clasificación
    ing_p, cos_p, gas_p = get_clasificacion(db)

    # Obtener grupos de presentación de mapping_groups_v2
    groups_v2, _ = get_grouped_partidas_v2(db, 'eerr')

    import unicodedata, functools
    @functools.lru_cache(maxsize=None)
    def norm(s):
        # Perf fix (ago-2026): memoizado -- ver nota equivalente en
        # eerr_completo_v2_ui_adapter, mismo patron duplicado.
        if not s: return ''
        s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
        return s.lower().strip()

    def resolve_leaf_value(partida_name, month, data_dict):
        if partida_name in groups_v2:
            return sum(data_dict.get(p, {}).get(month, 0) for p in groups_v2[partida_name])
        val = data_dict.get(partida_name, {}).get(month, 0)
        if val == 0:
            pn_norm = norm(partida_name)
            for k, v in data_dict.items():
                if norm(k) == pn_norm:
                    return v.get(month, 0)
        return val

    def resolve_leaf_value_prev(partida_name, data_dict):
        if partida_name in groups_v2:
            return sum(data_dict.get(p, 0) for p in groups_v2[partida_name])
        val = data_dict.get(partida_name, 0)
        if val == 0:
            pn_norm = norm(partida_name)
            for k, v in data_dict.items():
                if norm(k) == pn_norm:
                    return v
        return val

    # ── PASO 7: AGREGACIÓN JERÁRQUICA V2 DE SUBTOTALES ──
    db_overrides = db.execute('SELECT partida_name, target_subtotal FROM eerr_nodes').fetchall()
    effective = build_effective_structure(EERR_STRUCTURE, db_overrides=db_overrides)
    muestra_pct_gastos_map = calcular_muestra_pct_gastos(effective)
    structure_with_levels = [(node['partida_name'], node['is_header'], node['level']) for node in effective]

    subtotales_por_mes = {}
    for m in MONTHS:
        subtotales_por_mes[m] = {}
        for name, is_header, level in structure_with_levels:
            if not is_header:
                subtotales_por_mes[m][name] = resolve_leaf_value(name, m, by_partida)

        for i, (name, is_header, level) in enumerate(structure_with_levels):
            if is_header:
                total = 0
                j = i + 1
                while j < len(structure_with_levels):
                    c_name, c_is_header, c_level = structure_with_levels[j]
                    if c_level <= level:
                        break
                    if not c_is_header:
                        # Excluir cuentas que se duplicarían
                        if name == 'Subtotal Gastos de Administración' and c_name in [
                            'Gasto por impuesto a las pensiones',
                            'Gastos de IGTF',
                            'Gastos de comisiones bancarias',
                            'Gastos de intereses de mora',
                            'Gastos de mantenimiento y reparación a la propiedad alq.',
                            'Gastos de mantenimiento y reparación de edificaciones',
                            'Gastos de mantenimiento y reparación de maquinaria y equipos',
                            'Gastos de mantenimiento y reparación de mobiliario y equipo',
                            'Gastos de mantenimiento y reparación de vehiculo',
                            'Gastos de comida por viáticos administrativos',
                            'Gastos de hospedaje por viáticos administrativos',
                            'Gastos de pasajes por viáticos administrativos',
                            'Gastos de transporte por viáticos administrativos',
                            'Otros gastos de viáticos administrativos',
                            'Gastos de seguro de edificaciones',
                            'Gastos de seguro de vehiculos',
                            'Gasto por otras tasas',
                            'Gastos de impuesto por licencia de actividades economicas',
                            'Gastos de impuesto por publicidad',
                            'Gastos de patente vehicular',
                            'Gastos de tasa sencamer',
                            'Gastos de tasas de notaria y registro',
                            'Gastos de amortización de software',
                            'Gastos de depreciación de edificaciones',
                            'Gastos de depreciación de maquinarias y equipos',
                            'Gastos de depreciación de mobiliario y equipo',
                            'Gastos de depreciación de vehículos',
                            'Gastos de deterioro de edificaciones',
                            'Gastos de deterioro de maquinarias y equipos',
                            'Gastos de deterioro de mobiliario y equipo',
                            'Gastos de deterioro de vehículos',
                            'Gastos de deterioro por cuentas incobrables',
                            'Gastos de intereses sobre préstamos bancarios',
                            'Gastos de intereses sobre préstamos de terceros'
                        ]:
                            pass
                        elif name == 'Subtotal Gastos de Recursos Humanos' and c_name in [
                            'Gastos de uniformes y dotación al personal'
                        ]:
                            pass
                        elif name == 'Subtotal Gastos de Mercadeo' and c_name in [
                            'Gastos de impresiones de material gráfico',
                            'Gastos de patrocinio y donación',
                            'Gastos de decoración'
                        ]:
                            pass
                        elif name == 'Subtotal Gastos de Comercialización y Logistica' and c_name in [
                            'Gastos de comida por viáticos comerciales',
                            'Gastos de hospedaje por viáticos comerciales',
                            'Gastos de pasajes por viáticos comerciales',
                            'Gastos de transporte por viáticos comerciales',
                            'Otros gastos de viáticos comerciales',
                            'Gastos de almacenaje sobre compras no incluídos en el costo',
                            'Gastos de armado de bicicletas no incluídos en el costo',
                            'Gastos de bolsas no incluídos en el costo',
                            'Gastos de embalaje no incluídos en el costo',
                            'Gastos de etiquetas no incluídos en el costo',
                            'Gastos de importación no incluídos en el costo',
                            'Gastos de seguro de mercancía no incluídos en el costo',
                            'Gastos de títulos de propiedad no incluídos en el costo',
                            'Gastos por gasoil',
                            'Gastos por gasolina',
                            'Gastos de alquiler Stand y/o ferias comerciales',
                            'Gastos de otros viáticos Stand y/o ferias comerciales',
                            'Gastos de pasajes Stand y/o ferias comerciales',
                            'Gastos de premiaciones, donaciones Stand y/o ferias comerciales',
                            'Gastos de publicidad Stand y/o ferias comerciales',
                            'Gastos de viáticos comida Stand y/o ferias comerciales',
                            'Gastos de viáticos hospedaje Stand y/o ferias comerciales',
                            'Gastos de viáticos transporte Stand y/o ferias comerciales'
                        ]:
                            pass
                        elif name == 'Gastos de TI+I' and c_name in [
                            'Gastos de dominio de página web',
                            'Gastos de servidores',
                            'Gastos de software tecnológico'
                        ]:
                            pass
                        elif name == 'Otros Gastos no Operacionales' and c_name in [
                            'Deterioro de inventarios',
                            'Faltante de inventarios'
                        ]:
                            pass
                        else:
                            total += subtotales_por_mes[m].get(c_name, 0)
                    j += 1
                subtotales_por_mes[m][name] = total
                if name == 'Subtotal Gastos de Comercialización y Logistica':
                    subtotales_por_mes[m][name] += (
                        subtotales_por_mes[m].get('Gastos de comisiones empleados', 0)
                        + subtotales_por_mes[m].get('Gastos de comisiones por venta de personal externo', 0)
                    )

    # Definición de partidas operativas para Total Ingresos
    op_ing_partidas = ing_p - {
        'Ingresos por alquileres',
        'Ingresos por intereses',
        'Ingresos por comisiones',
        'Ingresos por servicios administrativos',
        'Sobrante en ventas',
        'Sobrante de inventarios',
        'Ganancia en venta de activos',
        'Ganancia por tasa cambiaria',
        'Ganancia por diferencias en pagos'
    }

    valores_calculados_por_mes = {}
    ingresos_ejec_mes = {}
    gastos_ejec_mes = {}
    ingresos_ppto_mes = {}
    gastos_ppto_mes = {}

    for m in MONTHS:
        ingresos_operativos = sum(by_partida.get(p, {}).get(m, 0) for p in op_ing_partidas)
        otros_ing = subtotales_por_mes[m].get('Otros Ingresos no Operacionales', 0)
        costo_ventas = sum(by_partida.get(p, {}).get(m, 0) for p in cos_p)
        utilidad_bruta = ingresos_operativos - costo_ventas

        gastos_operacionales = 0
        for nombre in ['Subtotal Gastos de Administración',
                       'Subtotal Gastos de Recursos Humanos',
                       'Subtotal Gastos de Comercialización y Logistica',
                       'Subtotal Gastos de Mercadeo',
                       'Gastos de TI+I']:
            gastos_operacionales += subtotales_por_mes[m].get(nombre, 0)

        comisiones = 0
        for nombre in ['Gastos de comisiones empleados',
                       'Gastos de comisiones empleados del taller',
                       'Gastos de comisiones por venta de personal externo']:
            comisiones += subtotales_por_mes[m].get(nombre, 0)

        utilidad_despues_comisiones = utilidad_bruta - gastos_operacionales
        utilidad_antes_comisiones = utilidad_despues_comisiones + comisiones

        otros_gastos = subtotales_por_mes[m].get('Otros Gastos no Operacionales', 0)
        gastos_impuestos = subtotales_por_mes[m].get('Gastos de impuestos, tasas y contribuciones', 0)
        gastos_intereses = subtotales_por_mes[m].get('Gastos de intereses sobre préstamos', 0)
        depreciaciones = subtotales_por_mes[m].get('Depreciaciones, deterioro y Amortización', 0)

        ebit = utilidad_bruta - gastos_operacionales + gastos_intereses + gastos_impuestos
        ebitda = ebit + depreciaciones

        utilidad_neta = utilidad_despues_comisiones - otros_gastos + otros_ing
        islr = subtotales_por_mes[m].get('ISLR', 0)
        utilidad_neta_despues_islr = utilidad_neta - islr

        totales_mes = {
            'Total Ingresos Operativos': ingresos_operativos,
            'Otros Ingresos no Operacionales': otros_ing,
            'Total Ingresos': ingresos_operativos,
            'Total Costo de Ventas': costo_ventas,
            'Utilidad Bruta': utilidad_bruta,
            'Total Gastos Operacionales': gastos_operacionales,
            'Utilidad antes de Comisiones por Ventas': utilidad_antes_comisiones,
            'Utilidad después de Comisiones por Ventas': utilidad_despues_comisiones,
            'Otros Gastos no Operacionales': otros_gastos,
            'Total Gastos Operacionales y No Operacionales': gastos_operacionales + otros_gastos,
            'Utilidad antes de Intereses e Impuestos (EBIT)': ebit,
            'Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA)': ebitda,
            'Utilidad Neta': utilidad_neta,
            'ISLR': islr,
            'Utilidad Neta despues de ISLR': utilidad_neta_despues_islr,
            'Utilidad Bruta por Venta de Mercancia y Taller': (
                subtotales_por_mes[m].get('Subtotal Ingresos por Venta de Mercancia', 0)
                + subtotales_por_mes[m].get('Subtotal Ingresos por Taller', 0)
                - subtotales_por_mes[m].get('Subtotal Costo de Ventas por Mercancia', 0)
            ),
            'Utilidad Bruta por Servicios': (
                subtotales_por_mes[m].get('Subtotal Ingresos por Servicios', 0)
                - subtotales_por_mes[m].get('Subtotal Costo de Ventas por Servicios', 0)
            ),
            'Utilidad Bruta por Eventos': (
                subtotales_por_mes[m].get('Subtotal Ingresos por Eventos', 0)
                - subtotales_por_mes[m].get('Subtotal Costo de Ventas por Eventos', 0)
            )
        }

        valores_calculados_por_mes[m] = {**subtotales_por_mes[m], **totales_mes}

        ingresos_ejec_mes[m] = ingresos_operativos
        gastos_ejec_mes[m] = gastos_operacionales + otros_gastos
        ingresos_ppto_mes[m] = sum(by_budget.get(p, {}).get(m, 0) for p in op_ing_partidas)
        gastos_ppto_mes[m] = sum(by_budget.get(p, {}).get(m, 0) for p in gas_p)

    # ── Subtotales jerárquicos y totales para AÑO ANTERIOR (fix ago-2026, 10-ago) ──
    # Antes, prev_val para partidas header usaba valores_calculados_por_mes.get('DIC', {})
    # -- es decir, diciembre del AÑO ACTUAL, no datos reales de by_prev_raw (año anterior).
    # Esto mostraba en pantalla un numero que no correspondia al año anterior real.
    subtotales_prev = {}
    for name, is_header, level in structure_with_levels:
        if not is_header:
            subtotales_prev[name] = resolve_leaf_value_prev(name, by_prev_raw)

    for i, (name, is_header, level) in enumerate(structure_with_levels):
        if is_header:
            total = 0
            j = i + 1
            while j < len(structure_with_levels):
                c_name, c_is_header, c_level = structure_with_levels[j]
                if c_level <= level:
                    break
                if not c_is_header:
                    if name == 'Subtotal Gastos de Administración' and c_name in [
                        'Gasto por impuesto a las pensiones',
                        'Gastos de IGTF',
                        'Gastos de comisiones bancarias',
                        'Gastos de intereses de mora',
                        'Gastos de mantenimiento y reparación a la propiedad alq.',
                        'Gastos de mantenimiento y reparación de edificaciones',
                        'Gastos de mantenimiento y reparación de maquinarias y equipos',
                        'Gastos de mantenimiento y reparación de mobiliario y equipo',
                        'Gastos de mantenimiento y reparación de vehiculo',
                        'Gastos de comida por viáticos administrativos',
                        'Gastos de hospedaje por viáticos administrativos',
                        'Gastos de pasajes por viáticos administrativos',
                        'Gastos de transporte por viáticos administrativos',
                        'Otros gastos de viáticos administrativos',
                        'Gastos de seguro de edificaciones',
                        'Gastos de seguro de vehiculos',
                        'Gasto por otras tasas',
                        'Gastos de impuesto por licencia de actividades economicas',
                        'Gastos de impuesto por publicidad',
                        'Gastos de patente vehicular',
                        'Gastos de tasa sencamer',
                        'Gastos de tasas de notaria y registro',
                        'Gastos de amortización de software',
                        'Gastos de depreciación de edificaciones',
                        'Gastos de depreciación de maquinarias y equipos',
                        'Gastos de depreciación de mobiliario y equipo',
                        'Gastos de depreciación de vehículos',
                        'Gastos de deterioro de edificaciones',
                        'Gastos de deterioro de maquinarias y equipos',
                        'Gastos de deterioro de mobiliario y equipo',
                        'Gastos de deterioro de vehículos',
                        'Gastos de deterioro por cuentas incobrables',
                        'Gastos de intereses sobre préstamos bancarios',
                        'Gastos de intereses sobre préstamos de terceros'
                    ]:
                        pass
                    elif name == 'Subtotal Gastos de Recursos Humanos' and c_name in [
                        'Gastos de uniformes y dotación al personal'
                    ]:
                        pass
                    elif name == 'Subtotal Gastos de Mercadeo' and c_name in [
                        'Gastos de impresiones de material gráfico',
                        'Gastos de patrocinio y donación',
                        'Gastos de decoración'
                    ]:
                        pass
                    elif name == 'Subtotal Gastos de Comercialización y Logistica' and c_name in [
                        'Gastos de comida por viáticos comerciales',
                        'Gastos de hospedaje por viáticos comerciales',
                        'Gastos de pasajes por viáticos comerciales',
                        'Gastos de transporte por viáticos comerciales',
                        'Otros gastos de viáticos comerciales',
                        'Gastos de almacenaje sobre compras no incluídos en el costo',
                        'Gastos de armado de bicicletas no incluídos en el costo',
                        'Gastos de bolsas no incluídos en el costo',
                        'Gastos de embalaje no incluídos en el costo',
                        'Gastos de etiquetas no incluídos en el costo',
                        'Gastos de importación no incluídos en el costo',
                        'Gastos de seguro de mercancía no incluídos en el costo',
                        'Gastos de títulos de propiedad no incluídos en el costo',
                        'Gastos por gasoil',
                        'Gastos por gasolina',
                        'Gastos de alquiler Stand y/o ferias comerciales',
                        'Gastos de otros viáticos Stand y/o ferias comerciales',
                        'Gastos de pasajes Stand y/o ferias comerciales',
                        'Gastos de premiaciones, donaciones Stand y/o ferias comerciales',
                        'Gastos de publicidad Stand y/o ferias comerciales',
                        'Gastos de viáticos comida Stand y/o ferias comerciales',
                        'Gastos de viáticos hospedaje Stand y/o ferias comerciales',
                        'Gastos de viáticos transporte Stand y/o ferias comerciales'
                    ]:
                        pass
                    elif name == 'Gastos de TI+I' and c_name in [
                        'Gastos de dominio de página web',
                        'Gastos de servidores',
                        'Gastos de software tecnológico'
                    ]:
                        pass
                    elif name == 'Otros Gastos no Operacionales' and c_name in [
                        'Deterioro de inventarios',
                        'Faltante de inventarios'
                    ]:
                        pass
                    else:
                        total += subtotales_prev.get(c_name, 0)
                j += 1
            subtotales_prev[name] = total
            if name == 'Subtotal Gastos de Comercialización y Logistica':
                subtotales_prev[name] += (
                    subtotales_prev.get('Gastos de comisiones empleados', 0)
                    + subtotales_prev.get('Gastos de comisiones por venta de personal externo', 0)
                )

    ingresos_operativos_prev = sum(by_prev_raw.get(p, 0) for p in op_ing_partidas)
    otros_ing_prev = subtotales_prev.get('Otros Ingresos no Operacionales', 0)
    costo_ventas_prev = sum(by_prev_raw.get(p, 0) for p in cos_p)
    utilidad_bruta_prev = ingresos_operativos_prev + otros_ing_prev - costo_ventas_prev

    gastos_operacionales_prev = 0
    for nombre in ['Subtotal Gastos de Administración',
                   'Subtotal Gastos de Recursos Humanos',
                   'Subtotal Gastos de Comercialización y Logistica',
                   'Subtotal Gastos de Mercadeo',
                   'Gastos de TI+I']:
        gastos_operacionales_prev += subtotales_prev.get(nombre, 0)

    comisiones_prev = 0
    for nombre in ['Gastos de comisiones empleados',
                   'Gastos de comisiones empleados del taller',
                   'Gastos de comisiones por venta de personal externo']:
        comisiones_prev += subtotales_prev.get(nombre, 0)

    utilidad_despues_comisiones_prev = utilidad_bruta_prev - gastos_operacionales_prev
    utilidad_antes_comisiones_prev = utilidad_despues_comisiones_prev + comisiones_prev

    otros_gastos_prev = subtotales_prev.get('Otros Gastos no Operacionales', 0)
    gastos_impuestos_prev = subtotales_prev.get('Gastos de impuestos, tasas y contribuciones', 0)
    gastos_intereses_prev = subtotales_prev.get('Gastos de intereses sobre préstamos', 0)
    depreciaciones_prev = subtotales_prev.get('Depreciaciones, deterioro y Amortización', 0)

    ebit_prev = utilidad_bruta_prev - gastos_operacionales_prev + gastos_intereses_prev + gastos_impuestos_prev
    ebitda_prev = ebit_prev + depreciaciones_prev

    utilidad_neta_prev = utilidad_despues_comisiones_prev - otros_gastos_prev
    islr_prev = subtotales_prev.get('ISLR', 0)
    utilidad_neta_despues_islr_prev = utilidad_neta_prev - islr_prev

    totales_prev_dict = {
        'Total Ingresos Operativos': ingresos_operativos_prev,
        'Otros Ingresos no Operacionales': otros_ing_prev,
        'Total Ingresos': ingresos_operativos_prev + otros_ing_prev,
        'Total Costo de Ventas': costo_ventas_prev,
        'Utilidad Bruta': utilidad_bruta_prev,
        'Total Gastos Operacionales': gastos_operacionales_prev,
        'Utilidad antes de Comisiones por Ventas': utilidad_antes_comisiones_prev,
        'Utilidad después de Comisiones por Ventas': utilidad_despues_comisiones_prev,
        'Otros Gastos no Operacionales': otros_gastos_prev,
        'Total Gastos Operacionales y No Operacionales': gastos_operacionales_prev + otros_gastos_prev,
        'Utilidad antes de Intereses e Impuestos (EBIT)': ebit_prev,
        'Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA)': ebitda_prev,
        'Utilidad Neta': utilidad_neta_prev,
        'ISLR': islr_prev,
        'Utilidad Neta despues de ISLR': utilidad_neta_despues_islr_prev,
        'Utilidad Bruta por Venta de Mercancia y Taller': (
            subtotales_prev.get('Subtotal Ingresos por Venta de Mercancia', 0)
            + subtotales_prev.get('Subtotal Ingresos por Taller', 0)
            - subtotales_prev.get('Subtotal Costo de Ventas por Mercancia', 0)
        ),
        'Utilidad Bruta por Servicios': (
            subtotales_prev.get('Subtotal Ingresos por Servicios', 0)
            - subtotales_prev.get('Subtotal Costo de Ventas por Servicios', 0)
        ),
        'Utilidad Bruta por Eventos': (
            subtotales_prev.get('Subtotal Ingresos por Eventos', 0)
            - subtotales_prev.get('Subtotal Costo de Ventas por Eventos', 0)
        )
    }
    valores_calculados_prev = {**subtotales_prev, **totales_prev_dict}

    ingresos_prev = sum(by_prev_raw.get(p, 0) for p in op_ing_partidas)
    gastos_prev = sum(by_prev_raw.get(p, 0) for p in gas_p)

    def safe_pct(num, den):
        return round(num / den * 100, 1) if den != 0 else 0

    def safe_var(val, base):
        if base == 0: return None
        return round((val - base) / abs(base) * 100, 1)

    rows = []
    for node in effective:
        partida_name = node['partida_name']
        is_header = node['is_header']
        parent = None
        bold = node['bold']
        bg_color = node['bg_color']
        es_nota = node['es_nota']
        parent_name = node['parent_name']
        indent = node['indent']

        if is_header:
            prev_val = valores_calculados_prev.get(partida_name, 0)
        else:
            prev_val = resolve_leaf_value_prev(partida_name, by_prev_raw)

        prev_pct_vtas = safe_pct(prev_val, divisor_prev(partida_name, by_prev_raw, ingresos_prev, ing_p))
        prev_pct_gastos = safe_pct(prev_val, gastos_prev)

        meses_data = []
        acum_ejec = 0
        acum_ppto = 0
        acum_ing_ejec = 0
        acum_ing_ppto = 0
        acum_gas_ejec = 0
        acum_gas_ppto = 0
        val_ejec_mes_anterior = None

        for m in MONTHS:
            month_type = MONTH_TYPES[m]

            if is_header:
                val_ejec = valores_calculados_por_mes[m].get(partida_name, 0)
                val_ppto = 0
            else:
                val_ejec = resolve_leaf_value(partida_name, m, by_partida)
                val_ppto = resolve_leaf_value(partida_name, m, by_budget)

            divisor_vtas_mes = divisor_ejec(partida_name, subtotales_por_mes[m], ingresos_ejec_mes[m], by_partida, m, ing_p)
            divisor_vtas_ppto = divisor_ppto_mes(partida_name, by_budget, m, ingresos_ppto_mes[m], ing_p)

            acum_ejec += val_ejec
            acum_ppto += val_ppto
            acum_ing_ejec += divisor_vtas_mes
            acum_ing_ppto += divisor_vtas_ppto
            acum_gas_ejec += gastos_ejec_mes[m]
            acum_gas_ppto += gastos_ppto_mes[m]

            pct_vtas_ejec = safe_pct(val_ejec, divisor_vtas_mes)
            pct_gastos_ejec = safe_pct(val_ejec, gastos_ejec_mes[m])

            mes_data = {
                'type': month_type,
                'month': m,
                'ejecutado': {
                    'valor': round(val_ejec, 2),
                    'pct_vtas': pct_vtas_ejec,
                    'pct_gastos': pct_gastos_ejec,
                }
            }

            if month_type != 'A':
                mes_data['vari_rel'] = safe_var(val_ejec, val_ejec_mes_anterior) if val_ejec_mes_anterior is not None else None

                if month_type == 'E':  # DIC: AÑO
                    mes_data['anio'] = {
                        'valor': round(acum_ejec, 2),
                        'pct_vtas': safe_pct(acum_ejec, acum_ing_ejec),
                        'pct_gastos': safe_pct(acum_ejec, acum_gas_ejec),
                    }
                else:
                    mes_data['acum_ejecutado'] = {
                        'valor': round(acum_ejec, 2),
                        'pct_vtas': safe_pct(acum_ejec, acum_ing_ejec),
                        'pct_gastos': safe_pct(acum_ejec, acum_gas_ejec),
                    }

                if month_type in ('C', 'D', 'E'):
                    mes_data['acum_ppto'] = {
                        'valor': round(acum_ppto, 2),
                        'pct_vtas': safe_pct(acum_ppto, acum_ing_ppto),
                    }
                    mes_data['var_ppto'] = safe_var(acum_ejec, acum_ppto)

                    if month_type == 'D':  # JUN
                        prom_ejec = acum_ejec / 6
                        prom_ppto = acum_ppto / 6
                        prom_ing_ejec = acum_ing_ejec / 6
                        prom_ing_ppto = acum_ing_ppto / 6
                        prom_gas_ejec = acum_gas_ejec / 6

                        mes_data['prom_6_ejec'] = {
                            'valor': round(prom_ejec, 2),
                            'pct_vtas': safe_pct(prom_ejec, prom_ing_ejec),
                            'pct_gastos': safe_pct(prom_ejec, prom_gas_ejec),
                        }
                        mes_data['prom_6_ppto'] = {
                            'valor': round(prom_ppto, 2),
                            'pct_vtas': safe_pct(prom_ppto, prom_ing_ppto),
                        }
                        mes_data['var_ppto_prom'] = safe_var(prom_ejec, prom_ppto)

            meses_data.append(mes_data)
            val_ejec_mes_anterior = val_ejec

        rows.append({
            'partida': partida_name,
            'is_header': is_header,
            'parent': parent,
            'bold': bold,
            'bg_color': bg_color,
            'es_nota': es_nota,
            'parent_name': parent_name,
            'indent': indent,
            'muestra_pct_gastos': muestra_pct_gastos_map.get(partida_name, False),
            'year_prev': {
                'valor': round(prev_val, 2),
                'pct_vtas': prev_pct_vtas,
                'pct_gastos': prev_pct_gastos,
            },
            'meses': meses_data,
        })

    return {
        'year': year,
        'year_prev': year_prev,
        'unit': unit,
        'rows': rows,
    }


def validate_esf_integrity(year, unit, esf_output, db, empresa_id=None):
    """
    Guarda de integridad para ESF.
    No replica el patrón de EERR 1:1 porque la identidad Activo=Pasivo+Patrimonio
    y el subtotal-vs-hojas se cumplen siempre por construcción algebraica en esf_engine
    (Resultados acumulados es un plug, headers se calculan sumando hijos directos).
    Valida lo que sí puede fallar: mapeo de cuentas y razonabilidad del plug.
    """
    logger = logging.getLogger('esf_integrity_guard')

    if not logger.handlers:
        logging.basicConfig(level=logging.INFO)
        try:
            fh = logging.FileHandler('integrity_guard_esf.log', encoding='utf-8')
            fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logger.addHandler(fh)
        except Exception:
            pass

    discrepancies = []

    # 1. Cuentas activas en financials_detail (report_type='esf') sin mapear en mapping_groups_v2
    try:
        missing_mappings = db.execute('''
            SELECT DISTINCT fd.odoo_code, fd.odoo_name
            FROM financials_detail fd
            LEFT JOIN mapping_groups_v2 mg
                ON fd.odoo_code = mg.odoo_code AND mg.report_type = 'esf'
            WHERE fd.report_type = 'esf' AND fd.year = ? AND mg.odoo_code IS NULL
              AND fd.amount_sign != 0
        ''', [year]).fetchall()
        for r in missing_mappings:
            msg = f"Cuenta ESF activa sin mapear en mapping_groups_v2: OdooCode='{r['odoo_code']}', Nombre='{r['odoo_name']}'"
            discrepancies.append(msg)
    except Exception as e:
        discrepancies.append(f"Error al validar cuentas ESF sin mapear: {str(e)}")

    # 2. Razonabilidad del plug "Resultados acumulados" (variación trimestre a trimestre)
    rows_map = {r['partida']: r for r in esf_output.get('rows', [])}
    res_acum = rows_map.get('Resultados acumulados')
    total_activos = rows_map.get('TOTAL ACTIVOS')

    if res_acum and total_activos:
        quarters_present = sorted(res_acum['quarters'].keys())
        for i in range(1, len(quarters_present)):
            q_prev = quarters_present[i - 1]
            q_curr = quarters_present[i]
            val_prev = res_acum['quarters'][q_prev]
            val_curr = res_acum['quarters'][q_curr]
            activos_curr = total_activos['quarters'].get(q_curr, 0.0)

            variacion = abs(val_curr - val_prev)
            if activos_curr:
                variacion_pct = variacion / abs(activos_curr)
                if variacion_pct > ESF_PLUG_VARIACION_UMBRAL:
                    msg = (f"Salto brusco en Resultados acumulados (plug) entre Q{q_prev} y Q{q_curr}: "
                           f"Q{q_prev}={val_prev:.2f}, Q{q_curr}={val_curr:.2f}, "
                           f"Variación={variacion:.2f} ({variacion_pct*100:.1f}% de Total Activos, "
                           f"umbral={ESF_PLUG_VARIACION_UMBRAL*100:.0f}%)")
                    discrepancies.append(msg)

            # Alerta separada: cambio de signo en el plug (independiente del %,
            # puede indicar patrimonio insuficiente frente a pérdidas acumuladas reales)
            if (val_prev > 0 and val_curr < 0) or (val_prev < 0 and val_curr > 0):
                msg_signo = (f"Cambio de signo en Resultados acumulados (plug) entre Q{q_prev} y Q{q_curr}: "
                             f"Q{q_prev}={val_prev:.2f} -> Q{q_curr}={val_curr:.2f}")
                discrepancies.append(msg_signo)

    if discrepancies:
        logger.warning(f"--- DETECTADAS DISCREPANCIAS DE INTEGRIDAD (ESF) - Unidad={unit}, Empresa={empresa_id}, Año={year} ---")
        for d in discrepancies:
            logger.warning(d)
    else:
        logger.info(f"Integridad ESF validada exitosamente para Unidad={unit}, Empresa={empresa_id}, Año={year}. Sin descuadres.")

    return discrepancies


def _reshape_esf_rows_to_quarters(res):
    """
    Transforma la salida de esf_engine (res['rows'] con 'partida'/'quarters') al
    formato result_quarters {totales, partidas} que consume compute_indicadores_v2.
    Pura transformación de datos -- sin validación de integridad (esa corre aparte,
    solo en el camino BCV, nunca sobre revalorizaciones Divisa Real). Extraída de
    compute_esf() para reutilizarse también en el camino Divisa Real.
    """
    result_quarters = {
        1: {'totales': {}, 'partidas': {}},
        2: {'totales': {}, 'partidas': {}},
        3: {'totales': {}, 'partidas': {}},
        4: {'totales': {}, 'partidas': {}}
    }
    for row in res.get('rows', []):
        partida = row.get('partida')
        quarters_val = row.get('quarters', {})
        for q in [1, 2, 3, 4]:
            val = quarters_val.get(q, 0.0)
            result_quarters[q]['totales'][partida] = val
            result_quarters[q]['partidas'][partida] = val
    for q in [1, 2, 3, 4]:
        tot = result_quarters[q]['totales']
        tot['Total Efectivo y Equivalentes']   = tot.get('Efectivo y Equivalentes', 0.0)
        tot['Total Cuentas por Cobrar (neto)'] = tot.get('Cuentas por Cobrar', 0.0)
        tot['Total Inventarios']               = tot.get('Inventarios', 0.0)
        tot['ACTIVOS CORRIENTES']              = tot.get('ACTIVOS CORRIENTES', 0.0)
        tot['Total Activos No Corrientes']     = tot.get('Total Activos No Corrientes', 0.0) or tot.get('ACTIVOS NO CORRIENTES', 0.0)
        tot['TOTAL ACTIVOS']                   = tot.get('TOTAL ACTIVOS', 0.0)
        tot['Total Cuentas por Pagar']         = tot.get('Cuentas por Pagar', 0.0)
        tot['TOTAL PASIVOS CORRIENTES']        = tot.get('TOTAL PASIVOS CORRIENTES', 0.0) or tot.get('Total Pasivos Corrientes', 0.0) or tot.get('PASIVOS CORRIENTES', 0.0)
        tot['TOTAL PASIVOS NO CORRIENTES']     = tot.get('TOTAL PASIVOS NO CORRIENTES', 0.0) or tot.get('Total Pasivos No Corrientes', 0.0) or tot.get('PASIVOS NO CORRIENTES', 0.0)
        tot['TOTAL PASIVOS']                   = tot.get('TOTAL PASIVOS', 0.0)
        tot['TOTAL PATRIMONIO']                = tot.get('TOTAL PATRIMONIO', 0.0) or tot.get('Total Patrimonio', 0.0) or tot.get('PATRIMONIO', 0.0)
        tot['TOTAL PASIVOS Y PATRIMONIO']      = tot.get('TOTAL PASIVOS Y PATRIMONIO', 0.0)
    return result_quarters


def compute_esf(db, year, unit='', empresa_id=None):
    """
    Calcula el Estado de Situación Financiera por quarter (consolidando unidades
    cuando unit está vacío). Devuelve (result_quarters, quarters_available).
    """
    if unit:
        uc = 'AND unit=?'
        params_q = [year, unit]
    elif empresa_id:
        uc = 'AND empresa_id=?'
        params_q = [year, empresa_id]
    else:
        uc = ''
        params_q = [year]
    rows_q = db.execute(f'SELECT DISTINCT quarter FROM esf_data WHERE year=? {uc}', params_q).fetchall()
    quarters_available = sorted([r['quarter'] for r in rows_q])

    res = esf_engine(year, unit, empresa_id=empresa_id)
    try:
        validate_esf_integrity(year, unit, res, db, empresa_id=empresa_id)
    except Exception as e:
        logging.getLogger('engine').error(f"Error al ejecutar validacion de integridad ESF: {str(e)}")
    
    result_quarters = _reshape_esf_rows_to_quarters(res)
    return result_quarters, quarters_available


def compute_indicadores_v2(db, year, empresa_id=None, datos_precalculados=None):
    """
    Calcula los 20 indicadores financieros por trimestre + año actual + año anterior.
    Estructura de salida compatible con el módulo Indicadores Financieros del frontend.

    datos_precalculados (opcional): dict con {'rows_curr', 'rows_prev', 'esf_rows',
    'result_quarters', 'esf_quarters_available'} ya resueltos externamente. Si se
    provee, la función NO llama a eerr_completo_v2_ui_adapter/esf_engine/compute_esf
    -- usa esos datos directos. Pensado para reutilizar las mismas 20 fórmulas con
    una fuente de datos distinta a BCV (ej. Divisa Real, vía calcular_estados_reales),
    sin duplicar lógica de cálculo -- ver ultrax_deuda_tecnica_refactor.md, regla
    "no parallel calculation engines".
    Si es None (default): comportamiento BCV actual, sin cambios.
    """
    import unicodedata

    def safe_div(a, b):
        if b is None or b == 0:
            return None
        return round(a / b, 4) if a is not None else None

    def vari_rel(prev, curr):
        if prev is None or curr is None:
            return None
        if prev == 0:
            return 1.0 if curr > 0 else None
        return round((curr - prev) / abs(prev), 4)

    QUARTER_MONTHS = {
        1: ['ENE','FEB','MAR'],
        2: ['ABR','MAY','JUN'],
        3: ['JUL','AGO','SEPT'],
        4: ['OCT','NOV','DIC']
    }

    # ── EERR: cargar financials por trimestre ─────────────────────────────────
    groups_v2, _ = get_grouped_partidas_v2(db, 'eerr')
    db_overrides = db.execute('SELECT partida_name, target_subtotal FROM eerr_nodes').fetchall()
    effective = build_effective_structure(EERR_STRUCTURE, db_overrides=db_overrides)

    def norm(s):
        if not s: return ''
        s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
        return s.lower().strip()

    NODOS = {
        'Total Ingresos': 'ingresos',
        'Total Costo de Ventas': 'costos',
        'Subtotal Costo de Ventas por Mercancia': 'costo_merc',
        'Utilidad Bruta': 'ut_bruta',
        'Total Gastos Operacionales': 'gas_op',
        'Utilidad Neta Operacional': 'ut_op',
        'Otros Ingresos no Operacionales': 'ot_ing',
        'Otros Gastos no Operacionales': 'ot_gas',
        'ISLR': 'islr',
        'Utilidad Neta despues de ISLR': 'ut_neta',
    }

    def _extract_eerr(rows, months):
        """Extrae subtotales EERR de rows ya cargados, filtrando por meses."""
        result = {v: 0.0 for v in NODOS.values()}
        for row in rows:
            partida = row.get('partida', '')
            if partida not in NODOS:
                continue
            key = NODOS[partida]
            for idx, mes_data in enumerate(row.get('meses', [])):
                if idx < len(MONTHS) and MONTHS[idx] in months:
                    result[key] += mes_data.get('ejecutado', {}).get('valor', 0) or 0
        # 'Total Ingresos' ya excluye los Ingresos No Operativos por diseño (regla
        # auditada, ver ultrax_funcionamiento.md, seccion "Formula de Total Ingresos
        # y Utilidad Bruta") -- no hace falta restarlos de nuevo aca. La resta previa
        # duplicaba la exclusion, causando que 'Ingresos Brutos' (pantalla
        # Indicadores Financieros) quedara $5,974.11 por debajo de totals.ingresos
        # del Dashboard, que sí usa el valor correcto directo de la partida.
        result['ut_bruta'] = result['ingresos'] - result['costos']
        result['ut_op']    = result['ut_bruta'] - result['gas_op']
        result['otros_nop'] = result['ot_ing'] - result['ot_gas']
        result['ut_ai']    = result['ut_op'] + result['otros_nop']
        result['ut_neta']  = result['ut_ai'] - result['islr']
        result['margen_bruto'] = safe_div(result['ut_bruta'], result['ingresos'])
        result['margen_neto']  = safe_div(result['ut_neta'], result['ingresos'])
        return result

    # ── Cache único EERR y ESF (o datos precalculados externos) ───────────────
    all_months = ['ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEPT','OCT','NOV','DIC']
    year_prev = str(int(year) - 1)

    if datos_precalculados is not None:
        _rows_curr = datos_precalculados['rows_curr']
        _rows_prev = datos_precalculados['rows_prev']
        _esf_rows = datos_precalculados['esf_rows']
        _result_quarters = datos_precalculados['result_quarters']
        _esf_quarters_available = datos_precalculados['esf_quarters_available']
    else:
        # EERR: una sola llamada por año
        _rows_curr = eerr_completo_v2_ui_adapter(db, year, '', empresa_id=empresa_id).get('rows', [])
        _rows_prev = eerr_completo_v2_ui_adapter(db, year_prev, '', empresa_id=empresa_id).get('rows', [])

        # ESF: una sola llamada para el año actual
        _esf_res = esf_engine(year, '', empresa_id=empresa_id)
        # Puede haber más de una fila con el mismo 'partida' (grupo nivel 3 +
        # detalle nivel 4 de una única cuenta hija) -- priorizar la fila de
        # grupo (nivel más bajo) para no perder la suma completa si el grupo
        # agrupa más de una cuenta Odoo bajo el mismo nombre de partida.
        _esf_rows = {}
        for n in _esf_res.get('rows', []):
            p = n['partida']
            if p not in _esf_rows or n.get('level', 99) < _esf_rows[p].get('_level', 99):
                qd = dict(n.get('quarters', {}))
                qd['_level'] = n.get('level', 99)
                _esf_rows[p] = qd
        _esf_rows = {p: {k: v for k, v in qd.items() if k != '_level'} for p, qd in _esf_rows.items()}
        _result_quarters, _esf_quarters_available = compute_esf(db, year, '', empresa_id=empresa_id)

    def get_esf_quarter(q):
        rows_esf = {p: qs.get(q, 0) or 0 for p, qs in _esf_rows.items()}
        tot = _result_quarters.get(q, {}).get('totales', {})
        return {
            'tot_activos':   tot.get('TOTAL ACTIVOS', 0),
            'act_corr':      tot.get('ACTIVOS CORRIENTES', 0),
            'pas_corr':      tot.get('TOTAL PASIVOS CORRIENTES', 0) or tot.get('PASIVOS CORRIENTES', 0),
            'tot_pas':       tot.get('TOTAL PASIVOS', 0),
            'patrimonio':    tot.get('TOTAL PATRIMONIO', 0) or tot.get('PATRIMONIO', 0),
            'efectivo':      tot.get('Total Efectivo y Equivalentes', 0),
            'inventarios':   tot.get('Total Inventarios', 0),
            'cxc':           tot.get('Total Cuentas por Cobrar (neto)', 0),
            'cxc_clientes':  rows_esf.get('Cuentas por cobrar clientes', 0),
            'cxc_grupo':     (rows_esf.get('A empresas relacionadas del grupo (CxC)', 0)
                               + rows_esf.get('A empresas externas del grupo (CxC)', 0)
                               + rows_esf.get('A socios (CxC)', 0)
                               + rows_esf.get('Cuentas por cobrar empleados', 0)),
            'res_ejercicio': rows_esf.get('Resultados del ejercicio', 0),
        }

    def qe(q, key):
        return quarters_data[q]['esf'].get(key, 0) or 0

    def periodo_cobro_q(q):
        """Período de cobro en días para el trimestre q: CxC clientes externos
        más CxC empresas del grupo/socios/empleados (cada una promediada con el
        trimestre anterior), sobre ingresos DEL TRIMESTRE puntual (no acumulados
        desde enero), por 90 días fijo -- réplica exacta de la metodología real
        de Yocelin (ver E123=(((E14+C14)/2)/(E108))*90 en su Excel BCV, donde
        E108 es el ingreso del trimestre puntual, no el acumulado)."""
        if q not in _esf_quarters_available:
            return None
        cxc_ext = prom_esf(q, 'cxc_clientes')
        cxc_grp = prom_esf(q, 'cxc_grupo')
        if cxc_ext is None or cxc_grp is None:
            return None
        ingresos_trimestre = quarters_data[q]['eerr'].get('ingresos', 0) or 0
        if not ingresos_trimestre:
            return None
        valor = round((cxc_ext + cxc_grp) / ingresos_trimestre * 90, 2)
        dias_cliente_externo = round(cxc_ext / ingresos_trimestre * 90, 2)
        dias_empresas_grupo = round(cxc_grp / ingresos_trimestre * 90, 2)
        return {
            'valor': valor,
            'dias_cliente_externo': dias_cliente_externo,
            'dias_empresas_grupo': dias_empresas_grupo,
        }

    def prom_esf(q, key):
        """Promedio del campo `key` del ESF entre el trimestre q y el anterior.
        Si no hay trimestre anterior con datos reales (ej. Q1), usa solo el valor de q."""
        if q not in _esf_quarters_available:
            return None
        curr = qe(q, key)
        prev_q = q - 1
        if prev_q >= 1 and prev_q in _esf_quarters_available:
            return (curr + qe(prev_q, key)) / 2
        return curr

    def inc_esf(q, key):
        """Valor incremental del trimestre q para un campo ESF acumulado (ej. Resultados
        del ejercicio) -- resta el valor del trimestre anterior si está disponible.
        Réplica de la metodología real de Yocelin (ver E119=E104-C104 en su Excel BCV)."""
        if q not in _esf_quarters_available:
            return None
        curr = qe(q, key)
        prev_q = q - 1
        if prev_q >= 1 and prev_q in _esf_quarters_available:
            return curr - qe(prev_q, key)
        return curr

    # ── Año anterior (acumulado anual) ────────────────────────────────────────
    prev_eerr = _extract_eerr(_rows_prev, all_months)
    prev_esf  = {
        'tot_activos':0,'act_corr':0,'pas_corr':0,'tot_pas':0,
        'patrimonio':0,'efectivo':0,'inventarios':0,'cxc':0,'res_ejercicio':0
    }
    # prev_esf es un stub sin calcular (ver ultrax_deuda_tecnica_refactor.md) --
    # no hay ESF real del año anterior cargado en el sistema. Los indicadores que
    # dependen de un promedio interanual real (ROE, ROA, Rotación de Inventarios,
    # Período de Cobro -- columna "Año Actual") deben devolver None en vez de una
    # aproximación intra-año-actual que aparenta ser un cálculo interanual válido.
    hay_esf_prev = False

    # ── Calcular por trimestre ────────────────────────────────────────────────
    quarters_data = {}
    acum_eerr = {k: 0 for k in ['ingresos','costos','costo_merc','ut_bruta','gas_op','ut_op','otros_nop','ut_ai','islr','ut_neta']}
    for q in [1, 2, 3, 4]:
        months = QUARTER_MONTHS[q]
        eerr_q = _extract_eerr(_rows_curr, months)
        esf_q  = get_esf_quarter(q)
        for k in acum_eerr:
            acum_eerr[k] += eerr_q.get(k, 0) or 0
        quarters_data[q] = {'eerr': eerr_q, 'esf': esf_q}

    # Ingresos acumulados desde el inicio del año hasta cada trimestre (para
    # Período de Cobro -- metodología Yocelin: el denominador es el ingreso
    # acumulado a la fecha, no el del trimestre aislado).
    ing_cum_q = {}
    _running = 0.0
    for _q in [1, 2, 3, 4]:
        _running += quarters_data[_q]['eerr'].get('ingresos', 0) or 0
        ing_cum_q[_q] = _running

    # Año actual acumulado
    ing_aa  = acum_eerr['ingresos']
    cos_aa  = acum_eerr['costos']
    esf_last = quarters_data[max(q for q in [1,2,3,4] if quarters_data[q]['esf']['tot_activos'] != 0) if any(quarters_data[q]['esf']['tot_activos'] for q in [1,2,3,4]) else 4]['esf']

    def build_ind(nombre, referencia, val_prev, vals_q, val_aa, es_pct=False, es_ratio=False):
        resultado = {'nombre': nombre, 'referencia': referencia, 'es_pct': es_pct, 'es_ratio': es_ratio}
        resultado['year_prev'] = val_prev
        resultado['anio_actual'] = val_aa
        trimestres = []
        vp = val_prev
        for q in [1,2,3,4]:
            v = vals_q[q]
            trimestres.append({'q': q, 'valor': v, 'vari_rel': vari_rel(vp, v)})
            if v is not None:
                vp = v
        resultado['trimestres'] = trimestres
        resultado['vari_rel_aa'] = vari_rel(val_prev, val_aa)
        return resultado

    def qv(q, key):
        return quarters_data[q]['eerr'].get(key)

    pc_data_q = {q: periodo_cobro_q(q) for q in [1, 2, 3, 4]}
    pc_data_aa = periodo_cobro_q(max(_esf_quarters_available) if _esf_quarters_available else 4)
    ind_pc = build_ind(
        'Período de cobro (30 a 60 días max)', '30-60 días',
        None,
        {q: (pc_data_q[q]['valor'] if pc_data_q[q] else None) for q in [1, 2, 3, 4]},
        (pc_data_aa['valor'] if pc_data_aa else None) if hay_esf_prev else None,
        es_ratio=True
    )
    for t in ind_pc['trimestres']:
        q = t['q']
        d = pc_data_q[q]
        t['dias_cliente_externo'] = d['dias_cliente_externo'] if d else None
        t['dias_empresas_grupo'] = d['dias_empresas_grupo'] if d else None

    indicadores = [
        build_ind('Ingresos Brutos', None,
            prev_eerr['ingresos'],
            {q: qv(q,'ingresos') for q in [1,2,3,4]},
            ing_aa),
        build_ind('Costo de ventas', None,
            prev_eerr['costos'],
            {q: qv(q,'costos') for q in [1,2,3,4]},
            cos_aa),
        build_ind('Utilidad Bruta', None,
            prev_eerr['ut_bruta'],
            {q: qv(q,'ut_bruta') for q in [1,2,3,4]},
            acum_eerr['ut_bruta']),
        build_ind('Margen Bruto (30% a 50%)', '30%-50%',
            prev_eerr['margen_bruto'],
            {q: qv(q,'margen_bruto') for q in [1,2,3,4]},
            safe_div(acum_eerr['ut_bruta'], ing_aa), es_pct=True),
        build_ind('Gastos Operacionales', None,
            prev_eerr['gas_op'],
            {q: qv(q,'gas_op') for q in [1,2,3,4]},
            acum_eerr['gas_op']),
        build_ind('Utilidad Neta operacional', None,
            prev_eerr['ut_op'],
            {q: qv(q,'ut_op') for q in [1,2,3,4]},
            acum_eerr['ut_op']),
        build_ind('Otros Ingresos y gastos no operacionales', None,
            prev_eerr['otros_nop'],
            {q: qv(q,'otros_nop') for q in [1,2,3,4]},
            acum_eerr['otros_nop']),
        build_ind('Utilidad Neta antes de ISLR', None,
            prev_eerr['ut_ai'],
            {q: qv(q,'ut_ai') for q in [1,2,3,4]},
            acum_eerr['ut_ai']),
        build_ind('ISLR', None,
            prev_eerr['islr'],
            {q: qv(q,'islr') for q in [1,2,3,4]},
            acum_eerr['islr']),
        build_ind('Utilidad Neta despues de ISLR', None,
            prev_eerr['ut_neta'],
            {q: qv(q,'ut_neta') for q in [1,2,3,4]},
            acum_eerr['ut_neta']),
        build_ind('Margen Neto (5% y 15%)', '5%-15%',
            prev_eerr['margen_neto'],
            {q: qv(q,'margen_neto') for q in [1,2,3,4]},
            safe_div(acum_eerr['ut_neta'], ing_aa), es_pct=True),
        build_ind('ROE (10% y 20%)', '10%-20%',
            None,
            {q: safe_div(inc_esf(q,'res_ejercicio'), prom_esf(q,'patrimonio')) for q in [1,2,3,4]},
            safe_div(esf_last['res_ejercicio'], prom_esf(max(_esf_quarters_available) if _esf_quarters_available else 4, 'patrimonio')) if hay_esf_prev else None, es_pct=True),
        build_ind('Rotación de Inventarios (2 y 3 meses)', '2-3 meses',
            None,
            {q: safe_div(prom_esf(q,'inventarios')*3, qv(q,'costo_merc')) if prom_esf(q,'inventarios') is not None else None for q in [1,2,3,4]},
            safe_div(esf_last['inventarios']*12, acum_eerr.get('costo_merc', 0)) if hay_esf_prev else None, es_ratio=True),
        build_ind('ROA (5% a 15%)', '5%-15%',
            None,
            {q: safe_div(inc_esf(q,'res_ejercicio'), prom_esf(q,'tot_activos')) for q in [1,2,3,4]},
            safe_div(esf_last['res_ejercicio'], prom_esf(max(_esf_quarters_available) if _esf_quarters_available else 4, 'tot_activos')) if hay_esf_prev else None, es_pct=True),
        ind_pc,
        build_ind('Ratio Corriente (entre 1,5 y 2)', '1.5-2',
            None,
            {q: safe_div(qe(q,'act_corr'), qe(q,'pas_corr')) for q in [1,2,3,4]},
            safe_div(esf_last['act_corr'], esf_last['pas_corr']), es_ratio=True),
        build_ind('Ratio Endeudamiento (entre 0,4 y 0,6)', '0.4-0.6',
            None,
            {q: safe_div(qe(q,'tot_pas'), qe(q,'patrimonio')) for q in [1,2,3,4]},
            safe_div(esf_last['tot_pas'], esf_last['patrimonio']), es_ratio=True),
        build_ind('Prueba Ácida (entre 0,8 y 1)', '0.8-1',
            None,
            {q: safe_div(qe(q,'act_corr')-qe(q,'inventarios'), qe(q,'pas_corr')) for q in [1,2,3,4]},
            safe_div(esf_last['act_corr']-esf_last['inventarios'], esf_last['pas_corr']), es_ratio=True),
        build_ind('Prueba Defensiva (entre 0,5 Y 0,7)', '0.5-0.7',
            None,
            {q: safe_div(qe(q,'efectivo'), qe(q,'pas_corr')) for q in [1,2,3,4]},
            safe_div(esf_last['efectivo'], esf_last['pas_corr']), es_ratio=True),
    ]
    return indicadores


def _neutralizar_plug_sin_datos(rows, esf_quarters_available):
    """
    Bug preexistente en esf_engine/calcular_estados_reales (detectado ago-2026):
    para un trimestre sin filas reales en esf_data, esf_engine calcula
    TOTAL ACTIVOS=0 y TOTAL PASIVOS=0 para ese trimestre, lo que produce un
    'Resultados acumulados' artificial (= -Utilidad Neta arrastrada) y de ahí un
    plug_divisa_q espurio que se inyecta en el mes de cierre como Ganancia/Pérdida
    en tasa cambiaria -- un valor fantasma, no un dato real.

    No se corrige en esf_engine/calcular_estados_reales (motor compartido, usado
    hoy por Dashboard/ESF/EERR Divisa Real en producción) para no arriesgar
    comportamiento ya validado -- ver ultrax_deuda_tecnica_refactor.md. Esta
    función neutraliza el efecto solo en los datos ya devueltos, únicamente para
    trimestres fuera de esf_quarters_available (sin datos reales de balance),
    antes de que compute_indicadores_v2 los consuma.

    Pone en 0 el mes de cierre de Ganancia/Pérdida en tasa cambiaria para esos
    trimestres, y resta el mismo monto del subtotal correspondiente
    (Otros Ingresos/Gastos no Operacionales) para no romper la cascada de
    subtotales. Muta `rows` in-place (estructura fresca por request, sin
    persistencia).
    """
    quarter_close_month = {1: 'MAR', 2: 'JUN', 3: 'SEPT', 4: 'DIC'}
    missing_quarters = [q for q in [1, 2, 3, 4] if q not in esf_quarters_available]
    if not missing_quarters:
        return rows

    missing_months = {quarter_close_month[q] for q in missing_quarters}
    plug_partidas = {
        'Ganancia por tasa cambiaria': 'Otros Ingresos no Operacionales',
        'Pérdida en tasa cambiaria': 'Otros Gastos no Operacionales',
    }

    ajustes = {}
    for row in rows:
        partida = row.get('partida')
        if partida not in plug_partidas:
            continue
        subtotal_partida = plug_partidas[partida]
        for m in row.get('meses', []):
            month = m.get('month')
            if month not in missing_months:
                continue
            valor = m.get('ejecutado', {}).get('valor', 0) or 0
            if valor:
                key = (subtotal_partida, month)
                ajustes[key] = ajustes.get(key, 0) + valor
                m['ejecutado']['valor'] = 0

    if ajustes:
        for row in rows:
            partida = row.get('partida')
            for m in row.get('meses', []):
                month = m.get('month')
                key = (partida, month)
                if key in ajustes:
                    m['ejecutado']['valor'] = (m['ejecutado'].get('valor', 0) or 0) - ajustes[key]

    return rows


def compute_indicadores_v2_divisa_real(db, year, empresa_id=None):
    """
    Punto de entrada de Indicadores Financieros en modo Divisa Real. Arma
    datos_precalculados a partir de calcular_estados_reales() (año actual y año
    anterior) y delega el cálculo de las 20 fórmulas a compute_indicadores_v2 --
    misma lógica que BCV, distinta fuente de datos. No duplica ninguna fórmula
    (ver ultrax_deuda_tecnica_refactor.md, regla "no parallel calculation engines").
    """
    year_prev = str(int(year) - 1)

    estados_curr = calcular_estados_reales(year, '', empresa_id=empresa_id, db=db)
    if 'error' in estados_curr:
        return estados_curr
    estados_prev = calcular_estados_reales(year_prev, '', empresa_id=empresa_id, db=db)
    if 'error' in estados_prev:
        rows_prev = []
    else:
        rows_prev = estados_prev.get('eerr_real', {}).get('rows', [])

    rows_curr = estados_curr.get('eerr_real', {}).get('rows', [])
    esf_real = estados_curr.get('esf_real', {})
    esf_rows = {n['partida']: n.get('quarters', {}) for n in esf_real.get('rows', [])}
    result_quarters = _reshape_esf_rows_to_quarters(esf_real)

    if empresa_id:
        uc = 'AND empresa_id=?'
        params_q = [year, empresa_id]
    else:
        uc = ''
        params_q = [year]
    rows_q = db.execute(f'SELECT DISTINCT quarter FROM esf_data WHERE year=? {uc}', params_q).fetchall()
    esf_quarters_available = sorted([r['quarter'] for r in rows_q])
    rows_q_prev = db.execute(f'SELECT DISTINCT quarter FROM esf_data WHERE year=? {uc.replace("year", "year")}', [year_prev] + (params_q[1:] if empresa_id else [])).fetchall()
    esf_quarters_available_prev = sorted([r['quarter'] for r in rows_q_prev])

    rows_curr = _neutralizar_plug_sin_datos(rows_curr, esf_quarters_available)
    rows_prev = _neutralizar_plug_sin_datos(rows_prev, esf_quarters_available_prev)

    datos_precalculados = {
        'rows_curr': rows_curr,
        'rows_prev': rows_prev,
        'esf_rows': esf_rows,
        'result_quarters': result_quarters,
        'esf_quarters_available': esf_quarters_available,
    }
    indicadores = compute_indicadores_v2(db, year, empresa_id=empresa_id, datos_precalculados=datos_precalculados)
    if isinstance(indicadores, dict) and 'error' in indicadores:
        return indicadores

    esf_totales = None
    if esf_quarters_available:
        esf_last_q = max(esf_quarters_available)
        esf_tot = result_quarters.get(esf_last_q, {}).get('totales', {})
        esf_totales = {
            'total_activos': round(esf_tot.get('TOTAL ACTIVOS', 0), 2),
            'total_pasivos': round(esf_tot.get('TOTAL PASIVOS', 0), 2),
            'patrimonio': round(esf_tot.get('TOTAL PATRIMONIO', 0), 2),
        }

    return {'indicadores': indicadores, 'esf_totales': esf_totales}


def eerr_divisa_real_trimestres(db, year, unit='', empresa_id=None):
    """
    EERR Divisa Real agrupado por trimestre para consumo del Dashboard (a futuro).
    Cada trimestre suma SOLO sus 3 meses propios (ENE-FEB-MAR para Q1, etc.) --
    NO acumulado desde enero. Mismo criterio ya usado en compute_indicadores_v2
    (_extract_eerr con QUARTER_MONTHS) y confirmado con Yocelin: los trimestres no
    se suman entre sí en ningún estado financiero de este sistema. Reutiliza
    calcular_estados_reales() -- no duplica lógica de cálculo.

    Aplica la misma neutralización de plug fantasma que
    compute_indicadores_v2_divisa_real, para trimestres sin datos reales de ESF
    (ver _neutralizar_plug_sin_datos, ultrax_deuda_tecnica_refactor.md).

    Retorna: {'year', 'unit', 'quarters': {1: {partida: valor, ...}, 2: {...}, 3: {...}, 4: {...}}}
    """
    QUARTER_MONTHS = {
        1: ['ENE', 'FEB', 'MAR'],
        2: ['ABR', 'MAY', 'JUN'],
        3: ['JUL', 'AGO', 'SEPT'],
        4: ['OCT', 'NOV', 'DIC']
    }

    estados = calcular_estados_reales(year, unit, empresa_id=empresa_id, db=db)
    if 'error' in estados:
        return estados

    rows = estados.get('eerr_real', {}).get('rows', [])

    if empresa_id:
        uc = 'AND empresa_id=?'
        params_q = [year, empresa_id]
    else:
        uc = ''
        params_q = [year]
    rows_q = db.execute(f'SELECT DISTINCT quarter FROM esf_data WHERE year=? {uc}', params_q).fetchall()
    esf_quarters_available = sorted([r['quarter'] for r in rows_q])

    # Capturar el plug fantasma ANTES de neutralizarlo, para propagarlo también a
    # Utilidad Neta / Utilidad Neta despues de ISLR -- filas ya calculadas por el
    # motor, no derivadas de Otros Ingresos/Gastos dentro de esta función, así que
    # _neutralizar_plug_sin_datos no las corrige por sí sola. Fix local, contenido
    # aquí -- no se toca _neutralizar_plug_sin_datos para no afectar
    # compute_indicadores_v2_divisa_real, que ya funciona correctamente por otro
    # camino (recalcula Utilidad Neta desde cero, no lee la fila directo).
    quarter_close_month = {1: 'MAR', 2: 'JUN', 3: 'SEPT', 4: 'DIC'}
    missing_quarters_local = [q for q in [1, 2, 3, 4] if q not in esf_quarters_available]
    missing_months_local = {quarter_close_month[q] for q in missing_quarters_local}
    plug_fantasma_por_mes = {}
    if missing_months_local:
        for row in rows:
            if row.get('partida') not in ('Ganancia por tasa cambiaria', 'Pérdida en tasa cambiaria'):
                continue
            for m in row.get('meses', []):
                month = m.get('month')
                if month not in missing_months_local:
                    continue
                valor = m.get('ejecutado', {}).get('valor', 0) or 0
                if valor:
                    signo = 1 if row.get('partida') == 'Ganancia por tasa cambiaria' else -1
                    plug_fantasma_por_mes[month] = plug_fantasma_por_mes.get(month, 0) + (signo * valor)

    rows = _neutralizar_plug_sin_datos(rows, esf_quarters_available)

    if plug_fantasma_por_mes:
        for row in rows:
            if row.get('partida') not in ('Utilidad Neta', 'Utilidad Neta despues de ISLR'):
                continue
            for m in row.get('meses', []):
                month = m.get('month')
                if month in plug_fantasma_por_mes:
                    m['ejecutado']['valor'] = (m['ejecutado'].get('valor', 0) or 0) - plug_fantasma_por_mes[month]

    quarters = {q: {} for q in [1, 2, 3, 4]}
    for row in rows:
        partida = row.get('partida', '')
        if not partida:
            continue
        for q, months in QUARTER_MONTHS.items():
            total = 0.0
            for mes_data in row.get('meses', []):
                if mes_data.get('month') in months:
                    total += mes_data.get('ejecutado', {}).get('valor', 0) or 0
            quarters[q][partida] = round(total, 2)

    return {'year': year, 'unit': unit, 'quarters': quarters}

