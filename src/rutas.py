"""Planeación local: catálogo público y distancias viales de referencia OSRM-auto."""

from __future__ import annotations

import hashlib
import json
import math
import threading
from pathlib import Path

from extractores.base import ExtractorEtico, ahora_utc

SERVICIO = "https://routing.openstreetmap.de/routed-car/route/v1/driving/"
_cliente = ExtractorEtico(pausa=1.1)
_candado = threading.Lock()


def coordenada(punto: dict) -> tuple[float, float]:
    lat, lon = float(punto["lat"]), float(punto["lon"])
    if not (math.isfinite(lat) and math.isfinite(lon)
            and 18.9 <= lat <= 19.3 and -104.6 <= lon <= -104.0):
        raise ValueError("La ubicación debe pertenecer al área de Manzanillo")
    return lat, lon


def cargar_catalogo(raiz: Path) -> list[dict]:
    puntero = json.loads((raiz / "data/referencias/catalogo_logistico.json").read_text(encoding="utf-8"))
    ruta = (raiz / puntero["archivo_bronce"]).resolve()
    if raiz.resolve() not in ruta.parents:
        raise ValueError("Archivo de catálogo fuera del repositorio")
    contenido = ruta.read_bytes()
    if hashlib.sha256(contenido).hexdigest() != puntero["sha256"]:
        raise ValueError("El catálogo no coincide con su huella de origen")
    documento = json.loads(contenido)
    lugares = documento["lugares"]
    if len(lugares) < 2 or len({r["id_denue"] for r in lugares}) != len(lugares):
        raise ValueError("El catálogo requiere al menos dos ubicaciones distintas")
    for r in lugares:
        coordenada(r)
        if not r["nombre"] or not r["tipo"] or not str(r["id_denue"]).isdigit():
            raise ValueError("Ubicación de catálogo incompleta")
        r.update(url_origen=documento["fuente"], fecha_captura_utc=documento["fecha_captura_utc"],
                 archivo_bronce=puntero["archivo_bronce"], sha256_bronce=puntero["sha256"])
    return lugares


def consultar_ruta(origen: dict, destino: dict, regreso: bool = False) -> dict:
    """Envía solo coordenadas públicas; nunca tarifas, costos ni datos del cliente."""
    a, b = coordenada(origen), coordenada(destino)
    if a == b:
        raise ValueError("Selecciona origen y destino distintos")
    puntos = [a, b, a] if regreso else [a, b]
    coords = ";".join(f"{lon:.7f},{lat:.7f}" for lat, lon in puntos)
    url = SERVICIO + coords
    # Un cliente y un candado por proceso: también limita sesiones concurrentes.
    with _candado:
        respuesta = _cliente.get(url, intentos=1, timeout=(5, 25), params={
            "overview": "full", "geometries": "geojson", "steps": "false",
            "continue_straight": "false", "generate_hints": "false",
        })
    datos = respuesta.json()
    if not isinstance(datos, dict) or datos.get("code") != "Ok" or not datos.get("routes"):
        raise ValueError("El motor no encontró un recorrido de referencia")
    ruta = datos["routes"][0]
    if not isinstance(ruta, dict):
        raise ValueError("Respuesta vial inválida")
    km = float(ruta["distance"]) / 1000
    geometria = ruta["geometry"]
    if not math.isfinite(km) or not 0 < km <= 300 or geometria.get("type") != "LineString":
        raise ValueError("Distancia o geometría vial inválida")
    trazado = geometria["coordinates"]
    if len(trazado) < 2:
        raise ValueError("Recorrido sin trazado")
    for lon, lat in trazado:
        coordenada({"lat": lat, "lon": lon})
    ajustes = [float(x.get("distance", 0)) for x in datos.get("waypoints", [])]
    if any(not math.isfinite(x) or x < 0 for x in ajustes):
        raise ValueError("Ajuste a la red vial inválido")
    return {"distancia_km": km, "coordenadas": trazado, "ajustes_m": ajustes,
            "fecha_consulta_utc": ahora_utc(), "fuente": url,
            "perfil": "OSRM automóvil; no validado para tractocamión", "regreso": regreso}


def costear(distancia_km: float, costo_km: float, adicionales: float,
            horas_espera: float | None = None, costo_hora: float | None = None,
            cobro: float | None = None) -> dict:
    for valor in [distancia_km, costo_km, adicionales, horas_espera, costo_hora, cobro]:
        if valor is not None and (not math.isfinite(valor) or valor < 0):
            raise ValueError("Los importes y distancias deben ser finitos y no negativos")
    if distancia_km <= 0:
        raise ValueError("La distancia debe ser mayor que cero")
    base = distancia_km * costo_km + adicionales
    espera = (horas_espera * costo_hora
              if horas_espera is not None and costo_hora is not None else None)
    total = base + espera if espera is not None else None
    return {"costo_sin_esperas": base, "costo_espera": espera, "costo_con_espera": total,
            "margen_contribucion": cobro - total if cobro is not None and total is not None else None}
