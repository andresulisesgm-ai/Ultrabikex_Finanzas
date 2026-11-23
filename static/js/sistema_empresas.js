let _seEmpresas = [];
const _seExpandidas = new Set();
let _seEditEmpId = null;
let _seNewUnitEmpId = null;
let _seEditUnitId = null;

function _seEsc(s) {
  if (typeof escAttr === 'function') return escAttr(s);
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

async function refrescarSelectoresGlobales() {
  if (typeof loadEmpresasDropdown === 'function') await loadEmpresasDropdown();
  if (typeof loadUnidadesCache === 'function') await loadUnidadesCache();
  try {
    const r = await fetch('/api/unidades');
    if (r.ok) {
      const data = await r.json();
      if (Array.isArray(data)) {
        window.units = data.map(u => u.nombre);
      }
    }
  } catch (e) {}
  if (typeof updateUnitSelectorsForEmpresa === 'function') updateUnitSelectorsForEmpresa();
}

async function loadSistemaEmpresas() {
  try {
    const r = await fetch('/api/sistema/empresas');
    const data = await r.json();
    if (!r.ok) {
      showA('se-er', data.error || 'Error cargando empresas');
      return;
    }
    _seEmpresas = Array.isArray(data) ? data : [];
    renderSistemaEmpresas();
  } catch (e) {
    showA('se-er', 'Error de conexión al cargar empresas');
  }
}

function abrirFormNuevaEmpresa() {
  const box = document.getElementById('se-form-empresa');
  if (!box) return;
  box.style.display = 'block';
  box.innerHTML = `
    <div style="font-weight:600;margin-bottom:10px">Nueva Empresa</div>
    <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end">
      <div class="fg" style="margin:0;min-width:180px;flex:1">
        <label>Nombre corto</label>
        <input type="text" id="se-new-emp-corto" placeholder="Ej: Ultrax Norte">
      </div>
      <div class="fg" style="margin:0;min-width:220px;flex:2">
        <label>Nombre legal</label>
        <input type="text" id="se-new-emp-legal" placeholder="Ej: Ultrax Norte C.A.">
      </div>
      <label style="display:flex;align-items:center;gap:6px;font-size:12px;margin-bottom:8px;cursor:pointer">
        <input type="checkbox" id="se-new-emp-unica">
        Unidad única (crear unidad automáticamente)
      </label>
      <div style="display:flex;gap:6px;margin-bottom:4px">
        <button class="bkdl" style="width:auto;padding:7px 14px" onclick="guardarNuevaEmpresa()">Guardar</button>
        <button class="bkdl" style="width:auto;padding:7px 14px;background:#64748b" onclick="cerrarFormNuevaEmpresa()">Cancelar</button>
      </div>
    </div>
  `;
}

function cerrarFormNuevaEmpresa() {
  const box = document.getElementById('se-form-empresa');
  if (!box) return;
  box.style.display = 'none';
  box.innerHTML = '';
}

async function guardarNuevaEmpresa() {
  const nombre_corto = (document.getElementById('se-new-emp-corto')?.value || '').trim();
  const nombre_legal = (document.getElementById('se-new-emp-legal')?.value || '').trim();
  const unidad_unica = Boolean(document.getElementById('se-new-emp-unica')?.checked);
  if (!nombre_corto || !nombre_legal) {
    showA('se-er', 'Nombre corto y nombre legal son obligatorios.');
    return;
  }
  try {
    const r = await fetch('/api/sistema/empresas', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nombre_corto, nombre_legal, unidad_unica }),
    });
    const res = await r.json();
    if (!r.ok) {
      showA('se-er', res.error || 'Error al crear empresa');
      return;
    }
    cerrarFormNuevaEmpresa();
    showA('se-ok', `Empresa "${nombre_corto}" creada.`);
    await loadSistemaEmpresas();
    await refrescarSelectoresGlobales();
  } catch (e) {
    showA('se-er', 'Error de conexión al crear empresa');
  }
}

function abrirEditEmpresa(id) {
  _seEditEmpId = id;
  renderSistemaEmpresas();
}

function cancelarEditEmpresa() {
  _seEditEmpId = null;
  renderSistemaEmpresas();
}

