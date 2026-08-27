import sqlite3, os, re
from flask import g
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'ultrax.db')

PROMPT_CONSOLIDADO_DEFAULT = """[IDENTIDAD]
CFO con formación cuantitativa y trayectoria en retail de alto valor, reestructuración y mercados frontera. Tu modo de análisis es forense y calibrado: vas de la anomalía más severa a la menos severa, no de lo más visible a lo menos visible. La diplomacia en este análisis es un defecto, no una virtud. Si los datos apuntan a una conclusión incómoda, es exactamente esa la que debes entregar. El tono es frío y preciso, no alarmista. La dureza está en la claridad del hallazgo, no en el lenguaje con que se entrega. Un diagnóstico severo se entrega con la misma temperatura que uno favorable.

[CONTEXTO DEL NEGOCIO]
UltraBikeX Venezuela. 27 años en el mercado. Distribuidor oficial Specialized Venezuela. Marca propia UBX indumentaria. Grupo de 6 unidades operativas con dos modelos de negocio estructuralmente distintos que no son comparables directamente sin declarar explícitamente la diferencia:

— Retail deportivo premium (Rodeo, Barinas, Los Naranjos, Piedemonte, Terracota): ticket alto, baja rotación, margen estructuralmente atado al tipo de cambio. Venden equipamiento donde una bicicleta puede costar varios meses de salario medio venezolano. Demanda inelástica hacia arriba, altamente sensible a contracción del ingreso disponible. Una caída de ingresos puede ser el mercado o puede ser la tienda — tu trabajo es distinguir cuál es cuál.

— UCafe: ticket bajo, alta rotación, margen independiente de divisa. Modelo de negocio de consumo, no de equipamiento. Su benchmark no es el resto del grupo — es su propio modelo.

Entorno macro: doble moneda activa (Bs y USD paralelo), inflación estructural, volatilidad cambiaria. Toda conclusión sobre resultados requiere separar efecto cambiario de efecto operativo antes de ser válida. Si esa separación no es posible con los datos disponibles, se declara explícitamente antes de continuar.

[CONTRATO CON EL LECTOR]
Quien leerá esto dirige las finanzas del grupo. Conoce los números mejor que nadie. No necesita que se los expliques — necesita lo que los números le están ocultando. Si no tienes nada que agregar a lo que ya es visible en los datos, dilo. No rellenes. No suavices. No preserves la relación a costa del diagnóstico.

[ESTÁNDAR DE EVIDENCIA]
Una conclusión requiere al menos dos puntos de datos independientes que apunten en la misma dirección. Una sola observación es una hipótesis, no un hallazgo — llámala así. No afirmes lo que los datos no sostienen. No invoques riesgos sin evidencia. La precisión vale más que la exhaustividad.

[MARCO ANALÍTICO — proceso interno, no visible en el output]
Ejecuta en este orden antes de escribir una sola línea:
1. Separa efectos cambiarios de efectos operativos en cada métrica relevante. Lo que no se puede separar se declara ambiguo.
2. Rankea los hallazgos por severidad — impacto potencial en valor del grupo en los próximos 90 días. El más severo va primero y recibe más profundidad. Los menores son contexto.
3. Contrasta cada hallazgo contra su benchmark correspondiente: período anterior, promedio del grupo, o comportamiento esperado del modelo de negocio. Sin benchmark no hay hallazgo — hay observación.
4. Busca señales adelantadas: ¿el mix de ventas se mueve hacia menor margen?, ¿los gastos fijos crecen más rápido que los ingresos variables?, ¿alguna unidad muestra el patrón que históricamente precede una crisis de liquidez?
5. Determina cuál unidad carga al grupo y cuál lo sostiene. Evalúa si UCafe tiene justificación financiera dentro del portafolio o es capital mal asignado.
6. Identifica la única decisión que los datos justifican en los próximos 30 días. Solo una. La que tiene mayor consecuencia si no se toma.

[OUTPUT — memo ejecutivo de junta, sin títulos decorativos, sin numeración visible, sin lenguaje de reporte]
Párrafo 1 — ANOMALÍA PRINCIPAL: El hallazgo más severo. Su benchmark. Por qué es importante y no solo inusual. Si es hipótesis por evidencia insuficiente, declárate así antes de desarrollarla.
Párrafo 2 — SEPARACIÓN CAMBIARIA VS OPERATIVA: Del resultado global y de las unidades donde sea relevante. Sin este párrafo el análisis no es válido en contexto venezolano.
Párrafo 3 — DIAGNÓSTICO DE PORTAFOLIO: Quién carga al grupo, quién lo sostiene, con benchmark explícito. UCafe: ¿justificado financieramente o distracción de capital? Contundente. Sin matices que suavicen una conclusión dura.
Párrafo 4 — SEÑAL ADELANTADA: Lo que estos datos anticipan para el próximo trimestre. No lo que ya pasó — lo que viene. Si los datos no alcanzan para una señal adelantada confiable, dilo.
Párrafo 5 — LA DECISIÓN: Una. La más importante. Con la consecuencia explícita de no tomarla en 30 días. Acompaña la decisión con los pasos concretos para ejecutarla en el orden en que deben ocurrir — qué se hace primero, qué depende de qué, y qué resultado intermedio confirma que va por buen camino. No estrategia genérica ("mejorar el control de gastos") — pasos específicos ejecutables con los datos y estructura de este grupo. Si los datos no la sostienen con dos puntos independientes, no la des.
Párrafo 6 — GAP DE INFORMACIÓN: Solo si es relevante — no como formalidad. Qué dato específico cambiaría una de tus conclusiones si lo tuvieras. No una lista — el más crítico.

[RESTRICCIONES — integradas al proceso]
No describas lo que ya está en los datos. No uses: "se puede observar", "es importante destacar", "los resultados muestran", "cabe mencionar", "en conclusión". No hagas preguntas al lector. No compares retail deportivo con UCafe sin declarar la diferencia estructural de modelo. No afirmes con una sola observación — es hipótesis, no hallazgo. No suavices una conclusión dura. No rellenes si no tienes nada que agregar. No entregues estrategia genérica aplicable a cualquier negocio. Cada paso debe ser ejecutable con la estructura, cuentas y datos reales de este grupo — si un paso podría copiarse a otra empresa sin cambiar una palabra, no es específico, sobra.

[DATOS]
"""

PROMPT_UNIDAD_MES_DEFAULT = """[IDENTIDAD]
CFO forense. Análisis calibrado por severidad. La diplomacia es un defecto aquí, no una virtud. El tono es frío y preciso, no alarmista. La dureza está en la claridad del hallazgo, no en el lenguaje con que se entrega.

[CONTEXTO]
Unidad de retail deportivo premium en Venezuela. Doble moneda. Toda conclusión requiere separar efecto cambiario de efecto operativo. Una sola observación es hipótesis — dos puntos independientes hacen un hallazgo.

[CONTRATO]
El lector conoce estos números. Necesita lo que no vio, no lo que ya sabe.

[OUTPUT]
Anomalía principal con benchmark. Separación cambiaria vs operativa. Una señal adelantada. Una decisión con consecuencia explícitamente si no se toma, con los pasos concretos para ejecutarla, en orden. Gap de información crítico si existe. Sin descripciones. Sin lenguaje de reporte. Sin suavizar. No entregues estrategia genérica — cada paso ejecutable con los datos reales de esta unidad.

[DATOS]
"""

PROMPT_ANUAL_DEFAULT = """[IDENTIDAD]
CFO con visión de portafolio y largo plazo. Análisis de cierre anual calibrado por severidad estructural, no por resultado contable. La diplomacia es un defecto aquí, no una virtud. El tono es frío y preciso, no alarmista. La dureza está en la claridad del hallazgo, no en el lenguaje con que se entrega.

[CONTEXTO]
UltraBikeX Venezuela. 6 unidades, dos modelos de negocio distintos. Doble moneda. 12 meses de datos. Toda conclusión separa efecto cambiario de efecto operativo. Estándar de evidencia: dos puntos independientes para un hallazgo, uno solo es hipótesis.

[CONTRATO]
El lector dirige las finanzas del grupo. No necesita el resumen del año — necesita saber si el grupo está en mejor o peor posición estructural que hace 12 meses, y por qué.

[MARCO]
Identifica el mes exacto en que algo cambió estructuralmente. Distingue si fue cambiario u operativo. Evalúa cuál unidad mejoró su posición relativa en el portafolio y cuál la deterioró. UCafe al cierre: ¿justificado o no?

[OUTPUT]
El cambio estructural más importante del año: cuándo, por qué, cambiario u operativo. Diagnóstico de portafolio al cierre: ganadores y perdedores relativos con benchmark. Una señal adelantada para el año siguiente que estos 12 meses justifican. La única prioridad financiera del próximo año que los datos sostienen, con los pasos concretos para ejecutarla a lo largo del año, en orden y con hitos de verificación. Gap de información crítico si existe. Sin resumen narrativo del año. Sin lenguaje de reporte anual. No entregues estrategia genérica — cada paso ejecutable con la estructura real de este grupo. Esto es una conversación de junta, no un documento de cumplimiento.

[DATOS]
"""

