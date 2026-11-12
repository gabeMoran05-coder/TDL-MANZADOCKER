# Seguridad del sistema de información (E1 · Calidad)

**Responsable:** Emilio Rodrigo Ayala Reynoso · **Revisión:** 12 de noviembre de 2026
**Herramientas:** gitleaks 8.30.1 · pip-audit · [`src/respaldo.py`](../../src/respaldo.py) · workflows [`ci.yml`](../../.github/workflows/ci.yml) y [`captura.yml`](../../.github/workflows/captura.yml)

La revisión se organiza con los tres pilares de la seguridad de la información: **confidencialidad** (que el token y los secretos no se expongan), **integridad** (que los datos no cambien sin que lo notemos) y **disponibilidad** (que haya respaldo y se pueda restaurar).

## 1. Resumen

| Revisión | Resultado del 12/11/2026 | Estado |
|---|---|---|
| Secretos en todo el historial de git (gitleaks) | **0 hallazgos** en 19 commits de todas las ramas | Cerrado; se repite en cada push (CI) |
| Vulnerabilidades en dependencias (pip-audit) | **0 vulnerabilidades conocidas** en `requirements.txt` | Cerrado; se repite en cada push (CI) |
| Permisos mínimos de workflows y token | `ci.yml`: solo lectura · `captura.yml`: escritura de contenido (necesaria para el commit del bot) · token de Banxico de solo consulta | Cerrado |
| Respaldo de Bronce probado | 17 archivos (2.8 MB) respaldados, restaurados y comparados por SHA-256: **0 diferencias** | Cerrado; se repite en cada captura |

## 2. Confidencialidad

**Búsqueda de secretos.** Se ejecutó `gitleaks git . --log-opts="--all" --redact` sobre el historial completo: 19 commits de `main`, `emilio/e1`, `gabriel/e0` y `gabriel/e1`, unos 1.8 MB revisados. Resultado: *no leaks found*.

Un segundo escaneo de la carpeta de trabajo (`gitleaks dir .`) encontró **1 hallazgo**: el token de Banxico en el archivo local `.env`. Es esperado y no es una fuga:
- `.env` está excluido por `.gitignore` (regla `.env*`, comprobado con `git check-ignore -v .env`).
- `git log --all -- .env` no devuelve ningún commit: nunca se ha subido.
- En GitHub, el token vive solo como secret `BANXICO_TOKEN` y únicamente el paso "Capturar fuentes" lo recibe como variable de entorno.
- El extractor lo envía en el encabezado `Bmx-Token`, no en la URL. Por eso no aparece ni en la bitácora ni en los JSON crudos de `data/bronce/banxico/json/`.

**Desde E1, gitleaks corre en cada push y pull request** (paso "Buscar secretos" de `ci.yml`, versión fija 8.30.1). Si alguien sube un secreto, la CI se pone en rojo.

**Riesgo residual aceptado:** el token se mostró en capturas de pantalla y se compartió por mensaje privado entre los integrantes. Es un token gratuito, de solo consulta y sin datos personales. Acción: **generar uno nuevo al cerrar el proyecto** (o antes, si aparece en un lugar público) y actualizar el secret.

## 3. Integridad

| Control | Dónde |
|---|---|
| SHA-256 de cada PDF descargado, con URL y fecha de captura | `data/bronce/asipona/capturas.csv` |
| Hash de las entradas de Bronce y del código en cada ejecución del pipeline | `calidad/e1/resumen.json` |
| Puerta de calidad Pandera: un dato que no cumple el contrato va a cuarentena con su motivo | `src/calidad.py`, `data/cuarentena/e1/` |
| Pruebas automáticas (ruff + pytest, cobertura mínima 90%) en cada push | `ci.yml` |
| Historial de git como registro de cada cambio y su autor | GitHub |

## 4. Disponibilidad: respaldo de la capa Bronce

