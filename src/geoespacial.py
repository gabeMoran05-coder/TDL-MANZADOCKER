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


COLUMNAS_CELDAS = ["celda", "registro_bronce", "sur", "oeste", "norte", "este", "lat", "lon",
                   "total", *[f"scian_{c}" for c in CATEGORIAS], "zona_estudio",
                   "paso_grados", "k_minimo", "url_origen", "fecha_captura_utc", "archivo_bronce"]


def transformar_agregado(documento: dict, archivo_bronce: str) -> tuple[gpd.GeoDataFrame, list[dict]]:
    """Valida los conteos por celda y los convierte en polígonos con su zona de estudio."""
    agregado = documento["agregado"]
    k, paso = agregado["k_minimo"], agregado["paso_grados"]
    filas, rechazos, vistas = [], [], set()
    for i, c in enumerate(agregado["celdas"], start=1):
        try:
            if c["celda"] in vistas:
                raise ValueError("celda duplicada")
            if not (c["sur"] < c["norte"] and c["oeste"] < c["este"]):
                raise ValueError("celda con límites inválidos")
            if abs((c["norte"] - c["sur"]) - paso) > 1e-9 or abs((c["este"] - c["oeste"]) - paso) > 1e-9:
                raise ValueError("celda de tamaño distinto al paso declarado")
            if c["total"] < k:
                raise ValueError("celda bajo el umbral de anonimato publicada")
            conocidos = [n for n in c["por_categoria"].values() if n is not None]
            if any(0 < n < k for n in conocidos) or sum(conocidos) > c["total"]:
                raise ValueError("conteo por categoría incoherente o bajo el umbral")
            vistas.add(c["celda"])
            filas.append({
                "celda": c["celda"], "registro_bronce": i,
                "sur": c["sur"], "oeste": c["oeste"], "norte": c["norte"], "este": c["este"],
                "lat": round((c["sur"] + c["norte"]) / 2, 6),
                "lon": round((c["oeste"] + c["este"]) / 2, 6), "total": int(c["total"]),
                **{f"scian_{cat}": c["por_categoria"].get(cat) for cat in CATEGORIAS},
                "paso_grados": paso, "k_minimo": k, "url_origen": documento["url_origen"],
                "fecha_captura_utc": documento["fecha_captura_utc"],
                "archivo_bronce": archivo_bronce,
            })
        except (ValueError, TypeError, KeyError) as error:
            rechazos.append({"registro_bronce": f"agregado:{i}", "motivo": str(error)})
    poligonos = gpd.GeoDataFrame(
        filas, geometry=[box(f["oeste"], f["sur"], f["este"], f["norte"]) for f in filas],
        crs="EPSG:4326")
    # Zona de estudio por el centro de la celda (puntos): cada celda recibe a lo más una.
    centros = gpd.GeoDataFrame(poligonos[["celda"]], crs="EPSG:4326",
                               geometry=gpd.points_from_xy(poligonos.lon, poligonos.lat))
    zona = (gpd.sjoin(centros, zonas(), how="left", predicate="intersects")
            .sort_values(["celda", "zona"]).drop_duplicates("celda").set_index("celda").zona)
    poligonos["zona_estudio"] = poligonos.celda.map(zona).fillna("fuera del área de estudio")
    return poligonos, rechazos


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
    agregado = {}
    if "agregado" in documento:
        celdas, rechazos_celdas = transformar_agregado(documento, puntero["archivo"])
        tabla_celdas = pd.DataFrame(celdas.drop(columns="geometry"))[COLUMNAS_CELDAS]
        tabla_celdas.to_csv(raiz / "data/plata/denue_celdas.csv", index=False, lineterminator="\n")
        tabla_celdas.to_csv(raiz / "data/oro/denue_celdas.csv", index=False, lineterminator="\n")
        celdas[COLUMNAS_CELDAS + ["geometry"]].to_file(
            raiz / "data/oro/denue_celdas.geojson", driver="GeoJSON")
        rechazos.extend(rechazos_celdas)
        pd.DataFrame(rechazos, columns=["registro_bronce", "motivo"]).to_csv(
            raiz / "data/cuarentena/e2/denue.csv", index=False, lineterminator="\n")
        sup = documento["agregado"]["suprimidas"]
        agregado = {
            "celdas_publicadas": len(celdas), "celdas_rechazadas": len(rechazos_celdas),
            "establecimientos_en_celdas": int(celdas.total.sum()),
            "celdas_suprimidas": sup["celdas"], "establecimientos_suprimidos": sup["establecimientos"],
            "total_establecimientos": documento["agregado"]["total_establecimientos"],
            "k_minimo": documento["agregado"]["k_minimo"],
            "paso_grados": documento["agregado"]["paso_grados"],
            "por_zona_estudio": celdas.groupby("zona_estudio").total.sum().astype(int).to_dict(),
        }
    else:  # captura anterior sin agregado: no dejar celdas de otra captura en Oro
        for viejo in ["data/plata/denue_celdas.csv", "data/oro/denue_celdas.csv",
                      "data/oro/denue_celdas.geojson"]:
            (raiz / viejo).unlink(missing_ok=True)
    resumen = {
        "estado": "ok", "archivo_bronce": puntero["archivo"], "agregado": agregado,
        "sha256_bronce": puntero["sha256"], "fecha_captura_utc": documento["fecha_captura_utc"],
        "entrada": len(documento["elements"]), "aceptados": len(puntos),
        "rechazados": len(rechazos), "por_zona": puntos.zona.value_counts().to_dict(),
        "crs": "EPSG:4326", "union": "geopandas.sjoin, intersects, celdas de estudio",
    }
    (raiz / "calidad/e2/geoespacial.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return resumen