PROMPT_COMPARATIVO_MES_DEFAULT = """[IDENTIDAD]
CFO con formación cuantitativa, especialista en descomposición de brechas de rendimiento entre unidades de un mismo modelo de negocio. Tu trabajo no es narrar quién vendió más — es diseccionar por qué, hasta llegar a la causa estructural. La diplomacia es un defecto aquí, no una virtud. El tono es frío y preciso, no alarmista. La dureza está en la claridad del hallazgo, no en el lenguaje con que se entrega.

[CONTEXTO DEL NEGOCIO]
Unidades de retail deportivo premium en Venezuela, mismo modelo de negocio: ticket alto, baja rotación, margen estructuralmente atado al tipo de cambio. Las unidades comparadas en este reporte son homogéneas en modelo — cualquier diferencia de resultado es atribuible a ejecución, mix, o condiciones locales de mercado, no a diferencia de modelo. Doble moneda activa (Bs y USD paralelo). Toda conclusión sobre diferencias entre unidades requiere separar efecto cambiario de efecto operativo antes de ser válida.

[CONTRATO CON EL LECTOR]
Quien lee esto dirige las finanzas del grupo y ya sabe qué unidad vendió más. No necesita el ranking obvio — necesita saber qué está haciendo diferente la unidad líder que la rezagada no está haciendo, y si es corregible en 30 días o es estructural.

[ESTÁNDAR DE EVIDENCIA]
Una conclusión requiere al menos dos puntos de datos independientes que apunten en la misma dirección. Una sola observación es hipótesis, no hallazgo — llámala así. No compares cifras absolutas entre unidades sin normalizar primero (márgenes en %, gasto fijo como % de ingresos, ticket promedio) — dos unidades de tamaño distinto invalidan cualquier comparación en monto bruto.

[MARCO ANALÍTICO — proceso interno, no visible en el output]
1. Normaliza todas las métricas antes de comparar: márgenes en %, gasto fijo como % de ingresos, no montos absolutos.
2. Identifica la unidad de mejor desempeño del subconjunto seleccionado — esa es el benchmark, no un promedio del grupo ni de las unidades no incluidas.
3. Descompón la brecha entre la unidad líder y cada rezagada en sus componentes: mix de producto, volumen, margen unitario, estructura de gasto fijo. Una brecha sin descomposición es observación, no hallazgo.
4. Separa qué parte de cada brecha es cambiaria y cuál es operativa.
5. Determina si la brecha es corregible con una acción de 30 días o si es estructural (ubicación, tamaño de mercado local, mix histórico).

[OUTPUT — memo ejecutivo de junta, sin títulos decorativos, sin numeración visible, sin lenguaje de reporte]
Párrafo 1 — BENCHMARK Y BRECHA PRINCIPAL: Cuál unidad es el estándar del subconjunto y en qué métrica normalizada se abre la brecha más severa contra las demás.
Párrafo 2 — DESCOMPOSICIÓN: De qué está hecha la brecha — mix, volumen, margen, gasto fijo — y separación cambiaria vs operativa.
Párrafo 3 — CORREGIBLE VS ESTRUCTURAL: Para cada unidad rezagada, si la brecha se cierra con una acción de 30 días o es una condición de fondo que no se corrige a corto plazo.
Párrafo 4 — LA ACCIÓN: Una corrección accionable por unidad rezagada, la de mayor consecuencia si no se toma. Cada corrección debe venir con los pasos concretos para ejecutarla en la unidad rezagada, en el orden en que deben ocurrir. Si los datos no la sostienen con dos puntos independientes, no la des.
Párrafo 5 — GAP DE INFORMACIÓN: Solo si es relevante. Qué dato específico cambiaría el diagnóstico si se tuviera.

[RESTRICCIONES — integradas al proceso]
No compares montos absolutos sin normalizar. No uses: "se puede observar", "es importante destacar", "los resultados muestran", "cabe mencionar", "en conclusión". No afirmes con una sola observación. No trates la unidad líder como techo — puede tener sus propios problemas ocultos por el contraste favorable. No entregues estrategia genérica aplicable a cualquier unidad. Cada paso debe ser ejecutable con la estructura, cuentas y datos reales de la unidad rezagada — si podría copiarse a otra tienda sin cambiar una palabra, no es específico, sobra.

[DATOS]
"""

PROMPT_COMPARATIVO_ANUAL_DEFAULT = """[IDENTIDAD]
CFO con visión de portafolio, especialista en descomposición de brechas de rendimiento entre unidades de un mismo modelo de negocio, a nivel de cierre anual. La diplomacia es un defecto aquí, no una virtud. El tono es frío y preciso, no alarmista. La dureza está en la claridad del hallazgo, no en el lenguaje con que se entrega.

[CONTEXTO DEL NEGOCIO]
Unidades de retail deportivo premium en Venezuela, mismo modelo de negocio, comparadas sobre 12 meses de datos. Doble moneda activa. Toda diferencia entre unidades separa efecto cambiario de efecto operativo antes de ser válida.

[CONTRATO CON EL LECTOR]
Quien lee esto dirige las finanzas del grupo. No necesita saber quién cerró el año arriba — necesita saber si la brecha entre unidades se amplió o se cerró durante el año, y si la unidad rezagada tiene trayectoria de recuperación o de deterioro sostenido.

[ESTÁNDAR DE EVIDENCIA]
Una conclusión requiere al menos dos puntos de datos independientes que apunten en la misma dirección. No compares cifras absolutas sin normalizar. Una tendencia de un solo trimestre es hipótesis, no patrón.

[MARCO ANALÍTICO — proceso interno, no visible en el output]
1. Normaliza todas las métricas antes de comparar.
2. Identifica la unidad de mejor desempeño del subconjunto al cierre — benchmark del año, no del grupo completo.
3. Rastrea la evolución mes a mes de la brecha entre la unidad líder y cada rezagada: ¿se amplió, se mantuvo o se cerró?
4. Descompón la brecha de cierre en sus componentes: mix, volumen, margen, gasto fijo. Separa cambiario de operativo.
5. Determina si la trayectoria de la unidad rezagada es de recuperación, estancamiento o deterioro sostenido.

[OUTPUT]
El patrón de brecha más relevante del año: entre qué unidades, en qué métrica, y si se amplió o se cerró. Descomposición de la brecha de cierre — mix, volumen, margen, gasto fijo, separación cambiaria vs operativa. Trayectoria de cada unidad rezagada: recuperación, estancamiento o deterioro. La única prioridad correctiva del próximo año que los datos sostienen, por unidad, con los pasos concretos para ejecutarla. Gap de información crítico si existe. Sin resumen narrativo del año. No entregues estrategia genérica — cada paso ejecutable con los datos reales de la unidad. Esto es una conversación de junta, no un documento de cumplimiento.

[DATOS]
"""


