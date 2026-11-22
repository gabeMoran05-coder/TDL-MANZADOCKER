# Entrega E2 · ManzaDocker, Observatorio del Puerto de Manzanillo

**Equipo:** Emilio Rodrigo Ayala Reynoso · Karol Gabriel Morán Aréchiga.<br>
**Etiqueta de esta entrega:** `e2`.<br>
**Tablero público:** pendiente de publicar; no se presenta una ejecución local como URL pública.<br>
**Alcance trabajado:** Ingeniería de Datos de E2 y aterrizaje del producto. Los apartados de Estadística y Calidad señalan lo que falta; esta ficha no los declara terminados.

## Resumen en tres líneas

Se agrega DENUE Colima al pipeline reproducible y al mapa del tablero mediante GeoPandas: los 632 establecimientos logísticos de Manzanillo, con 608 publicados en 28 celdas de ~1 km y un umbral de tres establecimientos por celda. Se publican solo totales, sin puntos individuales ni desgloses por categoría.
El linaje cubre los archivos de Oro indicados en la validación actual, preservando URL, fecha de ingesta, selectores y copias de las entradas por hash; las celdas DENUE se enlazan una a una con su renglón en Bronce.
La dirección comercial se enfoca en transportistas de retiros de importación: escenarios de capacidad y margen con datos propios, sin convertir TEU en ingresos.

## Ingeniería de Datos

| Criterio | Evidencia | Resultado y límite |
|---|---|---|
| Fuente especializada, 45 puntos | [Extractor DENUE](../../extractores/denue.py), [transformación y sjoin](../../src/geoespacial.py), [pipeline E2](../../src/e2.py), [tablero](../../tablero/app.py), [resumen](../../calidad/e2/geoespacial.json) | Descarga oficial real de INEGI, sin token. **Agregado (19/11/2026):** 632 establecimientos SCIAN 484/488/493 del municipio; 608 publicados en 28 celdas de 0.01° y 24 suprimidos en 18 celdas con menos de 3 ([celdas en Oro](../../data/oro/denue_celdas.csv), [GeoJSON](../../data/oro/denue_celdas.geojson)). La versión actual retiró los dos puntos individuales y el desglose por categoría de la captura DENUE. Cuenta establecimientos, no flota, viajes ni demanda. |
| Ética y legalidad, 30 puntos | [Declaración por fuente](../etica-datos.md), [revisión HTTP/robots](../../calidad/e2/fuentes_web.json), [aviso DENUE](../../data/bronce/denue/LICENCIA.md) | Privacidad antes de persistir, condiciones y atribución del INEGI y Banxico, sesgos y restricciones de ASIPONA declaradas. No se acredita una autorización comercial nueva de ASIPONA. |
| Linaje, 15 puntos | [Manifiesto](../../calidad/e2/linaje.json), [validación](../../calidad/e2/validacion_linaje.json), [implementación](../../src/linaje.py) | Cada registro referencia Bronce y su fecha real de ingesta. DENUE: uno a uno, cada celda del agregado (`denue_agregado`). E1: referencias por periodo más conjuntos conservadores de entradas válidas para derivadas globales; para E1 no es linaje exacto por celda. |
| Relatoría, 10 puntos | [Relatoría E2](../relatoria-E2.md) | Seis preguntas, problemas reales, evidencia y uso de IA. No inventa horas de PSP, entrevistas o revisión de compañeros. |

### Reproducción

Desde la raíz del repositorio, con Python y un entorno virtual:

```bash
pip install -r requirements.txt
python -m src.e2
python -m src.linaje validar
python -m src.linaje consultar --archivo data/oro/denue_celdas.csv --registro 1
python -m pytest -q --cov=src --cov-report=term-missing
ruff check src tests extractores/denue.py extractores/revisar_fuentes.py tablero/app.py
streamlit run tablero/app.py
```

`src.e2` usa exclusivamente Bronce versionado y no necesita red ni token. Una captura nueva se solicita con `python -m extractores.run_captura denue` o `python -m extractores.denue --forzar`; la captura de todas las fuentes requiere el token Banxico existente. La fuente especializada usa caché de siete días. Si cambia la serie de entrada del pronóstico, el sello de linaje exige recalcular el notebook E1.

### Diccionario y transformaciones geográficas

| Campo Oro | Significado |
|---|---|
| `celda`, `sur`, `oeste`, `norte`, `este` | Rejilla de estudio de 0.01°, no límites oficiales. |
| `total` | Conteo de establecimientos en la celda, con umbral mínimo de tres. |
| `lat`, `lon` | Centro de la celda en EPSG:4326, no coordenadas individuales. |
| `zona_estudio` | Zona asignada al centro mediante `geopandas.sjoin`; empates resueltos sin duplicar. |
| `registro_bronce`, `archivo_bronce` | Índice desde 1 dentro de `agregado.celdas` y archivo Bronce. |
| `url_origen`, `fecha_captura_utc` | Descarga oficial y fecha original de ingesta. |

Los centros de las celdas se unen a cuatro zonas del rectángulo de estudio. El mapa actual se muestra junto al observatorio, pero no se añade a los registros históricos de TEU como un dato disponible en el pasado. ASIPONA y Banxico mantienen sus contratos E1. El simulador económico usa entradas de sesión y no genera registros Oro ni almacena información de clientes.

