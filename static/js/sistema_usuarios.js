let _suUsuarios = [];

function _suEsc(s) {
  if (typeof escAttr === 'function') return escAttr(s);
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

async function loadSistemaUsuarios() {
  try {
    const r = await fetch('/api/admin/users');
    const data = await r.json();
    if (!r.ok) {
      showA('su-er', data.error || 'Error cargando usuarios');
      return;
    }
    _suUsuarios = Array.isArray(data) ? data : [];
    renderSistemaUsuarios();
  } catch (e) {
    showA('su-er', 'Error de conexión al cargar usuarios');
  }
}

function renderSistemaUsuarios() {
  const wrap = document.getElementById('su-tabla-wrap');
  if (!wrap) return;
  if (!_suUsuarios.length) {
    wrap.innerHTML = '<div style="padding:16px;color:var(--mu,#64748b);font-size:13px">No hay usuarios registrados.</div>';
    return;
  }

  const me = (typeof currentUser !== 'undefined' && currentUser) ? currentUser.username : '';

  const filas = _suUsuarios.map(u => {
    const esYo = u.username === me;
    const esSA = u.es_superadmin === 1;
    const rolBadge = esSA
      ? '<span style="background:#ede9fe;color:#5b21b6;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600">Superadmin</span>'
      : (u.role === 'admin'
          ? '<span style="background:#dbeafe;color:#1d4ed8;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600">Admin</span>'
          : '<span style="background:#f1f5f9;color:#475569;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600">Viewer</span>');

    const estadoBadge = u.activo
      ? '<span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600">Activo</span>'
      : '<span style="background:#fee2e2;color:#991b1b;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600">Inactivo</span>';

    const bloqueoBadge = u.bloqueado
      ? ' <span style="background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600">Bloqueado</span>'
      : '';

    const disableRol = esYo || esSA;
    const btnRol = `<button style="padding:4px 9px;font-size:11px;border:1px solid var(--border,#cbd5e1);border-radius:6px;background:#fff;${disableRol ? 'opacity:.45;cursor:not-allowed' : 'cursor:pointer'}" ${disableRol ? 'disabled' : ''} onclick="cambiarRolUsuario('${_suEsc(u.username)}', '${_suEsc(u.role)}', ${u.activo ? 1 : 0})">Cambiar rol</button>`;

    const btnToggle = esYo
      ? ''
      : `<button style="padding:4px 9px;font-size:11px;border:1px solid var(--border,#cbd5e1);border-radius:6px;background:#fff;cursor:pointer" onclick="toggleEstadoUsuario('${_suEsc(u.username)}', '${_suEsc(u.role)}', ${u.activo ? 1 : 0})">${u.activo ? 'Desactivar' : 'Activar'}</button>`;

    const btnReset = `<button style="padding:4px 9px;font-size:11px;border:1px solid var(--border,#cbd5e1);border-radius:6px;background:#fff;cursor:pointer" onclick="abrirFormResetUsuario('${_suEsc(u.username)}')">Restablecer clave</button>`;

    const btnUnlock = u.bloqueado
      ? `<button style="padding:4px 9px;font-size:11px;border:1px solid #f59e0b;border-radius:6px;background:#fffbeb;color:#92400e;cursor:pointer" onclick="desbloquearUsuario('${_suEsc(u.username)}')">Desbloquear ahora</button>`
      : '';

    return `
      <tr style="border-bottom:1px solid var(--border,#f1f5f9)">
        <td style="padding:9px 12px;font-weight:600">${_suEsc(u.username)}${esYo ? ' <span style="font-size:10px;color:var(--mu,#64748b)">(tú)</span>' : ''}</td>
        <td style="padding:9px 12px">${rolBadge}</td>
        <td style="padding:9px 12px">${estadoBadge}${bloqueoBadge}</td>
        <td style="padding:9px 12px;text-align:center">${u.intentos_fallidos || 0}</td>
        <td style="padding:9px 12px;display:flex;gap:6px;flex-wrap:wrap">${btnRol}${btnToggle}${btnReset}${btnUnlock}</td>
      </tr>
    `;
  }).join('');

  wrap.innerHTML = `
    <table style="width:100%;border-collapse:collapse;font-size:12px">
      <thead>
        <tr style="text-align:left;border-bottom:1px solid var(--border,#e2e8f0);color:var(--mu,#64748b);background:#f8fafc">
          <th style="padding:9px 12px">Usuario</th>
          <th style="padding:9px 12px">Rol</th>
          <th style="padding:9px 12px">Estado</th>
          <th style="padding:9px 12px;text-align:center">Intentos fallidos</th>
          <th style="padding:9px 12px">Acciones</th>
        </tr>
      </thead>
      <tbody>${filas}</tbody>
    </table>
  `;
}

function abrirFormNuevoUsuario() {
  const box = document.getElementById('su-form-wrap');
  if (!box) return;
  box.style.display = 'block';
  box.innerHTML = `
    <div style="font-weight:600;margin-bottom:10px">Nuevo usuario</div>
    <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end">
      <div class="fg" style="margin:0;min-width:160px;flex:1">
        <label>Usuario</label>
        <input type="text" id="su-new-user" placeholder="Ej: Maria" autocomplete="off">
      </div>
      <div class="fg" style="margin:0;min-width:180px;flex:1">
        <label>Clave (mín. 8 caracteres)</label>
        <input type="password" id="su-new-pass" autocomplete="new-password">
      </div>
      <div class="fg" style="margin:0;min-width:130px">
        <label>Rol</label>
        <select id="su-new-role">
          <option value="viewer">Viewer</option>
          <option value="admin">Admin</option>
        </select>
      </div>
      <div style="display:flex;gap:6px;margin-bottom:4px">
        <button class="bkdl" style="width:auto;padding:7px 14px" onclick="guardarNuevoUsuario()">Guardar</button>
        <button class="bkdl" style="width:auto;padding:7px 14px;background:#64748b" onclick="cerrarSuForm()">Cancelar</button>
      </div>
    </div>
  `;
}

function cerrarSuForm() {
  const box = document.getElementById('su-form-wrap');
  if (!box) return;
  box.style.display = 'none';
  box.innerHTML = '';
}

async function guardarNuevoUsuario() {
  const username = (document.getElementById('su-new-user')?.value || '').trim();
  const password = document.getElementById('su-new-pass')?.value || '';
  const role = document.getElementById('su-new-role')?.value || 'viewer';
  if (!username || password.length < 8) {
    showA('su-er', 'Usuario obligatorio y clave de al menos 8 caracteres.');
    return;
  }
  try {
    const r = await fetch('/api/admin/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password, role }),
    });
    const res = await r.json();
    if (!r.ok) {
      showA('su-er', res.error || 'Error al crear usuario');
      return;
    }
    cerrarSuForm();
    showA('su-ok', `Usuario "${username}" creado.`);
    await loadSistemaUsuarios();
  } catch (e) {
    showA('su-er', 'Error de conexión al crear usuario');
  }
}

