from flask import Blueprint, jsonify, request
from datetime import datetime
from db import get_db
from constants import MONTHS
from helpers import get_clasificacion

comparativas_bp = Blueprint('comparativas', __name__)


@comparativas_bp.route('/api/comparativa', methods=['GET'])
def comparativa():
    year = int(request.args.get('year', datetime.now().year))
    unit = request.args.get('unit', '')
    empresa_id = request.args.get('empresa_id', type=int)
    prev = year - 1
    db   = get_db()
    ing_p, cos_p, gas_p = get_clasificacion(db)
    filtros = []
    filtro_params = []
    if unit:
        filtros.append("unit=?")
        filtro_params.append(unit)
    if empresa_id is not None:
        filtros.append("empresa_id=?")
        filtro_params.append(empresa_id)
    uc = ("AND " + " AND ".join(filtros)) if filtros else ''
    uc_params = filtro_params

    def totals(yr):
        def s(partidas):
            if not partidas: return 0
            ph = ','.join('?' * len(partidas))
            r  = db.execute(
                f'SELECT SUM(amount) FROM financials WHERE year=? AND partida IN ({ph}) {uc}',
                [str(yr)] + list(partidas) + uc_params
            ).fetchone()
            return r[0] or 0
        i = s(ing_p); c = s(cos_p); g = s(gas_p)
        ub = i - c; un = i - c - g
        return {
            'ingresos': round(i, 2), 'costos': round(c, 2), 'gastos': round(g, 2),
            'utilidad_bruta': round(ub, 2), 'utilidad_neta': round(un, 2),
            'margen_bruto': round(ub / i * 100, 1) if i else 0,
            'margen_neto':  round(un / i * 100, 1) if i else 0
        }

    def by_month(yr):
        rows = []
        for m in MONTHS:
            def sm(partidas):
                if not partidas: return 0
                ph = ','.join('?' * len(partidas))
                r  = db.execute(
                    f'SELECT SUM(amount) FROM financials WHERE year=? AND month=? AND partida IN ({ph}) {uc}',
                    [str(yr), m] + list(partidas) + uc_params
                ).fetchone()
                return r[0] or 0
            i = sm(ing_p); c = sm(cos_p); g = sm(gas_p)
            rows.append({'month': m, 'ingresos': round(i, 2), 'costos': round(c, 2),
                         'gastos': round(g, 2), 'utilidad_neta': round(i - c - g, 2)})
        return rows

    return jsonify({
        'year': year, 'prev': prev,
        'actual': totals(year), 'anterior': totals(prev),
        'meses_actual': by_month(year), 'meses_anterior': by_month(prev)
    })
