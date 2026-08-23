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
