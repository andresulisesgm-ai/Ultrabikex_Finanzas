// ── DASHBOARD BUILDER CONFIG & LOGIC ──
const DEFAULT_DASHBOARD_CONFIG = [
  {
    "id": "kc-ingr",
    "type": "kpi",
    "title": "Ingresos Totales",
    "subtitle": "Acumulado año",
    "tooltip": "Ingresos operativos acumulados en el año. No incluye ingresos no operativos (alquileres, intereses, ganancia cambiaria, etc.)",
    "icon": "💰",
    "colorClass": "cb",
    "visible": true,
    "order": 1,
    "widthSpan": 1,
    "dataset": "ingresos"
  },
  {
    "id": "kc-ub",
    "type": "kpi",
    "title": "Utilidad Bruta",
    "subtitle": "",
    "tooltip": "Ingresos Totales menos Costo de Ventas.",
    "icon": "📈",
    "colorClass": "cg",
    "visible": true,
    "order": 2,
    "widthSpan": 1,
    "dataset": "utilidad_bruta"
  },
  {
    "id": "kc-un",
    "type": "kpi",
    "title": "Utilidad Neta",
    "subtitle": "",
    "tooltip": "Resultado final después de todos los gastos operativos y no operativos.",
    "icon": "🏆",
    "colorClass": "ca",
    "visible": true,
    "order": 3,
    "widthSpan": 1,
    "dataset": "utilidad_neta"
  },
  {
    "id": "kc-ebt",
    "type": "kpi",
    "title": "EBITDA",
    "subtitle": "Acumulado año",
    "tooltip": "Utilidad antes de intereses, impuestos, depreciación y amortización.",
    "icon": "⭐",
    "colorClass": "ca",
    "visible": true,
    "order": 5,
    "widthSpan": 1,
    "dataset": "ebitda"
  },
  {
    "id": "kc-act",
    "type": "kpi",
    "title": "Total Activos",
    "subtitle": "Consolidado · último trimestre",
    "tooltip": "Todo lo que posee la empresa. Consolidado, al cierre del último trimestre cargado. No se suma entre trimestres -- es una foto a un momento dado.",
    "icon": "🏦",
    "colorClass": "cb",
    "visible": true,
    "order": 6,
    "widthSpan": 1,
    "dataset": "total_activos"
  },
  {
    "id": "kc-pas",
    "type": "kpi",
    "title": "Total Pasivos",
    "subtitle": "Consolidado · último trimestre",
    "tooltip": "Deudas y obligaciones totales de la empresa. Consolidado, al cierre del último trimestre cargado.",
    "icon": "📋",
    "colorClass": "cr",
    "visible": true,
    "order": 7,
    "widthSpan": 1,
    "dataset": "total_pasivos"
  },
  {
    "id": "kc-pat",
    "type": "kpi",
    "title": "Patrimonio",
    "subtitle": "Consolidado · último trimestre",
    "tooltip": "Lo que le pertenece a los socios: Activos menos Pasivos.",
    "icon": "💎",
    "colorClass": "cg",
    "visible": true,
    "order": 8,
    "widthSpan": 1,
    "dataset": "patrimonio"
  },

  {
    "id": "sec-esf",
    "type": "section",
    "title": "🏦 Situación Financiera",
    "visible": true,
    "order": 9.5
  },
  {
    "id": "wc-estcap",
    "type": "chart",
    "title": "Estructura de Capital",
    "subtitle": "Activo vs Pasivo + Patrimonio",
    "visible": true,
    "order": 10,
    "size": "m",
    "widthSpan": 2,
    "chartType": "bar",
    "dataset": "estructura_capital"
  },
  {
    "id": "wc-estcapdet",
    "type": "chart",
    "title": "Estructura de Capital Detallada",
    "subtitle": "Activo y Pasivo por partida",
    "visible": true,
    "order": 11,
    "size": "m",
    "chartType": "bar",
    "dataset": "estructura_capital_detallada"
  },
  {
    "id": "wc-sitfin",
    "type": "chart",
    "title": "Situación Financiera Corriente",
    "subtitle": "Activo vs Pasivo, corriente y no corriente",
    "visible": true,
    "order": 12.2,
    "size": "m",
    "chartType": "bar",
    "dataset": "situacion_financiera"
  },
  {
    "id": "wc-periodo-cobro",
    "type": "chart",
    "title": "Período de Cobro en días",
    "subtitle": "Clientes Externo vs Empresas del Grupo, por trimestre",
    "visible": true,
    "order": 12.25,
    "size": "m",
    "chartType": "bar",
    "dataset": "periodo_cobro"
  },
  {
    "id": "wc-deuda-cobertura",
    "type": "chart",
    "title": "Deuda y Cobertura",
    "subtitle": "Total Pasivo vs Efectivo y Equivalentes",
    "visible": true,
    "order": 12,
    "size": "m",
    "chartType": "bar",
    "dataset": "deuda_cobertura"
  },
  {
    "id": "wc-roe",
    "type": "chart",
    "title": "ROE Acumulado",
    "subtitle": "Utilidad Neta acumulada / Patrimonio promedio",
    "visible": true,
    "order": 12.3,
    "size": "s",
    "chartType": "gauge",
    "dataset": "roe"
  },
  {
    "id": "wc-roa",
    "type": "chart",
    "title": "ROA Acumulado",
    "subtitle": "Ingresos acumulados / Activos promedio",
    "visible": true,
    "order": 12.4,
    "size": "s",
    "chartType": "gauge",
    "dataset": "roa"
  },
  {
    "id": "sec-eerr",
    "type": "section",
    "title": "📊 Estado de Resultados",
    "visible": true,
    "order": 12.5
  },
  {
    "id": "wc-margen",
    "type": "chart",
    "title": "Resultados y margen bruto",
    "subtitle": "Por trimestre · Respeta el filtro de unidad de negocio",
    "visible": true,
    "order": 13,
    "size": "m",
    "chartType": "bar",
    "dataset": "ingresos_costos_margen"
  },
  {
    "id": "wc-cascada",
    "type": "chart",
    "title": "Ingresos y utilidad",
    "subtitle": "De Ingresos a Utilidad Neta, paso a paso · Respeta el filtro de unidad de negocio",
    "visible": true,
    "order": 14,
    "size": "m",
    "chartType": "bar",
    "dataset": "cascada_pl"
  },
  {
    "id": "wc-heatmap-un",
    "type": "chart",
    "title": "Utilidad Neta por Unidad de Negocio",
    "subtitle": "Mapa de calor · Solo disponible al seleccionar una empresa con unidades propias",
    "visible": true,
    "order": 15,
    "size": "m",
    "chartType": "bar",
    "dataset": "heatmap_utilidad_unidad"
  },
  {
    "id": "wc-dona-unidad",
    "type": "chart",
    "title": "Ingresos por Unidad de Negocio",
    "subtitle": "% de participación · Solo disponible al seleccionar una empresa con unidades propias",
    "visible": true,
    "order": 16,
    "size": "s",
    "chartType": "doughnut",
    "dataset": "ingresos_por_unidad"
  },
  {
    "id": "wc-dona-segmento",
    "type": "chart",
    "title": "Ingresos por línea de negocio",
    "subtitle": "Venta de Mercancía · Servicios · Eventos · Taller",
    "visible": true,
    "order": 17,
    "size": "s",
    "chartType": "doughnut",
    "dataset": "ingresos_segmentos"
  }
];

const WIDGET_TEMPLATES = {
  'wc-pe': `
    <div class="ch"><div><div class="ct">⚖️ Punto de Equilibrio</div><div class="cs">Solo disponible por unidad</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-pe">✕</button></div></div>
    <div id="pe-card"></div>
  `,
  'wc-estcap': `
    <div class="ch"><div><div class="ct">Estructura de Capital</div><div class="cs">Activo vs Pasivo + Patrimonio <span id="estcap-badge" style="display:none;color:var(--red);font-weight:700">⚠ Descuadre</span></div></div>
      <div class="cact"><span class="dh">⠿</span>
        <select class="csel vsel" id="ct-ch-estcap" onchange="loadEstructuraCapital()" title="Vista"><option value="monto">Monto</option><option value="pct">100% Apilado</option></select>
        <button class="bcl" data-w="wc-estcap">✕</button></div></div>
    <div class="cv" style="height:230px"><canvas id="ch-estcap"></canvas></div>
    <div id="estcap-legend" style="padding:8px 4px 0"></div>
  `,
  'wc-estcapdet': `
    <div class="ch"><div><div class="ct">Estructura de Capital Detallada</div><div class="cs">Activo vs Pasivo + Patrimonio, por partida</div></div>
      <div class="cact"><span class="dh">⠿</span>
        <select class="csel vsel" id="ct-ch-estcapdet" onchange="loadEstructuraCapitalDetallada()" title="Vista"><option value="monto">Monto</option><option value="pct">100% Apilado</option></select>
        <button class="bcl" data-w="wc-estcapdet">✕</button></div></div>
    <div class="cv" style="height:230px"><canvas id="ch-estcapdet"></canvas></div>
    <div id="estcapdet-legend" style="padding:8px 16px 0"></div>
  `,
  'wc-sitfin': `
    <div class="ch"><div><div class="ct">Situación Financiera Corriente</div><div class="cs">Activo vs Pasivo, corriente y no corriente</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-sitfin">✕</button></div></div>
    <div class="cv" style="height:230px"><canvas id="ch-sitfin"></canvas></div>
    <div id="sitfin-legend" style="padding:8px 4px 0"></div>
  `,
  'wc-periodo-cobro': `
    <div class="ch"><div><div class="ct">Período de Cobro en días</div><div class="cs">Clientes Externo vs Empresas del Grupo</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-periodo-cobro">✕</button></div></div>
    <div class="cv" style="height:230px"><canvas id="ch-periodo-cobro"></canvas></div>
    <div id="periodo-cobro-legend" style="padding:8px 4px 0"></div>
  `,
  'wc-deuda-cobertura': `
    <div class="ch"><div><div class="ct">Deuda y Cobertura</div><div class="cs">Total Pasivo vs Efectivo y Equivalentes</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-deuda-cobertura">✕</button></div></div>
    <div class="cv" style="height:230px"><canvas id="ch-deuda-cobertura"></canvas></div>
    <div id="deuda-cobertura-legend" style="padding:8px 16px 0"></div>
  `,
  'wc-roe': `
    <div class="ch"><div><div class="ct">ROE Acumulado</div><div class="cs">Utilidad Neta acumulada / Patrimonio promedio</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-roe">✕</button></div></div>
    <div style="position:relative;height:110px"><canvas id="ch-roe-gauge"></canvas>
      <div style="position:absolute;top:55%;left:50%;transform:translate(-50%,-50%);text-align:center">
        <div style="font-size:11px;color:var(--mu2)">ROE</div>
        <div style="font-size:22px;font-weight:700" id="roe-gauge-num">—</div>
      </div>
    </div>
    <div class="cv" style="height:130px"><canvas id="ch-roe-bar"></canvas></div>
    <div id="roe-legend" style="padding:8px 16px 0"></div>
  `,
  'wc-roa': `
    <div class="ch"><div><div class="ct">ROA Acumulado</div><div class="cs">Utilidad Neta acumulada / Activos promedio</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-roa">✕</button></div></div>
    <div style="position:relative;height:110px"><canvas id="ch-roa-gauge"></canvas>
      <div style="position:absolute;top:55%;left:50%;transform:translate(-50%,-50%);text-align:center">
        <div style="font-size:11px;color:var(--mu2)">ROA</div>
        <div style="font-size:22px;font-weight:700" id="roa-gauge-num">—</div>
      </div>
    </div>
    <div class="cv" style="height:130px"><canvas id="ch-roa-bar"></canvas></div>
    <div id="roa-legend" style="padding:8px 16px 0"></div>
  `,
  'wc-margen': `
    <div class="ch"><div><div class="ct">Resultados y margen bruto</div><div class="cs">Respeta el filtro de unidad de negocio</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-margen">✕</button></div></div>
    <div class="cv" style="height:230px"><canvas id="ch-margen"></canvas></div>
    <div id="margen-legend" style="padding:8px 16px 0"></div>
  `,
  'wc-cascada': `
    <div class="ch"><div><div class="ct">Ingresos y utilidad</div><div class="cs">De Ingresos a Utilidad Neta, paso a paso · Respeta el filtro de unidad de negocio</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-cascada">✕</button></div></div>
    <div class="cv" style="height:230px"><canvas id="ch-cascada"></canvas></div>
    <div id="cascada-legend" style="padding:8px 16px 0"></div>
  `,
  'wc-heatmap-un': `
    <div class="ch"><div><div class="ct" id="heatmap-un-titulo">Utilidad Neta por Unidad de Negocio</div><div class="cs">Por unidad si hay una empresa seleccionada, por empresa en vista Holding</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-heatmap-un">✕</button></div></div>
    <div class="cv" style="height:230px"><canvas id="ch-heatmap-un"></canvas></div>
    <div id="heatmap-un-empty" style="display:none;text-align:center;color:var(--mu);font-size:12px;padding:24px 8px"></div>
    <div id="heatmap-un-legend" style="padding:8px 16px 0"></div>
  `,
  'wc-dona-unidad': `
    <div class="ch"><div><div class="ct">Ingresos por Unidad de Negocio</div><div class="cs">% de participación · Solo disponible al seleccionar una empresa con unidades propias</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-dona-unidad">✕</button></div></div>
    <div class="cv" style="height:230px;position:relative">
      <canvas id="ch-dona-unidad"></canvas>
      <div id="ch-dona-unidad-empty" style="display:none;text-align:center;color:var(--mu);font-size:12px;padding:24px 8px">Seleccioná una empresa con unidades de negocio propias para ver este gráfico.</div>
    </div>
    <div id="dona-unidad-legend" style="padding:8px 16px 0"></div>
  `,
  'wc-dona-segmento': `
    <div class="ch"><div><div class="ct">Ingresos por línea de negocio</div><div class="cs">Venta de Mercancía · Servicios · Eventos · Taller</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-dona-segmento">✕</button></div></div>
    <div class="cv" style="height:230px"><canvas id="ch-dona-segmento"></canvas></div>
    <div id="dona-segmento-legend" style="padding:8px 16px 0"></div>
  `,
  'wc-gau': `
    <div class="ch"><div><div class="ct">⏱ Indicadores Gauge</div><div class="cs">Margen Neto · Cobertura PE · Eficiencia Operativa</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-gau">✕</button></div></div>
    <div id="grow" style="display:flex;gap:16px;align-items:center;justify-content:center;flex-wrap:wrap">
      <div id="gauge-mn" style="width:200px;height:160px"></div>
      <div id="gauge-pe" style="width:200px;height:160px"></div>
      <div id="gauge-ef" style="width:200px;height:160px"></div>
    </div>
  `,
  'wc-rank': `
    <div class="ch"><div><div class="ct">🏅 Ranking de Rentabilidad</div><div class="cs">Ordenado por margen neto</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-rank">✕</button></div></div>
    <div id="rankbody"></div>
  `,
  'wc-main': `
    <div class="ch"><div><div class="ct">Ingresos · Costos · Gastos</div><div class="cs">Evolución mensual · clic para ver detalle</div></div>
      <div class="cact"><span class="dh">⠿</span>
        <select class="csel" id="mtype" onchange="rebuildMain()"><option value="bar">Barras</option><option value="line">Líneas</option><option value="combo">Combo</option></select>
        <button class="bcl" data-w="wc-main">✕</button></div></div>
    <div class="cv h240"><canvas id="ch-main"></canvas></div>
  `,
  'wc-tm': `
    <div class="ch"><div><div class="ct" id="tm-title">Participación por Unidad</div><div class="cs">Ingresos proporcionales</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-tm">✕</button></div></div>
    <div class="tmw" id="tmcon"></div>
  `,
  'wc-rad': `
    <div class="ch"><div><div class="ct" id="rad-title">Comparativo Multidimensional</div><div class="cs" id="rad-sub">Por unidad de negocio</div></div>
      <div class="cact"><span class="dh">⠿</span><select class="csel ctsel" id="ct-ch-rad" onchange="setChartType('ch-rad',this.value)" title="Tipo de gráfico"><option value="radar">Radar</option><option value="line">Líneas</option><option value="bar">Barras</option></select><button class="bcl" data-w="wc-rad">✕</button></div></div>
    <div class="cv h200"><canvas id="ch-rad"></canvas></div>
  `,
  'wc-mg': `
    <div class="ch"><div><div class="ct">Márgenes %</div><div class="cs">Bruto y neto mensual · clic para ver detalle</div></div>
      <div class="cact"><span class="dh">⠿</span><select class="csel ctsel" id="ct-ch-mg" onchange="setChartType('ch-mg',this.value)" title="Tipo de gráfico"><option value="line">Líneas</option><option value="bar">Barras</option></select><button class="bcl" data-w="wc-mg">✕</button></div></div>
    <div class="cv h200"><canvas id="ch-mg"></canvas></div>
  `,
  'wc-un': `
    <div class="ch"><div><div class="ct">Utilidad Neta Mensual</div><div class="cs">+/− por mes · clic para ver detalle</div></div>
      <div class="cact"><span class="dh">⠿</span><select class="csel ctsel" id="ct-ch-un" onchange="setChartType('ch-un',this.value)" title="Tipo de gráfico"><option value="bar">Barras</option><option value="line">Líneas</option></select><button class="bcl" data-w="wc-un">✕</button></div></div>
    <div class="cv h200"><canvas id="ch-un"></canvas></div>
  `,
  'wc-est': `
    <div class="ch"><div><div class="ct">Estructura de Gastos</div><div class="cs">Por categoría · clic para ver detalle</div></div>
      <div class="cact"><span class="dh">⠿</span><select class="csel ctsel" id="ct-ch-est" onchange="setChartType('ch-est',this.value)" title="Tipo de gráfico"><option value="doughnut">Dona</option><option value="pie">Pastel</option><option value="bar">Barras</option></select><button class="bcl" data-w="wc-est">✕</button></div></div>
    <div class="cv h200"><canvas id="ch-est"></canvas></div>
  `,
  'wc-tg': `
    <div class="ch"><div><div class="ct">Top 10 Gastos</div><div class="cs">Mayor impacto · clic para ver detalle</div></div>
      <div class="cact"><span class="dh">⠿</span><select class="csel ctsel" id="ct-ch-tg" onchange="setChartType('ch-tg',this.value)" title="Tipo de gráfico"><option value="bar">Barras</option><option value="line">Líneas</option></select><button class="bcl" data-w="wc-tg">✕</button></div></div>
    <div class="cv h280"><canvas id="ch-tg"></canvas></div>
  `,
  'wc-wf': `
    <div class="ch"><div><div class="ct">Cascada P&amp;L</div><div class="cs">De ingresos a utilidad neta</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-wf">✕</button></div></div>
    <div class="wf" id="wf"></div>
  `,
  'wc-tbl': `
    <div class="ch"><div><div class="ct">Resumen Mensual</div><div class="cs">Detalle por período</div></div>
      <div class="cact"><span class="dh">⠿</span>
        <select class="csel" id="tblmode" onchange="rTable()"><option value="$">Montos</option><option value="%">%</option></select>
        <button class="bcl" data-w="wc-tbl">✕</button></div></div>
    <div class="tw"><table><thead><tr><th>Mes</th><th>Ingresos</th><th>Costos</th><th>Util.Bruta</th><th>Gastos</th><th>Util.Neta</th><th>Mg.Bruto</th><th>Mg.Neto</th><th>%Costo</th><th>%Gasto</th></tr></thead><tbody id="tbody"></tbody></table></div>
  `,
  'wc-esf-kpi-activos': `
    <div class="ch"><div><div class="ct">🏦 Total Activos</div><div class="cs">Último quarter</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-esf-kpi-activos">✕</button></div></div>
    <div class="esf-kpi-val" id="esf-kpi-activos-val" style="font-size:28px;font-weight:700;color:var(--blue);padding:16px 0 4px">—</div>
    <div class="esf-kpi-lbl" style="font-size:11px;color:var(--mu2)">Activos Corrientes: <span id="esf-kpi-activos-ac">—</span> · No Corrientes: <span id="esf-kpi-activos-anc">—</span></div>
  `,
  'wc-esf-kpi-pasivos': `
    <div class="ch"><div><div class="ct">📋 Total Pasivos</div><div class="cs">Último quarter</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-esf-kpi-pasivos">✕</button></div></div>
    <div class="esf-kpi-val" id="esf-kpi-pasivos-val" style="font-size:28px;font-weight:700;color:var(--red);padding:16px 0 4px">—</div>
    <div class="esf-kpi-lbl" style="font-size:11px;color:var(--mu2)">Corrientes: <span id="esf-kpi-pasivos-pc">—</span> · No Corrientes: <span id="esf-kpi-pasivos-pnc">—</span></div>
  `,
  'wc-esf-kpi-patrimonio': `
    <div class="ch"><div><div class="ct">💎 Patrimonio</div><div class="cs">Último quarter</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-esf-kpi-patrimonio">✕</button></div></div>
    <div class="esf-kpi-val" id="esf-kpi-patrimonio-val" style="font-size:28px;font-weight:700;color:var(--green);padding:16px 0 4px">—</div>
    <div class="esf-kpi-lbl" style="font-size:11px;color:var(--mu2)">Pasivos + Patrimonio deben igualar Activos</div>
  `,
  'wc-esf-kpi-efectivo': `
    <div class="ch"><div><div class="ct">💵 Efectivo y Equivalentes</div><div class="cs">Último quarter</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-esf-kpi-efectivo">✕</button></div></div>
    <div class="esf-kpi-val" id="esf-kpi-efectivo-val" style="font-size:28px;font-weight:700;color:var(--blue);padding:16px 0 4px">—</div>
    <div class="esf-kpi-lbl" style="font-size:11px;color:var(--mu2)">% sobre Activos Corrientes: <span id="esf-kpi-efectivo-pct">—</span></div>
  `,
  'wc-esf-kpi-cxc': `
    <div class="ch"><div><div class="ct">📥 Cuentas por Cobrar</div><div class="cs">Último quarter</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-esf-kpi-cxc">✕</button></div></div>
    <div class="esf-kpi-val" id="esf-kpi-cxc-val" style="font-size:28px;font-weight:700;color:var(--amber);padding:16px 0 4px">—</div>
    <div class="esf-kpi-lbl" style="font-size:11px;color:var(--mu2)">% sobre Activos Corrientes: <span id="esf-kpi-cxc-pct">—</span></div>
  `,
  'wc-esf-kpi-inv': `
    <div class="ch"><div><div class="ct">📦 Inventarios</div><div class="cs">Último quarter</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-esf-kpi-inv">✕</button></div></div>
    <div class="esf-kpi-val" id="esf-kpi-inv-val" style="font-size:28px;font-weight:700;color:var(--purple);padding:16px 0 4px">—</div>
    <div class="esf-kpi-lbl" style="font-size:11px;color:var(--mu2)">% sobre Activos Corrientes: <span id="esf-kpi-inv-pct">—</span></div>
  `,
  'wc-esf-estructura': `
    <div class="ch"><div><div class="ct">🏗 Estructura Financiera</div><div class="cs">Activos · Pasivos · Patrimonio</div></div>
      <div class="cact"><span class="dh">⠿</span>
        <select class="csel ctsel" id="ct-ch-esf-est" onchange="setChartType('ch-esf-est',this.value)" title="Tipo de gráfico">
          <option value="doughnut">Dona</option>
          <option value="pie">Pastel</option>
          <option value="bar">Barras</option>
          <option value="polarArea">Área Polar</option>
        </select>
        <button class="bcl" data-w="wc-esf-estructura">✕</button></div></div>
    <div class="cv"><canvas id="ch-esf-est"></canvas></div>
  `,
  'wc-ind-roe': `
    <div class="ch"><div><div class="ct">📊 ROE</div><div class="cs">Retorno sobre Patrimonio</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-ind-roe">✕</button></div></div>
    <div class="esf-kpi-val" id="ind-roe-val" style="font-size:28px;font-weight:700;color:var(--green);padding:16px 0 4px">—</div>
    <div class="esf-kpi-lbl" style="font-size:11px;color:var(--mu2)">Utilidad Neta / Patrimonio × 100</div>
  `,
  'wc-ind-roa': `
    <div class="ch"><div><div class="ct">📊 ROA</div><div class="cs">Retorno sobre Activos</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-ind-roa">✕</button></div></div>
    <div class="esf-kpi-val" id="ind-roa-val" style="font-size:28px;font-weight:700;color:var(--blue);padding:16px 0 4px">—</div>
    <div class="esf-kpi-lbl" style="font-size:11px;color:var(--mu2)">Utilidad Neta / Total Activos × 100</div>
  `,
  'wc-ind-pa': `
    <div class="ch"><div><div class="ct">🧪 Prueba Ácida</div><div class="cs">Liquidez sin inventarios</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-ind-pa">✕</button></div></div>
    <div class="esf-kpi-val" id="ind-pa-val" style="font-size:28px;font-weight:700;color:var(--amber);padding:16px 0 4px">—</div>
    <div class="esf-kpi-lbl" style="font-size:11px;color:var(--mu2)">Ref: &gt;1.0 saludable</div>
  `,
  'wc-ind-pd': `
    <div class="ch"><div><div class="ct">🛡️ Prueba Defensiva</div><div class="cs">Solo efectivo / Pasivo Cte</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-ind-pd">✕</button></div></div>
    <div class="esf-kpi-val" id="ind-pd-val" style="font-size:28px;font-weight:700;color:var(--purple);padding:16px 0 4px">—</div>
    <div class="esf-kpi-lbl" style="font-size:11px;color:var(--mu2)">Ref: &gt;0.5 saludable</div>
  `,
  'wc-ind-end': `
    <div class="ch"><div><div class="ct">📉 Ratio Endeudamiento</div><div class="cs">Pasivos / Patrimonio</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-ind-end">✕</button></div></div>
    <div class="esf-kpi-val" id="ind-end-val" style="font-size:28px;font-weight:700;color:var(--red);padding:16px 0 4px">—</div>
    <div class="esf-kpi-lbl" style="font-size:11px;color:var(--mu2)">Ref: &lt;1.0 conservador · &lt;2.0 moderado</div>
  `,
  'wc-ind-rotinv': `
    <div class="ch"><div><div class="ct">🔄 Rotación Inventarios</div><div class="cs">Meses de cobertura</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-ind-rotinv">✕</button></div></div>
    <div class="esf-kpi-val" id="ind-rotinv-val" style="font-size:28px;font-weight:700;color:var(--blue);padding:16px 0 4px">—</div>
    <div class="esf-kpi-lbl" style="font-size:11px;color:var(--mu2)">Meses que duran los inventarios actuales</div>
  `,
  'wc-ind-rotact': `
    <div class="ch"><div><div class="ct">⚙️ Rotación de Activos</div><div class="cs">Veces por trimestre</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-ind-rotact">✕</button></div></div>
    <div class="esf-kpi-val" id="ind-rotact-val" style="font-size:28px;font-weight:700;color:var(--green);padding:16px 0 4px">—</div>
    <div class="esf-kpi-lbl" style="font-size:11px;color:var(--mu2)">Ingresos generados por cada $ de activo</div>
  `,
  'wc-ind-cobro': `
    <div class="ch"><div><div class="ct">📅 Período de Cobro</div><div class="cs">Días promedio de cobro</div></div>
      <div class="cact"><span class="dh">⠿</span><button class="bcl" data-w="wc-ind-cobro">✕</button></div></div>
    <div class="esf-kpi-val" id="ind-cobro-val" style="font-size:28px;font-weight:700;color:var(--amber);padding:16px 0 4px">—</div>
    <div class="esf-kpi-lbl" style="font-size:11px;color:var(--mu2)">Ref: &lt;30 días óptimo · &lt;60 aceptable</div>
  `,
  'wc-panel-indicadores': `
    <div class="ch"><div><div class="ct">📐 Panel de Indicadores</div><div class="cs">ROE · ROA · Liquidez · Rotación</div></div>
      <div class="cact"><span class="dh">⠿</span>
        <select class="csel ctsel" id="ct-ch-pind" onchange="setChartType('ch-pind',this.value)" title="Tipo de gráfico">
          <option value="bar">Barras</option>
          <option value="radar">Radar</option>
          <option value="polarArea">Área Polar</option>
          <option value="bar-h">Barras Horizontales</option>
          <option value="table">Tabla</option>
        </select>
        <button class="bcl" data-w="wc-panel-indicadores">✕</button></div></div>
    <canvas id="ch-pind" height="220"></canvas>
    <div id="ch-pind-table" style="display:none"></div>
  `,
  'wc-panel-esf': `
    <div class="ch"><div><div class="ct">🏗 Panel Balance ESF</div><div class="cs">Activos · Pasivos · Patrimonio</div></div>
      <div class="cact"><span class="dh">⠿</span>
        <select class="csel ctsel" id="ct-ch-pesf" onchange="setChartType('ch-pesf',this.value)" title="Tipo de gráfico">
          <option value="doughnut">Dona</option>
          <option value="bar">Barras</option>
          <option value="bar-stack">Barras Apiladas</option>
          <option value="polarArea">Área Polar</option>
          <option value="table">Tabla</option>
        </select>
        <button class="bcl" data-w="wc-panel-esf">✕</button></div></div>
    <div class="cv"><canvas id="ch-pesf"></canvas></div>
    <div id="ch-pesf-table" style="display:none"></div>
  `,
};

