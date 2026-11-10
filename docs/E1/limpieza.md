# E1 · Decisiones de limpieza e integración

**Observatorio:** Puerto de Manzanillo · **Equipo:** Emilio Rodrigo Ayala Reynoso y Karol Gabriel Morán Aréchiga<br>
**Alcance:** tarea de Ingeniería de Datos, entrega del 13 de noviembre de 2026 a las 17:59, hora de México.<br>
**Implementación:** scripts en [`src/`](../../src/); ejecución con `python -m src.limpieza`.

## 1. Fuentes y unidad de análisis

ASIPONA aporta una tabla larga mensual: año, mes, concepto, valor y metadatos del PDF. Banxico aporta cotizaciones diarias FIX de la serie SF43718, en pesos por dólar. Los PDF y JSON originales permanecen en Bronce. El pipeline trabaja sin red ni token y comprueba que los hashes de entrada no cambien durante el procesamiento.

Se tipan explícitamente las fechas, números y booleanos; se valida el estado de publicación y se conserva el identificador de la línea original. El concepto `teu_total` mide capacidad equivalente a contenedores de 20 pies, no unidades físicas de contenedores. No se mezclan TEU, toneladas, buques y pesos por dólar en una misma magnitud.

## 2. Faltantes: diagnóstico y tratamiento

| Patrón observado | Diagnóstico razonado | Tratamiento |
|---|---|---|
| Ceros de las cuatro terminales en noviembre y diciembre de 2021, mientras existe movimiento total del puerto | Ocho ausencias representadas como cero. El patrón depende del periodo, la terminal y el reporte: compatible con MAR condicionado a esas variables. No se prueba MAR ni se descarta MNAR con los datos observados. | Conservar `valor_original=0`; estimar cada valor con la mediana de hasta tres observaciones **reales anteriores** de esa misma terminal. Marcar `imputado` y el método. |
| Meses posteriores al último publicado, incluidos dos campos vacíos en la captura actual | Ausencia estructural por publicación; no es evidencia de movimiento cero ni un caso de MCAR. | Enviar la fila a cuarentena como `periodo_no_publicado`. No extrapolarla para aparentar observaciones históricas. |
| Conceptos de tráfico no disponibles antes de 2024 | Cambio de cobertura del informe, no faltantes aleatorios. | Conservar su cobertura real en Plata. No construir ceros para años sin esa variable. |
| Fines de semana y festivos sin cotización FIX | Calendario de la fuente. No se presume que todos los días hábiles deban tener dato sin un calendario bancario oficial. | No crear filas ni interpolar cotizaciones. Promediar solo observaciones válidas y conservar su cantidad. |
| Valor no numérico, negativo, infinito o fuera del rango contractual | Corrupción o incumplimiento de contrato, distinto de un faltante imputable. | Cuarentena; jamás imputar para ocultar un valor inválido. |

La mediana causal es una estimación conservadora para las variables auxiliares; no reconstruye una cifra oficial. Los imputados no alimentan otras imputaciones. Si no existe historial previo, el valor sigue ausente y la puerta lo rechaza. **No se imputa `teu_total`**, para evitar inventar el objetivo del pronóstico. Las cifras imputadas por terminal no tienen por qué reconciliar exactamente con el total del puerto; están identificadas para excluirlas o hacer análisis de sensibilidad en E3.

No se afirma que los faltantes sean MCAR. Clasificar MAR/MNAR requiere supuestos externos: aquí se presenta el patrón observado y la hipótesis compatible, sin una conclusión causal no demostrada.

## 3. Atípicos y ruido

Se ajustan por variable el rango intercuartílico (límites Q1 − 1.5×IQR y Q3 + 1.5×IQR) y el puntaje robusto `0.67448975 × (x − mediana) / MAD`, con umbral absoluto 3.5. Si MAD es cero, un valor distinto de la mediana se marca para revisión. Un extremo que cumple rangos del negocio **se conserva**; no se iguala un atípico estadístico con un error.

En la captura inicial de E1 se marcan 10 registros de ASIPONA por IQR y ninguno de Banxico. No se eliminan ni se winsorizan. Oro contiene media y mediana móviles de tres meses, calculadas con el mes actual y anteriores, para comparar suavizamiento del ruido sin sustituir la serie original ni usar meses futuros.

## 4. Escalas, discretización y jerarquías

Para TEU, toneladas, buques y FIX promedio mensual se generan ambas escalas:

- Min-Max: `(x − mínimo) / (máximo − mínimo)`, útil para comparar magnitudes de unidades distintas.
- Z-Score: `(x − media) / desviación poblacional`, con `ddof=0`, útil para análisis sensibles a la varianza.

Los parámetros se ajustan solo con entrenamiento. La captura inicial reserva mayo a octubre de 2026 como prueba (seis meses) y ajusta hasta abril de 2026. Una observación de prueba puede tener Min-Max fuera de [0,1]; no se recorta para ocultar cambios respecto del entrenamiento. Para una variable constante se devuelve cero en ambas escalas y se registra su rango/desviación cero.

