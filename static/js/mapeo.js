// ── MAPPING ───────────────────────────────────────────────────────────────
let SIN_CLASIFICAR_CODES = [];
let SIN_CLASIFICAR_ESF_CODES = [];
async function loadMap(){
  const r=await fetch('/api/mapping');
  MAP=await r.json();
  renderMap(MAP);
  await loadSinClasificar();
  await loadSinClasificarESF();
}
async function loadSinClasificarESF() {
  try {
    const r = await fetch('/api/mapping/sin-clasificar-esf');
    const d = await r.json();
    const badge = G('unmapped-badge-esf');
    if (d.count > 0) {
      badge.textContent = `${d.count} sin clasificar en ESF`;
      badge.style.display = 'inline-block';
      SIN_CLASIFICAR_ESF_CODES = d.accounts.map(a => a.odoo_code);
    } else {
      badge.style.display = 'none';
      SIN_CLASIFICAR_ESF_CODES = [];
    }
  } catch (err) {
    console.error("Error loading sin clasificar ESF:", err);
  }
}
async function loadSinClasificar() {
  try {
    const r = await fetch('/api/mapping/sin-clasificar');
    const d = await r.json();
    const badge = G('unmapped-badge');
    if (d.count > 0) {
      badge.textContent = `${d.count} sin clasificar en EERR`;
      badge.style.display = 'inline-block';
      SIN_CLASIFICAR_CODES = d.accounts.map(a => a.odoo_code);
    } else {
      badge.style.display = 'none';
      SIN_CLASIFICAR_CODES = [];
    }
  } catch (err) {
    console.error("Error loading sin clasificar:", err);
  }
}
function filterUnmapped() {
  const filtered = MAP.filter(m => SIN_CLASIFICAR_CODES.includes(m.odoo_code));
  renderMap(filtered);
}
function filterUnmappedESF() {
  const filtered = MAP.filter(m => SIN_CLASIFICAR_ESF_CODES.includes(m.odoo_code));
  renderMap(filtered);
}
function renderMap(data){G('mcnt').textContent=data.length+' cuentas';G('mbody').innerHTML=data.map(m=>`<tr><td><code style="background:var(--blue-l);padding:2px 5px;border-radius:4px;font-size:10px;color:var(--blue);font-family:'DM Mono'">${m.odoo_code}</code></td><td style="color:var(--mu)">${m.odoo_name}</td><td>${m.partida}</td><td><span class="chip ${m.sign==1?'chg':'chb'}">${m.sign==1?'Ingreso':'Gasto/Costo'}</span></td><td style="display:flex;gap:5px;padding:6px 8px"><button class="btns" onclick="editMap('${m.odoo_code}')">✏️</button><button class="btnd" onclick="delMap('${m.odoo_code}')">🗑️</button></td></tr>`).join('');}
function filterMap(){const q=G('msrch').value.toLowerCase();renderMap(MAP.filter(m=>m.odoo_code.includes(q)||m.odoo_name.toLowerCase().includes(q)||m.partida.toLowerCase().includes(q)));}
let OVERRIDES_DATA = null;
async function fetchOverrides() {
  const r = await fetch('/api/eerr_nodes/overrides');
  OVERRIDES_DATA = await r.json();
}

// Tree UI for EERR Groups
let EERR_GRUPOS_CACHE = null;

async function loadEerrGroupsIfNeeded() {
  if (EERR_GRUPOS_CACHE) return EERR_GRUPOS_CACHE;
  try {
    const res = await fetch('/api/eerr/grupos');
    EERR_GRUPOS_CACHE = await res.json();
    return EERR_GRUPOS_CACHE;
  } catch (err) {
    console.error("Error loading EERR groups:", err);
    return [];
  }
}

function cleanLabel(label, nivel) {
  if (!label) return '';
  let clean = label;
  if (nivel === 2 && clean.startsWith("  → ")) {
    clean = clean.substring(4);
  } else if (nivel === 3 && clean.startsWith("    → ")) {
    clean = clean.substring(6);
  }
  return clean.trim();
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
}

function buildTree(flatList) {
  const roots = [];
  const stack = [];
  
  for (let i = 0; i < flatList.length; i++) {
    const item = flatList[i];
    const node = {
      nombre: item.nombre,
      nivel: item.nivel,
      label: item.label,
      children: [],
      isLeaf: true
    };
    
    if (i < flatList.length - 1 && flatList[i+1].nivel > item.nivel) {
      node.isLeaf = false;
    }
    
    while (stack.length > 0 && stack[stack.length - 1].nivel >= node.nivel) {
      stack.pop();
    }
    
    if (stack.length === 0) {
      roots.push(node);
    } else {
      stack[stack.length - 1].children.push(node);
    }
    
    if (!node.isLeaf) {
      stack.push(node);
    }
  }
  return roots;
}

function hasSelectedDescendant(node, selectedValue) {
  if (!selectedValue) return false;
  if (node.children && node.children.length > 0) {
    for (const child of node.children) {
      if (child.isLeaf && child.nombre === selectedValue) {
        return true;
      }
      if (hasSelectedDescendant(child, selectedValue)) {
        return true;
      }
    }
  }
  return false;
}

