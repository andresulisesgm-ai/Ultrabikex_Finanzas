// ── DATOS ─────────────────────────────────────────────────────────────────
async function loadData(){
  const y=G('d-year').value, u=G('d-unit').value, m=G('d-month').value, rpt=G('d-report').value, emp=G('d-empresa').value;
  let url=`/api/data?year=${y}`;
  if(u)   url+=`&unit=${u}`;
  if(m)   url+=`&month=${m}`;
  if(rpt) url+=`&report_type=${rpt}`;
  if(emp) url+=`&empresa_id=${emp}`;
  const r=await fetch(url); const data=await r.json();
  const isAdmin=document.body.dataset.role==='admin';
  G('th-acciones').style.display=isAdmin?'':'none';
  const empresasById={}; EMPRESAS_CACHE.forEach(function(e){ empresasById[e.id]=e.nombre_corto; });
  G('dbody').innerHTML=data.map(row=>{
    const overrideBadge=row.has_override
      ?`<span title="Modificado: ${row.override_last.timestamp} | Anterior: ${fmt(row.override_last.valor_anterior)}" style="margin-left:4px;color:var(--amber);font-size:10px;cursor:help">✎</span>`
      :'';
    const empresaLabel=row.empresa_id ? (empresasById[row.empresa_id]||row.empresa_id) : '—';
    const acciones=isAdmin?`<td style="text-align:center;white-space:nowrap">
      <button class="btnm" style="padding:2px 7px;font-size:11px" onclick="editarOverride('${row.year}','${row.month}','${row.unit}','${row.odoo_code}',${row.amount_sign},${row.empresa_id===null?'null':row.empresa_id})">Editar</button>
      ${row.has_override?`<button class="btnm" style="padding:2px 7px;font-size:11px;margin-left:3px;background:var(--amber-l);color:var(--amber)" onclick="deshacerOverride('${row.year}','${row.month}','${row.unit}','${row.odoo_code}',${row.empresa_id===null?'null':row.empresa_id})">Deshacer</button>`:''}
    </td>`:'';
    return `<tr ${row.has_override?'style="background:var(--amber-l)"':''}>
      <td>${row.year}</td>
      <td>${row.month}</td>
      <td><span class="chip" style="background:var(--indigo-l,#e0e7ff);color:var(--indigo,#4338ca)">${empresaLabel}</span></td>
      <td><span class="chip chb">${row.unit}</span></td>
      <td style="font-family:'DM Mono';font-size:11px">${row.odoo_code}</td>
      <td style="color:var(--mu)">${row.odoo_name||''}</td>
      <td style="color:var(--mu)">${row.partida}</td>
      <td><span class="chip" style="background:${row.report_type==='eerr'?'var(--blue-l)':'var(--green-l)'};color:${row.report_type==='eerr'?'var(--blue)':'var(--green)'}">${row.report_type.toUpperCase()}</span></td>
      <td style="text-align:right;font-weight:600;font-family:'DM Mono'">${fmt(row.amount_sign)}${overrideBadge}</td>
      ${acciones}
    </tr>`;
  }).join('');
}

async function editarOverride(year,month,unit,odoo_code,amount_actual,empresa_id){
  const nuevo=prompt(`Valor actual: ${fmt(amount_actual)}\nIngresa el nuevo valor:`,amount_actual);
  if(nuevo===null||nuevo==='') return;
  const valor_nuevo=parseFloat(nuevo.replace(',','.'));
  if(isNaN(valor_nuevo)){alert('Valor inválido'); return;}
  const r=await fetch('/api/data/override',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({year,month,unit,odoo_code,valor_nuevo,empresa_id})});
  const d=await r.json();
  if(d.ok){loadData();}else{alert('Error: '+(d.error||'desconocido'));}
}

async function deshacerOverride(year,month,unit,odoo_code,empresa_id){
  if(!confirm('¿Deshacer el último cambio manual en esta cuenta?')) return;
  const r=await fetch('/api/data/override/undo',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({year,month,unit,odoo_code,empresa_id})});
  const d=await r.json();
  if(d.ok){loadData();}else{alert('Error: '+(d.error||'desconocido'));}
}
