// ── UTILS ─────────────────────────────────────────────────────────────────
const G=id=>document.getElementById(id);
let CURRENT_EMPRESA_ID = null;   // null = Holding (sin filtro, suma de las 4 empresas)
let UNIDADES_CACHE = [];
let CURRENT_PAGE = 'dashboard';
let EMPRESAS_CACHE = [];
const fmt=n=>n==null?'—':'$'+Number(n).toLocaleString('es-VE',{minimumFractionDigits:2,maximumFractionDigits:2});
const fmtS=n=>{if(!n)return'$0';const a=Math.abs(n);return(n<0?'-':'')+(a>=1e6?'$'+(a/1e6).toFixed(2)+'M':a>=1e3?'$'+(a/1e3).toFixed(2)+'K':'$'+a.toFixed(2));};
const pct=n=>n==null?'—':Number(n).toFixed(1)+'%';
const cl=(v,lo,hi)=>Math.min(Math.max(v,lo),hi);
const PAL=['#2563eb','#059669','#d97706','#dc2626','#7c3aed','#0891b2','#be185d','#65a30d'];
const MO=['ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEPT','OCT','NOV','DIC'];
let CH={},DD=null,MAP=[],sFile=null,sRF=null,mainDS=null;
let currentUser = window.currentUser;

function getCurrentYear() {
  const activePage = document.querySelector('.page.active');
  if (!activePage) return G('dash-year') ? G('dash-year').value : '2026';
  const id = activePage.id;
  if (id === 'page-eerr') return G('eerr-year').value;
  if (id === 'page-err_divisa') return G('err-divisa-year').value;
  if (id === 'page-presupuesto') return G('bgt-year').value;
  if (id === 'page-comparativa') return G('cmp-year').value;
  if (id === 'page-esf') return G('esf-year').value;
  return G('dash-year') ? G('dash-year').value : '2026';
}

function getCurrentUnit() {
  const activePage = document.querySelector('.page.active');
  if (!activePage) return G('dash-unit') ? G('dash-unit').value : '';
  const id = activePage.id;
  let val = '';
  if (id === 'page-eerr') val = G('eerr-unit').value;
  else if (id === 'page-err_divisa') val = G('err-divisa-unit').value;
  else if (id === 'page-presupuesto') val = G('bgt-unit').value;
  else if (id === 'page-comparativa') val = G('cmp-unit').value;
  else if (id === 'page-esf') val = G('esf-unit').value;
  else val = G('dash-unit') ? G('dash-unit').value : '';
  if (val === 'TODAS' || val === 'Consolidado' || val === 'Todas') return '';
  return val;
}

// ── AUTH ──────────────────────────────────────────────────────────────────
function isAdmin() {
  return currentUser && currentUser.role === 'admin';
}

function logout() {
  if(confirm('¿Cerrar sesión?')) {
    fetch('/api/logout', {method: 'POST'}).then(() => window.location.href = '/login');
  }
}

function updateUserInfo() {
  const info = G('userInfo');
  if(currentUser) {
    const roleClass = currentUser.role === 'viewer' ? 'viewer' : '';
    const roleName = currentUser.role === 'admin' ? 'Administrador' : 'Visor';
    info.innerHTML = `<span class="user-badge ${roleClass}">${currentUser.username} - ${roleName}</span>`;
  }
}

// ── LOCAL STORAGE ─────────────────────────────────────────────────────────
const LS={
  get:(k,d)=>{try{const v=localStorage.getItem(k);return v!=null?JSON.parse(v):d;}catch{return d;}},
  set:(k,v)=>{try{localStorage.setItem(k,JSON.stringify(v));}catch{}}
};

// Estado del modo Divisa Real (BCV o Real)
let modoDivisaReal=false;


