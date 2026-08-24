// ── EXPORTAR BRIEFING IA ─────────────────────────────────────────────────────
let aiTipoActual = 'eerr';

const AI_TIPO_META = {
  eerr:               { label: 'EERR',                  desc: 'Estado de resultados en bolívares' },
  eerr_divisa:        { label: 'EERR Divisa Real',       desc: 'EERR ajustado a dólares reales' },
  esf:                { label: 'ESF',                    desc: 'Balance general consolidado' },
  esf_divisa:         { label: 'ESF Divisa Real',        desc: 'Balance ajustado a divisa real, por trimestre' },
  completo:           { label: 'Completo',               desc: 'EERR + EERR Divisa Real + ESF + ESF Divisa Real' },
  comparativa:        { label: 'Comparativa',            desc: 'Comparación de unidades del grupo' },
  comparativa_divisa: { label: 'Comparativa Divisa Real', desc: 'Comparación de unidades en dólares reales' }
};

const AI_MONTH_LABELS = {
  '':'año completo','ENE':'Enero','FEB':'Febrero','MAR':'Marzo','ABR':'Abril',
  'MAY':'Mayo','JUN':'Junio','JUL':'Julio','AGO':'Agosto',
  'SEPT':'Septiembre','OCT':'Octubre','NOV':'Noviembre','DIC':'Diciembre'
};

function setAiTipo(tipo, el) {
  aiTipoActual = tipo;
  document.querySelectorAll('[id^="ai-tipo-"]').forEach(b => {
    b.style.background = 'var(--bg)';
    b.style.border = '0.5px solid var(--bd)';
    b.style.borderRadius = '6px';
    const lbl = b.querySelector('span:first-child');
    if (lbl) lbl.style.color = 'var(--tx)';
  });
  el.style.background = 'var(--green-l)';
  el.style.border = '1.5px solid var(--green)';
  el.style.borderRadius = '6px';
  const lbl = el.querySelector('span:first-child');
  if (lbl) lbl.style.color = 'var(--green)';
  const unitSel = document.getElementById('ai-unit');
  const unitWrapper = document.getElementById('ai-unit-wrapper');
  const unitsCompWrapper = document.getElementById('ai-units-comparativa-wrapper');
  const quarterWrapper = document.getElementById('ai-quarter-wrapper');

  if (quarterWrapper) {
    quarterWrapper.style.display = (tipo === 'esf_divisa' || tipo === 'completo') ? 'block' : 'none';
  }

  if (tipo === 'comparativa' || tipo === 'comparativa_divisa') {
    if (unitWrapper) unitWrapper.style.display = 'none';
    if (unitsCompWrapper) unitsCompWrapper.style.display = 'block';
  } else {
    if (unitWrapper) unitWrapper.style.display = 'block';
    if (unitsCompWrapper) unitsCompWrapper.style.display = 'none';
    if (unitSel) {
      if (tipo === 'esf' || tipo === 'esf_divisa') {
        unitSel.value = '';
        unitSel.disabled = true;
        unitSel.style.opacity = '0.4';
        unitSel.style.cursor = 'not-allowed';
      } else {
        unitSel.disabled = false;
        unitSel.style.opacity = '1';
        unitSel.style.cursor = 'pointer';
      }
    }
  }
  updateAiBriefingPreview();
}

