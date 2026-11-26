"""Comparación de robots HTTP simulados; sin solicitudes de red ni datos reales."""
from __future__ import annotations

import hashlib
import json
import platform
import statistics
import subprocess
import time
import tracemalloc
import types
from pathlib import Path

import requests

from extractores import base as actual

BASE = 'f9275de'
ROOT = Path(__file__).resolve().parents[1]


def version_anterior():
    codigo = subprocess.check_output(['git', 'show', f'{BASE}:extractores/base.py'], cwd=ROOT)
    modulo = types.ModuleType('base_anterior')
    modulo.__file__ = str(ROOT / 'extractores/base.py')
    exec(compile(codigo.decode('utf-8'), modulo.__file__, 'exec'), modulo.__dict__)
    return modulo


def carga(modulo):
    """100 casos de cada estado: 429, 403, 503 (bloquear) y 404 (permitir)."""
    errores = 0
    intentos_indebidos = 0
    conteos = {}
    for codigo in (429, 403, 503, 404):
        fallas_codigo = 0
        for _ in range(100):
            extractor = modulo.ExtractorEtico(pausa=0)
            llamadas = []

            class Respuesta:
                def __init__(self, estado):
                    self.status_code = estado

                def raise_for_status(self):
                    return None

            def respuesta(url, **kwargs):
                llamadas.append(url)
                return Respuesta(codigo if url.endswith('/robots.txt') else 200)

            extractor.sesion.get = respuesta
            try:
                extractor.get('https://ejemplo.invalid/datos', intentos=1)
                autorizado = True
            except PermissionError:
                autorizado = False
            esperado = codigo == 404
            if autorizado != esperado:
                errores += 1
                fallas_codigo += 1
            if codigo != 404 and len(llamadas) > 1:
                intentos_indebidos += 1
            extractor.sesion.close()
        conteos[str(codigo)] = fallas_codigo
    return {'casos': 400, 'errores_decision': errores,
            'intentos_indebidos': intentos_indebidos, 'errores_por_codigo': conteos}


def medir(modulo):
    tiempos = []
    for _ in range(5):
        inicio = time.perf_counter()
        resultado = carga(modulo)
        tiempos.append(time.perf_counter() - inicio)
    tracemalloc.start()
    carga(modulo)
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {'tiempos_s': tiempos, 'mediana_s': statistics.median(tiempos),
            'pico_memoria_python_bytes': pico, **resultado}


def main():
    salida = {'baseline_commit': BASE, 'python': platform.python_version(),
              'requests': requests.__version__, 'metodo': '400 casos sinteticos, 5 corridas '
              'secuenciales sin red; memoria tracemalloc en corrida separada',
              'codigo_actual_sha256': hashlib.sha256((ROOT / 'extractores/base.py').read_bytes()).hexdigest(),
              'antes': medir(version_anterior()), 'despues': medir(actual)}
    destino = ROOT / 'calidad/e3/benchmark_captura.json'
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(salida, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(salida, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
