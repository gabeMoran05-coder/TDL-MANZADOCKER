"""Extractor del tipo de cambio FIX (pesos por dolar) desde la API SIE de Banxico.

Serie SF43718: "Tipo de cambio FIX", publicada cada dia habil.
Documentacion de la API: https://www.banxico.org.mx/SieAPIRest/service/v1/
Requiere token gratuito en la variable de entorno BANXICO_TOKEN
(en GitHub: Settings > Secrets and variables > Actions > BANXICO_TOKEN).
Nunca se escribe el token en el codigo ni en el repositorio.

Salidas (capa bronce):
- data/bronce/banxico/json/<fecha_captura>.json   respuesta cruda de cada captura
- data/bronce/banxico/tipo_cambio_fix.csv         tabla acumulada, una fila por fecha
"""
from __future__ import annotations

import csv
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone

from extractores.base import RAIZ, ExtractorEtico, ahora_utc

SERIE = "SF43718"
API = "https://www.banxico.org.mx/SieAPIRest/service/v1/series/{serie}/datos/{ini}/{fin}"
INICIO_HISTORICO = date(2021, 1, 1)   # alineado con la serie de TEU de ASIPONA
DIAS_REVISION = 10                    # en capturas diarias se piden los ultimos 10 dias
DIR = RAIZ / "data" / "bronce" / "banxico"
TABLA = DIR / "tipo_cambio_fix.csv"
CAMPOS = ["fecha", "serie", "valor", "valor_crudo", "url_origen", "fecha_captura_utc"]


def _token() -> str:
    t = os.environ.get("BANXICO_TOKEN", "").strip()
    if not t:
        raise RuntimeError("Falta la variable de entorno BANXICO_TOKEN")
    return t


def _existentes() -> dict[str, dict]:
    if not TABLA.exists():
        return {}
    with TABLA.open(encoding="utf-8") as f:
        return {fila["fecha"]: fila for fila in csv.DictReader(f)}


def ejecutar() -> dict:
    token = _token()
    previas = _existentes()
    hoy = date.today()
    ini = INICIO_HISTORICO if not previas else hoy - timedelta(days=DIAS_REVISION)
    url = API.format(serie=SERIE, ini=ini.isoformat(), fin=hoy.isoformat())

    ext = ExtractorEtico(pausa=1.5)
    r = ext.get(url, headers={"Bmx-Token": token, "Accept": "application/json"})
    cuerpo = r.json()
    captura = ahora_utc()

    # 1) Respuesta cruda, tal como llego (el token va en un encabezado, no en el JSON)
    DIR.joinpath("json").mkdir(parents=True, exist_ok=True)
    marca = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    DIR.joinpath("json", f"{marca}.json").write_text(
        json.dumps({"url": url, "fecha_captura_utc": captura, "respuesta": cuerpo},
                   ensure_ascii=False, indent=1),
        encoding="utf-8")

    # 2) Tabla acumulada: solo se agregan fechas nuevas (la primera captura manda)
    series = cuerpo.get("bmx", {}).get("series", [])
    datos = series[0].get("datos", []) if series else []
    nuevas = 0
    for d in datos:
        fecha = datetime.strptime(d["fecha"], "%d/%m/%Y").date().isoformat()
        if fecha in previas:
            continue
        crudo = d.get("dato", "")
        try:
            valor = float(crudo.replace(",", ""))
        except ValueError:
            valor = ""            # p. ej. "N/E" (no existe dato ese dia)
        previas[fecha] = {"fecha": fecha, "serie": SERIE, "valor": valor,
                          "valor_crudo": crudo, "url_origen": url,
                          "fecha_captura_utc": captura}
        nuevas += 1

    with TABLA.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        w.writerows(previas[k] for k in sorted(previas))
    return {"registros": nuevas, "archivos_nuevos": 1, "total_fechas": len(previas)}


if __name__ == "__main__":
    print(ejecutar())
    sys.exit(0)
