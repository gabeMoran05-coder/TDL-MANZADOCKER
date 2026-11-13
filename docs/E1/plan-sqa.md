# Plan de Aseguramiento de la Calidad del Software (SQA)
## Observatorio del Puerto de Manzanillo · TDL-MANZADOCKER

**Estructura:** IEEE 730 (Software Quality Assurance Processes), adaptada a un equipo de dos personas
**Versión:** 1.0 · 12 de noviembre de 2026 · **Elaboró:** Emilio Rodrigo Ayala Reynoso · **Revisa:** Karol Gabriel Morán Aréchiga
**Vigencia:** de E1 (13 de noviembre de 2026) al reporte final (4 de diciembre de 2026). Se actualiza en cada entrega si cambia algo.

---

## 1. Propósito y alcance

**Propósito.** Dar confianza, con evidencia, de que el observatorio y sus datos cumplen lo que prometen: cifras de TEU fieles a la fuente oficial, un pronóstico elegido por su error y una captura que funciona sola. El plan define quién revisa qué, cuándo, con qué herramientas y qué pasa cuando algo falla.

**Alcance.** Cubre todo lo que vive en el repositorio:
- Código: `extractores/`, `src/`, `tablero/`, `tests/`, `.github/workflows/`.
- Datos: `data/bronce`, `plata`, `oro` y `cuarentena`.
- Notebooks de `laboratorio/`.
- Documentos de `docs/`.

No cubre la disponibilidad de los sitios de las fuentes (ASIPONA, Banxico), que no controlamos; sí cubre cómo reaccionamos cuando fallan.

**Aseguramiento vs. control de calidad.** En este plan:
- **Control de calidad (QC)** es revisar el producto: pruebas, puerta Pandera, revisión de un pull request.
- **Aseguramiento (SQA)** es asegurar que el proceso que produce el producto se sigue: que toda modificación pase por pull request, que los registros PSP estén al día y que las métricas se midan.

QC encuentra defectos; SQA evita que se repitan.

## 2. Documentos de referencia

| Documento | Uso |
|---|---|
| IEEE 730 | Estructura de este plan |
| ISO/IEC 25010 y 25012 | Evaluación del producto y de los datos (E2) |
| PSP (Personal Software Process) | Registros individuales de tiempo y defectos |
| [Propuesta E0](../E0/propuesta.md) | Pregunta central y objetivos de calidad OC1–OC3 |
| [Requerimientos](requerimientos.md) | Lo que se verifica |
| [Fiabilidad](fiabilidad.md) y [Seguridad](seguridad.md) | Evidencia de E1 |

## 3. Organización, roles y responsabilidades

| Rol | Quién | Responsabilidades de calidad |
|---|---|---|
| Data Engineer | Emilio | Calidad de extractores, pipeline, puerta de calidad y workflows. Mantiene este plan. |
| Data Statistician | Gabriel | Calidad de notebooks y pronósticos: supuestos verificados (puerta 3) y resultados reproducibles. |
| **Quality Lead de la entrega** | Rota: **E1 Emilio**, E2 Gabriel, E3 Emilio, E4 Gabriel | Revisa el trabajo del otro con la lista de comprobación (§7), confirma que la ficha `ENTREGA.md` enlaza evidencia real y da el visto bueno antes del tag. |
| Ambos | — | Llevan su registro PSP, responden por la parte del otro en la defensa y atienden los issues de los docentes. |

**Independencia del revisor.** Nadie aprueba su propio pull request: lo revisa el otro integrante. Con dos personas no hay un área de calidad separada; la independencia se logra rotando el rol de Quality Lead y exigiendo que la revisión deje rastro (comentarios o aprobación en el PR).

## 4. Estándares, prácticas y métricas

**Estándares que se siguen:**
- Código Python: `ruff` con la configuración de `pyproject.toml` (longitud 100; reglas E4, E7, E9, F, I).
- Commits en español, con el prefijo de la entrega (`E1: …`).
- Datos: contratos Pandera en `src/calidad.py`; nada se borra en silencio.
- Scraping ético y cero datos personales (reglas del proyecto).
- Documentos: plantillas del kit (ficha de entrega y relatoría).

**Métricas y metas:**

