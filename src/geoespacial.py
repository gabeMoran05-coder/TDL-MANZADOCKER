"""GeoPandas: unión de establecimientos DENUE con cuatro celdas de estudio."""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import box

from extractores.base import sha256
from extractores.denue import CATEGORIAS, URL

BBOX = (18.99, -104.36, 19.13, -104.24)  # sur, oeste, norte, este; no límite oficial


def zonas() -> gpd.GeoDataFrame:
    sur, oeste, norte, este = BBOX
    x, y = (oeste + este) / 2, (sur + norte) / 2
    return gpd.GeoDataFrame({
        "zona": ["suroeste", "sureste", "noroeste", "noreste"],
        "geometry": [box(oeste, sur, x, y), box(x, sur, este, y),
                     box(oeste, y, x, norte), box(x, y, este, norte)],
    }, crs="EPSG:4326")


def transformar(documento: dict) -> tuple[gpd.GeoDataFrame, list[dict]]:
    filas, rechazos, vistos = [], [], set()
    for i, r in enumerate(documento["elements"], start=1):
        try:
            identificador = str(r["id_denue"])
            lat, lon = float(r["lat"]), float(r["lon"])
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                raise ValueError("coordenadas fuera de rango")
            if identificador in vistos:
                raise ValueError("establecimiento DENUE duplicado")
            actividad = str(r["codigo_actividad"])
            if not identificador.isdigit() or len(actividad) != 6 or actividad[:3] not in CATEGORIAS:
                raise ValueError("identificador o actividad fuera del contrato")
            vistos.add(identificador)
            filas.append({
                "id_denue": identificador, "registro_bronce": i, "lat": lat, "lon": lon,
                "codigo_actividad": actividad, "categoria": CATEGORIAS[actividad[:3]],
                "puerto": "Manzanillo", "url_origen": URL,
                "fecha_captura_utc": documento["fecha_captura_utc"],
            })
        except (ValueError, TypeError, KeyError) as error:
            rechazos.append({"registro_bronce": i, "motivo": str(error)})
    if not filas:
        raise ValueError("Ningún establecimiento DENUE válido")
    puntos = gpd.GeoDataFrame(filas, geometry=gpd.points_from_xy(
        [r["lon"] for r in filas], [r["lat"] for r in filas]), crs="EPSG:4326")
    # intersects incluye bordes. Los empates se resuelven por orden alfabético, sin duplicar.
    union = gpd.sjoin(puntos, zonas(), how="left", predicate="intersects")
    union = union.sort_values(["id_denue", "zona"]).drop_duplicates("id_denue")
    fuera = union.zona.isna()
    rechazos.extend({"registro_bronce": int(r.registro_bronce),
                     "motivo": "centro fuera del área de estudio"}
                    for r in union.loc[fuera].itertuples())
    union = union.loc[~fuera].drop(columns="index_right").reset_index(drop=True)
    if union.empty:
        raise ValueError("Ningún centro cae en el área de estudio")
    return union, rechazos


def ejecutar(raiz: Path) -> dict:
    puntero = json.loads((raiz / "data/bronce/denue/actual.json").read_text(encoding="utf-8"))
    ruta = raiz / puntero["archivo"]
    if sha256(ruta.read_bytes()) != puntero["sha256"]:
        raise ValueError("La captura DENUE fue alterada")
    documento = json.loads(ruta.read_text(encoding="utf-8"))
    puntos, rechazos = transformar(documento)
    for carpeta in ["data/plata", "data/oro", "data/cuarentena/e2", "calidad/e2"]:
        (raiz / carpeta).mkdir(parents=True, exist_ok=True)
    tabla = pd.DataFrame(puntos.drop(columns="geometry"))
    tabla["archivo_bronce"] = puntero["archivo"]
    tabla.to_csv(raiz / "data/plata/denue_establecimientos.csv", index=False, lineterminator="\n")
    tabla.to_csv(raiz / "data/oro/contexto_geografico.csv", index=False, lineterminator="\n")
    puntos.to_file(raiz / "data/oro/contexto_geografico.geojson", driver="GeoJSON")
    pd.DataFrame(rechazos, columns=["registro_bronce", "motivo"]).to_csv(
        raiz / "data/cuarentena/e2/denue.csv", index=False, lineterminator="\n")
    resumen = {
        "estado": "ok", "archivo_bronce": puntero["archivo"],
        "sha256_bronce": puntero["sha256"], "fecha_captura_utc": documento["fecha_captura_utc"],
        "entrada": len(documento["elements"]), "aceptados": len(puntos),
        "rechazados": len(rechazos), "por_zona": puntos.zona.value_counts().to_dict(),
        "crs": "EPSG:4326", "union": "geopandas.sjoin, intersects, celdas de estudio",
    }
    (raiz / "calidad/e2/geoespacial.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return resumen
