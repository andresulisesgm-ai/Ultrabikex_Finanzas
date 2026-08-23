var PRINT_CHUNK = 4;
var printModeSel = 'fit';
var printEerdTabSel = 'resumen';
var printOrientSel = 'portrait';

function openPrintModal(){
  const activePage = document.querySelector('.page.active');
  const id = activePage ? activePage.id : '';
  const withOptions = ['page-eerrdet','page-esf','page-presupuesto','page-eerr','page-err_divisa','page-dashboard'].includes(id);
  if(!withOptions){ window.print(); return; }

  const splitOpt = document.getElementById('printSplitOption');
  const tabWrap = document.getElementById('printTabSelectorWrap');
  if(id === 'page-esf' || id === 'page-dashboard'){
    splitOpt.style.display = 'none';
    tabWrap.style.display = 'none';
    document.querySelector('input[name="printModeRadio"][value="fit"]').checked = true;
  } else {
    splitOpt.style.display = 'flex';
    tabWrap.style.display = (id === 'page-eerrdet') ? 'block' : 'none';
    if(id === 'page-eerrdet'){
      document.getElementById('printEerdTab').value = eerdTab;
    }
  }
  document.getElementById('printModal').style.display = 'flex';
}

function closePrintModal(){
  document.getElementById('printModal').style.display = 'none';
}

function confirmPrint(){
  printModeSel = document.querySelector('input[name="printModeRadio"]:checked').value;
  printEerdTabSel = document.getElementById('printEerdTab').value;
  closePrintModal();
  window.print();
}

window.addEventListener('beforeprint', applyPrintLayout);
window.addEventListener('afterprint', revertPrintLayout);

function getActivePrintInfo(){
  const activePage = document.querySelector('.page.active');
  if(!activePage) return null;
  if(activePage.id==='page-eerrdet') return {id:'page-eerrdet', wrap: document.querySelector('#erd-body .eerrd-wrap')};
  if(activePage.id==='page-esf') return {id:'page-esf', wrap: document.querySelector('#esf-body .esf-wrap')};
  if(activePage.id==='page-presupuesto') return {id:'page-presupuesto', wrap: document.querySelector('#bgt-body .bgt-wrap')};
  if(activePage.id==='page-eerr') return {id:'page-eerr', wrap: document.querySelector('#eerr-body .eerr-table')};
  if(activePage.id==='page-err_divisa') return {id:'page-err_divisa', wrap: document.querySelector('#err-divisa-body .eerr-table')};
  if(activePage.id==='page-dashboard') return {id:'page-dashboard', wrap: document.querySelector('#wcon')};
  return null;
}

function applyPrintLayout(){
  const info = getActivePrintInfo();
  const orientStyle = document.getElementById('dashboardPrintOrientation');
  if(orientStyle){
    orientStyle.textContent = (info && info.id === 'page-dashboard')
      ? '@media print { @page { size: letter landscape; margin: 9mm; } }'
      : '';
  }
  if(!info || !info.wrap) return;
  if(printModeSel === 'split' && info.id !== 'page-esf'){
    applySplitPages(info);
  } else {
    applyFitScale(info.wrap);
  }
}

function revertPrintLayout(){
  document.querySelectorAll('[data-print-scaled="1"]').forEach(function(el){
    el.style.zoom = '';
    el.removeAttribute('data-print-scaled');
  });
  const holder = document.getElementById('printSplitHolder');
  if(holder) holder.remove();
  document.querySelectorAll('[data-print-hidden="1"]').forEach(function(el){
    el.style.display = '';
    el.removeAttribute('data-print-hidden');
  });
}

function applyFitScale(wrap){
  const available = 1050;
  const natural = wrap.scrollWidth;
  const scale = Math.min(1, available / natural);
  if(scale < 1){
    wrap.style.zoom = scale;
    wrap.setAttribute('data-print-scaled','1');
  }
}

function chunkArr(arr, size){
  const out = [];
  for(let i=0;i<arr.length;i+=size) out.push(arr.slice(i,i+size));
  return out;
}

