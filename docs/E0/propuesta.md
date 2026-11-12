# Propuesta E0 · Observatorio del Puerto de Manzanillo (TDL-MANZADOCKER)

**Equipo:** Emilio Rodrigo Ayala Reynoso · Karol Gabriel Morán Aréchiga
**Institución:** Instituto Tecnológico de Colima (TecNM) · Proyecto Integrador Trusted Data Lab
**Fecha:** 9 de noviembre de 2026 · **Etiqueta:** `e0` · **Rama de Gabriel:** `gabriel/e0`

> **En un minuto:** vamos a pronosticar el volumen de contenedores, expresado en TEU, que moverá el Puerto de Manzanillo cada mes y a demostrar en qué meses se concentra la actividad. Usamos los informes oficiales de ASIPONA (70 meses capturados, de enero de 2021 a octubre de 2026) y el tipo de cambio diario de Banxico. Le sirve a quien planea camiones y citas en terminal. Un TEU representa capacidad equivalente a un contenedor de 20 pies; no es un conteo de contenedores físicos.

---

## 1. Ficha del observatorio

| Campo | Contenido |
|---|---|
| Origen de la idea | Propuesta propia del equipo (no proviene del Banco de ideas) |
| Sector | Logística portuaria: movimiento de contenedores |
| Región | Puerto de Manzanillo, Colima |
| Pregunta central | ¿Cuántos contenedores (TEU) moverá el Puerto de Manzanillo el próximo mes y en qué temporadas se concentra la actividad? |
| Cliente potencial | Empresas de autotransporte de carga que operan en el Puerto de Manzanillo, tanto de carga federal (nacional) como de maniobras locales. Se entrevistó a un transportista nacional (entrevistado principal) y a una transportista local; sus nombres y contactos se omiten en el repositorio público. |
| Quién pagaría por la respuesta | La empresa transportista que planea flota y programaciones. Ninguno de los entrevistados confirmó una compra ni un monto; el nacional pidió información diaria para maniobras locales y la local pidió desglose por terminal. El precio queda pendiente de validar. |
| Motivo para contratar, como hipótesis | Complementar los avisos del cliente, que llegan uno o dos días antes, con contexto de actividad por terminal. Las citas y el tráfico son necesidades operativas señaladas; un pronóstico mensual de TEU no permite por sí solo predecir retrasos ni viajes de una empresa. |
| Modelo de negocio por validar | Reporte mensual o tablero por suscripción, con pronóstico e intervalo de predicción y comparativo por terminal. Precio, periodicidad preferida y disposición de pago pendientes. |

**Lo que ya muestran los datos** (capa bronce, cifras oficiales sin procesar):

- Los acumulados reportados por ASIPONA son 3,371,438 TEU en 2021, 3,924,501 en 2024 y 3,893,357 en 2025; de enero a octubre de 2026 reporta 3,483,498. Se distinguen del resultado de sumar las cifras mensuales, que presenta diferencias de hasta dos unidades (§5).
- El mes más bajo de la serie fue febrero de 2023 (251,937 TEU) y el más alto, julio de 2026 (384,691 TEU).
- El promedio por mes de calendario sugiere una temporada más alta en julio-agosto y una más baja en febrero. **Es una observación descriptiva, no un hallazgo**: se pondrá a prueba con la descomposición de la serie en E1.
- Dos terminales concentran la mayor parte del movimiento (SSA y CONTECON, alrededor de 85% en 2026), seguidas de OCUPA y TIMSA.

## 2. Entrevista con el sector

Se entrevistó a dos personas del sector con las mismas cinco preguntas. Por sugerencia del docente, **se usan como principales las respuestas del transportista nacional**. Este no respondió la pregunta 3 (dijo no entenderla), así que **para la pregunta 3 se usa la respuesta de la transportista local**, señalada como tal en la tabla. Las identidades y los datos de contacto se omiten.

