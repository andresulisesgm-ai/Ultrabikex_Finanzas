// ── ESF ────────────────────────────────────────────────────────────────────────
let ESF_DATA = null, esfQ = 1;

let ESFDIV_YEAR = null;
let ESFDIV_Q = 1;
let ESFDIV_CACHE = {};
let ESFDIV_ROWS = null;

async function fetchESFDivQuarter(year, quarter){
  const empresaParam = CURRENT_EMPRESA_ID ? `&empresa_id=${CURRENT_EMPRESA_ID}` : '';
  const [res1, res2] = await Promise.all([
    fetch(`/api/esf-divisa-real?year=${year}&quarter=${quarter}${empresaParam}`),
    fetch(`/api/esf-divisa-real/detalle-cuentas?year=${year}&quarter=${quarter}${empresaParam}`)
  ]);
  const data = await res1.json();
  const detalle = await res2.json();
  if(!res1.ok){
    throw new Error(data.error || 'Error al cargar datos.');
  }
  return {data, detalle};
}

async function loadESFDivisaReal(){
  ESFDIV_YEAR = G('esfdiv-year').value;
  ESFDIV_CACHE[ESFDIV_YEAR] = {};
  await loadAndRenderESFDivQ(ESFDIV_Q || 1);
}

async function switchESFDivQ(tabEl, q){
  document.querySelectorAll('#esfdiv-qtabs .esf-qtab').forEach(t => t.classList.remove('active'));
  tabEl.classList.add('active');
  ESFDIV_Q = q;
  await loadAndRenderESFDivQ(q);
}

async function loadAndRenderESFDivQ(q){
  G('esfdiv-loading').style.display = 'block';
  G('esfdiv-content').style.display = 'none';
  G('esfdiv-error').style.display = 'none';
  try{
    const year = ESFDIV_YEAR || G('esfdiv-year').value;
    ESFDIV_CACHE[year] = ESFDIV_CACHE[year] || {};

    if(q === 0){
      const faltantes = [1,2,3,4].filter(qq => !ESFDIV_CACHE[year][qq]);
      if(faltantes.length){
        const resultados = await Promise.allSettled(faltantes.map(qq => fetchESFDivQuarter(year, qq)));
        faltantes.forEach((qq, idx) => {
          const r = resultados[idx];
          ESFDIV_CACHE[year][qq] = r.status === 'fulfilled' ? r.value : null;
        });
      }
      pintarESFDivisaRealTodos(year);
    } else {
      if(!ESFDIV_CACHE[year][q]){
        ESFDIV_CACHE[year][q] = await fetchESFDivQuarter(year, q);
      }
      const {data, detalle} = ESFDIV_CACHE[year][q];
      pintarESFDivisaReal(data, detalle);
    }
    G('esfdiv-loading').style.display = 'none';
    G('esfdiv-content').style.display = 'block';
  }catch(e){
    G('esfdiv-loading').style.display = 'none';
    G('esfdiv-error').style.display = 'block';
    G('esfdiv-error').textContent = e.message || 'Error de conexión.';
  }
}

function pintarESFDivisaReal(data, detalle){
  renderESFDivisaPartidasDetalle(detalle);
  renderESFDivisaCompleto(data.esf_completo);
}

function pintarESFDivisaRealTodos(year){
  const disponibles = [1,2,3,4].filter(qq => ESFDIV_CACHE[year][qq]);
  if(!disponibles.length){
    G('esfdiv-error').style.display = 'block';
    G('esfdiv-error').textContent = 'No hay datos disponibles para ningún trimestre.';
    return;
  }
  const base = ESFDIV_CACHE[year][disponibles[0]].data.esf_completo;
  const merged = JSON.parse(JSON.stringify(base));
  for(const row of merged.rows){
    row.quarters = row.quarters || {};
    for(const qq of [1,2,3,4]){
      const cached = ESFDIV_CACHE[year][qq];
      if(!cached) continue;
      const src = cached.data.esf_completo.rows.find(r => r.partida === row.partida);
      if(src && src.quarters){
        row.quarters[qq] = src.quarters[qq];
      }
    }
  }
  renderESFDivisaPartidasDetalle(null);
  renderESFDivisaCompleto(merged);
}

