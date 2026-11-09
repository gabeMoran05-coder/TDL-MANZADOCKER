"""Corre la captura de todas las fuentes y registra cada ejecucion en la bitacora.

Uso:  python -m extractores.run_captura            (todas las fuentes)
      python -m extractores.run_captura asipona    (solo una)

Cada fuente se ejecuta aunque otra falle. Al final sale con codigo 1 si alguna
fallo, para que GitHub Actions marque la ejecucion en rojo (pero la bitacora
y los datos capturados se guardan igual).
"""
from __future__ import annotations

import os
import sys
import time
import traceback
from datetime import datetime, timezone

from extractores import asipona, banxico
from extractores.base import registrar_bitacora

FUENTES = {
    "asipona": asipona.ejecutar,
    "banxico": banxico.ejecutar,
}


def main(nombres: list[str]) -> int:
    disparador = os.environ.get("GITHUB_EVENT_NAME", "manual-local")
    fallas = 0
    for nombre in nombres or list(FUENTES):
        t0 = time.time()
        inicio = datetime.now(timezone.utc)
        fila = {"fuente": nombre, "disparador": disparador,
                "inicio_utc": inicio.strftime("%Y-%m-%dT%H:%M:%SZ")}
        try:
            res = FUENTES[nombre]()
            fila.update(estado="ok", registros=res.get("registros", 0),
                        archivos_nuevos=res.get("archivos_nuevos", 0))
        except Exception as e:  # se registra cualquier falla, no se oculta
            fallas += 1
            fila.update(estado="falla", error=f"{type(e).__name__}: {e}"[:300])
            traceback.print_exc()
        fila["fin_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        fila["duracion_s"] = round(time.time() - t0, 1)
        registrar_bitacora(fila)
        print(fila)
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
