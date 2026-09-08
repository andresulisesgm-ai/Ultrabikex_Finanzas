from flask import Blueprint, jsonify, request
from constants import MONTHS
from helpers import get_clasificacion
from datetime import datetime
from db import get_db
from auth import admin_required

eerr_bp = Blueprint('eerr', __name__)


@eerr_bp.route('/api/eerr/grupos', methods=['GET'])
def get_eerr_grupos():
    from engine import EERR_STRUCTURE
    grupos = []
    for item in EERR_STRUCTURE:
        name = item[0]
        level = item[5] if len(item) > 5 else (0 if item[1] else 3)
        if level in (1, 2, 3):
            clean = name
            if level == 1:
                if clean.startswith("Subtotal "):
                    clean = clean[len("Subtotal "):]
                label = clean
            elif level == 2:
                if clean.startswith("Gastos de "):
                    clean = clean[len("Gastos de "):]
                elif clean.startswith("Ingresos por "):
                    clean = clean[len("Ingresos por "):]
                elif clean.startswith("Costos de "):
                    clean = clean[len("Costos de "):]
                clean = clean[0].upper() + clean[1:] if clean else clean
                label = "  → " + clean
            elif level == 3:
                if clean.startswith("Gastos de "):
                    clean = clean[len("Gastos de "):]
                elif clean.startswith("Ingresos por "):
                    clean = clean[len("Ingresos por "):]
                elif clean.startswith("Costos de "):
                    clean = clean[len("Costos de "):]
                clean = clean[0].upper() + clean[1:] if clean else clean
                label = "    → " + clean
            else:
                label = clean
            grupos.append({
                "nombre": name,
                "nivel": level,
                "label": label
            })
    return jsonify(grupos)


@eerr_bp.route('/api/eerr_nodes/overrides', methods=['GET'])
def get_eerr_nodes_overrides():
    from engine import EERR_STRUCTURE, build_effective_structure
    db = get_db()
    rows = db.execute('SELECT partida_name, target_subtotal FROM eerr_nodes').fetchall()
    overrides_list = [dict(r) for r in rows]

    effective = build_effective_structure(EERR_STRUCTURE, db_overrides=[])
    movable_partidas = []
    for node in effective:
        if node['movible'] == 'libre' and not node['is_header']:
            movable_partidas.append({
                'partida_name': node['partida_name'],
                'original_subtotal': node['parent_name']
            })

    return jsonify({
        'movable_partidas': movable_partidas,
        'overrides': overrides_list
    })

@eerr_bp.route('/api/eerr_nodes/overrides', methods=['POST'])
@admin_required
def save_eerr_nodes_overrides():
    d = request.json
    partida_name = d.get('partida_name')
    target_subtotal = d.get('target_subtotal')
    if not partida_name or not target_subtotal:
        return jsonify({'error': 'Faltan parámetros'}), 400
    db = get_db()
    if target_subtotal == 'original':
        db.execute('DELETE FROM eerr_nodes WHERE partida_name = ?', (partida_name,))
    else:
        exist = db.execute('SELECT 1 FROM eerr_nodes WHERE partida_name = ?', (partida_name,)).fetchone()
        if exist:
            db.execute(
                'UPDATE eerr_nodes SET target_subtotal = ? WHERE partida_name = ?',
                (target_subtotal, partida_name)
            )
        else:
            db.execute(
                'INSERT INTO eerr_nodes (partida_name, target_subtotal, nombre, nivel, tipo) VALUES (?, ?, ?, 0, "hoja")',
                (partida_name, target_subtotal, partida_name)
            )
    db.commit()
    return jsonify({'ok': True})


def get_clasificacion_by_type(db):
    """Retorna partidas agrupadas por income_type para el EERR detallado."""
    rows = db.execute(
        "SELECT partida, income_type, odoo_code FROM mapping WHERE income_type IS NOT NULL"
    ).fetchall()
    by_type = {'mercancia_taller': {'ing': set(), 'cos': set()},
               'servicios':        {'ing': set(), 'cos': set()},
               'eventos':          {'ing': set(), 'cos': set()}}
    for r in rows:
        t = r['income_type']
        if t not in by_type:
            continue
        code = r['odoo_code']
        if code.startswith('4.'):
            by_type[t]['ing'].add(r['partida'])
        elif code.startswith('5.'):
            by_type[t]['cos'].add(r['partida'])
    return by_type


