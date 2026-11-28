"""Tabla de TEU por terminal y tráfico: lectura, validación, linaje y MANOVA."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import pandas as pd
import pytest

from src import terminales_trafico as tt

RAIZ = Path(__file__).resolve().parents[1]

TEXTO = """MOVIMIENTO DE TEU'S POR EMPRESA
SSA 1 2 3
MOVIMIENTO DE TEU'S POR EMPRESA POR TRÁFICO
TEU'S TEU'S TEU'S TEU'S TEU'S
TOTAL IMPO EXPO CABOTAJE TRANSBORDO
EMPRESA % Var % Var % Var % Var % Var
2025 2024 2025 2024 2025 2024 2025 2024 2025 2024
SSA 1,000 900 11.1% 400 300 33.3% 350 350 0.0% 0 0 - 250 250 0.0%
CONTECON 800 700 14.3% 300 300 0.0% 300 250 20.0% 0 0 - 200 150 33.3%
OCUPA 300 200 50.0% 100 80 25.0% 190 110 72.7% 0 0 - 10 10 0.0%
TIMSA 200 100 -0.1 90 50 -0.0 80 30 -0.1 0 0 - 30 20 -0.0
TOTAL 2,300 1,900 21.1% 890 730 21.9% 920 740 24.3% 0 0 - 490 430 14.0%
NOTAS: No se incluye el peso de la tara de los contenedores.
"""


def test_lee_tabla_y_omite_encabezado_total():
    tabla = tt.leer_tabla(TEXTO)
    assert tabla["SSA"]["importacion"] == (400, 300)
    assert tabla["TIMSA"]["transbordo"] == (30, 20)   # % sin signo (formato 2024)
    assert tabla["TOTAL"]["total"] == (2300, 1900)
    assert tt.validar_tabla(tabla) == []


def test_redondeo_pequeno_se_documenta_y_grande_bloquea():
    tabla = tt.leer_tabla(TEXTO.replace("TOTAL 2,300", "TOTAL 2,301"))
    difs = tt.validar_tabla(tabla)
    assert difs and all(abs(d["diferencia"]) <= tt.TOLERANCIA_TEU for d in difs)
    with pytest.raises(ValueError, match="no cuadra"):
        tt.validar_tabla(tt.leer_tabla(TEXTO.replace("SSA 1,000 900", "SSA 1,100 900")))


def test_tabla_ausente_o_incompleta_es_error_claro():
    with pytest.raises(ValueError, match="no contiene"):
        tt.leer_tabla("otra cosa")
    with pytest.raises(ValueError, match="Faltan filas"):
        tt.leer_tabla(TEXTO.replace("OCUPA", "XXX"))
    with pytest.raises(ValueError, match="columnas"):
        tt.leer_tabla(TEXTO.replace("SSA 1,000 900 11.1%", "SSA 1,000 900"))


def _raiz_falsa(tmp_path: Path, textos: dict[str, str]) -> Path:
    filas = []
    for i, (archivo, texto) in enumerate(textos.items()):
        ruta = tmp_path / archivo
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(texto, encoding="utf-8")
        anio, mes = archivo.split("EM-")[1].removesuffix(".pdf").split("-")
        filas.append({"fecha_captura_utc": f"2026-11-0{i + 1}T00:00:00Z", "anio": anio,
                      "mes_reporte": int(mes), "url": f"https://ejemplo.mx/{i}.pdf",
                      "archivo": archivo, "bytes": len(texto),
                      "sha256": hashlib.sha256(ruta.read_bytes()).hexdigest(), "http_status": 200})
    captura = tmp_path / tt.CAPTURAS
    captura.parent.mkdir(parents=True, exist_ok=True)
    with captura.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    return tmp_path


def _leer(ruta: Path) -> str:
    return ruta.read_text(encoding="utf-8")


def _tabla(anio: int, actual: dict, anterior: dict) -> str:
    """Texto de EM con tabla por tráfico que cuadra; valores = (impo, expo, transbordo)."""
    def celdas(v):
        i, e, tr = v
        return [i + e + tr, i, e, 0, tr]
    lineas = ["MOVIMIENTO DE TEU'S POR EMPRESA POR TRÁFICO",
              "TOTAL IMPO EXPO CABOTAJE TRANSBORDO", f"{anio} {anio - 1}"]
    tot_a, tot_b = [0] * 5, [0] * 5
    for e in tt.TERMINALES:
        a, b = celdas(actual[e]), celdas(anterior[e])
        tot_a = [x + y for x, y in zip(tot_a, a)]
        tot_b = [x + y for x, y in zip(tot_b, b)]
        lineas.append(e + " " + " ".join(f"{x:,} {y:,} 0.0%" for x, y in zip(a, b)))
    lineas.append("TOTAL " + " ".join(f"{x:,} {y:,} 0.0%" for x, y in zip(tot_a, tot_b)))
    lineas.append("NOTAS: fin")
    return "\n".join(lineas)


V23 = {e: (100 + k, 90 + k, 10 + k) for k, e in enumerate(tt.TERMINALES)}
V24 = {e: (200 + k, 150 + k, 20 + k) for k, e in enumerate(tt.TERMINALES)}
V25 = {e: (300 + k, 250 + k, 30 + k) for k, e in enumerate(tt.TERMINALES)}


def test_construir_usa_ultimo_em_agrega_anio_previo_y_cruza(tmp_path):
    raiz = _raiz_falsa(tmp_path, {
        "data/bronce/asipona/pdf/2025/EM-2025-09.pdf": _tabla(2025, V24, V23),
        "data/bronce/asipona/pdf/2025/EM-2025-12.pdf": _tabla(2025, V25, V24),
        "data/bronce/asipona/pdf/2024/EM-2024-12.pdf": _tabla(2024, V24, V23),
    })
    filas, resumen = tt.construir(raiz, leer_pdf=_leer)
    anios = sorted({(f["anio"], f["columna_pdf"], f["meses"]) for f in filas})
    assert anios == [(2023, "anterior", 12), (2024, "actual", 12), (2025, "actual", 12)]
    assert all(f["archivo_origen"].endswith("EM-2025-12.pdf") for f in filas if f["anio"] == 2025)
    ssa = next(f for f in filas if f["anio"] == 2025 and f["terminal"] == "SSA")
    assert (ssa["teu_importacion"], ssa["teu_transbordo"], ssa["teu_total"]) == (300, 30, 580)
    # 2024 según el EM 2025 coincide con el EM 2024: 4 comparaciones sin diferencias
    assert resumen["verificacion_cruzada"]["comparaciones"] == 4
    assert resumen["verificacion_cruzada"]["con_diferencias"] == []
    assert resumen["redondeos_aceptados"] == []


def test_verificacion_cruzada_detecta_revision_de_asipona(tmp_path):
    revisado = {**V24, "SSA": (V24["SSA"][0] - 10, V24["SSA"][1], V24["SSA"][2] + 10)}
    raiz = _raiz_falsa(tmp_path, {
        "data/bronce/asipona/pdf/2025/EM-2025-12.pdf": _tabla(2025, V25, revisado),
        "data/bronce/asipona/pdf/2024/EM-2024-12.pdf": _tabla(2024, V24, V23),
    })
    _, resumen = tt.construir(raiz, leer_pdf=_leer)
    assert resumen["verificacion_cruzada"]["con_diferencias"] == [
        {"anio": 2024, "terminal": "SSA", "diferencias": {"importacion": 10, "transbordo": -10}}]


def test_pdf_alterado_bloquea(tmp_path):
    raiz = _raiz_falsa(tmp_path, {"data/bronce/asipona/pdf/2025/EM-2025-12.pdf": TEXTO})
    (raiz / "data/bronce/asipona/pdf/2025/EM-2025-12.pdf").write_text(TEXTO + "x", encoding="utf-8")
    with pytest.raises(ValueError, match="alterado"):
        tt.construir(raiz, leer_pdf=_leer)


def test_ejecutar_escribe_plata_y_resumen(tmp_path):
    raiz = _raiz_falsa(tmp_path, {"data/bronce/asipona/pdf/2025/EM-2025-12.pdf": TEXTO})
    resumen = tt.ejecutar(raiz, leer_pdf=_leer)
    datos = pd.read_csv(raiz / tt.SALIDA)
    assert len(datos) == 8 and set(datos.columna_pdf) == {"actual", "anterior"}
    assert resumen["sha256_salida"] == hashlib.sha256((raiz / tt.SALIDA).read_bytes()).hexdigest()
    assert (raiz / tt.RESUMEN).exists()


def test_plata_versionada_cuadra_con_su_resumen():
    """El CSV versionado es el que describe calidad/e3/terminal_trafico.json."""
    import json
    resumen = json.loads((RAIZ / tt.RESUMEN).read_text(encoding="utf-8"))
    datos = pd.read_csv(RAIZ / tt.SALIDA)
    assert hashlib.sha256((RAIZ / tt.SALIDA).read_bytes()).hexdigest() == resumen["sha256_salida"]
    assert len(datos) == resumen["filas"] == 28
    partes = datos[["teu_importacion", "teu_exportacion", "teu_cabotaje", "teu_transbordo"]].sum(axis=1)
    assert ((partes - datos.teu_total).abs() <= tt.TOLERANCIA_TEU).all()


def test_manova_manual_coincide_con_statsmodels():
    from statsmodels.multivariate.manova import MANOVA

    from scripts import manova_e3

    d = manova_e3.preparar(pd.read_csv(RAIZ / tt.SALIDA))
    propio = manova_e3.estadisticos(d)
    tabla = MANOVA.from_formula(" + ".join(manova_e3.RESPUESTAS) + " ~ C(terminal) + C(anio)",
                                data=d).mv_test().results["C(terminal)"]["stat"]
    assert propio["wilks"] == pytest.approx(tabla.loc["Wilks' lambda", "Value"], rel=1e-8)
    assert propio["pillai"] == pytest.approx(tabla.loc["Pillai's trace", "Value"], rel=1e-8)
    corto = manova_e3.permutacion(d, n=19, semilla=1)
    assert 0 < corto["p_pillai"] <= 1 and corto["permutaciones"] == 19
