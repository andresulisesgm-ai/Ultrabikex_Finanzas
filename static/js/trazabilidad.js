const TRAZA_MAP = {
  'ingr': 'ingresos',
  'cos':  'costos',
  'gas':  'gastos',
  'ub':   'utilidad_bruta',
  'un':   'utilidad_neta',
  'ebt':  'ebitda',
  'mb':   'ingresos',
  'mn':   'ingresos',
  'rc':   'costos',
  'rg':   'gastos'
};

const TRAZA_LABELS = {
  'ingresos':       'Ingresos totales',
  'costos':         'Costo de ventas',
  'gastos':         'Gastos operativos',
  'utilidad_bruta': 'Utilidad bruta',
  'utilidad_neta':  'Utilidad neta',
  'ebitda':         'EBITDA'
};

let _trazaCache = {};

async function showTraza(e, kcId) {
  e.stopPropagation();
  const kpiId = kcId.replace('kc-', '');
  const kpi   = TRAZA_MAP[kpiId];
  if (!kpi) return;

  const panel = G('traza-panel');
  panel.style.display = 'block';

  const rect = e.currentTarget.getBoundingClientRect();
  const scrollY = window.scrollY || document.documentElement.scrollTop;
  const scrollX = window.scrollX || document.documentElement.scrollLeft;
  panel.style.top  = (rect.bottom + scrollY + 6) + 'px';
  panel.style.left = (rect.left  + scrollX) + 'px';

  const year = G('sel-year') ? G('sel-year').value : new Date().getFullYear();
  const unit = G('sel-unit') ? G('sel-unit').value : '';
  const cacheKey = `${kpi}_${year}_${unit}`;

  G('tp-title').textContent = TRAZA_LABELS[kpi] || kpi;
  G('tp-total').textContent = 'Cargando...';
  G('tp-rows').innerHTML = '<div class="tp-loading">Consultando cuentas...</div>';

  if (_trazaCache[cacheKey]) {
    renderTrazaPanel(_trazaCache[cacheKey]);
    return;
  }

  try {
    const u = unit && unit !== 'TODAS' ? unit : '';
    const r = await fetch(`/api/trazabilidad?year=${year}&unit=${u}&kpi=${kpi}`);
    const d = await r.json();
    _trazaCache[cacheKey] = d;
    renderTrazaPanel(d);
  } catch(err) {
    G('tp-total').textContent = 'Error al cargar';
    G('tp-rows').innerHTML = '';
  }
}

function renderTrazaPanel(d) {
  G('tp-title').textContent = TRAZA_LABELS[d.kpi] || d.kpi;
  G('tp-total').textContent = `Total: ${fmtS(d.total)} · ${d.cuentas.length} cuentas`;
  G('tp-rows').innerHTML = d.cuentas.map(c => `
    <div class="tp-row">
      <span class="tp-code">${c.odoo_code}</span>
      <span class="tp-name" title="${c.odoo_name}">${c.odoo_name}</span>
      <span class="tp-val ${c.total < 0 ? 'tp-neg' : ''}">${fmtS(Math.abs(c.total))}</span>
    </div>
  `).join('');
}

document.addEventListener('click', (e) => {
  const panel = G('traza-panel');
  if (panel && panel.style.display === 'block') {
    if (!panel.contains(e.target)) {
      panel.style.display = 'none';
    }
  }
});

document.addEventListener('DOMContentLoaded', ()=>{
  const meses=['ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEPT','OCT','NOV','DIC'];
  const mesActual=meses[new Date().getMonth()];
  const sel=G('tasas-month');
  if(sel) sel.value=mesActual;
});
