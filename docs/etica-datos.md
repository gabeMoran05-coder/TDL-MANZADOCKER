# Declaración de ética y legalidad de datos · E2

Equipo: Emilio Rodrigo Ayala Reynoso y Karol Gabriel Morán Aréchiga. Revisión: 17 de noviembre de 2026 (Gabriel); actualización del 19 de noviembre de 2026 (Emilio): agregado DENUE por celda.

## Fuentes, condiciones y licencia

| Fuente | Condiciones y reutilización | Robots, frecuencia y riesgos |
|---|---|---|
| ASIPONA Manzanillo, Estadística Mensual | Estadísticas públicas usadas con atribución, URL y archivo original. E0 ya señala restricciones de los [términos de gob.mx](https://www.gob.mx/terminos). No se acredita una licencia abierta inequívoca para redistribución y explotación comercial. No se asigna una licencia elegida por el equipo a los informes. | Se verifica robots antes de cada descarga, con User-Agent identificable, pausa y reintentos acotados. E0 observó 404; la verificación E2 registra su propio estado. Un 404 no constituye permiso de copyright. Conservar diferencias de acumulados, revisiones y cuarentena; resolver el permiso de uso comercial antes de comercializar derivados de esa fuente. |
| Banxico SIE, SF43718 | La [salvedad de uso](https://www.banxico.org.mx/footer-es/salvedad-politicas-uso-banco-.html) permite reproducir/utilizar información con atribución y dirección del Banco. No se presenta como CC0. Se mantienen las condiciones del proveedor y sus [límites de consultas](https://www.banxico.org.mx/SieAPIRest/service/v1/doc/limiteConsultas). | API oficial con token en secret, nunca en URL ni repositorio. Una captura diaria. Promedios sobre días observados; fines de semana y cotizaciones no disponibles no se inventan. El FIX no equivale al precio pagado por cada cliente ni demuestra causalidad. |
| INEGI, DENUE Colima | [Términos de Libre Uso de la Información del INEGI](https://www.inegi.org.mx/inegi/terminos.html): permiten extracción, adaptación y uso comercial con crédito y metadatos, sin aparentar aval institucional. Fuente: INEGI, DENUE Colima. Se conserva el encabezado de edición del diccionario incluido en la descarga, la URL, el hash del ZIP y la fecha de captura. | [Descarga oficial](https://www.inegi.org.mx/contenidos/masiva/denue/denue_06_csv.zip) sin token; robots no prohíbe esa ruta en la revisión. Caché de siete días, mínimo dos segundos entre peticiones y reintentos acotados. No es un padrón de nuestros clientes ni prueba que las unidades tengan demanda de software. |

La revisión HTTP y robots se conserva con fecha real en [fuentes_web.json](../calidad/e2/fuentes_web.json). Un error o bloqueo no se interpreta como permiso. Las condiciones pueden cambiar; las capturas documentan únicamente el estado observado. Esta declaración no acredita autorización de ASIPONA aún pendiente ni cumplimiento legal absoluto.

## Privacidad y minimización antes de guardar Bronce

El ZIP y el CSV completo de DENUE se procesan exclusivamente en memoria. Se selecciona el municipio 007 de Colima y los subsectores SCIAN 484, 488 y 493. Antes de escribir Bronce se guardan solamente totales por celda de 0.01°. Se suprimen las celdas con menos de tres establecimientos y no se publican desgloses por categoría, para impedir su deducción por diferencia. Tampoco se guardan identificadores ni coordenadas individuales en la captura nueva.

La captura existente se derivó de la captura del 19/11/2026, conservando su fecha y el hash de la versión anterior; las copias con puntos y desgloses se retiraron de la versión actual. El historial de Git ya contiene las versiones anteriores y esta actualización no las elimina. El umbral reduce el riesgo de identificación, pero no garantiza anonimato frente a información externa ni frente a publicaciones anteriores.

Los escenarios del transportista usan agregados ingresados en sesión. No se escriben en archivos, se versionan ni se mandan a INEGI. Un futuro piloto requiere acuerdo sobre uso, acceso y conservación. Las entrevistas sin consentimiento confirmado no quedan autorizadas por esta declaración.

## Sesgos y límites

- **Selección:** el mapa muestra 608 establecimientos en 28 celdas. DENUE registra establecimientos, no empresas ni flota: un conteo alto no mide camiones, viajes ni demanda, y no sirve para estimar ingresos o empleo. El umbral k = 3 oculta 24 establecimientos en zonas poco densas, lo que subrepresenta la periferia.
- **Cobertura y actualización:** la fecha de ingesta es distinta de la edición del directorio y de la fecha de alta de un establecimiento. No se afirma que la captura describa altas o bajas de hoy. Se preservan el metadato de edición y el hash de la descarga.
- **Geografía:** el rectángulo 18.99–19.13 N y −104.36–−104.24 E y sus cuatro zonas son área de estudio, no límites oficiales de recinto, colonias o municipio. GeoPandas asigna cada centro de celda por intersección; conserva las celdas externas con esa condición indicada. Los centros no constituyen accesos viales autorizados ni rutas para camiones.
- **Temporalidad:** la captura geográfica es contexto actual. No se agrega a los meses históricos de 2021–2026 como variable predictora: eso induciría fuga temporal. El pronóstico TEU mensual no predice citas ni tiempos diarios de espera.
- **Economía:** TEU no equivale a servicios facturables ni ingresos. El simulador usa tarifas y costos que introduce el cliente, declara sus supuestos y no afirma ahorros observados. Evitar doble contabilización de espera y costos variables.

## Licencia, publicación y controles

Los datos DENUE seleccionados y sus derivados conservan la atribución al INEGI y los metadatos del proceso de selección: [aviso de datos](../data/bronce/denue/LICENCIA.md). Las adaptaciones se identifican como elaboración del equipo, sin afirmar que las respalda el INEGI. No se licencia todo el repositorio de forma uniforme ni se atribuye esta autorización a ASIPONA o Banxico.

El mapa base utiliza CARTO/OpenStreetMap. El comparador consulta OSRM/FOSSGIS solo al solicitar recorridos entre ubicaciones públicas del catálogo; envía coordenadas y conserva en sesion los costos e ingresos. No consulta INEGI por cada visitante. Las fuentes y sus condiciones se distinguen en docs/E2/mapa-costos.md. El linaje de Oro mantiene URL, fecha de ingesta, selectores y SHA-256; sus conjuntos amplios se declaran como tales.

## Fuente descartada y uso de IA

Se intentó OSM/Overpass. La instancia principal prohíbe `/api/` en robots; no se utilizó. La alternativa Private.coffee no respondió tras reintentos. No se publica una fuente ficticia: E2 usa DENUE real. Las consultas auxiliares de factibilidad no forman parte del producto. La asistencia de Codex para implementación y documentación se declara en `docs/relatoria-E2.md`.

## Ampliación del mapa y comparador

El catálogo cerrado de cinco organizaciones conserva etiquetas institucionales públicas elegidas expresamente; no nombres de personas ni datos de contacto. Las consultas OSRM utilizan solo esos puntos públicos. El proveedor registra peticiones; se limita a una por segundo por proceso y caché de 24 horas. El perfil es de automóvil y no valida accesos ni restricciones de carga. Los resultados de costos son escenarios del usuario y no cotizaciones verificadas. Detalle y fuentes: [mapa-costos.md](E2/mapa-costos.md).
