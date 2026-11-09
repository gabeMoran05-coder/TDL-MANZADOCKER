# Entrega E0 · Observatorio del Puerto de Manzanillo (TDL-MANZADOCKER)

**Equipo:** Emilio Rodrigo Ayala Reynoso · Karol Gabriel Morán Aréchiga · **Etiqueta prevista:** `e0` · **Tablero:** _pendiente (E1)_
**Repositorio:** https://github.com/gabeMoran05-coder/TDL-MANZADOCKER
**Rama de Gabriel:** [gabriel/e0](https://github.com/gabeMoran05-coder/TDL-MANZADOCKER/tree/gabriel/e0)
**Estado al 9 de noviembre de 2026:** en preparación; los pendientes de cierre se detallan al final.

## Resumen en tres líneas
1. Observatorio del Puerto de Manzanillo: pronosticar los TEU del mes siguiente y demostrar en qué temporadas se concentra la carga, para quien planea camiones y citas en terminal.
2. Dos fuentes capturadas con éxito en GitHub Actions: ASIPONA (PDF, 70 meses de TEU, ene-2021 a oct-2026) y Banxico (API, 1,473 fechas). Primera ejecución manual exitosa el 9/11; programación diaria activa.
3. Sistema de calidad iniciado: registros PSP individuales, bitácora y tres objetivos medibles (éxito programado ≥ 95%, conciliación con tolerancia de dos unidades 100%, serie completa 100%).

## Ingeniería de Datos
| Criterio de la rúbrica | Evidencia (enlace) | Nota del equipo |
|---|---|---|
| Plan de recopilación (20) | [propuesta.md §4](propuesta.md#4-plan-de-recopilación) | Estructura, formato, frecuencia, método de acceso, robots.txt y términos por fuente; fuentes descartadas y motivo |
| Captura de dos fuentes | [extractores/asipona.py](../../extractores/asipona.py) · [extractores/banxico.py](../../extractores/banxico.py) · [extractores/base.py](../../extractores/base.py) | Extractor ético del kit, adaptado: robots.txt leído con nuestro User-Agent y pausa mínima de 1.5 a 2 s |
| Captura programada | [.github/workflows/captura.yml](../../.github/workflows/captura.yml) · [Ejecución exitosa](https://github.com/gabeMoran05-coder/TDL-MANZADOCKER/actions/runs/42679626943) · [Commit del bot](https://github.com/gabeMoran05-coder/TDL-MANZADOCKER/commit/f126715) | Ambas fuentes `ok`, con datos y bitácora guardados. Ejecución manual verificada; horario diario 08:00 en Colima activo. Primera ejecución `schedule` pendiente de observar. |
| Serie histórica ≥ 36 periodos en bronce, con metadatos | [data/bronce/asipona/em_mensual.csv](../../data/bronce/asipona/em_mensual.csv) · [capturas.csv](../../data/bronce/asipona/capturas.csv) · [PDF crudos](../../data/bronce/asipona/pdf/) · [tipo_cambio_fix.csv](../../data/bronce/banxico/tipo_cambio_fix.csv) | 70 meses consecutivos, sin duplicados de año-mes; archivo, URL y fecha de captura; SHA-256 comprobados de 7 PDF. Banxico: 1,473 fechas. |

## Análisis Estadístico
| Criterio de la rúbrica | Evidencia (enlace) | Nota del equipo |
|---|---|---|
| Pregunta y cliente (20) | [propuesta.md §1](propuesta.md#1-ficha-del-observatorio) · [§2 Entrevista](propuesta.md#2-entrevista-con-el-sector) | Cinco preguntas y respuestas de una dueña de transportista, por mensajes de WhatsApp el 8/11 alrededor de las 16:50; duración de 15 minutos confirmada por Gabriel. Consentimiento y significado de «50%» pendientes. Cliente potencial identificado; pago no confirmado. |
| Preguntas analíticas (20) | [propuesta.md §3](propuesta.md#3-preguntas-analíticas) | Variable a pronosticar (E1), factores del experimento (E2) y grupos a comparar (E3) |
| Serie histórica identificada | [data/bronce/asipona/em_mensual.csv](../../data/bronce/asipona/em_mensual.csv) (`variable = teu_total`, `publicado = True`) | Segunda variable para la correlación cruzada: arribos de buques portacontenedores y tipo de cambio FIX |

## Calidad en los Sistemas de Información
| Criterio de la rúbrica | Evidencia (enlace) | Nota del equipo |
|---|---|---|
| Registros de defectos individuales | [defectos-emilio.csv](../../calidad/defectos-emilio.csv) · [defectos-gabriel.csv](../../calidad/defectos-gabriel.csv) | Tipos PSP; el defecto 1 de Emilio se detectó con la verificación suma = acumulado |
| Registros de tiempo individuales | [tiempo-emilio.csv](../../calidad/tiempo-emilio.csv) · [tiempo-gabriel.csv](../../calidad/tiempo-gabriel.csv) | Entrevista por mensajes del 8/11: 15 minutos, de aproximadamente 16:50 a 17:05 (fin calculado). Trabajo asistido de E0 del 9/11: fin aproximado 13:00 e inicio pendiente. Interrupciones de ambas sesiones pendientes. Ver [detalle](planeacion-gabriel.md). |
| Bitácora de captura activa | [calidad/bitacora_captura.csv](../../calidad/bitacora_captura.csv) | Inicio, fin, duración, fuente, estado, registros, disparador y error; base para MTBF, MTTR y disponibilidad en E1 |
| Tres objetivos de calidad medibles | [propuesta.md §6](propuesta.md#6-arranque-del-sistema-de-calidad) | OC1 éxito programado ≥ 95% · OC2 conciliación con tolerancia ≤ 2 unidades en 100% de combinaciones · OC3 completitud 100% |
| Revisión cruzada | Pendiente de realizar por un integrante y registrar nombre, fecha y resultado | La comprobación asistida de archivos no sustituye la revisión cruzada del equipo. |

## Pendientes para cerrar E0

- Confirmar el permiso para utilizar las notas anónimas de la entrevista. El medio por mensajes de WhatsApp y la duración de 15 minutos ya fueron confirmados por Gabriel.
- Aclarar qué significa «valdría un 50%» y validar periodicidad y disposición de pago; no se presenta como precio confirmado.
- Observar la primera captura con disparador `schedule`. El secret y la primera ejecución manual ya se verificaron; no se confunde una ejecución manual con historial programado.
- Completar las interrupciones de la entrevista del 8/11 y el inicio y las interrupciones de la sesión del 9/11. La entrevista ya incluye su duración confirmada y una hora de fin aproximada calculada; el registro de defectos permanece abierto, sin incidencias personales reportadas.
- Realizar la revisión cruzada y resolver la decisión pendiente sobre redistribución de los PDF señalada en [propuesta.md §8](propuesta.md#8-riesgos).
- Confirmar usuarios de GitHub de los tres docentes y sus invitaciones como colaboradores.
- Integrar los cambios de `gabriel/e0` a la rama de entrega y crear el tag `e0` en el commit acordado por el equipo antes del 9 de noviembre de 2026 a las 23:59, según la consigna compartida por Gabriel. La planeación personal hasta el 13 de noviembre no cambia este plazo.
- Registrar el enlace en el formulario oficial y marcar la tarea como entregada. El enlace del formulario no fue proporcionado y estos pasos no se declaran realizados.

## Relatoría de etapa
No aplica en E0 (la primera relatoría es `docs/relatoria-E1.md`).

## Issues de la entrega anterior
No aplica (primera entrega).