| Métrica | Meta | Fuente de la medición | Frecuencia |
|---|---|---|---|
| OC1 · Disponibilidad de la captura programada | ≥ 95% | `calidad/e1/fiabilidad.json` | Cada captura (automático) |
| MTTR de una falla de captura | ≤ 24 h | `calidad/e1/fiabilidad.json` | Cada captura |
| OC2 · Exactitud de extracción (suma de meses vs. acumulado) | 100% con diferencia ≤ 2 | `data/bronce/asipona/em_mensual.csv` | Cada captura |
| OC3 · Completitud de la serie de TEU | 100% de meses publicados | Puerta de calidad / Oro | Cada captura |
| Cobertura de pruebas de `src/` | ≥ 90% (Sello TDL: ≥ 60%) | CI (`pytest --cov`) | Cada push |
| Secretos en el historial | 0 | gitleaks en CI | Cada push |
| Vulnerabilidades conocidas en dependencias | 0 | pip-audit en CI | Cada push |
| Registros rechazados por la puerta | Se reportan; no hay meta, se explica cada motivo | `calidad/e1/resumen.json` | Cada captura |
| Defectos por fase (PSP) | Se reportan para la retrospectiva de E3 | `calidad/defectos-*.csv` | Cada entrega |

## 5. Revisiones y auditorías

| Revisión | Cuándo | Quién | Evidencia |
|---|---|---|---|
| Revisión de pull request con lista de comprobación (§7) | Antes de unir cualquier rama a `main` | El otro integrante | Aprobación y comentarios en el PR |
| Revisión de entrega | Antes de crear el tag de cada entrega | Quality Lead | Fila "Revisión cruzada" en `docs/E<n>/ENTREGA.md` |
| Panel de medio término | 17 y 18 de noviembre | Los tres docentes | Issues con etiqueta de materia |
| Auditoría cruzada ISO/IEC 25010 y 25012 | 19 al 23 de noviembre | Otro equipo | Reporte de hallazgos (E2) y su cierre (E3) |
| Revisión de issues de docentes | Antes de cada entrega | Ambos | Cada issue cerrado con el commit que lo atiende |

## 6. Pruebas

| Nivel | Qué se prueba | Dónde |
|---|---|---|
| Unitarias | Puerta de calidad, imputación, atípicos, escalas, fiabilidad, respaldo | `tests/test_e1.py`, `tests/test_fiabilidad.py`, `tests/test_respaldo.py` |
| Integración | El pipeline real de Bronce a Oro es reproducible y no modifica Bronce | `test_pipeline_real_reproducible_y_conserva_bronce` |
| De contrato | El CSV del pronóstico tiene las columnas e intervalos correctos | Prueba de Gabriel en `tests/` (E1) |
| Inyección de fallas | Registros corruptos, duplicados, columnas de más o de menos, fuente ausente, respaldo alterado | `test_e1.py`, `test_respaldo.py` |
| De interfaz | El tablero carga en escritorio y móvil sin errores de consola | Playwright, con capturas en el PR del tablero |

**Puertas de calidad del observatorio:**
1. **Validación de datos** (Bronce → Plata): Pandera; lo inválido va a cuarentena con motivo.
2. **Integración continua** (cada push y PR): gitleaks, pip-audit, ruff, pytest con cobertura ≥ 90% y generación de Plata y Oro. Un cambio que la rompe no entra a `main`.
3. **Supuestos estadísticos** (antes de publicar un hallazgo): estacionariedad y residuos del pronóstico; si un supuesto falla, se publica con un método que no dependa de él o no se publica.

## 7. Lista de comprobación para revisar un pull request

- [ ] La CI está en verde (gitleaks, pip-audit, ruff, pytest ≥ 90%).
- [ ] Ningún archivo nuevo contiene tokens, `.env`, nombres, teléfonos ni correos de personas.
- [ ] Los cambios a `data/bronce/` los hizo el bot o un extractor, no una edición a mano.
- [ ] Toda cifra nueva en `docs/` sale de un archivo o una ejecución enlazada.
- [ ] Si cambia un contrato de datos (columnas o tipos), se actualizó el diccionario y las pruebas.
- [ ] El código nuevo en `src/` tiene pruebas; la cobertura no bajó.
- [ ] El autor registró su tiempo y sus defectos de este trabajo en su PSP.
- [ ] El revisor puede explicar el cambio (requisito de la defensa individual).

