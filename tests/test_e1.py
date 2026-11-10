"""Pruebas de admisión, trazabilidad, causalidad y reproducción del pipeline."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import pandera.pandas as pa
import pytest

from src.calidad import aplicar_puerta, esquema_asipona
from src.limpieza import ejecutar, normalizar, sha256
from src.preprocesamiento import ajustar, escalar, imputar_causal, marcar_atipicos

RAIZ = Path(__file__).resolve().parents[1]


def registro_asipona(**cambios):
    fila = {
        "anio": "2026",
        "mes": "1",
        "variable": "teu_total",
        "valor": "300000",
        "publicado": "True",
        "mes_reporte": "10",
        "acumulado_reportado": "300000",
        "suma_meses": "300000",
        "cuadra": "True",
        "diferencia": "0",
        "archivo_origen": "data/bronce/asipona/pdf/2026/EM-2026-10.pdf",
        "url_origen": "https://www.puertomanzanillo.com.mx/EM-2026-10.pdf",
        "fecha_captura_utc": "2026-11-09T19:03:52Z",
    }
    fila.update(cambios)
    return fila


@pytest.mark.parametrize(
    "cambios",
    [
        {"valor": "-1"},
        {"valor": "inf"},
        {"valor": "texto"},
        {"valor": ""},
        {"valor": "9000000"},
        {"mes": "13"},
        {"mes": "1.5"},
        {"anio": "incorrecto"},
        {"diferencia": "3"},
        {"variable": "inventada"},
        {"publicado": "tal_vez"},
        {"fecha_captura_utc": "2026-99-09T19:03:52Z"},
        {"url_origen": "archivo-local"},
    ],
)
def test_filas_invalidas_quedan_trazadas(cambios):
    raw = registro_asipona(**cambios)
    buenos, _, malos = normalizar(pd.DataFrame([raw]), "asipona")
    assert buenos.empty
    assert len(malos) == 1
    assert malos[0]["motivo"]
    assert json.loads(malos[0]["registro_original_json"]) == raw


def test_no_publicado_no_se_interpreta_como_cero():
    buenos, _, malos = normalizar(
        pd.DataFrame([registro_asipona(mes="11", publicado="False", valor="0")]), "asipona"
    )
    assert buenos.empty
    assert "periodo_no_publicado" in malos[0]["motivo"]


def test_duplicados_se_aislan_completos():
    raw = registro_asipona()
    buenos, _, malos = normalizar(pd.DataFrame([raw, raw]), "asipona")
    assert buenos.empty and len(malos) == 2
    assert {r["id_origen"] for r in malos} == {"asipona:2", "asipona:3"}


@pytest.mark.parametrize("modificacion", ["agregar", "quitar"])
def test_cambio_de_esquema_rechaza_lote(modificacion):
    raw = pd.DataFrame([registro_asipona()])
    if modificacion == "agregar":
        raw["sorpresa"] = "no ignorar"
    else:
        raw = raw.drop(columns="cuadra")
    buenos, _, malos = normalizar(raw, "asipona")
    assert buenos.empty and len(malos) == 1
    assert "esquema_bronce" in malos[0]["motivo"]


def test_pandera_estricto_no_silencia_columnas_extras():
    buenos, originales, _ = normalizar(pd.DataFrame([registro_asipona()]), "asipona")
    buenos["inesperada"] = 1.0
    aceptados, malos = aplicar_puerta(buenos, esquema_asipona(), "asipona", originales)
    assert aceptados.empty and len(malos) == 1
    assert "inesperada" in malos[0]["registro_normalizado_json"]


def test_recalculo_del_acumulado_no_confia_en_bandera_cuadra():
    filas = [
        registro_asipona(
            mes=str(m), mes_reporte="12", acumulado_reportado="3600000", suma_meses="3600000"
        )
        for m in range(1, 13)
    ]
    filas[0]["valor"] = "300001"
    buenos, _, malos = normalizar(pd.DataFrame(filas), "asipona")
    assert buenos.empty and len(malos) == 12
    assert all("conflicto_suma_mensual" in r["motivo"] for r in malos)


@pytest.mark.parametrize(
    "cambios",
    [
        {"valor": "", "valor_crudo": "N/E"},
        {"valor": "20", "valor_crudo": "21"},
        {"valor": "-5", "valor_crudo": "-5"},
        {"fecha": "2026-02-30"},
        {"serie": "otra"},
    ],
)
def test_conflictos_banxico(cambios):
    raw = {
        "fecha": "2026-01-05",
        "serie": "SF43718",
        "valor": "20",
        "valor_crudo": "20.0000",
        "url_origen": "https://www.banxico.org.mx/SieAPIRest/serie",
        "fecha_captura_utc": "2026-11-09T19:03:52Z",
    }
    raw.update(cambios)
    buenos, _, malos = normalizar(pd.DataFrame([raw]), "banxico")
    assert buenos.empty and len(malos) == 1


def test_imputacion_no_mira_futuro_ni_reutiliza_imputados():
    datos = pd.DataFrame(
        {
            "fecha": pd.date_range("2021-07-01", periods=6, freq="MS"),
            "variable": "teu_ssa",
            "valor": [10.0, 30.0, 20.0, np.nan, np.nan, 900.0],
            "imputado": False,
            "metodo_imputacion": "observado",
        }
    )
    resultado = imputar_causal(datos)
    assert resultado.valor.tolist() == [10.0, 30.0, 20.0, 20.0, 20.0, 900.0]
    assert resultado.imputado.sum() == 2
    assert datos.valor.isna().sum() == 2


def test_imputacion_no_se_contamina_por_registro_invalido():
    raw = [
        registro_asipona(mes=str(m), variable="teu_ssa", valor=v)
        for m, v in [(1, "10"), (2, "999999999"), (3, "")]
    ]
    buenos, _, malos = normalizar(pd.DataFrame(raw), "asipona")
    assert len(malos) == 1
    assert buenos.loc[buenos.fecha.dt.month.eq(3), "valor"].iloc[0] == 10


def test_atipicos_conservados_y_ajuste_sin_prueba():
    datos = pd.DataFrame(
        {
            "fecha": pd.date_range("2025-01-01", periods=5, freq="MS"),
            "variable": "teu_total",
            "valor": [10.0, 11.0, 12.0, 13.0, 1000.0],
            "es_atipico_iqr": False,
            "es_atipico_robusto": False,
        }
    )
    resultado, p = marcar_atipicos(datos, pd.Timestamp("2025-04-01"))
    assert len(resultado) == 5 and resultado.iloc[-1].valor == 1000
    assert resultado.iloc[-1].es_atipico_iqr
    assert p["teu_total"]["max"] == 13


def test_escalas_y_variable_constante():
    p = ajustar(pd.Series([1.0, 2.0, 3.0]))
    minmax, z = escalar(pd.Series([1.0, 2.0, 3.0, 5.0]), p)
    assert minmax.tolist() == [0.0, 0.5, 1.0, 2.0]
    assert z.iloc[:3].mean() == pytest.approx(0)
    p_constante = ajustar(pd.Series([5.0, 5.0]))
    mm, zz = escalar(pd.Series([5.0, 5.0]), p_constante)
    assert mm.eq(0).all() and zz.eq(0).all()
    with pytest.raises(ValueError):
        ajustar(pd.Series([], dtype=float))


@pytest.fixture()
def copia_bronce(tmp_path):
    shutil.copytree(RAIZ / "data/bronce", tmp_path / "data/bronce")
    return tmp_path


def test_pipeline_real_reproducible_y_conserva_bronce(copia_bronce):
    raiz = copia_bronce
    archivos = list((raiz / "data/bronce").rglob("*"))
    antes = {str(p): sha256(p) for p in archivos if p.is_file()}
    resumen = ejecutar(raiz)
    assert resumen["meses_oro"] >= 70
    assert resumen["meses_prueba"] == 6
    assert resumen["asipona"]["imputados"] == 8
    for fuente in ["asipona", "banxico"]:
        s = resumen[fuente]
        assert s["entrada"] == s["aceptados"] + s["rechazados"]
    oro = pd.read_csv(raiz / "data/oro/mensual_integrado.csv")
    assert not oro.isna().any().any()
    assert oro.fecha.is_unique
    assert set(oro.actividad) == {"baja", "media", "alta"}
    assert oro[["pais", "estado", "puerto", "anio", "trimestre", "mes"]].notna().all().all()
    parquet = pd.read_parquet(raiz / "data/oro/mensual_integrado.parquet")
    assert len(parquet) == len(oro)
    productos = list((raiz / "data/plata").glob("*")) + list((raiz / "data/oro").glob("*"))
    hashes = {p: sha256(p) for p in productos}
    assert ejecutar(raiz) == resumen
    assert hashes == {p: sha256(p) for p in productos}
    assert antes == {str(p): sha256(p) for p in archivos if p.is_file()}
    cuarentena = pd.read_csv(raiz / "data/cuarentena/e1/asipona.csv")
    assert len(cuarentena) == resumen["asipona"]["rechazados"]
    assert cuarentena.motivo.notna().all()


def test_ruptura_de_serie_bloquea_publicacion_y_deja_bitacora(copia_bronce):
    ruta = copia_bronce / "data/bronce/asipona/em_mensual.csv"
    datos = pd.read_csv(ruta)
    datos.loc[datos.variable.eq("teu_total") & datos.anio.eq(2022) & datos.mes.eq(3), "valor"] = -1
    datos.to_csv(ruta, index=False)
    with pytest.raises(ValueError, match="consecutivos"):
        ejecutar(copia_bronce)
    assert not (copia_bronce / "data/plata/asipona_mensual.csv").exists()
    resumen = json.loads((copia_bronce / "calidad/e1/resumen.json").read_text(encoding="utf-8"))
    assert resumen["estado"] == "falla"
    malos = pd.read_csv(copia_bronce / "data/cuarentena/e1/asipona.csv")
    assert malos.registro_original_json.str.contains('"valor": "-1.0"').any()


def test_contrato_oro_estricto():
    from src.limpieza import esquema_oro

    with pytest.raises(pa.errors.SchemaErrors):
        esquema_oro().validate(pd.DataFrame({"inesperada": [1.0]}), lazy=True)


def test_fuente_ausente_registra_error_sin_publicar(tmp_path):
    with pytest.raises(FileNotFoundError):
        ejecutar(tmp_path)
    resumen = json.loads((tmp_path / "calidad/e1/resumen.json").read_text(encoding="utf-8"))
    assert resumen["estado"] == "falla"
    assert (tmp_path / "calidad/bitacora_pipeline.csv").exists()
    assert not (tmp_path / "data/plata/asipona_mensual.csv").exists()
