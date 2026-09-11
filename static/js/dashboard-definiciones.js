// Diccionario centralizado de definiciones financieras y rangos de referencia
// para el icono de definicion/rango en el Dashboard.
// Alcance: solo los 19 widgets activos de DEFAULT_DASHBOARD_CONFIG (KPIs + graficos).
// rango: "Pendiente de confirmar con Yocelin" es placeholder, no bloquea el uso del panel.
// Ver yocelin_preguntas_2.md para el detalle de que rangos estan pendientes.

const DASHBOARD_DEFINICIONES = {
  'kc-ingr': {
    definicion: "Todo el dinero que entra por la actividad principal del negocio (ventas), antes de restar cualquier costo o gasto. Es la linea de arriba del Estado de Resultados; todo lo demas se calcula a partir de aca. Un ingreso que crece pero con utilidad neta plana suele indicar que los costos o gastos estan creciendo al mismo ritmo o mas rapido -- hay que mirarlo siempre junto a la Utilidad Neta, no solo.",
    rango: "Pendiente de confirmar con Yocelin (depende de la meta de crecimiento del negocio)."
  },
  'kc-ub': {
    definicion: "Ingresos menos Costo de Ventas (lo que costo producir o comprar lo que se vendio). Mide que tan rentable es el producto/servicio en si, antes de gastos administrativos, de venta o financieros. Se suele leer como % (margen bruto = Utilidad Bruta / Ingresos): si ese % cae de un periodo a otro, algo paso con el costo de la mercancia o con el precio de venta.",
    rango: "Pendiente de confirmar con Yocelin (varia segun la linea de negocio)."
  },
  'kc-un': {
    definicion: "Lo que realmente queda despues de restar TODO: costo de ventas, gastos operativos, gastos financieros (intereses) e impuestos. Es el resultado final del periodo y el que mas le importa al dueno, porque es lo que efectivamente 'gana' la empresa. Utilidad Neta positiva pero decreciente en varios periodos seguidos es senal de alerta aunque los Ingresos sigan subiendo.",
    rango: "Pendiente de confirmar con Yocelin."
  },
  'kc-ebt': {
    definicion: "Utilidad antes de Intereses, Impuestos, Depreciacion y Amortizacion. Aisla la rentabilidad puramente operativa: cuanto genera el negocio del dia a dia, sin el efecto de como esta financiado (deuda) ni de decisiones contables (depreciacion) ni de la carga fiscal. Se usa para comparar la operacion entre empresas o unidades sin que la estructura de deuda de cada una distorsione la comparacion.",
    rango: "Pendiente de confirmar con Yocelin."
  },
  'kc-act': {
    definicion: "Todo lo que la empresa posee y controla a la fecha de corte (efectivo, cuentas por cobrar, inventario, propiedades, equipos, etc.), a valor contable. Es una magnitud (tamano de la empresa), no un ratio.",
    rango: "No aplica -- se evalua junto a otros indicadores (ROA, Rotacion de Activos) que si miden que tan bien se usan esos activos."
  },
  'kc-pas': {
    definicion: "Todo lo que la empresa debe a terceros (proveedores, bancos, impuestos por pagar, etc.), a la fecha de corte.",
    rango: "No aplica directamente -- su salud se mide via Ratio de Endeudamiento y Deuda y Cobertura, que comparan la deuda contra el tamano o la capacidad de pago de la empresa."
  },
  'kc-pat': {
    definicion: "Total Activos menos Total Pasivos: lo que le pertenece a los duenos despues de pagar todas las deudas. Crece cuando la empresa retiene utilidades (no las reparte) o cuando los socios aportan capital nuevo; baja si hay perdidas o retiros.",
    rango: "No aplica directamente -- es el denominador del ROE."
  },
  'wc-estcap': {
    definicion: "De que proporcion del financiamiento total viene de deuda (Pasivo) versus de los duenos (Patrimonio). Una empresa muy apalancada (mucha deuda relativa al patrimonio) tiene mas riesgo financiero pero tambien puede tener mas capacidad de crecimiento si esa deuda se usa bien.",
    rango: "Pendiente de confirmar con Yocelin para el perfil de riesgo de Ultrabikex."
  },
  'wc-estcapdet': {
    definicion: "El mismo analisis que Estructura de Capital, pero abriendo el Pasivo y el Patrimonio en sus componentes (deuda corto plazo, largo plazo, capital social, utilidades retenidas, etc.), para ver no solo cuanta deuda hay sino de que tipo.",
    rango: "Pendiente de confirmar con Yocelin (mismo criterio que Estructura de Capital)."
  },
  'wc-sitfin': {
    definicion: "Compara Activo Corriente (lo que se puede convertir en efectivo en el corto plazo) contra Pasivo Corriente (lo que hay que pagar en el corto plazo). Mide la capacidad inmediata de la empresa para cubrir sus obligaciones sin necesidad de vender activos de largo plazo.",
    rango: "Ratio Corriente entre 1.5 y 2.0 (por debajo de 1 es senal de riesgo de liquidez; muy por encima de 2 puede indicar efectivo ocioso)."
  },
  'wc-periodo-cobro': {
    definicion: "Cuantos dias, en promedio, tarda la empresa en cobrarle a sus clientes despues de una venta a credito. Un numero que sube con el tiempo indica que el dinero se esta demorando mas en entrar, lo que presiona el flujo de caja aunque las ventas se vean bien.",
    rango: "Pendiente de confirmar con Yocelin."
  },
  'wc-deuda-cobertura': {
    definicion: "Nivel de endeudamiento comparado contra la capacidad del negocio de cubrir esa deuda con su utilidad o flujo operativo (EBITDA). No basta con ver cuanta deuda hay, importa si el negocio genera suficiente para pagarla comodamente.",
    rango: "Pendiente de confirmar con Yocelin."
  },
  'wc-roe': {
    definicion: "ROE (Retorno sobre el Patrimonio) = Utilidad Neta / Patrimonio. Mide cuanto rendimiento le esta generando el negocio a cada dolar que los duenos tienen invertido. Es el indicador que mas le importa a un socio o inversionista, porque compara la ganancia contra 'su' plata, no contra el tamano total de la empresa.",
    rango: "10% a 20% (por debajo, el negocio rinde menos que alternativas de inversion razonables; por encima de 20% suele ser muy bueno, aunque hay que revisar si no es por poco patrimonio mas que por buena gestion)."
  },
  'wc-roa': {
    definicion: "ROA (Retorno sobre Activos) = Utilidad Neta / Total Activos. Mide que tan eficiente es la empresa generando utilidad con TODOS sus activos, esten financiados con deuda o con patrimonio propio. A diferencia del ROE, no depende de como este financiada la empresa -- por eso es mejor para comparar eficiencia operativa entre empresas con distinta estructura de deuda.",
    rango: "Pendiente de confirmar con Yocelin."
  },
  'wc-margen': {
    definicion: "Evolucion de Ingresos, Costo de Ventas y el % de margen bruto periodo a periodo. Sirve para detectar si la rentabilidad del producto se esta deteriorando (margen cayendo) incluso si el volumen de ventas crece.",
    rango: "Pendiente de confirmar con Yocelin (varia por linea de negocio)."
  },
  'wc-cascada': {
    definicion: "Vista tipo cascada que muestra visualmente como el ingreso total se va reduciendo paso a paso (costo de ventas, gastos operativos, gastos financieros, impuestos) hasta llegar a la utilidad neta.",
    rango: "No aplica -- es una herramienta de lectura visual, no un indicador con rango. Su valor es mostrar en que escalon se esta 'comiendo' mas la utilidad."
  },
  'wc-heatmap-un': {
    definicion: "Mapa de calor comparando que tan rentable es cada empresa/unidad del Holding en el mismo periodo, para detectar rapido cual esta jalando el resultado hacia arriba o hacia abajo.",
    rango: "No aplica un rango universal -- es comparativo entre unidades propias."
  },
  'wc-dona-unidad': {
    definicion: "Que porcentaje de los ingresos totales del Holding aporta cada unidad de negocio. Util para ver dependencia de una sola unidad.",
    rango: "No aplica."
  },
  'wc-dona-segmento': {
    definicion: "Mismo concepto que Ingresos por Unidad de Negocio, pero cortado por linea/segmento de negocio en vez de por empresa.",
    rango: "No aplica."
  }
};

function abrirDefinicionPanel(id, titulo) {
  const def = DASHBOARD_DEFINICIONES[id];
  if (!def) return;
  document.getElementById('dp-title').textContent = titulo;
  document.getElementById('dp-definicion').textContent = def.definicion;
  document.getElementById('dp-rango').textContent = def.rango;
  document.getElementById('definicion-panel').classList.add('dp-open');
}
function cerrarDefinicionPanel() {
  document.getElementById('definicion-panel').classList.remove('dp-open');
}

