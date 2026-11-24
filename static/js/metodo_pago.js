const METODOS_MONTHS = ['ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEPT','OCT','NOV','DIC'];
let _metodosResumenCache = { year: null, meses: {} };

async function cargarResumenMetodos(year){
  try{
    const r = await fetch(`/api/metodo_pago/resumen?year=${year}`);
    if(r.ok){
      const d = await r.json();
      _metodosResumenCache = { year: String(year), meses: d.meses || {} };
    } else {
      _metodosResumenCache = { year: String(year), meses: {} };
    }
  } catch(e){
    _metodosResumenCache = { year: String(year), meses: {} };
  }
  renderMesesBar();
}

function seleccionarMesMetodos(m){
  G('metodos-month').value = m;
  cargarMetodosPago();
}

function renderMesesBar(){
  const year = G('metodos-year').value;
  const activeMonth = G('metodos-month').value;
  const meses = (_metodosResumenCache.year === String(year) ? _metodosResumenCache.meses : {}) || {};
  const bar = G('metodos-meses-bar');
  if(bar){
    let pillsHtml = '';
    for(const m of METODOS_MONTHS){
      const info = meses[m] || { modificados: 0, total: 0 };
      const isActive = m === activeMonth;
      const isMod = (info.modificados || 0) > 0;
      pillsHtml += `<button type="button" class="mes-pill${isActive ? ' active' : ''}${isMod ? ' mod' : ''}" onclick="seleccionarMesMetodos('${m}')">${isMod ? '<span class="mes-dot"></span>' : ''}${m}${isMod ? `<span class="mes-cnt">(${info.modificados})</span>` : ''}</button>`;
    }
    bar.innerHTML = pillsHtml;
  }
  const sel = G('metodos-month');
  if(sel){
    for(const opt of sel.options){
      const info = meses[opt.value];
      opt.textContent = (info && info.modificados > 0) ? `${opt.value} ● (${info.modificados})` : opt.value;
    }
  }
}

function renderResumenMesActual(pendienteGuardar){
  const bar = G('metodos-resumen-bar');
  if(!bar) return;
  const year = G('metodos-year').value;
  const month = G('metodos-month').value;
  const rows = document.querySelectorAll('#metodos-tbody tr');
  let modCeldas = 0;
  let cuentasMod = 0;
  for(const tr of rows){
    let rowHasMod = false;
    const inputs = tr.querySelectorAll('.pct-input');
    for(const inp of inputs){
      const val = parseFloat(inp.value);
      if(!isNaN(val) && val !== 100){
        modCeldas++;
        rowHasMod = true;
      }
    }
    if(rowHasMod) cuentasMod++;
  }
  const info = (_metodosResumenCache.year === String(year) && _metodosResumenCache.meses[month]) ? _metodosResumenCache.meses[month] : {};
  const badgeHtml = modCeldas > 0
    ? `<span class="metodos-badge-mod">● ${modCeldas} ajustes en ${cuentasMod} cuentas</span>`
    : `<span class="metodos-badge-clean">Sin ajustes (100% Cash)</span>`;
  const fechaTxt = info.ultima_fecha ? info.ultima_fecha : '—';
  const userTxt = info.ultimo_usuario ? ` · ${escAttr(info.ultimo_usuario)}` : '';
  const pendTxt = pendienteGuardar ? ' <span style="color:#b45309;font-weight:700">· Cambios sin guardar</span>' : '';
  bar.innerHTML = `<div>${badgeHtml}${pendTxt}</div><div style="color:var(--mu)">Último cambio (${month} ${year}): <strong>${fechaTxt}</strong>${userTxt}</div>`;
  bar.style.display = 'flex';
}

function onPctInputChange(inp){
  const val = parseFloat(inp.value);
  const isMod = !isNaN(val) && val !== 100;
  inp.classList.toggle('pct-mod', isMod);
  const tr = inp.closest('tr');
  if(tr){
    tr.dataset.mod = tr.querySelector('.pct-input.pct-mod') ? '1' : '0';
  }
  renderResumenMesActual(true);
}

async function cargarMetodosPago(){
  const year=G('metodos-year').value, month=G('metodos-month').value;
  G('metodos-loading').style.display='block';
  G('metodos-container').style.display='none';

  const [rMap, rMet] = await Promise.all([
    fetch('/api/mapping'),
    fetch(`/api/metodo_pago?year=${year}&month=${month}`),
    cargarResumenMetodos(year),
  ]);
  const allCuentas=await rMap.json();

  // Filtrar solo cuentas 4.x/5.x/6.x (EERR), eliminar 1.x/2.x/3.x (ESF)
  const cuentas=allCuentas.filter(c=>(c.odoo_code.startsWith('4')||c.odoo_code.startsWith('5')||c.odoo_code.startsWith('6'))&&c.odoo_code.split('.').length-1===4);

  const metodos=rMet.ok?await rMet.json():[];

  // Dict: (unit, odoo_code) -> pct_cash
  const metMap={};
  for(const m of metodos){metMap[`${m.unit}_${m.odoo_code}`]=m.pct_cash;}

  // Renderizar tabla
  const units=window.units;
  let html='';
  for(const c of cuentas){
    const tipo=c.odoo_code.startsWith('4')?'ING':(c.odoo_code.startsWith('5')?'COS':'GAS');
    let rowMod=false;
    let cellsHtml='';
    for(const u of units){
      const key=`${u}_${c.odoo_code}`;
      const pct=metMap[key]!=null?metMap[key]:100;
      const isMod=parseFloat(pct)!==100;
      if(isMod)rowMod=true;
      cellsHtml+=`<td><input type="number" class="pct-input${isMod?' pct-mod':''}" data-unit="${u}" data-code="${c.odoo_code}" value="${pct}" min="0" max="100" step="0.01" oninput="onPctInputChange(this)" style="font-size:10px;padding:3px 5px;width:60px;text-align:right">%</td>`;
    }
    html+=`<tr data-mod="${rowMod?'1':'0'}"><td class="col-fix-1" style="font-family:'DM Mono';font-size:10px">${c.odoo_code}</td><td class="col-fix-2" style="font-size:10px" title="${escAttr(c.odoo_name)}">${c.odoo_name}</td><td style="font-size:10px;font-weight:600;text-align:center;color:${tipo==='ING'?'var(--primary)':'var(--amber)'}">${tipo}</td>${cellsHtml}</tr>`;
  }
  G('metodos-tbody').innerHTML=html;
  G('metodos-loading').style.display='none';
  G('metodos-container').style.display='block';
  filtrarMetodos();
  renderMesesBar();
  renderResumenMesActual(false);
}