async function guardarEditEmpresa(id) {
  const nombre_corto = (document.getElementById(`se-edit-emp-corto-${id}`)?.value || '').trim();
  const nombre_legal = (document.getElementById(`se-edit-emp-legal-${id}`)?.value || '').trim();
  if (!nombre_corto || !nombre_legal) {
    showA('se-er', 'Nombre corto y nombre legal son obligatorios.');
    return;
  }
  try {
    const r = await fetch(`/api/sistema/empresas/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nombre_corto, nombre_legal }),
    });
    const res = await r.json();
    if (!r.ok) {
      showA('se-er', res.error || 'Error al actualizar empresa');
      return;
    }
    _seEditEmpId = null;
    showA('se-ok', `Empresa "${nombre_corto}" actualizada.`);
    await loadSistemaEmpresas();
    await refrescarSelectoresGlobales();
  } catch (e) {
    showA('se-er', 'Error de conexión al actualizar empresa');
  }
}

async function toggleEmpresa(id) {
  const emp = _seEmpresas.find(e => e.id === id);
  if (!emp) return;
  if (emp.activo) {
    if (!confirm("También se desactivarán sus " + emp.unidades_activas + " unidades activas. Los datos históricos no se borran.")) return;
  } else {
    if (!confirm(`¿Activar la empresa "${emp.nombre_corto}"?`)) return;
  }
  try {
    const r = await fetch(`/api/sistema/empresas/${id}/toggle`, { method: 'POST' });
    const res = await r.json();
    if (!r.ok) {
      showA('se-er', res.error || 'Error al cambiar estado de empresa');
      return;
    }
    showA('se-ok', `Empresa "${emp.nombre_corto}" ${res.activo ? 'activada' : 'desactivada'}.`);
    await loadSistemaEmpresas();
    await refrescarSelectoresGlobales();
  } catch (e) {
    showA('se-er', 'Error de conexión al cambiar estado de empresa');
  }
}

function toggleExpandEmpresa(id) {
  if (_seExpandidas.has(id)) _seExpandidas.delete(id);
  else _seExpandidas.add(id);
  renderSistemaEmpresas();
}

function abrirNuevaUnidad(empId) {
  _seExpandidas.add(empId);
  _seNewUnitEmpId = empId;
  _seEditUnitId = null;
  renderSistemaEmpresas();
}

function cancelarNuevaUnidad() {
  _seNewUnitEmpId = null;
  renderSistemaEmpresas();
}

async function guardarNuevaUnidad(empId) {
  const nombre = (document.getElementById(`se-new-uni-nombre-${empId}`)?.value || '').trim();
  const es_pseudo = Boolean(document.getElementById(`se-new-uni-pseudo-${empId}`)?.checked);
  const excluir_comparativas = Boolean(document.getElementById(`se-new-uni-excl-${empId}`)?.checked);
  const recibe_plug_divisa = Boolean(document.getElementById(`se-new-uni-plug-${empId}`)?.checked);
  if (!nombre) {
    showA('se-er', 'El nombre de la unidad es obligatorio.');
    return;
  }
  try {
    const r = await fetch('/api/sistema/unidades', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ empresa_id: empId, nombre, es_pseudo, excluir_comparativas, recibe_plug_divisa }),
    });
    const res = await r.json();
    if (!r.ok) {
      showA('se-er', res.error || 'Error al crear unidad');
      return;
    }
    _seNewUnitEmpId = null;
    showA('se-ok', `Unidad "${nombre}" creada.`);
    await loadSistemaEmpresas();
    await refrescarSelectoresGlobales();
  } catch (e) {
    showA('se-er', 'Error de conexión al crear unidad');
  }
}

function abrirEditUnidad(unitId) {
  _seEditUnitId = unitId;
  _seNewUnitEmpId = null;
  renderSistemaEmpresas();
}

function cancelarEditUnidad() {
  _seEditUnitId = null;
  renderSistemaEmpresas();
}

async function guardarEditUnidad(unitId) {
  const nombre = (document.getElementById(`se-edit-uni-nombre-${unitId}`)?.value || '').trim();
  const es_pseudo = Boolean(document.getElementById(`se-edit-uni-pseudo-${unitId}`)?.checked);
  const excluir_comparativas = Boolean(document.getElementById(`se-edit-uni-excl-${unitId}`)?.checked);
  const recibe_plug_divisa = Boolean(document.getElementById(`se-edit-uni-plug-${unitId}`)?.checked);
  if (!nombre) {
    showA('se-er', 'El nombre de la unidad es obligatorio.');
    return;
  }
  try {
    const r = await fetch(`/api/sistema/unidades/${unitId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nombre, es_pseudo, excluir_comparativas, recibe_plug_divisa }),
    });
    const res = await r.json();
    if (!r.ok) {
      showA('se-er', res.error || 'Error al actualizar unidad');
      return;
    }
    _seEditUnitId = null;
    showA('se-ok', `Unidad "${nombre}" actualizada.`);
    await loadSistemaEmpresas();
    await refrescarSelectoresGlobales();
  } catch (e) {
    showA('se-er', 'Error de conexión al actualizar unidad');
  }
}

