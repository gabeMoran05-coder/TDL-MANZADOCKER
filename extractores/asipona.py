"""Extractor de la Estadistica Mensual (EM) de ASIPONA Manzanillo.

Fuente: https://www.puertomanzanillo.com.mx/esps/0000209/estadisticas.html
Cada PDF "EM" (formato ASPN-MAN-JES-F-05) trae una tabla con ENE..DIC del anio
en columnas. Con el EM mas reciente de cada anio se obtiene la serie mensual.

Salidas (capa bronce):
- data/bronce/asipona/pdf/<anio>/<archivo>.pdf   PDF crudo, tal como llego
- data/bronce/asipona/capturas.csv               metadatos de cada descarga
- data/bronce/asipona/em_mensual.csv             tabla extraida (formato largo)
"""
from __future__ import annotations

import csv
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urljoin

import pdfplumber

from extractores.base import RAIZ, ExtractorEtico, ahora_utc, sha256

SITIO = "https://www.puertomanzanillo.com.mx/"
PAG_ESTADISTICAS = SITIO + "esps/0000209/estadisticas.html"
DIR = RAIZ / "data" / "bronce" / "asipona"
DIR_PDF = DIR / "pdf"
CAPTURAS = DIR / "capturas.csv"
TABLA = DIR / "em_mensual.csv"

MESES = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO",
         "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]

# EM de cierre de anio, URLs verificadas el 2026-11-08 en las paginas "Anio <n>".
CATALOGO = {
    2021: (12, "upl/sec/ESTADISTICA-MENSUAL1221.pdf"),
    2022: (12, "upl/sec/ESTAD%C3%8DSTICA-MENSUAL-A-DICIEMBRE-2022.pdf"),
    2023: (12, "upl/sec/ESTAD%C3%8DSTICA-MENSUAL-A-DICIEMBRE-2023.pdf"),
    2024: (12, "upl/sec/EM-DICIEMBRE-2024.pdf"),
    2025: (12, "upl/sec/2025/estadisticas/EM-DICIEMBRE-2025.pdf"),
}
PRIMER_ANIO_DINAMICO = 2026

CAMPOS_CAPTURA = ["fecha_captura_utc", "anio", "mes_reporte", "url", "archivo",
                  "bytes", "sha256", "http_status"]
CAMPOS_TABLA = ["anio", "mes", "variable", "valor", "publicado", "mes_reporte",
                "acumulado_reportado", "suma_meses", "cuadra", "diferencia",
                "archivo_origen",
                "url_origen", "fecha_captura_utc"]

# ---------------------------------------------------------------- descubrimiento

def descubrir_em(ext: ExtractorEtico, anio: int) -> tuple[int, str] | None:
    """Busca en la pagina 'Anio <anio>' el EM mas reciente de ese anio."""
    portada = ext.get(PAG_ESTADISTICAS).text
    m = re.search(rf'href="([^"]*ano-{anio}\.html)"', portada)
    if not m:
        return None
    url_anio = urljoin(PAG_ESTADISTICAS, m.group(1))
    html = ext.get(url_anio).text
    mejor = None
    for href in re.findall(r'href="([^"]+\.pdf)"', html, flags=re.I):
        nombre = unquote(href.rsplit("/", 1)[-1]).upper()
        mm = re.fullmatch(r"EM-([A-Z]+)-(\d{4})\.PDF", nombre)
        if mm and int(mm.group(2)) == anio and mm.group(1) in MESES:
            mes = MESES.index(mm.group(1)) + 1
            if mejor is None or mes > mejor[0]:
                mejor = (mes, urljoin(url_anio, href))
    return mejor


def objetivos(ext: ExtractorEtico) -> list[tuple[int, int, str]]:
    """Lista (anio, mes_reporte, url) de los EM a usar."""
    lista = [(a, m, urljoin(SITIO, ruta)) for a, (m, ruta) in CATALOGO.items()]
    for anio in range(PRIMER_ANIO_DINAMICO, date.today().year + 1):
        hallado = descubrir_em(ext, anio)
        if hallado:
            lista.append((anio, hallado[0], hallado[1]))
    return lista

# ---------------------------------------------------------------- descarga

def descargar(ext: ExtractorEtico, anio: int, mes: int, url: str) -> tuple[Path, bool]:
    """Descarga el PDF si no existe en bronce. Devuelve (ruta, es_nuevo)."""
    # Nombre ASCII estable; la URL original queda en capturas.csv
    destino = DIR_PDF / str(anio) / f"EM-{anio}-{mes:02d}.pdf"
    if destino.exists():
        return destino, False
    r = ext.get(url)
    if not r.content.startswith(b"%PDF"):
        raise ValueError(f"La respuesta de {url} no es un PDF")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(r.content)
    nuevo_csv = not CAPTURAS.exists()
    with CAPTURAS.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS_CAPTURA)
        if nuevo_csv:
            w.writeheader()
        w.writerow({
            "fecha_captura_utc": ahora_utc(), "anio": anio, "mes_reporte": mes,
            "url": url, "archivo": destino.relative_to(RAIZ).as_posix(),
            "bytes": len(r.content), "sha256": sha256(r.content),
            "http_status": r.status_code,
        })
    return destino, True

# ---------------------------------------------------------------- extraccion