## 8. Reporte de problemas y acciones correctivas

| Tipo de problema | Dónde se registra | Acción |
|---|---|---|
| Defecto que uno mismo encuentra en su trabajo | `calidad/defectos-<nombre>.csv` (tipos PSP, fase en que se introdujo y en que se eliminó, minutos, defecto de origen) | Se corrige y se cita su número en la relatoría si fue costoso |
| Falla de captura o del pipeline | Fila en la bitácora (automática) y workflow en rojo | Si dura más de 24 h: issue con etiqueta `calidad` |
| Observación de un docente | Issue con etiqueta `ing-datos`, `estadistica` o `calidad` | Se cierra con el commit que lo atiende, antes de la siguiente entrega |
| Hallazgo de la auditoría cruzada | Reporte del equipo auditor (E2) | Acción correctiva, evidencia y estado en E3; ningún crítico abierto |
| Registro de datos inválido | `data/cuarentena/` (automático) | Se revisa el motivo; si es un error de la regla, se corrige con un PR y una prueba |

## 9. Herramientas

| Herramienta | Uso |
|---|---|
| GitHub y GitHub Actions | Repositorio, pull requests, issues, CI y captura programada |
| pytest y pytest-cov | Pruebas y cobertura |
| ruff | Estilo y errores comunes en Python |
| Pandera | Contratos de datos y puerta de calidad |
| gitleaks / pip-audit | Secretos y vulnerabilidades |
| `src/fiabilidad.py` / `src/respaldo.py` | Métricas de fiabilidad; respaldo verificable |
| Playwright | Prueba visual del tablero |
| Asistentes de IA (Claude Code, Codex) | Apoyo en código y documentación; se declaran en cada relatoría y todo se ejecuta y revisa antes de subirlo |

## 10. Control de versiones y configuración

- **`main`** es la rama estable; de ahí sale cada tag de entrega (`e0`, `e1`, …).
- **Ramas de trabajo:** `<nombre>/e<n>` (por ejemplo `emilio/e1`, `gabriel/e1`). Se unen a `main` solo por pull request revisado por el otro integrante.
- **Prohibido** `git push --force` sobre `main` y reescribir su historial. En la propia rama, después de un rebase, solo se permite `--force-with-lease`.
- **Antes de subir:** `git pull --rebase`, porque el bot de captura hace commits diarios en `main`.
- **Tags:** el Quality Lead crea el tag de la entrega sobre el commit revisado de `main`. Si hay que moverlo antes de la fecha límite, se acuerda entre los dos y se anota en la relatoría.
- **Secretos:** solo en GitHub Secrets o en `.env` local (ignorado).
- **Pendiente (S3 de seguridad):** activar la protección de `main` en GitHub para exigir PR y CI en verde.

## 11. Riesgos

| # | Riesgo | Prob. | Impacto | Mitigación |
|---|---|---|---|---|
| R1 | Los términos de gob.mx limitan redistribuir los PDF de ASIPONA y el repositorio es público | Media | Alto | Decisión pendiente del equipo; opción: versionar solo cifras, URL y SHA-256 |
| R2 | ASIPONA cambia el formato del PDF o la URL | Media | Alto | La validación contra el acumulado y la puerta Pandera lo detectan; catálogo fijo para el histórico |
| R3 | GitHub retrasa o salta el cron (ya se observaron retrasos de 6.7 a 9.3 h) | Alta | Bajo | Ejecución manual con `workflow_dispatch`; la disponibilidad se mide por día |
| R4 | Pocos días de bitácora para afirmar la disponibilidad con confianza | Alta | Medio | Reportar la cota estadística; acumular hasta E3 (Sello TDL: 14 días) |
| R5 | Un integrante no puede explicar la parte del otro en la defensa | Media | Alto | La revisión de PR obliga a leer y entender el cambio; repaso antes del panel |
| R6 | Fuga del token de Banxico | Baja | Bajo | gitleaks en CI; rotación al cierre del proyecto |
| R7 | Dependencias con versiones abiertas cambian el resultado | Baja | Medio | Prueba de reproducibilidad; congelar versiones para el dataset final |