window.DASHBOARD_CONFIG = [];
window.DASHBOARD_EDIT_MODE = false;
let ORIGINAL_CONFIG_BACKUP = null;

async function initDashboardConfig() {
  try {
    const res = await fetch('/api/dashboard/config');
    if (!res.ok) throw new Error('Error al cargar config');
    window.DASHBOARD_CONFIG = await res.json();
    
    // Aplicar localStorage overrides para modo normal (retrocompatibilidad)
    const localHidden = LS.get('hidden', null);
    const localKPI = LS.get('kpi', null);
    const localOrder = LS.get('worder', null);

    if (localHidden) {
      window.DASHBOARD_CONFIG.forEach(w => {
        if (localHidden.includes(w.id)) w.visible = false;
      });
    }

    if (localKPI) {
      window.DASHBOARD_CONFIG.forEach(w => {
        if (w.type === 'kpi') {
          const kpiId = w.id.replace('kc-', '');
          w.visible = localKPI.includes(kpiId);
        }
      });
    }

    let validOrder = null;
    if (localOrder) {
      const currentIds = window.DASHBOARD_CONFIG.map(w => w.id);
      const sameSet = currentIds.length === localOrder.length &&
        currentIds.every(id => localOrder.includes(id)) &&
        localOrder.every(id => currentIds.includes(id));
      if (sameSet) {
        validOrder = localOrder;
      } else {
        localStorage.removeItem('worder');
      }
    }

    if (validOrder) {
      window.DASHBOARD_CONFIG.sort((a, b) => {
        return validOrder.indexOf(a.id) - validOrder.indexOf(b.id);
      });
      window.DASHBOARD_CONFIG.forEach((w, idx) => {
        w.order = idx + 1;
      });
    }
  } catch (err) {
    console.error('Failed to load dashboard config:', err);
    window.DASHBOARD_CONFIG = JSON.parse(JSON.stringify(DEFAULT_DASHBOARD_CONFIG));
  }
}

function enterEditMode() {
  window.DASHBOARD_EDIT_MODE = true;
  ORIGINAL_CONFIG_BACKUP = JSON.parse(JSON.stringify(window.DASHBOARD_CONFIG));
  
  G('btn-edit-mode').style.display = 'none';
  G('edit-controls-group').style.display = 'flex';

  renderDashboardWidgets();
  loadDash();
}

function exitEditMode(save = false) {
  window.DASHBOARD_EDIT_MODE = false;
  
  G('btn-edit-mode').style.display = 'inline-block';
  G('edit-controls-group').style.display = 'none';

  if (!save && ORIGINAL_CONFIG_BACKUP) {
    window.DASHBOARD_CONFIG = ORIGINAL_CONFIG_BACKUP;
  }
  
  renderDashboardWidgets();
  loadDash();
}

async function saveDashboardConfig() {
  syncConfigFromDOM();

  try {
    const res = await fetch('/api/dashboard/config', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(window.DASHBOARD_CONFIG)
    });
    if (!res.ok) {
      alert('Error al guardar la configuración');
      return;
    }
    localStorage.removeItem('worder');
    localStorage.removeItem('hidden');
    localStorage.removeItem('kpi');
    
    alert('Configuración guardada exitosamente');
    exitEditMode(true);
  } catch (err) {
    console.error('Error saving config:', err);
    alert('Error de red al guardar la configuración');
  }
}

function syncConfigFromDOM() {
  const wcon = G('wcon');
  const kgrid = document.querySelector('.kgrid');
  
  let currentOrder = 1;

  if (kgrid) {
    [...kgrid.children].forEach(child => {
      const w = window.DASHBOARD_CONFIG.find(item => item.id === child.id);
      if (w) {
        w.order = currentOrder++;
        w.visible = !child.classList.contains('hidden');
      }
    });
  }

  if (wcon) {
    [...wcon.children].forEach(child => {
      const w = window.DASHBOARD_CONFIG.find(item => item.id === child.id);
      if (w) {
        w.order = currentOrder++;
        w.visible = !child.classList.contains('whidden');
        w.doubleWidth = child.classList.contains('ww');
        
        const select = child.querySelector('.ctsel');
        if (select) {
          w.chartType = select.value;
        }
      }
    });
  }
}

const CHART_OPTIONS = {
  'wc-main':         [['bar','Barras'],['line','Líneas'],['area','Área'],['bar-stack','Barras Apiladas'],['area-stack','Área Apilada']],
  'wc-mg':           [['line','Líneas'],['bar','Barras'],['area','Área'],['scatter','Dispersión']],
  'wc-un':           [['bar','Barras'],['line','Líneas'],['area','Área'],['scatter','Dispersión']],
  'wc-rad':          [['radar','Radar'],['line','Líneas'],['bar','Barras'],['polarArea','Área Polar']],
  'wc-est':          [['doughnut','Dona'],['pie','Pastel'],['bar','Barras'],['polarArea','Área Polar']],
  'wc-tg':           [['bar','Barras'],['line','Líneas'],['bar-h','Barras Horizontales'],['doughnut','Dona']],
  'wc-esf-estructura':[['doughnut','Dona'],['pie','Pastel'],['bar','Barras'],['polarArea','Área Polar']],
  'wc-panel-indicadores':[['bar','Barras'],['radar','Radar'],['polarArea','Área Polar'],['bar-h','Barras Horizontales'],['table','Tabla']],
  'wc-panel-esf':[['bar','Barras'],['bar-stack','Barras Apiladas'],['doughnut','Dona'],['polarArea','Área Polar'],['table','Tabla']]
};

function getCategoriesModal() {
  const cats = [
    { key:'eerr',      label:'📊 EERR — Resultados',       tipos:['chart','special','table'] },
    { key:'esf',       label:'🏦 ESF — Balance',            tipos:['esf'] },
    { key:'indicador', label:'📐 Indicadores Financieros',  tipos:['indicador'] },
    { key:'panel',     label:'📈 Panels con Gráfica',       tipos:['panel'] },
  ];
  if (DD && DD._tasas) {
    cats.push({ key:'divisa', label:'💵 Divisa Real',       tipos:['divisa'] });
  }
  return cats;
}

function openAddWidgetModal() {
  const modal = G('add-widget-modal');
  const list  = G('add-widget-list');
  if (!modal || !list) return;

  const hidden = window.DASHBOARD_CONFIG.filter(w => !w.visible);
  list.innerHTML = '';
  modal._step = 1;
  modal._selected = [];

  if (hidden.length === 0) {
    list.innerHTML = `<p style="color:var(--mu2);font-size:12px;text-align:center;padding:10px">Todos los widgets están en uso.</p>`;
    modal.classList.add('show');
    return;
  }

  // PASO 1 — categorías colapsables con checkboxes
  list.innerHTML = '<div id="awm-step1">' + getCategoriesModal().map(cat => {
    const ws = hidden.filter(w => cat.tipos.includes(w.type));
    if (!ws.length) return '';
    return `
      <div style="margin-bottom:6px;border:1px solid var(--bd);border-radius:8px;overflow:hidden">
        <div onclick="this.nextElementSibling.style.display=this.nextElementSibling.style.display==='none'?'flex':'none';this.querySelector('.aw-arr').textContent=this.nextElementSibling.style.display==='none'?'▶':'▼'"
          style="display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:var(--sf2);cursor:pointer;user-select:none">
          <span style="font-size:12px;font-weight:700;color:var(--fg)">${cat.label}</span>
          <span class="aw-arr" style="font-size:10px;color:var(--mu2)">▼</span>
        </div>
        <div style="padding:6px 8px;display:none;flex-direction:column;gap:4px">
          ${ws.map(w => `
            <label style="display:flex;align-items:center;gap:10px;cursor:pointer;padding:6px 4px;border-radius:5px">
              <input type="checkbox" data-widget-id="${w.id}" style="width:14px;height:14px;cursor:pointer;accent-color:var(--blue);flex-shrink:0">
              <div>
                <div style="font-size:11px;font-weight:600;color:var(--fg)">${w.icon||''} ${w.title}</div>
                <div style="font-size:9px;color:var(--mu2)">${w.subtitle||''}</div>
              </div>
            </label>
          `).join('')}
        </div>
      </div>
    `;
  }).join('') + '</div>';

  // Footer paso 1
  G('awm-footer').innerHTML = `
    <button class="btnc" onclick="closeAddWidgetModal()" style="padding:6px 14px">Cancelar</button>
    <button onclick="awmNext()" style="background:var(--blue);color:white;border:none;border-radius:6px;padding:6px 14px;font-size:11px;font-weight:600;cursor:pointer">Siguiente ▶</button>
  `;

  modal.classList.add('show');
}

function awmNext() {
  const modal = G('add-widget-modal');
  const checked = [...document.querySelectorAll('#awm-step1 input[type=checkbox]:checked')];
  if (!checked.length) { closeAddWidgetModal(); return; }

  const selected = checked.map(cb => window.DASHBOARD_CONFIG.find(w => w.id === cb.dataset.widgetId)).filter(Boolean);
  const needsChart = selected.filter(w => CHART_OPTIONS[w.id]);

  if (!needsChart.length) {
    // Ninguno necesita selección de gráfica — agregar directo
    selected.forEach(w => w.visible = true);
    renderDashboardWidgets(); loadDash(); closeAddWidgetModal(); return;
  }

  // PASO 2 — selección de tipo de gráfica
  const list = G('add-widget-list');
  list.innerHTML = `
    <div style="font-size:11px;color:var(--mu2);margin-bottom:8px">Elige el tipo de gráfica para cada widget:</div>
    ${needsChart.map(w => `
      <div style="padding:8px;background:var(--sf2);border:1px solid var(--bd);border-radius:6px;margin-bottom:4px">
        <div style="font-size:11px;font-weight:600;color:var(--fg);margin-bottom:6px">${w.icon||''} ${w.title}</div>
        <div style="display:flex;flex-wrap:wrap;gap:6px">
          ${CHART_OPTIONS[w.id].map(([val, lbl], i) => `
            <label style="display:flex;align-items:center;gap:4px;cursor:pointer;font-size:10px;color:var(--fg)">
              <input type="radio" name="ct-${w.id}" value="${val}" ${i===0?'checked':''} style="accent-color:var(--blue)">
              ${lbl}
            </label>
          `).join('')}
        </div>
      </div>
    `).join('')}
    ${selected.filter(w => !CHART_OPTIONS[w.id]).map(w => `
      <div style="padding:6px 8px;font-size:10px;color:var(--mu2);border-left:3px solid var(--bd);margin-bottom:4px">
        ✓ ${w.title} — sin selección de gráfica
      </div>
    `).join('')}
  `;

  // Guardar selección para el paso final
  modal._pending = { selected, needsChart };

  G('awm-footer').innerHTML = `
    <button class="btnc" onclick="openAddWidgetModal()" style="padding:6px 14px">◀ Volver</button>
    <button onclick="awmConfirm()" style="background:var(--green);color:white;border:none;border-radius:6px;padding:6px 14px;font-size:11px;font-weight:600;cursor:pointer">✓ Agregar</button>
  `;
}

function awmConfirm() {
  const modal = G('add-widget-modal');
  const { selected, needsChart } = modal._pending;

  needsChart.forEach(w => {
    const radio = document.querySelector(`input[name="ct-${w.id}"]:checked`);
    if (radio) w.chartType = radio.value;
  });

  selected.forEach(w => w.visible = true);
  renderDashboardWidgets();
  closeAddWidgetModal();
  setTimeout(() => loadDash(), 150);
}

function closeAddWidgetModal() {
  const modal = G('add-widget-modal');
  if (modal) modal.classList.remove('show');
}

function addWidget(id) {
  const w = window.DASHBOARD_CONFIG.find(item => item.id === id);
  if (w) {
    w.visible = true;
    renderDashboardWidgets();
    loadDash();
  }
  closeAddWidgetModal();
}

function removeWidget(id) {
  const w = window.DASHBOARD_CONFIG.find(item => item.id === id);
  if (w) {
    w.visible = false;
    renderDashboardWidgets();
    loadDash();
  }
}

function setWidgetSize(id, size) {
  const w = window.DASHBOARD_CONFIG.find(item => item.id === id);
  if (w) {
    w.size = size;
    w.doubleWidth = size === 'xl' || size === 'l';
    renderDashboardWidgets();
    loadDash();
    setTimeout(() => resizeWidgetCharts(id), 150);
  }
}

function resizeWidgetCharts(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.querySelectorAll('canvas').forEach(canvas => {
    const chart = Chart.getChart(canvas);
    if (chart) chart.resize();
  });
  ['gauge-mn','gauge-pe','gauge-ef'].forEach(gid => {
    const dom = el.querySelector('#' + gid);
    if (dom && dom._echart) dom._echart.resize();
  });
  const tmcon = el.querySelector('#tmcon');
  if (tmcon && window._lastTMItems) renderTM(window._lastTMItems, tmcon);
}