async function cambiarRolUsuario(username, roleActual, activoActual) {
  const nuevoRol = roleActual === 'admin' ? 'viewer' : 'admin';
  if (!confirm(`¿Cambiar el rol de "${username}" de ${roleActual} a ${nuevoRol}?`)) return;
  try {
    const r = await fetch(`/api/admin/users/${encodeURIComponent(username)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role: nuevoRol, activo: activoActual }),
    });
    const res = await r.json();
    if (!r.ok) {
      showA('su-er', res.error || 'Error al cambiar rol');
      return;
    }
    showA('su-ok', `Rol de "${username}" actualizado a ${nuevoRol}.`);
    await loadSistemaUsuarios();
  } catch (e) {
    showA('su-er', 'Error de conexión al cambiar rol');
  }
}

async function toggleEstadoUsuario(username, roleActual, activoActual) {
  const nuevoActivo = activoActual ? 0 : 1;
  const accion = nuevoActivo ? 'activar' : 'desactivar';
  if (!confirm(`¿Deseas ${accion} al usuario "${username}"?`)) return;
  try {
    const r = await fetch(`/api/admin/users/${encodeURIComponent(username)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role: roleActual, activo: nuevoActivo }),
    });
    const res = await r.json();
    if (!r.ok) {
      showA('su-er', res.error || 'Error al actualizar usuario');
      return;
    }
    showA('su-ok', `Usuario "${username}" ${nuevoActivo ? 'activado' : 'desactivado'}.`);
    await loadSistemaUsuarios();
  } catch (e) {
    showA('su-er', 'Error de conexión al actualizar usuario');
  }
}