| Dato | Entrevistado 2 · transportista nacional (principal) | Entrevistada 1 · transportista local (solo pregunta 3) |
|---|---|---|
| Perfil | Transportista de carga federal que también realiza maniobras locales en Manzanillo | Dueña de una transportista local en Manzanillo |
| Entrevistador | Karol Gabriel Morán Aréchiga | Karol Gabriel Morán Aréchiga |
| Fecha y hora | 10 de noviembre de 2026, alrededor de las 12:30 | 8 de noviembre de 2026, alrededor de las 16:50 |
| Medio | Mensajes de WhatsApp | Mensajes de WhatsApp |
| Duración | _[PENDIENTE: confirmar, mínimo 15 minutos]_ | 15 minutos |
| Consentimiento para usar notas anónimas | _[PENDIENTE: confirmar]_ | Sí |

| # | Pregunta | Respuesta (resumen) | Fuente | Lo que aprendimos |
|---|---|---|---|---|
| 1 | ¿Me puedes contar un caso reciente en el que hubo más o menos movimiento de carga del que esperaban? ¿Qué pasó en la operación de tu empresa? | Bajó la entrada de mercancía por mal tiempo en Asia (tifones en Japón, China, Corea): no llegaba mercancía, «no había importaciones». | Nacional | El volumen del puerto depende de eventos lejanos al origen de la carga, no solo de la demanda local. Una caída brusca en la serie puede ser real y no un error de datos; por eso los atípicos se marcan y no se borran. Falta ubicar con datos el mes al que se refiere. |
| 2 | Cuando esperan más movimiento, ¿qué cambian en camiones, turnos o programación y con cuánta anticipación necesitan saberlo? | Ajustan las programaciones; «no se sabe con cuánto tiempo de anticipación». | Nacional | La forma de reaccionar es reprogramar. Hoy no tienen un plazo de anticipación definido: un pronóstico con horizonte claro (1 a 3 meses) aporta algo que no tienen. |
| 3 | ¿Qué datos o señales consultan hoy para anticipar el volumen, cuáles les llegan tarde y qué tan seguido se equivocan? | El cliente avisa al transportista uno o dos días antes. | **Local** (el nacional no la entendió) | La única señal que reciben es de muy corto plazo. No se informaron otras fuentes ni una frecuencia de errores. |
| 4 | Cuando se retrasa un viaje, ¿qué influye más: el volumen de carga, las citas en terminal, el clima u otro factor? | El volumen de carga: cuando hay más despachos se acumula el tráfico y «se hace el relajo». | Nacional | El entrevistado relaciona más volumen con congestión. Es una hipótesis útil para el observatorio, no un hecho demostrado: nuestros datos no miden tráfico ni tiempos de espera. |
| 5 | Si tuvieras un tablero para planear la operación, ¿qué tendría que mostrar (mensual, semanal, por terminal) y cuánto valdría para ti o tu empresa? | Información diaria, «en el caso de los que hacemos maniobras locales». No respondió cuánto valdría. | Nacional | Para las maniobras locales se necesita detalle diario, y los datos oficiales del puerto son mensuales. El pronóstico mensual sirve para planear flota y contratos, no para la operación de cada día. El valor económico sigue sin respuesta. |

**Conclusión de la entrevista:** el transportista nacional confirma que el volumen del puerto cambia por causas externas (clima en Asia) y que, cuando sube, se congestiona la operación. Hoy reprograman sin saber con cuánta anticipación, y la única señal es el aviso del cliente con uno o dos días. Eso justifica un pronóstico mensual con intervalo como herramienta de planeación. A la vez, marca un límite honesto: para las maniobras locales piden información diaria, que el observatorio no puede dar con fuentes mensuales.

**Seguimiento pendiente:** cuánto pagaría y quién decide la contratación (ninguno de los dos entrevistados lo respondió con una cifra), y si un pronóstico semanal o mensual por terminal le serviría para planear.

## 3. Preguntas analíticas