function applySplitPages(info){
  let pagesHtml = '';
  if(info.id === 'page-eerrdet') pagesHtml = buildEerrdSplitHtml();
  else if(info.id === 'page-presupuesto') pagesHtml = buildBgtSplitHtml();
  else if(info.id === 'page-eerr') pagesHtml = buildEerrMainSplitHtml(EERR_MAIN_DATA);
  else if(info.id === 'page-err_divisa') pagesHtml = buildEerrMainSplitHtml(EERR_DIVISA_DATA);
  if(!pagesHtml) return;

  info.wrap.style.display = 'none';
  info.wrap.setAttribute('data-print-hidden','1');

  const holder = document.createElement('div');
  holder.id = 'printSplitHolder';
  holder.innerHTML = pagesHtml;
  info.wrap.parentNode.insertBefore(holder, info.wrap.nextSibling);

  const available = 1050;
  Array.from(holder.children).forEach(function(block){
    const natural = block.scrollWidth;
    const scale = Math.min(1, available / natural);
    if(scale < 1){
      block.style.zoom = scale;
    }
  });
}

function buildEerrdSplitHtml(){
  if(!EERRD) return '';
  const tab = printEerdTabSel || 'resumen';
  const months = EERRD.months;
  const chunks = chunkArr(months, PRINT_CHUNK);
  const d = EERRD;

  return chunks.map(function(mChunk, idx){
    const cols = '220px repeat(' + mChunk.length + ', 90px) 100px 60px repeat(' + mChunk.length + ', 70px)';

    function hdrRow(){
      const mCols = mChunk.map(function(m){ return '<div class="eerrd-num" style="font-weight:700;color:var(--tx2)">' + m + '</div>'; }).join('');
      const vCols = mChunk.map(function(m){
        const gi = months.indexOf(m);
        return '<div class="eerrd-var" style="font-weight:700;color:var(--tx2)">' + (gi===0?'—':('%vs'+months[gi-1])) + '</div>';
      }).join('');
      return '<div class="eerrd-hdr" style="grid-template-columns:' + cols + '"><div>Partida</div>' + mCols + '<div class="eerrd-num">ACUM EJEC</div><div class="eerrd-pct">%Ing</div>' + vCols + '</div>';
    }

    function buildRow(row, style, indent){
      if(!row) return '';
      style = style || '';
      const mCols = mChunk.map(function(m){
        const v = row.meses[m] || 0;
        return '<div class="eerrd-num" style="' + (v<0?'color:var(--red)':'') + '">' + (v===0?'—':fmtS(v)) + '</div>';
      }).join('');
      const acum = row.acum || 0;
      const ing = d.ingresos.total.acum || 1;
      const pctIng = ing ? (acum/ing*100).toFixed(1) + '%' : '—';
      const vCols = mChunk.map(function(m){
        const gi = months.indexOf(m);
        const v = (row.var_pct||[])[gi];
        if(v===undefined || v===null || gi===0) return '<div class="eerrd-var">—</div>';
        const cls = v>=0 ? 'var-pos' : 'var-neg';
        return '<div class="eerrd-var ' + cls + '">' + (v>=0?'▲':'▼') + Math.abs(v) + '%</div>';
      }).join('');
      return '<div class="eerrd-row ' + style + '" style="grid-template-columns:' + cols + '"><div style="' + (indent?'padding-left:16px;color:var(--mu)':'font-weight:600') + '">' + row.partida + '</div>' + mCols + '<div class="eerrd-num" style="' + (acum<0?'color:var(--red)':'color:var(--blue);font-weight:700') + '">' + fmtS(acum) + '</div><div class="eerrd-pct">' + pctIng + '</div>' + vCols + '</div>';
    }

    let body = hdrRow();
    if(tab === 'resumen'){
      body += buildRow(d.ingresos.total, 'hdr-row');
      body += buildRow(d.costos.total, 'hdr-row');
      body += buildRow(d.utilidad_bruta.total, 'grand');
      body += buildRow(d.utilidad_bruta.mercancia_taller, 'section', true);
      body += buildRow(d.utilidad_bruta.servicios, 'section', true);
      body += buildRow(d.utilidad_bruta.eventos, 'section', true);
      body += buildRow(d.gastos.total, 'hdr-row');
      body += buildRow(d.utilidad_neta, 'grand');
    } else if(tab === 'mercancia'){
      body += buildRow(d.ingresos.mercancia_taller, 'hdr-row');
      body += buildRow(d.costos.mercancia_taller, 'hdr-row');
      body += buildRow(d.utilidad_bruta.mercancia_taller, 'grand');
    } else if(tab === 'servicios'){
      body += buildRow(d.ingresos.servicios, 'hdr-row');
      body += buildRow(d.costos.servicios, 'hdr-row');
      body += buildRow(d.utilidad_bruta.servicios, 'grand');
    } else if(tab === 'eventos'){
      body += buildRow(d.ingresos.eventos, 'hdr-row');
      body += buildRow(d.costos.eventos, 'hdr-row');
      body += buildRow(d.utilidad_bruta.eventos, 'grand');
    } else if(tab === 'gastos'){
      body += buildRow(d.gastos.total, 'grand');
      (d.gastos.detalle || []).forEach(function(row){ body += buildRow(row, '', true); });
    }

    const pageBreak = idx>0 ? 'page-break-before:always;' : '';
    return '<div class="eerrd-wrap" style="' + pageBreak + '">' + body + '</div>';
  }).join('');
}

