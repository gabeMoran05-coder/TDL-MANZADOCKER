"""Contrato público del pronóstico que consume el tablero de Emilio."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import nbformat
import numpy as np
import pandas as pd
from PIL import Image

RAIZ = Path(__file__).resolve().parents[1]
COLUMNAS = ["fecha", "tipo", "valor", "li_95", "ls_95", "modelo"]


def test_csv_pronostico_cumple_contrato_y_conserva_historico():
    ruta = RAIZ / "data/oro/pronostico_teu.csv"
    datos = pd.read_csv(ruta)
    assert datos.columns.tolist() == COLUMNAS
    assert set(datos.tipo) == {"historico", "pronostico"}
    assert datos.fecha.str.fullmatch(r"\d{4}-\d{2}-01").all()
    fechas = pd.to_datetime(datos.fecha, format="%Y-%m-%d", errors="raise")
    assert fechas.is_unique and fechas.is_monotonic_increasing
    assert datos.modelo.notna().all() and datos.modelo.str.len().gt(0).all()
    for columna in ["valor", "li_95", "ls_95"]:
        assert pd.api.types.is_numeric_dtype(datos[columna])
    assert np.isfinite(datos.valor).all() and datos.valor.gt(0).all()

    historico = datos.loc[datos.tipo.eq("historico")]
    futuro = datos.loc[datos.tipo.eq("pronostico")]
    assert len(futuro) == 3
    assert np.isfinite(futuro[["valor", "li_95", "ls_95"]]).all().all()
    assert futuro.li_95.le(futuro.valor).all()
    assert futuro.valor.le(futuro.ls_95).all()
    assert historico[["li_95", "ls_95"]].isna().all().all()
    with ruta.open(encoding="utf-8", newline="") as archivo:
        filas = list(csv.DictReader(archivo))
    assert all(f["li_95"] == f["ls_95"] == "" for f in filas if f["tipo"] == "historico")

    oro = pd.read_csv(RAIZ / "data/oro/mensual_integrado.csv", parse_dates=["fecha"])
    assert len(historico) == len(oro)
    assert pd.to_datetime(historico.fecha).tolist() == oro.fecha.tolist()
    np.testing.assert_allclose(historico.valor, oro.teu_total, rtol=0, atol=1e-6)
    esperadas = pd.date_range(oro.fecha.max() + pd.offsets.MonthBegin(1), periods=3, freq="MS")
    assert pd.to_datetime(futuro.fecha).tolist() == esperadas.tolist()


def test_metricas_cuatro_modelos_y_ganador_consistente():
    resultado = json.loads((RAIZ / "data/oro/pronostico_metricas.json").read_text(encoding="utf-8"))
    assert set(resultado["modelos"]) == {"SES", "Holt", "Holt-Winters", "SARIMA"}
    for metricas in resultado["modelos"].values():
        assert set(metricas) == {"MAE", "RMSE", "MAPE"}
        assert all(
            isinstance(v, (int, float)) and np.isfinite(v) and v >= 0 for v in metricas.values()
        )
    ganador = min(
        resultado["modelos"],
        key=lambda m: tuple(resultado["modelos"][m][k] for k in ["MAPE", "RMSE", "MAE"]),
    )
    assert resultado["ganador"] == ganador
    csv_pronostico = pd.read_csv(RAIZ / "data/oro/pronostico_teu.csv")
    assert csv_pronostico.loc[csv_pronostico.tipo.eq("pronostico"), "modelo"].eq(ganador).all()
    parametros = json.loads(
        (RAIZ / "data/oro/parametros_transformacion.json").read_text(encoding="utf-8")
    )
    assert resultado["entrenamiento"]["fin"] == parametros["ajuste_hasta"]
    assert resultado["prueba"]["n"] == 6
    assert resultado["intervalo"]["nivel_nominal"] == 0.95
    assert resultado["intervalo"]["advertencias"]
    assert (
        resultado["datos_sha256"]
        == hashlib.sha256((RAIZ / "data/oro/mensual_integrado.csv").read_bytes()).hexdigest()
    )


def test_notebook_guardado_tiene_salidas_y_cero_celdas_fallidas():
    notebook = nbformat.read(RAIZ / "laboratorio/E1_pronostico.ipynb", as_version=4)
    nbformat.validate(notebook)
    celdas = [c for c in notebook.cells if c.cell_type == "code"]
    assert celdas and all(c.execution_count is not None for c in celdas)
    assert all(o.output_type != "error" for c in celdas for o in c.outputs)
    assert any(
        o.output_type == "display_data" and "image/png" in o.data for c in celdas for o in c.outputs
    )


def test_figuras_pronostico_son_png_legibles():
    figuras = sorted((RAIZ / "docs/E1/figuras").glob("pronostico_*.png"))
    assert len(figuras) == 7
    for figura in figuras:
        assert figura.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
        with Image.open(figura) as imagen:
            assert imagen.format == "PNG"
            imagen.verify()
