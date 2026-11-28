# Calidad, modelos de proceso y Sello TDL · E3

## Auditoría cruzada

No se localizó un informe del equipo auditor asignado ni hallazgos externos en la documentación E2. Por tanto no es posible construir una lista completa, verificar el cierre de cada hallazgo ni afirmar cero críticos abiertos. Solicitar el informe real con identificador, severidad, evidencia y recomendación; registrar acción, prueba de cierre y aceptación del auditor. Las observaciones internas de [seguridad E1](../E1/seguridad.md) no sustituyen la auditoría cruzada: S1 fijación de acciones por SHA, S2 versiones exactas, S3 protección de rama, S4 redistribución ASIPONA y S5 rotación de token requieren comprobación o acción; no se atribuye su cierre sin evidencia.

## Autoevaluación de proceso

Comparación orientativa sobre evidencia disponible, no evaluación acreditada. En MoProSoft se aprecian prácticas iniciales de operación (código, pruebas, captura y cuarentena), gerencia (plan SQA, riesgos, bitácoras parciales) y dirección (objetivos y propuesta), pero faltan seguimiento completo, auditoría externa y mediciones personales completas. Para CMMI existen prácticas de planeación, gestión de configuración, aseguramiento de calidad y medición en un proyecto; revisiones previas no fueron consistentes y las métricas no cubren todo el proceso. El perfil es **parcial y reactivo**, compatible con algunas prácticas de gestión a nivel de proyecto, pero sin evidencia suficiente para asignar formalmente capacidad o madurez de nivel 2. Ningún nivel está certificado. Prioridades: protección de rama y revisión previa; registrar estimaciones y tiempos; auditoría cruzada; control de versiones y reproducibilidad independiente.

| Enfoque | Alcance | Aplicación y brecha aquí |
|---|---|---|
| ISO 9001 | Sistema de gestión de calidad de la organización | SQA y riesgos existen; faltan evaluación integral, seguimiento y auditoría del sistema. |
| MoProSoft NMX-I-059 | Procesos de desarrollo y mantenimiento de software | Hay procesos de operación y gestión; falta evaluación formal de capacidad. |
| SPICE / ISO/IEC 33000 | Marco para evaluación de procesos y capacidad | Se requieren modelo de evaluación, evidencias y evaluación sistemática; no se ha aplicado formalmente. |
| CMMI | Mejora de desempeño mediante áreas de práctica y niveles | Hay prácticas parciales; no hay appraisal de madurez. |
| PSP/TSP | Medición y mejora personal y del equipo | Hay registros individuales; falta estimación, duración y cobertura completa. |