function updateAiBriefingPreview() {
  const tipo  = aiTipoActual;
  const unit  = document.getElementById('ai-unit') ? document.getElementById('ai-unit').value : '';
  const year  = document.getElementById('ai-year') ? document.getElementById('ai-year').value : '2026';
  const month = document.getElementById('ai-month') ? document.getElementById('ai-month').value : '';

  const unitLabel  = unit || 'Consolidado grupo';
  const monthLabel = AI_MONTH_LABELS[month] || month;
  const tipoLabel  = AI_TIPO_META[tipo] ? AI_TIPO_META[tipo].label : tipo;

  const TIPO_FOCO = {
    eerr:               'rentabilidad operativa, estructura de costos y evolución de márgenes',
    eerr_divisa:         'impacto cambiario sobre el resultado, ajuste por diferencial BCV/paralela y poder adquisitivo real',
    esf:                 'posición patrimonial, estructura de activos y nivel de endeudamiento',
    esf_divisa:          'posición líquida real (efectivo y obligaciones de corto plazo) en dólares, por trimestre',
    completo:            'visión integral: resultado operativo, posición de balance y coherencia entre ambos estados',
    comparativa:         'descomposición de brechas operativas y cambiarias entre las distintas unidades del grupo',
    comparativa_divisa:  'descomposición de brechas de rendimiento entre unidades en poder adquisitivo real'
  };

  const foco = TIPO_FOCO[tipo] || tipo;

  let promptLabel, contexto;
  if (tipo === 'comparativa' || tipo === 'comparativa_divisa') {
    const esDivisaComp = (tipo === 'comparativa_divisa');
    promptLabel = esDivisaComp ? 'CFO comparativo — brechas en dólares reales' : 'CFO comparativo — brechas de portafolio';
    if (esDivisaComp) {
      contexto = !month
        ? 'El CFO evaluará si la brecha real entre unidades se amplió o se cerró durante el año, ya sin ruido cambiario nominal.'
        : 'El CFO descompondrá la brecha en poder adquisitivo real entre las unidades para el mes seleccionado.';
    } else if (!month) {
      contexto = 'El CFO analizará la trayectoria anual comparada entre las unidades del grupo, evaluando cambios estructurales y consistencia.';
    } else {
      contexto = 'El CFO realizará una descomposición de brechas operativas y cambiarias entre las unidades para el mes seleccionado.';
    }
  } else {
    if (!unit) {
      promptLabel = 'CFO consolidado — análisis de portafolio';
      if (!month) {
        contexto = 'El CFO revisará el desempeño anual del grupo como portafolio, comparando unidades y detectando concentración de riesgo.';
      } else {
        contexto = 'El CFO analizará ' + monthLabel + ' dentro del contexto acumulado del grupo, con foco en señales tempranas de desviación.';
      }
    } else if (month) {
      promptLabel = 'CFO unidad/mes — análisis quirúrgico';
      contexto = 'El CFO hará un análisis quirúrgico de ' + unit + ' en ' + monthLabel + ', identificando causas raíz de variaciones puntuales.';
    } else {
      promptLabel = 'CFO anual — cierre y posición estructural';
      contexto = 'El CFO hará el cierre anual de ' + unit + ', evaluando posición estructural y sostenibilidad del margen.';
    }
  }

  const badge = document.getElementById('ai-prompt-label');
  if (badge) badge.textContent = 'Prompt: ' + promptLabel;

  const dataLine = document.getElementById('ai-preview-data');
  if (dataLine) dataLine.textContent = tipoLabel + ' ' + year + ' — ' + unitLabel + (month ? ', ' + monthLabel : ', año completo');

  const desc = document.getElementById('ai-preview-desc');
  let descText = 'Foco: ' + foco + '. ' + contexto;
  if (tipo === 'completo' && unit) {
    descText += ' Nota: el ESF incluido es siempre consolidado del grupo, independientemente de la unidad seleccionada.';
  }
  if (desc) desc.textContent = descText;

  cargarPromptConfigurado();
}

function getTipoPromptActual() {
  const unit  = document.getElementById('ai-unit') ? document.getElementById('ai-unit').value : '';
  const month = document.getElementById('ai-month') ? document.getElementById('ai-month').value : '';
  const tipo  = aiTipoActual;
  // 'tipo' ya lleva la señal de Divisa Real en su propio nombre (eerr_divisa,
  // esf_divisa, comparativa_divisa) -- no depende de ningún estado global.
  const es_divisa = tipo.includes('divisa');

  if (tipo === 'comparativa' || tipo === 'comparativa_divisa') {
    if (es_divisa) {
      return (month === '') ? 'comparativo_divisa_anual' : 'comparativo_divisa_mes';
    } else {
      return (month === '') ? 'comparativo_anual' : 'comparativo_mes';
    }
  } else if (tipo === 'esf') {
    return 'esf_consolidado';
  } else if (tipo === 'esf_divisa') {
    return 'esf_divisa_real';
  } else {
    if (unit === '') {
      if (es_divisa) {
        return (month === '') ? 'consolidado_divisa_anual' : 'consolidado_divisa_mes';
      } else {
        return (month === '') ? 'consolidado' : 'consolidado_mes';
      }
    } else if (month === '') {
      return es_divisa ? 'unidad_divisa_anual' : 'anual';
    } else {
      return es_divisa ? 'unidad_divisa_mes' : 'unidad_mes';
    }
  }
}

