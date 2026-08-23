async function cargarMetodosPago(){
  const year=G('metodos-year').value, month=G('metodos-month').value;
  G('metodos-loading').style.display='block';
  G('metodos-container').style.display='none';

  // Obtener todas las cuentas del mapping
  const rMap=await fetch('/api/mapping');
  const allCuentas=await rMap.json();

  // Filtrar solo cuentas 4.x/5.x/6.x (EERR), eliminar 1.x/2.x/3.x (ESF)
  const cuentas=allCuentas.filter(c=>(c.odoo_code.startsWith('4')||c.odoo_code.startsWith('5')||c.odoo_code.startsWith('6'))&&c.odoo_code.split('.').length-1===4);

  // Obtener % Cash ya configurados para este período
  const rMet=await fetch(`/api/metodo_pago?year=${year}&month=${month}`);
  const metodos=rMet.ok?await rMet.json():[];

  // Dict: (unit, odoo_code) -> pct_cash
  const metMap={};
  for(const m of metodos){metMap[`${m.unit}_${m.odoo_code}`]=m.pct_cash;}

  // Renderizar tabla
  const units={{ units|tojson }};
  let html='';
  for(const c of cuentas){
    const tipo=c.odoo_code.startsWith('4')?'ING':(c.odoo_code.startsWith('5')?'COS':'GAS');
    html+=`<tr><td style="font-family:'DM Mono';font-size:10px">${c.odoo_code}</td><td style="font-size:10px">${c.odoo_name}</td><td style="font-size:10px;font-weight:600;color:${tipo==='ING'?'var(--primary)':'var(--amber)'}">${tipo}</td>`;
    for(const u of units){
      const key=`${u}_${c.odoo_code}`;
      const pct=metMap[key]!=null?metMap[key]:100;
      html+=`<td><input type="number" class="pct-input" data-unit="${u}" data-code="${c.odoo_code}" value="${pct}" min="0" max="100" step="0.01" style="font-size:10px;padding:3px 5px;width:60px;text-align:right">%</td>`;
    }
    html+='</tr>';
  }
  G('metodos-tbody').innerHTML=html;
  G('metodos-loading').style.display='none';
  G('metodos-container').style.display='block';
}

function filtrarMetodos(){
  const q = G('metodos-buscador').value.trim().toLowerCase();
  const rows = document.querySelectorAll('#metodos-tbody tr');
  for(const row of rows){
    const codigo = row.cells[0]?.textContent.toLowerCase() || '';
    const nombre = row.cells[1]?.textContent.toLowerCase() || '';
    row.style.display = (codigo.includes(q) || nombre.includes(q)) ? '' : 'none';
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
  if(d.ok){showA('al-metodos-ok',`✅ ${d.inserted} configuraciones guardadas`);}
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
