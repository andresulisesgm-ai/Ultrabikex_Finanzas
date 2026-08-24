from flask import Blueprint, request, jsonify, Response
from datetime import datetime
from auth import admin_required
from db import get_db

briefing_bp = Blueprint('briefing', __name__)

TIPOS_PROMPT_VALIDOS = {'consolidado', 'unidad_mes', 'anual', 'comparativo_mes', 'comparativo_anual', 'consolidado_mes', 'consolidado_divisa_anual', 'consolidado_divisa_mes', 'unidad_divisa_anual', 'unidad_divisa_mes', 'esf_consolidado', 'esf_divisa_real', 'comparativo_divisa_mes', 'comparativo_divisa_anual'}


@briefing_bp.route('/api/briefing-prompt', methods=['GET'])
@admin_required
def get_briefing_prompt():
    tipo = request.args.get('tipo', '')
    default_flag = request.args.get('default', '0') == '1'
    if tipo not in TIPOS_PROMPT_VALIDOS:
        return jsonify({'error': 'tipo_reporte inválido'}), 400

    if default_flag:
        from db import (
            PROMPT_CONSOLIDADO_DEFAULT, PROMPT_CONSOLIDADO_MES_DEFAULT,
            PROMPT_CONSOLIDADO_DIVISA_ANUAL_DEFAULT, PROMPT_CONSOLIDADO_DIVISA_MES_DEFAULT,
            PROMPT_ANUAL_DEFAULT, PROMPT_UNIDAD_DIVISA_ANUAL_DEFAULT,
            PROMPT_UNIDAD_MES_DEFAULT, PROMPT_UNIDAD_DIVISA_MES_DEFAULT,
            PROMPT_ESF_CONSOLIDADO_DEFAULT, PROMPT_ESF_DIVISA_REAL_DEFAULT,
            PROMPT_COMPARATIVO_ANUAL_DEFAULT, PROMPT_COMPARATIVO_MES_DEFAULT,
            PROMPT_COMPARATIVO_DIVISA_ANUAL_DEFAULT, PROMPT_COMPARATIVO_DIVISA_MES_DEFAULT
        )
        fallbacks = {
            'consolidado': PROMPT_CONSOLIDADO_DEFAULT,
            'consolidado_mes': PROMPT_CONSOLIDADO_MES_DEFAULT,
            'consolidado_divisa_anual': PROMPT_CONSOLIDADO_DIVISA_ANUAL_DEFAULT,
            'consolidado_divisa_mes': PROMPT_CONSOLIDADO_DIVISA_MES_DEFAULT,
            'anual': PROMPT_ANUAL_DEFAULT,
            'unidad_divisa_anual': PROMPT_UNIDAD_DIVISA_ANUAL_DEFAULT,
            'unidad_mes': PROMPT_UNIDAD_MES_DEFAULT,
            'unidad_divisa_mes': PROMPT_UNIDAD_DIVISA_MES_DEFAULT,
            'esf_consolidado': PROMPT_ESF_CONSOLIDADO_DEFAULT,
            'esf_divisa_real': PROMPT_ESF_DIVISA_REAL_DEFAULT,
            'comparativo_anual': PROMPT_COMPARATIVO_ANUAL_DEFAULT,
            'comparativo_mes': PROMPT_COMPARATIVO_MES_DEFAULT,
            'comparativo_divisa_anual': PROMPT_COMPARATIVO_DIVISA_ANUAL_DEFAULT,
            'comparativo_divisa_mes': PROMPT_COMPARATIVO_DIVISA_MES_DEFAULT
        }
        return jsonify({'tipo_reporte': tipo, 'prompt_text': fallbacks.get(tipo, '')})

    db = get_db()
    row = db.execute(
        "SELECT prompt_text FROM briefing_prompts WHERE tipo_reporte = ?", (tipo,)
    ).fetchone()

    if row is None:
        return jsonify({'error': 'prompt no encontrado'}), 404

    return jsonify({'tipo_reporte': tipo, 'prompt_text': row['prompt_text']})