function buildBgtSplitHtml(){
  if(!BGT_DATA) return '';
  const months = BGT_DATA.comparativo.length ? Object.keys(BGT_DATA.comparativo[0].meses) : [];
  const chunks = chunkArr(months, PRINT_CHUNK);

  const filters = {
    ingresos:  function(row){ return row.partida.toLowerCase().includes('ingreso') || row.partida.toLowerCase().includes('devoluc') || row.partida.toLowerCase().includes('descuento') || row.partida.toLowerCase().includes('sobrante') || row.partida.toLowerCase().includes('ganancia'); },
    costos:    function(row){ return row.partida.toLowerCase().includes('costo'); },
    gastos:    function(row){ return row.partida.toLowerCase().includes('gasto') || row.partida.toLowerCase().includes('faltante') || row.partida.toLowerCase().includes('pérdida') || row.partida.toLowerCase().includes('multa') || row.partida.toLowerCase().includes('deterioro') || row.partida.toLowerCase().includes('islr'); },
    resumen:   function(){ return true; },
  };
  const filterFn = filters[bgtTab] || filters.resumen;
  let rows = BGT_DATA.comparativo.filter(filterFn);

  if(bgtTab === 'resumen'){
    const groups = { 'Total Ingresos': filters.ingresos, 'Total Costos': filters.costos, 'Total Gastos': filters.gastos };
    const summaryRows = Object.entries(groups).map(function(entry){
      const label = entry[0], fn = entry[1];
      const matching = BGT_DATA.comparativo.filter(fn);
      const sumB = matching.reduce(function(a,r){ return a + r.acum_presupuesto; }, 0);
      const sumR = matching.reduce(function(a,r){ return a + r.acum_real; }, 0);
      const meses = {};
      months.forEach(function(m){
        const b = matching.reduce(function(a,r){ return a + (r.meses[m]?.presupuesto || 0); }, 0);
        const rv = matching.reduce(function(a,r){ return a + (r.meses[m]?.real || 0); }, 0);
        meses[m] = { presupuesto:b, real:rv, var_pct: b ? ((rv-b)/Math.abs(b)*100).toFixed(1) : null };
      });
      return { partida:label, meses:meses, acum_presupuesto:sumB, acum_real:sumR, acum_var_pct: sumB ? ((sumR-sumB)/Math.abs(sumB)*100).toFixed(1) : null, _isTotal:true };
    });
    const totI = summaryRows.find(function(r){ return r.partida==='Total Ingresos'; });
    const totC = summaryRows.find(function(r){ return r.partida==='Total Costos'; });
    const totG = summaryRows.find(function(r){ return r.partida==='Total Gastos'; });
    const unRow = { partida:'Utilidad Neta', meses:{}, acum_presupuesto:0, acum_real:0, _isGrand:true };
    if(totI && totC && totG){
      months.forEach(function(m){
        const b = (totI.meses[m]?.presupuesto||0) - (totC.meses[m]?.presupuesto||0) - (totG.meses[m]?.presupuesto||0);
        const rv = (totI.meses[m]?.real||0) - (totC.meses[m]?.real||0) - (totG.meses[m]?.real||0);
        unRow.meses[m] = { presupuesto:b, real:rv, var_pct: b ? ((rv-b)/Math.abs(b)*100).toFixed(1) : null };
      });
      unRow.acum_presupuesto = totI.acum_presupuesto - totC.acum_presupuesto - totG.acum_presupuesto;
      unRow.acum_real = totI.acum_real - totC.acum_real - totG.acum_real;
      const bp = unRow.acum_presupuesto;
      unRow.acum_var_pct = bp ? ((unRow.acum_real-bp)/Math.abs(bp)*100).toFixed(1) : null;
    }
    rows = summaryRows.concat([unRow]);
  }

  return chunks.map(function(mChunk, idx){
    const gridCols = '240px repeat(' + mChunk.length + ', 160px) 130px 130px 80px';
    const mHdrs = mChunk.map(function(m){ return '<div class="bgt-cell" style="font-weight:700;color:var(--tx2)">' + m + '</div>'; }).join('');
    let body = '<div class="bgt-hdr" style="grid-template-columns:' + gridCols + '"><div>Partida</div>' + mHdrs + '<div class="bgt-cell">ACUM Ppto.</div><div class="bgt-cell">ACUM Real</div><div class="bgt-var" style="font-weight:700">%Var</div></div>';

    rows.forEach(function(row){
      const isGrand = row._isGrand, isTotal = row._isTotal;
      const rowCls = isGrand ? 'bgt-total' : isTotal ? 'bgt-row section' : 'bgt-row';
      const mCols = mChunk.map(function(m){
        const cell = row.meses[m] || {presupuesto:0, real:0, var_pct:null};
        const vPct = cell.var_pct;
        const vHtml = vPct===null ? '—' : '<span class="' + (parseFloat(vPct)>=0?'bgt-var-ok':'bgt-var-bad') + '">' + (parseFloat(vPct)>=0?'▲':'▼') + Math.abs(parseFloat(vPct)) + '%</span>';
        return '<div class="bgt-cell"><div>' + fmtS(cell.presupuesto) + '</div><div style="color:var(--green);font-size:10px">' + fmtS(cell.real) + '</div><div style="font-size:10px">' + vHtml + '</div></div>';
      }).join('');
      const vAcum = row.acum_var_pct;
      const vAcumHtml = vAcum===null ? '—' : '<span class="' + (parseFloat(vAcum)>=0?'bgt-var-ok':'bgt-var-bad') + '">' + (parseFloat(vAcum)>=0?'▲':'▼') + Math.abs(parseFloat(vAcum)) + '%</span>';
      body += '<div class="' + rowCls + '" style="grid-template-columns:' + gridCols + '"><div style="font-weight:' + (isGrand||isTotal?'700':'400') + '">' + row.partida + '</div>' + mCols + '<div class="bgt-cell">' + fmtS(row.acum_presupuesto) + '</div><div class="bgt-cell" style="color:var(--green)">' + fmtS(row.acum_real) + '</div><div class="bgt-cell">' + vAcumHtml + '</div></div>';
    });

    const pageBreak = idx>0 ? 'page-break-before:always;' : '';
    return '<div class="bgt-wrap" style="' + pageBreak + '">' + body + '</div>';
  }).join('');
}