function escAttr(s){ return String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/'/g,'&#39;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

async function fillYears(){
  try {
    const r = await fetch('/api/years');
    let years = await r.json();
    if (!Array.isArray(years) || !years.length) years = [String(new Date().getFullYear())];
    years = years.map(String);
    document.querySelectorAll('select#ysel, select[id$="-year"]').forEach(sel => {
      const prev = sel.value;
      sel.innerHTML = years.map(y => `<option value="${y}">${y}</option>`).join('');
      sel.value = years.includes(prev) ? prev : years[0];
    });
    const up = G('up-year');   // input numérico de la página de carga
    if (up && !years.includes(up.value)) up.value = years[0];
  } catch(e) { console.error('fillYears:', e); }
}

function showA(id,msg){const e=G(id);e.textContent=msg;e.classList.add('show');setTimeout(()=>e.classList.remove('show'),7000);}
// ── CERRAR APP ────────────────────────────────────────────────────────────
async function closeApp(){
  if(!confirm('¿Cerrar Ultrabikex Financial Analytics? Esto detendrá el servidor.'))return;
  try{await fetch('/api/shutdown',{method:'POST'});}catch{}
  document.body.innerHTML='<div style="display:flex;align-items:center;justify-content:center;height:100vh;font-family:DM Sans,sans-serif;color:#64748b;flex-direction:column;gap:10px"><div style="font-size:32px">⏻</div><div style="font-weight:600">Servidor detenido.</div><div style="font-size:12px">Puedes cerrar esta ventana.</div></div>';
}
// Deshabilita en el selector de trimestre las opciones sin tasa BCV/paralela
// completa (3 meses cargados en tasas_periodo) para el año activo. Solo
// bloquea -- no selecciona ningun valor. Se llama al activar Divisa Real y
// cada vez que cambia el anio mientras Divisa Real ya esta activo.
async function actualizarDisponibilidadTrimestres(){
  const qsel=G('dash-quarter');
  if(!qsel) return;
  const year=G('dash-year')?G('dash-year').value:String(new Date().getFullYear());
  const QUARTER_MONTHS_DISP={1:['ENE','FEB','MAR'],2:['ABR','MAY','JUN'],3:['JUL','AGO','SEPT'],4:['OCT','NOV','DIC']};
  let mesesConTasa=new Set();
  try{
    const rTasas=await fetch(`/api/tasas?year=${year}`);
    if(rTasas.ok){
      const tasas=await rTasas.json();
      mesesConTasa=new Set(tasas.map(t=>t.month));
    }
  }catch(e){}
  Array.from(qsel.options).forEach(opt=>{
    if(!opt.value) return; // "Trimestres" (sin filtro) siempre habilitado
    const q=parseInt(opt.value);
    const completo=QUARTER_MONTHS_DISP[q].every(m=>mesesConTasa.has(m));
    opt.disabled=!completo;
    opt.textContent=completo?`Q${q}`:`Q${q} (sin tasa)`;
  });
}

// ── TOGGLE MODO DIVISA ───────────────────────────────────────────────────
async function toggleDivisaMode(){
  modoDivisaReal=!modoDivisaReal;
  LS.set('modo_divisa_real',modoDivisaReal);
  const toggle=G('toggle-switch');
  const msel=G('dash-month');
  const qsel=G('dash-quarter');
  if(toggle){
    if(modoDivisaReal){
      toggle.parentElement.classList.add('active');
      if(msel) msel.style.display='block';
      if(qsel){
        // Regla (ago-2026, revisado): al activar Divisa Real, NO preseleccionar
        // ningun trimestre puntual -- arranca en "Trimestres" (sin filtro = todos).
        // Las opciones sin tasa BCV/paralela completa quedan deshabilitadas en el
        // dropdown para que el usuario solo pueda elegir trimestres con datos.
        qsel.value='';
        qsel.disabled=false;
        msel.value='';
        msel.disabled=true;
        await actualizarDisponibilidadTrimestres();
      }
    }else{
      toggle.parentElement.classList.remove('active');
      if(msel)msel.style.display='none';
    }
  }
  if(G('page-dashboard').classList.contains('active')){
    loadDash();
  }
}

let modoDivisaRealInd = false;
function toggleDivisaModeInd(){
  modoDivisaRealInd = !modoDivisaRealInd;
  const toggle = G('toggle-switch-ind');
  if(toggle){
    if(modoDivisaRealInd){
      toggle.parentElement.classList.add('active');
    }else{
      toggle.parentElement.classList.remove('active');
    }
  }
  loadIndicadores();
}

// Inicializar estado del toggle al cargar página
function initDivisaToggle(){
  const toggle=G('toggle-switch');
  const msel=G('dash-month');
  const qsel=G('dash-quarter');
  if(toggle&&modoDivisaReal){
    toggle.parentElement.classList.add('active');
    if(msel)msel.style.display='block';
  }
}

// ── PAGES ─────────────────────────────────────────────────────────────────
function togglePin(){
  const sb=document.querySelector('.sidebar');
  const main=document.querySelector('.main');
  const btn=G('pin-btn');
  const pinned=btn.classList.toggle('pinned');
  localStorage.setItem('sb-pinned', pinned?'1':'0');
  if(pinned){
    sb.classList.remove('collapsed');
    main.classList.remove('collapsed');
  } else {
    sb.classList.add('collapsed');
    main.classList.add('collapsed');
  }
}
function toggleCompanySel(e){
  e.stopPropagation();
  document.getElementById('company-sel').classList.toggle('open');
}
function deriveInitials(nombre){
  const words = nombre.replace(/C\.A\.?/i,'').trim().split(/\s+/).filter(Boolean);
  if(words.length >= 2) return (words[0][0]+words[1][0]).toUpperCase();
  return nombre.substring(0,2).toUpperCase();
}
function selectCompany(el,name,color,initials,empresaId){
  document.getElementById('company-sel-label').textContent=name;
  document.getElementById('logo-icon').style.background=color;
  document.getElementById('logo-icon').style.boxShadow='0 2px 8px rgba(15,23,42,.35)';
  document.getElementById('logo-icon').textContent=initials;
  document.querySelectorAll('.company-sel-item').forEach(function(i){i.classList.remove('active');});
  el.classList.add('active');
  document.getElementById('company-sel').classList.remove('open');

  CURRENT_EMPRESA_ID = empresaId;
  updateSidebarForEmpresa();

  updateUnitSelectorsForEmpresa();

  showPage('dashboard', G('nav-dashboard'));
}

function reloadCurrentPage(){
  if(CURRENT_PAGE === 'dashboard') loadDash();
  else if(CURRENT_PAGE === 'eerr') loadEERR();
  else if(CURRENT_PAGE === 'esf') loadESF();
  else if(CURRENT_PAGE === 'indicadores') loadIndicadores();
}
document.addEventListener('click',function(e){
  var sel=document.getElementById('company-sel');
  if(sel && !sel.contains(e.target)) sel.classList.remove('open');
});
document.addEventListener('DOMContentLoaded',function(){
  const now=new Date();
  const MONTHS=['ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEPT','OCT','NOV','DIC'];
  const my=G('metodos-year');const mm=G('metodos-month');
  if(my)my.value=now.getFullYear();
  if(mm){mm.value=MONTHS[now.getMonth()];}
  const pinned=localStorage.getItem('sb-pinned')!=='0';
  const sb=document.querySelector('.sidebar');
  const main=document.querySelector('.main');
  const btn=G('pin-btn');
  if(!btn)return;
  if(pinned){
    btn.classList.add('pinned');
  } else {
    sb.classList.add('collapsed');
    main.classList.add('collapsed');
  }
});
function showPage(name,el){
  CURRENT_PAGE = name;
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
  G('page-'+name).classList.add('active');
  if(el) el.classList.add('active');
  const T={dashboard:'Dashboard Financiero',carga:'Cargar Reportes',historial:'Historial de Cargas',mapping:'Mapeo de Cuentas',datos:'Ver Datos',backup:'Backup y Restaurar',comparativa:'Comparativas',eerr:'Estados de Resultados (EERR)',eerrdet:'ERR Detallado',esf:'Estado de Situación Financiera (ESF)',presupuesto:'Presupuesto vs Real',config_tasas:'Configuración de Tasas',err_divisa:'Estados de Resultados Divisa Real (EERR)',esf_divisa:'ESF Divisa Real',export_ai:'Exportar Briefing IA'};
  const S={dashboard:'Estado de resultados consolidado',carga:'Importar XLS de Odoo',historial:'Auditoría y reversión',mapping:'Configuración de cuentas contables',datos:'Explorador de datos',backup:'Gestión de copias de seguridad',comparativa:'Mismo período vs año anterior',eerr:'P&L estructurado por partida',eerrdet:'Desglose por tipo de ingreso + ACUM EJEC',esf:'Balance trimestral Q1–Q4',presupuesto:'Real vs valores presupuestados',config_tasas:'Tasas BCV/Paralela y métodos de pago por cuenta',esf_divisa:'Revalorización trimestral de efectivo en Bs',export_ai:'Generar prompt y datos para análisis con IA'};
  G('ptitle').textContent=T[name]||''; G('psub').textContent=S[name]||'';
  if(name==='dashboard'){ initDivisaToggle(); loadDash(); }
  if(name==='historial') loadHist();
  if(name==='mapping')   loadMap();
  if(name==='datos')     loadData();
  if(name==='comparativa') loadCmp();
  if(name==='eerr')      loadEERR();
  if(name==='eerrdet')   loadEERRDet();
  if(name==='esf')       loadESF();
  if(name==='config_tasas'){cargarTasas();cargarMetodosPago();cargarHistorialTasas();}
  if(name==='err_divisa') loadERRDivisa();
  if(name==='indicadores') loadIndicadores();
  if(name==='presupuesto') loadBgt();
  if(name==='esf_divisa') loadESFDivisaReal();
  if(name==='export_ai') cargarPromptConfigurado();

  const PAGES_WITH_EXCEL = ['eerr','err_divisa','esf','esf_divisa','presupuesto','comparativa','indicadores'];
  const btnExcel = document.getElementById('btn-export-excel');
  if (btnExcel) {
    btnExcel.style.display = PAGES_WITH_EXCEL.includes(name) ? '' : 'none';
  }
}