async function cargarPromptConfigurado() {
  const unit = document.getElementById('ai-unit') ? document.getElementById('ai-unit').value : '';
  const month = document.getElementById('ai-month') ? document.getElementById('ai-month').value : '';
  const tipo = aiTipoActual;

  const tipo_prompt = getTipoPromptActual();

  try {
    let r = await fetch(`/api/briefing-prompt?tipo=${tipo_prompt}`);
    if (!r.ok) {
      // Bug real corregido: si no hay fila guardada para este tipo (404 -- el caso
      // normal para cualquier tipo que nunca se guardó manualmente), el editor
      // quedaba con el contenido anterior sin avisar, en vez de mostrar el prompt
      // de fábrica. Cae automáticamente al default, igual que restablecerPromptDefault().
      r = await fetch(`/api/briefing-prompt?tipo=${tipo_prompt}&default=1`);
    }
    if (r.ok) {
      const d = await r.json();
      document.getElementById('ai-prompt-editor').value = d.prompt_text;
    } else {
      console.error('No se pudo cargar ningún prompt (ni guardado ni default) para', tipo_prompt);
    }
  } catch (e) {
    console.error('Error al cargar el prompt:', e);
  }
}

function getSelectedComparativaUnits() {
  return Array.from(document.querySelectorAll('.ai-unit-check:checked')).map(cb => cb.value);
}

async function downloadAiBriefing() {
  const year  = document.getElementById('ai-year').value;
  const month = document.getElementById('ai-month').value;
  const tipo  = aiTipoActual;
  const prompt_text = document.getElementById('ai-prompt-editor').value;

  let unit = '';
  let units = [];

  if (tipo === 'comparativa' || tipo === 'comparativa_divisa') {
    units = getSelectedComparativaUnits();
    if (units.length < 2) {
      alert('Selecciona al menos 2 unidades para comparar.');
      return;
    }
  } else {
    unit = document.getElementById('ai-unit').value;
  }

  let empresa_id_raw = document.getElementById('ai-empresa') ? document.getElementById('ai-empresa').value : '';
  if (unit.startsWith('EMPRESA:')) {
    empresa_id_raw = unit.split(':')[1];
    unit = '';
  }
  const empresa_id = empresa_id_raw === '1' ? null : (empresa_id_raw ? parseInt(empresa_id_raw) : null);
  const quarter_raw = document.getElementById('ai-quarter') ? document.getElementById('ai-quarter').value : '';
  const quarter = quarter_raw ? parseInt(quarter_raw) : null;

  try {
    const r = await fetch('/api/export/ai', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ year, month, unit, units, tipo, prompt_text, empresa_id, quarter })
    });
    if (!r.ok) { alert('Error al generar el briefing. Verifica los datos seleccionados.'); return; }
    const blob = await r.blob();
    const a = document.createElement('a');
    const cd = r.headers.get('Content-Disposition') || '';
    const match = cd.match(/filename="?([^"]+)"?/);
    a.href = URL.createObjectURL(blob);
    a.download = match ? match[1] : 'ultrax_briefing.md';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(a.href);
  } catch (e) {
    alert('Error de conexion al generar el briefing.');
  }
}

async function guardarPromptDefault() {
  const unit = document.getElementById('ai-unit') ? document.getElementById('ai-unit').value : '';
  const month = document.getElementById('ai-month') ? document.getElementById('ai-month').value : '';
  const tipo = aiTipoActual;

  const tipo_prompt = getTipoPromptActual();

  const prompt_text = document.getElementById('ai-prompt-editor').value;

  try {
    const r = await fetch('/api/briefing-prompt', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ tipo_reporte: tipo_prompt, prompt_text: prompt_text })
    });
    if (r.ok) {
      const savedDiv = document.getElementById('ai-last-saved');
      if (savedDiv) {
        const now = new Date();
        savedDiv.textContent = 'Guardado: ' + now.toLocaleTimeString();
      }
      alert('✅ Prompt guardado como predeterminado para este tipo de reporte.');
    } else {
      alert('⚠️ Error al guardar el prompt.');
    }
  } catch (e) {
    alert('⚠️ Error de conexión al guardar.');
  }
}

async function restablecerPromptDefault() {
  if (!confirm('¿Restablecer este prompt a los valores de fábrica de UltraBikeX?')) return;

  const unit = document.getElementById('ai-unit') ? document.getElementById('ai-unit').value : '';
  const month = document.getElementById('ai-month') ? document.getElementById('ai-month').value : '';
  const tipo = aiTipoActual;

  const tipo_prompt = getTipoPromptActual();

  try {
    const r = await fetch(`/api/briefing-prompt?tipo=${tipo_prompt}&default=1`);
    if (r.ok) {
      const d = await r.json();
      document.getElementById('ai-prompt-editor').value = d.prompt_text;
      const savedDiv = document.getElementById('ai-last-saved');
      if (savedDiv) savedDiv.textContent = 'Restablecido (sin guardar)';
    } else {
      alert('⚠️ Error al restablecer el prompt.');
    }
  } catch (e) {
    alert('⚠️ Error de conexión al restablecer.');
  }
}
