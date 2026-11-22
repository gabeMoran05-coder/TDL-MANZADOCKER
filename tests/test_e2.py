"""Evidencia E2: privacidad antes de guardar, unión espacial, integridad y economía."""

import io
import json
import shutil
import zipfile
from pathlib import Path

import pytest

from extractores import denue
from src import e2, geoespacial, linaje
from src.negocio import escenario

RAIZ = Path(__file__).resolve().parents[1]


def fila(**cambios):
    r = {"id": "1", "cve_ent": "06", "cve_mun": "007", "codigo_act": "484121",
         "raz_social": "EMPRESA DE PRUEBA SA DE CV", "nom_estab": "NOMBRE EXCLUIDO",
         "telefono": "NO_GUARDAR", "latitud": "19.04", "longitud": "-104.32"}
    r.update(cambios)
    return r


def test_privacidad_antes_de_bronce_y_seleccion():
    datos = [fila(), fila(raz_social="PERSONA FISICA"), fila(cve_mun="001"),
             fila(codigo_act="111111"), fila(latitud="nan"), fila(id="texto")]
    filas, conteos = denue.minimizar(datos)
    assert len(filas) == 1 and conteos["leidos"] == 6
    assert conteos["sin_forma_societaria"] == 1 and conteos["coordenadas_invalidas"] == 2
    assert not {"raz_social", "nom_estab", "telefono", "correoelec", "clee"} & set(filas[0])
    assert "NO_GUARDAR" not in json.dumps(filas)


def documento():
    elementos, _ = denue.minimizar([fila(), fila(id="2", latitud="19.10", longitud="-104.26")])
    return {"elements": elementos, "fecha_captura_utc": "2026-11-17T12:00:00Z"}


def test_union_geografica_bordes_duplicados_y_fuera():
    doc = documento()
    doc["elements"].extend([doc["elements"][0],
        {**doc["elements"][0], "id_denue": "3", "lat": 0},
        {**doc["elements"][0], "id_denue": "4", "lat": 999},
        {**doc["elements"][0], "id_denue": "5", "codigo_actividad": "000000"},
        {**doc["elements"][0], "id_denue": "6", "lat": 19.06, "lon": -104.30}])
    puntos, rechazos = geoespacial.transformar(doc)
    assert len(puntos) == 3 and len(rechazos) == 4
    assert puntos.id_denue.is_unique and puntos.crs.to_epsg() == 4326
    assert set(puntos.zona) >= {"suroeste", "noreste"}
    with pytest.raises(ValueError, match="Ningún establecimiento"):
        geoespacial.transformar({"elements": [{}]})
    with pytest.raises(ValueError, match="Ningún centro"):
        geoespacial.transformar({**doc, "elements": [{**doc["elements"][0], "lat": 0}]})


def zip_prueba(nombre="conjunto_de_datos/denue.csv"):
    memoria = io.BytesIO()
    with zipfile.ZipFile(memoria, "w") as archivo:
        registro = fila()
        import csv

        texto = io.StringIO()
        escritor = csv.DictWriter(texto, fieldnames=list(registro))
        escritor.writeheader()
        for _ in range(3):
            escritor.writerow(registro)
        archivo.writestr(nombre, texto.getvalue().encode("cp1252"))
    return memoria.getvalue()


def test_captura_sin_zip_personal_cache_y_error(tmp_path, monkeypatch):
    class Respuesta:
        content = zip_prueba()

    class Extractor:
        def __init__(self, **kwargs):
            pass

        def get(self, *args, **kwargs):
            return Respuesta()

    monkeypatch.setattr(denue, "ExtractorEtico", Extractor)
    assert denue.ejecutar(tmp_path)["archivos_nuevos"] == 1
    assert denue.ejecutar(tmp_path)["archivos_nuevos"] == 0
    p = tmp_path / "data/bronce/denue/actual.json"
    actual = json.loads(p.read_text())
    contenido = (tmp_path / actual["archivo"]).read_text()
    assert "NO_GUARDAR" not in contenido and "NOMBRE EXCLUIDO" not in contenido
    assert '"elements"' not in contenido and '"id_denue"' not in contenido
    assert '"por_categoria"' not in contenido
    assert not list(tmp_path.rglob("*.zip"))
    Respuesta.content = zip_prueba("otro.csv")
    with pytest.raises(ValueError, match="único CSV"):
        denue.ejecutar(tmp_path, forzar=True)


@pytest.fixture(scope="module")
def base_e2(tmp_path_factory):
    raiz = tmp_path_factory.mktemp("e2-base")
    shutil.copytree(RAIZ / "data/bronce", raiz / "data/bronce")
    shutil.copytree(RAIZ / "data/oro", raiz / "data/oro")
    resumen = e2.ejecutar(raiz)
    assert resumen["linaje"]["cobertura_pct"] == 100
    return raiz


@pytest.fixture()
def copia_e2(base_e2, tmp_path):
    shutil.copytree(base_e2, tmp_path, dirs_exist_ok=True)
    return tmp_path


