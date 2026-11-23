from flask import Blueprint, jsonify, request, session
from audit import registrar_auditoria
from auth import admin_required
from db import get_db

sistema_empresas_bp = Blueprint('sistema_empresas', __name__)


def _to_flag(val):
    return 1 if bool(val) else 0


@sistema_empresas_bp.route('/api/sistema/empresas', methods=['GET'])
@admin_required
def listar_empresas():
    """Lista todas las empresas y sus unidades para administración del sistema."""
    db = get_db()
    units_con_datos = {
        r[0] for r in db.execute(
            'SELECT DISTINCT unit FROM financials '
            'UNION '
            'SELECT DISTINCT unit FROM financials_detail'
        ).fetchall()
    }
    empresas_rows = db.execute(
        'SELECT id, nombre_corto, nombre_legal, color, activo FROM empresas ORDER BY id'
    ).fetchall()
    unidades_rows = db.execute(
        'SELECT id, nombre, empresa_id, activo, es_pseudo, excluir_comparativas, recibe_plug_divisa '
        'FROM unidades ORDER BY id'
    ).fetchall()

    unidades_por_emp = {}
    for u in unidades_rows:
        unidades_por_emp.setdefault(u['empresa_id'], []).append({
            'id': u['id'],
            'nombre': u['nombre'],
            'activo': u['activo'],
            'es_pseudo': u['es_pseudo'],
            'excluir_comparativas': u['excluir_comparativas'],
            'recibe_plug_divisa': u['recibe_plug_divisa'],
            'tiene_datos': u['nombre'] in units_con_datos,
        })

    res = []
    for e in empresas_rows:
        unis = unidades_por_emp.get(e['id'], [])
        res.append({
            'id': e['id'],
            'nombre_corto': e['nombre_corto'],
            'nombre_legal': e['nombre_legal'],
            'color': e['color'],
            'activo': e['activo'],
            'protegida': e['id'] == 1,
            'unidades_activas': sum(1 for u in unis if u['activo']),
            'unidades_total': len(unis),
            'unidades': unis,
        })
    return jsonify(res)


@sistema_empresas_bp.route('/api/sistema/empresas', methods=['POST'])
@admin_required
def crear_empresa():
    """Crea una nueva empresa y opcionalmente su unidad única asociada."""
    data = request.get_json(silent=True) or {}
    nombre_corto = (data.get('nombre_corto') or '').strip()
    nombre_legal = (data.get('nombre_legal') or '').strip()
    unidad_unica = bool(data.get('unidad_unica'))

    if not nombre_corto or not nombre_legal:
        return jsonify({'error': 'nombre_corto y nombre_legal son obligatorios'}), 400

    db = get_db()
    dup_emp = db.execute(
        'SELECT id FROM empresas WHERE LOWER(nombre_corto) = LOWER(?)',
        (nombre_corto,),
    ).fetchone()
    if dup_emp:
        return jsonify({'error': 'Ya existe una empresa con ese nombre corto'}), 409

    if unidad_unica:
        dup_uni = db.execute(
            'SELECT id FROM unidades WHERE LOWER(nombre) = LOWER(?)',
            (nombre_corto,),
        ).fetchone()
        if dup_uni:
            return jsonify({'error': 'Ya existe una unidad con ese nombre'}), 409

    cur = db.execute(
        'INSERT INTO empresas (nombre_corto, nombre_legal, color, activo) VALUES (?, ?, ?, ?)',
        (nombre_corto, nombre_legal, 'var(--blue)', 1),
    )
    new_id = cur.lastrowid
    if unidad_unica:
        db.execute(
            'INSERT INTO unidades (nombre, empresa_id, activo, es_pseudo) VALUES (?, ?, ?, ?)',
            (nombre_corto, new_id, 1, 1),
        )
    db.commit()
    registrar_auditoria(
        db,
        session.get('username', 'sistema'),
        'empresas',
        'crear_empresa',
        f'id={new_id}, nombre_corto={nombre_corto}, unidad_unica={unidad_unica}',
    )

    return jsonify({
        'id': new_id,
        'nombre_corto': nombre_corto,
        'nombre_legal': nombre_legal,
        'color': 'var(--blue)',
        'activo': 1,
    }), 201