function renderDashboardWidgets() {
  const wcon = G('wcon');
  if (!wcon) return;
  wcon.innerHTML = '';

  const sortedWidgets = window.DASHBOARD_CONFIG
    .filter(w => w.type !== 'kpi')
    .sort((a, b) => a.order - b.order);

  sortedWidgets.forEach(w => {
    if (w.type === 'section') {
      const sec = document.createElement('div');
      sec.className = 'wsection';
      sec.id = w.id;
      sec.textContent = w.title;
      wcon.appendChild(sec);
      return;
    }

    let isVisible = w.visible;
    const localHidden = LS.get('hidden', []);
    if (localHidden.includes(w.id)) {
      isVisible = false;
    }

    const sizeClass = { s: 'ws', m: 'wm', l: 'wl', xl: 'wxl' }[w.size || 'm'] || 'wm';
    const wcard = document.createElement('div');
    wcard.className = `wcard ${sizeClass} ${isVisible ? '' : 'whidden'}`;
    wcard.id = w.id;
    if (window.DASHBOARD_EDIT_MODE) {
      wcard.setAttribute('draggable', 'true');
    }
    
    let extraControls = '';
    if (window.DASHBOARD_EDIT_MODE) {
      wcard.classList.remove('whidden');
      wcard.style.border = '2px dashed var(--blue)';
      extraControls = `
  <div class="edit-card-overlay" style="position:absolute;top:0;right:0;background:rgba(37,99,235,0.08);padding:4px;border-bottom-left-radius:8px;display:flex;gap:4px;z-index:10;align-items:center;">
    <span style="font-size:9px;color:var(--blue);font-weight:600;margin-right:2px">Tamaño:</span>
    <button onclick="setWidgetSize('${w.id}','s')" style="font-size:9px;padding:1px 5px;border-radius:3px;border:1px solid var(--blue);background:${(w.size||'m')==='s'?'var(--blue)':'white'};color:${(w.size||'m')==='s'?'white':'var(--blue)'};cursor:pointer">S</button>
    <button onclick="setWidgetSize('${w.id}','m')" style="font-size:9px;padding:1px 5px;border-radius:3px;border:1px solid var(--blue);background:${(w.size||'m')==='m'?'var(--blue)':'white'};color:${(w.size||'m')==='m'?'white':'var(--blue)'};cursor:pointer">M</button>
    <button onclick="setWidgetSize('${w.id}','l')" style="font-size:9px;padding:1px 5px;border-radius:3px;border:1px solid var(--blue);background:${(w.size||'m')==='l'?'var(--blue)':'white'};color:${(w.size||'m')==='l'?'white':'var(--blue)'};cursor:pointer">L</button>
    <button onclick="setWidgetSize('${w.id}','xl')" style="font-size:9px;padding:1px 5px;border-radius:3px;border:1px solid var(--blue);background:${(w.size||'m')==='xl'?'var(--blue)':'white'};color:${(w.size||'m')==='xl'?'white':'var(--blue)'};cursor:pointer">XL</button>
    <button onclick="removeWidget('${w.id}')" style="background:var(--red);color:white;border:none;border-radius:4px;padding:2px 6px;font-size:10px;cursor:pointer;font-weight:bold;margin-left:4px">✕</button>
  </div>
`;
      wcard.style.position = 'relative';
    }

    const content = WIDGET_TEMPLATES[w.id] || '';
    wcard.innerHTML = content + extraControls;
    wcon.appendChild(wcard);
  });

  renderKPIs();
  initClose();
  initDrag();
  layoutMasonry();
  updateVisibilidadSeccionESF();
}

// Oculta la sección ESF completa (encabezado + 6 widgets: Estructura de Capital,
// Estructura de Capital Detallada, Situación Financiera Corriente, Deuda y
// Cobertura, ROE, ROA) cuando el usuario filtra por Unidad de Negocio específica
// o por Mes puntual -- en ese contexto ESF es ruido, ya que ESF es siempre
// consolidado y no aplica a unidad ni a mes puntual (solo a trimestre). Con
// Trimestre seleccionado, ESF sigue visible normalmente.
function updateVisibilidadSeccionESF() {
  const unit = G('dash-unit') ? G('dash-unit').value : 'TODAS';
  const mes = G('dash-month') ? G('dash-month').value : '';
  const debeOcultarse = (unit !== 'TODAS') || (mes !== '');

  const idsESF = ['sec-esf', 'wc-estcap', 'wc-estcapdet', 'wc-sitfin', 'wc-periodo-cobro', 'wc-deuda-cobertura', 'wc-roe', 'wc-roa', 'kc-act', 'kc-pas', 'kc-pat'];
  idsESF.forEach(id => {
    const el = G(id);
    if (el) el.style.display = debeOcultarse ? 'none' : '';
  });
  layoutMasonry();
}

function renderKPIs() {
  const kgrid = document.querySelector('.kgrid');
  if (!kgrid) return;
  kgrid.innerHTML = '';

  const kpis = window.DASHBOARD_CONFIG
    .filter(w => w.type === 'kpi')
    .sort((a, b) => a.order - b.order);

  kpis.forEach(w => {
    let isVisible = w.visible;
    const localKPI = LS.get('kpi', null);
    if (localKPI !== null) {
      isVisible = localKPI.includes(w.id.replace('kc-', ''));
    }

    const kc = document.createElement('div');
    kc.className = `kc ${w.colorClass} ${isVisible ? '' : 'hidden'}`;
    kc.id = w.id;
    kc.style.cursor = 'pointer';
    kc.addEventListener('click', (e) => showTraza(e, w.id));

    let extraControls = '';
    if (window.DASHBOARD_EDIT_MODE) {
      kc.classList.remove('hidden');
      kc.style.border = '2px dashed var(--blue)';
      kc.style.position = 'relative';
      extraControls = `
        <button onclick="removeWidget('${w.id}')" style="position: absolute; top: 2px; right: 2px; background: var(--red); color: white; border: none; border-radius: 4px; padding: 1px 4px; font-size: 8px; cursor: pointer; z-index: 10;">✕</button>
      `;
    }

    kc.innerHTML = `
      <div class="kstripe"></div>
      <div class="ktop">
        <span class="klbl">${w.title}</span>
        <span class="kico">${w.icon}</span>
      </div>
      <div class="kval" id="kv-${w.id.replace('kc-', '')}">—</div>
      <div class="ksub" id="ks-${w.id.replace('kc-', '')}">${w.subtitle || ''}</div>
      <div class="kbar">
        <div class="kbf" id="kb-${w.id.replace('kc-', '')}" style="width:0%"></div>
      </div>
      ${extraControls}
    `;
    kgrid.appendChild(kc);
  });

  renderKPIPills();
}

function renderKPIPills() {
  const container = G('kpi-pills-container');
  if (!container) return;
  container.innerHTML = '';

  const kpis = window.DASHBOARD_CONFIG
    .filter(w => w.type === 'kpi')
    .sort((a, b) => a.order - b.order);

  kpis.forEach(w => {
    let isVisible = w.visible;
    const localKPI = LS.get('kpi', null);
    if (localKPI !== null) {
      isVisible = localKPI.includes(w.id.replace('kc-', ''));
    }

    const pill = document.createElement('span');
    pill.className = `pill ${isVisible ? 'on' : ''} ${w.colorClass}`;
    pill.dataset.id = w.id.replace('kc-', '');
    pill.onclick = () => {
      if (window.DASHBOARD_EDIT_MODE) {
        w.visible = !w.visible;
        renderDashboardWidgets();
        loadDash();
      } else {
        tkpi(pill);
      }
    };
    pill.innerHTML = `<span class="dot"></span>${w.title}`;
    container.appendChild(pill);
  });
}

async function loadEmpresasDropdown(){
  try{
    const res = await fetch('/api/empresas');
    EMPRESAS_CACHE = await res.json();
    const menu = G('company-sel-menu');
    menu.innerHTML = '';
    EMPRESAS_CACHE.forEach(function(emp){
      const isHolding = emp.id === 1;
      const initials = deriveInitials(emp.nombre_corto);
      const item = document.createElement('div');
      item.className = 'company-sel-item' + (isHolding ? ' active' : '');
      item.onclick = function(){ selectCompany(item, emp.nombre_corto, emp.color, initials, isHolding ? null : emp.id); };
      item.innerHTML = `<span class="company-dot" style="background:${emp.color}"></span>${emp.nombre_corto}`;
      menu.appendChild(item);
    });
    poblarSelectorEmpresaESF();
    poblarSelectorEmpresaDatos();
    poblarSelectorEmpresaBriefing();
  }catch(e){
    console.error('Error cargando empresas', e);
    showA('global-error', 'No se pudieron cargar las empresas. Intenta recargar la pagina.');
  }

}

function poblarSelectorEmpresaESF(){
  const sel = G('up-empresa-esf');
  if(!sel) return;
  sel.innerHTML = '';
  EMPRESAS_CACHE.filter(function(e){ return e.id !== 1; }).forEach(function(emp){
    const opt = document.createElement('option');
    opt.value = emp.id;
    opt.textContent = emp.nombre_corto;
    sel.appendChild(opt);
  });
}

function poblarSelectorEmpresaDatos(){
  const sel = G('d-empresa');
  if(!sel) return;
  const current = sel.value;
  sel.innerHTML = '<option value="">Todas las empresas</option>';
  EMPRESAS_CACHE.filter(function(e){ return e.id !== 1; }).forEach(function(emp){
    const opt = document.createElement('option');
    opt.value = emp.id;
    opt.textContent = emp.nombre_corto;
    sel.appendChild(opt);
  });
  sel.value = current;
}

function poblarSelectorEmpresaBriefing(){
  const sel = G('ai-empresa');
  if(!sel) return;
  const current = sel.value;
  sel.innerHTML = '';
  EMPRESAS_CACHE.forEach(function(emp){
    const opt = document.createElement('option');
    opt.value = emp.id;
    opt.textContent = emp.nombre_corto;
    sel.appendChild(opt);
  });
  sel.value = current || (CURRENT_EMPRESA_ID !== null ? CURRENT_EMPRESA_ID : '1');
}

async function loadUnidadesCache(){
  try{
    const res = await fetch('/api/unidades');
    UNIDADES_CACHE = await res.json();
  }catch(e){
    console.error('Error cargando unidades', e);
    showA('global-error', 'No se pudieron cargar las unidades. Intenta recargar la pagina.');
  }

}

function updateAiUnitOptions(){
  const empresaSel = G('ai-empresa');
  const unitSel = G('ai-unit');
  if(!empresaSel || !unitSel) return;
  const empresaIdRaw = empresaSel.value;
  const current = unitSel.value;
  unitSel.innerHTML = '<option value="">Consolidado grupo</option>';

  if(empresaIdRaw === '1'){
    // Holding: todas las unidades reales + empresas sin unidad propia como opcion equivalente
    UNIDADES_CACHE.forEach(function(u){
      const opt = document.createElement('option');
      opt.value = u.nombre;
      opt.textContent = u.nombre;
      unitSel.appendChild(opt);
    });
    const empresasConUnidad = new Set(UNIDADES_CACHE.map(function(u){ return u.empresa_id; }));
    EMPRESAS_CACHE.filter(function(e){ return e.id !== 1 && !empresasConUnidad.has(e.id); }).forEach(function(emp){
      const opt = document.createElement('option');
      opt.value = 'EMPRESA:' + emp.id;
      opt.textContent = emp.nombre_corto + ' (empresa completa)';
      unitSel.appendChild(opt);
    });
  } else {
    const empresaId = parseInt(empresaIdRaw);
    UNIDADES_CACHE.filter(function(u){ return u.empresa_id === empresaId; }).forEach(function(u){
      const opt = document.createElement('option');
      opt.value = u.nombre;
      opt.textContent = u.nombre;
      unitSel.appendChild(opt);
    });
  }

  unitSel.value = current;
  if(unitSel.value !== current) unitSel.value = '';
}

function updateAiComparativaCheckboxes(){
  const empresaId = G('ai-empresa') ? parseInt(G('ai-empresa').value) : null;
  const cont = G('ai-units-comparativa-list');
  if(!cont) return;
  // Ucafe excluida: es venta de café, negocio distinto al resto (retail) — no es comparable, decisión de negocio.
  const unidadesEmpresa = (empresaId && !isNaN(empresaId))
    ? UNIDADES_CACHE.filter(function(u){ return u.empresa_id === empresaId && u.nombre !== 'Ucafe'; })
    : [];
  cont.innerHTML = unidadesEmpresa.map(function(u){
    return `<label style="display:flex;align-items:center;gap:8px;font-size:12px"><input type="checkbox" class="ai-unit-check" value="${u.nombre}" onchange="updateAiBriefingPreview()"> ${u.nombre}</label>`;
  }).join('');
}

function updateUnitSelectorsForEmpresa(){
  const tieneUnidadesPropias = CURRENT_EMPRESA_ID !== null &&
    UNIDADES_CACHE.some(function(u){ return u.empresa_id === CURRENT_EMPRESA_ID; });

  const unidadesEmpresa = CURRENT_EMPRESA_ID !== null
    ? UNIDADES_CACHE.filter(function(u){ return u.empresa_id === CURRENT_EMPRESA_ID; })
    : [];

  function repoblar(sel, valorTodas, labelTodas){
    if(!sel) return;
    sel.innerHTML = `<option value="${valorTodas}">${labelTodas}</option>`;
    unidadesEmpresa.forEach(function(u){
      const opt = document.createElement('option');
      opt.value = u.nombre;
      opt.textContent = u.nombre;
      sel.appendChild(opt);
    });
  }

  const dashUnit = G('dash-unit');
  repoblar(dashUnit, 'TODAS', 'Todas las Unidades');
  if(dashUnit){
    dashUnit.disabled = !tieneUnidadesPropias;
    if(!tieneUnidadesPropias) dashUnit.value = 'TODAS';
  }

  const eerrUnit = G('eerr-unit');
  repoblar(eerrUnit, '', 'Consolidado');
  if(eerrUnit){
    eerrUnit.disabled = !tieneUnidadesPropias;
    if(!tieneUnidadesPropias) eerrUnit.value = '';
  }

  const errDivisaUnit = G('err-divisa-unit');
  repoblar(errDivisaUnit, '', 'Consolidado');
  if(errDivisaUnit){
    errDivisaUnit.disabled = !tieneUnidadesPropias;
    if(!tieneUnidadesPropias) errDivisaUnit.value = '';
  }

  // Ucafe excluida de Comparativas: es venta de café, negocio distinto al resto (retail) — no es comparable, decisión de negocio.
  const cmpUnit = G('cmp-unit');
  if(cmpUnit){
    cmpUnit.innerHTML = '<option value="">Todas</option>';
    unidadesEmpresa.filter(function(u){ return u.nombre !== 'Ucafe'; }).forEach(function(u){
      const opt = document.createElement('option');
      opt.value = u.nombre;
      opt.textContent = u.nombre;
      cmpUnit.appendChild(opt);
    });
    cmpUnit.disabled = !tieneUnidadesPropias;
    if(!tieneUnidadesPropias) cmpUnit.value = '';
  }

  const exUnit = G('ex-unit');
  if(exUnit){
    exUnit.innerHTML = '<option value="">Consolidado — Todas</option>';
    unidadesEmpresa.forEach(function(u){
      const opt = document.createElement('option');
      opt.value = u.nombre;
      opt.textContent = u.nombre;
      exUnit.appendChild(opt);
    });
    exUnit.disabled = !tieneUnidadesPropias;
    if(!tieneUnidadesPropias) exUnit.value = '';
  }
}

function updateSidebarForEmpresa(){
  const esHolding = CURRENT_EMPRESA_ID === null;
  G('nav-cargar').style.display = esHolding ? 'none' : '';
  G('nav-tasas').style.display = esHolding ? 'none' : '';
}

// ── KPI PILLS ─────────────────────────────────────────────────────────────
function tkpi(pill){
  const id=pill.dataset.id, on=pill.classList.toggle('on');
  const c=G('kc-'+id); if(c) c.classList.toggle('hidden',!on);
  const p=LS.get('kpi',[]); if(on){if(!p.includes(id))p.push(id);}else{const i=p.indexOf(id);if(i>=0)p.splice(i,1);}
  LS.set('kpi',p);
}
function applyKpi(){
  const p=LS.get('kpi',null); if(p===null) return;
  document.querySelectorAll('.pill[data-id]').forEach(pill=>{
    const id=pill.dataset.id, on=p.includes(id);
    pill.classList.toggle('on',on);
    const c=G('kc-'+id); if(c) c.classList.toggle('hidden',!on);
  });
}

// ── WIDGET CLOSE / RESTORE ────────────────────────────────────────────────
function initClose(){
  document.querySelectorAll('.bcl[data-w]').forEach(btn=>{
    btn.addEventListener('click',e=>{
      e.stopPropagation();
      const w=btn.dataset.w, el=G(w);
      if(el) el.classList.add('whidden');
      const h=LS.get('hidden',[]); if(!h.includes(w))h.push(w); LS.set('hidden',h);
      chkBar();scheduleMasonry();
    });
  });
}
function applyHidden(){
  LS.get('hidden',[]).forEach(w=>{const el=G(w);if(el)el.classList.add('whidden');});
  chkBar();
}
function restoreW(){
  document.querySelectorAll('[id^="wc-"]').forEach(el=>el.classList.remove('whidden'));
  LS.set('hidden',[]); chkBar(); scheduleMasonry();
}
function chkBar(){
  G('rbar').style.display=document.querySelectorAll('[id^="wc-"].whidden').length?'block':'none';
}

// ── MASONRY (layout puzzle: encaja las tarjetas sin huecos verticales) ──────
let _mtTimer=null;
function layoutMasonry(){
  const con=G('wcon'); if(!con) return;
  if(!con.offsetParent){con.classList.remove('wcon-ready');return;}   // omite si el dashboard está oculto
  const ROW=8, GAP=12;
  con.querySelectorAll('.wcard, .wsection').forEach(card=>{
    if(card.classList.contains('whidden')){card.style.gridRowEnd='';return;}
    const h=card.getBoundingClientRect().height;
    const span=Math.max(1,Math.ceil((h+GAP)/(ROW+GAP)));
    card.style.gridRowEnd='span '+span;
  });
  con.classList.add('wcon-ready');
}
function scheduleMasonry(){clearTimeout(_mtTimer);_mtTimer=setTimeout(layoutMasonry,90);}
window.addEventListener('resize',scheduleMasonry);

// ── DRAG & DROP ───────────────────────────────────────────────────────────
let dragId=null;
function saveDragOrder(){
  const con=G('wcon');
  const order=[...con.children].map(c=>c.id).filter(Boolean);
  LS.set('worder',order);
}
function restoreDragOrder(){
  const order=LS.get('worder',null);
  if(!order||!order.length)return;
  const con=G('wcon');
  order.forEach(id=>{const el=G(id);if(el)con.appendChild(el);});
}
function initDrag(){
  const con=G('wcon');
  restoreDragOrder();
  document.querySelectorAll('.wcard[draggable]').forEach(card=>{
    card.addEventListener('dragstart',e=>{dragId=card.id;e.dataTransfer.effectAllowed='move';setTimeout(()=>card.classList.add('dragging'),0);});
    card.addEventListener('dragend',()=>{card.classList.remove('dragging');document.querySelectorAll('.wcard').forEach(c=>c.classList.remove('dragover'));saveDragOrder();dragId=null;scheduleMasonry();});
    card.addEventListener('dragover',e=>{e.preventDefault();if(card.id!==dragId){document.querySelectorAll('.wcard').forEach(c=>c.classList.remove('dragover'));card.classList.add('dragover');}});
    card.addEventListener('dragleave',()=>card.classList.remove('dragover'));
    card.addEventListener('drop',e=>{
      e.preventDefault();card.classList.remove('dragover');
      if(!dragId||dragId===card.id)return;
      const src=G(dragId),tgt=card,all=[...con.children];
      const si=all.indexOf(src),ti=all.indexOf(tgt);
      if(si<ti)con.insertBefore(src,tgt.nextSibling);else con.insertBefore(src,tgt);
    });
  });
}

// ── MODAL REDIMENSIONABLE ─────────────────────────────────────────────────────
function initModalResize(){
  document.querySelectorAll('.modal').forEach(modal=>{
    if(modal.querySelector('.modal-resize-handle'))return; // ya inicializado
    const handle=document.createElement('div');
    handle.className='modal-resize-handle';
    handle.title='Arrastra para redimensionar';
    modal.appendChild(handle);
    let isResizing=false,startX,startY,startW,startH;
    handle.addEventListener('mousedown',e=>{
      e.preventDefault();e.stopPropagation();
      isResizing=true;
      startX=e.clientX;startY=e.clientY;
      startW=modal.offsetWidth;startH=modal.offsetHeight;
      modal.style.maxWidth='none';modal.style.maxHeight='none';
      modal.style.width=startW+'px';modal.style.height=startH+'px';
    });
    document.addEventListener('mousemove',e=>{
      if(!isResizing)return;
      const dx=e.clientX-startX,dy=e.clientY-startY;
      modal.style.width=Math.max(320,startW+dx)+'px';
      modal.style.height=Math.max(200,startH+dy)+'px';
    });
    document.addEventListener('mouseup',()=>{if(isResizing)isResizing=false;});
  });
}

// ── GAUGES ────────────────────────────────────────────────────────────────
function mkEChart(domId, lbl, val, min, max, ref, sub) {
  const dom = G(domId);
  if (!dom) return;
  if (dom._echart) dom._echart.dispose();
  const chart = echarts.init(dom);
  dom._echart = chart;

  const pct = Math.max(0, Math.min(100, ((val - min) / (max - min)) * 100));

  chart.setOption({
    series: [{
      type: 'gauge',
      startAngle: 200,
      endAngle: -20,
      min: min,
      max: max,
      radius: '88%',
      center: ['50%', '62%'],
      splitNumber: 4,
      axisLine: {
        lineStyle: {
          width: 18,
          color: [
            [ref / max * 0.5, '#E24B4A'],
            [ref / max * 0.85, '#EF9F27'],
            [1, '#1D9E75']
          ]
        }
      },
      pointer: {
        length: '72%',
        width: 4,
        itemStyle: { color: '#444441' }
      },
      axisTick: {
        distance: -22,
        length: 6,
        lineStyle: { color: '#fff', width: 1.5 }
      },
      splitLine: {
        distance: -28,
        length: 14,
        lineStyle: { color: '#fff', width: 2.5 }
      },
      axisLabel: {
        color: '#888780',
        fontSize: 9,
        distance: -42,
        formatter: (v) => v === min || v === max || v === Math.round((min+max)/2) ? v + (max <= 200 ? '%' : '') : ''
      },
      detail: {
        valueAnimation: true,
        formatter: (v) => v.toFixed(1) + '%',
        color: '#2C2C2A',
        fontSize: 18,
        fontWeight: '500',
        offsetCenter: [0, '28%']
      },
      title: {
        offsetCenter: [0, '55%'],
        fontSize: 10,
        color: '#888780',
        fontWeight: '400'
      },
      data: [{ value: val, name: sub }]
    }]
  });
}

