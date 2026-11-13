# TDL-MANZADOCKER · Observatorio del Puerto de Manzanillo

Observatorio de datos del Puerto de Manzanillo: pronóstico de TEU, calidad de datos y análisis multivariado. Proyecto Integrador **Trusted Data Lab** (TecNM · Instituto Tecnológico de Colima, 2 nov – 4 dic 2026).

## Pregunta central
¿Cuántos contenedores (TEU) moverá el Puerto de Manzanillo el próximo mes y en qué temporadas se concentra la actividad?

## Equipo
| Integrante | Rol |
|---|---|
| Emilio Rodrigo Ayala Reynoso | Data Engineer |
| Karol Gabriel Morán Aréchiga | Data Statistician |

Docentes: Mtro. Armando Román Gallardo Heredia (Ingeniería de Datos) · Mtro. Joel (Análisis Estadístico) · Mtra. Isis (Calidad en los Sistemas de Información).

## Fuentes
| Fuente | Qué aporta | Acceso | Frecuencia |
|---|---|---|---|
| ASIPONA Manzanillo, Estadística Mensual (EM, formato ASPN-MAN-JES-F-05) | TEU mensuales totales, por terminal y por tráfico; toneladas contenerizadas; arribos de buques. Serie ene-2021 → oct-2026 (70 meses) | PDF en puertomanzanillo.com.mx | Mensual; se revisa a diario (GitHub Actions) |
| Banxico SIE, serie SF43718 (tipo de cambio FIX) | Pesos por dólar, diario desde ene-2021 | API REST con token gratuito (`BANXICO_TOKEN`) | Diaria (GitHub Actions) |

## Arquitectura (medallion)
```
extractores/  ->  data/bronce/  ->  pipeline/ (puerta de calidad)  ->  data/plata/  ->  data/oro/
                                              \-> data/cuarentena/ (rechazados con motivo)
```

## Cómo ejecutar
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   ·   Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
python -m extractores.run_captura           # todas las fuentes + bitácora
python -m extractores.run_captura asipona   # solo informes EM del puerto
python -m src.limpieza                     # Bronce -> Plata -> Oro + cuarentena
python -m pytest -q --cov=src              # pruebas de calidad y reproducción
ruff check src tests
```
La captura está programada cada día a las 08:00 (hora de Colima) con GitHub Actions (`.github/workflows/captura.yml`). Tras una captura exitosa ejecuta el pipeline E1; guarda datos, cuarentena y bitácoras. Las ejecuciones quedan en `calidad/bitacora_captura.csv` y `calidad/bitacora_pipeline.csv`.

Primera ejecución manual verificada: [Captura programada, 9 de noviembre de 2026](https://github.com/gabeMoran05-coder/TDL-MANZADOCKER/actions/runs/42679626943), exitosa para ambas fuentes. También existe captura con disparador `schedule` registrada el 9 de noviembre en el commit `0836001`.

## Entrega E1 · Ingeniería de Datos

[Ficha técnica](docs/E1/ENTREGA.md) · [Decisiones de limpieza](docs/E1/limpieza.md) · [Diccionario](docs/E1/diccionario.md) · [Relatoría](docs/relatoria-E1.md)

El pipeline valida contratos estrictos con Pandera, documenta faltantes e imputación causal, marca atípicos, genera Min-Max y Z-Score sin usar los seis meses de prueba, discretiza actividad e integra el FIX diario a frecuencia mensual. Los inválidos conservan contenido y motivo en `data/cuarentena/e1/`; Bronce se mantiene sin cambios. El [resumen automático](calidad/e1/resumen.json) contiene hashes, versiones, conteos y parámetros de la captura procesada.

## Entrega E1 · Análisis Estadístico

[Resumen del pronóstico](docs/E1/pronostico.md) · [Notebook](laboratorio/E1_pronostico.ipynb) · [Métricas y diagnósticos](data/oro/pronostico_metricas.json) · [Figuras](docs/E1/figuras/)

Cuatro modelos (SES, Holt, Holt-Winters y SARIMA) comparados en los últimos 6 meses; gana SES por MAPE (6.48%). Pronóstico de noviembre de 2026: 344,909 TEU, intervalo nominal del 95% de 307,550 a 382,269. Ficha completa de la entrega: [docs/E1/ENTREGA.md](docs/E1/ENTREGA.md).

## Entrega E1 · Calidad en los Sistemas de Información

[Fiabilidad y disponibilidad](docs/E1/fiabilidad.md) · [Seguridad](docs/E1/seguridad.md) · [Requerimientos verificables](docs/E1/requerimientos.md) · [Plan SQA (IEEE 730)](docs/E1/plan-sqa.md)

```bash
python -m src.fiabilidad          # tasa de éxito, MTBF, MTTR y disponibilidad -> calidad/e1/fiabilidad.json
python -m src.respaldo probar     # respaldo de Bronce + restauración + comparación SHA-256
```
La captura diaria recalcula la fiabilidad y sube un respaldo verificado de Bronce como artefacto de Actions (90 días). La CI corre gitleaks y pip-audit en cada push.

## Estructura
```
docs/          fichas de entrega (E0..E4), relatorías, plan SQA, ética, auditorías
calidad/       registros PSP de defectos y de tiempo (uno por integrante) y bitácora de captura
extractores/   un módulo por fuente (base.py = extractor ético)
pipeline/      bronce -> plata -> oro, puertas de calidad
src/           implementación E1: limpieza, preprocesamiento, contratos Pandera, fiabilidad y respaldo
data/          bronce, plata, oro, cuarentena
laboratorio/   notebooks: series de tiempo, experimento, multivariado
tablero/       Streamlit
tests/         pruebas automáticas
.github/workflows/  captura programada e integración continua
```

## Tablero público
**URL:** _pendiente de publicar en Streamlit Community Cloud._

```bash
pip install -r tablero/requirements.txt
streamlit run tablero/app.py
```
Muestra el pronóstico de TEU del siguiente mes con su intervalo del 95%, la serie mensual y el resultado de la puerta de calidad. Lee `data/oro/pronostico_teu.csv`; mientras ese archivo no exista, usa `tablero/datos_ejemplo/pronostico_teu.csv` y muestra un aviso de que es un ejemplo.

## Uso de IA generativa
Se declara en cada relatoría: herramienta y para qué se usó.
