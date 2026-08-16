from openpyxl.styles import Font, Alignment

NUM_FMT = '#,##0.00;-#,##0.00;"-"'
PCT_FMT = '0.0%;(0.0%);"-"'

# Ajustes frente a ESF_STRUCTURE_V2, decididos en sesión — si no está en el
# archivo de Yocelin, no se incluye en el exportable.
EXCLUIR_ESF_EXPORT = {
    'Ajuste por Diferencial Cambiario', 'Propiedades de inversión',
    'Total Activos Corrientes', 'Total Activos No Corrientes',
    'Total Pasivos Corrientes', 'Total Pasivos No Corrientes',
    'Total Patrimonio'
}
RENOMBRAR_ESF_EXPORT = {
    # Activos Corrientes
    'Caja en Bs': 'Cajas en Bs',
    'Caja en $': 'Cajas en $',
    'Fondo en Bs': 'Fondos en Bs',
    'Fondo en $': 'Fondos en $',
    'Bancos en Bs': 'Bancos en Bs',
    'Bancos en $': 'Bancos en $',
    'Bancos en transito en Bs': 'Bancos en transito en Bs',
    'Bancos en transito en $': 'Bancos en transito en $',
    'Cuentas por cobrar clientes': 'A clientes',
    'A empresas relacionadas del grupo (CxC)': 'A empresas relacionadas del grupo',
    'A empresas externas del grupo (CxC)': 'A empresas externas del grupo',
    'A socios (CxC)': 'A socios',
    'Cuentas por cobrar empleados': 'A empleados',
    'Cuentas por cobrar por sociedades': 'Por sociedades',
    'A empresas relacionadas del grupo (PxC)': 'A empresas relacionadas del grupo',
    'A empresas externas del grupo (PxC)': 'A empresas externas del grupo',
    'A socios (PxC)': 'A socios',
    'A empleados (PxC)': 'A empleados',
    'Otros prestamos por cobrar': 'A terceros',
    'Anticipos a proveedores': 'A proveedores',
    'Anticipos a socios': 'A socios',
    'Anticipos a empleados': 'A empleados',
    'Inventario de mercancias': 'De mercancía',
    'Inventario de suministros': 'De suministros',
    'Inventario en transito': 'En tránsito',
    'Inventarios de Consignacion': 'A consignación',
    'Impuestos pagados por anticipado': 'Impuestos ',

    # Activos No Corrientes
    'Cuentas por cobrar clientes L.P.': 'Deudores comerciales a LP',
    'Otras cuentas por cobrar L.P.': 'Otras cuentas por cobrar a LP',
    'Prestamos por cobrar L.P.': 'Préstamos por cobrar LP',
    'Propiedades de Inversión': 'Propiedades de inversión',

    # Pasivos Corrientes
    'A proveedores': 'A proveedores ',
    'A empresas relacionadas del grupo (CxP)': 'A empresas relacionadas del grupo',
    'A empresas externas del grupo (CxP)': 'A empresas externas del grupo',
    'A socios (CxP)': 'A socios',
    'Otras Cuentas por pagar': 'Otras cuentas por pagar',
    'Retenciones Laborales por pagar': 'Retenciones laborales a pagar',
    'A empresas relacionadas del grupo (PxP)': 'A empresas relacionadas del grupo',
    'A empresas externas del grupo (PxP)': 'A empresas externas del grupo',
    'A socios (PxP)': 'A socios',
    'A empleados (PxP)': 'A empleados',
    'Otros prestamos por pagar': 'Otros prestamos por pagar ',
    'Anticipos de Pasivo': 'Anticipos',
}
REPARENT_ESF_EXPORT = {
    # Se aplana: el hijo nivel 4 pasa a ocupar el lugar del header nivel 3 excluido.
    'Propiedades de Inversión': ('Otros activos no corrientes', 3),
}