async function toggleUnidad(unitId, nombre, activoActual) {
  const accion = activoActual ? 'desactivar' : 'activar';
  if (!confirm(`¿Deseas ${accion} la unidad "${nombre}"? Los datos históricos no se borran.`)) return;
  try {
    const r = await fetch(`/api/sistema/unidades/${unitId}/toggle`, { method: 'POST' });
    const res = await r.json();
    if (!r.ok) {
      showA('se-er', res.error || 'Error al cambiar estado de unidad');
      return;
    }
    showA('se-ok', `Unidad "${nombre}" ${res.activo ? 'activada' : 'desactivada'}.`);
    await loadSistemaEmpresas();
    await refrescarSelectoresGlobales();
  } catch (e) {
    showA('se-er', 'Error de conexión al cambiar estado de unidad');
  }
}

function renderSistemaEmpresas() {
  const cont = document.getElementById('se-lista');
  if (!cont) return;
  const q = (document.getElementById('se-search')?.value || '').trim().toLowerCase();

  const filtradas = _seEmpresas.filter(emp => {
    if (!q) return true;
    if ((emp.nombre_corto || '').toLowerCase().includes(q)) return true;
    if ((emp.nombre_legal || '').toLowerCase().includes(q)) return true;
    return (emp.unidades || []).some(u => (u.nombre || '').toLowerCase().includes(q));
  });

  if (!filtradas.length) {
    cont.innerHTML = '<div style="padding:18px;color:var(--mu,#64748b);font-size:13px">No hay empresas o unidades que coincidan con la búsqueda.</div>';
    return;
  }

  const ordenadas = [
    ...filtradas.filter(e => e.protegida),
    ...filtradas.filter(e => !e.protegida),
  ];

  cont.innerHTML = ordenadas.map(emp => {
    const badgeEstado = emp.activo
      ? '<span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600">Activa</span>'
      : '<span style="background:#fee2e2;color:#991b1b;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600">Inactiva</span>';

    if (emp.protegida) {
      return `
        <div style="background:#fff;border:1px solid var(--border,#e2e8f0);border-radius:10px;padding:14px;margin-bottom:12px">
          <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap">
            <div>
              <span style="font-weight:700;font-size:14px">${_seEsc(emp.nombre_corto)}</span>
              <span style="color:var(--mu,#64748b);font-size:12px;margin-left:8px">${_seEsc(emp.nombre_legal)}</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px">
              ${badgeEstado}
              <span style="background:#f1f5f9;color:#475569;padding:3px 9px;border-radius:6px;font-size:11px;font-weight:600">🔒 Sistema — no editable</span>
            </div>
          </div>
        </div>
      `;
    }

    const expandida = _seExpandidas.has(emp.id);
    const editandoEmp = _seEditEmpId === emp.id;

    const editEmpHtml = editandoEmp ? `
      <div style="margin-top:10px;padding-top:10px;border-top:1px solid var(--border,#e2e8f0);display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end">
        <div class="fg" style="margin:0;flex:1;min-width:180px">
          <label>Nombre corto</label>
          <input type="text" id="se-edit-emp-corto-${emp.id}" value="${_seEsc(emp.nombre_corto)}">
        </div>
        <div class="fg" style="margin:0;flex:2;min-width:220px">
          <label>Nombre legal</label>
          <input type="text" id="se-edit-emp-legal-${emp.id}" value="${_seEsc(emp.nombre_legal)}">
        </div>
        <div style="display:flex;gap:6px;margin-bottom:4px">
          <button class="bkdl" style="width:auto;padding:6px 12px" onclick="guardarEditEmpresa(${emp.id})">Guardar</button>
          <button class="bkdl" style="width:auto;padding:6px 12px;background:#64748b" onclick="cancelarEditEmpresa()">Cancelar</button>
        </div>
      </div>
    ` : '';

    const newUnitHtml = (expandida && _seNewUnitEmpId === emp.id) ? `
      <div style="background:#f8fafc;border:1px solid var(--border,#e2e8f0);border-radius:8px;padding:10px;margin:10px 0;display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end">
        <div class="fg" style="margin:0;min-width:180px;flex:1">
          <label>Nombre de unidad</label>
          <input type="text" id="se-new-uni-nombre-${emp.id}" placeholder="Ej: Chacao">
        </div>
        <label style="display:flex;align-items:center;gap:5px;font-size:12px;margin-bottom:8px;cursor:pointer">
          <input type="checkbox" id="se-new-uni-pseudo-${emp.id}"> Unidad única
        </label>
        <label style="display:flex;align-items:center;gap:5px;font-size:12px;margin-bottom:8px;cursor:pointer">
          <input type="checkbox" id="se-new-uni-excl-${emp.id}"> Excluir Comparativas
        </label>
        <label style="display:flex;align-items:center;gap:5px;font-size:12px;margin-bottom:8px;cursor:pointer">
          <input type="checkbox" id="se-new-uni-plug-${emp.id}"> Recibe Plug Divisa
        </label>
        <div style="display:flex;gap:6px;margin-bottom:4px">
          <button class="bkdl" style="width:auto;padding:6px 12px" onclick="guardarNuevaUnidad(${emp.id})">Guardar</button>
          <button class="bkdl" style="width:auto;padding:6px 12px;background:#64748b" onclick="cancelarNuevaUnidad()">Cancelar</button>
        </div>
      </div>
    ` : '';

    const filasUnidades = (emp.unidades || []).map(u => {
      if (_seEditUnitId === u.id) {
        return `
          <tr>
            <td colspan="6" style="background:#f8fafc;padding:10px">
              <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end">
                <div class="fg" style="margin:0;min-width:180px;flex:1">
                  <label>Nombre</label>
                  <input type="text" id="se-edit-uni-nombre-${u.id}" value="${_seEsc(u.nombre)}">
                </div>
                <label style="display:flex;align-items:center;gap:5px;font-size:12px;margin-bottom:8px;cursor:pointer">
                  <input type="checkbox" id="se-edit-uni-pseudo-${u.id}" ${u.es_pseudo ? 'checked' : ''}> Unidad única
                </label>
                <label style="display:flex;align-items:center;gap:5px;font-size:12px;margin-bottom:8px;cursor:pointer">
                  <input type="checkbox" id="se-edit-uni-excl-${u.id}" ${u.excluir_comparativas ? 'checked' : ''}> Excluir Comparativas
                </label>
                <label style="display:flex;align-items:center;gap:5px;font-size:12px;margin-bottom:8px;cursor:pointer">
                  <input type="checkbox" id="se-edit-uni-plug-${u.id}" ${u.recibe_plug_divisa ? 'checked' : ''}> Recibe Plug Divisa
                </label>
                <div style="display:flex;gap:6px;margin-bottom:4px">
                  <button class="bkdl" style="width:auto;padding:6px 12px" onclick="guardarEditUnidad(${u.id})">Guardar</button>
                  <button class="bkdl" style="width:auto;padding:6px 12px;background:#64748b" onclick="cancelarEditUnidad()">Cancelar</button>
                </div>
              </div>
            </td>
          </tr>
        `;
      }
      const badgeU = u.activo
        ? '<span style="background:#dcfce7;color:#166534;padding:2px 7px;border-radius:999px;font-size:11px;font-weight:600">Activa</span>'
        : '<span style="background:#fee2e2;color:#991b1b;padding:2px 7px;border-radius:999px;font-size:11px;font-weight:600">Inactiva</span>';
      return `
        <tr>
          <td style="padding:7px 8px;font-weight:600">${_seEsc(u.nombre)}</td>
          <td style="padding:7px 8px">${u.es_pseudo ? 'Unidad única' : 'Sucursal'}</td>
          <td style="padding:7px 8px;text-align:center">${u.excluir_comparativas ? '✓' : '—'}</td>
          <td style="padding:7px 8px;text-align:center">${u.recibe_plug_divisa ? '✓' : '—'}</td>
          <td style="padding:7px 8px">${badgeU}</td>
          <td style="padding:7px 8px;display:flex;gap:6px">
            <button style="padding:4px 9px;font-size:11px;border:1px solid var(--border,#cbd5e1);border-radius:6px;background:#fff;cursor:pointer" onclick="abrirEditUnidad(${u.id})">Editar</button>
            <button style="padding:4px 9px;font-size:11px;border:1px solid var(--border,#cbd5e1);border-radius:6px;background:#fff;cursor:pointer" onclick="toggleUnidad(${u.id}, '${_seEsc(u.nombre)}', ${u.activo ? 1 : 0})">${u.activo ? 'Desactivar' : 'Activar'}</button>
          </td>
        </tr>
      `;
    }).join('');

    const unidadesHtml = expandida ? `
      <div style="margin-top:12px;padding-top:12px;border-top:1px solid var(--border,#e2e8f0)">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
          <span style="font-size:12px;font-weight:600;color:var(--mu,#64748b)">Unidades (${emp.unidades_activas} / ${emp.unidades_total} activas)</span>
          <button class="bkdl" style="width:auto;padding:5px 11px;font-size:12px;${emp.activo ? '' : 'opacity:.5;cursor:not-allowed'}" ${emp.activo ? '' : 'disabled'} onclick="abrirNuevaUnidad(${emp.id})">+ Nueva Unidad</button>
        </div>
        ${newUnitHtml}
        <div style="overflow-x:auto">
          <table style="width:100%;border-collapse:collapse;font-size:12px">
            <thead>
              <tr style="text-align:left;border-bottom:1px solid var(--border,#e2e8f0);color:var(--mu,#64748b)">
                <th style="padding:6px 8px">Nombre</th>
                <th style="padding:6px 8px">Tipo</th>
                <th style="padding:6px 8px;text-align:center">Excluir Comparativas</th>
                <th style="padding:6px 8px;text-align:center">Recibe Plug Divisa</th>
                <th style="padding:6px 8px">Estado</th>
                <th style="padding:6px 8px">Acciones</th>
              </tr>
            </thead>
            <tbody>
              ${filasUnidades || '<tr><td colspan="6" style="padding:10px;color:var(--mu,#64748b)">Sin unidades registradas.</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>
    ` : '';

    return `
      <div style="background:#fff;border:1px solid var(--border,#e2e8f0);border-radius:10px;padding:14px;margin-bottom:12px">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap">
          <div>
            <span style="font-weight:700;font-size:14px">${_seEsc(emp.nombre_corto)}</span>
            <span style="color:var(--mu,#64748b);font-size:12px;margin-left:8px">${_seEsc(emp.nombre_legal)}</span>
            <span style="color:var(--mu,#64748b);font-size:12px;margin-left:10px">(${emp.unidades_activas} / ${emp.unidades_total} unidades)</span>
          </div>
          <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">
            ${badgeEstado}
            <button style="padding:5px 10px;font-size:12px;border:1px solid var(--border,#cbd5e1);border-radius:6px;background:#fff;cursor:pointer" onclick="abrirEditEmpresa(${emp.id})">Editar</button>
            <button style="padding:5px 10px;font-size:12px;border:1px solid var(--border,#cbd5e1);border-radius:6px;background:#fff;cursor:pointer" onclick="toggleEmpresa(${emp.id})">${emp.activo ? 'Desactivar' : 'Activar'}</button>
            <button style="padding:5px 10px;font-size:12px;border:1px solid var(--border,#cbd5e1);border-radius:6px;background:#f8fafc;cursor:pointer" onclick="toggleExpandEmpresa(${emp.id})">${expandida ? 'Ocultar unidades ▲' : 'Ver unidades ▼'}</button>
          </div>
        </div>
        ${editEmpHtml}
        ${unidadesHtml}
      </div>
    `;
  }).join('');
}
