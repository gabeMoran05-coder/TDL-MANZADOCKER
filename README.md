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

## Entrega E2 · Fuente especializada, linaje y dirección comercial

[Ficha E2](docs/E2/ENTREGA.md) · [Ética de datos](docs/etica-datos.md) · [Relatoría](docs/relatoria-E2.md) · [Dirección del producto](docs/E2/enfoque-producto.md)

Se agrega **DENUE Colima de INEGI**, con minimización antes de Bronce, unión espacial en GeoPandas y mapa del contexto logístico en el tablero. La captura publica 608 establecimientos en 28 celdas, sin desglose por categoría ni puntos individuales; otros 24 establecimientos quedan suprimidos por el umbral de tres. Los ocho archivos actuales de Oro y sus 574 registros tienen manifiesto verificable con URL, fecha de ingesta y snapshots de Bronce por SHA-256. El catálogo comercial del comparador se mantiene separado de esta captura.

La dirección comercial propuesta es **planeación de capacidad y margen para transportistas que retiran contenedores de importación**, atendiendo a varias empresas del mismo segmento. El tablero incorpora un escenario con entradas propias; TEU no se convierte automáticamente en viajes, ingresos o ahorros. Precio, datos operativos, venta y piloto siguen por validar. Los entregables E2 de Estadística y Calidad completos se declaran pendientes en la ficha.

```bash
pip install -r requirements.txt
python -m src.e2                         # E1 + DENUE + linaje, sin red
python -m src.linaje validar
python -m extractores.run_captura denue  # nueva captura si venció caché de siete días
streamlit run tablero/app.py
```

## Tablero público

### Comparador de trayectos y costos

El mapa incorpora cinco ubicaciones públicas del DENUE, recorridos viales de referencia y costos por servicio con entradas propias. Permite copiar el costo sin esperas al escenario mensual. También admite kilómetros validados por la empresa. [Alcance, procedencia y límites](docs/E2/mapa-costos.md).

Las consultas usan un perfil de automóvil y no certifican accesos ni restricciones para tractocamiones. Las ubicaciones no representan clientes o convenios del equipo.

**URL pública:** https://tdl-manzadocker.streamlit.app/ (comprobada el 22/11/2026 sin iniciar sesión: carga el pronóstico, el mapa con las 28 celdas del agregado DENUE y el simulador).

```bash
pip install -r tablero/requirements.txt
streamlit run tablero/app.py
```
Muestra el pronóstico de TEU del siguiente mes con su intervalo del 95%, la serie mensual y el resultado de la puerta de calidad. Lee `data/oro/pronostico_teu.csv`; mientras ese archivo no exista, usa `tablero/datos_ejemplo/pronostico_teu.csv` y muestra un aviso de que es un ejemplo.

## Uso de IA generativa
Se declara en cada relatoría: herramienta y para qué se usó.
