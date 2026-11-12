# Requerimientos verificables del observatorio (E1 · Calidad)

**Responsable:** Emilio Rodrigo Ayala Reynoso · **Versión:** 1.0, 12 de noviembre de 2026
**Revisión pendiente por:** Karol Gabriel Morán Aréchiga (en el pull request de `emilio/e1`)

Cada requerimiento se revisó contra las cuatro características de un buen requerimiento:
- **Necesario:** tiene un origen (la pregunta del cliente, un objetivo de calidad o una regla del proyecto).
- **No ambiguo:** usa un número o una condición concreta, no adjetivos.
- **Verificable:** dice cómo se comprueba.
- **Rastreable:** tiene un ID y un origen, y se puede seguir hasta su prueba.

**Orígenes usados:** P = pregunta central y entrevistas ([propuesta E0](../E0/propuesta.md)) · OC = objetivos de calidad de E0 · R = reglas del proyecto (PDF Trusted Data Lab) · E1 = rúbrica de E1.

## 1. Requerimientos funcionales

| ID | Requerimiento | Origen | Cómo se comprueba | Estado al 12/11 |
|---|---|---|---|---|
| RF-01 | El sistema captura automáticamente, una vez al día, la Estadística Mensual de ASIPONA y el tipo de cambio FIX de Banxico, y guarda cada archivo en `data/bronce/` con URL de origen y fecha de captura. | R (captura multifuente), OC1 | `captura.yml` (cron diario); columnas `url_origen` y `fecha_captura_utc` en Bronce; filas `schedule` en `calidad/bitacora_captura.csv` | Cumple |
| RF-02 | Cada ejecución de captura deja una fila por fuente en la bitácora con inicio, fin, duración, estado, registros y error. | OC1, E1 (fiabilidad) | `extractores/run_captura.py`; `tests/test_fiabilidad.py` lee la bitácora real | Cumple |
| RF-03 | La serie mensual de TEU totales en Oro cubre todos los meses publicados desde enero de 2021, sin huecos. | P, OC3 | `test_ruptura_de_serie_bloquea_publicacion_y_deja_bitacora`; 70 meses en `data/oro/mensual_integrado.csv` | Cumple |
| RF-04 | Todo registro que no cumple el contrato de datos (esquema, tipos, rangos, unicidad o reglas de negocio) pasa a `data/cuarentena/` con su fuente, etapa, motivo y contenido original; ninguno se borra en silencio. | E1 (puerta de calidad), R | `test_filas_invalidas_quedan_trazadas`, `test_duplicados_se_aislan_completos`, `test_cambio_de_esquema_rechaza_lote`, `test_pandera_estricto_no_silencia_columnas_extras` | Cumple |
| RF-05 | En cada ejecución, el número de registros de entrada es igual a aceptados + rechazados. | E1 | `calidad/e1/resumen.json` (asipona: 648 = 626 + 22); `test_pipeline_real_reproducible_y_conserva_bronce` lo verifica y `src/limpieza.py` detiene la ejecución si no se conserva el balance | Cumple |
| RF-06 | Un mes no publicado por la fuente nunca se interpreta como cero. | E1 (faltantes), OC2 | `test_no_publicado_no_se_interpreta_como_cero` | Cumple |
| RF-07 | La imputación de un faltante usa solo meses anteriores y queda marcada como estimación. | E1 (faltantes) | `test_imputacion_no_mira_futuro_ni_reutiliza_imputados`, `test_imputacion_no_se_contamina_por_registro_invalido` | Cumple |
| RF-08 | Los atípicos se marcan con IQR y puntaje robusto y se conservan; no se eliminan. | E1 (atípicos), entrevista (P1: las caídas por tifones son reales) | `test_atipicos_conservados_y_ajuste_sin_prueba`; columna `es_atipico_teu` en Oro | Cumple |
| RF-09 | Las escalas Min-Max y Z-Score se ajustan solo con los meses de entrenamiento (sin los 6 meses de prueba). | E1 (normalización) | `test_escalas_y_variable_constante`; `data/oro/parametros_transformacion.json` | Cumple |
| RF-10 | Las fuentes se integran en Oro con una sola fila por mes; un mes con datos de Banxico incompletos no entra. | E1 (integración) | `test_conflictos_banxico`, `test_contrato_oro_estricto`; columna `fix_mes_completo` | Cumple |
| RF-11 | El tablero publica el pronóstico de TEU del siguiente mes con su intervalo de predicción del 95% y una frase para el cliente. | P, E1 (Estadística) | Revisión del tablero publicado; contrato de `data/oro/pronostico_teu.csv` (`li_95 <= valor <= ls_95`) | En construcción |
| RF-12 | El modelo de pronóstico publicado es el de menor error (MAE, RMSE, MAPE) en los 6 meses de prueba entre SES, Holt, Holt-Winters y SARIMA. | E1 (Estadística) | `data/oro/pronostico_metricas.json`; notebook `laboratorio/E1_pronostico.ipynb` | En construcción (Gabriel) |