# Filas cuyo valor NO se escribe como fórmula de suma genérica — cada una
# tiene un cálculo especial replicado explícitamente abajo.
NOMBRES_ESPECIALES = {
    'Resultados del ejercicio', 'Resultados acumulados',
    'ACTIVOS CORRIENTES', 'ACTIVOS NO CORRIENTES',
    'PASIVOS CORRIENTES', 'PASIVOS NO CORRIENTES', 'PATRIMONIO',
    'Total Activos Corrientes', 'Total Activos No Corrientes',
    'Total Pasivos Corrientes', 'Total Pasivos No Corrientes',
    'Total Patrimonio',
    'TOTAL ACTIVOS', 'TOTAL PASIVOS', 'TOTAL PASIVOS Y PATRIMONIO',
}


class ESFExporter:
    """Genera ESF ULTRAX consolidado con fórmulas vivas, más EERR ULTRAX
    (año actual, con las 6 unidades y notas) y EERR ULTRAX (Año Anterior)
    (solo consolidado) dentro del mismo archivo, para trazabilidad de
    'Resultados del ejercicio'."""

    def __init__(self, year, months, empresa_id=None):
        self.year = year
        self.months = months  # lista completa de meses del año, ej. ENE..DIC
        self.empresa_id = empresa_id

    def generate(self):
        import openpyxl, os, tempfile
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
        from engine import esf_engine, ESF_STRUCTURE_V2
        from exporters.excel_eerr import ExcelExporter
        from db import get_db

        year_prev = str(int(self.year) - 1)

        wb = openpyxl.Workbook()
        wb.remove(wb.active)

        from helpers import _nombre_empresa_display
        db_conn = get_db()
        nombre_emp = _nombre_empresa_display(db_conn, self.empresa_id)

        # Unidades reales de la empresa activa (o la lista de todas las unidades si es Holding/empresa_id=None).
        if self.empresa_id is not None:
            units_export = [r[0] for r in db_conn.execute('SELECT nombre FROM unidades WHERE empresa_id=?', [self.empresa_id]).fetchall()]
        else:
            # Holding (sin empresa_id explícito): agregado de todas las unidades reales de las 4 empresas.
            units_export = [r[0] for r in db_conn.execute('SELECT nombre FROM unidades').fetchall()]

        # 1. EERR ULTRAX (año actual): unidades reales + notas, reusando el exportador existente.
        eerr_meta = ExcelExporter(self.year, units_export, self.months, empresa_id=self.empresa_id).generate(
            wb=wb, save=False, return_meta=True
        )
        # 2. EERR ULTRAX (Año Anterior): solo consolidado, sin unidades ni notas
        #    (units=[] hace que sheets_to_build solo contenga el nombre consolidado).
        eerr_prev_meta = ExcelExporter(year_prev, [], self.months, empresa_id=self.empresa_id).generate(
            wb=wb, save=False, return_meta=True, consolidado_name=f'EERR {nombre_emp} (Año Ant.)'[:31]
        )

        sheet_curr = eerr_meta['sheet_name_consolidado']
        row_islr_curr = eerr_meta['partida_rows_consolidado'].get('Utilidad Neta despues de ISLR')
        cols_curr = eerr_meta['month_start_cols']

        sheet_prev = eerr_prev_meta['sheet_name_consolidado']
        row_islr_prev = eerr_prev_meta['partida_rows_consolidado'].get('Utilidad Neta despues de ISLR')
        cols_prev = eerr_prev_meta['month_start_cols']

        # 3. Datos ESF vía motor central — año actual (Q1-Q4) y año anterior (se usa Q4).
        data_curr = esf_engine(self.year, '', empresa_id=self.empresa_id)
        data_prev = esf_engine(year_prev, '', empresa_id=self.empresa_id)

        expected_levels = {item[0]: item[5] for item in ESF_STRUCTURE_V2}
        qdata_curr = {}
        for r in data_curr['rows']:
            partida = r['partida']
            if partida in expected_levels and r.get('level') == expected_levels[partida]:
                qdata_curr[partida] = r['quarters']

        qdata_prev = {}
        for r in data_prev['rows']:
            partida = r['partida']
            if partida in expected_levels and r.get('level') == expected_levels[partida]:
                qdata_prev[partida] = r['quarters']

        # 4. Estructura filtrada/ajustada para el exportable.
        filtered = []
        for item in ESF_STRUCTURE_V2:
            name, is_header, _, bold, bg_color, level, _, parent_name, indent = item
            if name in EXCLUIR_ESF_EXPORT:
                continue
            if name in REPARENT_ESF_EXPORT:
                parent_name, level = REPARENT_ESF_EXPORT[name]
                is_header = False
            display = RENOMBRAR_ESF_EXPORT.get(name, name)
            filtered.append({
                'name': name, 'display': display, 'is_header': is_header,
                'bold': bold, 'level': level, 'parent_name': parent_name, 'indent': indent,
            })

        # Reordenamiento de TOTAL ACTIVOS para moverlo al final de los activos (justo antes de PASIVOS CORRIENTES)
        idx_ta = None
        for i, f in enumerate(filtered):
            if f['name'] == 'TOTAL ACTIVOS':
                idx_ta = i
                break
        if idx_ta is not None:
            ta_item = filtered.pop(idx_ta)
            idx_pc = None
            for i, f in enumerate(filtered):
                if f['name'] == 'PASIVOS CORRIENTES':
                    idx_pc = i
                    break
            if idx_pc is not None:
                filtered.insert(idx_pc, ta_item)
            else:
                filtered.append(ta_item)

        HDR_FILL  = PatternFill('solid', start_color='1F3864')
        SEC_FILL  = PatternFill('solid', start_color='F2F2F2')
        WHITE_FILL= PatternFill('solid', start_color='FFFFFF')
        TEAL_FILL = PatternFill('solid', start_color='D6DCE4')
        DARK_FONT = Font(name='Arial', bold=True, color='000000', size=10)
        NORM_FONT = Font(name='Arial', size=9)
        thin      = Side(style='thin', color='D9D9D9')
        border    = Border(left=thin, right=thin, top=thin, bottom=thin)

        nombre_hoja_esf = f'ESF {nombre_emp}'[:31]
        ws = wb.create_sheet(nombre_hoja_esf)
        ws.sheet_view.showGridLines = False

        headers = ['PARTIDA', 'Año Anterior', 'Q1', 'Vari Rel.', 'Q2', 'Vari Rel.', 'Q3', 'Vari Rel.', 'Q4', 'Vari Rel.', 'Vari Rel. actual vs anterior']
        for ci, h in enumerate(headers, 1):
            c = ws.cell(row=2, column=ci, value=h)
            c.font = Font(name='Arial', bold=True, color='FFFFFF', size=10)
            c.fill = HDR_FILL
            c.alignment = Alignment(horizontal='center', vertical='center')
            c.border = border

        ws.merge_cells('A1:K1')
        title = ws['A1']
        title.value = f'ESTADO DE SITUACIÓN FINANCIERA — {nombre_emp.upper()} — {self.year}'
        title.font = Font(name='Arial', bold=True, color='FFFFFF', size=12)
        title.fill = HDR_FILL
        title.alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 24

        ws.column_dimensions['A'].width = 48
        for ci in range(2, 12):
            ws.column_dimensions[get_column_letter(ci)].width = 14

        COL_AA, COL_Q1, COL_V1, COL_Q2, COL_V2, COL_Q3, COL_V3, COL_Q4, COL_V4, COL_VF = range(2, 12)

        row_num = 3
        row_of = {}
        for f in filtered:
            fill, fnt = (TEAL_FILL, DARK_FONT) if f['name'] in NOMBRES_ESPECIALES else \
                        (SEC_FILL, DARK_FONT) if f['is_header'] else (WHITE_FILL, NORM_FONT)

            a = ws.cell(row=row_num, column=1, value=f['display'])
            a.font = fnt
            a.fill = fill
            a.alignment = Alignment(vertical='center', indent=f['indent'])
            a.border = border

            qc = qdata_curr.get(f['name'], {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0})
            qp = qdata_prev.get(f['name'], {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0})

            valores = [qp.get(4, 0.0), qc.get(1, 0.0), None, qc.get(2, 0.0), None,
                       qc.get(3, 0.0), None, qc.get(4, 0.0), None, None]
            for i, val in enumerate(valores):
                if val is None:
                    continue
                c = ws.cell(row=row_num, column=2 + i, value=val)
                c.number_format = NUM_FMT
                c.font = fnt
                c.fill = fill
                c.border = border
                c.alignment = Alignment(horizontal='right', vertical='center')

            row_of[f['name']] = row_num
            row_num += 1

        def L(col):
            return get_column_letter(col)

        def set_formula(name, col, formula):
            r = row_of.get(name)
            if r is None:
                return
            c = ws.cell(row=r, column=col, value=formula)
            c.number_format = NUM_FMT

        # --- Nivel 2: headers que suman sus hijos nivel 3 (parent_name == su nombre) ---
        hijos_por_padre = {}
        for f in filtered:
            hijos_por_padre.setdefault(f['parent_name'], []).append(f['name'])

        headers_nivel2 = [f['name'] for f in filtered if f['is_header'] and f['name'] not in NOMBRES_ESPECIALES]
        for padre in headers_nivel2:
            hijos = hijos_por_padre.get(padre, [])
            hijos_rows = [row_of[h] for h in hijos if h in row_of]
            if not hijos_rows:
                continue
            for col in (COL_AA, COL_Q1, COL_Q2, COL_Q3, COL_Q4):
                refs = '+'.join(f'{L(col)}{hr}' for hr in hijos_rows)
                set_formula(padre, col, f'={refs}')

        # --- CATEGORIAS_NIVEL1: Se calculan sumando sus hijos nivel 2 directos ---
        CATEGORIAS_NIVEL1 = {
            'ACTIVOS CORRIENTES': ['Efectivo y Equivalentes', 'Cuentas por Cobrar', 'Otras Cuentas por Cobrar', 'Préstamos por Cobrar', 'Anticipos', 'Inventarios', 'Prepagados'],
            'ACTIVOS NO CORRIENTES': ['Otros activos no corrientes', 'Propiedades, Plantas y Equipos'],
            'PASIVOS CORRIENTES': ['Cuentas por Pagar', 'Otras cuentas por pagar', 'Préstamos por Pagar', 'Anticipos de Pasivo', 'Provisiones'],
            'PASIVOS NO CORRIENTES': ['Otras cuentas por pagar L.P.'],
            'PATRIMONIO': ['Capital social', 'Reservas legales y estatutarias', 'Superavit por revaluacion', 'Resultados acumulados', 'Resultados del ejercicio'],
        }

        for cat, hijos in CATEGORIAS_NIVEL1.items():
            hijos_rows = [row_of[h] for h in hijos if h in row_of]
            if not hijos_rows:
                continue
            for col in (COL_AA, COL_Q1, COL_Q2, COL_Q3, COL_Q4):
                refs = '+'.join(f'{L(col)}{hr}' for hr in hijos_rows)
                set_formula(cat, col, f'={refs}')

        # --- Nivel 0: TOTAL ACTIVOS / TOTAL PASIVOS / TOTAL PASIVOS Y PATRIMONIO ---
        r_ac = row_of.get('ACTIVOS CORRIENTES')
        r_anc = row_of.get('ACTIVOS NO CORRIENTES')
        r_pc = row_of.get('PASIVOS CORRIENTES')
        r_pnc = row_of.get('PASIVOS NO CORRIENTES')
        r_pat = row_of.get('PATRIMONIO')
        r_ta = row_of.get('TOTAL ACTIVOS')
        r_tp = row_of.get('TOTAL PASIVOS')
        for col in (COL_AA, COL_Q1, COL_Q2, COL_Q3, COL_Q4):
            if r_ac and r_anc:
                set_formula('TOTAL ACTIVOS', col, f'={L(col)}{r_ac}+{L(col)}{r_anc}')
            if r_pc and r_pnc:
                set_formula('TOTAL PASIVOS', col, f'={L(col)}{r_pc}+{L(col)}{r_pnc}')
            if r_tp and r_pat:
                set_formula('TOTAL PASIVOS Y PATRIMONIO', col, f'={L(col)}{r_tp}+{L(col)}{r_pat}')

        # --- Resultados del ejercicio: enlazado a EERR (única partida que viene de otro motor) ---
        # Toma el ACUM EJEC del último mes de cada trimestre (ya es el acumulado desde enero, no sumar meses).
        ultimo_mes_q = {
            1: 'MAR',
            2: 'JUN',
            3: 'SEPT',
            4: self.months[-1] if self.months else 'DIC',
        }
        if row_islr_curr:
            for q, col in zip((1, 2, 3, 4), (COL_Q1, COL_Q2, COL_Q3, COL_Q4)):
                m = ultimo_mes_q[q]
                if m in cols_curr:
                    col_acum = cols_curr[m] + 4
                    ref = f"'{sheet_curr}'!{L(col_acum)}{row_islr_curr}"
                    set_formula('Resultados del ejercicio', col, f'={ref}')
        if row_islr_prev:
            meses_prev = [m for m in self.months if m in cols_prev]
            if meses_prev:
                ultimo_mes_prev = meses_prev[-1]
                col_acum_prev = cols_prev[ultimo_mes_prev] + 4
                ref = f"'{sheet_prev}'!{L(col_acum_prev)}{row_islr_prev}"
                set_formula('Resultados del ejercicio', COL_AA, f'={ref}')

        # --- Resultados acumulados: plug, formula viva SOLO para Q1-Q4.
        #     Año Anterior queda como valor fijo (decisión pendiente, ver ultrax_logs.md). ---
        r_cap = row_of.get('Capital social')
        r_res = row_of.get('Reservas legales y estatutarias')
        r_sup = row_of.get('Superavit por revaluacion')
        r_rej = row_of.get('Resultados del ejercicio')
        if r_ta and r_tp and r_cap and r_res and r_sup and r_rej:
            for col in (COL_Q1, COL_Q2, COL_Q3, COL_Q4):
                formula = (f'={L(col)}{r_ta}-{L(col)}{r_tp}-{L(col)}{r_cap}'
                           f'-{L(col)}{r_res}-{L(col)}{r_sup}-{L(col)}{r_rej}')
                set_formula('Resultados acumulados', col, formula)

        # --- Vari Rel.: Q1 vs Año Anterior, Q2 vs Q1, Q3 vs Q2, Q4 vs Q3, y Q4 vs Año Anterior ---
        VARI_PARES = [
            (COL_V1, COL_Q1, COL_AA),
            (COL_V2, COL_Q2, COL_Q1),
            (COL_V3, COL_Q3, COL_Q2),
            (COL_V4, COL_Q4, COL_Q3),
            (COL_VF, COL_Q4, COL_AA),
        ]
        for f in filtered:
            r = row_of[f['name']]
            for col_v, col_actual, col_base in VARI_PARES:
                actual_ref = f'{L(col_actual)}{r}'
                base_ref = f'{L(col_base)}{r}'
                formula = (
                    f'=IF(AND({base_ref}=0,{actual_ref}>0),100%,'
                    f'IF(AND({base_ref}<0,{actual_ref}>=0),({base_ref}-{actual_ref})/{base_ref},'
                    f'IF(AND({base_ref}>0,{actual_ref}>0),({actual_ref}-{base_ref})/{base_ref},'
                    f'IF(AND({base_ref}=0,{actual_ref}<=0),"",'
                    f'({actual_ref}-{base_ref})/{base_ref}))))'
                )
                c = ws.cell(row=r, column=col_v, value=formula)
                c.number_format = PCT_FMT
                c.font = NORM_FONT
                c.border = border
                c.alignment = Alignment(horizontal='right', vertical='center')

        ws.sheet_properties.outlinePr.summaryBelow = False
        for f in filtered:
            if f.get('level') == 3:
                r = row_of.get(f['name'])
                if r is not None:
                    ws.row_dimensions[r].outlineLevel = 1
                    ws.row_dimensions[r].hidden = True
        ws.sheet_view.showOutlineSymbols = True

        ws.freeze_panes = 'B3'

        # ESF visible como primera pestaña.
        wb.move_sheet(nombre_hoja_esf, offset=-(len(wb.sheetnames) - 1))
        wb.move_sheet(eerr_meta['sheet_name_consolidado'], offset=-(wb.sheetnames.index(eerr_meta['sheet_name_consolidado']) - 1))

        path = os.path.join(tempfile.gettempdir(), f'ESF_{nombre_emp}_{self.year}.xlsx')
        wb.save(path)
        return path
