// ── UPLOAD ────────────────────────────────────────────────────────────────
// ── TABS CARGA ERR/ESF ────────────────────────────────────────────────────
function switchTab(type){
  const tabs=['err','esf'];
  tabs.forEach(t=>{
    G('tab-'+t).classList.toggle('active',t===type);
    G('form-'+t).style.display=t===type?'block':'none';
  });
}

// ── CARGA ERR ──────────────────────────────────────────────────────────────
let sFileERR=null;
function onFileERR(i){
  if(!isAdmin()){alert('⛔ Acceso denegado: se requiere rol de administrador');return;}
  sFileERR=i.files[0];G('dfn-err').textContent=sFileERR?sFileERR.name:'';G('btnup-err').disabled=!sFileERR;
}
async function doUploadERR(){
  if(!isAdmin()){alert('⛔ Acceso denegado: se requiere rol de administrador');return;}
  if(!sFileERR)return;const btn=G('btnup-err');btn.disabled=true;btn.textContent='Procesando...';
  const fd=new FormData();fd.append('file',sFileERR);fd.append('unit',G('up-unit-err').value);fd.append('month',G('up-month-err').value);fd.append('year',G('up-year-err').value);fd.append('is_esf','false');
  try{const r=await fetch('/api/upload',{method:'POST',body:fd});const d=await r.json();
    if(d.exists){
      const ok=confirm(`Ya existe una carga para ${fd.get('unit')} ${fd.get('month')} ${fd.get('year')}. ¿Deseas reemplazarla?`);
      if(ok){fd.append('force','true');const r2=await fetch('/api/upload',{method:'POST',body:fd});const d2=await r2.json();if(d2.error)showA('al-er','❌ '+d2.error);else{const c=d2.conciliacion;const cMsg=c?(c.ok?' ✅ Conciliado':` ⚠️ Diferencia: $${c.diferencia.toLocaleString('es-VE',{minimumFractionDigits:2})}`):'';const fin=d2.inserted_financials||0;showA('al-ok',`✅ ${fin} cuentas de ERR importadas. Sin mapear: ${d2.skipped}.${cMsg}`);fillYears();if(d2.unmapped&&d2.unmapped.length){G('umbox-eerr').style.display='block';G('umitems-eerr').innerHTML=d2.unmapped.map(u=>`<div class="umi"><span><strong>${u.code}</strong> — ${u.name}</span><span>${fmt(u.amount)}</span></div>`).join('');}else{G('umbox-eerr').style.display='none';}}}
      else showA('al-er','❌ Carga cancelada.');
    }
    else if(d.error)showA('al-er','❌ '+d.error);
    else{
      const c=d.conciliacion;
      const cMsg=c?(c.ok?' ✅ Conciliado':` ⚠️ Diferencia: $${c.diferencia.toLocaleString('es-VE',{minimumFractionDigits:2})}`):'';
      const fin=d.inserted_financials||0;
      showA('al-ok',`✅ ${fin} cuentas de ERR importadas. Sin mapear: ${d.skipped}.${cMsg}`);
      fillYears();
      if (d.unmapped && d.unmapped.length) {
        G('umbox-eerr').style.display = 'block';
        G('umitems-eerr').innerHTML = d.unmapped.map(u =>
          `<div class="umi"><span><strong>${u.code}</strong> — ${u.name}</span><span>${fmt(u.amount)}</span></div>`
        ).join('');
      } else {
        G('umbox-eerr').style.display = 'none';
      }}
  }catch{showA('al-er','❌ Error de conexión');}
  btn.disabled=false;btn.textContent='Procesar e Importar ERR';
}

// ── CARGA ESF ──────────────────────────────────────────────────────────────
let sFileESF=null;
function onFileESF(i){
  if(!isAdmin()){alert('⛔ Acceso denegado: se requiere rol de administrador');return;}
  sFileESF=i.files[0];G('dfn-esf').textContent=sFileESF?sFileESF.name:'';G('btnup-esf').disabled=!sFileESF;
}
async function doUploadESF(){
  if(!isAdmin()){alert('⛔ Acceso denegado: se requiere rol de administrador');return;}
  if(!sFileESF)return;
  const empresaIdEsf=G('up-empresa-esf').value;
  if(!empresaIdEsf){alert('Selecciona la empresa antes de importar');return;}
  const btn=G('btnup-esf');btn.disabled=true;btn.textContent='Procesando...';
  const MONTH_MAP={'1':'MAR','2':'JUN','3':'SEPT','4':'DIC'};  // Quarter → último mes
  const fd=new FormData();fd.append('file',sFileESF);fd.append('unit','CONSOLIDADO');fd.append('month',MONTH_MAP[G('up-quarter-esf').value]);fd.append('year',G('up-year-esf').value);fd.append('is_esf','true');fd.append('empresa_id',empresaIdEsf);
  try{const r=await fetch('/api/upload',{method:'POST',body:fd});const d=await r.json();
    if(d.exists){
      const qLabel=G('up-quarter-esf').value;
      const ok=confirm(`Ya existe una carga para ESF Q${qLabel} ${G('up-year-esf').value}. ¿Deseas reemplazarla?`);
      if(ok){fd.append('force','true');const r2=await fetch('/api/upload',{method:'POST',body:fd});const d2=await r2.json();if(d2.error)showA('al-er','❌ '+d2.error);else{const esf=d2.inserted_esf||0;showA('al-ok',`✅ ${esf} cuentas de ESF importadas. Sin mapear: ${d2.skipped}.`);fillYears();if(d2.unmapped&&d2.unmapped.length){G('umbox-esf').style.display='block';G('umitems-esf').innerHTML=d2.unmapped.map(u=>`<div class="umi"><span><strong>${u.code}</strong> — ${u.name}</span><span>${fmt(u.amount)}</span></div>`).join('');}else{G('umbox-esf').style.display='none';}}}
      else showA('al-er','❌ Carga cancelada.');
    }
    else if(d.error)showA('al-er','❌ '+d.error);
    else{
      const esf=d.inserted_esf||0;
      showA('al-ok',`✅ ${esf} cuentas de ESF importadas. Sin mapear: ${d.skipped}.`);
      fillYears();
      if (d.unmapped && d.unmapped.length) {
        G('umbox-esf').style.display = 'block';
        G('umitems-esf').innerHTML = d.unmapped.map(u =>
          `<div class="umi"><span><strong>${u.code}</strong> — ${u.name}</span><span>${fmt(u.amount)}</span></div>`
        ).join('');
      } else {
        G('umbox-esf').style.display = 'none';
      }}
  }catch{showA('al-er','❌ Error de conexión');}
  btn.disabled=false;btn.textContent='Procesar e Importar ESF';
}