function renderGauges(mn, peCov, rg) {
  try {
    mkEChart('gauge-mn', 'Margen Neto', mn, -20, 30, 10, 'Ref ≥10%');
    mkEChart('gauge-pe', 'Cobertura PE', peCov != null ? peCov : 0, 0, 150, 100, 'Ref ≥100%');
    mkEChart('gauge-ef', 'Efic. Operativa', 100 - rg, 0, 100, 60, '100−%Gasto/Vta');
  } catch(e) { console.warn('gauges', e); }
}

// ── RANKING ───────────────────────────────────────────────────────────────
function renderRank(pu){
  if(!pu||!pu.length){G('rankbody').innerHTML='<p style="color:var(--mu);font-size:12px;padding:10px 0">Sin datos.</p>';return;}
  const s=[...pu].sort((a,b)=>b.margen_neto-a.margen_neto);
  const mx=Math.max(...s.map(u=>Math.abs(u.utilidad_neta)),1);
  G('rankbody').innerHTML=s.map((u,i)=>{
    const p=i+1,cls=p===1?'p1':p===2?'p2':p===3?'p3':'pn',bw=cl(Math.abs(u.utilidad_neta)/mx*100,0,100),pos=u.utilidad_neta>=0;
    return`<div class="rkrow"><div class="rkpos ${cls}">${p}</div><div class="rkunit">${u.unit}</div><div class="rkbw"><div class="rkb ${pos?'pos':'neg'}" style="width:${bw}%"></div></div><div class="rkval ${pos?'pos':'neg'}">${fmtS(u.utilidad_neta)}</div><div class="rkpct" style="color:${u.margen_neto>=0?'var(--green)':'var(--red)'}">${pct(u.margen_neto)}</div></div>`;
  }).join('');
}

// ── PE ─────────────────────────────────────────────────────────────────────
function renderPE(pe){
  const w=G('wc-pe');
  if(!pe){if(w)w.style.display='none';return;}
  if(w){w.style.display='';if(LS.get('hidden',[]).includes('wc-pe'))w.classList.add('whidden');}
  const cov=cl(pe.cobertura_pct,0,150),fill=cov/150*100,mk=100/150*100;
  G('pe-card').innerHTML=`
    <div class="pe-body">
      <div><div class="pe-val">${fmtS(pe.pe_ingresos)}</div><div class="pe-lbl">Ingresos en P.E.</div></div>
      <div><div class="pe-val">${fmtS(pe.ingresos_actuales)}</div><div class="pe-lbl">Ingresos Actuales</div></div>
      <div><div class="pe-val" style="color:${pe.cobertura_pct>=100?'var(--green)':'var(--red)'}">${pct(pe.cobertura_pct)}</div><div class="pe-lbl">Cobertura P.E.</div></div>
    </div>
    <div class="pe-track"><div class="pe-fill" style="width:${fill}%"></div><div class="pe-mark" style="left:${mk}%"></div></div>
    <div class="pe-lbls"><span>$0</span><span style="color:var(--red);font-weight:600">P.E.=${fmtS(pe.pe_ingresos)}</span><span>${fmtS(pe.pe_ingresos*1.5)}</span></div>
    <div style="margin-top:7px;font-size:10px;color:var(--mu)">Mc: ${pct(pe.margen_contribucion_pct)} — ${pe.cobertura_pct>=100?'✅ Por encima del PE':'⚠️ Por debajo del PE'}</div>`;
}

// ── TREEMAP ───────────────────────────────────────────────────────────────
function renderTM(items,con){
  try{
    con.innerHTML='';
    if(!items||!items.length)return;
    const tot=items.reduce((a,i)=>a+i.v,0); if(!tot)return;
    const W=con.offsetWidth||400,H=con.offsetHeight||185;
    function sq(its,x,y,w,h){
      if(!its.length)return[];
      const rs=[];let rem=[...its];
      while(rem.length){
        let row=[],rs2=0,worst=Infinity;
        const len=w<h?w:h;
        for(let i=0;i<rem.length;i++){
          const it=rem[i];row.push(it);rs2+=it.v;
          const ra=row.map(it2=>{const a=(it2.v/tot)*W*H,ra=(rs2/tot)*W*H,s=ra/len;return Math.max(a/s,s/(a/s||1));});
          const nw=Math.max(...ra);
          if(nw>worst&&row.length>1){row.pop();rs2-=it.v;break;}
          worst=nw;
        }
        rem=rem.slice(row.length);
        const ra=(rs2/tot)*W*H;
        if(w>=h){const rw=ra/h;let cy=y;row.forEach(it=>{const rh=(it.v/rs2)*h;rs.push({...it,x,y:cy,w:rw,h:rh});cy+=rh;});x+=rw;w-=rw;}
        else{const rh=ra/w;let cx=x;row.forEach(it=>{const rw=(it.v/rs2)*w;rs.push({...it,x:cx,y,w:rw,h:rh});cx+=rw;});y+=rh;h-=rh;}
      }
      return rs;
    }
    sq(items,0,0,W,H).forEach(r=>{
      const el=document.createElement('div');
      el.className='tmc';
      el.style.cssText=`left:${r.x}px;top:${r.y}px;width:${r.w}px;height:${r.h}px;background:${r.c}`;
      const p=(r.v/tot*100).toFixed(1);
      el.innerHTML=`<div class="tml">${r.w>55&&r.h>30?`<div class="tmn">${r.l}</div>`:''}${r.w>55&&r.h>45?`<div class="tmv">${fmtS(r.v)}</div>`:''}${r.w>65&&r.h>60?`<div class="tmp">${p}%</div>`:''}</div>`;
      el.title=`${r.l}: ${fmt(r.v)} (${p}%)`;
      con.appendChild(el);
    });
  }catch(e){console.warn('treemap',e);}
}

function buildCharts(isTodas){
  const d=DD,L=d.months.map(m=>m.month);
  mainDS={labels:L,datasets:[
    {label:'Ingresos',data:d.months.map(m=>m.ingresos),backgroundColor:'rgba(37,99,235,.7)',borderColor:'#2563eb',borderWidth:1.5,borderRadius:4,order:2},
    {label:'Costos',  data:d.months.map(m=>m.costos),  backgroundColor:'rgba(220,38,38,.6)', borderColor:'#dc2626',borderWidth:1.5,borderRadius:4,order:2},
    {label:'Gastos',  data:d.months.map(m=>m.gastos),  backgroundColor:'rgba(217,119,6,.6)', borderColor:'#d97706',borderWidth:1.5,borderRadius:4,order:2},
  ]};
  rebuildMain();
  const u=d.por_unidad||[],tmCon=G('tmcon');
  if(isTodas&&u.length){
    G('tm-title').textContent='Participación por Unidad';
    setTimeout(()=>renderTM(u.map((x,i)=>({l:x.unit,v:x.ingresos,c:PAL[i%PAL.length]})),tmCon),60);
    G('rad-title').textContent='Comparativo Multidimensional';G('rad-sub').textContent='6 dimensiones por unidad · clic para ver detalle';
    const mx=Math.max(...u.map(x=>x.ingresos),1);
    mkPref('ch-rad','radar',['Ingresos','Mg.Bruto','Mg.Neto','Ef.Costo','Ef.Gasto','Util.Neta'],
      u.map((x,i)=>({label:x.unit,data:[cl(x.ingresos/mx*100,0,100),cl(x.margen_bruto,0,100),cl(x.margen_neto+20,0,100),cl(100-x.ratio_costo,0,100),cl(100-x.ratio_gasto,0,100),cl((x.utilidad_neta/(x.ingresos||1)*100)+50,0,100)],
        borderColor:PAL[i%PAL.length],backgroundColor:PAL[i%PAL.length]+'14',pointBackgroundColor:PAL[i%PAL.length],pointBorderColor:'#fff',pointBorderWidth:2,borderWidth:2})),
      {onClick:(e,els)=>chartUniversalClick('ch-rad',els),scales:{r:{ticks:{display:false},grid:{color:'rgba(0,0,0,.07)'},pointLabels:{color:'#64748b',font:{size:9,family:'DM Sans'}},angleLines:{color:'rgba(0,0,0,.07)'}}},
       plugins:{legend:{position:'bottom',labels:{color:'#64748b',font:{size:9,family:'DM Sans'},boxWidth:8,padding:9}},tooltip:{callbacks:{label:ctx=>`${ctx.dataset.label}`}}}},
      ['radar','line','bar']);
  } else if(!isTodas){
    const cats=d.cat_gastos||[];
    G('tm-title').textContent='Estructura de Gastos';
    setTimeout(()=>renderTM(cats.map((c,i)=>({l:c.categoria,v:c.total,c:PAL[i%PAL.length]})),tmCon),60);
    G('rad-title').textContent='Ingresos vs Util. Neta';G('rad-sub').textContent='Evolución mensual · clic para ver detalle';
    mkPref('ch-rad','line',L,[
      {label:'Ingresos',data:d.months.map(m=>m.ingresos),borderColor:'#2563eb',backgroundColor:'rgba(37,99,235,.07)',tension:.4,fill:true,pointRadius:3,pointBackgroundColor:'#2563eb',pointBorderColor:'#fff',pointBorderWidth:2},
      {label:'Util.Neta',data:d.months.map(m=>m.utilidad_neta),borderColor:'#059669',backgroundColor:'rgba(5,150,105,.07)',tension:.4,fill:true,pointRadius:3,pointBackgroundColor:'#059669',pointBorderColor:'#fff',pointBorderWidth:2},
    ],{...cOpts(),onClick:(e,els)=>chartUniversalClick('ch-rad',els)},['line','bar']);
  }
  mkPref('ch-mg','line',L,[
    {label:'Mg Bruto %',data:d.months.map(m=>m.margen_bruto),borderColor:'#059669',backgroundColor:'rgba(5,150,105,.08)',tension:.4,fill:true,pointRadius:3,pointBackgroundColor:'#059669',pointBorderColor:'#fff',pointBorderWidth:2},
    {label:'Mg Neto %', data:d.months.map(m=>m.margen_neto), borderColor:'#2563eb',backgroundColor:'rgba(37,99,235,.08)',tension:.4,fill:true,pointRadius:3,pointBackgroundColor:'#2563eb',pointBorderColor:'#fff',pointBorderWidth:2},
  ],{onClick:(e,els)=>chartUniversalClick('ch-mg',els),...cOpts({scales:{x:{grid:{color:'rgba(0,0,0,.04)'},ticks:{color:'#94a3b8',font:{size:10}}},y:{grid:{color:'rgba(0,0,0,.06)'},ticks:{color:'#94a3b8',font:{size:10},callback:v=>v+'%'}}}})},['line','bar']);
  mkPref('ch-un','bar',L,[{label:'Utilidad Neta',data:d.months.map(m=>m.utilidad_neta),
    backgroundColor:d.months.map(m=>m.utilidad_neta>=0?'rgba(5,150,105,.75)':'rgba(220,38,38,.75)'),
    borderColor:d.months.map(m=>m.utilidad_neta>=0?'#059669':'#dc2626'),borderWidth:1,borderRadius:4}],
    {onClick:(e,els)=>chartUniversalClick('ch-un',els),...cOpts({plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>` Util.Neta: ${fmt(ctx.parsed.y)}`}}}})},['bar','line']);
  const cats=d.cat_gastos||[];
  mkPref('ch-est','doughnut',cats.map(c=>c.categoria),[{data:cats.map(c=>c.total),backgroundColor:PAL,borderWidth:2,borderColor:'#fff',hoverOffset:6}],
    {onClick:(e,els)=>chartGastoClick('ch-est',els)},['doughnut','pie','bar']);
  const tg=d.top_gastos||[],totG=tg.reduce((a,g)=>a+g.total,0)||1;
  mkPref('ch-tg','bar',tg.map(g=>g.partida.length>42?g.partida.substring(0,42)+'…':g.partida),
    [{label:'Monto',data:tg.map(g=>g.total),backgroundColor:tg.map((_,i)=>`rgba(220,38,38,${.85-i*.06})`),borderColor:'#dc2626',borderWidth:1,borderRadius:3}],
    cOpts({indexAxis:'y',onClick:(e,els)=>chartGastoClick('ch-tg',els),scales:{x:{grid:{color:'rgba(0,0,0,.04)'},ticks:{color:'#94a3b8',font:{size:9},callback:v=>'$'+(v>=1e3?(v/1e3).toFixed(0)+'K':v)}},y:{grid:{display:false},ticks:{color:'#64748b',font:{size:9}}}},
      plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>` ${fmt(ctx.parsed.x)} (${(ctx.parsed.x/totG*100).toFixed(1)}%)`}}}}),['bar','line']);
}

// ── DRILL-DOWN DE GASTOS (gráficos interactivos #2) ─────────────────────────
async function chartEstCapDetClick(e, els, quartersConDatos) {
  if (!els || !els.length || !DD) return;
  const el = els[0];
  const chart = e.chart || CH['ch-estcapdet'];
  const ds = chart.data.datasets[el.datasetIndex];
  const partida = ds._partidaReal || ds.label;
  if (!partida || partida.startsWith('Otros (')) return;
  const quarter = quartersConDatos[el.index];
  const year = G('dash-year').value, unit = G('dash-unit').value;
  const panel = G('traza-panel');
  panel.style.display = 'block';
  const scrollY = window.scrollY || document.documentElement.scrollTop;
  const scrollX = window.scrollX || document.documentElement.scrollLeft;
  panel.style.top = (e.native.clientY + scrollY + 10) + 'px';
  panel.style.left = (e.native.clientX + scrollX) + 'px';
  G('tp-title').textContent = partida;
  G('tp-total').textContent = 'Cargando...';
  G('tp-rows').innerHTML = '<div class="tp-loading">Consultando cuentas...</div>';
  try {
    const u = unit && unit !== 'TODAS' ? unit : '';
    const dr = modoDivisaReal ? 1 : 0;
    const r = await fetch(`/api/esf/trazabilidad?year=${year}&quarter=${quarter}&unit=${u}&empresa_id=${CURRENT_EMPRESA_ID||''}&partida=${encodeURIComponent(partida)}&divisa_real=${dr}`);
    const d = await r.json();
    G('tp-title').textContent = d.partida + (d.divisa_real ? ' (Divisa Real)' : '');
    G('tp-total').textContent = `Total: ${fmtS(d.total)} · Q${d.quarter} · ${d.cuentas.length} cuentas`;
    G('tp-rows').innerHTML = d.cuentas.length
      ? d.cuentas.map(c => `
        <div class="tp-row">
          <span class="tp-name" title="${c.label}">${c.label}</span>
          <span class="tp-val ${c.total < 0 ? 'tp-neg' : ''}">${fmtS(Math.abs(c.total))}</span>
        </div>`).join('')
      : '<p style="color:var(--mu);font-size:12px;padding:8px 0">Sin cuentas con movimiento.</p>';
  } catch(err) {
    G('tp-total').textContent = 'Error al cargar';
    G('tp-rows').innerHTML = '';
  }
}
function chartGastoClick(id,els){
  if(!els||!els.length||!DD)return;
  const idx=els[0].index;
  if(id==='ch-est'){const c=(DD.cat_gastos||[])[idx]; if(c)openGastoDetalle({categoria:c.categoria});}
  else if(id==='ch-tg'){const g=(DD.top_gastos||[])[idx]; if(g)openGastoDetalle({partida:g.partida});}
}
async function openGastoDetalle(q){
  const year=G('dash-year').value, unit=G('dash-unit').value;
  let url=`/api/gasto/detalle?year=${year}&unit=${encodeURIComponent(unit)}`;
  url += q.partida ? `&partida=${encodeURIComponent(q.partida)}` : `&categoria=${encodeURIComponent(q.categoria)}`;
  G('det-title').textContent='Cargando…'; G('det-sub').textContent=''; G('det-parts').innerHTML='';
  G('detmod').classList.add('show');
  try{
    const r=await fetch(url); const d=await r.json();
    if(d.error){G('det-title').textContent='Error'; G('det-parts').innerHTML=`<p style="color:var(--red);font-size:12px">${d.error}</p>`; return;}
    renderGastoDetalle(d);
  }catch(e){G('det-title').textContent='Error'; G('det-parts').innerHTML=`<p style="color:var(--red);font-size:12px">${e.message}</p>`;}
}
function renderGastoDetalle(d){
  G('det-title').textContent=(d.es_categoria?'Categoría · ':'Partida · ')+d.titulo;
  G('det-sub').textContent=`${d.unit} · ${d.year} · Total ${fmt(d.total)} · ${pct(d.pct_gastos)} del total de gastos`;
  G('det-parts').innerHTML = d.partidas.length
    ? d.partidas.map(p=>`<div class="detrow"><span>${p.partida}</span><span class="detval">${fmt(p.total)}</span></div>`).join('')
    : '<p style="color:var(--mu);font-size:12px;padding:8px 0">Sin partidas con movimiento en el período.</p>';
  setTimeout(()=>{
    mk('ch-det','bar',d.meses.map(m=>m.month),
      [{label:d.titulo,data:d.meses.map(m=>m.amount),backgroundColor:'rgba(220,38,38,.6)',borderColor:'#dc2626',borderWidth:1,borderRadius:4}],
      cOpts({plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>` ${fmt(ctx.parsed.y)}`}}}}));
  },50);
}
function closeDet(){G('detmod').classList.remove('show'); if(CH['ch-det']){CH['ch-det'].destroy();delete CH['ch-det'];}}

// ── DRILL-DOWN UNIVERSAL (todos los gráficos) ────────────────────────────────
function chartUniversalClick(id,els){
  if(!DD)return; // solo funciona en dashboard con datos cargados
  openUniversalDetalle(id);
}
async function openUniversalDetalle(id){
  const year=G('dash-year').value, unit=G('dash-unit').value;
  let url=`/api/grafico/detalle?chart_id=${id}&year=${year}&unit=${encodeURIComponent(unit)}&empresa_id=${CURRENT_EMPRESA_ID||''}`;
  G('det-title').textContent='Cargando…'; G('det-sub').textContent=''; G('det-parts').innerHTML='';
  G('detmod').classList.add('show');
  try{
    const r=await fetch(url); const d=await r.json();
    if(d.error){G('det-title').textContent='Error'; G('det-parts').innerHTML=`<p style="color:var(--red);font-size:12px">${d.error}</p>`; return;}
    renderUniversalDetalle(d);
  }catch(e){G('det-title').textContent='Error'; G('det-parts').innerHTML=`<p style="color:var(--red);font-size:12px">${e.message}</p>`;}
}
function renderUniversalDetalle(d){
  G('det-title').textContent=d.titulo;
  G('det-sub').textContent=`${d.unit} · ${d.year}`;
  if(d.meses){
    // Tabla mensual (ch-main, ch-mg, ch-un, ch-rad unidad)
    const cols=Object.keys(d.meses[0]).filter(k=>k!=='month');
    const hdr=`<div class="detrow" style="font-weight:700;background:var(--sf3);position:sticky;top:0"><span>Mes</span>${cols.map(c=>`<span>${c.replace(/_/g,' ')}</span>`).join('')}</div>`;
    G('det-parts').innerHTML=hdr+d.meses.map(m=>{
      const vals=cols.map(c=>`<span class="detval">${typeof m[c]==='number'?fmt(m[c]):m[c]}</span>`).join('');
      return`<div class="detrow"><span>${m.month}</span>${vals}</div>`;
    }).join('');
  }else if(d.unidades){
    // Tabla por unidad (ch-rad consolidado)
    const cols=Object.keys(d.unidades[0]).filter(k=>k!=='unit');
    const hdr=`<div class="detrow" style="font-weight:700;background:var(--sf3);position:sticky;top:0"><span>Unidad</span>${cols.map(c=>`<span>${c.replace(/_/g,' ')}</span>`).join('')}</div>`;
    G('det-parts').innerHTML=hdr+d.unidades.map(u=>{
      const vals=cols.map(c=>`<span class="detval">${typeof u[c]==='number'?(c.includes('margen')||c.includes('pct')?pct(u[c]):fmt(u[c])):u[c]}</span>`).join('');
      return`<div class="detrow"><span>${u.unit}</span>${vals}</div>`;
    }).join('');
  }else{
    G('det-parts').innerHTML='<p style="color:var(--mu);font-size:12px;padding:8px 0">Sin datos.</p>';
  }
  // No hay gráfico para tablas genéricas (el modal solo muestra la tabla)
  if(CH['ch-det']){CH['ch-det'].destroy();delete CH['ch-det'];}
}