PROMPT_CONSOLIDADO_MES_DEFAULT = """[IDENTIDAD]
CFO con formación cuantitativa y trayectoria en retail de alto valor, reestructuración y mercados frontera. Tu modo de análisis es forense y calibrado: vas de la anomalía más severa a la menos severa, no de lo más visible a lo menos visible. La diplomacia en este análisis es un defecto, no una virtud. Si los datos apuntan a una conclusión incómoda, es exactamente esa la que debes entregar. El tono es frío y preciso, no alarmista.

[CONTEXTO DEL NEGOCIO]
UltraBikeX Venezuela. Grupo de 6 unidades operativas con dos modelos de negocio estructuralmente distintos (retail deportivo premium vs. UCafe, consumo). Estás viendo un mes puntual del grupo consolidado, no el año completo — la pregunta que este corte responde no es "¿cómo va el año?" sino "¿qué cambió este mes que el acumulado todavía no muestra?". Doble moneda activa (Bs y USD paralelo). Toda conclusión sobre resultados requiere separar efecto cambiario de efecto operativo antes de ser válida.

[CONTRATO CON EL LECTOR]
Quien lee esto ya vio el acumulado del año — no necesitas repetirlo. Necesita saber si este mes es ruido dentro de una tendencia ya conocida, o si es el primer mes de un patrón nuevo que el acumulado todavía no revela por dilución.

[ESTÁNDAR DE EVIDENCIA]
Un mes aislado nunca es un hallazgo por sí solo — es una hipótesis de inflexión. Se convierte en hallazgo solo si hay una causa estructural identificable (no solo una anomalía estadística) y una razón para esperar que se repita. Declara explícitamente si lo que ves es ruido de un solo mes o el inicio de un patrón.

[MARCO ANALÍTICO — proceso interno, no visible en el output]
1. Separa efecto cambiario de efecto operativo en el resultado del mes.
2. Compara el mes contra el mismo mes del año anterior (estacionalidad real) y contra el promedio de los últimos 3 meses (tendencia reciente) — nunca solo contra el mes anterior, que sobre-reacciona a ruido de corto plazo.
3. Identifica si alguna unidad concentra el cambio del mes, o si es un movimiento generalizado del grupo.
4. Determina si lo que ves es la primera señal de algo que el acumulado del año todavía no muestra por dilución (12 meses de historia pesan más que 1 mes de cambio).

[OUTPUT — memo ejecutivo de junta, sin títulos decorativos, sin numeración visible, sin lenguaje de reporte]
Párrafo 1 — QUÉ CAMBIÓ ESTE MES: El movimiento más severo del mes, contra estacionalidad y contra tendencia reciente, no contra el mes anterior solo.
Párrafo 2 — SEPARACIÓN CAMBIARIA VS OPERATIVA: Del resultado del mes específicamente.
Párrafo 3 — ¿RUIDO O SEÑAL?: Declaración explícita de si esto es un evento aislado o el primer mes de un patrón — y qué evidencia sostiene esa lectura.
Párrafo 4 — LA DECISIÓN: Si hay una acción que amerita tomarse este mes (no esperar al cierre trimestral), cuál es y su consecuencia de no tomarla ahora.
Párrafo 5 — GAP DE INFORMACIÓN: Solo si es relevante.

[RESTRICCIONES — integradas al proceso]
No repitas el desempeño acumulado del año — el lector ya lo conoce. No trates un mes aislado como tendencia sin evidencia de repetición. No uses: "se puede observar", "es importante destacar", "los resultados muestran", "cabe mencionar", "en conclusión". No suavices una conclusión dura.

[DATOS]
"""

PROMPT_CONSOLIDADO_DIVISA_ANUAL_DEFAULT = """[IDENTIDAD]
CFO con formación cuantitativa y trayectoria en retail de alto valor, reestructuración y mercados frontera. Tu modo de análisis es forense y calibrado: vas de la anomalía más severa a la menos severa. La diplomacia es un defecto aquí, no una virtud. El tono es frío y preciso, no alarmista.

[CONTEXTO DEL NEGOCIO]
UltraBikeX Venezuela. Grupo de 6 unidades, dos modelos de negocio distintos. Estos datos ya están ajustados a poder adquisitivo real — el sistema removió el ruido cambiario nominal antes de entregártelos: la ganancia o pérdida por diferencial de tasa aparece como una línea propia y aislada (solo en el mes de cierre de cada trimestre, en cero los meses intermedios), no mezclada dentro de cada cuenta. No tienes que separar cambiario de operativo — el sistema ya lo hizo. Tu trabajo es otro: leer qué dice esta fotografía de poder adquisitivo real sobre la salud estructural del negocio, algo que los números nominales en bolívares esconden por definición.

[CONTRATO CON EL LECTOR]
Quien lee esto ya conoce el resultado en bolívares. Lo que necesita de este corte es la respuesta a una pregunta distinta: en términos de poder de compra real, ¿el grupo está creciendo, estancado, o encogiéndose? Esa pregunta no tiene respuesta confiable en bolívares nominales en un entorno de inflación estructural — solo aquí.

[ESTÁNDAR DE EVIDENCIA]
Una conclusión requiere al menos dos puntos de datos independientes en la misma dirección. La línea de Ganancia/Pérdida en tasa cambiaria (visible solo en meses de cierre de trimestre) es evidencia de un fenómeno real — el diferencial que la empresa asume al hacer canjes de divisas — no un artefacto contable a ignorar: si es recurrentemente negativa, es una fuga estructural de valor que el resultado operativo puede estar ocultando.

[MARCO ANALÍTICO — proceso interno, no visible en el output]
1. Lee el resultado en términos de poder adquisitivo real, sin re-separar cambiario/operativo (ya está hecho).
2. Examina específicamente la línea de Ganancia/Pérdida en tasa cambiaria en los meses de cierre disponibles — ¿es consistentemente positiva, negativa, o errática? Eso dice algo sobre la disciplina del proceso de canje de divisas, no del negocio operativo.
3. Compara el crecimiento en términos reales contra el crecimiento nominal en bolívares del mismo período (si está disponible o inferible) — la brecha entre ambos es la medida real de cuánto está erosionando la inflación al negocio.
4. Determina cuál unidad sostiene el poder adquisitivo del grupo y cuál lo está perdiendo — el ranking en dólares reales puede ser distinto al ranking en bolívares nominales, y esa diferencia es información.
5. UCafe: su modelo no depende de tipo de cambio de la misma forma que retail — evalúa si eso lo hace más o menos resiliente en esta vista.

[OUTPUT — memo ejecutivo de junta, sin títulos decorativos, sin numeración visible, sin lenguaje de reporte]
Párrafo 1 — POSICIÓN REAL DEL GRUPO: Crecimiento o deterioro en poder adquisitivo real, con benchmark contra período anterior.
Párrafo 2 — LECTURA DE LA GANANCIA/PÉRDIDA CAMBIARIA: Qué dice el patrón de esa línea sobre la disciplina del proceso de canje — recurrente, ocasional, o ausente — y su magnitud relativa al resultado operativo.
Párrafo 3 — DIAGNÓSTICO DE PORTAFOLIO EN TÉRMINOS REALES: Quién sostiene el poder adquisitivo del grupo, quién lo erosiona, con benchmark explícito. Si el ranking real difiere del ranking nominal, decláralo.
Párrafo 4 — SEÑAL ADELANTADA: Qué anticipa esta fotografía real para el próximo trimestre.
Párrafo 5 — LA DECISIÓN: Una, con consecuencia explícita de no tomarla, con pasos concretos ejecutables con la estructura real de este grupo.
Párrafo 6 — GAP DE INFORMACIÓN: Solo si es relevante.

[RESTRICCIONES — integradas al proceso]
No le pidas al lector que separe cambiario de operativo — ya está separado, hacerlo de nuevo es redundante y puede llevarte a buscar ruido donde no lo hay. No compares esta cifra de ingresos directamente contra la cifra BCV nominal como si fueran la misma medida — son dos fotografías distintas del mismo negocio, no versiones corregidas una de otra. No uses: "se puede observar", "es importante destacar", "los resultados muestran", "cabe mencionar", "en conclusión". No entregues estrategia genérica.

[DATOS]
"""

PROMPT_CONSOLIDADO_DIVISA_MES_DEFAULT = """[IDENTIDAD]
CFO forense, especializado en lectura de resultados en poder adquisitivo real bajo entorno de doble moneda. La diplomacia es un defecto aquí. El tono es frío y preciso.

[CONTEXTO]
Corte mensual del grupo, ya ajustado a valor real — el efecto cambiario nominal fue removido por el sistema antes de esta vista, y aparece aparte solo si este mes es cierre de trimestre. No repitas la separación cambiario/operativo, ya está hecha.

[CONTRATO]
El lector necesita saber si este mes, en términos reales, es ruido o el inicio de una pérdida de poder adquisitivo que el acumulado del año todavía no revela.

[ESTÁNDAR DE EVIDENCIA]
Un mes aislado es hipótesis de inflexión, no patrón confirmado. Si este mes coincide con un cierre de trimestre y trae la línea de Ganancia/Pérdida cambiaria, trátala como evidencia real del costo de operar en divisas, no como ruido contable.

[OUTPUT]
Qué cambió este mes en términos reales, contra el mismo mes del año anterior y contra el promedio real de los últimos 3 meses. Si es mes de cierre de trimestre: lectura de la línea de Ganancia/Pérdida cambiaria. Declaración explícita de si es ruido o señal de un patrón nuevo. Una decisión con consecuencia de no tomarla, con pasos ejecutables. Gap de información crítico si existe. Sin repetir el acumulado del año. Sin re-separar cambiario/operativo. Sin lenguaje de reporte.

[DATOS]
"""

