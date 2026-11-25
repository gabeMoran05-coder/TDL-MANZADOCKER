"""Comparación reproducible de normalización; no modifica capas de datos."""
import hashlib
import json
import platform
import statistics
import subprocess
import time
import tracemalloc
import types
from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal

from src import limpieza

BASE = 'ceceab9'

def baseline():
    codigo = subprocess.check_output(['git', 'show', f'{BASE}:src/limpieza.py']).decode('utf-8')
    modulo = types.ModuleType('baseline_e3')
    exec(compile(codigo, 'baseline_e3', 'exec'), modulo.__dict__)
    return modulo

def medir(funcion, datos):
    tiempos = []
    for _ in range(3):
        inicio = time.perf_counter()
        salida = funcion(datos, 'banxico')
        tiempos.append(time.perf_counter() - inicio)
    tracemalloc.start()
    funcion(datos, 'banxico')
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return salida, tiempos, pico

def main():
    ruta = Path('data/bronce/banxico/tipo_cambio_fix.csv')
    datos = pd.read_csv(ruta, dtype=str, keep_default_na=False, skip_blank_lines=False)
    anterior = baseline()
    a, ta, ma = medir(anterior.normalizar, datos)
    b, tb, mb = medir(limpieza.normalizar, datos)
    assert_frame_equal(a[0], b[0])
    assert a[1:] == b[1:]
    # Errores conocidos: fecha de captura y valor inválidos y conflicto con valor crudo.
    defectos = datos.iloc[:3].copy()
    defectos.iloc[0, defectos.columns.get_loc('fecha_captura_utc')] = 'invalida'
    defectos.iloc[1, defectos.columns.get_loc('valor')] = 'abc'
    defectos.iloc[2, defectos.columns.get_loc('valor')] = '999'
    x = anterior.normalizar(defectos, 'banxico')
    y = limpieza.normalizar(defectos, 'banxico')
    assert_frame_equal(x[0], y[0])
    assert x[1:] == y[1:]
    salida = {
        'baseline_commit': BASE, 'entrada': str(ruta),
        'entrada_sha256': hashlib.sha256(ruta.read_bytes()).hexdigest(),
        'python': platform.python_version(), 'pandas': pd.__version__,
        'metodo': '3 ejecuciones secuenciales por versión, mediana sin tracemalloc; pico Python en ejecución separada',
        'filas': len(datos), 'antes_segundos': ta, 'despues_segundos': tb,
        'mediana_antes_s': statistics.median(ta), 'mediana_despues_s': statistics.median(tb),
        'pico_antes_bytes': ma, 'pico_despues_bytes': mb,
        'rechazos_antes': len(a[2]), 'rechazos_despues': len(b[2]),
        'defectos_inyectados': 3, 'defectos_rechazados_antes': len(x[2]),
        'defectos_rechazados_despues': len(y[2]), 'salidas_equivalentes': True,
    }
    Path('calidad/e3/benchmark.json').write_text(json.dumps(salida, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps(salida, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