function rebuildMain(){
  if(!mainDS)return;
  const type=G('mtype').value;
  if(CH['ch-main'])CH['ch-main'].destroy();
  const ctx=G('ch-main');if(!ctx)return;
  if(type==='combo'){
    const L=mainDS.labels,un=DD.months.map(m=>m.utilidad_neta);
    const ds=[
      {type:'bar', label:'Ingresos',data:DD.months.map(m=>m.ingresos),backgroundColor:'rgba(37,99,235,.7)',borderColor:'#2563eb',borderWidth:1,borderRadius:4,order:2},
      {type:'bar', label:'Costos',  data:DD.months.map(m=>m.costos),  backgroundColor:'rgba(220,38,38,.6)',borderColor:'#dc2626',borderWidth:1,borderRadius:4,order:2},
      {type:'bar', label:'Gastos',  data:DD.months.map(m=>m.gastos),  backgroundColor:'rgba(217,119,6,.6)',borderColor:'#d97706',borderWidth:1,borderRadius:4,order:2},
      {type:'line',label:'Util.Neta',data:un,borderColor:'#7c3aed',backgroundColor:'rgba(124,58,237,.08)',tension:.4,fill:true,pointRadius:4,pointBackgroundColor:un.map(v=>v>=0?'#059669':'#dc2626'),pointBorderColor:'#fff',pointBorderWidth:2,borderWidth:2,order:1},
    ];
    CH['ch-main']=new Chart(ctx.getContext('2d'),{type:'bar',data:{labels:L,datasets:ds},options:{onClick:(e,els)=>chartUniversalClick('ch-main',els),...cOpts()}});
  } else {
    const ds=mainDS.datasets.map(d=>({...d,type,fill:false,tension:.4,
      backgroundColor:type==='line'?d.borderColor:d.backgroundColor,
      pointRadius:type==='line'?3:undefined,pointBackgroundColor:type==='line'?d.borderColor:undefined,
      pointBorderColor:type==='line'?'#fff':undefined,pointBorderWidth:type==='line'?2:undefined}));
    CH['ch-main']=new Chart(ctx.getContext('2d'),{type,data:{labels:mainDS.labels,datasets:ds},options:{onClick:(e,els)=>chartUniversalClick('ch-main',els),...cOpts()}});
  }
}

function rWF(tI,tC,ub,tG,un){
  const max=tI||1;
  const rows=[{l:'Ingresos Totales',v:tI,c:'#2563eb'},{l:'(−) Costo de Ventas',v:tC,c:'#dc2626'},
              {l:'= Utilidad Bruta',v:ub,c:'#059669'},{l:'(−) Gastos Operac.',v:tG,c:'#d97706'},
              {l:'= Utilidad Neta',v:un,c:un>=0?'#059669':'#dc2626'}];
  G('wf').innerHTML=rows.map(r=>`<div class="wfrow"><div class="wflbl">${r.l}</div><div class="wftr"><div class="wff" style="width:${cl(Math.abs(r.v)/max*100,2,100)}%;background:${r.c}18;border-left:3px solid ${r.c}"><span style="color:${r.c};font-size:10px">${fmtS(r.v)}</span></div></div><div class="wfn" style="color:${r.c}">${fmt(r.v)}</div></div>`).join('');
}

function rTable(){
  if(!DD)return;
  const mode=G('tblmode')?G('tblmode').value:'$';
  const isPct=mode==='%';
  G('tbody').innerHTML=DD.months.map(m=>{
    const uc=m.utilidad_neta>=0?'chg':'chr',mb=m.margen_bruto>=30?'chg':m.margen_bruto>=20?'chy':'chr',mn=m.margen_neto>=5?'chg':m.margen_neto>=0?'chy':'chr';
    if(isPct){
      const tI=m.ingresos||1;
      return`<tr><td>${m.month}</td><td>100%</td><td>${pct(m.costos/tI*100)}</td><td><span class="chip ${mb}">${pct(m.margen_bruto)}</span></td><td>${pct(m.gastos/tI*100)}</td><td><span class="chip ${uc}">${pct(m.margen_neto)}</span></td><td><span class="chip ${mb}">${pct(m.margen_bruto)}</span></td><td><span class="chip ${mn}">${pct(m.margen_neto)}</span></td><td>${pct(m.ratio_costo)}</td><td>${pct(m.ratio_gasto)}</td></tr>`;
    }
    return`<tr><td>${m.month}</td><td>${fmt(m.ingresos)}</td><td>${fmt(m.costos)}</td><td>${fmt(m.utilidad_bruta)}</td><td>${fmt(m.gastos)}</td><td><span class="chip ${uc}">${fmt(m.utilidad_neta)}</span></td><td><span class="chip ${mb}">${pct(m.margen_bruto)}</span></td><td><span class="chip ${mn}">${pct(m.margen_neto)}</span></td><td>${pct(m.ratio_costo)}</td><td>${pct(m.ratio_gasto)}</td></tr>`;
  }).join('');
}

// ── ESF Dashboard: fuente de filas segun modo BCV/Divisa Real ─────────────
// En modo Normal, /api/esf/completo trae los 4 trimestres del año en una sola
// llamada. En modo Divisa Real, /api/esf-divisa-real exige un quarter puntual
// solo para validar que ese trimestre tenga tasas cargadas, pero el bloque que
// usamos (esf_completo) siempre trae los 4 trimestres juntos sin importar cual
// quarter se haya mandado -- probamos del mas reciente al mas viejo hasta que
// alguno responda 200, y usamos esa respuesta igual para los 4 trimestres.
let _esfRowsCache = null;
let _esfRowsCacheKey = null;
let _esfRowsPromise = null;

async function fetchESFRowsDashboard(year) {
  const modoAlEntrar = modoDivisaReal;
  const cacheKey = `${year}|${modoDivisaReal}|${CURRENT_EMPRESA_ID}`;
  console.log('[FETCH-IN]', performance.now().toFixed(1), 'modo=', modoDivisaReal, 'cacheKey=', cacheKey);
  if (_esfRowsCacheKey === cacheKey && _esfRowsCache !== null) {
    console.log('[FETCH-OUT]', performance.now().toFixed(1), 'modoAlEntrar=', modoAlEntrar, 'modoAlSalir=', modoDivisaReal);
    return _esfRowsCache;
  }
  if (_esfRowsPromise && _esfRowsCacheKey === cacheKey) {
    console.log('[FETCH-OUT]', performance.now().toFixed(1), 'modoAlEntrar=', modoAlEntrar, 'modoAlSalir=', modoDivisaReal);
    return _esfRowsPromise;
  }

  _esfRowsCacheKey = cacheKey;
  _esfRowsCache = null;
  _esfRowsPromise = (async () => {
    // Fix ago-2026 (condicion de carrera): captura la key con la que arranco ESTA
    // promesa. Si para cuando termina de resolver ya cambio _esfRowsCacheKey (otra
    // llamada mas reciente, ej. cambio de empresa seguido de activar Divisa Real,
    // arranco en el medio), esta promesa vieja NO debe pisar el cache -- se descarta
    // en silencio y devuelve su propio resultado sin contaminar el estado global.
    const cacheKeyDeEstaLlamada = cacheKey;
    const empresaParam = CURRENT_EMPRESA_ID ? `&empresa_id=${CURRENT_EMPRESA_ID}` : '';
    let result = null;
    if (!modoDivisaReal) {
      const r = await fetch(`/api/esf/completo?year=${year}&unit=${empresaParam}`);
      if (r.ok) {
        const data = await r.json();
        result = data.rows || null;
      }
    } else {
      for (const q of [4, 3, 2, 1]) {
        const r = await fetch(`/api/esf-divisa-real?year=${year}&quarter=${q}${empresaParam}`);
        if (r.ok) {
          const data = await r.json();
          result = (data.esf_completo && data.esf_completo.rows) || null;
          break;
        }
      }
    }
    if (_esfRowsCacheKey === cacheKeyDeEstaLlamada) {
      _esfRowsCache = result;
    }
    console.log('[FETCH-OUT]', performance.now().toFixed(1), 'modoAlEntrar=', modoAlEntrar, 'modoAlSalir=', modoDivisaReal);
    return result;
  })();

  return _esfRowsPromise;
}

// Devuelve el color plano para cada trimestre del array recibido. Antes atenuaba
// (opacidad reducida) los trimestres fuera del filtro dash-quarter activo, pero
// desde que el filtro de trimestre pasó de "atenuar" a "ocultar" (ago-2026), cada
// llamador ya filtra su array a 1 solo elemento antes de invocar esta funcion --
// la logica de atenuado nunca se ejecutaba (nunca habia mas de un elemento para
// comparar). Simplificada para reflejar el comportamiento real.
function dimPorTrimestre(colorHex, quartersConDatos) {
  return quartersConDatos.map(() => colorHex);
}

function loadEstructuraCapital() {
  const wActivo = window.DASHBOARD_CONFIG.find(w => w.id === 'wc-estcap' && w.visible);
  if (!wActivo) return;
  const year = G('dash-year').value;
  // ESF es siempre consolidado -- nunca se filtra por unidad de negocio, sin importar
  // el filtro de unidad del Dashboard (regla de negocio confirmada, ver ultrax_reglas.md).
  console.log('[loadEstructuraCapital-CALL]', performance.now().toFixed(1), 'modo=', modoDivisaReal);
  fetchESFRowsDashboard(year)
    .then(rows => {
      if (!rows) return;
      const findRow = (partida) => rows.find(r => r.partida === partida);
      const rActivos = findRow('TOTAL ACTIVOS');
      const rPasivos = findRow('TOTAL PASIVOS');
      const rPatrimonio = findRow('Total Patrimonio');
      if (!rActivos || !rPasivos || !rPatrimonio) return;

      const selectedQuarterEstcap = G('dash-quarter') ? G('dash-quarter').value : '';
      let quartersConDatos = [1,2,3,4].filter(q => (rActivos.quarters[q] || 0) !== 0);
      if (selectedQuarterEstcap) {
        quartersConDatos = quartersConDatos.filter(q => String(q) === selectedQuarterEstcap);
      }
      if (!quartersConDatos.length) return;

      const labels = quartersConDatos.map(q => 'Q'+q);
      const activoData = quartersConDatos.map(q => rActivos.quarters[q] || 0);
      const pasivoData = quartersConDatos.map(q => rPasivos.quarters[q] || 0);
      const patrimonioData = quartersConDatos.map(q => rPatrimonio.quarters[q] || 0);

      // Guardián visual: Activo debe ser igual a Pasivo + Patrimonio (tolerancia 1 unidad)
      const hayDescuadre = quartersConDatos.some((q, i) =>
        Math.abs(activoData[i] - (pasivoData[i] + patrimonioData[i])) > 1);
      const badge = G('estcap-badge');
      if (badge) badge.style.display = hayDescuadre ? 'inline-block' : 'none';

      const ctsel = document.getElementById('ct-ch-estcap');
      const modoPct = ctsel && ctsel.value === 'pct';

      let dsActivo, dsPasivo, dsPatrimonio;
      if (modoPct) {
        dsActivo = activoData.map(() => 100);
        dsPasivo = pasivoData.map((v,i) => activoData[i] ? (v/activoData[i]*100) : 0);
        dsPatrimonio = patrimonioData.map((v,i) => activoData[i] ? (v/activoData[i]*100) : 0);
      } else {
        dsActivo = activoData; dsPasivo = pasivoData; dsPatrimonio = patrimonioData;
      }

      const canvas = G('ch-estcap');
      if (!canvas) return;
      if (CH['ch-estcap']) CH['ch-estcap'].destroy();

      CH['ch-estcap'] = new Chart(canvas, {
        type: 'bar',
        data: {
          labels,
          datasets: [
            { label: 'Activo Total', _partidaReal: 'TOTAL ACTIVOS', data: dsActivo, backgroundColor: dimPorTrimestre('#2563eb', quartersConDatos), stack: 'activo' },
            { label: 'Pasivo', _partidaReal: 'TOTAL PASIVOS', data: dsPasivo, backgroundColor: dimPorTrimestre('#f97316', quartersConDatos), stack: 'pasivo-pat' },
            { label: 'Patrimonio', _partidaReal: 'Total Patrimonio', data: dsPatrimonio, backgroundColor: dimPorTrimestre('#0891b2', quartersConDatos), stack: 'pasivo-pat' }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          onClick: (e, els) => chartEstCapDetClick(e, els, quartersConDatos),
          scales: {
            x: { stacked: true },
            y: { stacked: true, ticks: { callback: v => modoPct ? v+'%' : fmtS(v) } }
          },
          datasets: { bar: { maxBarThickness: 40, categoryPercentage: 0.9, barPercentage: 0.95 } },
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) => `${ctx.dataset.label}: ${modoPct ? ctx.raw.toFixed(1)+'%' : fmtS(ctx.raw)}`
              }
            }
          }
        }
      });

      // Leyenda propia, lista agrupada con monto por trimestre visible y el
      // rotulo de trimestre (Q1/Q2/etc) en negrita -- mismo patron pedido por
      // Yocelin para Estructura de Capital Detallada, replicado aqui.
      const legendEl = G('estcap-legend');
      if (legendEl) {
        const series = [
          { nombre: 'Activo Total', color: '#2563eb', data: dsActivo },
          { nombre: 'Pasivo', color: '#f97316', data: dsPasivo },
          { nombre: 'Patrimonio', color: '#0891b2', data: dsPatrimonio }
        ];
        const filas = series.map(s => {
          const montos = modoPct ? '' : labels.map((lbl, i) => `<strong style="color:var(--tx)">${lbl}</strong> ${fmtS(s.data[i])}`).join(' &middot; ');
          return `<div style="margin-bottom:6px">
            <div style="display:flex;align-items:center;gap:6px;font-size:11px"><span style="width:9px;height:9px;background:${s.color};border-radius:2px;display:inline-block;flex-shrink:0"></span>${s.nombre}</div>
            ${montos ? `<div style="font-size:10px;color:var(--mu2);margin-left:15px">${montos}</div>` : ''}
          </div>`;
        }).join('');
        const valorPintado = `<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;justify-items:center;text-align:center">${filas}</div>`;
        console.log('[loadEstructuraCapital-PAINT]', performance.now().toFixed(1), 'modo=', modoDivisaReal, 'valorPintado=', valorPintado);
        legendEl.innerHTML = valorPintado;
      }
      scheduleMasonry();
    })
    .catch(err => console.error('Error cargando Estructura de Capital:', err));
}

function loadDeudaCobertura() {
  const wActivo = window.DASHBOARD_CONFIG.find(w => w.id === 'wc-deuda-cobertura' && w.visible);
  if (!wActivo) return;
  const year = G('dash-year').value;
  // ESF es siempre consolidado -- nunca se filtra por unidad de negocio, sin importar
  // el filtro de unidad del Dashboard (regla de negocio confirmada, ver ultrax_reglas.md).
  console.log('[loadDeudaCobertura-CALL]', performance.now().toFixed(1), 'modo=', modoDivisaReal);
  fetchESFRowsDashboard(year)
    .then(rows => {
      if (!rows) return;
      const findRow = (partida) => rows.find(r => r.partida === partida);
      const rPasivos = findRow('Total Pasivos Corrientes');
      const rEfectivo = findRow('Efectivo y Equivalentes');
      if (!rPasivos || !rEfectivo) return;

      const selectedQuarterDC = G('dash-quarter') ? G('dash-quarter').value : '';
      let quartersConDatos = [1,2,3,4].filter(q => (rPasivos.quarters[q] || 0) !== 0);
      if (selectedQuarterDC) {
        quartersConDatos = quartersConDatos.filter(q => String(q) === selectedQuarterDC);
      }
      if (!quartersConDatos.length) return;

      const labels = quartersConDatos.map(q => 'Q'+q);
      const deudaData = quartersConDatos.map(q => rPasivos.quarters[q] || 0);
      const efectivoData = quartersConDatos.map(q => rEfectivo.quarters[q] || 0);

      const canvas = G('ch-deuda-cobertura');
      if (!canvas) return;
      if (CH['ch-deuda-cobertura']) CH['ch-deuda-cobertura'].destroy();

      CH['ch-deuda-cobertura'] = new Chart(canvas, {
        type: 'bar',
        data: {
          labels,
          datasets: [
            { label: 'Deuda (Pasivo Corriente)', _partidaReal: 'Total Pasivos Corrientes', data: deudaData, backgroundColor: dimPorTrimestre('#f97316', quartersConDatos) },
            { label: 'Efectivo y Equivalentes', _partidaReal: 'Efectivo y Equivalentes', data: efectivoData, backgroundColor: dimPorTrimestre('#2563eb', quartersConDatos) }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          onClick: (e, els) => chartEstCapDetClick(e, els, quartersConDatos),
          scales: { y: { ticks: { callback: v => fmtS(v) } } },
          datasets: { bar: { maxBarThickness: 40, categoryPercentage: 0.9, barPercentage: 0.95 } },
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: { label: (ctx) => `${ctx.dataset.label}: ${fmtS(ctx.raw)}` }
            }
          }
        }
      });

      // Leyenda propia, 2 columnas simples, Q1/Q2 en negrita.
      const legendEl = G('deuda-cobertura-legend');
      if (legendEl) {
        const series = [
          { nombre: 'Deuda (Pasivo Corriente)', color: '#f97316', data: deudaData },
          { nombre: 'Efectivo y Equivalentes', color: '#2563eb', data: efectivoData }
        ];
        const filas = series.map(s => {
          const montos = labels.map((lbl, i) => `<strong style="color:var(--tx)">${lbl}</strong> ${fmtS(s.data[i])}`).join(' &middot; ');
          return `<div style="margin-bottom:6px">
            <div style="display:flex;align-items:center;gap:6px;font-size:11px"><span style="width:9px;height:9px;background:${s.color};border-radius:2px;display:inline-block;flex-shrink:0"></span>${s.nombre}</div>
            <div style="font-size:10px;color:var(--mu2);margin-left:15px">${montos}</div>
          </div>`;
        }).join('');
        const valorPintado = `<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;justify-items:center;text-align:center">${filas}</div>`;
        console.log('[loadDeudaCobertura-PAINT]', performance.now().toFixed(1), 'modo=', modoDivisaReal, 'valorPintado=', valorPintado);
        legendEl.innerHTML = valorPintado;
      }
      scheduleMasonry();
    })
    .catch(err => console.error('Error cargando Deuda y Cobertura:', err));
}