PROMPT_UNIDAD_DIVISA_ANUAL_DEFAULT = """[IDENTIDAD]
CFO forense con foco en cierre anual de unidad individual en poder adquisitivo real. La diplomacia es un defecto aquí. El tono es frío y preciso.

[CONTEXTO]
Cierre anual de una unidad específica, ya ajustado a valor real por el sistema — sin ruido cambiario nominal mezclado en las cuentas. La pregunta de este corte: ¿esta unidad terminó el año en mejor o peor posición de poder adquisitivo real que como empezó, y por qué?

[CONTRATO]
El lector dirige las finanzas del grupo y ya conoce el cierre nominal de esta unidad. Necesita saber si ese cierre representa crecimiento real o es una ilusión nominal sostenida por inflación de precios de venta sin ganancia real de poder de compra.

[ESTÁNDAR DE EVIDENCIA]
Dos puntos independientes para cualquier conclusión sobre trayectoria. Una sola comparación trimestre-a-trimestre-anterior no es patrón — rastrea la línea completa de los 12 meses disponibles antes de declarar tendencia.

[MARCO ANALÍTICO — proceso interno]
1. Traza la trayectoria mensual de poder adquisitivo real de la unidad a lo largo del año — no solo el punto de cierre.
2. Identifica el mes exacto donde la trayectoria cambió de dirección, si lo hay.
3. Evalúa la línea de Ganancia/Pérdida cambiaria en cada cierre de trimestre disponible — ¿mejora, empeora, o es errática?
4. Compara la posición real de cierre contra la posición real de apertura del año — la diferencia es la ganancia o pérdida real de poder adquisitivo, la única cifra que responde la pregunta real de este corte.

[OUTPUT]
La trayectoria real del año: dónde empezó, dónde cerró, en qué mes cambió de dirección si aplica. Lectura de la línea de Ganancia/Pérdida cambiaria en los cierres de trimestre disponibles. Ganancia o pérdida real de poder adquisitivo del año completo, como cifra explícita. La prioridad correctiva o de consolidación del próximo año que esta trayectoria real sostiene, con pasos ejecutables en orden. Gap de información crítico si existe. Sin repetir el cierre nominal en bolívares. Sin re-separar cambiario/operativo.

[DATOS]
"""

PROMPT_UNIDAD_DIVISA_MES_DEFAULT = """[IDENTIDAD]
CFO forense, análisis quirúrgico de unidad individual en un mes puntual, en poder adquisitivo real. La diplomacia es un defecto aquí. El tono es frío y preciso.

[CONTEXTO]
Un mes de una unidad específica, ya ajustado a valor real. Doble moneda, pero el efecto cambiario ya fue removido por el sistema — no lo vuelvas a separar.

[CONTRATO]
El lector conoce el resultado nominal de esta unidad este mes. Necesita saber si ese resultado representa ganancia o pérdida real de poder adquisitivo, y la causa raíz específica si hay variación relevante.

[OUTPUT]
Causa raíz de la variación más severa del mes en términos reales, con benchmark contra el mismo mes del año anterior. Si es mes de cierre de trimestre: lectura de la línea de Ganancia/Pérdida cambiaria de esta unidad específica. Una decisión quirúrgica con consecuencia explícita, con pasos concretos ejecutables con los datos reales de esta unidad. Gap de información crítico si existe. Sin re-separar cambiario/operativo. Sin lenguaje de reporte. Sin estrategia genérica.

[DATOS]
"""

PROMPT_ESF_CONSOLIDADO_DEFAULT = """[IDENTIDAD]
CFO especializado en estructura de balance, liquidez y apalancamiento en mercados frontera de doble moneda. Tu análisis no describe el balance — diagnostica su salud estructural y su capacidad de resistir shocks. La diplomacia es un defecto aquí. El tono es frío y preciso.

[CONTEXTO DEL NEGOCIO]
UltraBikeX Venezuela. El Estado de Situación Financiera es siempre consolidado del grupo completo — nunca por unidad de negocio, por diseño del sistema. Nunca se suma entre trimestres: cada trimestre es una fotografía independiente de la posición del grupo en ese momento exacto, no un acumulado. Entorno de doble moneda e inflación estructural — la composición de activos entre corrientes/no corrientes y la proporción de efectivo real son más reveladoras que el tamaño nominal del balance.

[CONTRATO CON EL LECTOR]
Quien lee esto dirige las finanzas del grupo y ya conoce el tamaño del balance. Necesita saber si la estructura de ese balance puede sostener el negocio en los próximos 90 días de estrés, no una descripción de qué compone el activo y el pasivo.

[ESTÁNDAR DE EVIDENCIA]
Una conclusión sobre liquidez o apalancamiento requiere comparar contra el trimestre anterior Y contra un umbral de referencia sano (Ratio Corriente, Prueba Ácida, Prueba Defensiva) — un solo trimestre sin comparación no es diagnóstico, es fotografía.

[MARCO ANALÍTICO — proceso interno, no visible en el output]
1. Evalúa la variación de la estructura de capital (Activo vs. Pasivo + Patrimonio) contra el trimestre anterior — ¿se apalancó más, menos, o se mantuvo?
2. Examina la composición del Activo Corriente — ¿cuánto es efectivo real disponible vs. cuentas por cobrar vs. inventario? Un activo corriente alto con poco efectivo real es una liquidez ilusoria.
3. Contrasta Ratio Corriente, Prueba Ácida y Prueba Defensiva entre sí — si divergen mucho, la causa (inventario, cuentas por cobrar) es el hallazgo, no el ratio en sí.
4. Revisa la proporción de Pasivo Corriente vs. No Corriente — deuda de corto plazo alta en un entorno de doble moneda es un riesgo distinto a deuda de largo plazo.
5. Determina si el Patrimonio creció o se erosionó en el trimestre, y si ese cambio viene de resultado operativo o de un ajuste de balance.

[OUTPUT — memo ejecutivo de junta, sin títulos decorativos, sin numeración visible, sin lenguaje de reporte]
Párrafo 1 — CAMBIO ESTRUCTURAL DEL TRIMESTRE: La variación más severa en la estructura de capital, contra el trimestre anterior.
Párrafo 2 — CALIDAD DE LA LIQUIDEZ: Composición real del Activo Corriente — cuánto es efectivo disponible de verdad, contrastando los 3 ratios de liquidez entre sí.
Párrafo 3 — PERFIL DE DEUDA: Corriente vs. No Corriente, y qué implica para los próximos 90 días.
Párrafo 4 — SEÑAL ADELANTADA: Qué anticipa esta estructura de balance para el próximo trimestre si la tendencia continúa.
Párrafo 5 — LA DECISIÓN: Una acción sobre estructura de balance que los datos sostienen, con consecuencia de no tomarla, con pasos concretos.
Párrafo 6 — GAP DE INFORMACIÓN: Solo si es relevante.

[RESTRICCIONES — integradas al proceso]
No describas qué compone el activo/pasivo — diagnostica si esa composición es sana. No trates el tamaño nominal del balance como indicador de salud sin mirar composición. No compares contra trimestres no consecutivos sin declarar por qué. No uses: "se puede observar", "es importante destacar", "los resultados muestran", "cabe mencionar", "en conclusión". No entregues estrategia genérica de gestión de balance aplicable a cualquier empresa.

[DATOS]
"""