async function renderESFDivisaPartidasDetalle(detalle){
  const cont = G('esfdiv-partidas-detalle');
  if (CURRENT_EMPRESA_ID === null) {
    cont.innerHTML = '<p style="color:var(--mu);font-size:11px;padding:10px 0">Selecciona una empresa específica (no Holding) para ajustar Ganancia/Pérdida en tasa cambiaria.</p>';
    return;
  }
  const year = ESFDIV_YEAR || G('esfdiv-year').value;
  const empresaParam = CURRENT_EMPRESA_ID ? `&empresa_id=${CURRENT_EMPRESA_ID}` : '';
  const quarters = ESFDIV_Q === 0 ? [1,2,3,4] : [ESFDIV_Q];
  cont.innerHTML = '<p style="color:var(--mu);font-size:11px;padding:10px 0">Cargando...</p>';
  const resultados = await Promise.all(quarters.map(q =>
    fetch(`/api/divisa_real/ganancia_perdida?year=${year}&quarter=${q}${empresaParam}`).then(r => r.ok ? r.json() : null)
  ));
  let html = '';
  quarters.forEach((q, idx) => {
    const d = resultados[idx];
    if (!d) return;
    const ganancia = d.override_ganancia !== null ? d.override_ganancia : d.sugerido_ganancia;
    const perdida = d.override_perdida !== null ? d.override_perdida : d.sugerido_perdida;
    const esOverride = d.override_ganancia !== null;
    html += `<div style="margin-bottom:12px;border-bottom:1px solid var(--bd);padding-bottom:8px">
      <div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;font-weight:700;padding:4px 0">
        <span>Q${q}</span>
        <span style="font-weight:400;color:${esOverride ? 'var(--green)' : 'var(--mu2)'}">${esOverride ? 'Confirmado' : 'Sugerido'}</span>
      </div>
      <div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;padding:3px 0">
        <span>Ganancia</span>
        <input type="number" class="pct-input" id="gpd-ganancia-${q}" value="${ganancia}" step="0.01" style="width:100px;text-align:right">
      </div>
      <div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;padding:3px 0">
        <span>Pérdida</span>
        <input type="number" class="pct-input" id="gpd-perdida-${q}" value="${perdida}" step="0.01" style="width:100px;text-align:right">
      </div>
      <div style="display:flex;gap:6px;margin-top:4px">
        <button class="btnm-sm" onclick="guardarGananciaPerdidaDivisa(${q})">Guardar Q${q}</button>
        ${esOverride ? `<button class="btnm-sm" style="background:var(--amber-l);color:var(--amber)" onclick="deshacerGananciaPerdidaDivisa(${q})">Deshacer</button>` : ''}
      </div>
    </div>`;
  });
  cont.innerHTML = html || '<p style="color:var(--mu);font-size:11px;padding:10px 0">Sin datos.</p>';
}

async function guardarGananciaPerdidaDivisa(q){
  const year = ESFDIV_YEAR || G('esfdiv-year').value;
  const empresaId = CURRENT_EMPRESA_ID || null;
  const ganancia = parseFloat(G(`gpd-ganancia-${q}`).value) || 0;
  const perdida = parseFloat(G(`gpd-perdida-${q}`).value) || 0;
  const r = await fetch('/api/divisa_real/ganancia_perdida', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({year, quarter: q, empresa_id: empresaId, ganancia, perdida})
  });
  if (r.ok) {
    renderESFDivisaPartidasDetalle(null);
  } else {
    alert('Error al guardar el ajuste.');
  }
}

async function deshacerGananciaPerdidaDivisa(q){
  if(!confirm(`¿Deshacer el ajuste manual de Q${q} y volver al valor sugerido?`)) return;
  const year = ESFDIV_YEAR || G('esfdiv-year').value;
  const empresaId = CURRENT_EMPRESA_ID || null;
  const r = await fetch('/api/divisa_real/ganancia_perdida/undo', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({year, quarter: q, empresa_id: empresaId})
  });
  if (r.ok) {
    renderESFDivisaPartidasDetalle(null);
  } else {
    alert('Error al deshacer el ajuste.');
  }
}

