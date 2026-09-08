// ── ERR DIVISA REAL ───────────────────────────────────────────────────────
var EERR_DIVISA_DATA = null;

function lightenHex(hex, alpha = 0.4) {
  const h = hex.replace('#', '');
  const r = parseInt(h.substring(0, 2), 16);
  const g = parseInt(h.substring(2, 4), 16);
  const b = parseInt(h.substring(4, 6), 16);
  const nr = Math.round(r * alpha + 255 * (1 - alpha));
  const ng = Math.round(g * alpha + 255 * (1 - alpha));
  const nb = Math.round(b * alpha + 255 * (1 - alpha));
  return `#${nr.toString(16).padStart(2,'0')}${ng.toString(16).padStart(2,'0')}${nb.toString(16).padStart(2,'0')}`;
}

async function loadERRDivisa(){
  const year=G('err-divisa-year').value, unit=G('err-divisa-unit').value;
  const r=await fetch(`/api/eerr/divisa_real?year=${year}&unit=${encodeURIComponent(unit)}&empresa_id=${CURRENT_EMPRESA_ID||''}`);
  if(!r.ok){
    const err=await r.json();
    G('err-divisa-body').innerHTML=`<div style="padding:30px;text-align:center;color:var(--red)">⚠️ No se puede calcular el EERR Divisa Real.<br><br>${err.error||'Error desconocido'}<br><br><span style="color:var(--mu);font-size:11px">Carga las tasas faltantes en Configuración → Tasas de Cambio.</span></div>`;
    return;
  }
  const d=await r.json();
  EERR_DIVISA_DATA = d;

  const hStyle='font-size:8px;font-weight:700;text-align:center;padding:7px 4px;color:var(--mu);border:1px solid var(--bd)';
    const cStyle="font-size:8px;padding:5px 4px;text-align:right;font-family:'DM Mono',monospace;border:1px solid var(--bd)";
  const lStyle='font-size:8px;padding:6px 8px;text-align:left;border:1px solid var(--bd);white-space:nowrap';
  const hRowStyle='font-weight:700;background:var(--primary)15;color:var(--primary)';

  const fmtZ=(v)=>v===0||v===null?'':fmt(v);
  const pctZ=(v)=>v===0||v===null?'':pct(v);
  const varCol=(v)=>v===null||v===0?'':v>=0?`<span style="color:var(--green)">▲${pct(Math.abs(v))}</span>`:`<span style="color:var(--red)">▼${pct(Math.abs(v))}</span>`;

  // Mapeo de columnas por mes (igual que EERR normal)
  const monthCols={
    'ENE':3, 'FEB':7, 'MAR':10, 'ABR':7, 'MAY':7, 'JUN':16,
    'JUL':7, 'AGO':7, 'SEPT':10, 'OCT':7, 'NOV':7, 'DIC':10
  };

  // Headers principales
  let hdr1='<th rowspan="2" style="'+hStyle+';text-align:left;position:sticky;left:0;background:#fff;z-index:6;min-width:220px;width:220px;border-right:2px solid var(--bd)">Partida</th>';
  hdr1+=`<th colspan="3" style="${hStyle};background:#fff;border-right:2px solid var(--bd)">${d.year_prev}</th>`;

  const meses=['ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEPT','OCT','NOV','DIC'];
  for(let m of meses){
    const cols=monthCols[m];
    const bg=meses.indexOf(m)%2===0?'background-color:#f0f4f8':'background-color:#ffffff';
    hdr1+=`<th colspan="${cols}" style="${hStyle};${bg};border-left:2px solid var(--bd)">${m}</th>`;
  }

  // Subheaders dinámicos según tipo de mes
  let hdr2='<th style="${hStyle};background:#fff;border-right:2px solid var(--bd)">Valor</th><th style="${hStyle};background:#fff">%V</th><th style="${hStyle};background:#fff;border-right:2px solid var(--bd)">%G</th>';

  const firstRow=d.rows[0];
  for(let i=0;i<meses.length;i++){
    const mes=meses[i];
    const type=firstRow.meses[i].type;
    const bg=i%2===0?'background-color:#f0f4f8':'background-color:#ffffff';
    const bLeft=`border-left:2px solid var(--bd)`;

    hdr2+=`<th style="${hStyle};${bg};${bLeft}">Monto</th>`;
    hdr2+=`<th style="${hStyle};${bg}">%V</th>`;
    hdr2+=`<th style="${hStyle};${bg}">%G</th>`;

    if(type!=='A'){
      hdr2+=`<th style="${hStyle};${bg}">Vari Rel.</th>`;

      if(type==='E'){
        hdr2+=`<th style="${hStyle};${bg}">AÑO</th>`;
        hdr2+=`<th style="${hStyle};${bg}">%V</th>`;
        hdr2+=`<th style="${hStyle};${bg}">%G</th>`;
      }else{
        hdr2+=`<th style="${hStyle};${bg}">ACUM EJEC</th>`;
        hdr2+=`<th style="${hStyle};${bg}">%V</th>`;
        hdr2+=`<th style="${hStyle};${bg}">%G</th>`;
      }

      if(type==='C' || type==='D' || type==='E'){
        hdr2+=`<th style="${hStyle};${bg}">ACUM PPTO</th>`;
        hdr2+=`<th style="${hStyle};${bg}">%V</th>`;
        hdr2+=`<th style="${hStyle};${bg}">Var PPTO</th>`;

        if(type==='D'){
          hdr2+=`<th style="${hStyle};${bg}">PROM 6 EJEC</th>`;
          hdr2+=`<th style="${hStyle};${bg}">%V</th>`;
          hdr2+=`<th style="${hStyle};${bg}">%G</th>`;
          hdr2+=`<th style="${hStyle};${bg}">PROM 6 PPTO</th>`;
          hdr2+=`<th style="${hStyle};${bg}">%V</th>`;
          hdr2+=`<th style="${hStyle};${bg}">Var PPTO</th>`;
        }
      }
    }
  }

  // Rows
  let rows='';
  // Build hierarchy mapping each row index to its parent row index
  const parentIndices = new Array(d.rows.length).fill(null);
  const stack = []; // array of {indent, index}
  
  for (let i = 0; i < d.rows.length; i++) {
    const row = d.rows[i];
    const explicitParentName = row.parent_name;
    let parentIndex = null;
    
    if (explicitParentName && explicitParentName !== 'None' && explicitParentName !== 'null') {
      parentIndex = d.rows.findIndex(r => r.partida === explicitParentName);
      if (parentIndex === -1) parentIndex = null;
    }
    
    if (parentIndex === null) {
      while (stack.length > 0 && stack[stack.length - 1].indent >= row.indent) {
        stack.pop();
      }
      if (stack.length > 0) {
        parentIndex = stack[stack.length - 1].index;
      }
    }
    
    parentIndices[i] = parentIndex;
    stack.push({ indent: row.indent, index: i });
  }

  // Determine which row indices are parents
  const isParent = new Array(d.rows.length).fill(false);
  for (let i = 0; i < d.rows.length; i++) {
    const pIdx = parentIndices[i];
    if (pIdx !== null) {
      isParent[pIdx] = true;
    }
  }

  for (let i = 0; i < d.rows.length; i++) {
    const row = d.rows[i];
    const isHdr = row.is_header;
    const isTotal = row.indent === 0;
    const useBold = row.bold || isHdr || isTotal;
    const bgColor = row.bg_color ? `#${row.bg_color.substring(2)}` : null;
    const bgColorWithAlpha = bgColor ? bgColor + '66' : '';
    
    const parentIdx = parentIndices[i];
    const hasChildren = isParent[i];
    
    const isVisibleInitially = row.indent <= 1;
    const displayStyle = isVisibleInitially ? '' : 'display:none;';
    const rStyle = displayStyle + (isHdr ? hRowStyle : (bgColorWithAlpha ? `background:${bgColorWithAlpha}` : ''));
    const boldStyle = useBold ? 'font-weight:700' : '';
    const cellBg = bgColor ? `background:${lightenHex(bgColor)}` : 'background:#fff';
    
    const padLeft = (row.indent * 12 + 8) + 'px';

    const isAlwaysExpanded = row.partida === "Total Ingresos" || row.partida === "Total Gastos Operacionales";
    let saved = null;
    try {
      saved = localStorage.getItem('eerr_expanded_' + row.partida);
    } catch (e) {
      console.error('Error reading from localStorage:', e);
    }
    const initiallyExpanded = isAlwaysExpanded || saved === '1';

    let toggleHtml = '';
    if (hasChildren && !isAlwaysExpanded) {
      const toggleChar = initiallyExpanded ? '▼' : '▶';
      toggleHtml = `<span class="eerr-toggle" onclick="toggleEERRRow(event, 'divisa-${i}')" style="cursor:pointer;margin-right:6px;display:inline-block;width:12px;font-family:monospace;color:var(--primary);font-weight:bold">${toggleChar}</span>`;
    }

    const escapedPartida = row.partida.replace(/"/g, '&quot;');
    let r = `<tr data-row-id="divisa-${i}" data-parent-id="${parentIdx !== null ? 'divisa-' + parentIdx : ''}" data-indent="${row.indent}" data-expanded="${initiallyExpanded ? 'true' : 'false'}" data-partida="${escapedPartida}" style="${rStyle}">`;
    r += `<td style="${lStyle};position:sticky;left:0;${cellBg};z-index:6;min-width:220px;width:220px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;border-right:2px solid var(--bd);padding-left:${padLeft};${boldStyle}">${toggleHtml}${row.partida}</td>`;

    r += `<td style="${cStyle};${boldStyle}">${fmtZ(row.year_prev.valor)}</td>`;
    r += `<td style="${cStyle}">${pctZ(row.year_prev.pct_vtas)}</td>`;
    r += `<td style="${cStyle};border-right:2px solid var(--bd)">${row.muestra_pct_gastos ? pctZ(row.year_prev.pct_gastos) : ''}</td>`;
    
      // Renderizar celdas según tipo de mes
    for(let i=0;i<row.meses.length;i++){
      const m=row.meses[i];
      const type=m.type;
      const bg=i%2===0?'background-color:#f0f4f8':'background-color:#ffffff';
      const bLeft='border-left:2px solid var(--bd)';

      r+=`<td style="${cStyle};${bg};${bLeft};${boldStyle}">${fmtZ(m.ejecutado.valor)}</td>`;
      r+=`<td style="${cStyle};${bg}">${pctZ(m.ejecutado.pct_vtas)}</td>`;
      r+=`<td style="${cStyle};${bg}">${row.muestra_pct_gastos ? pctZ(m.ejecutado.pct_gastos) : ''}</td>`;

      if(type!=='A'){
        r+=`<td style="${cStyle};${bg}">${varCol(m.vari_rel)}</td>`;

        if(type==='E'){
          r+=`<td style="${cStyle};${bg};${boldStyle}">${fmtZ(m.anio.valor)}</td>`;
          r+=`<td style="${cStyle};${bg}">${pctZ(m.anio.pct_vtas)}</td>`;
          r+=`<td style="${cStyle};${bg}">${row.muestra_pct_gastos ? pctZ(m.anio.pct_gastos) : ''}</td>`;
        }else{
          r+=`<td style="${cStyle};${bg};${boldStyle}">${fmtZ(m.acum_ejecutado.valor)}</td>`;
          r+=`<td style="${cStyle};${bg}">${pctZ(m.acum_ejecutado.pct_vtas)}</td>`;
          r+=`<td style="${cStyle};${bg}">${row.muestra_pct_gastos ? pctZ(m.acum_ejecutado.pct_gastos) : ''}</td>`;
        }

        if(type==='C' || type==='D' || type==='E'){
          r+=`<td style="${cStyle};${bg}">${fmtZ(m.acum_ppto.valor)}</td>`;
          r+=`<td style="${cStyle};${bg}">${pctZ(m.acum_ppto.pct_vtas)}</td>`;
          r+=`<td style="${cStyle};${bg}">${varCol(m.var_ppto)}</td>`;

          if(type==='D'){
            r+=`<td style="${cStyle};${bg}">${fmtZ(m.prom_6_ejec.valor)}</td>`;
            r+=`<td style="${cStyle};${bg}">${pctZ(m.prom_6_ejec.pct_vtas)}</td>`;
            r+=`<td style="${cStyle};${bg}">${row.muestra_pct_gastos ? pctZ(m.prom_6_ejec.pct_gastos) : ''}</td>`;
            r+=`<td style="${cStyle};${bg}">${fmtZ(m.prom_6_ppto.valor)}</td>`;
            r+=`<td style="${cStyle};${bg}">${pctZ(m.prom_6_ppto.pct_vtas)}</td>`;
            r+=`<td style="${cStyle};${bg}">${varCol(m.var_ppto_prom)}</td>`;
          }
        }
      }
    }
    r+='</tr>';
    rows+=r;
  }

  G('err-divisa-body').innerHTML=`
    <div class="tw" style="max-height:calc(100vh - 180px);overflow:auto;position:relative">
    <table class="eerr-table" style="width:100%;border-collapse:collapse">
      <thead style="position:sticky;top:0;z-index:10">
        <tr>${hdr1}</tr>
        <tr>${hdr2}</tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
    </div>
  `;
  updateEERRRowVisibility();

  // Ocultar "Utilidad Distribuible" (ya no aplica con estructura completa)
  G('utilidad-distribuible').style.display='none';
}