La actividad se discretiza como baja, media o alta con los cuantiles 1/3 y 2/3 de los TEU de entrenamiento. Son categorías relativas del conjunto, no una medida directa de saturación de terminales. Las jerarquías son año → trimestre → mes y México → Colima → Manzanillo; las terminales SSA, CONTECON, OCUPA y TIMSA forman otra dimensión del puerto.

Las variables transformadas se guardan junto a las originales. [`parametros_transformacion.json`](../../data/oro/parametros_transformacion.json) permite reconstruir cada escala. Las características del mes t pueden emplearse para estudiar t+1; no deben usarse para predecir el propio objetivo t como si fueran conocidas antes de observarlo.

## 5. Integración, conflictos y reducción

Se unifica la clave como fecha del primer día del mes. ASIPONA se pivota por concepto; Banxico se agrega por mes con promedio, mínimo, máximo, días observados y última fecha. La unión es `one_to_one`, conservando la fila mensual del puerto solo si supera la puerta de Oro.

Los duplicados de claves se rechazan completos: no se selecciona arbitrariamente uno. Se comprueba que `valor` y `valor_crudo` de Banxico coincidan numéricamente. Para grupos anuales completos de ASIPONA se recalcula la suma de los meses y se contrasta con `suma_meses`, el acumulado y la diferencia declarada; la tolerancia frente al acumulado es de dos unidades. No se fuerza una conciliación exacta que la fuente no tiene. Para 2023 se conserva la versión de su propio EM elegida en Bronce, con trazabilidad al PDF; no se mezcla silenciosamente con la revisión citada por otro año.

En la captura inicial, 1,473 cotizaciones se reducen a 71 meses: **95.1799% menos filas**. Se pierde el orden y la trayectoria intramensual en la tabla agregada, pero se conservan mínimo, máximo y conteo; los datos diarios siguen en Plata. Noviembre de 2026 es parcial y aún no tiene observación ASIPONA: se conserva en Plata, se informa en el resumen y no entra en los 70 meses de Oro.

Oro selecciona tres conceptos portuarios y FIX para la tabla mensual de 70 filas; los demás conceptos siguen en Plata. La tabla de terminales conserva 280 observaciones terminal-mes. No se realiza muestreo aleatorio que rompa el orden de una serie corta.

## 6. Puerta automática y cuarentena

Los contratos de [`src/calidad.py`](../../src/calidad.py) utilizan Pandera con `strict=True`, tipos sin coerción implícita y validación acumulada (`lazy=True`). Se admiten únicamente las columnas declaradas. Se comprueban unicidad, fechas, valores finitos, claves, trazabilidad e intervalos de negocio amplios: TEU hasta 2 millones por mes; toneladas hasta 30 millones; buques hasta 5 mil; FIX entre 0.01 y 1,000 MXN/USD. Son límites de detección de errores y no estimaciones de lo que ocurrirá.

La validación previa a la imputación excluye datos corruptos antes de que puedan alterar una mediana. La puerta final de Plata no permite `valor` ausente. La puerta de Oro exige datos integrados completos y un mes de FIX terminado. La serie objetivo debe conservar al menos 36 meses consecutivos; una ruptura bloquea la publicación.

Cada rechazo conserva fuente, etapa, identificador de línea, motivo, registro original y registro normalizado en [`data/cuarentena/e1/`](../../data/cuarentena/e1/). Un error estructural sin índice de fila rechaza el lote completo. No se usa la opción de borrar registros inválidos de Pandera. Los estados se guardan en CSV y en un historial JSONL identificado por hashes de entradas, código y versiones de librerías. Para cada fuente se verifica `entrada = aceptados + rechazados`.

Solo después de validar se preparan los productos en un directorio temporal y se reemplazan sus archivos. Si hay una falla, la ejecución devuelve error y conserva cuarentena, resumen y bitácora; no declara válidos productos nuevos. Los productos previos, si existen, representan la última ejecución exitosa y deben contrastarse con el estado del resumen actual.

## 7. Reproducción y automatización

```bash
pip install -r requirements.txt
python -m src.limpieza
python -m pytest -q --cov=src --cov-report=term-missing
ruff check src tests
```

[`Captura programada`](../../.github/workflows/captura.yml) ejecuta la limpieza después de una captura exitosa y guarda Bronce, Plata, Oro, cuarentena y bitácoras. Una falla de captura o pipeline termina en rojo. [`Calidad E1`](../../.github/workflows/ci.yml) ejecuta linter, pruebas y pipeline en pushes, pull requests y el tag `e1`; conserva un artefacto con los resultados. La bitácora técnica registra tiempo de máquina, distinto de las horas personales PSP de los integrantes.

Referencias técnicas: [contratos estrictos de Pandera](https://pandera.readthedocs.io/en/stable/dataframe_schemas.html) y [validación acumulada y casos de fallo](https://pandera.readthedocs.io/en/stable/lazy_validation.html). El uso de las fuentes y las limitaciones de redistribución documentadas en [E0](../E0/propuesta.md#4-plan-de-recopilación) continúan vigentes; este pipeline no realiza descargas adicionales.
