# Entrega E1 · Observatorio del Puerto de Manzanillo (TDL-MANZADOCKER)

**Equipo:** Emilio Rodrigo Ayala Reynoso (Data Engineer, Quality Lead de E1) · Karol Gabriel Morán Aréchiga (Data Statistician)<br>
**Etiqueta:** [`e1`](https://github.com/gabeMoran05-coder/TDL-MANZADOCKER/tree/e1) · **Entrega:** 13 de noviembre de 2026, 17:59 · **Tablero:** _URL de Streamlit Community Cloud pendiente_ ([código](../../tablero/app.py))<br>
**Repositorio:** https://github.com/gabeMoran05-coder/TDL-MANZADOCKER

## Resumen en tres líneas

1. Los datos viajan solos de Bronce a Plata y Oro: una puerta Pandera admitió 626 de 648 registros del puerto y apartó 22 en cuarentena con su motivo (meses aún no publicados); 70 meses integrados con el tipo de cambio.
2. Cuatro modelos comparados en 6 meses que no vieron: gana suavizamiento exponencial simple (MAPE 6.48%) y pronostica 344,909 TEU para noviembre de 2026 (rango nominal del 95%: 307,550–382,269), publicado en el tablero.
3. La captura programada cumplió 4 de 4 días (OC1 en lo observado, con muestra corta); 0 secretos, 0 vulnerabilidades, respaldo de Bronce probado; plan SQA IEEE 730; CI con 54 pruebas y 97% de cobertura.

## Ingeniería de Datos

| Criterio de la rúbrica | Evidencia (enlace) | Nota del equipo |
|---|---|---|
| Valores faltantes (15) | [Limpieza §2](limpieza.md#2-faltantes-diagnóstico-y-tratamiento) · [preprocesamiento.py](../../src/preprocesamiento.py) | Se distinguen ausencias estructurales, 8 ceros sospechosos de 2021 por terminal y errores. MAR se plantea como hipótesis, sin afirmarla probada; imputación por mediana causal (solo meses anteriores). |
| Atípicos y ruido (15) | [Limpieza §3](limpieza.md#3-atípicos-y-ruido) · [Plata ASIPONA](../../data/plata/asipona_mensual.csv) | IQR y puntaje robusto; los extremos válidos se marcan y se conservan (la entrevista confirma caídas reales por tifones en Asia). |
| Normalización, discretización y reducción (15) | [Oro](../../data/oro/mensual_integrado.csv) · [parámetros](../../data/oro/parametros_transformacion.json) · [Limpieza §4–5](limpieza.md#4-escalas-discretización-y-jerarquías) · [diccionario](diccionario.md) | Min-Max y Z-Score ajustados sin los 6 meses de prueba; actividad baja/media/alta; jerarquías año/trimestre/mes y país/estado/puerto; FIX diario agregado a mensual (reducción 95.19%, se conserva el diario en Plata). |
| Integración de fuentes (20) | [limpieza.py](../../src/limpieza.py) · [Oro CSV](../../data/oro/mensual_integrado.csv) · [Parquet](../../data/oro/mensual_integrado.parquet) | Clave mensual uno a uno; tipos y unidades explícitos; duplicados, conflictos de cotización y meses incompletos resueltos. |
| Puerta de calidad (25) | [calidad.py](../../src/calidad.py) · [cuarentena](../../data/cuarentena/e1/) · [pruebas](../../tests/test_e1.py) | Contratos estrictos; cada rechazo guarda fuente, etapa, motivo y registro original; balance entrada = aceptados + rechazados. |

## Análisis Estadístico

| Criterio de la rúbrica | Evidencia (enlace) | Nota del equipo |
|---|---|---|
| Caracterización y descomposición (15) | [Pronóstico](pronostico.md#descomposición-adf-y-dependencia) · [notebook](../../laboratorio/E1_pronostico.ipynb) · [figuras](figuras/) | Aditiva elegida por menor error de reconstrucción (12,219 vs. 12,340 TEU); la diferencia es pequeña y se dice. |
| Estacionariedad y autocorrelación (15) | [Pronóstico](pronostico.md#descomposición-adf-y-dependencia) | ADF: nivel p=0.289, primera diferencia p≈2×10⁻⁵ → d=1, D=0. ACF/PACF interpretadas. Correlación cruzada: solo buques en k=0 (r=0.68), sin anticipación; FIX sin rezagos significativos. |
| Cuatro modelos (25) | [Pronóstico](pronostico.md#cuatro-modelos-y-selección) · [métricas](../../data/oro/pronostico_metricas.json) | SES, Holt, Holt-Winters y SARIMA(2,1,1) elegido por AIC entre 23 candidatos guiados por ACF/PACF. |
| Selección por error (20) | [tabla de errores](pronostico.md#cuatro-modelos-y-selección) | Gana SES por MAPE (6.48%); se informa que SARIMA gana en RMSE y Holt-Winters en MAE, y que el margen es pequeño. |
| Residuos y comunicación (15) | [Pronóstico](pronostico.md#residuos-intervalo-y-resultado-para-el-cliente) · [tablero](../../tablero/app.py) · [CSV](../../data/oro/pronostico_teu.csv) | Ljung-Box no rechaza (p=0.08, 0.37, 0.32); intervalo nominal del 95% publicado con una frase condicional para el cliente. |

## Calidad en los Sistemas de Información

| Criterio de la rúbrica | Evidencia (enlace) | Nota del equipo |
|---|---|---|
| Fiabilidad y disponibilidad (25) | [fiabilidad.md](fiabilidad.md) · [fiabilidad.py](../../src/fiabilidad.py) · [resultado](../../calidad/e1/fiabilidad.json) · [bitácora](../../calidad/bitacora_captura.csv) | 4 de 4 capturas programadas y 4 de 4 días; MTBF no medible aún (sin fallas, cota inferior 70 h). Hay 4–5 días de bitácora, no 7: la captura programada empezó el 9 de noviembre. Retraso del cron de 7.6 h en promedio. |
| Seguridad (15) | [seguridad.md](seguridad.md) · [respaldo.py](../../src/respaldo.py) · [prueba de respaldo](../../calidad/e1/respaldo_prueba.json) | gitleaks: 0 secretos en todo el historial; pip-audit: 0 vulnerabilidades; respaldo de Bronce restaurado y comparado por SHA-256 (17 archivos, 0 diferencias). |
| Requerimientos (10) | [requerimientos.md](requerimientos.md) | 12 funcionales y 10 no funcionales, cada uno con origen, comprobación y estado. |
| Plan SQA (25) | [plan-sqa.md](plan-sqa.md) | Estructura IEEE 730 adaptada a dos personas: roles, métricas OC1–OC3 y MTTR ≤ 24 h, revisiones, pruebas, lista de comprobación de PR, herramientas, ramas y riesgos. |
| Integración continua (15) | [ci.yml](../../.github/workflows/ci.yml) · [CI de main con todo unido](https://github.com/gabeMoran05-coder/TDL-MANZADOCKER/actions/runs/43477084951) · [captura](../../.github/workflows/captura.yml) | En cada push y PR: gitleaks, pip-audit, ruff, pytest (54 pruebas, cobertura 97%, mínimo 90%) y generación de Plata y Oro. |

## Revisión cruzada

| Revisión | Quién | Resultado |
|---|---|---|
| PR #2 (Estadística, Gabriel) | Emilio, como Quality Lead, **después** de la unión | Contrato del CSV correcto, 54 pruebas en verde al combinar ambos PR, pip-audit y gitleaks sin hallazgos, residuos revisados. Se unió el 12/11 sin revisión previa. |
| PR #1 (Calidad y tablero, Emilio) | Unido por Emilio el 13/11 con CI en verde, **sin revisión previa de Gabriel** | Desviación del plan SQA registrada en la relatoría; acción correctiva para E2: activar la protección de `main`. |
| PR #3 (ficha y relatoría, Emilio) | Unido por Emilio el 13/11 con CI en verde, **sin revisión de Gabriel** (no estaba disponible antes de la hora límite) | Solo documentación y una frase del tablero; Gabriel revisará después de la entrega. |

## Relatoría de etapa

[docs/relatoria-E1.md](../relatoria-E1.md)

## Issues de la entrega anterior

No se recibieron issues de los docentes sobre E0 (consultado el 13 de noviembre de 2026).
