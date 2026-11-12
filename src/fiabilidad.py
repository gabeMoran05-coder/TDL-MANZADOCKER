"""Fiabilidad y disponibilidad de la captura, medidas con la bitacora real.

Uso: python -m src.fiabilidad [--raiz RUTA] [--corte AAAA-MM-DDTHH:MM:SSZ]

Lee calidad/bitacora_captura.csv (una fila por fuente y ejecucion) y escribe
calidad/e1/fiabilidad.json. Definiciones (ver docs/E1/fiabilidad.md):

- Ejecucion: filas con el mismo disparador que inician con menos de
  VENTANA_EJECUCION_MIN minutos de diferencia. Una ejecucion es exitosa solo si
  todas sus fuentes terminaron en "ok".
- Falla: ejecucion (o fila, en el calculo por fuente) con estado distinto de "ok".
- MTTR: tiempo desde una falla hasta la siguiente ejecucion exitosa.
- MTBF: tiempo de operacion observado / numero de fallas. Sin fallas no existe
  un MTBF medible; se informa el tiempo observado como cota inferior.
- Disponibilidad: A = MTBF / (MTBF + MTTR); sin fallas, A observada = 1.
- Cumplimiento del calendario: dias con al menos una ejecucion programada
  exitosa / dias del periodo (la captura esta programada una vez al dia).
"""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

BITACORA = "calidad/bitacora_captura.csv"
SALIDA = "calidad/e1/fiabilidad.json"
HORA_PROGRAMADA_UTC = 14  # cron "0 14 * * *" en .github/workflows/captura.yml
VENTANA_EJECUCION_MIN = 10
OBJETIVO_DISPONIBILIDAD = 0.95  # OC1 de la propuesta E0


def leer_bitacora(ruta: Path) -> pd.DataFrame:
    datos = pd.read_csv(ruta, dtype=str, keep_default_na=False)
    if datos.empty:
        return datos.assign(inicio=pd.Series(dtype="datetime64[ns, UTC]"))
    datos["inicio"] = pd.to_datetime(datos["inicio_utc"], utc=True)
    datos["fin"] = pd.to_datetime(datos["fin_utc"], utc=True)
    datos["exito"] = datos["estado"].str.strip().str.lower().eq("ok")
    datos["programada"] = datos["disparador"].eq("schedule")
    return datos.sort_values("inicio").reset_index(drop=True)


def agrupar_ejecuciones(filas: pd.DataFrame) -> pd.DataFrame:
    """Une las filas de cada fuente en ejecuciones completas."""
    if filas.empty:
        return pd.DataFrame(columns=["inicio", "fin", "disparador", "exito", "fuentes"])
    ejecuciones = []
    actual = None
    for _, fila in filas.iterrows():
        nueva = (
            actual is None
            or fila["disparador"] != actual["disparador"]
            or fila["inicio"] - actual["inicio"] > timedelta(minutes=VENTANA_EJECUCION_MIN)
        )
        if nueva:
            actual = {"inicio": fila["inicio"], "fin": fila["fin"],
                      "disparador": fila["disparador"], "exito": True, "fuentes": []}
            ejecuciones.append(actual)
        actual["fin"] = max(actual["fin"], fila["fin"])
        actual["exito"] = actual["exito"] and bool(fila["exito"])
        actual["fuentes"].append(fila["fuente"])
    return pd.DataFrame(ejecuciones)


def metricas(eventos: pd.DataFrame, corte: datetime) -> dict:
    """Tasa de exito, MTBF, MTTR y disponibilidad de una secuencia de eventos.

    `eventos` necesita columnas inicio (UTC) y exito (bool), en orden temporal.
    """
    total = len(eventos)
    if total == 0:
        return {"ejecuciones": 0, "exitosas": 0, "fallas": 0, "tasa_exito": None,
                "horas_observadas": 0.0, "mtbf_h": None, "mttr_h": None,
                "disponibilidad": None, "nota": "sin ejecuciones en el periodo"}
    exitosas = int(eventos["exito"].sum())
    inicio = eventos["inicio"].iloc[0]
    horas = max((corte - inicio).total_seconds() / 3600, 0.0)

    reparaciones = []
    caido_desde = None
    for _, ev in eventos.iterrows():
        if not ev["exito"] and caido_desde is None:
            caido_desde = ev["inicio"]
        elif ev["exito"] and caido_desde is not None:
            reparaciones.append((ev["inicio"] - caido_desde).total_seconds() / 3600)
            caido_desde = None
    abierta = caido_desde is not None
    if abierta:  # falla sin reparar al corte: cuenta hasta el corte
        reparaciones.append((corte - caido_desde).total_seconds() / 3600)

    fallas = total - exitosas
    resultado = {"ejecuciones": total, "exitosas": exitosas, "fallas": fallas,
                 "tasa_exito": round(exitosas / total, 4),
                 "horas_observadas": round(horas, 2)}
    if fallas == 0:
        resultado.update(mtbf_h=None, mttr_h=None, disponibilidad=1.0,
                         nota=f"sin fallas en {horas:.1f} h observadas: el MTBF no es "
                              f"medible todavia (cota inferior {horas:.1f} h)")
        return resultado
    caida = sum(reparaciones)
    mtbf = max(horas - caida, 0.0) / fallas
    mttr = caida / len(reparaciones)
    resultado.update(mtbf_h=round(mtbf, 2), mttr_h=round(mttr, 2),
                     disponibilidad=round(mtbf / (mtbf + mttr), 4) if mtbf + mttr else None,
                     nota="falla abierta al corte" if abierta else "")
    return resultado


