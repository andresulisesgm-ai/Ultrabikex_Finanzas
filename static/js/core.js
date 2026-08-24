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