PROMPT_ESF_DIVISA_REAL_DEFAULT = """[IDENTIDAD]
CFO especializado en gestión de liquidez real en entornos de doble moneda. Tu foco es un subconjunto acotado y específico del balance — no el balance completo. La diplomacia es un defecto aquí. El tono es frío y preciso.

[CONTEXTO DEL NEGOCIO]
Este corte NO es el balance completo — es la revalorización a tasa paralela de un subconjunto específico de cuentas altamente líquidas o de corto plazo: caja, bancos, impuestos pagados por anticipado, retenciones e impuestos por pagar (45 cuentas exactas, definidas por el sistema). El resto del balance (más de 120 cuentas — inventario, activo fijo, cuentas por cobrar) permanece en su valor nominal en bolívares y NO está en estos datos. No trates el "Saldo Total" de este corte como si fuera el Total de Activos del grupo — son magnitudes de escala completamente distinta y no comparables entre sí.

[CONTRATO CON EL LECTOR]
Quien lee esto ya conoce el balance completo en bolívares. Lo que necesita de este corte específico es una pregunta puntual: de la posición de efectivo y obligaciones de corto plazo, ¿cuánto vale en dólares reales, y ese valor real está creciendo o encogiéndose trimestre contra trimestre?

[ESTÁNDAR DE EVIDENCIA]
Un solo trimestre no permite conclusión de tendencia — se necesita comparación explícita contra el trimestre anterior con datos disponibles. Si solo hay un trimestre con datos, decláralo y limita la conclusión a una fotografía, no a una trayectoria.

[MARCO ANALÍTICO — proceso interno, no visible en el output]
1. Ubica el Saldo Total en dólares (paralelo) de este trimestre — esa es la cifra central, no el Saldo Total en bolívares, que no tiene significado comparativo por sí solo en un entorno inflacionario.
2. Si hay trimestre anterior con datos, compara el valor real (USD) entre ambos — ¿la posición líquida real creció, se mantuvo, o se erosionó?
3. Dentro de las partidas, distingue cuánto es efectivo/bancos puro (lo más líquido) de cuánto son impuestos por pagar o retenciones (obligaciones, no disponibilidad real) — una posición "alta" dominada por impuestos por pagar no es la misma noticia que una dominada por caja disponible.
4. Si la tasa paralela no estaba cargada para algún mes del trimestre, decláralo — afecta la precisión de la cifra final.

[OUTPUT — memo ejecutivo de junta, sin títulos decorativos, sin numeración visible, sin lenguaje de reporte]
Párrafo 1 — POSICIÓN LÍQUIDA REAL: El Saldo Total en dólares reales de este trimestre, y qué tan disponible (caja/bancos) vs. comprometida (obligaciones) es esa cifra.
Párrafo 2 — TRAYECTORIA: Comparación contra el trimestre anterior si hay datos disponibles — creció, se mantuvo, o se erosionó en términos reales. Si no hay comparación posible, decláralo explícitamente.
Párrafo 3 — LA DECISIÓN: Si la posición líquida real amerita una acción (ej. ajustar el ritmo de canje de divisas, revisar el calendario de pagos de impuestos), cuál es y su consecuencia de no tomarla.
Párrafo 4 — GAP DE INFORMACIÓN: Solo si es relevante — especialmente si falta tasa paralela de algún mes del trimestre.

[RESTRICCIONES — integradas al proceso]
No compares el Saldo Total de este corte contra el Total de Activos del balance completo — son magnitudes no comparables por diseño, uno es un subconjunto de 45 cuentas, el otro es el balance entero. No trates este corte como diagnóstico de la salud patrimonial completa del grupo — es exclusivamente sobre posición líquida de corto plazo en términos reales. No uses: "se puede observar", "es importante destacar", "los resultados muestran", "cabe mencionar", "en conclusión".

[DATOS]
"""

PROMPT_COMPARATIVO_DIVISA_MES_DEFAULT = """[IDENTIDAD]
CFO especializado en descomposición de brechas de rendimiento entre unidades del mismo modelo de negocio, en poder adquisitivo real. La diplomacia es un defecto aquí. El tono es frío y preciso.

[CONTEXTO DEL NEGOCIO]
Unidades de retail deportivo premium comparadas en un mes puntual, ya ajustadas a valor real por el sistema — sin ruido cambiario nominal mezclado. No necesitas separar cambiario de operativo antes de comparar: las cifras ya están en la misma base real, lo que hace la comparación entre unidades más limpia que en BCV, donde el efecto cambiario nominal puede distorsionar diferencias de tamaño.

[CONTRATO CON EL LECTOR]
Quien lee esto ya sabe qué unidad vendió más en bolívares. Necesita saber si esa diferencia se sostiene en términos de poder adquisitivo real, o si es una ilusión nominal — dos unidades pueden verse muy distintas en bolívares y casi iguales en dólares reales, o al revés.

[ESTÁNDAR DE EVIDENCIA]
Normaliza todas las métricas antes de comparar (márgenes en %, no montos absolutos). Una brecha nominal grande que se reduce a casi nada en términos reales es en sí misma un hallazgo relevante — decláralo explícitamente si ocurre.

[MARCO ANALÍTICO — proceso interno]
1. Normaliza las métricas del subconjunto seleccionado en términos reales.
2. Identifica si el ranking de desempeño real coincide con el ranking nominal en bolívares — si difiere, esa discrepancia es el hallazgo principal.
3. Descompón la brecha real entre la unidad líder y las rezagadas: mix, volumen, margen — ya sin necesidad de descontar efecto cambiario, que está fuera de estos datos.
4. Determina si la brecha real es corregible en 30 días o es estructural.

[OUTPUT]
Si el ranking real difiere del ranking nominal en bolívares, decláralo como hallazgo principal. Descomposición de la brecha real (mix, volumen, margen) entre la unidad líder y las rezagadas. Corregible vs. estructural por unidad. Una acción por unidad rezagada con mayor consecuencia, con pasos ejecutables. Gap de información crítico si existe. Sin re-separar cambiario/operativo. Sin comparar montos absolutos sin normalizar.

[DATOS]
"""

PROMPT_COMPARATIVO_DIVISA_ANUAL_DEFAULT = """[IDENTIDAD]
CFO con visión de portafolio, descomposición de brechas de rendimiento entre unidades a nivel de cierre anual, en poder adquisitivo real. La diplomacia es un defecto aquí. El tono es frío y preciso.

[CONTEXTO DEL NEGOCIO]
Unidades comparadas sobre 12 meses de datos ya ajustados a valor real por el sistema. La pregunta de este corte: a lo largo del año, ¿la brecha real entre unidades se amplió, se mantuvo, o se cerró — y ese patrón real coincide con lo que muestran los bolívares nominales?

[CONTRATO CON EL LECTOR]
El lector dirige las finanzas del grupo. Necesita saber si la trayectoria de la unidad rezagada, en términos reales, es de recuperación o de deterioro sostenido — una pregunta que los bolívares nominales, con inflación estructural de por medio, pueden estar respondiendo mal.

[ESTÁNDAR DE EVIDENCIA]
Normaliza antes de comparar. Una tendencia de un solo trimestre real es hipótesis, no patrón — rastrea la evolución completa del año.

[MARCO ANALÍTICO — proceso interno]
1. Normaliza las métricas del año en términos reales.
2. Rastrea la evolución trimestral de la brecha real entre la unidad líder y cada rezagada.
3. Compara esa trayectoria real contra la trayectoria nominal en bolívares del mismo período — si divergen, esa divergencia es el hallazgo.
4. Determina si la trayectoria real de la unidad rezagada es de recuperación, estancamiento, o deterioro sostenido.

[OUTPUT]
El patrón de brecha real más relevante del año, y si coincide o diverge del patrón nominal en bolívares. Trayectoria real de cada unidad rezagada: recuperación, estancamiento o deterioro. La prioridad correctiva del próximo año por unidad, con pasos ejecutables. Gap de información crítico si existe. Sin re-separar cambiario/operativo. Sin resumen narrativo del año.

[DATOS]
"""


# ══════════════════════════════════════════════════════════════════════════════
# NUEVO SISTEMA DE MAPPING DESDE EXCEL REAL
# ══════════════════════════════════════════════════════════════════════════════

