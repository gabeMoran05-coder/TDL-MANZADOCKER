"""Extractor etico: respeta robots.txt, se identifica y no satura sitios.

Basado en el codigo base del Kit de arranque TDL. Cambios respecto al kit:
- robots.txt se descarga con nuestra sesion (mismo User-Agent) y se interpreta
  segun RFC 9309: 4xx = sin restricciones; 5xx o error de red = no se descarga nada.
- Funciones auxiliares para guardar metadatos de captura y la bitacora de ejecuciones.
"""
from __future__ import annotations

import csv
import hashlib
import time
import urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

UA = (
    "TDL-Observatorio/1.0 (proyecto academico TecNM Colima; "
    "+https://github.com/gabeMoran05-coder/TDL-MANZADOCKER)"
)

RAIZ = Path(__file__).resolve().parent.parent
BITACORA = RAIZ / "calidad" / "bitacora_captura.csv"
CAMPOS_BITACORA = [
    "inicio_utc", "fin_utc", "duracion_s", "fuente", "estado",
    "registros", "archivos_nuevos", "disparador", "error",
]


class ExtractorEtico:
    def __init__(self, pausa: float = 1.5):
        self.pausa = pausa  # segundos minimos entre peticiones al mismo dominio
        self.robots: dict[str, urllib.robotparser.RobotFileParser] = {}
        self.ultimo: dict[str, float] = {}
        self.sesion = requests.Session()
        self.sesion.headers["User-Agent"] = UA

    def _reglas(self, url: str) -> urllib.robotparser.RobotFileParser:
        p = urlparse(url)
        base = f"{p.scheme}://{p.netloc}"
        if base not in self.robots:
            rp = urllib.robotparser.RobotFileParser(base + "/robots.txt")
            try:
                r = self.sesion.get(base + "/robots.txt", timeout=20)
                self.ultimo[p.netloc] = time.time()
            except requests.RequestException:
                rp.disallow_all = True  # sin poder leer reglas, no se descarga
            else:
                if r.status_code >= 500:
                    rp.disallow_all = True
                elif r.status_code in (401, 403):
                    rp.disallow_all = True
                elif r.status_code >= 400:
                    rp.allow_all = True  # RFC 9309: robots.txt inexistente
                else:
                    rp.parse(r.text.splitlines())
            self.robots[base] = rp
        return self.robots[base]

    def permitido(self, url: str) -> bool:
        return self._reglas(url).can_fetch(UA, url)

    def get(self, url: str, intentos: int = 3, **kwargs) -> requests.Response:
        reglas = self._reglas(url)
        if not reglas.can_fetch(UA, url):
            raise PermissionError(f"robots.txt no permite {url}")
        dominio = urlparse(url).netloc
        pausa = max(self.pausa, reglas.crawl_delay(UA) or 0)
        timeout = kwargs.pop("timeout", 60)
        for i in range(intentos):
            espera = pausa - (time.time() - self.ultimo.get(dominio, 0))
            if espera > 0:
                time.sleep(espera)
            r = self.sesion.get(url, timeout=timeout, **kwargs)
            self.ultimo[dominio] = time.time()
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(pausa * 2 ** i)  # espera exponencial ante saturacion
                continue
            r.raise_for_status()
            return r
        raise RuntimeError(f"Sin respuesta valida de {url} tras {intentos} intentos")


def ahora_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256(datos: bytes) -> str:
    return hashlib.sha256(datos).hexdigest()


def registrar_bitacora(fila: dict) -> None:
    """Agrega una fila a calidad/bitacora_captura.csv (crea encabezado si no existe)."""
    BITACORA.parent.mkdir(parents=True, exist_ok=True)
    nuevo = not BITACORA.exists()
    with BITACORA.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS_BITACORA)
        if nuevo:
            w.writeheader()
        w.writerow({k: fila.get(k, "") for k in CAMPOS_BITACORA})
