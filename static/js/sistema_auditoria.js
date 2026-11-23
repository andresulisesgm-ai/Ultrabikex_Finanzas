function _audEsc(s) {
  if (typeof escAttr === 'function') return escAttr(s);
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

async function loadAuditoria() {
  const wrap = document.getElementById('aud-tabla-wrap');
  const totEl = document.getElementById('aud-total');
  const modSel = document.getElementById('aud-modulo');
  if (!wrap) return;

  const modulo = modSel ? modSel.value : '';
  const usuario = (document.getElementById('aud-usuario')?.value || '').trim();
  const desde = document.getElementById('aud-desde')?.value || '';
  const hasta = document.getElementById('aud-hasta')?.value || '';

  const params = new URLSearchParams();
  params.set('limit', '100');
  if (modulo) params.set('modulo', modulo);
  if (usuario) params.set('usuario', usuario);
  if (desde) params.set('desde', desde);
  if (hasta) params.set('hasta', hasta);

  wrap.innerHTML = '<div style="padding:16px;font-size:12px;color:var(--mu,#64748b)">Cargando registro de auditoría...</div>';
  try {
    const r = await fetch(`/api/admin/audit_log?${params.toString()}`);
    const data = await r.json();
    if (!r.ok) {
      wrap.innerHTML = `<div style="padding:16px;font-size:12px;color:#b91c1c">${_audEsc(data.error || 'Error al cargar auditoría')}</div>`;
      return;
    }

    if (modSel && Array.isArray(data.modulos)) {
      const prev = modSel.value;
      modSel.innerHTML = '<option value="">Todos</option>' + data.modulos.map(m => `<option value="${_audEsc(m)}">${_audEsc(m)}</option>`).join('');
      if (data.modulos.includes(prev)) modSel.value = prev;
    }

    if (totEl) totEl.textContent = `${data.total || 0} registros`;

    const items = Array.isArray(data.items) ? data.items : [];
    if (!items.length) {
      wrap.innerHTML = '<div style="padding:16px;font-size:13px;color:var(--mu,#64748b)">No hay registros de auditoría para los filtros seleccionados.</div>';
      return;
    }

    const rows = items.map(it => `
      <tr style="border-bottom:1px solid var(--border,#f1f5f9)">
        <td style="padding:8px 10px;white-space:nowrap;font-family:monospace">${_audEsc(it.fecha_hora)}</td>
        <td style="padding:8px 10px;font-weight:600">${_audEsc(it.usuario)}</td>
        <td style="padding:8px 10px"><span style="background:#f1f5f9;color:#334155;padding:2px 7px;border-radius:999px;font-size:11px">${_audEsc(it.modulo)}</span></td>
        <td style="padding:8px 10px">${_audEsc(it.accion)}</td>
        <td style="padding:8px 10px;color:var(--mu,#475569);word-break:break-word">${_audEsc(it.detalle || '')}</td>
      </tr>
    `).join('');

    wrap.innerHTML = `
      <table style="width:100%;border-collapse:collapse;font-size:12px">
        <thead>
          <tr style="text-align:left;border-bottom:1px solid var(--border,#e2e8f0);color:var(--mu,#64748b);background:#f8fafc">
            <th style="padding:8px 10px">Fecha/Hora (VE)</th>
            <th style="padding:8px 10px">Usuario</th>
            <th style="padding:8px 10px">Módulo</th>
            <th style="padding:8px 10px">Acción</th>
            <th style="padding:8px 10px">Detalle</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    `;
  } catch (e) {
    wrap.innerHTML = '<div style="padding:16px;font-size:12px;color:#b91c1c">Error de conexión al cargar auditoría.</div>';
  }
}

function limpiarFiltrosAuditoria() {
  const modSel = document.getElementById('aud-modulo');
  const usrIn = document.getElementById('aud-usuario');
  const desIn = document.getElementById('aud-desde');
  const hasIn = document.getElementById('aud-hasta');
  if (modSel) modSel.value = '';
  if (usrIn) usrIn.value = '';
  if (desIn) desIn.value = '';
  if (hasIn) hasIn.value = '';
  loadAuditoria();
}
