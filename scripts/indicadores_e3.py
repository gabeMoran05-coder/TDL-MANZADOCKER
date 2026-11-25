"""Indicadores E3 acotados a los archivos y ventana declarados."""
import json
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from src.fiabilidad import agrupar_ejecuciones, leer_bitacora

RAIZ = Path(__file__).resolve().parents[1]


def main():
    fin = date(2026, 11, 24)
    dias = [fin - timedelta(days=i) for i in range(13, -1, -1)]
    eventos = agrupar_ejecuciones(leer_bitacora(RAIZ / 'calidad/bitacora_captura.csv'))
    exitos = set(eventos.loc[eventos.disparador.eq('schedule') & eventos.exito, 'inicio'].dt.date)
    completos = {}
    for archivo in ('mensual_integrado.csv', 'terminales_mes.csv', 'denue_celdas.csv'):
        datos = pd.read_csv(RAIZ / 'data/oro' / archivo)
        presentes = int(datos.notna().sum().sum())
        completos[archivo] = {'presentes': presentes, 'celdas': int(datos.size),
                              'proporcion': presentes / datos.size}
    resultado = {'ventana_utc': [str(dias[0]), str(dias[-1])],
                 'dias_exitosos': sum(d in exitos for d in dias), 'dias': len(dias),
                 'dias_sin_exito': [str(d) for d in dias if d not in exitos],
                 'completitud_no_nulos': completos}
    (RAIZ / 'calidad/e3/indicadores.json').write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
