from flask import Blueprint, request, jsonify
from auth import admin_required
from db import get_db

mapeo_bp = Blueprint('mapeo', __name__)


@mapeo_bp.route('/api/mapping/unmapped', methods=['GET'])
def get_unmapped_accounts():
    """
    Retorna cuentas que existen en financials/esf_data pero NO en mapping.
    Útil para detectar cuentas que se auto-mapearon o que faltan.
    """
    db = get_db()

    # Cuentas únicas en financials
    fin_partidas = set(r['partida'] for r in db.execute('SELECT DISTINCT partida FROM financials').fetchall())

    # Cuentas únicas en esf_data
    esf_partidas = set(r['partida'] for r in db.execute('SELECT DISTINCT partida FROM esf_data').fetchall())

    # Cuentas únicas en mapping
    mapped_partidas = set(r['partida'] for r in db.execute('SELECT DISTINCT partida FROM mapping').fetchall())

    # Diferencias
    unmapped_fin = fin_partidas - mapped_partidas
    unmapped_esf = esf_partidas - mapped_partidas

    # Obtener detalles de las partidas sin mapear
    result = {
        'financials_unmapped': sorted(list(unmapped_fin)),
        'esf_unmapped': sorted(list(unmapped_esf)),
        'total_unmapped': len(unmapped_fin) + len(unmapped_esf),
        'total_in_financials': len(fin_partidas),
        'total_in_esf': len(esf_partidas),
        'total_in_mapping': len(mapped_partidas)
    }

    return jsonify(result)


@mapeo_bp.route('/api/mapping', methods=['GET'])
def get_mapping():
    db = get_db()
    return jsonify([dict(r) for r in db.execute('SELECT * FROM mapping ORDER BY odoo_code').fetchall()])


@mapeo_bp.route('/api/mapping', methods=['POST'])
@admin_required
def add_mapping():
    d  = request.json
    db = get_db()
    try:
        db.execute(
            'INSERT OR REPLACE INTO mapping (odoo_code, odoo_name, partida, sign, income_type) VALUES (?,?,?,?,?)',
            (d['odoo_code'], d['odoo_name'], d['partida'], d.get('sign', 1), d.get('income_type'))
        )
        db.execute(
            'INSERT INTO mapping_log (action, odoo_code, odoo_name, partida, sign, income_type) VALUES (?,?,?,?,?,?)',
            ('INSERT', d['odoo_code'], d['odoo_name'], d['partida'], d.get('sign', 1), d.get('income_type'))
        )
        # Update or Insert mapping_groups_v2 if group_name is provided
        group_name = d.get('group_name')
        if group_name:
            exist = db.execute('SELECT 1 FROM mapping_groups_v2 WHERE odoo_code = ?', (d['odoo_code'],)).fetchone()
            if exist:
                db.execute(
                    'UPDATE mapping_groups_v2 SET group_name = ? WHERE odoo_code = ?',
                    (group_name, d['odoo_code'])
                )
            else:
                db.execute(
                    'INSERT INTO mapping_groups_v2 (group_name, odoo_code, report_type, display_order) VALUES (?, ?, ?, ?)',
                    (group_name, d['odoo_code'], 'eerr', 100)
                )
        db.commit()
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mapeo_bp.route('/api/mapping/grupo', methods=['GET'])
def get_mapping_grupo():
    code = request.args.get('code', '')
    if not code:
        return jsonify({'group_name': None})
    db = get_db()
    row = db.execute('SELECT group_name FROM mapping_groups_v2 WHERE odoo_code = ?', (code,)).fetchone()
    return jsonify({'group_name': row['group_name'] if row else None})


