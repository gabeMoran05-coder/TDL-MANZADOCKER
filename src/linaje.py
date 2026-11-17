"""Linaje verificable por registro: Oro -> grupos de dependencia -> Bronce inmutable.

Uso: python -m src.linaje [generar|validar|consultar] --archivo RUTA --registro 1
Los índices son registros lógicos desde 1 (en CSV, la cabecera no cuenta).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
from pathlib import Path

import pandas as pd

from extractores.base import RAIZ, ahora_utc

MANIFIESTO = "calidad/e2/linaje.json"


def hash_archivo(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def leer(ruta: Path) -> list[dict]:
    if ruta.suffix == ".csv":
        with ruta.open(encoding="utf-8", newline="") as archivo:
            return list(csv.DictReader(archivo))
    if ruta.suffix == ".parquet":
        return pd.read_parquet(ruta).to_dict("records")
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    if ruta.suffix == ".geojson":
        return [r["properties"] for r in datos["features"]]
    return [{"clave": k, "valor": v} for k, v in sorted(datos.items())]


def guardar(objeto: dict, ruta: Path):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(objeto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def generar(raiz: Path = RAIZ) -> dict:
    metricas = raiz / "data/oro/pronostico_metricas.json"
    if metricas.exists():
        huella = json.loads(metricas.read_text(encoding="utf-8")).get("datos_sha256")
        if huella != hash_archivo(raiz / "data/oro/mensual_integrado.csv"):
            raise ValueError("Pronóstico desactualizado: recalcular el notebook E1 antes de sellar linaje")
    origenes, grupos, archivos_bronce = {}, {}, {}
    por_periodo = {}
    for fuente, archivo in [("asipona", "em_mensual.csv"), ("banxico", "tipo_cambio_fix.csv")]:
        entrada = raiz / f"data/bronce/{fuente}/{archivo}"
        digest = hash_archivo(entrada)
        copia = f"data/bronce/linaje/{fuente}-{digest}.csv"
        destino = raiz / copia
        destino.parent.mkdir(parents=True, exist_ok=True)
        if not destino.exists():
            destino.write_bytes(entrada.read_bytes())
        archivos_bronce[copia] = digest
        ids = set(pd.read_csv(raiz / (
            "data/plata/asipona_mensual.csv" if fuente == "asipona"
            else "data/plata/banxico_diario.csv")).id_origen)
        grupo = []
        for n, r in enumerate(leer(destino), start=1):
            identificador = f"{fuente}:{n+1}"
            if identificador not in ids:
                continue
            clave = f"{fuente}:{digest[:16]}:{n}"
            periodo = (r["anio"] + "-" + r["mes"].zfill(2)
                       if fuente == "asipona" else r["fecha"][:7])
            por_periodo.setdefault(periodo, []).append(clave)
            origenes[clave] = {
                "fuente": fuente, "archivo_bronce": copia, "registro": n,
                "linea_csv": n + 1, "id_origen": identificador,
                "url_origen": r["url_origen"], "fecha_captura_utc": r["fecha_captura_utc"],
                "archivo_original": r.get("archivo_origen"),
                "periodo": periodo, "variable_o_serie": r.get("variable", r.get("serie")),
            }
            if r.get("archivo_origen"):
                original = r["archivo_origen"]
                archivos_bronce[original] = hash_archivo(raiz / original)
            grupo.append(clave)
        if not grupo:
            raise ValueError("Fuente sin dependencias válidas: " + fuente)
        grupos[fuente] = grupo
    puntero = json.loads((raiz / "data/bronce/denue/actual.json").read_text(encoding="utf-8"))
    denue = puntero["archivo"]
    documento = json.loads((raiz / denue).read_text(encoding="utf-8"))
    if hash_archivo(raiz / denue) != puntero["sha256"]:
        raise ValueError("Captura DENUE alterada")
    archivos_bronce[denue] = puntero["sha256"]
    denue_ids = {}
    for n, r in enumerate(documento["elements"], start=1):
        identificador = str(r["id_denue"])
        clave = f"denue:{puntero['sha256'][:16]}:{n}"
        origenes[clave] = {
            "fuente": "denue", "archivo_bronce": denue, "registro": n,
            "id_origen": identificador,
            "url_origen": documento["url_origen"],
            "fecha_captura_utc": documento["fecha_captura_utc"],
        }
        denue_ids[identificador] = clave
    grupos["denue"] = sorted(denue_ids.values())
    # E1 calcula escalas y atípicos por conjunto; las imputaciones miran meses anteriores.
    # Conservamos un superconjunto explícito de entradas válidas en vez de perder dependencias.
    oro = {}
    for ruta in sorted((raiz / "data/oro").iterdir()):
        if not ruta.is_file() or ruta.name.startswith("."):
            continue
        if ruta.suffix not in {".csv", ".parquet", ".json", ".geojson"}:
            raise ValueError("Formato Oro no cubierto por linaje: " + ruta.name)
        registros = []
        for n, r in enumerate(leer(ruta), start=1):
            geo = ruta.stem == "contexto_geografico"
            registros.append({
                "registro": n,
                "clave_negocio": str(r.get("id_denue", r.get("id_origen", r.get("fecha", r.get("clave", n))))),
                "grupos": [] if geo else ["asipona", "banxico"],
                "origenes_directos": ([denue_ids[r["id_denue"]]] if geo
                                       else por_periodo.get(str(r.get("fecha", ""))[:7], [])),
                "metodo": "establecimiento DENUE + sjoin con celdas" if geo else
                          "E1: integración, agregación, imputación causal y/o ajuste estadístico",
            })
        oro[ruta.relative_to(raiz).as_posix()] = {
            "sha256": hash_archivo(ruta), "registros": registros,
        }
    manifiesto = {
        "version": 1, "generado_utc": ahora_utc(), "oro": oro,
        "codigo_sha256": {p.relative_to(raiz).as_posix(): hash_archivo(p)
                          for carpeta in ["src", "extractores"]
                          for p in sorted((raiz / carpeta).glob("*.py"))},
        "versiones": {p: importlib.metadata.version(p)
                      for p in ["pandas", "geopandas", "shapely", "pyarrow"]},
        "origenes": origenes, "grupos": grupos, "archivos_bronce": archivos_bronce,
        "granularidad": "Cada registro Oro identifica registros Bronce, URL y fecha real de ingesta.",
        "precision": "E1 usa grupos conservadores de todas las filas válidas de ASIPONA y Banxico; "
                     "pueden incluir filas no utilizadas por una celda concreta. DENUE es uno a uno. "
                     "La generación del manifiesto no es la fecha de ingesta.",
    }
    guardar(manifiesto, raiz / MANIFIESTO)
    return validar(raiz)


def validar(raiz: Path = RAIZ) -> dict:
    m = json.loads((raiz / MANIFIESTO).read_text(encoding="utf-8"))
    reales = {p.relative_to(raiz).as_posix() for p in (raiz / "data/oro").iterdir()
              if p.is_file() and not p.name.startswith(".")}
    if reales != set(m["oro"]):
        raise ValueError("Hay archivos Oro sin linaje o eliminados")
    for archivo, digest in m["archivos_bronce"].items():
        if hash_archivo(raiz / archivo) != digest:
            raise ValueError("Bronce alterado: " + archivo)
    cache = {}
    for origen in m["origenes"].values():
        archivo = origen["archivo_bronce"]
        if archivo not in m["archivos_bronce"]:
            raise ValueError("Fuente no preservada en Bronce")
        if not origen["url_origen"].startswith("https://"):
            raise ValueError("URL de origen inválida")
        if pd.isna(pd.to_datetime(origen["fecha_captura_utc"], utc=True, errors="coerce")):
            raise ValueError("Fecha de ingesta inválida")
        if archivo not in cache:
            ruta = raiz / archivo
            cache[archivo] = (json.loads(ruta.read_text(encoding="utf-8"))["elements"]
                             if origen["fuente"] == "denue" else leer(ruta))
        if not 1 <= origen["registro"] <= len(cache[archivo]):
            raise ValueError("Selector Bronce fuera de rango")
        if origen["fuente"] == "denue":
            original = cache[archivo][origen["registro"] - 1]
            documento = json.loads((raiz / archivo).read_text(encoding="utf-8"))
            if (str(original["id_denue"]) != origen["id_origen"]
                    or documento["fecha_captura_utc"] != origen["fecha_captura_utc"]
                    or documento["url_origen"] != origen["url_origen"]):
                raise ValueError("Procedencia DENUE no coincide con Bronce")
        else:
            original = cache[archivo][origen["registro"] - 1]
            if any(original[c] != origen[c] for c in ["url_origen", "fecha_captura_utc"]):
                raise ValueError("Metadatos de ingesta no coinciden con Bronce")
    filas = 0
    for archivo, producto in m["oro"].items():
        if hash_archivo(raiz / archivo) != producto["sha256"]:
            raise ValueError("Oro alterado o manifiesto desactualizado: " + archivo)
        if len(leer(raiz / archivo)) != len(producto["registros"]):
            raise ValueError("Número de registros sin cobertura: " + archivo)
        for n, registro in enumerate(producto["registros"], start=1):
            if registro["registro"] != n:
                raise ValueError("Índice de registro inválido")
            ids = registro["origenes_directos"] + [
                k for grupo in registro["grupos"] for k in m["grupos"][grupo]]
            if not ids:
                raise ValueError("Registro sin origen: " + archivo)
            if not set(ids).issubset(m["origenes"]):
                raise ValueError("Referencia Bronce desconocida")
            filas += 1
    resultado = {"estado": "ok", "archivos_oro": len(reales), "registros_oro": filas,
                 "registros_con_linaje": filas, "cobertura_pct": 100,
                 "registros_bronce_referenciados": len(m["origenes"])}
    guardar(resultado, raiz / "calidad/e2/validacion_linaje.json")
    return resultado


def consultar(raiz: Path, archivo: str, registro: int) -> dict:
    validar(raiz)
    m = json.loads((raiz / MANIFIESTO).read_text(encoding="utf-8"))
    if registro < 1:
        raise ValueError("registro empieza en 1")
    fila = m["oro"][archivo]["registros"][registro - 1]
    ids = fila["origenes_directos"] + [k for g in fila["grupos"] for k in m["grupos"][g]]
    return {"archivo": archivo, **fila, "precision": m["precision"],
            "origenes": [m["origenes"][k] for k in sorted(set(ids))]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("accion", choices=["generar", "validar", "consultar"], default="validar", nargs="?")
    parser.add_argument("--raiz", type=Path, default=RAIZ)
    parser.add_argument("--archivo", default="data/oro/contexto_geografico.csv")
    parser.add_argument("--registro", type=int, default=1)
    args = parser.parse_args()
    resultado = (consultar(args.raiz, args.archivo, args.registro) if args.accion == "consultar"
                 else (generar if args.accion == "generar" else validar)(args.raiz))
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
