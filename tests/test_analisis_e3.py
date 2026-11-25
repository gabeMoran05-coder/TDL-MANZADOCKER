
import numpy as np
import pandas as pd
import pytest

from scripts.analisis_e3 import SOURCE, VARIABLES, calcular


def test_pca_reproducible_y_cargas():
    tabla, valores, vectores, puntos, cargas, distancias, resultado = calcular(pd.read_csv(SOURCE))
    assert len(tabla) == resultado['n'] and len(tabla) > 6
    assert list(tabla.columns) == VARIABLES
    assert np.isclose(sum(resultado['varianza_explicada']), 1)
    assert np.allclose(vectores.T @ vectores, np.eye(5))
    assert np.all(distancias >= 0)
    assert np.allclose(cargas, vectores * np.sqrt(valores))
    assert puntos.shape == (len(tabla), 5)


def test_pca_rechaza_duplicados():
    datos = pd.read_csv(SOURCE)
    repetido = datos[datos.variable.eq(VARIABLES[0])].iloc[[0]]
    with pytest.raises(ValueError, match='duplicadas'):
        calcular(pd.concat([datos, repetido], ignore_index=True))
