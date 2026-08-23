// ── CHARTS ────────────────────────────────────────────────────────────────
function cOpts(ex={}){
  return{responsive:true,maintainAspectRatio:false,animation:{duration:500,easing:'easeInOutQuart'},
    plugins:{legend:{position:'bottom',labels:{color:'#64748b',font:{size:10,family:'DM Sans'},boxWidth:10,padding:11}},
      tooltip:{backgroundColor:'rgba(255,255,255,.97)',titleColor:'#0f172a',bodyColor:'#334155',borderColor:'#e2e8f0',borderWidth:1,padding:9,cornerRadius:7,titleFont:{size:11,weight:'700',family:'DM Sans'},bodyFont:{size:11,family:'DM Mono'},
        callbacks:{label:ctx=>{const v=ctx.parsed.y??ctx.raw;return typeof v==='number'?` ${ctx.dataset.label||ctx.label}: $${Number(v).toLocaleString('es-VE',{minimumFractionDigits:2})}`:` ${ctx.label}: $${Number(ctx.raw).toLocaleString('es-VE',{minimumFractionDigits:2})}`;}}}},
    scales:{x:{grid:{color:'rgba(0,0,0,.04)'},ticks:{color:'#94a3b8',font:{size:10}}},
            y:{grid:{color:'rgba(0,0,0,.06)'},ticks:{color:'#94a3b8',font:{size:10},callback:v=>'$'+(Math.abs(v)>=1e6?(v/1e6).toFixed(1)+'M':Math.abs(v)>=1e3?(v/1e3).toFixed(0)+'K':v)}}},
    ...ex};
}
function mk(id,type,labels,datasets,ex={}){
  if(CH[id])CH[id].destroy();
  const ctx=G(id);if(!ctx)return;
  const isR=type==='doughnut'||type==='pie'||type==='radar';
  const base=isR?{responsive:true,maintainAspectRatio:false,animation:{duration:500},
    plugins:{legend:{position:'bottom',labels:{color:'#64748b',font:{size:10,family:'DM Sans'},boxWidth:10,padding:10}},
      tooltip:{backgroundColor:'rgba(255,255,255,.97)',titleColor:'#0f172a',bodyColor:'#334155',borderColor:'#e2e8f0',borderWidth:1,padding:9,cornerRadius:7,bodyFont:{family:'DM Mono'},
        callbacks:{label:ctx=>{if(type==='radar')return` ${ctx.dataset.label}`;return` ${ctx.label}: $${Number(ctx.raw).toLocaleString('es-VE',{minimumFractionDigits:2})} (${(ctx.parsed/ctx.dataset.data.reduce((a,b)=>a+b,0)*100).toFixed(1)}%)`;}}}}}:cOpts();
  CH[id]=new Chart(ctx.getContext('2d'),{type,data:{labels,datasets},options:{...base,...ex}});
}

// Crea un chart respetando el tipo preferido por el usuario (persistido) y
// registra su spec para poder reconstruirlo al cambiar de tipo (#5 adaptabilidad).
const CHART_SPECS={};
function mkPref(id,defType,labels,datasets,ex,types){
  types=types||[defType];
  CHART_SPECS[id]={defType,labels,datasets,ex:ex||{},types};
  let t=LS.get('ct_'+id,defType); if(!types.includes(t))t=defType;
  const sel=G('ct-'+id); if(sel)sel.value=t;
  mk(id,t,labels,datasets,ex||{});
}
function setChartType(id,t){
  const s=CHART_SPECS[id]; if(!s)return;
  if(!s.types.includes(t))t=s.defType;
  LS.set('ct_'+id,t);
  mk(id,t,s.labels,s.datasets,s.ex);
  scheduleMasonry();
}
