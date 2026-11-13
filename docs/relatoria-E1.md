# Relatoría E1 · De Bronce a datos validados

**Equipo:** Emilio Rodrigo Ayala Reynoso y Karol Gabriel Morán Aréchiga<br>
**Fecha:** 10 de noviembre de 2026 · **Alcance de esta versión:** Ingeniería de Datos.

## 1. ¿Qué nos propusimos?

Automatizar el paso de las dos fuentes de Bronce a Plata y Oro, admitiendo únicamente registros que cumplan contratos explícitos. Conservar todos los rechazos con motivo y mantener una serie integrada de al menos 36 meses, sin modificar los archivos crudos.

## 2. ¿Qué hicimos?

El 10 de noviembre se creó la rama `gabriel/e1` a partir de `main`, incluido el commit de captura programada `0836001`. Se revisaron las tablas de ASIPONA y Banxico, se implementaron limpieza, integración y contratos Pandera en `src/`, y se conectó el procesamiento con GitHub Actions. La implementación y documentación se realizaron con asistencia de Codex, bajo la solicitud de Gabriel; no se atribuyen estas operaciones a trabajo manual de Emilio.

La primera ejecución admitió 626 de 648 filas ASIPONA, estimó ocho valores por terminal y puso 22 posiciones no publicadas en cuarentena. Banxico aportó 1,473 cotizaciones válidas: se agregaron a 71 meses y se integraron 70 con los datos del puerto; noviembre parcial permaneció en Plata. Se generaron 280 observaciones terminal-mes.

La [verificación de CI](https://github.com/gabeMoran05-coder/TDL-MANZADOCKER/actions/runs/42892014765) y la [captura con limpieza completa](https://github.com/gabeMoran05-coder/TDL-MANZADOCKER/actions/runs/42892045653) terminaron en verde. Esta última agregó una cotización y dejó Banxico en 1,474 registros. La validación local aprobó 32 pruebas con 96.01% de cobertura; CI exige al menos 90%.

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

---

## Anexo de Estadística · Gabriel · 12 de noviembre de 2026

Este anexo se agrega sin sustituir la relatoría previa; Emilio lo unificará como Quality Lead.

### 1. Qué nos propusimos

Caracterizar y pronosticar `teu_total` de Oro con cuatro familias y el mismo corte de limpieza: 64 meses hasta abril de 2026 para ajustar y seis meses para comparar errores. Exportar un pronóstico de tres meses con un intervalo nominal del 95% y el contrato exacto del tablero.

### 2. Qué hicimos

El 12 de noviembre se actualizó `gabriel/e1` mediante `git pull --rebase origin main`. Se contrastaron diccionario, tabla Oro y parámetros; se ejecutó `laboratorio/E1_pronostico.ipynb`, con siete figuras y sus salidas guardadas, y se generaron CSV/JSON. El notebook no utiliza red ni tokens. Se agregaron dependencias y tres pruebas del contrato. Esta actividad fue asistida por Codex a solicitud de Gabriel; no se atribuye a trabajo manual de Emilio.

No se conocen los horarios personales ni las interrupciones de esta sesión. Se conservan los registros PSP individuales sin nuevas filas; el tiempo del asistente y de la máquina no se presenta como tiempo personal.

### 3. Qué decidimos y por qué

La descomposición aditiva ajustó ligeramente mejor en entrenamiento. Se utiliza una diferencia regular y ninguna estacional para la búsqueda SARIMA, informando la sensibilidad ADF con tendencia. ACF/PACF orientan 23 candidatos; AIC elige SARIMA(2,1,1)×(0,0,0,12), sin parámetros estacionales, y la comparación externa elige SES por MAPE (6.4824%). El margen frente a Holt-Winters es pequeño; se mantienen las tres métricas para no ocultar resultados distintos.

La correlación con buques es contemporánea; no se encontraron anticipaciones significativas tras preblanqueo y Holm. Los modelos son univariados y evitan solicitar buques o FIX futuros. El intervalo es condicional al modelo; no se convierte en promesa de 19/20 meses. Se propone ajustar esa frase del tablero durante la revisión de Emilio.

### 4. Qué salió mal y cómo lo corregimos

La verificación detectó escapes incorrectos al generar dos celdas y un argumento `old_names` retirado en AutoReg 0.15. Se corrigieron, se validó la sintaxis con Ruff y se ejecutó nuevamente el notebook completo sin errores de celda. Windows bloqueó `jupyter.exe`; se utilizó el punto de entrada oficial `python -m nbconvert`, sin cambiar la política del sistema. Son incidencias propuestas a Gabriel para confirmar como sintaxis, interfaz y entorno; no se inventan tiempos ni se registran como defectos personales automáticamente.

### 5. Qué aprendimos de cada materia

**Estadística:** ADF depende de tendencia y rezagos; rechazar una prueba no demuestra todos los supuestos. El menor MAPE no implica menor RMSE, y seis meses no establecen un ganador definitivo. Los residuos no rechazan Ljung-Box/normalidad/varianza en los contrastes usados, pero la varianza móvil cambia.

**Ingeniería de Datos:** el corte y contrato de Oro permiten comparar modelos sin fuga de prueba. Las columnas exportadas, fechas, valores históricos e intervalos se verifican antes de alimentar el tablero; el hash señala el conjunto exacto usado.

**Calidad:** la ejecución completa, las salidas persistidas y las pruebas aportan evidencia reproducible; la revisión cruzada y el cierre común continúan a cargo de Emilio.

### 6. Evidencias y uso de IA

[Notebook ejecutado](../laboratorio/E1_pronostico.ipynb), [resumen del pronóstico](E1/pronostico.md), [CSV](../data/oro/pronostico_teu.csv), [métricas y diagnósticos](../data/oro/pronostico_metricas.json), [figuras](E1/figuras/) y [pruebas](../tests/test_pronostico.py). Codex (OpenAI) se utilizó para código, ejecución, gráficos y redacción; todas las cifras se calcularon con Oro.