@sistema_empresas_bp.route('/api/sistema/empresas/<int:empresa_id>', methods=['PUT'])
@admin_required
def actualizar_empresa(empresa_id):
    """Actualiza nombre_corto y nombre_legal de una empresa (excepto Holding)."""
    if empresa_id == 1:
        return jsonify({'error': 'Holding no editable'}), 403

    db = get_db()
    emp = db.execute(
        'SELECT id, color, activo FROM empresas WHERE id = ?', (empresa_id,)
    ).fetchone()
    if not emp:
        return jsonify({'error': 'Empresa no encontrada'}), 404

    data = request.get_json(silent=True) or {}
    nombre_corto = (data.get('nombre_corto') or '').strip()
    nombre_legal = (data.get('nombre_legal') or '').strip()
    if not nombre_corto or not nombre_legal:
        return jsonify({'error': 'nombre_corto y nombre_legal son obligatorios'}), 400

    dup = db.execute(
        'SELECT id FROM empresas WHERE LOWER(nombre_corto) = LOWER(?) AND id != ?',
        (nombre_corto, empresa_id),
    ).fetchone()
    if dup:
        return jsonify({'error': 'Ya existe otra empresa con ese nombre corto'}), 409

    db.execute(
        'UPDATE empresas SET nombre_corto = ?, nombre_legal = ? WHERE id = ?',
        (nombre_corto, nombre_legal, empresa_id),
    )
    db.commit()
    registrar_auditoria(
        db,
        session.get('username', 'sistema'),
        'empresas',
        'editar_empresa',
        f'id={empresa_id}, nombre_corto={nombre_corto}',
    )
    return jsonify({
        'id': empresa_id,
        'nombre_corto': nombre_corto,
        'nombre_legal': nombre_legal,
        'color': emp['color'],
        'activo': emp['activo'],
    }), 200


@sistema_empresas_bp.route('/api/sistema/empresas/<int:empresa_id>/toggle', methods=['POST'])
@admin_required
def toggle_empresa(empresa_id):
    """Activa o desactiva una empresa; al desactivar, desactiva sus unidades."""
    if empresa_id == 1:
        return jsonify({'error': 'Holding no editable'}), 403

    db = get_db()
    emp = db.execute(
        'SELECT id, activo FROM empresas WHERE id = ?', (empresa_id,)
    ).fetchone()
    if not emp:
        return jsonify({'error': 'Empresa no encontrada'}), 404

    nuevo_activo = 0 if emp['activo'] else 1
    db.execute('UPDATE empresas SET activo = ? WHERE id = ?', (nuevo_activo, empresa_id))
    if nuevo_activo == 0:
        db.execute('UPDATE unidades SET activo = 0 WHERE empresa_id = ?', (empresa_id,))
    db.commit()
    registrar_auditoria(
        db,
        session.get('username', 'sistema'),
        'empresas',
        'toggle_empresa',
        f'id={empresa_id}, activo={nuevo_activo}',
    )
    return jsonify({'id': empresa_id, 'activo': nuevo_activo}), 200


@sistema_empresas_bp.route('/api/sistema/unidades', methods=['POST'])
@admin_required
def crear_unidad():
    """Crea una nueva unidad de negocio asociada a una empresa activa."""
    data = request.get_json(silent=True) or {}
    empresa_id = data.get('empresa_id')
    nombre = (data.get('nombre') or '').strip()
    es_pseudo = _to_flag(data.get('es_pseudo'))
    excluir_comparativas = _to_flag(data.get('excluir_comparativas'))
    recibe_plug_divisa = _to_flag(data.get('recibe_plug_divisa'))

    if empresa_id == 1:
        return jsonify({'error': 'No se pueden agregar unidades al Holding'}), 403

    db = get_db()
    emp = db.execute(
        'SELECT id, activo FROM empresas WHERE id = ?', (empresa_id,)
    ).fetchone()
    if not emp:
        return jsonify({'error': 'Empresa no encontrada'}), 404
    if not emp['activo']:
        return jsonify({'error': 'La empresa está inactiva'}), 400

    if not nombre:
        return jsonify({'error': 'El nombre de la unidad es obligatorio'}), 400

    dup = db.execute(
        'SELECT id FROM unidades WHERE LOWER(nombre) = LOWER(?)',
        (nombre,),
    ).fetchone()
    if dup:
        return jsonify({'error': 'Ya existe una unidad con ese nombre'}), 409

    cur = db.execute(
        'INSERT INTO unidades (nombre, empresa_id, activo, es_pseudo, excluir_comparativas, recibe_plug_divisa) '
        'VALUES (?, ?, 1, ?, ?, ?)',
        (nombre, empresa_id, es_pseudo, excluir_comparativas, recibe_plug_divisa),
    )
    db.commit()
    registrar_auditoria(
        db,
        session.get('username', 'sistema'),
        'empresas',
        'crear_unidad',
        f'empresa_id={empresa_id}, nombre={nombre}',
    )
    return jsonify({
        'id': cur.lastrowid,
        'nombre': nombre,
        'empresa_id': empresa_id,
        'activo': 1,
        'es_pseudo': es_pseudo,
        'excluir_comparativas': excluir_comparativas,
        'recibe_plug_divisa': recibe_plug_divisa,
    }), 201


