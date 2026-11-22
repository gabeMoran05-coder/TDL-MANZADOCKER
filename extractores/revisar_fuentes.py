"""Conserva estado de las condiciones y robots. No descarga directorios personales."""

from __future__ import annotations

import json
import time
import urllib.robotparser

import requests

from extractores.base import RAIZ, UA, ahora_utc, sha256
from extractores.denue import URL

PAGINAS = [
    ("https://www.inegi.org.mx/robots.txt", URL),
    ("https://www.inegi.org.mx/inegi/terminos.html", None),
    ("https://www.puertomanzanillo.com.mx/robots.txt",
     "https://www.puertomanzanillo.com.mx/esps/0000209/estadisticas.html"),
    ("https://www.gob.mx/terminos", None),
    ("https://www.banxico.org.mx/robots.txt", "https://www.banxico.org.mx/SieAPIRest/"),
    ("https://www.banxico.org.mx/footer-es/salvedad-politicas-uso-banco-.html", None),
]


def ejecutar():
    resultados = []
    for url, objetivo in PAGINAS:
        r = {"url": url, "revisado_utc": ahora_utc()}
        try:
            respuesta = requests.get(url, headers={"User-Agent": UA}, timeout=20)
            r.update(status_http=respuesta.status_code, sha256_respuesta=sha256(respuesta.content))
            if objetivo:
                reglas = urllib.robotparser.RobotFileParser()
                reglas.parse(respuesta.text.splitlines())
                permitido = (reglas.can_fetch(UA, objetivo) if respuesta.status_code == 200
                             else respuesta.status_code in (404, 410))
                r.update(ruta_comprobada=objetivo, permitido_robots=permitido,
                         contenido_robots=respuesta.text if respuesta.status_code == 200 else None)
        except requests.RequestException as error:
            r.update(error=type(error).__name__)
        resultados.append(r)
        time.sleep(2)
    destino = RAIZ / "calidad/e2/fuentes_web.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps({"user_agent": UA, "verificaciones": resultados},
                                 ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps([{k: v for k, v in r.items() if k != "contenido_robots"}
                      for r in resultados], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    ejecutar()
