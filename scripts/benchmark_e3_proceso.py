"""Benchmark E3 complementario: entrada fija, un proceso por versión y memoria total.

Diferencias con scripts/benchmark_e3.py (que se conserva sin cambios):
- La entrada se lee de un commit fijo con `git show` y se verifica su SHA-256, así
  el resultado no depende de la captura Banxico del día.
- Cada versión corre en su propio proceso; las versiones se alternan en varias rondas
  y se descarta una corrida de calentamiento por proceso.
- Se reportan por separado la memoria Python (tracemalloc) y la memoria total del
  proceso (pico de working set en Windows o ru_maxrss en Linux).

Uso:  python -m scripts.benchmark_e3_proceso
Escribe calidad/e3/benchmark_proceso.json; no modifica capas de datos.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import platform
import statistics
import subprocess
import sys
import time
import tracemalloc
import types
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BASE = "ceceab9"                       # versión anterior de src/limpieza.py
ENTRADA_COMMIT = "f9275de"             # captura Banxico usada en benchmark_26nov.json
ENTRADA_RUTA = "data/bronce/banxico/tipo_cambio_fix.csv"
ENTRADA_SHA256 = "b60791e08b2eda231651592cd5fccfebd8c55d6addaf53f978ede14a72331029"
SALIDA = RAIZ / "calidad/e3/benchmark_proceso.json"


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=RAIZ)


def memoria_proceso() -> dict:
    """Memoria del proceso actual en bytes: actual y pico desde que inició."""
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes

        class Contadores(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                        ("PeakWorkingSetSize", ctypes.c_size_t),
                        ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t),
                        ("PeakPagefileUsage", ctypes.c_size_t)]

        c = Contadores()
        c.cb = ctypes.sizeof(c)
        kernel32, psapi = ctypes.WinDLL("kernel32"), ctypes.WinDLL("psapi")
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Contadores),
                                               wintypes.DWORD]
        if not psapi.GetProcessMemoryInfo(kernel32.GetCurrentProcess(), ctypes.byref(c), c.cb):
            raise OSError("GetProcessMemoryInfo falló")
        return {"actual_bytes": c.WorkingSetSize, "pico_bytes": c.PeakWorkingSetSize,
                "metrica": "working set (Windows psapi)"}
    import os
    import resource
    pico = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    pico *= 1 if sys.platform == "darwin" else 1024  # Linux reporta KiB
    with open("/proc/self/statm") as f:
        actual = int(f.read().split()[1]) * os.sysconf("SC_PAGE_SIZE")
    return {"actual_bytes": actual, "pico_bytes": pico, "metrica": "RSS (ru_maxrss)"}


def cargar_version(version: str):
    if version == "despues":
        from src import limpieza
        return limpieza
    codigo = git("show", f"{BASE}:src/limpieza.py").decode("utf-8")
    modulo = types.ModuleType("baseline_e3")
    exec(compile(codigo, "baseline_e3", "exec"), modulo.__dict__)
    return modulo


def leer_entrada():
    import pandas as pd
    crudo = git("show", f"{ENTRADA_COMMIT}:{ENTRADA_RUTA}")
    if hashlib.sha256(crudo).hexdigest() != ENTRADA_SHA256:
        raise ValueError("La entrada fija no coincide con su SHA-256 registrado")
    return pd.read_csv(io.BytesIO(crudo), dtype=str, keep_default_na=False,
                       skip_blank_lines=False)


def huella(resultado) -> str:
    """SHA-256 de la salida completa (tabla, originales y rechazos) para comparar versiones."""
    tabla, *resto = resultado
    texto = tabla.to_csv(index=False) + json.dumps(resto, default=str, sort_keys=True)
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def trabajador(version: str, repeticiones: int) -> dict:
    """Corre dentro de un proceso nuevo: mide una sola versión."""
    datos = leer_entrada()
    modulo = cargar_version(version)
    tras_carga = memoria_proceso()
    modulo.normalizar(datos, "banxico")             # calentamiento, no se cuenta
    tiempos = []
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        resultado = modulo.normalizar(datos, "banxico")
        tiempos.append(time.perf_counter() - inicio)
    final = memoria_proceso()
    tracemalloc.start()                              # corrida separada: tracemalloc la frena
    modulo.normalizar(datos, "banxico")
    pico_python = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    defectos = datos.iloc[:3].copy()
    defectos.iloc[0, defectos.columns.get_loc("fecha_captura_utc")] = "invalida"
    defectos.iloc[1, defectos.columns.get_loc("valor")] = "abc"
    defectos.iloc[2, defectos.columns.get_loc("valor")] = "999"
    return {"version": version, "tiempos_s": tiempos, "filas": len(datos),
            "rechazos": len(resultado[2]), "huella_salida": huella(resultado),
            "defectos_rechazados": len(modulo.normalizar(defectos, "banxico")[2]),
            "memoria_proceso": {"metrica": final["metrica"],
                                "tras_cargar_bytes": tras_carga["actual_bytes"],
                                "pico_bytes": final["pico_bytes"],
                                "incremento_pico_bytes": final["pico_bytes"]
                                - tras_carga["actual_bytes"]},
            "pico_python_tracemalloc_bytes": pico_python}


def lanzar(version: str, repeticiones: int) -> dict:
    salida = subprocess.check_output(
        [sys.executable, "-m", "scripts.benchmark_e3_proceso", "--trabajador", version,
         "--repeticiones", str(repeticiones)], cwd=RAIZ)
    return json.loads(salida.decode("utf-8").strip().splitlines()[-1])


def resumir(corridas: list[dict]) -> dict:
    tiempos = [t for c in corridas for t in c["tiempos_s"]]
    picos = [c["memoria_proceso"]["pico_bytes"] for c in corridas]
    incrementos = [c["memoria_proceso"]["incremento_pico_bytes"] for c in corridas]
    return {"corridas_medidas": len(tiempos), "tiempos_s": tiempos,
            "mediana_s": statistics.median(tiempos), "minimo_s": min(tiempos),
            "maximo_s": max(tiempos),
            "memoria_proceso_pico_mediana_bytes": statistics.median(picos),
            "memoria_proceso_incremento_mediana_bytes": statistics.median(incrementos),
            "pico_python_tracemalloc_mediana_bytes":
                statistics.median(c["pico_python_tracemalloc_bytes"] for c in corridas),
            "rechazos": corridas[0]["rechazos"],
            "defectos_rechazados": corridas[0]["defectos_rechazados"],
            "huella_salida": corridas[0]["huella_salida"]}


def principal(rondas: int, repeticiones: int) -> dict:
    corridas = {"antes": [], "despues": []}
    for _ in range(rondas):                         # antes, después, antes, después...
        for version in corridas:
            corridas[version].append(lanzar(version, repeticiones))
    huellas = {c["huella_salida"] for v in corridas.values() for c in v}
    if len(huellas) != 1:
        raise AssertionError("Las versiones no producen la misma salida")
    antes, despues = resumir(corridas["antes"]), resumir(corridas["despues"])
    import pandas as pd
    resultado = {
        "tipo": "datos reales (captura Banxico Bronce fijada por commit), sin red",
        "baseline_commit": BASE, "despues_commit": git("rev-parse", "--short", "HEAD").decode().strip(),
        "despues_limpieza_sha256": hashlib.sha256((RAIZ / "src/limpieza.py").read_bytes()).hexdigest(),
        "entrada": {"commit": ENTRADA_COMMIT, "ruta": ENTRADA_RUTA, "sha256": ENTRADA_SHA256,
                    "filas": corridas["antes"][0]["filas"]},
        "metodo": (f"{rondas} rondas alternando versiones; cada ronda lanza un proceso por "
                   f"versión con 1 calentamiento y {repeticiones} corridas medidas; "
                   "tracemalloc en corrida separada; memoria del proceso leída del sistema"),
        "entorno": {"python": platform.python_version(), "pandas": pd.__version__,
                    "sistema": platform.platform(), "procesador": platform.processor()},
        "antes": antes, "despues": despues,
        "reduccion_mediana_tiempo_pct": round(100 * (1 - despues["mediana_s"] / antes["mediana_s"]), 1),
        "reduccion_incremento_memoria_proceso_pct": round(100 * (
            1 - despues["memoria_proceso_incremento_mediana_bytes"]
            / antes["memoria_proceso_incremento_mediana_bytes"]), 1),
        "salidas_identicas": True,
    }
    SALIDA.write_text(json.dumps(resultado, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return resultado


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--trabajador", choices=["antes", "despues"])
    p.add_argument("--rondas", type=int, default=3)
    p.add_argument("--repeticiones", type=int, default=5)
    a = p.parse_args()
    if a.trabajador:
        print(json.dumps(trabajador(a.trabajador, a.repeticiones)))
    else:
        r = principal(a.rondas, a.repeticiones)
        print(json.dumps({k: r[k] for k in ("reduccion_mediana_tiempo_pct",
                                            "reduccion_incremento_memoria_proceso_pct")}))
        for v in ("antes", "despues"):
            print(v, {k: r[v][k] for k in ("mediana_s", "minimo_s", "maximo_s",
                                           "memoria_proceso_pico_mediana_bytes",
                                           "memoria_proceso_incremento_mediana_bytes",
                                           "pico_python_tracemalloc_mediana_bytes",
                                           "rechazos", "defectos_rechazados")})
