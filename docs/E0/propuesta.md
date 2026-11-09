# Propuesta E0 · Observatorio del Puerto de Manzanillo (TDL-MANZADOCKER)

**Equipo:** Emilio Rodrigo Ayala Reynoso · Karol Gabriel Morán Aréchiga
**Institución:** Instituto Tecnológico de Colima (TecNM) · Proyecto Integrador Trusted Data Lab
**Fecha:** 9 de noviembre de 2026 · **Etiqueta:** `e0`

> **En un minuto:** vamos a pronosticar cuántos contenedores (TEU) moverá el Puerto de Manzanillo cada mes y a demostrar en qué meses se concentra la actividad. Usamos los informes oficiales de ASIPONA Manzanillo (69 meses ya capturados, de enero de 2021 a septiembre de 2026) y el tipo de cambio diario de Banxico. Le sirve a quien tiene que planear camiones, choferes y citas en terminal: transportistas, líneas de autotransporte y agencias de logística.

---

## 1. Ficha del observatorio

| Campo | Contenido |
|---|---|
| Origen de la idea | Propuesta propia del equipo (no proviene del Banco de ideas) |
| Sector | Logística portuaria: movimiento de contenedores |
| Región | Puerto de Manzanillo, Colima (el puerto con más TEU del país) |
| Pregunta central | ¿Cuántos contenedores (TEU) moverá el Puerto de Manzanillo el próximo mes y en qué temporadas se concentra la actividad? |
| Quién paga por la respuesta | Líneas de autotransporte y agencias de logística que programan camiones, choferes y citas en terminal. _[Confirmar con la entrevista: quién decide y quién pagaría.]_ |
| Por qué pagaría | Un mes con más carga de la esperada significa camiones insuficientes, esperas largas y viajes perdidos; uno con menos carga significa unidades paradas. Saberlo con anticipación permite ajustar flota y turnos. |
| Modelo de negocio inicial | Reporte de inteligencia mensual por suscripción (pronóstico del mes siguiente con intervalo de confianza y comparativo por terminal). |

**Lo que ya muestran los datos** (capa bronce, cifras oficiales sin procesar):

- El puerto pasó de 3,371,438 TEU en 2021 a 3,924,501 en 2024 (+16.4%). En 2025 bajó ligeramente (3,893,357) y de enero a septiembre de 2026 suma 3,154,778 TEU, +9.5% contra el mismo periodo de 2025.
- El mes más bajo de la serie fue febrero de 2023 (251,937 TEU) y el más alto, julio de 2026 (384,691 TEU).
- El promedio por mes de calendario sugiere una temporada más alta en julio-agosto y una más baja en febrero. **Es una observación descriptiva, no un hallazgo**: se pondrá a prueba con la descomposición de la serie en E1.
- Dos terminales concentran la mayor parte del movimiento (SSA y CONTECON, alrededor de 85% en 2026), seguidas de OCUPA y TIMSA.

## 2. Entrevista con el sector

_[PENDIENTE — la realiza Gabriel el 9 de noviembre. Mínimo 15 minutos.]_

| Dato | Valor |
|---|---|
| Entrevistado | Entrevistado 1 · transportista _[independiente / de empresa]_, _[n]_ años operando en el puerto (anonimizado: sin nombre ni contacto) |
| Fecha, hora y duración | _[ ]_ |
| Medio | _[en persona / llamada]_ |
| Consentimiento | Se le explicó el proyecto y aceptó que se tomaran notas: _[sí/no]_ |

