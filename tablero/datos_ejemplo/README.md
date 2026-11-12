# Datos de ejemplo del tablero

`pronostico_teu.csv` **no es el pronóstico oficial.** Sirve para construir y probar el tablero mientras se integra el notebook de Estadística (`laboratorio/E1_pronostico.ipynb`), que exporta el oficial a `data/oro/pronostico_teu.csv`.

- Histórico: `teu_total` de `data/oro/mensual_integrado.csv` (ene-2021 a oct-2026).
- Pronóstico: método ingenuo estacional (el valor del mismo mes del año anterior).
- Intervalo: ± 1.96 × desviación estándar de los errores de ese método en el histórico (58 errores, σ ≈ 25,267 TEU).

Mismo contrato que el archivo oficial: `fecha, tipo (historico|pronostico), valor, li_95, ls_95, modelo`.

Cuando exista `data/oro/pronostico_teu.csv`, el tablero lo usa automáticamente y deja de mostrar el aviso de ejemplo.
