"""PCA descriptivo portuario; genera evidencia E3 sin modificar datos Oro."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/plata/asipona_mensual.csv'
OUT = ROOT / 'calidad/e3'
VARIABLES = ['teu_total', 'ton_contenerizada', 'buques_contenerizada',
             'teu_importacion', 'teu_exportacion']


def calcular(datos):
    seleccion = datos.loc[datos.variable.isin(VARIABLES), ['fecha', 'variable', 'valor', 'imputado']]
    if seleccion.duplicated(['fecha', 'variable']).any():
        raise ValueError('Hay claves fecha-variable duplicadas')
    # No se mezclan imputaciones con observaciones para esta exploración.
    seleccion = seleccion.loc[~seleccion.imputado.astype(str).str.lower().eq('true')]
    tabla = seleccion.pivot(index='fecha', columns='variable', values='valor').reindex(columns=VARIABLES)
    tabla = tabla.dropna().sort_index()
    x = tabla.to_numpy(dtype=float)
    if len(x) <= len(VARIABLES) + 1 or not np.isfinite(x).all():
        raise ValueError('Muestra insuficiente o no finita')
    desviacion = x.std(axis=0, ddof=1)
    if (desviacion == 0).any():
        raise ValueError('Variable constante')
    z = (x - x.mean(axis=0)) / desviacion
    correlacion = np.cov(z, rowvar=False, ddof=1)
    valores, vectores = np.linalg.eigh(correlacion)
    orden = np.argsort(valores)[::-1]
    valores, vectores = valores[orden], vectores[:, orden]
    if valores.min() <= 1e-10:
        raise ValueError('Covarianza singular: no se calcula Mardia')
    # Orientación determinista: mayor carga absoluta positiva.
    for j in range(vectores.shape[1]):
        if vectores[np.argmax(np.abs(vectores[:, j])), j] < 0:
            vectores[:, j] *= -1
    puntos = z @ vectores
    cargas = vectores * np.sqrt(valores)
    n, p = z.shape
    # Mardia utiliza covarianza con divisor n; PCA usa divisor n-1.
    inversa_mardia = np.linalg.inv(correlacion) * n / (n - 1)
    distancias = np.einsum('ij,jk,ik->i', z, inversa_mardia, z)
    gram = z @ inversa_mardia @ z.T
    b1 = np.mean(gram ** 3)
    b2 = np.mean(distancias ** 2)
    chi = n * b1 / 6
    grados = p * (p + 1) * (p + 2) / 6
    zk = (b2 - p * (p + 2)) / np.sqrt(8 * p * (p + 2) / n)
    return tabla, valores, vectores, puntos, cargas, distancias, {
        'n': n, 'variables': VARIABLES, 'inicio': str(tabla.index.min()), 'fin': str(tabla.index.max()),
        'sha256_entrada': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'covarianza': tabla.cov().round(8).to_dict(), 'correlacion': tabla.corr().round(8).to_dict(),
        'valores_propios': valores.tolist(), 'varianza_explicada': (valores / valores.sum()).tolist(),
        'cargas': pd.DataFrame(cargas, index=VARIABLES, columns=[f'PC{i+1}' for i in range(len(VARIABLES))]).round(6).to_dict(),
        'mardia': {'asimetria': b1, 'chi2': chi, 'gl': grados, 'p_asimetria': stats.chi2.sf(chi, grados),
                   'curtosis': b2, 'z_curtosis': zk, 'p_curtosis': 2 * stats.norm.sf(abs(zk))},
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tabla, valores, vectores, puntos, cargas, distancias, resultado = calcular(pd.read_csv(SOURCE))
    (OUT / 'pca.json').write_text(json.dumps(resultado, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    pd.DataFrame({'fecha': tabla.index, 'PC1': puntos[:, 0], 'PC2': puntos[:, 1]}).to_csv(OUT / 'pca_puntos.csv', index=False)
    fig, ax = plt.subplots(1, 3, figsize=(16, 5), constrained_layout=True)
    ax[0].bar(range(1, 6), 100 * valores / valores.sum())
    ax[0].set(xlabel='Componente', ylabel='Varianza explicada (%)', title='Sedimentación')
    ax[1].scatter(puntos[:, 0], puntos[:, 1], alpha=.7)
    for i, nombre in enumerate(VARIABLES):
        ax[1].arrow(0, 0, cargas[i, 0]*2, cargas[i, 1]*2, color='firebrick', head_width=.06, length_includes_head=True)
        ax[1].annotate(nombre, (cargas[i, 0]*2, cargas[i, 1]*2), fontsize=8)
    ax[1].axhline(0, color='gray', lw=.5)
    ax[1].axvline(0, color='gray', lw=.5)
    ax[1].set(xlabel='PC1', ylabel='PC2', title='Meses y cargas (flechas ×2)')
    q = stats.chi2.ppf((np.arange(len(distancias)) + .5)/len(distancias), len(VARIABLES))
    ax[2].scatter(q, np.sort(distancias))
    ax[2].plot([0, max(q)], [0, max(q)], 'r--')
    ax[2].set(xlabel='Cuantiles χ²(5)', ylabel='Distancia cuadrada', title='Q-Q de Mahalanobis')
    fig.savefig(OUT / 'pca_diagnosticos.png', dpi=150)
    plt.close(fig)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
