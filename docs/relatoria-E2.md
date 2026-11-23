# Relatoría E2 · Fuente especializada y dirección comercial de ManzaDocker

Equipo: Emilio Rodrigo Ayala Reynoso y Karol Gabriel Morán Aréchiga. Avance: 17 de noviembre de 2026 (Gabriel) y 19 de noviembre de 2026 (Emilio). Alcance: Ingeniería de Datos y aterrizaje del producto; Estadística y Calidad completas siguen pendientes.

## 1. ¿Qué nos propusimos?

Integrar una fuente especializada real al pipeline y al tablero, conservar trazabilidad verificable para todos los registros actuales de Oro y explicar condiciones de uso y privacidad por fuente. Después de la retroalimentación del profesor, definir un segmento comprador y una decisión relacionada con dinero que el producto pueda apoyar sin exagerar los datos disponibles.

## 2. ¿Qué hicimos?

| Fecha | Actividad y evidencia | Responsable y tiempo |
|---|---|---|
| 17/11/2026 | Revisión del PDF del proyecto y de la base E1, actualizada desde `origin/main`. Trabajo aislado en `codex/e2-fuente-linaje`. | Implementación asistida por Codex a solicitud de Gabriel. Tiempo humano no registrado; no se inventa PSP. |
| 17/11/2026 | Evaluación de OSM: robots bloquea la instancia principal y la alternativa no responde. Sustitución por descarga oficial DENUE Colima. | Asistencia de Codex; revisión humana de esta decisión pendiente. |
| 17/11/2026 | Proyección mínima en memoria, unión espacial GeoPandas, mapa y registros de calidad. La descarga incluye 42,073 filas; el filtro conservador produce dos establecimientos. | Evidencia en Bronce y `calidad/e2/geoespacial.json`; sin atribuir ejecución manual a Emilio. |
| 17/11/2026 | Linaje por registro para ocho productos Oro, con 522 registros; snapshots por hash y verificación de integridad, fechas y selectores. | Código, manifiesto, informe y pruebas en el repositorio. |
| 17/11/2026 | Incorporación de la retroalimentación del profesor: transportistas de retiros de importación, escenarios de capacidad y margen, y plan de piloto comercial. | Criterio propuesto por Codex y documentado para decisión del equipo; no representa una venta validada. |
| 17/11/2026 | Pruebas automáticas del pipeline y del tablero; actualización de dependencias de visualización en entorno aislado. | Salidas de pruebas y evidencia sintética; tiempo humano no registrado. |
| 19/11/2026 | Integración de `codex/mapa-costos` con `main` en la rama `emilio/e2`; conflictos solo en salidas del pipeline. Corrección de acentos dañados en ética y ficha. | Emilio, con Claude Code. Tiempo en `calidad/tiempo-emilio.csv`. |
| 19/11/2026 | Agregado DENUE por celda con k-anonimato: de 2 a 632 establecimientos representados (608 en 28 celdas, 24 suprimidos). Linaje por celda, capa en el mapa y reintento del extractor ante conexión cortada. 87 pruebas, cobertura 95.47 %. | Emilio, con Claude Code. Commits en `emilio/e2`. |

## 3. ¿Qué decidimos y por qué?

1. **DENUE en lugar de insistir con Overpass.** La ruta bloqueada no se usa y los reintentos de la alternativa se acotan. INEGI ofrece descarga accesible y condiciones explícitas de reutilización. Se descarta mantener una fuente sin captura real.
2. **Privacidad antes de persistencia.** No guardar el ZIP completo ni nombres/contactos. La selección exige forma societaria explícita y minimiza campos. Esto reduce a dos establecimientos y produce sesgo; no usamos ese conteo como tamaño del mercado ni lo ocultamos para mejorar una métrica.
3. **Agregar en lugar de puntos (19/11, Emilio).** El filtro societario dejaba 2 de 632 establecimientos porque casi ninguna razón social en DENUE incluye la forma societaria escrita. Se cuentan todos por celda de ~1 km antes de guardar, con k = 3. *(Corrección del 22/11: la versión de Emilio también guardaba el desglose por categoría; ese diseño fue un error, ver §4.)* *Descartado:* relajar el filtro y guardar puntos, que habría expuesto ubicaciones de personas físicas; y celdas más grandes, que borran la diferencia entre el recinto y la periferia.
4. **Un segmento, una operación principal.** Transportistas que retiran contenedores de importación, con capacidad y margen como pregunta económica. Se descarta construir a la vez herramientas de terminal, ferrocarril y graneles. TEU se conserva como contexto, no como conversión automática a viajes o dinero.

## 4. ¿Qué salió mal y cómo lo corregimos?