def classify_account(codigo: str) -> tuple:
    """
    Clasifica una cuenta según su código retornando (sign, income_type).

    Reglas:
    - 1.x → (1, None) [Activo]
    - 1.02.06.XX.500|.501 → (-1, None) [Dep/Det Acum - reducen activo]
    - 1.02.07.XX.500|.002 → (-1, None) [Amort Acum - reducen activo]
    - 2.x → (-1, None) [Pasivo]
    - 3.x → (-1, None) [Patrimonio]
    - 4.01.01.02.x | 4.01.01.03.x → (1, 'mercancia') [Devoluciones/descuentos]
    - 4.01.01.x → (1, 'mercancia')
    - 4.01.02.x → (1, 'servicios')
    - 4.01.03.x → (1, 'eventos')
    - 4.01.04.x → (1, 'taller')
    - 4.02.x → (1, None) [Ingresos no operativos]
    - 5.01.01.x → (-1, 'mercancia')
    - 5.01.02.x → (-1, 'servicios')
    - 5.01.03.x → (-1, 'eventos')
    - 5.01.04.x → (-1, 'taller')
    - 6.x → (-1, None) [Gastos]
    """

    # Cuentas de activo con depreciación/deterioro/amortización acumulada (reducen el activo)
    if re.match(r'^1\.02\.06\.\d+\.(500|501)$', codigo):
        return (1, None)
    if re.match(r'^1\.02\.07\.\d+\.(500|002)$', codigo):
        return (1, None)

    # Devoluciones y descuentos sobre ventas (reducen ingresos)
    if codigo.startswith('4.01.01.02.') or codigo.startswith('4.01.01.03.'):
        return (1, 'mercancia')

    # Ingresos operativos por tipo
    if codigo.startswith('4.01.01.'):
        return (1, 'mercancia')
    if codigo.startswith('4.01.02.'):
        return (1, 'servicios')
    if codigo.startswith('4.01.03.'):
        return (1, 'eventos')
    if codigo.startswith('4.01.04.'):
        return (1, 'taller')

    # Ingresos no operativos
    if codigo.startswith('4.02.'):
        return (1, None)

    # Costos de venta por tipo
    if codigo.startswith('5.01.01.'):
        return (-1, 'mercancia')
    if codigo.startswith('5.01.02.'):
        return (-1, 'servicios')
    if codigo.startswith('5.01.03.'):
        return (-1, 'eventos')
    if codigo.startswith('5.01.04.'):
        return (-1, 'taller')

    # Clasificación genérica por primer dígito
    first = codigo[0] if codigo else ''
    if first == '1':
        return (1, None)   # Activo
    if first == '2':
        return (-1, None)  # Pasivo
    if first == '3':
        return (-1, None)  # Patrimonio
    if first == '4':
        return (1, None)   # Ingresos (catch-all)
    if first == '5':
        return (-1, None)  # Costos (catch-all)
    if first == '6':
        return (-1, None)  # Gastos

    # Default seguro
    return (-1, None)


def load_mapping_from_excel(excel_path='Cuenta (account.account) (5).xlsx'):
    """
    Setup opcional de una sola vez: lee un plan de cuentas de Odoo en Excel y
    genera el INITIAL_MAPPING para sembrar la tabla `mapping` desde cero.
    No forma parte del arranque normal de la app -- el mapping real vive en
    la tabla `mapping` de SQLite y se administra desde la pantalla Mapeo de
    Cuentas. Sin el archivo de origen (caso normal en desarrollo/producción),
    retorna lista vacía sin bloquear el arranque.
    Retorna lista de tuplas: (odoo_code, odoo_name, partida, sign, income_type)
    """
    try:
        import pandas as pd
    except ImportError:
        return []

    excel_full_path = os.path.join(os.path.dirname(__file__), excel_path)

    if not os.path.exists(excel_full_path):
        # Esperado: este archivo de origen no vive en el proyecto salvo que se
        # esté re-sembrando el mapping desde cero a propósito.
        return []

    try:
        df = pd.read_excel(excel_full_path, engine='openpyxl')
    except Exception as e:
        print(f"[WARN]  Error leyendo Excel: {e}")
        return []

    # Normalizar nombres de columnas
    df.columns = ['codigo', 'moneda', 'nombre']
    df['codigo'] = df['codigo'].astype(str).str.strip()
    df['nombre'] = df['nombre'].astype(str).str.strip()

    # Filtrar solo cuentas operativas (nivel 5: X.XX.XX.XX.XXX)
    # Incluye también niveles 3 y 4 para cuentas que no tienen subdivisión
    df_cuentas = df[df['codigo'].str.match(r'^\d+\.\d+', na=False)]

    mapping = []
    for _, row in df_cuentas.iterrows():
        codigo = row['codigo']
        nombre = row['nombre']

        # Saltar registros vacíos o inválidos
        if not codigo or codigo == 'nan' or not nombre or nombre == 'nan':
            continue

        sign, income_type = classify_account(codigo)

        # (odoo_code, odoo_name, partida, sign, income_type)
        mapping.append((codigo, nombre, nombre, sign, income_type))

    print(f"[OK] {len(mapping)} cuentas cargadas desde {excel_path}")
    return mapping


# Generar INITIAL_MAPPING desde el Excel (setup opcional, ver load_mapping_from_excel)
INITIAL_MAPPING = load_mapping_from_excel()

# Sin archivo de origen, queda vacío -- comportamiento normal y esperado
# (el mapping real ya vive en la tabla `mapping`, administrado desde la
# pantalla Mapeo de Cuentas). reset_mapping() solo es necesario si se quiere
# re-sembrar el mapping desde un Excel nuevo.
if not INITIAL_MAPPING:
    INITIAL_MAPPING = []


# ══════════════════════════════════════════════════════════════════════════════
# GRUPOS INICIALES DE PRESENTACIÓN
# ══════════════════════════════════════════════════════════════════════════════

INITIAL_GROUPS = [
    # (group_name, odoo_code, report_type, display_order)

    # EERR - Gastos de mantenimiento
    ('Mantenimiento y reparaciones', '6.01.01.02.001', 'eerr', 10),
    ('Mantenimiento y reparaciones', '6.01.01.02.002', 'eerr', 10),
    ('Mantenimiento y reparaciones', '6.01.01.02.003', 'eerr', 10),
    ('Mantenimiento y reparaciones', '6.01.01.02.004', 'eerr', 10),
    ('Mantenimiento y reparaciones', '6.01.01.02.005', 'eerr', 10),

    # EERR - Viáticos administrativos
    ('Viáticos administrativos', '6.01.01.03.001', 'eerr', 20),
    ('Viáticos administrativos', '6.01.01.03.002', 'eerr', 20),
    ('Viáticos administrativos', '6.01.01.03.003', 'eerr', 20),
    ('Viáticos administrativos', '6.01.01.03.004', 'eerr', 20),
    ('Viáticos administrativos', '6.01.01.03.005', 'eerr', 20),

    # EERR - Gastos de seguro
    ('Gastos de seguro', '6.01.01.04.001', 'eerr', 30),
    ('Gastos de seguro', '6.01.01.04.002', 'eerr', 30),
    ('Gastos de seguro', '6.01.01.04.003', 'eerr', 30),
    ('Gastos de seguro', '6.01.01.04.004', 'eerr', 30),

    # EERR - Impuestos, tasas y contribuciones
    ('Gastos de impuestos, tasas y contribuciones', '6.01.01.05.001', 'eerr', 40),
    ('Gastos de impuestos, tasas y contribuciones', '6.01.01.05.002', 'eerr', 40),
    ('Gastos de impuestos, tasas y contribuciones', '6.01.01.05.003', 'eerr', 40),
    ('Gastos de impuestos, tasas y contribuciones', '6.01.01.05.004', 'eerr', 40),
    ('Gastos de impuestos, tasas y contribuciones', '6.01.01.05.005', 'eerr', 40),
    ('Gastos de impuestos, tasas y contribuciones', '6.01.01.05.006', 'eerr', 40),
    ('Gastos de impuestos, tasas y contribuciones', '6.01.01.05.007', 'eerr', 40),

    # EERR - Depreciaciones (agrupadas)
    ('Depreciaciones, deterioro y Amortización', '6.01.01.06.001', 'eerr', 50),
    ('Depreciaciones, deterioro y Amortización', '6.01.01.06.002', 'eerr', 50),
    ('Depreciaciones, deterioro y Amortización', '6.01.01.06.003', 'eerr', 50),
    ('Depreciaciones, deterioro y Amortización', '6.01.01.06.004', 'eerr', 50),
    ('Depreciaciones, deterioro y Amortización', '6.01.01.07.001', 'eerr', 50),
    ('Depreciaciones, deterioro y Amortización', '6.01.01.07.002', 'eerr', 50),
    ('Depreciaciones, deterioro y Amortización', '6.01.01.07.003', 'eerr', 50),
    ('Depreciaciones, deterioro y Amortización', '6.01.01.07.004', 'eerr', 50),
    ('Depreciaciones, deterioro y Amortización', '6.01.01.07.005', 'eerr', 50),
    ('Depreciaciones, deterioro y Amortización', '6.01.01.08.001', 'eerr', 50),

    # EERR - Gastos bancarios
    ('Gastos Bancarios', '6.01.01.09.001', 'eerr', 60),
    ('Gastos Bancarios', '6.01.01.09.002', 'eerr', 60),

    # EERR - Gastos de intereses
    ('Gastos de intereses sobre préstamos', '6.01.01.10.001', 'eerr', 70),
    ('Gastos de intereses sobre préstamos', '6.01.01.10.002', 'eerr', 70),
    ('Gastos de intereses sobre préstamos', '6.01.01.10.003', 'eerr', 70),
]


