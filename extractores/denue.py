"""DENUE Colima: selección de sociedades de logística, minimizada antes de Bronce."""

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
            filas, conteos = minimizar(csv.DictReader(io.StringIO(texto)))
    if not filas:
        raise ValueError("DENUE no devolvió sociedades logísticas seleccionadas")
    documento = {
        "fuente": "INEGI / DENUE Colima", "url_origen": URL,
        "fecha_captura_utc": ahora, "archivo_csv_origen": nombres[0],
        "sha256_zip_origen": sha256(respuesta.content), "elements": filas, "conteos": conteos,
        "metadato_edicion": metadato, "codificacion_csv_origen": "cp1252",
        "licencia": "Términos de Libre Uso de la Información del INEGI",
        "terminos": "https://www.inegi.org.mx/inegi/terminos.html",
        "seleccion": "06/007, SCIAN 484/488/493, forma societaria explícita",
        "privacidad": "Lista blanca; sin nombres, razón social, domicilio, contactos ni CLEE",
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
