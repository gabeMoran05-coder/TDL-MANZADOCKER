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
```
La captura está programada cada día a las 08:00 (hora de Colima) con GitHub Actions (`.github/workflows/captura.yml`) y cada ejecución queda en `calidad/bitacora_captura.csv`.

Primera ejecución manual verificada: [Captura programada, 9 de noviembre de 2026](https://github.com/gabeMoran05-coder/TDL-MANZADOCKER/actions/runs/42679626943), exitosa para ambas fuentes. La programación diaria está activa; la primera ejecución con disparador `schedule` aún está pendiente de observar.

## Estructura
```
docs/          fichas de entrega (E0..E4), relatorías, plan SQA, ética, auditorías
calidad/       registros PSP de defectos y de tiempo (uno por integrante) y bitácora de captura
extractores/   un módulo por fuente (base.py = extractor ético)
pipeline/      bronce -> plata -> oro, puertas de calidad
data/          bronce, plata, oro, cuarentena
laboratorio/   notebooks: series de tiempo, experimento, multivariado
tablero/       Streamlit
tests/         pruebas automáticas
.github/workflows/  captura programada e integración continua
```

## Tablero público
_Pendiente (E1)._

## Uso de IA generativa
Se declara en cada relatoría: herramienta y para qué se usó.