| # | Pregunta | Respuesta (resumen) | Lo que aprendimos |
|---|---|---|---|
| 0 | ¿Eres independiente o trabajas para una empresa? ¿Cuántos años llevas y con qué terminales trabajas más? | | |
| 1 | ¿Me puedes contar un caso reciente en el que hubo más o menos movimiento de carga del que esperaban? ¿Qué pasó en tu operación? | | |
| 2 | Cuando hay más carga, ¿qué cambia para ti (más viajes, más espera, otras tarifas)? ¿Con cuántos días de anticipación te serviría saberlo? | | |
| 3 | ¿Qué datos o señales consultas hoy para anticipar el volumen, cuáles te llegan tarde y qué tan seguido se equivocan? | | |
| 4 | Cuando se retrasa un viaje, ¿qué influye más: el volumen de carga, las citas en terminal, el clima u otro factor? | | |
| 5 | Si tuvieras un tablero para planear, ¿qué tendría que mostrar? ¿Mensual, semanal o por terminal? ¿Quién en tu gremio o empresa pagaría por saber esto con anticipación, y cuánto? | | |

**Conclusión de la entrevista:** _[cómo cambia o confirma la pregunta central y quién es el cliente que paga]_

## 3. Preguntas analíticas

| Técnica (entrega) | Pregunta medible | Datos |
|---|---|---|
| **Pronóstico (E1)** | ¿Cuántos TEU totales moverá el puerto en cada uno de los próximos 3 meses, con un intervalo de predicción del 95%? Gana el modelo (SES, Holt, Holt-Winters o SARIMA) con menor MAPE en los últimos 6 meses retenidos como prueba. | `teu_total` mensual, ene-2021 a sep-2026 (69 periodos). Correlación cruzada con los arribos mensuales de buques portacontenedores (misma fuente) y con el tipo de cambio FIX promedio mensual (Banxico). |
| **Experimento (E2), ruta ingeniería** | ¿Qué combinación de factores minimiza el tiempo de procesamiento y la tasa de error al extraer los PDF de la capa bronce? Diseño 2³ con al menos 2 réplicas y orden aleatorizado. Factores: A = número de procesos (1 vs 4), B = biblioteca de extracción de texto (pdfplumber vs pypdf), C = formato de salida (CSV vs Parquet). Respuestas: tiempo (s) y tasa de error (% de variables cuya suma no cuadra con el acumulado). | Copias locales de los PDF ya capturados; nunca contra el sitio de ASIPONA. Se incluye la biblioteca como factor porque, con un solo extractor, la tasa de error no variaría entre tratamientos. |
| **Multivariado (E3)** | ¿Las cuatro terminales (SSA, CONTECON, OCUPA, TIMSA) tienen perfiles de operación distintos cuando se consideran a la vez cinco variables mensuales? MANOVA con unidad de análisis terminal-mes. | Variables candidatas por terminal y mes: TEU totales, TEU de importación, de exportación, de transbordo y participación en el total del puerto. Los TEU totales por terminal ya están mes a mes; los de importación, exportación y transbordo vienen acumulados en el año y se obtendrán restando EM consecutivos. _[A confirmar en E1.]_ |

## 4. Plan de recopilación

| | Fuente 1 · ASIPONA Manzanillo | Fuente 2 · Banxico SIE |
|---|---|---|
| Qué es | Estadística Mensual (EM, formato ASPN-MAN-JES-F-05) de la Administración del Sistema Portuario Nacional Manzanillo | Serie SF43718, tipo de cambio FIX (pesos por dólar) |
| Estructura | Tabla de 2 páginas: conceptos en filas y ENE a DIC en columnas, más el acumulado del año, el del año anterior y la variación %. Se extraen 9 variables: TEU total, TEU por terminal (4), TEU por tráfico (impo, expo, transbordo de entrada y de salida; solo 2024 en adelante), toneladas contenerizadas y arribos de buques portacontenedores. | JSON `bmx.series[].datos[]` con `fecha` (dd/mm/aaaa) y `dato` (texto; "N/E" si no hay dato) |
| Formato | PDF con texto (no escaneado) | JSON por API REST |
| Frecuencia de actualización | Mensual. El EM de un mes se publica semanas después (el de septiembre de 2026 ya está publicado al 8 de noviembre). | Diaria, cada día hábil bancario |
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

