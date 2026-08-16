from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from auth import admin_required
from db import get_db
from engine import OdooParser, MONTH_TO_QUARTER

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/api/upload', methods=['POST'])
@admin_required
def upload():
    file    = request.files.get('file')
    if file and not file.filename.lower().endswith(('.xlsx', '.xls')):
        return jsonify({'error': 'El archivo debe ser .xlsx o .xls'}), 400
    unit    = request.form.get('unit')
    month   = request.form.get('month')
    year    = request.form.get('year', str(datetime.now().year))
    is_esf  = request.form.get('is_esf', 'false').lower() == 'true'
    empresa_id = request.form.get('empresa_id', type=int) or None
    if is_esf:
        unit = 'CONSOLIDADO'
        if not empresa_id:
            return jsonify({'error': 'empresa_id es requerido para cargas de ESF'}), 400

    if not all([file, unit, month]):
        return jsonify({'error': 'Faltan parámetros'}), 400

    force = request.form.get('force', 'false').lower() == 'true'

    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    if file_size > 10 * 1024 * 1024:
        return jsonify({'error': 'El archivo excede el tamaño máximo permitido (10MB)'}), 400

    safe_filename = secure_filename(file.filename)
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], safe_filename)
    file.save(path)

    try:
        parser   = OdooParser(path)
        accounts = parser.parse()
        if not accounts:
            return jsonify({'error': 'No se reconoció ninguna cuenta en el archivo. Verifica el formato.'}), 400

        balance_count = sum(1 for code in accounts if OdooParser.is_balance_account(code))
        result_count = len(accounts) - balance_count

        if is_esf and result_count > balance_count:
            return jsonify({'error': f'El archivo parece ser un EERR (mayoría de cuentas de resultado: {result_count} vs {balance_count} de balance), pero se marcó como ESF. Verifica el archivo o la selección.'}), 400

        if not is_esf and balance_count > result_count:
            return jsonify({'error': f'El archivo parece ser un ESF (mayoría de cuentas de balance: {balance_count} vs {result_count} de resultado), pero se marcó como EERR. Verifica el archivo o la selección.'}), 400

        db = get_db()

        if not force:
            if is_esf:
                quarter_check = MONTH_TO_QUARTER.get(month, 1)
                existing = db.execute(
                    'SELECT COUNT() FROM esf_data WHERE year=? AND quarter=? AND unit=? AND empresa_id=?',
                    (year, quarter_check, 'CONSOLIDADO', empresa_id)
                ).fetchone()[0]
            else:
                existing = db.execute(
                    'SELECT COUNT() FROM financials WHERE year=? AND month=? AND unit=?',
                    (year, month, unit)
                ).fetchone()[0]
            if existing > 0:
                return jsonify({'exists': True}), 200

        inserted_fin, inserted_esf, skipped, unmapped = 0, 0, 0, []
        quarter = MONTH_TO_QUARTER.get(month, 1)

        if is_esf:
            db.execute(
                'DELETE FROM esf_data WHERE year=? AND quarter=? AND unit=? AND empresa_id=?',
                (year, quarter, unit, empresa_id)
            )
            db.execute(
                'DELETE FROM financials_detail WHERE year=? AND quarter=? AND unit=? AND report_type=\'esf\' AND empresa_id=?',
                (year, quarter, unit, empresa_id)
            )
            db.commit()
        else:
            db.execute(
                'DELETE FROM financials WHERE year=? AND month=? AND unit=?',
                (year, month, unit)
            )
            db.execute(
                'DELETE FROM financials_detail WHERE year=? AND month=? AND unit=? AND report_type=\'eerr\'',
                (year, month, unit)
            )
            db.commit()

        for code, amount in accounts.items():
            is_balance = OdooParser.is_balance_account(code)

            m = db.execute('SELECT partida, sign, income_type FROM mapping WHERE odoo_code = ?', (code,)).fetchone()

            if not m:
                name_clean = parser.names.get(code, '').strip().lower()
                auto = None
                if name_clean:
                    auto = db.execute(
                        'SELECT partida, sign, income_type FROM mapping WHERE lower(odoo_name)=?',
                        (name_clean,)
                    ).fetchone()
                if not auto:
                    prefix = '.'.join(code.split('.')[:2])
                    auto = db.execute(
                        "SELECT partida, sign, income_type FROM mapping WHERE odoo_code LIKE ? LIMIT 1",
                        (prefix + '%',)
                    ).fetchone()
                if auto:
                    db.execute(
                        'INSERT OR IGNORE INTO mapping (odoo_code, odoo_name, partida, sign, income_type) VALUES (?,?,?,?,?)',
                        (code, parser.names.get(code, ''), auto['partida'], auto['sign'], auto['income_type'])
                    )
                    db.commit()
                    m = auto

            if m:
                signed_amount = amount * (m['sign'] if m['sign'] else -1)

                report_type = 'esf' if (is_balance or is_esf) else 'eerr'
                db.execute(
                    '''INSERT INTO financials_detail
                       (year, month, unit, odoo_code, odoo_name, partida, amount_orig,
                       amount_sign, report_type, quarter, empresa_id)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?)
                       ON CONFLICT(year, month, unit, odoo_code, empresa_id)
                       DO UPDATE SET amount_orig=excluded.amount_orig,
                                    amount_sign=excluded.amount_sign,
                                    partida=excluded.partida''',
                    (year, month, unit, code, parser.names.get(code, ''),
                     m['partida'], amount, signed_amount, report_type, quarter,
                     empresa_id if is_esf else None)
                )

                if is_balance or is_esf:
                    db.execute(
                        '''INSERT INTO esf_data (year, quarter, unit, partida, amount, empresa_id) VALUES (?,?,?,?,?,?)
                           ON CONFLICT(year, quarter, unit, partida, empresa_id) DO UPDATE SET amount=excluded.amount''',
                        (year, quarter, unit, m['partida'], signed_amount, empresa_id if is_esf else None)
                    )
                    inserted_esf += 1
                else:
                    db.execute(
                        '''INSERT INTO financials (year, month, unit, partida, amount) VALUES (?,?,?,?,?)
                           ON CONFLICT(year, month, unit, partida) DO UPDATE SET amount=excluded.amount''',
                        (year, month, unit, m['partida'], signed_amount)
                    )
                    inserted_fin += 1
            else:
                unmapped.append({'code': code, 'name': parser.names.get(code, ''), 'amount': amount})
                skipped += 1

        db.commit()
        if force:
            prev = db.execute(
                '''SELECT id FROM history WHERE year=? AND month=? AND unit=? AND is_esf=?
                   AND superseded_by IS NULL ORDER BY created_at DESC LIMIT 1''',
                (year, month, unit, 1 if is_esf else 0)
            ).fetchone()
            if prev:
                new_entry = db.execute(
                    'INSERT INTO history (year, month, unit, inserted, is_esf, empresa_id) VALUES (?,?,?,?,?,?)',
                    (year, month, unit, inserted_fin + inserted_esf, 1 if is_esf else 0, empresa_id if is_esf else None)
                )
                new_id = new_entry.lastrowid
                db.execute(
                    'UPDATE history SET superseded_by=?, superseded_at=datetime(\'now\',\'localtime\') WHERE id=?',
                    (new_id, prev['id'])
                )
                db.commit()
            else:
                db.execute(
                    'INSERT INTO history (year, month, unit, inserted, is_esf, empresa_id) VALUES (?,?,?,?,?,?)',
                    (year, month, unit, inserted_fin + inserted_esf, 1 if is_esf else 0, empresa_id if is_esf else None)
                )
                db.commit()
        else:
            db.execute(
                'INSERT INTO history (year, month, unit, inserted, is_esf, empresa_id) VALUES (?,?,?,?,?,?)',
                (year, month, unit, inserted_fin + inserted_esf, 1 if is_esf else 0, empresa_id if is_esf else None)
            )
            db.commit()

        total_odoo = sum(abs(v) for c, v in accounts.items() if not OdooParser.is_balance_account(c))
        total_db_row = db.execute(
            'SELECT SUM(ABS(amount)) FROM financials WHERE year=? AND month=? AND unit=?',
            (year, month, unit)
        ).fetchone()
        total_db = total_db_row[0] or 0
        concilia = {
            'total_odoo': round(total_odoo, 2),
            'total_db': round(total_db, 2),
            'diferencia': round(abs(total_odoo - total_db), 2),
            'ok': abs(total_odoo - total_db) < 0.01
        }

        if unmapped:
            print("\n" + "="*80)
            print(f"CUENTAS SIN MAPEAR - {year}/{month}/{unit}")
            print("="*80)
            for u in unmapped:
                print(f"  Code: {u['code']:20s} | Name: {u['name']:50s} | Amount: {u['amount']:>15,.2f}")
            print("="*80 + "\n")

        return jsonify({
            'inserted_financials': inserted_fin,
            'inserted_esf': inserted_esf,
            'skipped': skipped,
            'unmapped': unmapped,
            'conciliacion': concilia
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