function buildEerrMainSplitHtml(d){
  if(!d) return '';

  const hStyle='font-size:8px;font-weight:700;text-align:center;padding:7px 4px;color:var(--mu);border:1px solid var(--bd)';
  const cStyle="font-size:8px;padding:5px 4px;text-align:right;font-family:'DM Mono',monospace;border:1px solid var(--bd)";
  const lStyle='font-size:8px;padding:6px 8px;text-align:left;border:1px solid var(--bd);white-space:nowrap';
  const hRowStyle='font-weight:700;background:var(--primary)15;color:var(--primary)';

  const fmtZ=function(v){ return (v===0||v===null) ? '' : fmt(v); };
  const pctZ=function(v){ return (v===0||v===null) ? '' : pct(v); };
  const varCol=function(v){
    if(v===null||v===0) return '';
    return v>=0 ? '<span style="color:var(--green)">▲'+pct(Math.abs(v))+'</span>' : '<span style="color:var(--red)">▼'+pct(Math.abs(v))+'</span>';
  };

  const monthCols={ 'ENE':3,'FEB':7,'MAR':10,'ABR':7,'MAY':7,'JUN':16,'JUL':7,'AGO':7,'SEPT':10,'OCT':7,'NOV':7,'DIC':10 };
  const meses=['ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEPT','OCT','NOV','DIC'];
  const chunks = chunkArr(meses, PRINT_CHUNK);

  return chunks.map(function(mChunk, pageIdx){
    let hdr1='<th rowspan="2" style="'+hStyle+';text-align:left;min-width:220px;width:220px;border-right:2px solid var(--bd)">Partida</th>';
    hdr1+='<th colspan="3" style="'+hStyle+';border-right:2px solid var(--bd)">'+d.year_prev+'</th>';
    mChunk.forEach(function(m){
      const cols = monthCols[m];
      const bg = meses.indexOf(m)%2===0 ? 'background-color:#f0f4f8' : 'background-color:#ffffff';
      hdr1 += '<th colspan="'+cols+'" style="'+hStyle+';'+bg+';border-left:2px solid var(--bd)">'+m+'</th>';
    });

    let hdr2='<th style="'+hStyle+';border-right:2px solid var(--bd)">Valor</th><th style="'+hStyle+'">%V</th><th style="'+hStyle+';border-right:2px solid var(--bd)">%G</th>';
    const firstRow = d.rows[0];
    mChunk.forEach(function(m){
      const gi = meses.indexOf(m);
      const type = firstRow.meses[gi].type;
      const bg = gi%2===0 ? 'background-color:#f0f4f8' : 'background-color:#ffffff';
      const bLeft = 'border-left:2px solid var(--bd)';
      hdr2 += '<th style="'+hStyle+';'+bg+';'+bLeft+'">Monto</th><th style="'+hStyle+';'+bg+'">%V</th><th style="'+hStyle+';'+bg+'">%G</th>';
      if(type!=='A'){
        hdr2 += '<th style="'+hStyle+';'+bg+'">Vari Rel.</th>';
        if(type==='E'){
          hdr2 += '<th style="'+hStyle+';'+bg+'">AÑO</th><th style="'+hStyle+';'+bg+'">%V</th><th style="'+hStyle+';'+bg+'">%G</th>';
        } else {
          hdr2 += '<th style="'+hStyle+';'+bg+'">ACUM EJEC</th><th style="'+hStyle+';'+bg+'">%V</th><th style="'+hStyle+';'+bg+'">%G</th>';
        }
        if(type==='C'||type==='D'||type==='E'){
          hdr2 += '<th style="'+hStyle+';'+bg+'">ACUM PPTO</th><th style="'+hStyle+';'+bg+'">%V</th><th style="'+hStyle+';'+bg+'">Var PPTO</th>';
          if(type==='D'){
            hdr2 += '<th style="'+hStyle+';'+bg+'">PROM 6 EJEC</th><th style="'+hStyle+';'+bg+'">%V</th><th style="'+hStyle+';'+bg+'">%G</th><th style="'+hStyle+';'+bg+'">PROM 6 PPTO</th><th style="'+hStyle+';'+bg+'">%V</th><th style="'+hStyle+';'+bg+'">Var PPTO</th>';
          }
        }
      }
    });

    let rows='';
    for(let i=0;i<d.rows.length;i++){
      const row = d.rows[i];
      const isHdr = row.is_header;
      const isTotal = row.indent===0;
      const useBold = row.bold || isHdr || isTotal;
      const bgColor = row.bg_color ? '#'+row.bg_color.substring(2) : null;
      const bgColorWithAlpha = bgColor ? bgColor+'66' : '';
      const rStyle = (isHdr?hRowStyle:(bgColorWithAlpha?'background:'+bgColorWithAlpha:''));
      const boldStyle = useBold ? 'font-weight:700' : '';
      const cellBg = bgColorWithAlpha ? 'background:'+bgColorWithAlpha : 'background:#fff';
      const padLeft = (row.indent*12+8)+'px';

      let r = '<tr style="'+rStyle+'">';
      r += '<td style="'+lStyle+';'+cellBg+';min-width:220px;width:220px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;border-right:2px solid var(--bd);padding-left:'+padLeft+';'+boldStyle+'">'+row.partida+'</td>';
      r += '<td style="'+cStyle+';'+boldStyle+'">'+fmtZ(row.year_prev.valor)+'</td>';
      r += '<td style="'+cStyle+'">'+pctZ(row.year_prev.pct_vtas)+'</td>';
      r += '<td style="'+cStyle+';border-right:2px solid var(--bd)">'+(row.muestra_pct_gastos?pctZ(row.year_prev.pct_gastos):'')+'</td>';

      mChunk.forEach(function(m){
        const gi = meses.indexOf(m);
        const mm = row.meses[gi];
        const type = mm.type;
        const bg = gi%2===0 ? 'background-color:#f0f4f8' : 'background-color:#ffffff';
        const bLeft = 'border-left:2px solid var(--bd)';
        r += '<td style="'+cStyle+';'+bg+';'+bLeft+';'+boldStyle+'">'+fmtZ(mm.ejecutado.valor)+'</td>';
        r += '<td style="'+cStyle+';'+bg+'">'+pctZ(mm.ejecutado.pct_vtas)+'</td>';
        r += '<td style="'+cStyle+';'+bg+'">'+(row.muestra_pct_gastos?pctZ(mm.ejecutado.pct_gastos):'')+'</td>';
        if(type!=='A'){
          r += '<td style="'+cStyle+';'+bg+'">'+varCol(mm.vari_rel)+'</td>';
          if(type==='E'){
            r += '<td style="'+cStyle+';'+bg+';'+boldStyle+'">'+fmtZ(mm.anio.valor)+'</td>';
            r += '<td style="'+cStyle+';'+bg+'">'+pctZ(mm.anio.pct_vtas)+'</td>';
            r += '<td style="'+cStyle+';'+bg+'">'+(row.muestra_pct_gastos?pctZ(mm.anio.pct_gastos):'')+'</td>';
          } else {
            r += '<td style="'+cStyle+';'+bg+';'+boldStyle+'">'+fmtZ(mm.acum_ejecutado.valor)+'</td>';
            r += '<td style="'+cStyle+';'+bg+'">'+pctZ(mm.acum_ejecutado.pct_vtas)+'</td>';
            r += '<td style="'+cStyle+';'+bg+'">'+(row.muestra_pct_gastos?pctZ(mm.acum_ejecutado.pct_gastos):'')+'</td>';
          }
          if(type==='C'||type==='D'||type==='E'){
            r += '<td style="'+cStyle+';'+bg+'">'+fmtZ(mm.acum_ppto.valor)+'</td>';
            r += '<td style="'+cStyle+';'+bg+'">'+pctZ(mm.acum_ppto.pct_vtas)+'</td>';
            r += '<td style="'+cStyle+';'+bg+'">'+varCol(mm.var_ppto)+'</td>';
            if(type==='D'){
              r += '<td style="'+cStyle+';'+bg+'">'+fmtZ(mm.prom_6_ejec.valor)+'</td>';
              r += '<td style="'+cStyle+';'+bg+'">'+pctZ(mm.prom_6_ejec.pct_vtas)+'</td>';
              r += '<td style="'+cStyle+';'+bg+'">'+(row.muestra_pct_gastos?pctZ(mm.prom_6_ejec.pct_gastos):'')+'</td>';
              r += '<td style="'+cStyle+';'+bg+'">'+fmtZ(mm.prom_6_ppto.valor)+'</td>';
              r += '<td style="'+cStyle+';'+bg+'">'+pctZ(mm.prom_6_ppto.pct_vtas)+'</td>';
              r += '<td style="'+cStyle+';'+bg+'">'+varCol(mm.var_ppto_prom)+'</td>';
            }
          }
        }
      });
      r += '</tr>';
      rows += r;
    }

    const pageBreak = pageIdx>0 ? 'page-break-before:always;' : '';
    return '<div style="'+pageBreak+'"><table class="eerr-table" style="width:100%;border-collapse:collapse"><thead><tr>'+hdr1+'</tr><tr>'+hdr2+'</tr></thead><tbody>'+rows+'</tbody></table></div>';
  }).join('');
}