def calendario(programadas: pd.DataFrame, corte: datetime) -> dict:
    """Dias con captura programada exitosa y retraso respecto al cron."""
    if programadas.empty:
        return {"dias_periodo": 0, "dias_con_exito": 0, "cumplimiento": None,
                "dias_sin_captura": [], "retraso_h": {}}
    primer_dia: date = programadas["inicio"].iloc[0].date()
    dias = [primer_dia + timedelta(days=i) for i in range((corte.date() - primer_dia).days + 1)]
    # el dia del corte solo cuenta si ya paso la hora programada
    if corte.hour < HORA_PROGRAMADA_UTC and dias and dias[-1] == corte.date():
        dias = dias[:-1]
    exitosos = set(programadas.loc[programadas["exito"], "inicio"].dt.date)
    retrasos = [
        (ev - ev.normalize() - timedelta(hours=HORA_PROGRAMADA_UTC)).total_seconds() / 3600
        for ev in programadas["inicio"]
    ]
    return {
        "dias_periodo": len(dias),
        "dias_con_exito": sum(d in exitosos for d in dias),
        "cumplimiento": round(sum(d in exitosos for d in dias) / len(dias), 4) if dias else None,
        "dias_sin_captura": [d.isoformat() for d in dias if d not in exitosos],
        "retraso_h": {"minimo": round(min(retrasos), 2), "promedio": round(sum(retrasos) / len(retrasos), 2),
                      "maximo": round(max(retrasos), 2)},
    }


def evaluar(raiz: Path, corte: datetime | None = None) -> dict:
    filas = leer_bitacora(raiz / BITACORA)
    if corte is None:
        corte = filas["fin"].max().to_pydatetime() if not filas.empty else datetime.now(timezone.utc)
    filas = filas[filas["inicio"] <= corte] if not filas.empty else filas
    ejecuciones = agrupar_ejecuciones(filas)
    programadas = ejecuciones[ejecuciones["disparador"].eq("schedule")] if not ejecuciones.empty \
        else ejecuciones
    manuales = ejecuciones[~ejecuciones["disparador"].eq("schedule")] if not ejecuciones.empty \
        else ejecuciones

    por_fuente = {}
    for fuente, grupo in (filas.groupby("fuente") if not filas.empty else []):
        por_fuente[fuente] = {
            "todas": metricas(grupo, corte),
            "programadas": metricas(grupo[grupo["programada"]], corte),
        }

    total_prog = metricas(programadas.reset_index(drop=True), corte)
    cal = calendario(programadas.reset_index(drop=True), corte)
    referencia = total_prog["disponibilidad"]
    return {
        "generado_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "corte_utc": corte.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "bitacora": BITACORA,
        "definiciones": "ver docs/E1/fiabilidad.md",
        "objetivo_oc1": OBJETIVO_DISPONIBILIDAD,
        "programadas": total_prog,
        "manuales": metricas(manuales.reset_index(drop=True), corte),
        "todas": metricas(ejecuciones.reset_index(drop=True), corte),
        "por_fuente": por_fuente,
        "calendario": cal,
        "cumple_oc1": {
            "disponibilidad": None if referencia is None else referencia >= OBJETIVO_DISPONIBILIDAD,
            "calendario": None if cal["cumplimiento"] is None
            else cal["cumplimiento"] >= OBJETIVO_DISPONIBILIDAD,
        },
    }


def main(argv: list[str] | None = None) -> dict:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--raiz", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--corte", help="fecha de corte UTC; por defecto, la ultima ejecucion")
    args = parser.parse_args(argv)
    corte = pd.Timestamp(args.corte).tz_convert("UTC").to_pydatetime() if args.corte else None
    resultado = evaluar(args.raiz, corte)
    salida = args.raiz / SALIDA
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: resultado[k] for k in ("programadas", "calendario", "cumple_oc1")},
                     ensure_ascii=False, indent=2))
    return resultado


if __name__ == "__main__":
    main()