function loadEstructuraCapitalDetallada() {
  const wActivo = window.DASHBOARD_CONFIG.find(w => w.id === 'wc-estcapdet' && w.visible);
  if (!wActivo) return;
  const year = G('dash-year').value;
  console.log('[loadEstructuraCapitalDetallada-CALL]', performance.now().toFixed(1), 'modo=', modoDivisaReal);
  fetchESFRowsDashboard(year)
    .then(rows => {
      if (!rows) return;
      const totalRow = rows.find(r => r.partida === 'TOTAL ACTIVOS');
      const selectedQuarterDet = G('dash-quarter') ? G('dash-quarter').value : '';
      let quartersConDatos = [1,2,3,4].filter(q => totalRow && (totalRow.quarters[q] || 0) !== 0);
      if (selectedQuarterDet) {
        quartersConDatos = quartersConDatos.filter(q => String(q) === selectedQuarterDet);
      }
      if (!quartersConDatos.length) return;
      const labels = quartersConDatos.map(q => 'Q'+q);

      const activoPartidas = rows.filter(r => r.level === 2 && (r.parent_name === 'ACTIVOS CORRIENTES' || r.parent_name === 'ACTIVOS NO CORRIENTES'));
      const pasivoPartidas = rows.filter(r => r.level === 2 && (r.parent_name === 'PASIVOS CORRIENTES' || r.parent_name === 'PASIVOS NO CORRIENTES'));
      const patrimonioPartidas = rows.filter(r => r.level === 2 && r.parent_name === 'PATRIMONIO');

      const ctsel = document.getElementById('ct-ch-estcapdet');
      const modoPct = ctsel && ctsel.value === 'pct';

      // Paleta financiera sobria (opcion C, decidida con Andres esta sesion): azul
      // cielo/ambar/teal en vez de azul marino/naranja fuerte -- misma regla de
      // categoria (azul=Activo, naranja=Pasivo, teal=Patrimonio), tonos mas legibles.
      // Genera un degradado de N tonos a partir de un color base, mezclando
      // progresivamente hacia blanco -- el color base (idx=0) queda intacto,
      // los siguientes se aclaran en pasos iguales. Reemplaza las listas fijas
      // de hex anteriores, cuyo segundo tono era mas oscuro que el base
      // (rompia el criterio de "mas claro segun se aleja del base" pedido).
      function generarDegradado(colorBase, cantidad) {
        const hex = colorBase.replace('#', '');
        const r = parseInt(hex.substring(0, 2), 16);
        const g = parseInt(hex.substring(2, 4), 16);
        const b = parseInt(hex.substring(4, 6), 16);
        const tonos = [];
        for (let i = 0; i < cantidad; i++) {
          const t = i / (cantidad - 1); // 0 = color base, 1 = casi blanco
          const mezclaHacia = (canal) => Math.round(canal + (255 - canal) * t * 0.85);
          const rr = mezclaHacia(r).toString(16).padStart(2, '0');
          const gg = mezclaHacia(g).toString(16).padStart(2, '0');
          const bb = mezclaHacia(b).toString(16).padStart(2, '0');
          tonos.push('#' + rr + gg + bb);
        }
        return tonos;
      }
      const paletaAzules = generarDegradado('#2563eb', 5);
      const paletaNaranjas = generarDegradado('#f97316', 5);
      const paletaTeals = generarDegradado('#0891b2', 5);
      const MAX_PARTIDAS = 4;

      function prepararItems(partidasRaw) {
        const conPromedio = partidasRaw.map(r => {
          const vals = quartersConDatos.map(q => r.quarters[q] || 0);
          const prom = vals.reduce((a,b)=>a+b,0) / (vals.length || 1);
          return { r, vals, prom };
        }).filter(x => x.vals.some(v => v !== 0));
        conPromedio.sort((a,b) => b.prom - a.prom);
        const principales = conPromedio.slice(0, MAX_PARTIDAS);
        const resto = conPromedio.slice(MAX_PARTIDAS);
        const items = [...principales];
        if (resto.length) {
          const valsOtros = quartersConDatos.map((q,i) => resto.reduce((acc,x) => acc + x.vals[i], 0));
          items.push({ r: { partida: `Otros (${resto.length})` }, vals: valsOtros });
        }
        return items;
      }

      const itemsActivo = prepararItems(activoPartidas);
      const itemsPasivo = prepararItems(pasivoPartidas);
      const itemsPatrimonio = prepararItems(patrimonioPartidas);

      const totalActivoQ = quartersConDatos.map((q,i) => itemsActivo.reduce((a,x) => a + x.vals[i], 0));
      const totalPasPatQ = quartersConDatos.map((q,i) =>
        itemsPasivo.reduce((a,x) => a + x.vals[i], 0) + itemsPatrimonio.reduce((a,x) => a + x.vals[i], 0));

      function armarDataset(items, paleta, stackId, totales) {
        return items.map((x, idx) => ({
          label: x.r.partida,
          data: modoPct ? x.vals.map((v,i) => totales[i] ? (v/totales[i]*100) : 0) : x.vals,
          backgroundColor: dimPorTrimestre(paleta[idx % paleta.length], quartersConDatos),
          stack: stackId
        }));
      }

      const datasets = [
        ...armarDataset(itemsActivo, paletaAzules, 'activo', totalActivoQ),
        ...armarDataset(itemsPasivo, paletaNaranjas, 'pasivo-pat', totalPasPatQ),
        ...armarDataset(itemsPatrimonio, paletaTeals, 'pasivo-pat', totalPasPatQ)
      ];

      const canvas = G('ch-estcapdet');
      if (!canvas) return;
      if (CH['ch-estcapdet']) CH['ch-estcapdet'].destroy();

      CH['ch-estcapdet'] = new Chart(canvas, {
        type: 'bar',
        data: { labels, datasets },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          onClick: (e, els) => chartEstCapDetClick(e, els, quartersConDatos),
          scales: {
            x: { stacked: true },
            y: { stacked: true, ticks: { callback: v => modoPct ? v+'%' : fmtS(v) } }
          },
          datasets: { bar: { maxBarThickness: 40, categoryPercentage: 0.9, barPercentage: 0.95 } },
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) => `${ctx.dataset.label}: ${modoPct ? ctx.raw.toFixed(1)+'%' : fmtS(ctx.raw)}`
              }
            }
          }
        }
      });

      // Leyenda propia, agrupada por categoria (Activo/Pasivo/Patrimonio), con monto
      // por cada trimestre visible -- Chart.js no arma esto solo. Regla decidida esta
      // sesion: ninguna leyenda del Dashboard muestra "solo el ultimo trimestre".
      function renderGrupo(titulo, colorTitulo, items, paleta) {
        const filas = items.map((x, idx) => {
          const color = paleta[idx % paleta.length];
          const montos = modoPct ? '' : quartersConDatos.map((q,i) => `<strong style="color:var(--tx)">${labels[i]}</strong> ${fmtS(x.vals[i])}`).join(' &middot; ');
          return `<div style="margin-bottom:6px">
            <div style="display:flex;align-items:center;gap:6px;font-size:11px"><span style="width:9px;height:9px;background:${color};border-radius:2px;display:inline-block;flex-shrink:0"></span>${x.r.partida}</div>
            ${montos ? `<div style="font-size:10px;color:var(--mu2);margin-left:15px">${montos}</div>` : ''}
          </div>`;
        }).join('');
        return `<div><p style="margin:0 0 6px;font-weight:700;color:${colorTitulo};font-size:11px">${titulo}</p>${filas}</div>`;
      }

      const legendEl = G('estcapdet-legend');
      if (legendEl) {
        const valorPintado = `<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;justify-items:center;text-align:center">
          ${renderGrupo('Activo', '#2563eb', itemsActivo, paletaAzules)}
          ${renderGrupo('Pasivo', '#f97316', itemsPasivo, paletaNaranjas)}
          ${renderGrupo('Patrimonio', '#0891b2', itemsPatrimonio, paletaTeals)}
        </div>`;
        console.log('[loadEstructuraCapitalDetallada-PAINT]', performance.now().toFixed(1), 'modo=', modoDivisaReal, 'valorPintado=', valorPintado);
        legendEl.innerHTML = valorPintado;
      }
      scheduleMasonry();
    })
    .catch(err => console.error('Error cargando Estructura de Capital Detallada:', err));
}

function loadSituacionFinanciera() {
  const wActivo = window.DASHBOARD_CONFIG.find(w => w.id === 'wc-sitfin' && w.visible);
  if (!wActivo) return;
  const year = G('dash-year').value;
  console.log('[loadSituacionFinanciera-CALL]', performance.now().toFixed(1), 'modo=', modoDivisaReal);
  fetchESFRowsDashboard(year)
    .then(rows => {
      if (!rows) return;
      const find = (p) => rows.find(r => r.partida === p);
      const rAC = find('Total Activos Corrientes');
      const rANC = find('Total Activos No Corrientes');
      const rPC = find('Total Pasivos Corrientes');
      const rPNC = find('Total Pasivos No Corrientes');
      if (!rAC || !rANC || !rPC || !rPNC) return;

      const selectedQuarterSF = G('dash-quarter') ? G('dash-quarter').value : '';
      let quartersConDatos = [1,2,3,4].filter(q => (rAC.quarters[q] || 0) !== 0);
      if (selectedQuarterSF) {
        quartersConDatos = quartersConDatos.filter(q => String(q) === selectedQuarterSF);
      }
      if (!quartersConDatos.length) return;
      const labels = quartersConDatos.map(q => 'Q'+q);

      const dsAC  = quartersConDatos.map(q => rAC.quarters[q] || 0);
      const dsANC = quartersConDatos.map(q => rANC.quarters[q] || 0);
      const dsPC  = quartersConDatos.map(q => rPC.quarters[q] || 0);
      const dsPNC = quartersConDatos.map(q => rPNC.quarters[q] || 0);

      const canvas = G('ch-sitfin');
      if (!canvas) return;
      if (CH['ch-sitfin']) CH['ch-sitfin'].destroy();

      CH['ch-sitfin'] = new Chart(canvas, {
        type: 'bar',
        data: {
          labels,
          datasets: [
            { label: 'Activo Corriente', _partidaReal: 'Total Activos Corrientes', data: dsAC, backgroundColor: dimPorTrimestre('#2563eb', quartersConDatos), stack: 'activo' },
            { label: 'Activo No Corriente', _partidaReal: 'Total Activos No Corrientes', data: dsANC, backgroundColor: dimPorTrimestre('#7dd3fc', quartersConDatos), stack: 'activo' },
            { label: 'Pasivo Corriente', _partidaReal: 'Total Pasivos Corrientes', data: dsPC, backgroundColor: dimPorTrimestre('#f97316', quartersConDatos), stack: 'pasivo' },
            { label: 'Pasivo No Corriente', _partidaReal: 'Total Pasivos No Corrientes', data: dsPNC, backgroundColor: dimPorTrimestre('#fb923c', quartersConDatos), stack: 'pasivo' }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          onClick: (e, els) => chartEstCapDetClick(e, els, quartersConDatos),
          scales: {
            x: { stacked: true },
            y: { stacked: true, ticks: { callback: v => fmtS(v) } }
          },
          datasets: { bar: { maxBarThickness: 40, categoryPercentage: 0.9, barPercentage: 0.95 } },
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) => `${ctx.dataset.label}: ${fmtS(ctx.raw)}`
              }
            }
          }
        }
      });

      // Leyenda propia agrupada por categoria (Activo/Pasivo), Q1/Q2 en negrita.
      const legendEl = G('sitfin-legend');
      if (legendEl) {
        function renderGrupo(titulo, colorTitulo, series) {
          const filas = series.map(s => {
            const montos = labels.map((lbl, i) => `<strong style="color:var(--tx)">${lbl}</strong> ${fmtS(s.data[i])}`).join(' &middot; ');
            return `<div style="margin-bottom:6px">
              <div style="display:flex;align-items:center;gap:6px;font-size:11px"><span style="width:9px;height:9px;background:${s.color};border-radius:2px;display:inline-block;flex-shrink:0"></span>${s.nombre}</div>
              <div style="font-size:10px;color:var(--mu2);margin-left:15px">${montos}</div>
            </div>`;
          }).join('');
          return `<div><p style="margin:0 0 6px;font-weight:700;color:${colorTitulo};font-size:11px">${titulo}</p>${filas}</div>`;
        }
        const valorPintado = `<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;justify-items:center;text-align:center">
          ${renderGrupo('Activo', '#2563eb', [
            { nombre: 'Activo Corriente', color: '#2563eb', data: dsAC },
            { nombre: 'Activo No Corriente', color: '#7dd3fc', data: dsANC }
          ])}
          ${renderGrupo('Pasivo', '#f97316', [
            { nombre: 'Pasivo Corriente', color: '#f97316', data: dsPC },
            { nombre: 'Pasivo No Corriente', color: '#fb923c', data: dsPNC }
          ])}
        </div>`;
        console.log('[loadSituacionFinanciera-PAINT]', performance.now().toFixed(1), 'modo=', modoDivisaReal, 'valorPintado=', valorPintado);
        legendEl.innerHTML = valorPintado;
      }
      scheduleMasonry();
    })
    .catch(err => console.error('Error cargando Situacion Financiera:', err));
}

function loadPeriodoCobro() {
  const w = window.DASHBOARD_CONFIG.find(x => x.id === 'wc-periodo-cobro' && x.visible);
  if (!w) return;
  const year = G('dash-year').value;
  const empresaParam = CURRENT_EMPRESA_ID ? `&empresa_id=${CURRENT_EMPRESA_ID}` : '';
  fetch(`${modoDivisaReal ? '/api/indicadores/divisa_real' : '/api/indicadores'}?year=${year}${empresaParam}`)
    .then(r => r.ok ? r.json() : null)
    .then(data => {
      if (!data) return;
      const inds = data.indicadores || [];
      const ind = inds.find(x => x.nombre === 'Período de cobro (30 a 60 días max)');
      if (!ind) return;
      const trimestres = ind.trimestres || [];
      const selectedQuarterPC = G('dash-quarter') ? G('dash-quarter').value : '';
      let idxConDatos = [0, 1, 2, 3].filter(i => trimestres[i] && trimestres[i].valor !== null);
      if (selectedQuarterPC) {
        idxConDatos = idxConDatos.filter(i => String(i + 1) === selectedQuarterPC);
      }
      if (!idxConDatos.length) return;
      const labels = idxConDatos.map(i => 'Q' + (i + 1));
      const dsExt = idxConDatos.map(i => trimestres[i].dias_cliente_externo || 0);
      const dsGrp = idxConDatos.map(i => trimestres[i].dias_empresas_grupo || 0);

      const canvas = G('ch-periodo-cobro');
      if (!canvas) return;
      if (CH['ch-periodo-cobro']) CH['ch-periodo-cobro'].destroy();
      CH['ch-periodo-cobro'] = new Chart(canvas, {
        type: 'bar',
        data: {
          labels,
          datasets: [
            { label: 'Clientes Externo', data: dsExt, backgroundColor: dimPorTrimestre('#f97316', idxConDatos.map(i => i+1)), stack: 'pc' },
            { label: 'Empresas del Grupo', data: dsGrp, backgroundColor: dimPorTrimestre('#059669', idxConDatos.map(i => i+1)), stack: 'pc' }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: { x: { stacked: true }, y: { stacked: true, ticks: { callback: v => v.toFixed(1) } } },
          datasets: { bar: { maxBarThickness: 40, categoryPercentage: 0.9, barPercentage: 0.95 } },
          plugins: {
            legend: { display: false },
            tooltip: { callbacks: { label: (ctx) => `${ctx.dataset.label}: ${ctx.raw.toFixed(1)} días` } }
          }
        }
      });

      const legendEl = G('periodo-cobro-legend');
      if (legendEl) {
        const montosExt = labels.map((lbl, i) => `<strong style="color:var(--tx)">${lbl}</strong> ${dsExt[i].toFixed(1)}`).join(' &middot; ');
        const montosGrp = labels.map((lbl, i) => `<strong style="color:var(--tx)">${lbl}</strong> ${dsGrp[i].toFixed(1)}`).join(' &middot; ');
        legendEl.innerHTML = `<div style="display:flex;flex-direction:column;gap:6px;align-items:center;text-align:center">
          <div><div style="display:flex;align-items:center;justify-content:center;gap:6px;font-size:11px"><span style="width:9px;height:9px;background:#f97316;border-radius:2px;display:inline-block;flex-shrink:0"></span>Clientes Externo</div>
          <div style="font-size:10px;color:var(--mu2);margin-top:4px">${montosExt}</div></div>
          <div><div style="display:flex;align-items:center;justify-content:center;gap:6px;font-size:11px"><span style="width:9px;height:9px;background:#059669;border-radius:2px;display:inline-block;flex-shrink:0"></span>Empresas del Grupo</div>
          <div style="font-size:10px;color:var(--mu2);margin-top:4px">${montosGrp}</div></div>
        </div>`;
      }
      scheduleMasonry();
    })
    .catch(err => console.error('Error cargando Período de Cobro:', err));
}

function crearGauge(canvasId, valorPct, colorFill) {
  const canvas = G(canvasId);
  if (!canvas) return;
  if (CH[canvasId]) CH[canvasId].destroy();
  const pct = Math.max(0, Math.min(100, valorPct));
  CH[canvasId] = new Chart(canvas, {
    type: 'doughnut',
    data: { datasets: [{ data: [pct, 100 - pct], backgroundColor: [colorFill, '#e5e7eb'], borderWidth: 0 }] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      rotation: -90,
      circumference: 180,
      cutout: '75%',
      plugins: { legend: { display: false }, tooltip: { enabled: false } }
    }
  });
}

function loadROEROA() {
  const wRoe = window.DASHBOARD_CONFIG.find(w => w.id === 'wc-roe' && w.visible);
  const wRoa = window.DASHBOARD_CONFIG.find(w => w.id === 'wc-roa' && w.visible);
  if (!wRoe && !wRoa) return;
  const year = G('dash-year').value;
  const empresaParam = CURRENT_EMPRESA_ID ? `&empresa_id=${CURRENT_EMPRESA_ID}` : '';
  fetch(`${modoDivisaReal ? '/api/indicadores/divisa_real' : '/api/indicadores'}?year=${year}${empresaParam}`)
    .then(r => r.ok ? r.json() : null)
    .then(data => {
      if (!data) return;
      const inds = data.indicadores || [];

      function renderInd(id, gaugeCanvasId, gaugeNumId, barCanvasId, color) {
        const w = window.DASHBOARD_CONFIG.find(x => x.id === 'wc-' + id && x.visible);
        if (!w) return;
        const ind = inds.find(x => x.nombre && x.nombre.toLowerCase().startsWith(id.toLowerCase()));
        if (!ind) return;
        const trimestres = ind.trimestres || [];
        const selectedQuarterRoe = G('dash-quarter') ? G('dash-quarter').value : '';
        let idxConDatos = [0, 1, 2, 3].filter(i => trimestres[i] && trimestres[i].valor !== null);
        if (selectedQuarterRoe) {
          idxConDatos = idxConDatos.filter(i => String(i + 1) === selectedQuarterRoe);
        }
        if (!idxConDatos.length) return;
        const labels = idxConDatos.map(i => 'Q' + (i + 1));
        const valores = idxConDatos.map(i => (trimestres[i].valor || 0) * 100);
        // El gauge muestra el acumulado real "Año Actual" (utilidad acumulada /
        // promedio del periodo completo), no el ultimo trimestre -- activado en
        // el backend esta misma sesion (engine.py, hay_esf_prev). Si no hay
        // acumulado disponible (ej. un solo trimestre sin fallback valido),
        // usar el ultimo trimestre como estaba antes.
        const ultimoVal = (ind.anio_actual != null) ? ind.anio_actual * 100 : valores[valores.length - 1];

        crearGauge(gaugeCanvasId, ultimoVal, color);
        const numEl = G(gaugeNumId);
        if (numEl) numEl.textContent = ultimoVal.toFixed(1) + '%';

        const canvas = G(barCanvasId);
        if (!canvas) return;
        if (CH[barCanvasId]) CH[barCanvasId].destroy();
        CH[barCanvasId] = new Chart(canvas, {
          type: 'bar',
          data: { labels, datasets: [{ label: ind.nombre, data: valores, backgroundColor: dimPorTrimestre(color, idxConDatos.map(i => i + 1)) }] },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { ticks: { callback: v => v.toFixed(0) + '%' } } },
            datasets: { bar: { maxBarThickness: 40, categoryPercentage: 0.9, barPercentage: 0.95 } },
            plugins: {
              legend: { display: false },
              tooltip: { callbacks: { label: (ctx) => `${ctx.dataset.label}: ${ctx.raw.toFixed(1)}%` } }
            }
          }
        });

        // Leyenda propia, 1 columna simple, Q1/Q2 en negrita.
        const legendEl = G(id + '-legend');
        if (legendEl) {
          const montos = labels.map((lbl, i) => `<strong style="color:var(--tx)">${lbl}</strong> ${valores[i].toFixed(1)}%`).join(' &middot; ');
          legendEl.innerHTML = `<div style="text-align:center">
            <div style="display:flex;align-items:center;justify-content:center;gap:6px;font-size:11px"><span style="width:9px;height:9px;background:${color};border-radius:2px;display:inline-block;flex-shrink:0"></span>${id.toUpperCase()}</div>
            <div style="font-size:10px;color:var(--mu2);margin-top:4px">${montos}</div>
          </div>`;
        }
      }

      renderInd('roe', 'ch-roe-gauge', 'roe-gauge-num', 'ch-roe-bar', '#059669');
      renderInd('roa', 'ch-roa-gauge', 'roa-gauge-num', 'ch-roa-bar', '#0891b2');
      scheduleMasonry();
    })
    .catch(err => console.error('Error cargando ROE/ROA:', err));
}

function loadIngresosCostosMargen() {
  const wActivo = window.DASHBOARD_CONFIG.find(w => w.id === 'wc-margen' && w.visible);
  if (!wActivo || !DD || !DD.months) return;

  const meses = DD.months;
  const QUARTER_MONTHS_MARGEN = {1:['ENE','FEB','MAR'],2:['ABR','MAY','JUN'],3:['JUL','AGO','SEPT'],4:['OCT','NOV','DIC']};
  const selectedMonth = G('dash-month') && G('dash-month').value;
  const selectedQuarter = G('dash-quarter') && G('dash-quarter').value;
  let conDatos;
  if (DD._modo_divisa) {
    // Divisa Real: DD.months ya viene agrupado por trimestre ('Q1','Q2'...), no
    // por mes -- QUARTER_MONTHS_MARGEN asume nombres de mes reales, no aplica aqui.
    const mesesDR = selectedQuarter ? meses.filter(mm => mm.month === 'Q' + selectedQuarter) : meses;
    conDatos = mesesDR.map(mm => ({ label: mm.month, meses: [mm] }));
  } else if (selectedMonth) {
    const m = meses.find(mm => mm.month === selectedMonth);
    conDatos = m ? [{ label: selectedMonth, meses: [m] }] : [];
  } else if (selectedQuarter) {
    const mesesQ = meses.filter(mm => QUARTER_MONTHS_MARGEN[selectedQuarter].includes(mm.month));
    conDatos = mesesQ.length ? [{ label: 'Q' + selectedQuarter, meses: mesesQ }] : [];
  } else {
    conDatos = [1,2,3,4].map(q => ({ label: 'Q' + q, meses: meses.filter(mm => QUARTER_MONTHS_MARGEN[q].includes(mm.month)) })).filter(t => t.meses.some(m => (m.ingresos || 0) !== 0));
  }
  if (!conDatos.length) return;

  const labels = conDatos.map(t => t.label);
  const dsIngresos = conDatos.map(t => t.meses.reduce((a,m) => a + (m.ingresos || 0), 0));
  const dsCostos   = conDatos.map(t => t.meses.reduce((a,m) => a + (m.costos || 0), 0));
  const dsUtilidad = conDatos.map(t => t.meses.reduce((a,m) => a + (m.utilidad_bruta || 0), 0));
  const dsMargen   = dsIngresos.map((ing, i) => ing ? (dsUtilidad[i] / ing * 100) : 0);

  const canvas = G('ch-margen');
  if (!canvas) return;
  if (CH['ch-margen']) CH['ch-margen'].destroy();

  CH['ch-margen'] = new Chart(canvas, {
    data: {
      labels,
      datasets: [
        { type: 'bar', label: 'Ingresos', data: dsIngresos, backgroundColor: '#2563eb', yAxisID: 'y', order: 2 },
        { type: 'bar', label: 'Costos', data: dsCostos, backgroundColor: '#d97706', yAxisID: 'y', order: 2 },
        { type: 'bar', label: 'Utilidad Bruta', data: dsUtilidad, backgroundColor: '#059669', yAxisID: 'y', order: 2 },
        { type: 'line', label: 'Margen Bruto %', data: dsMargen, borderColor: '#7c3aed', backgroundColor: '#7c3aed', yAxisID: 'y1', order: 1, tension: 0.3 }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      datasets: { bar: { maxBarThickness: 40, categoryPercentage: 0.9, barPercentage: 0.95 } },
      scales: {
        y: { type: 'linear', position: 'left', ticks: { callback: v => fmtS(v) } },
        y1: { type: 'linear', position: 'right', min: 0, max: 100, grid: { drawOnChartArea: false }, ticks: { callback: v => v.toFixed(0)+'%' } }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ctx.dataset.type === 'line'
              ? `${ctx.dataset.label}: ${ctx.raw.toFixed(1)}%`
              : `${ctx.dataset.label}: ${fmtS(ctx.raw)}`
          }
        }
      }
    }
  });

  // Leyenda propia, 4 filas (3 barras + 1 linea), Q1/Q2 en negrita, formato
  // segun tipo de serie (monto o %).
  const legendEl = G('margen-legend');
  if (legendEl) {
    const series = [
      { nombre: 'Ingresos', color: '#2563eb', data: dsIngresos, esPct: false },
      { nombre: 'Costos', color: '#d97706', data: dsCostos, esPct: false },
      { nombre: 'Utilidad Bruta', color: '#059669', data: dsUtilidad, esPct: false },
      { nombre: 'Margen Bruto %', color: '#7c3aed', data: dsMargen, esPct: true }
    ];
    const filas = series.map(s => {
      const montos = labels.map((lbl, i) => `<strong style="color:var(--tx)">${lbl}</strong> ${s.esPct ? s.data[i].toFixed(1)+'%' : fmtS(s.data[i])}`).join(' &middot; ');
      return `<div style="margin-bottom:6px">
        <div style="display:flex;align-items:center;gap:6px;font-size:11px"><span style="width:9px;height:9px;background:${s.color};border-radius:2px;display:inline-block;flex-shrink:0"></span>${s.nombre}</div>
        <div style="font-size:10px;color:var(--mu2);margin-left:15px">${montos}</div>
      </div>`;
    }).join('');
    legendEl.innerHTML = `<div style="display:flex;justify-content:center"><div style="display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:12px;justify-items:start;text-align:left">${filas}</div></div>`;
  }
}