function filtrarMetodos(){
  const q = G('metodos-buscador').value.trim().toLowerCase();
  const soloMod = G('metodos-solo-mod')?.checked || false;
  const rows = document.querySelectorAll('#metodos-tbody tr');
  for(const row of rows){
    const codigo = row.cells[0]?.textContent.toLowerCase() || '';
    const nombre = row.cells[1]?.textContent.toLowerCase() || '';
    const matchText = codigo.includes(q) || nombre.includes(q);
    const matchMod = !soloMod || row.dataset.mod === '1';
    row.style.display = (matchText && matchMod) ? '' : 'none';
  }
}

async function guardarMetodos(){
  const year=G('metodos-year').value, month=G('metodos-month').value;
  const inputs=document.querySelectorAll('.pct-input');
  const metodos=[];
  for(const inp of inputs){
    const pct=parseFloat(inp.value)||0;
    metodos.push({unit:inp.dataset.unit,odoo_code:inp.dataset.code,pct_cash:pct});
  }
  const r=await fetch('/api/metodo_pago',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({year,month,metodos})});
  const d=await r.json();
  if(d.ok){
    showA('al-metodos-ok',`✅ ${d.inserted} configuraciones guardadas`);
    await cargarResumenMetodos(year);
    renderResumenMesActual(false);
  }
  else{showA('al-metodos-er','❌ '+d.error);}
}

function toggleCopiarDropdown(){
  const dd=G('copiar-dropdown');
  if(!dd)return;
  dd.style.display=dd.style.display==='none'?'block':'none';
}

function toggleCopiarTodas(el){
  document.querySelectorAll('.cop-unit').forEach(c=>c.checked=el.checked);
  actualizarBtnCopiar();
}

function actualizarBtnCopiar(){
  const selected=Array.from(document.querySelectorAll('.cop-unit:checked'));
  const allCb=G('cop-unit-all');
  const allUnits=document.querySelectorAll('.cop-unit');
  if(allCb)allCb.checked=selected.length===allUnits.length&&allUnits.length>0;
  const btn=G('copiar-confirmar-btn');
  if(!btn)return;
  if(selected.length>0){
    btn.disabled=false;btn.style.opacity='1';btn.style.cursor='pointer';
  } else {
    btn.disabled=true;btn.style.opacity='0.4';btn.style.cursor='not-allowed';
  }
}

document.addEventListener('click',function(e){
  const wrap=G('copiar-dropdown-wrap');
  if(wrap&&!wrap.contains(e.target)){
    const dd=G('copiar-dropdown');
    if(dd)dd.style.display='none';
  }
});

async function ejecutarCopiarMetodos(){
  const selected=Array.from(document.querySelectorAll('.cop-unit:checked')).map(c=>c.value);
  if(!selected.length){showA('al-metodos-er','Selecciona al menos una unidad.');return;}
  const allUnits=document.querySelectorAll('.cop-unit');
  const esTotal=selected.length===allUnits.length;
  const year=G('metodos-year').value, month=G('metodos-month').value;
  const MONTHS=['ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEPT','OCT','NOV','DIC'];
  const idx=MONTHS.indexOf(month);
  let from_month,from_year;
  if(idx===0){from_month='DIC';from_year=String(parseInt(year)-1);}
  else{from_month=MONTHS[idx-1];from_year=year;}
  const unitsLabel=esTotal?'todas las unidades':selected.join(', ');
  if(!confirm('¿Copiar configuración de '+from_month+' '+from_year+' para '+unitsLabel+'? Esto sobreescribirá los valores actuales.'))return;
  const body={from_year,from_month,to_year:year,to_month:month};
  if(!esTotal)body.units=selected;
  const r=await fetch('/api/metodo_pago/copiar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const d=await r.json();
  const dd=G('copiar-dropdown');
  if(dd)dd.style.display='none';
  if(d.ok){showA('al-metodos-ok','✅ '+d.copied+' métodos copiados desde '+from_month+' '+from_year+' para '+unitsLabel);cargarMetodosPago();}
  else{showA('al-metodos-er','❌ '+d.error);}
}
