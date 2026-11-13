# Relatoría E1 · Datos de confianza y pronóstico · Observatorio del Puerto de Manzanillo

**Equipo:** Emilio Rodrigo Ayala Reynoso (Data Engineer, Quality Lead de E1) · Karol Gabriel Morán Aréchiga (Data Statistician)<br>
**Periodo:** 9 al 13 de noviembre de 2026 · **Versión unificada** por el Quality Lead a partir de la relatoría de Ingeniería de Datos (10/11) y el anexo de Estadística (12/11) de Gabriel.

## 1. ¿Qué nos propusimos?

Que los datos pasaran solos de Bronce a Plata y Oro, sin borrar nada en silencio; pronosticar los TEU de los próximos 3 meses con el modelo de menor error en 6 meses no vistos; y demostrar con la bitácora que la captura cumple OC1 (disponibilidad ≥ 95%), con un plan SQA que diga cómo lo sostenemos.

## 2. ¿Qué hicimos?

| Fecha | Quién | Qué | Tiempo |
|---|---|---|---|
| 9/11 | Bot | Primera captura programada (23:17 UTC); desde entonces, una diaria sin fallas | Automático |
| 10/11 | Gabriel | Limpieza, integración, puerta Pandera y cuarentena en `src/`; CI en verde (commits `3880002`, `cc79d58`); primer tag `e1` | No registrado en PSP |
| 12/11, 13:00–13:30 | Emilio | Revisión del avance, reparto de E1; propuesta E0 con la entrevista al transportista nacional | 30 min |
| 12/11, 16:55–17:55 | Emilio | Fiabilidad, respaldo de Bronce, seguridad, requerimientos, plan SQA, tablero; PR #1 | 60 min |
| 12/11 (commits 20:11–20:12, unión 20:51) | Gabriel | Notebook de pronóstico, figuras, métricas, CSV para el tablero; PR #2 unido a `main` | No registrado en PSP |
| 13/11 | Emilio | Revisión del PR #2; unión de los PR #1 y #3; ficha, esta relatoría y tag | En registro de tiempo |

Resultado: 626 de 648 registros del puerto aceptados y 22 en cuarentena (meses no publicados); 70 meses en Oro; SES pronostica 344,909 TEU para noviembre de 2026 (rango nominal 307,550–382,269); 4 de 4 capturas programadas exitosas; 54 pruebas con 97% de cobertura.

## 3. ¿Qué decidimos y por qué?

1. **Imputar solo con el pasado y nunca el objetivo.** Los 8 ceros por terminal de 2021 se imputan con la mediana de hasta tres meses anteriores; `teu_total` no se imputa. *Descartado:* interpolar con meses futuros (fuga de información hacia la prueba).
2. **Elegir el modelo por MAPE en 6 meses fijos.** Gana SES (6.48%) aunque SARIMA gana en RMSE y Holt-Winters en MAE; se reportan las tres métricas y se aclara que el margen es pequeño. *Descartado:* elegir el modelo más sofisticado o cambiar de métrica después de ver los resultados.
3. **Medir la disponibilidad solo con capturas programadas** y reportar la cota estadística (con 4 de 4, el límite inferior al 95% es 47%). *Descartado:* contar las ejecuciones manuales, que se lanzan cuando todo funciona e inflan el resultado.

## 4. ¿Qué salió mal y cómo lo corregimos?

- **Proceso: los tres pull requests se unieron sin revisión previa.** El PR #2 lo unió Gabriel el 12/11; el PR #1 y el PR #3 (esta ficha y relatoría) los unió Emilio el 13/11 porque Gabriel no estaba disponible antes de la hora límite. El PR #2 se revisó después (comentario del Quality Lead con la lista del plan SQA §7); el #1 y el #3 pasaron la CI completa y Gabriel los revisará después de la entrega. *Corrección para E2:* activar la protección de `main` (hallazgo S3 de seguridad), para que GitHub exija revisión y CI antes de unir.
- **Defectos 3 y 4 de Emilio (tablero):** la caché no detectaba el pronóstico oficial (defecto 3, de diseño); la primera corrección usó un parámetro que Streamlit ignora (defecto 4, causado por el 3). Se encontraron con una prueba en Playwright que cambia el archivo con el servidor encendido.
- **Incidencias de Gabriel (pendientes de confirmar en su PSP):** escapes al generar celdas del notebook, un argumento retirado en statsmodels 0.15 y una regla de `.gitattributes` que trataba las figuras PNG como texto; las tres se corrigieron y la última tiene prueba.
- **Fuente:** ceros de 2021 que no son ceros reales y diferencias de 1–2 TEU entre la suma de meses y el acumulado oficial; se conservan en Bronce y se interpretan en Plata.
- **Registros PSP incompletos:** Gabriel no registró sus horas de E1. Se reporta así en lugar de estimarlas.

## 5. ¿Qué aprendimos de cada materia?

**Ingeniería de Datos.** Guardar el archivo crudo, la URL, el motivo de cada rechazo y el balance entrada = aceptados + rechazados permite explicar cualquier cifra: por ejemplo, que los 22 rechazos no son errores, sino meses que ASIPONA todavía no publica.

**Análisis Estadístico.** Que una prueba no rechace no demuestra el supuesto: Ljung-Box no rechaza (p = 0.08, 0.37, 0.32), pero la varianza móvil cambia hasta 5.3 veces; por eso el tablero presenta el intervalo como nominal y condicional, no como promesa.

**Calidad en los Sistemas de Información.** Una métrica sin tamaño de muestra engaña: "100% de disponibilidad" con 4 observaciones apenas garantiza 47% con 95% de confianza. Y un plan SQA solo funciona si la herramienta lo impone: lo escribimos, pero sin la protección de `main` los dos lo saltamos.

## 6. Evidencias

[Ficha E1](E1/ENTREGA.md) · [limpieza](E1/limpieza.md) · [pronóstico](E1/pronostico.md) y [notebook](../laboratorio/E1_pronostico.ipynb) · [fiabilidad](E1/fiabilidad.md) · [seguridad](E1/seguridad.md) · [requerimientos](E1/requerimientos.md) · [plan SQA](E1/plan-sqa.md) · [PR #1](https://github.com/gabeMoran05-coder/TDL-MANZADOCKER/pull/1) · [PR #2](https://github.com/gabeMoran05-coder/TDL-MANZADOCKER/pull/2) · [CI de main con todo unido](https://github.com/gabeMoran05-coder/TDL-MANZADOCKER/actions/runs/43477084951) · [defectos de Emilio](../calidad/defectos-emilio.csv) · [tiempo de Emilio](../calidad/tiempo-emilio.csv)

## Uso de IA generativa

**Codex (OpenAI)**, por Gabriel: limpieza, pruebas y notebook de pronóstico. **Claude Code (Anthropic)**, por Emilio: fiabilidad, respaldo, documentos de calidad, tablero y esta unificación. Todo se ejecutó y verificó antes de subirlo; las cifras salen de las ejecuciones y cada integrante debe poder explicar la parte del otro en el panel.