Referencias: [NYCE MoProSoft](https://nyce.org.mx/inspeccion-de-software-moprosoft-nmx-i-059-02-nyce-2016/), [CMMI niveles](https://prod.cmmiinstitute.com/learning/appraisals/levels), [ISO/IEC 33002](https://www.iso.org/standard/54177.html), [ISO 9001](https://www.iso.org/standard/62085.html). No se afirma conformidad con normas ni certificación.

## Retrospectiva PSP

Los [registros de tiempo de Emilio](../../calidad/tiempo-emilio.csv) contienen 23 entradas completas y 318 minutos netos: planeación 21, diseño 4, código 117, documentación 58 y revisión 118 (corte 27/11). Los [de Gabriel](../../calidad/tiempo-gabriel.csv) contienen 10 entradas, sin ninguna con inicio, fin **e interrupciones** completos; la entrevista indica 15 minutos aproximados, pero no confirma interrupciones. No se calcula total personal comparable. No existen estimaciones previas en estos archivos, así que no puede calcularse exactitud de estimación.

En [defectos de Emilio](../../calidad/defectos-emilio.csv), hay 10 registrados: 7 se introdujeron en código y 3 en diseño; 7 se eliminaron en revisión y 3 en pruebas. Siete tienen tiempos que suman 29 minutos; los defectos 8, 9 y 10 no tienen duración medida. En [Gabriel](../../calidad/defectos-gabriel.csv), 4 se introdujeron en código, 2 en integración y 1 en selección de fuente; se eliminaron 4 en pruebas, 2 en revisión y 1 en validación de fuente; no hay minutos de corrección medidos. Son defectos registrados, no denominadores completos: no puede calcularse rendimiento de revisión ni tasa de escape.

Por fecha, Emilio registró 2 defectos el 8/11, 2 el 12/11, 4 entre el 19 y 22/11 y 2 en E3 (26 y 27/11: robots 429 y encabezados DENUE); Gabriel registró 7 el 17/11. Los registros no incluyen estimaciones ni una clasificación uniforme E0–E3 y en E3 solo hay dos sesiones de Emilio (27/11, 86 min en total, sin estimación previa): no se infiere una tendencia de rendimiento ni se convierte tiempo del agente en tiempo humano. Completar estimaciones previas, interrupciones, fase/etapa y defectos detectados por fase antes de comparar.

## Tendencia aplicada: observabilidad de datos

La observabilidad de datos vigila actualización, volumen, esquema y calidad durante todo el ciclo de vida. Aquí existen bitácoras por fuente, contratos Pandera, cuarentena con motivo, hashes y linaje; el caso DENUE ilustra privacidad antes de persistir. La brecha es que éxito técnico no equivale a captura puntual: medir días previstos sin ejecución, retraso y completitud por fuente, alertar y asignar dueño de respuesta. Mantener umbrales y resultados por fecha, sin sustituir la revisión del dato por un estado verde. El [plan SQA](../E1/plan-sqa.md) documenta umbrales y controles; aún no acredita un servicio de alertas independiente.

## Evaluación del Sello TDL

Corte de evidencia de captura: 24/11/2026 23:24 UTC. Ventana de 14 días completos UTC, 11–24/11: 13 días con al menos una ejecución programada exitosa de 14 (92.86 %); el 23 no registra inicio. El cron se retrasó hasta el 24 y hubo dos ejecuciones ese día. La métrica E1 de MTBF/MTTR registra 100 % observado para ejecuciones sin fallo, pero no mide ausencia de ejecución ni sustituye cumplimiento de calendario. Se muestra ambos por la ambigüedad del umbral de disponibilidad; bajo cumplimiento diario no alcanza 95 %.

| Criterio | Umbral | Evidencia y estado |
|---|---|---|
| Disponibilidad captura, últimos 14 días | ≥95 % | 13/14 días con ejecución programada exitosa, 92.86 %; no alcanza bajo este criterio de calendario. [Bitácora](../../calidad/bitacora_captura.csv). |
| Completitud Oro | ≥95 % | 100 % de celdas no nulas en mensual integrado (2,100/2,100), terminales (4,480/4,480) y DENUE (420/420). Medición parcial de tres CSV, no certifica todos los productos Oro ni pertinencia de campos. |
| Cobertura automática | ≥60 % | **Cumple.** 94.78 % de `src` con 97 pruebas aprobadas en `emilio/e3` el 27/11 (`pytest --cov=src`); [informe del 25/11](../../calidad/e3/cobertura.json). No cubre todo el tablero ni los extractores. |
| Secretos expuestos | 0 | **Cumple.** gitleaks 8.30.1 el 27/11 sobre todo el historial (`--all`, 57 commits sin fusiones): 0 hallazgos. En la carpeta local solo aparece `.env`, ignorado por Git y nunca versionado. [Evidencia sin valores](../../calidad/e3/secretos.json). |
| Hallazgos críticos de auditoría abiertos | 0 | Desconocido: no se recibió el informe cruzado. |
| Reproducibilidad | Tercero clona y obtiene mismos resultados | **Parcial.** Emilio, que no escribió los scripts E3, los ejecutó en una copia limpia de `e3-revision-2` con entorno nuevo: `pca.json`, `pca_puntos.csv` e `indicadores.json` salieron con SHA-256 idéntico y pasaron 96 pruebas ([detalle](../../calidad/e3/reproduccion_emilio.json)). Es del mismo equipo y en su propio equipo de cómputo; falta un tercero externo. |

**Actualización del 27/11 (disponibilidad).** Las capturas programadas del 26 y 27/11 fallaron en DENUE: INEGI cambió los encabezados del CSV a mayúsculas y el extractor descartaba todas las filas («DENUE no devolvió celdas publicables»). ASIPONA y Banxico sí se capturaron. Con el mismo criterio de calendario, la ventana 14–27/11 da 11/14 días (78.57 %; sin éxito el 23, 26 y 27). La corrección y su prueba están en la rama `emilio/e3`; la captura diaria corre sobre `main`, así que seguirá fallando hasta que se una. Aunque se una de inmediato, cualquier ventana de 14 días que cierre antes de la entrega incluye esos tres días: el umbral de 95 % no puede alcanzarse para E3.

[Cálculo reproducible](../../scripts/indicadores_e3.py) y [resultados](../../calidad/e3/indicadores.json). Ejecutar `python -m scripts.indicadores_e3`; el corte queda fijo para reproducir esta revisión.

No se solicita ni declara obtenido el sello mientras falten los criterios y evidencias. El formulario oficial de entrega no fue proporcionado.
