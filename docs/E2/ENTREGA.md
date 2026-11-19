# Entrega E2 · ManzaDocker, Observatorio del Puerto de Manzanillo

**Equipo:** Emilio Rodrigo Ayala Reynoso · Karol Gabriel Morán Aréchiga.<br>
**Etiqueta de esta entrega:** `e2`.<br>
**Tablero público:** pendiente de publicar; no se presenta una ejecución local como URL pública.<br>
**Alcance trabajado:** Ingeniería de Datos de E2 y aterrizaje del producto. Los apartados de Estadística y Calidad señalan lo que falta; esta ficha no los declara terminados.

## Resumen en tres líneas

Se agrega DENUE Colima, minimizado antes de Bronce, al pipeline reproducible y al mapa del tablero mediante GeoPandas.
El linaje cubre los ocho archivos actuales de Oro y sus 522 registros, preservando URL, fecha de ingesta, selectores y copias de las entradas por hash.
La dirección comercial se enfoca en transportistas de retiros de importación: escenarios de capacidad y margen con datos propios, sin convertir TEU en ingresos.

## Ingeniería de Datos

| Criterio | Evidencia | Resultado y límite |
|---|---|---|
| Fuente especializada, 45 puntos | [Extractor DENUE](../../extractores/denue.py), [transformación y sjoin](../../src/geoespacial.py), [pipeline E2](../../src/e2.py), [tablero](../../tablero/app.py), [resumen](../../calidad/e2/geoespacial.json) | Descarga oficial real de INEGI, sin token. Dos establecimientos seleccionados por actividad, municipio y forma societaria explícita, ambos en el área. Es una muestra conservadora pequeña, no un censo ni un mercado estimado. |
| Ética y legalidad, 30 puntos | [Declaración por fuente](../etica-datos.md), [revisión HTTP/robots](../../calidad/e2/fuentes_web.json), [aviso DENUE](../../data/bronce/denue/LICENCIA.md) | Privacidad antes de persistir, condiciones y atribución del INEGI y Banxico, sesgos y restricciones de ASIPONA declaradas. No se acredita una autorización comercial nueva de ASIPONA. |
| Linaje, 15 puntos | [Manifiesto](../../calidad/e2/linaje.json), [validación](../../calidad/e2/validacion_linaje.json), [implementación](../../src/linaje.py) | Cada registro referencia Bronce y su fecha real de ingesta. DENUE: uno a uno; E1: referencias por periodo más conjuntos conservadores de entradas válidas para derivadas globales. No es linaje exacto por celda. |
| Relatoría, 10 puntos | [Relatoría E2](../relatoria-E2.md) | Seis preguntas, problemas reales, evidencia y uso de IA. No inventa horas de PSP, entrevistas o revisión de compañeros. |

### Reproducción

Desde la raíz del repositorio, con Python y un entorno virtual:

```bash
pip install -r requirements.txt
python -m src.e2
python -m src.linaje validar
python -m src.linaje consultar --archivo data/oro/contexto_geografico.csv --registro 1
python -m pytest -q --cov=src --cov-report=term-missing
ruff check src tests extractores/denue.py extractores/revisar_fuentes.py tablero/app.py
streamlit run tablero/app.py
```

`src.e2` usa exclusivamente Bronce versionado y no necesita red ni token. Una captura nueva se solicita con `python -m extractores.run_captura denue` o `python -m extractores.denue --forzar`; la captura de todas las fuentes requiere el token Banxico existente. La fuente especializada usa caché de siete días. Si cambia la serie de entrada del pronóstico, el sello de linaje exige recalcular el notebook E1.

### Diccionario y transformaciones geográficas

| Campo Oro | Significado |
|---|---|
| `id_denue` | Identificador público del establecimiento seleccionado; no identifica a un operador o contacto. |
| `codigo_actividad`, `categoria` | Código SCIAN original y categoría derivada de su subsector 484, 488 o 493. No certifica que maneje contenedores. |
| `lat`, `lon` | Ubicación del establecimiento, en EPSG:4326; no es un acceso vial. |
| `zona` | Celda de estudio asignada con `geopandas.sjoin`, `intersects`; los empates en bordes se resuelven sin duplicar. No es colonia ni zona oficial. |
| `puerto` | Contexto del observatorio: Manzanillo. No implica que el establecimiento tenga contrato con el puerto. |
| `registro_bronce`, `archivo_bronce` | Posición y archivo de la proyección minimizada de Bronce. GeoJSON conserva el selector en propiedades; el manifiesto conserva el archivo. |
| `url_origen`, `fecha_captura_utc` | Descarga oficial y fecha de ingesta. La edición del directorio y el registro original del CSV se preservan en Bronce. |

