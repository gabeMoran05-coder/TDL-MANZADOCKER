"""DENUE Colima: logística de Manzanillo minimizada antes de Bronce.

Guarda dos productos: (1) la selección original de sociedades con forma societaria
explícita (puntos, sin nombres) y (2) conteos agregados por celda y categoría de todos
los establecimientos SCIAN 484/488/493, sin datos individuales (k-anonimato, k=3).
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import re
import zipfile
from datetime import datetime
from pathlib import Path

from extractores.base import RAIZ, ExtractorEtico, ahora_utc, sha256

URL = "https://www.inegi.org.mx/contenidos/masiva/denue/denue_06_csv.zip"
CATEGORIAS = {"484": "Autotransporte de carga", "488": "Servicios relacionados con el transporte",
              "493": "Almacenamiento"}


def minimizar(filas) -> tuple[list[dict], dict]:
    """Excluye personas físicas y nunca devuelve razones sociales/contactos/domicilios."""
    salida = []
    conteos = {"leidos": 0, "seleccionados": 0, "sin_forma_societaria": 0,
               "coordenadas_invalidas": 0}
    for n, r in enumerate(filas, start=1):
        conteos["leidos"] += 1
        actividad = r.get("codigo_act", "").strip()
        if (r.get("cve_ent", "").strip().zfill(2) != "06"
                or r.get("cve_mun", "").strip().zfill(3) != "007"
                or actividad[:3] not in CATEGORIAS):
            continue
        razon = re.sub(r"[^A-Z]", "", r.get("raz_social", "").upper())
        if not razon.endswith(("SADECV", "SDERLDECV", "SADERLDECV", "SASDECV", "SAPIDECV", "SABDECV")):
            conteos["sin_forma_societaria"] += 1
            continue
        try:
            lat, lon = float(r["latitud"]), float(r["longitud"])
            if not all(math.isfinite(v) for v in [lat, lon]) or not (-90 <= lat <= 90 and -180 <= lon <= 180):
                raise ValueError("coordenadas")
            if not r["id"].isdigit() or not actividad.isdigit() or len(actividad) != 6:
                raise ValueError("identificador o actividad")
        except (ValueError, KeyError):
            conteos["coordenadas_invalidas"] += 1
            continue
        salida.append({"id_denue": r["id"], "codigo_actividad": actividad,
                       "cve_ent": "06", "cve_mun": "007", "lat": lat, "lon": lon,
                       "registro_csv_origen": n})
    conteos["seleccionados"] = len(salida)
    return salida, conteos


PASO_GRADOS = 0.01   # celda de ~1.1 km; rejilla de estudio, no límite oficial
K_MINIMO = 3         # celdas y conteos por categoría con menos de K se suprimen


def agregar(filas, paso: float = PASO_GRADOS, k: int = K_MINIMO) -> dict:
    """Cuenta establecimientos logísticos de Manzanillo por celda y categoría.

    Se aplica antes de persistir: no sale ningún id, nombre, razón social, domicilio
    ni coordenada individual. Celdas con menos de k establecimientos se suman a un
    renglón suprimido sin ubicación; dentro de una celda publicada, una categoría con
    1..k-1 establecimientos se reporta como None (suprimida).
    """
    celdas: dict[tuple[int, int], dict[str, int]] = {}
    for r in filas:
        actividad = r.get("codigo_act", "").strip()
        if (r.get("cve_ent", "").strip().zfill(2) != "06"
                or r.get("cve_mun", "").strip().zfill(3) != "007"
                or actividad[:3] not in CATEGORIAS):
            continue
        try:
            lat, lon = float(r["latitud"]), float(r["longitud"])
        except (KeyError, ValueError):
            continue
        if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90
                and -180 <= lon <= 180):
            continue
        clave = (math.floor(lat / paso), math.floor(lon / paso))
        conteo = celdas.setdefault(clave, dict.fromkeys(CATEGORIAS, 0))
        conteo[actividad[:3]] += 1
    publicadas, suprimidas = [], {"celdas": 0, "establecimientos": 0,
                                  "por_categoria": dict.fromkeys(CATEGORIAS, 0)}
    for (i, j), conteo in sorted(celdas.items()):
        total = sum(conteo.values())
        if total < k:
            suprimidas["celdas"] += 1
            suprimidas["establecimientos"] += total
            for c, n in conteo.items():
                suprimidas["por_categoria"][c] += n
            continue
        publicadas.append({
            "celda": f"{i}_{j}", "sur": round(i * paso, 6), "oeste": round(j * paso, 6),
            "norte": round((i + 1) * paso, 6), "este": round((j + 1) * paso, 6),
            "total": total,
            "por_categoria": {c: (n if n == 0 or n >= k else None) for c, n in conteo.items()},
        })
    return {"paso_grados": paso, "k_minimo": k, "celdas": publicadas, "suprimidas": suprimidas,
            "total_establecimientos": sum(c["total"] for c in publicadas)
            + suprimidas["establecimientos"]}


def ejecutar(raiz: Path = RAIZ, forzar: bool = False) -> dict:
    carpeta = raiz / "data/bronce/denue"
    puntero = carpeta / "actual.json"
    ahora = ahora_utc()
    if puntero.exists() and not forzar:
        actual = json.loads(puntero.read_text(encoding="utf-8"))
        edad = datetime.fromisoformat(ahora.replace("Z", "+00:00")) - datetime.fromisoformat(
            actual["fecha_captura_utc"].replace("Z", "+00:00"))
        if edad.total_seconds() < 7 * 86400:
            return {"registros": actual["registros"], "archivos_nuevos": 0}
    respuesta = ExtractorEtico(pausa=2).get(URL, timeout=60)
    # El ZIP y el CSV completo se procesan en memoria, nunca se escriben en disco.
    with zipfile.ZipFile(io.BytesIO(respuesta.content)) as archivo:
        nombres = [n for n in archivo.namelist()
                   if n.startswith("conjunto_de_datos/") and n.endswith(".csv")]
        if len(nombres) != 1:
            raise ValueError("La descarga DENUE no contiene un único CSV de datos")
        diccionarios = [n for n in archivo.namelist() if "diccionario_de_datos" in n and n.endswith(".csv")]
        metadato = archivo.read(diccionarios[0]).decode("cp1252").splitlines()[0] if diccionarios else ""
        with archivo.open(nombres[0]) as datos:
            texto = datos.read().removeprefix(b"\xef\xbb\xbf").decode("cp1252")
            crudas = list(csv.DictReader(io.StringIO(texto)))
            filas, conteos = minimizar(crudas)
            agregado = agregar(crudas)
            del crudas, texto  # el detalle individual no sale de memoria
    if not filas:
        raise ValueError("DENUE no devolvió sociedades logísticas seleccionadas")
    documento = {
        "fuente": "INEGI / DENUE Colima", "url_origen": URL,
        "fecha_captura_utc": ahora, "archivo_csv_origen": nombres[0],
        "sha256_zip_origen": sha256(respuesta.content), "elements": filas, "conteos": conteos,
        "agregado": agregado,
        "metadato_edicion": metadato, "codificacion_csv_origen": "cp1252",
        "licencia": "Términos de Libre Uso de la Información del INEGI",
        "terminos": "https://www.inegi.org.mx/inegi/terminos.html",
        "seleccion": "06/007, SCIAN 484/488/493, forma societaria explícita",
        "privacidad": "Lista blanca; sin nombres, razón social, domicilio, contactos ni CLEE",
        "privacidad_agregado": (f"Conteos por celda de {PASO_GRADOS} grados y categoría SCIAN, "
                                f"sin identificadores ni coordenadas individuales; celdas y "
                                f"categorías con menos de {K_MINIMO} establecimientos suprimidas"),
    }
    contenido = (json.dumps(documento, ensure_ascii=False, indent=2) + "\n").encode()
    carpeta.mkdir(parents=True, exist_ok=True)
    nombre = ahora.replace(":", "").replace("-", "") + "-" + sha256(contenido)[:12] + ".json"
    destino = carpeta / nombre
    destino.write_bytes(contenido)
    puntero.write_text(json.dumps({
        "archivo": destino.relative_to(raiz).as_posix(), "sha256": sha256(contenido),
        "fecha_captura_utc": ahora, "registros": len(filas),
    }, indent=2) + "\n", encoding="utf-8")
    return {"registros": len(filas), "archivos_nuevos": 1}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forzar", action="store_true")
    args = parser.parse_args()
    print(ejecutar(forzar=args.forzar))
