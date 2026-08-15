from flask import Blueprint, jsonify, request
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


@eerr_bp.route('/api/eerr', methods=['GET'])
def eerr():
    year  = request.args.get('year', str(datetime.now().year))
    unit  = request.args.get('unit', '')
    month = request.args.get('month', '')
    db    = get_db()
    uc    = "AND unit=?" if unit else ''
    mc    = "AND month=?" if month else ''
    params = [year] + ([unit] if unit else []) + ([month] if month else [])

    rows = db.execute(
        f'SELECT partida, SUM(amount) total FROM financials WHERE year=? {uc} {mc} GROUP BY partida',
        params
    ).fetchall()
    data = {r['partida']: r['total'] for r in rows}

    ing_codes = set(r['partida'] for r in db.execute("SELECT DISTINCT partida FROM mapping WHERE odoo_code LIKE '4.%'").fetchall())
    cos_codes = set(r['partida'] for r in db.execute("SELECT DISTINCT partida FROM mapping WHERE odoo_code LIKE '5.%'").fetchall())
    gas_codes = set(r['partida'] for r in db.execute("SELECT DISTINCT partida FROM mapping WHERE odoo_code LIKE '6.%'").fetchall())

    def total(codes): return sum(data.get(p, 0) for p in codes)
    tI = total(ing_codes); tC = total(cos_codes); tG = total(gas_codes)
    ub = tI - tC; un = tI - tC - tG

    detail_ing = {p: data.get(p, 0) for p in ing_codes if data.get(p, 0)}
    detail_cos = {p: data.get(p, 0) for p in cos_codes if data.get(p, 0)}
    detail_gas = {p: data.get(p, 0) for p in gas_codes if data.get(p, 0)}

    return jsonify({
        'ingresos': tI, 'costos': tC, 'gastos': tG,
        'utilidad_bruta': ub, 'utilidad_neta': un,
        'margen_bruto': round(ub / tI * 100, 1) if tI else 0,
        'margen_neto':  round(un / tI * 100, 1) if tI else 0,
        'detail_ing': detail_ing, 'detail_cos': detail_cos, 'detail_gas': detail_gas
    })