| Técnica (entrega) | Pregunta medible | Datos |
|---|---|---|
| **Pronóstico (E1)** | ¿Cuántos TEU totales moverá el puerto en cada uno de los próximos 3 meses, con un intervalo de predicción del 95%? Gana el modelo (SES, Holt, Holt-Winters o SARIMA) con menor MAPE en los últimos 6 meses retenidos como prueba. | `teu_total` mensual, ene-2021 a oct-2026 (70 periodos). Correlación cruzada con los arribos mensuales de buques portacontenedores (misma fuente) y con el tipo de cambio FIX promedio mensual (Banxico). |
| **Experimento (E2), ruta ingeniería** | ¿Qué combinación de factores minimiza el tiempo de procesamiento y la tasa de error al extraer los PDF de la capa bronce? Diseño 2³ con al menos 2 réplicas y orden aleatorizado. Factores: A = número de procesos (1 vs 4), B = biblioteca de extracción de texto (pdfplumber vs pypdf), C = formato de salida (CSV vs Parquet). Respuestas: tiempo (s) y tasa de error (% de variables cuya suma no cuadra con el acumulado). | Copias locales de los PDF ya capturados; nunca contra el sitio de ASIPONA. Se incluye la biblioteca como factor porque, con un solo extractor, la tasa de error no variaría entre tratamientos. |
| **Multivariado (E3)** | ¿Las cuatro terminales (SSA, CONTECON, OCUPA, TIMSA) tienen perfiles de operación distintos cuando se consideran a la vez cinco variables mensuales? MANOVA con unidad de análisis terminal-mes. | Variables candidatas por terminal y mes: TEU totales, TEU de importación, de exportación, de transbordo y participación en el total del puerto. Los TEU totales por terminal ya están mes a mes; los de importación, exportación y transbordo vienen acumulados en el año y se obtendrán restando EM consecutivos. _[A confirmar en E1.]_ |

## 4. Plan de recopilación

| | Fuente 1 · ASIPONA Manzanillo | Fuente 2 · Banxico SIE |
|---|---|---|
| Qué es | Estadística Mensual (EM, formato ASPN-MAN-JES-F-05) de la Administración del Sistema Portuario Nacional Manzanillo | Serie SF43718, tipo de cambio FIX (pesos por dólar) |
| Estructura | Tabla de 2 páginas: conceptos en filas y ENE a DIC en columnas, más acumulados y variación %. Se extraen TEU totales, por terminal (4), por tráfico (importación, exportación, transbordo de entrada y de salida; desde 2024), toneladas contenerizadas y arribos de portacontenedores. Son hasta 11 conceptos según el año. | JSON `bmx.series[].datos[]` con `fecha` (dd/mm/aaaa) y `dato` (texto; "N/E" si no hay dato) |
| Formato | PDF con texto (no escaneado) | JSON por API REST |
| Frecuencia de actualización | Mensual, con retraso de publicación. La ejecución del 9 de noviembre descargó el EM de octubre de 2026. | Diaria, cada día hábil bancario |
| Método de acceso | Scraping de la página "Año <n>" para encontrar el EM más reciente, más un catálogo de URLs verificadas para 2021-2025; descarga con `extractores/asipona.py`, extracción de texto con pdfplumber | `GET /SieAPIRest/service/v1/series/SF43718/datos/{inicio}/{fin}` con encabezado `Bmx-Token` (token gratuito, guardado como secret de GitHub) |
| Página de origen | https://www.puertomanzanillo.com.mx/esps/0000209/estadisticas.html | https://www.banxico.org.mx/SieAPIRest/service/v1/ |
| robots.txt | `https://www.puertomanzanillo.com.mx/robots.txt` y la versión sin `www` responden **404** (verificado el 8/11/2026; captura de pantalla 18:38). Según RFC 9309, un 4xx significa que no hay restricciones declaradas. | `https://www.banxico.org.mx/robots.txt` prohíbe solo `/dyn`, `/ALEPH`, `/ALEPHcgi-bin/` y `/V`. La ruta `/SieAPIRest/` **está permitida** (verificado con el propio extractor). |
| Términos de uso | El pie del sitio enlaza a los términos generales de https://www.gob.mx/terminos (leídos el 8/11/2026). Autorizan a "visualizar y descargar los materiales … solamente para su uso personal y no para un uso comercial" y piden no "reproducir o mostrar pública o comercialmente los materiales, ni … distribuir". También señalan que cada dependencia responde por su información "de conformidad con sus propios términos". Nuestro uso es académico y sin fines de lucro, pero **publicar los PDF o el dataset derivado en un repositorio público requiere confirmación** (ver §8, riesgo 1). | La [Salvedad de uso](https://www.banxico.org.mx/footer-es/salvedad-politicas-uso-banco-.html) autoriza "de manera general" que la información "pueda reproducirse o utilizarse", con la condición de "mencionar la fuente … así como la dirección de Internet del Banco de México". El [Límite de consultas](https://www.banxico.org.mx/SieAPIRest/service/v1/doc/limiteConsultas) para datos históricos es de 200 consultas en 5 minutos y 10,000 por día por token; nosotros hacemos 1 al día. |
| Datos personales | Ninguno: solo cifras agregadas del puerto | Ninguno |
| Cómo nos comportamos | User-Agent honesto con la URL del repositorio, 2 s entre peticiones al mismo dominio, reintentos con espera exponencial; el PDF de un periodo ya guardado no se vuelve a descargar | 1 petición diaria (últimos 10 días); el histórico se descargó una sola vez |