## 2. Requerimientos no funcionales

| ID | Requerimiento | Origen | Cómo se comprueba | Estado al 12/11 |
|---|---|---|---|---|
| RNF-01 | **Disponibilidad:** al menos 95% de las capturas programadas terminan con éxito (OC1). | OC1 | `python -m src.fiabilidad` → `calidad/e1/fiabilidad.json` | Cumple en lo observado (4 de 4); muestra corta, ver [fiabilidad](fiabilidad.md) |
| RNF-02 | **Recuperación:** una falla de captura se corrige en 24 h o menos (MTTR ≤ 24 h). | Plan SQA | `mttr_h` en `calidad/e1/fiabilidad.json` | Sin fallas aún; no medible |
| RNF-03 | **Exactitud de extracción:** en el 100% de las combinaciones variable-año, la suma de meses difiere del acumulado reportado por 2 unidades o menos (OC2). | OC2 | Columna `diferencia` de `data/bronce/asipona/em_mensual.csv`; `test_recalculo_del_acumulado_no_confia_en_bandera_cuadra` | Cumple |
| RNF-04 | **Reproducibilidad:** ejecutar dos veces el pipeline sobre el mismo Bronce produce archivos idénticos (mismo SHA-256) y no modifica Bronce. | R (todo es reproducible) | `test_pipeline_real_reproducible_y_conserva_bronce` | Cumple |
| RNF-05 | **Mantenibilidad:** cada cambio a `main` pasa ruff sin errores y pytest con al menos 90% de cobertura de `src/`. | Plan SQA | `ci.yml`; `fail_under = 90` en `pyproject.toml` | Cumple |
| RNF-06 | **Seguridad:** 0 secretos en el historial y 0 vulnerabilidades conocidas en las dependencias en cada push. | E1 (seguridad) | Pasos gitleaks y pip-audit de `ci.yml` | Cumple |
| RNF-07 | **Respaldo:** cada captura genera un respaldo de Bronce verificado por SHA-256 y lo conserva 90 días. | E1 (seguridad) | `src/respaldo.py`; artefacto `respaldo-bronce-<id>` en Actions; `calidad/e1/respaldo_prueba.json` | Cumple localmente; primer artefacto en la siguiente captura |
| RNF-08 | **Ética del scraping:** cada petición respeta robots.txt, se identifica con un User-Agent con la URL del repositorio y espera al menos 1 s entre peticiones al mismo dominio. | R (scraping ético) | `extractores/base.py` (`ExtractorEtico`, pausa mínima de 1.5 s) | Cumple |
| RNF-09 | **Privacidad:** el repositorio no contiene nombres, teléfonos ni correos de personas entrevistadas. | R (cero datos personales) | Revisión de `docs/` en cada pull request (lista de comprobación del plan SQA) | Cumple |
| RNF-10 | **Usabilidad:** el tablero se lee sin desplazamiento horizontal en un teléfono de 375 px de ancho. | P (cliente no técnico) | Prueba con Playwright en escritorio y móvil (capturas en el PR) | En construcción |

## 3. Requerimientos revisados y reescritos

Ejemplos de cómo se corrigieron redacciones que no cumplían las cuatro características:

| Redacción original | Problema | Versión verificable |
|---|---|---|
| "El sistema debe ser confiable." | Ambigua y no verificable | RNF-01 y RNF-02 |
| "Los datos deben estar limpios." | No dice qué es limpio ni cómo medirlo | RF-04, RF-05 y RF-06 |
| "El tablero debe ser fácil de usar." | Adjetivo sin medida | RNF-10 (ancho concreto y prueba automatizada) |
| "Hay que pronosticar bien." | Sin criterio de "bien" | RF-12 (criterio de menor error en datos no vistos) |

## 4. Matriz de rastreabilidad (resumen)

| Origen | Requerimientos |
|---|---|
| Pregunta central y entrevistas | RF-03, RF-08, RF-11, RNF-10 |
| OC1 (disponibilidad ≥ 95%) | RF-01, RF-02, RNF-01 |
| OC2 (exactitud de extracción) | RF-06, RNF-03 |
| OC3 (completitud de la serie) | RF-03 |
| Rúbrica E1, Ingeniería de Datos | RF-04 a RF-10 |
| Rúbrica E1, Estadística | RF-11, RF-12 |
| Rúbrica E1, Calidad | RNF-01, RNF-02, RNF-05 a RNF-07 |
| Reglas del proyecto | RF-01, RNF-04, RNF-08, RNF-09 |
