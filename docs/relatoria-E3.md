# Relatoría E3

1. **¿Qué nos propusimos?** Mejorar y medir una etapa del pipeline, reducir decisiones de captura inseguras y publicar un dataset curado con procedencia y condiciones de uso.

2. **¿Qué hicimos?** El 25/11/2026 se optimizó la interpretación repetida de fechas y se preparó el datasheet del agregado DENUE. El 26/11 se revisó la captura, se corrigió el tratamiento de HTTP 429 en `robots.txt` y se ejecutaron comparaciones sin red sobre Bronce versionado y respuestas simuladas. Codex apoyó implementación, medición y redacción; no se imputan horas humanas no registradas.

3. **¿Qué resultados obtuvimos?** Con 1,484 filas Banxico, la mediana de normalización bajó de 3.235 a 0.897 segundos y el pico de memoria rastreada de 2,104,185 a 2,087,309 bytes. Las salidas y rechazos fueron iguales. En 400 casos simulados de robots, las decisiones incorrectas bajaron de 100 a 0; ese microensayo tardó más después, 0.0471 frente a 0.0651 segundos. El agregado DENUE publicado contiene 28 celdas y 608 establecimientos; otros 24 fueron suprimidos.

4. **¿Qué salió mal y cómo respondimos?** La respuesta 429 podía interpretarse como permiso para descargar; ahora bloquea el acceso y se prueba junto con 403, 503 y 404. La mejora de errores se demostró en simulación, no en capturas reales. No se documentó una licencia abierta inequívoca de ASIPONA, por lo que el dataset para terceros utiliza DENUE con condiciones y atribución del INEGI.

5. **¿Qué aprendimos y qué falta?** Medir tiempo, memoria y errores requiere cargas y definiciones distintas: una mejora de velocidad no implica menos fallos. No hay evidencia de experimento E2 con combinación ganadora ni de auditoría cruzada; tampoco se han demostrado fallos reales evitados. Faltan los datos por terminal para la MANOVA prevista, la validación independiente y los demás criterios del Sello TDL. El formulario oficial no fue proporcionado.

6. **Evidencias.** [Ficha](E3/ENTREGA.md), [datasheet](E3/datasheet.md), [normalización](../calidad/e3/benchmark_26nov.json), [captura simulada](../calidad/e3/benchmark_captura.json), [pruebas de captura](../tests/test_extractor_base.py), [PCA](E3/multivariado.md) y [calidad](E3/calidad.md).
