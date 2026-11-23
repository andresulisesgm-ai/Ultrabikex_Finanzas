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
  if(currentUser && info) {
    info.innerHTML = `
      <button class="tb-sel" type="button" onclick="toggleUserProfileMenu(event)" style="cursor:pointer;display:inline-flex;align-items:center;gap:6px">
        <i class="ph ph-user-circle" style="font-size:15px"></i>
        <span>${currentUser.username}</span>
        <span style="font-size:10px;opacity:.85">▾</span>
      </button>
      <div id="user-profile-menu" style="display:none;position:absolute;top:calc(100% + 6px);right:0;min-width:190px;background:#fff;border:1px solid #cbd5e1;border-radius:8px;box-shadow:0 8px 24px rgba(15,23,42,.18);padding:6px;z-index:999">
        <button onclick="if(typeof abrirMiPerfil==='function') abrirMiPerfil();" style="display:block;width:100%;text-align:left;padding:7px 9px;border:none;background:transparent;border-radius:6px;font-size:12px;color:#0f172a;cursor:pointer">🔑 Cambiar clave</button>
        <button onclick="logout()" style="display:block;width:100%;text-align:left;padding:7px 9px;border:none;background:transparent;border-radius:6px;font-size:12px;color:#b91c1c;cursor:pointer">⏻ Cerrar sesión</button>
      </div>`;
  }
  const sysEmpNav = document.getElementById('nav-sistema-empresas');
  if (sysEmpNav) {
    sysEmpNav.style.display = (currentUser && currentUser.role === 'admin') ? '' : 'none';
  }
  const resetPwdNav = document.getElementById('nav-reset-pwd');
  if (resetPwdNav) {
    resetPwdNav.style.display = (currentUser && currentUser.es_superadmin === 1) ? '' : 'none';
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
      if(msel){
        msel.style.display='block';
        msel.disabled = qsel && qsel.value !== '';
      }
      if(qsel){
        // Regla (sep-2026, revisado): Normal/Divisa Real ya no resetea la
        // seleccion de mes/trimestre -- se respeta lo que el usuario ya
        // tenia elegido en cualquiera de los dos modos.
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

  const navActivo = document.querySelector('.nav-item.active') || G('nav-dashboard');
  showPage(CURRENT_PAGE, navActivo);
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
  var pm=document.getElementById('user-profile-menu');
  var ui=document.getElementById('userInfo');
  if(pm && ui && !ui.contains(e.target)) pm.style.display='none';
});
document.addEventListener('DOMContentLoaded',function(){
  const now=new Date();
  const MONTHS=['ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEPT','OCT','NOV','DIC'];
  const my=G('metodos-year');const mm=G('metodos-month');
  if(my)my.value=now.getFullYear();
  if(mm){mm.value=MONTHS[now.getMonth()];}
  const uye=G('up-year-err'); if(uye) uye.value=now.getFullYear();
  const uys=G('up-year-esf'); if(uys) uys.value=now.getFullYear();
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
function toggleNavSection(key, headerEl){
  const grp = G('nav-group-' + key);
  if(!grp) return;
  const open = grp.style.display !== 'none';
  grp.style.display = open ? 'none' : '';
  const arrow = headerEl ? headerEl.querySelector('.nav-sec-arrow') : null;
  if(arrow) arrow.textContent = open ? '▸' : '▾';
}

function showPage(name,el){
  CURRENT_PAGE = name;
  const CONFIG_PAGES = ['carga','mapping','config_tasas','historial','datos'];
  const SISTEMA_PAGES = ['export_ai','backup','sistema_empresas','reset_pwd'];
  if(CONFIG_PAGES.includes(name)){
    const g = G('nav-group-config');
    if(g){ g.style.display = ''; const a = g.previousElementSibling?.querySelector('.nav-sec-arrow'); if(a) a.textContent = '▾'; }
  } else if(SISTEMA_PAGES.includes(name)){
    const g = G('nav-group-sistema');
    if(g){ g.style.display = ''; const a = g.previousElementSibling?.querySelector('.nav-sec-arrow'); if(a) a.textContent = '▾'; }
  }
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
  G('page-'+name).classList.add('active');
  if(el) el.classList.add('active');
  const T={home:'Home',dashboard:'Dashboard Financiero',carga:'Cargar Reportes',historial:'Historial de Cargas',mapping:'Mapeo de Cuentas',datos:'Ver Datos',backup:'Backup y Restaurar',comparativa:'Comparativas',eerr:'Estados de Resultados (EERR)',eerrdet:'ERR Detallado',esf:'Estado de Situación Financiera (ESF)',presupuesto:'Presupuesto vs Real',config_tasas:'Configuración de Tasas',err_divisa:'Estados de Resultados Divisa Real (EERR)',esf_divisa:'ESF Divisa Real',export_ai:'Exportar Briefing IA',sistema_empresas:'Empresas y Unidades',reset_pwd:'Usuarios y Claves'};
  const S={home:'Resumen del holding — Divisa Real',dashboard:'Estado de resultados consolidado',carga:'Importar XLS de Odoo',historial:'Auditoría y reversión',mapping:'Configuración de cuentas contables',datos:'Explorador de datos',backup:'Gestión de copias de seguridad',comparativa:'Mismo período vs año anterior',eerr:'P&L estructurado por partida',eerrdet:'Desglose por tipo de ingreso + ACUM EJEC',esf:'Balance trimestral Q1–Q4',presupuesto:'Real vs valores presupuestados',config_tasas:'Tasas BCV/Paralela y métodos de pago por cuenta',esf_divisa:'Revalorización trimestral de efectivo en Bs',export_ai:'Generar prompt y datos para análisis con IA',sistema_empresas:'Administración de empresas legales y unidades de negocio',reset_pwd:'Administración de usuarios, roles y contraseñas'};
  G('ptitle').textContent=T[name]||''; G('psub').textContent=S[name]||'';
  if(name==='home')       loadHome();
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
  if(name==='sistema_empresas' && typeof loadSistemaEmpresas==='function') loadSistemaEmpresas();
  if(name==='reset_pwd' && typeof loadSistemaUsuarios==='function') loadSistemaUsuarios();
  if(name==='backup' && typeof loadAutoBackups==='function') loadAutoBackups();

  const PAGES_WITH_EXCEL = ['eerr','err_divisa','esf','esf_divisa','presupuesto','comparativa','indicadores'];
  const btnExcel = document.getElementById('btn-export-excel');
  if (btnExcel) {
    btnExcel.style.display = PAGES_WITH_EXCEL.includes(name) ? '' : 'none';
  }
}

async function loadUsersForReset() {
  try {
    const res = await fetch('/api/admin/list_users');
    const users = await res.json();
    const sel = document.getElementById('rp-user');
    if (sel) sel.innerHTML = users.map(u => `<option value="${u.username}">${u.username} (${u.role})</option>`).join('');
  } catch (e) {
    console.error('Error cargando usuarios', e);
  }
}

async function doResetPassword() {
  const username = document.getElementById('rp-user').value;
  const newPassword = document.getElementById('rp-newpass').value;
  const okBox = document.getElementById('rp-ok');
  const erBox = document.getElementById('rp-er');
  okBox.innerHTML = '';
  erBox.innerHTML = '';

  if (!newPassword || newPassword.length < 8) {
    erBox.innerHTML = 'La clave nueva debe tener al menos 8 caracteres.';
    return;
  }

  try {
    const res = await fetch('/api/admin/reset_password', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({username: username, new_password: newPassword})
    });
    const data = await res.json();
    if (data.success) {
      okBox.innerHTML = data.message;
      document.getElementById('rp-newpass').value = '';
    } else {
      erBox.innerHTML = data.message || 'Error al restablecer la clave.';
    }
  } catch (e) {
    erBox.innerHTML = 'Error de conexion. Intenta de nuevo.';
  }
}


