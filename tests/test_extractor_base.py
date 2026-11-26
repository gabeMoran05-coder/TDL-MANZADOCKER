"""ExtractorEtico reintenta ante conexiones cortadas, igual que ante 429/5xx."""

from __future__ import annotations

import pytest
import requests

from extractores import base


class Respuesta:
    status_code = 200

    def raise_for_status(self):
        return None


def extractor(monkeypatch, errores):
    e = base.ExtractorEtico(pausa=0)
    e.robots["https://ejemplo.mx"] = type("Reglas", (), {
        "can_fetch": lambda *a: True, "crawl_delay": lambda *a: 0})()
    llamadas = []

    def get(url, **kwargs):
        llamadas.append(url)
        if errores:
            raise errores.pop(0)
        return Respuesta()

    monkeypatch.setattr(e.sesion, "get", get)
    monkeypatch.setattr(base.time, "sleep", lambda s: None)
    return e, llamadas


def test_reintenta_conexion_cortada_y_luego_responde(monkeypatch):
    cortada = requests.exceptions.ChunkedEncodingError("Connection broken: 10054")
    e, llamadas = extractor(monkeypatch, [cortada, requests.ConnectionError("reset")])
    assert e.get("https://ejemplo.mx/a.zip", intentos=3).status_code == 200
    assert len(llamadas) == 3


def test_falla_clara_si_la_conexion_no_se_recupera(monkeypatch):
    errores = [requests.Timeout("lento") for _ in range(3)]
    e, llamadas = extractor(monkeypatch, errores)
    with pytest.raises(RuntimeError, match="tras 3 intentos: Timeout"):
        e.get("https://ejemplo.mx/a.zip", intentos=3)
    assert len(llamadas) == 3


@pytest.mark.parametrize(('codigo', 'permitido'), [(429, False), (404, True), (503, False)])
def test_respuesta_robots_no_convierte_saturacion_en_permiso(monkeypatch, codigo, permitido):
    e = base.ExtractorEtico(pausa=0)
    llamadas = []

    class RespuestaRobots:
        status_code = codigo

    def get(url, **kwargs):
        llamadas.append(url)
        return RespuestaRobots()

    monkeypatch.setattr(e.sesion, 'get', get)
    assert e.permitido('https://ejemplo.mx/datos') is permitido
    if not permitido:
        with pytest.raises(PermissionError):
            e.get('https://ejemplo.mx/datos')
        assert llamadas == ['https://ejemplo.mx/robots.txt']
