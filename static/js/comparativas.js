// ── COMPARATIVAS ──────────────────────────────────────────────────────────
async function loadCmp(){
  const year=G('cmp-year').value, unit=G('cmp-unit').value;
  const empresaParam = (CURRENT_EMPRESA_ID !== null && CURRENT_EMPRESA_ID !== undefined) ? `&empresa_id=${CURRENT_EMPRESA_ID}` : '';
  const r=await fetch(`/api/comparativa?year=${year}&unit=${unit}${empresaParam}`);
  const d=await r.json();
  const {actual:a,anterior:p,year:y,prev:py}=d;
  function delta(cur,ant){if(!ant)return'—';const pct2=(cur-ant)/Math.abs(ant)*100;const col=pct2>=0?'var(--green)':'var(--red)';return`<span style="color:${col};font-weight:600">${pct2>=0?'▲':'▼'} ${Math.abs(pct2).toFixed(1)}%</span>`;}
  function row(label,cur,ant,isP=false){
    const f=isP?pct:fmt;
    const pctChg=ant?((cur-ant)/Math.abs(ant)*100):null;
    const col=pctChg!=null?(pctChg>=0?'var(--green)':'var(--red)'):'var(--mu)';
    const arr=pctChg!=null?(pctChg>=0?'▲':'▼'):'';
    const pctTxt=pctChg!=null?`<span style="color:${col};font-weight:600">${arr} ${Math.abs(pctChg).toFixed(1)}%</span>`:'—';
    return`<tr><td style="font-weight:600">${label}</td><td style="text-align:right;font-family:'DM Mono'">${f(cur)}</td><td style="text-align:right;font-family:'DM Mono';color:var(--mu)">${f(ant)}</td><td style="text-align:right">${pctTxt}</td></tr>`;
  }
  G('cmp-body').innerHTML=`
    <div class="tw" style="margin-bottom:14px">
    <table><thead><tr><th>Indicador</th><th style="text-align:right">${y}</th><th style="text-align:right">${py}</th><th style="text-align:right">Variación</th></tr></thead>
    <tbody>
      ${row('Ingresos',a.ingresos,p.ingresos)}
      ${row('Costos',a.costos,p.costos)}
      ${row('Utilidad Bruta',a.utilidad_bruta,p.utilidad_bruta)}
      ${row('Gastos Operativos',a.gastos,p.gastos)}
      ${row('Utilidad Neta',a.utilidad_neta,p.utilidad_neta)}
      ${row('Margen Bruto %',a.margen_bruto,p.margen_bruto,true)}
      ${row('Margen Neto %',a.margen_neto,p.margen_neto,true)}
    </tbody></table></div>
    <div style="font-size:11px;font-weight:700;margin-bottom:8px;color:var(--mu)">Evolución Mensual — Ingresos</div>
    <div style="position:relative;height:180px"><canvas id="ch-cmp"></canvas></div>`;
  setTimeout(()=>{
    if(CH['ch-cmp'])CH['ch-cmp'].destroy();
    const ctx=G('ch-cmp');if(!ctx)return;
    CH['ch-cmp']=new Chart(ctx.getContext('2d'),{type:'line',data:{labels:d.meses_actual.map(m=>m.month),datasets:[
      {label:String(y),data:d.meses_actual.map(m=>m.ingresos),borderColor:'#2563eb',backgroundColor:'rgba(37,99,235,.08)',tension:.4,fill:true,pointRadius:3,pointBackgroundColor:'#2563eb',pointBorderColor:'#fff',pointBorderWidth:2},
      {label:String(py),data:d.meses_anterior.map(m=>m.ingresos),borderColor:'#94a3b8',backgroundColor:'rgba(148,163,184,.06)',tension:.4,fill:true,pointRadius:3,pointBackgroundColor:'#94a3b8',pointBorderColor:'#fff',pointBorderWidth:2,borderDash:[4,3]},
    ]},options:cOpts()});
  },60);
}