# ══════════════════════════════════════════════════════════════════════════════
# DATABASE FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def get_db():
    if 'db' not in g.__dict__:
        conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA busy_timeout=30000')
        g.db = conn
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def _crear_tabla_briefing_prompts(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS briefing_prompts (
            tipo_reporte TEXT PRIMARY KEY,
            prompt_text TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )
    """)

    prompts_default = {
        "consolidado": PROMPT_CONSOLIDADO_DEFAULT,
        "unidad_mes": PROMPT_UNIDAD_MES_DEFAULT,
        "anual": PROMPT_ANUAL_DEFAULT,
        "comparativo_mes": PROMPT_COMPARATIVO_MES_DEFAULT,
        "comparativo_anual": PROMPT_COMPARATIVO_ANUAL_DEFAULT,
    }

    for tipo, texto in prompts_default.items():
        conn.execute("""
            INSERT OR IGNORE INTO briefing_prompts (tipo_reporte, prompt_text)
            VALUES (?, ?)
        """, (tipo, texto))

    conn.commit()

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    conn.executescript('''
        CREATE TABLE IF NOT EXISTS mapping (
            odoo_code   TEXT PRIMARY KEY,
            odoo_name   TEXT NOT NULL,
            partida     TEXT NOT NULL,
            sign        INTEGER NOT NULL DEFAULT -1,
            income_type TEXT DEFAULT NULL
        );
        CREATE TABLE IF NOT EXISTS financials (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            year    TEXT NOT NULL,
            month   TEXT NOT NULL,
            unit    TEXT NOT NULL,
            partida TEXT NOT NULL,
            amount  REAL NOT NULL DEFAULT 0,
            UNIQUE(year, month, unit, partida)
        );
        CREATE INDEX IF NOT EXISTS idx_fin ON financials(year, month, unit);
        CREATE TABLE IF NOT EXISTS esf_data (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            year      TEXT NOT NULL,
            quarter   INTEGER NOT NULL,
            unit      TEXT NOT NULL,
            partida   TEXT NOT NULL,
            amount    REAL NOT NULL DEFAULT 0,
            UNIQUE(year, quarter, unit, partida)
        );
        CREATE INDEX IF NOT EXISTS idx_esf ON esf_data(year, quarter, unit);
        CREATE TABLE IF NOT EXISTS budget (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            year    TEXT NOT NULL,
            month   TEXT NOT NULL,
            unit    TEXT NOT NULL,
            partida TEXT NOT NULL,
            amount  REAL NOT NULL DEFAULT 0,
            UNIQUE(year, month, unit, partida)
        );
        CREATE INDEX IF NOT EXISTS idx_budget ON budget(year, month, unit);
        CREATE TABLE IF NOT EXISTS history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            year        TEXT NOT NULL,
            month       TEXT NOT NULL,
            unit        TEXT NOT NULL,
            inserted    INTEGER NOT NULL DEFAULT 0,
            reverted    INTEGER NOT NULL DEFAULT 0,
            created_at  TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS mapping_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            action      TEXT NOT NULL,
            odoo_code   TEXT NOT NULL,
            odoo_name   TEXT,
            partida     TEXT,
            sign        INTEGER,
            income_type TEXT,
            created_at  TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS tasas_periodo (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            year                    TEXT NOT NULL,
            month                   TEXT NOT NULL,
            tasa_bcv_inicio         REAL NOT NULL,
            tasa_bcv_fin            REAL NOT NULL,
            tasa_bcv_promedio       REAL NOT NULL,
            tasa_paralela_inicio    REAL NOT NULL,
            tasa_paralela_fin       REAL NOT NULL,
            tasa_paralela_promedio  REAL NOT NULL,
            factor_diferencial      REAL NOT NULL,
            factor_recargo          REAL NOT NULL DEFAULT 1.35,
            created_at              TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            UNIQUE(year, month)
        );
        CREATE TABLE IF NOT EXISTS metodo_pago_cuenta (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            year            TEXT NOT NULL,
            month           TEXT NOT NULL,
            unit            TEXT NOT NULL,
            odoo_code       TEXT NOT NULL,
            pct_cash        REAL NOT NULL DEFAULT 0 CHECK(pct_cash >= 0 AND pct_cash <= 100),
            created_at      TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            UNIQUE(year, month, unit, odoo_code)
        );

        CREATE TABLE IF NOT EXISTS dashboard_config (
            username TEXT PRIMARY KEY,
            config_json TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS esf_divisa_real_overrides (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            year            TEXT NOT NULL,
            quarter         INTEGER NOT NULL,
            odoo_code       TEXT NOT NULL,
            valor_override  REAL NOT NULL,
            updated_at      TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            UNIQUE(year, quarter, odoo_code)
        );

        CREATE TABLE IF NOT EXISTS ganancia_perdida_divisa_override (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            year            TEXT NOT NULL,
            quarter         INTEGER NOT NULL,
            empresa_id      INTEGER,
            ganancia        REAL NOT NULL DEFAULT 0,
            perdida         REAL NOT NULL DEFAULT 0,
            updated_at      TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            UNIQUE(year, quarter, empresa_id)
        );

        CREATE TABLE IF NOT EXISTS esf_divisa_real_override_log (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            year            TEXT NOT NULL,
            quarter         INTEGER NOT NULL,
            odoo_code       TEXT NOT NULL,
            valor_anterior  REAL,
            valor_nuevo     REAL,
            timestamp       TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS validation_baselines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year TEXT NOT NULL,
            unit TEXT NOT NULL,
            month TEXT NOT NULL,
            partida TEXT NOT NULL,
            valor_esperado REAL NOT NULL,
            fecha_actualizacion TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            UNIQUE(year, unit, month, partida)
        );
    ''')

    _crear_tabla_briefing_prompts(conn)

    # ── Migración de BDs existentes ──────────────────────────────────────────
    # Añadir income_type a mapping si no existe
    cols = {r[1] for r in conn.execute("PRAGMA table_info(mapping)").fetchall()}
    if 'income_type' not in cols:
        conn.execute("ALTER TABLE mapping ADD COLUMN income_type TEXT DEFAULT NULL")
        print("Migración: columna income_type añadida a mapping")

    # Añadir income_type a mapping_log si no existe
    cols_log = {r[1] for r in conn.execute("PRAGMA table_info(mapping_log)").fetchall()}
    if 'income_type' not in cols_log:
        conn.execute("ALTER TABLE mapping_log ADD COLUMN income_type TEXT DEFAULT NULL")
        print("Migración: columna income_type añadida a mapping_log")

    # Añadir columnas inicio/fin a tasas_periodo si no existen
    cols_tasas = {r[1] for r in conn.execute("PRAGMA table_info(tasas_periodo)").fetchall()}
    if 'tasa_bcv_inicio' not in cols_tasas:
        conn.execute("ALTER TABLE tasas_periodo ADD COLUMN tasa_bcv_inicio REAL DEFAULT 0")
        conn.execute("ALTER TABLE tasas_periodo ADD COLUMN tasa_bcv_fin REAL DEFAULT 0")
        conn.execute("ALTER TABLE tasas_periodo ADD COLUMN tasa_paralela_inicio REAL DEFAULT 0")
        conn.execute("ALTER TABLE tasas_periodo ADD COLUMN tasa_paralela_fin REAL DEFAULT 0")
        print("Migración: columnas inicio/fin añadidas a tasas_periodo")

    # Migrar metodo_pago_cuenta de enum a porcentaje
    cols_metodo = {r[1] for r in conn.execute("PRAGMA table_info(metodo_pago_cuenta)").fetchall()}
    if 'metodo_pago' in cols_metodo and 'pct_cash' not in cols_metodo:
        conn.execute('''
            CREATE TABLE metodo_pago_cuenta_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year TEXT NOT NULL,
                month TEXT NOT NULL,
                unit TEXT NOT NULL,
                odoo_code TEXT NOT NULL,
                pct_cash REAL NOT NULL DEFAULT 0 CHECK(pct_cash >= 0 AND pct_cash <= 100),
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
                UNIQUE(year, month, unit, odoo_code)
            )
        ''')
        conn.execute('''
            INSERT INTO metodo_pago_cuenta_new (id, year, month, unit, odoo_code, pct_cash, created_at)
            SELECT id, year, month, unit, odoo_code,
                   CASE metodo_pago
                       WHEN 'usd_cash' THEN 100
                       WHEN 'bcv' THEN 0
                       WHEN 'ingreso_bs' THEN 0
                       ELSE 0
                   END,
                   created_at
            FROM metodo_pago_cuenta
        ''')
        conn.execute("DROP TABLE metodo_pago_cuenta")
        conn.execute("ALTER TABLE metodo_pago_cuenta_new RENAME TO metodo_pago_cuenta")
        print("Migración: metodo_pago_cuenta convertido de enum a pct_cash")

    # ── Seed / upsert del mapping inicial ────────────────────────────────────
    if INITIAL_MAPPING:
        conn.executemany(
            '''INSERT INTO mapping (odoo_code, odoo_name, partida, sign, income_type)
               VALUES (?,?,?,?,?)
               ON CONFLICT(odoo_code) DO UPDATE SET
                   odoo_name=excluded.odoo_name,
                   partida=excluded.partida,
                   sign=excluded.sign,
                   income_type=excluded.income_type''',
            INITIAL_MAPPING
        )
        print(f"[OK] {len(INITIAL_MAPPING)} cuentas insertadas/actualizadas en mapping")

    conn.commit()
    conn.close()
    print(f"DB inicializada en {DB_PATH}")


def migrate_db():
    """Ejecutar migraciones sobre BD existente sin reinicializar datos."""
    conn = sqlite3.connect(DB_PATH)

    cols = {r[1] for r in conn.execute("PRAGMA table_info(mapping)").fetchall()}
    if 'income_type' not in cols:
        conn.execute("ALTER TABLE mapping ADD COLUMN income_type TEXT DEFAULT NULL")

    cols_log = {r[1] for r in conn.execute("PRAGMA table_info(mapping_log)").fetchall()}
    if 'income_type' not in cols_log:
        conn.execute("ALTER TABLE mapping_log ADD COLUMN income_type TEXT DEFAULT NULL")

    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}

    if 'esf_data' not in tables:
        conn.execute('''CREATE TABLE esf_data (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            year    TEXT NOT NULL,
            quarter INTEGER NOT NULL,
            unit    TEXT NOT NULL,
            partida TEXT NOT NULL,
            amount  REAL NOT NULL DEFAULT 0,
            UNIQUE(year, quarter, unit, partida)
        )''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_esf ON esf_data(year, quarter, unit)')

    if 'budget' not in tables:
        conn.execute('''CREATE TABLE budget (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            year    TEXT NOT NULL,
            month   TEXT NOT NULL,
            unit    TEXT NOT NULL,
            partida TEXT NOT NULL,
            amount  REAL NOT NULL DEFAULT 0,
            UNIQUE(year, month, unit, partida)
        )''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_budget ON budget(year, month, unit)')

    conn.execute('DROP TABLE IF EXISTS esf_ajuste_diferencial')

    if 'esf_divisa_real_overrides' not in tables:
        conn.execute('''CREATE TABLE esf_divisa_real_overrides (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            year            TEXT NOT NULL,
            quarter         INTEGER NOT NULL,
            odoo_code       TEXT NOT NULL,
            valor_override  REAL NOT NULL,
            updated_at      TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            UNIQUE(year, quarter, odoo_code)
        )''')

    if 'esf_divisa_real_override_log' not in tables:
        conn.execute('''CREATE TABLE esf_divisa_real_override_log (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            year            TEXT NOT NULL,
            quarter         INTEGER NOT NULL,
            odoo_code       TEXT NOT NULL,
            valor_anterior  REAL,
            valor_nuevo     REAL,
            timestamp       TEXT NOT NULL
        )''')

    if 'briefing_prompts' not in tables:
        _crear_tabla_briefing_prompts(conn)

    conn.execute('DROP TABLE IF EXISTS esf_upload_history')

    if 'empresas' not in tables:
        conn.execute('''CREATE TABLE empresas (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_corto    TEXT NOT NULL UNIQUE,
            nombre_legal    TEXT NOT NULL,
            color           TEXT NOT NULL,
            created_at      TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )''')
        conn.execute('''INSERT INTO empresas (nombre_corto, nombre_legal, color) VALUES
            ('Ultrabikex Holding', 'Ultrabikex Holding (consolidado)', 'var(--tx)'),
            ('Ultrax C.A.', 'Ultrax C.A.', 'var(--blue)'),
            ('Ultrabikex C.A.', 'Ultrabikex C.A.', 'var(--mu)'),
            ('UxBarinas C.A.', 'UxBarinas C.A.', 'var(--indigo)'),
            ('Grupo Ultra2000 C.A.', 'Grupo Ultra2000 C.A.', 'var(--teal)')
        ''')

    if 'unidades' not in tables:
        conn.execute('''CREATE TABLE unidades (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre          TEXT NOT NULL UNIQUE,
            empresa_id      INTEGER NOT NULL,
            created_at      TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (empresa_id) REFERENCES empresas(id)
        )''')
        conn.execute('''INSERT INTO unidades (nombre, empresa_id) VALUES
            ('Rodeo', 2),
            ('PiedeMonte', 2),
            ('Terracota', 2),
            ('Ucafe', 2),
            ('Barinas', 2),
            ('Naranjos', 2)
        ''')

    cols_esf = {r[1] for r in conn.execute("PRAGMA table_info(esf_data)").fetchall()}
    if 'empresa_id' not in cols_esf:
        conn.execute("ALTER TABLE esf_data ADD COLUMN empresa_id INTEGER DEFAULT NULL")
        conn.execute("UPDATE esf_data SET empresa_id = 2 WHERE unit = 'CONSOLIDADO' AND empresa_id IS NULL")

    cols_hist = {r[1] for r in conn.execute("PRAGMA table_info(history)").fetchall()}
    if 'empresa_id' not in cols_hist:
        conn.execute("ALTER TABLE history ADD COLUMN empresa_id INTEGER DEFAULT NULL")
        if 'is_esf' in cols_hist:
            conn.execute("UPDATE history SET empresa_id = 2 WHERE is_esf = 1 AND empresa_id IS NULL")



    # Actualizar income_type en registros existentes del mapping inicial
    if INITIAL_MAPPING:
        conn.executemany(
            '''UPDATE mapping SET income_type=? WHERE odoo_code=? AND income_type IS NULL''',
            [(row[4], row[0]) for row in INITIAL_MAPPING if row[4] is not None]
        )

    conn.commit()
    conn.close()
    print("Migración completada")


def reset_mapping():
    """
    [WARN]  USAR CON PRECAUCIÓN: Borra y recrea la tabla mapping con el plan de cuentas actual.
    Solo ejecutar UNA VEZ después de verificar INITIAL_MAPPING.

    Crea backup automático antes de borrar.
    """
    if not INITIAL_MAPPING:
        return {
            'error': 'INITIAL_MAPPING está vacío. Instala pandas/openpyxl y reinicia la app.',
            'ok': False
        }

    conn = sqlite3.connect(DB_PATH)

    # Backup de seguridad
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(backup_dir, exist_ok=True)
    backup_path = os.path.join(backup_dir, f'mapping_backup_{timestamp}.csv')

    # Exportar mapping actual
    old_mapping = conn.execute('SELECT * FROM mapping').fetchall()
    if old_mapping:
        import csv
        with open(backup_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['odoo_code', 'odoo_name', 'partida', 'sign', 'income_type'])
            writer.writerows(old_mapping)
        print(f"[OK] Backup guardado en: {backup_path}")

    # Borrar tabla
    conn.execute('DELETE FROM mapping')

    # Insertar nuevo mapping
    conn.executemany(
        '''INSERT INTO mapping (odoo_code, odoo_name, partida, sign, income_type)
           VALUES (?,?,?,?,?)''',
        INITIAL_MAPPING
    )

    conn.commit()
    conn.close()

    print(f"[OK] Mapping reseteado: {len(INITIAL_MAPPING)} cuentas insertadas")
    return {
        'ok': True,
        'inserted': len(INITIAL_MAPPING),
        'backup': backup_path,
        'old_count': len(old_mapping) if old_mapping else 0
    }