# Primer digito 1-9: un "0" suelto es un mes sin movimiento, nunca el inicio de
# un numero (defecto 1 de Emilio: "0 17,399,502" se unia como "017,399,502").
_DIGITO_PARTIDO = re.compile(r"(?<![\d,.])([1-9]) (\d{2},\d{3})\b")
_NUM = re.compile(r"^-?[\d,]+(\.\d+)?%?$")


def reparar_digitos(texto: str) -> str:
    """El PDF separa a veces el primer digito: '2 70,603' -> '270,603'."""
    return _DIGITO_PARTIDO.sub(r"\1\2", texto)


def numeros(resto: str) -> list[float | None]:
    vals: list[float | None] = []
    for tok in reparar_digitos(resto).split():
        if tok == "-":
            vals.append(None)
        elif _NUM.match(tok):
            vals.append(float(tok.rstrip("%").replace(",", "")))
    return vals


def extraer_lineas(texto: str) -> dict[str, list[float | None]]:
    """Recorre el texto del EM y devuelve {variable: [valores]}."""
    seccion = None
    suma_teu = 0
    out: dict[str, list[float | None]] = {}
    for linea in texto.splitlines():
        l = linea.strip()
        u = l.upper()
        if u.startswith("MOVIMIENTO DE CARGA TONELADAS"):
            seccion = "ton"
        elif u.startswith("ARRIBO DE BUQUES"):
            seccion = "arribos"
        elif re.match(r"MOVIMIENTO DE TEU.S POR EMPRESA POR TR", u):
            seccion = "fin"
        elif re.match(r"MOVIMIENTO DE TEU.S POR EMPRESA", u):
            seccion = "empresa"
        elif u.startswith("MOVIMIENTO DE CONTENEDORES"):
            seccion = "contenedores"

        var = None
        resto = ""
        if seccion == "ton" and u.startswith("CARGA CONTENERIZADA"):
            var, resto = "ton_contenerizada", l[len("Carga Contenerizada"):]
        elif seccion == "arribos" and u.startswith("CARGA CONTENERIZADA"):
            var, resto = "buques_contenerizada", l[len("Carga Contenerizada"):]
        elif re.match(r"CONTENEDORES TEU.S", u):
            var, resto = "teu_total", l[len("CONTENEDORES TEU'S"):]
        elif seccion == "contenedores" and re.match(r"SUMA TEU.S", u):
            suma_teu += 1
            nombres = {1: "teu_importacion", 2: "teu_exportacion",
                       3: "teu_transbordo_entrada", 4: "teu_transbordo_salida"}
            var, resto = nombres.get(suma_teu), l[len("SUMA TEU'S"):]
        elif seccion == "empresa":
            for t in ("SSA", "CONTECON", "OCUPA", "TIMSA"):
                if u.startswith(t + " "):
                    var, resto = f"teu_{t.lower()}", l[len(t):]
        if var and var not in out:
            out[var] = numeros(resto)
    return out


def procesar_pdf(ruta: Path, anio: int, mes_reporte: int, url: str,
                 fecha: str) -> list[dict]:
    with pdfplumber.open(ruta) as pdf:
        texto = "\n".join(p.extract_text() or "" for p in pdf.pages)
    filas = []
    for var, vals in extraer_lineas(texto).items():
        if len(vals) < 12:
            raise ValueError(f"{ruta.name}: '{var}' trae {len(vals)} valores (<12)")
        meses, extra = vals[:12], vals[12:]
        acumulado = extra[0] if extra else None
        suma = sum(v for v in meses if v is not None)
        cuadra = "" if acumulado is None else str(abs(suma - acumulado) < 0.5)
        for i, v in enumerate(meses, start=1):
            filas.append({
                "anio": anio, "mes": i, "variable": var,
                "valor": "" if v is None else int(v),
                "publicado": i <= mes_reporte, "mes_reporte": mes_reporte,
                "acumulado_reportado": "" if acumulado is None else int(acumulado),
                "suma_meses": int(suma), "cuadra": cuadra,
                "diferencia": "" if acumulado is None else int(suma - acumulado),
                "archivo_origen": ruta.relative_to(RAIZ).as_posix(),
                "url_origen": url, "fecha_captura_utc": fecha,
            })
    return filas


def fecha_captura(archivo: Path) -> str:
    """Fecha de captura registrada en capturas.csv para ese archivo."""
    rel = archivo.relative_to(RAIZ).as_posix()
    if CAPTURAS.exists():
        with CAPTURAS.open(encoding="utf-8") as f:
            for fila in csv.DictReader(f):
                if fila["archivo"] == rel:
                    return fila["fecha_captura_utc"]
    return ""

# ---------------------------------------------------------------- principal

def ejecutar() -> dict:
    ext = ExtractorEtico(pausa=2.0)
    nuevos = 0
    filas: list[dict] = []
    for anio, mes, url in sorted(objetivos(ext)):
        ruta, es_nuevo = descargar(ext, anio, mes, url)
        nuevos += es_nuevo
        filas += procesar_pdf(ruta, anio, mes, url, fecha_captura(ruta))
    TABLA.parent.mkdir(parents=True, exist_ok=True)
    with TABLA.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS_TABLA)
        w.writeheader()
        w.writerows(filas)
    return {"registros": len(filas), "archivos_nuevos": nuevos}


if __name__ == "__main__":
    res = ejecutar()
    print(res)
    sys.exit(0)
