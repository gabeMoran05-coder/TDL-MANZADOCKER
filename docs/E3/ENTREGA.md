# E3 · Ingeniería de Datos: ficha de entrega

## Optimización de normalización: entrada real

Se reutiliza durante cada lote el resultado de interpretar fechas de captura repetidas. La comparación ejecuta `normalizar` de Banxico en la versión anterior `ceceab9` y la optimizada, con el mismo CSV Bronce de 1,484 filas, sin red. No mide todo el pipeline ni la descarga.

| Indicador | Antes | Después |
|---|---:|---:|
| Mediana de 3 corridas | 3.235 s | 0.897 s |
| Pico de memoria Python, medición separada | 2,104,185 bytes | 2,087,309 bytes |
| Rechazos sobre la entrada real | 0 | 0 |
| Defectos sintéticos rechazados | 3/3 | 3/3 |

La mediana disminuyó **72.3 %** y el pico rastreado **0.8 %** en este entorno. Las salidas, originales y rechazos fueron equivalentes; no se observa reducción de errores en esta carga. `tracemalloc` no mide toda la memoria RSS ni asignaciones nativas. [Resultados, hashes y versiones](../../calidad/e3/benchmark_26nov.json). Las mediciones anteriores del 25/11 se conservan en [benchmark.json](../../calidad/e3/benchmark.json).

## Corrección medida de la captura: respuestas simuladas

Se detectó que una respuesta **HTTP 429 en robots.txt** se trataba como permiso de captura. Ahora bloquea la descarga, igual que 403 y 5xx: saturación no significa que se permitan todas las rutas. La prueba usa un servidor simulado: 100 respuestas 429, 100 de cada uno de los controles 403, 503 y 404, sin red. El resultado no prueba cuántas veces ocurrió el problema en operación.

| Indicador sobre 400 casos simulados | Antes | Después |
|---|---:|---:|
| Decisiones incorrectas | 100 | 0 |
| Intentos de descarga pese al bloqueo esperado | 100 | 0 |
| Mediana de 5 corridas | 0.0471 s | 0.0651 s |
| Pico de memoria Python, corrida separada | 645,369 bytes | 620,415 bytes |

En esta prueba los errores de decisión bajaron de 25 % a 0 %; los 100 casos 429 dejaron de autorizar descargas. El tiempo **aumentó** aproximadamente 38.2 % en esta carga pequeña y simulada; no se presenta como mejora de velocidad de captura. La memoria rastreada disminuyó aproximadamente 3.9 %, sin equivaler al uso total del proceso. [Datos completos](../../calidad/e3/benchmark_captura.json), [código](../../extractores/base.py) y [pruebas](../../tests/test_extractor_base.py).

La mejora de 429 es una corrección identificada al revisar el código. No se localizó el resultado de un experimento factorial E2 ni un informe de auditoría cruzada; por ello no se atribuye a ninguno ni se afirma cumplido el requisito del documento integrador de aplicar su combinación ganadora o recomendaciones. Tampoco se cuantifica una reducción de fallos reales en producción.

### Reproducción

Desde un clon con Python, dependencias de `requirements.txt` y el historial Git que incluye `ceceab9` y `f9275de`:

```bash
python -m scripts.benchmark_e3
python -m scripts.benchmark_captura_e3
python -m pytest -q tests/test_extractor_base.py
```

Las mediciones dependen del equipo y del CSV Bronce; el JSON registra su SHA-256. Para reproducir la medición de normalización del 26/11, usar la captura referenciada en `benchmark_26nov.json`. El primer comando sobrescribe `benchmark.json` y el segundo sobrescribe `benchmark_captura.json`; conviene guardar copias antes de comparar.

## Dataset y ficha

El agregado [DENUE por celda](../../data/oro/denue_celdas.csv) y su [datasheet](datasheet.md) ya están publicados en la etiqueta `e3`. Conservan los términos de libre uso y atribución del INEGI; no se asigna esa licencia a ASIPONA ni a Banxico. La ficha declara metodología, composición, supresión, limitaciones, fecha y hashes.

## Estado del paquete

[Relatoría](../relatoria-E3.md) · [Análisis multivariado](multivariado.md) · [Calidad y Sello TDL](calidad.md). El PCA descriptivo corresponde a meses del puerto, no a la MANOVA por terminal solicitada en E0. La auditoría cruzada, el experimento E2, la validación independiente y otros requisitos del paquete de las tres materias permanecen pendientes; el sello no se declara obtenido. El formulario oficial no fue proporcionado. La etiqueta `e3` original ya existe y no se ha sobrescrito; esta revisión se identifica como `e3-revision-2`. Si el formulario exige exclusivamente `e3`, el equipo debe acordar cómo proceder antes de cambiar la etiqueta original.