@mapeo_bp.route('/api/mapping/sin-clasificar', methods=['GET'])
def get_mapping_sin_clasificar():
    from engine import EERR_STRUCTURE
    eerr_leaves = set(item[0].lower().strip() for item in EERR_STRUCTURE if not item[1])
    db = get_db()
    rows = db.execute('''
        SELECT m.odoo_code, m.odoo_name, m.partida, m.sign, m.income_type
        FROM mapping m
        LEFT JOIN mapping_groups_v2 mg ON m.odoo_code = mg.odoo_code
        WHERE (m.odoo_code LIKE '4%' OR m.odoo_code LIKE '5%' OR m.odoo_code LIKE '6%')
          AND mg.odoo_code IS NULL
          AND (length(m.odoo_code) - length(replace(m.odoo_code, '.', ''))) = 4
    ''').fetchall()
    
    unclassified = []
    for r in rows:
        partida = r['partida'].lower().strip()
        if partida in eerr_leaves:
            unclassified.append(dict(r))
            
    return jsonify({
        'count': len(unclassified),
        'accounts': unclassified
    })


@mapeo_bp.route('/api/mapping/sin-clasificar-esf', methods=['GET'])
def get_mapping_sin_clasificar_esf():
    from engine import ESF_STRUCTURE_V2
    esf_leaves = set(item[0].lower().strip() for item in ESF_STRUCTURE_V2 if not item[1])
    db = get_db()
    rows = db.execute('''
        SELECT m.odoo_code, m.odoo_name, m.partida, m.sign, m.income_type
        FROM mapping m
        LEFT JOIN mapping_groups_v2 mg ON m.odoo_code = mg.odoo_code
            AND mg.report_type = 'esf'
        WHERE (m.odoo_code LIKE '1%' OR m.odoo_code LIKE '2%' OR m.odoo_code LIKE '3%')
          AND mg.odoo_code IS NULL
          AND (length(m.odoo_code) - length(replace(m.odoo_code, '.', ''))) = 4
    ''').fetchall()
    unclassified = []
    for r in rows:
        partida = r['partida'].lower().strip()
        if partida in esf_leaves:
            unclassified.append(dict(r))
    return jsonify({
        'count': len(unclassified),
        'accounts': unclassified
    })


@mapeo_bp.route('/api/mapping/<code>', methods=['DELETE'])
@admin_required
def delete_mapping(code):
    db  = get_db()
    row = db.execute('SELECT * FROM mapping WHERE odoo_code=?', (code,)).fetchone()
    if row:
        db.execute(
            'INSERT INTO mapping_log (action, odoo_code, odoo_name, partida, sign, income_type) VALUES (?,?,?,?,?,?)',
            ('DELETE', row['odoo_code'], row['odoo_name'], row['partida'], row['sign'], row['income_type'])
        )
    db.execute('DELETE FROM mapping WHERE odoo_code=?', (code,))
    db.commit()
    return jsonify({'ok': True})


@mapeo_bp.route('/api/mapping/log', methods=['GET'])
def mapping_log():
    db = get_db()
    return jsonify([dict(r) for r in db.execute('SELECT * FROM mapping_log ORDER BY id DESC LIMIT 200').fetchall()])


@mapeo_bp.route('/api/mapping/log/<int:lid>/restore', methods=['POST'])
@admin_required
def restore_mapping_log(lid):
    db    = get_db()
    entry = db.execute('SELECT * FROM mapping_log WHERE id=?', (lid,)).fetchone()
    if not entry:                        return jsonify({'error': 'No encontrado'}), 404
    if entry['action'] != 'DELETE':      return jsonify({'error': 'Solo se pueden restaurar eliminaciones'}), 400
    db.execute(
        'INSERT OR IGNORE INTO mapping (odoo_code, odoo_name, partida, sign, income_type) VALUES (?,?,?,?,?)',
        (entry['odoo_code'], entry['odoo_name'], entry['partida'], entry['sign'], entry['income_type'])
    )
    db.commit()
    return jsonify({'ok': True})


@mapeo_bp.route('/api/mapping/reset', methods=['POST'])
@admin_required
def reset_mapping_endpoint():
    """
    Endpoint para ejecutar reset_mapping() desde la UI.
    ⚠️  ADVERTENCIA: Borra y recrea toda la tabla mapping.
    """
    from db import reset_mapping
    result = reset_mapping()
    return jsonify(result)

