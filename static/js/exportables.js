// ── EXCEL ─────────────────────────────────────────────────────────────────
function onExTipoChange(){
  const tipo = G('ex-tipo').value;
  G('ex-unit-wrap').style.display = (tipo === 'esf' || tipo === 'esf_divisa' || tipo === 'indicadores') ? 'none' : '';
  G('ex-quarter-wrap').style.display = (tipo === 'esf' || tipo === 'esf_divisa') ? '' : 'none';
}
function openExcelModal(){
  const activePage = document.querySelector('.page.active');
  const id = activePage ? activePage.id : '';
  G('ex-tipo').value = (id === 'page-esf') ? 'esf' : (id === 'page-esf_divisa') ? 'esf_divisa' : 'eerr';
  G('ex-year').value = getCurrentYear();
  updateUnitSelectorsForEmpresa();
  G('ex-unit').value = getCurrentUnit();
  onExTipoChange();
  G('exmod').classList.add('show');
}
function closeExcel(){G('exmod').classList.remove('show');}
function doExport(){
  const tipo = G('ex-tipo').value, year = G('ex-year').value, u = G('ex-unit').value;
  const empresaParam = (CURRENT_EMPRESA_ID !== null && CURRENT_EMPRESA_ID !== undefined) ? `&empresa_id=${CURRENT_EMPRESA_ID}` : '';
  let url;
  if (tipo === 'esf') {
    const q = G('ex-quarter').value;
    url = `/api/export/esf?year=${year}${empresaParam}`;
    if (q) url += `&quarter=${q}`;
  } else if (tipo === 'esf_divisa') {
    url = `/api/export/esf-divisa-real?year=${year}${empresaParam}`;
  } else if (tipo === 'indicadores') {
    url = `/api/export/excel?tipo=indicadores&year=${year}`;
  } else {
    url = `/api/export/excel?year=${year}${empresaParam}`;
    if (tipo === 'eerr_divisa') url += `&divisa=1`;
    if (u) url += `&unit=${encodeURIComponent(u)}`;
  }
  window.location.href = url;
  closeExcel();
}