@briefing_bp.route('/api/briefing-prompt', methods=['POST'])
@admin_required
def save_briefing_prompt():
    data = request.get_json()
    tipo = data.get('tipo_reporte', '')
    texto = data.get('prompt_text', '')

    if tipo not in TIPOS_PROMPT_VALIDOS:
        return jsonify({'error': 'tipo_reporte inválido'}), 400
    if not texto.strip():
        return jsonify({'error': 'prompt_text vacío'}), 400

    db = get_db()
    db.execute("""
        INSERT INTO briefing_prompts (tipo_reporte, prompt_text, updated_at)
        VALUES (?, ?, datetime('now','localtime'))
        ON CONFLICT(tipo_reporte) DO UPDATE SET
            prompt_text = excluded.prompt_text,
            updated_at = excluded.updated_at
    """, (tipo, texto))
    db.commit()

    return jsonify({'status': 'ok', 'tipo_reporte': tipo})


@briefing_bp.route('/api/export/ai', methods=['GET', 'POST'])
@admin_required
def export_ai():
    import io
    from db import (
        PROMPT_CONSOLIDADO_DEFAULT, PROMPT_CONSOLIDADO_MES_DEFAULT,
        PROMPT_CONSOLIDADO_DIVISA_ANUAL_DEFAULT, PROMPT_CONSOLIDADO_DIVISA_MES_DEFAULT,
        PROMPT_ANUAL_DEFAULT, PROMPT_UNIDAD_DIVISA_ANUAL_DEFAULT,
        PROMPT_UNIDAD_MES_DEFAULT, PROMPT_UNIDAD_DIVISA_MES_DEFAULT,
        PROMPT_ESF_CONSOLIDADO_DEFAULT, PROMPT_ESF_DIVISA_REAL_DEFAULT,
        PROMPT_COMPARATIVO_ANUAL_DEFAULT, PROMPT_COMPARATIVO_MES_DEFAULT,
        PROMPT_COMPARATIVO_DIVISA_ANUAL_DEFAULT, PROMPT_COMPARATIVO_DIVISA_MES_DEFAULT
    )

    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        year = data.get('year') or request.args.get('year', str(datetime.now().year))
        month = data.get('month') or request.args.get('month', '')
        unit = data.get('unit') or request.args.get('unit', '')
        tipo = data.get('tipo') or request.args.get('tipo', 'eerr')
        prompt_text = data.get('prompt_text')
        empresa_id = data.get('empresa_id') or request.args.get('empresa_id', type=int)
        quarter = data.get('quarter') or request.args.get('quarter', type=int)
    else:
        year = request.args.get('year', str(datetime.now().year))
        month = request.args.get('month', '')
        unit = request.args.get('unit', '')
        tipo = request.args.get('tipo', 'eerr')
        prompt_text = request.args.get('prompt_text')
        empresa_id = request.args.get('empresa_id', type=int)
        quarter = request.args.get('quarter', type=int)

    db = get_db()

    # ── Selección de prompt ────────────────────────────────────────────────────
    if not prompt_text:
        # 'tipo' ya lleva la señal de Divisa Real en su propio nombre (eerr_divisa,
        # esf_divisa, comparativa_divisa) -- no hace falta ningún parámetro aparte.
        es_divisa = 'divisa' in tipo
        if tipo in ('comparativa', 'comparativa_divisa'):
            if es_divisa:
                tipo_prompt = 'comparativo_divisa_anual' if month == '' else 'comparativo_divisa_mes'
            else:
                tipo_prompt = 'comparativo_anual' if month == '' else 'comparativo_mes'
        elif tipo == 'esf':
            tipo_prompt = 'esf_consolidado'
        elif tipo == 'esf_divisa':
            tipo_prompt = 'esf_divisa_real'
        else:
            if unit == '':
                if es_divisa:
                    tipo_prompt = 'consolidado_divisa_anual' if month == '' else 'consolidado_divisa_mes'
                else:
                    tipo_prompt = 'consolidado' if month == '' else 'consolidado_mes'
            elif month == '':
                tipo_prompt = 'unidad_divisa_anual' if es_divisa else 'anual'
            else:
                tipo_prompt = 'unidad_divisa_mes' if es_divisa else 'unidad_mes'

        row_p = db.execute("SELECT prompt_text FROM briefing_prompts WHERE tipo_reporte = ?", (tipo_prompt,)).fetchone()
        if row_p:
            prompt = row_p['prompt_text']
        else:
            # Fallback a constantes importadas de db.py -- las 14 combinaciones,
            # no solo las 5 originales (bug encontrado en auditoría: este
            # diccionario había quedado desactualizado respecto al de
            # get_briefing_prompt(), dejando los 9 tipos nuevos inalcanzables
            # en la práctica mientras la tabla briefing_prompts no tuviera fila
            # guardada para ellos).
            fallbacks = {
                'consolidado': PROMPT_CONSOLIDADO_DEFAULT,
                'consolidado_mes': PROMPT_CONSOLIDADO_MES_DEFAULT,
                'consolidado_divisa_anual': PROMPT_CONSOLIDADO_DIVISA_ANUAL_DEFAULT,
                'consolidado_divisa_mes': PROMPT_CONSOLIDADO_DIVISA_MES_DEFAULT,
                'anual': PROMPT_ANUAL_DEFAULT,
                'unidad_divisa_anual': PROMPT_UNIDAD_DIVISA_ANUAL_DEFAULT,
                'unidad_mes': PROMPT_UNIDAD_MES_DEFAULT,
                'unidad_divisa_mes': PROMPT_UNIDAD_DIVISA_MES_DEFAULT,
                'esf_consolidado': PROMPT_ESF_CONSOLIDADO_DEFAULT,
                'esf_divisa_real': PROMPT_ESF_DIVISA_REAL_DEFAULT,
                'comparativo_anual': PROMPT_COMPARATIVO_ANUAL_DEFAULT,
                'comparativo_mes': PROMPT_COMPARATIVO_MES_DEFAULT,
                'comparativo_divisa_anual': PROMPT_COMPARATIVO_DIVISA_ANUAL_DEFAULT,
                'comparativo_divisa_mes': PROMPT_COMPARATIVO_DIVISA_MES_DEFAULT
            }
            prompt = fallbacks.get(tipo_prompt, PROMPT_CONSOLIDADO_DEFAULT)
    else:
        prompt = prompt_text

    # ── Construcción del archivo .md ───────────────────────────────────────────
    lines = []
    lines.append(prompt)
    lines.append('')

    # Encabezado
    periodo = f"{month} {year}" if month else f"Año completo {year}"
    from helpers import _nombre_empresa
    alcance = unit if unit else ('Consolidado grupo' if empresa_id is None else _nombre_empresa(db, empresa_id))
    moneda = "USD Paralelo" if 'divisa' in tipo else "USD / Bs"

    lines.append(f"# BRIEFING FINANCIERO — ULTRABIKEX")
    lines.append(f"**Período:** {periodo}")
    lines.append(f"**Alcance:** {alcance}")
    lines.append(f"**Moneda:** {moneda}")
    lines.append(f"**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append('')
    lines.append('---')
    lines.append('')

    # ── EERR ──────────────────────────────────────────────────────────────────
    if tipo in ['eerr', 'completo']:
        lines.append('## ESTADO DE RESULTADOS')
        lines.append('')
        from engine import eerr_completo_v2_ui_adapter
        data = eerr_completo_v2_ui_adapter(db, year, unit, empresa_id=empresa_id)
        rows = data.get('rows', [])

        meses_disponibles = []
        if rows:
            meses_disponibles = [m['month'] for m in rows[0].get('meses', [])]
            if month:
                meses_disponibles = [m for m in meses_disponibles if m == month.upper()]

        header = '| Partida | ' + ' | '.join(meses_disponibles) + ' | ACUM |' if meses_disponibles else '| Partida | ACUM |'
        separator = '|---' * (len(meses_disponibles) + 2) + '|'
        lines.append(header)
        lines.append(separator)

        for row in rows:
            partida = row.get('partida', '')
            prefix = '**' if row.get('bold') else ''
            suffix = '**' if row.get('bold') else ''
            meses_data = {m['month']: m.get('ejecutado', {}).get('valor', 0) for m in row.get('meses', [])}

            if meses_disponibles:
                valores = ' | '.join(f"{meses_data.get(m, 0):,.0f}" for m in meses_disponibles)
                acum = sum(m.get('ejecutado', {}).get('valor', 0) for m in row.get('meses', []))
                lines.append(f"| {prefix}{partida}{suffix} | {valores} | {acum:,.0f} |")
            else:
                acum = sum(m.get('ejecutado', {}).get('valor', 0) for m in row.get('meses', []))
                lines.append(f"| {prefix}{partida}{suffix} | {acum:,.0f} |")

        lines.append('')
        lines.append('---')
        lines.append('')

    # ── EERR DIVISA REAL ─────────────────────────────────────────────────────
    if tipo in ['eerr_divisa', 'completo']:
        lines.append('## ESTADO DE RESULTADOS — DIVISA REAL')
        lines.append('')
        from engine import _calcular_eerr_divisa_real
        data_dr = _calcular_eerr_divisa_real(db, year, unit, empresa_id=empresa_id)
        rows_dr = data_dr.get('rows', [])

        meses_disponibles_dr = []
        if rows_dr:
            meses_disponibles_dr = [m['month'] for m in rows_dr[0].get('meses', [])]
            if month:
                meses_disponibles_dr = [m for m in meses_disponibles_dr if m == month.upper()]

        header_dr = '| Partida | ' + ' | '.join(meses_disponibles_dr) + ' | ACUM |' if meses_disponibles_dr else '| Partida | ACUM |'
        separator_dr = '|---' * (len(meses_disponibles_dr) + 2) + '|'
        lines.append(header_dr)
        lines.append(separator_dr)

        for row in rows_dr:
            partida = row.get('partida', '')
            prefix = '**' if row.get('bold') else ''
            suffix = '**' if row.get('bold') else ''
            meses_data = {m['month']: m.get('ejecutado', {}).get('valor', 0) for m in row.get('meses', [])}

            if meses_disponibles_dr:
                valores = ' | '.join(f"{meses_data.get(m, 0):,.0f}" for m in meses_disponibles_dr)
                acum = sum(m.get('ejecutado', {}).get('valor', 0) for m in row.get('meses', []))
                lines.append(f"| {prefix}{partida}{suffix} | {valores} | {acum:,.0f} |")
            else:
                acum = sum(m.get('ejecutado', {}).get('valor', 0) for m in row.get('meses', []))
                lines.append(f"| {prefix}{partida}{suffix} | {acum:,.0f} |")

        lines.append('')
        lines.append('---')
        lines.append('')

    # ── ESF ───────────────────────────────────────────────────────────────────
    if tipo in ['esf', 'completo']:
        lines.append('## ESTADO DE SITUACIÓN FINANCIERA')
        lines.append('')
        from engine import compute_esf
        result_quarters, quarters_available = compute_esf(db, year, unit, empresa_id=empresa_id)

        for q in quarters_available:
            lines.append(f"### Q{q}")
            totales = result_quarters[q]['totales']
            claves = [
                'ACTIVOS CORRIENTES', 'Total Activos No Corrientes', 'TOTAL ACTIVOS',
                'TOTAL PASIVOS CORRIENTES', 'TOTAL PASIVOS NO CORRIENTES', 'TOTAL PASIVOS',
                'TOTAL PATRIMONIO', 'TOTAL PASIVOS Y PATRIMONIO'
            ]
            lines.append('| Partida | Valor |')
            lines.append('|---|---|')
            for clave in claves:
                val = totales.get(clave, 0)
                lines.append(f"| {clave} | {val:,.0f} |")
            lines.append('')

    # ── ESF DIVISA REAL ─────────────────────────────────────────────────────
    if tipo in ['esf_divisa', 'completo']:
        lines.append('## ESTADO DE SITUACIÓN FINANCIERA — DIVISA REAL')
        lines.append('')
        if not quarter:
            lines.append('_No se especificó trimestre; sección omitida._')
            lines.append('')
        else:
            from engine import calcular_esf_divisa_real
            result_dr = calcular_esf_divisa_real(year, quarter, empresa_id=empresa_id, db=db)
            if 'error' in result_dr:
                lines.append(f"_{result_dr['error']}_")
                lines.append('')
            else:
                lines.append(f"**Trimestre:** Q{quarter} | **Tasa paralela fin de mes:** {result_dr['tasa_paralela_fin']}")
                lines.append('')
                lines.append('| Partida | Bs |')
                lines.append('|---|---|')
                for k, v in result_dr['partidas'].items():
                    lines.append(f"| {k} | {v:,.2f} |")
                lines.append(f"| **Saldo Total** | **{result_dr['saldo_total_bs']:,.2f}** |")
                lines.append('')
                usd_txt = f"{result_dr['saldo_total_usd']:,.2f}" if result_dr['saldo_total_usd'] is not None else "N/D"
                lines.append(f"**Saldo Total USD (paralelo):** {usd_txt}")
                lines.append('')
        lines.append('---')
        lines.append('')

    # ── COMPARATIVA POR UNIDAD ────────────────────────────────────────────────
    if tipo in ('comparativa', 'comparativa_divisa'):
        # Bug encontrado en auditoría: esta sección siempre usaba el adaptador BCV
        # (eerr_completo_v2_ui_adapter), incluso cuando el modo elegido era Divisa
        # Real -- el prompt cambiaba pero los números seguían siendo BCV. Corregido:
        # ahora usa el motor correcto según el tipo.
        es_comparativa_divisa = (tipo == 'comparativa_divisa')
        if es_comparativa_divisa:
            from engine import _calcular_eerr_divisa_real
        else:
            from engine import eerr_completo_v2_ui_adapter
        empresa_id_comp = request.args.get('empresa_id', type=int) if request.method == 'GET' else data.get('empresa_id')
        # Ucafe excluida: es venta de café, negocio distinto al resto (retail) — no es comparable, decisión de negocio.
        if empresa_id_comp is not None:
            rows_unidades = db.execute('SELECT nombre FROM unidades WHERE empresa_id=? AND nombre != ?', [empresa_id_comp, 'Ucafe']).fetchall()
            UNIDADES_COMPARABLES = {r[0] for r in rows_unidades}
        else:
            UNIDADES_COMPARABLES = {r[0] for r in db.execute('SELECT nombre FROM unidades WHERE nombre != ?', ['Ucafe']).fetchall()}

        if request.method == 'POST':
            units = data.get('units') or []
        else:
            units = request.args.getlist('units')

        units = [u for u in units if u in UNIDADES_COMPARABLES]
        units = list(dict.fromkeys(units))

        if len(units) < 2:
            return jsonify({'error': 'Selecciona al menos 2 unidades válidas para comparar'}), 400

        lines.append('## COMPARATIVA DE UNIDADES OPERATIVAS' + (' — DIVISA REAL' if es_comparativa_divisa else ''))
        lines.append('')
        lines.append('| Unidad | Ingresos | Costos | Gastos Operacionales | Otros | Utilidad Neta | Margen Bruto | Margen Neto |')
        lines.append('|---|---|---|---|---|---|---|---|')

        for u in units:
            if es_comparativa_divisa:
                data_u = _calcular_eerr_divisa_real(db, year, u, empresa_id=empresa_id_comp)
            else:
                data_u = eerr_completo_v2_ui_adapter(db, year, u)
            rows_u = data_u.get('rows', [])

            def valor_partida(nombre_partida):
                for row in rows_u:
                    if row.get('partida', '').strip() == nombre_partida:
                        if month:
                            for m in row.get('meses', []):
                                if m['month'] == month.upper():
                                    return m.get('ejecutado', {}).get('valor', 0)
                            return 0
                        else:
                            return sum(m.get('ejecutado', {}).get('valor', 0) for m in row.get('meses', []))
                return 0

            i = valor_partida('Total Ingresos')
            c = valor_partida('Total Costo de Ventas')
            ub = valor_partida('Utilidad Bruta')
            g = valor_partida('Total Gastos Operacionales')
            un = valor_partida('Utilidad Neta')
            otros = ub - g - un

            mb = (ub / i * 100) if i else 0
            mn = (un / i * 100) if i else 0

            lines.append(f"| {u} | {i:,.2f} | {c:,.2f} | {g:,.2f} | {otros:,.2f} | {un:,.2f} | {mb:.1f}% | {mn:.1f}% |")

        lines.append('')
        lines.append('---')
        lines.append('')

    # ── Entrega ────────────────────────────────────────────────────────────────
    contenido = '\n'.join(lines)
    nombre = f"ultrax_briefing_{alcance.replace(' ','_')}_{periodo.replace(' ','_')}.md"

    return Response(
        contenido,
        mimetype='text/markdown',
        headers={'Content-Disposition': f'attachment; filename="{nombre}"'}
    )
