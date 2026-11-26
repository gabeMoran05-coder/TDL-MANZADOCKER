# Datasheet: establecimientos logísticos por celda en Manzanillo

## Motivación y responsables

El equipo Emilio Rodrigo Ayala Reynoso y Karol Gabriel Morán Aréchiga elaboró este agregado para describir el contexto territorial del observatorio. Fuente: INEGI, Directorio Estadístico Nacional de Unidades Económicas (DENUE), Colima. Es una transformación del equipo, no un producto ni aval del INEGI.

## Acceso, versión y licencia

- Dataset: [CSV UTF-8](../../data/oro/denue_celdas.csv) y [GeoJSON EPSG:4326](../../data/oro/denue_celdas.geojson), publicados en la etiqueta [e3](https://github.com/gabeMoran05-coder/TDL-MANZADOCKER/tree/e3/data/oro).
- SHA-256 CSV: `6e9e5d407f2746cf35352d756f9ba6239a207d0a5d75e9e5343c70336416d506`.
- Fuente: [descarga DENUE Colima](https://www.inegi.org.mx/contenidos/masiva/denue/denue_06_csv.zip), SHA-256 del ZIP `948e292e567ce16a8b7485f15846ddaaf9c9cda6fda9be07334bb6afc5480af6`. Captura: 2026-11-19 19:32:06 UTC; metadato del diccionario: 20/05/2026. La fecha del diccionario no prueba la fecha de actualización de todos los registros.
- Condiciones abiertas del proveedor: [Términos de Libre Uso del INEGI](https://www.inegi.org.mx/inegi/terminos.html), revisados el 26/11/2026. Permiten copiar, publicar, adaptar y uso comercial con las condiciones de créditos, metadatos y señalamiento de transformaciones. Conservar atribución y metadatos, identificar la elaboración del equipo y no sugerir aval del INEGI. No se afirma que sea CC BY o CC0. [Aviso de fuente](../../data/bronce/denue/LICENCIA.md). Estos términos no licencian las otras fuentes del repositorio.

## Composición y diccionario

28 filas, una por celda publicada; 608 establecimientos agregados de 632 seleccionados. Se suprimieron 18 celdas con 24 establecimientos por tener menos de 3. No hay puntos individuales, nombres ni desglose por actividad. La unidad es la celda, no una empresa. Sin etiquetas objetivo ni datos de entrenamiento personales.

| Campo | Definición |
|---|---|
| celda | Identificador de rejilla de 0.01 grados |
| registro_bronce | Posición de la celda en el agregado Bronce, desde 1 |
| sur, oeste, norte, este | Límites de celda en grados, EPSG:4326 |
| lat, lon | Centro de celda, no ubicación de establecimiento |
| total | Número de establecimientos seleccionados, mínimo 3 |
| zona_estudio | Cuadrante asignado al centro; también puede quedar fuera |
| paso_grados, k_minimo | Resolución de 0.01° y umbral de 3 |
| url_origen, fecha_captura_utc, archivo_bronce | Procedencia, instante de ingesta UTC y ruta del agregado sanitizado |

## Recolección y procesamiento

Descarga pública del ZIP oficial; selección del municipio 007 de Colima y subsectores SCIAN 484, 488 y 493. Agregación en rejilla, supresión de celdas pequeñas y eliminación de detalle por categoría antes de persistir. La captura actual sanitizada deriva de la captura del 19 de noviembre, no de una descarga nueva. Se validan campos, duplicados, límites, tamaño y umbral; se asigna un cuadrante por intersección espacial del centro. El rectángulo de estudio no es un límite oficial. [Código](../../src/geoespacial.py), [resumen](../../calidad/e2/geoespacial.json), [linaje](../../calidad/e2/linaje.json). El historial Git contiene versiones previas con mayor detalle; la supresión actual no las revoca.

## Usos y limitaciones

Recomendado: exploración espacial agregada del contexto logístico y reproducción del mapa, atribuyendo la fuente. No recomendado: identificar establecimientos, medir flota, empleo, ingresos, demanda o accesos para camiones; usar esta captura como variable histórica anterior a su levantamiento; inferir cobertura completa de zonas poco densas. El umbral reduce riesgo de identificación sin garantizar anonimato; el directorio puede tener omisiones y desactualizaciones. No se dispone de un canal de mantenimiento o actualización garantizada; al actualizar, conservar la captura y sus metadatos y verificar condiciones vigentes.
