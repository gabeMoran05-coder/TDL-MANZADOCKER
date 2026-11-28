# Análisis multivariado E3

## Alcance y muestra

La pregunta E0 compara SSA, CONTECON, OCUPA y TIMSA por terminal-mes, con TEU, importación, exportación, transbordo y participación. En Plata existen 70 valores por terminal de TEU y participación derivada; no existen series de importación, exportación y transbordo **por terminal**. Los 34 meses de estos tráficos disponibles corresponden al puerto completo. Copiarlos a las cuatro terminales produciría pseudorreplicación; la participación es una función de TEU y total portuario. No hay cinco respuestas independientes por terminal, y las terminales comparten el mismo mes. No se calcula MANOVA ni Wilks/Pillai: se requieren datos por terminal, revisión de dependencia temporal, tamaño, valores extremos y homogeneidad de matrices de covarianza. Una MANOVA contrasta un vector de medias conjuntamente, mientras que varios ANOVA separados multiplican pruebas y no usan la covariación de las respuestas.

## Exploración alternativa: un mes por fila

La matriz contiene 34 meses completos, enero 2024 a octubre 2026, y cinco variables observadas del puerto: TEU total, toneladas contenerizadas, buques, TEU importación y exportación. No se incluyeron imputaciones. La intersección de fechas reduce la muestra de 70 meses a 34. [Resultados, matrices de covarianza y correlación y hash](../../calidad/e3/pca.json); [puntos](../../calidad/e3/pca_puntos.csv); [gráficas](../../calidad/e3/pca_diagnosticos.png). Reproducir: `python -m scripts.analisis_e3`.

PCA sobre variables centradas y divididas por su desviación muestral. PC1 explica 68.49 % y PC2 17.48 %, juntos 85.97 %. Las cargas de PC1 son positivas (0.753–0.962): se denomina **actividad portuaria conjunta**. PC2 contrapone exportación (0.567) a importación (−0.533) y toneladas (−0.459): **contraste de tráfico y carga**. Los signos son convencionales. Los puntos son meses; las flechas representan correlaciones variable-componente escaladas por 2 para visualización. Este mapa ayuda a reconocer meses con perfiles distintos, no asigna capacidad a una terminal, ni prueba causalidad o rentabilidad.

El diagnóstico de Mardia usa covarianza con divisor n: asimetría 3.180, aproximación χ²(35) = 18.018, p = 0.992; curtosis 29.647, z = −1.865, p = 0.062. La gráfica Q-Q compara distancias cuadradas con χ²(5), mostrando desvíos en la cola superior. Estas probabilidades son aproximaciones bajo independencia y normalidad; los meses consecutivos pueden estar correlacionados, la muestra es pequeña y el TEU total contiene tráfico de importación y exportación. No se concluye que se cumplen los supuestos ni se usa el diagnóstico para validar MANOVA. PCA es descriptivo, no un análisis de grupos por terminal.

El tablero muestra el mapa solo si coincide el SHA-256 de la entrada; ante cambios debe regenerarse. La matriz puede incluir datos revisados por ASIPONA: fuentes y sus condiciones se mantienen en el repositorio, sin aplicar a estas series la licencia de DENUE.
