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
# Formato: (partida_name, is_header, parent, bold, bg_color)
# Colores: FF6AD9E8 (azul claro), FF66FF66 (verde), FFFFFF00 (amarillo)

EERR_STRUCTURE = [
    ('ESTADO DE RESULTADOS', True, None, True, None, 0),
    ('PARTIDAS', True, None, True, None, 0),
    ('Total Ingresos', True, None, True, 'FF6AD9E8', 0),
    ('Subtotal Ingresos por Venta de Mercancia', True, None, True, None, 1),
    ('Ingresos por venta de mercancias', False, None, False, None, 3),
    ('Devoluciones sobre ventas', False, None, False, None, 3),
    ('Descuentos sobre ventas', False, None, False, None, 3),
    ('Subtotal Ingresos por Servicios', True, None, True, None, 1),
    ('Ingresos por servicios del café', False, None, False, None, 3),
    ('Ingresos por zona FIT', False, None, False, None, 3),
    ('Ingresos por fletes', False, None, False, None, 3),
    ('Subtotal Ingresos por Eventos', True, None, True, None, 1),
    ('Ingresos por eventos', False, None, False, None, 3),
    ('Subtotal Ingresos por Taller', True, None, True, None, 1),
    ('Ingresos por taller', False, None, False, None, 3),
    ('Total Costo de Ventas', True, None, True, None, 0),
    ('Subtotal Costo de Ventas por Mercancia', True, None, True, None, 1),
    ('Costos de venta por mercancia', False, None, False, None, 3),
    ('Subtotal Costo de Ventas por Servicios', True, None, True, None, 1),
    ('Costo de venta por servicio del café', False, None, False, None, 3),
    ('Subtotal Costo de Ventas por Eventos', True, None, True, None, 1),
    ('Costo de ventas por eventos', False, None, False, None, 3),
    ('Utilidad Bruta por Venta de Mercancia y Taller', True, None, True, 'FF66FF66', 0),
    ('Utilidad Bruta por Servicios', True, None, True, 'FF66FF66', 0),
    ('Utilidad Bruta por Eventos', True, None, True, 'FF66FF66', 0),
    ('Utilidad Bruta', True, None, True, 'FF66FF66', 0),
    ('Total Gastos Operacionales', True, None, True, None, 0),
    ('Subtotal Gastos de Administración', True, None, True, None, 1),
    ('Gastos de servicios públicos (Agua, luz, Aseo Urbano)', False, None, False, None, 3),
    ('Gastos de servicios de telefonía e internet', False, None, False, None, 3),
    ('Gastos de alquiler del local', False, None, False, None, 3),
    ('Gastos de Condominio', False, None, False, None, 3),
    ('Gastos de asistencia outsorcing', False, None, False, None, 3),
    ('Gastos de alquiler de bienes muebles', False, None, False, None, 3),
    ('Gastos de artículos de oficina', False, None, False, None, 3),
    ('Gastos de artículos de limpieza e higiene', False, None, False, None, 3),
    ('Gastos de alimentos y bebidas', False, None, False, None, 3),
    ('Gastos de envíos y encomiendas administrativas', False, None, False, None, 3),
    ('Gastos de honorarios profesionales', False, None, False, None, 3),
    ('Gastos de estacionamiento', False, None, False, None, 3),
    ('Gastos de gestoría', False, None, False, None, 3),
    ('Gastos legales', False, None, False, None, 3),
    ('Gastos de taxi, transporte y/o delivery', False, None, False, None, 3),
    ('Gastos de suministros para taller', False, None, False, None, 3),
    ('Gastos de suministros del café', False, None, False, None, 3),
    ('Gastos por fiestas, festejos y/o reuniones', False, None, False, None, 3),
    ('Gastos de vigilancia', False, None, False, None, 3),
    ('Gastos de retenciones no descontadas', False, None, False, None, 3),
    ('Mantenimiento y reparaciones', False, None, False, None, 3),
    ('Viáticos administrativos', False, None, False, None, 3),
    ('Gastos de seguro', False, None, False, None, 3),
    ('Gastos de impuestos, tasas y contribuciones', False, None, False, None, 3),
    ('Depreciaciones, deterioro y Amortización', False, None, False, None, 3),
    ('Gasto por impuesto a las pensiones', False, None, False, None, 3),
    ('Gastos de IGTF', False, None, False, None, 3),
    ('Gastos de comisiones bancarias', False, None, False, None, 3),
    ('Gastos Bancarios', False, None, False, None, 3),
    ('Gastos de intereses sobre préstamos', False, None, False, None, 3),
    ('Subtotal Gastos de Recursos Humanos', True, None, True, None, 1),
    ('Gastos de sueldos y salarios empleados y directivos', True, None, False, None, 2),
    ('Gastos de sueldos y salarios empleados', False, None, False, None, 3),
    ('Gastos de sueldos y salarios directivos', False, None, False, None, 3),
    ('Gastos de horas extras, feriados y bono nocturno', False, None, False, None, 3),
    ('Gastos de Bono de alimentación empleados', False, None, False, None, 3),
    ('Gastos de Bono de alimentación directivos', False, None, False, None, 3),
    ('Gastos de complementos empleados y directivos', True, None, False, None, 2),
    ('Gastos de complemento de sueldos y salarios empleados', False, None, False, None, 3),
    ('Gastos de complemento de sueldos y salarios directivos', False, None, False, None, 3),
    ('Gastos de personal externo', True, None, False, None, 2),
    ('Gastos de servicios de personal externo', False, None, False, None, 3),
    ('Gastos de pasivos laborales vacaciones', True, None, False, None, 2),
    ('Gastos de vacaciones empleados', False, None, False, None, 3),
    ('Gastos de vacaciones directivos', False, None, False, None, 3),
    ('Gastos de complemento de vacaciones empleados', False, None, False, None, 3),
    ('Gastos de complemento de vacaciones directivos', False, None, False, None, 3),
    ('Gastos de pasivos laborales utilidades', True, None, False, None, 2),
    ('Gastos de bono vacacional empleados', False, None, False, None, 3),
    ('Gastos de bono vacacional directivos', False, None, False, None, 3),
    ('Gastos de complemento bono vacacional empleados', False, None, False, None, 3),
    ('Gastos de complemento bono vacacional directivos', False, None, False, None, 3),
    ('Gastos de utilidades empleados', False, None, False, None, 3),
    ('Gastos de utilidades directivos', False, None, False, None, 3),
    ('Gastos de complemento de utilidades empleados', False, None, False, None, 3),
    ('Gastos de complemento de utilidades directivos', False, None, False, None, 3),
    ('Gastos de pasivos laborales prestaciones e intereses', True, None, False, None, 2),
    ('Gastos de prestaciones sociales empleados', False, None, False, None, 3),
    ('Gastos de prestaciones sociales directivos', False, None, False, None, 3),
    ('Gastos de complemento de prestaciones sociales empleados', False, None, False, None, 3),
    ('Gastos de complemento de prestaciones sociales directivos', False, None, False, None, 3),
    ('Gastos de intereses sobres prestaciones sociales empleados', False, None, False, None, 3),
    ('Gastos de intereses sobres prestaciones sociales directivos', False, None, False, None, 3),
    ('Gastos de complemento de intereses sobre prestaciones sociales empleados', False, None, False, None, 3),
    ('Gastos de complemento de intereses sobre prestaciones sociales directivos', False, None, False, None, 3),
    ('Gastos de pasivos laborales aportes', True, None, False, None, 2),
    ('Gastos de aporte patronal IVSS', False, None, False, None, 3),
    ('Gastos de aporte patronal SPF', False, None, False, None, 3),
    ('Gastos de aporte patronal FAOV', False, None, False, None, 3),
    ('Gastos de aporte patronal INCES', False, None, False, None, 3),
    ('Gastos de bono de guardería', False, None, False, None, 3),
    ('Gastos de pasivos laborales HCM', True, None, False, None, 2),
    ('Gastos de póliza HCM', False, None, False, None, 3),
    ('Gastos de salud y seguridad laboral', False, None, False, None, 3),
    ('Gastos de salud y seguridad laboral dotación', False, None, False, None, 3),
    ('Gastos de uniformes y dotación al personal', False, None, False, None, 3),
    ('Gastos de salud y seguridad laboral fiestas y agasajos', True, None, False, None, 2),
    ('Gastos de fiestas y agasajos al personal', False, None, False, None, 3),
    ('Otros gastos de personal', True, None, False, None, 2),
    ('Gastos de otros bonos empleados', False, None, False, None, 3),
    ('Gastos de transporte del personal', False, None, False, None, 3),
    ('Gastos de donaciones y obsequios al personal', False, None, False, None, 3),
    ('Gastos de capacitación al personal', False, None, False, None, 3),
    ('Subtotal Gastos de Comercialización y Logistica', True, None, True, None, 1),
    ('Gastos de viáticos comerciales', False, None, False, None, 3),
    ('Gastos de comisiones empleados', False, None, False, None, 3),
    ('Gastos de comisiones empleados del taller', False, None, False, None, 3),
    ('Gastos de comisiones por venta de personal externo', False, None, False, None, 3),
    ('Gastos de fletes y envios no asociados al costo', False, None, False, None, 3),
    ('Otros gastos no asociados al costo', False, None, False, None, 3),
    ('Gastos por combustible', False, None, False, None, 3),
    ('Gastos de representación', False, None, False, None, 3),
    ('Gastos por garantia', False, None, False, None, 3),
    ('Gastos por suscripciones', False, None, False, None, 3),
    ('Gastos de Stand y/o ferias comerciales', False, None, False, None, 3),
    ('Subtotal Gastos de Mercadeo', True, None, True, None, 1),
    ('Gastos de redes sociales', False, None, False, None, 3),
    ('Gastos de medios publicitarios', False, None, False, None, 3),
    ('Gastos de impresiones de material gráfico', False, None, False, None, 3),
    ('Otros gastos de publicidad y promoción', False, None, False, None, 3),
    ('Gastos de patrocinio y donación', False, None, False, None, 3),
    ('Gastos de patrocinio, donación y/o obsequios en efectivo', False, None, False, None, 3),
    ('Gastos de patrocinio, donación y/o obsequios en productos', False, None, False, None, 3),
    ('Gastos de viáticos por eventos', False, None, False, None, 3),
    ('Gastos de materiales y servicios por eventos', False, None, False, None, 3),
    ('Gastos de alimentos y bebidas por eventos', False, None, False, None, 3),
    ('Gastos de personal por eventos', False, None, False, None, 3),
    ('Gastos de patrocinio, donación y/o obseq por eventos', False, None, False, None, 3),
    ('Subtotal Gastos de TI+I', True, None, True, None, 1),
    ('Gastos de página web', False, None, False, None, 3),
    ('Gastos de desarrollo', False, None, False, None, 3),
    ('Utilidad antes de Comisiones por Ventas', True, None, True, 'FF66FF66', 0),
    ('Gastos de comisiones por ventas', False, None, False, None, 3),
    ('Gastos de comisiones por ventas taller', False, None, False, None, 3),
    ('Utilidad después de Comisiones por Ventas', True, None, True, 'FF66FF66', 0),
    ('Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA)', True, None, True, 'FF66FF66', 0),
    ('Utilidad antes de Intereses e Impuestos (EBIT)', True, None, True, 'FF66FF66', 0),
    ('Otros Gastos no Operacionales', True, None, True, None, 0),
    ('Faltante en Ventas', False, None, False, None, 3),
    ('Pérdida en venta de activos', False, None, False, None, 3),
    ('Pérdida en siniestro de activos', False, None, False, None, 3),
    ('Pérdida en tasa cambiaria', False, None, False, None, 3),
    ('Pérdida por diferencia en pagos', False, None, False, None, 3),
    ('Multas', False, None, False, None, 3),
    ('Faltante y deterioro de inventarios', False, None, False, None, 3),
    ('Total Gastos Operacionales y No Operacionales', True, None, True, 'FFFFFF00', 0),
    ('Otros Ingresos no Operacionales', True, None, True, None, 0),
    ('Ingresos por alquileres', False, None, False, None, 3),
    ('Ingresos por intereses', False, None, False, None, 3),
    ('Ingresos por comisiones', False, None, False, None, 3),
    ('Ingresos por servicios administrativos', False, None, False, None, 3),
    ('Sobrante en ventas', False, None, False, None, 3),
    ('Sobrante de inventarios', False, None, False, None, 3),
    ('Ganancia en venta de activos', False, None, False, None, 3),
    ('Ganancia por tasa cambiaria', False, None, False, None, 3),
    ('Ganancia por diferencias en pagos', False, None, False, None, 3),
    ('Utilidad Neta', True, None, True, 'FF66FF66', 0),
    ('ISLR', True, None, True, None, 0),
    ('Utilidad Neta despues de ISLR', True, None, True, 'FF66FF66', 0),
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
    def __init__(self, data, year, units, months):
        self.data = data  # list of dicts: year, month, unit, partida, amount
        self.year = year
        self.units = units
        self.months = months

    def _build_lookup(self):
        lookup = {}
        for row in self.data:
            key = (row['unit'], row['month'], row['partida'])
            lookup[key] = row['amount']
        return lookup

    def generate(self):
        wb = openpyxl.Workbook()
        lookup = self._build_lookup()

        HDR_FILL  = PatternFill('solid', start_color='1F3864')
        SUB_FILL  = PatternFill('solid', start_color='2E75B6')
        SEC_FILL  = PatternFill('solid', start_color='BDD7EE')
        WHITE_FILL= PatternFill('solid', start_color='FFFFFF')
        ACUM_FILL = PatternFill('solid', start_color='EBF3FB')
        VAR_FILL  = PatternFill('solid', start_color='FFF2CC')
        WHITE_FONT= Font(name='Arial', bold=True, color='FFFFFF', size=10)
        DARK_FONT = Font(name='Arial', bold=True, color='1F3864', size=10)
        NORM_FONT = Font(name='Arial', size=9)
        NUM_FMT   = '#,##0.00;(#,##0.00);"-"'
        PCT_FMT   = '0.0%;(0.0%);"-"'

        thin   = Side(style='thin', color='BDD7EE')
        border = Border(left=thin, right=thin, top=thin, bottom=thin)

        sheets_to_build = self.units + ['CONSOLIDADO']
        wb.remove(wb.active)

        # Número de columnas de meses + ANUAL + ACUM EJEC + %VAR + %VTAS + %GASTOS
        # Layout: A=Partida, B=ANUAL, C..N=meses, O=ACUM EJEC, P=%VAR, Q=%VTAS, R=%GASTOS
        N_MONTHS = len(self.months)
        COL_ANUAL    = 2
        COL_M_START  = 3
        COL_M_END    = COL_M_START + N_MONTHS - 1
        COL_ACUM     = COL_M_END + 1
        COL_VAR      = COL_M_END + 2
        COL_PVTAS    = COL_M_END + 3
        COL_PGASTOS  = COL_M_END + 4

        for unit in sheets_to_build:
            ws = wb.create_sheet(unit)
            ws.sheet_view.showGridLines = False

            # Fila 1: Título
            last_col = get_column_letter(COL_PGASTOS)
            ws.merge_cells(f'A1:{last_col}1')
            title = ws['A1']
            title.value = f'ESTADO DE RESULTADOS — {unit.upper()} — {self.year}'
            title.font  = Font(name='Arial', bold=True, color='FFFFFF', size=12)
            title.fill  = HDR_FILL
            title.alignment = Alignment(horizontal='center', vertical='center')
            ws.row_dimensions[1].height = 24

            # Fila 2: Encabezados
            ws.row_dimensions[2].height = 20
            headers = ['PARTIDAS', 'ANUAL'] + self.months + ['ACUM EJEC', '%VAR', '%VTAS', '%GASTOS']
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
            ws.column_dimensions[get_column_letter(COL_ACUM)].width   = 14
            ws.column_dimensions[get_column_letter(COL_VAR)].width    = 9
            ws.column_dimensions[get_column_letter(COL_PVTAS)].width  = 9
            ws.column_dimensions[get_column_letter(COL_PGASTOS)].width= 9

            row_num     = 3
            partida_rows= {}

            for item in EERR_STRUCTURE:
                partida = item[0]
                is_header = item[1]
                ws.row_dimensions[row_num].height = 16

                if partida in ('Total Ingresos', 'Total Costo de Ventas', 'Utilidad Bruta',
                               'Total Gastos', 'Utilidad Neta', 'Utilidad Neta despues de ISLR'):
                    fill, fnt = HDR_FILL, WHITE_FONT
                elif is_header:
                    fill, fnt = SEC_FILL, DARK_FONT
                else:
                    fill, fnt = WHITE_FILL, NORM_FONT

                # Columna A: nombre partida
                a_cell = ws.cell(row=row_num, column=1, value=partida)
                a_cell.font      = fnt
                a_cell.fill      = fill
                a_cell.alignment = Alignment(vertical='center', indent=0 if is_header else 2)
                a_cell.border    = border

                # Columnas de meses (C..N)
                for m_idx, month in enumerate(self.months):
                    col = COL_M_START + m_idx
                    if is_header:
                        val = None
                    else:
                        if unit == 'CONSOLIDADO':
                            val = sum(lookup.get((u, month, partida), 0) for u in self.units)
                        else:
                            val = lookup.get((unit, month, partida), 0)
                        val = val if val else None
                    c = ws.cell(row=row_num, column=col, value=val)
                    c.number_format = NUM_FMT
                    c.font      = fnt
                    c.fill      = fill
                    c.alignment = Alignment(horizontal='right', vertical='center')
                    c.border    = border

                # Columna B: ANUAL = SUM(meses)
                month_range = f'{get_column_letter(COL_M_START)}{row_num}:{get_column_letter(COL_M_END)}{row_num}'
                b_cell = ws.cell(row=row_num, column=COL_ANUAL)
                b_cell.value         = f'=SUM({month_range})'
                b_cell.number_format = NUM_FMT
                b_cell.font          = fnt
                b_cell.fill          = fill
                b_cell.alignment     = Alignment(horizontal='right', vertical='center')
                b_cell.border        = border

                # Columna ACUM EJEC: suma acumulada mes a mes hasta el último mes con dato
                # Usamos la misma fórmula que ANUAL por ahora; se puede hacer dinámica con
                # una columna auxiliar oculta, pero en Excel el ANUAL ya es el acumulado.
                acum_cell = ws.cell(row=row_num, column=COL_ACUM)
                acum_cell.value         = f'=B{row_num}'
                acum_cell.number_format = NUM_FMT
                acum_cell.font          = Font(name='Arial', size=9, italic=True, bold=is_header)
                acum_cell.fill          = ACUM_FILL if not is_header else fill
                acum_cell.alignment     = Alignment(horizontal='right', vertical='center')
                acum_cell.border        = border

                # Columna %VAR: variación relativa vs mes anterior
                # Para cada fila calculamos en Python la posición del penúltimo mes con dato.
                # En Excel usamos una fórmula dinámica: (último mes - penúltimo) / ABS(penúltimo)
                # Simplificación: %VAR = (mes N - mes N-1) / ABS(mes N-1), donde N=DIC o último cargado
                # Dejamos fórmula genérica comparando el último par de meses definidos
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
            total_gas_row = partida_rows.get('Total Gastos')
            for p, r in partida_rows.items():
                pv = ws.cell(row=r, column=COL_PVTAS)
                pg = ws.cell(row=r, column=COL_PGASTOS)
                if total_ing_row:
                    pv.value = f'=IF(B{total_ing_row}<>0,B{r}/B{total_ing_row},"")'
                    pv.number_format = PCT_FMT
                if total_gas_row:
                    pg.value = f'=IF(B{total_gas_row}<>0,B{r}/B{total_gas_row},"")'
                    pg.number_format = PCT_FMT
                for c in [pv, pg]:
                    c.font      = NORM_FONT
                    c.border    = border
                    c.alignment = Alignment(horizontal='right', vertical='center')

        for ws in wb.worksheets:
            ws.freeze_panes = 'B3'

        path = os.path.join(tempfile.gettempdir(), f'EEFF_ULTRAX_{self.year}.xlsx')
        wb.save(path)
        return path


class ESFExporter:
    """Genera Excel del Estado de Situación Financiera por trimestre."""
    def __init__(self, data, year, units):
        # data: list of dicts {year, quarter, unit, partida, amount}
        self.data  = data
        self.year  = year
        self.units = units

    def _build_lookup(self):
        lookup = {}
        for row in self.data:
            key = (row['unit'], row['quarter'], row['partida'])
            lookup[key] = row['amount']
        return lookup

    def generate(self):
        wb     = openpyxl.Workbook()
        lookup = self._build_lookup()
        QUARTERS = [1, 2, 3, 4]
        Q_LABELS = {1: 'Q1 (Ene-Mar)', 2: 'Q2 (Abr-Jun)', 3: 'Q3 (Jul-Sep)', 4: 'Q4 (Oct-Dic)'}

        HDR_FILL  = PatternFill('solid', start_color='1F3864')
        SUB_FILL  = PatternFill('solid', start_color='2E75B6')
        SEC_FILL  = PatternFill('solid', start_color='BDD7EE')
        WHITE_FILL= PatternFill('solid', start_color='FFFFFF')
        VAR_FILL  = PatternFill('solid', start_color='FFF2CC')
        WHITE_FONT= Font(name='Arial', bold=True, color='FFFFFF', size=10)
        DARK_FONT = Font(name='Arial', bold=True, color='1F3864', size=10)
        NORM_FONT = Font(name='Arial', size=9)
        NUM_FMT   = '#,##0.00;(#,##0.00);"-"'
        PCT_FMT   = '0.0%;(0.0%);"-"'
        thin      = Side(style='thin', color='BDD7EE')
        border    = Border(left=thin, right=thin, top=thin, bottom=thin)

        sheets_to_build = self.units + ['CONSOLIDADO']
        wb.remove(wb.active)

        # Layout: A=Partida, B=Q1, C=Q2, D=Q3, E=Q4, F=%VarQ1Q2, G=%VarQ2Q3, H=%VarQ3Q4
        COL_Q     = {1: 2, 2: 3, 3: 4, 4: 5}
        COL_VAR12 = 6
        COL_VAR23 = 7
        COL_VAR34 = 8

        for unit in sheets_to_build:
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
            for partida, is_header, section in ESF_STRUCTURE:
                ws.row_dimensions[row_num].height = 16

                if partida in ('TOTAL ACTIVOS', 'TOTAL PASIVOS Y PATRIMONIO',
                               'TOTAL PASIVOS', 'TOTAL PATRIMONIO',
                               'TOTAL PASIVOS CORRIENTES', 'TOTAL PASIVOS NO CORRIENTES'):
                    fill, fnt = HDR_FILL, WHITE_FONT
                elif is_header:
                    fill, fnt = SEC_FILL, DARK_FONT
                else:
                    fill, fnt = WHITE_FILL, NORM_FONT

                a_cell = ws.cell(row=row_num, column=1, value=partida)
                a_cell.font      = fnt
                a_cell.fill      = fill
                a_cell.alignment = Alignment(vertical='center', indent=0 if is_header else 2)
                a_cell.border    = border

                for q in QUARTERS:
                    col = COL_Q[q]
                    if is_header:
                        val = None
                    else:
                        if unit == 'CONSOLIDADO':
                            val = sum(lookup.get((u, q, partida), 0) for u in self.units)
                        else:
                            val = lookup.get((unit, q, partida), 0)
                        val = val if val else None
                    c = ws.cell(row=row_num, column=col, value=val)
                    c.number_format = NUM_FMT
                    c.font      = fnt
                    c.fill      = fill
                    c.alignment = Alignment(horizontal='right', vertical='center')
                    c.border    = border

                # %Var trimestral
                for var_col, qa, qb in [(COL_VAR12, 'B', 'C'), (COL_VAR23, 'C', 'D'), (COL_VAR34, 'D', 'E')]:
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

                row_num += 1

            ws.freeze_panes = 'B3'

        path = os.path.join(tempfile.gettempdir(), f'ESF_ULTRAX_{self.year}.xlsx')
        wb.save(path)
        return path