def test_linaje_hasta_bronce_inalterable_y_reproduccion(copia_e2):
    r = linaje.consultar(copia_e2, "data/oro/denue_celdas.csv", 1)
    assert len(r["origenes"]) == 1
    origen = r["origenes"][0]
    bruto = json.loads((copia_e2 / origen["archivo_bronce"]).read_text())
    assert bruto["agregado"]["celdas"][origen["registro"] - 1]["celda"] == r["clave_negocio"]
    assert origen["fecha_captura_utc"] == bruto["fecha_captura_utc"]
    r2 = linaje.consultar(copia_e2, "data/oro/mensual_integrado.csv", 1)
    assert {o["fuente"] for o in r2["origenes"]} == {"asipona", "banxico"}
    assert all((copia_e2 / o["archivo_bronce"]).exists() for o in r2["origenes"])
    assert e2.ejecutar(copia_e2)["linaje"] == linaje.validar(copia_e2)
    with pytest.raises(ValueError, match="empieza en 1"):
        linaje.consultar(copia_e2, "data/oro/denue_celdas.csv", 0)


@pytest.mark.parametrize("ataque", ["oro", "bronce", "nuevo", "indice", "sin_origen", "fecha", "url", "selector"])
def test_tampering_y_perdida_de_linaje_bloquean(copia_e2, ataque):
    ruta = copia_e2 / linaje.MANIFIESTO
    m = json.loads(ruta.read_text())
    if ataque == "oro":
        with (copia_e2 / "data/oro/denue_celdas.csv").open("a") as f:
            f.write("alterado")
    elif ataque == "bronce":
        archivo = next(iter(m["archivos_bronce"]))
        (copia_e2 / archivo).write_text("alterado")
    elif ataque == "nuevo":
        (copia_e2 / "data/oro/sin_linaje.csv").write_text("valor\n1\n")
    else:
        fila_geo = m["oro"]["data/oro/denue_celdas.csv"]["registros"][0]
        origen = m["origenes"][fila_geo["origenes_directos"][0]]
        if ataque == "indice":
            fila_geo["registro"] = 9999
        elif ataque == "sin_origen":
            fila_geo["origenes_directos"] = []
        elif ataque == "fecha":
            origen["fecha_captura_utc"] = "fecha-invalida"
        elif ataque == "url":
            origen["url_origen"] = "invalida"
        elif ataque == "selector":
            origen["registro"] = 999999
        linaje.guardar(m, ruta)
    with pytest.raises(ValueError):
        linaje.validar(copia_e2)


def test_captura_geografica_alterada_bloquea(copia_e2):
    p = copia_e2 / "data/bronce/denue/actual.json"
    puntero = json.loads(p.read_text())
    puntero["sha256"] = "incorrecto"
    p.write_text(json.dumps(puntero))
    with pytest.raises(ValueError, match="alterada"):
        geoespacial.ejecutar(copia_e2)
    with pytest.raises(ValueError, match="alterada"):
        linaje.generar(copia_e2)


def test_pronostico_no_puede_sellar_entradas_diferentes(copia_e2):
    ruta = copia_e2 / "data/oro/pronostico_metricas.json"
    datos = json.loads(ruta.read_text())
    datos["datos_sha256"] = "otra_version"
    ruta.write_text(json.dumps(datos))
    with pytest.raises(ValueError, match="Pronóstico desactualizado"):
        linaje.generar(copia_e2)


def test_fecha_inventada_en_linaje_no_cambia_la_ingesta(copia_e2):
    ruta = copia_e2 / linaje.MANIFIESTO
    m = json.loads(ruta.read_text())
    next(o for o in m["origenes"].values() if o["fuente"] == "denue_agregado")[
        "fecha_captura_utc"] = "2026-01-01T00:00:00Z"
    linaje.guardar(m, ruta)
    with pytest.raises(ValueError, match="Procedencia del agregado DENUE"):
        linaje.validar(copia_e2)


def test_escenario_economico_no_confunde_teu_y_servicios():
    # Caso sintético de prueba, no resultado de una empresa entrevistada.
    datos = dict(solicitados=100, capacidad=80, tarifa=1000, costo_variable=600,
                 horas_espera=2, costo_hora=100, costos_fijos=1000, suscripcion=500)
    r = escenario(**datos)
    assert r["servicios_atendibles"] == 80 and r["servicios_sin_capacidad"] == 20
    assert r["costo_esperas_estimado"] == 16000
    assert r["margen_contribucion_por_servicio"] == 200
    assert r["resultado_operativo_estimado"] == 14500
    for valor in [-1, float("nan"), float("inf")]:
        with pytest.raises(ValueError):
            escenario(**{**datos, "tarifa": valor})
    with pytest.raises(ValueError):
        escenario(**{**datos, "solicitados": 1.5})
    assert escenario(**{**datos, "costo_variable": 2000})["resultado_operativo_estimado"] < 0