| Componente | Estado al 8/11/2026 |
|---|---|
| `extractores/base.py` | Extractor ético del kit, adaptado: lee robots.txt con nuestro User-Agent, respeta Crawl-delay y pausa mínima, y reintenta ante 429/5xx |
| `extractores/asipona.py` | 6 PDF descargados (EM de diciembre 2021-2025 y de septiembre 2026) → `data/bronce/asipona/em_mensual.csv`, 648 registros con archivo y URL de origen y fecha de captura; metadatos y SHA-256 de cada PDF en `capturas.csv` |
| `extractores/banxico.py` | 1,472 días hábiles (4/1/2021 a 6/11/2026) → `data/bronce/banxico/tipo_cambio_fix.csv`, más la respuesta cruda de cada captura en `json/` |
| Serie histórica | **69 periodos mensuales** de TEU (mínimo pedido: 36) |
| Captura programada | `.github/workflows/captura.yml`: diaria a las 14:00 UTC (08:00 en Colima) y manual (`workflow_dispatch`); hace commit de `data/bronce` y de la bitácora. _[Actualizar con el enlace a la primera ejecución en GitHub Actions.]_ |
| Bitácora | `calidad/bitacora_captura.csv`: inicio, fin, duración, fuente, estado, registros, disparador y error de cada ejecución |

**Problemas de la fuente detectados al capturar** (alimentan la puerta de calidad de E1):
1. **Redondeo de la fuente:** en 13 combinaciones de variable y año, la suma de los meses difiere del acumulado que publica ASIPONA por 1 o 2 unidades. Se guarda la diferencia en la columna `diferencia`; no se corrige en bronce.
2. **Hueco en 2021:** el EM de diciembre de 2021 trae noviembre y diciembre en 0 para cada terminal, aunque el total del puerto sí tiene esos meses. No son ceros reales: se tratarán como faltantes en E1.
3. **Cifras revisadas:** el total de 2023 es 3,698,582 en su propio EM y 3,699,254 en el EM de 2024 y en el histórico. Habrá que decidir qué versión usar.
4. **Dígitos partidos:** el texto del PDF a veces separa el primer dígito (`2 70,603`). El extractor lo corrige y la verificación contra el acumulado confirma cada año (defecto 1 en `calidad/defectos-emilio.csv`).

## 6. Arranque del sistema de calidad

**Registros PSP individuales:** `calidad/defectos-emilio.csv`, `calidad/defectos-gabriel.csv`, `calidad/tiempo-emilio.csv` y `calidad/tiempo-gabriel.csv`, con el formato del kit.

**Objetivos de calidad medibles** (se miden en E1 con la bitácora del 9 al 16 de noviembre):

| # | Objetivo | Métrica | Meta | Cómo se mide |
|---|---|---|---|---|
| OC1 | Disponibilidad de la captura | Ejecuciones programadas exitosas ÷ ejecuciones programadas | **≥ 95%** | `calidad/bitacora_captura.csv` (filas con `disparador = schedule`) |
| OC2 | Exactitud de la extracción de PDF | % de combinaciones variable-año con \|suma de meses − acumulado reportado\| ≤ 2 | **100%** | Columna `diferencia` de `em_mensual.csv` (hoy: 100%, máximo de 2) |
| OC3 | Completitud de la serie principal | Meses con `teu_total` ÷ meses publicados desde ene-2021 | **100%** | `em_mensual.csv` (hoy: 69 de 69) |

Meta adicional para el plan SQA de E1: tiempo medio de reparación (MTTR) de una falla de captura **≤ 24 horas**.

## 7. Roles y reparto

| Integrante | Rol | E0 |
|---|---|---|
| Emilio Rodrigo Ayala Reynoso | Data Engineer | Repositorio, extractores, serie histórica, workflow y bitácora |
| Karol Gabriel Morán Aréchiga | Data Statistician | Entrevista, secret de la API y del workflow, revisión como Quality Lead |

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
