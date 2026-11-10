# Relatoría E1 · De Bronce a datos validados

**Equipo:** Emilio Rodrigo Ayala Reynoso y Karol Gabriel Morán Aréchiga<br>
**Fecha:** 10 de noviembre de 2026 · **Alcance de esta versión:** Ingeniería de Datos.

## 1. ¿Qué nos propusimos?

Automatizar el paso de las dos fuentes de Bronce a Plata y Oro, admitiendo únicamente registros que cumplan contratos explícitos. Conservar todos los rechazos con motivo y mantener una serie integrada de al menos 36 meses, sin modificar los archivos crudos.

## 2. ¿Qué hicimos?

El 10 de noviembre se creó la rama `gabriel/e1` a partir de `main`, incluido el commit de captura programada `0836001`. Se revisaron las tablas de ASIPONA y Banxico, se implementaron limpieza, integración y contratos Pandera en `src/`, y se conectó el procesamiento con GitHub Actions. La implementación y documentación se realizaron con asistencia de Codex, bajo la solicitud de Gabriel; no se atribuyen estas operaciones a trabajo manual de Emilio.

La primera ejecución admitió 626 de 648 filas ASIPONA, estimó ocho valores por terminal y puso 22 posiciones no publicadas en cuarentena. Banxico aportó 1,473 cotizaciones válidas: se agregaron a 71 meses y se integraron 70 con los datos del puerto; noviembre parcial permaneció en Plata. Se generaron 280 observaciones terminal-mes.

Los tiempos de máquina están en `calidad/bitacora_pipeline.csv`. Las horas personales de los integrantes y la revisión cruzada no están confirmadas para esta sesión y no se fabrican a partir del tiempo del asistente.

## 3. ¿Qué decidimos y por qué?

Se separaron los ceros sospechosos de 2021, las posiciones futuras y los valores corruptos. Para los ocho faltantes auxiliares se eligió la mediana de hasta tres observaciones reales anteriores: evita usar meses futuros y resiste extremos. No se imputa el objetivo `teu_total`.

Los extremos físicamente válidos se marcan por IQR y puntaje robusto, conservando la observación. Se eligió comparar suavizados en columnas adicionales para no borrar una temporada de actividad auténtica. Las escalas y los cortes de discretización se ajustan sin los seis últimos meses reservados para prueba.

Banxico se agrega mensualmente y la unión exige una sola fila por mes. Un mes parcial no entra en Oro. Se mantienen cotizaciones diarias y metadatos para revisar lo que se pierde al agregar. Los errores estructurales rechazan el lote; los errores de fila conservan su evidencia en cuarentena.

## 4. ¿Qué salió mal y cómo lo corregimos?

El examen de Bronce encontró ocho ceros publicados por terminal en noviembre-diciembre de 2021, dos celdas vacías en meses no publicados y diferencias pequeñas entre sumas y acumulados. Se corrigió su interpretación en Plata, conservando Bronce y el valor original. No se forzó que una imputación coincidiera con el acumulado oficial.

En la preparación local faltaban dependencias de validación y cobertura; se preparó el entorno y se añadieron comprobaciones automáticas. Las pruebas inyectan registros corruptos, duplicados y cambios de esquema para comprobar que no atraviesen la puerta ni contaminen una imputación. Estas incidencias técnicas no se asignan como defectos personales PSP sin confirmar autoría y tiempo de corrección.

## 5. ¿Qué aprendimos de cada materia?

**Ingeniería de Datos:** conservar archivo crudo, línea, URL, transformación y motivo de rechazo permite explicar la diferencia entre una observación válida, una estimación y un mes todavía no publicado.

**Análisis Estadístico:** un patrón de ausencia no demuestra MCAR, MAR o MNAR; la explicación depende de supuestos sobre la fuente. Un atípico puede ser actividad real. Ajustar escalas con meses de prueba produciría fuga temporal.

**Calidad:** una validación útil debe dejar evidencia del fallo y comprobar conservación de filas. Repetir el pipeline, verificar hashes y forzar fallas aporta evidencia técnica; no sustituye la revisión humana del equipo.

## 6. Evidencias

[Ficha E1](E1/ENTREGA.md), [decisiones de limpieza](E1/limpieza.md), [scripts](../src/), [pruebas](../tests/test_e1.py), [resumen automático](../calidad/e1/resumen.json), [Plata](../data/plata/), [Oro](../data/oro/) y [cuarentena](../data/cuarentena/e1/).

Se declara el uso de **Codex (OpenAI)** para programación, pruebas y redacción. Esta versión relata el trabajo de Ingeniería de Datos solicitado; no afirma haber completado los pronósticos ni el plan SQA de las otras materias.
