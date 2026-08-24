// ── HISTORY ───────────────────────────────────────────────────────────────
async function loadHist(){
  const res=await fetch('/api/history');const data=await res.json();
  if(!data.length){G('histlist').innerHTML='<p style="color:var(--mu);font-size:12px;padding:12px 0">No hay cargas.</p>';return;}
  G('histlist').innerHTML=data.map(h=>{
    const sustituida=h.superseded_by!=null;
    const dot=h.reverted?'rev':sustituida?'sup':'';
    const sustituidaPor=sustituida?data.find(x=>x.id===h.superseded_by):null;
    const subLabel=h.reverted?'⚠️ Revertida — ':sustituida?`🔄 Sustituida por ${sustituidaPor?sustituidaPor.unit+' — '+sustituidaPor.month+' '+sustituidaPor.year:''} el ${h.superseded_at} — `:'';
    const accion=h.reverted?'<span style="color:var(--red);font-size:11px;font-weight:600">Revertida</span>':sustituida?'<span style="color:var(--mu);font-size:11px;font-weight:600">Sustituida</span>':`<button class="btnd" onclick="revert(${h.id})">↩ Revertir</button>`;
    return `<div class="hi"><div class="hdot ${dot}"></div><div class="hinf"><div class="htit">${h.unit} — ${h.month} ${h.year} <span style="font-weight:400;color:var(--mu)">(${h.inserted} cuentas)</span></div><div class="hsub">${subLabel}${h.created_at}</div></div><div>${accion}</div></div>`;
  }).join('');
}
async function revert(id){if(!confirm('¿Revertir esta carga?'))return;const r=await fetch(`/api/history/${id}/revert`,{method:'POST'});const d=await r.json();if(d.ok)loadHist();else alert('Error: '+d.error);}
