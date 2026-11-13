"""Pruebas del calculo de fiabilidad y disponibilidad (src/fiabilidad.py)."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd
import pytest

from src.fiabilidad import (
    agrupar_ejecuciones,
    calendario,
    evaluar,
    leer_bitacora,
    main,
    metricas,
)

ENCABEZADO = ("inicio_utc,fin_utc,duracion_s,fuente,estado,registros,"
              "archivos_nuevos,disparador,error\n")


def utc(texto: str) -> datetime:
    return datetime.fromisoformat(texto.replace("Z", "+00:00")).astimezone(timezone.utc)


def escribir_bitacora(raiz, filas: list[str]):
    ruta = raiz / "calidad" / "bitacora_captura.csv"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(ENCABEZADO + "".join(f + "\n" for f in filas), encoding="utf-8")
    return ruta


def fila(inicio, fuente="asipona", estado="ok", disparador="schedule", segundos=5):
    fin = (pd.Timestamp(inicio) + pd.Timedelta(seconds=segundos)).strftime("%Y-%m-%dT%H:%M:%SZ")
    error = "" if estado == "ok" else "RuntimeError: prueba"
    return f"{inicio},{fin},{segundos},{fuente},{estado},1,0,{disparador},{error}"


def eventos(*pares):
    return pd.DataFrame({"inicio": [pd.Timestamp(t) for t, _ in pares],
                         "exito": [e for _, e in pares]})


def test_sin_fallas_no_inventa_mtbf():
    ev = eventos(("2026-11-10T14:00Z", True), ("2026-11-11T14:00Z", True))
    r = metricas(ev, utc("2026-11-12T14:00Z"))
    assert r["tasa_exito"] == 1.0
    assert r["mtbf_h"] is None and r["mttr_h"] is None
    assert r["disponibilidad"] == 1.0
    assert r["horas_observadas"] == 48.0
    assert "cota inferior" in r["nota"]


def test_falla_reparada_calcula_mtbf_mttr_y_disponibilidad():
    # 100 h observadas, una falla a las 50 h reparada 10 h despues
    ev = eventos(("2026-11-01T00:00Z", True), ("2026-11-03T02:00Z", False),
                 ("2026-11-03T12:00Z", True))
    r = metricas(ev, utc("2026-11-05T04:00Z"))
    assert r["fallas"] == 1 and r["exitosas"] == 2
    assert r["mttr_h"] == 10.0
    assert r["mtbf_h"] == 90.0
    assert r["disponibilidad"] == pytest.approx(0.9, abs=1e-4)
    assert r["nota"] == ""


def test_fallas_consecutivas_cuentan_una_sola_caida():
    ev = eventos(("2026-11-01T00:00Z", False), ("2026-11-01T01:00Z", False),
                 ("2026-11-01T03:00Z", True))
    r = metricas(ev, utc("2026-11-01T10:00Z"))
    assert r["fallas"] == 2
    assert r["mttr_h"] == 3.0  # una sola reparacion de 3 h


def test_falla_abierta_cuenta_hasta_el_corte():
    ev = eventos(("2026-11-01T00:00Z", True), ("2026-11-01T06:00Z", False))
    r = metricas(ev, utc("2026-11-01T10:00Z"))
    assert r["mttr_h"] == 4.0
    assert r["nota"] == "falla abierta al corte"


def test_sin_eventos():
    r = metricas(eventos(), utc("2026-11-01T00:00Z"))
    assert r["ejecuciones"] == 0 and r["disponibilidad"] is None


def test_agrupa_fuentes_de_la_misma_ejecucion(tmp_path):
    ruta = escribir_bitacora(tmp_path, [
        fila("2026-11-10T20:00:00Z", "asipona"),
        fila("2026-11-10T20:00:08Z", "banxico", estado="falla"),
        fila("2026-11-10T20:00:30Z", "asipona", disparador="workflow_dispatch"),
        fila("2026-11-11T20:00:00Z", "asipona"),
    ])
    ej = agrupar_ejecuciones(leer_bitacora(ruta))
    assert len(ej) == 3
    assert ej.loc[0, "fuentes"] == ["asipona", "banxico"]
    assert not ej.loc[0, "exito"]  # basta una fuente fallida
    assert agrupar_ejecuciones(leer_bitacora(ruta).iloc[0:0]).empty


def test_calendario_detecta_dias_sin_captura_y_retraso():
    prog = eventos(("2026-11-09T16:00Z", True), ("2026-11-11T20:00Z", True))
    c = calendario(prog, utc("2026-11-11T23:00Z"))
    assert c["dias_periodo"] == 3
    assert c["dias_sin_captura"] == ["2026-11-10"]
    assert c["cumplimiento"] == pytest.approx(2 / 3, abs=1e-4)
    assert c["retraso_h"] == {"minimo": 2.0, "promedio": 4.0, "maximo": 6.0}


def test_calendario_no_cuenta_el_dia_del_corte_antes_de_la_hora():
    prog = eventos(("2026-11-09T16:00Z", True))
    c = calendario(prog, utc("2026-11-10T09:00Z"))
    assert c["dias_periodo"] == 1 and c["cumplimiento"] == 1.0
    assert calendario(eventos(), utc("2026-11-10T09:00Z"))["cumplimiento"] is None


def test_evaluar_y_main_escriben_json(tmp_path):
    escribir_bitacora(tmp_path, [
        fila("2026-11-09T01:00:00Z", disparador="manual-local"),
        fila("2026-11-09T23:00:00Z"),
        fila("2026-11-10T21:00:00Z", estado="falla"),
        fila("2026-11-11T21:00:00Z"),
    ])
    r = evaluar(tmp_path)
    assert r["programadas"]["ejecuciones"] == 3
    assert r["programadas"]["fallas"] == 1
    assert r["manuales"]["ejecuciones"] == 1
    assert r["por_fuente"]["asipona"]["programadas"]["tasa_exito"] == pytest.approx(0.6667)
    assert r["calendario"]["dias_sin_captura"] == ["2026-11-10"]
    assert r["cumple_oc1"]["calendario"] is False

    salida = main(["--raiz", str(tmp_path), "--corte", "2026-11-12T00:00:00Z"])
    guardado = json.loads((tmp_path / "calidad/e1/fiabilidad.json").read_text(encoding="utf-8"))
    assert guardado["corte_utc"] == "2026-11-12T00:00:00Z"
    assert guardado["programadas"] == salida["programadas"]


def test_bitacora_vacia(tmp_path):
    escribir_bitacora(tmp_path, [])
    r = evaluar(tmp_path, utc("2026-11-12T00:00Z"))
    assert r["todas"]["ejecuciones"] == 0
    assert r["cumple_oc1"] == {"disponibilidad": None, "calendario": None}


def test_bitacora_real_del_repositorio():
    """La bitacora versionada debe poder evaluarse sin errores."""
    from pathlib import Path

    raiz = Path(__file__).resolve().parents[1]
    r = evaluar(raiz)
    assert r["todas"]["ejecuciones"] >= 1
    assert 0.0 <= r["todas"]["tasa_exito"] <= 1.0