function renderTreeNode(node, selectedValue) {
  const isSelected = selectedValue && node.nombre === selectedValue;
  
  if (node.isLeaf) {
    return `
      <div class="tree-item leaf-node ${isSelected ? 'selected' : ''}" 
           data-name="${escapeHtml(node.nombre)}" 
           onclick="selectLeafNode('${escapeHtml(node.nombre)}')"
           style="display: flex; align-items: center; justify-content: space-between; padding: 6px 10px; margin: 2px 0; border-radius: 6px; cursor: pointer; transition: all 0.15s;">
        <span class="node-label" style="display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--tx2);">
          <span style="font-size: 8px; color: var(--mu2); margin-right: 4px;">●</span>
          ${escapeHtml(cleanLabel(node.label, node.nivel))}
        </span>
        <span class="check-mark" style="color: var(--green); font-weight: bold; font-size: 12px; visibility: ${isSelected ? 'visible' : 'hidden'};">✓</span>
      </div>
    `;
  } else {
    const isExpanded = hasSelectedDescendant(node, selectedValue);
    const arrow = isExpanded ? '▼' : '▶';
    const childrenHtml = node.children.map(child => renderTreeNode(child, selectedValue)).join('');
    
    return `
      <div class="tree-group level-${node.nivel}" style="margin: 4px 0;">
        <div class="tree-item parent-node" 
             onclick="toggleParentNode(this)"
             style="display: flex; align-items: center; gap: 8px; padding: 6px 10px; margin: 2px 0; border-radius: 6px; cursor: pointer; user-select: none;">
          <span class="arrow-icon" style="font-size: 8px; width: 12px; display: inline-block; color: var(--mu);">${arrow}</span>
          <span style="font-size: ${node.nivel === 1 ? '13px' : '12px'}; font-weight: ${node.nivel === 1 ? '700' : '600'}; color: ${node.nivel === 1 ? 'var(--tx)' : 'var(--tx2)'};">${escapeHtml(cleanLabel(node.label, node.nivel))}</span>
        </div>
        <div class="tree-children" style="padding-left: 16px; display: ${isExpanded ? 'block' : 'none'};">
          ${childrenHtml}
        </div>
      </div>
    `;
  }
}

function toggleParentNode(el) {
  const childrenDiv = el.nextElementSibling;
  const arrowSpan = el.querySelector('.arrow-icon');
  if (childrenDiv.style.display === 'none') {
    childrenDiv.style.display = 'block';
    arrowSpan.textContent = '▼';
  } else {
    childrenDiv.style.display = 'none';
    arrowSpan.textContent = '▶';
  }
}

async function openTreePanel() {
  const groups = await loadEerrGroupsIfNeeded();
  const currentValue = G('m-grupo-eerr').value;
  const treeRoots = buildTree(groups);
  const container = G('eerr-tree-container');
  
  const unclassifiedHtml = `
    <div class="tree-item leaf-node ${!currentValue ? 'selected' : ''}" 
         data-name="" 
         onclick="selectLeafNode('')"
         style="display: flex; align-items: center; justify-content: space-between; padding: 6px 10px; margin-bottom: 8px; border-bottom: 1px solid var(--bd); border-radius: 6px; cursor: pointer; transition: all 0.15s;">
      <span class="node-label" style="display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--mu); font-weight: 500;">
        <span style="font-size: 8px; color: var(--mu2); margin-right: 4px;">○</span>
        — Sin clasificar —
      </span>
      <span class="check-mark" style="color: var(--green); font-weight: bold; font-size: 12px; visibility: ${!currentValue ? 'visible' : 'hidden'};">✓</span>
    </div>
  `;
  
  container.innerHTML = unclassifiedHtml + treeRoots.map(root => renderTreeNode(root, currentValue)).join('');
  G('eerr-tree-overlay').classList.add('show');
}

function closeTreePanel() {
  G('eerr-tree-overlay').classList.remove('show');
}

async function selectLeafNode(nombre) {
  const groups = await loadEerrGroupsIfNeeded();
  const match = groups.find(g => g.nombre === nombre);
  
  G('m-grupo-eerr').value = nombre;
  G('m-grupo-eerr-text').value = match ? cleanLabel(match.label, match.nivel) : '— Sin clasificar —';
  
  closeTreePanel();
}

