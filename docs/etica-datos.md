# Declaraci?n de ?tica y legalidad de datos ? E2

Equipo: Emilio Rodrigo Ayala Reynoso y Karol Gabriel Mor?n Ar?chiga. Revisi?n: 17 de noviembre de 2026.

## Fuentes, condiciones y licencia

| Fuente | Condiciones y reutilizaci?n | Robots, frecuencia y riesgos |
|---|---|---|
| ASIPONA Manzanillo, Estad?stica Mensual | Estad?sticas p?blicas usadas con atribuci?n, URL y archivo original. E0 ya se?ala restricciones de los [t?rminos de gob.mx](https://www.gob.mx/terminos). No se acredita una licencia abierta inequ?voca para redistribuci?n y explotaci?n comercial. No se asigna una licencia elegida por el equipo a los informes. | Se verifica robots antes de cada descarga, con User-Agent identificable, pausa y reintentos acotados. E0 observ? 404; la verificaci?n E2 registra su propio estado. Un 404 no constituye permiso de copyright. Conservar diferencias de acumulados, revisiones y cuarentena; resolver el permiso de uso comercial antes de comercializar derivados de esa fuente. |
| Banxico SIE, SF43718 | La [salvedad de uso](https://www.banxico.org.mx/footer-es/salvedad-politicas-uso-banco-.html) permite reproducir/utilizar informaci?n con atribuci?n y direcci?n del Banco. No se presenta como CC0. Se mantienen las condiciones del proveedor y sus [l?mites de consultas](https://www.banxico.org.mx/SieAPIRest/service/v1/doc/limiteConsultas). | API oficial con token en secret, nunca en URL ni repositorio. Una captura diaria. Promedios sobre d?as observados; fines de semana y cotizaciones no disponibles no se inventan. El FIX no equivale al precio pagado por cada cliente ni demuestra causalidad. |
| INEGI, DENUE Colima | [T?rminos de Libre Uso de la Informaci?n del INEGI](https://www.inegi.org.mx/inegi/terminos.html): permiten extracci?n, adaptaci?n y uso comercial con cr?dito y metadatos, sin aparentar aval institucional. Fuente: INEGI, DENUE Colima. Se conserva el encabezado de edici?n del diccionario incluido en la descarga, la URL, el hash del ZIP y la fecha de captura. | [Descarga oficial](https://www.inegi.org.mx/contenidos/masiva/denue/denue_06_csv.zip) sin token; robots no proh?be esa ruta en la revisi?n. Cach? de siete d?as, m?nimo dos segundos entre peticiones y reintentos acotados. No es un padr?n de nuestros clientes ni prueba que las unidades tengan demanda de software. |

La revisi?n HTTP y robots se conserva con fecha real en [fuentes_web.json](../calidad/e2/fuentes_web.json). Un error o bloqueo no se interpreta como permiso. Las condiciones pueden cambiar; las capturas documentan ?nicamente el estado observado. Esta declaraci?n no acredita autorizaci?n de ASIPONA a?n pendiente ni cumplimiento legal absoluto.

## Privacidad y minimizaci?n antes de guardar Bronce

El ZIP y el CSV completo de DENUE se procesan exclusivamente en memoria. Se selecciona municipio 007 de Colima, subsectores SCIAN 484 (autotransporte de carga), 488 (servicios relacionados con transporte) y 493 (almacenamiento). Para evitar incorporar personas f?sicas, se exige un sufijo societario expl?cito en la raz?n social. Esa cadena solo se usa para filtrar y no se persiste. Es una regla conservadora basada en el dato publicado, no una certificaci?n registral de personalidad jur?dica.

Antes de escribir Bronce, la lista blanca conserva ?nicamente identificador p?blico del establecimiento, c?digo de actividad, entidad/municipio, coordenadas num?ricas y posici?n del registro en el CSV fuente. Se eliminan nombre, raz?n social, CLEE, domicilio, correo, tel?fono, sitio web y dem?s campos. No se guarda el ZIP original con datos personales. La capa Bronce es cruda con proyecci?n m?nima previa por privacidad, excepci?n prevista por el proyecto.

El identificador DENUE corresponde a un establecimiento econ?mico, no a un identificador de una persona. Las coordenadas corresponden a las unidades de forma societaria seleccionada. No se capturan ubicaciones de operadores, placas, recorridos, contenedores ni perfiles. Los directorios de servicios aportados por el usuario solo son referencia comercial: no se incorporan como una base de contactos ni se contacta a las personas listadas.

Los escenarios del transportista usan agregados ingresados en sesi?n. No se escriben en archivos, se versionan ni se mandan a INEGI. Un futuro piloto requiere acuerdo sobre uso, acceso y conservaci?n. Las entrevistas sin consentimiento confirmado no quedan autorizadas por esta declaraci?n.

## Sesgos y l?mites

- **Selecci?n:** la forma societaria expl?cita excluye muchos establecimientos y favorece la identificaci?n m?s clara en el directorio. La muestra obtenida es peque?a; no representa a todas las transportistas ni sirve para estimar tama?o de mercado, competencia, ingresos o empleo.
- **Cobertura y actualizaci?n:** la fecha de ingesta es distinta de la edici?n del directorio y de la fecha de alta de un establecimiento. No se afirma que la captura describa altas o bajas de hoy. Se preservan el metadato de edici?n y el hash de la descarga.
- **Geograf?a:** el rect?ngulo 18.99?19.13 N y ?104.36??104.24 E y sus cuatro celdas son ?rea de estudio, no l?mites oficiales de recinto, colonias o municipio. GeoPandas asigna puntos por intersecci?n y deja en cuarentena los que quedan fuera. Las coordenadas no constituyen accesos viales autorizados ni rutas para camiones.
- **Temporalidad:** la captura geogr?fica es contexto actual. No se agrega a los meses hist?ricos de 2021?2026 como variable predictora: eso inducir?a fuga temporal. El pron?stico TEU mensual no predice citas ni tiempos diarios de espera.
- **Econom?a:** TEU no equivale a servicios facturables ni ingresos. El simulador usa tarifas y costos que introduce el cliente, declara sus supuestos y no afirma ahorros observados. Evitar doble contabilizaci?n de espera y costos variables.

## Licencia, publicaci?n y controles

Los datos DENUE seleccionados y sus derivados conservan la atribuci?n al INEGI y los metadatos del proceso de selecci?n: [aviso de datos](../data/bronce/denue/LICENCIA.md). Las adaptaciones se identifican como elaboraci?n del equipo, sin afirmar que las respalda el INEGI. No se licencia todo el repositorio de forma uniforme ni se atribuye esta autorizaci?n a ASIPONA o Banxico.

El mapa base utiliza CARTO/OpenStreetMap. El comparador consulta OSRM/FOSSGIS solo al solicitar recorridos entre ubicaciones publicas del catalogo; envia coordenadas y conserva en sesion los costos e ingresos. No consulta INEGI por cada visitante. Las fuentes y sus condiciones se distinguen en docs/E2/mapa-costos.md. El linaje de Oro mantiene URL, fecha de ingesta, selectores y SHA-256; sus conjuntos amplios se declaran como tales.

## Fuente descartada y uso de IA

Se intent? OSM/Overpass. La instancia principal proh?be `/api/` en robots; no se utiliz?. La alternativa Private.coffee no respondi? tras reintentos. No se publica una fuente ficticia: E2 usa DENUE real. Las consultas auxiliares de factibilidad no forman parte del producto. La asistencia de Codex para implementaci?n y documentaci?n se declara en `docs/relatoria-E2.md`.

## Ampliacion del mapa y comparador

El catalogo cerrado de cinco organizaciones conserva etiquetas institucionales publicas elegidas expresamente; no nombres de personas ni datos de contacto. Las consultas OSRM utilizan solo esos puntos publicos. El proveedor registra peticiones; se limita a una por segundo por proceso y cache de 24 horas. El perfil es de automovil y no valida accesos ni restricciones de carga. Los resultados de costos son escenarios del usuario y no cotizaciones verificadas. Detalle y fuentes: [mapa-costos.md](E2/mapa-costos.md).
