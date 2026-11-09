# Entrega E0 · Observatorio del Puerto de Manzanillo (TDL-MANZADOCKER)

**Equipo:** Emilio Rodrigo Ayala Reynoso · Karol Gabriel Morán Aréchiga · **Etiqueta:** `e0` · **Tablero:** _pendiente (E1)_
**Repositorio:** https://github.com/gabeMoran05-coder/TDL-MANZADOCKER

## Resumen en tres líneas
1. Observatorio del Puerto de Manzanillo: pronosticar los TEU del mes siguiente y demostrar en qué temporadas se concentra la carga, para quien planea camiones y citas en terminal.
2. Dos fuentes funcionando: Estadística Mensual de ASIPONA (PDF, 69 meses de TEU, ene-2021 a sep-2026) y tipo de cambio FIX de Banxico (API, 1,472 días); captura diaria con GitHub Actions.
3. Sistema de calidad iniciado: registros PSP individuales, bitácora de cada ejecución y tres objetivos medibles (disponibilidad ≥ 95%, extracción exacta 100%, serie completa 100%).

## Ingeniería de Datos
| Criterio de la rúbrica | Evidencia (enlace) | Nota del equipo |
|---|---|---|
| Plan de recopilación (20) | [propuesta.md §4](propuesta.md#4-plan-de-recopilación) | Estructura, formato, frecuencia, método de acceso, robots.txt y términos por fuente; fuentes descartadas y motivo |
| Captura de dos fuentes | [extractores/asipona.py](../../extractores/asipona.py) · [extractores/banxico.py](../../extractores/banxico.py) · [extractores/base.py](../../extractores/base.py) | Extractor ético del kit, adaptado: robots.txt leído con nuestro User-Agent y pausa mínima de 1.5 a 2 s |
| Captura programada | [.github/workflows/captura.yml](../../.github/workflows/captura.yml) · _[enlace a una ejecución exitosa en Actions]_ | Diaria a las 08:00 en Colima, más ejecución manual |
| Serie histórica ≥ 36 periodos en bronce, con metadatos | [data/bronce/asipona/em_mensual.csv](../../data/bronce/asipona/em_mensual.csv) · [capturas.csv](../../data/bronce/asipona/capturas.csv) · [PDF crudos](../../data/bronce/asipona/pdf/) · [tipo_cambio_fix.csv](../../data/bronce/banxico/tipo_cambio_fix.csv) | 69 meses; cada fila con archivo, URL de origen y fecha de captura; SHA-256 de cada PDF |

## Análisis Estadístico
| Criterio de la rúbrica | Evidencia (enlace) | Nota del equipo |
|---|---|---|
| Pregunta y cliente (20) | [propuesta.md §1](propuesta.md#1-ficha-del-observatorio) · [§2 Entrevista](propuesta.md#2-entrevista-con-el-sector) | Entrevista anonimizada con un transportista del puerto |
| Preguntas analíticas (20) | [propuesta.md §3](propuesta.md#3-preguntas-analíticas) | Variable a pronosticar (E1), factores del experimento (E2) y grupos a comparar (E3) |
| Serie histórica identificada | [data/bronce/asipona/em_mensual.csv](../../data/bronce/asipona/em_mensual.csv) (`variable = teu_total`, `publicado = True`) | Segunda variable para la correlación cruzada: arribos de buques portacontenedores y tipo de cambio FIX |

## Calidad en los Sistemas de Información
| Criterio de la rúbrica | Evidencia (enlace) | Nota del equipo |
|---|---|---|
| Registros de defectos individuales | [defectos-emilio.csv](../../calidad/defectos-emilio.csv) · [defectos-gabriel.csv](../../calidad/defectos-gabriel.csv) | Tipos PSP; el defecto 1 de Emilio se detectó con la verificación suma = acumulado |
| Registros de tiempo individuales | [tiempo-emilio.csv](../../calidad/tiempo-emilio.csv) · [tiempo-gabriel.csv](../../calidad/tiempo-gabriel.csv) | Formato del kit |
| Bitácora de captura activa | [calidad/bitacora_captura.csv](../../calidad/bitacora_captura.csv) | Inicio, fin, duración, fuente, estado, registros, disparador y error; base para MTBF, MTTR y disponibilidad en E1 |
| Tres objetivos de calidad medibles | [propuesta.md §6](propuesta.md#6-arranque-del-sistema-de-calidad) | OC1 disponibilidad ≥ 95% · OC2 extracción exacta 100% · OC3 completitud de la serie 100% |
| Revisión cruzada | _[Quality Lead: nombre · fecha · resultado]_ | Uno revisa el trabajo del otro contra la rúbrica antes de crear el tag |

## Relatoría de etapa
No aplica en E0 (la primera relatoría es `docs/relatoria-E1.md`).

## Issues de la entrega anterior
No aplica (primera entrega).