Bronce es la única capa que no se puede regenerar: si un PDF se borra del sitio de ASIPONA, solo existe nuestra copia. Plata y Oro se reconstruyen desde Bronce con `python -m src.limpieza`.

**Cómo funciona** ([`src/respaldo.py`](../../src/respaldo.py)):
1. `crear`: empaqueta `data/bronce/` en un ZIP con un `MANIFIESTO.json` que guarda la ruta, los bytes y el SHA-256 de cada archivo.
2. `verificar`: extrae el ZIP en una carpeta temporal, recalcula cada SHA-256 y lo compara contra el manifiesto y contra los archivos vivos de Bronce.
3. `probar`: hace el ciclo completo y guarda la evidencia en [`calidad/e1/respaldo_prueba.json`](../../calidad/e1/respaldo_prueba.json).

**Prueba de restauración (12/11/2026, 23:14 UTC):** 17 archivos, 2,803,570 bytes (ZIP de 2,269,434 bytes), **0 errores**.

**Dónde vive el respaldo:**
- Copia 1: el propio historial de git en GitHub.
- Copia 2: desde E1, cada captura diaria crea el ZIP, lo verifica y lo sube como **artefacto de GitHub Actions** (`respaldo-bronce-<id>`), que se conserva 90 días. No se versiona dentro del repo para no duplicar los datos.

Las pruebas (`tests/test_respaldo.py`) comprueban también los casos malos: un archivo de Bronce modificado después del respaldo, un archivo borrado, un ZIP con un archivo alterado o faltante, y Bronce vacío. En todos, la verificación falla.

**Cómo restaurar a mano:** descargar el artefacto desde la pestaña Actions, verificarlo con `python -m src.respaldo verificar respaldo_bronce.zip` y descomprimirlo sobre la raíz del repositorio.

## 5. Permisos mínimos

| Elemento | Permiso | Por qué |
|---|---|---|
| `GITHUB_TOKEN` en `ci.yml` | `contents: read` | Solo lee código y corre pruebas |
| `GITHUB_TOKEN` en `captura.yml` | `contents: write` | El bot necesita hacer commit de `data/` y `calidad/`; no tiene permisos sobre issues, PR ni configuración |
| Secret `BANXICO_TOKEN` | Solo en el paso "Capturar fuentes" | Los demás pasos no lo reciben |
| Token de Banxico | Solo consulta de series públicas | No permite escribir ni acceder a datos personales |
| Colaboradores | Los dos integrantes y los tres docentes | Requisito del proyecto |

## 6. Hallazgos abiertos

| # | Hallazgo | Severidad | Acción propuesta | Responsable |
|---|---|---|---|---|
| S1 | Las acciones de GitHub se fijan por etiqueta (`@v4`, `@v5`), no por hash de commit; una etiqueta comprometida podría cambiar el código que corre | Menor | Fijar por SHA en E2 | Emilio |
| S2 | `requirements.txt` usa rangos (`>=`), así que la instalación puede cambiar entre corridas | Menor | Generar un archivo de versiones exactas para el dataset final (E3) | Emilio |
| S3 | No consta que `main` tenga una regla de protección (solo el dueño puede verlo y activarlo) | Mayor | Activar en Settings → Branches: exigir pull request revisado y CI en verde antes de unir a `main` | Gabriel (dueño del repo) |
| S4 | Repositorio público con los PDF de ASIPONA; los términos de gob.mx limitan la redistribución | Mayor (legal) | Pendiente de decisión del equipo; ver riesgo 1 de la propuesta E0 | Equipo |
| S5 | El token de Banxico se compartió en capturas y mensajes | Menor | Rotarlo al cierre del proyecto | Emilio |

## 7. Cómo reproducirlo

```bash
gitleaks git . --log-opts="--all" --redact     # secretos en todo el historial
pip-audit -r requirements.txt                   # vulnerabilidades de dependencias
python -m src.respaldo probar                   # respaldo + restauración + comparación
python -m pytest -q tests/test_respaldo.py
```
