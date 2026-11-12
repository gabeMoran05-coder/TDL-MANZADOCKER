# Fiabilidad y disponibilidad de la captura (E1 · Calidad)

**Responsable:** Emilio Rodrigo Ayala Reynoso · **Corte de los datos de este documento:** 12 de noviembre de 2026, 21:19 UTC (última ejecución programada en `main`)
**Cálculo:** [`src/fiabilidad.py`](../../src/fiabilidad.py) · **Pruebas:** [`tests/test_fiabilidad.py`](../../tests/test_fiabilidad.py) · **Resultado vigente:** [`calidad/e1/fiabilidad.json`](../../calidad/e1/fiabilidad.json)
**Fuente de datos:** [`calidad/bitacora_captura.csv`](../../calidad/bitacora_captura.csv), una fila por fuente y ejecución, escrita por [`extractores/run_captura.py`](../../extractores/run_captura.py)

Los valores no se suponen: salen de la bitácora real. El workflow de captura recalcula `fiabilidad.json` en cada ejecución diaria, así que el JSON puede tener un corte más reciente que este documento.

## 1. Definiciones

| Concepto | Definición operativa en este proyecto |
|---|---|
| Ejecución | Filas de la bitácora con el mismo disparador que inician con menos de 10 minutos de diferencia (una por fuente: `asipona` y `banxico`). Una ejecución es **exitosa** solo si todas sus fuentes terminaron en `ok`. |
| Falla | Ejecución con al menos una fuente en estado distinto de `ok`. Varias fallas seguidas cuentan como una sola caída. |
| Programada / manual | Programada = disparador `schedule` (cron diario). Manual = `workflow_dispatch` o `manual-local`. **La disponibilidad se mide solo con las programadas**, porque las manuales las lanza una persona cuando todo funciona y sesgarían el resultado. |
| Tasa de éxito | Ejecuciones exitosas / ejecuciones. |
| MTTR | Tiempo medio desde que empieza una caída hasta la siguiente ejecución exitosa. Una caída abierta al corte cuenta hasta el corte. |
| MTBF | Tiempo de operación observado (desde la primera ejecución hasta el corte, menos el tiempo caído) / número de fallas. |
| Disponibilidad | A = MTBF / (MTBF + MTTR). Sin fallas, la disponibilidad observada es 1 y el MTBF no es medible: se informa el tiempo observado como cota inferior. |
| Cumplimiento del calendario | Días con al menos una captura programada exitosa / días del periodo. Complementa a la disponibilidad porque el cron debe correr una vez al día. |

## 2. Resultados al 12 de noviembre de 2026

| Métrica | Programadas | Manuales | Todas |
|---|---|---|---|
| Ejecuciones | 4 | 3 | 7 |
| Exitosas | 4 | 3 | 7 |
| Fallas | 0 | 0 | 0 |
| Tasa de éxito | **100%** | 100% | 100% |
| Horas observadas | 70.0 h | — | — |
| MTBF | No medible (sin fallas; cota inferior 70.0 h) | — | — |
| MTTR | No aplica (sin fallas) | — | — |
| Disponibilidad observada | **100%** | — | — |

Por fuente (programadas): `asipona` 4 de 4 y `banxico` 4 de 4.

**Calendario:** 4 de 4 días con captura programada exitosa (9, 10, 11 y 12 de noviembre), 100%.

**Contra el objetivo OC1 (disponibilidad ≥ 95%):** se cumple en lo observado.

## 3. Lo que estos números no dicen (lectura honesta)

1. **Hay menos días de los pedidos.** La entrega pide 7 días de bitácora (del 6 al 13 de noviembre). La captura programada empezó a correr el 9 de noviembre, porque el workflow se publicó la noche del 8. Al corte hay 4 días; si la ejecución del 13 corre antes de la entrega, serán 5.
2. **Pocas observaciones, poca certeza.** Con 4 éxitos en 4 intentos, el límite inferior de confianza al 95% para la tasa de éxito es apenas 0.05^(1/4) ≈ **47%** (intervalo exacto de Clopper-Pearson, unilateral). Con 5 de 5 sería ≈ 55%. Hacen falta del orden de 59 éxitos seguidos para afirmar con 95% de confianza que la tasa es al menos 95%. Por eso decimos "se cumple en lo observado" y no "el sistema tiene 95% de disponibilidad".
3. **El MTBF todavía no existe.** No ha habido ninguna falla. Inventar un valor sería suponer; se reporta la cota inferior de 70 horas y se recalcula sola cuando ocurra la primera falla.
4. **El cron de GitHub se retrasa.** El workflow está programado a las 14:00 UTC (08:00 en Colima), pero las ejecuciones empezaron entre **6.7 y 9.3 horas tarde** (promedio 7.6 h): 23:17, 20:42, 21:04 y 21:19 UTC. GitHub documenta que las tareas programadas pueden retrasarse en horas de alta demanda. Para el observatorio no es crítico, porque las fuentes publican una vez al día o al mes, pero significa que el dato del día llega por la tarde y no por la mañana.
5. **Se mide la captura, no el sitio de la fuente.** Una ejecución exitosa demuestra que en ese momento se pudo capturar; no mide si ASIPONA o Banxico estuvieron disponibles el resto del día.

## 4. Cómo reproducirlo

```bash
python -m src.fiabilidad                                  # corte = última ejecución de la bitácora
python -m src.fiabilidad --corte 2026-11-13T23:59:59Z     # corte fijo
python -m pytest -q tests/test_fiabilidad.py
```

Las pruebas incluyen casos sintéticos con una falla reparada (MTTR 10 h, MTBF 90 h, A = 0.90), fallas consecutivas, una falla abierta al corte, días sin captura y bitácora vacía, para comprobar que las fórmulas funcionan también cuando sí hay fallas.

## 5. Acciones

| Acción | Responsable | Cuándo |
|---|---|---|
| Recalcular automáticamente en cada captura (paso "Medir fiabilidad" en `captura.yml`) | Emilio | E1 (hecho) |
| Revisar `fiabilidad.json` en cada entrega y reportar en la relatoría si alguna métrica baja de OC1 | Quality Lead de la entrega | E2, E3 |
| Si una falla dura más de 24 h (meta de MTTR del plan SQA), abrir un issue con etiqueta `calidad` y registrarla como defecto | Quien la detecte | Continuo |
| Para el Sello TDL (95% en los últimos 14 días), no tocar el cron ni el workflow sin pasar por un pull request revisado | Ambos | Hasta E3 |
