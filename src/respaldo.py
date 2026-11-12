"""Respaldo de la capa Bronce con manifiesto SHA-256 y prueba de restauracion.

Uso:
  python -m src.respaldo crear     [--raiz RUTA] [--salida ZIP]
  python -m src.respaldo verificar ZIP [--raiz RUTA]
  python -m src.respaldo probar    [--raiz RUTA]   (crea, restaura en temporal y compara)

El ZIP incluye MANIFIESTO.json con ruta, bytes y SHA-256 de cada archivo.
Verificar = extraer en una carpeta temporal, recalcular cada SHA-256 y comparar
contra el manifiesto y contra los archivos vivos de data/bronce.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

BRONCE = "data/bronce"
MANIFIESTO = "MANIFIESTO.json"
PRUEBA = "calidad/e1/respaldo_prueba.json"


def sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def inventario(raiz: Path) -> dict[str, dict]:
    base = raiz / BRONCE
    return {
        p.relative_to(raiz).as_posix(): {"bytes": p.stat().st_size, "sha256": sha256(p)}
        for p in sorted(base.rglob("*"))
        if p.is_file() and p.name != ".gitkeep"
    }


def crear(raiz: Path, salida: Path) -> dict:
    archivos = inventario(raiz)
    if not archivos:
        raise FileNotFoundError(f"No hay archivos en {raiz / BRONCE}")
    manifiesto = {
        "creado_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "origen": BRONCE,
        "archivos": archivos,
        "total_archivos": len(archivos),
        "total_bytes": sum(a["bytes"] for a in archivos.values()),
    }
    salida.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(salida, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for ruta in archivos:
            z.write(raiz / ruta, ruta)
        z.writestr(MANIFIESTO, json.dumps(manifiesto, ensure_ascii=False, indent=1))
    return manifiesto


def verificar(zip_ruta: Path, raiz: Path | None = None) -> dict:
    """Restaura el ZIP en una carpeta temporal y compara hashes."""
    errores: list[str] = []
    with tempfile.TemporaryDirectory() as tmp, zipfile.ZipFile(zip_ruta) as z:
        manifiesto = json.loads(z.read(MANIFIESTO))
        z.extractall(tmp)
        destino = Path(tmp)
        for ruta, meta in manifiesto["archivos"].items():
            restaurado = destino / ruta
            if not restaurado.exists():
                errores.append(f"falta en el respaldo: {ruta}")
                continue
            if sha256(restaurado) != meta["sha256"]:
                errores.append(f"hash restaurado distinto del manifiesto: {ruta}")
            if raiz is not None:
                vivo = raiz / ruta
                if not vivo.exists():
                    errores.append(f"ya no existe en Bronce: {ruta}")
                elif sha256(vivo) != meta["sha256"]:
                    errores.append(f"Bronce cambio desde el respaldo: {ruta}")
    return {
        "zip": zip_ruta.name,
        "archivos_verificados": manifiesto["total_archivos"],
        "bytes": manifiesto["total_bytes"],
        "comparado_con_bronce_vivo": raiz is not None,
        "errores": errores,
        "ok": not errores,
    }


def probar(raiz: Path) -> dict:
    """Ciclo completo: crear -> restaurar en temporal -> comparar. Guarda la evidencia."""
    with tempfile.TemporaryDirectory() as tmp:
        zip_ruta = Path(tmp) / "respaldo_bronce.zip"
        manifiesto = crear(raiz, zip_ruta)
        resultado = verificar(zip_ruta, raiz)
        resultado.update(
            probado_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            zip_bytes=zip_ruta.stat().st_size,
            manifiesto_sha256=hashlib.sha256(
                json.dumps(manifiesto["archivos"], sort_keys=True).encode()
            ).hexdigest(),
        )
    salida = raiz / PRUEBA
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return resultado


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Respaldo verificable de la capa Bronce")
    sub = parser.add_subparsers(dest="accion", required=True)
    for nombre in ("crear", "verificar", "probar"):
        p = sub.add_parser(nombre)
        p.add_argument("--raiz", type=Path, default=Path(__file__).resolve().parents[1])
        if nombre == "crear":
            p.add_argument("--salida", type=Path, default=Path("respaldo_bronce.zip"))
        if nombre == "verificar":
            p.add_argument("zip", type=Path)
    args = parser.parse_args(argv)

    if args.accion == "crear":
        m = crear(args.raiz, args.salida)
        print(f"Respaldo creado: {args.salida} ({m['total_archivos']} archivos, "
              f"{m['total_bytes']} bytes)")
        return 0
    resultado = verificar(args.zip, args.raiz) if args.accion == "verificar" else probar(args.raiz)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0 if resultado["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
