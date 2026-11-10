# Entrega E1 · Capa Plata, limpieza y puerta de calidad

**Equipo:** Emilio Rodrigo Ayala Reynoso · Karol Gabriel Morán Aréchiga<br>
**Materia:** Ingeniería de Datos · **Docente:** Armando Gallardo Heredia<br>
**Entrega indicada:** 13 de noviembre de 2026, 17:59, hora de México<br>
**Repositorio:** https://github.com/gabeMoran05-coder/TDL-MANZADOCKER<br>
**Rama de desarrollo:** `gabriel/e1` · **Etiqueta:** `e1`

## Resultado y alcance

El pipeline transforma las tablas de Bronce en Plata validada y Oro integrado mediante scripts en `src/`, la alternativa permitida al notebook. Trabaja sin red ni token, conserva Bronce y registra cada rechazo con motivo y contenido original. La captura programada encadena extracción y limpieza; CI verifica el código y los datos.

La primera ejecución de E1, el 10 de noviembre de 2026, produjo 626 registros ASIPONA en Plata (ocho imputaciones identificadas), 1,473 cotizaciones Banxico, 70 meses integrados y 280 registros terminal-mes. Se enviaron 22 posiciones aún no publicadas a cuarentena. Las cifras de futuras capturas se consultan en el [resumen automático](../../calidad/e1/resumen.json), con hashes de las entradas y versiones de las dependencias.

La verificación completa en GitHub del mismo día agregó la cotización del 10 de noviembre: **1,474 registros diarios Banxico**, con 70 meses de Oro y 22 rechazos conservados. Los datos, las bitácoras y los productos fueron guardados por el bot en el commit `005a0ed`.

## Evidencia por requisito

| Requisito de la tarea | Evidencia | Comportamiento verificable |
|---|---|---|
| Diagnóstico de faltantes e imputación justificada | [Limpieza §2](limpieza.md#2-faltantes-diagnóstico-y-tratamiento) · [preprocesamiento.py](../../src/preprocesamiento.py) | Se distinguen ausencias estructurales, ocho ceros sospechosos y errores. MAR se plantea como hipótesis condicionada, sin afirmar que esté probado; se imputa con mediana causal. |
| Atípicos y ruido | [Limpieza §3](limpieza.md#3-atípicos-y-ruido) · [Plata ASIPONA](../../data/plata/asipona_mensual.csv) | IQR y puntaje robusto; se conservan extremos válidos y se comparan suavizados móviles de tres meses. |
| Min-Max y Z-Score | [Oro mensual](../../data/oro/mensual_integrado.csv) · [parámetros](../../data/oro/parametros_transformacion.json) | Cuatro variables con ambas escalas, ajustadas solo en entrenamiento; seis meses de prueba separados. |
| Discretización y jerarquías | [Limpieza §4](limpieza.md#4-escalas-discretización-y-jerarquías) · [diccionario](diccionario.md) | Actividad baja/media/alta por cuantiles; año/trimestre/mes y país/estado/puerto; terminal como dimensión. |
| Reducción de datos y pérdida documentada | [Limpieza §5](limpieza.md#5-integración-conflictos-y-reducción) · [Banxico mensual](../../data/plata/banxico_mensual.csv) | Primera ejecución: 1,473 cotizaciones a 71 meses, reducción de 95.1799%; se pierde trayectoria intramensual en el agregado y se conserva el diario en Plata. |
| Integración y conflictos | [limpieza.py](../../src/limpieza.py) · [Oro CSV](../../data/oro/mensual_integrado.csv) · [Parquet](../../data/oro/mensual_integrado.parquet) | Clave mensual y unión uno-a-uno; tipos y unidades explícitos; duplicados, diferencias de cotización, sumas y periodos incompletos revisados. |
| Puerta automática Pandera | [calidad.py](../../src/calidad.py) · [pruebas](../../tests/test_e1.py) | Contratos estrictos, unicidad, fechas, valores finitos, rangos y trazabilidad; datos corruptos no alimentan la imputación. |
| Cuarentena con motivo | [CSV e historial JSONL](../../data/cuarentena/e1/) | Fuente, etapa, línea, motivo y registros original/normalizado; balance entrada = aceptados + rechazados. |
| Automatización y reproducibilidad | [Captura](../../.github/workflows/captura.yml) · [CI E1](../../.github/workflows/ci.yml) · [bitácora](../../calidad/bitacora_pipeline.csv) | Captura exitosa → limpieza → validación → almacenamiento; una falla produce estado rojo y deja evidencia. |
| Ficha y relatoría | Este documento · [relatoria-E1.md](../relatoria-E1.md) | Decisiones, cronología comprobable, límites y uso de IA declarados. |

## Comprobación

```bash
pip install -r requirements.txt
ruff check src tests
python -m pytest -q --cov=src --cov-report=term-missing
python -m src.limpieza
```

Las pruebas incluyen corrupción de valores y fechas, columnas adicionales o ausentes, claves duplicadas, conflicto FIX, causalidad de la imputación, escalas constantes, extrema válida conservada, continuidad mensual y ejecución repetida con hashes idénticos de productos y Bronce sin cambios.

Validación local del 10 de noviembre de 2026: **32 pruebas aprobadas**, **96.01% de cobertura** y Ruff sin errores. La cobertura mínima automática es 90%. [Registro de validación local](../../calidad/e1/validacion_local.json).

Ejecuciones verificadas en GitHub el 10 de noviembre de 2026:

- [Calidad E1: linter, pruebas, generación y artefacto, en verde](https://github.com/gabeMoran05-coder/TDL-MANZADOCKER/actions/runs/42892014765).
- [Captura completa: Bronce → Plata → Oro y cuarentena, en verde](https://github.com/gabeMoran05-coder/TDL-MANZADOCKER/actions/runs/42892045653).

El [tag `e1`](https://github.com/gabeMoran05-coder/TDL-MANZADOCKER/tree/e1) identifica el corte de entrega. Los cambios también están integrados en `main`; se conserva `gabriel/e1` como rama de desarrollo de Gabriel.

## Límites y revisión del equipo

- La imputación por terminal es una estimación señalada, no una cifra oficial ni una prueba de su mecanismo de ausencia.
- Las alertas de atípicos no demuestran errores ni relaciones causales; el pronóstico y la evaluación estadística corresponden al trabajo posterior del laboratorio.
- Esta ficha cubre la tarea de Ingeniería de Datos compartida por Gabriel. No declara terminados el pronóstico, el tablero ni el plan SQA que otras materias puedan solicitar para E1.
- Las horas personales PSP y la revisión cruzada deben ser confirmadas por los integrantes. La bitácora técnica no se presenta como tiempo personal.
- Continúa documentada en E0 la decisión pendiente sobre redistribución de materiales ASIPONA. Este pipeline no cambia permisos de fuentes ni realiza nuevas descargas.

## Uso de IA

Codex (OpenAI) se utilizó para revisar los archivos del proyecto, implementar los scripts y pruebas, ejecutar el pipeline y redactar esta documentación. Los resultados numéricos provienen de ejecuciones sobre Bronce; no se inventaron respuestas, horas personales ni revisiones humanas.