Las coordenadas se unen a cuatro celdas del rectángulo de estudio. El mapa actual se muestra junto al observatorio, pero no se añade a los registros históricos de TEU como un dato disponible en el pasado. ASIPONA y Banxico mantienen sus contratos E1. El simulador económico usa entradas de sesión y no genera registros Oro ni almacena información de clientes.

### Trazabilidad y evidencia técnica

- Los CSV Bronce de ASIPONA y Banxico que pueden actualizarse se copian con su SHA-256 a `data/bronce/linaje/`; se conservan las fechas de captura originales.
- Las referencias por periodo identifican los registros del mes. Los grupos amplios también conservan las posibles dependencias de escalas, medias móviles, imputación y ajuste de modelos. Son un superconjunto declarado, no una afirmación de que toda fila intervenga en cada cifra.
- CSV: el selector de registro empieza en 1 y excluye cabecera; `linea_csv` añade la cabecera. GeoJSON: índice de feature; Parquet: índice de fila. JSON de parámetros y métricas: claves superiores ordenadas.
- La validación bloquea archivos Oro nuevos sin manifiesto, cambios de hash, pérdida de referencias, fechas inventadas y selectores fuera de rango. Bronce minimizado DENUE conserva la posición en el CSV de origen y el hash del ZIP, que no se guarda por privacidad.
- El código y las versiones de transformación se registran en el manifiesto. La verificación local terminó con 71 pruebas aprobadas, cobertura 95.48 % (umbral 90 %), Ruff sin hallazgos y pip-audit de requirements sin vulnerabilidades conocidas. [Resultado local](../../calidad/e2/validacion_local.json), [cobertura](../../calidad/e2/cobertura.json) y [auditoría de dependencias](../../calidad/e2/auditoria_dependencias.json).
- [Pruebas de privacidad, espacialidad, integridad y negocio](../../tests/test_e2.py) y [prueba funcional de tablero](../../tests/test_tablero.py); [evidencia sintética del tablero](../../calidad/e2/validacion_tablero.json). El dinero del caso de prueba no es facturación ni ahorro de un cliente.

## Análisis Estadístico

| Criterio | Evidencia E2 | Estado |
|---|---|---|
| Factorial 2³ aleatorizado con réplicas | La ruta de ingeniería ya está planteada en E0; falta ejecutar y analizar el experimento E2. | Pendiente. El simulador económico no sustituye un experimento. |
| ANOVA de dos vías con interacción | No generado en este cambio. | Pendiente. |
| Completo frente a fraccionado, alias y ahorro | No generado en este cambio. | Pendiente. |
| Supuestos y corrida de confirmación | No generado en este cambio. | Pendiente. |

## Calidad en los Sistemas de Información

| Criterio | Evidencia E2 | Estado |
|---|---|---|
| Evaluación ISO/IEC 25010 | Hay pruebas del sistema, pero falta la evaluación medida por característica. | Pendiente. |
| Evaluación ISO/IEC 25012 | Hay puertas, trazabilidad y conteos; falta la matriz completa de características sobre Oro. | Pendiente. |
| Antecedentes normativos | No generado en este cambio. | Pendiente. |
| Auditoría cruzada | Requiere al equipo asignado y su revisión real. | Pendiente; no se inventa auditoría. |

## Dirección comercial

### Ampliación posterior al tag publicado

La rama `codex/mapa-costos` agrega un catálogo de cinco organizaciones públicas del DENUE, recorridos viales de referencia OSRM y comparación de costos que puede alimentar el escenario mensual. [Comportamiento, fuentes y límites](mapa-costos.md). La ampliación pasó 80 pruebas locales con 95.27 % de cobertura; la comprobación vial real OCUPA Puerto–Terminal de Servicios HAZESA devolvió 4.693 km con perfil de automóvil. Es una referencia de planeación, no navegación validada para tractocamiones. El tag `e2` conserva su versión anterior; la integración y publicación pública siguen el proceso de revisión del equipo.

[Decisión de producto, cliente, dinero y piloto](enfoque-producto.md). Un segmento inicial de transportistas puede incluir varias empresas del mismo tipo. La propuesta de suscripción, el acceso a datos operativos, el precio y los ahorros quedan por validar con un comprador real.

## Issues de la entrega anterior

No se realizó una revisión remota verificable de issues en esta sesión; no se afirma que estén todos atendidos. La ficha E1 y el historial conservan el estado anterior. Antes de la entrega oficial, revisar las observaciones docentes y enlazar aquí los commits que las atiendan.

## Registro oficial

Enlace de la etiqueta: `https://github.com/gabeMoran05-coder/TDL-MANZADOCKER/tree/e2` una vez publicada. El formulario oficial no fue proporcionado ni se ha enviado desde esta sesión. Antes de registrar el paquete completo de las tres materias, atender los pendientes indicados y comprobar el tablero público.