function loadCascadaPL() {
  const wActivo = window.DASHBOARD_CONFIG.find(w => w.id === 'wc-cascada' && w.visible);
  if (!wActivo || !DD || !DD.totals) return;

  const t = DD.totals;
  const gastosOperativosPuros = t.gastos - (t.otros_gastos_no_operacionales || 0);

  // Solo Ingresos (primero) y Utilidad Neta (ultimo) tocan el piso desde 0.
  // Utilidad Bruta es un subtotal intermedio -- ya no toca el piso, se dibuja
  // como un marcador fino flotando en su nivel real (no es un delta real, el
  // acumulado no cambia en ese paso, por eso no puede ser tipo 'delta' comun).
  const pasos = [
    { label: 'Ingresos', labelEje: 'Ingresos', valor: t.ingresos, tipo: 'total' },
    { label: 'Costo de Ventas', labelEje: ['Costo de', 'Ventas'], valor: -t.costos, tipo: 'delta' },
    { label: 'Utilidad Bruta', labelEje: ['Utilidad', 'Bruta'], valor: t.utilidad_bruta, tipo: 'marcador' },
    { label: 'Gastos', labelEje: 'Gastos', valor: -gastosOperativosPuros, tipo: 'delta' },
    { label: 'Otros Ingresos No Operativos', labelEje: ['Otros Ingresos', 'No Operativos'], valor: t.otros_ingresos_no_operacionales || 0, tipo: 'delta' },
    { label: 'Otros Gastos No Operativos', labelEje: ['Otros Gastos', 'No Operativos'], valor: -(t.otros_gastos_no_operacionales || 0), tipo: 'delta' },
    { label: 'Utilidad Neta', labelEje: ['Utilidad', 'Neta'], valor: t.utilidad_neta, tipo: 'total' }
  ];

  let acumulado = 0;
  const labels = [];
  const base = [];
  const valores = [];
  const colores = [];
  const MARCADOR_ALTO = Math.max(t.ingresos || 0, t.utilidad_neta || 0) * 0.015;

  pasos.forEach(p => {
    labels.push(p.labelEje);
    if (p.tipo === 'total') {
      base.push(0);
      valores.push(p.valor);
      colores.push('#2563eb');
      acumulado = p.valor;
    } else if (p.tipo === 'marcador') {
      base.push(Math.max(0, acumulado - MARCADOR_ALTO / 2));
      valores.push(MARCADOR_ALTO);
      colores.push('#2563eb');
    } else {
      const antes = acumulado;
      const despues = acumulado + p.valor;
      base.push(Math.min(antes, despues));
      valores.push(Math.abs(p.valor));
      colores.push(p.valor >= 0 ? '#059669' : '#dc2626');
      acumulado = despues;
    }
  });

  const canvas = G('ch-cascada');
  if (!canvas) return;
  if (CH['ch-cascada']) CH['ch-cascada'].destroy();

  // Etiquetas de valor debajo de cada barra -- se posicionan en la coordenada de pixel
  // exacta que Chart.js calculo para cada barra (getPixelForTick), no con anchos de grid
  // adivinados. Se dibujan en animation.onComplete porque el layout final del eje X
  // (y por tanto la posicion real de cada barra) recien esta disponible ahi, no
  // inmediatamente despues de "new Chart(...)".
  CH['ch-cascada'] = new Chart(canvas, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: 'base', data: base, backgroundColor: 'transparent', stack: 's' },
        { label: 'valor', data: valores, backgroundColor: colores, stack: 's' }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      datasets: { bar: { maxBarThickness: 40, categoryPercentage: 0.9, barPercentage: 0.95 } },
      scales: {
        x: { stacked: true, ticks: { font: { size: 9 } } },
        y: { stacked: true, ticks: { callback: v => fmtS(v) } }
      },
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                title: (items) => pasos[items[0].dataIndex].label,
                label: (ctx) => {
                  if (ctx.dataset.label === 'base') return null;
                  const p = pasos[ctx.dataIndex];
                  return fmtS(p.valor);
                }
              }
            },
            datalabels: false
          }
    }
  });

  // Leyenda propia, una fila por paso (sin trimestres, es un snapshot unico).
  const legendEl = G('cascada-legend');
  if (legendEl) {
    const filas = pasos.map(p => {
      const color = p.tipo === 'total' ? '#2563eb' : (p.valor >= 0 ? '#059669' : '#dc2626');
      return `<div style="display:flex;align-items:center;gap:6px;font-size:11px;margin-bottom:4px"><span style="width:9px;height:9px;background:${color};border-radius:2px;display:inline-block;flex-shrink:0"></span>${p.label}: <span style="color:var(--mu2)">${fmtS(p.valor)}</span></div>`;
    }).join('');
    legendEl.innerHTML = `<div style="display:flex;justify-content:center"><div style="display:grid;grid-template-columns:repeat(4,auto);gap:6px 16px">${filas}</div></div>`;
  }
}

function loadHeatmapUtilidadUnidad() {
  const wActivo = window.DASHBOARD_CONFIG.find(w => w.id === 'wc-heatmap-un' && w.visible);
  if (!wActivo) return;
  const canvas = G('ch-heatmap-un');
  const emptyMsg = G('heatmap-un-empty');
  if (!canvas) return;

  function colorPara(v, maxPos, maxNegAbs) {
    if (v >= 0) {
      const t = maxPos ? Math.min(v / maxPos, 1) : 0;
      const l = 55 - t * 25;
      return 'hsl(158, 60%, ' + l + '%)';
    } else {
      const t = maxNegAbs ? Math.min(Math.abs(v) / maxNegAbs, 1) : 0;
      const l = 55 - t * 25;
      return 'hsl(0, 65%, ' + l + '%)';
    }
  }

  function pintarGrafico(items, etiquetaVacia) {
    if (!items.length) {
      canvas.style.display = 'none';
      if (emptyMsg) { emptyMsg.style.display = 'block'; emptyMsg.textContent = etiquetaVacia; }
      if (CH['ch-heatmap-un']) { CH['ch-heatmap-un'].destroy(); CH['ch-heatmap-un'] = null; }
      return;
    }
    canvas.style.display = 'block';
    if (emptyMsg) emptyMsg.style.display = 'none';

    const ordenados = items.slice().sort(function(a, b) { return b.utilidad_neta - a.utilidad_neta; });
    const valores = ordenados.map(function(x) { return x.utilidad_neta; });
    const maxPos = Math.max.apply(null, [0].concat(valores));
    const maxNegAbs = Math.abs(Math.min.apply(null, [0].concat(valores)));
    const labels = ordenados.map(function(x) { return x.nombre; });
    const colores = ordenados.map(function(x) { return colorPara(x.utilidad_neta, maxPos, maxNegAbs); });

    if (CH['ch-heatmap-un']) CH['ch-heatmap-un'].destroy();
    CH['ch-heatmap-un'] = new Chart(canvas, {
      type: 'bar',
      data: {
        labels,
        datasets: [{ label: 'Utilidad Neta', data: valores, backgroundColor: colores }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        datasets: { bar: { maxBarThickness: 40, categoryPercentage: 0.9, barPercentage: 0.95 } },
        scales: {
          x: { grid: { display: false } },
          y: {
            ticks: { callback: v => fmtS(v) },
            grid: {
              color: (ctx) => ctx.tick.value === 0 ? 'rgba(15,23,42,0.5)' : 'rgba(15,23,42,0.08)',
              lineWidth: (ctx) => ctx.tick.value === 0 ? 2 : 1
            }
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => fmtS(ctx.raw)
            }
          }
        }
      }
    });

    const legendEl = G('heatmap-un-legend');
    if (legendEl) {
      const filas = labels.map((lbl, i) => {
        return `<div style="display:flex;align-items:center;gap:6px;font-size:11px;margin-bottom:4px"><span style="width:9px;height:9px;background:${colores[i]};border-radius:2px;display:inline-block;flex-shrink:0"></span>${lbl}: <span style="color:var(--mu2)">${fmtS(valores[i])}</span></div>`;
      }).join('');
      legendEl.innerHTML = `<div style="display:flex;justify-content:center"><div>${filas}</div></div>`;
    }
  }

  const unidades = (DD && DD.por_unidad) || [];
  if (unidades.length) {
    const titulo = G('heatmap-un-titulo');
    if (titulo) titulo.textContent = 'Utilidad Neta por Unidad de Negocio';
    pintarGrafico(unidades.map(function(u) { return { nombre: u.unit, utilidad_neta: u.utilidad_neta }; }), '');
    return;
  }

  const empresas = (DD && DD.por_empresa) || [];
  const titulo2 = G('heatmap-un-titulo');
  if (titulo2) titulo2.textContent = 'Utilidad Neta por Empresa';
  pintarGrafico(
    empresas.map(function(e) { return { nombre: e.empresa, utilidad_neta: e.utilidad_neta }; }),
    'Sin datos suficientes todavia para mostrar Utilidad Neta por empresa.'
  );
}

function loadDonaUnidad() {
  const wActivo = window.DASHBOARD_CONFIG.find(w => w.id === 'wc-dona-unidad' && w.visible);
  if (!wActivo) return;
  const canvas = G('ch-dona-unidad');
  const emptyMsg = G('ch-dona-unidad-empty');
  if (!canvas) return;

  const unidades = (DD && DD.por_unidad) || [];
  const empresas = (DD && DD.por_empresa) || [];
  let items, tituloSufijo;
  if (unidades.length) {
    items = unidades.map(function(u) { return { nombre: u.unit, valor: u.ingresos }; });
    tituloSufijo = 'Unidad de Negocio';
  } else if (empresas.length) {
    items = empresas.map(function(e) { return { nombre: e.empresa, valor: e.ingresos }; });
    tituloSufijo = 'Empresa (Holding)';
  } else {
    items = [];
    tituloSufijo = 'Unidad de Negocio';
  }

  const tituloEl = canvas.closest('.wcard').querySelector('.ct');
  if (tituloEl) tituloEl.textContent = 'Ingresos por ' + tituloSufijo;

  if (!items.length) {
    canvas.style.display = 'none';
    if (emptyMsg) emptyMsg.style.display = 'block';
    if (CH['ch-dona-unidad']) { CH['ch-dona-unidad'].destroy(); CH['ch-dona-unidad'] = null; }
    return;
  }
  canvas.style.display = 'block';
  if (emptyMsg) emptyMsg.style.display = 'none';
  if (CH['ch-dona-unidad']) CH['ch-dona-unidad'].destroy();
  const paleta = ['#2563eb','#059669','#d97706','#dc2626','#7c3aed','#0891b2'];
  CH['ch-dona-unidad'] = new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels: items.map(function(x) { return x.nombre; }),
      datasets: [{ data: items.map(function(x) { return x.valor; }), backgroundColor: paleta }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: function(ctx) {
          const total = ctx.dataset.data.reduce(function(a,b){return a+b;},0);
          const pct = total ? (ctx.raw/total*100).toFixed(1) : 0;
          return ctx.label + ': ' + fmtS(ctx.raw) + ' (' + pct + '%)';
        } } }
      }
    }
  });

  const legendEl = G('dona-unidad-legend');
  if (legendEl) {
    const total = items.reduce((a,x) => a + x.valor, 0);
    const filas = items.map((x, i) => {
      const pct = total ? (x.valor/total*100).toFixed(1) : 0;
      return `<div style="display:flex;align-items:center;gap:6px;font-size:11px;margin-bottom:4px"><span style="width:9px;height:9px;background:${paleta[i % paleta.length]};border-radius:2px;display:inline-block;flex-shrink:0"></span>${x.nombre}: <span style="color:var(--mu2)">${fmtS(x.valor)} (${pct}%)</span></div>`;
    }).join('');
    legendEl.innerHTML = `<div style="display:flex;justify-content:center"><div>${filas}</div></div>`;
  }
}

function loadDonaSegmento() {
  const wActivo = window.DASHBOARD_CONFIG.find(w => w.id === 'wc-dona-segmento' && w.visible);
  const limpiarSiExiste = function() {
    if (CH['ch-dona-segmento']) { CH['ch-dona-segmento'].destroy(); CH['ch-dona-segmento'] = null; }
    const legendEl = G('dona-segmento-legend');
    if (legendEl) legendEl.innerHTML = '';
  };
  if (!wActivo || !DD || !DD.totals || !DD.totals.ingresos_segmentos) { limpiarSiExiste(); return; }
  const canvas = G('ch-dona-segmento');
  if (!canvas) return;
  const seg = DD.totals.ingresos_segmentos;
  const labels = Object.keys(seg).filter(function(k) { return seg[k] !== 0; });
  if (!labels.length) { limpiarSiExiste(); return; }
  if (CH['ch-dona-segmento']) CH['ch-dona-segmento'].destroy();
  const paletaSegmentos = { 'Venta de Mercancía': '#2563eb', 'Servicios': '#f97316', 'Taller': '#7c3aed', 'Eventos': '#059669' };
  const paleta = labels.map(function(k) { return paletaSegmentos[k] || '#94a3b8'; });
  CH['ch-dona-segmento'] = new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{ data: labels.map(function(k) { return seg[k]; }), backgroundColor: paleta }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: function(ctx) {
          const total = ctx.dataset.data.reduce(function(a,b){return a+b;},0);
          const pct = total ? (ctx.raw/total*100).toFixed(1) : 0;
          return 'Ingresos por ' + ctx.label + ': ' + fmtS(ctx.raw) + ' (' + pct + '%)';
        } } }
      }
    }
  });

  const legendEl = G('dona-segmento-legend');
  if (legendEl) {
    const total = labels.reduce((a,k) => a + seg[k], 0);
    const filas = labels.map((k, i) => {
      const pct = total ? (seg[k]/total*100).toFixed(1) : 0;
      return `<div style="display:flex;align-items:center;gap:6px;font-size:11px;margin-bottom:4px"><span style="width:9px;height:9px;background:${paleta[i]};border-radius:2px;display:inline-block;flex-shrink:0"></span>Ingresos por ${k}: <span style="color:var(--mu2)">${fmtS(seg[k])} (${pct}%)</span></div>`;
    }).join('');
    legendEl.innerHTML = `<div style="display:flex;justify-content:center"><div>${filas}</div></div>`;
  }
}

// ── HOME LOAD ─────────────────────────────────────────────────────────────
const HOME_EERR_ITEMS = [
  ['ingresos','Ingresos','big'], ['utilidad_neta','Utilidad neta','med'], ['ebitda','Ebitda','sm'],
  ['costo_ventas','Costo de ventas','sm'], ['gastos_operacionales','Gastos operacionales','med'], ['utilidad_bruta','Utilidad bruta','sm']
];
const HOME_IND_ITEMS = [
  ['roe','ROE','pct'], ['roa','ROA','pct'],
  ['periodo_cobro','Período de cobro','dias'], ['rotacion_inventarios','Rotación inventarios','ratio'], ['margen_neto','Margen neto','pct']
];

function _homeBento(clave, label, valor, tam){
  return `<div class="home-b ${tam}"><div class="l">${label}</div><div class="v">${fmtS(valor)}</div></div>`;
}
function _homeBentoInd(clave, label, valor, tipo){
  let txt='—';
  if(valor!=null){
    if(tipo==='pct') txt=(valor*100).toFixed(1)+'%';
    else if(tipo==='dias') txt=valor.toFixed(1)+' días';
    else txt=valor.toFixed(2)+'x';
  }
  return `<div class="home-b sm"><div class="l">${label}</div><div class="v">${txt}</div></div>`;
}
function _homeBalRow(label, valor, cls){
  return `<div class="home-bal-row ${cls||''}"><span>${label}</span><span class="v">${fmtS(valor)}</span></div>`;
}
function _homeBalSeccion(sec){
  return sec.detalle.map(function(d){return _homeBalRow(d.partida, d.valor, '');}).join('') + _homeBalRow(sec.label, sec.total, 'sub');
}
function _homeEsfPanel(data){
  const bySec = {};
  data.esf_detalle.forEach(function(s){ bySec[s.clave]=s; });
  const izq = '<div class="home-bal-col"><h4>Activos</h4>' +
    _homeBalSeccion(bySec.activo_corriente) +
    _homeBalSeccion(bySec.activo_no_corriente) +
    '<div class="home-bal-tot"><span>TOTAL ACTIVOS</span><span class="v">' + fmtS(data.total_activo_gral) + '</span></div></div>';
  const der = '<div class="home-bal-col"><h4>Pasivos + Patrimonio</h4>' +
    _homeBalSeccion(bySec.pasivo_corriente) +
    _homeBalSeccion(bySec.pasivo_no_corriente) +
    _homeBalSeccion(bySec.patrimonio) +
    '<div class="home-bal-tot"><span>TOTAL PASIVO + PATRIM.</span><span class="v">' + fmtS(data.total_pasivo_patrimonio_gral) + '</span></div></div>';
  return '<div class="home-bal-cols">' + izq + der + '</div>';
}

async function loadHome(){
  try{
    const r = await fetch(`/api/home/resumen?empresa_id=${CURRENT_EMPRESA_ID||''}`);
    if(!r.ok){ G('home-subtitulo').textContent='Error cargando datos del Home'; return; }
    const data = await r.json();
    if(data.error){ G('home-subtitulo').textContent = data.error; return; }

    const empresaLabelEl = document.getElementById('company-sel-label');
    const empresaLabel = empresaLabelEl ? empresaLabelEl.textContent : 'Ultrabikex Holding';
    G('home-saludo').textContent = data.saludo + ', ' + data.username + (data.extra_saludo||'');
    G('home-subtitulo').textContent = `${empresaLabel} · Divisa Real · Q${data.quarter} ${data.year}`;

    G('home-eerr-bento').innerHTML = HOME_EERR_ITEMS.map(function(x){return _homeBento(x[0],x[1],data.eerr[x[0]],x[2]);}).join('');
    G('home-ind-bento').innerHTML = HOME_IND_ITEMS.map(function(x){return _homeBentoInd(x[0],x[1],data.indicadores[x[0]],x[2]);}).join('');
    G('home-esf-panel').innerHTML = `<div class="home-esf-head">Año ${data.year} · último período cargado (Q${data.quarter})</div>` + _homeEsfPanel(data);
  }catch(e){
    G('home-subtitulo').textContent='Error cargando datos del Home';
  }
}

