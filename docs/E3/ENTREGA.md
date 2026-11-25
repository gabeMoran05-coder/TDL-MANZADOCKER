# E3 · Ingeniería de Datos: ficha de entrega

## Optimización medida

Se reutiliza por lote el resultado de interpretar cada fecha de captura repetida durante la normalización. No cambia reglas ni puertas. Se midió exclusivamente `normalizar` de Banxico, no la captura de red ni el pipeline integral. La selección es una mejora propia; no se afirma que provenga del experimento E2 o de una auditoría externa, ambos pendientes de evidenciar.

| Indicador | Antes | Después |
|---|---:|---:|
| Mediana de 3 corridas, 1,483 filas | 1.654 s | 0.506 s |
| Pico de memoria Python con tracemalloc, corrida separada | 2,100,184 bytes | 2,085,726 bytes |
| Rechazos sobre entrada real | 0 | 0 |
| Defectos sintéticos detectados | 3/3 | 3/3 |

La reducción de tiempo es 69.4 % y la de memoria rastreada 0.69 %. No se demuestra reducción de errores: el número detectado y las salidas son iguales. Memoria Python no equivale al pico RSS del proceso; los resultados dependen de equipo y entorno. El primer tiempo incluye calentamiento y se reportan todas las corridas. [Resultados y versiones](../../calidad/e3/benchmark.json); [código reproducible](../../scripts/benchmark_e3.py). Comando: `python -m scripts.benchmark_e3`. Requiere Git y el commit base `ceceab9`. Compara cuadros, originales y rechazos, además de tres defectos inyectados; no prueba todos los casos posibles.

## Dataset para terceros

[Datasheet y condiciones de uso](datasheet.md). Se publica el agregado DENUE, no el integrado ASIPONA/Banxico, porque no consta una licencia abierta inequívoca para ASIPONA. La disponibilidad pública requiere subir los cambios; no se ha atribuido una licencia Creative Commons a la fuente.

## Verificaci?n del 25/11/2026

`python -m pytest -q --cov=src --cov-report=json:calidad/e3/cobertura.json`: 93 pruebas aprobadas y 94.67 % de cobertura de `src`. Ruff sin hallazgos en el tablero y los archivos nuevos de an?lisis, indicadores y pruebas. La cobertura no representa todo el tablero ni prueba por s? sola reproducibilidad independiente.

## Ampliaci?n multidisciplinaria

[An?lisis multivariado y l?mites de MANOVA](multivariado.md) ? [Autoevaluaci?n, PSP y estado del Sello TDL](calidad.md). El PCA descriptivo del puerto usa 34 meses, no las cuatro terminales previstas. Se agreg? el mapa al tablero con comprobaci?n del hash de origen. La matriz, Mardia y figuras son reproducibles; la dependencia temporal impide interpretar las pruebas como garant?a de normalidad. Falta informaci?n por terminal para una MANOVA defendible.

La auditor?a cruzada no est? disponible y la combinaci?n ganadora del experimento E2 no se encuentra documentada. Las 14 fechas UTC hasta el 24/11 incluyen 13 d?as de captura programada exitosa. No hay evidencia suficiente para el sello; v?ase el detalle por criterio en calidad.md. Contin?a pendiente medir una reducci?n de errores y aplicar una optimizaci?n de captura derivada del experimento o auditor?a.

La etiqueta `e3` publicada anteriormente se?ala el commit original; esta ampliaci?n no la sobrescribe. El formulario oficial no fue proporcionado. La etiqueta que finalmente deba evaluarse debe acordarse con el equipo y docentes si el formulario exige espec?ficamente `e3`.
