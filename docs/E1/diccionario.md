# Diccionario de datos · E1

## Plata

| Archivo / campo | Tipo | Unidad o interpretación |
|---|---|---|
| `asipona_mensual.csv` / `fecha` | fecha | Primer día del mes de referencia |
| `variable` | texto enumerado | TEU total/terminal/tráfico, toneladas o buques; nombres del extractor Bronce |
| `valor` | float64 finito | Unidad del concepto; los conteos publicados se conservan y las estimaciones pueden tener decimales |
| `valor_original` | float64 nullable | Valor extraído antes del tratamiento; los ocho ceros sospechosos permanecen aquí |
| `imputado`, `metodo_imputacion` | booleano, texto | Distinguen observación de estimación causal |
| `diferencia_acumulado` | float64 | Suma de los valores crudos menos acumulado reportado, antes de imputar |
| `id_origen` | texto | Fuente y número de línea del CSV de Bronce, contando encabezado |
| `url_origen`, `archivo_origen`, `fecha_captura_utc` | texto | Procedencia y captura UTC del registro |
| `es_atipico_iqr`, `es_atipico_robusto` | booleano | Señales de revisión; no implican rechazo automático |
| `banxico_diario.csv` / `fecha` | fecha | Fecha de cotización en la fuente |
| `serie` | texto | Siempre `SF43718` |
| `valor`, `valor_crudo` | float64, texto | FIX en pesos por dólar y representación original |
| `banxico_mensual.csv` / `fix_promedio_mxn_usd` | float64 | Media aritmética de cotizaciones válidas del mes |
| `fix_minimo_mxn_usd`, `fix_maximo_mxn_usd` | float64 | Extremos mensuales observados |
| `fix_dias_observados` | entero | Número de cotizaciones admitidas; no es porcentaje de días hábiles cubiertos |
| `fix_ultima_fecha` | fecha | Última cotización observada en el mes |
| `fix_mes_completo` | booleano | El calendario del mes terminó a la fecha de captura; no certifica cobertura de todos los días bancarios |

## Oro

[`mensual_integrado.csv`](../../data/oro/mensual_integrado.csv) y su versión Parquet representan un mes del Puerto de Manzanillo por fila. Incluyen `fecha`, `id_origen`, `teu_total` (TEU), `ton_contenerizada` (toneladas), `buques_contenerizada` (buques), las seis columnas FIX de la tabla anterior y `es_atipico_teu` (IQR o robusto del TEU total).

| Campos derivados | Tipo | Definición |
|---|---|---|
| `<variable>_minmax` | float64 | `(x − mínimo) / rango`, para los tres conceptos portuarios y FIX promedio |
| `<variable>_zscore` | float64 | `(x − media) / std`, mismos cuatro conceptos; desviación poblacional |
| `actividad` | texto | Baja/media/alta respecto a los cuantiles de entrenamiento |
| `teu_media_movil_3`, `teu_mediana_movil_3` | float64 | Suavizado con mes actual y hasta dos anteriores; unidad TEU |
| `anio`, `trimestre`, `mes` | entero | Jerarquía temporal de la observación |
| `pais`, `estado`, `puerto` | texto | México, Colima, Manzanillo |
| `particion` | texto | Entrenamiento o prueba; los últimos seis meses son prueba |

[`terminales_mes.csv`](../../data/oro/terminales_mes.csv) contiene un registro terminal-mes con los metadatos de ASIPONA más `terminal`, `teu_total` del puerto y `participacion_pct = 100 × valor / teu_total`. Las participaciones de meses con imputación son estimaciones y no una conciliación oficial. Se conservan los indicadores de imputación y atípicos.

[`parametros_transformacion.json`](../../data/oro/parametros_transformacion.json) incluye fecha máxima de ajuste, mínimos, máximos, media, desviación, mediana, MAD, límites IQR y cuantiles. El identificador de ejecución, hashes, versiones y balance de filas se guardan en [`calidad/e1/resumen.json`](../../calidad/e1/resumen.json).

## Cuarentena

Los CSV por fuente tienen `fuente`, `etapa`, `id_origen`, `motivo`, `registro_original_json` y `registro_normalizado_json`. Los registros no publicados también se conservan aquí, en lugar de borrarse de forma silenciosa. El historial JSONL agrupa los rechazos de cada combinación de entradas/código/entorno. Bronce conserva la evidencia original.
