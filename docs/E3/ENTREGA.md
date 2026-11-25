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

## Estado de entrega

[Relatoría](../relatoria-E3.md). El documento integrador también pide para E3 análisis multivariado, cierre de auditoría, PSP y Sello TDL. No hay evidencia nueva de esos componentes en esta entrega de Ingeniería; no se declara completado el paquete de las tres materias ni el sello. El formulario oficial no fue proporcionado. La optimización de obtención según combinación ganadora o auditoría sigue pendiente de comprobar porque no hay evidencia de esos antecedentes. No se afirma mejora de errores.
