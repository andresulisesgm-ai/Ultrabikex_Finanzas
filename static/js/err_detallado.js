// ── EERR DETALLADO ───────────────────────────────────────────────────────────
let EERRD = null, eerdTab = 'resumen';

function switchEerdTab(el, tab) {
  document.querySelectorAll('.eerrd-tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  eerdTab = tab;
  renderEERRDet();
}

async function loadEERRDet() {
  const year = G('erd-year').value, unit = G('erd-unit').value;
  const mf = G('erd-mf').value, mt = G('erd-mt').value;
  let url = `/api/eerr/detalle?year=${year}&unit=${encodeURIComponent(unit)}`;
  if (mf) url += `&month_from=${mf}`;
  if (mt) url += `&month_to=${mt}`;
  G('erd-body').innerHTML = '<p style="color:var(--mu);font-size:12px;padding:20px 0">Cargando...</p>';
  try {
    const r = await fetch(url);
    EERRD = await r.json();
    renderEERRDet();
  } catch(e) {
    G('erd-body').innerHTML = `<p style="color:var(--red);font-size:12px;padding:20px 0">Error: ${e.message}</p>`;
  }
}

function renderEERRDet() {
  if (!EERRD) return;
  const months = EERRD.months;
  const N = months.length;

  // Grid template: partida + N meses + ACUM + %ACUM + N variaciones
  const cols = `220px repeat(${N}, 90px) 100px 60px repeat(${N}, 70px)`;

  function buildHdrRow() {
    const mCols = months.map(m => `<div class="eerrd-num" style="font-weight:700;color:var(--tx2)">${m}</div>`).join('');
    const vCols = months.map((m, i) => `<div class="eerrd-var" style="font-weight:700;color:var(--tx2)">${i === 0 ? '—' : `%vs${months[i-1]}`}</div>`).join('');
    return `<div class="eerrd-hdr" style="grid-template-columns:${cols}">
      <div>Partida</div>${mCols}<div class="eerrd-num">ACUM EJEC</div><div class="eerrd-pct">%Ing</div>${vCols}
    </div>`;
  }

  function buildRow(row, style = '', indent = false) {
    if (!row) return '';
    const mCols = months.map(m => {
      const v = row.meses[m] || 0;
      return `<div class="eerrd-num" style="${v < 0 ? 'color:var(--red)' : ''}">${v === 0 ? '—' : fmtS(v)}</div>`;
    }).join('');
    const acum = row.acum || 0;
    const ing = EERRD.ingresos.total.acum || 1;
    const pctIng = ing ? (acum / ing * 100).toFixed(1) + '%' : '—';
    const vCols = (row.var_pct || months.map(() => null)).map((v, i) => {
      if (v === null || i === 0) return `<div class="eerrd-var">—</div>`;
      const cls = v >= 0 ? 'var-pos' : 'var-neg';
      return `<div class="eerrd-var ${cls}">${v >= 0 ? '▲' : '▼'}${Math.abs(v)}%</div>`;
    }).join('');
    return `<div class="eerrd-row ${style}" style="grid-template-columns:${cols}">
      <div style="${indent ? 'padding-left:16px;color:var(--mu)' : 'font-weight:600'}">${row.partida}</div>
      ${mCols}
      <div class="eerrd-num" style="${acum < 0 ? 'color:var(--red)' : 'color:var(--blue);font-weight:700'}">${fmtS(acum)}</div>
      <div class="eerrd-pct">${pctIng}</div>
      ${vCols}
    </div>`;
  }

  const d = EERRD;
  let html = '<div class="eerrd-wrap">' + buildHdrRow();

  if (eerdTab === 'resumen') {
    html += buildRow(d.ingresos.total, 'hdr-row');
    html += buildRow(d.costos.total, 'hdr-row');
    html += buildRow(d.utilidad_bruta.total, 'grand');
    html += `<div class="eerrd-row section" style="grid-template-columns:${cols}"><div colspan="${N+4}" style="font-weight:700;color:var(--tx2)">Desglose Utilidad Bruta por Tipo</div>${months.map(()=>'<div></div>').join('')}<div></div><div></div>${months.map(()=>'<div></div>').join('')}</div>`;
    html += buildRow(d.utilidad_bruta.mercancia_taller, 'section', true);
    html += buildRow(d.utilidad_bruta.servicios, 'section', true);
    html += buildRow(d.utilidad_bruta.eventos, 'section', true);
    html += buildRow(d.gastos.total, 'hdr-row');
    html += buildRow(d.utilidad_neta, 'grand');

  } else if (eerdTab === 'mercancia') {
    html += buildRow(d.ingresos.mercancia_taller, 'hdr-row');
    html += buildRow(d.costos.mercancia_taller, 'hdr-row');
    html += buildRow(d.utilidad_bruta.mercancia_taller, 'grand');

  } else if (eerdTab === 'servicios') {
    html += buildRow(d.ingresos.servicios, 'hdr-row');
    html += buildRow(d.costos.servicios, 'hdr-row');
    html += buildRow(d.utilidad_bruta.servicios, 'grand');

  } else if (eerdTab === 'eventos') {
    html += buildRow(d.ingresos.eventos, 'hdr-row');
    html += buildRow(d.costos.eventos, 'hdr-row');
    html += buildRow(d.utilidad_bruta.eventos, 'grand');

  } else if (eerdTab === 'gastos') {
    html += buildRow(d.gastos.total, 'grand');
    (d.gastos.detalle || []).forEach(row => { html += buildRow(row, '', true); });
  }

  html += '</div>';
  G('erd-body').innerHTML = html;
}