@sistema_empresas_bp.route('/api/sistema/unidades/<int:unidad_id>', methods=['PUT'])
@admin_required
def actualizar_unidad(unidad_id):
    """Actualiza una unidad; bloquea renombrado si ya tiene datos contables."""
    db = get_db()
    uni = db.execute(
        'SELECT id, nombre, empresa_id, activo FROM unidades WHERE id = ?',
        (unidad_id,),
    ).fetchone()
    if not uni:
        return jsonify({'error': 'Unidad no encontrada'}), 404

    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombre') or '').strip()
    if not nombre:
        return jsonify({'error': 'El nombre de la unidad es obligatorio'}), 400

    nombre_actual = uni['nombre']
    if nombre != nombre_actual:
        dup = db.execute(
            'SELECT id FROM unidades WHERE LOWER(nombre) = LOWER(?) AND id != ?',
            (nombre, unidad_id),
        ).fetchone()
        if dup:
            return jsonify({'error': 'Ya existe otra unidad con ese nombre'}), 409

        tiene_fin = db.execute(
            'SELECT 1 FROM financials WHERE unit = ? LIMIT 1', (nombre_actual,)
        ).fetchone()
        tiene_det = db.execute(
            'SELECT 1 FROM financials_detail WHERE unit = ? LIMIT 1', (nombre_actual,)
        ).fetchone()
        if tiene_fin or tiene_det:
            return jsonify({'error': 'No se puede renombrar: la unidad ya tiene datos contables cargados'}), 409

    es_pseudo = _to_flag(data.get('es_pseudo'))
    excluir_comparativas = _to_flag(data.get('excluir_comparativas'))
    recibe_plug_divisa = _to_flag(data.get('recibe_plug_divisa'))

    db.execute(
        'UPDATE unidades SET nombre = ?, es_pseudo = ?, excluir_comparativas = ?, recibe_plug_divisa = ? WHERE id = ?',
        (nombre, es_pseudo, excluir_comparativas, recibe_plug_divisa, unidad_id),
    )
    db.commit()
    registrar_auditoria(
        db,
        session.get('username', 'sistema'),
        'empresas',
        'editar_unidad',
        f'id={unidad_id}, nombre={nombre}',
    )
    return jsonify({
        'id': unidad_id,
        'nombre': nombre,
        'empresa_id': uni['empresa_id'],
        'activo': uni['activo'],
        'es_pseudo': es_pseudo,
        'excluir_comparativas': excluir_comparativas,
        'recibe_plug_divisa': recibe_plug_divisa,
    }), 200


@sistema_empresas_bp.route('/api/sistema/unidades/<int:unidad_id>/toggle', methods=['POST'])
@admin_required
def toggle_unidad(unidad_id):
    """Activa o desactiva una unidad; impide activarla si su empresa está inactiva."""
    db = get_db()
    uni = db.execute(
        'SELECT u.id, u.activo, e.activo AS empresa_activo '
        'FROM unidades u JOIN empresas e ON e.id = u.empresa_id '
        'WHERE u.id = ?',
        (unidad_id,),
    ).fetchone()
    if not uni:
        return jsonify({'error': 'Unidad no encontrada'}), 404

    nuevo_activo = 0 if uni['activo'] else 1
    if nuevo_activo == 1 and not uni['empresa_activo']:
        return jsonify({'error': 'Active primero la empresa'}), 400

    db.execute('UPDATE unidades SET activo = ? WHERE id = ?', (nuevo_activo, unidad_id))
    db.commit()
    registrar_auditoria(
        db,
        session.get('username', 'sistema'),
        'empresas',
        'toggle_unidad',
        f'id={unidad_id}, activo={nuevo_activo}',
    )
    return jsonify({'id': unidad_id, 'activo': nuevo_activo}), 200
