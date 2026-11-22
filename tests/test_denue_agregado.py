"""Agregado DENUE por celda: k-anonimato antes de Bronce, polígonos en Oro y linaje exacto."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from extractores import denue
from src import e2, geoespacial, linaje

RAIZ = Path(__file__).resolve().parents[1]


def fila(**cambios):
    r = {"id": "77", "cve_ent": "06", "cve_mun": "007", "codigo_act": "484121",
         "raz_social": "PERSONA SIN FORMA", "nom_estab": "NOMBRE EXCLUIDO",
         "telefono": "NO_GUARDAR", "latitud": "19.0405", "longitud": "-104.3205"}
    r.update(cambios)
    return r


def filas_prueba():
    misma_celda = [fila(id=str(i)) for i in range(3)] + [fila(id="9", codigo_act="488519")]
    return misma_celda + [
        fila(id="20", latitud="19.1005", longitud="-104.2605"),   # celda con 1: se suprime
        fila(id="30", cve_mun="001"),                               # otro municipio
        fila(id="31", codigo_act="111111"),                         # otra actividad
        fila(id="32", latitud="nan"),                               # coordenada inválida
    ]


def test_agregado_k_anonimato_sin_datos_individuales():
    a = denue.agregar(filas_prueba())
    assert a["k_minimo"] == 3 and a["total_establecimientos"] == 5
    assert len(a["celdas"]) == 1
    celda = a["celdas"][0]
    assert celda["total"] == 4
    assert "por_categoria" not in celda
    assert a["suprimidas"] == {"celdas": 1, "establecimientos": 1}
    texto = json.dumps(a)
    for prohibido in ["NO_GUARDAR", "NOMBRE EXCLUIDO", "PERSONA", "19.0405", "-104.3205"]:
        assert prohibido not in texto
    assert celda["sur"] <= 19.0405 < celda["norte"] and celda["oeste"] <= -104.3205 < celda["este"]


def documento_agregado(celdas):
    return {"url_origen": denue.URL, "fecha_captura_utc": "2026-11-19T19:00:00Z",
            "agregado": {"paso_grados": 0.01, "k_minimo": 3, "celdas": celdas,
                         "suprimidas": {"celdas": 0, "establecimientos": 0},
                         "total_establecimientos": sum(c["total"] for c in celdas)}}


def celda(i=1904, j=-10433, total=3, **cats):
    return {"celda": f"{i}_{j}", "sur": round(i * 0.01, 6), "oeste": round(j * 0.01, 6),
            "norte": round((i + 1) * 0.01, 6), "este": round((j + 1) * 0.01, 6),
            "total": total, **({"por_categoria": cats} if cats else {})}


def test_transformar_agregado_valida_y_rechaza():
    buenas = [celda(), celda(i=1910, j=-10427, total=5)]
    malas = [celda(),                                         # duplicada
             celda(i=1905, total=2),                          # bajo el umbral
             {**celda(i=1906), "norte": 19.20},               # tamaño distinto
             celda(i=1907, total=4, **{"488": 1}),            # categoría bajo el umbral
             {**celda(i=1908), "sur": 19.10, "norte": 19.09}]  # límites invertidos
    poligonos, rechazos = geoespacial.transformar_agregado(
        documento_agregado(buenas + malas), "data/bronce/denue/x.json")
    assert list(poligonos.celda) == ["1904_-10433", "1910_-10427"]
    assert poligonos.crs.to_epsg() == 4326 and poligonos.total.sum() == 8
    assert set(poligonos.zona_estudio) <= {"suroeste", "sureste", "noroeste", "noreste",
                                          "fuera del área de estudio"}
    assert len(rechazos) == 5 and all(r["registro_bronce"].startswith("agregado:") for r in rechazos)


@pytest.fixture(scope="module")
def raiz_agregado(tmp_path_factory):
    """Copia del repo con una captura DENUE que incluye agregado (Bronce nuevo, inmutable)."""
    raiz = tmp_path_factory.mktemp("e2-agregado")
    shutil.copytree(RAIZ / "data/bronce", raiz / "data/bronce")
    shutil.copytree(RAIZ / "data/oro", raiz / "data/oro")
    puntero = raiz / "data/bronce/denue/actual.json"
    actual = json.loads(puntero.read_text(encoding="utf-8"))
    doc = json.loads((raiz / actual["archivo"]).read_text(encoding="utf-8"))
    if "agregado" not in doc:
        doc["agregado"] = denue.agregar(filas_prueba())
    contenido = (json.dumps(doc, ensure_ascii=False, indent=2) + "\n").encode()
    nuevo = "data/bronce/denue/prueba-agregado.json"
    (raiz / nuevo).write_bytes(contenido)
    puntero.write_text(json.dumps({**actual, "archivo": nuevo,
                                   "sha256": hashlib.sha256(contenido).hexdigest()}), encoding="utf-8")
    e2.ejecutar(raiz)
    return raiz


def test_celdas_en_oro_con_linaje_uno_a_uno(raiz_agregado):
    tabla = (raiz_agregado / "data/oro/denue_celdas.csv").read_text(encoding="utf-8")
    assert "id_denue" not in tabla and "NO_GUARDAR" not in tabla
    assert (raiz_agregado / "data/oro/denue_celdas.geojson").exists()
    r = linaje.consultar(raiz_agregado, "data/oro/denue_celdas.csv", 1)
    assert len(r["origenes"]) == 1 and r["grupos"] == []
    origen = r["origenes"][0]
    bruto = json.loads((raiz_agregado / origen["archivo_bronce"]).read_text(encoding="utf-8"))
    assert bruto["agregado"]["celdas"][origen["registro"] - 1]["celda"] == r["clave_negocio"]
    assert origen["fecha_captura_utc"] == bruto["fecha_captura_utc"]
    resumen = json.loads((raiz_agregado / "calidad/e2/geoespacial.json").read_text(encoding="utf-8"))
    assert resumen["agregado"]["establecimientos_en_celdas"] + \
        resumen["agregado"]["establecimientos_suprimidos"] == resumen["agregado"]["total_establecimientos"]


def test_celda_alterada_en_bronce_o_manifiesto_bloquea(raiz_agregado, tmp_path):
    shutil.copytree(raiz_agregado, tmp_path, dirs_exist_ok=True)
    ruta = tmp_path / linaje.MANIFIESTO
    m = json.loads(ruta.read_text(encoding="utf-8"))
    clave = next(k for k, o in m["origenes"].items() if o["fuente"] == "denue_agregado")
    m["origenes"][clave]["id_origen"] = "0_0"
    ruta.write_text(json.dumps(m), encoding="utf-8")
    with pytest.raises(ValueError, match="agregado DENUE no coincide"):
        linaje.validar(tmp_path)


def test_captura_sin_agregado_limpia_celdas_viejas(raiz_agregado, tmp_path):
    shutil.copytree(raiz_agregado, tmp_path, dirs_exist_ok=True)
    puntero = tmp_path / "data/bronce/denue/actual.json"
    actual = json.loads(puntero.read_text(encoding="utf-8"))
    doc = json.loads((tmp_path / actual["archivo"]).read_text(encoding="utf-8"))
    doc.pop("agregado")
    contenido = (json.dumps(doc) + "\n").encode()
    (tmp_path / "data/bronce/denue/sin-agregado.json").write_bytes(contenido)
    puntero.write_text(json.dumps({**actual, "archivo": "data/bronce/denue/sin-agregado.json",
                                   "sha256": hashlib.sha256(contenido).hexdigest()}), encoding="utf-8")
    geoespacial.ejecutar(tmp_path)
    assert not (tmp_path / "data/oro/denue_celdas.csv").exists()


def test_documento_con_individuales_no_se_transforma():
    doc = documento_agregado([celda()])
    doc["elements"] = [{"id_denue": "77", "lat": 19.0405, "lon": -104.3205}]
    with pytest.raises(ValueError, match="detalle individual"):
        geoespacial.transformar_agregado(doc, "captura.json")


def test_sin_celdas_publicables_es_error_claro():
    with pytest.raises(ValueError, match="Ninguna celda"):
        geoespacial.transformar_agregado(documento_agregado([]), "captura.json")


def test_intercambio_de_origenes_validos_no_oculta_error(raiz_agregado, tmp_path):
    shutil.copytree(raiz_agregado, tmp_path, dirs_exist_ok=True)
    ruta = tmp_path / linaje.MANIFIESTO
    m = json.loads(ruta.read_text(encoding="utf-8"))
    filas = m["oro"]["data/oro/denue_celdas.csv"]["registros"]
    filas[0]["origenes_directos"], filas[1]["origenes_directos"] = (
        filas[1]["origenes_directos"], filas[0]["origenes_directos"])
    linaje.guardar(m, ruta)
    with pytest.raises(ValueError, match="Celda Oro no coincide"):
        linaje.validar(tmp_path)


def test_valor_oro_cambiado_con_hash_actualizado_no_pasa(raiz_agregado, tmp_path):
    import csv

    shutil.copytree(raiz_agregado, tmp_path, dirs_exist_ok=True)
    archivo = "data/oro/denue_celdas.csv"
    ruta = tmp_path / archivo
    with ruta.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        campos = reader.fieldnames
        filas = list(reader)
    filas[0]["total"] = str(int(filas[0]["total"]) + 1)
    with ruta.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(filas)
    manifiesto = tmp_path / linaje.MANIFIESTO
    m = json.loads(manifiesto.read_text(encoding="utf-8"))
    m["oro"][archivo]["sha256"] = linaje.hash_archivo(ruta)
    linaje.guardar(m, manifiesto)
    with pytest.raises(ValueError, match="Valores de celda Oro"):
        linaje.validar(tmp_path)