function renderESFDivisaCompleto(esfCompleto){
  ESFDIV_ROWS = esfCompleto.rows;
  const qAll = ESFDIV_Q === 0;
  const quarters = qAll ? [1,2,3,4] : [ESFDIV_Q];
  const rows = esfCompleto.rows;

  const qCols = quarters.map(q => `90px`).join(' ');
  const varCols = qAll ? '65px 65px 65px' : '';
  const gridCols = `1fr 100px ${qCols}${qAll ? ' ' + varCols : ''}`;

  function cleanPartidaName(name) {
    return name.replace(/\s*\((CxC|PxC|CxP|PxP)\)/g, '');
  }
  function qVal(q, rowObj) {
    return (rowObj.quarters && rowObj.quarters[q]) || 0;
  }
  function qVar(q1, q2, rowObj) {
    const a = qVal(q1, rowObj), b = qVal(q2, rowObj);
    if (!a) return null;
    return ((b - a) / Math.abs(a) * 100).toFixed(1);
  }
  function numCells(rowObj) {
    const prevVal = rowObj.year_prev || 0;
    const prevColored = prevVal < 0 ? 'color:var(--red)' : '';
    const prevCell = `<div class="esf-num" style="${prevColored}">${prevVal === 0 ? '—' : fmt(prevVal)}</div>`;
    const vals = quarters.map(q => qVal(q, rowObj));
    const nums = vals.map(v => {
      const colored = v < 0 ? 'color:var(--red)' : '';
      return `<div class="esf-num" style="${colored}">${v === 0 ? '—' : fmt(v)}</div>`;
    }).join('');
    let varHtml = '';
    if (qAll) {
      const v12 = qVar(1,2,rowObj), v23 = qVar(2,3,rowObj), v34 = qVar(3,4,rowObj);
      const varCell = v => v === null ? '<div class="esf-var">—</div>' :
        `<div class="esf-var ${parseFloat(v) >= 0 ? 'var-pos' : 'var-neg'}">${parseFloat(v) >= 0 ? '▲' : '▼'}${Math.abs(parseFloat(v))}%</div>`;
      varHtml = varCell(v12) + varCell(v23) + varCell(v34);
    }
    return prevCell + nums + varHtml;
  }

  const isParent = new Array(rows.length).fill(false);
  const parentIndices = new Array(rows.length).fill(null);
  for (let i = 0; i < rows.length; i++) {
    const r = rows[i];
    if (r.parent_name) {
      for (let j = i - 1; j >= 0; j--) {
        if (rows[j].partida === r.parent_name) {
          parentIndices[i] = j;
          isParent[j] = true;
          break;
        }
      }
    }
  }

  const totalActivosRow = rows.find(r => r.partida === 'TOTAL ACTIVOS');
  const _HIDDEN_SUBS = new Set([
    'Total Activos Corrientes','Total Activos No Corrientes',
    'Total Pasivos Corrientes','Total Pasivos No Corrientes'
  ]);

  let htmlRows = '';
  for (let i = 0; i < rows.length; i++) {
    const r = rows[i];
    if (r.partida === 'TOTAL ACTIVOS') continue;

    if (_HIDDEN_SUBS.has(r.partida)) {
      if (r.partida === 'Total Activos No Corrientes' && totalActivosRow) {
        htmlRows += `<div class="esfdiv-row esf-grand"
                          data-esfdiv-row-id="total-activos-moved"
                          data-level="0" data-expanded="true"
                          data-partida="TOTAL ACTIVOS"
                          style="grid-template-columns:${gridCols}">
          <div style="padding-left:10px;font-weight:700">TOTAL ACTIVOS</div>
          ${numCells(totalActivosRow)}
        </div>`;
      }
      continue;
    }

    const cleanName = cleanPartidaName(r.partida);
    const isHdr = r.is_header;
    const level = r.level;
    const isTotal = level === 0;
    const useBold = r.bold || isHdr || isTotal;
    const parentIdx = parentIndices[i];
    const hasChildren = isParent[i];

    let cls = 'esf-leaf';
    if (level === 0) {
      cls = 'esf-grand';
    } else if (level === 1) {
      cls = r.partida.startsWith('Total') || r.partida.startsWith('TOTAL') ? 'esf-sub' : 'esf-sec';
    } else if (level === 2 && isHdr) {
      cls = 'esf-sub';
    }

    const boldStyle = useBold ? 'font-weight:700' : '';
    const padLeft = (r.indent * 12 + 10) + 'px';
    const isAlwaysExpanded = level <= 1;
    let saved = null;
    try {
      saved = localStorage.getItem('esfdiv_expanded_' + r.partida);
    } catch (e) {
      console.error('Error reading ESF Divisa Real expanded state:', e);
    }
    const initiallyExpanded = isAlwaysExpanded || saved === '1';

    let toggleHtml = '';
    if (hasChildren && !isAlwaysExpanded) {
      const toggleChar = initiallyExpanded ? '▼' : '▶';
      toggleHtml = `<span class="esf-toggle" onclick="toggleESFDivRow(event, ${i})"
        style="cursor:pointer;margin-right:6px;display:inline-block;width:12px;font-family:monospace;color:var(--primary);font-weight:bold">${toggleChar}</span>`;
    }

    const escapedPartida = r.partida.replace(/"/g, '&quot;');

    htmlRows += `<div class="esfdiv-row ${cls}"
                      data-esfdiv-row-id="${i}"
                      data-parent-id="${parentIdx !== null ? parentIdx : ''}"
                      data-level="${level}"
                      data-expanded="${initiallyExpanded ? 'true' : 'false'}"
                      data-partida="${escapedPartida}"
                      style="grid-template-columns:${gridCols}">
      <div style="padding-left:${padLeft};${boldStyle}">${toggleHtml}${cleanName}</div>
      ${numCells(r)}
    </div>`;
  }

  const activos = rows.find(r => r.partida === 'TOTAL ACTIVOS');
  const pasivos = rows.find(r => r.partida === 'TOTAL PASIVOS');
  const patrimonio = rows.find(r => r.partida === 'Total Patrimonio');
  const getDif = (q) => {
    const a = activos ? qVal(q, activos) : 0;
    const p = pasivos ? qVal(q, pasivos) : 0;
    const pt = patrimonio ? qVal(q, patrimonio) : 0;
    return a - p - pt;
  };

  htmlRows += `<div class="esfdiv-row esf-grand" style="grid-template-columns:${gridCols};border-top:2px solid var(--bd);margin-top:6px">
    <div style="padding-left:10px;font-weight:700">DIFERENCIA (Activos - Pasivos - Patrimonio)</div>
    <div class="esf-num"></div>
    ${quarters.map(q => {
      const d = getDif(q);
      const c = Math.abs(d) > 1.0 ? 'color:var(--red)' : 'color:var(--green)';
      return `<div style="${c};font-family:'DM Mono',monospace;text-align:right">${fmt(d)}</div>`;
    }).join('')}
    ${qAll ? '<div></div><div></div><div></div>' : ''}
  </div>`;

  const qLabels = {1:'Q1 (Ene–Mar)', 2:'Q2 (Abr–Jun)', 3:'Q3 (Jul–Sep)', 4:'Q4 (Oct–Dic)'};
  const prevYearHdr = esfCompleto.year_prev || (parseInt(ESFDIV_YEAR) - 1).toString();
  const qHdrs = quarters.map(q => `<div style="text-align:right">${qLabels[q]}</div>`).join('');
  const varHdrs = qAll ? '<div style="text-align:right">Var Q1-2</div><div style="text-align:right">Var Q2-3</div><div style="text-align:right">Var Q3-4</div>' : '';
  const hdrHtml = `<div class="esfdiv-hdr" style="grid-template-columns:${gridCols}">
    <div>Partida</div>
    <div style="text-align:right">Cierre ${prevYearHdr}</div>
    ${qHdrs}
    ${varHdrs}
  </div>`;

  G('esfdiv-completo-body').innerHTML = `<div class="esfdiv-wrap">${hdrHtml}${htmlRows}</div>`;
  updateESFDivRowVisibility();
}

function updateESFDivRowVisibility() {
  const rows = document.querySelectorAll('div.esfdiv-row[data-esfdiv-row-id]');
  const expandedStates = {};
  rows.forEach(r => {
    const id = r.getAttribute('data-esfdiv-row-id');
    expandedStates[id] = r.getAttribute('data-expanded') === 'true';
  });
  function isRowVisible(id, level, parentId) {
    if (level <= 2) return true;
    if (parentId === null || parentId === undefined || parentId === '') return false;
    const parentRow = document.querySelector(`div.esfdiv-row[data-esfdiv-row-id="${parentId}"]`);
    if (!parentRow) return false;
    const parentLevel = parseInt(parentRow.getAttribute('data-level') || '0', 10);
    const parentParentId = parentRow.getAttribute('data-parent-id');
    return isRowVisible(parentId, parentLevel, parentParentId) && expandedStates[parentId];
  }
  rows.forEach(r => {
    const id = r.getAttribute('data-esfdiv-row-id');
    const level = parseInt(r.getAttribute('data-level') || '0', 10);
    const parentId = r.getAttribute('data-parent-id');
    r.style.display = isRowVisible(id, level, parentId) ? 'grid' : 'none';
  });
}

function toggleESFDivRow(event, rowId) {
  event.stopPropagation();
  const rowEl = document.querySelector(`div.esfdiv-row[data-esfdiv-row-id="${rowId}"]`);
  if (!rowEl) return;
  const toggleBtn = rowEl.querySelector('.esf-toggle');
  if (!toggleBtn) return;
  const newExpanded = !(rowEl.getAttribute('data-expanded') === 'true');
  rowEl.setAttribute('data-expanded', newExpanded ? 'true' : 'false');
  toggleBtn.textContent = newExpanded ? '▼' : '▶';
  const partida = rowEl.getAttribute('data-partida');
  if (partida) {
    try {
      localStorage.setItem('esfdiv_expanded_' + partida, newExpanded ? '1' : '0');
    } catch (e) {
      console.error('Error saving ESF Divisa Real expanded state:', e);
    }
  }
  updateESFDivRowVisibility();
}


async function loadESF() {
  const year = G('esf-year').value, unit = '';
  G('esf-body').innerHTML = '<p style="color:var(--mu);font-size:12px;padding:20px 0">Cargando...</p>';
  try {
    const r = await fetch(`/api/esf/completo?year=${year}&unit=${encodeURIComponent(unit)}&empresa_id=${CURRENT_EMPRESA_ID||''}`);
    ESF_DATA = await r.json();
    renderESF();
  } catch(e) {
    G('esf-body').innerHTML = `<p style="color:var(--red);font-size:12px;padding:20px 0">Error: ${e.message}</p>`;
  }
}

function switchESFQ(el, q) {
  document.querySelectorAll('.esf-qtab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  esfQ = q;
  renderESF();
}

function updateESFRowVisibility() {
  const rows = document.querySelectorAll('div.esf-row[data-row-id]');
  const expandedStates = {};
  
  rows.forEach(r => {
    const id = r.getAttribute('data-row-id');
    const expanded = r.getAttribute('data-expanded') === 'true';
    expandedStates[id] = expanded;
  });
  
  function isRowVisible(id, level, parentId) {
    if (level <= 2) {
      return true;
    }
    if (parentId === null || parentId === undefined || parentId === '') {
      return false;
    }
    
    const parentRow = document.querySelector(`div.esf-row[data-row-id="${parentId}"]`);
    if (!parentRow) return false;
    
    const parentLevel = parseInt(parentRow.getAttribute('data-level') || '0', 10);
    const parentParentId = parentRow.getAttribute('data-parent-id');
    
    return isRowVisible(parentId, parentLevel, parentParentId) && expandedStates[parentId];
  }
  
  rows.forEach(r => {
    const id = r.getAttribute('data-row-id');
    const level = parseInt(r.getAttribute('data-level') || '0', 10);
    const parentId = r.getAttribute('data-parent-id');
    
    const visible = isRowVisible(id, level, parentId);
    r.style.display = visible ? 'grid' : 'none';
  });
}

function toggleESFRow(event, rowId) {
  event.stopPropagation();
  const rowEl = document.querySelector(`div.esf-row[data-row-id="${rowId}"]`);
  if (!rowEl) return;
  const toggleBtn = rowEl.querySelector('.esf-toggle');
  if (!toggleBtn) return;
  
  const isExpanded = rowEl.getAttribute('data-expanded') === 'true';
  const newExpanded = !isExpanded;
  
  rowEl.setAttribute('data-expanded', newExpanded ? 'true' : 'false');
  toggleBtn.textContent = newExpanded ? '▼' : '▶';
  
  const partida = rowEl.getAttribute('data-partida');
  if (partida) {
    try {
      localStorage.setItem('esf_expanded_' + partida, newExpanded ? '1' : '0');
    } catch (e) {
      console.error('Error saving ESF expanded state to localStorage:', e);
    }
  }
  
  updateESFRowVisibility();
}

function renderESF() {
  if (!ESF_DATA) return;
  const qAll = esfQ === 0;
  const quarters = qAll ? [1,2,3,4] : [esfQ];
  const qLabels = {1:'Q1 (Ene–Mar)', 2:'Q2 (Abr–Jun)', 3:'Q3 (Jul–Sep)', 4:'Q4 (Oct–Dic)'};

  const qCols = quarters.map(q => `90px`).join(' ');
  const varCols = qAll ? '65px 65px 65px' : '';
  const gridCols = `260px 100px ${qCols}${qAll ? ' ' + varCols : ''}`;

  function cleanPartidaName(name) {
    return name.replace(/\s*\((CxC|PxC|CxP|PxP)\)/g, '');
  }

  function qVal(q, rowObj) {
    return rowObj.quarters[q] || 0;
  }

  function qVar(q1, q2, rowObj) {
    const a = qVal(q1, rowObj), b = qVal(q2, rowObj);
    if (!a) return null;
    return ((b - a) / Math.abs(a) * 100).toFixed(1);
  }

  function numCells(rowObj) {
    const prevVal = rowObj.year_prev || 0;
    const prevColored = prevVal < 0 ? 'color:var(--red)' : '';
    const prevCell = `<div class="esf-num" style="${prevColored}">${prevVal === 0 ? '—' : fmt(prevVal)}</div>`;
    const vals = quarters.map(q => qVal(q, rowObj));
    const nums = vals.map(v => {
      const colored = v < 0 ? 'color:var(--red)' : '';
      return `<div class="esf-num" style="${colored}">${v === 0 ? '—' : fmt(v)}</div>`;
    }).join('');
    let varHtml = '';
    if (qAll) {
      const v12 = qVar(1,2,rowObj), v23 = qVar(2,3,rowObj), v34 = qVar(3,4,rowObj);
      const varCell = v => v === null ? '<div class="esf-var">—</div>' :
        `<div class="esf-var ${parseFloat(v) >= 0 ? 'var-pos' : 'var-neg'}">${parseFloat(v) >= 0 ? '▲' : '▼'}${Math.abs(parseFloat(v))}%</div>`;
      varHtml = varCell(v12) + varCell(v23) + varCell(v34);
    }
    return prevCell + nums + varHtml;
  }

  const rows = ESF_DATA.rows;
  const isParent = new Array(rows.length).fill(false);
  const parentIndices = new Array(rows.length).fill(null);
  
  for (let i = 0; i < rows.length; i++) {
    const r = rows[i];
    if (r.parent_name) {
      for (let j = i - 1; j >= 0; j--) {
        if (rows[j].partida === r.parent_name) {
          parentIndices[i] = j;
          isParent[j] = true;
          break;
        }
      }
    }
  }

  // Reordenamiento visual: extraer TOTAL ACTIVOS para moverlo después de Total Activos No Corrientes
  const totalActivosRow = rows.find(r => r.partida === 'TOTAL ACTIVOS');

  let htmlRows = '';
  for (let i = 0; i < rows.length; i++) {
    const r = rows[i];

    // Saltar TOTAL ACTIVOS en su posición original
    if (r.partida === 'TOTAL ACTIVOS') continue;

    // Ocultar subtotales redundantes (el header de sección ya muestra el valor)
    const _HIDDEN_SUBS = new Set([
      'Total Activos Corrientes','Total Activos No Corrientes',
      'Total Pasivos Corrientes','Total Pasivos No Corrientes'
    ]);
    if (_HIDDEN_SUBS.has(r.partida)) {
      if (r.partida === 'Total Activos No Corrientes' && totalActivosRow) {
        htmlRows += `<div class="esf-row esf-grand" 
                          data-row-id="total-activos-moved" 
                          data-level="0" data-expanded="true" 
                          data-partida="TOTAL ACTIVOS"
                          style="grid-template-columns:${gridCols}">
          <div style="padding-left:10px;font-weight:700">TOTAL ACTIVOS</div>
          ${numCells(totalActivosRow)}
        </div>`;
      }
      continue;
    }

    const cleanName = cleanPartidaName(r.partida);
    const isHdr = r.is_header;
    const level = r.level;
    const isTotal = level === 0;
    const useBold = r.bold || isHdr || isTotal;
    const parentIdx = parentIndices[i];
    const hasChildren = isParent[i];

    let cls = 'esf-leaf';
    if (level === 0) {
      cls = 'esf-grand';
    } else if (level === 1) {
      cls = r.partida.startsWith('Total') || r.partida.startsWith('TOTAL') ? 'esf-sub' : 'esf-sec';
    } else if (level === 2 && isHdr) {
      cls = 'esf-sub';
    }

    const boldStyle = useBold ? 'font-weight:700' : '';
    const padLeft = (r.indent * 12 + 10) + 'px';

    const isAlwaysExpanded = level <= 1;
    let saved = null;
    try {
      saved = localStorage.getItem('esf_expanded_' + r.partida);
    } catch (e) {
      console.error('Error reading ESF expanded state from localStorage:', e);
    }
    const initiallyExpanded = isAlwaysExpanded || saved === '1';

    let toggleHtml = '';
    if (hasChildren && !isAlwaysExpanded) {
      const toggleChar = initiallyExpanded ? '▼' : '▶';
      toggleHtml = `<span class="esf-toggle" onclick="toggleESFRow(event, ${i})" style="cursor:pointer;margin-right:6px;display:inline-block;width:12px;font-family:monospace;color:var(--primary);font-weight:bold">${toggleChar}</span>`;
    }

    const escapedPartida = r.partida.replace(/"/g, '&quot;');

    htmlRows += `<div class="esf-row ${cls}" 
                      data-row-id="${i}" 
                      data-parent-id="${parentIdx !== null ? parentIdx : ''}" 
                      data-level="${level}" 
                      data-expanded="${initiallyExpanded ? 'true' : 'false'}" 
                      data-partida="${escapedPartida}"
                      style="grid-template-columns:${gridCols}">
      <div style="padding-left:${padLeft};${boldStyle}">${toggleHtml}${cleanName}</div>
      ${numCells(r)}
    </div>`;


  }

  // Fila DIFERENCIA al final (Total Activos - Total Pasivos - Patrimonio)
  const getDiferencia = (q) => {
    const activos = rows.find(r => r.partida === 'TOTAL ACTIVOS');
    const pasivos = rows.find(r => r.partida === 'TOTAL PASIVOS');
    const patrimonio = rows.find(r => r.partida === 'Total Patrimonio');
    const a = activos ? (activos.quarters[q] || 0) : 0;
    const p = pasivos ? (pasivos.quarters[q] || 0) : 0;
    const pt = patrimonio ? (patrimonio.quarters[q] || 0) : 0;
    return a - p - pt;
  };
  const difRowObj = {
    quarters: {
      1: getDiferencia(1),
      2: getDiferencia(2),
      3: getDiferencia(3),
      4: getDiferencia(4)
    }
  };
  htmlRows += `<div class="esf-row esf-grand" 
                    data-row-id="diferencia" 
                    data-level="0" 
                    data-expanded="true" 
                    data-partida="DIFERENCIA"
                    style="grid-template-columns:${gridCols};background:var(--purple,#6c5ce7);margin-top:8px;color:var(--white,#fff)">
    <div style="padding-left:10px;font-weight:700;color:var(--white,#fff)">DIFERENCIA</div>
    ${numCells(difRowObj)}
  </div>`;

  const prevHdr = `<div class="esf-num" style="font-weight:700">${ESF_DATA.year_prev || 'Año Ant.'}</div>`;
  const qHdrs = quarters.map(q => `<div class="esf-num" style="font-weight:700">${qLabels[q]}</div>`).join('');
  const vHdrs = qAll ? '<div class="esf-var" style="font-weight:700">Q1→Q2</div><div class="esf-var" style="font-weight:700">Q2→Q3</div><div class="esf-var" style="font-weight:700">Q3→Q4</div>' : '';
  
  let html = `<div class="esf-wrap">
    <div class="esf-hdr" style="grid-template-columns:${gridCols}">
      <div>Partida</div>${prevHdr}${qHdrs}${vHdrs}
    </div>
    ${htmlRows}
  </div>`;

  G('esf-body').innerHTML = html;
  updateESFRowVisibility();
}
