"""Reproduce E1 + contexto DENUE + linaje sin red. La captura va por separado."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from extractores.base import RAIZ
from src.geoespacial import ejecutar as geoespacial
from src.limpieza import ejecutar as limpiar
from src.linaje import generar


def ejecutar(raiz: Path = RAIZ) -> dict:
    limpiar(raiz)
    return {"geoespacial": geoespacial(raiz), "linaje": generar(raiz)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", type=Path, default=RAIZ)
    args = parser.parse_args()
    print(json.dumps(ejecutar(args.raiz), ensure_ascii=False, indent=2))
