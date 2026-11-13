# E1 · Pronóstico mensual de TEU

**Gabriel Morán · Data Statistician · 12 de noviembre de 2026.**
Resultados de [E1_pronostico.ipynb](../../laboratorio/E1_pronostico.ipynb), ejecutado completo con salidas guardadas. [Gráficas](figuras/) y [métricas/diagnósticos](../../data/oro/pronostico_metricas.json) permiten revisar cada cifra.

## Datos y caracterización

Objetivo: `teu_total`, confirmado con el diccionario. Se usan 70 meses, enero de 2021–octubre de 2026, sin faltantes en las tres series analizadas. El corte de `parametros_transformacion.json` es abril de 2026: 64 meses de entrenamiento y mayo–octubre de 2026 como bloque fijo de prueba. Se conserva ese corte.

La pendiente descriptiva de entrenamiento es 1,086.2 TEU/mes, con cambios visibles pero sin rupturas estructurales confirmadas. Menos de seis años limitan identificar ciclos plurianuales independientes. Mínimo: 251,937 TEU en febrero de 2023; máximo: 384,691 en julio de 2026.

## Descomposición, ADF y dependencia

Se elige descomposición **aditiva**, periodo 12: RMSE de reconstrucción 12,219.4 frente a 12,339.8 TEU multiplicativa, comparando los mismos meses interiores en unidades iguales. La mejora es pequeña; el perfil de entrenamiento tiene máximo en octubre y mínimo en febrero, no una garantía para cada año.

ADF (máximo 12, autolag AIC): nivel con constante p=0.28884; diferencia regular 2.1389e-05; estacional 0.29006; ambas 0.45315. Se usa **d=1, D=0**. Con tendencia en niveles se rechaza (p=4.1089e-07): también es plausible estacionariedad alrededor de tendencia; no se demuestra integración I(1).

ACF transformada: rezagos puntuales 1 y 6; PACF: 1 y 7. El rezago 1 negativo cercano a −0.5 aconseja vigilar sobrediferenciación. Tras preblanqueo y Holm (50 contrastes), solo buques en **k=0** es significativo (r=0.6832; p=2.38×10⁻⁷): asociación contemporánea, no anticipación. Con FIX no se detectan rezagos significativos; no prueba ausencia de relación.

## Cuatro modelos y selección

SES, Holt y Holt-Winters se ajustan como ETS. De 23 SARIMA convergentes, AIC elige (2,1,1)×(0,0,0,12): caso ARIMA anidado sin forzar estacionalidad. ADF y ACF/PACF orientan la búsqueda. Los cuatro usan un único origen y los mismos seis meses de prueba.

| Modelo | MAE (TEU) | RMSE (TEU) | MAPE |
|---|---:|---:|---:|
| SES | 24,120.50 | 30,033.69 | 6.4824% |
| Holt | 25,025.63 | 27,414.61 | 6.8918% |
| Holt-Winters | 23,484.11 | 27,898.45 | 6.5107% |
| SARIMA | 24,973.01 | 27,188.33 | 6.8849% |

Gana **SES por MAPE**, criterio fijado en E0; SARIMA minimiza RMSE y Holt-Winters MAE. La ventaja frente a Holt-Winters es solo 0.0283 puntos porcentuales: seis meses no demuestran superioridad futura.

## Residuos, intervalo y resultado para el cliente

Reentrenado SES con 70 meses, se revisan 58 residuos. Ljung-Box p=0.08368, 0.37389 y 0.31651 en rezagos 6, 12 y 24 (model_df=0, orientativo). Jarque-Bera p=0.54560; ARCH(6) p=0.82511; Levene p=0.99501. No rechazar no prueba los supuestos: la varianza móvil máxima es 5.34 veces la mínima.

| Mes | Pronóstico TEU | Intervalo nominal 95% |
|---|---:|---:|
| 2026-11 | 344,909 | 307,550–382,269 |
| 2026-12 | 344,909 | 305,909–383,910 |
| 2027-01 | 344,909 | 304,334–385,485 |

SES mantiene el nivel puntual sin tendencia ni estacionalidad; la incertidumbre crece. Los intervalos gaussianos son individuales y condicionales, con parámetros estimados; no cubren plenamente selección del modelo ni cambios estructurales.

> Para planear flota: estimamos 344,909 TEU en noviembre, rango nominal 307,550–382,269 bajo el modelo. Es capacidad del puerto, no garantía ni demanda de tu empresa; combínalo con los avisos del cliente. Noviembre sigue a octubre publicado y ya está en curso.

## Exportación, reproducción y revisión

Se exportan [pronostico_teu.csv](../../data/oro/pronostico_teu.csv) con las seis columnas exactas y límites vacíos en histórico, y [pronostico_metricas.json](../../data/oro/pronostico_metricas.json) con cuatro modelos, ganador, supuestos y SHA-256. Si cambia Oro debe ejecutarse nuevamente; la prueba detecta un pronóstico desactualizado.

Reproducir: `jupyter nbconvert --to notebook --execute --inplace laboratorio/E1_pronostico.ipynb`. En Windows se usó `python -m nbconvert` porque el lanzador está bloqueado, con el kernel del entorno correcto. Las [pruebas](../../tests/test_pronostico.py) validan el contrato y las salidas guardadas.

Para Emilio: se propone sustituir «19 de cada 20 meses» del tablero por la frase condicional del JSON; no se ha medido esa cobertura prospectivamente. Revisión, integración y tag quedan a su cargo.

Incidencias propuestas para confirmar en PSP: escapes al generar dos celdas (sintaxis), argumento `old_names` retirado de AutoReg 0.15 (interfaz) y lanzador Jupyter bloqueado (entorno). Ya están resueltas/verificadas; no se asignan autoría personal, minutos ni registros CSV sin confirmación.

Se corrigió además la regla Git que normalizaba PNG como texto (construcción): las siete figuras se marcan binarias y se verifica su legibilidad también como objetos Git.

**Codex (OpenAI)** asistió en programación, ejecución y redacción. Las cifras proceden de la ejecución; el notebook enlaza las referencias primarias de statsmodels.
