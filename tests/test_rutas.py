"""Rutas de referencia, origen verificable y separación de costos de espera."""

import json
from pathlib import Path

import pytest

from src import rutas

RAIZ = Path(__file__).resolve().parents[1]
A = {"lat": 19.05953084, "lon": -104.30166032}
B = {"lat": 19.0763764, "lon": -104.28213144}


def test_catalogo_publico_trazado_y_alteracion(tmp_path):
    catalogo = rutas.cargar_catalogo(RAIZ)
    assert len(catalogo) == 5 and all(r["id_denue"].isdigit() for r in catalogo)
    assert all(r["fecha_captura_utc"] and r["registro_csv_origen"] for r in catalogo)
    assert all(not ({"telefono", "correoelec", "representante", "domicilio"} & set(r)) for r in catalogo)
    (tmp_path / "data/referencias").mkdir(parents=True)
    puntero = json.loads((RAIZ / "data/referencias/catalogo_logistico.json").read_text())
    puntero["archivo_bronce"] = "../../archivo-ajeno"
    (tmp_path / "data/referencias/catalogo_logistico.json").write_text(json.dumps(puntero))
    with pytest.raises(ValueError, match="fuera"):
        rutas.cargar_catalogo(tmp_path)


def test_ruta_ida_y_regreso_se_consulta_completo(monkeypatch):
    urls = []

    class Respuesta:
        def json(self):
            return {"code": "Ok", "routes": [{"distance": 4693,
                "geometry": {"type": "LineString", "coordinates": [[A["lon"], A["lat"]],
                    [B["lon"], B["lat"]]]}}], "waypoints": [{"distance": 5}]}

    def get(url, **kwargs):
        urls.append(url)
        assert kwargs["params"]["geometries"] == "geojson"
        assert kwargs["intentos"] == 1
        return Respuesta()

    monkeypatch.setattr(rutas._cliente, "get", get)
    assert rutas.consultar_ruta(A, B)["distancia_km"] == pytest.approx(4.693)
    r = rutas.consultar_ruta(A, B, regreso=True)
    assert r["regreso"] and urls[-1].count(";") == 2
    assert "4693" not in urls[-1]  # no se envían resultados económicos
    assert r["fecha_consulta_utc"] and "automóvil" in r["perfil"]
    with pytest.raises(ValueError, match="distintos"):
        rutas.consultar_ruta(A, A)
    with pytest.raises(ValueError, match="Manzanillo"):
        rutas.consultar_ruta({"lat": 0, "lon": 0}, B)


@pytest.mark.parametrize("respuesta", [
    {"code": "NoRoute"}, {"code": "Ok", "routes": []},
    {"code": "Ok", "routes": [{"distance": -1, "geometry": {"type": "Point"}}]},
    {"code": "Ok", "routes": [{"distance": 100, "geometry": {"type": "LineString", "coordinates": []}}]},
])
def test_motor_invalido_no_genera_distancia(respuesta, monkeypatch):
    class Respuesta:
        def json(self):
            return respuesta
    monkeypatch.setattr(rutas._cliente, "get", lambda *a, **k: Respuesta())
    with pytest.raises(ValueError):
        rutas.consultar_ruta(A, B)


def test_costo_sin_esperas_y_campos_incompletos():
    r = rutas.costear(10, 20, 50, 2, 100, 1000)
    assert r == {"costo_sin_esperas": 250, "costo_espera": 200,
                 "costo_con_espera": 450, "margen_contribucion": 550}
    r = rutas.costear(10, 20, 50)
    assert r["costo_sin_esperas"] == 250 and r["costo_con_espera"] is None
    assert r["margen_contribucion"] is None
    for distancia in [0, -1, float("nan"), float("inf")]:
        with pytest.raises(ValueError):
            rutas.costear(distancia, 20, 0)
