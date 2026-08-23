// ── PRESUPUESTO ────────────────────────────────────────────────────────────────
let BGT_DATA = null, bgtTab = 'ingresos';

function switchBgtTab(el, tab) {
  document.querySelectorAll('.bgt-tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  bgtTab = tab;
  renderBgt();
}

async function loadBgt() {
  const year = G('bgt-year').value, unit = G('bgt-unit').value, month = G('bgt-month').value;
  G('bgt-body').innerHTML = '<p style="color:var(--mu);font-size:12px;padding:20px 0">Cargando...</p>';
  try {
    let url = `/api/budget?year=${year}&unit=${encodeURIComponent(unit)}`;
    if (month) url += `&month=${month}`;
    const r = await fetch(url);
    BGT_DATA = await r.json();
    renderBgt();
  } catch(e) {
    G('bgt-body').innerHTML = `<p style="color:var(--red);font-size:12px;padding:20px 0">Error: ${e.message}</p>`;
  }
}

function renderBgt() {
  if (!BGT_DATA) return;
  const months = BGT_DATA.comparativo.length ? Object.keys(BGT_DATA.comparativo[0].meses) : [];
  const N = months.length;
  const gridCols = `240px repeat(${N}, 160px) 130px 130px 80px`;
  const unitSel = G('bgt-unit').value;   // edición inline solo con unidad específica

  // Filtrar partidas por pestaña activa
  // Simplificado: por prefijo del nombre de partida
  const filters = {
    ingresos:  row => row.partida.toLowerCase().includes('ingreso') || row.partida.toLowerCase().includes('devoluc') || row.partida.toLowerCase().includes('descuento') || row.partida.toLowerCase().includes('sobrante') || row.partida.toLowerCase().includes('ganancia'),
    costos:    row => row.partida.toLowerCase().includes('costo'),
    gastos:    row => row.partida.toLowerCase().includes('gasto') || row.partida.toLowerCase().includes('faltante') || row.partida.toLowerCase().includes('pérdida') || row.partida.toLowerCase().includes('multa') || row.partida.toLowerCase().includes('deterioro') || row.partida.toLowerCase().includes('islr'),
    resumen:   () => true,
  };

  const filterFn = filters[bgtTab] || filters.resumen;
  let rows = BGT_DATA.comparativo.filter(filterFn);

  if (bgtTab === 'resumen') {
    // En resumen solo mostramos totales agregados por grupo
    const groups = {
      'Total Ingresos': filters.ingresos,
      'Total Costos':   filters.costos,
      'Total Gastos':   filters.gastos,
    };
    const summaryRows = Object.entries(groups).map(([label, fn]) => {
      const matching = BGT_DATA.comparativo.filter(fn);
      const sumB = matching.reduce((a, r) => a + r.acum_presupuesto, 0);
      const sumR = matching.reduce((a, r) => a + r.acum_real, 0);
      const meses = {};
      months.forEach(m => {
        const b = matching.reduce((a, r) => a + (r.meses[m]?.presupuesto || 0), 0);
        const rv = matching.reduce((a, r) => a + (r.meses[m]?.real || 0), 0);
        meses[m] = { presupuesto: b, real: rv, var_pct: b ? ((rv - b) / Math.abs(b) * 100).toFixed(1) : null };
      });
      return { partida: label, meses, acum_presupuesto: sumB, acum_real: sumR, acum_var_pct: sumB ? ((sumR - sumB) / Math.abs(sumB) * 100).toFixed(1) : null, _isTotal: true };
    });
    // Utilidad neta
    const totI = summaryRows.find(r => r.partida === 'Total Ingresos');
    const totC = summaryRows.find(r => r.partida === 'Total Costos');
    const totG = summaryRows.find(r => r.partida === 'Total Gastos');
    const unRow = { partida: 'Utilidad Neta', meses: {}, acum_presupuesto: 0, acum_real: 0, _isGrand: true };
    if (totI && totC && totG) {
      months.forEach(m => {
        const b = (totI.meses[m]?.presupuesto || 0) - (totC.meses[m]?.presupuesto || 0) - (totG.meses[m]?.presupuesto || 0);
        const rv = (totI.meses[m]?.real || 0) - (totC.meses[m]?.real || 0) - (totG.meses[m]?.real || 0);
        unRow.meses[m] = { presupuesto: b, real: rv, var_pct: b ? ((rv - b) / Math.abs(b) * 100).toFixed(1) : null };
      });
      unRow.acum_presupuesto = totI.acum_presupuesto - totC.acum_presupuesto - totG.acum_presupuesto;
      unRow.acum_real = totI.acum_real - totC.acum_real - totG.acum_real;
      const bp = unRow.acum_presupuesto;
      unRow.acum_var_pct = bp ? ((unRow.acum_real - bp) / Math.abs(bp) * 100).toFixed(1) : null;
    }
    rows = [...summaryRows, unRow];
  }

  // Header
  const mHdrs = months.map(m => `<div class="bgt-cell" style="font-weight:700;color:var(--tx2)">${m}</div>`).join('');
  const editNote = bgtTab === 'resumen' ? '' :
    (!unitSel
      ? `<div style="font-size:11px;color:var(--mu);padding:4px 0 8px">✏️ Selecciona una <strong>unidad específica</strong> (no Consolidado) para editar el presupuesto en línea.</div>`
      : `<div style="font-size:11px;color:var(--mu);padding:4px 0 8px">✏️ Edición en línea activa para <strong>${unitSel}</strong> — clic en una celda de presupuesto para modificar.</div>`);
  let html = editNote + `<div class="bgt-wrap">
    <div class="bgt-hdr" style="grid-template-columns:${gridCols}">
      <div>Partida</div>${mHdrs}<div class="bgt-cell">ACUM Ppto.</div><div class="bgt-cell">ACUM Real</div><div class="bgt-var" style="font-weight:700">%Var</div>
    </div>`;

  rows.forEach(row => {
    const isGrand = row._isGrand;
    const isTotal = row._isTotal;
    const rowCls = isGrand ? 'bgt-total' : isTotal ? 'bgt-row section' : 'bgt-row';
    const editable = !isGrand && !isTotal && bgtTab !== 'resumen' && !!unitSel;
    const mCols = months.map(m => {
      const cell = row.meses[m] || {presupuesto:0, real:0, var_pct:null};
      const vPct = cell.var_pct;
      const vHtml = vPct === null ? '—' :
        `<span class="${parseFloat(vPct) >= 0 ? 'bgt-var-ok' : 'bgt-var-bad'}">${parseFloat(vPct) >= 0 ? '▲' : '▼'}${Math.abs(parseFloat(vPct))}%</span>`;
      const pptoHtml = editable
        ? `<input class="bgt-input inline" type="number" step="0.01" value="${cell.presupuesto}" data-partida="${escAttr(row.partida)}" data-month="${m}" onchange="editBgt(this)" title="Editar presupuesto de ${unitSel}">`
        : fmtS(cell.presupuesto);
      return `<div class="bgt-cell"><div>${pptoHtml}</div><div style="color:var(--green);font-size:10px">${fmtS(cell.real)}</div><div style="font-size:10px">${vHtml}</div></div>`;
    }).join('');
    const vAcum = row.acum_var_pct;
    const vAcumHtml = vAcum === null ? '—' :
      `<span class="${parseFloat(vAcum) >= 0 ? 'bgt-var-ok' : 'bgt-var-bad'}">${parseFloat(vAcum) >= 0 ? '▲' : '▼'}${Math.abs(parseFloat(vAcum))}%</span>`;
    html += `<div class="${rowCls}" style="grid-template-columns:${gridCols}">
      <div style="font-weight:${isGrand || isTotal ? '700' : '400'}">${row.partida}</div>
      ${mCols}
      <div class="bgt-cell">${fmtS(row.acum_presupuesto)}</div>
      <div class="bgt-cell" style="color:var(--green)">${fmtS(row.acum_real)}</div>
      <div class="bgt-cell">${vAcumHtml}</div>
    </div>`;
  });

  if (!rows.length) {
    html += `<div style="padding:20px;color:var(--mu);font-size:12px;text-align:center">Sin datos de presupuesto para este período.<br>Usa "+ Cargar Ppto." para ingresar valores.</div>`;
  }

  html += '</div>';
  G('bgt-body').innerHTML = html;
}