### Trazabilidad y evidencia técnica

- Los CSV Bronce de ASIPONA y Banxico que pueden actualizarse se copian con su SHA-256 a `data/bronce/linaje/`; se conservan las fechas de captura originales.
- Las referencias por periodo identifican los registros del mes. Los grupos amplios también conservan las posibles dependencias de escalas, medias móviles, imputación y ajuste de modelos. Son un superconjunto declarado, no una afirmación de que toda fila intervenga en cada cifra.
- CSV: el selector de registro empieza en 1 y excluye cabecera; `linea_csv` añade la cabecera. GeoJSON: índice de feature; Parquet: índice de fila. JSON de parámetros y métricas: claves superiores ordenadas.
- La validación bloquea archivos Oro nuevos sin manifiesto, cambios de hash, pérdida de referencias, fechas inventadas y selectores fuera de rango. Bronce conserva los selectores de las celdas y el hash del ZIP; el derivado sanitizado conserva además el hash de la captura de origen y su fecha original de ingesta.
- El código y las versiones de transformación se registran en el manifiesto. La verificación histórica del 17/11 terminó con 71 pruebas aprobadas, cobertura 95.48 % (umbral 90 %), Ruff sin hallazgos y pip-audit de requirements sin vulnerabilidades conocidas. [Resultado local](../../calidad/e2/validacion_local.json), [cobertura](../../calidad/e2/cobertura.json) y [auditoría de dependencias](../../calidad/e2/auditoria_dependencias.json).
- [Pruebas de privacidad, espacialidad, integridad y negocio](../../tests/test_e2.py) y [prueba funcional de tablero](../../tests/test_tablero.py); [evidencia sintética del tablero](../../calidad/e2/validacion_tablero.json). El dinero del caso de prueba no es facturación ni ahorro de un cliente.

### Integración y avance del 19 de noviembre (Emilio)

- **Integración:** `codex/mapa-costos` (que contiene `codex/e2-fuente-linaje`) se unió con `main` en la rama `emilio/e2`. Los únicos conflictos fueron salidas del pipeline: la bitácora del pipeline (unión de filas) y `resumen.json` (regenerado con `python -m src.e2` desde Bronce).
- **Agregado DENUE:** `extractores/denue.py` (`agregar`), `src/geoespacial.py` (`transformar_agregado`) y `src/linaje.py` (`denue_agregado`). Pruebas en [`tests/test_denue_agregado.py`](../../tests/test_denue_agregado.py).
- **Robustez de captura:** durante la captura, INEGI cortó la conexión (`ChunkedEncodingError`); el extractor ético solo reintentaba ante 429/5xx. Ahora también reintenta ante conexión cortada o tiempo de espera ([prueba](../../tests/test_extractor_base.py)).
- **Documentación:** se corrigieron los acentos dañados (`?` en lugar de letra acentuada) de esta ficha y de la declaración de ética; ambos archivos son UTF-8 válido.
- **Verificación local (19/11/2026):** 87 pruebas aprobadas, cobertura 95.47 % (umbral 90 %), Ruff sin hallazgos, pip-audit sin vulnerabilidades conocidas (incluye `tablero/requirements.txt`) y gitleaks sin secretos en el historial. Pipeline E2 sin red: 10 archivos y 578 registros de Oro con linaje 100 %.
- **Pendiente:** URL pública del tablero (solo puede publicarla el dueño del repositorio en Streamlit Community Cloud) y la decisión con Gabriel sobre mover el tag `e2`.

### Corrección de privacidad posterior a la integración

Se eliminó el desglose por categoría, porque en 11 celdas permitía deducir un conteo suprimido por resta. Se retiraron de la versión actual los snapshots con puntos y categorías y sus productos individuales de Plata/Oro. Se conserva el catálogo comercial de referencia del comparador, separado del agregado. El historial de Git sigue conteniendo las versiones anteriores; esta corrección no revoca datos ya publicados. La comprobación de linaje contrasta también cada fila Oro con su celda y valores en Bronce.

Verificación del 22/11/2026: 91 pruebas aprobadas, cobertura de `src` de 94.65 %, Ruff sin hallazgos y pipeline con 574 registros Oro (8 archivos), todos con linaje. Las 28 filas del CSV agregado se contrastaron con Bronce sin diferencias. Evidencia: [revisión de privacidad](../../calidad/e2/revision_privacidad.json) y [cobertura](../../calidad/e2/cobertura-privacidad.json). Las cifras de verificaciones anteriores se conservan como antecedentes fechados.

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

Revisión del 19/11/2026 en GitHub: no hay issues de los docentes abiertos ni cerrados; solo existen los pull requests #1, #2 y #3 de E1.

## Registro oficial

Enlace de la etiqueta: `https://github.com/gabeMoran05-coder/TDL-MANZADOCKER/tree/e2` una vez publicada. El formulario oficial no fue proporcionado ni se ha enviado desde esta sesión. Antes de registrar el paquete completo de las tres materias, atender los pendientes indicados y comprobar el tablero público.
