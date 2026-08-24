// ── CONFIGURACIÓN DE TASAS ────────────────────────────────────────────────
function calcPromedios(){
  const bcvIni=parseFloat(G('tasas-bcv-ini').value)||0;
  const bcvFin=parseFloat(G('tasas-bcv-fin').value)||0;
  const parIni=parseFloat(G('tasas-par-ini').value)||0;
  const parFin=parseFloat(G('tasas-par-fin').value)||0;

  let bcvProm=0, parProm=0;
  if(bcvIni>0&&bcvFin>0){
    bcvProm=(bcvIni+bcvFin)/2;
    G('bcv-promedio').textContent=bcvProm.toFixed(4);
  }else{
    G('bcv-promedio').textContent='—';
  }

  if(parIni>0&&parFin>0){
    parProm=(parIni+parFin)/2;
    G('par-promedio').textContent=parProm.toFixed(4);
  }else{
    G('par-promedio').textContent='—';
  }

  if(bcvProm>0&&parProm>0){
    const dif=(parProm/bcvProm).toFixed(4);
    G('factor-diferencial').textContent=dif;
  }else{
    G('factor-diferencial').textContent='—';
  }
}

async function guardarTasas(){
  if(!isAdmin()){alert('⛔ Acceso denegado: se requiere rol de administrador');return;}
  const year=G('tasas-year').value, month=G('tasas-month').value;
  const bcvIni=parseFloat(G('tasas-bcv-ini').value);
  const bcvFin=parseFloat(G('tasas-bcv-fin').value);
  const parIni=parseFloat(G('tasas-par-ini').value);
  const parFin=parseFloat(G('tasas-par-fin').value);

  if(!bcvIni||!bcvFin||!parIni||!parFin){showA('al-tasas-er','❌ Completa todas las tasas (inicio y fin)');return;}
  if(bcvIni<=0||bcvFin<=0){showA('al-tasas-er','❌ Tasas BCV deben ser mayores a 0');return;}

  const chk=await fetch(`/api/tasas?year=${year}&month=${month}`);
  if(chk.ok){
    const ok=confirm(`Ya existe una tasa guardada para ${month} ${year}. ¿Deseas reemplazarla?`);
    if(!ok)return;
  }

  const r=await fetch('/api/tasas',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({
    year,month,
    tasa_bcv_inicio:bcvIni,
    tasa_bcv_fin:bcvFin,
    tasa_paralela_inicio:parIni,
    tasa_paralela_fin:parFin
  })});
  const d=await r.json();
  if(d.ok){
    showA('al-tasas-ok',`✅ Tasas guardadas para ${month} ${year}. Promedio BCV: ${d.tasa_bcv_promedio}, Diferencial: ${d.factor_diferencial}`);
    cargarHistorialTasas();
  }
  else{showA('al-tasas-er','❌ '+d.error);}
}

async function cargarTasas(){
  const year=G('tasas-year').value, month=G('tasas-month').value;
  const r=await fetch(`/api/tasas?year=${year}&month=${month}`);
  if(!r.ok){
    const meses=['ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEPT','OCT','NOV','DIC'];
    const hoy=new Date();
    const yearActual=String(hoy.getFullYear());
    const mesActualIdx=hoy.getMonth();
    const esPasado=(year<yearActual)||(year===yearActual&&meses.indexOf(month)<mesActualIdx);
    if(esPasado){
      showA('al-tasas-er',`⚠️ No hay tasa registrada para ${month} ${year}`);
    }
    return;
  }
  const d=await r.json();
  G('tasas-bcv-ini').value=d.tasa_bcv_inicio||'';
  G('tasas-bcv-fin').value=d.tasa_bcv_fin||'';
  G('tasas-par-ini').value=d.tasa_paralela_inicio||'';
  G('tasas-par-fin').value=d.tasa_paralela_fin||'';

  calcPromedios();
  showA('al-tasas-ok',`✅ Tasas cargadas: ${month} ${year}`);
}

async function cargarHistorialTasas() {
  try {
    const r = await fetch('/api/tasas');
    const data = await r.json();
    const tbody = G('tasas-historial-tbody');
    G('tasas-historial-loading').style.display = 'none';
    if (!data.length) {
      G('tasas-historial-empty').style.display = 'block';
      G('tasas-historial-wrap').style.display = 'none';
      return;
    }
    G('tasas-historial-empty').style.display = 'none';
    G('tasas-historial-wrap').style.display = 'block';
    tbody.innerHTML = data.map(t => `
      <tr>
        <td>${t.year}</td>
        <td>${t.month}</td>
        <td>${t.tasa_bcv_promedio.toFixed(4)}</td>
        <td>${t.tasa_paralela_promedio.toFixed(4)}</td>
        <td>${t.factor_diferencial.toFixed(4)}</td>
        <td>
          <button class="btnm-sm" onclick="editarTasa('${t.year}','${t.month}')">✏ Editar</button>
          <button class="btnd" onclick="eliminarTasa(${t.id})">🗑 Borrar</button>
        </td>
      </tr>
    `).join('');
  } catch {
    G('tasas-historial-loading').textContent = 'Error al cargar.';
  }
}

async function editarTasa(year, month){
  G('tasas-year').value = year;
  G('tasas-month').value = month;
  await cargarTasas();
  G('tasas-year').scrollIntoView({behavior:'smooth', block:'center'});
}

async function eliminarTasa(id) {
  if (!confirm('¿Eliminar esta tasa? Esta acción no se puede deshacer.')) return;
  const r = await fetch(`/api/tasas/${id}`, { method: 'DELETE' });
  const d = await r.json();
  if (d.ok) cargarHistorialTasas();
}
