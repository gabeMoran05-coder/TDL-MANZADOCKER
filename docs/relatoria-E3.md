# Relatoría E3 · Observatorio del Puerto de Manzanillo

Equipo: Emilio Rodrigo Ayala Reynoso y Karol Gabriel Morán Aréchiga · Periodo: 24 al 27 de noviembre de 2026

## 1. ¿Qué nos propusimos?

- Reducir de forma medible el tiempo del pipeline sin cambiar su salida y corregir los errores de captura.
- Publicar el agregado DENUE con licencia y datasheet.
- Comparar las cuatro terminales en varias variables a la vez (MANOVA) y resumir el puerto con PCA.
- Presentar la evidencia de cada criterio del Sello TDL.

## 2. ¿Qué hicimos?

| Fecha | Qué se hizo | Quién y tiempo |
|---|---|---|
| 25/11 | Optimización de `normalizar` (fechas de captura repetidas se interpretan una vez) y benchmark contra `ceceab9`. Datasheet DENUE. Etiqueta `e3` | Gabriel, con Codex; tiempo no registrado |
| 25/11 | PCA de 34 meses, Mardia, mapa en el tablero; evaluación de calidad, MoProSoft/CMMI, PSP y tendencias (`e3-revision-1`) | Gabriel, con Codex; tiempo no registrado |
| 26/11 | Corrección de robots.txt con HTTP 429 y ensayo simulado de 400 casos (`e3-revision-2`) | Gabriel, con Codex; tiempo no registrado |
| 27/11 | Revisión de etiquetas, diagnóstico y corrección de DENUE, benchmark con memoria de proceso, reproducción en copia limpia y gitleaks | Emilio, con Claude Code; 14 min en [tiempo-emilio](../calidad/tiempo-emilio.csv) |
| 27/11 | Extracción de tráfico por terminal desde los PDF en Bronce, MANOVA y actualización de la ficha | Emilio, con Claude Code; 20:48–22:00 en el mismo registro |

Gabriel no tiene registros de tiempo E3; no se estiman horas que no se midieron.

## 3. ¿Qué decidimos y por qué?

- **MANOVA con acumulados anuales.** ASIPONA publica el tráfico por terminal solo como acumulado del año.
  - **Elegido:** 28 observaciones terminal-año de los 7 PDF ya guardados, sin descargar nada. La unidad es más gruesa, pero el dato es real y reproducible.
  - **Descartado:** copiar a cada terminal los tráficos del puerto completo, porque sería pseudorreplicación.
  - **Descartado:** descargar unos 60 EM mensuales y restar acumulados, porque agrava el riesgo, sin resolver, de redistribuir los PDF.
  - Las respuestas son razones logarítmicas y no porcentajes, porque los porcentajes suman 100. El año entra como bloque.
- **Medición de rendimiento.** No se reemplazó el benchmark de Gabriel: se agregó uno con entrada fija por SHA-256, un proceso por versión y memoria total del proceso. Así se separa lo que mejoró (el tiempo) de lo que no mejoró (la memoria).
- **DENUE.** Se aceptan encabezados en mayúsculas o minúsculas. Se descartó fijar un formato, porque un cambio de INEGI volvería a tumbar la captura.

## 4. ¿Qué salió mal y cómo lo corregimos?

- **Defecto 9 de Emilio** ([registro](../calidad/defectos-emilio.csv)):
  - Desde E0, un HTTP 429 en robots.txt se trataba como permiso para descargar.
  - Lo encontró Gabriel. Ahora bloquea la descarga; en 400 casos simulados, las decisiones incorrectas bajaron de 100 a 0.
- **Defecto 10 de Emilio:**
  - El 26 y 27/11 INEGI cambió los encabezados del CSV a mayúsculas. La captura DENUE falló con 0 celdas y la disponibilidad de 14 días bajó a 78.57 %.
  - Se corrigió y se agregó una prueba. Con la descarga real, el resultado pasó de 0 a 29 celdas.
- **La memoria no bajó.** La mediana de tiempo bajó 71.2 %, pero el pico del proceso siguió en 124.8 MiB. Se reporta tal cual.
- **No se pudo cumplir:**
  - No llegó el informe de la auditoría cruzada.
  - No existe el experimento E2, así que la optimización no aplica una «combinación ganadora».

## 5. ¿Qué aprendimos?

### Ingeniería de Datos

Una fuente externa puede cambiar su formato sin aviso. La bitácora de captura detectó el fallo de DENUE en dos días, y la prueba con la descarga real confirmó la causa antes de corregir.

Medir bien exige fijar la entrada: la misma versión tardó 8.17 s y 1.65 s en corridas distintas.

### Análisis Estadístico

- La MANOVA (Wilks 0.0011, Pillai 1.92, p < 0.001; permutación p = 0.0001) muestra perfiles distintos por terminal: SSA concentra el transbordo (28 %) y OCUPA la exportación (57 %).
- Los supuestos no se rechazan (Mardia p = 0.24 y 0.97; Box p = 0.22), pero con 7 observaciones por terminal tienen poca potencia. Por eso se agregó una prueba de permutación.

### Calidad en los Sistemas de Información

- Reproducir con hashes da evidencia más fuerte que releer: el PCA y los indicadores salieron idénticos en una copia limpia.
- La disponibilidad del Sello depende de días que ya pasaron: los fallos del 23, 26 y 27/11 no se recuperan.

## 6. Evidencias

- [Ficha con mapa de la rúbrica](E3/ENTREGA.md)
- [Datasheet](E3/datasheet.md)
- [Multivariado](E3/multivariado.md)
- [Calidad y Sello](E3/calidad.md)
- [MANOVA](../calidad/e3/manova.json)
- [Tráfico por terminal](../data/plata/terminal_trafico_anual.csv)
- [Benchmark de proceso](../calidad/e3/benchmark_proceso.json)
- [Captura simulada](../calidad/e3/benchmark_captura.json)
- [Secretos](../calidad/e3/secretos.json)
- [Reproducción](../calidad/e3/reproduccion_emilio.json)

## Uso de IA generativa

- **Gabriel:** Codex apoyó la implementación, la medición y la redacción.
- **Emilio:** Claude Code apoyó el diagnóstico, el código, las pruebas, la MANOVA y la redacción.

Las cifras salen de ejecuciones guardadas en el repositorio. Ambos integrantes deben poder explicar cada resultado en el Demo Day.