@eerr_bp.route('/api/eerr/detalle', methods=['GET'])
def eerr_detalle():
    """
    EERR con desglose por tipo de ingreso (mercancia_taller, servicios, eventos),
    columna ACUM EJEC y %VAR mes a mes.
    Parámetros: year, unit (opcional), month_from, month_to (opcionales para filtrar rango)
    """
    year       = request.args.get('year', str(datetime.now().year))
    unit       = request.args.get('unit', '')
    month_from = request.args.get('month_from', '')
    month_to   = request.args.get('month_to', '')
    db         = get_db()

    if month_from and month_to and month_from in MONTHS and month_to in MONTHS:
        fi = MONTHS.index(month_from); ti = MONTHS.index(month_to)
        active_months = MONTHS[fi:ti+1] if fi <= ti else MONTHS[fi:] + MONTHS[:ti+1]
    else:
        active_months = MONTHS

    uc = "AND unit=?" if unit else ''
    ph_m = ','.join('?' * len(active_months))
    params = [year] + ([unit] if unit else []) + active_months

    rows = db.execute(
        f'''SELECT partida, month, SUM(amount) amount
            FROM financials
            WHERE year=? {uc} AND month IN ({ph_m})
            GROUP BY partida, month''',
        params
    ).fetchall()

    by_partida = {}
    for r in rows:
        by_partida.setdefault(r['partida'], {})[r['month']] = r['amount']

    by_type = get_clasificacion_by_type(db)
    ing_p, cos_p, gas_p = get_clasificacion(db)

    def sum_type(type_key, flow):
        partidas = by_type.get(type_key, {}).get(flow, set())
        result   = {}
        for m in active_months:
            result[m] = sum(by_partida.get(p, {}).get(m, 0) for p in partidas)
        return result

    def sum_partidas(partidas):
        result = {}
        for m in active_months:
            result[m] = sum(by_partida.get(p, {}).get(m, 0) for p in partidas)
        return result

    def acum(monthly_dict):
        return sum(monthly_dict.values())

    def var_pct(monthly_dict):
        vals = [monthly_dict.get(m, 0) for m in active_months]
        result = []
        for i, v in enumerate(vals):
            if i == 0 or vals[i-1] == 0:
                result.append(None)
            else:
                result.append(round((v - vals[i-1]) / abs(vals[i-1]) * 100, 1))
        return result

    ing_mt  = sum_type('mercancia_taller', 'ing')
    ing_svc = sum_type('servicios', 'ing')
    ing_evt = sum_type('eventos', 'ing')
    ing_tot = sum_partidas(ing_p)

    cos_mt  = sum_type('mercancia_taller', 'cos')
    cos_svc = sum_type('servicios', 'cos')
    cos_evt = sum_type('eventos', 'cos')
    cos_tot = sum_partidas(cos_p)

    def diff_monthly(a, b):
        return {m: a.get(m, 0) - b.get(m, 0) for m in active_months}

    ub_mt  = diff_monthly(ing_mt,  cos_mt)
    ub_svc = diff_monthly(ing_svc, cos_svc)
    ub_evt = diff_monthly(ing_evt, cos_evt)
    ub_tot = diff_monthly(ing_tot, cos_tot)

    gas_tot = sum_partidas(gas_p)
    un_tot  = {m: ing_tot.get(m, 0) - cos_tot.get(m, 0) - gas_tot.get(m, 0) for m in active_months}

    def build_row(label, monthly):
        return {
            'partida': label,
            'meses':   {m: round(monthly.get(m, 0), 2) for m in active_months},
            'acum':    round(acum(monthly), 2),
            'var_pct': var_pct(monthly)
        }

    gas_detail = []
    for p in sorted(gas_p):
        monthly = {m: by_partida.get(p, {}).get(m, 0) for m in active_months}
        if acum(monthly) != 0:
            gas_detail.append(build_row(p, monthly))

    return jsonify({
        'year': year, 'unit': unit, 'months': active_months,
        'ingresos': {
            'total':           build_row('Total Ingresos', ing_tot),
            'mercancia_taller':build_row('Mercancía y Taller', ing_mt),
            'servicios':       build_row('Servicios', ing_svc),
            'eventos':         build_row('Eventos', ing_evt),
        },
        'costos': {
            'total':           build_row('Total Costos', cos_tot),
            'mercancia_taller':build_row('Costo Mercancía y Taller', cos_mt),
            'servicios':       build_row('Costo Servicios', cos_svc),
            'eventos':         build_row('Costo Eventos', cos_evt),
        },
        'utilidad_bruta': {
            'total':           build_row('Utilidad Bruta', ub_tot),
            'mercancia_taller':build_row('UB Mercancía y Taller', ub_mt),
            'servicios':       build_row('UB Servicios', ub_svc),
            'eventos':         build_row('UB Eventos', ub_evt),
        },
        'gastos': {
            'total':  build_row('Total Gastos', gas_tot),
            'detalle':gas_detail,
        },
        'utilidad_neta': build_row('Utilidad Neta', un_tot),
    })