async function openModal(){
  G('m-code').value='';
  G('m-name').value='';
  G('m-partida').value='';
  G('m-sign').value='-1';
  G('m-group-container').style.display = 'none';
  G('m-group-blocked-msg').style.display = 'none';
  
  G('m-grupo-eerr').value = '';
  G('m-grupo-eerr-text').value = '— Sin clasificar —';
  
  loadEerrGroupsIfNeeded();
  
  G('modal').classList.add('show');
}
async function editMap(code){
  try {
    if(!isAdmin()){alert('⛔ Acceso denegado: se requiere rol de administrador');return;}
    const m=MAP.find(x=>x.odoo_code===code);if(!m)return;
    G('m-code').value=m.odoo_code;
    G('m-name').value=m.odoo_name;
    G('m-partida').value=m.partida;
    G('m-sign').value=m.sign;
    
    try {
      const resCurrent = await fetch(`/api/mapping/grupo?code=${code}`);
      const current = await resCurrent.json();
      const currentVal = current.group_name || '';
      
      G('m-grupo-eerr').value = currentVal;
      if (currentVal) {
        const groups = await loadEerrGroupsIfNeeded();
        const match = groups.find(g => g.nombre === currentVal);
        G('m-grupo-eerr-text').value = match ? cleanLabel(match.label, match.nivel) : currentVal;
      } else {
        G('m-grupo-eerr-text').value = '— Sin clasificar —';
      }
    } catch (err) {
      console.error("Error loading current mapping EERR group:", err);
      G('m-grupo-eerr').value = '';
      G('m-grupo-eerr-text').value = '— Sin clasificar —';
    }
    
    await fetchOverrides();
    const movable = OVERRIDES_DATA.movable_partidas.find(p => p.partida_name === m.partida);
    
    if (movable) {
      G('m-group-container').style.display = 'block';
      G('m-group-blocked-msg').style.display = 'none';
      const optOrig = G('m-group').options[0];
      optOrig.textContent = `(Original: ${movable.original_subtotal.replace('Subtotal Gastos de ', '')})`;
      
      const hasOverride = OVERRIDES_DATA.overrides.find(o => o.partida_name === m.partida);
      if (hasOverride) {
        G('m-group').value = hasOverride.target_subtotal;
      } else {
        G('m-group').value = 'original';
      }
    } else {
      G('m-group-container').style.display = 'none';
      G('m-group-blocked-msg').style.display = 'block';
      const blocked_leaves = [
        'Gasto por impuesto a las pensiones',
        'Gastos de IGTF',
        'Gastos de comisiones bancarias',
        'Gastos de impresiones de material gráfico',
        'Gastos de patrocinio y donación'
      ];
      if (blocked_leaves.includes(m.partida)) {
        G('m-group-blocked-msg').innerHTML = 'ℹ️ Esta partida está <strong>bloqueada</strong> por reglas de presentación fija (impuestos, IGTF, comisiones).';
      } else {
        G('m-group-blocked-msg').innerHTML = 'ℹ️ Esta partida no califica para reubicación (es un ingreso, costo de ventas o cuenta no operacional).';
      }
    }
    G('modal').classList.add('show');
  } catch (globalErr) {
    console.error("CRITICAL ERROR IN editMap:", globalErr);
    alert("Error en editMap: " + globalErr.message + "\nStack: " + globalErr.stack);
  }
}
function closeModal(){G('modal').classList.remove('show');}
async function saveMap(){
  if(!isAdmin()){alert('⛔ Acceso denegado: se requiere rol de administrador');return;}
  const d={
    odoo_code:G('m-code').value.trim(),
    odoo_name:G('m-name').value.trim(),
    partida:G('m-partida').value.trim(),
    sign:parseInt(G('m-sign').value),
    group_name:G('m-grupo-eerr').value
  };
  if(!d.odoo_code||!d.partida)return alert('Código y Partida obligatorios');
  
  await fetch('/api/mapping',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});
  
  if (G('m-group-container').style.display === 'block') {
    const target = G('m-group').value;
    await fetch('/api/eerr_nodes/overrides', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        partida_name: d.partida,
        target_subtotal: target
      })
    });
  }
  
  closeModal();
  loadMap();
}
async function toggleMapLog(){
  const p=G('maplog-panel');
  if(p.style.display==='none'){p.style.display='block';await loadMapLog();}
  else p.style.display='none';
}
async function loadMapLog(){
  const r=await fetch('/api/mapping/log');const data=await r.json();
  G('maplog-body').innerHTML=data.map(l=>{
    const isD=l.action==='DELETE';
    return`<tr><td><span class="chip ${isD?'chr':'chg'}">${isD?'🗑 Eliminado':'✚ Insertado'}</span></td><td><code style="background:var(--blue-l);padding:2px 5px;border-radius:4px;font-size:10px;color:var(--blue)">${l.odoo_code}</code></td><td style="color:var(--mu)">${l.odoo_name||''}</td><td>${l.partida||''}</td><td style="color:var(--mu2)">${l.created_at}</td><td>${isD?`<button class="btns" onclick="restoreMapEntry(${l.id})">↩ Restaurar</button>`:''}</td></tr>`;
  }).join('')||'<tr><td colspan="6" style="color:var(--mu);text-align:center;padding:12px">Sin cambios registrados.</td></tr>';
}
async function restoreMapEntry(id){
  if(!isAdmin()){alert('⛔ Acceso denegado: se requiere rol de administrador');return;}
  const r=await fetch(`/api/mapping/log/${id}/restore`,{method:'POST'});
  const d=await r.json();
  if(d.ok){loadMap();loadMapLog();}else alert('Error: '+d.error);
}
async function delMap(code){
  if(!isAdmin()){alert('⛔ Acceso denegado: se requiere rol de administrador');return;}
  if(!confirm('¿Eliminar?'))return;await fetch('/api/mapping/'+code,{method:'DELETE'});loadMap();
}