El [registro de incidencias E2](../calidad/e2/incidencias.csv) identifica problemas de acceso de fuente (E2-01), codificación del CSV (E2-02), normalización de sufijos societarios (E2-03), validación repetida de dependencias (E2-04) e incompatibilidad de visualización del entorno (E2-05). Las correcciones están en código y tienen pruebas de admisión, privacidad, integridad o ejecución. No se asignan minutos de corrección que nadie midió.

El 19/11, INEGI cortó la conexión a media descarga (`ChunkedEncodingError`) y el extractor ético no reintentaba ese caso; se corrigió con prueba (defecto 5 de Emilio). Al programar el agregado, una condición con `not` mal agrupado dejaba pasar celdas con límites invertidos (defecto 6) y la primera corrección del reintento no atrapaba `ChunkedEncodingError` (defecto 7, causado por el 5); ambos se encontraron en revisión antes de ejecutar.

**Defecto de privacidad en mi agregado (defecto 8 de Emilio, encontrado por Gabriel el 22/11).** Yo suprimía las categorías con 1 o 2 establecimientos pero publicaba también el total de la celda, así que el valor suprimido se despejaba restando; Gabriel comprobó que ocurría en 11 celdas. Además, la captura inicial conservaba dos puntos individuales con identificador y coordenadas, por una regla de selección anterior. Se corrigió quitando el desglose y los puntos de la versión actual y comprobando cada celda contra Bronce. Una prueba mía incluso mostraba el caso (`{"484": 3, "488": None, "493": 0}` con total 4) y yo la di por buena en lugar de ver que dejaba el dato recuperable. Las versiones anteriores siguen en el historial de Git; la corrección no las revoca.

Los pendientes de licencia comercial ASIPONA, datos operativos de un cliente, precio, tablero público, experimento y auditoría no se presentan como problemas ya resueltos.

## 5. ¿Qué aprendimos de cada materia?

### Ingeniería de Datos

Una fuente accesible no implica que todos sus campos deban almacenarse. El ZIP DENUE se procesa en memoria y la proyección minimizada llega a Bronce; el linaje conserva procedencia y posición sin redistribuir contactos. Los hashes y las fechas permiten detectar que cambió una entrada y evitan reemplazar la ingesta por la fecha de procesamiento. Minimizar no tiene que significar perder cobertura: agregar con un umbral de anonimato pasa de 2 a 632 establecimientos representados sin guardar un solo dato individual.

### Análisis Estadístico

El mapa actual no es una variable histórica disponible desde 2021 y no se usa en el pronóstico. La muestra de dos sociedades tampoco representa todas las transportistas. La dirección comercial exige observar viajes, costos y tiempos propios; no permite inferir utilidad empresarial desde TEU ni afirmar causalidad en una comparación simple antes/después. Falta ejecutar el experimento E2 y sus análisis.

### Calidad en los Sistemas de Información

Se convierten requisitos en fallos comprobables: una fecha de ingesta inventada, un archivo modificado o un registro sin origen deben impedir la validación. Una prueba sintética del tablero comprueba cálculo y ejecución, pero no equivale a medir ahorro de un cliente ni a completar la evaluación ISO y auditoría cruzada.

## 6. Evidencias

- [Ficha E2 y reproducción](E2/ENTREGA.md).
- [Declaración de ética](etica-datos.md), [revisión de condiciones y robots](../calidad/e2/fuentes_web.json).
- [Resumen geoespacial](../calidad/e2/geoespacial.json), [manifiesto de linaje](../calidad/e2/linaje.json), [validación](../calidad/e2/validacion_linaje.json).
- [Celdas DENUE en Oro](../data/oro/denue_celdas.csv), [pruebas del agregado](../tests/test_denue_agregado.py), [prueba de reintento](../tests/test_extractor_base.py).
- [Pruebas E2](../tests/test_e2.py), [prueba del tablero](../tests/test_tablero.py), [caso sintético ejecutado](../calidad/e2/validacion_tablero.json).
- [Dirección del producto y piloto propuesto](E2/enfoque-producto.md).
- Los commits de implementación y de evidencia de esta rama y el tag `e2` identifican el estado entregado. No se atribuyen revisión, aceptación o commits a un integrante que no participó en esta sesión.

## Uso de IA generativa

Se usó Codex para leer requisitos, inspeccionar la base E1, investigar fuentes oficiales, implementar y probar integración, linaje y simulador, y redactar documentación y una recomendación comercial. Las pruebas son evidencia de ejecución del software, no de aprendizaje individual, consentimiento, venta o revisión por pares. El equipo debe revisar, poder explicar y defender las decisiones y los límites de esta versión. El 19/11, Emilio usó **Claude Code (Anthropic)** para integrar las ramas, programar el agregado DENUE, el linaje por celda y el reintento, escribir sus pruebas y actualizar esta documentación; todo se ejecutó y verificó antes de subirlo.