**Fuentes descartadas:**
- **Open-Meteo** (clima): su `robots.txt` responde `Disallow: /` en `api.open-meteo.com` y en `archive-api.open-meteo.com`, y la regla del proyecto es buscar otra fuente.
- **Ingresos de camiones** (informe "RE"): solo vienen como etiquetas de una gráfica y su extracción es frágil. Se sustituyen por los arribos de buques, que vienen en la tabla EM.

## 5. Captura funcionando (capa bronce)

| Componente | Estado comprobado al 9/11/2026 |
|---|---|
| `extractores/base.py` | Extractor ético del kit, adaptado: lee robots.txt con nuestro User-Agent, respeta Crawl-delay y pausa mínima, y reintenta ante 429/5xx |
| `extractores/asipona.py` | 7 PDF descargados (diciembre 2021-2025, septiembre y octubre 2026). `data/bronce/asipona/em_mensual.csv` contiene 648 filas, incluidas posiciones aún no publicadas; cada fila tiene archivo, URL y fecha de captura. Metadatos y SHA-256 de los PDF en `capturas.csv`. |
| `extractores/banxico.py` | 1,473 fechas (4/1/2021 a 9/11/2026) en `data/bronce/banxico/tipo_cambio_fix.csv`, más las respuestas crudas en `json/`. |
| Serie histórica | **70 periodos mensuales publicados y consecutivos** de TEU (mínimo pedido: 36), sin duplicados de año-mes. |
| Captura programada | `.github/workflows/captura.yml`: diaria a las 14:00 UTC (08:00 en Colima) y manual. El secret `BANXICO_TOKEN` está configurado. [Primera ejecución manual exitosa, 9/11/2026](https://github.com/gabeMoran05-coder/TDL-MANZADOCKER/actions/runs/42679626943): ambas fuentes en estado `ok`; [commit del bot](https://github.com/gabeMoran05-coder/TDL-MANZADOCKER/commit/f126715). La primera ejecución con disparador `schedule` sigue pendiente de observar. |
| Bitácora | `calidad/bitacora_captura.csv`: inicio, fin, duración, fuente, estado, registros, disparador y error de cada ejecución |

**Problemas de la fuente detectados al capturar** (alimentan la puerta de calidad de E1):
1. **Discrepancias pequeñas de la fuente:** en 12 combinaciones de variable y año, la suma de los meses difiere del acumulado por 1 o 2 unidades en la captura actual. Se guarda `diferencia`; no se altera bronce ni se afirma una causa sin verificarla.
2. **Hueco en 2021:** el EM de diciembre de 2021 trae noviembre y diciembre en 0 para cada terminal, aunque el total del puerto sí tiene esos meses. No son ceros reales: se tratarán como faltantes en E1.
3. **Cifras revisadas:** el total de 2023 es 3,698,582 en su propio EM y 3,699,254 en el EM de 2024 y en el histórico. Habrá que decidir qué versión usar.
4. **Dígitos partidos:** el texto del PDF a veces separa el primer dígito (`2 70,603`). El extractor lo corrige y la verificación contra el acumulado confirma cada año (defecto 1 en `calidad/defectos-emilio.csv`).

## 6. Arranque del sistema de calidad

**Registros PSP individuales:** `calidad/defectos-emilio.csv`, `calidad/defectos-gabriel.csv`, `calidad/tiempo-emilio.csv` y `calidad/tiempo-gabriel.csv`, con el formato del kit.

El registro de tiempo de Gabriel incluye la entrevista por mensajes del 8 de noviembre, de 15 minutos, y el trabajo asistido en E0 del día 9. Para la entrevista, el fin aproximado de las 17:05 se calcula a partir del inicio aproximado de las 16:50 y la duración confirmada. El inicio de la sesión del día 9 y las interrupciones de ambas sesiones siguen pendientes en la [planeación y registro](planeacion-gabriel.md); no se calcula el tiempo efectivo sin esos datos. El registro de defectos permanece abierto, sin incidencias personales reportadas. Las fechas generales del proyecto corresponden a planeación, no a horas trabajadas.

**Objetivos de calidad medibles** (se miden en E1 con la bitácora del 9 al 16 de noviembre):

| # | Objetivo | Métrica | Meta | Cómo se mide |
|---|---|---|---|---|
| OC1 | Éxito de la captura programada | 100 × ejecuciones programadas con ambas fuentes en estado `ok` ÷ ejecuciones programadas iniciadas | **≥ 95%** | Historial de Actions y `calidad/bitacora_captura.csv`, agrupando ambas fuentes por ejecución con `disparador = schedule`. Si no hay ejecuciones, se informa «sin evidencia», no 100%. |
| OC2 | Conciliación de la extracción de PDF con tolerancia | % de combinaciones variable-año con \|suma de meses − acumulado reportado\| ≤ 2 | **100%** | Columna `diferencia` de `em_mensual.csv` (hoy: 100%, máximo de 2). La tolerancia no significa igualdad exacta. |
| OC3 | Completitud de la serie principal | 100 × meses con `teu_total` ÷ meses publicados desde ene-2021 | **100%** | `em_mensual.csv` (hoy: 70 de 70) |

Meta adicional para el plan SQA de E1: tiempo medio de reparación (MTTR) de una falla de captura **≤ 24 horas**.

## 7. Roles y reparto

| Integrante | Rol | E0 |
|---|---|---|
| Emilio Rodrigo Ayala Reynoso | Data Engineer | Repositorio, extractores, serie histórica, workflow y bitácora |
| Karol Gabriel Morán Aréchiga | Data Statistician | Entrevista y propuesta; rama `gabriel/e0`; coordinación de secret y ejecución de Actions; revisión como Quality Lead pendiente de realizar |

## 8. Riesgos

| Riesgo | Mitigación |
|---|---|
| 1. Los términos de gob.mx limitan la redistribución pública de los materiales y el repositorio es público | Consulta al Mtro. Román (ética y legalidad, tema 4.3). Opciones: (a) dejar de versionar los PDF crudos y conservar solo las URL, el SHA-256 y las cifras extraídas; (b) usar el conjunto de SEMAR en datos.gob.mx (CC BY 4.0), que hoy solo cubre de dic-2025 en adelante y cuyo servidor responde 403 a clientes automatizados. _[Decisión del equipo pendiente.]_ |
| ASIPONA cambia el formato del PDF o la URL de la página del año | La verificación contra el acumulado detecta la extracción rota; el catálogo fijo protege el histórico |
| El EM se publica con semanas de retraso | El pronóstico se plantea para el mes siguiente al último publicado; se documenta la latencia |
| Falla de GitHub Actions o de la API de Banxico | La bitácora registra la falla; se puede ejecutar a mano con `workflow_dispatch` |
| Exposición del token de Banxico | Solo como secret de GitHub o en `.env` (ignorado por git); gitleaks en E1 |

## 9. Uso de IA generativa

Se usó Claude Code (Anthropic) para: localizar y verificar las URL de los informes, revisar robots.txt, y redactar el código de los extractores, el workflow y este borrador. Todo se ejecutó y verificó en local antes de subirlo; el equipo revisó y puede explicar cada parte.

Para esta actualización se usó Codex (OpenAI) para clonar el repositorio, crear la rama de Gabriel, integrar sus respuestas, configurar el secret mediante la API de GitHub y comprobar una ejecución manual de Actions. También se verificaron conteos, continuidad mensual, metadatos, SHA-256 y enlaces locales. No se atribuye al asistente la realización de la entrevista ni una revisión cruzada de los integrantes.
