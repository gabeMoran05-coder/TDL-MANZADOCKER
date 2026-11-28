# Análisis multivariado E3

## MANOVA: ¿las cuatro terminales tienen el mismo tamaño y perfil de tráfico?

**Datos.** La pregunta E0 compara SSA, CONTECON, OCUPA y TIMSA. Los EM de ASIPONA publican importación, exportación, cabotaje y transbordo por terminal, pero solo como acumulado del año (tabla «Movimiento de TEU's por empresa por tráfico»), no por mes.

[terminales_trafico](../../src/terminales_trafico.py) extrae esa tabla de los 7 PDF que ya estaban en Bronce, sin descargar nada:
- **Muestra:** 28 observaciones terminal-año, 2020–2026.
- **Años:** 2026 es enero–octubre. 2020 sale de la columna «año anterior» del EM 2021.
- **Validaciones:**
  - En cada PDF, las terminales suman el TOTAL y los tráficos suman el total de cada terminal.
  - ASIPONA redondea: aparecen 6 diferencias de 1 TEU, que se documentan.
  - Se verifica el SHA-256 de cada PDF.
- **Verificación cruzada:** se comparó el «año anterior» de cada EM contra el EM de ese año. 4 de 16 comparaciones difieren porque ASIPONA revisó cifras; la mayor es CONTECON 2023, con −683 TEU en total (−852 en transbordo).

[Datos Plata](../../data/plata/terminal_trafico_anual.csv) · [resumen de extracción](../../calidad/e3/terminal_trafico.json).

**Respuestas.** Las participaciones suman 100 %, así que no se usan porcentajes: se usan razones logarítmicas.
- `ln(TEU total)`: tamaño.
- `ln(exportación/importación)`: perfil exportador.
- `ln(transbordo/importación)`: perfil de transbordo.

El cabotaje es 0 salvo 178 TEU de TIMSA en 2020, y se omite. El año entra como **bloque**, porque absorbe los choques comunes del puerto y que 2026 sea un año parcial. Modelo: `respuestas ~ terminal + año`.

**Resultado** ([JSON completo](../../calidad/e3/manova.json); reproducir con `python -m scripts.manova_e3`):

| Estadístico (efecto terminal) | Valor | F aprox. | gl | p |
|---|---:|---:|---|---:|
| Lambda de Wilks | 0.0011 | 66.20 | 9; 39.1 | < 0.001 |
| Traza de Pillai | 1.918 | 10.64 | 9; 54 | < 0.001 |
| Permutación de terminales dentro de cada año (9,999, semilla fija) | — | — | — | 0.0001 (Pillai y Wilks) |

Las terminales difieren en conjunto. La permutación no depende de la normalidad y da el mismo resultado; 0.0001 es el valor más pequeño que permiten 9,999 permutaciones.

Perfil promedio 2020–2026 (importación / exportación / transbordo):

| Terminal | Importación | Exportación | Transbordo |
|---|---:|---:|---:|
| SSA | 37.0 % | 34.8 % | **28.2 %** |
| CONTECON | 43.1 % | 40.2 % | 16.7 % |
| TIMSA | 46.9 % | 40.0 % | 13.2 % |
| OCUPA | 39.8 % | **57.4 %** | 2.8 % |

**Lectura para el cliente:** las terminales no son intercambiables.
- SSA concentra el transbordo: contenedores que solo cambian de buque y no salen por carretera.
- OCUPA es la más exportadora y casi no tiene transbordo.
- Para un transportista que retira importaciones, la mayor importación absoluta está en CONTECON y SSA. TIMSA tiene la mayor proporción de importación, pero con menor volumen.

**Supuestos** (sobre residuos del modelo, 18 grados de libertad):
- **Normalidad multivariada (Mardia):** asimetría p = 0.243 y curtosis p = 0.968; no hay evidencia en contra.
- **Igualdad de covarianzas (M de Box):** χ²(18) = 22.20, p = 0.223; no hay evidencia en contra.
- **Límites:**
  - Con 7 observaciones por terminal, estas pruebas tienen poca potencia: no detectar un problema no prueba que no exista.
  - Las mismas terminales se observan cada año, así que puede quedar correlación serial dentro de cada una. Por eso se presenta también la permutación.

**¿Por qué no basta con varios ANOVA separados?** Cada ANOVA mira una respuesta y multiplica las pruebas: con tres al 5 %, la probabilidad de al menos un falso positivo sube hasta cerca de 14 %. La MANOVA prueba el vector completo de medias con un solo nivel de error y aprovecha que las respuestas están correlacionadas: dos respuestas que separan poco cada una pueden separar mucho juntas.

Como referencia, los ANOVA separados con corrección de Bonferroni también son significativos:
- `ln(TEU total)`: F = 512.0.
- `ln(exportación/importación)`: F = 14.4, p = 0.0002.
- `ln(transbordo/importación)`: F = 44.1, p < 0.001.

La diferencia de tamaño es la más fuerte, pero el perfil de tráfico también separa a las terminales por sí solo.

**Lo que no prueba:**
- No dice por qué difieren las terminales: puede ser por contratos con navieras, equipamiento o espacio.
- No predice meses.
- Es un análisis anual, no mensual. Obtener meses exigiría descargar los EM de cada mes y restar acumulados.

## Exploración alternativa: un mes por fila

La matriz contiene 34 meses completos, enero 2024 a octubre 2026, y cinco variables observadas del puerto: TEU total, toneladas contenerizadas, buques, TEU importación y exportación. No se incluyeron imputaciones. La intersección de fechas reduce la muestra de 70 meses a 34. [Resultados, matrices de covarianza y correlación y hash](../../calidad/e3/pca.json); [puntos](../../calidad/e3/pca_puntos.csv); [gráficas](../../calidad/e3/pca_diagnosticos.png). Reproducir: `python -m scripts.analisis_e3`.

PCA sobre variables centradas y divididas por su desviación muestral. PC1 explica 68.49 % y PC2 17.48 %, juntos 85.97 %. Las cargas de PC1 son positivas (0.753–0.962): se denomina **actividad portuaria conjunta**. PC2 contrapone exportación (0.567) a importación (−0.533) y toneladas (−0.459): **contraste de tráfico y carga**. Los signos son convencionales. Los puntos son meses; las flechas representan correlaciones variable-componente escaladas por 2 para visualización. Este mapa ayuda a reconocer meses con perfiles distintos, no asigna capacidad a una terminal, ni prueba causalidad o rentabilidad.

El diagnóstico de Mardia usa covarianza con divisor n: asimetría 3.180, aproximación χ²(35) = 18.018, p = 0.992; curtosis 29.647, z = −1.865, p = 0.062. La gráfica Q-Q compara distancias cuadradas con χ²(5), mostrando desvíos en la cola superior. Estas probabilidades son aproximaciones bajo independencia y normalidad; los meses consecutivos pueden estar correlacionados, la muestra es pequeña y el TEU total contiene tráfico de importación y exportación. No se concluye que se cumplen los supuestos ni se usa el diagnóstico para validar MANOVA. PCA es descriptivo, no un análisis de grupos por terminal.

El tablero muestra el mapa solo si coincide el SHA-256 de la entrada; ante cambios debe regenerarse. La matriz puede incluir datos revisados por ASIPONA: fuentes y sus condiciones se mantienen en el repositorio, sin aplicar a estas series la licencia de DENUE.
