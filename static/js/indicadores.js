async function loadIndicadores(){
  const year=G('ind-year').value;
  const endpointInd = modoDivisaRealInd ? '/api/indicadores/divisa_real' : '/api/indicadores';
  const r=await fetch(`${endpointInd}?year=${year}&empresa_id=${CURRENT_EMPRESA_ID||''}`);
  if(!r.ok){
    const err=await r.json();
    G('ind-body').innerHTML=`<div style="padding:30px;text-align:center;color:var(--red)">⚠️ ${err.error||'Error cargando indicadores'}</div>`;
    return;
  }
  const d=await r.json();
  const inds=d.indicadores||[];
  if(!inds.length){
    G('ind-body').innerHTML=`<div style="padding:30px;text-align:center;color:var(--mu)">Sin datos para ${year}</div>`;
    return;
  }

  const ys=G('ind-year').value;
  const yp=String(parseInt(ys)-1);

  const hStyle='font-size:11px;font-weight:700;text-align:center;padding:9px 6px;color:var(--mu);border:1px solid var(--bd);background:var(--sf)';
  const cStyle="font-size:11px;padding:7px 6px;text-align:right;font-family:'DM Mono',monospace;border:1px solid var(--bd)";
  const lStyle='font-size:11px;padding:8px 10px;text-align:left;border:1px solid var(--bd);white-space:nowrap;min-width:260px';

  function fmtInd(v, esPct, esRatio){
    if(v===null||v===undefined) return '<span style="color:var(--mu)">—</span>';
    if(esPct) return (v*100).toFixed(1)+'%';
    if(esRatio) return v.toFixed(2);
    return fmt(v);
  }

  function variCol(v){
    if(v===null||v===undefined) return '<span style="color:var(--mu)">—</span>';
    const pct=(v*100).toFixed(1)+'%';
    if(v>0) return `<span style="color:var(--green)">▲ ${pct}</span>`;
    if(v<0) return `<span style="color:var(--red)">▼ ${Math.abs(v*100).toFixed(1)}%</span>`;
    return `<span style="color:var(--mu)">— 0%</span>`;
  }

  const QQ=[
    {q:1,label:'Q1<br><span style="font-weight:400">Ene–Mar</span>'},
    {q:2,label:'Q2<br><span style="font-weight:400">Abr–Jun</span>'},
    {q:3,label:'Q3<br><span style="font-weight:400">Jul–Sep</span>'},
    {q:4,label:'Q4<br><span style="font-weight:400">Oct–Dic</span>'}
  ];

  let hdr=`<tr>
    <th style="${hStyle};text-align:left;position:sticky;left:0;background:var(--sf);z-index:6;min-width:260px">INDICADORES</th>
    <th style="${hStyle}">${yp}</th>`;
  for(const qq of QQ){
    hdr+=`<th style="${hStyle}">${qq.label}</th><th style="${hStyle}">Vari Rel.</th>`;
  }
  hdr+=`<th style="${hStyle}">AÑO ACTUAL<br><span style="font-weight:400">${ys}</span></th>`;
  hdr+=`<th style="${hStyle}">Vari Rel.</th></tr>`;

  let rows='';
  for(const ind of inds){
    const esPct=ind.es_pct;
    const esRatio=ind.es_ratio;
    const nombre=ind.nombre;
    let row=`<tr><td style="${lStyle};position:sticky;left:0;background:#fff;z-index:4">${nombre}</td>`;
    row+=`<td style="${cStyle}">${fmtInd(ind.year_prev,esPct,esRatio)}</td>`;
    for(let j=0;j<4;j++){
      const t=ind.trimestres[j];
      row+=`<td style="${cStyle}">${fmtInd(t.valor,esPct,esRatio)}</td>`;
      row+=`<td style="${cStyle}">${variCol(t.vari_rel)}</td>`;
    }
    row+=`<td style="${cStyle};font-weight:700">${fmtInd(ind.anio_actual,esPct,esRatio)}</td>`;
    row+=`<td style="${cStyle}">${variCol(ind.vari_rel_aa)}</td>`;
    row+='</tr>';
    rows+=row;
  }

  G('ind-body').innerHTML=`
    <div class="tw" style="max-height:calc(100vh - 180px);overflow:auto;position:relative">
    <table style="width:100%;border-collapse:collapse">
      <thead style="position:sticky;top:0;z-index:10">${hdr}</thead>
      <tbody>${rows}</tbody>
    </table></div>`;
}
