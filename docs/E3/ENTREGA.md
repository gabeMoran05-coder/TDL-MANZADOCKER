# Entrega E3 · Observatorio del Puerto de Manzanillo

Equipo: Emilio Rodrigo Ayala Reynoso (Data Engineer) · Karol Gabriel Morán Aréchiga (Data Statistician) · Tablero: https://tdl-manzadocker.streamlit.app/

## Resumen en tres líneas

- **Optimización:** la normalización Banxico es 71–72 % más rápida con la misma salida. Se corrigió la captura cuando robots.txt responde 429 y cuando INEGI cambió sus encabezados.
- **Dataset:** se publica el agregado DENUE por celda con datasheet y términos de libre uso del INEGI.
- **Análisis:** la MANOVA muestra que las cuatro terminales difieren en tamaño y perfil de tráfico (Pillai = 1.92, p < 0.001, confirmado por permutación). El PCA resume la actividad mensual del puerto.

## Mapa de la rúbrica

| Materia | Criterio (puntos) | Evidencia | Estado |
|---|---|---|---|
| Ing. Datos | Optimización medida (50) | [Abajo en esta ficha](#optimización-de-normalización-entrada-real) · [benchmark con memoria de proceso](../../calidad/e3/benchmark_proceso.json) · [captura simulada](../../calidad/e3/benchmark_captura.json) | Tiempo −71.2 %; errores de decisión 100 → 0 (simulación); DENUE 0 → 29 celdas (real); memoria sin cambio. Sin experimento E2 ni auditoría que aplicar |
| Ing. Datos | Dataset publicado (40) | [Datasheet](datasheet.md) · [CSV](../../data/oro/denue_celdas.csv) · [GeoJSON](../../data/oro/denue_celdas.geojson) | Completo |
| Estadística | Matriz y normalidad (15) | [PCA, Mardia y Q-Q](multivariado.md#exploración-alternativa-un-mes-por-fila) · [MANOVA: Mardia y Box sobre residuos](multivariado.md#manova-las-cuatro-terminales-tienen-el-mismo-tamaño-y-perfil-de-tráfico) | Completo |
| Estadística | Componentes principales (35) | [Multivariado](multivariado.md) · [pca.json](../../calidad/e3/pca.json) · [gráficas](../../calidad/e3/pca_diagnosticos.png) | Completo |
| Estadística | MANOVA (25) | [Multivariado](multivariado.md#manova-las-cuatro-terminales-tienen-el-mismo-tamaño-y-perfil-de-tráfico) · [manova.json](../../calidad/e3/manova.json) · [datos por terminal](../../data/plata/terminal_trafico_anual.csv) | Wilks y Pillai, permutación, supuestos y contraste con varios ANOVA. Unidad anual (28 obs.) |
| Estadística | Mapa en el tablero (15) | [Tablero](https://tdl-manzadocker.streamlit.app/) · [código](../../tablero/app.py) | PCA con interpretación |
| Calidad | Cierre de auditoría (30) | [Calidad](calidad.md#auditoría-cruzada) | **Pendiente:** no se ha recibido el informe del equipo auditor |
| Calidad | Modelos de proceso (25) | [Calidad](calidad.md#autoevaluación-de-proceso) | Completo |
| Calidad | Retrospectiva PSP (25) | [Calidad](calidad.md#retrospectiva-psp) | Con registros reales; sin estimaciones previas |
| Calidad | Tendencias (10) | [Calidad](calidad.md#tendencia-aplicada-observabilidad-de-datos) | Completo |
| Calidad | Solicitud del Sello TDL | [Calidad](calidad.md#evaluación-del-sello-tdl) | Cumplen completitud, cobertura y secretos. No cumplen disponibilidad ni auditoría. Reproducibilidad parcial |
| Las tres | Relatoría (10) | [relatoria-E3.md](../relatoria-E3.md) | Completo |

Comandos para reproducir:

```bash
python -m src.terminales_trafico        # tabla por terminal y tráfico desde PDF en Bronce
python -m scripts.manova_e3             # MANOVA y supuestos
python -m scripts.analisis_e3           # PCA
python -m scripts.benchmark_e3_proceso  # optimización con memoria de proceso
python -m pytest -q --cov=src
```

# Ingeniería de Datos

## Optimización de normalización: entrada real

Se reutiliza durante cada lote el resultado de interpretar fechas de captura repetidas. La comparación ejecuta `normalizar` de Banxico en la versión anterior `ceceab9` y la optimizada, con el mismo CSV Bronce de 1,484 filas, sin red. No mide todo el pipeline ni la descarga.

| Indicador | Antes | Después |
|---|---:|---:|
| Mediana de 3 corridas | 3.235 s | 0.897 s |
| Pico de memoria Python, medición separada | 2,104,185 bytes | 2,087,309 bytes |
| Rechazos sobre la entrada real | 0 | 0 |
| Defectos sintéticos rechazados | 3/3 | 3/3 |

La mediana disminuyó **72.3 %** y el pico rastreado **0.8 %** en este entorno. Las salidas, originales y rechazos fueron equivalentes; no se observa reducción de errores en esta carga. `tracemalloc` no mide toda la memoria RSS ni asignaciones nativas. [Resultados, hashes y versiones](../../calidad/e3/benchmark_26nov.json). Las mediciones anteriores del 25/11 se conservan en [benchmark.json](../../calidad/e3/benchmark.json).

### Medición complementaria: entrada fija y memoria total del proceso

Entre corridas de la misma versión hubo mucha variación (8.17 s y 1.65 s el 25/11), y `benchmark_e3` lee la captura Banxico del día. Por eso Emilio agregó [benchmark_e3_proceso](../../scripts/benchmark_e3_proceso.py), que no reemplaza el anterior:
- Fija la entrada en el commit `f9275de` y verifica su SHA-256 (`b60791e0…`, 1,484 filas, la misma del 26/11).
- Ejecuta cada versión en un proceso propio y alterna 3 rondas, con un calentamiento y 5 corridas medidas por ronda.
- Lee la memoria total del proceso del sistema operativo (pico de *working set* en Windows; `ru_maxrss` en Linux), aparte de `tracemalloc`.

Medición del 27/11 en el equipo de Emilio (Windows 11, Python 3.14):

| Indicador (15 corridas por versión) | Antes | Después |
|---|---:|---:|
| Mediana | 1.339 s | 0.385 s |
| Mínimo y máximo | 1.087–1.967 s | 0.338–1.203 s |
| Pico de memoria del proceso (mediana) | 124.8 MiB | 124.8 MiB |
| Aumento de memoria del proceso durante la normalización | 20.5 MiB | 20.7 MiB |
| Pico de memoria Python (`tracemalloc`) | 2,108,551 bytes | 2,088,668 bytes |
| Rechazos y defectos sintéticos rechazados | 0 y 3/3 | 0 y 3/3 |

- **Tiempo:** la mediana bajó **71.2 %**, en línea con el 72.3 % del 26/11.
- **Memoria:** el proceso no usa menos memoria. Casi todo el pico viene de cargar pandas, y la diferencia en el aumento (+1 %) está dentro del ruido.
- **Salidas:** las dos versiones dieron una salida con la misma huella SHA-256.

[Resultados completos](../../calidad/e3/benchmark_proceso.json).

## Corrección con datos reales: captura DENUE

Las capturas programadas del 26 y 27/11 fallaron en DENUE: INEGI cambió los encabezados del CSV a mayúsculas (`CVE_MUN`, `CODIGO_ACT`, `LATITUD`…) y el extractor descartaba sus 42,223 filas. Ahora acepta los encabezados en mayúsculas o minúsculas, y una [prueba](../../tests/test_denue_agregado.py) comprueba que ambos dan el mismo agregado.
- **Antes de la corrección:** con la descarga real del 27/11, el agregado tenía 0 celdas y la captura terminaba en error.
- **Después:** con la misma descarga, 29 celdas y 635 establecimientos.

La prueba se hizo en memoria, sin guardar en Bronce. Es un solo caso real y no mide una tasa de fallos.

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
python -m scripts.benchmark_e3_proceso
python -m scripts.benchmark_captura_e3
python -m pytest -q tests/test_extractor_base.py tests/test_denue_agregado.py
```

El 27/11, Emilio (que no escribió estos scripts) los ejecutó en una copia limpia de `e3-revision-2`:
- PCA e indicadores salieron con SHA-256 idéntico.
- En el ensayo simulado, las decisiones incorrectas también bajaron de 100 a 0. El tiempo aumentó 26 % y la memoria `tracemalloc` aumentó 26 %, contra +38 % y −3.9 % registrados.

[Detalle](../../calidad/e3/reproduccion_emilio.json).

Las mediciones dependen del equipo y del CSV Bronce; el JSON registra su SHA-256. Para reproducir la medición de normalización del 26/11, usar la captura referenciada en `benchmark_26nov.json`. El primer comando sobrescribe `benchmark.json` y el segundo sobrescribe `benchmark_captura.json`; conviene guardar copias antes de comparar.

## Dataset y ficha

El agregado [DENUE por celda](../../data/oro/denue_celdas.csv) y su [datasheet](datasheet.md) ya están publicados en la etiqueta `e3`. Conservan los términos de libre uso y atribución del INEGI; no se asigna esa licencia a ASIPONA ni a Banxico. La ficha declara metodología, composición, supresión, limitaciones, fecha y hashes.

## Estado del paquete

[Relatoría](../relatoria-E3.md) · [Análisis multivariado](multivariado.md) · [Calidad y Sello TDL](calidad.md). El PCA describe meses del puerto. La MANOVA por terminal se hizo con acumulados anuales, porque los EM no publican tráfico por terminal y mes. Se verificaron con evidencia:
- 0 secretos en el historial.
- Cobertura de 94.78 %.
- Reproducción interna de los resultados E3.

Siguen pendientes:
- La auditoría cruzada.
- El experimento E2.
- La reproducción por un tercero externo.
- La disponibilidad de captura: 78.57 % en 14–27/11, por el fallo de DENUE.

El sello no se declara obtenido. El formulario oficial no fue proporcionado. La etiqueta `e3` original ya existe y no se ha sobrescrito; esta revisión se identifica como `e3-revision-2`. Si el formulario exige exclusivamente `e3`, el equipo debe acordar cómo proceder antes de cambiar la etiqueta original.