def validate_eerr_v2_integrity(year, unit, adapter_output, db, empresa_id=None):
    """
    Guarda de integridad para EERR V2 y el adaptador V1.
    Realiza validaciones de coherencia financiera y de contrato de interfaz,
    registrando cualquier desviación de forma no bloqueante.
    """
    import logging
    logger = logging.getLogger('eerr_v2_integrity_guard')

    if not logger.handlers:
        logging.basicConfig(level=logging.INFO)
        try:
            fh = logging.FileHandler('integrity_guard.log', encoding='utf-8')
            fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logger.addHandler(fh)
        except Exception:
            pass

    discrepancies = []

    from engine import EERR_STRUCTURE, build_effective_structure, SUBTOTAL_EXCLUSIONS
    db_overrides = db.execute('SELECT partida_name, target_subtotal FROM eerr_nodes').fetchall()
    effective = build_effective_structure(EERR_STRUCTURE, db_overrides=db_overrides)
    structure_with_levels = [(node['partida_name'], node['is_header'], node['level']) for node in effective]

    rows_map = {r['partida']: r for r in adapter_output['rows']}

    for i, (name, is_header, level) in enumerate(structure_with_levels):
        if is_header:
            j = i + 1
            child_leaves = []
            while j < len(structure_with_levels):
                c_name, c_is_header, c_level = structure_with_levels[j]
                if c_level <= level:
                    break
                if not c_is_header:
                    if c_name in SUBTOTAL_EXCLUSIONS.get(name, []):
                        pass
                    else:
                        child_leaves.append(c_name)
                j += 1
            if name == 'Subtotal Gastos de Comercialización y Logistica':
                child_leaves.append('Gastos de comisiones empleados')
                child_leaves.append('Gastos de comisiones por venta de personal externo')

            for m_idx, m in enumerate(MONTHS):
                sum_leaves = 0.0
                for leaf_name in child_leaves:
                    if leaf_name in rows_map:
                        sum_leaves += rows_map[leaf_name]['meses'][m_idx]['ejecutado']['valor']

                header_val = 0.0
                if name in rows_map:
                    header_val = rows_map[name]['meses'][m_idx]['ejecutado']['valor']

                if name in [
                    'Subtotal Gastos de Administración',
                    'Subtotal Gastos de Recursos Humanos',
                    'Subtotal Gastos de Comercialización y Logistica',
                    'Subtotal Gastos de Mercadeo',
                    'Gastos de TI+I',
                    'Gastos de sueldos y salarios empleados y directivos',
                    'Gastos de complementos empleados y directivos',
                    'Gastos de personal externo',
                    'Gastos de pasivos laborales vacaciones',
                    'Gastos de pasivos laborales utilidades',
                    'Gastos de pasivos laborales aportes',
                    'Gastos de pasivos laborales HCM',
                    'Gastos de salud y seguridad laboral fiestas y agasajos',
                    'Otros gastos de personal'
                ]:
                    diff = abs(header_val - sum_leaves)
                    if diff > 0.05:
                        msg = f"Discrepancia de subtotal en [{name}] para el mes {m}: Valor Header={header_val:.2f}, Suma Hojas={sum_leaves:.2f} (Diff={diff:.2f})"
                        discrepancies.append(msg)

    baseline_rows = db.execute(
        'SELECT month, partida, valor_esperado FROM validation_baselines WHERE year = ? AND unit = ?',
        [year, unit]
    ).fetchall()
    if baseline_rows:
        months_in_adapter = adapter_output['rows'][0]['meses'] if adapter_output['rows'] else []
        month_index = {m['month']: idx for idx, m in enumerate(months_in_adapter)}
        for row in baseline_rows:
            b_month = row['month']
            row_name = row['partida']
            expected_val = row['valor_esperado']
            if row_name in rows_map and b_month in month_index:
                idx = month_index[b_month]
                actual_val = rows_map[row_name]['meses'][idx]['ejecutado']['valor']
                diff = abs(actual_val - expected_val)
                if diff > 0.05:
                    msg = f"Descuadre contra baseline validado en [{row_name}] mes {b_month}: Esperado={expected_val:.2f}, Obtenido={actual_val:.2f} (Diff={diff:.2f})"
                    discrepancies.append(msg)
            elif row_name not in rows_map:
                discrepancies.append(f"Fila obligatoria de baseline [{row_name}] no encontrada en la respuesta")

    try:
        missing_mappings = db.execute('''
            SELECT DISTINCT m.partida, m.odoo_code
            FROM financials f
            JOIN (
                SELECT odoo_code, partida FROM mapping m
                WHERE NOT EXISTS (
                    SELECT 1 FROM mapping sub 
                    WHERE sub.odoo_code LIKE m.odoo_code || '.%' AND sub.odoo_code != m.odoo_code
                )
            ) m ON f.partida = m.partida
            LEFT JOIN mapping_groups_v2 mg ON m.odoo_code = mg.odoo_code
            WHERE mg.odoo_code IS NULL AND f.year = ?
        ''', [year]).fetchall()
        for r in missing_mappings:
            msg = f"Cuenta transaccional activa sin mapear en mapping_groups_v2: Partida='{r['partida']}', OdooCode='{r['odoo_code']}'"
            discrepancies.append(msg)
    except Exception as e:
        discrepancies.append(f"Error al validar cuentas sin mapear: {str(e)}")

    required_keys_always = {'type', 'month', 'ejecutado'}
    required_keys_ejecutado = {'valor', 'pct_vtas', 'pct_gastos'}

    for r in adapter_output['rows']:
        partida = r['partida']
        for m_idx, m_data in enumerate(r['meses']):
            missing_keys = required_keys_always - set(m_data.keys())
            if missing_keys:
                discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Faltan claves básicas del contrato: {missing_keys}")
                continue

            ejec = m_data['ejecutado']
            if not isinstance(ejec, dict):
                discrepancies.append(f"Fila [{partida}] mes index {m_idx}: 'ejecutado' debe ser un diccionario")
                continue
            missing_ejec = required_keys_ejecutado - set(ejec.keys())
            if missing_ejec:
                discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Faltan claves en 'ejecutado': {missing_ejec}")

            m_type = m_data['type']

            if m_type != 'A':
                if 'vari_rel' not in m_data:
                    discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Falta 'vari_rel' en mes tipo {m_type}")

                if m_type == 'E':
                    if 'anio' not in m_data:
                        discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Falta 'anio' en mes tipo E")
                    else:
                        missing_anio = required_keys_ejecutado - set(m_data['anio'].keys())
                        if missing_anio:
                            discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Faltan claves en 'anio': {missing_anio}")
                else:
                    if 'acum_ejecutado' not in m_data:
                        discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Falta 'acum_ejecutado' en mes tipo {m_type}")
                    else:
                        missing_acum = required_keys_ejecutado - set(m_data['acum_ejecutado'].keys())
                        if missing_acum:
                            discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Faltan claves en 'acum_ejecutado': {missing_acum}")

                if m_type in ('C', 'D', 'E'):
                    if 'acum_ppto' not in m_data:
                        discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Falta 'acum_ppto' en mes tipo {m_type}")
                    else:
                        missing_ppto = {'valor', 'pct_vtas'} - set(m_data['acum_ppto'].keys())
                        if missing_ppto:
                            discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Faltan claves en 'acum_ppto': {missing_ppto}")
                    if 'var_ppto' not in m_data:
                        discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Falta 'var_ppto' en mes tipo {m_type}")

                    if m_type == 'D':
                        if 'prom_6_ejec' not in m_data:
                            discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Falta 'prom_6_ejec' en mes tipo D")
                        else:
                            missing_prom_ejec = required_keys_ejecutado - set(m_data['prom_6_ejec'].keys())
                            if missing_prom_ejec:
                                discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Faltan claves en 'prom_6_ejec': {missing_prom_ejec}")
                        if 'prom_6_ppto' not in m_data:
                            discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Falta 'prom_6_ppto' en mes tipo D")
                        else:
                            missing_prom_ppto = {'valor', 'pct_vtas'} - set(m_data['prom_6_ppto'].keys())
                            if missing_prom_ppto:
                                discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Faltan claves en 'prom_6_ppto': {missing_prom_ppto}")
                        if 'var_ppto_prom' not in m_data:
                            discrepancies.append(f"Fila [{partida}] mes index {m_idx}: Falta 'var_ppto_prom' en mes tipo D")

    if discrepancies:
        logger.warning(f"--- DETECTADAS DISCREPANCIAS DE INTEGRIDAD (EERR V2) - Unidad={unit}, Empresa={empresa_id}, Año={year} ---")
        for d in discrepancies:
            logger.warning(d)
        return False, discrepancies
    else:
        logger.info(f"Integridad validada exitosamente para Unidad={unit}, Empresa={empresa_id}, Año={year}. Sin descuadres.")
        return True, []


@eerr_bp.route('/api/eerr/completo', methods=['GET'])
def eerr_completo():
    year = request.args.get('year', str(datetime.now().year))
    unit = request.args.get('unit', '')
    empresa_id = request.args.get('empresa_id', type=int) or None
    db = get_db()

    from engine import eerr_completo_v2_ui_adapter
    data = eerr_completo_v2_ui_adapter(db, year, unit, empresa_id=empresa_id)

    try:
        validate_eerr_v2_integrity(year, unit, data, db, empresa_id=empresa_id)
    except Exception as e:
        import logging
        logging.getLogger('eerr_v2_integrity_guard').error(f"Error al ejecutar validacion de integridad: {str(e)}")

    return jsonify(data)
