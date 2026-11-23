// ── BACKUP / RESTORE ──────────────────────────────────────────────────────
function onRF(i){sRF=i.files[0];G('rfn').textContent=sRF?sRF.name:'';G('btnrs').disabled=!sRF;}
async function doRestore(){
  if(!isAdmin()){alert('⛔ Acceso denegado: se requiere rol de administrador');return;}
  if(!sRF)return;if(!confirm('⚠️ Reemplazará TODOS los datos. ¿Continuar?'))return;
  const btn=G('btnrs');btn.disabled=true;btn.textContent='Restaurando...';
  const fd=new FormData();fd.append('file',sRF);
  try{const r=await fetch('/api/restore',{method:'POST',body:fd});const d=await r.json();
    if(d.ok)showA('bk-ok','✅ '+d.message);else showA('bk-er','❌ '+d.error);
  }catch{showA('bk-er','❌ Error de conexión');}
  btn.disabled=false;btn.textContent='↺ Restaurar';
}

function _bkEsc(s){
  if(typeof escAttr==='function')return escAttr(s);
  return String(s==null?'':s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/'/g,'&#39;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

async function loadAutoBackups(){
  const card=document.getElementById('bk-auto-card');
  const wrap=document.getElementById('bk-auto-wrap');
  if(!card||!wrap)return;
  if(typeof isAdmin==='function'&&!isAdmin()){
    card.style.display='none';
    return;
  }
  card.style.display='block';
  wrap.innerHTML='<div style="font-size:12px;color:var(--mu)">Cargando respaldos...</div>';
  try{
    const r=await fetch('/api/backup/auto/list');
    const data=await r.json();
    if(!r.ok){
      wrap.innerHTML=`<div style="font-size:12px;color:#b91c1c">${_bkEsc(data.error||'Error cargando respaldos')}</div>`;
      return;
    }
    if(!Array.isArray(data)||!data.length){
      wrap.innerHTML='<div style="font-size:12px;color:var(--mu)">Aún no hay respaldos automáticos generados.</div>';
      return;
    }
    const rows=data.map(it=>`
      <tr style="border-bottom:1px solid var(--border,#f1f5f9)">
        <td style="padding:7px 8px">${_bkEsc(it.fecha_ve)}</td>
        <td style="padding:7px 8px;font-family:monospace">${_bkEsc(it.filename)}</td>
        <td style="padding:7px 8px;text-align:right">${Number(it.size_mb).toFixed(2)} MB</td>
        <td style="padding:7px 8px;display:flex;gap:6px">
          <button style="padding:4px 9px;font-size:11px;border:1px solid var(--border,#cbd5e1);border-radius:6px;background:#fff;cursor:pointer" onclick="window.location.href='/api/backup/auto/download/${encodeURIComponent(it.filename)}'">⬇ Descargar</button>
          <button style="padding:4px 9px;font-size:11px;border:1px solid var(--border,#cbd5e1);border-radius:6px;background:#fff;cursor:pointer" onclick="restoreAutoBackup('${_bkEsc(it.filename)}')">↺ Restaurar</button>
        </td>
      </tr>
    `).join('');
    wrap.innerHTML=`
      <table style="width:100%;border-collapse:collapse;font-size:12px">
        <thead>
          <tr style="text-align:left;border-bottom:1px solid var(--border,#e2e8f0);color:var(--mu)">
            <th style="padding:6px 8px">Fecha/Hora (VE)</th>
            <th style="padding:6px 8px">Archivo</th>
            <th style="padding:6px 8px;text-align:right">Tamaño</th>
            <th style="padding:6px 8px">Acciones</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    `;
  }catch(e){
    wrap.innerHTML='<div style="font-size:12px;color:#b91c1c">Error de conexión al listar respaldos.</div>';
  }
}

async function restoreAutoBackup(filename){
  if(typeof isAdmin==='function'&&!isAdmin()){alert('⛔ Acceso denegado: se requiere rol de administrador');return;}
  if(!confirm('⚠️ Vas a restaurar el respaldo automático '+filename+'. Esto reemplazará TODOS los datos actuales (se guardará una copia .bk). ¿Continuar?'))return;
  if(!confirm('Confirmación final: ¿seguro que deseas sobrescribir la base de datos actual con '+filename+'?'))return;
  try{
    const r=await fetch(`/api/backup/auto/restore/${encodeURIComponent(filename)}`,{method:'POST'});
    const d=await r.json();
    if(r.ok&&d.ok)showA('bk-ok','✅ '+d.message);
    else showA('bk-er','❌ '+(d.error||'Error al restaurar'));
  }catch(e){
    showA('bk-er','❌ Error de conexión');
  }
}
