"""TEU por terminal y por tráfico desde los PDF EM de ASIPONA ya guardados en Bronce.

La tabla «MOVIMIENTO DE TEU'S POR EMPRESA POR TRÁFICO» solo publica acumulados del
año (columna actual y año anterior), no meses. Se usa el EM más reciente de cada año:
diciembre da el año completo; para el año en curso, el acumulado hasta el último mes.

No descarga nada: lee los PDF listados en data/bronce/asipona/capturas.csv y verifica
su SHA-256. Valida que las terminales sumen el TOTAL y que cada fila cuadre con sus
tráficos. El año anterior que trae cada PDF se usa como verificación cruzada.

Uso: python -m src.terminales_trafico
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CAPTURAS = "data/bronce/asipona/capturas.csv"
SALIDA = "data/plata/terminal_trafico_anual.csv"
RESUMEN = "calidad/e3/terminal_trafico.json"
TERMINALES = ("SSA", "CONTECON", "OCUPA", "TIMSA")
TRAFICOS = ("total", "importacion", "exportacion", "cabotaje", "transbordo")
CAMPOS = ["anio", "terminal", "meses", "columna_pdf", "teu_total", "teu_importacion", "teu_exportacion",
          "teu_cabotaje", "teu_transbordo", "archivo_origen", "sha256_pdf", "url_origen",
          "fecha_captura_utc"]
TOLERANCIA_TEU = 2
_FILA = re.compile(r"^(SSA|CONTECON|OCUPA|TIMSA|TOTAL)\s+(.*)$")


def _entero(tok: str) -> int:
    if tok == "-":
        return 0
    return int(tok.replace(",", ""))


def leer_tabla(texto: str) -> dict[str, dict[str, tuple[int, int]]]:
    """Devuelve {terminal: {trafico: (actual, anterior)}} de la tabla por tráfico.

    Cada tráfico ocupa tres columnas: actual, anterior y % de variación.
    """
    lineas = texto.splitlines()
    inicio = next((i for i, linea in enumerate(lineas)
                   if re.match(r"MOVIMIENTO DE TEU.S POR EMPRESA POR TR", linea.strip().upper())), None)
    if inicio is None:
        raise ValueError("El PDF no contiene la tabla por empresa y tráfico")
    tabla: dict[str, dict[str, tuple[int, int]]] = {}
    for linea in lineas[inicio + 1:]:
        m = _FILA.match(linea.strip())
        if not m:
            if tabla and linea.strip().upper().startswith("NOTAS"):
                break
            continue
        toks = m.group(2).split()
        if not re.match(r"^[\d,]+$", toks[0]):
            continue  # encabezado «TOTAL IMPO EXPO CABOTAJE TRANSBORDO»
        if len(toks) != 15:
            raise ValueError(f"Fila {m.group(1)} con {len(toks)} columnas (se esperaban 15)")
        tabla[m.group(1)] = {t: (_entero(toks[3 * k]), _entero(toks[3 * k + 1]))
                             for k, t in enumerate(TRAFICOS)}
        if m.group(1) == "TOTAL":
            break
    faltan = set(TERMINALES + ("TOTAL",)) - set(tabla)
    if faltan:
        raise ValueError(f"Faltan filas en la tabla: {sorted(faltan)}")
    return tabla


def validar_tabla(tabla: dict[str, dict[str, tuple[int, int]]],
                  tolerancia: int = TOLERANCIA_TEU) -> list[dict]:
    """Terminales suman el TOTAL y cada fila cuadra: total = impo + expo + cabotaje + transbordo.

    ASIPONA redondea TEU (un contenedor de 45' vale 2.25 TEU), así que se aceptan
    diferencias de hasta `tolerancia` TEU; se devuelven todas para documentarlas.
    """
    difs = []
    for col, nombre in ((0, "actual"), (1, "anterior")):
        for t in TRAFICOS:
            suma = sum(tabla[e][t][col] for e in TERMINALES)
            if suma != tabla["TOTAL"][t][col]:
                difs.append({"columna": nombre, "regla": f"terminales = TOTAL ({t})",
                             "diferencia": suma - tabla["TOTAL"][t][col]})
        for e in TERMINALES + ("TOTAL",):
            partes = sum(tabla[e][t][col] for t in TRAFICOS[1:])
            if partes != tabla[e]["total"][col]:
                difs.append({"columna": nombre, "regla": f"tráficos = total ({e})",
                             "diferencia": partes - tabla[e]["total"][col]})
    graves = [d for d in difs if abs(d["diferencia"]) > tolerancia]
    if graves:
        raise ValueError(f"La tabla no cuadra: {graves}")
    return difs


def _texto_pdf(ruta: Path) -> str:
    import pdfplumber
    with pdfplumber.open(ruta) as pdf:
        return "\n".join(p.extract_text() or "" for p in pdf.pages)


def construir(raiz: Path = RAIZ, leer_pdf=_texto_pdf) -> tuple[list[dict], dict]:
    with (raiz / CAPTURAS).open(encoding="utf-8") as f:
        capturas = list(csv.DictReader(f))
    # EM más reciente de cada año (mayor mes_reporte)
    ultimo: dict[int, dict] = {}
    for c in capturas:
        anio, mes = int(c["anio"]), int(c["mes_reporte"])
        if anio not in ultimo or mes > int(ultimo[anio]["mes_reporte"]):
            ultimo[anio] = c
    filas, anteriores, cruces, redondeos, origen = [], {}, [], [], {}
    for anio, c in sorted(ultimo.items()):
        ruta = raiz / c["archivo"]
        digest = hashlib.sha256(ruta.read_bytes()).hexdigest()
        if digest != c["sha256"]:
            raise ValueError(f"PDF alterado respecto a su captura: {c['archivo']}")
        tabla = leer_tabla(leer_pdf(ruta))
        for d in validar_tabla(tabla):
            redondeos.append({"anio": anio, **d})
        meses = int(c["mes_reporte"])
        for e in TERMINALES:
            filas.append({"anio": anio, "terminal": e, "meses": meses, "columna_pdf": "actual",
                          **{f"teu_{t}": tabla[e][t][0] for t in TRAFICOS},
                          "archivo_origen": c["archivo"], "sha256_pdf": digest,
                          "url_origen": c["url"], "fecha_captura_utc": c["fecha_captura_utc"]})
            anteriores[(anio - 1, e, meses)] = {t: tabla[e][t][1] for t in TRAFICOS}
            origen[(anio - 1, e, meses)] = (c, digest)
    # Verificación cruzada: el año anterior de un EM de diciembre contra el EM de ese año
    actuales = {(f["anio"], f["terminal"], f["meses"]): f for f in filas}
    for clave, valores in sorted(anteriores.items()):
        if clave in actuales:
            difs = {t: actuales[clave][f"teu_{t}"] - v for t, v in valores.items()
                    if actuales[clave][f"teu_{t}"] != v}
            cruces.append({"anio": clave[0], "terminal": clave[1], "diferencias": difs})
    # Años sin EM propio en Bronce (2020): se toman de la columna «año anterior» del EM
    # de diciembre siguiente; solo años completos.
    for (anio, e, meses), valores in sorted(anteriores.items()):
        if meses == 12 and (anio, e, 12) not in actuales and anio not in ultimo:
            c, digest = origen[(anio, e, meses)]
            filas.append({"anio": anio, "terminal": e, "meses": 12, "columna_pdf": "anterior",
                          **{f"teu_{t}": v for t, v in valores.items()},
                          "archivo_origen": c["archivo"], "sha256_pdf": digest,
                          "url_origen": c["url"], "fecha_captura_utc": c["fecha_captura_utc"]})
    filas.sort(key=lambda f: (f["anio"], TERMINALES.index(f["terminal"])))
    resumen = {
        "fuente": "ASIPONA Manzanillo, EM (ASPN-MAN-JES-F-05), tabla por empresa y tráfico",
        "nota": "Acumulados anuales publicados; el año en curso es acumulado parcial (columna meses).",
        "pdfs": [{"anio": a, "archivo": c["archivo"], "mes_reporte": int(c["mes_reporte"])}
                 for a, c in sorted(ultimo.items())],
        "filas": len(filas),
        "validaciones": f"terminales = TOTAL por tráfico y total = suma de tráficos, en ambas columnas de cada PDF; tolerancia de redondeo {TOLERANCIA_TEU} TEU",
        "redondeos_aceptados": redondeos,
        "verificacion_cruzada": {"comparaciones": len(cruces),
                                 "con_diferencias": [c for c in cruces if c["diferencias"]]},
    }
    return filas, resumen


def ejecutar(raiz: Path = RAIZ, leer_pdf=_texto_pdf) -> dict:
    filas, resumen = construir(raiz, leer_pdf)
    salida = raiz / SALIDA
    salida.parent.mkdir(parents=True, exist_ok=True)
    with salida.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS, lineterminator="\n")
        w.writeheader()
        w.writerows(filas)
    resumen["sha256_salida"] = hashlib.sha256(salida.read_bytes()).hexdigest()
    (raiz / RESUMEN).parent.mkdir(parents=True, exist_ok=True)
    (raiz / RESUMEN).write_text(json.dumps(resumen, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8")
    return resumen


if __name__ == "__main__":
    r = ejecutar()
    print(json.dumps({k: r[k] for k in ("filas", "verificacion_cruzada")}, ensure_ascii=False, indent=1))
