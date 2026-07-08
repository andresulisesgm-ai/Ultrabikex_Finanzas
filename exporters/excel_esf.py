from engine import ESF_STRUCTURE, esf_engine


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
            header_stack = []
            partida_row  = {}

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

                for q in QUARTERS:
                    col = COL_Q[q]
                    c   = ws.cell(row=row_num, column=col)
                    c.font      = fnt
                    c.fill      = fill
                    c.alignment = Alignment(horizontal='right', vertical='center')
                    c.border    = border
                    c.number_format = NUM_FMT

                    if is_header:
                        val = quarters_v.get(q, None) or quarters_v.get(str(q), None)
                        c.value = val if val else None
                    else:
                        val = quarters_v.get(q, None) or quarters_v.get(str(q), None)
                        c.value = val if val else None

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

            engine_unit = unit if unit != 'CONSOLIDADO' else ''
            self._build_notes_sheet(wb, unit, engine_unit)

        path = os.path.join(tempfile.gettempdir(), f'ESF_ULTRAX_{self.year}.xlsx')
        wb.save(path)
        return path

    def _build_notes_sheet(self, wb, unit, engine_unit):
        import sqlite3, os
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
        from openpyxl.utils import get_column_letter

        DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'ultrax.db')
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

        ws.merge_cells('A1:G1')
        t = ws['A1']
        t.value     = f'NOTAS — ESTADO DE SITUACIÓN FINANCIERA — {unit.upper()} — {self.year}'
        t.font      = Font(name='Arial', bold=True, color='FFFFFF', size=12)
        t.fill      = HDR_FILL
        t.alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 24

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

        partidas_order = [item[0] for item in ESF_STRUCTURE if not item[1]]

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

        from collections import defaultdict
        data = defaultdict(lambda: defaultdict(lambda: {'name': '', 'quarters': {}}))
        for r in rows:
            data[r['group_name']][r['odoo_code']]['name'] = r['odoo_name']
            data[r['group_name']][r['odoo_code']]['quarters'][r['quarter']] = r['amount_sign']

        row_num = 3
        for partida in partidas_order:
            if partida not in data:
                continue

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