// ── DASHBOARD LOAD ────────────────────────────────────────────────────────
let _dashSeq = 0;
async function loadDash(){
  try{
    const mySeq = ++_dashSeq;
    const year=G('dash-year').value, unit=G('dash-unit').value;

    // Modo Divisa Real: carga datos ajustados de un mes específico
        if(modoDivisaReal){
              await actualizarDisponibilidadTrimestres();
              const month=G('dash-month').value;
              const qParam=G('dash-quarter')?G('dash-quarter').value:'';

          if(month){
            const rMes=await fetch(`/api/dashboard_divisa_real?year=${year}&month=${month}&unit=${unit}&empresa_id=${CURRENT_EMPRESA_ID||''}`);
            if(!rMes.ok){
              G('schips').innerHTML=`<span style="color:var(--red);font-size:12px">⚠️ Error cargando datos Divisa Real</span>`;
              return;
            }
            const dataMes=await rMes.json();
            if (mySeq !== _dashSeq) return;
            const dr=dataMes.divisa_real||{};
            DD={
              months:[{
                month:month,
                ingresos:dr.ingresos||0, costos:dr.costos||0, gastos:dr.gastos||0,
                utilidad_bruta:dr.utilidad_bruta||0, utilidad_neta:dr.utilidad_neta||0,
                margen_bruto:dr.ingresos?dr.utilidad_bruta/dr.ingresos*100:0,
                margen_neto:dr.ingresos?dr.utilidad_neta/dr.ingresos*100:0,
                ratio_costo:dr.ingresos?dr.costos/dr.ingresos*100:0,
                ratio_gasto:dr.ingresos?dr.gastos/dr.ingresos*100:0
              }],
              loaded:[{unit:unit==='TODAS'?'TODAS':unit,month:month}],
              por_unidad:[],
              top_gastos:[],
              cat_gastos:[],
              punto_equilibrio:null,
              indicadores_avanzados:[],
              totals:{
                ingresos:dr.ingresos||0,
                costos:dr.costos||0,
                gastos:dr.gastos||0,
                utilidad_bruta:dr.utilidad_bruta||0,
                utilidad_neta:dr.utilidad_neta||0,
                ebitda:dr.ebitda||0,
                otros_ingresos_no_operacionales:dr.otros_ingresos_no_operacionales||0,
                otros_gastos_no_operacionales:dr.otros_gastos_no_operacionales||0,
                total_activos:null,
                total_pasivos:null,
                patrimonio:null,
                ingresos_segmentos:dr.ingresos_segmentos||{}
              },
              _modo_divisa:true,
              _tasas:dataMes.tasas||null
            };
            if (mySeq !== _dashSeq) return;
          }else{
          const [rInd,rEerr]=await Promise.all([
            fetch(`/api/indicadores/divisa_real?year=${year}&empresa_id=${CURRENT_EMPRESA_ID||''}${qParam?`&quarter=${qParam}`:''}`),
            fetch(`/api/eerr/divisa_real/trimestres?year=${year}&unit=${unit==='TODAS'?'':unit}&empresa_id=${CURRENT_EMPRESA_ID||''}`)
          ]);
          if(!rInd.ok||!rEerr.ok){
            G('schips').innerHTML=`<span style="color:var(--red);font-size:12px">⚠️ Error cargando datos Divisa Real</span>`;
            return;
          }
          const dataInd=await rInd.json();
          const dataEerr=await rEerr.json();
          if (mySeq !== _dashSeq) return;

          let quartersUsar;
          if(qParam){
            quartersUsar=[parseInt(qParam)];
          }else{
            quartersUsar=[1,2,3,4];
          }
          const totalesEerr={ingresos:0,costos:0,gastos:0,utilidad_bruta:0,utilidad_neta:0,ebitda:0,otros_ing:0,otros_gas:0,
            seg_mercancia:0,seg_servicios:0,seg_eventos:0,seg_taller:0};
          quartersUsar.forEach(q=>{
            const qd=dataEerr.quarters[q]||{};
            totalesEerr.ingresos+=qd['Total Ingresos']||0;
            totalesEerr.costos+=qd['Total Costo de Ventas']||0;
            totalesEerr.gastos+=qd['Total Gastos Operacionales']||0;
            totalesEerr.utilidad_bruta+=qd['Utilidad Bruta']||0;
            totalesEerr.utilidad_neta+=qd['Utilidad Neta']||0;
            totalesEerr.ebitda+=qd['Utilidad antes de intereses, impuestos, depreciación y amortización (EBITDA)']||0;
            totalesEerr.otros_ing+=qd['Otros Ingresos no Operacionales']||0;
            totalesEerr.otros_gas+=qd['Otros Gastos no Operacionales']||0;
            totalesEerr.seg_mercancia+=qd['Subtotal Ingresos por Venta de Mercancia']||0;
            totalesEerr.seg_servicios+=qd['Subtotal Ingresos por Servicios']||0;
            totalesEerr.seg_eventos+=qd['Subtotal Ingresos por Eventos']||0;
            totalesEerr.seg_taller+=qd['Subtotal Ingresos por Taller']||0;
          });

          const esfTot=dataInd.esf_totales||{};
          const inds=dataInd.indicadores||[];

          DD={
            months:quartersUsar.map(q=>{
              const qd=dataEerr.quarters[q]||{};
              const ing=qd['Total Ingresos']||0;
              const cos=qd['Total Costo de Ventas']||0;
              const gas=qd['Total Gastos Operacionales']||0;
              const ub=qd['Utilidad Bruta']||0;
              const un=qd['Utilidad Neta']||0;
              return {
                month:'Q'+q,
                ingresos:ing, costos:cos, gastos:gas,
                utilidad_bruta:ub, utilidad_neta:un,
                margen_bruto:ing?ub/ing*100:0,
                margen_neto:ing?un/ing*100:0,
                ratio_costo:ing?cos/ing*100:0,
                ratio_gasto:ing?gas/ing*100:0
              };
            }),
            loaded:[{unit:unit==='TODAS'?'TODAS':unit,month:month||'ANUAL'}],
            por_unidad:(dataEerr.por_unidad||[]).map(pu=>{
              const t={ingresos:0,costos:0,gastos:0,utilidad_bruta:0,utilidad_neta:0};
              quartersUsar.forEach(q=>{
                const qd=pu.quarters[q]||{};
                t.ingresos+=qd['Total Ingresos']||0;
                t.costos+=qd['Total Costo de Ventas']||0;
                t.gastos+=qd['Total Gastos Operacionales']||0;
                t.utilidad_bruta+=qd['Utilidad Bruta']||0;
                t.utilidad_neta+=qd['Utilidad Neta']||0;
              });
              return {unit:pu.unit,ingresos:t.ingresos,costos:t.costos,gastos:t.gastos,utilidad_bruta:t.utilidad_bruta,utilidad_neta:t.utilidad_neta};
            }),
            top_gastos:[],
            cat_gastos:[],
            punto_equilibrio:null,
            indicadores_avanzados:inds,
            totals:{
              ingresos:totalesEerr.ingresos,
              costos:totalesEerr.costos,
              gastos:totalesEerr.gastos,
              utilidad_bruta:totalesEerr.utilidad_bruta,
              utilidad_neta:totalesEerr.utilidad_neta,
              ebitda:totalesEerr.ebitda,
              otros_ingresos_no_operacionales:totalesEerr.otros_ing,
              otros_gastos_no_operacionales:totalesEerr.otros_gas,
              total_activos:esfTot.total_activos!=null?esfTot.total_activos:null,
              total_pasivos:esfTot.total_pasivos!=null?esfTot.total_pasivos:null,
              patrimonio:esfTot.patrimonio!=null?esfTot.patrimonio:null,
              ingresos_segmentos:{
                'Venta de Mercancía':totalesEerr.seg_mercancia,
                'Servicios':totalesEerr.seg_servicios,
                'Eventos':totalesEerr.seg_eventos,
                'Taller':totalesEerr.seg_taller
              }
            },
            _modo_divisa:true,
            _tasas:null
          };
          if (mySeq !== _dashSeq) return;
          }
        }else{
      // Modo BCV normal: carga año completo
      const qParam = G('dash-quarter') ? G('dash-quarter').value : '';
      const res=await fetch(`/api/dashboard?year=${year}&unit=${unit}&empresa_id=${CURRENT_EMPRESA_ID||''}&quarter=${qParam}`);
      if(!res.ok){G('schips').innerHTML=`<span style="color:var(--red);font-size:12px">Error ${res.status} — recarga</span>`;return;}
      DD=await res.json();
      if (mySeq !== _dashSeq) return;
      DD._modo_divisa=false;
    }

    let mesesFiltrados;
        if (modoDivisaReal) {
          mesesFiltrados = DD.months;
        } else {
      // Modo Normal: filtro trimestral universal. QUARTER_MONTHS_DASH replica el
      // mismo agrupamiento que ya usa el backend (engine.py QUARTER_MONTHS).
      const selectedQuarter = G('dash-quarter') ? G('dash-quarter').value : '';
      const QUARTER_MONTHS_DASH = {'1':['ENE','FEB','MAR'],'2':['ABR','MAY','JUN'],'3':['JUL','AGO','SEPT'],'4':['OCT','NOV','DIC']};
      if (!selectedQuarter) {
        mesesFiltrados = DD.months;
      } else {
        mesesFiltrados = DD.months.filter(m => QUARTER_MONTHS_DASH[selectedQuarter].includes(m.month));
      }
    }

    // Redefinir para sincronizar automáticamente todas las vistas de gráficos y tablas
    DD.months = mesesFiltrados;
    const isTodas=unit==='TODAS';
    const ban=G('banner');ban.className='banner '+(isTodas?'b-all':'b-unit');
    G('bico').textContent=isTodas?'⬡':'◎';

    // Texto del banner según modo
    let bannerText=isTodas?'Vista Consolidada — Todas las Unidades':`Vista Detallada — ${unit}`;
    if(DD._modo_divisa){
      bannerText+=' · 💵 DIVISA REAL';
      const tasas=DD._tasas;
      if(tasas){
        bannerText+=` (Dif: ${tasas.diferencial.toFixed(2)})`;
      }
    }
    G('btxt').textContent=bannerText;

    const byU={};(DD.loaded||[]).forEach(l=>{if(!byU[l.unit])byU[l.unit]=[];byU[l.unit].push(l.month);});
    G('schips').innerHTML=Object.entries(byU).map(([u,ms])=>`<span class="s-chip">${u}: ${ms.join(' ')}</span>`).join(' ')||'<span class="s-empty">Sin datos cargados</span>';
    const tI = DD.totals ? DD.totals.ingresos : mesesFiltrados.reduce((a,m)=>a+m.ingresos,0);
    const tC = DD.totals ? DD.totals.costos : mesesFiltrados.reduce((a,m)=>a+m.costos,0);
    const tG = DD.totals ? DD.totals.gastos : mesesFiltrados.reduce((a,m)=>a+m.gastos,0);
    const ub = DD.totals ? DD.totals.utilidad_bruta : (tI - tC);
    const un = DD.totals ? DD.totals.utilidad_neta : (tI - tC - tG);
    const ebt = DD.totals ? DD.totals.ebitda : un;
    const mb=tI?ub/tI*100:0,mn=tI?un/tI*100:0,rc=tI?tC/tI*100:0,rg=tI?tG/tI*100:0;
    const sk=(id,v,s,b)=>{const kv=G('kv-'+id);if(kv)kv.textContent=v;const ks=G('ks-'+id);if(ks&&s)ks.textContent=s;const kb=G('kb-'+id);if(kb)kb.style.width=cl(b,0,100)+'%';};
    sk('ingr',fmtS(tI),'Acumulado año',100);
    sk('ub',fmtS(ub),'Margen: '+pct(mb),mb);
    sk('un',fmtS(un),'Margen: '+pct(mn),cl(Math.abs(mn),0,100));
    const kvUn=G('kv-un');if(kvUn)kvUn.style.color=un>=0?'var(--green)':'var(--red)';
    sk('mn',pct(mn),null,Math.abs(mn));
    const kvMn=G('kv-mn');if(kvMn)kvMn.style.color=mn>=5?'var(--green)':mn>=0?'var(--amber)':'var(--red)';
    sk('ebt',fmtS(ebt),null,tI?ebt/tI*100:0);
    const ta=DD.totals?DD.totals.total_activos:null;
    const tp=DD.totals?DD.totals.total_pasivos:null;
    const pat=DD.totals?DD.totals.patrimonio:null;
    sk('act',ta!=null?fmtS(ta):'—','Consolidado',100);
    sk('pas',tp!=null?fmtS(tp):'—','Consolidado',100);
    sk('pat',pat!=null?fmtS(pat):'—','Consolidado',100);
    const peCov=DD.punto_equilibrio?.cobertura_pct??null;
    const ia=DD.indicadores_avanzados||null;
    loadEstructuraCapital();
    loadEstructuraCapitalDetallada();
    loadSituacionFinanciera();
    loadPeriodoCobro();
    loadDeudaCobertura();
    loadROEROA();
    loadIngresosCostosMargen();
    loadCascadaPL();
    loadHeatmapUtilidadUnidad();
    loadDonaUnidad();
    loadDonaSegmento();
    // NOTA: renderSem, renderGauges, renderRank, renderPE, buildCharts, rTable, rWF
    // dejan de llamarse aqui -- alimentaban widgets ya eliminados del Dashboard
    // (Semaforo, Gauges, Ranking, Punto de Equilibrio, graficos viejos, tabla,
    // cascada vieja). Las funciones NO se borran, solo se dejan de invocar; se
    // reactivan/reescriben una por una al reconstruir cada grafico nuevo.
    applyHidden();
    scheduleMasonry();

    // Renderizar Panel de Indicadores
    const pindActivo = window.DASHBOARD_CONFIG.find(w => w.id === 'wc-panel-indicadores' && w.visible);
    if (pindActivo && ia) {
      const labels = ['ROE %','ROA %','Prueba Ácida','Prueba Defensiva','Endeudamiento','Rot. Inv.','Rot. Activos','P. Cobro'];
      const valores = [
        ia.roe!=null?ia.roe*100:null, ia.roa!=null?ia.roa*100:null,
        ia.prueba_acida, ia.prueba_defensiva,
        ia.ratio_endeud, ia.rotacion_inv, ia.rotacion_activos!=null?ia.rotacion_activos*4:null, ia.periodo_cobro
      ];
      const ctsel = document.getElementById('ct-ch-pind');
      const ctype = ctsel ? ctsel.value : 'bar';
      const canvas = G('ch-pind');
      const tableDiv = G('ch-pind-table');
      if (ctype === 'table') {
        if (canvas) canvas.style.display = 'none';
        if (tableDiv) {
          tableDiv.style.display = 'block';
          tableDiv.innerHTML = `<table style="width:100%;font-size:11px;border-collapse:collapse">
            <thead><tr><th style="text-align:left;padding:4px;border-bottom:1px solid var(--bd)">Indicador</th><th style="text-align:right;padding:4px;border-bottom:1px solid var(--bd)">Valor</th></tr></thead>
            <tbody>${labels.map((l,i)=>`<tr><td style="padding:4px;border-bottom:1px solid var(--bd)">${l}</td><td style="text-align:right;padding:4px;border-bottom:1px solid var(--bd)">${valores[i]!=null?Number(valores[i]).toFixed(2):'—'}</td></tr>`).join('')}</tbody>
          </table>`;
        }
      } else {
        if (canvas) canvas.style.display = '';
        if (tableDiv) tableDiv.style.display = 'none';
        if (CH['ch-pind']) CH['ch-pind'].destroy();
        const realType = ctype === 'bar-h' ? 'bar' : ctype;
        const opts = ctype === 'bar-h' ? {indexAxis:'y'} : {};
        if (canvas) CH['ch-pind'] = new Chart(canvas, {
          type: realType,
          data: { labels, datasets: [{ label: 'Valor', data: valores, backgroundColor: PAL }] },
          options: { responsive:true, ...opts, plugins:{ legend:{display:false} } }
        });
      }
    }

    // Renderizar Panel Balance ESF
    const pesfActivo = window.DASHBOARD_CONFIG.find(w => w.id === 'wc-panel-esf' && w.visible);
    if (pesfActivo) {
      fetch(`/api/esf/totals?year=${year}&unit=${unit==='TODAS'?'':unit}`)
        .then(r => r.ok ? r.json() : null)
        .then(esf => {
          if (!esf) return;
          const t = esf.totales;
          const labels = ['Activos Corrientes','Activos No Corrientes','Pasivos Corrientes','Pasivos No Corrientes','Patrimonio'];
          const valores = [t.activos_corrientes, t.activos_no_corrientes, t.pasivos_corrientes, t.pasivos_no_corrientes, t.patrimonio];
          const colors = ['#2563eb','#0891b2','#dc2626','#f97316','#059669'];
          const ctsel = document.getElementById('ct-ch-pesf');
          const ctype = ctsel ? ctsel.value : 'bar';
          const canvas = G('ch-pesf');
          const tableDiv = G('ch-pesf-table');
          if (ctype === 'table') {
            if (canvas) canvas.style.display = 'none';
            if (tableDiv) {
              tableDiv.style.display = 'block';
              tableDiv.innerHTML = `<table style="width:100%;font-size:11px;border-collapse:collapse">
                <thead><tr><th style="text-align:left;padding:4px;border-bottom:1px solid var(--bd)">Rubro</th><th style="text-align:right;padding:4px;border-bottom:1px solid var(--bd)">Monto</th></tr></thead>
                <tbody>${labels.map((l,i)=>`<tr><td style="padding:4px;border-bottom:1px solid var(--bd)">${l}</td><td style="text-align:right;padding:4px;border-bottom:1px solid var(--bd)">${fmtS(valores[i])}</td></tr>`).join('')}</tbody>
              </table>`;
            }
          } else {
            if (canvas) canvas.style.display = '';
            if (tableDiv) tableDiv.style.display = 'none';
            if (CH['ch-pesf']) CH['ch-pesf'].destroy();
            const realType = ctype === 'bar-stack' ? 'bar' : ctype;
            const stacked = ctype === 'bar-stack';
            if (canvas) CH['ch-pesf'] = new Chart(canvas, {
              type: realType,
              data: { labels, datasets: [{ label: 'Monto', data: valores, backgroundColor: colors }] },
              options: { responsive:true, maintainAspectRatio:false, plugins:{ legend:{position:'bottom', labels:{font:{size:10}}} }, scales: stacked ? {x:{stacked:true},y:{stacked:true}} : {} }
            });
          }
        });
    }

    // Renderizar widgets ESF
    const esfActivo = window.DASHBOARD_CONFIG.find(w => w.id === 'wc-esf-kpi-activos' && w.visible);
    if (esfActivo) {
      fetch(`/api/esf/totals?year=${year}&unit=${unit==='TODAS'?'':unit}`)
        .then(r => r.ok ? r.json() : null)
        .then(esf => {
          if (!esf) return;
          const t = esf.totales;
          const setE = (id, val) => { const el = G(id); if (el) el.textContent = fmtS(val); };
          const setPct = (id, num, den) => { const el = G(id); if (el) el.textContent = den ? pct(num/den*100) : '—'; };
          setE('esf-kpi-activos-val', t.total_activos);
          setE('esf-kpi-activos-ac', fmtS(t.activos_corrientes));
          setE('esf-kpi-activos-anc', fmtS(t.activos_no_corrientes));
          setE('esf-kpi-pasivos-val', t.total_pasivos);
          setE('esf-kpi-pasivos-pc', fmtS(t.pasivos_corrientes));
          setE('esf-kpi-pasivos-pnc', fmtS(t.pasivos_no_corrientes));
          setE('esf-kpi-patrimonio-val', t.patrimonio);
          setE('esf-kpi-efectivo-val', t.efectivo);
          setPct('esf-kpi-efectivo-pct', t.efectivo, t.activos_corrientes);
          setE('esf-kpi-cxc-val', t.cuentas_por_cobrar);
          setPct('esf-kpi-cxc-pct', t.cuentas_por_cobrar, t.activos_corrientes);
          setE('esf-kpi-inv-val', t.inventarios);
          setPct('esf-kpi-inv-pct', t.inventarios, t.activos_corrientes);

          // Gráfica estructura financiera
          const esfEstCanvas = G('ch-esf-est');
          if (esfEstCanvas) {
            if (CH['ch-esf-est']) CH['ch-esf-est'].destroy();
            const ctsel = document.getElementById('ct-ch-esf-est');
            const ctype = ctsel ? ctsel.value : 'doughnut';
            CH['ch-esf-est'] = new Chart(esfEstCanvas, {
              type: ctype,
              data: {
                labels: ['Activos Corrientes', 'Activos No Corrientes', 'Pasivos Corrientes', 'Pasivos No Corrientes', 'Patrimonio'],
                datasets: [{
                  data: [t.activos_corrientes, t.activos_no_corrientes, t.pasivos_corrientes, t.pasivos_no_corrientes, t.patrimonio],
                  backgroundColor: ['#2563eb','#0891b2','#dc2626','#f97316','#059669']
                }]
              },
              options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { font: { size: 10 } } } } }
            });
          }
        });
    }

    // Renderizar widgets de indicadores avanzados
    if (ia) {
      const setI = (id, val, suffix) => {
        const el = G(id);
        if (!el) return;
        el.textContent = val == null ? '—' : (suffix === '%' ? pct(val * 100) : Number(val).toFixed(2) + (suffix || ''));
      };
      setI('ind-roe-val', ia.roe, '%');
      setI('ind-roa-val', ia.roa, '%');
      setI('ind-pa-val', ia.prueba_acida, 'x');
      setI('ind-pd-val', ia.prueba_defensiva, 'x');
      setI('ind-end-val', ia.ratio_endeud, 'x');
      setI('ind-rotinv-val', ia.rotacion_inv, ' m');
      setI('ind-rotact-val', ia.rotacion_activos, 'x');
      setI('ind-cobro-val', ia.periodo_cobro, ' d');
    }

  }catch(err){
    console.error('loadDash:',err);
    G('schips').innerHTML=`<span style="color:var(--red);font-size:12px">Error JS: ${err.message}</span>`;
  }
}
// ── INIT ──────────────────────────────────────────────────────────────────
(async function init() {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
    return;
  }
  updateUserInfo();
  await initDashboardConfig();
  renderDashboardWidgets();
  initModalResize();
  await fillYears();
  await loadEmpresasDropdown();
  await loadUnidadesCache();
  updateAiUnitOptions();
  updateAiComparativaCheckboxes();
  updateUnitSelectorsForEmpresa();
  updateSidebarForEmpresa();

  G('dash-month').addEventListener('change', function() {
    const hasMes = this.value !== '';
    const qsel = G('dash-quarter');
    if (qsel) {
      if (hasMes) {
        qsel.value = '';
        qsel.disabled = true;
      } else {
        qsel.disabled = false;
      }
    }
    updateVisibilidadSeccionESF();
    loadDash();
  });

  G('dash-quarter').addEventListener('change', function() {
    const hasQ = this.value !== '';
    const msel = G('dash-month');
    if (msel) {
      if (hasQ) {
        msel.value = '';
        msel.disabled = true;
      } else {
        msel.disabled = false;
      }
    }
    updateVisibilidadSeccionESF();
    loadDash();
  });

  loadHome();
})();