function abrirFormResetUsuario(username) {
  const box = document.getElementById('su-form-wrap');
  if (!box) return;
  box.style.display = 'block';
  box.innerHTML = `
    <div style="font-weight:600;margin-bottom:10px">Restablecer clave de ${_suEsc(username)}</div>
    <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end">
      <div class="fg" style="margin:0;min-width:220px;flex:1">
        <label>Clave nueva (mín. 8 caracteres)</label>
        <input type="password" id="su-reset-pass" autocomplete="new-password">
      </div>
      <div style="display:flex;gap:6px;margin-bottom:4px">
        <button class="bkdl" style="width:auto;padding:7px 14px" onclick="guardarResetUsuario('${_suEsc(username)}')">Guardar</button>
        <button class="bkdl" style="width:auto;padding:7px 14px;background:#64748b" onclick="cerrarSuForm()">Cancelar</button>
      </div>
    </div>
  `;
}

async function guardarResetUsuario(username) {
  const newPassword = document.getElementById('su-reset-pass')?.value || '';
  if (newPassword.length < 8) {
    showA('su-er', 'La clave nueva debe tener al menos 8 caracteres.');
    return;
  }
  try {
    const r = await fetch('/api/admin/reset_password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, new_password: newPassword }),
    });
    const res = await r.json();
    if (!r.ok || !res.success) {
      showA('su-er', res.message || res.error || 'Error al restablecer clave');
      return;
    }
    cerrarSuForm();
    showA('su-ok', res.message || `Clave de "${username}" restablecida.`);
    await loadSistemaUsuarios();
  } catch (e) {
    showA('su-er', 'Error de conexión al restablecer clave');
  }
}

async function desbloquearUsuario(username) {
  if (!confirm(`¿Desbloquear ahora al usuario "${username}"?`)) return;
  try {
    const r = await fetch(`/api/admin/users/${encodeURIComponent(username)}/unlock`, { method: 'POST' });
    const res = await r.json();
    if (!r.ok) {
      showA('su-er', res.error || 'Error al desbloquear usuario');
      return;
    }
    showA('su-ok', `Usuario "${username}" desbloqueado.`);
    await loadSistemaUsuarios();
  } catch (e) {
    showA('su-er', 'Error de conexión al desbloquear usuario');
  }
}

function toggleUserProfileMenu(ev) {
  if (ev) ev.stopPropagation();
  const menu = document.getElementById('user-profile-menu');
  if (!menu) return;
  menu.style.display = (menu.style.display === 'none' || !menu.style.display) ? 'block' : 'none';
}

function abrirMiPerfil() {
  const menu = document.getElementById('user-profile-menu');
  if (menu) menu.style.display = 'none';
  const ok = document.getElementById('mp-ok');
  const er = document.getElementById('mp-er');
  if (ok) { ok.textContent = ''; ok.classList.remove('show'); }
  if (er) { er.textContent = ''; er.classList.remove('show'); }
  ['mp-actual', 'mp-nueva', 'mp-confirmar'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  const ov = document.getElementById('modal-mi-perfil');
  if (ov) ov.classList.add('show');
}

function cerrarMiPerfil() {
  const ov = document.getElementById('modal-mi-perfil');
  if (ov) ov.classList.remove('show');
}

async function guardarMiClave() {
  const clave_actual = document.getElementById('mp-actual')?.value || '';
  const clave_nueva = document.getElementById('mp-nueva')?.value || '';
  const clave_confirmacion = document.getElementById('mp-confirmar')?.value || '';
  if (!clave_actual || !clave_nueva || !clave_confirmacion) {
    showA('mp-er', 'Todos los campos son obligatorios.');
    return;
  }
  if (clave_nueva.length < 8) {
    showA('mp-er', 'La clave nueva debe tener al menos 8 caracteres.');
    return;
  }
  if (clave_nueva !== clave_confirmacion) {
    showA('mp-er', 'La confirmación no coincide con la clave nueva.');
    return;
  }
  try {
    const r = await fetch('/api/perfil/cambiar_clave', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ clave_actual, clave_nueva, clave_confirmacion }),
    });
    const res = await r.json();
    if (!r.ok) {
      showA('mp-er', res.error || 'Error al actualizar la clave');
      return;
    }
    ['mp-actual', 'mp-nueva', 'mp-confirmar'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.value = '';
    });
    showA('mp-ok', res.message || 'Clave actualizada correctamente');
    setTimeout(() => cerrarMiPerfil(), 1200);
  } catch (e) {
    showA('mp-er', 'Error de conexión al actualizar la clave');
  }
}
